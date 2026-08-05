from __future__ import annotations

import shutil
import tempfile
import unittest
from pathlib import Path

import yaml

from scripts import agent_queue
from scripts import validate_agent_protocol as validator


ROOT = Path(__file__).resolve().parents[1]


def request(task_id: str = "test-task", agent: str = "agent:terra", **updates: object) -> dict:
    value = {
        "schema_version": 2,
        "task_id": task_id,
        "task_type": "implementation",
        "created_by": agent,
        "decision_author": agent,
        "materialized_by": agent,
        "assigned_agent": agent,
        "repository": "example/example",
        "issue": None,
        "status": "ready",
        "input_refs": ["AGENTS.md"],
        "goal": "Exercise the current Agent task contract.",
        "allowed_actions": ["read_repository", "write_result", "write_report"],
        "prohibited_actions": ["upstream_write", "create_pull_request"],
        "expected_outputs": [f"agent-work/tasks/{task_id}/RESULT.yaml", f"agent-work/tasks/{task_id}/REPORT.md"],
        "completion": {"criteria": ["The task validates."], "validation": [], "handoff": "Agent decision."},
        "approval_required": False,
        "target_repository": {"name": "example/example", "phase": "implementation", "fork": {"url": "git@example/fork.git"}, "local": {"path": "/tmp/example", "discovery": True}},
    }
    value.update(updates)
    return value


def result(task_id: str = "test-task", agent: str = "agent:terra", **updates: object) -> dict:
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


def decision(task_id: str = "test-task", agent: str = "agent:terra", **updates: object) -> dict:
    value = {
        "schema_version": 2,
        "task_id": task_id,
        "created_by": agent,
        "decision_author": agent,
        "materialized_by": agent,
        "status": "completed",
        "result_ref": "RESULT.yaml",
        "result_revision": 1,
        "conclusion": "The bounded task is complete.",
        "confidence": "high",
        "evidence_refs": ["RESULT.yaml"],
        "risks": [],
        "next_action": "Await the next task.",
    }
    value.update(updates)
    return value


class AgentProtocolTests(unittest.TestCase):
    def setUp(self) -> None:
        errors: list[str] = []
        self.schema, self.permissions, self.state_machine = validator.protocol_documents(ROOT, errors)
        self.assertEqual([], errors)
        self.temporary = tempfile.TemporaryDirectory()
        self.root = Path(self.temporary.name)
        shutil.copytree(ROOT / "agent-protocol", self.root / "agent-protocol")
        shutil.copytree(ROOT / "agents", self.root / "agents")
        (self.root / "agent-work" / "tasks").mkdir(parents=True)

    def tearDown(self) -> None:
        self.temporary.cleanup()

    def write_task(self, request_data: dict, result_data: dict | None = None, decision_data: dict | None = None) -> Path:
        task = self.root / "agent-work" / "tasks" / request_data["task_id"]
        task.mkdir()
        (task / "REQUEST.yaml").write_text(yaml.safe_dump(request_data, sort_keys=False), encoding="utf-8")
        if result_data is not None:
            (task / "RESULT.yaml").write_text(yaml.safe_dump(result_data, sort_keys=False), encoding="utf-8")
            (task / "REPORT.md").write_text("# Report\n", encoding="utf-8")
        if decision_data is not None:
            (task / "DECISION.yaml").write_text(yaml.safe_dump(decision_data, sort_keys=False), encoding="utf-8")
        return task

    def inspect(self, task: Path):
        return validator.inspect_task_directory(task, self.schema, self.permissions)

    def test_protocol_documents_are_current(self) -> None:
        errors: list[str] = []
        validator.validate_protocol_documents(self.schema, self.permissions, self.state_machine, errors)
        self.assertEqual([], errors)

    def test_current_task_validates(self) -> None:
        record, errors = self.inspect(self.write_task(request(), result(), decision()))
        self.assertEqual([], errors)
        self.assertEqual("completed", record.status)

    def test_luna_can_produce_decision(self) -> None:
        task_id = "luna-decision"
        record, errors = self.inspect(self.write_task(request(task_id, "agent:luna", task_type="deep-audit", repository="example/example", issue="example/example#1", evidence_refs=["evidence.yaml"], target_repository={"name": "example/example", "phase": "deep-audit"}), result(task_id, "agent:luna"), decision(task_id, "agent:luna")))
        self.assertEqual([], errors)
        self.assertEqual("completed", record.status)

    def test_review_yaml_is_rejected(self) -> None:
        task = self.write_task(request())
        (task / "REVIEW.yaml").write_text("removed: true\n", encoding="utf-8")
        _, errors = self.inspect(task)
        self.assertTrue(any("removed; use DECISION.yaml" in error for error in errors))

    def test_protected_action_requires_user_approval(self) -> None:
        data = request(allowed_actions=["create_pull_request"], prohibited_actions=[], approval_required=True)
        _, errors = self.inspect(self.write_task(data))
        self.assertTrue(any("protected actions require" in error for error in errors))

    def test_sol_cannot_modify_repository(self) -> None:
        errors = validator.validate_change_set([{"actor": "agent:sol", "action": "repository_modify", "path": "agent-work/tasks/x/RESULT.yaml"}], self.permissions)
        self.assertTrue(any("cannot perform action" in error for error in errors))

    def test_current_lifecycle_has_no_review_state(self) -> None:
        self.assertNotIn("awaiting-review", self.state_machine["queue_artifact_state"]["states"])
        self.assertEqual([], validator.validate_transition(self.state_machine, "decision", "implementation"))

    def test_queue_has_only_current_agent_choices(self) -> None:
        records, errors = agent_queue.load_queue(self.root)
        self.assertEqual([], errors)
        self.assertEqual([], records)

    def test_repository_protocol_validates(self) -> None:
        self.assertEqual([], validator.validate(ROOT))


if __name__ == "__main__":
    unittest.main()
