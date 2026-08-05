"""Repository-scoped, resumable discovery facts; not an Issue state machine."""

from __future__ import annotations

from copy import deepcopy
from datetime import datetime, timezone
from pathlib import Path
from threading import Lock
from typing import Any

import yaml


def _now() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def _slug(repository: str) -> str:
    return repository.replace("/", "-")


def _write_yaml(path: Path, value: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_name(f".{path.name}.tmp")
    try:
        temporary.write_text(yaml.safe_dump(value, allow_unicode=True, sort_keys=False), encoding="utf-8")
        temporary.replace(path)
    except Exception:
        temporary.unlink(missing_ok=True)
        raise


def _stored_result(result: dict[str, Any]) -> dict[str, Any]:
    """Keep detailed facts only for issues that remain discovery candidates."""
    status = result.get("related_pr_status")
    if status == "no_known_related_pr":
        return deepcopy(result)
    compact: dict[str, Any] = {
        "issue": result.get("issue"),
        "related_pr_status": status,
    }
    if status == "related_pr_found":
        compact["related_prs"] = [
            evidence["pr"]
            for evidence in result.get("related_pr_evidence", [])
            if isinstance(evidence, dict) and isinstance(evidence.get("pr"), str)
        ]
    elif status == "insufficient_evidence":
        compact["limitations"] = list(result.get("limitations") or [])
    return compact


class DiscoveryLedger:
    """Persist audit results per repository without assigning or syncing state."""

    def __init__(self, root: Path, repository: str, query: dict[str, Any]) -> None:
        self.root = root / _slug(repository)
        self.repository = repository
        self.index_path = self.root / "INDEX.yaml"
        self.scan_id = _now().replace(":", "-")
        self.scan_path = self.root / "scans" / f"{self.scan_id}.yaml"
        self._lock = Lock()
        self._index = self._load_index()
        if self._compact_existing_results():
            _write_yaml(self.index_path, self._index)
        self._scan: dict[str, Any] = {
            "schema_version": 1,
            "repository": repository,
            "scan_id": self.scan_id,
            "started_at": _now(),
            "completed_at": None,
            "status": "running",
            "query": query,
            "audited": [],
            "reused": [],
            "local_exclusions": [],
            "limitations": [],
            "error": None,
        }
        _write_yaml(self.scan_path, self._scan)

    def _load_index(self) -> dict[str, Any]:
        if not self.index_path.exists():
            return {"schema_version": 1, "repository": self.repository, "issues": {}}
        try:
            value = yaml.safe_load(self.index_path.read_text(encoding="utf-8"))
        except (OSError, UnicodeError, yaml.YAMLError):
            return {"schema_version": 1, "repository": self.repository, "issues": {}}
        if not isinstance(value, dict) or value.get("repository") != self.repository or not isinstance(value.get("issues"), dict):
            return {"schema_version": 1, "repository": self.repository, "issues": {}}
        return value

    def _compact_existing_results(self) -> bool:
        changed = False
        for entry in self._index["issues"].values():
            if not isinstance(entry, dict) or not isinstance(entry.get("result"), dict):
                continue
            compact = _stored_result(entry["result"])
            if compact != entry["result"]:
                entry["result"] = compact
                changed = True
        return changed

    def reusable(self, issue: dict[str, Any], max_age_seconds: float) -> dict[str, Any] | None:
        number = issue.get("number")
        if not isinstance(number, int):
            return None
        key = f"{self.repository}#{number}"
        entry = self._index["issues"].get(key)
        if not isinstance(entry, dict) or entry.get("remote_updated_at") != issue.get("updated_at"):
            return None
        scanned_at = entry.get("last_scanned_at")
        try:
            age = (datetime.now(timezone.utc) - datetime.fromisoformat(str(scanned_at).replace("Z", "+00:00"))).total_seconds()
        except ValueError:
            return None
        if max_age_seconds <= 0 or age > max_age_seconds:
            return None
        result = entry.get("result")
        return deepcopy(result) if isinstance(result, dict) else None

    def record_audit(self, result: dict[str, Any], remote_updated_at: Any) -> None:
        issue = result.get("issue")
        if not isinstance(issue, str):
            return
        with self._lock:
            self._index["issues"][issue] = {
                "remote_updated_at": remote_updated_at,
                "last_scanned_at": _now(),
                "last_scan_id": self.scan_id,
                "result": _stored_result(result),
            }
            self._scan["audited"].append(issue)
            _write_yaml(self.index_path, self._index)
            _write_yaml(self.scan_path, self._scan)

    def record_reuse(self, result: dict[str, Any]) -> None:
        issue = result.get("issue")
        if not isinstance(issue, str):
            return
        with self._lock:
            self._scan["reused"].append(issue)
            _write_yaml(self.scan_path, self._scan)

    def record_local_exclusions(self, exclusions: list[dict[str, Any]]) -> None:
        with self._lock:
            self._scan["local_exclusions"] = deepcopy(exclusions)
            _write_yaml(self.scan_path, self._scan)

    def finish(self, status: str, limitations: list[str], error: str | None = None) -> None:
        with self._lock:
            self._scan["status"] = status
            self._scan["completed_at"] = _now()
            self._scan["limitations"] = sorted(set(limitations))
            self._scan["error"] = error
            _write_yaml(self.scan_path, self._scan)
