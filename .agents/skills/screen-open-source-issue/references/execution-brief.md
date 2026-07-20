# Issue-screening Execution Brief

This Brief authorizes one bounded candidate scan. It is distinct from the contribution-stage Brief used by `harvest-open-source-issue`.

```yaml
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

## Required Brief content

- A finite candidate count, explicit Issue list, date range, or equivalent bounded scope.
- Inclusion/exclusion rules and technical preferences.
- Required audit depth and search/access limitations already known.
- Exact output location and expected facts-repository state.
- Separate approval values for every mutation or public action.
- Expected deliverables, stop conditions, and return format.

Missing approval fields mean `prohibited`. `create_screening_records` permits only the lightweight scan directory. It does not authorize registry changes, formal Issue initialization, Commit, Push, assignment, comment, label changes, or PR work.

## Stop conditions

Stop and report before mutation when the Brief is absent/unbounded, repository baseline differs materially, unknown local changes exist, required search access is unavailable for the requested confidence, a requested action exceeds approval, or the output path already exists. Do not broaden the scan to compensate.

## Return contract

Report schema-v2 funnel counts (`quick_filtered_out` separately from all Deep Audit buckets); final classifications/confidence and limitations; persisted admission state for available candidates; files changed; validation commands and outcomes; branch, HEAD, worktree, diff status; and which of Commit, Push, registry mutation, formal Issue initialization, and public actions were or were not performed.

Quick Filter records never carry screening classification/confidence or admission data. Candidate Admission Gate evaluation updates the independent `admission` mapping and never authorizes registry mutation, Issue initialization, or contribution-Brief creation by implication. Use [output-schema.md](output-schema.md) as the authoritative data contract.
