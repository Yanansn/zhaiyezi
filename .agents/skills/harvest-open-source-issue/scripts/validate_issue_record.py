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
STATUSES = {
    "candidate", "screening", "awaiting-triage", "selected", "analyzing",
    "planned", "implementing", "testing", "pr-ready", "submitted",
    "reviewing", "merged", "blocked", "rejected", "superseded", "closed",
}


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
    if not re.search(r'^issue:\s*"[^/]+/[^#]+#[0-9]+"\s*$', status_text, re.MULTILINE):
        raise SystemExit("STATUS.yaml has an invalid or missing issue identifier")
    print("issue record is valid")


if __name__ == "__main__":
    main()
