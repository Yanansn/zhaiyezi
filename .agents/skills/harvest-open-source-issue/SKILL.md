---
name: harvest-open-source-issue
description: Execute a stage-scoped open-source contribution from a confirmed Execution Brief by verifying live facts, reading real code, building precise code maps, implementing, testing, diagnosing failures, updating records, and performing approved Git or GitHub publication steps. Use when Codex receives a bounded engineering brief for an already screened issue or resumes an established contribution stage.
---

# Harvest Open Source Issues

Treat Codex as the engineering execution agent for an issue that ordinary Chat has already screened and explained. Execute one bounded stage at a time and preserve evidence for the next Chat handoff.

## Intake gate

- Require an `Execution Brief` containing the issue, confirmed facts, goal, required investigation, constraints, expected deliverables, and approval boundary.
- Read [execution-brief.md](references/execution-brief.md) when starting a new stage or when the brief is incomplete.
- Identify the facts repository and, for real code work, the separate upstream working repository from the brief.
- Verify the brief against repository records, live GitHub state, and each applicable local repository's branch, commit, remotes, and worktree before acting.
- Require separate authorization for fetching the official upstream, fast-forwarding the local base, merging or rebasing a working branch, and rewriting or force-pushing a working branch.
- If the brief is absent, materially stale, or lacks a stage goal, deliverables, or approval boundary, report the gap and stop. Do not expand into candidate screening or open-ended research.

## Operating principles

- Distinguish GitHub facts, source-code facts, test evidence, and inference.
- Read the issue body, current labels, assignees, discussion, linked pull requests, and repository contribution instructions before implementation.
- Build a code map and identify analogous implementations or tests before proposing a solution.
- Keep changes scoped to the accepted issue. Do not bundle opportunistic refactors.
- Run the narrowest meaningful checks first. Never claim success without recorded evidence.
- Report engineering evidence concisely: what changed, why it works, how it was validated, and remaining risks.
- Require user confirmation before public comments, issue assignment, pushes, pull requests, reviews, or other person-facing actions.
- Default to no subagents. Use them only when the brief permits them and parallel work has clear value.
- Update only records whose facts changed in the current stage.
- Treat unpushed local results as invisible to ordinary Chat; never present them as shared facts.
- At the end of each stage, state explicitly what was pushed and what remains local. Use [execution-brief.md](references/execution-brief.md) for the full return contract.
- Make upstream code changes only in the upstream working repository; make contribution-record changes only in the facts repository.
- Treat every GitHub-facing message or artifact as speech by the user. Follow [public-communication.md](references/public-communication.md); never publish directly from research or infer publication permission from a completed Draft.

## Workflow

1. **Verify intake and discover the project**
   - Parse the Execution Brief and state the exact stage boundary.
   - Verify the facts repository and upstream working repository independently when both apply.
   - Resolve remote roles from configured repository URLs instead of assuming `origin` is the Fork or `upstream` is official.
   - When authorized, fetch the official remote with pruning, identify its default development branch, and compare the local base, official base, and working branch with `rev-list`, `rev-parse`, and `merge-base`.
   - Fast-forward a local base only when the worktree is clean, the local base has no unique commits, the histories have not diverged, `--ff-only` can succeed, and the brief explicitly permits it. Record the base Commit before and after.
   - Stop on dirty state, unique local base commits, divergence, unknown commits, remote mismatch, an unknown default branch, fetch failure, or any need for merge Commit, rebase, reset, or discarded work.
   - Read `AGENTS.md`, `CONTRIBUTING.md`, issue/PR templates, build files, test guidance, and relevant ownership files.
   - Record language, build system, test framework, CI, contribution rules, CLA/DCO requirements, and community conventions.
   - Read [project-discovery.md](references/project-discovery.md).
2. **Map when requested**
   - Identify the background a target reader needs. Add only necessary issue-specific explanations to `KNOWLEDGE.md`; reuse links for stable cross-issue material instead of copying it.
   - Decide whether a collection affects root cause or fix scope. If so, build an Inventory with an explicit counting boundary, method, definitions, usage, extensibility, completeness and limitations.
   - Trace relevant files, registration, call paths and tests. Add Lifecycle / Data Flow when objects or configuration pass through meaningful creation, conversion, filtering or consumption stages.
   - Do not infer the whole system from one example or call a keyword-search result complete. Inventory exists to prevent local observations from producing a wrong fix boundary, not to document the entire upstream project.
   - Record these source facts in `CODE-MAP.md`, then keep conclusions and solution comparisons in `ANALYSIS.md`. Read [research-contract.md](references/research-contract.md).
   - Do not modify upstream code when the brief says the stage is code-map-only.
3. **Plan when requested**
   - State the root cause or unresolved hypothesis, preferred solution, alternatives, risks, compatibility concerns, and validation strategy.
   - If maintainers have not accepted the direction, prepare a concise confirmation comment and pause before substantial implementation.
4. **Implement when requested**
   - Create a descriptive branch from the verified official base after checking repository conventions.
   - Treat updating an existing working branch as separate from synchronizing the local base. Never merge or rebase the official base into a branch with commits without explicit authorization; do not rebase or force-push an open PR by default.
   - Work in the upstream working repository and make the smallest coherent change. Explain important code decisions and connect them to the code map.
5. **Validate when requested or required by implementation**
   - Format and lint, run targeted unit or package tests, then integration/e2e tests when proportional and feasible.
   - Record exact commands, environment, results, limitations, and CI-only coverage in `TESTING.md`.
   - Read [testing.md](references/testing.md).
6. **Prepare or publish when authorized**
   - Inspect both repositories for unrelated changes and keep their commits separate.
   - Before creating a PR, verify the user Fork remote, official upstream remote, target base branch, and head branch.
   - In the upstream working repository run `git status -sb`, `git log --oneline <upstream-base>..HEAD`, `git diff --check <upstream-base>...HEAD`, and `git diff --stat <upstream-base>...HEAD`.
   - Check the PR template, `CONTRIBUTING`, CLA/DCO, `Signed-off-by`, release-note requirements, Issue linkage, unrelated changes, and whether commits need cleanup or squash.
   - Propose branch name, commit structure and messages, PR title/body, issue linkage, release note, and reviewer notes according to repository rules.
   - For any GitHub comment, reply, PR description, Review, Discussion or RFC, first create an exact Draft, obtain Technical Review, then wait for explicit user approval. Technical Review may come from ordinary Chat, a human reviewer or a team. A Draft PR is already public and follows the same gate.
   - Treat preparation, initial publication, maintainer reply and update of existing public content as separate permissions. Missing publication fields mean prohibited.
   - Immediately before an authorized publication, obtain the actual authenticated GitHub identity and compare it with the user-specified expected identity. Never infer identity from an SSH key name, remote URL or history; stop if they differ or cannot be verified.
   - Re-verify the live target and exact approved content. Afterward record the URL, publication time, actual content and maintainer-feedback state.
   - Perform Commit, Push, PR, comment, or review actions only when the brief or a later user message explicitly authorizes each external boundary.
7. **Review and close**
   - Diagnose CI failures, respond to review, iterate implementation and tests, and update records.
   - Finish with merged, rejected, superseded, or blocked status plus a learning retrospective and suggested next issue.

## Multi-repository execution order

1. Read the rules, handoff, brief, and issue record in the facts repository.
2. Verify the facts repository branch, commit, remote, and worktree.
3. Enter the upstream working repository and verify official upstream, user Fork, base branch, working branch, commit, and worktree. If authorized, fetch the official remote and safely fast-forward only an eligible local base.
4. Verify the live upstream Issue, PR, comments, assignee, CI, and Review state.
5. Perform the requested investigation, implementation, or validation in the upstream working repository.
6. Return to the facts repository and update only changed records.
7. Inspect `git diff` and `git status` separately in both repositories.
8. Commit, Push, and create or update a PR only under their respective explicit approvals.
9. Report the facts repository, upstream working repository, and PR states separately.

Never use a generic `git pull` for base synchronization. Prefer an authorized `git fetch --prune <official-remote>`, followed by `git switch <base>` and `git merge --ff-only <official-remote>/<base>` only when all safety conditions hold. Never recover automatically with `reset --hard`, clean, stash, rebase, restore, branch deletion, or force-push.

## Record contract

Use one directory per issue under `issues/<owner>-<repo>-<number>/`. Maintain:

- `STATUS.yaml`: machine-readable current state, blockers, next actions, facts repository, official upstream/base, user Fork/working branch, PR, and last verification time.
- `ISSUE.md`: source facts and structured requirement summary.
- `KNOWLEDGE.md`: optional-in-content background, terms, mental models, distinctions and exceptions needed by a new reader; the file is part of new records but may remain minimal when no domain explanation is needed.
- `ANALYSIS.md`: accessible technical explanation, root cause or hypotheses, scope, and non-goals.
- `CODE-MAP.md`: relevant files, conditional Inventory, call flow, Lifecycle / Data Flow, analogous code, tests, and ownership.
- `PLAN.md`: chosen solution, alternatives, risk, and validation plan.
- `IMPLEMENTATION.md`: actual changes and reasoning.
- `TESTING.md`: commands, environment, evidence, failures, limitations, and CI results.
- `LEARNING.md`: concepts learned and reusable problem-solving methods.
- `PR.md`: official repository, user Fork, base/head branches, commits, title/body, Issue linkage, URL/number, CI, review feedback, and outcome.
- `COMMENT-DRAFT.md`: when a public comment is being considered, the exact Draft, claims/evidence, maintainer questions, publication status, approval flags, target, and post-publication URL/time.
- `JOURNAL.md`: append-only dated decisions and material actions.

Use `scripts/init_issue_record.py` to initialize a record and `scripts/validate_issue_record.py` before reporting a stage complete. Never overwrite journal history.

Inventory and Lifecycle are conditional sections, not new status values or mandatory standalone files. The record contract and suggested section shapes are defined in [research-contract.md](references/research-contract.md).

Public communication lifecycle labels are artifact metadata, not Issue statuses. Keep the existing Issue status model unchanged; track the core booleans plus the lightweight expected-identity and identity-verification gate under `public_communication` in `STATUS.yaml`.

Do not rewrite all record files on every turn. Use this minimum mapping:

- discovery or code map: `KNOWLEDGE.md` only when reader prerequisites change, `CODE-MAP.md` for source facts, plus `STATUS.yaml` and `JOURNAL.md` only when state or next action changes;
- plan: `PLAN.md` and changed status/journal facts;
- implementation: `IMPLEMENTATION.md` and changed status/journal facts;
- validation or CI: `TESTING.md` and changed status/journal facts;
- publication or review: `PR.md` and changed status/journal facts;
- terminal outcome: final status, outcome, relevant testing/PR evidence, `LEARNING.md`, `JOURNAL.md`, and the project handoff.

## Status model

Use one of: `candidate`, `screening`, `awaiting-triage`, `selected`, `analyzing`, `planned`, `implementing`, `testing`, `pr-ready`, `submitted`, `reviewing`, `merged`, `blocked`, `rejected`, `superseded`, `closed`.

Ordinary Chat normally hands off an issue after screening. Do not skip from an unverified brief directly to implementation. A contribution is complete only when its outcome and learning retrospective are recorded.

## Adaptation

Keep this workflow repository-agnostic. Infer project-specific practices from the repository. Load an ecosystem profile from `references/profiles/` only when present and applicable; repository instructions always override a profile. Add a profile only after repeated real work demonstrates reusable, stable guidance.
