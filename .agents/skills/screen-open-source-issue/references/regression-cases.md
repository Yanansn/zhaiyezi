# Screening rule regression cases

These are documentation fixtures, not instructions to query GitHub automatically. They preserve the stated historical audit context as of 2026-07-20; later live state may differ.

| Candidate | Expected classification | Input facts | Rule protected / misclassification prevented |
| --- | --- | --- | --- |
| `kubernetes/kubernetes#140423` | `competing-open-prs` | PR `#140425` says `Fixes #140423`; PR `#140454` says `Related-to #140423`. | Open every reference and detect competition; do not trust Development alone or treat `Related-to` as automatically non-implementation. |
| `kubernetes/kubernetes#140541` | `implementation-pr-exists` or `already-implemented`, according to verified PR state | Comments and PR `#140623` show an implementation already exists. | Do not call an unassigned Issue available when discussion/PR evidence shows implementation. |
| `kubernetes/kubernetes#140502` | `implementation-pr-exists` (historically an active competing implementation) | Active PR `#140565`; the user previously commented on the Issue. | Separate public participation from ownership and detect active implementation before admission. |
| `kubernetes/kubernetes#140598` | `watchlist` | A PR was closed, while Review says the root cause remains unresolved. | Closed PR does not prove fixed or newly available; retain review context and a recheck trigger. |
| `kubernetes/kubernetes#140653` | `implicit-owner` | A commenter explicitly offered to investigate, reproduced the problem, and was willing to fix it. | No assignee and no PR do not erase contextual ownership. |
| `kubernetes/kubernetes#140642` | `infrastructure` | The work concerns 5000-node scalability and GCE infrastructure. | Avoid admitting environment work that cannot be independently validated in the stated contributor scope. |
| `kubernetes/kubernetes#140635` | `blocked-by-design` | API compatibility and SIG design confirmation are required. | Do not turn unresolved design choice into an implementation task. |
| `kubernetes/kubernetes#140606` | `author-implementation` | The Issue author reports an implementation and tests are ready. | Respect an author's unsubmitted implementation rather than racing to a PR. |

When using a case, record which input fact, expected classification, and protected rule were exercised. If a future live audit changes the classification, add a dated note; do not rewrite the historical premise.

## Repository-agnostic schema cases

| Case | Expected result | Rule protected |
| --- | --- | --- |
| LMCache Issue has no assignee but a commenter is implementing | `implicit-owner` or stronger occupied classification | No assignee is not no owner; strength distinguishes interest from implementation. |
| No explicit Issue number but a semantically overlapping PR exists | Structured `semantic-implementation` related item | Explicit-number discovery is not semantic Deep Audit. |
| CPU unit tests pass while GPU E2E is not run | Valid matrix with separate evidence and limitation | Lower verification layers do not imply accelerator completion. |
| GitHub default is `main`, contribution target is `dev` | Both branch fields retained | Default branch is not automatically the PR base. |
| Single-repository Brief discovers a required second-repository change | `scope-expansion-required`; admission cannot pass | Read-only related scope does not grant modification authority. |
| Reproduction attributes the behavior to a third-party project | `not-an-upstream-bug` | Generic attribution replaces Kubernetes-only language. |
| Historical closed PR does not overlap the current implementation | `historical-attempt`, `blocks_contribution: false` | History informs but does not automatically block. |
| Competing open PR covers the behavior | `competing-implementation`, `blocks_contribution: true`; Gate cannot pass | Active competition blocks admission. |
| Evidence collection contains complete raw evidence | Valid only without classification, admission, or RESULTS.yaml | Collection and judgment remain separate. |
| LMCache Profile suggests `dev`, live rules say another branch | Live contribution target wins and override is recorded | Static Profiles never override live repository instructions. |
