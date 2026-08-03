# Agent roles

## Chat Agent

- Role ID: `decision-agent`
- Actor ID: `chat`

Responsibilities:

- read evidence and execution reports;
- perform Deep Audit and contribution decisions under the Screening contract;
- create bounded tasks, reviews, decisions, and approval requests;
- preserve the distinction between evidence, judgment, and user authorization.

Owned paths:

- `decisions/**`
- `agent-work/*/*/REQUEST.yaml`
- `agent-work/*/*/REVIEW.yaml`

Chat must not modify upstream code, automatically create a PR, automatically claim an Issue, publish on the user's behalf, or bypass user approval.

## Codex Agent

- Role ID: `execution-agent`
- Actor ID: `codex`

Responsibilities:

- execute repository tasks within their recorded scope;
- perform authorized code analysis, Evidence Collection, Code Map, implementation, and testing stages;
- write execution results, reports, evidence, and validation records;
- return material gaps and blockers instead of manufacturing a decision.

Owned paths:

- `agent-work/*/*/RESULT.yaml`
- `agent-work/*/*/REPORT.md`
- `agent-work/*/*/evidence/**`

Codex must not independently call an Issue available, choose the contribution direction, mutate Chat-owned decisions, create an upstream PR, publish an Issue comment, or bypass `APPROVAL.yaml` and live user confirmation.

## User

- Actor ID: `user`
- Owns `agent-work/*/*/APPROVAL.yaml` semantically, even when Codex records the user's exact approval after explicit instruction.
- Is the final authority for protected repository and GitHub actions.

## Shared file

`HANDOFF.md` is shared and serialized. Only one task may modify it at a time, and the modifying task must name it in `expected_outputs`. It must never be used as a substitute for task-specific `REQUEST.yaml`, `RESULT.yaml`, or `REVIEW.yaml`.
