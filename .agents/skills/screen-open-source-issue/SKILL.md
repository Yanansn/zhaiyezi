---
name: screen-open-source-issue
description: Record Chat-produced candidate screening results by default, or rigorously audit bounded open-source Issues only when the user explicitly asks Codex to screen them; this Skill does not implement fixes or perform unapproved public actions.
---

# Screen Open Source Issues

By default, use this Skill to record a bounded `Screening Result Brief` produced by Chat. Chat performs candidate discovery, Quick Filter, Deep Audit, classification, and recommendation; Codex treats that result as factual input and does not repeat the GitHub investigation. Codex initializes and updates the lightweight screening record, runs the validator, updates handoff facts when needed, and performs Git operations only when separately authorized.

Codex performs the complete screening investigation only when the user explicitly requests Codex to do so. `issue-evidence-collection` is a separate bounded mode that collects raw Issue, discussion, relationship, search, and ownership-signal evidence without assigning a classification. A `Code Verification Brief` authorizes only listed source-code facts; neither narrow mode authorizes a complete Screening.

This Skill does not implement fixes, initialize formal Issue records without approval, or publish comments, assignments, labels, branches, commits, pushes, or PRs.

After admission, hand the candidate to `harvest-open-source-issue`; do not copy that Skill's ecosystem research, code-map, implementation, testing, or PR lifecycle into this one.

## Operating modes and intake

### Default: record a Chat Screening Result Brief

Require a bounded Brief containing the candidate set, classifications, confidence, recommendations, evidence summaries, limitations, Gate recommendation, scan scope/time, output location, and approval boundaries. Validate internal completeness and schema compatibility, but do not reopen Issues, search PRs, re-evaluate ownership, or repeat Deep Audit. If required record data is missing or contradictory, report the gap instead of investigating it yourself.

The default Codex workflow is:

1. Verify the facts-repository baseline and approval boundary.
2. Initialize the screening record when authorized.
3. Record the supplied facts in `SCOPE.yaml`, `RESULTS.yaml`, and `REPORT.md`.
4. Run `scripts/validate_screening_record.py` and report any Brief/schema gaps.
5. Update `HANDOFF.md` only when the durable handoff summary changes.
6. Commit or Push only under separate explicit authorization.

### Exception: user-authorized complete Codex Screening

Only an explicit user request for Codex to screen a bounded candidate set activates the full investigation workflow below. Require these fields:

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

Reject an absent or unbounded Brief. Confirm the facts-repository branch, HEAD, remote, and worktree before writing. Stop on unknown local changes. Read [execution-brief.md](references/execution-brief.md) for all three input modes and the approval contract.

### Exception: Code Verification Brief

Verify only the enumerated code facts and return source paths, baseline, commands, results, and limitations. Do not inspect the complete Issue ecosystem, search for ownership or competing PRs, assign a screening classification, or make a Gate recommendation unless the Brief separately and explicitly authorizes complete Screening.

### Exception: issue-evidence-collection

Require a bounded Issue list, scan ID, output location, evidence sources, and access/approval boundary. Collect the full Issue body, all comments with pagination completeness, visible Timeline and Development relations, explicit-number PR evidence, raw title/symptom/symbol search results, unjudged ownership signals, related items, and limitations under `evidence/<issue-number>.yaml`.

This mode must not emit `RESULTS.yaml`, `screening_classification`, confidence, `available`, admission, registry changes, formal Issue directories, assignment, comments, or publication. A later Chat or explicitly authorized complete Screening may interpret the evidence, but the collection step itself does not.

## Full investigation workflow (explicit authorization only)

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

Candidate Discovery remains a low-cost locator. Its `related_pr_found` means PR evidence was found; `no_known_related_pr` means no known structured or explicit-number PR evidence was found; `insufficient_evidence` cannot enter an availability decision. Semantic PRs, implicit owners, and current-base fixes remain Deep Audit work.

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
