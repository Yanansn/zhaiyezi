# Codex Multi-Agent Protocol

`agent-protocol/` coordinates durable facts under `agent-work/tasks/<task-id>/`.
The current workflow is Codex-internal and does not require Chat as a review
or decision gate.

## Agents and artifacts

Current tasks use `schema_version: 2` and are assigned to `agent:luna`,
`agent:terra`, or `agent:sol`.

- Luna produces discovery, evidence, screening, and decision proposals.
- Terra produces deep audits, plans, implementation changes, and tests.
- Sol provides escalation-only architecture/concurrency/debug review.
- `DECISION.yaml` contains conclusion, confidence, evidence references, risks,
  and the next action.
- `approval_required` is mandatory for current REQUESTs. It records whether
  a task expects protected actions; it never grants them.

`APPROVAL.yaml` remains User-owned. Target-fork pushes, Pull Requests, and
all public GitHub actions need explicit User approval. Luna and Terra may
write facts and commit `zhaiyezi`; no agent may perform upstream writes by
default.

## Lifecycle

```text
candidate → evidence → analysis → decision → implementation → pull-request
```

The `decision` stage must be materialized in `DECISION.yaml`; it replaces the
former mandatory Chat Review. Repository binding, target repository discovery,
evidence collection, and screening records are retained.

`state-machine.yaml` is the authoritative lifecycle definition. This README
and `lifecycle.md` explain it but do not introduce additional transitions.

## Commands

```bash
python3 scripts/validate_agent_protocol.py
python3 scripts/agent_queue.py list
python3 scripts/agent_queue.py next --agent agent:luna
python3 scripts/agent_queue.py next --agent agent:terra
```

See [roles.md](roles.md), [lifecycle.md](lifecycle.md),
[permissions.yaml](permissions.yaml), [task-schema.yaml](task-schema.yaml),
and [state-machine.yaml](state-machine.yaml).
