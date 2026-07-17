# Code map

Inspected upstream: `kubernetes/kubernetes` `master@7e8950f1ec186066fabdfe69d69f92fbb04592da`.

## Filesystem and TestPattern inventory

Counting method: `test/e2e/storage/framework/testpattern.go` contains **46 named package-level `TestPattern` definitions**. This is a source-definition count, not a claim that only 46 values can exist at runtime: custom suites accept arbitrary `[]TestPattern`, and `GenericEphemeralTestPatterns` copies `DefaultFsGenericEphemeralVolume` into late- and immediate-binding variants. Of the 46 named definitions, **21 set `FsType` explicitly** and 25 use the zero value `""`.

This inventory deliberately distinguishes three sets: (1) all named definitions in current source, (2) the subset selected by each current default suite—especially `multiVolume`, and (3) the theoretically open strings accepted from external driver configuration. The table is complete for named definitions in this file at the inspected commit; it is not a closed list of runtime-created values or external strings. Counting used a structural scan of every `TestPattern{...}` definition followed by reference searches across `test/e2e/storage/testsuites` and propagation tracing through the framework and external driver adapter, rather than treating a filesystem keyword search as proof of completeness.

The only explicit values are:

| `FsType` | Named definitions | Dynamic pattern used by `multiVolume` |
|---|---:|---|
| `ext3` | 5 | No |
| `ext4` | 5 | `Ext4DynamicPV` |
| `xfs` | 5 | `XfsDynamicPV` |
| `ntfs` | 6 | `NtfsDynamicPV` |

There are no `btrfs`, `zfs` or `exfat` `TestPattern` values under `test/e2e/storage`. An empty `FsType` normally means “let the driver or StorageClass choose the default filesystem”; for block-mode patterns it also reflects that no filesystem is mounted.

Suite names below are direct references in the current default suite constructors. “None” means the named value exists but no default suite directly selects it; a custom suite still can. “SC” means the value is passed to `GetDynamicProvisionStorageClass`; the external driver injects a parameter only when it is non-empty.

| TestPattern | `Name` | `FsType` | `VolumeMode` | `VolType` | Direct suite use | SC | #140502 relevance |
|---|---|---|---|---|---|---|---|
| `DefaultFsInlineVolume` | Inline-volume (default fs) | `""` | default | Inline | disruptive, subpath, volume_io, volumes | No | No |
| `DefaultFsCSIEphemeralVolume` | CSI Ephemeral-volume (default fs) | `""` | default | CSI inline | ephemeral | No | No |
| `DefaultFsGenericEphemeralVolume` | Generic Ephemeral-volume (default fs) | `""` | default | Generic ephemeral | ephemeral (two derived binding variants), volumelimits | Yes | No |
| `DefaultFsPreprovisionedPV` | Pre-provisioned PV (default fs) | `""` | default | Preprovisioned | subpath, volume_io, volumes | No | No |
| `DefaultFsDynamicPV` | Dynamic PV (default fs) | `""` | default | Dynamic | capacity, fsgroupchangepolicy, provisioning, readwriteoncepod, selinuxmount, subpath, volume_expand, volume_io, volume_modify, volume_modify_stress, volume_stress, volumes | Yes | Baseline |
| `Ext3InlineVolume` | Inline-volume (ext3) | ext3 | default | Inline | volumes | No | No |
| `Ext3CSIEphemeralVolume` | CSI Ephemeral-volume (ext3) | ext3 | default | CSI inline | None | No | No |
| `Ext3GenericEphemeralVolume` | Generic Ephemeral-volume (ext3) | ext3 | default | Generic ephemeral | None | Yes if selected | No |
| `Ext3PreprovisionedPV` | Pre-provisioned PV (ext3) | ext3 | default | Preprovisioned | volumes | No | No |
| `Ext3DynamicPV` | Dynamic PV (ext3) | ext3 | default | Dynamic | volumes | Yes | Scope analogue; not currently in `multiVolume` |
| `Ext4InlineVolume` | Inline-volume (ext4) | ext4 | default | Inline | volumes | No | No |
| `Ext4CSIEphemeralVolume` | CSI Ephemeral-volume (ext4) | ext4 | default | CSI inline | None | No | No |
| `Ext4GenericEphemeralVolume` | Generic Ephemeral-volume (ext4) | ext4 | default | Generic ephemeral | None | Yes if selected | No |
| `Ext4PreprovisionedPV` | Pre-provisioned PV (ext4) | ext4 | default | Preprovisioned | volumes | No | No |
| `Ext4DynamicPV` | Dynamic PV (ext4) | ext4 | default | Dynamic | multivolume, volumes | Yes | **Direct** |
| `XfsInlineVolume` | Inline-volume (xfs) | xfs | default | Inline | volumes | No | No |
| `XfsCSIEphemeralVolume` | CSI Ephemeral-volume (xfs) | xfs | default | CSI inline | None | No | No |
| `XfsGenericEphemeralVolume` | Generic Ephemeral-volume (xfs) | xfs | default | Generic ephemeral | None | Yes if selected | No |
| `XfsPreprovisionedPV` | Pre-provisioned PV (xfs) | xfs | default | Preprovisioned | volumes | No | No |
| `XfsDynamicPV` | Dynamic PV (xfs) | xfs | default | Dynamic | multivolume, volume_expand, volumes | Yes | **Direct** |
| `NtfsInlineVolume` | Inline-volume (ntfs) | ntfs | default | Inline | volumes | No | No |
| `NtfsCSIEphemeralVolume` | CSI Ephemeral-volume (ntfs) [alpha] | ntfs | default | CSI inline | None | No | No |
| `NtfsGenericEphemeralVolume` | Generic Ephemeral-volume (ntfs) | ntfs | default | Generic ephemeral | None | Yes if selected | No |
| `NtfsPreprovisionedPV` | Pre-provisioned PV (ntfs) | ntfs | default | Preprovisioned | volumes | No | No |
| `NtfsDynamicPV` | Dynamic PV (ntfs) | ntfs | default | Dynamic | multivolume, provisioning, subpath, volume_expand, volume_io, volume_modify, volume_modify_stress, volumes | Yes | **Direct on Windows** |
| `FsVolModePreprovisionedPV` | Pre-provisioned PV (filesystem volmode) | `""` | Filesystem | Preprovisioned | disruptive, multivolume, volumemode | No | No explicit fs |
| `FsVolModeDynamicPV` | Dynamic PV (filesystem volmode) | `""` | Filesystem | Dynamic | disruptive, multivolume, volumelimits, volumemode, volumeperf | Yes | Baseline |
| `BlockVolModePreprovisionedPV` | Pre-provisioned PV (block volmode) | `""` | Block | Preprovisioned | disruptive, multivolume, volumemode, volumes | No | No filesystem |
| `BlockVolModeDynamicPV` | Dynamic PV (block volmode) | `""` | Block | Dynamic | disruptive, multivolume, provisioning, pvcdeletionperf, volume_expand, volume_modify, volume_modify_stress, volume_stress, volumemode, volumes | Yes | No filesystem |
| `BlockVolModeGenericEphemeralVolume` | Generic Ephemeral-volume (block volmode) (late-binding) | `""` | Block | Generic ephemeral | ephemeral | Yes | No filesystem |
| `SnapshotMetadata` | SnapshotMetadata | `""` | Block | Dynamic | snapshot-metadata | Yes | No |
| `DynamicSnapshotDelete` | Dynamic Snapshot (delete policy) | `""` | default | Dynamic | snapshottable, snapshottable_stress | Yes | No |
| `VolumeGroupSnapshotDelete` | (delete policy) | `""` | default | Dynamic | volume_group_snapshot_class, volume_group_snapshottable, volume_group_snapshottable_stress | Yes | No |
| `VolumeGroupSnapshotRetain` | (retain policy) | `""` | default | Dynamic | volume_group_snapshottable | Yes | No |
| `PreprovisionedVolumeGroupSnapshotDelete` | Pre-provisioned VolumeGroupSnapshot (delete policy) | `""` | default | Dynamic | volume_group_snapshottable | Yes | No |
| `PreprovisionedVolumeGroupSnapshotRetain` | Pre-provisioned VolumeGroupSnapshot (retain policy) | `""` | default | Dynamic | volume_group_snapshottable | Yes | No |
| `PreprovisionedSnapshotDelete` | Pre-provisioned Snapshot (delete policy) | `""` | default | Dynamic | snapshottable | Yes | No |
| `EphemeralSnapshotDelete` | Ephemeral Snapshot (delete policy) | `""` | default | Generic ephemeral | snapshottable | Yes | No |
| `DynamicSnapshotRetain` | Dynamic Snapshot (retain policy) | `""` | default | Dynamic | snapshottable, snapshottable_stress | Yes | No |
| `PreprovisionedSnapshotRetain` | Pre-provisioned Snapshot (retain policy) | `""` | default | Dynamic | snapshottable | Yes | No |
| `EphemeralSnapshotRetain` | Ephemeral Snapshot (retain policy) | `""` | default | Generic ephemeral | snapshottable | Yes | No |
| `DefaultFsDynamicPVAllowExpansion` | Dynamic PV (default fs)(allowExpansion) | `""` | default | Dynamic | volume_expand | Yes | No |
| `NtfsDynamicPVAllowExpansion` | Dynamic PV (ntfs)(allowExpansion) | ntfs | default | Dynamic | volume_expand | Yes | Scope analogue |
| `BlockVolModeDynamicPVAllowExpansion` | Dynamic PV (block volmode)(allowExpansion) | `""` | Block | Dynamic | volume_expand | Yes | No filesystem |
| `TopologyImmediate` | Dynamic PV (immediate binding) | `""` | default | Dynamic | topology | Yes | No |
| `TopologyDelayed` | Dynamic PV (delayed binding) | `""` | default | Dynamic | topology | Yes | No |

Other fields matter for registration and resource behavior even though they do not change the inventory count:

- `Ext4DynamicPV`, `XfsDynamicPV`, `NtfsDynamicPV`, `DefaultFsDynamicPV` and several block/snapshot patterns set snapshot type/deletion policy.
- all xfs patterns carry `WithSlow`; all ntfs patterns carry the Windows feature tag.
- expansion patterns, `DefaultFsGenericEphemeralVolume`, `XfsDynamicPV` and the generic block pattern set `AllowExpansion`.
- topology and derived generic-ephemeral patterns set binding mode.

### `SupportedFsType` is open, but patterns bound the effective matrix

`DriverInfo.SupportedFsType` is `sets.String`, implemented as `map[string]Empty`; it is not an enum and has no filesystem whitelist. External driver YAML/JSON is decoded into this set, with `{""}` as the default when no values are supplied. `SkipInvalidDriverPatternCombination` performs only exact set membership plus two platform rules: xfs is skipped on Windows and ntfs is skipped outside Windows.

Therefore an external driver definition can declare arbitrary strings, but declaring one does **not** invent a test pattern. The generic suite exercises the intersection of driver-declared values and patterns selected by a suite. Current source provides no btrfs/zfs/exfat pattern to select.

### Propagation depends on volume type

- A selected pattern's `Name` always contributes to the registered test name. `FsType` is not name-only metadata: when non-empty, it also follows the volume-type-specific resource path below. A named definition that no suite selects registers no test and creates no resource.
- Dynamic PV and generic ephemeral patterns pass `pattern.FsType` to `GetDynamicProvisionStorageClass`. The external driver writes `csi.storage.k8s.io/fstype` only for a non-empty value.
- CSI inline patterns place a non-empty value directly in `CSIVolumeSource.FSType`; they do not use a StorageClass.
- ordinary inline and pre-provisioned patterns pass the value into driver-specific volume/PV source construction; they do not use the dynamic StorageClass path.
- default-fs patterns pass `""`; the external adapter does not inject an fstype parameter. A pre-existing StorageClass or driver may still choose a filesystem, so “default” does not prove which filesystem is eventually mounted.
- block-mode patterns have no explicit fsType; their StorageClass path does not inject one and Pods use a raw `VolumeDevice`.
- For dynamic CSI patterns, a non-empty StorageClass parameter may cause the provisioner to set the bound PV's CSI `FSType`, but that final PV field is provisioner output and cannot be proven from Kubernetes test source alone.

## Confirmed source-code facts

### Registration and name generation

1. `test/e2e/storage/external/external.go`
   - `AddDriverDefinition` loads the YAML/JSON external driver definition.
   - It creates the outer `External Storage` description and calls `DefineTestSuites(driver, testsuites.CSISuites)`.
   - `loadDriverDefinition` defaults `SupportedFsType` to only `""`; explicit ext4/xfs patterns therefore require the external definition to add those values.
2. `test/e2e/storage/testsuites/base.go`
   - `CSISuites` includes `BaseSuites`; `BaseSuites` includes `InitMultiVolumeTestSuite`.
3. `test/e2e/storage/testsuites/multivolume.go`
   - `InitMultiVolumeTestSuite` includes `Ext4DynamicPV`, `XfsDynamicPV` and `NtfsDynamicPV` among the suite's patterns.
   - The suite name is `multiVolume` and carries the `[Slow]` tag.
4. `test/e2e/storage/framework/testpattern.go`
   - `Ext4DynamicPV` has `Name: "Dynamic PV (ext4)"`, `VolType: DynamicPV`, `FsType: "ext4"`, and an empty `VolMode`.
   - `XfsDynamicPV` follows the same path with `FsType: "xfs"`.
   - `NtfsDynamicPV` follows the same path with `FsType: "ntfs"` and a Windows tag. `Ext3DynamicPV` is real, but the current `multiVolume` defaults do not include it.
5. `test/e2e/storage/framework/testsuite.go`
   - `DefineTestSuites` iterates every suite × pattern pair.
   - `RegisterTests` creates `[Testpattern: <pattern.Name>]`, then appends suite name/tags and the `ginkgo.It` text. This directly explains the reported name.
   - Registration happens before runtime skip checks; `CapRWX` does not create the name. It determines whether this individual test proceeds instead of skipping.

### Generic filters and capability path

- `SkipInvalidDriverPatternCombination` calls the driver-specific `SkipUnsupportedTest`, checks the required driver interface, and checks `DriverInfo.SupportedFsType.Has(pattern.FsType)` plus Windows/xfs and non-Windows/ntfs rules. The ntfs rule filters a real pattern; it is not merely defensive platform code.
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

`xfs` and, on Windows, `ntfs` follow the identical path. For a dynamically provisioned CSI volume, the external provisioner/driver create the PV. Kubernetes' `CSIPersistentVolumeSource.FSType` is explicitly the filesystem type to mount, but its final value in this test cannot be proven without observing the provisioner result.

## Lifecycle and data flow

The issue-relevant value crosses these ownership and transformation boundaries:

```text
external driver YAML/JSON
  → decode DriverInfo.SupportedFsType and capabilities
  → DefineTestSuites registers suite × TestPattern names
  → runtime filters driver interface, FsType, platform and capabilities
  → multiVolume case requests RWX
  → VolumeResource creates dynamic StorageClass and PVC
  → external provisioner / CSI driver creates the volume and PV
  → two Pods consume the bound PVC
  → cross-Pod reads and writes observe the result
```

The source proves registration, filtering and the constructed Kubernetes request. The provisioner owns final PV generation, so its returned CSI fields and real mount outcome require runtime observation.

### Test behavior facts

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

1. Where can the display name be changed only for this RWX multi-Pod case when `TestPattern.Name` is established during suite registration but RWX capability is checked at runtime?
2. Does the intended naming fix leave `TestPattern.FsType` and the resulting StorageClass parameter unchanged?
3. Which patterns and generated names are in scope, and what acceptance assertion should cover them?
4. Should external driver definitions be split by storage flavor when their capabilities differ, or should the framework gain conditional capabilities? This remains a model question, not the current implementation direction.
5. Does the vSphere test definition use a single StorageClass for block and file volumes, and what CSI capability/PV fsType does its provisioner return for RWX?
6. When topology affinity already exists, `SetAntiAffinity` appends a separate `NodeSelectorTerm`; because terms are ORed, does the observed run actually place the Pods on different nodes?

## Minimal validation points

- No validation design is accepted yet. A confirmed name-layer implementation should first identify a narrow assertion over generated test names while proving that test selection and resource parameters remain as intended.
- If registration structure changes, test the chosen naming behavior without initializing a Ginkgo suite or cluster where feasible.
- Existing `TestDriverParameter` verifies external YAML/JSON decoding but not compatibility combinations.
- Package compilation and a targeted naming unit test may run without a cluster once the boundary is confirmed. Proving real PV fields, CSI requests and simultaneous mounts requires a CSI E2E environment; a full E2E is outside this stage.

## Root-cause and next-stage conclusion

The source map still proves that FsType is not only display metadata: the value reaches the StorageClass while the case requests RWX. That source fact remains valid even though new community evidence favors fixing the generated name rather than skipping the test.

Active PR `#140565` implements the previously identified overbroad non-empty-`FsType` skip. Path-relevant reviewer/approver `gnufied` expressed a high-authority preference that the test should not be skipped and that the problem is in the name; the Review state is `COMMENTED`, not approval or changes requested. The code map does not yet reveal a confirmed case-local naming mechanism or acceptance boundary, so the recommended state is `awaiting-scope-confirmation`; no Plan or Implementation should be derived from this map until that gate passes.
