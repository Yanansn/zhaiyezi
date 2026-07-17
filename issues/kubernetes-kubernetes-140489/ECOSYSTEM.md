# Issue ecosystem

Last verified: 2026-07-17T03:50:58Z

## 1. Issue Timeline

### Labels

- Initial automation added `needs-sig` and `needs-triage`.
- The reporter routed the Issue to `sig/network`, `sig/testing`, `area/ipv6`, and `area/network-policy` on 2026-07-13.
- `bowei` requested `help wanted` and `triage/accepted` on 2026-07-16; both labels remain present.
- `needs-sig` and `needs-triage` are no longer present.

### Project movement

No Project item was available through the current authentication. The GraphQL token lacks `read:project`; no project placement is inferred.

### Milestone

No milestone.

### Assignee

No assignee and no claim comment.

### State changes

The Issue remains open. No close/reopen event was observed.

## 2. Timeline Events

- [`kubernetes/kubernetes#140491`](https://github.com/kubernetes/kubernetes/issues/140491) cross-references this Issue. It is a closed predecessor, not an implementation. Its final comment says the SCTP and IPv6 work should be combined because one SCTP test is dual-stack.
- [`kubernetes/test-infra#37410`](https://github.com/kubernetes/test-infra/pull/37410) is related evidence. It adds a coverage-analysis tool and reports unexecuted tests; it does not add an AKS/EKS job or fix #140489.
- Search and Timeline inspection found no active PR that claims or implements #140489.

## 3. Development

### Linked branches

No linked implementation.

### Linked pull requests

No linked implementation. PR #37410 is coverage-analysis tooling, not an implementation PR for this Issue.

## 4. Downstream

- AKS and EKS are candidate execution environments, not downstream fixes.
- No downstream workaround or vendor-specific implementation for the missing upstream periodic was found.
- Microsoft documents AKS dual-stack with Azure CNI Overlay and optional Cilium NetworkPolicy support. This proves platform capability in supported configurations, not the configuration of the Kubernetes Prow AKS build cluster.
- AWS documents IPv6 EKS clusters, but also states that EKS does not provide dual-stacked Pods or Services. This makes managed EKS an incomplete match for the upstream `[Feature:IPv6DualStack]` test unless the job instead runs a nested dual-stack cluster such as Kind.

## 5. Related Work

- [`kubernetes/test-infra#35031`](https://github.com/kubernetes/test-infra/issues/35031) recorded that COS does not support SCTP for the affected Kind NetworkPolicy jobs.
- Merged [`kubernetes/test-infra#35032`](https://github.com/kubernetes/test-infra/pull/35032) added explicit `[Feature:SCTPConnectivity]` skips to the kube-network-policies periodic and presubmit configs. This is historical evidence of the environment limitation, not a solution.
- Existing Kind IPv6, dual-stack, NetworkPolicy, and EC2 jobs are inventoried in `INVENTORY.md`; all checked combinations omit or explicitly skip at least one required capability.

## 6. CI

- PR #37410's seven-day analysis reported the two shared `e2e_node` SCTP specs as never executed and described the broader `e2e` SCTP/Networking-IPv6 gap.
- `ci-kubernetes-e2e-kind-ipv6-canary` is the closest AKS-hosted periodic. It runs privileged Kind on `k8s-infra-aks-prow-build` with Docker IPv6 and `IP_FAMILY=ipv6`, but its label filter selects only tests with no Feature label.
- Existing SIG Network Kind IPv6 and dual-stack jobs run on the default Prow build cluster and explicitly skip SCTP; the external-connectivity spec is also skipped by label/name filters.
- Existing kube-network-policies jobs configure a policy provider but explicitly skip SCTP because of the COS kernel limitation.
- Existing jobs scheduled on `eks-prow-build-cluster` generally provision Kubernetes on EC2 with `kubetest2 ec2`; the periodic feature runs skip all `[Feature:.+]` tests. The Prow scheduling cluster name is not proof that the test target is managed EKS.
- Public GCS job-history objects returned HTTP 403 during this screening, so recent run artifacts could not be independently used as success evidence. Configuration and live GitHub discussion are recorded separately from unverified runtime assumptions.

## 7. Maintainer Position

- `danwinship` identified the coverage gap, described GCE/COS and underlay concerns, and proposed an AKS/EKS periodic with the combined capability set.
- `upodroid` stated that the AKS build cluster now has external IPv6 and dual-stack networking.
- `bowei` accepted the Issue and marked it `help wanted`, but did not specify a job design.
- No relevant participant has confirmed that the AKS worker kernel exposes SCTP to Docker-in-Docker, which NetworkPolicy implementation should be installed, whether one or multiple periodics are acceptable, or who owns runtime validation.

### Discussion re-analysis log

- Previous assumption: The Issue body suggested AKS or EKS might provide a single reusable environment.
- New evidence: Current test-infra configs contain an AKS-hosted IPv6 Kind canary, but no checked AKS/EKS job combines all four capabilities; EKS documentation says managed EKS Pods and Services are not dual-stack.
- Commenter role and authority: `danwinship`, `upodroid`, and `bowei` are repository members; `bowei` is also an approver for the relevant test-infra SIG Network job path. Their comments are strong project evidence, but none establishes the missing runtime facts or a confirmed implementation boundary.
- Evidence classification: Problem clarification plus platform suggestion; no Maintainer Direction for a specific patch.
- Impact: A bounded configuration contribution looks plausible, but implementation cannot be selected solely from job names or platform defaults.
- Updated conclusion: Continue only after maintainers confirm runtime capability, ownership, and expected job split.
- Remaining uncertainty: SCTP module visibility, SCTP-capable CNI/NetworkPolicy enforcement, external IPv6 from the nested test Pod, protected resource use, and pre-merge runtime validation.
- Next decision gate: Maintainer confirmation of the CI environment and validation owner.

## 8. Open Questions

- Is `k8s-infra-aks-prow-build` the intended host for a new narrow Kind periodic?
- What node OS/kernel does that build cluster use, and can a privileged Docker-in-Docker job load or use `sctp.ko`?
- Which CNI or NetworkPolicy provider is expected to enforce SCTP in both IPv4 and dual-stack cases?
- Must a single job cover all target labels, or may external IPv6 and SCTP/NetworkPolicy coverage be split?
- Can SIG K8s Infra provide an on-demand rehearsal, or must runtime validation wait until merge?
- Which path should own the job: `sig-k8s-infra`, `sig-network`, or a generator elsewhere?

## 9. Current Ecosystem Summary

```text
Upstream:
Issue open, accepted, help wanted, unassigned; no linked implementation.

Downstream:
AKS and EKS provide relevant platform capabilities, but no downstream fix exists.

Known workaround:
Existing jobs skip the uncovered Feature tests; that preserves CI health but does not add coverage.

Active implementation:
None. test-infra#37410 is analysis tooling, not the implementation.

Open questions:
AKS SCTP kernel/module access, policy-capable CNI, exact job split, resource ownership, and runtime validation authority.
```
