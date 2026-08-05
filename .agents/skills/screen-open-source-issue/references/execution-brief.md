# Screening Task Brief

Use one bounded brief for one screening stage. The assigned Agent owns the
work; no Chat handoff is required.

```yaml
task_id: example-screening
task_type: evidence-collection | screening-record | deep-audit | code-verification
assigned_agent: agent:luna | agent:terra | agent:sol
repository: owner/repository
issue_scope: []
goal: one concrete stage result
evidence_refs: []
output_location: agent-work/tasks/<task-id>
allowed_actions: []
prohibited_actions: []
approval_required: false
```

## Stage minimums

| Stage | Agent | Minimum input | Minimum output |
| --- | --- | --- | --- |
| candidate/screening-record | Luna | finite candidate scope | `REQUEST.yaml`, `RESULT.yaml` |
| issue-evidence-collection | Luna | finite Issue list and sources | `SCOPE.yaml`, `REPORT.md`, `evidence/*.yaml` |
| deep-audit | Terra | completed evidence and target binding | `RESULT.yaml` |
| code-verification | Terra | enumerated paths/symbols and baseline | code facts, commands, results, limitations |
| escalation review | Sol | supplied evidence and analysis | escalation `DECISION.yaml` |

## Approval boundary

The brief must list allowed and prohibited actions. Missing approval fields mean
prohibited. Registry mutation, formal Issue initialization, facts Push, target
fork Push, PR creation, comments, labels, assignment, and other public actions
are separate approvals. `approval_required: true` does not itself authorize an
action.

## Preflight and stop conditions

Before mutation, verify the facts repository branch, HEAD, remote, and
worktree. For target-repository work, verify that repository independently.
Stop on missing scope, contradictory facts, stale baseline, unknown changes,
inaccessible required evidence, an existing output path, or an action outside
the brief. Return the gap to the assigned Agent; do not broaden the search.

## Evidence boundaries

Evidence collection records raw facts only. It must not classify, recommend
admission, modify registry, initialize formal Issue records, or publish.
Screening classification, confidence, and admission are separate fields.
`available` never means admitted or authorized for implementation.

## Return

Report collected facts, classifications when authorized, limitations, output
files, validation results, Git state, and actions not performed. State whether
Commit or Push occurred.
