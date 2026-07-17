# Issue: generated RWX scenarios use ext4/xfs patterns

## Source facts

- Upstream: [`kubernetes/kubernetes#140502`](https://github.com/kubernetes/kubernetes/issues/140502)
- Title: `The generated test scenarios for RWX volume types dont make sense`
- Opened by `gnufied` on 2026-07-13.
- State verified on 2026-07-17: open, no assignee, no milestone, and still awaiting triage.
- Labels: `kind/bug`, `sig/storage`, `needs-triage`; `triage/accepted` is absent.
- After `bzsuni` asked for the preferred fix boundary, Issue author `gnufied` suggested exploring removal of filesystem names from the affected test name. The wording is exploratory and does not by itself confirm an implementation boundary.
- Contributor `darshansreenivas` linked active Kubernetes PR [`#140565`](https://github.com/kubernetes/kubernetes/pull/140565), which skips the case whenever `pattern.FsType` is non-empty. In an inline comment within a `COMMENTED` Review, `gnufied` said the test should not be skipped and the problem is the test name. The PR remains open and blocked, with no approving or changes-requested Review.
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

- The highest-authority current preference is not to skip the test, but the exact way to change the generated name has not been established.
- It is not confirmed whether a fix should preserve `TestPattern.FsType` and the resulting StorageClass parameters unchanged, nor which generated names are in scope.
- Non-goals and an observable acceptance criterion remain unstated. The Issue is therefore `awaiting-scope-confirmation`, not ready for Plan or Coding.
