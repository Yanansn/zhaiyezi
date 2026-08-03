# Coordination lifecycle

## Artifact handshake

Chat hands work to Codex through `REQUEST.yaml`. A chat message may alert Codex that a task exists, but cannot replace the repository task or expand its permissions.

Codex returns work through `RESULT.yaml`, `REPORT.md`, and the requested evidence paths. Chat reviews those exact artifacts and records `REVIEW.yaml`. A result is not accepted merely because Codex finished running commands.

When a requested action requires user confirmation, the exact approved actions and scope must be recorded in `APPROVAL.yaml`. Approval for one action does not transfer to another action, repository, task, or publication.

## Task sequence

```text
REQUEST.yaml (ready)
→ RESULT.yaml (active)
→ RESULT.yaml (review)
→ REVIEW.yaml (completed | changes-requested | blocked)
→ next REQUEST.yaml when another bounded stage is needed
```

Codex can write a blocked or failed result without a Review. A completed queue task requires an approved Chat Review. Protected actions additionally require user approval before execution, not merely before Review.

## Contribution sequence

The coordination sequence mirrors, but does not replace, existing records:

```text
discovered
→ evidence_requested
→ evidence_completed
→ awaiting_review
→ deep_audit
→ admission_pending
→ implementation_ready
→ implementing
→ verification
→ pr_ready
→ completed
```

Mandatory gates:

- `evidence_completed → awaiting_review`; it cannot jump to Admission or `available`.
- Chat owns Deep Audit conclusions and records the Admission recommendation.
- `admission_pending → implementation_ready` requires the existing Candidate Admission Gate plus user authorization for registry and Issue-record actions where applicable.
- `implementation_ready → implementing` requires a new bounded implementation task.
- `pr_ready` only hands into the existing `submitted → reviewing → terminal` PR lifecycle when a PR is in scope and separately authorized.

## Repository visibility

Local changes are execution state, not shared state. Chat may treat a task result as shared only after the facts-repository Commit and Push explicitly authorized for that task are complete. The resulting commit SHA should be included in the execution report.
