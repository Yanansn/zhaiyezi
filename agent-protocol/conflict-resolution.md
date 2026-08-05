# Conflict resolution

Task directories stay at `agent-work/tasks/<task-id>/`; state changes never
move a task directory. Current semantic ownership is defined by
`permissions.yaml`:

- Luna/Terra own bounded task artifacts and facts outputs.
- Sol owns escalation `DECISION.yaml` artifacts only.
- User owns `APPROVAL.yaml` and public-action authorization.

Never merge, reinterpret, or overwrite another Agent's artifact. Record a new
result revision or `DECISION.yaml` when a correction is needed. A task with
ambiguous scope, conflicting writers, or a completed decision that would need
rewriting is blocked for explicit resolution.

Validate before editing:

```bash
python3 scripts/validate_agent_protocol.py
```

For a structural ownership check, name the actor, action, and path:

```bash
python3 scripts/validate_agent_protocol.py \
  --change agent:terra:repository_modify:agent-work/tasks/example/RESULT.yaml
```
