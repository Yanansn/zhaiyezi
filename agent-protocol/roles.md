# Agent roles

## Chat (`decision-agent`)

Chat semantically owns:

- `decisions/**`
- `agent-work/tasks/*/REQUEST.yaml`
- `agent-work/tasks/*/REVIEW.yaml`

Chat authors bounded requests and reviews Codex results. When Chat lacks repository write capability, Codex may materialize the complete Chat-authored content under explicit user instruction. Chat remains `decision_author`; materialization does not let Codex alter scope, permissions, status, or conclusions. Chat does not edit `RESULT.yaml`, manufacture execution evidence, publish as the user, or turn evidence into an Admission decision without the existing Screening gate.

## Codex (`execution-agent`)

Codex semantically owns:

- `agent-work/tasks/*/RESULT.yaml`
- `agent-work/tasks/*/REPORT.md`
- `agent-work/tasks/*/evidence/**`
- `screenings/**`

Codex executes the recorded stage, reports validation and limitations, and returns gaps instead of inventing a decision. It may act as repository materializer for Chat-authored REQUEST/REVIEW/decisions only with complete bounded content, explicit user instruction, valid provenance, and matching path authorization. It may similarly materialize a complete user approval only under that user's current explicit instruction. Codex never becomes the decision author through materialization and cannot independently classify, admit, approve, or publish.

## User (`approval-authority`)

The user semantically owns `agent-work/tasks/*/APPROVAL.yaml` and standing authorizations and is the final authority for protected Git and GitHub actions. Codex may materialize only the user's exact, complete current instruction, preserving `decision_author: user` provenance.

## Shared file

`HANDOFF.md` is shared and serialized. A task modifying it must name it in `expected_outputs`, and concurrent writers must stop. It is not a substitute for task artifacts.
