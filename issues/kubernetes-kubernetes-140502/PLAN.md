# Plan

## Preferred solution

Not selected. Discussion re-analysis invalidated the earlier compatibility-guard preference as an implementation-ready direction. Wait for confirmation of the exact naming boundary, underlying `FsType` behavior, non-goals and acceptance criteria before preparing a plan.

## Alternatives

- Naming-layer change that preserves the cross-node RWX test (current high-authority preference; exact mechanism unresolved).
- Case-local guard in the cross-node RWX test (earlier candidate; in tension with the current path-approver preference).
- Conditional capability model in `DriverInfo` (more expressive, much larger scope).
- Split downstream external driver definitions by storage flavor (depends on the exact vSphere test configuration).

## Risks

- A guard that is too broad could suppress valid shared-filesystem or raw-block RWX coverage.
- A guard that lists only ext4/xfs may leave the same conceptual issue for ntfs or future local filesystems.

## Validation plan

To be decided only after the Confirmed Implementation Boundary Gate passes. No current test proposal should be treated as accepted.
