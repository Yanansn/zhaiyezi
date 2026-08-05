# Conflict resolution

Task directories remain at `agent-work/tasks/<task-id>/`; changing state never moves a directory. Semantic ownership is per artifact:

- Luna/Terra: bounded `REQUEST.yaml`, `RESULT.yaml`, `REPORT.md`, `evidence/**`, and `DECISION.yaml` artifacts permitted by their roles
- Sol: escalation-only `DECISION.yaml` and `decisions/**` proposals
- Historical Chat/Codex: schema v1 `REQUEST.yaml`, `REVIEW.yaml`, `RESULT.yaml`, `REPORT.md`, and `evidence/**`
- User: `APPROVAL.yaml`
- serialized: `HANDOFF.md`

Repository materialization is not semantic ownership. Codex may write Chat/User-authored artifacts only through the bounded materialization rules in `permissions.yaml`. It must preserve `decision_author`, record `materialized_by` and the current user-instruction source, and stop rather than fill any ambiguity with its own inference.

Before editing, validate the protocol, derive the current state, verify the owned output paths, and check branch/HEAD/worktree. Stop when an owned artifact changed since the recorded input baseline.

Never auto-merge, reinterpret, or overwrite another semantic author's artifact. Current workflows record a correction or escalation in a new `DECISION.yaml`/result revision; schema v1 keeps its historic `REVIEW.yaml` mechanics. A materializer may correct transcription only from a new explicit instruction; scope ambiguity or a completed decision that would need rewriting is a blocker.

Legacy queue directories are not active queues. Follow [migration.md](migration.md); preserve each artifact and stop on collisions.

The validator rejects cross-owner edits and concurrent writers. A structural materialization check must explicitly name its action; omitting the action remains an ownership violation:

```bash
python3 scripts/validate_agent_protocol.py \
  --change chat:HANDOFF.md \
  --change codex:HANDOFF.md
```

For a delegated write, include the materialization action:

```bash
python3 scripts/validate_agent_protocol.py \
  --change codex:materialize_chat_artifact:agent-work/tasks/example/REQUEST.yaml
```

Do not use reset, stash, clean, restore, rebase, or force-push as automatic conflict recovery.
