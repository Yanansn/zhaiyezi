# Agent Coordination Layer

`agent-protocol/` defines how Chat and Codex coordinate through the repository. It is an envelope around the existing Screening, Evidence Collection, Candidate Admission, and Harvest contracts; it does not replace their schemas or state machines.

```text
Chat (decision-agent)
  → agent-work/*/REQUEST.yaml
  → Codex (execution-agent)
  → RESULT.yaml + REPORT.md + evidence
  → Chat REVIEW.yaml
  → user APPROVAL.yaml when a protected action is requested
```

The repository is shared memory, a task queue, and an evidence store. Chat must only rely on committed and pushed records. Codex may work locally, but an unpushed result is not shared state.

## Queue layout

- `agent-work/inbox/`: immutable requests with effective status `ready`.
- `agent-work/active/`: claimed work with effective status `active` or `review`.
- `agent-work/blocked/`: tasks whose latest execution result is `blocked`.
- `agent-work/completed/`: tasks with a Chat-owned approved `REVIEW.yaml` and effective status `completed`.

A task directory moves between queues. Chat owns `REQUEST.yaml` and `REVIEW.yaml`; Codex owns `RESULT.yaml`, `REPORT.md`, and `evidence/`; the user owns `APPROVAL.yaml`. Moving a task directory does not transfer ownership of its files.

## Codex startup

1. Verify the facts-repository remote, branch, HEAD, and clean worktree.
2. Synchronize only when authorized. For this facts repository, `git pull --ff-only` is permitted only after verifying `origin` and a clean, non-diverged branch; the explicit `git fetch --prune origin` plus `git merge --ff-only origin/main` sequence remains the safer auditable form required by `AGENTS.md`.
3. Read `AGENTS.md`, `HANDOFF.md`, and every file in `agent-protocol/`.
4. Find `agent-work/inbox/*/REQUEST.yaml` with `status: ready` and `assigned_agent: codex`.
5. Validate the protocol and task with `python3 scripts/validate_agent_protocol.py`.
6. Execute only the task's allowed actions and existing stage-specific Skill contract.
7. Write `RESULT.yaml`, `REPORT.md`, and requested evidence; move the task to `active/` with result status `review`, or to `blocked/` with the blocker recorded.
8. Run the task-specific validators and tests.
9. Commit or Push only when both the task and current user authorization allow each action.

## Chat startup

1. Read the latest remote `main`; do not infer local Codex state.
2. Read `agent-protocol/`, `decisions/`, and tasks in `completed/`, `blocked/`, and `active/` awaiting review.
3. Review the referenced result and evidence.
4. Write `REVIEW.yaml`; create the next `REQUEST.yaml` when more work is needed.
5. Request user approval and record `APPROVAL.yaml` before any protected action.

## Existing workflow compatibility

- Evidence completion is not Deep Audit, `available`, Admission, or selection.
- Admission remains the mapping defined by the Screening schema and Candidate Admission Gate.
- Real contribution stages and Issue statuses remain governed by `harvest-open-source-issue` and `AGENTS.md`.
- `pr_ready` in the coordination lifecycle means an execution artifact is ready for the existing PR lifecycle. It does not skip `submitted`, `reviewing`, or a terminal Issue outcome.
- A queue task never grants registry mutation, upstream writes, Commit, Push, or publication by implication.

See [roles.md](roles.md), [lifecycle.md](lifecycle.md), [permissions.yaml](permissions.yaml), [task-schema.yaml](task-schema.yaml), [state-machine.yaml](state-machine.yaml), and [conflict-resolution.md](conflict-resolution.md).
