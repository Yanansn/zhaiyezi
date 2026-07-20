# Candidate audit workflow

This is the normative stage order. Save concise facts and URLs in `RESULTS.yaml` and user-facing conclusions in `REPORT.md`. A hard exclusion may stop expensive later checks, but only candidates completing every stage may be `available`.

## Stage 1 — Candidate Discovery

- Input: repository, bounded scope, include/exclude labels, scan time.
- Checks: query exactly the requested state, ordering, limit, and label scope; retain discovery URLs or query details.
- Conclusions: discovered or out-of-scope.
- Stop: query cannot be reproduced or scope is unbounded.
- Evidence: query, retrieval time, count, limitations.

## Stage 2 — Quick Filter

- Input: discovered candidates.
- Checks: state, include/exclude labels, obvious category mismatch, duplicate, terminal resolution.
- Conclusions: deep-audit queue or `quick_filtered_out` with one allowed low-cost rule.
- Stop: explicit excluded label/category or clearly closed/out of scope.
- Evidence: Issue URL/title, filter time/rule/reason, state, labels, assignees, and the three minimum metadata checks defined by `output-schema.md`.

Quick Filter does not read the complete discussion or assign `screening_classification`, `screening_confidence`, or `admission`. If exclusion requires PR search, ownership judgment, design analysis, or any other Deep Audit evidence, enqueue the candidate instead.

## Stage 3 — Issue Metadata Audit

- Input: deep-audit candidate.
- Checks: full body, author, state, labels, assignees, milestone, project visibility, timestamps, component/SIG.
- Conclusions: continue, occupied, blocked, or insufficient evidence.
- Stop: authoritative metadata establishes a hard blocker.
- Evidence: audited time, metadata summary, unavailable fields.

## Stage 4 — Full Comment Audit

- Input: Issue and all comment pages.
- Checks: read every comment in context; detect reproduction, root-cause, ownership, implementation, abandonment, and maintainer direction.
- Conclusions: continue, implicit-owner, author-implementation, watchlist, or blocker.
- Stop: pagination or comments cannot be completed for an `available` decision.
- Evidence: page completeness, relevant comment URLs, author/role, concise meaning.

## Stage 5 — Development Audit

- Input: Development UI/API relationships and Timeline.
- Checks: linked branches, PRs, commits, cross-references, auto-closing references; record visibility limits.
- Conclusions: continue or an implementation-related classification.
- Stop: none—an empty Development result never completes the search.
- Evidence: every visible related item and its relationship.

## Stage 6 — Issue Number Reference Search

- Input: repository and Issue number.
- Checks: search `#<number>`, `Fixes #<number>`, `Closes #<number>`, `Related-to #<number>`, and `Refs #<number>` across relevant Issues and PRs.
- Conclusions: continue or linked-work classification.
- Stop: incomplete search forbids `available` and high confidence.
- Evidence: queries, timestamps, relevant and zero-result summaries.

## Stage 7 — Title and Symptom Search

- Input: title, error text, test name, log fragments, component.
- Checks: search distinctive combinations and common variants; avoid treating generic keyword matches as the same bug.
- Conclusions: continue, historical/competing work, already fixed, or unrelated.
- Stop: key symptom cannot be searched or validated.
- Evidence: queries and classified high-relevance results.

## Stage 8 — Function/File/Symbol Search

- Input: body/comments and, when needed, current upstream source.
- Checks: search core functions, structs, variables, files, tests, components, and SIG terms; verify symbols exist on the current base.
- Conclusions: bounded/unbounded surface, third-party/infrastructure, or insufficient evidence.
- Stop: required source access or symbol search unavailable.
- Evidence: searched symbols/paths, current base/time, limitations.

## Stage 9 — Linked PR Audit

- Input: all high-relevance PRs and commits from Stages 5–8.
- Checks: open each item; read body, status, commits, review, CI, closure/merge reason, base/head, and actual scope.
- Conclusions: upstream-implementation, competing-implementation, source-or-regression-pr, downstream-workaround, historical-related-work, reference-only, or unrelated.
- Stop: a relevant PR cannot be opened or its status cannot be verified.
- Evidence: URLs, current state, relationship, review/merge implications.

## Stage 10 — Ownership Audit

- Input: assignees, author, all comments, linked work, contribution conventions.
- Checks: explicit and implicit ownership, activity age, abandonment, maintainer reopening, and contributor progress.
- Conclusions: occupied, implicit-owner, author-implementation, or no known owner.
- Stop: unresolved ownership forbids `available`.
- Evidence: exact contextual signal, author, URL/date, current interpretation.

## Stage 11 — Design and Scope Audit

- Input: Issue contract, maintainer discussion, APIs and linked design work.
- Checks: problem clarity, desired behavior, non-goals, compatibility, required SIG/design decision, conflicting directions.
- Conclusions: clear enough, blocked-by-design, watchlist, or insufficient-evidence.
- Stop: solution choice depends on an unresolved design decision.
- Evidence: decision statements, remaining ambiguity, authority and date.

## Stage 12 — Complexity and Feasibility Audit

- Input: apparent code surface, tests, environment, ownership, preferences.
- Checks: independent completion, language fit, local/CI testability, hardware/cloud/proprietary dependencies, cross-repository scope, review path.
- Conclusions: feasible, infrastructure, third-party, watchlist, or do-not-pursue.
- Stop: required access or cost exceeds the Brief.
- Evidence: affected areas, validation route, dependencies, risk summary.

## Stage 13 — Final Classification

- Input: completed evidence.
- Checks: use one allowed classification and confidence from `classifications.md`; hard blockers override scores or preferences.
- Conclusions: final `screening_classification`, `screening_confidence`, reason, and next action in `available`, `watchlist`, or `excluded_after_audit`.
- Stop: contradictory or missing facts become `insufficient-evidence` or `watchlist`.
- Evidence: concise evidence chain, limitations, audited time.

## Stage 14 — Candidate Admission Gate

- Input: an `available` candidate and completed record.
- Checks: apply every condition in `candidate-admission-gate.md`; obtain explicit user approval for admission actions.
- Conclusions: update the available candidate's independent `admission` mapping; do not alter its classification to represent Gate state.
- Stop: any failed Gate condition or missing approval.
- Evidence: Gate decision, decision time, user authorization, separately authorized mutations.

## Mandatory flow

```text
Issue → metadata Quick Filter (`quick_filtered_out` or Deep Audit queue)
→ body → labels → assignee → comments → Development
→ number and closing-reference searches
→ title, error, test, log and symbol searches
→ open every related PR/commit/Issue/Discussion
→ classify source, implementation, competition, workaround, history,
  ownership and design blockers
→ final classification → Candidate Admission Gate
```
