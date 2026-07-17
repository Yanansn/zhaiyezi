# Issue: Migrate 'Good First Migration' Immutable Fields to Declarative Validation

## Source facts

- [Issue #136785](https://github.com/kubernetes/kubernetes/issues/136785) is open, was created on 2026-02-05, and was last updated on 2026-06-28 at verification time.
- Labels: `sig/api-machinery`, `help wanted`, `triage/accepted`, `area/api-validation`.
- Milestone: none.
- Assignees: `colecschmidt`, `Shubhamag12`, `darshansreenivas`, `itzPranshul`, `arjun-vegeta`, and `wathmal96`. These assignments cover the umbrella issue and do not identify an active RuntimeClass slice.
- The task list still renders `RuntimeClass.Handler` unchecked and names v1, v1beta1, and v1alpha1 source files.
- On 2026-06-26, contributor `yuminn-k` noted that several unchecked entries, including `RuntimeClass.Handler`, appeared already present on master or covered by active PRs.
- Git history and [merged PR #135046](https://github.com/kubernetes/kubernetes/pull/135046) resolve that ambiguity: RuntimeClass declarative validation was merged on 2025-12-18.

Project metadata could not be read because the authenticated token lacks `read:project`; no Project membership is inferred.

## Plain-language problem

The screening question was whether a small immutable-field migration remained available. It does not: the tracker checkbox is stale, while current source already contains the intended result.

## Scope and acceptance signals

The proposed slice would have required declarative immutability for the RuntimeClass handler across all registered versioned representations, preservation of create/update behavior, strategy integration, generated validation, and focused equivalence tests. All of those signals are present on current master. No new implementation is justified.
