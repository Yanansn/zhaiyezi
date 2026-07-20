---
name: screen-open-source-issue
description: Scan and rigorously audit candidate open-source Issues to identify work that is safe and worthwhile to admit into the zhaiyezi contribution workflow; this Skill does not implement source changes or perform unapproved public actions.
---

# Screen Open Source Issues

Use this Skill only with a bounded issue-screening Execution Brief. It discovers and audits candidates, records lightweight results, and applies the Candidate Admission Gate. It does not implement fixes, initialize formal Issue records without approval, or publish comments, assignments, labels, branches, commits, pushes, or PRs.

After admission, hand the candidate to `harvest-open-source-issue`; do not copy that Skill's ecosystem research, code-map, implementation, testing, or PR lifecycle into this one.

## Intake

Require these fields:

```yaml
repository:
candidate_scope:
include_labels: []
exclude_labels: []
technical_preferences: {}
scan_date:
```

Example:

```yaml
repository: kubernetes/kubernetes
candidate_scope:
  latest: 80
include_labels:
  - kind/bug
  - kind/failing-test
  - kind/flake
exclude_labels:
  - kind/feature
  - kind/documentation
technical_preferences:
  languages: [go]
  areas: []
scan_date: 2026-07-20
```

Reject an absent or unbounded Brief. Confirm the facts-repository branch, HEAD, remote, and worktree before writing. Stop on unknown local changes. Read [execution-brief.md](references/execution-brief.md) for the approval contract.

## Workflow

1. Create the scan scope and lightweight record using `scripts/init_screening_record.py` when authorized.
2. Follow all fourteen stages in [audit-workflow.md](references/audit-workflow.md).
3. Apply the minimum searches and result classifications in [search-contract.md](references/search-contract.md).
4. Classify candidates and confidence using [classifications.md](references/classifications.md).
5. Persist concise evidence using [output-schema.md](references/output-schema.md); excluded candidates do not receive `issues/` directories.
6. Validate the record with `scripts/validate_screening_record.py`.
7. Apply [candidate-admission-gate.md](references/candidate-admission-gate.md). Admission still requires the user's explicit choice.
8. Use [regression-cases.md](references/regression-cases.md) when reviewing rule changes.

## Non-negotiable evidence rules

- No assignee does not mean available.
- An empty Development section does not mean no PR exists.
- No displayed linked PR does not prove no implementation exists.
- Development is one evidence source, never the complete search.
- Every `available` result must complete every mandatory audit and search.
- Missing or inaccessible evidence produces `insufficient-evidence` or `watchlist`, never a guess.
- Open every high-relevance Issue, PR, commit, or Discussion and classify its relationship.
- Respect explicit investigation or implementation ownership even when no assignee or PR exists.
- Quick Filter records are metadata-only exclusions and do not carry Deep Audit classifications, confidence, or admission state.
- `screening_classification: available` does not mean the Candidate Admission Gate passed; persist Gate evaluation separately in `admission`.

## Record layers

```text
Quick Filter record
≠ Deep Audit classification
≠ Candidate Admission Gate decision
```

Stage 2 may emit `quick_filtered_out` only for explicit, low-cost, reproducible rules. Anything requiring full comments, PR search, ownership judgment, or design analysis enters Deep Audit. Stage 13 assigns classification and confidence to Deep Audit candidates. Stage 14 updates only the `admission` mapping of an `available` candidate. The authoritative schema is [output-schema.md](references/output-schema.md).

## Boundary with the contribution lifecycle

Screening classifications are not Issue statuses. `available` means only that the Deep Audit found no known conflict or blocker. It means neither Gate passed nor `selected`.

```text
screening_classification: available
+ Candidate Admission Gate passed
+ user approval
→ registry entry
→ status: candidate or screening
→ harvest-open-source-issue
```

Modifying `registry/issues.yaml`, initializing an Issue record, committing or pushing the facts repository, and every public action are separate approvals. Default all of them to prohibited.
