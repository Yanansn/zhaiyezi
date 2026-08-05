from __future__ import annotations

from datetime import datetime, timezone
import shutil
import tempfile
import unittest
from pathlib import Path

import yaml

from scripts import agent_queue
from scripts import validate_agent_protocol as validator


ROOT = Path(__file__).resolve().parents[1]
NOW = datetime(2026, 8, 3, 12, 0, tzinfo=timezone.utc)


def protocol(root: Path = ROOT) -> tuple[dict, dict, dict]:
    errors: list[str] = []
    documents = validator.protocol_documents(root, errors)
    if errors:
        raise AssertionError(errors)
    return documents


def request(task_id: str = "test-task", **updates: object) -> dict:
    value = {
        "schema_version": 1,
        "task_id": task_id,
        "task_type": "example",
        "created_by": "chat",
        "decision_author": "chat",
        "materialized_by": "chat",
        "assigned_agent": "codex",
        "repository": "example/example",
        "issue": None,
        "status": "ready",
        "created_at": "2026-08-03T00:00:00Z",
        "priority": "normal",
        "input_refs": ["AGENTS.md"],
        "goal": "Exercise the repository-backed task contract.",
        "allowed_actions": ["read_repository", "write_result", "write_report"],
        "prohibited_actions": ["upstream_write", "create_pull_request"],
        "expected_outputs": [
            f"agent-work/tasks/{task_id}/RESULT.yaml",
            f"agent-work/tasks/{task_id}/REPORT.md",
        ],
        "completion": {
            "criteria": ["The result validates."],
            "validation": ["python3 scripts/validate_agent_protocol.py"],
            "handoff": "Chat reviews RESULT.yaml.",
        },
    }
    value.update(updates)
    return value


def result(task_id: str = "test-task", **updates: object) -> dict:
    value = {
        "schema_version": 1,
        "task_id": task_id,
        "created_by": "codex",
        "decision_author": "codex",
        "materialized_by": "codex",
        "status": "active",
        "revision": 1,
        "request_ref": "REQUEST.yaml",
        "outputs": ["REPORT.md"],
        "actions_performed": ["read_repository", "write_result", "write_report"],
        "actions_not_performed": ["upstream_write"],
        "validation": [],
        "limitations": [],
    }
    value.update(updates)
    return value


def review(task_id: str = "test-task", **updates: object) -> dict:
    value = {
        "schema_version": 1,
        "task_id": task_id,
        "created_by": "chat",
        "decision_author": "chat",
        "materialized_by": "chat",
        "status": "completed",
        "result_ref": "RESULT.yaml",
        "result_revision": 1,
        "decision": "approved",
        "findings": [],
        "next_actions": [],
    }
    value.update(updates)
    return value


class AgentProtocolTests(unittest.TestCase):
    def setUp(self) -> None:
        self.schema, self.permissions, self.state_machine = protocol()
        self.temporary = tempfile.TemporaryDirectory()
        self.root = Path(self.temporary.name)
        shutil.copytree(ROOT / "agent-protocol", self.root / "agent-protocol")
        (self.root / "agent-work" / "tasks").mkdir(parents=True)

    def tearDown(self) -> None:
        self.temporary.cleanup()

    def write_task(
        self,
        request_data: dict,
        result_data: dict | None = None,
        review_data: dict | None = None,
        approval_data: dict | None = None,
    ) -> Path:
        task = self.root / "agent-work" / "tasks" / request_data["task_id"]
        task.mkdir(parents=True, exist_ok=True)
        (task / "REQUEST.yaml").write_text(
            yaml.safe_dump(request_data, sort_keys=False), encoding="utf-8"
        )
        if result_data is not None:
            (task / "RESULT.yaml").write_text(
                yaml.safe_dump(result_data, sort_keys=False), encoding="utf-8"
            )
            (task / "REPORT.md").write_text("# Execution report\n", encoding="utf-8")
        if review_data is not None:
            (task / "REVIEW.yaml").write_text(
                yaml.safe_dump(review_data, sort_keys=False), encoding="utf-8"
            )
        if approval_data is not None:
            (task / "APPROVAL.yaml").write_text(
                yaml.safe_dump(approval_data, sort_keys=False), encoding="utf-8"
            )
        return task

    def inspect(self, task: Path) -> tuple[validator.TaskRecord | None, list[str]]:
        return validator.inspect_task_directory(
            task, self.schema, self.permissions, now=NOW
        )

    def standing_authorization(self, **updates: object) -> dict:
        value = yaml.safe_load(
            (ROOT / "agent-protocol" / "examples" / "standing-authorization.yaml")
            .read_text(encoding="utf-8")
        )
        value.pop("template_only")
        value.update(updates)
        return value

    @staticmethod
    def delegated_materialization(summary: str = "User supplied the complete artifact.") -> dict:
        return {
            "authority": "user-instruction",
            "scope": "bounded",
            "source_summary": summary,
        }

    def test_protocol_example_is_not_in_queue_next(self) -> None:
        records, errors = agent_queue.load_queue(self.root)
        self.assertEqual([], errors)
        self.assertIsNone(agent_queue.next_task(records, "codex"))

    def test_ready_codex_task_is_returned_by_next(self) -> None:
        self.write_task(request())
        records, errors = agent_queue.load_queue(self.root)
        self.assertEqual([], errors)
        self.assertEqual("test-task", agent_queue.next_task(records, "codex").request["task_id"])

    def test_chat_task_is_not_returned_to_codex(self) -> None:
        self.write_task(request(assigned_agent="chat"))
        records, errors = agent_queue.load_queue(self.root)
        self.assertEqual([], errors)
        self.assertIsNone(agent_queue.next_task(records, "codex"))

    def test_queue_sorting_is_deterministic(self) -> None:
        requests = [
            request("normal", priority="normal", created_at="2026-08-01T00:00:00Z"),
            request("high-late", priority="high", created_at="2026-08-02T00:00:00Z"),
            request("high-a", priority="high", created_at="2026-08-01T00:00:00Z"),
            request("high-b", priority="high", created_at="2026-08-01T00:00:00Z"),
        ]
        for value in reversed(requests):
            self.write_task(value)
        records, errors = agent_queue.load_queue(self.root)
        self.assertEqual([], errors)
        self.assertEqual(
            ["high-a", "high-b", "high-late", "normal"],
            [record.request["task_id"] for record in records],
        )

    def test_fixed_directory_does_not_move_request(self) -> None:
        task = self.write_task(request())
        request_path = task / "REQUEST.yaml"
        before = request_path.read_text(encoding="utf-8")
        (task / "RESULT.yaml").write_text(
            yaml.safe_dump(result(status="review"), sort_keys=False), encoding="utf-8"
        )
        (task / "REPORT.md").write_text("# Execution report\n", encoding="utf-8")
        record, errors = self.inspect(task)
        self.assertEqual([], errors)
        self.assertEqual("awaiting-review", record.status)
        self.assertEqual(before, request_path.read_text(encoding="utf-8"))

    def test_result_review_derives_awaiting_review(self) -> None:
        record, errors = self.inspect(
            self.write_task(request(), result(status="review"))
        )
        self.assertEqual([], errors)
        self.assertEqual("awaiting-review", record.status)

    def test_result_requires_codex_provenance(self) -> None:
        _, errors = self.inspect(
            self.write_task(request(), result(decision_author="chat"))
        )
        self.assertTrue(any("decision_author: must be codex" in error for error in errors))

    def test_approved_review_derives_completed(self) -> None:
        record, errors = self.inspect(
            self.write_task(request(), result(status="review"), review())
        )
        self.assertEqual([], errors)
        self.assertEqual("completed", record.status)

    def test_changes_requested_derives_correctly(self) -> None:
        requested = review(status="changes-requested", decision="changes-requested")
        record, errors = self.inspect(
            self.write_task(request(), result(status="review"), requested)
        )
        self.assertEqual([], errors)
        self.assertEqual("changes-requested", record.status)

    def test_new_result_revision_preserves_changes_requested_review(self) -> None:
        requested = review(status="changes-requested", decision="changes-requested")
        revised = result(revision=2, status="review", supersedes_review="REVIEW.yaml")
        record, errors = self.inspect(self.write_task(request(), revised, requested))
        self.assertEqual([], errors)
        self.assertEqual("awaiting-review", record.status)

    def test_result_cannot_declare_completed_without_review(self) -> None:
        _, errors = self.inspect(self.write_task(request(), result(status="completed")))
        self.assertTrue(any("invalid result status" in error for error in errors))

    def test_chat_cannot_modify_result(self) -> None:
        errors = validator.validate_change_set(
            [{"actor": "chat", "path": "agent-work/tasks/test-task/RESULT.yaml"}],
            self.permissions,
        )
        self.assertTrue(any("cannot modify" in error for error in errors))

    def test_codex_cannot_modify_request(self) -> None:
        errors = validator.validate_change_set(
            [{"actor": "codex", "path": "agent-work/tasks/test-task/REQUEST.yaml"}],
            self.permissions,
        )
        self.assertTrue(any("cannot modify" in error for error in errors))

    def test_chat_authored_chat_materialized_request_is_valid(self) -> None:
        _, errors = self.inspect(self.write_task(request()))
        self.assertEqual([], errors)

    def test_chat_authored_codex_materialized_request_is_valid(self) -> None:
        request_data = request(
            materialized_by="codex",
            materialization=self.delegated_materialization(),
        )
        task = self.write_task(request_data)
        _, errors = validator.inspect_task_directory(
            task,
            self.schema,
            self.permissions,
            [self.standing_authorization()],
            now=NOW,
        )
        self.assertEqual([], errors)

    def test_codex_cannot_be_request_decision_author(self) -> None:
        _, errors = self.inspect(
            self.write_task(request(decision_author="codex"))
        )
        self.assertTrue(any("decision_author: must be chat" in error for error in errors))

    def test_codex_materialized_request_requires_provenance(self) -> None:
        task = self.write_task(request(materialized_by="codex"))
        _, errors = validator.inspect_task_directory(
            task,
            self.schema,
            self.permissions,
            [self.standing_authorization()],
            now=NOW,
        )
        self.assertTrue(any("materialization: required" in error for error in errors))

    def test_legacy_request_without_provenance_has_migration_errors(self) -> None:
        request_data = request()
        request_data.pop("decision_author")
        request_data.pop("materialized_by")
        _, errors = self.inspect(self.write_task(request_data))
        self.assertTrue(any("missing required field decision_author" in error for error in errors))
        self.assertTrue(any("missing required field materialized_by" in error for error in errors))

    def test_materializer_must_be_a_legal_actor(self) -> None:
        _, errors = self.inspect(
            self.write_task(request(materialized_by="github-connector"))
        )
        self.assertTrue(any("materialized_by: must be one of" in error for error in errors))

    def test_codex_materialized_request_cannot_expand_protected_actions(self) -> None:
        request_data = request(
            materialized_by="codex",
            materialization=self.delegated_materialization(),
            allowed_actions=["create_pull_request"],
            prohibited_actions=[],
        )
        task = self.write_task(request_data)
        _, errors = validator.inspect_task_directory(
            task,
            self.schema,
            self.permissions,
            [self.standing_authorization()],
            now=NOW,
        )
        self.assertTrue(any("create_pull_request requires" in error for error in errors))

    def test_codex_can_structurally_materialize_chat_path_only_with_action(self) -> None:
        path = "agent-work/tasks/test-task/REQUEST.yaml"
        allowed = validator.validate_change_set(
            [{"actor": "codex", "action": "materialize_chat_artifact", "path": path}],
            self.permissions,
        )
        denied = validator.validate_change_set(
            [{"actor": "codex", "path": path}], self.permissions
        )
        self.assertEqual([], allowed)
        self.assertTrue(any("cannot modify" in error for error in denied))

    def test_valid_standing_authorization_allows_facts_push(self) -> None:
        authorization = self.standing_authorization()
        allowed = validator.standing_authorizes(
            authorization,
            "codex",
            "push_facts_repository",
            ["agent-work/tasks/test-task/RESULT.yaml"],
            "Yanansn/zhaiyezi",
            "main",
            now=NOW,
        )
        self.assertTrue(allowed)

        request_data = request(
            allowed_actions=["push_facts_repository"],
            expected_outputs=["agent-work/tasks/test-task/RESULT.yaml"],
        )
        task = self.write_task(request_data)
        _, errors = validator.inspect_task_directory(
            task,
            self.schema,
            self.permissions,
            [authorization],
            now=NOW,
        )
        self.assertEqual([], errors)

    def test_protected_action_requires_task_or_standing_authorization(self) -> None:
        request_data = request(
            allowed_actions=["create_pull_request"],
            prohibited_actions=[],
        )
        task = self.write_task(request_data)
        _, errors = self.inspect(task)
        self.assertTrue(any("requires current task approval" in error for error in errors))

        approval = {
            "schema_version": 1,
            "task_id": "test-task",
            "approved_by": "user",
            "decision_author": "user",
            "materialized_by": "user",
            "status": "approved",
            "actions": ["create_pull_request"],
            "scope": "Only this task and this PR creation.",
        }
        self.write_task(request_data, approval_data=approval)
        _, errors = self.inspect(task)
        self.assertEqual([], errors)

    def test_chat_review_may_be_materialized_by_codex(self) -> None:
        review_data = review(
            materialized_by="codex",
            materialization=self.delegated_materialization(
                "User instructed Codex to record Chat's approved Review."
            ),
        )
        task = self.write_task(request(), result(status="review"), review_data)
        record, errors = validator.inspect_task_directory(
            task,
            self.schema,
            self.permissions,
            [self.standing_authorization()],
            now=NOW,
        )
        self.assertEqual([], errors)
        self.assertEqual("completed", record.status)

    def test_codex_cannot_be_review_decision_author(self) -> None:
        review_data = review(decision_author="codex")
        _, errors = self.inspect(
            self.write_task(request(), result(status="review"), review_data)
        )
        self.assertTrue(any("decision_author: must be chat" in error for error in errors))

    def test_codex_materialized_review_cannot_modify_request_permissions(self) -> None:
        review_data = review(
            materialized_by="codex",
            materialization=self.delegated_materialization(),
            allowed_actions=["create_pull_request"],
        )
        task = self.write_task(request(), result(status="review"), review_data)
        _, errors = validator.inspect_task_directory(
            task,
            self.schema,
            self.permissions,
            [self.standing_authorization()],
            now=NOW,
        )
        self.assertTrue(any("cannot modify REQUEST permissions" in error for error in errors))

    def test_user_approval_may_be_materialized_by_codex(self) -> None:
        request_data = request(
            allowed_actions=["create_pull_request"], prohibited_actions=[]
        )
        approval = {
            "schema_version": 1,
            "task_id": "test-task",
            "approved_by": "user",
            "decision_author": "user",
            "materialized_by": "codex",
            "materialization": self.delegated_materialization(
                "User explicitly approved this task's single PR creation action."
            ),
            "status": "approved",
            "actions": ["create_pull_request"],
            "scope": "Only this task and this PR creation.",
        }
        _, errors = self.inspect(
            self.write_task(request_data, approval_data=approval)
        )
        self.assertEqual([], errors)

    def test_codex_cannot_be_approval_decision_author(self) -> None:
        approval = {
            "schema_version": 1,
            "task_id": "test-task",
            "approved_by": "user",
            "decision_author": "codex",
            "materialized_by": "codex",
            "status": "approved",
            "actions": [],
            "scope": "No actions.",
        }
        _, errors = self.inspect(
            self.write_task(request(), approval_data=approval)
        )
        self.assertTrue(any("decision_author: must be user" in error for error in errors))

    def test_standing_authorization_rejects_path_mismatch(self) -> None:
        authorization = self.standing_authorization()
        self.assertFalse(
            validator.standing_authorizes(
                authorization, "codex", "push_facts_repository",
                ["registry/issues.yaml"], "Yanansn/zhaiyezi", "main", now=NOW,
            )
        )

    def test_standing_authorization_materializes_only_bounded_chat_paths(self) -> None:
        authorization = self.standing_authorization()
        self.assertTrue(
            validator.standing_authorizes(
                authorization,
                "codex",
                "materialize_chat_artifact",
                ["agent-work/tasks/test-task/REQUEST.yaml"],
                "Yanansn/zhaiyezi",
                "main",
                now=NOW,
            )
        )
        self.assertFalse(
            validator.standing_authorizes(
                authorization,
                "codex",
                "materialize_chat_artifact",
                ["registry/issues.yaml"],
                "Yanansn/zhaiyezi",
                "main",
                now=NOW,
            )
        )
        self.assertFalse(
            validator.standing_authorizes(
                authorization,
                "codex",
                "materialize_user_artifact",
                ["agent-work/tasks/test-task/APPROVAL.yaml"],
                "Yanansn/zhaiyezi",
                "main",
                now=NOW,
            )
        )
        self.assertFalse(
            validator.standing_authorizes(
                authorization,
                "codex",
                "materialize_chat_artifact",
                ["decisions/authorizations/new-approval.yaml"],
                "Yanansn/zhaiyezi",
                "main",
                now=NOW,
            )
        )

    def test_standing_authorization_star_does_not_cross_directory(self) -> None:
        authorization = self.standing_authorization()
        self.assertFalse(
            validator.standing_authorizes(
                authorization, "codex", "push_facts_repository",
                ["agent-work/tasks/test-task/nested/RESULT.yaml"],
                "Yanansn/zhaiyezi", "main", now=NOW,
            )
        )

    def test_standing_authorization_rejects_branch_mismatch(self) -> None:
        authorization = self.standing_authorization()
        self.assertFalse(
            validator.standing_authorizes(
                authorization, "codex", "push_facts_repository",
                ["screenings/example/REPORT.md"], "Yanansn/zhaiyezi", "feature", now=NOW,
            )
        )

    def test_standing_authorization_rejects_repository_mismatch(self) -> None:
        authorization = self.standing_authorization()
        self.assertFalse(
            validator.standing_authorizes(
                authorization, "codex", "push_facts_repository",
                ["screenings/example/REPORT.md"], "other/repository", "main", now=NOW,
            )
        )

    def test_revoked_and_expired_authorizations_are_rejected(self) -> None:
        revoked = self.standing_authorization(
            status="revoked",
            revocation={"supported": True, "revoked_at": "2026-08-03T01:00:00Z"},
        )
        expired = self.standing_authorization(expires_at="2026-08-03T02:00:00Z")
        for authorization in (revoked, expired):
            with self.subTest(status=authorization["status"]):
                self.assertFalse(
                    validator.standing_authorizes(
                        authorization, "codex", "push_facts_repository",
                        ["screenings/example/REPORT.md"],
                        "Yanansn/zhaiyezi", "main", now=NOW,
                    )
                )

    def test_standing_authorization_cannot_grant_pull_request(self) -> None:
        authorization = self.standing_authorization()
        authorization["grants"]["codex"]["actions"].append("create_pull_request")
        errors = validator.validate_standing_authorization(
            authorization,
            Path("decisions/authorizations/test.yaml"),
            self.schema,
            self.permissions,
            template=False,
            now=NOW,
        )
        self.assertTrue(any("cannot grant create_pull_request" in error for error in errors))

    def test_example_template_is_not_an_actual_authorization(self) -> None:
        errors: list[str] = []
        authorizations = validator.load_standing_authorizations(
            self.root, self.schema, self.permissions, errors, now=NOW
        )
        self.assertEqual([], errors)
        self.assertEqual([], authorizations)
        template = yaml.safe_load(
            (self.root / "agent-protocol/examples/standing-authorization.yaml")
            .read_text(encoding="utf-8")
        )
        self.assertFalse(
            validator.standing_authorizes(
                template, "codex", "push_facts_repository",
                ["screenings/example/REPORT.md"], "Yanansn/zhaiyezi", "main", now=NOW,
            )
        )

    def test_multi_agent_lifecycle_requires_analysis_and_decision(self) -> None:
        self.assertEqual(
            ["forbidden transition: candidate -> analysis"],
            validator.validate_transition(
                self.state_machine, "candidate", "analysis"
            ),
        )
        self.assertNotIn(
            "available", self.state_machine["contribution_coordination"]["states"]
        )
        self.assertEqual(
            ["forbidden transition: evidence -> implementation"],
            validator.validate_transition(
                self.state_machine, "evidence", "implementation"
            ),
        )
        self.assertEqual(
            ["forbidden transition: analysis -> implementation"],
            validator.validate_transition(
                self.state_machine, "analysis", "implementation"
            ),
        )

    def test_deep_audit_task_schema_is_first_class(self) -> None:
        self.assertIn("deep-audit", self.schema["enums"]["task_type"])
        self.assertEqual(
            ["evidence_refs"],
            self.schema["task_type_contracts"]["deep-audit"][
                "required_request_fields"
            ],
        )

    def test_validator_accepts_deep_audit_with_evidence_refs(self) -> None:
        task_request = request(
            task_id="deep-audit-task",
            task_type="deep-audit",
            repository="LMCache/LMCache",
            issue="LMCache/LMCache#4132",
            evidence_refs=[
                "agent-work/tasks/lmcache-4132-evidence/RESULT.yaml",
            ],
            target_repository={
                "name": "LMCache/LMCache",
                "phase": "deep-audit",
            },
            allowed_actions=[
                "read_repository",
                "analyze_code",
                "write_result",
                "write_report",
            ],
        )
        _, errors = self.inspect(self.write_task(task_request))
        self.assertEqual([], errors)

    def test_deep_audit_requires_evidence_refs(self) -> None:
        task_request = request(
            task_id="deep-audit-no-evidence",
            task_type="deep-audit",
            repository="LMCache/LMCache",
            issue="LMCache/LMCache#4132",
        )
        _, errors = self.inspect(self.write_task(task_request))
        self.assertTrue(any("evidence_refs" in error for error in errors))

    def test_deep_audit_requires_target_repository(self) -> None:
        task_request = request(
            task_id="deep-audit-no-target",
            task_type="deep-audit",
            repository="LMCache/LMCache",
            issue="LMCache/LMCache#4132",
            evidence_refs=["agent-work/tasks/lmcache-4132-evidence/RESULT.yaml"],
        )
        _, errors = self.inspect(self.write_task(task_request))
        self.assertTrue(any("target_repository" in error for error in errors))

    def test_deep_audit_cannot_transition_directly_to_implementation(self) -> None:
        self.assertEqual(
            ["forbidden transition: analysis -> implementation"],
            validator.validate_transition(
                self.state_machine, "analysis", "implementation"
            ),
        )
        self.assertEqual(
            [],
            validator.validate_transition(
                self.state_machine, "decision", "implementation"
            ),
        )

    def test_deep_audit_cannot_allow_upstream_permission(self) -> None:
        task_request = request(
            task_id="deep-audit-upstream",
            task_type="deep-audit",
            repository="LMCache/LMCache",
            issue="LMCache/LMCache#4132",
            evidence_refs=["agent-work/tasks/lmcache-4132-evidence/RESULT.yaml"],
            allowed_actions=["upstream_write"],
            prohibited_actions=[],
        )
        _, errors = self.inspect(self.write_task(task_request))
        self.assertTrue(any("deep-audit cannot allow" in error for error in errors))

    def test_implementation_requires_fork_and_local_discovery(self) -> None:
        task_request = request(
            task_id="implementation-without-binding",
            task_type="implementation",
            repository="LMCache/LMCache",
            issue="LMCache/LMCache#4132",
        )
        _, errors = self.inspect(self.write_task(task_request))
        self.assertTrue(any("target_repository" in error for error in errors))

        task_request["target_repository"] = {
            "name": "LMCache/LMCache",
            "phase": "implementation",
            "fork": {"url": "git@github.com:user/LMCache.git"},
            "local": {"path": "/tmp/lmcache", "discovery": False},
        }
        _, errors = self.inspect(self.write_task(task_request))
        self.assertTrue(any("must be true" in error for error in errors))

    def test_target_binding_does_not_authorize_upstream_write(self) -> None:
        task_request = request(
            task_id="bound-upstream-write",
            task_type="deep-audit",
            repository="LMCache/LMCache",
            issue="LMCache/LMCache#4132",
            evidence_refs=["agent-work/tasks/lmcache-4132-evidence/RESULT.yaml"],
            target_repository={"name": "LMCache/LMCache", "phase": "deep-audit"},
            allowed_actions=["upstream_write"],
            prohibited_actions=[],
        )
        _, errors = self.inspect(self.write_task(task_request))
        self.assertTrue(any("deep-audit cannot allow" in error for error in errors))

    def test_repository_modify_requires_user_approval(self) -> None:
        task_request = request(
            task_id="repository-modify-without-approval",
            task_type="implementation",
            repository="LMCache/LMCache",
            issue="LMCache/LMCache#4132",
            target_repository={
                "name": "LMCache/LMCache",
                "phase": "implementation",
                "fork": {"url": "git@github.com:user/LMCache.git"},
                "local": {"path": "/tmp/lmcache", "discovery": True},
            },
            allowed_actions=["repository_modify"],
            prohibited_actions=[],
        )
        _, errors = self.inspect(self.write_task(task_request))
        self.assertTrue(any("repository_modify requires" in error for error in errors))

    def test_legacy_queue_task_has_clear_migration_error(self) -> None:
        legacy = self.root / "agent-work" / "inbox" / "legacy-task"
        legacy.mkdir(parents=True)
        (legacy / "REQUEST.yaml").write_text("task_id: legacy-task\n", encoding="utf-8")
        errors = validator.legacy_queue_errors(self.root)
        self.assertTrue(any("legacy queue task detected" in error for error in errors))
        self.assertTrue(any("agent-work/tasks/legacy-task" in error for error in errors))

    def test_invalid_queue_task_is_reported_not_silently_skipped(self) -> None:
        task = self.root / "agent-work/tasks/broken"
        task.mkdir()
        (task / "REQUEST.yaml").write_text("task_id: different\n", encoding="utf-8")
        records, errors = agent_queue.load_queue(self.root)
        self.assertEqual([], records)
        self.assertTrue(any("REQUEST.yaml" in error for error in errors))

    def test_repository_protocol_validates(self) -> None:
        self.assertEqual([], validator.validate(ROOT, now=NOW))


if __name__ == "__main__":
    unittest.main()
