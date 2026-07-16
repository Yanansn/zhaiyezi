# Plan

## Preferred solution

Not selected in the `code-map` stage. Wait for SIG Storage to confirm the intended fsType compatibility rule before preparing an implementation plan.

## Alternatives

- Case-local guard in the cross-node RWX test (current smallest candidate).
- Conditional capability model in `DriverInfo` (more expressive, much larger scope).
- Split downstream external driver definitions by storage flavor (depends on the exact vSphere test configuration).

## Risks

- A guard that is too broad could suppress valid shared-filesystem or raw-block RWX coverage.
- A guard that lists only ext4/xfs may leave the same conceptual issue for ntfs or future local filesystems.

## Validation plan

To be decided in a future `plan` stage; the code map identifies a pure table-driven predicate test as the minimum candidate.
