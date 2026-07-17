# Intake and feasibility screening

Last verified: 2026-07-17T16:39:37+08:00

## Candidate

- Tracking issue: [kubernetes/kubernetes#136785](https://github.com/kubernetes/kubernetes/issues/136785)
- Candidate slice: `RuntimeClass.Handler` immutable validation
- Phase boundary: intake and feasibility screening only
- Decision: `superseded`

## Intake result

The slice is not available. The issue body still shows `RuntimeClass.Handler` as unchecked, but [PR #135046](https://github.com/kubernetes/kubernetes/pull/135046) merged the node API group's RuntimeClass declarative validation on 2025-12-18, before issue #136785 was opened on 2026-02-05. Current `upstream/master@8bd10c1aede813509875bac792f3bce79fbb6414` contains the tags, generated validation, strategy wiring, equivalence tests, and handwritten-error coverage markers.

## Feasibility absent supersession

The work is technically bounded and locally testable without a cluster. It spans three registered external API representations, requires path normalization for v1alpha1, and already has focused create/update equivalence tests. These favorable engineering properties do not overcome the availability failure.

## Approval boundary observed

- Official upstream fetch: performed as required by the brief.
- Kubernetes source modification, code generation, branch creation, commit, push, issue assignment, comment, and PR: not performed.
- Facts repository files: updated locally.
- Facts repository commit and push: not authorized and not performed.
