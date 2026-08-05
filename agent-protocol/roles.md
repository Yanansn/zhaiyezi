# Codex Multi-Agent Roles

The current workflow is executed by Codex internal agents. No external
handoff is required for a lifecycle stage.

| Agent | Primary responsibility | May modify target source | May commit facts |
| --- | --- | --- | --- |
| `agent:luna` | discovery, evidence, screening, contribution value, decision proposals | no | yes |
| `agent:terra` | deep audit, source analysis, implementation planning, code and tests | yes, only in a bounded task | yes |
| `agent:sol` | architecture/concurrency/debug escalation and final technical review | no | no |
| `user` | approvals for target-fork push, PRs, and public GitHub actions | by explicit approval | by explicit approval |

`agent:sol` produces escalation-oriented `DECISION.yaml` artifacts only. It
does not modify source, facts reports, or Git history.

## Decision ownership

Current artifacts use `schema_version: 2` and identify semantic ownership as
`decision_author: agent:luna`, `agent:terra`, `agent:sol`, or `user`.
`materialized_by` is the same internal agent for current artifacts.

There is one current artifact format: schema version 2 with Agent ownership
and `DECISION.yaml`.
