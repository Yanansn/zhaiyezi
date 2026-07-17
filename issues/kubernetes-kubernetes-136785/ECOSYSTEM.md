# Issue ecosystem

Last verified: 2026-07-17T16:39:37+08:00

## 1. Issue Timeline

### Labels

- 2026-02-05: automation added `needs-sig` and `needs-triage`, then removed both after `sig/api-machinery` and `triage/accepted` were applied.
- 2026-02-05: `help wanted` added.
- 2026-03-23: `area/api-validation` added.
- Current: `sig/api-machinery`, `help wanted`, `triage/accepted`, `area/api-validation`.

### Project movement

Unavailable: GraphQL returned an insufficient-scope error because the token lacks `read:project`. No Project state is inferred.

### Milestone

No milestone.

### Assignee

The umbrella issue accumulated six assignees between February and June 2026. Comments identify work on other checklist entries, not an unfinished RuntimeClass migration. `darshansreenivas`, one current assignee, authored the already-merged RuntimeClass PR before this issue existed.

### State changes

The issue remains open. No close/reopen event was present in the complete filtered GraphQL timeline.

## 2. Timeline Events

The complete filtered Timeline had no next page. It contains cross-references for many checklist slices, including PRs #136795, #136800, #136803, #136804, #136809, #136811, #136822, #136828, #136886, #136974, #137094, #137095, #137982, #138077-#138082, #139206, #139953, #135050, and #140062, plus issue #137303. None is a separate RuntimeClass implementation.

Relevant classifications:

- [PR #135046](https://github.com/kubernetes/kubernetes/pull/135046): real upstream implementation, merged before #136785; absent from this issue's cross-reference timeline because it relates to umbrella #134280 instead.
- [PR #135885](https://github.com/kubernetes/kubernetes/pull/135885): historical follow-up attempt for RuntimeClass path normalization; closed without merge.
- [PR #137982](https://github.com/kubernetes/kubernetes/pull/137982): merged framework support for matching DV parent short-circuit errors to handwritten child errors; related infrastructure, not the RuntimeClass implementation.
- [PR #136886](https://github.com/kubernetes/kubernetes/pull/136886): merged single-field `Secret.Type` analogue from this tracker.
- [PR #137050](https://github.com/kubernetes/kubernetes/pull/137050): open and returned by broad RuntimeClass/DV search, but its changed-file list does not touch RuntimeClass, node API types, or node validation; reference-only for this screening.

## 3. Development

### Linked branches

No RuntimeClass branch is linked to issue #136785.

### Linked pull requests

No RuntimeClass implementation is linked through this issue's Development/connected events. The implementation is nevertheless conclusively present through merged [PR #135046](https://github.com/kubernetes/kubernetes/pull/135046), merge commit `3347801a5960fe70648dab358c4aeda38a4c5b64`.

## 4. Downstream

No RuntimeClass-specific downstream workaround, vendor patch, or distribution dependency was identified in the issue body, comments, or filtered Timeline. None is necessary to decide availability.

## 5. Related Work

- Direct implementation: PR #135046, 16 files, merged 2025-12-18. It wired node DV, annotated all three external RuntimeClass representations, generated validators, marked handwritten errors, normalized v1alpha1 paths, and added create/update equivalence tests.
- Closest small merged analogue: PR #136886 migrated one scalar field, `Secret.Type`, in eight files and added create/update equivalence coverage.
- Framework prerequisite mentioned by the issue maintainer: PR #137982 merged 2026-05-02. This removed a blocker for struct-shaped candidates but was not required to make the already-completed scalar RuntimeClass work available again.

## 6. CI

- PR #135046 is merged and carried `lgtm`, `approved`, `cncf-cla: yes`, and `ok-to-test` labels.
- This screening did not attempt to reconstruct historical Prow job details because the merge and current source are decisive.
- Local focused tests passed without a cluster; see `TESTING.md`.
- No RuntimeClass-specific TestGrid or downstream CI concern was found.

## 7. Maintainer Position

Issue author and Kubernetes member `lalitc375` defined these candidates as simple migrations, asked contributors to preserve DV/HV equivalence, and on 2026-05-04 stated that the listed fields were ready after PR #137982. That statement is general guidance; it does not negate the earlier merged RuntimeClass implementation.

### Discussion re-analysis log

- Previous assumption: The unchecked task-list item might represent available work.
- New evidence: Contributor `yuminn-k` flagged RuntimeClass as already on master or under active work; current source and merged PR #135046 prove it was completed before #136785 opened.
- Commenter role and authority: `yuminn-k` is a community contributor without recorded maintainer authority; the claim is independently confirmed by authoritative source history and merged-PR state.
- Evidence classification: Clarification supported by upstream implementation fact.
- Impact: Availability fails; no claim, plan, or implementation may proceed.
- Updated conclusion: The RuntimeClass.Handler slice is superseded.
- Remaining uncertainty: The tracker checkbox has not been updated; this is record drift, not technical or ownership ambiguity.
- Next decision gate: Select and live-screen another candidate; no RuntimeClass implementation gate remains.

## 8. Open Questions

- Whether maintainers will update the stale checklist is unknown and irrelevant to this terminal screening.
- Project metadata remains unavailable without `read:project` scope.

## 9. Current Ecosystem Summary

```text
Upstream: Issue open and checklist stale; RuntimeClass migration already merged in PR #135046.
Downstream: No relevant workaround or dependency identified.
Known workaround: Not applicable.
Active implementation: None needed; current master already contains the implementation.
Open questions: Only tracker-maintenance and inaccessible Project metadata remain.
```
