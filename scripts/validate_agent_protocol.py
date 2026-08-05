#!/usr/bin/env python3
"""Validate the current Codex Multi-Agent Protocol."""

from __future__ import annotations

import argparse
from dataclasses import dataclass
import re
import subprocess
from pathlib import Path
from typing import Any

import yaml


AGENTS = {"agent:luna", "agent:terra", "agent:sol"}
TASK_ID_RE = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._-]*$")
REPOSITORY_RE = re.compile(r"^[^/\s]+/[^/\s]+$")
ISSUE_RE = re.compile(r"^[^/\s]+/[^#\s]+#[1-9][0-9]*$")
PROTECTED_ACTIONS = {
    "push_facts_repository", "modify_registry", "initialize_formal_issue",
    "fetch_official_upstream", "modify_upstream_code", "upstream_write",
    "push_upstream_branch", "create_issue", "comment_issue", "assign_issue",
    "add_labels", "create_pull_request",
}
TARGET_PHASES = {"evidence", "deep-audit", "implementation"}
RESULT_STATES = {"active": "active", "decision": "awaiting-decision", "completed": "completed", "blocked": "blocked", "failed": "failed"}
DECISION_STATES = {"completed": "completed", "changes-requested": "changes-requested", "rejected": "rejected"}


@dataclass(frozen=True)
class TaskRecord:
    path: Path
    request: dict[str, Any]
    result: dict[str, Any] | None
    decision: dict[str, Any] | None
    approval: dict[str, Any] | None
    status: str


def path_matches(path: str, pattern: str) -> bool:
    expression = re.escape(pattern.lstrip("./")).replace(r"\*\*", ".*").replace(r"\*", "[^/]*")
    return re.fullmatch(expression, path.lstrip("./")) is not None


def load_yaml(path: Path, errors: list[str]) -> dict[str, Any]:
    try:
        value = yaml.safe_load(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, yaml.YAMLError) as error:
        errors.append(f"{path}: cannot parse YAML: {error}")
        return {}
    if not isinstance(value, dict):
        errors.append(f"{path}: must contain a YAML mapping")
        return {}
    return value


def require_fields(value: dict[str, Any], fields: list[str], location: str, errors: list[str]) -> None:
    for field in fields:
        if field not in value:
            errors.append(f"{location}: missing required field {field}")


def string_items(value: Any) -> list[str]:
    return [item for item in value if isinstance(item, str)] if isinstance(value, list) else []


def _absolute_path_strings(value: Any, location: str) -> list[str]:
    found: list[str] = []
    if isinstance(value, dict):
        for key, child in value.items():
            found.extend(_absolute_path_strings(child, f"{location}.{key}"))
    elif isinstance(value, list):
        for index, child in enumerate(value):
            found.extend(_absolute_path_strings(child, f"{location}[{index}]"))
    elif isinstance(value, str) and value.startswith("/"):
        found.append(f"{location}: absolute path is not allowed")
    return found


def validate_repository_registry(root: Path) -> list[str]:
    errors: list[str] = []
    registry_path = root / "repositories" / "registry.yaml"
    discovery_path = root / "repositories" / "discovery.yaml"
    registry = load_yaml(registry_path, errors)
    discovery = load_yaml(discovery_path, errors)
    if registry.get("schema_version") != 1:
        errors.append(f"{registry_path}: schema_version must be 1")
    entries = registry.get("repositories")
    if not isinstance(entries, dict) or not entries:
        errors.append(f"{registry_path}.repositories: must be a non-empty mapping")
    else:
        for name, entry in entries.items():
            location = f"{registry_path}.repositories.{name}"
            if not isinstance(name, str) or not REPOSITORY_RE.fullmatch(name):
                errors.append(f"{location}: key must use owner/name")
            if not isinstance(entry, dict):
                errors.append(f"{location}: must be a mapping")
                continue
            if entry.get("type") != "target":
                errors.append(f"{location}.type: must be target")
            upstream = entry.get("upstream")
            if not isinstance(upstream, dict) or not isinstance(upstream.get("url"), str):
                errors.append(f"{location}.upstream.url: must be a URL string")
            fork = entry.get("fork")
            if not isinstance(fork, dict) or not isinstance(fork.get("enabled"), bool):
                errors.append(f"{location}.fork.enabled: must be boolean")
            local = entry.get("local", {}).get("discovery") if isinstance(entry.get("local"), dict) else None
            if not isinstance(local, dict) or not isinstance(local.get("enabled"), bool):
                errors.append(f"{location}.local.discovery.enabled: must be boolean")
            contribution = entry.get("contribution")
            if not isinstance(contribution, dict) or not isinstance(contribution.get("enabled"), bool):
                errors.append(f"{location}.contribution.enabled: must be boolean")
            identity = entry.get("git_identity")
            if not isinstance(identity, dict):
                errors.append(f"{location}.git_identity: must be a mapping")
            else:
                if not isinstance(identity.get("name"), str) or not identity.get("name", "").strip():
                    errors.append(f"{location}.git_identity.name: must be non-empty")
                if not isinstance(identity.get("email"), str) or "@" not in identity.get("email", ""):
                    errors.append(f"{location}.git_identity.email: must be an email string")
                signing = identity.get("signing")
                if not isinstance(signing, dict) or not isinstance(signing.get("required"), bool):
                    errors.append(f"{location}.git_identity.signing.required: must be boolean")
    errors.extend(_absolute_path_strings(registry, str(registry_path)))
    if discovery.get("schema_version") != 1:
        errors.append(f"{discovery_path}: schema_version must be 1")
    roots = discovery.get("scan_roots")
    if not isinstance(roots, list) or not roots or any(not isinstance(item, str) or not item or item.startswith("/") for item in roots):
        errors.append(f"{discovery_path}.scan_roots: must be non-empty relative paths")
    return errors


def validate_agent_roles(root: Path, permissions: dict[str, Any] | None = None) -> list[str]:
    errors: list[str] = []
    expected = {"luna": "discovery-and-decision", "terra": "analysis-and-execution", "sol": "escalation-review"}
    for name, role in expected.items():
        path = root / "agents" / f"{name}.yaml"
        data = load_yaml(path, errors)
        if data.get("schema_version") != 1 or data.get("agent") != name or data.get("role") != role:
            errors.append(f"{path}: invalid Agent role declaration")
        for field in ("responsibilities", "allowed_actions", "prohibited_actions"):
            if not isinstance(data.get(field), list) or not data[field]:
                errors.append(f"{path}.{field}: must be a non-empty list")
        if permissions is not None:
            declared = set(string_items(data.get("allowed_actions")))
            configured = set(string_items(permissions.get("roles", {}).get(name, {}).get("allowed_actions")))
            if declared != configured:
                errors.append(f"{path}: allowed_actions must match permissions.yaml role {name}")
    sol = load_yaml(root / "agents" / "sol.yaml", [])
    if not {"repository_modify", "commit_facts_repository", "push_facts_repository"}.issubset(set(string_items(sol.get("prohibited_actions")))):
        errors.append("agents/sol.yaml: Sol must remain escalation-only")
    return errors


def protocol_documents(root: Path, errors: list[str]) -> tuple[dict[str, Any], dict[str, Any], dict[str, Any]]:
    protocol = root / "agent-protocol"
    return (load_yaml(protocol / "task-schema.yaml", errors), load_yaml(protocol / "permissions.yaml", errors), load_yaml(protocol / "state-machine.yaml", errors))


def validate_protocol_documents(schema: dict[str, Any], permissions: dict[str, Any], state_machine: dict[str, Any], errors: list[str]) -> None:
    if schema.get("schema_version") != 4:
        errors.append("task-schema.yaml: schema_version must be 4")
    if permissions.get("schema_version") != 3:
        errors.append("permissions.yaml: schema_version must be 3")
    if state_machine.get("schema_version") != 2:
        errors.append("state-machine.yaml: schema_version must be 2")
    if set(schema.get("enums", {}).get("created_by", [])) != AGENTS | {"user"}:
        errors.append("task-schema.yaml: current Agent authors are invalid")
    queue = state_machine.get("queue_artifact_state", {})
    expected_states = {"ready", "active", "awaiting-decision", "changes-requested", "blocked", "failed", "rejected", "completed"}
    if set(queue.get("states", [])) != expected_states:
        errors.append("state-machine.yaml: queue states must be current multi-agent states")
    expected_lifecycle = {"candidate": ["evidence"], "evidence": ["analysis"], "analysis": ["decision"], "decision": ["implementation"], "implementation": ["pull-request"], "pull-request": []}
    if state_machine.get("contribution_coordination", {}).get("transitions") != expected_lifecycle:
        errors.append("state-machine.yaml: lifecycle is invalid")
    if "deep-audit" not in schema.get("enums", {}).get("task_type", []):
        errors.append("task-schema.yaml: deep-audit is missing")
    if schema.get("target_repository_contract", {}).get("phases") != ["evidence", "deep-audit", "implementation"]:
        errors.append("task-schema.yaml: target repository phases are invalid")
    actors = permissions.get("actors", {})
    if set(actors) != AGENTS | {"user"}:
        errors.append("permissions.yaml: only current Agents and user may be actors")
    always = set(permissions.get("always_user_confirmation_actions", []))
    if not PROTECTED_ACTIONS.issubset(always):
        errors.append("permissions.yaml: protected public actions are incomplete")
    if set(permissions.get("approval_required_actions", [])) != PROTECTED_ACTIONS:
        errors.append("permissions.yaml: approval action set is invalid")
    if "REVIEW.yaml" in str(schema) or "chat" in str(permissions).lower() or "codex" in str(permissions).lower():
        errors.append("protocol documents contain removed Chat/Codex protocol")


def validate_target_repository_binding(request: dict[str, Any], schema: dict[str, Any], location: str, errors: list[str]) -> None:
    task_type = request.get("task_type")
    binding = request.get("target_repository")
    if task_type in {"deep-audit", "implementation"} and not isinstance(binding, dict):
        errors.append(f"{location}.target_repository: {task_type} requires a binding")
        return
    if binding is None:
        return
    if not isinstance(binding, dict):
        errors.append(f"{location}.target_repository: must be a mapping")
        return
    for field in schema.get("target_repository_contract", {}).get("required_fields", ["name", "phase"]):
        if field not in binding:
            errors.append(f"{location}.target_repository.{field}: required")
    name = binding.get("name")
    if not isinstance(name, str) or not REPOSITORY_RE.fullmatch(name) or name != request.get("repository"):
        errors.append(f"{location}.target_repository.name: must match repository owner/name")
    phase = binding.get("phase")
    if phase not in TARGET_PHASES:
        errors.append(f"{location}.target_repository.phase: invalid phase")
    if task_type in TARGET_PHASES and phase != task_type:
        errors.append(f"{location}.target_repository.phase: must match task type")
    if task_type == "implementation":
        fork, local = binding.get("fork"), binding.get("local")
        if not isinstance(fork, dict) or not isinstance(fork.get("url"), str):
            errors.append(f"{location}.target_repository.fork.url: required")
        if not isinstance(local, dict) or not isinstance(local.get("path"), str) or local.get("discovery") is not True:
            errors.append(f"{location}.target_repository.local: path and discovery=true required")


def validate_request(request: dict[str, Any], schema: dict[str, Any], permissions: dict[str, Any], location: str, errors: list[str]) -> None:
    require_fields(request, schema.get("request", {}).get("required_fields", []), location, errors)
    if request.get("schema_version") != 2:
        errors.append(f"{location}.schema_version: must be 2")
    if request.get("created_by") not in AGENTS | {"user"} or request.get("decision_author") != request.get("created_by") or request.get("materialized_by") != request.get("created_by"):
        errors.append(f"{location}: current artifacts must be self-authored by an Agent or user")
    if request.get("assigned_agent") not in AGENTS:
        errors.append(f"{location}.assigned_agent: must be a current Agent")
    if request.get("status") != "ready":
        errors.append(f"{location}.status: must be ready")
    task_type = request.get("task_type")
    if task_type not in schema.get("enums", {}).get("task_type", []):
        errors.append(f"{location}.task_type: invalid task type")
    task_id = request.get("task_id")
    if not isinstance(task_id, str) or not TASK_ID_RE.fullmatch(task_id):
        errors.append(f"{location}.task_id: invalid identifier")
    repository = request.get("repository")
    if not isinstance(repository, str) or not REPOSITORY_RE.fullmatch(repository):
        errors.append(f"{location}.repository: must use owner/name")
    issue = request.get("issue")
    if issue is not None and (not isinstance(issue, str) or not ISSUE_RE.fullmatch(issue)):
        errors.append(f"{location}.issue: invalid issue reference")
    if isinstance(issue, str) and not issue.startswith(f"{repository}#"):
        errors.append(f"{location}.issue: repository must match request repository")
    for field in ("input_refs", "allowed_actions", "prohibited_actions", "expected_outputs"):
        if not isinstance(request.get(field), list) or len(string_items(request[field])) != len(request[field]):
            errors.append(f"{location}.{field}: must be a list of strings")
    if not isinstance(request.get("approval_required"), bool):
        errors.append(f"{location}.approval_required: must be boolean")
    action_catalog = permissions.get("action_catalog", {})
    allowed_actions = set(string_items(request.get("allowed_actions")))
    prohibited_actions = set(string_items(request.get("prohibited_actions")))
    unknown_actions = (allowed_actions | prohibited_actions) - set(action_catalog)
    if unknown_actions:
        errors.append(f"{location}: unknown actions: {', '.join(sorted(unknown_actions))}")
    role_name = permissions.get("actors", {}).get(request.get("assigned_agent"), {}).get("role")
    role_actions = set(string_items(permissions.get("roles", {}).get(role_name, {}).get("allowed_actions")))
    non_protected_forbidden = (allowed_actions - set(PROTECTED_ACTIONS)) - role_actions
    if non_protected_forbidden:
        errors.append(f"{location}: assigned Agent cannot perform: {', '.join(sorted(non_protected_forbidden))}")
    if allowed_actions & prohibited_actions:
        errors.append(f"{location}: actions cannot be both allowed and prohibited")
    contract = schema.get("task_type_contracts", {}).get(task_type, {})
    contract_prohibited = set(string_items(contract.get("prohibited_allowed_actions")))
    overlap = allowed_actions & contract_prohibited
    if overlap:
        errors.append(f"{location}: task type prohibits allowed actions: {', '.join(sorted(overlap))}")
    if task_type == "deep-audit":
        refs = request.get("evidence_refs")
        if not isinstance(refs, list) or not refs:
            errors.append(f"{location}.evidence_refs: deep-audit requires a non-empty list")
    validate_target_repository_binding(request, schema, location, errors)
    if not isinstance(request.get("goal"), str) or not request["goal"].strip():
        errors.append(f"{location}.goal: must be non-empty")
    completion = request.get("completion")
    if completion is not None and not isinstance(completion, dict):
        errors.append(f"{location}.completion: must be a mapping when provided")
    elif isinstance(completion, dict):
        require_fields(completion, schema.get("completion_contract", {}).get("required_fields", []), f"{location}.completion", errors)
        handoff = completion.get("handoff")
        if not isinstance(handoff, dict):
            errors.append(f"{location}.completion.handoff: must name the next stage and recommended Agent")
        else:
            require_fields(handoff, schema.get("completion_contract", {}).get("handoff", {}).get("required_fields", []), f"{location}.completion.handoff", errors)
            if handoff.get("recommended_agent") not in set(schema.get("completion_contract", {}).get("handoff", {}).get("recommended_agents", [])):
                errors.append(f"{location}.completion.handoff.recommended_agent: invalid")
            if not isinstance(handoff.get("next_stage"), str) or not handoff.get("next_stage", "").strip():
                errors.append(f"{location}.completion.handoff.next_stage: must be non-empty")
            if not isinstance(handoff.get("message"), str) or not handoff.get("message", "").strip():
                errors.append(f"{location}.completion.handoff.message: must be non-empty")


def validate_result(result: dict[str, Any], request: dict[str, Any], schema: dict[str, Any], location: str, errors: list[str]) -> None:
    require_fields(result, schema.get("result", {}).get("required_fields", []), location, errors)
    if result.get("schema_version") != 2 or result.get("task_id") != request.get("task_id"):
        errors.append(f"{location}: must be schema 2 and match REQUEST.task_id")
    author = result.get("created_by")
    if author not in {"agent:luna", "agent:terra"} or result.get("decision_author") != author or result.get("materialized_by") != author:
        errors.append(f"{location}: RESULT must be authored by Luna or Terra")
    if result.get("status") not in schema.get("enums", {}).get("result_status", []):
        errors.append(f"{location}.status: invalid result status")
    if not isinstance(result.get("revision", 1), int) or result.get("revision", 1) < 1:
        errors.append(f"{location}.revision: must be a positive integer")
    for field in ("outputs", "actions_performed", "actions_not_performed", "validation", "limitations"):
        if not isinstance(result.get(field), list):
            errors.append(f"{location}.{field}: must be a list")
    if request.get("task_type") == "screening-record":
        contract = schema.get("task_type_contracts", {}).get("screening-record", {})
        for field in contract.get("required_result_fields", []):
            if field not in result:
                errors.append(f"{location}.{field}: required for screening-record")
        if result.get("confidence") not in schema.get("enums", {}).get("decision_confidence", []):
            errors.append(f"{location}.confidence: invalid screening confidence")
        if not isinstance(result.get("evidence_refs"), list) or not result.get("evidence_refs"):
            errors.append(f"{location}.evidence_refs: screening-record requires a non-empty list")
        if not isinstance(result.get("feasibility"), dict):
            errors.append(f"{location}.feasibility: screening-record requires a mapping")
        if not isinstance(result.get("next_action"), str) or not result.get("next_action", "").strip():
            errors.append(f"{location}.next_action: screening-record requires a non-empty value")
    performed = set(string_items(result.get("actions_performed")))
    allowed = set(string_items(request.get("allowed_actions")))
    prohibited = set(string_items(request.get("prohibited_actions")))
    if performed - allowed:
        errors.append(f"{location}: actions not allowed by REQUEST.yaml: {', '.join(sorted(performed - allowed))}")
    if performed & prohibited:
        errors.append(f"{location}: prohibited actions performed: {', '.join(sorted(performed & prohibited))}")


def validate_decision(decision: dict[str, Any], request: dict[str, Any], result: dict[str, Any] | None, schema: dict[str, Any], location: str, errors: list[str]) -> None:
    require_fields(decision, schema.get("decision", {}).get("required_fields", []), location, errors)
    if decision.get("schema_version") != 2 or decision.get("task_id") != request.get("task_id"):
        errors.append(f"{location}: must be schema 2 and match REQUEST.task_id")
    author = decision.get("created_by")
    if author not in AGENTS or decision.get("decision_author") != author or decision.get("materialized_by") != author:
        errors.append(f"{location}: DECISION must be self-authored by a current Agent")
    if decision.get("status") not in schema.get("enums", {}).get("decision_status", []):
        errors.append(f"{location}.status: invalid decision status")
    if decision.get("result_ref") != "RESULT.yaml":
        errors.append(f"{location}.result_ref: must be RESULT.yaml")
    if result is not None and decision.get("result_revision") != result.get("revision", 1):
        errors.append(f"{location}.result_revision: must match RESULT revision")
    if decision.get("confidence") not in schema.get("enums", {}).get("decision_confidence", []):
        errors.append(f"{location}.confidence: invalid confidence")
    for field in ("conclusion", "next_action"):
        if not isinstance(decision.get(field), str) or not decision[field].strip():
            errors.append(f"{location}.{field}: must be non-empty")
    for field in ("evidence_refs", "risks"):
        if not isinstance(decision.get(field), list) or len(string_items(decision[field])) != len(decision[field]):
            errors.append(f"{location}.{field}: must be a list of strings")


def validate_approval(approval: dict[str, Any], request: dict[str, Any], schema: dict[str, Any], location: str, errors: list[str]) -> None:
    require_fields(approval, schema.get("approval", {}).get("required_fields", []), location, errors)
    if approval.get("schema_version") != 2 or approval.get("task_id") != request.get("task_id"):
        errors.append(f"{location}: must be schema 2 and match REQUEST.task_id")
    if approval.get("approved_by") != "user" or approval.get("decision_author") != "user" or approval.get("materialized_by") != "user":
        errors.append(f"{location}: APPROVAL must be user-authored")
    if approval.get("status") not in {"approved", "revoked"}:
        errors.append(f"{location}.status: invalid approval status")
    actions = set(string_items(approval.get("actions")))
    allowed = set(string_items(request.get("allowed_actions")))
    if not actions.issubset(allowed):
        errors.append(f"{location}.actions: exceeds REQUEST allowed actions")


def result_revision(result: dict[str, Any] | None) -> int:
    return result.get("revision", 1) if isinstance(result, dict) else 0


def derive_task_status(request: dict[str, Any], result: dict[str, Any] | None, decision: dict[str, Any] | None) -> str:
    if decision is not None and decision.get("result_revision") == result_revision(result):
        return DECISION_STATES.get(decision.get("status"), "invalid")
    if result is not None:
        return RESULT_STATES.get(result.get("status"), "invalid")
    return "ready"


def inspect_task_directory(task: Path, schema: dict[str, Any], permissions: dict[str, Any], *, now: Any = None) -> tuple[TaskRecord | None, list[str]]:
    errors: list[str] = []
    request_path, result_path = task / "REQUEST.yaml", task / "RESULT.yaml"
    if not request_path.exists():
        return None, [f"{request_path}: required file is missing"]
    request = load_yaml(request_path, errors)
    validate_request(request, schema, permissions, str(request_path), errors)
    result = load_yaml(result_path, errors) if result_path.exists() else None
    decision_path, approval_path = task / "DECISION.yaml", task / "APPROVAL.yaml"
    decision = load_yaml(decision_path, errors) if decision_path.exists() else None
    approval = load_yaml(approval_path, errors) if approval_path.exists() else None
    if (task / "REVIEW.yaml").exists():
        errors.append(f"{task / 'REVIEW.yaml'}: removed; use DECISION.yaml")
    if result is not None:
        validate_result(result, request, schema, str(result_path), errors)
    if decision is not None:
        validate_decision(decision, request, result, schema, str(decision_path), errors)
    if approval is not None:
        validate_approval(approval, request, schema, str(approval_path), errors)
    status = derive_task_status(request, result, decision)
    if status == "completed" and decision is None and request.get("task_type") not in {"screening-record", "deep-audit"}:
        errors.append(f"{task}: completed task requires DECISION.yaml")
    allowed = set(string_items(request.get("allowed_actions")))
    if allowed & PROTECTED_ACTIONS:
        if request.get("approval_required") is not True:
            errors.append(f"{request_path}.approval_required: must be true for protected actions")
        approved = set(string_items(approval.get("actions"))) if approval and approval.get("status") == "approved" else set()
        if not (allowed & PROTECTED_ACTIONS).issubset(approved):
            errors.append(f"{request_path}: protected actions require current user APPROVAL.yaml")
    return (None, errors) if errors else (TaskRecord(task, request, result, decision, approval, status), [])


def collect_task_records(root: Path, schema: dict[str, Any], permissions: dict[str, Any], errors: list[str]) -> list[TaskRecord]:
    records: list[TaskRecord] = []
    tasks = root / "agent-work" / "tasks"
    if not tasks.exists():
        return records
    for task in sorted(path for path in tasks.iterdir() if path.is_dir()):
        record, task_errors = inspect_task_directory(task, schema, permissions)
        errors.extend(task_errors)
        if record is not None:
            records.append(record)
    return records


def validate_task_directory(task: Path, schema: dict[str, Any], permissions: dict[str, Any]) -> list[str]:
    _, errors = inspect_task_directory(task, schema, permissions)
    return errors


def validate_transition(state_machine: dict[str, Any], source: str, target: str, section: str = "contribution_coordination") -> list[str]:
    transitions = state_machine.get(section, {}).get("transitions", {})
    if source not in transitions:
        return [f"unknown source state {source!r} in {section}"]
    return [] if target in transitions[source] else [f"forbidden transition: {source} -> {target}"]


def owners_for_path(path: str, permissions: dict[str, Any]) -> set[str]:
    owners: set[str] = set()
    for actor, data in permissions.get("actors", {}).items():
        role = data.get("role") if isinstance(data, dict) else None
        patterns = permissions.get("roles", {}).get(role, {}).get("owned_paths", [])
        if any(path_matches(path, pattern) for pattern in patterns):
            owners.add(actor)
    return owners


def validate_change_set(changes: list[dict[str, str]], permissions: dict[str, Any], **_: Any) -> list[str]:
    errors: list[str] = []
    by_path: dict[str, set[str]] = {}
    for change in changes:
        actor, path, action = change.get("actor", ""), change.get("path", "").lstrip("./"), change.get("action")
        by_path.setdefault(path, set()).add(actor)
        actor_data = permissions.get("actors", {}).get(actor)
        role = actor_data.get("role") if isinstance(actor_data, dict) else None
        if actor not in permissions.get("actors", {}):
            errors.append(f"actor {actor!r} is not authorized")
        elif action and action not in permissions.get("roles", {}).get(role, {}).get("allowed_actions", []):
            errors.append(f"actor {actor!r} cannot perform action {action!r}")
        owners = owners_for_path(path, permissions)
        if owners and actor not in owners:
            errors.append(f"actor {actor!r} cannot modify {path!r}; owned by {', '.join(sorted(owners))}")
        elif not owners and path not in permissions.get("shared_serialized_paths", []):
            errors.append(f"path {path!r} has no Agent ownership rule")
    for path, actors in by_path.items():
        if len(actors) > 1:
            errors.append(f"conflict: multiple actors modify {path!r}: {', '.join(sorted(actors))}")
    return errors


def configured_repository_state(root: Path) -> tuple[str, str]:
    return "Yanansn/zhaiyezi", "main"


def repository_state(root: Path) -> tuple[str, str]:
    repository, branch = configured_repository_state(root)
    try:
        branch = subprocess.run(["git", "-C", str(root), "branch", "--show-current"], check=True, capture_output=True, text=True).stdout.strip() or branch
        remote = subprocess.run(["git", "-C", str(root), "remote", "get-url", "origin"], check=True, capture_output=True, text=True).stdout.strip().removesuffix(".git")
        segments = [part for part in remote.replace(":", "/").split("/") if part]
        if len(segments) >= 2:
            repository = "/".join(segments[-2:])
    except (OSError, subprocess.CalledProcessError):
        pass
    return repository, branch


def validate(root: Path, *, now: Any = None) -> list[str]:
    errors: list[str] = []
    errors.extend(validate_repository_registry(root))
    schema, permissions, state_machine = protocol_documents(root, errors)
    errors.extend(validate_agent_roles(root, permissions))
    validate_protocol_documents(schema, permissions, state_machine, errors)
    collect_task_records(root, schema, permissions, errors)
    return errors


def parse_change(value: str, errors: list[str]) -> dict[str, str] | None:
    parts = value.split(":", 2)
    if len(parts) not in {2, 3} or not parts[0] or not parts[-1] or (len(parts) == 3 and not parts[1]):
        errors.append(f"invalid --change value {value!r}; use ACTOR:PATH or ACTOR:ACTION:PATH")
        return None
    change = {"actor": parts[0], "path": parts[-1]}
    if len(parts) == 3:
        change["action"] = parts[1]
    return change


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("root", nargs="?", type=Path, default=Path(__file__).resolve().parents[1])
    parser.add_argument("--change", action="append", default=[])
    args = parser.parse_args()
    root = args.root.resolve()
    errors = validate(root)
    schema, permissions, _ = protocol_documents(root, errors)
    changes = [parse_change(value, errors) for value in args.change]
    if args.change:
        errors.extend(validate_change_set([change for change in changes if change], permissions))
    for error in errors:
        print(f"ERROR {error}")
    if not errors:
        print(f"OK agent protocol: {root}")
    return 1 if errors else 0


if __name__ == "__main__":
    raise SystemExit(main())
