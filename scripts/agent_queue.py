#!/usr/bin/env python3
"""Inspect the multi-agent task queue without mutating it."""

from __future__ import annotations

import argparse
from datetime import datetime, timezone
from pathlib import Path
import sys

try:
    from scripts import validate_agent_protocol as validator
except ImportError:  # Direct execution from scripts/.
    import validate_agent_protocol as validator


PRIORITY = {"urgent": 0, "high": 1, "normal": 2, "low": 3}


def created_at(record: validator.TaskRecord) -> datetime:
    value = record.request.get("created_at")
    if not isinstance(value, str):
        return datetime.max.replace(tzinfo=timezone.utc)
    parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    if parsed.tzinfo is None:
        parsed = parsed.replace(tzinfo=timezone.utc)
    return parsed.astimezone(timezone.utc)


def sort_records(
    records: list[validator.TaskRecord],
) -> list[validator.TaskRecord]:
    return sorted(
        records,
        key=lambda record: (
            PRIORITY.get(record.request.get("priority", "normal"), PRIORITY["normal"]),
            created_at(record),
            record.request["task_id"],
        ),
    )


def load_queue(root: Path) -> tuple[list[validator.TaskRecord], list[str]]:
    errors: list[str] = []
    schema, permissions, state_machine = validator.protocol_documents(root, errors)
    validator.validate_protocol_documents(schema, permissions, state_machine, errors)
    errors.extend(validator.validate_examples(root, schema, permissions))
    errors.extend(validator.legacy_queue_errors(root))
    authorizations = validator.load_standing_authorizations(
        root, schema, permissions, errors
    )
    repository, branch = validator.repository_state(root)
    records = validator.collect_task_records(
        root,
        schema,
        permissions,
        authorizations,
        errors,
        repository=repository,
        branch=branch,
    )
    return sort_records(records), errors


def filter_records(
    records: list[validator.TaskRecord],
    *,
    agent: str | None = None,
    status: str | None = None,
) -> list[validator.TaskRecord]:
    return [
        record
        for record in records
        if (agent is None or record.request.get("assigned_agent") == agent)
        and (status is None or record.status == status)
    ]


def next_task(
    records: list[validator.TaskRecord], agent: str
) -> validator.TaskRecord | None:
    matching = filter_records(records, agent=agent, status="ready")
    return matching[0] if matching else None


def print_record(record: validator.TaskRecord) -> None:
    request = record.request
    print(f"task_id: {request['task_id']}")
    print(f"status: {record.status}")
    print(f"assigned_agent: {request['assigned_agent']}")
    print(f"priority: {request.get('priority', 'normal')}")
    print(f"created_at: {request.get('created_at', '-')}")
    print(f"task_type: {request['task_type']}")
    print(f"repository: {request['repository']}")
    print(f"path: {record.path}")
    print(f"goal: {request['goal']}")


def print_list(records: list[validator.TaskRecord]) -> None:
    if not records:
        print("No matching tasks.")
        return
    print("TASK_ID\tSTATUS\tAGENT\tPRIORITY\tCREATED_AT")
    for record in records:
        request = record.request
        print(
            "\t".join(
                (
                    request["task_id"],
                    record.status,
                    request["assigned_agent"],
                    request.get("priority", "normal"),
                    request.get("created_at", "-"),
                )
            )
        )


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--root", type=Path, default=Path(__file__).resolve().parents[1]
    )
    commands = parser.add_subparsers(dest="command", required=True)

    list_parser = commands.add_parser("list", help="list valid queue tasks")
    list_parser.add_argument("--agent", choices=("agent:luna", "agent:terra", "agent:sol", "chat", "codex"))
    list_parser.add_argument(
        "--status",
        choices=(
            "ready", "active", "awaiting-decision", "awaiting-review", "changes-requested",
            "blocked", "failed", "rejected", "completed",
        ),
    )

    next_parser = commands.add_parser("next", help="show the next ready task")
    next_parser.add_argument("--agent", required=True, choices=("agent:luna", "agent:terra", "agent:sol", "chat", "codex"))

    show_parser = commands.add_parser("show", help="show one real queue task")
    show_parser.add_argument("--task", required=True)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    root = args.root.resolve()
    records, errors = load_queue(root)
    if errors:
        for error in errors:
            print(f"ERROR {error}", file=sys.stderr)
        return 1

    if args.command == "list":
        print_list(filter_records(records, agent=args.agent, status=args.status))
        return 0
    if args.command == "next":
        record = next_task(records, args.agent)
        if record is None:
            print("No matching tasks.")
        else:
            print_record(record)
        return 0

    record = next(
        (candidate for candidate in records if candidate.request["task_id"] == args.task),
        None,
    )
    if record is None:
        print(f"Task not found: {args.task}", file=sys.stderr)
        return 1
    print_record(record)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
