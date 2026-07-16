# Project discovery

Record these facts before implementation:

- Project purpose and affected subsystem
- Primary languages and generated-code boundaries
- Build, formatting, linting, and test commands
- Local versus CI-only test requirements
- `AGENTS.md`, contribution guide, code of conduct, ownership, and PR template rules
- CLA or DCO requirements
- Issue assignment and triage conventions
- CI and reviewer approval model

Prefer repository files and current maintainer statements over general ecosystem assumptions.

Before moving from discovery into analysis, decide and record:

- which domain concepts the target reader must understand;
- whether a bounded object set affects root cause, compatibility or fix scope and therefore needs an Inventory;
- whether creation, conversion, propagation or consumption crosses enough boundaries to need a Lifecycle / Data Flow;
- what evidence would make an Inventory complete, and which runtime or external extensions remain outside the source-defined set.

Use [research-contract.md](research-contract.md) for document responsibilities and stopping boundaries. Discovery should make the next engineering decision reliable, not expand into documentation of the entire project.
