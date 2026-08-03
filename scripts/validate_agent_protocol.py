#!/usr/bin/env python3
"""Validate the repository-backed Chat/Codex coordination protocol."""

from __future__ import annotations

import argparse
from fnmatch import fnmatch
import re
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
}
QUEUES = ("inbox", "active", "completed", "blocked")
TASK_ID_RE = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._-]*$")
REPOSITORY_RE = re.compile(r"^[^/\s]+/[^/\s]+$")
ISSUE_RE = re.compile(r"^[^/\s]+/[^#\s]+#[1-9][0-9]*$")


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


def require_fields(
    value: dict[str, Any], required: list[str], location: str, errors: list[str]
) -> None:
    for field in required:
        if field not in value:
            errors.append(f"{location}: missing required field {field}")


def protocol_documents(
    root: Path, errors: list[str]
) -> tuple[dict[str, Any], dict[str, Any], dict[str, Any]]:
    protocol = root / "agent-protocol"
    if not protocol.is_dir():
        errors.append(f"missing protocol directory: {protocol}")
        return {}, {}, {}
    present = {path.name for path in protocol.iterdir() if path.is_file()}
    missing = sorted(PROTOCOL_FILES - present)
    if missing:
        errors.append("agent-protocol is missing: " + ", ".join(missing))
    task_schema = load_yaml(protocol / "task-schema.yaml", errors)
    permissions = load_yaml(protocol / "permissions.yaml", errors)
    state_machine = load_yaml(protocol / "state-machine.yaml", errors)
    return task_schema, permissions, state_machine


def validate_protocol_documents(
    task_schema: dict[str, Any],
    permissions: dict[str, Any],
    state_machine: dict[str, Any],
    errors: list[str],
) -> None:
    for name, document in (
        ("task-schema.yaml", task_schema),
        ("permissions.yaml", permissions),
        ("state-machine.yaml", state_machine),
    ):
        if document.get("schema_version") != 1:
            errors.append(f"{name}: schema_version must be 1")

    request = task_schema.get("request")
    if not isinstance(request, dict):
        errors.append("task-schema.yaml: request must be a mapping")
    else:
        required = request.get("required_fields")
        expected = {
            "task_id", "task_type", "created_by", "assigned_agent",
            "repository", "issue", "status", "input_refs", "goal",
            "allowed_actions", "prohibited_actions", "expected_outputs",
            "completion",
        }
        if not isinstance(required, list) or not expected.issubset(set(required)):
            errors.append("task-schema.yaml: request.required_fields is incomplete")

    enums = task_schema.get("enums")
    if not isinstance(enums, dict):
        errors.append("task-schema.yaml: enums must be a mapping")
    else:
        required_statuses = {"ready", "active", "blocked", "review", "completed", "failed"}
        if set(enums.get("task_status", [])) != required_statuses:
            errors.append("task-schema.yaml: task_status must define the six protocol statuses")
        if not {"chat", "codex"}.issubset(set(enums.get("assigned_agent", []))):
            errors.append("task-schema.yaml: assigned_agent must include chat and codex")

    catalog = permissions.get("action_catalog")
    approval_actions = permissions.get("approval_required_actions")
    if not isinstance(catalog, dict):
        errors.append("permissions.yaml: action_catalog must be a mapping")
        catalog = {}
    if not isinstance(approval_actions, list):
        errors.append("permissions.yaml: approval_required_actions must be a list")
        approval_actions = []
    unknown_approval = sorted(set(approval_actions) - set(catalog))
    if unknown_approval:
        errors.append("permissions.yaml: unknown approval actions: " + ", ".join(unknown_approval))
    for action in (
        "upstream_write", "create_issue", "comment_issue", "assign_issue",
        "create_pull_request",
    ):
        if action not in approval_actions:
            errors.append(f"permissions.yaml: {action} must require user confirmation")

    task_queue = state_machine.get("task_queue")
    coordination = state_machine.get("contribution_coordination")
    if not isinstance(task_queue, dict):
        errors.append("state-machine.yaml: task_queue must be a mapping")
    if not isinstance(coordination, dict):
        errors.append("state-machine.yaml: contribution_coordination must be a mapping")
    else:
        transitions = coordination.get("transitions", {})
        if transitions.get("evidence_completed") != ["awaiting_review"]:
            errors.append(
                "state-machine.yaml: evidence_completed must transition only to awaiting_review"
            )


def validate_request(
    request: dict[str, Any],
    schema: dict[str, Any],
    permissions: dict[str, Any],
    location: str,
    errors: list[str],
) -> None:
    contract = schema.get("request", {})
    require_fields(request, contract.get("required_fields", []), location, errors)
    enums = schema.get("enums", {})
    if request.get("schema_version") != 1:
        errors.append(f"{location}: schema_version must be 1")
    task_id = request.get("task_id")
    if not isinstance(task_id, str) or not TASK_ID_RE.fullmatch(task_id):
        errors.append(f"{location}: task_id has an invalid format")
    for field in ("task_type", "created_by", "assigned_agent", "status"):
        enum_name = "task_status" if field == "status" else field
        if request.get(field) not in enums.get(enum_name, []):
            errors.append(f"{location}: invalid {field}: {request.get(field)!r}")
    repository = request.get("repository")
    if not isinstance(repository, str) or not REPOSITORY_RE.fullmatch(repository):
        errors.append(f"{location}: repository must use owner/name")
    issue = request.get("issue")
    if issue is not None and (not isinstance(issue, str) or not ISSUE_RE.fullmatch(issue)):
        errors.append(f"{location}: issue must be null or owner/repository#number")
    if isinstance(issue, str) and not issue.startswith(f"{repository}#"):
        errors.append(f"{location}: issue repository must match repository")
    for field in ("input_refs", "allowed_actions", "prohibited_actions", "expected_outputs"):
        if not isinstance(request.get(field), list):
            errors.append(f"{location}: {field} must be a list")
    if not isinstance(request.get("goal"), str) or not request.get("goal", "").strip():
        errors.append(f"{location}: goal must be a non-empty string")
    completion = request.get("completion")
    if not isinstance(completion, dict):
        errors.append(f"{location}: completion must be a mapping")
    else:
        require_fields(
            completion,
            schema.get("completion_contract", {}).get("required_fields", []),
            f"{location}.completion",
            errors,
        )

    catalog = permissions.get("action_catalog", {})
    allowed = request.get("allowed_actions", [])
    prohibited = request.get("prohibited_actions", [])
    if isinstance(allowed, list) and isinstance(prohibited, list):
        unknown = sorted((set(allowed) | set(prohibited)) - set(catalog))
        if unknown:
            errors.append(f"{location}: unknown actions: {', '.join(unknown)}")
        overlap = sorted(set(allowed) & set(prohibited))
        if overlap:
            errors.append(
                f"{location}: actions cannot be both allowed and prohibited: "
                + ", ".join(overlap)
            )


def validate_result(
    result: dict[str, Any], request: dict[str, Any], schema: dict[str, Any], location: str,
    errors: list[str],
) -> None:
    require_fields(result, schema.get("result", {}).get("required_fields", []), location, errors)
    if result.get("schema_version") != 1:
        errors.append(f"{location}: schema_version must be 1")
    if result.get("task_id") != request.get("task_id"):
        errors.append(f"{location}: task_id must match REQUEST.yaml")
    if result.get("created_by") != "codex":
        errors.append(f"{location}: created_by must be codex")
    if result.get("status") not in schema.get("enums", {}).get("result_status", []):
        errors.append(f"{location}: invalid result status: {result.get('status')!r}")
    for field in (
        "outputs", "actions_performed", "actions_not_performed", "validation",
        "limitations",
    ):
        if not isinstance(result.get(field), list):
            errors.append(f"{location}: {field} must be a list")


def validate_review(
    review: dict[str, Any], request: dict[str, Any], schema: dict[str, Any], location: str,
    errors: list[str],
) -> None:
    require_fields(review, schema.get("review", {}).get("required_fields", []), location, errors)
    if review.get("schema_version") != 1:
        errors.append(f"{location}: schema_version must be 1")
    if review.get("task_id") != request.get("task_id"):
        errors.append(f"{location}: task_id must match REQUEST.yaml")
    if review.get("created_by") != "chat":
        errors.append(f"{location}: created_by must be chat")
    enums = schema.get("enums", {})
    if review.get("status") not in enums.get("review_status", []):
        errors.append(f"{location}: invalid review status: {review.get('status')!r}")
    if review.get("decision") not in enums.get("review_decision", []):
        errors.append(f"{location}: invalid review decision: {review.get('decision')!r}")
    for field in ("findings", "next_actions"):
        if not isinstance(review.get(field), list):
            errors.append(f"{location}: {field} must be a list")


def validate_approval(
    approval: dict[str, Any], request: dict[str, Any], schema: dict[str, Any], location: str,
    errors: list[str],
) -> None:
    require_fields(
        approval,
        schema.get("approval", {}).get("required_fields", []),
        location,
        errors,
    )
    if approval.get("schema_version") != 1:
        errors.append(f"{location}: schema_version must be 1")
    if approval.get("task_id") != request.get("task_id"):
        errors.append(f"{location}: task_id must match REQUEST.yaml")
    if approval.get("approved_by") != "user":
        errors.append(f"{location}: approved_by must be user")
    if approval.get("status") not in schema.get("enums", {}).get("approval_status", []):
        errors.append(f"{location}: invalid approval status: {approval.get('status')!r}")
    if not isinstance(approval.get("actions"), list):
        errors.append(f"{location}: actions must be a list")
    if not isinstance(approval.get("scope"), str) or not approval.get("scope", "").strip():
        errors.append(f"{location}: scope must be a non-empty string")


def validate_task_directory(
    task: Path,
    queue: str,
    schema: dict[str, Any],
    permissions: dict[str, Any],
    state_machine: dict[str, Any],
) -> list[str]:
    errors: list[str] = []
    request_path = task / "REQUEST.yaml"
    if not request_path.is_file():
        return [f"{task}: missing REQUEST.yaml"]
    request = load_yaml(request_path, errors)
    validate_request(request, schema, permissions, str(request_path), errors)

    result = None
    review = None
    approval = None
    if (task / "RESULT.yaml").is_file():
        result = load_yaml(task / "RESULT.yaml", errors)
        validate_result(result, request, schema, str(task / "RESULT.yaml"), errors)
        if not (task / "REPORT.md").is_file():
            errors.append(f"{task}: RESULT.yaml requires REPORT.md")
    if (task / "REVIEW.yaml").is_file():
        review = load_yaml(task / "REVIEW.yaml", errors)
        validate_review(review, request, schema, str(task / "REVIEW.yaml"), errors)
    if (task / "APPROVAL.yaml").is_file():
        approval = load_yaml(task / "APPROVAL.yaml", errors)
        validate_approval(approval, request, schema, str(task / "APPROVAL.yaml"), errors)

    allowed = set(request.get("allowed_actions", []))
    prohibited = set(request.get("prohibited_actions", []))
    catalog = set(permissions.get("action_catalog", {}))
    if result is not None:
        performed = set(result.get("actions_performed", []))
        unknown = sorted(performed - catalog)
        unauthorized = sorted(performed - allowed)
        forbidden = sorted(performed & prohibited)
        if unknown:
            errors.append(f"{task}: RESULT.yaml performed unknown actions: {', '.join(unknown)}")
        if unauthorized:
            errors.append(
                f"{task}: RESULT.yaml performed actions not allowed by REQUEST.yaml: "
                + ", ".join(unauthorized)
            )
        if forbidden:
            errors.append(
                f"{task}: RESULT.yaml performed prohibited actions: "
                + ", ".join(forbidden)
            )
    if approval is not None:
        approved_actions = set(approval.get("actions", []))
        unknown = sorted(approved_actions - catalog)
        out_of_scope = sorted(approved_actions - allowed)
        if unknown:
            errors.append(f"{task}: APPROVAL.yaml contains unknown actions: {', '.join(unknown)}")
        if out_of_scope:
            errors.append(
                f"{task}: APPROVAL.yaml exceeds REQUEST.yaml scope: "
                + ", ".join(out_of_scope)
            )

    effective_status = request.get("status")
    if result is not None:
        effective_status = result.get("status")
    if review is not None:
        effective_status = review.get("status")
    directory_states = state_machine.get("task_queue", {}).get("directory_states", {})
    if effective_status not in directory_states.get(queue, []):
        errors.append(
            f"{task}: effective status {effective_status!r} is invalid in queue {queue!r}"
        )
    if queue in {"active", "blocked", "completed"} and result is None:
        errors.append(f"{task}: queue {queue!r} requires RESULT.yaml")
    if queue == "completed":
        if review is None:
            errors.append(f"{task}: completed task requires REVIEW.yaml")
        elif review.get("status") != "completed" or review.get("decision") != "approved":
            errors.append(f"{task}: completed task requires an approved completed Review")

    protected = allowed & set(permissions.get("approval_required_actions", []))
    if protected:
        approved = (
            set(approval.get("actions", []))
            if approval and approval.get("status") == "approved"
            else set()
        )
        missing = sorted(protected - approved)
        if missing:
            errors.append(
                f"{task}: protected allowed actions lack APPROVAL.yaml authorization: "
                + ", ".join(missing)
            )
    return errors


def validate_transition(
    state_machine: dict[str, Any], source: str, target: str,
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
        role_data = permissions.get("roles", {}).get(role, {})
        if any(fnmatch(normalized, pattern) for pattern in role_data.get("owned_paths", [])):
            owners.add(actor)
    return owners


def validate_change_set(changes: list[dict[str, str]], permissions: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    by_path: dict[str, set[str]] = {}
    shared = permissions.get("shared_serialized_paths", [])
    for change in changes:
        actor = change.get("actor", "")
        path = change.get("path", "").lstrip("./")
        by_path.setdefault(path, set()).add(actor)
        owners = owners_for_path(path, permissions)
        is_shared = any(fnmatch(path, pattern) for pattern in shared)
        if owners and actor not in owners:
            errors.append(
                f"actor {actor!r} cannot modify {path!r}; owned by {', '.join(sorted(owners))}"
            )
        elif not owners and not is_shared:
            errors.append(f"path {path!r} has no Agent ownership rule")
    for path, actors in by_path.items():
        if len(actors) > 1:
            errors.append(
                f"conflict: multiple actors modify {path!r}: {', '.join(sorted(actors))}"
            )
    return errors


def validate(root: Path) -> list[str]:
    errors: list[str] = []
    schema, permissions, state_machine = protocol_documents(root, errors)
    validate_protocol_documents(schema, permissions, state_machine, errors)
    work = root / "agent-work"
    if not work.is_dir():
        errors.append(f"missing task queue: {work}")
        return errors
    task_locations: dict[str, list[str]] = {}
    for queue in QUEUES:
        queue_path = work / queue
        if not queue_path.is_dir():
            errors.append(f"missing queue directory: {queue_path}")
            continue
        for task in sorted(path for path in queue_path.iterdir() if path.is_dir()):
            errors.extend(
                validate_task_directory(task, queue, schema, permissions, state_machine)
            )
            request_errors: list[str] = []
            request = load_yaml(task / "REQUEST.yaml", request_errors)
            errors.extend(request_errors)
            task_id = request.get("task_id")
            if isinstance(task_id, str):
                task_locations.setdefault(task_id, []).append(str(task))
    for task_id, locations in task_locations.items():
        if len(locations) > 1:
            errors.append(
                f"task_id {task_id!r} exists in multiple queues: "
                + ", ".join(locations)
            )
    return errors


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "root", nargs="?", type=Path, default=Path(__file__).resolve().parents[1]
    )
    parser.add_argument(
        "--change",
        action="append",
        default=[],
        metavar="ACTOR:PATH",
        help="validate a proposed actor/path change; repeat to detect conflicts",
    )
    args = parser.parse_args()
    root = args.root.resolve()
    errors = validate(root)
    if args.change:
        protocol_errors: list[str] = []
        _, permissions, _ = protocol_documents(root, protocol_errors)
        errors.extend(protocol_errors)
        changes: list[dict[str, str]] = []
        for change in args.change:
            actor, separator, path = change.partition(":")
            if not separator or not actor or not path:
                errors.append(f"invalid --change value {change!r}; use ACTOR:PATH")
                continue
            changes.append({"actor": actor, "path": path})
        errors.extend(validate_change_set(changes, permissions))
    for error in errors:
        print(f"ERROR {error}", file=sys.stderr)
    if errors:
        return 1
    print(f"OK agent protocol: {root}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
