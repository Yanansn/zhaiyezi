# Analysis

读懂本分析所需的 PV/PVC、StorageClass、CSI、RWX、Filesystem、TestPattern 和 `multiVolume` 背景，见 [KNOWLEDGE.md](KNOWLEDGE.md)。完整 TestPattern 与 FsType 清单见 [CODE-MAP.md](CODE-MAP.md#filesystem-and-testpattern-inventory)。

## Current behavior

The external test definition exposes two independent pieces of metadata:

1. `DriverInfo.SupportedFsType` determines which `TestPattern` values survive the generic pattern filter.
2. `DriverInfo.Capabilities[CapRWX]` determines whether the multi-node single-volume test skips at runtime.

There is no data structure expressing “a local filesystem is supported for RWO block-backed volumes, while RWX is supported only for a file-volume flavor.” Therefore, when both facts are globally true for one external driver definition, the framework forms their Cartesian product.

The complete current inventory sharpens this model:

- 46 named `TestPattern` definitions exist; 21 set an explicit fsType.
- the explicit set is ext3 (5), ext4 (5), xfs (5), and ntfs (6).
- `Ext4DynamicPV`, `XfsDynamicPV`, and `NtfsDynamicPV` all belong to `multiVolume`; `Ext3DynamicPV` currently does not.
- `SupportedFsType` is an open string set, not an enum. External definitions can declare other strings, but without a suite-selected `TestPattern` those values do not create tests.
- no btrfs, zfs or exfat storage TestPattern currently exists.

For `Ext4DynamicPV`, the test does all of the following:

- registers the name `Dynamic PV (ext4)`;
- creates a StorageClass with `csi.storage.k8s.io/fstype=ext4`;
- creates a PVC requesting `ReadWriteMany`;
- leaves `volumeMode` empty, which becomes the API's default `Filesystem` mode;
- keeps two Pods alive with the same PVC and checks that one Pod can read data written by the other.

The dynamically provisioned PV is created by the external CSI provisioner, not directly by this test. The test retrieves the bound PV, so the exact generated PV fields still depend on the provisioner and driver. Source inspection proves the request, but a real CSI run is needed to observe whether the driver rejects, rewrites or fulfills it.

## Technical qualification

“RWX always conflicts with ext4/xfs” is too broad if it refers to a storage system's internal backing format. The source-proven problem is narrower: this test propagates the explicit pattern `FsType` into the client-facing CSI provisioning path while also requesting multi-node writer semantics.

The test intends to place Pod 2 away from Pod 1 by adding required node anti-affinity. When no prior node affinity exists, this forces different nodes. If topology affinity has already added separate `NodeSelectorTerms`, those terms are ORed by the Kubernetes API; the current helper composition may not universally guarantee different nodes. This is a secondary observation, not the cause of the ext4/xfs combination, and should not be bundled into this issue without maintainer direction.

## Root-cause classification

| Class | Judgment | Confidence | Evidence |
|---|---|---:|---|
| A. Name only | Community-favored hypothesis; technical boundary incomplete | Medium | `gnufied` favors the name layer, while `pattern.FsType` also propagates into the StorageClass and its intended preservation is unconfirmed. |
| B. TestPattern × RWX combination | Source-proven combination; defect classification disputed | High for the combination | The suite registers ext4/xfs patterns for every test case; the cross-node test checks only global `CapRWX`. |
| C. Actual resource configuration | Present in the generated request | High | The code constructs `RWX + Filesystem + csi.storage.k8s.io/fstype=ext4/xfs`. Runtime driver behavior remains E2E-dependent. |
| D. Driver capability/configuration | Possible contributing factor, not proven incorrect | Medium | The external definition must expose the filesystem and RWX capabilities for the observed case to run, but each declaration can be true for different volume flavors. The framework cannot express that condition. |

## Likely fix layer

The earlier analysis favored the individual cross-node RWX test in `test/e2e/storage/testsuites/multivolume.go`, before it creates resources. A suite-wide skip would remove other valid explicit-filesystem `multiVolume` cases. That remained an analysis conclusion, not an accepted implementation direction.

New discussion changes the decision context. PR `#140565` implements the broad non-empty-`FsType` skip, while path-relevant reviewer/approver `gnufied` says the test should not be skipped and that the problem lies in its name. This places the active PR approach in tension with a high-authority preference and points toward the naming layer, so the former predicate-versus-metadata choice must not be carried forward as the plan.

The new direction still does not specify how a case-local display name should be produced when `TestPattern.Name` is part of registration while RWX capability and driver behavior are checked later. It also does not confirm whether `TestPattern.FsType` and the StorageClass parameter must remain unchanged. These questions affect the change boundary and acceptance test, so no implementation plan is ready.

## Community discussion re-analysis

- **Previous assumption:** the fix likely required a case-local compatibility predicate or explicit `TestPattern` metadata.
- **New evidence:** `gnufied` explored removing filesystem names from the affected test name; active PR `#140565` instead skips every non-empty `FsType`; `gnufied` expressed a preference in Review not to skip the test.
- **Authority:** `gnufied` is the reporter, repository member, and path-relevant reviewer/approver. This makes the Review high-weight evidence, but not a replacement for a technically complete boundary.
- **Classification:** the Issue wording is Proposal/Suggestion; the inline comment is a path-approver Preference in a `COMMENTED` Review, not formal approval, changes requested, SIG consensus or Confirmed Implementation Boundary.
- **Updated conclusion:** investigate a naming-layer fix that preserves the test, while leaving the exact mechanism and resource behavior open.
- **Remaining uncertainty:** affected cases, exact generated name, underlying `FsType`/StorageClass behavior, non-goals, and acceptance criteria.
- **Next gate:** `awaiting-scope-confirmation`; do not enter Plan or Implementation until the boundary is confirmed.

## Scope and non-goals

- No Kubernetes source modification in this stage.
- No implementation based solely on the exploratory Issue suggestion or the unapproved PR.
- No claim that the vSphere driver itself is defective without its exact external test definition and CSI request/response evidence.
- No attempt to fix the separate node-affinity composition observation.
- No full cluster or CSI E2E execution.
