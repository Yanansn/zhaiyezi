# Code map

Inspected upstream: `kubernetes/kubernetes` `master@1b4e48f52199bcfb28ef6efd60522a082c3e78d0`.

## Confirmed source-code facts

### Registration and name generation

1. `test/e2e/storage/external/external.go`
   - `AddDriverDefinition` loads the YAML/JSON external driver definition.
   - It creates the outer `External Storage` description and calls `DefineTestSuites(driver, testsuites.CSISuites)`.
   - `loadDriverDefinition` defaults `SupportedFsType` to only `""`; explicit ext4/xfs patterns therefore require the external definition to add those values.
2. `test/e2e/storage/testsuites/base.go`
   - `CSISuites` includes `BaseSuites`; `BaseSuites` includes `InitMultiVolumeTestSuite`.
3. `test/e2e/storage/testsuites/multivolume.go`
   - `InitMultiVolumeTestSuite` includes `Ext4DynamicPV` and `XfsDynamicPV` among the suite's patterns.
   - The suite name is `multiVolume` and carries the `[Slow]` tag.
4. `test/e2e/storage/framework/testpattern.go`
   - `Ext4DynamicPV` has `Name: "Dynamic PV (ext4)"`, `VolType: DynamicPV`, `FsType: "ext4"`, and an empty `VolMode`.
   - `XfsDynamicPV` follows the same path with `FsType: "xfs"`.
5. `test/e2e/storage/framework/testsuite.go`
   - `DefineTestSuites` iterates every suite × pattern pair.
   - `RegisterTests` creates `[Testpattern: <pattern.Name>]`, then appends suite name/tags and the `ginkgo.It` text. This directly explains the reported name.
   - Registration happens before runtime skip checks; `CapRWX` does not create the name. It determines whether this individual test proceeds instead of skipping.

### Generic filters and capability path

- `SkipInvalidDriverPatternCombination` calls the driver-specific `SkipUnsupportedTest`, checks the required driver interface, and checks `DriverInfo.SupportedFsType.Has(pattern.FsType)` plus Windows/xfs and non-Windows/ntfs rules.
- `multiVolumeTestSuite.SkipUnsupportedTests` checks pre-provisioned and block-mode support, but has no fsType/access-mode compatibility rule.
- The individual cross-node test checks `DriverInfo.Capabilities[CapRWX]`. `CapRWX` is a global boolean defined as support for ReadWriteMany access modes.
- `DriverInfo` stores `SupportedFsType` and `Capabilities` independently. It has no capability indexed by TestPattern, StorageClass flavor, access mode or fsType.

### fsType propagation

```text
Ext4DynamicPV.FsType ("ext4")
  → CreateVolumeResourceWithAccessModes(..., pattern, [ReadWriteMany])
  → DynamicPVTestDriver.GetDynamicProvisionStorageClass(..., pattern.FsType)
  → external.driverDefinition.GetDynamicProvisionStorageClass
  → StorageClass.parameters["csi.storage.k8s.io/fstype"] = "ext4"
```

`xfs` follows the identical path. For a dynamically provisioned CSI volume, the external provisioner/driver create the PV. Kubernetes' `CSIPersistentVolumeSource.FSType` is explicitly the filesystem type to mount, but its final value in this test cannot be proven without observing the provisioner result.

## Test behavior facts

### Resource creation

The relevant call chain is:

```text
cross-node ginkgo.It
  → CreateVolumeResourceWithAccessModes(..., [ReadWriteMany])
    → GetDynamicProvisionStorageClass(fsType)
    → create StorageClass
    → createPVCPVFromDynamicProvisionSC
      → MakePersistentVolumeClaim
      → create PVC and wait for binding
      → read dynamically provisioned PV
  → TestConcurrentAccessToSingleVolume(..., 2, sameNode=false, readOnly=false)
    → CreateSecPodWithNodeSelection twice
      → MakePodSpec / setVolumes
      → each Pod mounts the same PVC at /mnt/volume1
```

- **StorageClass:** created by the test. For explicit ext4/xfs patterns, it contains the corresponding CSI fstype parameter.
- **PVC accessModes:** exactly `[ReadWriteMany]` since commit `975e653af44e` (`RWX tests should create RWX volumes`).
- **PVC volumeMode:** the pattern supplies the empty value; `MakePersistentVolumeClaim` normalizes an empty pointer to nil, so Kubernetes defaults to `Filesystem`.
- **PV:** dynamically created by the CSI provisioner and retrieved after the PVC binds. The test itself does not construct its CSI source.
- **Pods:** two running Pods reference the same PVC read/write. Filesystem volumes use a `VolumeMount`; block patterns use a `VolumeDevice`.
- **Node placement:** after Pod 1 starts, the helper adds required `metadata.name NotIn <pod1-node>` for Pod 2. With no pre-existing topology terms this forces a different node. See the topology composition caveat under Open questions.
- **Operations:** while both Pods are alive, Pod 1 writes and reads; Pod 2 reads Pod 1's bytes, writes new bytes and reads them. Then Pod 2 is deleted and Pod 1 reads/writes again. This is stronger than merely checking that mounts succeed.
- **RWO/ROX/RWX:** this case always overrides driver defaults with RWX. A separate same-node read-only test uses the normal resource helper and `CapMultiPODs`; ROX behavior is tested elsewhere with `CapReadOnlyMany`.

## Relevant files and responsibilities

| File | Responsibility |
|---|---|
| `test/e2e/storage/external/external.go` | Decode external driver metadata, register CSI suites, create StorageClass and inject CSI fstype. |
| `test/e2e/storage/testsuites/base.go` | Include `multiVolume` in the base/CSI suite list. |
| `test/e2e/storage/framework/testdriver.go` | Define `DriverInfo`, `SupportedFsType`, `CapRWX` and driver interfaces. |
| `test/e2e/storage/framework/testpattern.go` | Define ext4/xfs/default/block TestPatterns. |
| `test/e2e/storage/framework/testsuite.go` | Form test names and run global driver/pattern filters. |
| `test/e2e/storage/testsuites/multivolume.go` | Register patterns, apply case-specific capabilities, create RWX resource and exercise two Pods. |
| `test/e2e/storage/framework/volume_resource.go` | Create StorageClass/PVC, wait for dynamic PV, propagate fsType/volumeMode/accessModes. |
| `test/e2e/framework/pv/pv.go` | Build the PVC and apply RWO/default-volume-mode fallbacks. |
| `test/e2e/framework/pod/create.go` | Convert PVCs to Pod VolumeMounts/VolumeDevices. |
| `test/e2e/framework/pod/node_selection.go` | Add node affinity/anti-affinity for same/different-node cases. |

## Analogues and reusable mechanisms

- `SkipInvalidDriverPatternCombination` is the existing global pattern filter, but it only asks whether a driver supports a filesystem at all.
- Other suites use suite-level or individual-test `Skipf` checks for combinations such as block support, expansion capability, ROX capability and filesystem-only behavior. The cross-node `ginkgo.It` already uses this pattern for `CapRWX`, making a case-local compatibility guard consistent with existing style.
- In-tree NFS and Azure File advertise `CapRWX` but only the default filesystem pattern (`SupportedFsType: {""}`), so they do not generate explicit ext4/xfs combinations.
- A suite-wide `SkipUnsupportedTests` rule is not reusable here because ext4/xfs remain valid for other `multiVolume` cases.

## History relevant to the root cause

- `b4c88acec63` (2019), `Add e2e tests for multiAttach`: introduced the cross-node single-volume test.
- `28511e82ad96` (2021), `Add e2e test for a volume + its clone used on the same node`: added ext4/xfs patterns to the entire `multiVolume` suite for clone/snapshot filesystem coverage, unintentionally exposing all suite cases to those patterns.
- `975e653af44e` (2025), `RWX tests should create RWX volumes`: corrected this case to explicitly request `ReadWriteMany` instead of relying on the driver's default access modes. That confirms the intended resource semantics and makes the invalid combination concrete.

## Inferences

- The observed external vSphere case implies its loaded driver definition exposes ext4 support and `CapRWX=true`; otherwise the generic fsType filter or case-level capability check would skip it. The exact YAML was not located in Kubernetes and may belong to the downstream test setup.
- The framework is the stronger root-cause candidate because a driver can legitimately support ext4/xfs for block-backed RWO volumes and RWX for a separate shared-file volume flavor, while the current metadata cannot express that conditional relationship.
- A real CSI driver may reject this request instead of mounting an unsafe filesystem. Source inspection proves the attempted request, not successful provisioning or driver behavior.

## Open questions

1. Should the compatibility guard list `ext4` and `xfs`, also include `ntfs`, or reject every non-empty explicit `FsType` for this case?
2. Should external driver definitions be split by storage flavor when their capabilities differ, or should the framework gain conditional capabilities?
3. Does the vSphere test definition use a single StorageClass for block and file volumes, and what CSI capability/PV fsType does its provisioner return for RWX?
4. When topology affinity already exists, `SetAntiAffinity` appends a separate `NodeSelectorTerm`; because terms are ORed, does the observed run actually place the Pods on different nodes?

## Minimal validation points

- Add a pure table-driven unit test around a small predicate for cross-node RWX-compatible patterns. Cover default filesystem, ext4, xfs, block, and any maintainer-approved Windows case.
- If registration structure changes, test the chosen pattern selection without initializing a Ginkgo suite or cluster.
- Existing `TestDriverParameter` verifies external YAML/JSON decoding but not compatibility combinations.
- Package compilation and the predicate unit test can run without a cluster. Proving real PV fields, CSI requests and simultaneous mounts requires a CSI E2E environment; a full E2E is outside this stage.

## Root-cause and next-stage conclusion

The most likely classification is **B + C**, with **D as a possible configuration/model contributor** and **A insufficient**. The recommended state remains `awaiting-triage`: prepare a short maintainer confirmation comment proposing a case-local guard and asking for the desired fsType scope, but do not post it without separate authorization.
