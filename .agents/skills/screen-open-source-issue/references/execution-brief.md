# Screening collaboration Briefs

This contract defines three distinct inputs. The default is a Chat-produced `Screening Result Brief` that Codex records without repeating the investigation. A complete Codex Screening requires explicit user authorization. A `Code Verification Brief` authorizes only enumerated source-code checks. All are distinct from the contribution-stage Brief used by `harvest-open-source-issue`.

## Default: Screening Result Brief

Chat completes Candidate Discovery, Quick Filter, Deep Audit, Classification, and Screening Recommendation, then supplies:

```yaml
brief_type: screening-result
stage: screening-record
produced_by: chat

repository: owner/repository
scan_date: YYYY-MM-DD
candidate_scope: {}

screening_result:
  candidates: []
  recommendation_summary:
  evidence_summary: []
  limitations: []
  candidate_admission_gate_recommendations: []

output_location: screenings/<owner>-<repository>/<scan-id>

baseline:
  facts_repository: Yanansn/zhaiyezi
  local_path:
  expected_branch:
  expected_commit: verify-before-start
  expected_worktree: clean

approval:
  create_screening_records: allowed
  modify_registry: prohibited
  initialize_issue_record: prohibited
  commit_facts_repository: prohibited
  push_facts_repository: prohibited
```

Candidate data must contain enough classification, confidence, recommendation, evidence, limitations, and Gate recommendation information to produce schema-valid `SCOPE.yaml`, `RESULTS.yaml`, and `REPORT.md`. Codex treats it as factual input. It checks completeness and record consistency but does not reopen Issues, search PRs, reassess owners, or repeat Deep Audit. Missing or contradictory facts are returned to Chat for correction.

## Exception: complete Codex Screening Brief

This mode authorizes one bounded candidate investigation only when the user explicitly asks Codex to perform the complete Screening.

```yaml
brief_type: complete-codex-screening
stage: issue-screening

repository: owner/repository
candidate_scope:
  latest: 80
  state: open
  sort: created-desc
include_labels: []
exclude_labels: []
technical_preferences:
  languages: []
  areas: []
scan_date: YYYY-MM-DD

required_checks:
  full_comments: true
  timeline_and_development: true
  issue_number_references: true
  title_and_symptoms: true
  symbols_and_files: true
  linked_items: true
  ownership: true
  design_and_scope: true
  complexity_and_feasibility: true

output_location: screenings/<owner>-<repository>/<scan-id>

baseline:
  facts_repository: Yanansn/zhaiyezi
  local_path:
  expected_branch:
  expected_commit: verify-before-start
  expected_worktree: clean

approval:
  create_screening_records: allowed
  modify_registry: prohibited
  initialize_issue_record: prohibited
  publish_public_comment: prohibited
  assign_issue: prohibited
  commit_facts_repository: prohibited
  push_facts_repository: prohibited
```

### Required complete-Screening content

- A finite candidate count, explicit Issue list, date range, or equivalent bounded scope.
- Inclusion/exclusion rules and technical preferences.
- Required audit depth and search/access limitations already known.
- Exact output location and expected facts-repository state.
- Separate approval values for every mutation or public action.
- Expected deliverables, stop conditions, and return format.

Missing approval fields mean `prohibited`. `create_screening_records` permits only the lightweight scan directory. It does not authorize registry changes, formal Issue initialization, Commit, Push, assignment, comment, label changes, or PR work.

## Exception: Code Verification Brief

```yaml
brief_type: code-verification
stage: code-verification

repository: owner/repository
source_baseline:
  local_path:
  branch:
  commit: verify-before-start

facts_to_verify:
  - question:
    paths_or_symbols: []
    required_evidence: []

constraints:
  repeat_issue_screening: prohibited
  inspect_issue_or_pr_ownership: prohibited
  assign_classification: prohibited
  make_gate_recommendation: prohibited

output:
  code_facts:
  commands_and_results:
  limitations:

approval:
  fetch_official_upstream: prohibited
  modify_files: prohibited
  commit_facts_repository: prohibited
  push_facts_repository: prohibited
```

Codex verifies only the listed code facts, such as whether the current baseline already contains a fix, whether a function/test exists, whether the path crosses packages, or whether a targeted local check can run. It does not repeat the Issue/PR/Owner/design audit. Fetching or any mutation retains its own approval boundary.

## Stop conditions

Stop and report before mutation when the Brief is absent/unbounded, repository baseline differs materially, unknown local changes exist, a requested action exceeds approval, or the output path already exists. For a Screening Result Brief, missing schema-required facts are a Chat handback, not permission for Codex to investigate GitHub. For explicitly authorized complete Screening, also stop when required search access is unavailable for the requested confidence. Do not broaden any mode to compensate.

## Return contract

For Screening Result recording or complete Screening, report schema-v2 funnel counts (`quick_filtered_out` separately from all Deep Audit buckets), classifications/confidence/limitations, persisted admission state, files changed, validation outcomes, and Git state. For Code Verification, report only the requested code facts, baseline, commands, results, and limitations. Always state which of Commit, Push, registry mutation, formal Issue initialization, and public actions were or were not performed.

Quick Filter records never carry screening classification/confidence or admission data. Candidate Admission Gate evaluation updates the independent `admission` mapping and never authorizes registry mutation, Issue initialization, or contribution-Brief creation by implication. Use [output-schema.md](output-schema.md) as the authoritative data contract.
