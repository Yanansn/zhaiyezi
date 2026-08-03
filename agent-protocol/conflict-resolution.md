# Conflict resolution

Task directories remain at `agent-work/tasks/<task-id>/`; changing state never moves a directory. Semantic ownership is per artifact:

- Chat: `REQUEST.yaml`, `REVIEW.yaml`, `decisions/**`
- Codex: `RESULT.yaml`, `REPORT.md`, `evidence/**`, `screenings/**`
- User: `APPROVAL.yaml`
- serialized: `HANDOFF.md`

Repository materialization is not semantic ownership. Codex may write Chat/User-authored artifacts only through the bounded materialization rules in `permissions.yaml`. It must preserve `decision_author`, record `materialized_by` and the current user-instruction source, and stop rather than fill any ambiguity with its own inference.

Before editing, validate the protocol, derive the current state, verify the owned output paths, and check branch/HEAD/worktree. Stop when an owned artifact changed since the recorded input baseline.

Never auto-merge, reinterpret, or overwrite another semantic author's artifact. Chat requests corrections in an immutable `REVIEW.yaml`; Codex responds with a higher `RESULT.revision` and keeps the Review as history. A materializer may correct transcription only from a new explicit instruction; scope ambiguity or an approved/rejected Review that would need rewriting is a blocker.

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
