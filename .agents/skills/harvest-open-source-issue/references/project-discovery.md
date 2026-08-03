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
- Hardware, model, accelerator, external-service, and compatibility requirements

Apply [profiles/README.md](profiles/README.md) in this precedence order: common workflow, language, ecosystem, repository, then live repository instructions. Profiles only supply discovery questions; record selected Profiles and live overrides in `PROJECT.yaml`.

## Branch model

Record these independently with evidence:

```yaml
branches:
  github_default_branch:
  contribution_target_branch:
  issue_affected_branch:
  latest_release_branch:
  evidence: []
```

The GitHub default branch is not necessarily the contribution target or PR base branch. Confirm the target from current contribution rules, templates, active PRs, and maintainer direction.

## Structured discovery and scope

Keep `PROJECT.yaml` synchronized with the narrative records. It captures primary languages, build systems, format/lint/test commands, generated-code boundaries, local versus CI-only tests, CLA/DCO, ownership conventions, PR base, release notes, hardware, compatibility, and external services.

For cross-repository work, record the primary repository, read-only related repositories, expected and excluded change repositories, and whether scope is single-repository, confirmed multi-repository, or requires expansion. Discovering a needed second-repository change pauses implementation until a new Brief confirms scope. Each working repository needs independent remote, base, branch, commit, worktree, and Push authorization evidence.

Prefer repository files and current maintainer statements over general ecosystem assumptions.

Before moving from discovery into analysis, decide and record:

- which domain concepts the target reader must understand;
- whether a bounded object set affects root cause, compatibility or fix scope and therefore needs an Inventory;
- whether creation, conversion, propagation or consumption crosses enough boundaries to need a Lifecycle / Data Flow;
- what evidence would make an Inventory complete, and which runtime or external extensions remain outside the source-defined set.

Use [research-contract.md](research-contract.md) for document responsibilities and stopping boundaries. Discovery should make the next engineering decision reliable, not expand into documentation of the entire project.
