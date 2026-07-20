# Search contract

For every deeply audited candidate, record the query, execution time, result scope, relevant URLs, relationship classifications, and limitations.

## Minimum reference searches

Run all of:

```text
#<issue-number>
Fixes #<issue-number>
Closes #<issue-number>
Related-to #<issue-number>
Refs #<issue-number>
```

Search Issues and PRs, and commits or code where the platform supports them. Development and cross-reference panels are supplemental evidence.

## Semantic and source searches

Search distinctive combinations of:

- core title terms;
- exact error messages, test names, and log fragments;
- core function, struct, variable, and file names;
- component, subsystem, SIG, or ownership names.

Open every high-relevance result. Verify its actual scope and current state before classifying it. Generic keyword overlap is not proof of the same defect.

## Relationship classifications

- `upstream-implementation`: an upstream change intended to fix the candidate.
- `competing-implementation`: another active implementation of substantially the same work.
- `source-or-regression-pr`: the change that introduced or exposed the behavior.
- `downstream-workaround`: downstream mitigation without an upstream fix.
- `historical-related-work`: prior work that informs but does not currently implement the candidate.
- `reference-only`: mentions the candidate without implementing or proving it.
- `unrelated`: matched terms but addresses a different problem.

Do not infer that a cross-reference is an implementation, a closed PR resolved the Issue, a merged PR is present and complete on the current base, or a keyword match is the same defect. Verify merge commit/base and current behavior when claiming `already-implemented` or `already-fixed`.

When search, pagination, Timeline, Development, Project, PR, or code access is limited, record:

```yaml
search_limitations:
  - "description of the missing capability and its impact"
```

Lower confidence. A limitation affecting a mandatory ownership, implementation, design, or current-base conclusion forbids `available`.
