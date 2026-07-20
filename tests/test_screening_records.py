from __future__ import annotations

import copy
import tempfile
import unittest
from pathlib import Path

import yaml

from scripts import validate_screening_record as validator


REPOSITORY_ROOT = Path(__file__).resolve().parents[1]


def scope() -> dict:
    return {
        "schema_version": 1,
        "repository": "example/example",
        "scan": {
            "id": "test-screening-v2",
            "started_at": None,
            "completed_at": None,
            "candidate_limit": 10,
            "sort": "created-desc",
            "state": "open",
        },
        "include": {"labels": []},
        "exclude": {"labels": [], "categories": []},
        "technical_preferences": {"languages": [], "areas": []},
        "search_capabilities": {
            "issue_search": True,
            "pr_search": True,
            "code_search": True,
            "timeline_access": True,
        },
        "limitations": [],
    }


def evidence() -> dict:
    return {key: True for key in validator.DEEP_AUDIT_EVIDENCE_FIELDS}


def admission(**updates: object) -> dict:
    value = {
        "gate_status": "not-evaluated",
        "evidence_refreshed_at": None,
        "user_decision": "pending",
        "medium_confidence_limitations_accepted": False,
        "accepted_limitations": [],
        "registry_mutation_authorized": False,
        "issue_initialization_authorized": False,
        "contribution_brief_authorized": False,
        "admitted_at": None,
        "notes": None,
    }
    value.update(updates)
    return value


def deep_candidate(classification: str, confidence: str = "high") -> dict:
    return {
        "issue": "example/example#1",
        "url": "https://github.com/example/example/issues/1",
        "title": "Example candidate",
        "screening_classification": classification,
        "screening_confidence": confidence,
        "assignees": [],
        "labels": ["kind/bug"],
        "audited_at": "2026-07-20T01:00:00Z",
        "evidence": evidence(),
        "related_items": [],
        "reason": "Audited fixture.",
        "limitations": [],
        "recommended_next_action": "Review the result.",
    }


def available_candidate(confidence: str = "high", gate: dict | None = None) -> dict:
    candidate = deep_candidate("available", confidence)
    candidate["admission"] = admission() if gate is None else gate
    return candidate


def quick_candidate() -> dict:
    return {
        "issue": "example/example#2",
        "url": "https://github.com/example/example/issues/2",
        "title": "Documentation-only candidate",
        "filtered_at": "2026-07-20T00:30:00Z",
        "rule": "excluded-label",
        "reason": "Matches an explicitly excluded label.",
        "metadata": {
            "state": "open",
            "labels": ["kind/documentation"],
            "assignees": [],
        },
        "evidence": {
            "issue_metadata_checked": True,
            "labels_checked": True,
            "assignees_checked": True,
        },
        "limitations": [],
    }


def results(
    *,
    quick: list[dict] | None = None,
    available: list[dict] | None = None,
    watchlist: list[dict] | None = None,
    excluded: list[dict] | None = None,
) -> dict:
    quick = [] if quick is None else quick
    available = [] if available is None else available
    watchlist = [] if watchlist is None else watchlist
    excluded = [] if excluded is None else excluded
    deeply_audited = len(available) + len(watchlist) + len(excluded)
    return {
        "schema_version": 2,
        "scan_id": "test-screening-v2",
        "repository": "example/example",
        "summary": {
            "discovered": len(quick) + deeply_audited,
            "quick_filtered_out": len(quick),
            "deep_audit_queue": deeply_audited,
            "deeply_audited": deeply_audited,
            "available": len(available),
            "watchlist": len(watchlist),
            "excluded_after_audit": len(excluded),
        },
        "quick_filtered_out": quick,
        "available": available,
        "watchlist": watchlist,
        "excluded_after_audit": excluded,
    }


class ScreeningRecordTests(unittest.TestCase):
    def validate_data(self, result_data: dict) -> list[str]:
        with tempfile.TemporaryDirectory() as temporary:
            record = Path(temporary) / "record"
            record.mkdir()
            (record / "SCOPE.yaml").write_text(
                yaml.safe_dump(scope(), sort_keys=False), encoding="utf-8"
            )
            (record / "RESULTS.yaml").write_text(
                yaml.safe_dump(result_data, sort_keys=False), encoding="utf-8"
            )
            (record / "REPORT.md").write_text("# Test report\n", encoding="utf-8")
            return validator.validate(record)

    def assert_error(self, result_data: dict, fragment: str) -> None:
        errors = self.validate_data(result_data)
        self.assertTrue(errors, "invalid record unexpectedly passed")
        self.assertTrue(
            any(fragment in error for error in errors),
            f"expected {fragment!r} in errors: {errors}",
        )

    def test_empty_template_record_passes(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            record = Path(temporary) / "record"
            record.mkdir()
            replacements = {
                "{{REPOSITORY}}": "example/example",
                "{{SCAN_ID}}": "test-screening-v2",
                "{{CANDIDATE_LIMIT}}": "10",
            }
            for template in (REPOSITORY_ROOT / "templates" / "screening").iterdir():
                content = template.read_text(encoding="utf-8")
                for marker, value in replacements.items():
                    content = content.replace(marker, value)
                (record / template.name).write_text(content, encoding="utf-8")
            self.assertEqual([], validator.validate(record))

    def test_valid_quick_filtered_candidate(self) -> None:
        self.assertEqual([], self.validate_data(results(quick=[quick_candidate()])))

    def test_valid_high_available_not_evaluated(self) -> None:
        self.assertEqual([], self.validate_data(results(available=[available_candidate()])))

    def test_valid_medium_available_passed_with_accepted_limitations(self) -> None:
        gate = admission(
            gate_status="passed",
            evidence_refreshed_at="2026-07-20T02:00:00Z",
            user_decision="continue",
            medium_confidence_limitations_accepted=True,
            accepted_limitations=["Project metadata is unavailable."],
            admitted_at="2026-07-20T02:05:00Z",
        )
        candidate = available_candidate("medium", gate)
        self.assertEqual([], self.validate_data(results(available=[candidate])))

    def test_valid_watchlist_candidate(self) -> None:
        candidate = deep_candidate("watchlist", "medium")
        candidate["recheck_trigger"] = "Recheck when the linked PR closes."
        self.assertEqual([], self.validate_data(results(watchlist=[candidate])))

    def test_valid_excluded_after_audit_candidate(self) -> None:
        candidate = deep_candidate("implicit-owner")
        self.assertEqual([], self.validate_data(results(excluded=[candidate])))

    def test_quick_filter_missing_minimum_evidence_fails(self) -> None:
        candidate = quick_candidate()
        del candidate["evidence"]["assignees_checked"]
        self.assert_error(results(quick=[candidate]), "missing evidence: assignees_checked")

    def test_quick_filter_with_classification_fails(self) -> None:
        candidate = quick_candidate()
        candidate["screening_classification"] = "do-not-pursue"
        self.assert_error(results(quick=[candidate]), "forbids Deep Audit fields")

    def test_available_with_false_evidence_fails(self) -> None:
        candidate = available_candidate()
        candidate["evidence"]["all_comments_checked"] = False
        self.assert_error(results(available=[candidate]), "available audit is incomplete")

    def test_available_without_admission_fails(self) -> None:
        candidate = available_candidate()
        del candidate["admission"]
        self.assert_error(results(available=[candidate]), "requires admission mapping")

    def test_medium_passed_without_acceptance_fails(self) -> None:
        gate = admission(
            gate_status="passed",
            evidence_refreshed_at="2026-07-20T02:00:00Z",
            user_decision="continue",
            admitted_at="2026-07-20T02:05:00Z",
        )
        candidate = available_candidate("medium", gate)
        self.assert_error(results(available=[candidate]), "requires accepted limitations")

    def test_passed_with_pending_user_decision_fails(self) -> None:
        gate = admission(
            gate_status="passed",
            evidence_refreshed_at="2026-07-20T02:00:00Z",
            admitted_at="2026-07-20T02:05:00Z",
        )
        candidate = available_candidate(gate=gate)
        self.assert_error(results(available=[candidate]), "requires user_decision 'continue'")

    def test_passed_without_evidence_refresh_fails(self) -> None:
        gate = admission(
            gate_status="passed",
            user_decision="continue",
            admitted_at="2026-07-20T02:05:00Z",
        )
        candidate = available_candidate(gate=gate)
        self.assert_error(results(available=[candidate]), "requires evidence_refreshed_at")

    def test_watchlist_without_recheck_trigger_fails(self) -> None:
        candidate = deep_candidate("watchlist", "medium")
        self.assert_error(results(watchlist=[candidate]), "requires non-empty recheck_trigger")

    def test_excluded_after_audit_with_available_classification_fails(self) -> None:
        candidate = available_candidate()
        self.assert_error(results(excluded=[candidate]), "classification is not allowed after audit")

    def test_summary_bucket_count_mismatch_fails(self) -> None:
        result_data = results(quick=[quick_candidate()])
        result_data["summary"]["quick_filtered_out"] = 0
        self.assert_error(result_data, "does not match quick_filtered_out length")

    def test_discovered_funnel_mismatch_fails(self) -> None:
        result_data = results(quick=[quick_candidate()])
        result_data["summary"]["discovered"] = 2
        self.assert_error(result_data, "discovered must equal quick_filtered_out")

    def test_unknown_classification_fails(self) -> None:
        candidate = deep_candidate("mystery")
        self.assert_error(results(excluded=[candidate]), "unknown classification")

    def test_unknown_quick_filter_rule_fails(self) -> None:
        candidate = quick_candidate()
        candidate["rule"] = "mystery"
        self.assert_error(results(quick=[candidate]), "unknown quick-filter rule")

    def test_unknown_gate_status_fails(self) -> None:
        candidate = available_candidate(gate=admission(gate_status="mystery"))
        self.assert_error(results(available=[candidate]), "unknown gate_status")


if __name__ == "__main__":
    unittest.main()
