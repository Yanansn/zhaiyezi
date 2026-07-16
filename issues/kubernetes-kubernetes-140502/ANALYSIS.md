# Analysis

## Concepts

- A **TestPattern** is a reusable bundle of inputs that a Storage E2E suite combines with each of its test cases. Its name labels the generated test, while fields such as volume type, filesystem type and volume mode control resource creation.
- **FsType** is the filesystem requested for a mounted volume. An explicit value such as `ext4` asks the dynamic CSI path to put that value in the StorageClass fstype parameter. `FsType == ""` means the generic framework does not choose one and leaves the default to the driver or existing StorageClass; it does not prove that the final volume has no filesystem.
- **RWX / ReadWriteMany** describes the access requested by a PVC: the volume may be mounted read/write by many nodes. It does not identify the storage implementation or filesystem.
- **Filesystem volume mode** means Pods receive a mounted directory. It is the Kubernetes default when `volumeMode` is omitted. **Block volume mode** exposes a raw device and has no mounted filesystem.
- **ext4/xfs** are ordinary Linux filesystems normally mounted over a block device. They do not provide the distributed locking/coherency needed for independent hosts to mount the same ordinary filesystem read/write.
- **Shared filesystems** such as NFS, SMB or CephFS coordinate multi-client access through a server or distributed protocol. Their backing server may internally use ext4/xfs, but that is different from telling each Kubernetes node to mount the CSI volume as ext4/xfs.
- A **CSI driver** receives the requested access mode and mount capability. Whether its storage can satisfy multi-node writer semantics depends on the volume flavor and driver implementation.

Kubernetes documentation also separates these axes: `Filesystem` and `Block` are volume modes, while `ReadWriteMany` is an access mode whose support depends on the driver. See [Persistent Volumes](https://kubernetes.io/docs/concepts/storage/persistent-volumes/).

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
| A. Name only | Rejected as the complete explanation | High | `pattern.FsType` is propagated into the StorageClass, not only `pattern.Name`. |
| B. TestPattern × RWX combination | Primary framework defect | High | The suite registers ext4/xfs patterns for every test case; the cross-node test checks only global `CapRWX`. |
| C. Actual resource configuration | Present in the generated request | High | The code constructs `RWX + Filesystem + csi.storage.k8s.io/fstype=ext4/xfs`. Runtime driver behavior remains E2E-dependent. |
| D. Driver capability/configuration | Possible contributing factor, not proven incorrect | Medium | The external definition must expose the filesystem and RWX capabilities for the observed case to run, but each declaration can be true for different volume flavors. The framework cannot express that condition. |

## Likely fix layer

The smallest coherent layer is the individual cross-node RWX test in `test/e2e/storage/testsuites/multivolume.go`, before it creates resources. A suite-wide skip would incorrectly remove other valid explicit-filesystem `multiVolume` cases. Renaming the pattern would hide real configuration and is insufficient.

An ext4/xfs-only guard is incomplete because `NtfsDynamicPV` reaches the same test on Windows. Conversely, rejecting every non-empty `FsType` confuses representation with semantics: the set is open and a future explicit shared filesystem could legitimately support cross-node RWX. The more precise options are (in increasing structural scope) a narrowly documented predicate for known single-host filesystems or explicit compatibility metadata on `TestPattern`. SIG Storage should choose between those representations before implementation. `ext3` should be discussed as future-proofing because its dynamic pattern exists even though `multiVolume` does not currently select it.

The maintainer question should therefore be updated from “ext4/xfs versus any non-empty fsType” to: “The inventory finds ext4, xfs and Windows ntfs in the affected suite, plus an existing ext3 dynamic pattern outside it. Should the cross-node RWX case use an explicit pattern compatibility property, or a local-filesystem predicate covering these known values?”

## Scope and non-goals

- No Kubernetes source modification in this stage.
- No claim that the vSphere driver itself is defective without its exact external test definition and CSI request/response evidence.
- No attempt to fix the separate node-affinity composition observation.
- No full cluster or CSI E2E execution.
