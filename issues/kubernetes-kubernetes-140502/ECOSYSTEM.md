# Issue ecosystem

Last verified: `2026-07-17T02:05:58Z`

Primary sources:

- Upstream Issue: https://github.com/kubernetes/kubernetes/issues/140502
- Downstream cross-reference: https://github.com/openshift/release/pull/81632
- Earlier downstream selector work: https://github.com/openshift/release/pull/75916
- Downstream comment that links the Issue: https://github.com/openshift/release/pull/81632#issuecomment-4960181805
- Active upstream proposal: https://github.com/kubernetes/kubernetes/pull/140565

## 1. Issue Timeline

| UTC time | Event | Meaning |
|---|---|---|
| 2026-07-13 16:20:08 | Issue opened by `gnufied`; `kind/bug` applied. | Upstream problem report created. |
| 2026-07-13 16:20:15–17 | Automation applied `needs-sig` and `needs-triage`; the triage bot commented. | The Issue entered SIG routing and awaits triage acceptance. |
| 2026-07-13 16:20:40–44 | `gnufied` commented `/sig storage`; automation applied `sig/storage` and removed `needs-sig`. | SIG Storage is the routing target, but `triage/accepted` is still absent. |
| 2026-07-13 16:20:44–45 | ProjectV2 automation added the Issue and changed an item status. | A project workflow event exists. The exact Project and status are unavailable to the current token because it lacks `read:project`; the public Issue sidebar currently exposes no Project name. |
| 2026-07-13 16:25:22 | `openshift/release#81632` cross-referenced the Issue. | Downstream CI work mentioned the upstream problem; this did not create an upstream Development link. |
| 2026-07-16 08:56:31 | `bzsuni` published the researched fix-boundary question. | Awaiting maintainer direction; no ownership or implementation commitment was made. |
| 2026-07-16 14:15:58 | `gnufied` wondered whether filesystem names could be removed from the affected test name. | New exploratory direction evidence; not a confirmed boundary. |
| 2026-07-16 14:56:11 | `darshansreenivas` proposed skipping non-empty `FsType` patterns and linked Kubernetes PR `#140565`. | An active implementation proposal now exists and requires comparison with the discussion. |
| 2026-07-16 15:02:11 | In a `COMMENTED` Review on `#140565`, `gnufied` said the test should not be skipped and that the problem is the test name. | High-authority path-approver preference is in tension with the PR implementation, but is neither an approval/request-changes review nor a complete name-change boundary. |

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
| `kubernetes/kubernetes#140565` | Linked by its author in the Issue discussion. | Active upstream implementation proposal; not an accepted fix and not linked in the Issue Development section. |

A cross-reference records that another artifact mentioned the Issue. It does not prove that the artifact implements the upstream fix, belongs to the upstream repository, or is linked in GitHub Development.

## 3. Development

### Linked branches

No linked implementation.

### Linked pull requests

The Issue Development section still shows no linked implementation. However, Issue comment `#4993348064` directly links active Kubernetes PR `#140565`; it must be treated as active related implementation even though GitHub has not populated Development.

PR `#140565` adds a case-local skip for every non-empty `pattern.FsType`. It is open, non-draft, unmerged, has no approving or changes-requested Review, and is currently blocked. Its implementation is in tension with `gnufied`'s inline `COMMENTED` Review that the test should not be skipped.

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
- Active Kubernetes PR `#140565` proposes a non-empty-`FsType` skip. It is relevant implementation work, but not a confirmed or approved fix.

## 6. CI

- The upstream Issue cites an OpenShift Prow run for `periodic-ci-openshift-release-main-nightly-4.23-e2e-vsphere-ovn-csi-vcf9` as the observed failure context.
- `openshift/release#81632` changes downstream CI scheduling/configuration rather than upstream test logic.
- No separate Kubernetes TestGrid or upstream Prow failure tied to this Issue has been identified in the current research.
- The downstream selector can reduce exposure to incompatible environments, but it does not settle the upstream naming versus runtime-behavior boundary.

## 7. Maintainer Position

- Issue author and Kubernetes member `gnufied` states that generated RWX scenarios using ext4/XFS do not make sense and should be fixed.
- `/sig storage` routed the Issue to SIG Storage; the Issue remains `needs-triage`, not `triage/accepted`.
- In `openshift/release#81632`, `gnufied` explicitly distinguishes the two layers: upstream generated test names still need a fix, while the downstream PR is merged to get tests green for now.
- The earlier choice between a compatibility guard and `TestPattern` metadata has been overtaken by new discussion and is no longer implementation-ready.
- `gnufied` is the Issue author, a Kubernetes repository member, and a path-relevant reviewer and approver through `test/e2e/storage/OWNERS` and the `sig-storage-reviewers` / `sig-storage-approvers` aliases. This gives the comment and Review substantial decision weight, but does not replace technical boundary analysis.
- `gnufied`'s Issue comment is a Proposal/Suggestion because it uses exploratory wording (“I wonder if”). The inline PR comment is a Preference from a path-relevant approver, recorded in a `COMMENTED` Review: high-authority evidence against the current skip, but not a formal approval, changes request, SIG consensus or Confirmed Implementation Boundary.
- `darshansreenivas` is a repository member and the author of `#140565`; no path-specific reviewer or approver role was established in the inspected ownership files. The PR is an implementation proposal, not community consensus.

### Discussion re-analysis log

- Previous assumption: the likely fix belonged in a case-local fsType/RWX compatibility guard or explicit `TestPattern` metadata; no active upstream implementation or maintainer response existed.
- New evidence: `gnufied` suggested removing filesystem names for this RWX multi-Pod case; `darshansreenivas` opened `#140565` to skip every non-empty `FsType`; `gnufied` reviewed that PR and said not to skip the test because the problem is its name.
- Commenter role and authority: `gnufied` is the reporter, repository member, and path-relevant reviewer/approver; `darshansreenivas` is a repository member and PR author, with no path ownership established by this review.
- Evidence classification: exploratory Issue Proposal plus a path-approver Preference against the current skip implementation; no Maintainer Direction or Confirmed Implementation Boundary has been established.
- Impact: the former preferred compatibility-guard direction is no longer ready to plan, and the active PR is in tension with the higher-authority Review preference.
- Updated conclusion: the strongest current evidence favors preserving the test and investigating the naming layer, but does not establish that merely deleting text is sufficient or that underlying `FsType` behavior should change.
- Remaining uncertainty: exact name-generation change, affected patterns/cases, whether `TestPattern.FsType` and StorageClass behavior remain unchanged, non-goals, and acceptance criteria.
- Next decision gate: obtain enough scope evidence to pass the Confirmed Implementation Boundary Gate; until then keep `awaiting-scope-confirmation` and do not code.

## 8. Open Questions

1. Exactly which generated name should change, and how can the name be adjusted only for the RWX multi-Pod case when pattern names are registered before runtime capability checks?
2. Must `TestPattern.FsType` and `csi.storage.k8s.io/fstype` behavior remain unchanged while only display text changes?
3. Which patterns/cases are in scope, and what output or test behavior is the acceptance criterion?
4. Will the OpenShift `vsanfs=true` selector remain necessary after an upstream fix?
5. What ProjectV2 board and status received the Issue? Current credentials cannot resolve this metadata.
6. Is the same failure visible in upstream Kubernetes CI or other downstream CSI environments?

## 9. Current Ecosystem Summary

```text
Upstream:
kubernetes/kubernetes#140502 is open, unassigned, routed to SIG Storage, and still needs triage. PR #140565 is an active related implementation proposal even though Development is empty.

Downstream:
OpenShift release CI observed the failure and merged openshift/release#81632 for the 4.23 vSphere VCF 9 job, following earlier selector work in #75916.

Known workaround:
Select CI environments with vsanfs=true. This is a downstream scheduling/configuration workaround, not a Kubernetes code fix.

Active implementation:
PR #140565 proposes skipping every non-empty FsType pattern. It is open, blocked, has no approving review, and is in tension with gnufied's path-approver preference not to skip the test.

Open questions:
The strongest current evidence favors changing the test name while preserving the test, but the exact naming mechanism, underlying FsType behavior, non-goals and acceptance criteria remain unconfirmed. The current gate is Awaiting Scope Confirmation.
```
