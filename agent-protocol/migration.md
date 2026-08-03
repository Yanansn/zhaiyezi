# Fixed-path queue migration

Protocol v2 replaces the movable `agent-work/inbox/`, `active/`, `blocked/`, and `completed/` queues with `agent-work/tasks/<task-id>/`.

For each legacy task:

1. Validate that `REQUEST.task_id` matches the legacy directory name.
2. Create `agent-work/tasks/<task-id>/` only when that destination does not exist.
3. Copy each artifact without changing content or ownership: Chat files remain Chat files, Codex files remain Codex files, and user Approval remains user-owned.
4. Derive state from the copied artifacts using `state-machine.yaml`; do not encode the old directory name as state.
5. Run `python3 scripts/validate_agent_protocol.py`.
6. Remove the legacy directory only after the new task validates and preservation is independently confirmed.

If the destination exists, task IDs disagree, both locations contain different versions of the same artifact, or provenance is unclear, stop and resolve the conflict manually. The validator reports any legacy directory that still contains `REQUEST.yaml`; it never migrates or deletes data automatically.

Examples now live under `agent-protocol/examples/` and never participate in queue selection.
