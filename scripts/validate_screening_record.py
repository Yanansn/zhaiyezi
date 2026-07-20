#!/usr/bin/env python3
"""Validate a lightweight zhaiyezi candidate-screening record."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path
from typing import Any

try:
    import yaml
except ImportError as error:  # pragma: no cover - environment failure
    raise SystemExit("PyYAML is required to validate screening records") from error


REQUIRED_FILES = {"SCOPE.yaml", "RESULTS.yaml", "REPORT.md"}
CLASSIFICATIONS = {
    "available",
    "occupied",
    "implicit-owner",
    "author-implementation",
    "implementation-pr-exists",
    "competing-open-prs",
    "already-implemented",
    "already-fixed",
    "blocked-by-design",
    "infrastructure",
    "third-party",
    "not-a-kubernetes-bug",
    "insufficient-evidence",
    "watchlist",
    "do-not-pursue",
}
CONFIDENCES = {"high", "medium", "low"}
RESULT_BUCKETS = ("available", "watchlist", "excluded")
SUMMARY_FIELDS = ("discovered", "quick_filtered", "deeply_audited", *RESULT_BUCKETS)
EVIDENCE_FIELDS = (
    "issue_body_checked",
    "labels_checked",
    "assignees_checked",
    "all_comments_checked",
    "development_checked",
    "issue_number_search_checked",
    "fixes_search_checked",
    "related_search_checked",
    "closes_search_checked",
    "refs_search_checked",
    "title_keyword_search_checked",
    "symbol_search_checked",
    "linked_prs_checked",
    "ownership_checked",
    "design_checked",
    "complexity_checked",
)
CANDIDATE_FIELDS = (
    "issue",
    "url",
    "title",
    "screening_classification",
    "screening_confidence",
    "assignees",
    "labels",
    "audited_at",
    "evidence",
    "related_items",
    "reason",
    "limitations",
    "recommended_next_action",
)


def load_yaml(path: Path, errors: list[str]) -> Any:
    try:
        data = yaml.safe_load(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, yaml.YAMLError) as error:
        errors.append(f"{path.name} cannot be parsed: {error}")
        return None
    if not isinstance(data, dict):
        errors.append(f"{path.name} must contain a YAML mapping")
        return None
    return data


def present(value: Any) -> bool:
    return value is not None and (not isinstance(value, str) or bool(value.strip()))


def validate_scope(scope: dict[str, Any], errors: list[str]) -> None:
    if scope.get("schema_version") != 1:
        errors.append("SCOPE.yaml schema_version must be 1")
    if not present(scope.get("repository")):
        errors.append("SCOPE.yaml requires repository")
    scan = scope.get("scan")
    if not isinstance(scan, dict):
        errors.append("SCOPE.yaml requires scan mapping")
    else:
        for key in ("id", "candidate_limit", "sort", "state"):
            if not present(scan.get(key)):
                errors.append(f"SCOPE.yaml scan requires {key}")
        limit = scan.get("candidate_limit")
        if not isinstance(limit, int) or isinstance(limit, bool) or limit < 1:
            errors.append("SCOPE.yaml scan.candidate_limit must be a positive integer")
    include = scope.get("include")
    if not isinstance(include, dict):
        errors.append("SCOPE.yaml requires include mapping")
    elif not isinstance(include.get("labels"), list):
        errors.append("SCOPE.yaml include.labels must be a list")
    exclude = scope.get("exclude")
    if not isinstance(exclude, dict):
        errors.append("SCOPE.yaml requires exclude mapping")
    else:
        for key in ("labels", "categories"):
            if not isinstance(exclude.get(key), list):
                errors.append(f"SCOPE.yaml exclude.{key} must be a list")
    preferences = scope.get("technical_preferences")
    if not isinstance(preferences, dict):
        errors.append("SCOPE.yaml requires technical_preferences mapping")
    else:
        for key in ("languages", "areas"):
            if not isinstance(preferences.get(key), list):
                errors.append(f"SCOPE.yaml technical_preferences.{key} must be a list")
    capabilities = scope.get("search_capabilities")
    if not isinstance(capabilities, dict):
        errors.append("SCOPE.yaml requires search_capabilities mapping")
    else:
        for key in ("issue_search", "pr_search", "code_search", "timeline_access"):
            if not isinstance(capabilities.get(key), bool):
                errors.append(f"SCOPE.yaml search_capabilities.{key} must be boolean")
    if not isinstance(scope.get("limitations"), list):
        errors.append("SCOPE.yaml limitations must be a list")


def validate_candidate(
    candidate: Any, bucket: str, index: int, errors: list[str]
) -> None:
    location = f"RESULTS.yaml {bucket}[{index}]"
    if not isinstance(candidate, dict):
        errors.append(f"{location} must be a mapping")
        return
    missing = [key for key in CANDIDATE_FIELDS if key not in candidate]
    if missing:
        errors.append(f"{location} missing fields: {', '.join(missing)}")
    classification = candidate.get("screening_classification")
    if classification not in CLASSIFICATIONS:
        errors.append(f"{location} has unknown classification: {classification!r}")
    confidence = candidate.get("screening_confidence")
    if confidence not in CONFIDENCES:
        errors.append(f"{location} has unknown confidence: {confidence!r}")
    if bucket == "available" and classification != "available":
        errors.append(f"{location} must use classification 'available'")
    if bucket != "available" and classification == "available":
        errors.append(f"{location} places an available classification in {bucket}")
    if bucket == "watchlist" and classification not in {"watchlist", "insufficient-evidence"}:
        errors.append(f"{location} must use watchlist or insufficient-evidence classification")
    if bucket == "excluded" and classification in {"watchlist", "insufficient-evidence"}:
        errors.append(f"{location} places a recheck classification in excluded")

    for key in ("assignees", "labels", "related_items", "limitations"):
        if key in candidate and not isinstance(candidate[key], list):
            errors.append(f"{location} field {key} must be a list")
    for key in ("issue", "url", "title", "audited_at", "reason", "recommended_next_action"):
        if not present(candidate.get(key)):
            errors.append(f"{location} requires non-empty {key}")

    evidence = candidate.get("evidence")
    if not isinstance(evidence, dict):
        errors.append(f"{location} evidence must be a mapping")
        return
    missing_evidence = [key for key in EVIDENCE_FIELDS if key not in evidence]
    if missing_evidence:
        errors.append(f"{location} missing evidence: {', '.join(missing_evidence)}")
    invalid_evidence = [
        key for key in EVIDENCE_FIELDS if key in evidence and not isinstance(evidence[key], bool)
    ]
    if invalid_evidence:
        errors.append(f"{location} evidence must be boolean: {', '.join(invalid_evidence)}")
    if bucket == "available":
        incomplete = [key for key in EVIDENCE_FIELDS if evidence.get(key) is not True]
        if incomplete:
            errors.append(f"{location} available audit is incomplete: {', '.join(incomplete)}")
        if confidence not in {"high", "medium"}:
            errors.append(f"{location} available confidence must be high or medium")


def validate_results(
    results: dict[str, Any], scope: dict[str, Any], errors: list[str]
) -> None:
    if results.get("schema_version") != 1:
        errors.append("RESULTS.yaml schema_version must be 1")
    if results.get("repository") != scope.get("repository"):
        errors.append("RESULTS.yaml repository must match SCOPE.yaml")
    scan = scope.get("scan") if isinstance(scope.get("scan"), dict) else {}
    if results.get("scan_id") != scan.get("id"):
        errors.append("RESULTS.yaml scan_id must match SCOPE.yaml scan.id")

    summary = results.get("summary")
    if not isinstance(summary, dict):
        errors.append("RESULTS.yaml requires summary mapping")
        summary = {}
    for key in SUMMARY_FIELDS:
        value = summary.get(key)
        if not isinstance(value, int) or isinstance(value, bool) or value < 0:
            errors.append(f"RESULTS.yaml summary.{key} must be a non-negative integer")

    buckets: dict[str, list[Any]] = {}
    for bucket in RESULT_BUCKETS:
        value = results.get(bucket)
        if not isinstance(value, list):
            errors.append(f"RESULTS.yaml {bucket} must be a list")
            value = []
        buckets[bucket] = value
        if summary.get(bucket) != len(value):
            errors.append(
                f"RESULTS.yaml summary.{bucket}={summary.get(bucket)!r} "
                f"does not match {bucket} length {len(value)}"
            )
        for index, candidate in enumerate(value):
            validate_candidate(candidate, bucket, index, errors)

    classified = sum(len(items) for items in buckets.values())
    deeply_audited = summary.get("deeply_audited")
    discovered = summary.get("discovered")
    quick_filtered = summary.get("quick_filtered")
    if isinstance(discovered, int) and discovered != classified:
        errors.append("RESULTS.yaml summary.discovered must match all result-list entries")
    if all(isinstance(value, int) for value in (discovered, quick_filtered, deeply_audited)):
        if not discovered >= quick_filtered >= deeply_audited:
            errors.append(
                "RESULTS.yaml funnel must satisfy discovered >= quick_filtered >= deeply_audited"
            )


def validate(record: Path) -> list[str]:
    errors: list[str] = []
    if not record.is_dir():
        return [f"not a directory: {record}"]
    present_files = {path.name for path in record.iterdir() if path.is_file()}
    missing = sorted(REQUIRED_FILES - present_files)
    if missing:
        return [f"missing required files: {', '.join(missing)}"]

    scope = load_yaml(record / "SCOPE.yaml", errors)
    results = load_yaml(record / "RESULTS.yaml", errors)
    report = (record / "REPORT.md").read_text(encoding="utf-8")
    if not report.strip():
        errors.append("REPORT.md must not be empty")
    if isinstance(scope, dict):
        validate_scope(scope, errors)
    if isinstance(scope, dict) and isinstance(results, dict):
        validate_results(results, scope, errors)
    return errors


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("records", nargs="+", type=Path)
    args = parser.parse_args()
    failed = False
    for record in args.records:
        errors = validate(record.resolve())
        for error in errors:
            failed = True
            print(f"ERROR {record}: {error}", file=sys.stderr)
        if not errors:
            print(f"OK {record}")
    return 1 if failed else 0


if __name__ == "__main__":
    raise SystemExit(main())
