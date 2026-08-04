# Agent Coordination Layer

`agent-protocol/` defines the repository-backed handshake between Chat and Codex. It wraps the existing Screening, Candidate Admission, and Harvest contracts; it never replaces their classifications, gates, or Issue/PR lifecycle.

```text
agent-work/tasks/<task-id>/REQUEST.yaml       Chat-authored decision
agent-work/tasks/<task-id>/RESULT.yaml        Codex-authored result
agent-work/tasks/<task-id>/REPORT.md          Codex-authored report
agent-work/tasks/<task-id>/evidence/**        Codex-authored evidence
agent-work/tasks/<task-id>/REVIEW.yaml        Chat-authored decision
agent-work/tasks/<task-id>/APPROVAL.yaml      user-authored approval
```

`deep-audit` is a first-class task type. It consumes completed evidence and
produces a screening recommendation for Chat review. It requires non-empty
`evidence_refs` and does not authorize Admission, implementation, upstream
writes, or Pull Requests.

## Target Repository Management

`repositories/registry.yaml` stores target repository URLs, fork enablement,
local discovery enablement, contribution enablement, language, and expected
Git identity. It must not store absolute local paths. The discovery roots in
`repositories/discovery.yaml` are home-relative and are resolved at runtime by
`scripts/repository_discovery.py` from Git remotes.

REQUESTs may include `target_repository` with a repository name and phase.
Evidence may omit it; Deep Audit requires it; Implementation additionally
requires fork and local discovery results. Binding a target repository never
grants upstream write or Pull Request permission. `repository_read` is
read-only target access; `repository_modify` requires the separate approval
boundary for local fork changes.

Task directories never move. Queue state is derived from the artifacts in that fixed directory. Files under `agent-protocol/examples/` are examples only and are never queue entries.

## Semantic ownership and materialization

`decision_author` identifies who supplied and owns an artifact's meaning. `materialized_by` identifies who wrote that already-decided content into the repository. Chat remains the decision author of REQUEST and REVIEW; Codex remains the decision author of RESULT, REPORT, and evidence; the user remains the decision author of APPROVAL and standing authorization.

When Chat lacks repository write access, Codex may materialize a Chat-authored REQUEST, REVIEW, or decision under a current explicit user instruction and a matching standing authorization. The artifact must record `decision_author: chat`, `materialized_by: codex`, and bounded `materialization` provenance. Materialization does not transfer decision ownership and does not permit Codex to infer or alter scope, conclusions, permissions, status, or approval.

Codex may materialize a user-authored APPROVAL or standing authorization only when the user has supplied its complete approval scope in the current instruction. `decision_author: user` remains mandatory. This action is never granted by standing authorization.

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
5. If explicitly instructed to materialize a complete Chat decision, preserve its exact scope and provenance, validate it, and only then treat the persisted REQUEST as a task.
6. Execute only the recorded scope and allowed actions; write Codex-authored artifacts in the same task directory and run the requested validation.
7. Commit or Push only with a task-specific approval or an active standing authorization that exactly matches repository, branch, actor, action, and every changed path.

## Chat startup

1. Read the latest pushed `main`; local Codex state is not shared state.
2. Run the validator and inspect `python3 scripts/agent_queue.py list --agent chat` plus tasks in `awaiting-review` or `changes-requested`.
3. Author REQUEST/REVIEW content and review the exact result revision named by `REVIEW.yaml`; when repository writes are unavailable, provide the complete bounded content for Codex materialization.
4. Record `changes-requested` in `REVIEW.yaml`. Codex then creates a new `RESULT.yaml` revision; Chat must not modify `RESULT.yaml` or rewrite the previous `REVIEW.yaml`.
5. Obtain fresh user approval for actions that cannot be covered by standing authorization.

## Authorization boundary

`APPROVAL.yaml` is task-scoped. An optional standing authorization may exist only at `decisions/authorizations/*.yaml`. It may authorize Commit/Push of allowed facts-repository paths and Codex materialization of Chat-authored artifacts on the exact `Yanansn/zhaiyezi` branch. It cannot authorize Codex to originate a Chat decision or user approval. The example at `agent-protocol/examples/standing-authorization.yaml` is a template, not authorization.

Registry changes, formal Issue initialization, upstream fetch/code/write/branch Push, Issue/PR/comment/assignment/label actions, and publication always require new user confirmation. Live identity verification remains mandatory before public actions.

Evidence completion enters the `deep_audit` coordination stage. Deep Audit then
enters `awaiting_review`; it does not mean `available`, Candidate Admission
passed, selection, or implementation authorization. Queue `completed` only
means the current execution artifact was approved; the formal contribution
lifecycle remains authoritative.

See [roles.md](roles.md), [lifecycle.md](lifecycle.md), [permissions.yaml](permissions.yaml), [task-schema.yaml](task-schema.yaml), [state-machine.yaml](state-machine.yaml), [conflict-resolution.md](conflict-resolution.md), and [migration.md](migration.md).
