# Agent decisions

Current Codex Multi-Agent tasks record their task-scoped decision proposal in
`agent-work/tasks/<task-id>/DECISION.yaml`. A durable cross-task decision may
also be recorded here when it has a clear scope and references its evidence.

An Agent Decision Proposal contains the conclusion, confidence, evidence
references, risks, and next action. It is not a User approval: target-fork
Push, Pull Request creation, and public GitHub actions remain subject to an
explicit User-owned `APPROVAL.yaml`.

All durable decisions use the current Agent ownership model.
