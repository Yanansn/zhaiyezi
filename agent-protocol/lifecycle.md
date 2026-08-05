# Codex Multi-Agent Lifecycle

```text
candidate → evidence → analysis → decision → implementation → pull-request
```

- `candidate`: Luna locates and values potential work.
- `evidence`: Luna records raw upstream and repository facts.
- `analysis`: Terra verifies source behavior, feasibility, and scope.
- `decision`: a separate `DECISION.yaml` is created only when an independent
  decision gate or escalation is needed. Screening conclusions live in
  `RESULT.yaml`.
- `implementation`: Terra performs bounded local code changes and tests.
- `pull-request`: target-fork push, PR creation, and every public action
  require explicit User approval.

`DECISION.yaml` may close a task but does not by itself authorize a public
action. A screening task may close with `RESULT.yaml` alone.

`state-machine.yaml` is the source of truth for transitions and queue-state
derivation. This document is explanatory only.

Repository binding, evidence, screening, and the Candidate Admission boundary
remain separate facts.
