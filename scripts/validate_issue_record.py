#!/usr/bin/env python3
"""Perform lightweight structural validation of zhaiyezi issue records."""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path


REQUIRED_FILES = {
    "ISSUE.md",
    "ANALYSIS.md",
    "CODE-MAP.md",
    "PLAN.md",
    "IMPLEMENTATION.md",
    "TESTING.md",
    "LEARNING.md",
    "PR.md",
    "JOURNAL.md",
    "STATUS.yaml",
}
TERMINAL_STATUSES = {"merged", "closed", "rejected", "blocked", "superseded"}
KNOWN_STATUSES = {
    "candidate",
    "screening",
    "awaiting-triage",
    "selected",
    "analyzing",
    "planned",
    "implementing",
    "testing",
    "pr-ready",
    "submitted",
    "reviewing",
    *TERMINAL_STATUSES,
}


def yaml_scalar(text: str, key: str) -> str | None:
    match = re.search(rf"(?m)^{re.escape(key)}:\s*[\"']?([^\"'\n#]+)", text)
    return match.group(1).strip() if match else None


def meaningful_markdown(text: str) -> str:
    text = re.sub(r"<!--.*?-->", "", text, flags=re.DOTALL)
    lines = [line for line in text.splitlines() if not line.lstrip().startswith("#")]
    return "\n".join(lines).strip()


def validate(record: Path) -> tuple[list[str], list[str]]:
    errors: list[str] = []
    warnings: list[str] = []
    if not record.is_dir():
        return [f"not a directory: {record}"], warnings

    missing = sorted(REQUIRED_FILES - {path.name for path in record.iterdir() if path.is_file()})
    if missing:
        errors.append(f"missing required files: {', '.join(missing)}")
        return errors, warnings

    status_text = (record / "STATUS.yaml").read_text(encoding="utf-8")
    issue = yaml_scalar(status_text, "issue")
    status = yaml_scalar(status_text, "status")
    if not issue:
        errors.append("STATUS.yaml has no top-level issue")
    if status not in KNOWN_STATUSES:
        errors.append(f"STATUS.yaml has unknown status: {status!r}")

    knowledge_path = record / "KNOWLEDGE.md"
    if not knowledge_path.exists():
        message = "legacy record has no KNOWLEDGE.md; add it before resuming research"
        if status in TERMINAL_STATUSES:
            warnings.append(message)
        else:
            errors.append("missing required file for an active record: KNOWLEDGE.md")
    else:
        knowledge = meaningful_markdown(knowledge_path.read_text(encoding="utf-8"))
        analysis = meaningful_markdown((record / "ANALYSIS.md").read_text(encoding="utf-8"))
        if not knowledge and len(analysis) >= 500:
            warnings.append(
                "ANALYSIS.md is substantive while KNOWLEDGE.md is empty; review whether key domain terms need explanation"
            )

    journal = (record / "JOURNAL.md").read_text(encoding="utf-8")
    if not journal.startswith("# Journal"):
        errors.append("JOURNAL.md must start with '# Journal'")
    return errors, warnings


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("records", nargs="+", type=Path)
    args = parser.parse_args()
    failed = False
    for record in args.records:
        errors, warnings = validate(record.resolve())
        for warning in warnings:
            print(f"WARNING {record}: {warning}")
        for error in errors:
            failed = True
            print(f"ERROR {record}: {error}", file=sys.stderr)
        if not errors:
            print(f"OK {record}")
    return 1 if failed else 0


if __name__ == "__main__":
    raise SystemExit(main())
