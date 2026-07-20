# Screening output schema

This is the authoritative schema for persisted screening results. Other screening documents reference it rather than restating the complete data model.

Store one bounded scan under:

```text
screenings/<owner>-<repository>/<YYYY-MM-DD>-<scan-id>/
├── SCOPE.yaml
├── RESULTS.yaml
└── REPORT.md
```

Use `templates/screening/` through `scripts/init_screening_record.py`. Do not create full `issues/` directories for filtered, excluded, or watchlisted candidates.

## SCOPE.yaml

`SCOPE.yaml` remains schema version 1. It records repository, scan ID/times, candidate limit, sort/state, include/exclude labels and categories, technical preferences, search capabilities, and limitations. Unknown capabilities must be false or recorded as limitations.

## RESULTS.yaml schema version 2

```yaml
schema_version: 2
scan_id: scan-id
repository: owner/repository

summary:
  discovered: 0
  quick_filtered_out: 0
  deep_audit_queue: 0
  deeply_audited: 0
  available: 0
  watchlist: 0
  excluded_after_audit: 0

quick_filtered_out: []
available: []
watchlist: []
excluded_after_audit: []
```

Schema version 2 persists only completed scans; an enqueued-but-not-audited intermediate state is unsupported. The exact funnel equations are:

```text
discovered = quick_filtered_out + deep_audit_queue
deep_audit_queue = deeply_audited
deeply_audited = available + watchlist + excluded_after_audit
discovered = quick_filtered_out + available + watchlist + excluded_after_audit
```

Every summary bucket count must equal its list length. The validator rejects legacy `quick_filtered` and `excluded` names.

## Quick Filter record

`quick_filtered_out` contains Stage 2 exclusions based only on explicit, low-cost, reproducible metadata rules:

```yaml
- issue: "owner/repo#123"
  url: https://example.invalid/issue/123
  title: Example
  filtered_at: "2026-07-20T00:00:00Z"
  rule: excluded-label
  reason: "Matches an explicitly excluded label."
  metadata:
    state: open
    labels: []
    assignees: []
  evidence:
    issue_metadata_checked: true
    labels_checked: true
    assignees_checked: true
  limitations: []
```

Allowed rules:

```text
excluded-label
closed-or-terminal
duplicate-in-scan
out-of-scope-category
language-mismatch
explicit-scope-mismatch
```

The three minimum evidence values must be boolean `true`. Quick Filter records must not contain `screening_classification`, `screening_confidence`, or `admission`. If exclusion needs complete comments, PR search, ownership judgment, or design analysis, it belongs in Deep Audit.

## Deep Audit record

The `available`, `watchlist`, and `excluded_after_audit` buckets use the common fields below:

```yaml
- issue:
  url:
  title:
  screening_classification:
  screening_confidence:
  assignees: []
  labels: []
  audited_at:
  evidence:
    issue_body_checked:
    labels_checked:
    assignees_checked:
    all_comments_checked:
    development_checked:
    issue_number_search_checked:
    fixes_search_checked:
    related_search_checked:
    closes_search_checked:
    refs_search_checked:
    title_keyword_search_checked:
    symbol_search_checked:
    linked_prs_checked:
    ownership_checked:
    design_checked:
    complexity_checked:
  related_items: []
  reason:
  limitations: []
  recommended_next_action:
```

All sixteen evidence keys must exist and be boolean. `available` requires classification `available`, confidence `high` or `medium`, all evidence `true`, non-empty audit time/reason/next action, and an `admission` mapping. Classification alone never means Gate passed.

`watchlist` permits only `watchlist` or `insufficient-evidence` and additionally requires a non-empty `recheck_trigger`.

`excluded_after_audit` permits every defined classification except `available`, `watchlist`, and `insufficient-evidence`.

## Admission record

Every available candidate includes:

```yaml
admission:
  gate_status: not-evaluated
  evidence_refreshed_at: null
  user_decision: pending
  medium_confidence_limitations_accepted: false
  accepted_limitations: []
  registry_mutation_authorized: false
  issue_initialization_authorized: false
  contribution_brief_authorized: false
  admitted_at: null
  notes: null
```

Allowed `gate_status` values are `not-evaluated`, `awaiting-user-decision`, `passed`, `failed`, and `stale-recheck-required`. Allowed `user_decision` values are `pending`, `continue`, and `decline`.

`passed` requires `user_decision: continue`, non-empty `evidence_refreshed_at` and `admitted_at`, and an available classification. Medium-confidence candidates additionally require `medium_confidence_limitations_accepted: true` and a non-empty `accepted_limitations` list. High-confidence candidates need no accepted limitation.

`user_decision: decline` cannot accompany `passed`. Registry mutation, formal Issue initialization, and contribution-Brief authorization are independent booleans; Gate passage never changes or implies them. Non-available candidates need no admission record and can never carry `gate_status: passed`.

## REPORT.md

Lead with the outcome. Include scope/rules/time, the schema-v2 funnel, Quick Filter exclusions, available candidates, watchlist, exclusions after audit, Admission Gate state, search/access limitations, and next step. If none passed Deep Audit, state:

> 本轮没有通过完整审计的可认领 Issue。

Never lower the audit standard to produce an available result.
