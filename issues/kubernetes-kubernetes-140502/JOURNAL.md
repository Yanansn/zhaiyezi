# Journal

## 2026-07-16

- Issue record initialized.
- Verified the Issue is open, unassigned, still labeled `needs-triage`, and has no linked Kubernetes implementation PR.
- Verified facts repository `main` was clean at `a4317e681cb9ba8d051e41968bb3d83fcecc80ea`.
- Verified Kubernetes local `master`, `upstream/master`, and official remote `master` all pointed to `1b4e48f52199bcfb28ef6efd60522a082c3e78d0` with ahead/behind `0/0`; no fetch or synchronization was needed.
- Traced test registration, TestPattern naming, capability filtering, StorageClass/PVC/PV creation, Pod placement and cross-Pod read/write behavior.
- Confirmed ext4/xfs are not name-only metadata: the explicit fsType is written to the CSI StorageClass while the test requests a Filesystem RWX PVC.
- Classified the likely root cause as TestPattern/RWX combination plus an actual invalid resource request (B+C), with external driver configuration or the capability model as a possible contributor (D).
- Ran `go test ./test/e2e/storage/external -run '^TestDriverParameter$' -count=1`; it passed without a cluster.
- Decided not to implement or comment before SIG Storage confirms the desired compatibility rule.
- Re-verified the live Issue as open, unassigned, still labeled `needs-triage`, with no linked implementation PR or stop condition.
- Fetched official `upstream/master` and fast-forwarded the clean local Kubernetes `master` from `1b4e48f52199bcfb28ef6efd60522a082c3e78d0` to `7e8950f1ec186066fabdfe69d69f92fbb04592da`; local master is now `0/0` against upstream. The user fork was intentionally not synchronized.
- Completed a source-definition inventory: 46 named TestPatterns, 21 with explicit fsType, covering ext3 (5), ext4 (5), xfs (5), and ntfs (6); no btrfs, zfs or exfat storage pattern exists.
- Confirmed `NtfsDynamicPV` is a real Windows-tagged pattern selected by `multiVolume` and reaches the same dynamic StorageClass path as ext4/xfs. `Ext3DynamicPV` exists but is not currently selected by that suite.
- Confirmed `SupportedFsType` is an open string set decoded from external driver data, while the effective tested values remain bounded by suite-selected TestPatterns.
- Refined the prospective fix scope: an ext4/xfs-only check is incomplete, while rejecting every non-empty fsType is semantically overbroad. Maintainer confirmation should compare explicit pattern compatibility metadata with a documented known-local-filesystem predicate.
