# Current Handoff

## Operating mode

The repository uses the Codex Multi-Agent Workflow. Luna owns candidate discovery, evidence, screening, and decision proposals; Terra owns deep audit, source analysis, planning, implementation, and tests; Sol is escalation-only for architecture, concurrency, and difficult debugging.

The lifecycle is `candidate → evidence → analysis → decision → implementation → pull-request`. A decision proposal is recorded as `DECISION.yaml`. Candidate Admission remains an independent gate and is never inferred from evidence completion.

## Recovery checklist

From the repository root:

```bash
git status --short --branch
git log -1 --oneline
python3 scripts/validate_agent_protocol.py
python3 scripts/agent_queue.py list
```

Read `AGENTS.md`, `agent-protocol/`, the applicable Skill, and the selected task's `REQUEST.yaml` before acting. Execute only one `ready` task assigned to the current Agent. If no valid task exists, report the gap instead of inventing scope.

## Repository facts

- `repositories/` is the target repository registry, discovery, and binding source.
- `agent-work/tasks/` contains current bounded task artifacts.
- `screenings/` contains lightweight screening history.
- `issues/` contains formal Issue research records, including historical Kubernetes records.
- `decisions/` contains Agent decision proposals.

Historical Issue facts remain in their existing records and are not reinterpreted by this handoff. Formal Issue records retain their own stricter documentation contract; lightweight tasks do not need to create one.

## Approval and publication

Facts-repository writes are separate from upstream writes. Target Fork Push, PR creation, Issue/comment/label actions, and other public GitHub actions require explicit User approval and live identity verification. No current task should perform those actions without an exact approval artifact.

## Current next action

Check the queue and remote state, then create or execute a bounded task only when its scope, outputs, assigned Agent, and approval boundary are recorded. Preserve unrelated local files and report any divergence between the facts repository and target repository.
