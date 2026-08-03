# LMCache #4086 Deep Audit

## Outcome

Do not start a separate contribution for `LMCache/LMCache#4086` now. The
recommended screening classification is `implementation-pr-exists` with high
confidence: open PR #2932 changes the same 16-bit multimodal identifier
projection identified by the Issue and adds focused tests. It does not mention
#4086 explicitly, but its behavior and file overlap make it a semantic
implementation rather than an unrelated keyword match.

This result is not formal contribution admission. No registry entry, formal
Issue record, contribution status, or `REVIEW.yaml` was created.

## Request and materialization

The user supplied the bounded Chat decision to audit only the existing evidence.
Codex materialized that decision as `REQUEST.yaml` with Chat retained as
`decision_author` and Codex recorded only as `materialized_by`. Codex then made
and recorded the Deep Audit judgment in the Codex-owned `RESULT.yaml` and this
report. Materialization did not grant any upstream or public action.

## Evidence reviewed

The evidence collection completed the Issue body, its one comment, visible
Timeline and Development relationships, explicit-number PR searches,
title/symptom and symbol searches, current-`dev` source excerpts, ownership
signals, and feasibility leads. Its inspected baseline was
`dev@a012dd9977eb1482940b70a9f8a196734cb9c7ff`, collected at
`2026-08-03T08:32:14Z`.

No PR was linked through Development or found by the five explicit #4086
queries. That absence is not treated as proof that no implementation exists;
the semantic searches identified the overlapping work below.

## Related implementation findings

- PR #2932 is open and is the primary blocking semantic implementation. It
  replaces 16-bit multimodal key material with a signed-int64-safe 63-bit value
  in the same vLLM integration utility and adds unit tests. Although its body
  names Issue #3301 rather than #4086, it substantially implements the collision
  mitigation proposed in #4086.
- PR #3902 is open but only partially overlaps: it adds VLM-aware identity for
  MP CacheBlend and explicitly fails closed for a non-MP V1 path.
- PR #4176 is open and partially overlaps through broader MP/SGLang multimodal
  cache identity work.
- PR #4183 is merged and added MP multimodal key identity plus tests for the
  same-prompt/different-image behavior, while retaining the 16-bit projection
  addressed by PR #2932.

The Issue comment also says the relevant non-MP mode is planned for gradual
deprecation, while inviting a fix. That makes a distinct contribution possible
in principle, but less attractive while the direct semantic PR remains open.

## Screening decision

- Classification: `implementation-pr-exists`
- Confidence: high for the classification
- Contribution recommendation: do not pursue a duplicate implementation now
- Admission: ineligible; not evaluated as `available`

High confidence here means the collected evidence clearly establishes an active
semantic implementation. It does not claim that PR #2932 is already merged or
that it has been proven by runtime reproduction to resolve every connector path.

## Limitations

This audit intentionally used only the existing evidence. It did not refresh
GitHub, clone or fetch LMCache, run LMCache tests, reproduce the GPU/model
failure, or audit vLLM source. GitHub Classic Projects was unavailable during
collection, and broad `CacheEngineKey`/`ObjectKey` searches were representative
rather than a complete inventory. These limitations prevent a complete-fix
claim but do not negate the observed active PR overlap.

## Next action

Monitor PR #2932 and Issue #4086. Re-run a bounded evidence refresh if PR #2932
closes without merge, materially changes scope, or maintainers identify a
separate unimplemented boundary. Any registry change, formal contribution
initialization, upstream work, or public interaction requires a new explicit
authorization.
