# Analysis

## Screening question

Is #140489 a contribution that a normal external contributor can carry far enough to justify continued work, given that the final behavior depends on protected Kubernetes CI infrastructure?

## What is already feasible

The task has a bounded configuration surface and several reusable references:

- the AKS Prow cluster already hosts a privileged IPv6 Kind periodic;
- SIG Network already maintains IPv6 and dual-stack Kind job shapes;
- existing jobs show two ways to install or select a NetworkPolicy provider;
- test-infra has repository-local validation for Prow YAML and job policy;
- the exact target test set and current skip behavior can be checked locally.

This is enough for a contributor to prepare a focused test-infra patch after the intended topology is confirmed. It is not enough to assert that the patch would work in Prow.

## Why implementation is not ready

The missing proof is environmental, not syntactic:

1. The checked AKS job does not expose its worker OS or kernel configuration. A platform default is not evidence that privileged nested Kind can use SCTP.
2. The checked AKS job does not install a NetworkPolicy provider. The three policy tests require real SCTP enforcement, not merely API acceptance.
3. The AKS build cluster's external IPv6 capability was reported by a repository member, but the current canary excludes the Feature test, and public job artifacts were unavailable during screening.
4. Managed EKS IPv6 is not Kubernetes dual-stack for Pods and Services according to current AWS documentation. Existing test-infra jobs on `eks-prow-build-cluster` mostly provision separate EC2 clusters and skip all Feature tests.
5. A periodic's decisive validation happens on protected infrastructure. An external contributor can run config checks but cannot independently reproduce the Prow cluster, credentials, routing, quota, or kernel.

## Candidate directions for maintainer confirmation

### AKS-hosted nested Kind

This has the strongest existing reference because `ci-kubernetes-e2e-kind-ipv6-canary` already supplies the Prow cluster selector, DinD permissions, image, resources, and IPv6 bootstrap. It remains conditional on SCTP kernel access and a policy-capable CNI/provider. It is the leading direction, not a confirmed design.

### Split coverage across jobs

External IPv6 and SCTP/NetworkPolicy have different dependencies. Separate narrow periodics may reduce coupling if maintainers do not require one job to cover every label. The Issue wording currently asks for the combined capability set, so splitting it requires explicit agreement.

### AWS/EC2 or EKS-based route

Current AWS jobs provide non-COS Ubuntu and a `kubetest2 ec2 --ip-family=dual` reference, but no checked job proves external IPv6 or SCTP NetworkPolicy. Protected AWS service accounts and provisioning add a larger ownership and validation boundary. Managed EKS itself does not satisfy Kubernetes dual-stack Pods/Services.

## Validation boundary

### A normal contributor can validate locally

- YAML parsing and Prow config loading;
- job naming, annotations, policy, and fixture consistency;
- generated-job consistency if a generated path is chosen;
- Ginkgo selection against the complete current test list;
- static review that the intended skip/filter no longer excludes the runnable target specs.

### Only Prow or cloud owners can validate

- the AKS worker's SCTP kernel/module behavior in DinD;
- external IPv6 from the nested test Pod;
- dual-stack cluster behavior on the selected host;
- SCTP Pod/Service transport and NetworkPolicy enforcement;
- cloud quota, scheduling, secrets, cleanup, and repeated periodic stability.

The existing AKS Kind canary references no Azure credential secret or Boskos resource, which makes a configuration contribution plausible. Access to the AKS build cluster and any on-demand rehearsal still belongs to maintainers.

The candidate is a periodic and therefore has no PR `trigger` or `rerun_command` in the checked YAML. A contributor PR can receive test-infra's ordinary static/config presubmits according to project trust rules, but the configuration exposes no way for an unprivileged contributor to schedule this AKS periodic. A real pre-merge rehearsal would need a maintainer-provided trigger or temporary test arrangement.

## Screening score

| Dimension | Score | Evidence |
|---|---:|---|
| Requirement clarity | 1/2 | Desired coverage is clear; exact topology and job split are not. |
| Maintainer acceptance | 2/2 | `triage/accepted` and `help wanted` are present. |
| No conflicting assignee or linked PR | 2/2 | No assignee, claim, or implementation PR found. |
| Bounded code surface | 1/2 | Likely one job YAML, but provider setup or ownership may move the path. |
| Local testability | 1/2 | Config and selection are local; runtime capability is not. |
| Environment affordability | 0/2 | Decisive checks require protected cloud/Prow resources. |
| Fit with contributor knowledge | 1/2 | YAML and source tracing are accessible; CI networking is specialized. |
| Learning value | 2/2 | Strong coverage of Prow, Kind, IPv6, SCTP, and NetworkPolicy layers. |
| Likely review path | 1/2 | Relevant OWNERS are known, but SIG Network and SIG K8s Infra ownership overlaps. |

Total: 11/18. The environment gate overrides any temptation to call this immediately implementation-ready.

## Recommendation

**pursue-after-maintainer-confirmation**

This Issue is suitable for an external contributor to continue investigating and likely to prepare a bounded YAML contribution, but not yet suitable for implementation. Before a patch, maintainers should confirm:

- the intended host/topology, preferably whether the AKS Kind canary is the base;
- SCTP kernel/module availability in that exact runtime;
- the NetworkPolicy provider and its SCTP/dual-stack support;
- one combined job versus multiple narrow jobs;
- who can execute or observe a pre-merge runtime rehearsal.

An upstream clarification comment is recommended. A Draft is prepared in `COMMENT-DRAFT.md`, but it has not received Technical Review or user approval and must not be published.
