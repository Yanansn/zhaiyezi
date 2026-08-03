# Conflict resolution

## Ownership first

- Chat-owned: `REQUEST.yaml`, `REVIEW.yaml`, and `decisions/**`.
- Codex-owned: `RESULT.yaml`, `REPORT.md`, and task `evidence/**`.
- User-owned approval: `APPROVAL.yaml`.
- Shared and serialized: `HANDOFF.md`.

An Agent must not edit another role's owned file. Corrections are expressed through a new owned artifact: Chat requests changes in `REVIEW.yaml`; Codex explains a contract problem in `RESULT.yaml` or `REPORT.md`.

## Before editing

1. Verify the task directory, queue, effective status, and owned output paths.
2. Verify branch, HEAD, remote, and worktree.
3. Synchronize the facts repository only when authorized and only by fast-forward. `git pull --ff-only` must never be used to conceal a dirty or diverged state; the auditable equivalent is `git fetch --prune origin` followed by `git merge --ff-only origin/main`.
4. Stop if another Agent changed an owned file since the task's `input_refs` baseline.

## Conflict handling

- Never auto-merge an owned-file conflict.
- Never overwrite another Agent's artifact.
- Never use reset, stash, clean, restore, rebase, or force-push as automatic recovery.
- Preserve both facts by stopping the task and writing a blocker in the current Agent's owned artifact.
- Chat resolves task-contract conflicts by issuing a replacement `REQUEST.yaml` or Review.
- A `HANDOFF.md` collision requires serialization: finish or abandon one task before the other updates it.

The validator can check a proposed change set with actor/path pairs and rejects cross-owner edits or two Agents touching the same owned/shared path:

```bash
python3 scripts/validate_agent_protocol.py \
  --change chat:HANDOFF.md \
  --change codex:HANDOFF.md
```
