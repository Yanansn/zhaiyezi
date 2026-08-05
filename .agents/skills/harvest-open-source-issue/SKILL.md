---
name: harvest-open-source-issue
description: Execute one bounded contribution stage from a confirmed Agent task, with independent repository checks, targeted validation, and explicit public-action gates.
---

# Harvest Open Source Issues

This Skill covers accepted Issue work: ecosystem analysis when needed, code
mapping, planning, implementation, testing, review response, and publication
preparation. It does not discover unbounded candidates or infer authorization.

## Agent ownership

- `agent:terra` owns code map, plan, implementation, tests, and local diagnosis.
- `agent:luna` supplies evidence, screening facts, and decision proposals.
- `agent:sol` reviews architecture, concurrency, difficult failures, and
  high-risk final decisions; it does not implement.
- `user` owns target-fork Push, PR creation, comments, reviews, labels,
  assignments, and all other public GitHub actions.

## Shared Preflight

Require a valid current `REQUEST.yaml` with one stage, exact goal, deliverables,
constraints, and approval boundary. Then:

1. Run `python3 scripts/validate_agent_protocol.py`.
2. Check facts repository branch, HEAD, remote, and worktree.
3. For code work, independently check the target repository path, branch, HEAD,
   remotes, base, working branch, and worktree.
4. Resolve remote roles from URLs; never assume `origin` is the fork.
5. Stop on dirty or unknown state, divergent bases, stale scope, missing brief,
   or an action not explicitly authorized.

Fetch, fast-forward, merge, rebase, force-push, upstream modification, and
public actions each require their own explicit authorization.

## Minimum records by stage

Use only the smallest applicable set:

| Stage | Required records |
| --- | --- |
| evidence / screening | task `REQUEST.yaml` and `RESULT.yaml`; optional short `REPORT.md` |
| ecosystem or discussion re-analysis | `ECOSYSTEM.md`, plus `STATUS.yaml`/`JOURNAL.md` when state changes |
| code map | `CODE-MAP.md` |
| plan | `PLAN.md` |
| implementation | `IMPLEMENTATION.md` |
| validation | `TESTING.md` |
| publication | `PR.md` and the exact public Draft |
| terminal outcome | changed status, `JOURNAL.md`, and `LEARNING.md` when useful |

`PROJECT.yaml`, `ISSUE.md`, `KNOWLEDGE.md`, `ECOSYSTEM.md`, `COMMENT-DRAFT.md`
and `LEARNING.md` are conditional unless the task or changed facts require
them. Do not create placeholder documents merely to satisfy a checklist.

## Stage rules

### Environment feasibility before analysis or implementation

Before a Deep Audit, plan, or implementation task, confirm the minimum runtime
and dependency path needed for the Issue. Record available hardware, model,
framework, integration, external-service, and cross-repository requirements.
If the required environment is unavailable, use the cheapest meaningful
alternative (source facts, CPU/unit tests, or public CI evidence) only when it
can answer the bounded question. Otherwise stop before implementation and
record the limitation; do not spend a full reproduction or implementation
budget merely to discover that validation is impossible.

CI-only continuation is allowed only when the task explicitly accepts that risk
or maintainer/upstream evidence makes the boundary sufficiently clear. Missing
environment must lower feasibility or remain a limitation; it must not be
silently treated as Issue invalidity or implementation authorization.

### Ecosystem and discussion

Create or refresh `ECOSYSTEM.md` when the Issue is active and ecosystem facts
could affect ownership, scope, feasibility, acceptance, or implementation.
For binding-only, protocol, pure code-verification, or facts-only tasks, record
the limitation and do not perform a full ecosystem audit. New comments, PRs,
Timeline events, workarounds, or CI evidence that may change the decision force
discussion re-analysis and pause implementation.

### Code map and plan

Read the relevant source, ownership files, analogous code, and tests. Build an
Inventory or Lifecycle/Data Flow only when it affects the boundary. Keep source
facts in `CODE-MAP.md` and inference, risks, alternatives, and unresolved
questions in `ANALYSIS.md` when that file is needed. Do not call a keyword
search a complete inventory.

Implementation requires a confirmed boundary, explicit non-goals, acceptance
criteria, and a new task that authorizes local modification. Scope expansion or
material new discussion pauses coding.

### Implementation and validation

Modify only the target working repository and keep the change focused. Run the
narrowest meaningful checks first, then proportional integration/CI checks.
Record exact commands, environment, results, failures, and limitations in
`TESTING.md`. Never claim GPU, distributed, benchmark, or CI coverage from a
smaller local test.

### Publication

Prepare an exact Draft before any public action. Sol or an equivalent technical
review may review high-risk content, but publication always requires explicit
User approval and live identity verification. Immediately before publication,
recheck target, base/head, content, authorization, identity, and worktree.
After publication, record URL, time, actual content, and maintainer feedback.

## Repository boundary

Facts repository and upstream working repository remain separate. Never commit
upstream source into facts, and never commit facts artifacts into upstream.
Inspect both repositories separately at the end of every stage and report what
was committed, pushed, published, or left local.

## Stop and return

Stop instead of broadening the task when scope, ownership, baseline, required
evidence, authorization, or public identity is unclear. Return the changed
records, validation commands/results, limitations, Git state, and the next
bounded action. Do not infer admission or implementation permission from a
completed audit or decision.
