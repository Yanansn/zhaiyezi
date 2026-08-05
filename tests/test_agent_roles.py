from __future__ import annotations

import shutil
import tempfile
import unittest
from datetime import datetime, timezone
from pathlib import Path

import yaml

from scripts import validate_agent_protocol as validator


ROOT = Path(__file__).resolve().parents[1]
NOW = datetime(2026, 8, 5, 12, 0, tzinfo=timezone.utc)


def current_request(task_id: str, assigned_agent: str, **updates: object) -> dict:
    value = {
        "schema_version": 2,
        "task_id": task_id,
        "task_type": "code-verification",
        "created_by": assigned_agent,
        "decision_author": assigned_agent,
        "materialized_by": assigned_agent,
        "assigned_agent": assigned_agent,
        "repository": "example/example",
        "issue": None,
        "status": "ready",
        "input_refs": ["AGENTS.md"],
        "goal": "Exercise the multi-agent contract.",
        "allowed_actions": ["read_repository", "write_result", "write_report"],
        "prohibited_actions": ["upstream_write", "create_pull_request"],
        "expected_outputs": [
            f"agent-work/tasks/{task_id}/RESULT.yaml",
            f"agent-work/tasks/{task_id}/REPORT.md",
            f"agent-work/tasks/{task_id}/DECISION.yaml",
        ],
        "completion": {"criteria": ["A decision validates."], "validation": [], "handoff": {"next_stage": "decision", "recommended_agent": "agent:luna", "message": "Switch to the recommended Agent before continuing."}},
        "approval_required": False,
    }
    value.update(updates)
    return value


def current_result(task_id: str, agent: str, **updates: object) -> dict:
    value = {
        "schema_version": 2,
        "task_id": task_id,
        "created_by": agent,
        "decision_author": agent,
        "materialized_by": agent,
        "status": "decision",
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


def decision(task_id: str, agent: str = "agent:luna", **updates: object) -> dict:
    value = {
        "schema_version": 2,
        "task_id": task_id,
        "created_by": agent,
        "decision_author": agent,
        "materialized_by": agent,
        "status": "completed",
        "result_ref": "RESULT.yaml",
        "result_revision": 1,
        "conclusion": "Continue within the bounded workflow.",
        "confidence": "medium",
        "evidence_refs": ["RESULT.yaml"],
        "risks": [],
        "next_action": "Await the next bounded task.",
    }
    value.update(updates)
    return value


class AgentRoleTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temporary = tempfile.TemporaryDirectory()
        self.root = Path(self.temporary.name)
        shutil.copytree(ROOT / "agent-protocol", self.root / "agent-protocol")
        shutil.copytree(ROOT / "agents", self.root / "agents")
        (self.root / "agent-work" / "tasks").mkdir(parents=True)
        errors: list[str] = []
        self.schema, self.permissions, self.state_machine = validator.protocol_documents(self.root, errors)
        self.assertEqual([], errors)

    def tearDown(self) -> None:
        self.temporary.cleanup()

    def write_task(self, request_data: dict, result_data: dict | None = None, decision_data: dict | None = None) -> Path:
        task = self.root / "agent-work" / "tasks" / request_data["task_id"]
        task.mkdir()
        (task / "REQUEST.yaml").write_text(yaml.safe_dump(request_data, sort_keys=False), encoding="utf-8")
        if result_data:
            (task / "RESULT.yaml").write_text(yaml.safe_dump(result_data, sort_keys=False), encoding="utf-8")
            (task / "REPORT.md").write_text("# Report\n", encoding="utf-8")
        if decision_data:
            (task / "DECISION.yaml").write_text(yaml.safe_dump(decision_data, sort_keys=False), encoding="utf-8")
        return task

    def inspect(self, task: Path):
        return validator.inspect_task_directory(task, self.schema, self.permissions, now=NOW)

    def test_luna_can_generate_decision(self) -> None:
        task_id = "luna-decision"
        record, errors = self.inspect(self.write_task(
            current_request(task_id, "agent:luna"),
            current_result(task_id, "agent:luna"),
            decision(task_id),
        ))
        self.assertEqual([], errors)
        self.assertEqual("completed", record.status)

    def test_terra_can_run_bounded_implementation(self) -> None:
        task_id = "terra-implementation"
        request = current_request(
            task_id, "agent:terra", task_type="implementation",
            allowed_actions=["read_repository", "repository_modify", "run_tests", "write_result", "write_report", "commit_facts_repository"],
            prohibited_actions=["upstream_write", "create_pull_request"],
            target_repository={"name": "example/example", "phase": "implementation", "fork": {"url": "git@example/fork.git"}, "local": {"path": "/tmp/example", "discovery": True}},
        )
        _, errors = self.inspect(self.write_task(request))
        self.assertEqual([], errors)

    def test_sol_can_only_escalate(self) -> None:
        errors = validator.validate_change_set(
            [{"actor": "agent:sol", "action": "repository_modify", "path": "agent-work/tasks/x/RESULT.yaml"}],
            self.permissions,
        )
        self.assertTrue(any("cannot perform action 'repository_modify'" in error for error in errors))

    def test_pull_request_requires_user_approval(self) -> None:
        request = current_request(
            "pr-without-approval", "agent:terra", task_type="publication",
            approval_required=True,
            allowed_actions=["create_pull_request"],
            prohibited_actions=[],
        )
        _, errors = self.inspect(self.write_task(request))
        self.assertTrue(any("protected actions require current user APPROVAL.yaml" in error for error in errors))

    def test_agent_decision_replaces_chat_review(self) -> None:
        task_id = "decision-without-review"
        task = self.write_task(
            current_request(task_id, "agent:terra"),
            current_result(task_id, "agent:terra"),
            decision(task_id, "agent:terra"),
        )
        record, errors = self.inspect(task)
        self.assertEqual([], errors)
        self.assertEqual("completed", record.status)
        self.assertFalse((task / "REVIEW.yaml").exists())


if __name__ == "__main__":
    unittest.main()
