# Issue ecosystem

Last verified: `2026-07-16T09:24:55Z`

Primary sources:

- Upstream Issue: https://github.com/kubernetes/kubernetes/issues/140502
- Downstream cross-reference: https://github.com/openshift/release/pull/81632
- Earlier downstream selector work: https://github.com/openshift/release/pull/75916
- Downstream comment that links the Issue: https://github.com/openshift/release/pull/81632#issuecomment-4960181805

## 1. Issue Timeline

| UTC time | Event | Meaning |
|---|---|---|
| 2026-07-13 16:20:08 | Issue opened by `gnufied`; `kind/bug` applied. | Upstream problem report created. |
| 2026-07-13 16:20:15–17 | Automation applied `needs-sig` and `needs-triage`; the triage bot commented. | The Issue entered SIG routing and awaits triage acceptance. |
| 2026-07-13 16:20:40–44 | `gnufied` commented `/sig storage`; automation applied `sig/storage` and removed `needs-sig`. | SIG Storage is the routing target, but `triage/accepted` is still absent. |
| 2026-07-13 16:20:44–45 | ProjectV2 automation added the Issue and changed an item status. | A project workflow event exists. The exact Project and status are unavailable to the current token because it lacks `read:project`; the public Issue sidebar currently exposes no Project name. |
| 2026-07-13 16:25:22 | `openshift/release#81632` cross-referenced the Issue. | Downstream CI work mentioned the upstream problem; this did not create an upstream Development link. |
| 2026-07-16 08:56:31 | `bzsuni` published the researched fix-boundary question. | Awaiting maintainer direction; no ownership or implementation commitment was made. |

Current fields:

- Labels: `kind/bug`, `sig/storage`, `needs-triage`.
- Project movement: ProjectV2 add/status-change events are visible, but Project identity and status are not available with current credentials.
- Milestone: none.
- Assignee: none.
- State: open.

## 2. Timeline Events

The `mentioned this` / cross-reference entry comes from a `gnufied` comment on `openshift/release#81632` linking `kubernetes/kubernetes#140502`. That comment says an upstream fix is still needed and the downstream PR should be merged to get downstream tests green in the meantime.

Classification:

| Linked item | Relationship | Classification |
|---|---|---|
| `openshift/release#81632` | Cross-reference from a downstream PR comment. | Downstream CI workaround and supporting evidence; **not** a Kubernetes implementation PR. |
| `openshift/release#75916` | Historical predecessor named in `#81632`. | Related downstream infrastructure work; not an upstream fix. |

A cross-reference records that another artifact mentioned the Issue. It does not prove that the artifact implements the upstream fix, belongs to the upstream repository, or is linked in GitHub Development.

## 3. Development

### Linked branches

No linked implementation.

### Linked pull requests

No linked implementation.

The upstream Issue Development section has no branch or Pull Request. A live search found no Kubernetes PR referencing `140502`, and the only Timeline PR cross-reference is the merged downstream `openshift/release#81632`.

## 4. Downstream

The observed downstream is OpenShift CI for the vSphere VCF 9 CSI job.

`openshift/release#81632` was merged on `2026-07-14T16:05:15Z`. It changes one CI configuration line for the OpenShift 4.23 job:

```diff
- POOL_SELECTOR: vsphere-type=vcf9
+ POOL_SELECTOR: vsphere-type=vcf9,vsanfs=true
```

This constrains the job to nodes/environments with `vsanfs=true`. The PR does not modify Kubernetes e2e test registration, `TestPattern`, StorageClass parameters, PVC access modes or the generated scenarios. It is therefore a downstream environment-selection workaround that helps keep the downstream job green while the upstream behavior remains unresolved.

No Kind, Minikube, Cluster API, other CSI driver or vendor workaround has been identified in the current Timeline.

## 5. Related Work

- `openshift/release#75916` was merged on `2026-03-09T16:56:47Z`. It added multi-pool-selector support and applied the `vsanfs` selector to earlier OpenShift jobs after a job used a vCenter without the required storage configuration.
- `openshift/release#81632` is a follow-up that applies the same selector to the OpenShift 4.23 job.
- No historical, reverted or active Kubernetes fix PR for `kubernetes/kubernetes#140502` has been identified.

## 6. CI

- The upstream Issue cites an OpenShift Prow run for `periodic-ci-openshift-release-main-nightly-4.23-e2e-vsphere-ovn-csi-vcf9` as the observed failure context.
- `openshift/release#81632` changes downstream CI scheduling/configuration rather than upstream test logic.
- No separate Kubernetes TestGrid or upstream Prow failure tied to this Issue has been identified in the current research.
- The downstream selector can reduce exposure to incompatible environments, but it does not validate or settle the correct upstream TestPattern/RWX compatibility rule.

## 7. Maintainer Position

- Issue author and Kubernetes member `gnufied` states that generated RWX scenarios using ext4/XFS do not make sense and should be fixed.
- `/sig storage` routed the Issue to SIG Storage; the Issue remains `needs-triage`, not `triage/accepted`.
- In `openshift/release#81632`, `gnufied` explicitly distinguishes the two layers: upstream generated test names still need a fix, while the downstream PR is merged to get tests green for now.
- No maintainer has yet answered whether the upstream fix should be a case-local compatibility check, explicit `TestPattern` compatibility metadata, or another boundary.

## 8. Open Questions

1. Should the upstream fix change only generated scenario selection/naming, or also guard the actual fsType propagated into the StorageClass?
2. Should compatibility be represented by a case-local check or explicit `TestPattern` metadata?
3. Which filesystem patterns and driver/runtime combinations define the compatibility boundary?
4. Will the OpenShift `vsanfs=true` selector remain necessary after an upstream fix?
5. What ProjectV2 board and status received the Issue? Current credentials cannot resolve this metadata.
6. Is the same failure visible in upstream Kubernetes CI or other downstream CSI environments?

## 9. Current Ecosystem Summary

```text
Upstream:
kubernetes/kubernetes#140502 is open, unassigned, routed to SIG Storage, and still needs triage. No upstream implementation is linked.

Downstream:
OpenShift release CI observed the failure and merged openshift/release#81632 for the 4.23 vSphere VCF 9 job, following earlier selector work in #75916.

Known workaround:
Select CI environments with vsanfs=true. This is a downstream scheduling/configuration workaround, not a Kubernetes code fix.

Active implementation:
None identified upstream or in the Issue Development section.

Open questions:
The upstream compatibility representation and exact fix boundary remain unconfirmed; broader CI impact and ProjectV2 metadata are also unresolved.
```
