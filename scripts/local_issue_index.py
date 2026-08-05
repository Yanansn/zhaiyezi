"""Build a read-only index of Issues already known to zhaiyezi."""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
import re
from typing import Any

import yaml


ISSUE_RE = re.compile(r"^(?P<repository>[^/#\s]+/[^/#\s]+)#(?P<number>[1-9][0-9]*)$")
TERMINAL_STATUSES = {"merged", "closed", "rejected", "blocked", "superseded"}
ACTIVE_STATUSES = {
    "candidate", "screening", "awaiting-triage", "selected", "analyzing",
    "discussion-reanalysis", "awaiting-scope-confirmation", "planned",
    "implementing", "testing", "pr-ready", "submitted", "reviewing",
    "ready", "active", "awaiting-decision", "changes-requested",
}
TERMINAL_CLASSIFICATIONS = {
    "duplicate", "not-actionable", "implementation-pr-exists",
}


@dataclass
class KnownIssue:
    issue: str
    reasons: set[str] = field(default_factory=set)
    sources: set[str] = field(default_factory=set)


def _issue_key(value: Any, repository: str | None = None) -> str | None:
    if not isinstance(value, str):
        return None
    match = ISSUE_RE.fullmatch(value.strip())
    if match:
        return f"{match.group('repository')}#{match.group('number')}"
    if repository and value.strip().isdigit() and int(value) > 0:
        return f"{repository}#{int(value)}"
    return None


def _load(path: Path) -> dict[str, Any] | None:
    try:
        value = yaml.safe_load(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, yaml.YAMLError):
        return None
    return value if isinstance(value, dict) else None


def _add(index: dict[str, KnownIssue], issue: str | None, reason: str, source: Path, root: Path) -> None:
    if issue is None:
        return
    key = issue.casefold()
    entry = index.setdefault(key, KnownIssue(issue=issue))
    entry.reasons.add(reason)
    entry.sources.add(str(source.relative_to(root)))


def build_index(root: Path, repository: str) -> dict[str, KnownIssue]:
    """Read current and historical local records without changing them."""
    index: dict[str, KnownIssue] = {}
    issues_root = root / "issues"
    for path in issues_root.glob("*/STATUS.yaml") if issues_root.exists() else ():
        data = _load(path)
        if not data or data.get("status") not in ACTIVE_STATUSES | TERMINAL_STATUSES:
            continue
        issue = _issue_key(data.get("issue"), repository)
        reason = "formal-issue-terminal" if data.get("status") in TERMINAL_STATUSES else "formal-issue-active"
        _add(index, issue, reason, path, root)

    tasks_root = root / "agent-work" / "tasks"
    for path in tasks_root.glob("*/REQUEST.yaml") if tasks_root.exists() else ():
        data = _load(path)
        if not data:
            continue
        _add(index, _issue_key(data.get("issue"), repository), "active-task", path, root)

    screenings_root = root / "screenings"
    for path in screenings_root.rglob("*.yaml") if screenings_root.exists() else ():
        data = _load(path)
        if not data:
            continue
        issue = _issue_key(data.get("issue"), repository)
        if issue is None:
            continue
        classification = data.get("classification") or data.get("screening_classification")
        reason = "screened-terminal" if classification in TERMINAL_CLASSIFICATIONS else "known-evidence"
        _add(index, issue, reason, path, root)
    return index


def exclusion_map(index: dict[str, KnownIssue], repository: str) -> dict[int, KnownIssue]:
    prefix = repository.casefold() + "#"
    result: dict[int, KnownIssue] = {}
    for entry in index.values():
        if entry.issue.casefold().startswith(prefix):
            result[int(entry.issue.rsplit("#", 1)[1])] = entry
    return result
