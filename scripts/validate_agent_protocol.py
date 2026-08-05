#!/usr/bin/env python3
"""Validate the Codex multi-agent protocol and legacy task artifacts."""

from __future__ import annotations

import argparse
from dataclasses import dataclass
from datetime import datetime, timezone
import re
import subprocess
import sys
from pathlib import Path
from typing import Any

try:
    import yaml
except ImportError as error:  # pragma: no cover - environment failure
    raise SystemExit("PyYAML is required to validate the Agent Protocol") from error


PROTOCOL_FILES = {
    "README.md",
    "roles.md",
    "lifecycle.md",
    "permissions.yaml",
    "task-schema.yaml",
    "state-machine.yaml",
    "conflict-resolution.md",
    "migration.md",
}
LEGACY_QUEUES = ("inbox", "active", "completed", "blocked")
TASK_ID_RE = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._-]*$")
REPOSITORY_RE = re.compile(r"^[^/\s]+/[^/\s]+$")
ISSUE_RE = re.compile(r"^[^/\s]+/[^#\s]+#[1-9][0-9]*$")
RESULT_STATES = {
    "active": "active",
    "review": "awaiting-review",
    "decision": "awaiting-decision",
    "blocked": "blocked",
    "failed": "failed",
}
REVIEW_STATES = {
    ("approved", "completed"): "completed",
    ("changes-requested", "changes-requested"): "changes-requested",
    ("rejected", "rejected"): "rejected",
}
DECISION_STATES = {
    "completed": "completed",
    "changes-requested": "changes-requested",
    "rejected": "rejected",
}
AGENT_ACTORS = {"agent:luna", "agent:terra", "agent:sol"}
LEGACY_ACTORS = {"chat", "codex", "user"}
CHAT_MATERIALIZATION_DENIED_PATHS = ("decisions/authorizations/**",)
TARGET_REPOSITORY_PHASES = {"evidence", "deep-audit", "implementation"}
UPSTREAM_ACTIONS = {
    "fetch_official_upstream",
    "modify_upstream_code",
    "upstream_write",
    "push_upstream_branch",
    "create_pull_request",
}


def path_matches(path: str, pattern: str) -> bool:
    """Match repository paths while keeping one `*` inside one path segment."""
    expression = re.escape(pattern.lstrip("./"))
    expression = expression.replace(r"\*\*", ".*").replace(r"\*", "[^/]*")
    return re.fullmatch(expression, path.lstrip("./")) is not None


@dataclass(frozen=True)
class TaskRecord:
    path: Path
    request: dict[str, Any]
    result: dict[str, Any] | None
    review: dict[str, Any] | None
    decision: dict[str, Any] | None
    approval: dict[str, Any] | None
    status: str


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
    repositories = root / "repositories"
    registry_path = repositories / "registry.yaml"
    discovery_path = repositories / "discovery.yaml"
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
    scan_roots = discovery.get("scan_roots")
    if not isinstance(scan_roots, list) or not scan_roots or any(
        not isinstance(item, str) or not item or item.startswith("/")
        for item in scan_roots
    ):
        errors.append(f"{discovery_path}.scan_roots: must be non-empty relative paths")
    return errors


def validate_agent_roles(root: Path) -> list[str]:
    errors: list[str] = []
    expected = {
        "luna": "discovery-and-decision",
        "terra": "analysis-and-execution",
        "sol": "escalation-review",
    }
    directory = root / "agents"
    for name, role in expected.items():
        path = directory / f"{name}.yaml"
        data = load_yaml(path, errors)
        if data.get("schema_version") != 1:
            errors.append(f"{path}.schema_version: must be 1")
        if data.get("agent") != name:
            errors.append(f"{path}.agent: must be {name}")
        if data.get("role") != role:
            errors.append(f"{path}.role: must be {role}")
        for field in ("responsibilities", "allowed_actions", "prohibited_actions"):
            if not isinstance(data.get(field), list) or not data[field]:
                errors.append(f"{path}.{field}: must be a non-empty list")
    sol = load_yaml(directory / "sol.yaml", [])
    prohibited = set(string_items(sol.get("prohibited_actions")))
    if not {"repository_modify", "commit_facts_repository", "push_facts_repository"}.issubset(prohibited):
        errors.append("agents/sol.yaml: Sol must remain escalation-only")
    return errors


def validate_target_repository_binding(
    request: dict[str, Any], schema: dict[str, Any], location: str, errors: list[str]
) -> None:
    task_type = request.get("task_type")
    binding = request.get("target_repository")
    if task_type == "deep-audit" and not isinstance(binding, dict):
        errors.append(f"{location}.target_repository: deep-audit requires a binding")
        return
    if task_type == "implementation" and not isinstance(binding, dict):
        errors.append(f"{location}.target_repository: implementation requires a binding")
        return
    if binding is None:
        return
    if not isinstance(binding, dict):
        errors.append(f"{location}.target_repository: must be a mapping")
        return
    contract = schema.get("target_repository_contract", {})
    for field in contract.get("required_fields", ["name", "phase"]):
        if field not in binding:
            errors.append(f"{location}.target_repository.{field}: required")
    name = binding.get("name")
    if not isinstance(name, str) or not REPOSITORY_RE.fullmatch(name):
        errors.append(f"{location}.target_repository.name: must use owner/name")
    elif name != request.get("repository"):
        errors.append(f"{location}.target_repository.name: must match repository")
    phase = binding.get("phase")
    if phase not in TARGET_REPOSITORY_PHASES:
        errors.append(f"{location}.target_repository.phase: invalid phase")
    elif task_type == "deep-audit" and phase != "deep-audit":
        errors.append(f"{location}.target_repository.phase: deep-audit requires deep-audit")
    elif task_type == "implementation" and phase != "implementation":
        errors.append(f"{location}.target_repository.phase: implementation requires implementation")
    if task_type == "implementation":
        fork = binding.get("fork")
        local = binding.get("local")
        if not isinstance(fork, dict) or not isinstance(fork.get("url"), str):
            errors.append(f"{location}.target_repository.fork.url: implementation requires fork")
        if not isinstance(local, dict) or not isinstance(local.get("path"), str):
            errors.append(f"{location}.target_repository.local.path: implementation requires local discovery result")
        if not isinstance(local, dict) or local.get("discovery") is not True:
            errors.append(f"{location}.target_repository.local.discovery: must be true")


def require_fields(
    value: dict[str, Any], required: list[str], location: str, errors: list[str]
) -> None:
    for field in required:
        if field not in value:
            errors.append(f"{location}: missing required field {field}")


def string_items(value: Any) -> list[str]:
    if not isinstance(value, list):
        return []
    return [item for item in value if isinstance(item, str)]


def protocol_documents(
    root: Path, errors: list[str]
) -> tuple[dict[str, Any], dict[str, Any], dict[str, Any]]:
    protocol = root / "agent-protocol"
    if not protocol.is_dir():
        errors.append(f"{protocol}: missing protocol directory")
        return {}, {}, {}
    present = {path.name for path in protocol.iterdir() if path.is_file()}
    missing = sorted(PROTOCOL_FILES - present)
    if missing:
        errors.append(f"{protocol}: missing files: {', '.join(missing)}")
    return (
        load_yaml(protocol / "task-schema.yaml", errors),
        load_yaml(protocol / "permissions.yaml", errors),
        load_yaml(protocol / "state-machine.yaml", errors),
    )


def parse_time(value: Any, location: str, errors: list[str]) -> datetime | None:
    if value is None:
        return None
    if not isinstance(value, str):
        errors.append(f"{location}: must be an ISO-8601 string or null")
        return None
    try:
        parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError:
        errors.append(f"{location}: invalid ISO-8601 timestamp {value!r}")
        return None
    if parsed.tzinfo is None:
        parsed = parsed.replace(tzinfo=timezone.utc)
    return parsed.astimezone(timezone.utc)


def validate_protocol_documents(
    schema: dict[str, Any],
    permissions: dict[str, Any],
    state_machine: dict[str, Any],
    errors: list[str],
) -> None:
    if schema.get("schema_version") != 4:
        errors.append("agent-protocol/task-schema.yaml: schema_version must be 4")
    if permissions.get("schema_version") != 3:
        errors.append("agent-protocol/permissions.yaml: schema_version must be 3")
    if state_machine.get("schema_version") != 2:
        errors.append("agent-protocol/state-machine.yaml: schema_version must be 2")
    if schema.get("task_directory") != "agent-work/tasks/<task-id>":
        errors.append("agent-protocol/task-schema.yaml: task_directory must be fixed")

    required_states = {
        "ready", "active", "awaiting-decision", "awaiting-review", "changes-requested",
        "blocked", "failed", "rejected", "completed",
    }
    queue = state_machine.get("queue_artifact_state", {})
    if set(queue.get("states", [])) != required_states:
        errors.append("agent-protocol/state-machine.yaml: queue states are incomplete")
    coordination = state_machine.get("contribution_coordination", {})
    expected_lifecycle = {
        "candidate": ["evidence"],
        "evidence": ["analysis"],
        "analysis": ["decision"],
        "decision": ["implementation"],
        "implementation": ["pull-request"],
        "pull-request": [],
    }
    if coordination.get("transitions") != expected_lifecycle:
        errors.append("agent-protocol/state-machine.yaml: multi-agent lifecycle is invalid")

    deep_audit_contract = schema.get("task_type_contracts", {}).get("deep-audit", {})
    if "deep-audit" not in schema.get("enums", {}).get("task_type", []):
        errors.append("agent-protocol/task-schema.yaml: deep-audit task type is missing")
    if deep_audit_contract.get("required_request_fields") != ["evidence_refs"]:
        errors.append(
            "agent-protocol/task-schema.yaml: deep-audit must require evidence_refs"
        )
    target_contract = schema.get("target_repository_contract", {})
    if target_contract.get("phases") != ["evidence", "deep-audit", "implementation"]:
        errors.append("agent-protocol/task-schema.yaml: target repository phases are invalid")

    catalog = permissions.get("action_catalog")
    standing = set(permissions.get("standing_authorizable_actions", []))
    always = set(permissions.get("always_user_confirmation_actions", []))
    required_always = {
        "materialize_user_artifact",
        "modify_registry", "initialize_formal_issue", "fetch_official_upstream",
        "modify_upstream_code", "upstream_write", "push_upstream_branch",
        "create_issue", "comment_issue", "assign_issue", "add_labels",
        "create_pull_request",
    }
    if not isinstance(catalog, dict):
        errors.append("agent-protocol/permissions.yaml.action_catalog: must be a mapping")
        catalog = {}
    if standing != {
        "commit_facts_repository", "push_facts_repository", "materialize_chat_artifact"
    }:
        errors.append(
            "agent-protocol/permissions.yaml.standing_authorizable_actions: "
            "must contain only facts Commit/Push and legacy Chat artifact materialization"
        )
    if not required_always.issubset(always):
        errors.append(
            "agent-protocol/permissions.yaml.always_user_confirmation_actions: "
            "missing protected actions"
        )
    if standing & always:
        errors.append("agent-protocol/permissions.yaml: standing and always actions overlap")
    unknown = (standing | always) - set(catalog)
    if unknown:
        errors.append(
            "agent-protocol/permissions.yaml: unknown protected actions: "
            + ", ".join(sorted(unknown))
        )
    materialization = permissions.get("materialization", {}).get("codex", {})
    chat_rule = materialization.get("materialize_chat_artifact", {})
    required_chat_paths = {
        "agent-work/tasks/*/REQUEST.yaml",
        "agent-work/tasks/*/REVIEW.yaml",
        "decisions/**",
    }
    if not required_chat_paths.issubset(set(chat_rule.get("paths", []))):
        errors.append(
            "agent-protocol/permissions.yaml.materialization: missing bounded Chat paths"
        )
    if "decisions/authorizations/**" not in chat_rule.get("excluded_paths", []):
        errors.append(
            "agent-protocol/permissions.yaml.materialization: user authorizations "
            "must be excluded from Chat materialization"
        )
    if set(schema.get("compatibility", {}).get("current_agents", [])) != AGENT_ACTORS:
        errors.append("agent-protocol/task-schema.yaml: current agents are invalid")


def validate_provenance(
    value: dict[str, Any],
    expected_author: str,
    allowed_materializers: set[str],
    schema: dict[str, Any],
    location: str,
    errors: list[str],
) -> None:
    if value.get("decision_author") != expected_author:
        errors.append(
            f"{location}.decision_author: must be {expected_author}"
        )
    materializer = value.get("materialized_by")
    if materializer not in allowed_materializers:
        errors.append(
            f"{location}.materialized_by: must be one of "
            + ", ".join(sorted(allowed_materializers))
        )
        return

    materialization = value.get("materialization")
    if materializer == expected_author:
        if materialization is not None:
            errors.append(
                f"{location}.materialization: must be absent when author materializes directly"
            )
        return

    if not isinstance(materialization, dict):
        errors.append(
            f"{location}.materialization: required for delegated materialization"
        )
        return
    contract = schema.get("materialization_contract", {})
    require_fields(
        materialization,
        contract.get("required_fields", []),
        f"{location}.materialization",
        errors,
    )
    if materialization.get("authority") not in contract.get("authority", []):
        errors.append(
            f"{location}.materialization.authority: must be user-instruction"
        )
    if materialization.get("scope") not in contract.get("scope", []):
        errors.append(f"{location}.materialization.scope: must be bounded")
    summary = materialization.get("source_summary")
    if not isinstance(summary, str) or not summary.strip():
        errors.append(
            f"{location}.materialization.source_summary: must be a non-empty string"
        )


def is_legacy_artifact(value: dict[str, Any]) -> bool:
    """Version 1 artifacts retain the former Chat/Codex ownership contract."""
    return value.get("schema_version") == 1


def validate_agent_provenance(
    value: dict[str, Any],
    location: str,
    errors: list[str],
    *,
    allowed_authors: set[str],
) -> None:
    author = value.get("decision_author")
    creator = value.get("created_by")
    materializer = value.get("materialized_by")
    if author not in allowed_authors:
        errors.append(f"{location}.decision_author: must be an authorized agent or user")
    if creator != author:
        errors.append(f"{location}.created_by: must match decision_author")
    if materializer not in AGENT_ACTORS | {"user"}:
        errors.append(f"{location}.materialized_by: must be an agent or user")
    if materializer != author:
        errors.append(
            f"{location}.materialized_by: current multi-agent artifacts must be self-materialized"
        )
    if value.get("materialization") is not None:
        errors.append(f"{location}.materialization: is legacy-only and must be absent")


def validate_request(
    request: dict[str, Any],
    schema: dict[str, Any],
    permissions: dict[str, Any],
    location: str,
    errors: list[str],
) -> None:
    require_fields(
        request, schema.get("request", {}).get("required_fields", []), location, errors
    )
    legacy = is_legacy_artifact(request)
    if request.get("schema_version") not in {1, 2}:
        errors.append(f"{location}.schema_version: must be 1 (legacy) or 2")
    task_id = request.get("task_id")
    if not isinstance(task_id, str) or not TASK_ID_RE.fullmatch(task_id):
        errors.append(f"{location}.task_id: invalid task identifier")
    enums = schema.get("enums", {})
    if request.get("task_type") not in enums.get("task_type", []):
        errors.append(f"{location}.task_type: unknown value {request.get('task_type')!r}")
    if legacy:
        if request.get("created_by") != "chat":
            errors.append(f"{location}.created_by: legacy REQUEST.yaml owner must be chat")
        validate_provenance(
            request, "chat", {"chat", "codex"}, schema, location, errors
        )
        allowed_assignees = enums.get("legacy_assigned_agent", [])
    else:
        validate_agent_provenance(
            request, location, errors, allowed_authors=AGENT_ACTORS | {"user"}
        )
        if not isinstance(request.get("approval_required"), bool):
            errors.append(f"{location}.approval_required: must be boolean")
        allowed_assignees = enums.get("assigned_agent", [])
    if request.get("assigned_agent") not in allowed_assignees:
        errors.append(f"{location}.assigned_agent: invalid Agent")
    if request.get("status") != "ready":
        errors.append(f"{location}.status: new REQUEST.yaml status must be ready")
    repository = request.get("repository")
    if not isinstance(repository, str) or not REPOSITORY_RE.fullmatch(repository):
        errors.append(f"{location}.repository: must use owner/name")
    issue = request.get("issue")
    if issue is not None and (not isinstance(issue, str) or not ISSUE_RE.fullmatch(issue)):
        errors.append(f"{location}.issue: must be null or owner/repository#number")
    if isinstance(issue, str) and not issue.startswith(f"{repository}#"):
        errors.append(f"{location}.issue: repository must match REQUEST.repository")
    for field in (
        "input_refs", "allowed_actions", "prohibited_actions", "expected_outputs"
    ):
        if not isinstance(request.get(field), list):
            errors.append(f"{location}.{field}: must be a list")
        elif len(string_items(request[field])) != len(request[field]):
            errors.append(f"{location}.{field}: every item must be a string")
    if request.get("task_type") == "deep-audit":
        evidence_refs = request.get("evidence_refs")
        if not isinstance(evidence_refs, list) or not evidence_refs:
            errors.append(
                f"{location}.evidence_refs: deep-audit requires a non-empty list"
            )
        elif len(string_items(evidence_refs)) != len(evidence_refs):
            errors.append(
                f"{location}.evidence_refs: every item must be a string"
            )
    validate_target_repository_binding(request, schema, location, errors)
    if not isinstance(request.get("goal"), str) or not request.get("goal", "").strip():
        errors.append(f"{location}.goal: must be a non-empty string")
    completion = request.get("completion")
    if not isinstance(completion, dict):
        errors.append(f"{location}.completion: must be a mapping")
    else:
        require_fields(
            completion,
            schema.get("completion_contract", {}).get("required_fields", []),
            f"{location}.completion",
            errors,
        )

    priority = request.get("priority", "normal")
    if priority not in enums.get("priority", []):
        errors.append(f"{location}.priority: invalid value {priority!r}")
    if "created_at" in request:
        parse_time(request.get("created_at"), f"{location}.created_at", errors)

    catalog = set(permissions.get("action_catalog", {}))
    allowed = string_items(request.get("allowed_actions"))
    prohibited = string_items(request.get("prohibited_actions"))
    if isinstance(request.get("allowed_actions"), list) and isinstance(
        request.get("prohibited_actions"), list
    ):
        unknown = sorted((set(allowed) | set(prohibited)) - catalog)
        if unknown:
            errors.append(f"{location}: unknown actions: {', '.join(unknown)}")
        overlap = sorted(set(allowed) & set(prohibited))
        if overlap:
            errors.append(
                f"{location}: actions are both allowed and prohibited: "
                + ", ".join(overlap)
            )
    if request.get("task_type") == "deep-audit":
        forbidden = set(
            schema.get("task_type_contracts", {})
            .get("deep-audit", {})
            .get("prohibited_allowed_actions", [])
        )
        unauthorized = sorted(forbidden & set(allowed))
        if unauthorized:
            errors.append(
                f"{location}: deep-audit cannot allow protected action(s): "
                + ", ".join(unauthorized)
            )


def validate_result(
    result: dict[str, Any],
    request: dict[str, Any],
    schema: dict[str, Any],
    location: str,
    errors: list[str],
) -> None:
    require_fields(
        result, schema.get("result", {}).get("required_fields", []), location, errors
    )
    legacy = is_legacy_artifact(request)
    if result.get("schema_version") != request.get("schema_version"):
        errors.append(f"{location}.schema_version: must match REQUEST.yaml")
    if result.get("task_id") != request.get("task_id"):
        errors.append(f"{location}.task_id: must match REQUEST.yaml")
    if legacy:
        if result.get("created_by") != "codex":
            errors.append(f"{location}.created_by: legacy RESULT.yaml owner must be codex")
        validate_provenance(result, "codex", {"codex"}, schema, location, errors)
        allowed_statuses = schema.get("enums", {}).get("legacy_result_status", [])
    else:
        validate_agent_provenance(
            result, location, errors, allowed_authors={"agent:luna", "agent:terra"}
        )
        allowed_statuses = schema.get("enums", {}).get("result_status", [])
    if result.get("status") not in allowed_statuses:
        errors.append(f"{location}.status: invalid result status")
    revision = result.get("revision", 1)
    if not isinstance(revision, int) or isinstance(revision, bool) or revision < 1:
        errors.append(f"{location}.revision: must be a positive integer")
    for field in (
        "outputs", "actions_performed", "actions_not_performed", "validation",
        "limitations",
    ):
        if not isinstance(result.get(field), list):
            errors.append(f"{location}.{field}: must be a list")
        elif len(string_items(result[field])) != len(result[field]):
            errors.append(f"{location}.{field}: every item must be a string")
    if result.get("status") == "blocked" and not result.get("limitations"):
        errors.append(f"{location}.limitations: blocked result requires a blocker")


def validate_review(
    review: dict[str, Any],
    request: dict[str, Any],
    schema: dict[str, Any],
    location: str,
    errors: list[str],
) -> None:
    require_fields(
        review, schema.get("review", {}).get("required_fields", []), location, errors
    )
    if review.get("schema_version") != 1:
        errors.append(f"{location}.schema_version: must be 1")
    if review.get("task_id") != request.get("task_id"):
        errors.append(f"{location}.task_id: must match REQUEST.yaml")
    if review.get("created_by") != "chat":
        errors.append(f"{location}.created_by: REVIEW.yaml owner must be chat")
    validate_provenance(
        review, "chat", {"chat", "codex"}, schema, location, errors
    )
    for forbidden_field in (
        "allowed_actions", "prohibited_actions", "expected_outputs", "permissions"
    ):
        if forbidden_field in review:
            errors.append(
                f"{location}.{forbidden_field}: REVIEW.yaml cannot modify REQUEST permissions"
            )
    status = review.get("status")
    decision = review.get("decision")
    if status not in schema.get("enums", {}).get("review_status", []):
        errors.append(f"{location}.status: invalid review status")
    if decision not in schema.get("enums", {}).get("review_decision", []):
        errors.append(f"{location}.decision: invalid review decision")
    if (decision, status) not in REVIEW_STATES:
        errors.append(f"{location}: decision and status do not form a valid Review state")
    revision = review.get("result_revision")
    if not isinstance(revision, int) or isinstance(revision, bool) or revision < 1:
        errors.append(f"{location}.result_revision: must be a positive integer")
    for field in ("findings", "next_actions"):
        if not isinstance(review.get(field), list):
            errors.append(f"{location}.{field}: must be a list")


def validate_decision(
    decision: dict[str, Any],
    request: dict[str, Any],
    result: dict[str, Any] | None,
    schema: dict[str, Any],
    location: str,
    errors: list[str],
) -> None:
    require_fields(
        decision, schema.get("decision", {}).get("required_fields", []), location, errors
    )
    if decision.get("schema_version") != 2:
        errors.append(f"{location}.schema_version: must be 2")
    if decision.get("task_id") != request.get("task_id"):
        errors.append(f"{location}.task_id: must match REQUEST.yaml")
    validate_agent_provenance(
        decision, location, errors, allowed_authors=AGENT_ACTORS
    )
    if decision.get("status") not in schema.get("enums", {}).get("decision_status", []):
        errors.append(f"{location}.status: invalid decision status")
    if decision.get("result_ref") != "RESULT.yaml":
        errors.append(f"{location}.result_ref: must be RESULT.yaml")
    revision = decision.get("result_revision")
    if not isinstance(revision, int) or isinstance(revision, bool) or revision < 1:
        errors.append(f"{location}.result_revision: must be a positive integer")
    if result is None:
        errors.append(f"{location}: requires RESULT.yaml")
    elif revision != result_revision(result):
        errors.append(f"{location}.result_revision: must match current RESULT revision")
    if decision.get("confidence") not in schema.get("enums", {}).get("decision_confidence", []):
        errors.append(f"{location}.confidence: invalid confidence")
    if not isinstance(decision.get("conclusion"), str) or not decision["conclusion"].strip():
        errors.append(f"{location}.conclusion: must be a non-empty string")
    if not isinstance(decision.get("next_action"), str) or not decision["next_action"].strip():
        errors.append(f"{location}.next_action: must be a non-empty string")
    for field in ("evidence_refs", "risks"):
        if not isinstance(decision.get(field), list) or len(string_items(decision[field])) != len(decision[field]):
            errors.append(f"{location}.{field}: must be a list of strings")


def validate_approval(
    approval: dict[str, Any],
    request: dict[str, Any],
    schema: dict[str, Any],
    location: str,
    errors: list[str],
) -> None:
    require_fields(
        approval,
        schema.get("approval", {}).get("required_fields", []),
        location,
        errors,
    )
    if approval.get("schema_version") != 1:
        errors.append(f"{location}.schema_version: must be 1")
    if approval.get("task_id") != request.get("task_id"):
        errors.append(f"{location}.task_id: must match REQUEST.yaml")
    if approval.get("approved_by") != "user":
        errors.append(f"{location}.approved_by: APPROVAL.yaml owner must be user")
    validate_provenance(
        approval, "user", {"user", "codex"}, schema, location, errors
    )
    if approval.get("status") not in schema.get("enums", {}).get(
        "approval_status", []
    ):
        errors.append(f"{location}.status: invalid approval status")
    if not isinstance(approval.get("actions"), list):
        errors.append(f"{location}.actions: must be a list")
    elif len(string_items(approval["actions"])) != len(approval["actions"]):
        errors.append(f"{location}.actions: every item must be a string")
    if not isinstance(approval.get("scope"), str) or not approval.get("scope", "").strip():
        errors.append(f"{location}.scope: must be a non-empty string")


def result_revision(result: dict[str, Any] | None) -> int:
    return result.get("revision", 1) if result else 0


def derive_task_status(
    request: dict[str, Any],
    result: dict[str, Any] | None,
    review: dict[str, Any] | None,
    decision: dict[str, Any] | None,
    location: str,
    errors: list[str],
) -> str:
    if not is_legacy_artifact(request) and decision is not None:
        if decision.get("result_revision") == result_revision(result):
            return DECISION_STATES.get(decision.get("status"), "invalid")
    if review is not None:
        current_revision = result_revision(result)
        reviewed_revision = review.get("result_revision")
        if isinstance(reviewed_revision, int) and reviewed_revision > current_revision:
            errors.append(f"{location}/REVIEW.yaml.result_revision: exceeds RESULT revision")
        if reviewed_revision == current_revision:
            return REVIEW_STATES.get(
                (review.get("decision"), review.get("status")), "invalid"
            )
        if isinstance(reviewed_revision, int) and reviewed_revision < current_revision:
            if review.get("decision") != "changes-requested":
                errors.append(
                    f"{location}/RESULT.yaml.revision: cannot supersede an approved or rejected Review"
                )
            elif result and result.get("supersedes_review") != "REVIEW.yaml":
                errors.append(
                    f"{location}/RESULT.yaml.supersedes_review: must name REVIEW.yaml"
                )
    if result is not None:
        return RESULT_STATES.get(result.get("status"), "invalid")
    return "ready" if request.get("status") == "ready" else "invalid"


def validate_standing_authorization(
    authorization: dict[str, Any],
    path: Path,
    schema: dict[str, Any],
    permissions: dict[str, Any],
    *,
    template: bool,
    now: datetime | None = None,
) -> list[str]:
    errors: list[str] = []
    location = str(path)
    contract = schema.get("standing_authorization", {})
    require_fields(
        authorization, contract.get("required_fields", []), location, errors
    )
    if authorization.get("schema_version") != 1:
        errors.append(f"{location}.schema_version: must be 1")
    if authorization.get("kind") != "standing-authorization":
        errors.append(f"{location}.kind: must be standing-authorization")
    auth_id = authorization.get("authorization_id")
    if not isinstance(auth_id, str) or not TASK_ID_RE.fullmatch(auth_id):
        errors.append(f"{location}.authorization_id: invalid identifier")
    if authorization.get("approved_by") != "user":
        errors.append(f"{location}.approved_by: must be user")
    validate_provenance(
        authorization, "user", {"user", "codex"}, schema, location, errors
    )
    status = authorization.get("status")
    if status not in schema.get("enums", {}).get(
        "standing_authorization_status", []
    ):
        errors.append(f"{location}.status: must be approved or revoked")

    standing = permissions.get("standing_authorization", {})
    if authorization.get("repository") != standing.get("repository"):
        errors.append(
            f"{location}.repository: must be {standing.get('repository')!r}"
        )
    if authorization.get("branch") != standing.get("branch"):
        errors.append(f"{location}.branch: must be {standing.get('branch')!r}")
    effective = parse_time(
        authorization.get("effective_from"), f"{location}.effective_from", errors
    )
    expires = parse_time(
        authorization.get("expires_at"), f"{location}.expires_at", errors
    )
    if effective and expires and expires <= effective:
        errors.append(f"{location}.expires_at: must be after effective_from")

    grants = authorization.get("grants")
    standing_actions = set(permissions.get("standing_authorizable_actions", []))
    allowlists = standing.get("actor_path_allowlist", {})
    if not isinstance(grants, dict) or not grants:
        errors.append(f"{location}.grants: must be a non-empty mapping")
    else:
        for actor, grant in grants.items():
            grant_location = f"{location}.grants.{actor}"
            if actor not in {"chat", "codex"}:
                errors.append(f"{grant_location}: unsupported actor")
                continue
            if not isinstance(grant, dict):
                errors.append(f"{grant_location}: must be a mapping")
                continue
            actions = grant.get("actions")
            paths = grant.get("paths")
            if not isinstance(actions, list) or not actions:
                errors.append(f"{grant_location}.actions: must be a non-empty list")
                actions = []
            elif len(string_items(actions)) != len(actions):
                errors.append(f"{grant_location}.actions: every item must be a string")
            if not isinstance(paths, list) or not paths:
                errors.append(f"{grant_location}.paths: must be a non-empty list")
                paths = []
            elif len(string_items(paths)) != len(paths):
                errors.append(f"{grant_location}.paths: every item must be a string")
            actions = string_items(actions)
            paths = string_items(paths)
            forbidden_actions = sorted(set(actions) - standing_actions)
            if forbidden_actions:
                errors.append(
                    f"{grant_location}.actions: cannot grant "
                    + ", ".join(forbidden_actions)
                )
            forbidden_paths = sorted(set(paths) - set(allowlists.get(actor, [])))
            if forbidden_paths:
                errors.append(
                    f"{grant_location}.paths: outside actor allowlist: "
                    + ", ".join(forbidden_paths)
                )

    always = set(permissions.get("always_user_confirmation_actions", []))
    recorded_always = authorization.get("always_requires_new_approval")
    if not isinstance(recorded_always, list) or not always.issubset(
        set(recorded_always)
    ):
        errors.append(
            f"{location}.always_requires_new_approval: missing protected actions"
        )
    revocation = authorization.get("revocation")
    if not isinstance(revocation, dict) or revocation.get("supported") is not True:
        errors.append(f"{location}.revocation.supported: must be true")
    elif status == "revoked" and not revocation.get("revoked_at"):
        errors.append(f"{location}.revocation.revoked_at: required when revoked")
    elif revocation.get("revoked_at") is not None:
        parse_time(
            revocation.get("revoked_at"),
            f"{location}.revocation.revoked_at",
            errors,
        )

    if template:
        if authorization.get("template_only") is not True:
            errors.append(f"{location}.template_only: example must be true")
    elif authorization.get("template_only") is True:
        errors.append(f"{location}.template_only: template cannot be an actual authorization")

    current = now or datetime.now(timezone.utc)
    if not template and status == "approved" and effective and current < effective:
        errors.append(f"{location}.effective_from: authorization is not effective yet")
    return errors


def standing_authorizes(
    authorization: dict[str, Any],
    actor: str,
    action: str,
    paths: list[str],
    repository: str,
    branch: str,
    *,
    now: datetime | None = None,
) -> bool:
    current = now or datetime.now(timezone.utc)
    if action == "materialize_chat_artifact" and any(
        path_matches(path, pattern)
        for path in paths
        for pattern in CHAT_MATERIALIZATION_DENIED_PATHS
    ):
        return False
    if authorization.get("template_only") is True:
        return False
    if authorization.get("status") != "approved":
        return False
    if authorization.get("repository") != repository:
        return False
    if authorization.get("branch") != branch:
        return False
    effective = parse_time(authorization.get("effective_from"), "effective_from", [])
    expires = parse_time(authorization.get("expires_at"), "expires_at", [])
    if effective is None or current < effective:
        return False
    if expires is not None and current >= expires:
        return False
    revocation = authorization.get("revocation", {})
    if not isinstance(revocation, dict):
        return False
    if revocation.get("revoked_at") is not None:
        return False
    grants = authorization.get("grants")
    if not isinstance(grants, dict):
        return False
    grant = grants.get(actor)
    if not isinstance(grant, dict):
        return False
    if action not in string_items(grant.get("actions")):
        return False
    patterns = string_items(grant.get("paths"))
    return bool(paths) and all(
        any(path_matches(path, pattern) for pattern in patterns)
        for path in paths
    )


def load_standing_authorizations(
    root: Path,
    schema: dict[str, Any],
    permissions: dict[str, Any],
    errors: list[str],
    *,
    now: datetime | None = None,
) -> list[dict[str, Any]]:
    directory = root / "decisions" / "authorizations"
    if not directory.is_dir():
        return []
    authorizations: list[dict[str, Any]] = []
    for path in sorted(directory.glob("*.yaml")):
        authorization = load_yaml(path, errors)
        errors.extend(
            validate_standing_authorization(
                authorization, path, schema, permissions, template=False, now=now
            )
        )
        authorizations.append(authorization)
    return authorizations


def task_action_authorized(
    action: str,
    request: dict[str, Any],
    approval: dict[str, Any] | None,
    standing_authorizations: list[dict[str, Any]],
    permissions: dict[str, Any],
    repository: str,
    branch: str,
    *,
    now: datetime | None = None,
) -> bool:
    if approval and approval.get("status") == "approved":
        if action in string_items(approval.get("actions")):
            return True
    if action not in permissions.get("standing_authorizable_actions", []):
        return False
    actor = request.get("assigned_agent")
    paths = string_items(request.get("expected_outputs"))
    return any(
        standing_authorizes(
            authorization,
            actor,
            action,
            paths,
            repository,
            branch,
            now=now,
        )
        for authorization in standing_authorizations
    )


def inspect_task_directory(
    task: Path,
    schema: dict[str, Any],
    permissions: dict[str, Any],
    standing_authorizations: list[dict[str, Any]] | None = None,
    *,
    repository: str = "Yanansn/zhaiyezi",
    branch: str = "main",
    now: datetime | None = None,
) -> tuple[TaskRecord | None, list[str]]:
    errors: list[str] = []
    request_path = task / "REQUEST.yaml"
    if not request_path.is_file():
        return None, [f"{request_path}: required file is missing"]
    request = load_yaml(request_path, errors)
    validate_request(request, schema, permissions, str(request_path), errors)
    if task.name != request.get("task_id"):
        errors.append(
            f"{request_path}.task_id: {request.get('task_id')!r} must match directory {task.name!r}"
        )

    artifacts: dict[str, dict[str, Any] | None] = {
        "RESULT.yaml": None,
        "REVIEW.yaml": None,
        "DECISION.yaml": None,
        "APPROVAL.yaml": None,
    }
    for filename in artifacts:
        path = task / filename
        if path.is_file():
            artifacts[filename] = load_yaml(path, errors)
    result = artifacts["RESULT.yaml"]
    review = artifacts["REVIEW.yaml"]
    decision = artifacts["DECISION.yaml"]
    approval = artifacts["APPROVAL.yaml"]
    if result is not None:
        validate_result(result, request, schema, str(task / "RESULT.yaml"), errors)
        if not (task / "REPORT.md").is_file():
            errors.append(f"{task / 'REPORT.md'}: required when RESULT.yaml exists")
    if review is not None:
        validate_review(review, request, schema, str(task / "REVIEW.yaml"), errors)
        if result is None:
            errors.append(f"{task / 'REVIEW.yaml'}: requires RESULT.yaml")
        if not is_legacy_artifact(request):
            errors.append(f"{task / 'REVIEW.yaml'}: REVIEW.yaml is legacy-only; use DECISION.yaml")
    if decision is not None:
        if is_legacy_artifact(request):
            errors.append(f"{task / 'DECISION.yaml'}: DECISION.yaml requires a schema_version 2 REQUEST")
        validate_decision(decision, request, result, schema, str(task / "DECISION.yaml"), errors)
    if approval is not None:
        validate_approval(approval, request, schema, str(task / "APPROVAL.yaml"), errors)

    status = derive_task_status(request, result, review, decision, str(task), errors)
    if status == "completed" and ((is_legacy_artifact(request) and review is None) or (not is_legacy_artifact(request) and decision is None)):
        errors.append(f"{task}: completed status requires its current decision artifact")

    catalog = set(permissions.get("action_catalog", {}))
    allowed = set(string_items(request.get("allowed_actions")))
    prohibited = set(string_items(request.get("prohibited_actions")))
    if result is not None:
        performed = set(string_items(result.get("actions_performed")))
        unknown = sorted(performed - catalog)
        unauthorized = sorted(performed - allowed)
        forbidden = sorted(performed & prohibited)
        if unknown:
            errors.append(f"{task / 'RESULT.yaml'}: unknown actions: {', '.join(unknown)}")
        if unauthorized:
            errors.append(
                f"{task / 'RESULT.yaml'}: actions not allowed by REQUEST.yaml: "
                + ", ".join(unauthorized)
            )
        if forbidden:
            errors.append(
                f"{task / 'RESULT.yaml'}: prohibited actions performed: "
                + ", ".join(forbidden)
            )
    if approval is not None:
        approved_actions = set(string_items(approval.get("actions")))
        unknown = sorted(approved_actions - catalog)
        out_of_scope = sorted(approved_actions - allowed)
        if unknown:
            errors.append(f"{task / 'APPROVAL.yaml'}: unknown actions: {', '.join(unknown)}")
        if out_of_scope:
            errors.append(
                f"{task / 'APPROVAL.yaml'}: actions exceed REQUEST.yaml: "
                + ", ".join(out_of_scope)
            )

    authorizations = standing_authorizations or []
    delegated_chat_artifacts = [(request, "REQUEST.yaml")]
    if review is not None:
        delegated_chat_artifacts.append((review, "REVIEW.yaml"))
    for artifact, filename in delegated_chat_artifacts:
        if artifact.get("materialized_by") != "codex":
            continue
        artifact_path = f"agent-work/tasks/{task.name}/{filename}"
        if not any(
            standing_authorizes(
                authorization,
                "codex",
                "materialize_chat_artifact",
                [artifact_path],
                repository,
                branch,
                now=now,
            )
            for authorization in authorizations
        ):
            errors.append(
                f"{task / filename}.materialized_by: Codex materialization requires "
                "a valid standing authorization for this Chat-owned path"
            )
    approval_actions = set(permissions.get("approval_required_actions", []))
    if is_legacy_artifact(request):
        approval_actions.update({"repository_modify", "commit_facts_repository"})
    for action in sorted(allowed & approval_actions):
        if not is_legacy_artifact(request) and action in {"create_pull_request", "push_upstream_branch", "upstream_write", "comment_issue", "create_issue", "assign_issue", "add_labels"} and request.get("approval_required") is not True:
            errors.append(f"{request_path}.approval_required: must be true for {action}")
            continue
        if not task_action_authorized(
            action,
            request,
            approval,
            authorizations,
            permissions,
            repository,
            branch,
            now=now,
        ):
            errors.append(
                f"{request_path}.allowed_actions: {action} requires current task approval "
                "or a valid standing authorization"
            )

    record = TaskRecord(task, request, result, review, decision, approval, status)
    return (None, errors) if errors else (record, [])


def validate_task_directory(
    task: Path,
    schema: dict[str, Any],
    permissions: dict[str, Any],
    standing_authorizations: list[dict[str, Any]] | None = None,
    **kwargs: Any,
) -> list[str]:
    _, errors = inspect_task_directory(
        task, schema, permissions, standing_authorizations, **kwargs
    )
    return errors


def validate_examples(
    root: Path,
    schema: dict[str, Any],
    permissions: dict[str, Any],
) -> list[str]:
    errors: list[str] = []
    example = root / "agent-protocol" / "examples" / "example-task" / "REQUEST.yaml"
    request = load_yaml(example, errors)
    validate_request(request, schema, permissions, str(example), errors)
    if request.get("task_id") != example.parent.name:
        errors.append(f"{example}.task_id: must match example directory")
    standing_path = root / "agent-protocol" / "examples" / "standing-authorization.yaml"
    standing = load_yaml(standing_path, errors)
    errors.extend(
        validate_standing_authorization(
            standing, standing_path, schema, permissions, template=True
        )
    )
    return errors


def legacy_queue_errors(root: Path) -> list[str]:
    errors: list[str] = []
    for name in LEGACY_QUEUES:
        queue = root / "agent-work" / name
        if not queue.is_dir():
            continue
        for task in sorted(path for path in queue.iterdir() if path.is_dir()):
            if (task / "REQUEST.yaml").is_file():
                errors.append(
                    f"{task}: legacy queue task detected; migrate without moving owned "
                    f"artifacts to agent-work/tasks/{task.name}/"
                )
    return errors


def collect_task_records(
    root: Path,
    schema: dict[str, Any],
    permissions: dict[str, Any],
    authorizations: list[dict[str, Any]],
    errors: list[str],
    *,
    repository: str = "Yanansn/zhaiyezi",
    branch: str = "main",
    now: datetime | None = None,
) -> list[TaskRecord]:
    tasks_root = root / "agent-work" / "tasks"
    if not tasks_root.is_dir():
        errors.append(f"{tasks_root}: missing fixed task directory")
        return []
    records: list[TaskRecord] = []
    seen: dict[str, Path] = {}
    for task in sorted(path for path in tasks_root.iterdir() if path.is_dir()):
        record, task_errors = inspect_task_directory(
            task,
            schema,
            permissions,
            authorizations,
            repository=repository,
            branch=branch,
            now=now,
        )
        errors.extend(task_errors)
        if record is None:
            continue
        task_id = record.request["task_id"]
        if task_id in seen:
            errors.append(
                f"{task}: duplicate task_id {task_id!r}; first seen at {seen[task_id]}"
            )
            continue
        seen[task_id] = task
        records.append(record)
    return records


def validate_transition(
    state_machine: dict[str, Any],
    source: str,
    target: str,
    section: str = "contribution_coordination",
) -> list[str]:
    transitions = state_machine.get(section, {}).get("transitions", {})
    if source not in transitions:
        return [f"unknown source state {source!r} in {section}"]
    if target not in transitions[source]:
        return [f"forbidden transition: {source} -> {target}"]
    return []


def owners_for_path(path: str, permissions: dict[str, Any]) -> set[str]:
    normalized = path.lstrip("./")
    owners: set[str] = set()
    for actor, actor_data in permissions.get("actors", {}).items():
        role = actor_data.get("role")
        patterns = permissions.get("roles", {}).get(role, {}).get("owned_paths", [])
        if any(path_matches(normalized, pattern) for pattern in patterns):
            owners.add(actor)
    return owners


def delegated_materialization_path_allowed(
    actor: str,
    action: str | None,
    path: str,
    permissions: dict[str, Any],
) -> bool:
    if actor != "codex" or not action:
        return False
    rule = (
        permissions.get("materialization", {})
        .get("codex", {})
        .get(action, {})
    )
    allowed = any(path_matches(path, pattern) for pattern in rule.get("paths", []))
    excluded = any(
        path_matches(path, pattern) for pattern in rule.get("excluded_paths", [])
    )
    return allowed and not excluded


def validate_change_set(
    changes: list[dict[str, str]],
    permissions: dict[str, Any],
    standing_authorizations: list[dict[str, Any]] | None = None,
    *,
    repository: str = "Yanansn/zhaiyezi",
    branch: str = "main",
    now: datetime | None = None,
) -> list[str]:
    errors: list[str] = []
    by_path: dict[str, set[str]] = {}
    shared = permissions.get("shared_serialized_paths", [])
    for change in changes:
        actor = change.get("actor", "")
        path = change.get("path", "").lstrip("./")
        action = change.get("action")
        by_path.setdefault(path, set()).add(actor)
        owners = owners_for_path(path, permissions)
        is_shared = any(path_matches(path, pattern) for pattern in shared)
        delegated = delegated_materialization_path_allowed(
            actor, action, path, permissions
        )
        actor_data = permissions.get("actors", {}).get(actor)
        role = actor_data.get("role") if isinstance(actor_data, dict) else None
        if action and isinstance(role, str):
            allowed_actions = set(
                permissions.get("roles", {}).get(role, {}).get("allowed_actions", [])
            )
            if action not in allowed_actions:
                errors.append(
                    f"actor {actor!r} cannot perform action {action!r}"
                )
        if (
            delegated
            and action == "materialize_chat_artifact"
            and standing_authorizations is not None
            and not any(
                standing_authorizes(
                    authorization,
                    actor,
                    action,
                    [path],
                    repository,
                    branch,
                    now=now,
                )
                for authorization in standing_authorizations
            )
        ):
            errors.append(
                f"actor {actor!r} cannot materialize {path!r}; no valid standing authorization"
            )
        if owners and actor not in owners and not delegated:
            errors.append(
                f"actor {actor!r} cannot modify {path!r}; owned by "
                + ", ".join(sorted(owners))
            )
        elif not owners and not is_shared:
            errors.append(f"path {path!r} has no Agent ownership rule")
    for path, actors in by_path.items():
        if len(actors) > 1:
            errors.append(
                f"conflict: multiple actors modify {path!r}: "
                + ", ".join(sorted(actors))
            )
    return errors


def configured_repository_state(root: Path) -> tuple[str, str]:
    try:
        permissions = yaml.safe_load(
            (root / "agent-protocol" / "permissions.yaml").read_text(encoding="utf-8")
        )
        standing = permissions["standing_authorization"]
        return standing["repository"], standing["branch"]
    except (OSError, UnicodeError, yaml.YAMLError, KeyError, TypeError):
        return "", ""


def repository_state(root: Path) -> tuple[str, str]:
    """Return the live origin repository and branch, with protocol defaults as fallback."""
    repository, branch = configured_repository_state(root)
    try:
        branch_run = subprocess.run(
            ["git", "-C", str(root), "branch", "--show-current"],
            check=True,
            capture_output=True,
            text=True,
        )
        if branch_run.stdout.strip():
            branch = branch_run.stdout.strip()
        remote_run = subprocess.run(
            ["git", "-C", str(root), "remote", "get-url", "origin"],
            check=True,
            capture_output=True,
            text=True,
        )
        remote = remote_run.stdout.strip().removesuffix(".git")
        remote_path = (
            remote.split(":", 1)[1]
            if "://" not in remote and ":" in remote
            else remote
        )
        segments = [segment for segment in remote_path.rstrip("/").split("/") if segment]
        if len(segments) >= 2:
            repository = "/".join(segments[-2:])
    except (OSError, subprocess.CalledProcessError):
        pass
    return repository, branch


def validate(root: Path, *, now: datetime | None = None) -> list[str]:
    errors: list[str] = []
    errors.extend(validate_repository_registry(root))
    errors.extend(validate_agent_roles(root))
    schema, permissions, state_machine = protocol_documents(root, errors)
    validate_protocol_documents(schema, permissions, state_machine, errors)
    errors.extend(validate_examples(root, schema, permissions))
    errors.extend(legacy_queue_errors(root))
    authorizations = load_standing_authorizations(
        root, schema, permissions, errors, now=now
    )
    repository, branch = repository_state(root)
    collect_task_records(
        root,
        schema,
        permissions,
        authorizations,
        errors,
        repository=repository,
        branch=branch,
        now=now,
    )
    return errors


def parse_change(value: str, errors: list[str]) -> dict[str, str] | None:
    parts = value.split(":", 2)
    if len(parts) == 2:
        actor, path = parts
        action = None
    elif len(parts) == 3:
        actor, action, path = parts
    else:
        actor, action, path = "", None, ""
    if not actor or not path or (len(parts) == 3 and not action):
        errors.append(
            f"invalid --change value {value!r}; use ACTOR:PATH or ACTOR:ACTION:PATH"
        )
        return None
    change = {"actor": actor, "path": path}
    if action:
        change["action"] = action
    return change


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "root", nargs="?", type=Path, default=Path(__file__).resolve().parents[1]
    )
    parser.add_argument(
        "--change", action="append", default=[], metavar="ACTOR[:ACTION]:PATH"
    )
    parser.add_argument(
        "--authorization", type=Path, help="validate one standing authorization file"
    )
    args = parser.parse_args()
    root = args.root.resolve()
    errors = validate(root)
    schema, permissions, _ = protocol_documents(root, errors)
    if args.authorization:
        path = args.authorization.resolve()
        authorization = load_yaml(path, errors)
        template = "examples" in path.parts
        errors.extend(
            validate_standing_authorization(
                authorization, path, schema, permissions, template=template
            )
        )
    changes = [parse_change(value, errors) for value in args.change]
    if args.change:
        authorizations = load_standing_authorizations(
            root, schema, permissions, errors
        )
        repository, branch = repository_state(root)
        errors.extend(
            validate_change_set(
                [change for change in changes if change],
                permissions,
                authorizations,
                repository=repository,
                branch=branch,
            )
        )
    for error in errors:
        print(f"ERROR {error}", file=sys.stderr)
    if errors:
        return 1
    print(f"OK agent protocol: {root}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
