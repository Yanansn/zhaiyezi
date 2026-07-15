---
name: harvest-open-source-issue
description: Systematically investigate, explain, implement, test, and carry an open-source issue through contribution while teaching the project and preserving auditable records. Use when Codex needs to screen candidate issues, learn an unfamiliar repository through a real issue, build a code map and solution, make and explain changes, guide or run tests, prepare branches/commits/pull requests, respond to CI or review, or resume an existing issue contribution.
---

# Harvest Open Source Issues

Treat an issue as both a contribution task and a structured learning path. Advance it through explicit stages and preserve evidence in the project record.

## Operating principles

- Distinguish GitHub facts, source-code facts, test evidence, and inference.
- Read the issue body, current labels, assignees, discussion, linked pull requests, and repository contribution instructions before recommending implementation.
- Explain the affected subsystem and terminology in plain language before editing.
- Build a code map and identify analogous implementations or tests before proposing a solution.
- Keep changes scoped to the accepted issue. Do not bundle opportunistic refactors.
- Run the narrowest meaningful checks first. Never claim success without recorded evidence.
- Teach the reasoning behind code, commands, tests, and community workflow.
- Require user confirmation before public comments, issue assignment, pushes, pull requests, reviews, or other person-facing actions.
- Update the issue record after every material stage transition.

## Workflow

1. **Discover the project**
   - Read `AGENTS.md`, `CONTRIBUTING.md`, issue/PR templates, build files, test guidance, and relevant ownership files.
   - Record language, build system, test framework, CI, contribution rules, CLA/DCO requirements, and community conventions.
   - Read [project-discovery.md](references/project-discovery.md).
2. **Screen the issue**
   - Check freshness, triage state, ownership, linked work, clarity, environment cost, scope, testability, learning value, and likely blockers.
   - Choose `selected`, `awaiting-confirmation`, `research-only`, `rejected`, or `blocked`; explain why.
   - Read [screening.md](references/screening.md).
3. **Explain and map**
   - Explain current behavior, expected behavior, impact, terminology, scope, and non-goals.
   - Trace the relevant code path and existing tests. Record files and responsibilities in `CODE-MAP.md`.
4. **Plan**
   - State the root cause or unresolved hypothesis, preferred solution, alternatives, risks, compatibility concerns, and validation strategy.
   - If maintainers have not accepted the direction, prepare a concise confirmation comment and pause before substantial implementation.
5. **Implement**
   - Create a descriptive branch after checking repository conventions.
   - Make the smallest coherent change. Explain important code decisions and connect them to the code map.
6. **Validate**
   - Format and lint, run targeted unit or package tests, then integration/e2e tests when proportional and feasible.
   - Record exact commands, environment, results, limitations, and CI-only coverage in `TESTING.md`.
   - Read [testing.md](references/testing.md).
7. **Prepare the contribution**
   - Inspect the staged diff for unrelated changes.
   - Propose branch name, commit structure and messages, PR title/body, issue linkage, release note, and reviewer notes according to repository rules.
   - Obtain confirmation before external actions.
8. **Review and close**
   - Diagnose CI failures, respond to review, iterate implementation and tests, and update records.
   - Finish with merged, rejected, superseded, or blocked status plus a learning retrospective and suggested next issue.

## Record contract

Use one directory per issue under `issues/<owner>-<repo>-<number>/`. Maintain:

- `STATUS.yaml`: machine-readable current state, blockers, next actions, branch, PR, and last verification time.
- `ISSUE.md`: source facts and structured requirement summary.
- `ANALYSIS.md`: accessible technical explanation, root cause or hypotheses, scope, and non-goals.
- `CODE-MAP.md`: relevant files, call flow, analogous code, tests, and ownership.
- `PLAN.md`: chosen solution, alternatives, risk, and validation plan.
- `IMPLEMENTATION.md`: actual changes and reasoning.
- `TESTING.md`: commands, environment, evidence, failures, limitations, and CI results.
- `LEARNING.md`: concepts learned and reusable problem-solving methods.
- `PR.md`: branch, commits, PR draft, review feedback, and outcome.
- `JOURNAL.md`: append-only dated decisions and material actions.

Use `scripts/init_issue_record.py` to initialize a record and `scripts/validate_issue_record.py` before reporting a stage complete. Never overwrite journal history.

## Status model

Use one of: `candidate`, `screening`, `awaiting-triage`, `selected`, `analyzing`, `planned`, `implementing`, `testing`, `pr-ready`, `submitted`, `reviewing`, `merged`, `blocked`, `rejected`, `superseded`, `closed`.

Do not skip directly from `candidate` to `implementing`. A contribution is complete only when its outcome and learning retrospective are recorded.

## Adaptation

Keep this workflow repository-agnostic. Infer project-specific practices from the repository. Load an ecosystem profile from `references/profiles/` only when present and applicable; repository instructions always override a profile. Add a profile only after repeated real work demonstrates reusable, stable guidance.
