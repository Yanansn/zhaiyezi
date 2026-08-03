# Agent Coordination Layer

`agent-protocol/` defines the repository-backed handshake between Chat and Codex. It wraps the existing Screening, Candidate Admission, and Harvest contracts; it never replaces their classifications, gates, or Issue/PR lifecycle.

```text
agent-work/tasks/<task-id>/REQUEST.yaml       Chat-owned, immutable
agent-work/tasks/<task-id>/RESULT.yaml        Codex-owned, revisioned
agent-work/tasks/<task-id>/REPORT.md          Codex-owned
agent-work/tasks/<task-id>/evidence/**        Codex-owned
agent-work/tasks/<task-id>/REVIEW.yaml        Chat-owned
agent-work/tasks/<task-id>/APPROVAL.yaml      user-owned
```

Task directories never move. Queue state is derived from the artifacts in that fixed directory. Files under `agent-protocol/examples/` are examples only and are never queue entries.

## Deterministic queue

```bash
python3 scripts/agent_queue.py list
python3 scripts/agent_queue.py list --agent codex --status ready
python3 scripts/agent_queue.py next --agent codex
python3 scripts/agent_queue.py show --task example-task
```

`list` and `next` sort by priority (`urgent`, `high`, `normal`, `low`), then `created_at`, then `task_id`. Invalid tasks are reported and cause a non-zero exit; they are not silently skipped. `next` only returns a `ready` task assigned to the requested Agent.

## Codex startup

1. Verify remote, branch, HEAD, and worktree; synchronize only when separately authorized.
2. Read `AGENTS.md`, `HANDOFF.md`, the applicable Brief and Skill, and this protocol.
3. Run `python3 scripts/validate_agent_protocol.py`.
4. Run `python3 scripts/agent_queue.py next --agent codex`.
5. Execute only the recorded scope and allowed actions.
6. Write Codex-owned artifacts in the same task directory and run the requested validation.
7. Commit or Push only with a task-specific approval or an active standing authorization that exactly matches repository, branch, actor, action, and every changed path.

## Chat startup

1. Read the latest pushed `main`; local Codex state is not shared state.
2. Run the validator and inspect `python3 scripts/agent_queue.py list --agent chat` plus tasks in `awaiting-review` or `changes-requested`.
3. Write only Chat-owned artifacts. Review the exact result revision named by `REVIEW.yaml`.
4. Record `changes-requested` in `REVIEW.yaml`. Codex then creates a new `RESULT.yaml` revision; Chat must not modify `RESULT.yaml` or rewrite the previous `REVIEW.yaml`.
5. Obtain fresh user approval for actions that cannot be covered by standing authorization.

## Authorization boundary

`APPROVAL.yaml` is task-scoped. An optional standing authorization may exist only at `decisions/authorizations/*.yaml`, and may authorize only Commit/Push of actor-owned facts-repository paths on the exact `Yanansn/zhaiyezi` branch. The example at `agent-protocol/examples/standing-authorization.yaml` is a template, not authorization.

Registry changes, formal Issue initialization, upstream fetch/code/write/branch Push, Issue/PR/comment/assignment/label actions, and publication always require new user confirmation. Live identity verification remains mandatory before public actions.

Evidence completion enters Review. It does not mean `available`, Candidate Admission passed, selection, or implementation authorization. Queue `completed` only means the current execution artifact was approved; the formal contribution lifecycle remains authoritative.

See [roles.md](roles.md), [lifecycle.md](lifecycle.md), [permissions.yaml](permissions.yaml), [task-schema.yaml](task-schema.yaml), [state-machine.yaml](state-machine.yaml), [conflict-resolution.md](conflict-resolution.md), and [migration.md](migration.md).
