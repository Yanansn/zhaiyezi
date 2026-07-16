# Issue: generated RWX scenarios use ext4/xfs patterns

## Source facts

- Upstream: [`kubernetes/kubernetes#140502`](https://github.com/kubernetes/kubernetes/issues/140502)
- Title: `The generated test scenarios for RWX volume types dont make sense`
- Opened by `gnufied` on 2026-07-13.
- State verified on 2026-07-16: open, no assignee, no linked Kubernetes implementation PR.
- Labels: `kind/bug`, `sig/storage`, `needs-triage`; `triage/accepted` is absent.
- Discussion consists of the automatic awaiting-triage message and the author's `/sig storage` command. No contributor has claimed implementation.
- The timeline cross-references merged `openshift/release#81632`, which changes an OpenShift vSphere CI pool selector (`vsanfs=true`); it is not a Kubernetes implementation fix.
- Reported test name:

  ```text
  External Storage [Driver: csi.vsphere.vmware.com]
  [Testpattern: Dynamic PV (ext4)] multiVolume [Slow]
  should concurrently access the single volume from pods on different node
  ```

## Plain-language problem

The generic storage suite combines a filesystem pattern such as `Dynamic PV (ext4)` with a test that requests one `ReadWriteMany` volume and mounts it read/write from two Pods intended for different nodes. The name is generated from real pattern metadata: `ext4` is also passed into dynamic provisioning, so this is not merely confusing display text.

The author's statement that “RWX cannot support ext4” needs qualification. A shared storage service may use ext4 internally on its server or backing devices, while clients mount a network/shared filesystem. The questionable case here is asking the CSI provisioning/mount path for an explicit client-facing `ext4` or `xfs` filesystem and then using the same filesystem volume from multiple nodes.

## Requirement summary

- Determine how the suite creates the name and the actual StorageClass, PVC, PV and Pods.
- Determine why `SupportedFsType: ext4/xfs` and `CapRWX` are combined.
- Decide whether the defect belongs in naming, pattern filtering, resource creation, or external driver configuration.
- Identify a small validation strategy that does not require a full CSI E2E run.

## Acceptance signals and current gate

- A correct fix must prevent an invalid explicit filesystem/RWX combination without removing valid ext4/xfs tests elsewhere in `multiVolume`.
- It must preserve valid RWX tests for shared filesystems and raw block modes.
- SIG Storage has not accepted or directed the issue yet. Implementation should wait for `triage/accepted` or a maintainer-confirmed direction because the correct compatibility rule (specific filesystems versus all explicit `FsType` values) is a policy decision.
