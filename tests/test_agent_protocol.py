from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

import yaml

from scripts import validate_agent_protocol as validator


ROOT = Path(__file__).resolve().parents[1]


def protocol() -> tuple[dict, dict, dict]:
    errors: list[str] = []
    documents = validator.protocol_documents(ROOT, errors)
    if errors:
        raise AssertionError(errors)
    return documents


def request(**updates: object) -> dict:
    value = {
        "schema_version": 1,
        "task_id": "test-task",
        "task_type": "example",
        "created_by": "chat",
        "assigned_agent": "codex",
        "repository": "example/example",
        "issue": None,
        "status": "ready",
        "input_refs": ["AGENTS.md"],
        "goal": "Exercise the repository-backed task contract.",
        "allowed_actions": ["read_repository", "write_result", "write_report"],
        "prohibited_actions": ["upstream_write", "create_pull_request"],
        "expected_outputs": ["RESULT.yaml", "REPORT.md"],
        "completion": {
            "criteria": ["The result validates."],
            "validation": ["python3 scripts/validate_agent_protocol.py"],
            "handoff": "Chat reviews RESULT.yaml.",
        },
    }
    value.update(updates)
    return value


def result(**updates: object) -> dict:
    value = {
        "schema_version": 1,
        "task_id": "test-task",
        "created_by": "codex",
        "status": "active",
        "request_ref": "REQUEST.yaml",
        "outputs": ["REPORT.md"],
        "actions_performed": ["read_repository", "write_result", "write_report"],
        "actions_not_performed": ["upstream_write"],
        "validation": [],
        "limitations": [],
    }
    value.update(updates)
    return value


class AgentProtocolTests(unittest.TestCase):
    def setUp(self) -> None:
        self.schema, self.permissions, self.state_machine = protocol()

    def write_task(
        self,
        root: Path,
        queue: str,
        request_data: dict,
        result_data: dict | None = None,
    ) -> Path:
        task = root / queue / "test-task"
        task.mkdir(parents=True)
        (task / "REQUEST.yaml").write_text(
            yaml.safe_dump(request_data, sort_keys=False), encoding="utf-8"
        )
        if result_data is not None:
            (task / "RESULT.yaml").write_text(
                yaml.safe_dump(result_data, sort_keys=False), encoding="utf-8"
            )
            (task / "REPORT.md").write_text("# Execution report\n", encoding="utf-8")
        return task

    def test_chat_creates_valid_request(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            task = self.write_task(Path(temporary), "inbox", request())
            errors = validator.validate_task_directory(
                task, "inbox", self.schema, self.permissions, self.state_machine
            )
        self.assertEqual([], errors)

    def test_codex_creates_valid_result(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            task = self.write_task(Path(temporary), "active", request(), result())
            errors = validator.validate_task_directory(
                task, "active", self.schema, self.permissions, self.state_machine
            )
        self.assertEqual([], errors)

    def test_codex_cannot_modify_decisions(self) -> None:
        errors = validator.validate_change_set(
            [{"actor": "codex", "path": "decisions/DECISION-0003.md"}],
            self.permissions,
        )
        self.assertTrue(any("owned by chat" in error for error in errors))

    def test_evidence_completed_cannot_jump_to_admission(self) -> None:
        errors = validator.validate_transition(
            self.state_machine, "evidence_completed", "admission_pending"
        )
        self.assertEqual(
            ["forbidden transition: evidence_completed -> admission_pending"], errors
        )

    def test_upstream_write_without_approval_is_rejected(self) -> None:
        request_data = request(
            allowed_actions=["read_repository", "upstream_write"],
            prohibited_actions=["create_pull_request"],
        )
        with tempfile.TemporaryDirectory() as temporary:
            task = self.write_task(Path(temporary), "inbox", request_data)
            errors = validator.validate_task_directory(
                task, "inbox", self.schema, self.permissions, self.state_machine
            )
        self.assertTrue(any("lack APPROVAL.yaml authorization" in error for error in errors))

    def test_two_agents_modifying_same_owned_file_is_a_conflict(self) -> None:
        errors = validator.validate_change_set(
            [
                {"actor": "chat", "path": "HANDOFF.md"},
                {"actor": "codex", "path": "HANDOFF.md"},
            ],
            self.permissions,
        )
        self.assertTrue(any("multiple actors modify" in error for error in errors))

    def test_repository_example_and_protocol_validate(self) -> None:
        self.assertEqual([], validator.validate(ROOT))


if __name__ == "__main__":
    unittest.main()
