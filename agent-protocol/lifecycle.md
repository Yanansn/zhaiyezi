# Coordination lifecycle

## Artifact-derived task state

The fixed directory `agent-work/tasks/<task-id>/` is never renamed or moved. State is derived as follows:

```text
REQUEST ready, no RESULT                         ready
RESULT active                                    active
RESULT review, not reviewed at that revision     awaiting-review
RESULT blocked                                   blocked
RESULT failed                                    failed
REVIEW changes-requested for current revision    changes-requested
REVIEW rejected for current revision             rejected
REVIEW approved/completed for current revision   completed
```

Only an approved Chat Review can produce queue `completed`. A result cannot declare itself completed. After `changes-requested`, Codex preserves `REVIEW.yaml`, increments `RESULT.revision`, and records `supersedes_review: REVIEW.yaml`; the newer result then derives a new execution state. Approved or rejected Reviews cannot be superseded.

## Artifact handshake

Chat authors an immutable `REQUEST.yaml`. Codex authors `RESULT.yaml`, `REPORT.md`, and requested evidence. Chat reviews the exact `RESULT.revision` in `REVIEW.yaml`. Protected actions must be authorized before execution, not retroactively during Review.

Repository materialization is separate from that semantic authorship: when Chat cannot write the repository, Codex may serialize a complete Chat decision under explicit user instruction. Delegated artifacts retain `decision_author: chat`, identify `materialized_by: codex`, and record the bounded source. Codex must stop on ambiguity and cannot execute a delegated REQUEST until it is persisted and validates.

User approval follows the same provenance rule but a stricter gate: Codex can materialize only a complete current user approval, and standing authorization cannot manufacture or pre-authorize `materialize_user_artifact`.

## Contribution compatibility

```text
discovered → evidence_requested → evidence_completed → awaiting_review
→ deep_audit → admission_pending → implementation_ready → implementing
→ verification → pr_ready → completed
```

- `evidence_completed` can only enter `awaiting_review`; it is not `available` or Admission.
- Deep Audit and Admission use the existing Screening contracts.
- Registry mutation and formal Issue initialization remain independently approved.
- Implementation requires a bounded implementation request after the existing boundary gate.
- Queue `completed` and coordination `pr_ready` do not skip the formal `submitted`, `reviewing`, and terminal PR states.

Only committed and pushed facts are shared with remote Chat. A local queue state remains local until separately authorized Commit and Push succeed.
