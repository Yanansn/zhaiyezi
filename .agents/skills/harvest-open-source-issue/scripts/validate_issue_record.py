#!/usr/bin/env python3
"""Validate the required files and basic status fields of an issue record."""

from __future__ import annotations

import argparse
import re
from pathlib import Path


REQUIRED = {
    "STATUS.yaml", "ISSUE.md", "ANALYSIS.md", "CODE-MAP.md", "PLAN.md",
    "IMPLEMENTATION.md", "TESTING.md", "LEARNING.md", "PR.md", "JOURNAL.md",
}
TERMINAL_STATUSES = {"merged", "blocked", "rejected", "superseded", "closed"}
STATUSES = {
    "candidate", "screening", "awaiting-triage", "selected", "analyzing",
    "planned", "implementing", "testing", "pr-ready", "submitted",
    "reviewing", "merged", "blocked", "rejected", "superseded", "closed",
}
PUBLIC_FIELDS = ("draft_ready", "reviewed", "user_approved", "published")


def public_bool(status_text: str, key: str) -> bool | None:
    section = re.search(
        r"(?m)^public_communication:\s*\n(?P<body>(?:^[ \t]+.*(?:\n|$))*)",
        status_text,
    )
    if not section:
        return None
    match = re.search(
        rf"(?m)^\s+{re.escape(key)}:\s*(true|false)\s*$",
        section.group("body"),
    )
    return None if not match else match.group(1) == "true"


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("record", type=Path)
    args = parser.parse_args()
    missing = sorted(REQUIRED - {p.name for p in args.record.iterdir()})
    if missing:
        raise SystemExit(f"missing required files: {', '.join(missing)}")
    status_text = (args.record / "STATUS.yaml").read_text(encoding="utf-8")
    match = re.search(r"^status:\s*([^\s]+)\s*$", status_text, re.MULTILINE)
    if not match or match.group(1) not in STATUSES:
        raise SystemExit("STATUS.yaml has an invalid or missing status")
    status = match.group(1)
    if not re.search(r'^issue:\s*"[^/]+/[^#]+#[0-9]+"\s*$', status_text, re.MULTILINE):
        raise SystemExit("STATUS.yaml has an invalid or missing issue identifier")
    knowledge = args.record / "KNOWLEDGE.md"
    if not knowledge.exists():
        if status in TERMINAL_STATUSES:
            print("warning: legacy terminal record has no KNOWLEDGE.md")
        else:
            raise SystemExit("active record is missing KNOWLEDGE.md")
    communication = {key: public_bool(status_text, key) for key in PUBLIC_FIELDS}
    if all(value is None for value in communication.values()):
        if status in TERMINAL_STATUSES:
            print("warning: legacy terminal record has no public_communication fields")
        else:
            raise SystemExit("active record is missing public_communication fields")
    elif any(value is None for value in communication.values()):
        raise SystemExit("public_communication fields are incomplete")
    else:
        if communication["published"] and not communication["user_approved"]:
            raise SystemExit("published communication requires user approval")
        if communication["user_approved"] and not communication["reviewed"]:
            raise SystemExit("user approval requires Chat Review")
        if communication["reviewed"] and not communication["draft_ready"]:
            raise SystemExit("Chat Review requires a ready Draft")
    comment = args.record / "COMMENT-DRAFT.md"
    if comment.exists() and "## Publication status" not in comment.read_text(encoding="utf-8"):
        raise SystemExit("COMMENT-DRAFT.md is missing Publication status")
    print("issue record is valid")


if __name__ == "__main__":
    main()
