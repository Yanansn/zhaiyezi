from __future__ import annotations

import copy
import subprocess
import tempfile
import unittest
from pathlib import Path

import yaml

from scripts import validate_issue_record as issue_validator
from scripts import repository_discovery
from scripts import validate_screening_record as screening_validator
from scripts import validate_agent_protocol as protocol_validator


ROOT = Path(__file__).resolve().parents[1]
FIXTURES = ROOT / "tests" / "fixtures" / "lmcache"


def load_fixture(name: str) -> dict:
    return yaml.safe_load((FIXTURES / name).read_text(encoding="utf-8"))


def scope(stage: str = "issue-screening") -> dict:
    return {
        "schema_version": 1,
        "stage": stage,
        "repository": "LMCache/LMCache",
        "scan": {
            "id": "lmcache-v3",
            "started_at": None,
            "completed_at": None,
            "candidate_limit": 10,
            "sort": "created-desc",
            "state": "open",
        },
        "include": {"labels": []},
        "exclude": {"labels": [], "categories": []},
        "technical_preferences": {"languages": ["python", "cpp"], "areas": []},
        "search_capabilities": {
            "issue_search": True,
            "pr_search": True,
            "code_search": True,
            "timeline_access": True,
        },
        "limitations": [],
    }


def admission(gate_status: str = "not-evaluated") -> dict:
    passed = gate_status == "passed"
    return {
        "gate_status": gate_status,
        "evidence_refreshed_at": "2026-08-03T01:00:00Z" if passed else None,
        "user_decision": "continue" if passed else "pending",
        "medium_confidence_limitations_accepted": False,
        "accepted_limitations": [],
        "registry_mutation_authorized": False,
        "issue_initialization_authorized": False,
        "contribution_brief_authorized": False,
        "admitted_at": "2026-08-03T01:05:00Z" if passed else None,
        "notes": None,
    }


class RepositoryAgnosticScreeningTests(unittest.TestCase):
    def validate_results(self, results: dict) -> list[str]:
        with tempfile.TemporaryDirectory() as temporary:
            record = Path(temporary)
            (record / "SCOPE.yaml").write_text(
                yaml.safe_dump(scope(), sort_keys=False), encoding="utf-8"
            )
            (record / "RESULTS.yaml").write_text(
                yaml.safe_dump(results, sort_keys=False), encoding="utf-8"
            )
            (record / "REPORT.md").write_text("# report\n", encoding="utf-8")
            return screening_validator.validate(record)

    def available_result(self, *, gate_status: str = "not-evaluated") -> tuple[dict, dict]:
        results = load_fixture("screening-results-v3.yaml")
        candidate = results["excluded_after_audit"].pop()
        candidate["screening_classification"] = "available"
        candidate["ownership"] = {
            "status": "no-known-owner",
            "confidence": "high",
            "signals": [],
            "inactivity": {"days_since_last_progress": None},
            "release_signal": None,
        }
        candidate["admission"] = admission(gate_status)
        results["available"] = [candidate]
        results["summary"]["available"] = 1
        results["summary"]["excluded_after_audit"] = 0
        return results, candidate

    def test_lmcache_unassigned_but_active_implementation_is_implicit_owner(self) -> None:
        results = load_fixture("screening-results-v3.yaml")
        self.assertEqual([], self.validate_results(results))
        candidate = results["excluded_after_audit"][0]
        self.assertEqual([], candidate["assignees"])
        self.assertEqual("implicit-owner", candidate["ownership"]["status"])
        self.assertEqual("implementation-in-progress", candidate["ownership"]["signals"][0]["strength"])

    def test_semantic_pr_without_explicit_issue_reference_is_valid_evidence(self) -> None:
        results = load_fixture("screening-results-v3.yaml")
        item = results["excluded_after_audit"][0]["related_items"][0]
        item.update(
            relationship="semantic-implementation",
            explicit_issue_reference=False,
            state="open",
            blocks_contribution=True,
        )
        self.assertEqual([], self.validate_results(results))

    def test_cpu_passed_and_gpu_not_run_remain_distinct_valid_layers(self) -> None:
        results = load_fixture("screening-results-v3.yaml")
        self.assertEqual([], self.validate_results(results))
        matrix = results["excluded_after_audit"][0]["verification_matrix"]
        self.assertEqual("passed", matrix["cpu_unit"]["status"])
        self.assertEqual("not-run", matrix["gpu_single"]["status"])

    def test_cross_repository_change_requires_scope_expansion(self) -> None:
        results = load_fixture("screening-results-v3.yaml")
        repository_scope = results["excluded_after_audit"][0]["repository_scope"]
        repository_scope["expected_change_repositories"].append("vllm-project/vllm")
        errors = self.validate_results(results)
        self.assertTrue(any("expected changes outside primary repository" in error for error in errors))

    def test_not_an_upstream_bug_is_valid_in_v3_and_legacy_name_is_not(self) -> None:
        results = load_fixture("screening-results-v3.yaml")
        candidate = results["excluded_after_audit"][0]
        candidate["screening_classification"] = "not-an-upstream-bug"
        self.assertEqual([], self.validate_results(results))
        candidate["screening_classification"] = "not-a-kubernetes-bug"
        self.assertTrue(any("unknown classification" in error for error in self.validate_results(results)))

    def test_historical_pr_does_not_block_available_admission(self) -> None:
        results, _ = self.available_result(gate_status="passed")
        self.assertEqual([], self.validate_results(results))

    def test_competing_open_pr_blocks_admission(self) -> None:
        results, candidate = self.available_result(gate_status="passed")
        item = candidate["related_items"][0]
        item.update(
            relationship="competing-implementation",
            state="open",
            blocks_contribution=True,
        )
        errors = self.validate_results(results)
        self.assertTrue(any("blocking related_items" in error for error in errors))

    def test_scope_expansion_blocks_admission(self) -> None:
        results, candidate = self.available_result(gate_status="passed")
        candidate["repository_scope"]["scope_status"] = "scope-expansion-required"
        errors = self.validate_results(results)
        self.assertTrue(any("scope expansion is required" in error for error in errors))

    def test_no_known_owner_conflicts_with_active_implementation_signal(self) -> None:
        results, candidate = self.available_result()
        candidate["ownership"]["signals"] = [
            {
                "actor": "contributor",
                "actor_role": "community-contributor",
                "type": "comment",
                "strength": "implementation-in-progress",
                "active": True,
                "summary": "Has a local fix.",
                "url": "https://example.invalid/comment",
                "observed_at": "2026-08-03T00:00:00Z",
            }
        ]
        errors = self.validate_results(results)
        self.assertTrue(any("conflicts with an active ownership signal" in error for error in errors))

    def test_evidence_collection_forbids_results_and_classification(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            record = Path(temporary)
            (record / "SCOPE.yaml").write_text(
                yaml.safe_dump(scope("issue-evidence-collection"), sort_keys=False),
                encoding="utf-8",
            )
            (record / "REPORT.md").write_text("# evidence\n", encoding="utf-8")
            evidence_directory = record / "evidence"
            evidence_directory.mkdir()
            evidence = yaml.safe_load(
                (ROOT / "templates" / "evidence" / "ISSUE-EVIDENCE.yaml").read_text(encoding="utf-8")
            )
            evidence.update(
                repository="LMCache/LMCache",
                issue="LMCache/LMCache#123",
                url="https://github.com/LMCache/LMCache/issues/123",
                title="Evidence fixture",
                collected_at="2026-08-03T00:00:00Z",
            )
            (evidence_directory / "123.yaml").write_text(
                yaml.safe_dump(evidence, sort_keys=False), encoding="utf-8"
            )
            self.assertEqual([], screening_validator.validate(record))
            evidence["screening_classification"] = "available"
            (evidence_directory / "123.yaml").write_text(
                yaml.safe_dump(evidence, sort_keys=False), encoding="utf-8"
            )
            self.assertTrue(any("forbids classification" in error for error in screening_validator.validate(record)))


class ProfileAndIssueRecordTests(unittest.TestCase):
    def test_lmcache_branch_fixture_keeps_default_and_contribution_targets(self) -> None:
        project = load_fixture("project.yaml")
        self.assertEqual([], issue_validator.validate_project(FIXTURES / "project.yaml"))
        self.assertEqual("main", project["branches"]["github_default_branch"])
        self.assertEqual("dev", project["branches"]["contribution_target_branch"])

    def test_all_profiles_follow_contract(self) -> None:
        profiles_root = (
            ROOT / ".agents" / "skills" / "harvest-open-source-issue" / "references" / "profiles"
        )
        profile_paths = sorted(path for path in profiles_root.rglob("*.yaml") if path.name != "schema.yaml")
        self.assertEqual(5, len(profile_paths))
        for path in profile_paths:
            profile = yaml.safe_load(path.read_text(encoding="utf-8"))
            with self.subTest(path=path):
                self.assertEqual(1, profile.get("schema_version"))
                self.assertIn(profile.get("kind"), {"language", "ecosystem", "repository"})
                for key in ("name", "match", "checks", "limitations"):
                    self.assertIn(key, profile)

    def test_profile_precedence_puts_live_instructions_last(self) -> None:
        schema_path = (
            ROOT / ".agents" / "skills" / "harvest-open-source-issue" / "references" / "profiles" / "schema.yaml"
        )
        schema = yaml.safe_load(schema_path.read_text(encoding="utf-8"))
        self.assertEqual("repository-live-instructions", schema["profile_contract"]["precedence"][-1])

    def test_required_gpu_layer_cannot_be_not_applicable(self) -> None:
        project = load_fixture("project.yaml")
        project["verification_matrix"]["gpu_single"]["status"] = "not-applicable"
        with tempfile.TemporaryDirectory() as temporary:
            path = Path(temporary) / "PROJECT.yaml"
            path.write_text(yaml.safe_dump(project, sort_keys=False), encoding="utf-8")
            errors = issue_validator.validate_project(path)
        self.assertTrue(any("cannot be required and not-applicable" in error for error in errors))


class TargetRepositoryManagementTests(unittest.TestCase):
    def test_registry_yaml_parses_without_absolute_paths(self) -> None:
        registry, discovery = repository_discovery.load_documents()
        self.assertEqual(1, registry["schema_version"])
        self.assertIn("LMCache/LMCache", registry["repositories"])
        self.assertEqual(1, discovery["schema_version"])
        self.assertEqual([], protocol_validator.validate_repository_registry(ROOT))

    def test_repository_discovery_matches_upstream_and_fork_remotes(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            home = Path(temporary)
            repository = home / "projects" / "LMCache"
            repository.mkdir(parents=True)
            subprocess.run(["git", "-C", str(repository), "init", "-q"], check=True)
            subprocess.run(
                ["git", "-C", str(repository), "remote", "add", "upstream", "https://github.com/LMCache/LMCache.git"],
                check=True,
            )
            subprocess.run(
                ["git", "-C", str(repository), "remote", "add", "origin", "git@github.com:bzsuni/LMCache.git"],
                check=True,
            )
            registry = {
                "repositories": {
                    "LMCache/LMCache": {
                        "upstream": {"url": "https://github.com/LMCache/LMCache"}
                    }
                }
            }
            discovery = {"scan_roots": ["projects"]}
            results = repository_discovery.discover(registry, discovery, home=home)
            self.assertEqual(1, len(results))
            self.assertEqual("LMCache/LMCache", results[0]["repository"])
            self.assertEqual("git@github.com:bzsuni/LMCache.git", results[0]["fork"])
            self.assertEqual(str(repository), results[0]["local_path"])

    def test_git_identity_mismatch_is_detected(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            repository = Path(temporary)
            subprocess.run(["git", "-C", str(repository), "init", "-q"], check=True)
            subprocess.run(
                ["git", "-C", str(repository), "config", "user.name", "someone-else"],
                check=True,
            )
            subprocess.run(
                ["git", "-C", str(repository), "config", "user.email", "other@example.com"],
                check=True,
            )
            self.assertFalse(
                repository_discovery.identity_matches(
                    repository,
                    {"name": "bzsuni", "email": "bingzhe.sun@daocloud.io"},
                )
            )

    def test_registry_absolute_path_is_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            repositories = root / "repositories"
            repositories.mkdir()
            registry = copy.deepcopy(repository_discovery.load_documents()[0])
            registry["repositories"]["LMCache/LMCache"]["local"]["path"] = "/home/sun/py/LMCache"
            (repositories / "registry.yaml").write_text(
                yaml.safe_dump(registry, sort_keys=False), encoding="utf-8"
            )
            (repositories / "discovery.yaml").write_text(
                yaml.safe_dump(repository_discovery.load_documents()[1], sort_keys=False),
                encoding="utf-8",
            )
            errors = protocol_validator.validate_repository_registry(root)
            self.assertTrue(any("absolute path" in error for error in errors))


if __name__ == "__main__":
    unittest.main()
