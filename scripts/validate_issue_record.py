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
PUBLIC_COMMUNICATION_FIELDS = (
    "draft_ready",
    "reviewed",
    "user_approved",
    "published",
    "identity_verified",
)


def yaml_scalar(text: str, key: str) -> str | None:
    match = re.search(rf"(?m)^{re.escape(key)}:\s*[\"']?([^\"'\n#]+)", text)
    return match.group(1).strip() if match else None


def meaningful_markdown(text: str) -> str:
    text = re.sub(r"<!--.*?-->", "", text, flags=re.DOTALL)
    lines = [line for line in text.splitlines() if not line.lstrip().startswith("#")]
    return "\n".join(lines).strip()


def yaml_bool_in_section(text: str, section: str, key: str) -> bool | None:
    section_match = re.search(
        rf"(?m)^{re.escape(section)}:\s*\n(?P<body>(?:^[ \t]+.*(?:\n|$))*)",
        text,
    )
    if not section_match:
        return None
    value_match = re.search(
        rf"(?m)^\s+{re.escape(key)}:\s*(true|false)\s*$",
        section_match.group("body"),
    )
    if not value_match:
        return None
    return value_match.group(1) == "true"


def yaml_value_in_section(text: str, section: str, key: str) -> str | None:
    section_match = re.search(
        rf"(?m)^{re.escape(section)}:\s*\n(?P<body>(?:^[ \t]+.*(?:\n|$))*)",
        text,
    )
    if not section_match:
        return None
    value_match = re.search(
        rf"(?m)^\s+{re.escape(key)}:\s*[\"']?([^\"'\n#]+)",
        section_match.group("body"),
    )
    return value_match.group(1).strip() if value_match else None


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

    communication = {
        key: yaml_bool_in_section(status_text, "public_communication", key)
        for key in PUBLIC_COMMUNICATION_FIELDS
    }
    if all(value is None for value in communication.values()):
        message = "legacy record has no public_communication fields; add them before resuming public work"
        if status in TERMINAL_STATUSES:
            warnings.append(message)
        else:
            errors.append("STATUS.yaml is missing the public_communication contract")
    elif any(value is None for value in communication.values()):
        errors.append("STATUS.yaml has incomplete public_communication fields")
    else:
        if communication["published"] and not communication["user_approved"]:
            errors.append("published public communication must have user_approved: true")
        if communication["published"] and not communication["identity_verified"]:
            errors.append("published public communication must have identity_verified: true")
        if communication["user_approved"] and not communication["reviewed"]:
            errors.append("user-approved public communication must have reviewed: true")
        if communication["reviewed"] and not communication["draft_ready"]:
            errors.append("reviewed public communication must have draft_ready: true")
        expected_identity = yaml_value_in_section(
            status_text, "public_communication", "expected_identity"
        )
        if communication["identity_verified"] and expected_identity in (None, "null"):
            errors.append("verified public identity requires expected_identity")

    comment_draft = record / "COMMENT-DRAFT.md"
    if comment_draft.exists():
        comment_text = comment_draft.read_text(encoding="utf-8")
        required_markers = (
            "## Publication status",
            "- Current status:",
            "- Expected GitHub identity:",
            "- Authenticated GitHub identity:",
            "- Identity verified:",
            "- Technical review completed:",
            "- User approved:",
            "- Publication authorized:",
            "- Published at:",
            "- GitHub URL:",
        )
        missing_markers = [marker for marker in required_markers if marker not in comment_text]
        if missing_markers:
            errors.append(
                "COMMENT-DRAFT.md has incomplete publication metadata: "
                + ", ".join(missing_markers)
            )

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

    ecosystem_path = record / "ECOSYSTEM.md"
    if not ecosystem_path.exists():
        message = "legacy record has no ECOSYSTEM.md; add it before resuming research"
        if status in TERMINAL_STATUSES:
            warnings.append(message)
        else:
            errors.append("missing mandatory file for an active record: ECOSYSTEM.md")
    else:
        ecosystem_text = ecosystem_path.read_text(encoding="utf-8")
        ecosystem_markers = (
            "## 1. Issue Timeline",
            "## 2. Timeline Events",
            "## 3. Development",
            "## 4. Downstream",
            "## 5. Related Work",
            "## 6. CI",
            "## 7. Maintainer Position",
            "## 8. Open Questions",
            "## 9. Current Ecosystem Summary",
            "Upstream:",
            "Downstream:",
            "Known workaround:",
            "Active implementation:",
            "Open questions:",
        )
        missing_markers = [
            marker for marker in ecosystem_markers if marker not in ecosystem_text
        ]
        if missing_markers:
            errors.append(
                "ECOSYSTEM.md has incomplete mandatory structure: "
                + ", ".join(missing_markers)
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
