# Issue

## Source facts

- Repository: `kubernetes/kubernetes`
- Issue: `#140523`
- Title: `EvictionRequest: add CRUD tests for conformance`
- State: open
- Created: 2026-07-14
- Labels observed: `sig/node`, `wg/node-lifecycle`, `kind/feature`, `needs-triage`
- Assignee: none observed
- Human discussion: none observed; only the triage bot response
- Requested changes:
  - remove the `getLifecycleAPIGroup` entry from `test/conformance/testdata/pending_eligible_endpoints.yaml`
  - add tests that exercise the EvictionRequest API operation and can eventually be promoted to conformance

## Requirement summary

The issue states that a GA API endpoint lacks the operation coverage required for Kubernetes conformance. The work is expected to add an appropriate API test and then remove the endpoint from the list of GA endpoints still waiting for eligible coverage.

## Acceptance signals

- The issue was opened by a Kubernetes contributor and routed to SIG Node/WG Node Lifecycle.
- It has not yet received `triage/accepted` or maintainer implementation guidance.
- Implementation should therefore wait until code investigation produces a precise proposal and maintainers confirm the direction.
