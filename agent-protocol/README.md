# Codex Multi-Agent Protocol

`agent-protocol/` coordinates durable facts under `agent-work/tasks/<task-id>/`.
The current workflow is Codex-internal and uses Agent artifacts as its review
and decision mechanism.

## Agents and artifacts

Current tasks use `schema_version: 2` and are assigned to `agent:luna`,
`agent:terra`, or `agent:sol`.

- Luna produces discovery, evidence, screening, and decision proposals.
- Terra produces deep audits, plans, implementation changes, and tests.
- Sol provides escalation-only architecture/concurrency/debug review.
- Screening tasks use only `REQUEST.yaml` and `RESULT.yaml`; `REPORT.md` is an
  optional short human summary. `DECISION.yaml` is reserved for independent
  decision gates or escalation.
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

Decision gates may be materialized in `DECISION.yaml` as a first-class Agent
artifact. Repository binding, target repository discovery, and evidence
collection remain available; screening no longer requires a parallel
历史 `screenings/` records remain readable, but new screening tasks are not
duplicated there.

`state-machine.yaml` is the authoritative lifecycle definition. This README
and `lifecycle.md` explain it but do not introduce additional transitions.

Before `analysis`/Deep Audit, agents run a lightweight Pre-Deep-Audit Gate:
check concrete Issue scope, readable evidence, valid target binding and source
baseline, at least one useful verification route, required runtime dependencies,
and bounded time/token/environment cost. A missing GPU or integration runtime
stops high-cost investigation when no meaningful low-cost alternative exists;
the result records a feasibility limitation and does not claim the Issue is
invalid. Deep Audit is not started merely because a candidate exists.

The gate also checks for `author-claimed`: when the Issue author or a maintainer
has publicly announced an implementation, draft, or forthcoming PR, the task is
paused and marked `author-claimed`. This is a temporary coordination boundary,
not a duplicate or admission decision; resume only after a PR, explicit
withdrawal, or maintainer release of the contribution scope.

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
