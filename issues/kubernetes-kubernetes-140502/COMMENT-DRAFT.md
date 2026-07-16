# Maintainer confirmation comment draft

## Publication status

- Current status: Draft
- Target: `kubernetes/kubernetes#140502` Issue comment
- Expected GitHub identity: `Yanansn`
- Actual GitHub identity: verify-before-publish
- Reviewed by Chat: no
- User approved: no
- Publication authorized: no
- Published at: not-published
- GitHub URL: not-published

## Purpose

Summarize the source investigation without claiming ownership, and ask SIG Storage to choose the compatibility representation before planning or implementation begins.

## Draft

I traced the registration and resource creation path for this test.

This appears to be more than a naming issue: a non-empty `TestPattern.FsType` is passed to the dynamically created StorageClass as `csi.storage.k8s.io/fstype`, while the affected case requests a `ReadWriteMany` Filesystem PVC and validates writable access from two Pods.

The current `multiVolume` patterns include ext4, xfs, and Windows ntfs. Removing explicit filesystem patterns from the entire suite would also remove valid coverage from other cases, while skipping every non-empty `FsType` may be too broad.

Would SIG Storage prefer a case-local compatibility check for conventional single-host filesystem patterns, or explicit cross-node RWX compatibility metadata on `TestPattern`?

If a local check is preferred, should ext3, ext4, xfs, and ntfs be handled consistently?

## Claims and evidence

| Claim in draft | Source evidence | Facts record |
|---|---|---|
| `multiVolume` selects ext4, xfs and ntfs DynamicPV patterns; ext3 exists outside its defaults. | `test/e2e/storage/testsuites/multivolume.go`: `InitMultiVolumeTestSuite`; `test/e2e/storage/framework/testpattern.go`: `Ext3DynamicPV`, `Ext4DynamicPV`, `XfsDynamicPV`, `NtfsDynamicPV`. | [CODE-MAP.md](CODE-MAP.md#filesystem-and-testpattern-inventory) |
| Pattern names form test names, while `FsType` also affects resource creation. | `test/e2e/storage/framework/testsuite.go`: `DefineTestSuites`, `RegisterTests`; `test/e2e/storage/framework/volume_resource.go`: dynamic volume resource creation. | [CODE-MAP.md](CODE-MAP.md#registration-and-name-generation) |
| External dynamic provisioning injects non-empty fsType into the StorageClass. | `test/e2e/storage/external/external.go`: `driverDefinition.GetDynamicProvisionStorageClass`. | [CODE-MAP.md](CODE-MAP.md#fstype-propagation) |
| The case requests RWX and performs writable cross-Pod checks on one PVC. | `test/e2e/storage/testsuites/multivolume.go`: the cross-node `ginkgo.It`; `CreateVolumeResourceWithAccessModes`; `TestConcurrentAccessToSingleVolume`. | [CODE-MAP.md](CODE-MAP.md#lifecycle-and-data-flow) |
| Driver metadata cannot express conditional fsType/RWX combinations. | `test/e2e/storage/framework/testdriver.go`: independent `DriverInfo.SupportedFsType` and `Capabilities`; `testsuite.go`: independent filters. | [ANALYSIS.md](ANALYSIS.md#current-behavior) |
| All-non-empty and ext4/xfs-only guards have different compatibility risks. | Open `SupportedFsType` set and complete named-pattern inventory. | [ANALYSIS.md](ANALYSIS.md#likely-fix-layer) |

## Questions for maintainers

1. Should the affected case use a local compatibility predicate, or should compatibility be explicit TestPattern metadata?
2. If a predicate is preferred, should ext3, ext4, xfs and ntfs be treated consistently even though ext3 is not currently selected by `multiVolume`?

## Publication checklist

- [x] Issue verified open on 2026-07-16.
- [x] No assignee or implementation claim found.
- [x] No active linked Kubernetes implementation PR found.
- [x] Issue still has `needs-triage` and does not have `triage/accepted`.
- [x] Draft does not claim or assign the task.
- [x] Draft does not promise an implementation or PR.
- [x] Draft does not make an unverified accusation against the vSphere CSI Driver.
- [x] Secondary node-affinity observations are excluded.
- [ ] User has explicitly authorized publication. **Not authorized in this stage.**
