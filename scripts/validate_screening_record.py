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
EXCLUDED_AFTER_AUDIT_CLASSIFICATIONS = CLASSIFICATIONS - {
    "available",
    "watchlist",
    "insufficient-evidence",
}
CONFIDENCES = {"high", "medium", "low"}
QUICK_FILTER_RULES = {
    "excluded-label",
    "closed-or-terminal",
    "duplicate-in-scan",
    "out-of-scope-category",
    "language-mismatch",
    "explicit-scope-mismatch",
}
QUICK_FILTER_EVIDENCE_FIELDS = (
    "issue_metadata_checked",
    "labels_checked",
    "assignees_checked",
)
DEEP_AUDIT_BUCKETS = ("available", "watchlist", "excluded_after_audit")
RESULT_BUCKETS = ("quick_filtered_out", *DEEP_AUDIT_BUCKETS)
SUMMARY_FIELDS = (
    "discovered",
    "quick_filtered_out",
    "deep_audit_queue",
    "deeply_audited",
    "available",
    "watchlist",
    "excluded_after_audit",
)
DEEP_AUDIT_EVIDENCE_FIELDS = (
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
DEEP_AUDIT_FIELDS = (
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
QUICK_FILTER_FIELDS = (
    "issue",
    "url",
    "title",
    "filtered_at",
    "rule",
    "reason",
    "metadata",
    "evidence",
    "limitations",
)
ADMISSION_FIELDS = (
    "gate_status",
    "evidence_refreshed_at",
    "user_decision",
    "medium_confidence_limitations_accepted",
    "accepted_limitations",
    "registry_mutation_authorized",
    "issue_initialization_authorized",
    "contribution_brief_authorized",
    "admitted_at",
    "notes",
)
ADMISSION_BOOLEAN_FIELDS = (
    "medium_confidence_limitations_accepted",
    "registry_mutation_authorized",
    "issue_initialization_authorized",
    "contribution_brief_authorized",
)
GATE_STATUSES = {
    "not-evaluated",
    "awaiting-user-decision",
    "passed",
    "failed",
    "stale-recheck-required",
}
USER_DECISIONS = {"pending", "continue", "decline"}


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


def validate_quick_filter(candidate: Any, index: int, errors: list[str]) -> None:
    location = f"RESULTS.yaml quick_filtered_out[{index}]"
    if not isinstance(candidate, dict):
        errors.append(f"{location} must be a mapping")
        return
    missing = [key for key in QUICK_FILTER_FIELDS if key not in candidate]
    if missing:
        errors.append(f"{location} missing fields: {', '.join(missing)}")
    forbidden = [
        key
        for key in ("screening_classification", "screening_confidence", "admission")
        if key in candidate
    ]
    if forbidden:
        errors.append(f"{location} forbids Deep Audit fields: {', '.join(forbidden)}")
    for key in ("issue", "url", "title", "filtered_at", "reason"):
        if not present(candidate.get(key)):
            errors.append(f"{location} requires non-empty {key}")
    rule = candidate.get("rule")
    if rule not in QUICK_FILTER_RULES:
        errors.append(f"{location} has unknown quick-filter rule: {rule!r}")
    if not isinstance(candidate.get("limitations"), list):
        errors.append(f"{location} limitations must be a list")

    metadata = candidate.get("metadata")
    if not isinstance(metadata, dict):
        errors.append(f"{location} metadata must be a mapping")
    else:
        if not present(metadata.get("state")):
            errors.append(f"{location} metadata requires non-empty state")
        for key in ("labels", "assignees"):
            if not isinstance(metadata.get(key), list):
                errors.append(f"{location} metadata.{key} must be a list")

    evidence = candidate.get("evidence")
    if not isinstance(evidence, dict):
        errors.append(f"{location} evidence must be a mapping")
        return
    missing_evidence = [key for key in QUICK_FILTER_EVIDENCE_FIELDS if key not in evidence]
    if missing_evidence:
        errors.append(f"{location} missing evidence: {', '.join(missing_evidence)}")
    invalid_evidence = [
        key
        for key in QUICK_FILTER_EVIDENCE_FIELDS
        if key in evidence and not isinstance(evidence[key], bool)
    ]
    if invalid_evidence:
        errors.append(f"{location} evidence must be boolean: {', '.join(invalid_evidence)}")
    incomplete = [key for key in QUICK_FILTER_EVIDENCE_FIELDS if evidence.get(key) is not True]
    if incomplete:
        errors.append(f"{location} metadata audit is incomplete: {', '.join(incomplete)}")


def validate_admission(
    admission: Any,
    candidate: dict[str, Any],
    bucket: str,
    location: str,
    errors: list[str],
) -> None:
    admission_location = f"{location} admission"
    if not isinstance(admission, dict):
        errors.append(f"{admission_location} must be a mapping")
        return
    missing = [key for key in ADMISSION_FIELDS if key not in admission]
    if missing:
        errors.append(f"{admission_location} missing fields: {', '.join(missing)}")
    gate_status = admission.get("gate_status")
    if gate_status not in GATE_STATUSES:
        errors.append(f"{admission_location} has unknown gate_status: {gate_status!r}")
    user_decision = admission.get("user_decision")
    if user_decision not in USER_DECISIONS:
        errors.append(f"{admission_location} has unknown user_decision: {user_decision!r}")
    for key in ADMISSION_BOOLEAN_FIELDS:
        if not isinstance(admission.get(key), bool):
            errors.append(f"{admission_location} {key} must be boolean")
    accepted_limitations = admission.get("accepted_limitations")
    if not isinstance(accepted_limitations, list):
        errors.append(f"{admission_location} accepted_limitations must be a list")

    if bucket != "available" and gate_status == "passed":
        errors.append(f"{admission_location} non-available candidate cannot pass the Gate")
    if user_decision == "decline" and gate_status == "passed":
        errors.append(f"{admission_location} declined candidate cannot pass the Gate")
    if gate_status != "passed":
        return

    if candidate.get("screening_classification") != "available":
        errors.append(f"{admission_location} passed Gate requires available classification")
    if user_decision != "continue":
        errors.append(f"{admission_location} passed Gate requires user_decision 'continue'")
    if not present(admission.get("evidence_refreshed_at")):
        errors.append(f"{admission_location} passed Gate requires evidence_refreshed_at")
    if not present(admission.get("admitted_at")):
        errors.append(f"{admission_location} passed Gate requires admitted_at")
    if candidate.get("screening_confidence") == "medium":
        if admission.get("medium_confidence_limitations_accepted") is not True:
            errors.append(
                f"{admission_location} medium-confidence Gate passage requires accepted limitations"
            )
        if not isinstance(accepted_limitations, list) or not accepted_limitations:
            errors.append(
                f"{admission_location} medium-confidence Gate passage requires non-empty accepted_limitations"
            )


def validate_deep_audit(
    candidate: Any, bucket: str, index: int, errors: list[str]
) -> None:
    location = f"RESULTS.yaml {bucket}[{index}]"
    if not isinstance(candidate, dict):
        errors.append(f"{location} must be a mapping")
        return
    missing = [key for key in DEEP_AUDIT_FIELDS if key not in candidate]
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
    if bucket == "watchlist" and classification not in {"watchlist", "insufficient-evidence"}:
        errors.append(f"{location} must use watchlist or insufficient-evidence classification")
    if bucket == "excluded_after_audit" and classification not in EXCLUDED_AFTER_AUDIT_CLASSIFICATIONS:
        errors.append(f"{location} classification is not allowed after audit: {classification!r}")

    for key in ("assignees", "labels", "related_items", "limitations"):
        if key in candidate and not isinstance(candidate[key], list):
            errors.append(f"{location} field {key} must be a list")
    for key in ("issue", "url", "title", "audited_at", "reason", "recommended_next_action"):
        if not present(candidate.get(key)):
            errors.append(f"{location} requires non-empty {key}")
    if bucket == "watchlist" and not present(candidate.get("recheck_trigger")):
        errors.append(f"{location} requires non-empty recheck_trigger")

    evidence = candidate.get("evidence")
    if not isinstance(evidence, dict):
        errors.append(f"{location} evidence must be a mapping")
    else:
        missing_evidence = [key for key in DEEP_AUDIT_EVIDENCE_FIELDS if key not in evidence]
        if missing_evidence:
            errors.append(f"{location} missing evidence: {', '.join(missing_evidence)}")
        invalid_evidence = [
            key
            for key in DEEP_AUDIT_EVIDENCE_FIELDS
            if key in evidence and not isinstance(evidence[key], bool)
        ]
        if invalid_evidence:
            errors.append(f"{location} evidence must be boolean: {', '.join(invalid_evidence)}")
        if bucket == "available":
            incomplete = [
                key for key in DEEP_AUDIT_EVIDENCE_FIELDS if evidence.get(key) is not True
            ]
            if incomplete:
                errors.append(f"{location} available audit is incomplete: {', '.join(incomplete)}")

    if bucket == "available":
        if confidence not in {"high", "medium"}:
            errors.append(f"{location} available confidence must be high or medium")
        if "admission" not in candidate:
            errors.append(f"{location} available candidate requires admission mapping")
        else:
            validate_admission(candidate["admission"], candidate, bucket, location, errors)
    elif "admission" in candidate:
        validate_admission(candidate["admission"], candidate, bucket, location, errors)


def validate_results(
    results: dict[str, Any], scope: dict[str, Any], errors: list[str]
) -> None:
    if results.get("schema_version") != 2:
        errors.append("RESULTS.yaml schema_version must be 2")
    if results.get("repository") != scope.get("repository"):
        errors.append("RESULTS.yaml repository must match SCOPE.yaml")
    scan = scope.get("scan") if isinstance(scope.get("scan"), dict) else {}
    if results.get("scan_id") != scan.get("id"):
        errors.append("RESULTS.yaml scan_id must match SCOPE.yaml scan.id")
    for legacy_field in ("quick_filtered", "excluded"):
        if legacy_field in results:
            errors.append(f"RESULTS.yaml uses legacy bucket: {legacy_field}")

    summary = results.get("summary")
    if not isinstance(summary, dict):
        errors.append("RESULTS.yaml requires summary mapping")
        summary = {}
    for legacy_field in ("quick_filtered", "excluded"):
        if legacy_field in summary:
            errors.append(f"RESULTS.yaml summary uses legacy field: {legacy_field}")
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

    for index, candidate in enumerate(buckets["quick_filtered_out"]):
        validate_quick_filter(candidate, index, errors)
    for bucket in DEEP_AUDIT_BUCKETS:
        for index, candidate in enumerate(buckets[bucket]):
            validate_deep_audit(candidate, bucket, index, errors)

    quick_count = len(buckets["quick_filtered_out"])
    available_count = len(buckets["available"])
    watchlist_count = len(buckets["watchlist"])
    excluded_count = len(buckets["excluded_after_audit"])
    deeply_audited_count = available_count + watchlist_count + excluded_count
    discovered_count = quick_count + deeply_audited_count
    if summary.get("deeply_audited") != deeply_audited_count:
        errors.append(
            "RESULTS.yaml summary.deeply_audited must equal available + watchlist "
            "+ excluded_after_audit"
        )
    deep_audit_queue = summary.get("deep_audit_queue")
    deeply_audited = summary.get("deeply_audited")
    discovered = summary.get("discovered")
    if deep_audit_queue != deeply_audited:
        errors.append("RESULTS.yaml deep_audit_queue must equal deeply_audited")
    if isinstance(deep_audit_queue, int) and not isinstance(deep_audit_queue, bool) and discovered != quick_count + deep_audit_queue:
        errors.append("RESULTS.yaml discovered must equal quick_filtered_out + deep_audit_queue")
    if discovered != discovered_count:
        errors.append(
            "RESULTS.yaml discovered must equal quick_filtered_out + available + watchlist "
            "+ excluded_after_audit"
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
    try:
        report = (record / "REPORT.md").read_text(encoding="utf-8")
    except (OSError, UnicodeError) as error:
        errors.append(f"REPORT.md cannot be read: {error}")
    else:
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
