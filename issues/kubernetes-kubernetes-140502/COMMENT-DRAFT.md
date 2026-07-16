# Maintainer confirmation comment draft

## Publication status

- Current status: Published
- Target: `kubernetes/kubernetes#140502` Issue comment
- Expected GitHub identity: `bzsuni`
- Authenticated GitHub identity: `bzsuni`
- Identity verified: yes
- Technical review completed: yes
- User approved: yes
- Publication authorized: yes
- Published at: `2026-07-16T08:56:31Z`
- GitHub URL: https://github.com/kubernetes/kubernetes/issues/140502#issuecomment-4989997742
- Comment ID: `4989997742`

## Purpose

Summarize the source investigation without claiming ownership, and ask SIG Storage to choose the compatibility representation before planning or implementation begins.

## Draft

I traced the registration and resource creation path for this case.

This appears to be more than a naming issue. `TestPattern.FsType` is propagated into the dynamically created StorageClass (`csi.storage.k8s.io/fstype`), while the affected test requests a `ReadWriteMany` Filesystem PVC and validates writable access from two Pods.

One thing I'm unsure about is the intended fix boundary.

`multiVolume` currently includes ext4, xfs and Windows ntfs patterns. Removing explicit filesystem patterns from the suite seems too broad, while skipping every non-empty `FsType` also seems broader than necessary.

Would SIG Storage prefer:

- a case-local compatibility check for these filesystem patterns; or
- explicit compatibility metadata on `TestPattern`?

I'd like to understand the preferred direction before preparing a PR.

## Claims and evidence

| Claim in draft | Source evidence | Facts record |
|---|---|---|
| `multiVolume` selects ext4, xfs and ntfs DynamicPV patterns. | `test/e2e/storage/testsuites/multivolume.go`: `InitMultiVolumeTestSuite`; `test/e2e/storage/framework/testpattern.go`: `Ext4DynamicPV`, `XfsDynamicPV`, `NtfsDynamicPV`. | [CODE-MAP.md](CODE-MAP.md#filesystem-and-testpattern-inventory) |
| Pattern names form test names, while `FsType` also affects resource creation. | `test/e2e/storage/framework/testsuite.go`: `DefineTestSuites`, `RegisterTests`; `test/e2e/storage/framework/volume_resource.go`: dynamic volume resource creation. | [CODE-MAP.md](CODE-MAP.md#registration-and-name-generation) |
| External dynamic provisioning injects non-empty fsType into the StorageClass. | `test/e2e/storage/external/external.go`: `driverDefinition.GetDynamicProvisionStorageClass`. | [CODE-MAP.md](CODE-MAP.md#fstype-propagation) |
| The case requests RWX and performs writable cross-Pod checks on one PVC. | `test/e2e/storage/testsuites/multivolume.go`: the cross-node `ginkgo.It`; `CreateVolumeResourceWithAccessModes`; `TestConcurrentAccessToSingleVolume`. | [CODE-MAP.md](CODE-MAP.md#lifecycle-and-data-flow) |
| Driver metadata cannot express conditional fsType/RWX combinations. | `test/e2e/storage/framework/testdriver.go`: independent `DriverInfo.SupportedFsType` and `Capabilities`; `testsuite.go`: independent filters. | [ANALYSIS.md](ANALYSIS.md#current-behavior) |
| Suite-wide removal and all-non-empty guards have different compatibility risks. | Open `SupportedFsType` set and current suite pattern usage. | [ANALYSIS.md](ANALYSIS.md#likely-fix-layer) |

## Questions for maintainers

1. Should the affected case use a case-local compatibility check, or explicit TestPattern metadata?
2. Is that direction suitable before preparing a PR?

## Publication checklist

- [x] Issue verified open on 2026-07-16.
- [x] No assignee or implementation claim found.
- [x] No active linked Kubernetes implementation PR found.
- [x] Issue still has `needs-triage` and does not have `triage/accepted`.
- [x] Draft does not claim or assign the task.
- [x] Draft does not promise an implementation or PR.
- [x] Draft does not make an unverified accusation against the vSphere CSI Driver.
- [x] Secondary node-affinity observations are excluded.
- [x] Authenticated GitHub identity matched expected identity `bzsuni` immediately before publication.
- [x] User explicitly authorized this exact publication.
