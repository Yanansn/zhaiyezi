# Screening output schema

Store one bounded scan under:

```text
screenings/<owner>-<repository>/<YYYY-MM-DD>-<scan-id>/
├── SCOPE.yaml
├── RESULTS.yaml
└── REPORT.md
```

Use `templates/screening/` through `scripts/init_screening_record.py`. Do not create full `issues/` directories for excluded or watchlisted candidates.

## SCOPE.yaml

Records reproducibility: schema version, repository, scan ID/times, candidate limit, sort/state, include/exclude labels and categories, technical preferences, search capabilities, and limitations. Unknown capabilities must be false or recorded as limitations, not assumed.

## RESULTS.yaml

Contains `summary` counts and three lists: `available`, `watchlist`, and `excluded`. Their lengths must match summary fields, and every discovered candidate belongs to exactly one list. `discovered`, `quick_filtered`, and `deeply_audited` are the counts remaining at those successive funnel stages, so they must be non-negative and satisfy `discovered >= quick_filtered >= deeply_audited`.

Each candidate records:

- Issue ID, URL, title, classification, confidence, assignees, labels, and audit time;
- every mandatory evidence boolean;
- concise related-item URLs and relationship types;
- reason, limitations, and recommended next action.

Do not paste entire GitHub bodies or discussions into YAML. Preserve only enough summary and URLs for review.

Mandatory evidence keys are:

```text
issue_body_checked
labels_checked
assignees_checked
all_comments_checked
development_checked
issue_number_search_checked
fixes_search_checked
related_search_checked
closes_search_checked
refs_search_checked
title_keyword_search_checked
symbol_search_checked
linked_prs_checked
ownership_checked
design_checked
complexity_checked
```

All must be `true` for `available`.

## REPORT.md

Lead with the outcome. Include scan target/scope, inclusion/exclusion rules, execution time, funnel counts, available candidates, watchlist, primary exclusions, search/access limitations, and recommended next step. If none passed, state exactly:

> 本轮没有通过完整审计的可认领 Issue。

Never lower the audit standard to produce an available result.
