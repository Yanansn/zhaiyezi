# Agent roles

## Chat (`decision-agent`)

Chat owns:

- `decisions/**`
- `agent-work/tasks/*/REQUEST.yaml`
- `agent-work/tasks/*/REVIEW.yaml`

Chat creates bounded requests and reviews Codex results. It does not edit `RESULT.yaml`, manufacture execution evidence, publish as the user, or turn evidence into an Admission decision without the existing Screening gate.

## Codex (`execution-agent`)

Codex owns:

- `agent-work/tasks/*/RESULT.yaml`
- `agent-work/tasks/*/REPORT.md`
- `agent-work/tasks/*/evidence/**`
- `screenings/**`

Codex executes the recorded stage, reports validation and limitations, and returns gaps instead of inventing a decision. It does not edit Chat-owned artifacts or independently classify a candidate, admit an Issue, or publish upstream.

## User (`approval-authority`)

The user semantically owns `agent-work/tasks/*/APPROVAL.yaml` and is the final authority for protected Git and GitHub actions. Codex may record only the user's exact current instruction.

## Shared file

`HANDOFF.md` is shared and serialized. A task modifying it must name it in `expected_outputs`, and concurrent writers must stop. It is not a substitute for task artifacts.
