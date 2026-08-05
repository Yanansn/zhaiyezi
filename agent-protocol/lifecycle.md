# Codex Multi-Agent Lifecycle

```text
candidate → evidence → analysis → decision → implementation → pull-request
```

- `candidate`: Luna locates and values potential work.
- `evidence`: Luna records raw upstream and repository facts.
- `analysis`: Terra verifies source behavior, feasibility, and scope.
- `decision`: Luna, Terra, or Sol writes `DECISION.yaml` with conclusion,
  confidence, evidence references, risks, and next action.
- `implementation`: Terra performs bounded local code changes and tests.
- `pull-request`: target-fork push, PR creation, and every public action
  require explicit User approval.

There is no mandatory Chat Review transition. A completed `DECISION.yaml`
closes the corresponding task artifact; it does not by itself authorize a
public action.

`state-machine.yaml` is the source of truth for transitions and queue-state
derivation. This document is explanatory only.

Repository binding, evidence, screening, and the Candidate Admission boundary
remain separate facts.
