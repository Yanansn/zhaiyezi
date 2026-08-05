# Historical screening output schema

This document describes the legacy `screenings/` format and remains only for
reading or validating historical records. New candidate and screening tasks
use `agent-work/tasks/<task-id>/REQUEST.yaml` and `RESULT.yaml`; a short
`REPORT.md` is optional. The Agent Protocol task schema is authoritative for
new work.

## Versions and migration

- `SCOPE.yaml` remains version 1 and may set `stage: issue-screening` or `stage: issue-evidence-collection`. Missing `stage` means legacy `issue-screening`.
- New `RESULTS.yaml` records use schema version 3.
- The validator keeps schema-v2 records readable. Only v2 accepts legacy `not-a-kubernetes-bug`; v3 uses `not-an-upstream-bug`.
- Migration is explicit: change the version and classification, then add all v3 ownership, related-item, feasibility, verification, environment, and repository-scope fields. Never silently rewrite historical records.

## Screening directory and funnel

```text
screenings/<owner>-<repository>/<scan-id>/
├── SCOPE.yaml
├── RESULTS.yaml
└── REPORT.md
```

```yaml
schema_version: 3
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

Completed scans obey:

```text
discovered = quick_filtered_out + deep_audit_queue
deep_audit_queue = deeply_audited
deeply_audited = available + watchlist + excluded_after_audit
```

Quick Filter records retain the v2 shape and are limited to explicit metadata rules: `excluded-label`, `closed-or-terminal`, `duplicate-in-scan`, `out-of-scope-category`, `language-mismatch`, or `explicit-scope-mismatch`. They require checked Issue metadata, labels, and assignees and forbid classification, confidence, and admission.

## RESULTS v3 Deep Audit

The common v2 fields remain: Issue identity, URL/title, classification/confidence, assignees, labels, audit time, sixteen boolean evidence checks, reason, limitations, recommendation, and optional/required admission according to bucket. V3 adds the following required structures.

### Ownership

```yaml
ownership:
  status: no-known-owner
  confidence: high
  signals:
    - actor: contributor
      actor_role: community-contributor
      type: comment
      strength: active-investigation
      active: true
      summary: "Reported active investigation."
      url: https://example.invalid/comment
      observed_at: "2026-08-03T00:00:00Z"
  inactivity:
    days_since_last_progress: 3
  release_signal: null
```

Statuses are `no-known-owner`, `implicit-owner`, `explicit-owner`, `abandoned`, or `unknown`. Strength is one of `weak-interest`, `conditional-interest`, `active-investigation`, `implementation-in-progress`, `implementation-ready`, or `explicit-abandonment`. Preserve the actual statement: wanting work, investigating, reproducing, finding root cause, having a local fix, promising a PR, and abandoning work are not equivalent. No assignee never proves no owner.

### Related items and semantic implementation evidence

```yaml
related_items:
  - type: pull-request
    repository: owner/repository
    number: 456
    url: https://example.invalid/pull/456
    state: open
    relationship: semantic-implementation
    explicit_issue_reference: false
    overlap:
      level: high
      files: [src/cache.py]
      behavior: "Changes the failing cache identity path."
    blocks_contribution: true
    verified_at: "2026-08-03T00:00:00Z"
```

Relationships are `explicit-implementation`, `semantic-implementation`, `partial-overlap`, `competing-implementation`, `historical-attempt`, `source-change`, `regression-source`, `downstream-workaround`, `reference-only`, or `unrelated`. A historical item may be non-blocking; a blocking item prevents Gate passage. Candidate Discovery's `no_known_related_pr` still means only that it found no known structured or explicit-number PR evidence—it never means `available`.

### Feasibility, verification, and environment

```yaml
feasibility:
  languages: [python, cpp]
  estimated_surface: {files: 3, subsystems: [cache-key]}
  runtime_dependencies: [pytorch]
  hardware:
    cpu_only_reproduction: true
    gpu_required_for_full_validation: true
    multi_gpu_required: false
  external_services: []
  model_requirements: []
  local_execution: {possible: true, highest_level: cpu-unit}
  ci_dependency: {required: true}
  design_dependency: {blocked: false}
  codex_assessment: {implementation: feasible, verification: limited, overall: limited}

verification_matrix:
  static: {required: true, status: passed, evidence: "ruff passed", reason: null}
  cpu_unit: {required: true, status: passed, evidence: "pytest test_cache.py", reason: null}
  cpu_integration: {required: false, status: not-applicable, evidence: null, reason: null}
  gpu_single: {required: true, status: not-run, evidence: null, reason: no-compatible-gpu}
  gpu_multi: {required: false, status: not-applicable, evidence: null, reason: null}
  model_e2e: {required: false, status: not-applicable, evidence: null, models: [], reason: null}
  benchmark: {required: false, status: not-planned, evidence: null, reason: null}
  upstream_ci: {required: true, status: ci-only, evidence: null, reason: protected-environment}

environment:
  os: linux
  architecture: x86_64
  python: "3.12"
  compiler: null
  pytorch: null
  cuda: null
  rocm: null
  gpu: null
  driver: null
  vllm: null
  base_commit: abc123
```

Verification statuses are `not-planned`, `not-applicable`, `pending`, `passed`, `failed`, `blocked`, `not-run`, and `ci-only`. Passed requires evidence; failed/blocked/not-run/ci-only require a reason; a required layer cannot be not-applicable. Null environment values are valid when unknown and must not be guessed. Implementation completion does not imply GPU, model, distributed, benchmark, or project-CI completion.

### Repository scope

```yaml
repository_scope:
  primary: {repository: LMCache/LMCache, issue: "LMCache/LMCache#123"}
  related: [vllm-project/vllm]
  expected_change_repositories: [LMCache/LMCache]
  excluded_change_repositories: [vllm-project/vllm]
  scope_status: single-repository
  working_repositories:
    - {repository: LMCache/LMCache, remote: null, base: dev, branch: null, commit: null, worktree: not-verified, push_authorized: false}
```

Allowed scope statuses are `single-repository`, `multi-repository-confirmed`, and `scope-expansion-required`. Expected changes outside the primary repository require confirmed multi-repository scope or a pause for expansion. A candidate cannot pass admission while expansion is required. Related repositories are read-only unless separately authorized; each working repository keeps independent Git and Push evidence.

## Admission

Available candidates retain the v2 admission mapping: Gate status, evidence refresh, user decision, medium-confidence limitation acceptance, three independent authorization booleans, admission time, and notes. `passed` requires `available`, high/accepted-medium confidence, refreshed evidence, `user_decision: continue`, no blocking related item, and no pending repository scope expansion. Gate passage never grants registry, Issue initialization, Commit, Push, or publication permission.

## Evidence-only schema v1

```text
screenings/<owner>-<repository>/<scan-id>/
├── SCOPE.yaml                 # stage: issue-evidence-collection
├── REPORT.md
└── evidence/<issue-number>.yaml
```

Copy `templates/evidence/ISSUE-EVIDENCE.yaml`. Record complete body, paginated comments, visible Timeline and Development items, explicit-number/title-symptom/symbol search results, extracted ownership signals, structured related items, and limitations. Evidence files use `schema_version: 1` and `stage: issue-evidence-collection`. They forbid classification, confidence, admission, and `available`; the directory forbids `RESULTS.yaml`.

## Report

Lead with outcome, bounded scope, funnel or evidence completeness, limitations, Gate state when applicable, and the next authorized step. Never lower audit quality to manufacture an available candidate.
