# Conflict resolution

Task directories remain at `agent-work/tasks/<task-id>/`; changing state never moves a directory. Ownership is per artifact:

- Chat: `REQUEST.yaml`, `REVIEW.yaml`, `decisions/**`
- Codex: `RESULT.yaml`, `REPORT.md`, `evidence/**`, `screenings/**`
- User: `APPROVAL.yaml`
- serialized: `HANDOFF.md`

Before editing, validate the protocol, derive the current state, verify the owned output paths, and check branch/HEAD/worktree. Stop when an owned artifact changed since the recorded input baseline.

Never auto-merge or overwrite another actor's artifact. Chat requests corrections in an immutable `REVIEW.yaml`; Codex responds with a higher `RESULT.revision` and keeps the Review as history. Contract ambiguity or an approved/rejected Review that would need rewriting is a blocker, not permission to mutate history.

Legacy queue directories are not active queues. Follow [migration.md](migration.md); preserve each artifact and stop on collisions.

The validator rejects cross-owner edits and concurrent writers:

```bash
python3 scripts/validate_agent_protocol.py \
  --change chat:HANDOFF.md \
  --change codex:HANDOFF.md
```

Do not use reset, stash, clean, restore, rebase, or force-push as automatic conflict recovery.
