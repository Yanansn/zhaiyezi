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


SCREENING_REQUIRED_FILES = {"SCOPE.yaml", "RESULTS.yaml", "REPORT.md"}
EVIDENCE_REQUIRED_FILES = {"SCOPE.yaml", "REPORT.md"}
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
    "not-an-upstream-bug",
    "insufficient-evidence",
    "watchlist",
    "do-not-pursue",
}
V2_CLASSIFICATIONS = (CLASSIFICATIONS - {"not-an-upstream-bug"}) | {
    "not-a-kubernetes-bug"
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
V3_DEEP_AUDIT_FIELDS = DEEP_AUDIT_FIELDS + (
    "ownership",
    "feasibility",
    "verification_matrix",
    "environment",
    "repository_scope",
)
OWNERSHIP_STATUSES = {
    "no-known-owner",
    "implicit-owner",
    "explicit-owner",
    "abandoned",
    "unknown",
}
OWNERSHIP_STRENGTHS = {
    "weak-interest",
    "conditional-interest",
    "active-investigation",
    "implementation-in-progress",
    "implementation-ready",
    "explicit-abandonment",
}
RELATED_ITEM_RELATIONSHIPS = {
    "explicit-implementation",
    "semantic-implementation",
    "partial-overlap",
    "competing-implementation",
    "historical-attempt",
    "source-change",
    "regression-source",
    "downstream-workaround",
    "reference-only",
    "unrelated",
}
OVERLAP_LEVELS = {"none", "low", "medium", "high", "complete", "unknown"}
VERIFICATION_LEVELS = (
    "static",
    "cpu_unit",
    "cpu_integration",
    "gpu_single",
    "gpu_multi",
    "model_e2e",
    "benchmark",
    "upstream_ci",
)
VERIFICATION_STATUSES = {
    "not-planned",
    "not-applicable",
    "pending",
    "passed",
    "failed",
    "blocked",
    "not-run",
    "ci-only",
}
SCOPE_STATUSES = {
    "single-repository",
    "multi-repository-confirmed",
    "scope-expansion-required",
}
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

    stage = scope.get("stage", "issue-screening")
    if stage not in {"issue-screening", "issue-evidence-collection"}:
        errors.append(f"SCOPE.yaml stage has unsupported value: {stage!r}")


def require_mapping(value: Any, location: str, errors: list[str]) -> dict[str, Any]:
    if not isinstance(value, dict):
        errors.append(f"{location} must be a mapping")
        return {}
    return value


def validate_ownership(value: Any, location: str, errors: list[str]) -> None:
    ownership = require_mapping(value, location, errors)
    if ownership.get("status") not in OWNERSHIP_STATUSES:
        errors.append(f"{location}.status has unknown value: {ownership.get('status')!r}")
    if ownership.get("confidence") not in CONFIDENCES:
        errors.append(f"{location}.confidence has unknown value: {ownership.get('confidence')!r}")
    signals = ownership.get("signals")
    if not isinstance(signals, list):
        errors.append(f"{location}.signals must be a list")
        signals = []
    for index, signal in enumerate(signals):
        signal_location = f"{location}.signals[{index}]"
        signal = require_mapping(signal, signal_location, errors)
        for key in ("actor", "actor_role", "type", "summary", "url", "observed_at"):
            if key not in signal:
                errors.append(f"{signal_location} requires {key}")
        if signal.get("strength") not in OWNERSHIP_STRENGTHS:
            errors.append(f"{signal_location}.strength has unknown value: {signal.get('strength')!r}")
        if not isinstance(signal.get("active"), bool):
            errors.append(f"{signal_location}.active must be boolean")
    active_owner_strengths = {
        "active-investigation", "implementation-in-progress", "implementation-ready"
    }
    if ownership.get("status") == "no-known-owner" and any(
        isinstance(signal, dict)
        and signal.get("active") is True
        and signal.get("strength") in active_owner_strengths
        for signal in signals
    ):
        errors.append(f"{location}.status no-known-owner conflicts with an active ownership signal")
    if ownership.get("status") in {"implicit-owner", "explicit-owner"} and not any(
        isinstance(signal, dict)
        and signal.get("active") is True
        and signal.get("strength") in active_owner_strengths
        for signal in signals
    ):
        errors.append(f"{location}.status {ownership.get('status')} requires an active ownership signal")
    inactivity = require_mapping(ownership.get("inactivity"), f"{location}.inactivity", errors)
    days = inactivity.get("days_since_last_progress")
    if days is not None and (not isinstance(days, int) or isinstance(days, bool) or days < 0):
        errors.append(f"{location}.inactivity.days_since_last_progress must be null or a non-negative integer")
    if "release_signal" not in ownership:
        errors.append(f"{location} requires release_signal")


def validate_related_items(value: Any, location: str, errors: list[str]) -> None:
    if not isinstance(value, list):
        errors.append(f"{location} must be a list")
        return
    for index, item in enumerate(value):
        item_location = f"{location}[{index}]"
        item = require_mapping(item, item_location, errors)
        for key in (
            "type", "repository", "number", "url", "state", "relationship",
            "explicit_issue_reference", "overlap", "blocks_contribution", "verified_at",
        ):
            if key not in item:
                errors.append(f"{item_location} requires {key}")
        if item.get("relationship") not in RELATED_ITEM_RELATIONSHIPS:
            errors.append(f"{item_location}.relationship has unknown value: {item.get('relationship')!r}")
        if not isinstance(item.get("explicit_issue_reference"), bool):
            errors.append(f"{item_location}.explicit_issue_reference must be boolean")
        if not isinstance(item.get("blocks_contribution"), bool):
            errors.append(f"{item_location}.blocks_contribution must be boolean")
        overlap = require_mapping(item.get("overlap"), f"{item_location}.overlap", errors)
        if overlap.get("level") not in OVERLAP_LEVELS:
            errors.append(f"{item_location}.overlap.level has unknown value: {overlap.get('level')!r}")
        if not isinstance(overlap.get("files"), list):
            errors.append(f"{item_location}.overlap.files must be a list")
        if "behavior" not in overlap:
            errors.append(f"{item_location}.overlap requires behavior")


def validate_feasibility(value: Any, location: str, errors: list[str]) -> None:
    feasibility = require_mapping(value, location, errors)
    for key in ("languages", "runtime_dependencies", "external_services", "model_requirements"):
        if not isinstance(feasibility.get(key), list):
            errors.append(f"{location}.{key} must be a list")
    surface = require_mapping(feasibility.get("estimated_surface"), f"{location}.estimated_surface", errors)
    files = surface.get("files")
    if files is not None and (not isinstance(files, int) or isinstance(files, bool) or files < 0):
        errors.append(f"{location}.estimated_surface.files must be null or a non-negative integer")
    if not isinstance(surface.get("subsystems"), list):
        errors.append(f"{location}.estimated_surface.subsystems must be a list")
    hardware = require_mapping(feasibility.get("hardware"), f"{location}.hardware", errors)
    for key in ("cpu_only_reproduction", "gpu_required_for_full_validation", "multi_gpu_required"):
        if hardware.get(key) is not None and not isinstance(hardware.get(key), bool):
            errors.append(f"{location}.hardware.{key} must be boolean or null")
    local = require_mapping(feasibility.get("local_execution"), f"{location}.local_execution", errors)
    if local.get("possible") is not None and not isinstance(local.get("possible"), bool):
        errors.append(f"{location}.local_execution.possible must be boolean or null")
    for section in ("ci_dependency", "design_dependency"):
        mapping = require_mapping(feasibility.get(section), f"{location}.{section}", errors)
        key = "required" if section == "ci_dependency" else "blocked"
        if mapping.get(key) is not None and not isinstance(mapping.get(key), bool):
            errors.append(f"{location}.{section}.{key} must be boolean or null")
    assessment = require_mapping(feasibility.get("codex_assessment"), f"{location}.codex_assessment", errors)
    for key in ("implementation", "verification", "overall"):
        if key not in assessment:
            errors.append(f"{location}.codex_assessment requires {key}")


def validate_verification_matrix(value: Any, location: str, errors: list[str]) -> None:
    matrix = require_mapping(value, location, errors)
    for level in VERIFICATION_LEVELS:
        level_location = f"{location}.{level}"
        entry = require_mapping(matrix.get(level), level_location, errors)
        if not isinstance(entry.get("required"), bool):
            errors.append(f"{level_location}.required must be boolean")
        status = entry.get("status")
        if status not in VERIFICATION_STATUSES:
            errors.append(f"{level_location}.status has unknown value: {status!r}")
        if entry.get("required") is True and status == "not-applicable":
            errors.append(f"{level_location} cannot be required and not-applicable")
        if status == "passed" and not present(entry.get("evidence")):
            errors.append(f"{level_location}.status passed requires evidence")
        if status in {"failed", "blocked", "not-run", "ci-only"} and not present(entry.get("reason")):
            errors.append(f"{level_location}.status {status} requires reason")
        if level == "model_e2e" and not isinstance(entry.get("models"), list):
            errors.append(f"{level_location}.models must be a list")


def validate_environment(value: Any, location: str, errors: list[str]) -> None:
    environment = require_mapping(value, location, errors)
    for key in (
        "os", "architecture", "python", "compiler", "pytorch", "cuda", "rocm",
        "gpu", "driver", "vllm", "base_commit",
    ):
        if key not in environment:
            errors.append(f"{location} requires {key}")
        elif environment[key] is not None and not isinstance(environment[key], str):
            errors.append(f"{location}.{key} must be a string or null")


def validate_repository_scope(value: Any, location: str, errors: list[str]) -> None:
    scope = require_mapping(value, location, errors)
    primary = require_mapping(scope.get("primary"), f"{location}.primary", errors)
    for key in ("repository", "issue"):
        if not present(primary.get(key)):
            errors.append(f"{location}.primary requires non-empty {key}")
    for key in ("related", "expected_change_repositories", "excluded_change_repositories"):
        if not isinstance(scope.get(key), list):
            errors.append(f"{location}.{key} must be a list")
    working_repositories = scope.get("working_repositories")
    if not isinstance(working_repositories, list):
        errors.append(f"{location}.working_repositories must be a list")
    else:
        for index, working in enumerate(working_repositories):
            working_location = f"{location}.working_repositories[{index}]"
            working = require_mapping(working, working_location, errors)
            for key in ("repository", "remote", "base", "branch", "commit", "worktree", "push_authorized"):
                if key not in working:
                    errors.append(f"{working_location} requires {key}")
            if not isinstance(working.get("push_authorized"), bool):
                errors.append(f"{working_location}.push_authorized must be boolean")
    status = scope.get("scope_status")
    if status not in SCOPE_STATUSES:
        errors.append(f"{location}.scope_status has unknown value: {status!r}")
    expected = scope.get("expected_change_repositories", [])
    primary_repository = primary.get("repository")
    cross_repo = [repository for repository in expected if repository != primary_repository]
    if cross_repo and status == "single-repository":
        errors.append(f"{location} expected changes outside primary repository require scope-expansion-required or multi-repository-confirmed")


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
    candidate: Any, bucket: str, index: int, schema_version: int, errors: list[str]
) -> None:
    location = f"RESULTS.yaml {bucket}[{index}]"
    if not isinstance(candidate, dict):
        errors.append(f"{location} must be a mapping")
        return
    required_fields = V3_DEEP_AUDIT_FIELDS if schema_version == 3 else DEEP_AUDIT_FIELDS
    missing = [key for key in required_fields if key not in candidate]
    if missing:
        errors.append(f"{location} missing fields: {', '.join(missing)}")
    classification = candidate.get("screening_classification")
    classifications = CLASSIFICATIONS if schema_version == 3 else V2_CLASSIFICATIONS
    if classification not in classifications:
        errors.append(f"{location} has unknown classification: {classification!r}")
    confidence = candidate.get("screening_confidence")
    if confidence not in CONFIDENCES:
        errors.append(f"{location} has unknown confidence: {confidence!r}")
    if bucket == "available" and classification != "available":
        errors.append(f"{location} must use classification 'available'")
    if bucket == "watchlist" and classification not in {"watchlist", "insufficient-evidence"}:
        errors.append(f"{location} must use watchlist or insufficient-evidence classification")
    excluded_classifications = classifications - {
        "available", "watchlist", "insufficient-evidence"
    }
    if bucket == "excluded_after_audit" and classification not in excluded_classifications:
        errors.append(f"{location} classification is not allowed after audit: {classification!r}")

    for key in ("assignees", "labels", "limitations"):
        if key in candidate and not isinstance(candidate[key], list):
            errors.append(f"{location} field {key} must be a list")
    if schema_version == 3:
        validate_ownership(candidate.get("ownership"), f"{location}.ownership", errors)
        validate_related_items(candidate.get("related_items"), f"{location}.related_items", errors)
        validate_feasibility(candidate.get("feasibility"), f"{location}.feasibility", errors)
        validate_verification_matrix(
            candidate.get("verification_matrix"), f"{location}.verification_matrix", errors
        )
        validate_environment(candidate.get("environment"), f"{location}.environment", errors)
        validate_repository_scope(
            candidate.get("repository_scope"), f"{location}.repository_scope", errors
        )
    elif "related_items" in candidate and not isinstance(candidate["related_items"], list):
        errors.append(f"{location} field related_items must be a list")
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
            if schema_version == 3:
                blocking = [
                    item
                    for item in candidate.get("related_items", [])
                    if isinstance(item, dict)
                    and item.get("blocks_contribution") is True
                ]
                if blocking:
                    errors.append(f"{location} cannot be available with blocking related_items")
                repository_scope = candidate.get("repository_scope", {})
                if isinstance(repository_scope, dict) and repository_scope.get("scope_status") == "scope-expansion-required":
                    errors.append(f"{location} cannot be available while repository scope expansion is required")
    elif "admission" in candidate:
        validate_admission(candidate["admission"], candidate, bucket, location, errors)


def validate_results(
    results: dict[str, Any], scope: dict[str, Any], errors: list[str]
) -> None:
    schema_version = results.get("schema_version")
    if schema_version not in {2, 3}:
        errors.append("RESULTS.yaml schema_version must be 2 or 3")
        schema_version = 3
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
            validate_deep_audit(candidate, bucket, index, schema_version, errors)

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


def validate_evidence_file(path: Path, scope: dict[str, Any], errors: list[str]) -> None:
    evidence = load_yaml(path, errors)
    if not isinstance(evidence, dict):
        return
    location = str(path.relative_to(path.parents[1]))
    if evidence.get("schema_version") != 1:
        errors.append(f"{location} schema_version must be 1")
    if evidence.get("stage") != "issue-evidence-collection":
        errors.append(f"{location} stage must be 'issue-evidence-collection'")
    if evidence.get("repository") != scope.get("repository"):
        errors.append(f"{location} repository must match SCOPE.yaml")
    for forbidden in ("screening_classification", "screening_confidence", "admission", "available"):
        if forbidden in evidence:
            errors.append(f"{location} forbids classification or admission field: {forbidden}")
    for key in ("issue", "repository", "url", "title", "collected_at"):
        if not present(evidence.get(key)):
            errors.append(f"{location} requires non-empty {key}")
    body = require_mapping(evidence.get("body"), f"{location}.body", errors)
    if not isinstance(body.get("complete"), bool):
        errors.append(f"{location}.body.complete must be boolean")
    comments = require_mapping(evidence.get("comments"), f"{location}.comments", errors)
    if not isinstance(comments.get("items"), list):
        errors.append(f"{location}.comments.items must be a list")
    if not isinstance(comments.get("pagination_complete"), bool):
        errors.append(f"{location}.comments.pagination_complete must be boolean")
    for section in ("timeline", "development"):
        mapping = require_mapping(evidence.get(section), f"{location}.{section}", errors)
        if not isinstance(mapping.get("items"), list):
            errors.append(f"{location}.{section}.items must be a list")
        if not isinstance(mapping.get("complete"), bool):
            errors.append(f"{location}.{section}.complete must be boolean")
    searches = require_mapping(evidence.get("searches"), f"{location}.searches", errors)
    for key in ("explicit_issue_number", "title_symptom", "symbols"):
        if not isinstance(searches.get(key), list):
            errors.append(f"{location}.searches.{key} must be a list")
    if not isinstance(evidence.get("ownership_signals"), list):
        errors.append(f"{location}.ownership_signals must be a list")
    validate_related_items(evidence.get("related_items"), f"{location}.related_items", errors)
    if not isinstance(evidence.get("limitations"), list):
        errors.append(f"{location}.limitations must be a list")


def validate(record: Path) -> list[str]:
    errors: list[str] = []
    if not record.is_dir():
        return [f"not a directory: {record}"]
    present_files = {path.name for path in record.iterdir() if path.is_file()}
    scope = load_yaml(record / "SCOPE.yaml", errors) if "SCOPE.yaml" in present_files else None
    stage = scope.get("stage", "issue-screening") if isinstance(scope, dict) else "issue-screening"
    required_files = EVIDENCE_REQUIRED_FILES if stage == "issue-evidence-collection" else SCREENING_REQUIRED_FILES
    missing = sorted(required_files - present_files)
    if missing:
        return [f"missing required files: {', '.join(missing)}"]
    results = load_yaml(record / "RESULTS.yaml", errors) if "RESULTS.yaml" in present_files else None
    try:
        report = (record / "REPORT.md").read_text(encoding="utf-8")
    except (OSError, UnicodeError) as error:
        errors.append(f"REPORT.md cannot be read: {error}")
    else:
        if not report.strip():
            errors.append("REPORT.md must not be empty")
    if isinstance(scope, dict):
        validate_scope(scope, errors)
    if stage == "issue-evidence-collection":
        if "RESULTS.yaml" in present_files:
            errors.append("issue-evidence-collection record must not contain RESULTS.yaml")
        evidence_directory = record / "evidence"
        evidence_files = sorted(evidence_directory.glob("*.yaml")) if evidence_directory.is_dir() else []
        if not evidence_files:
            errors.append("issue-evidence-collection record requires at least one evidence/*.yaml file")
        elif isinstance(scope, dict):
            for evidence_file in evidence_files:
                validate_evidence_file(evidence_file, scope, errors)
    elif isinstance(scope, dict) and isinstance(results, dict):
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
