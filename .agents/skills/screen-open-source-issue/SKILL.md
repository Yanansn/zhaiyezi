---
name: screen-open-source-issue
description: Run a bounded candidate, evidence, or screening task through the Codex Multi-Agent workflow without implementing fixes or performing public actions.
---

# Screen Open Source Issues

This Skill covers candidate discovery, evidence collection, screening, and
screening records. It does not implement upstream fixes, modify registry
admission state, or perform public GitHub actions.

## Agent ownership

- `agent:luna`: discovery, evidence collection, Quick Filter, screening,
  contribution-value analysis, and decision proposal.
- `agent:terra`: explicitly bounded Deep Audit or source/code verification.
- `agent:sol`: escalation review for architecture, concurrency, difficult
  debugging, or a high-risk final decision.

No manual review handoff is required. A task must have a valid
`REQUEST.yaml`, an assigned current Agent, a bounded goal, output paths, and an
approval boundary.

## Shared Preflight

Before any mutation:

1. Run `python3 scripts/validate_agent_protocol.py`.
2. Check the facts repository branch, HEAD, remote, and worktree.
3. Read the current REQUEST and only the records needed for this stage.
4. Stop on missing scope, contradictory facts, unknown local changes, or an
   action outside the request.

The facts repository and any target repository are checked independently.
Target binding never grants upstream write or public-action permission.

## Modes

### Pre-Deep-Audit Gate

Before creating or running a Deep Audit, perform a cheap, current gate. Confirm
that the Issue has a concrete symptom or affected boundary, public evidence is
readable enough to define scope, target binding and source baseline are valid,
and at least one meaningful verification route exists: local unit/CPU tests,
source facts, public CI/maintainer evidence, or a bounded reproduction path.

Before spending further screening or Deep Audit effort, check Issue comments and
maintainer discussion for an author-claimed boundary. If the Issue author or a
maintainer says they are implementing it, already have a draft, or will open a
PR, stop the workflow and record `author-claimed` with the author, timestamp,
comment, and URL. This marker is not a duplicate or admission decision. Do not
create a Deep Audit or implementation task until the author opens the PR,
explicitly withdraws the claim, or maintainers publicly release the scope.

Also record required runtime dependencies and whether the local environment has
them. Missing GPU, model, vLLM, CUDA, external service, or cross-repository
access is a feasibility limitation. If no low-cost alternative can support a
useful conclusion, stop before Deep Audit and record `needs-more-investigation`
or `watchlist` with the blocker. Do not spend a full audit budget to discover a
known environment blocker.

The gate must also check that expected effort fits the task's time, token, and
environment budget. Continuing without the required runtime is allowed only
when the task explicitly accepts CI-only risk or reliable upstream/maintainer
evidence makes the remaining question bounded; record that exception.

### Candidate / screening record — Luna

Use the task's smallest record set:

- `agent-work/tasks/<task-id>/REQUEST.yaml`
- `agent-work/tasks/<task-id>/RESULT.yaml`
- optional short `REPORT.md`

Record classification, confidence, evidence references, feasibility,
limitations, and next action directly in `RESULT.yaml`. `available` never
means admitted. Historical `screenings/` records remain readable; new tasks
use `scripts/validate_agent_protocol.py`.

### Evidence collection — Luna

Require a finite Issue list, sources, output location, and limitations. Collect
Issue body, comments, Timeline/Development, explicit PR references, searches,
related items, and raw ownership signals. Store evidence under
`evidence/<issue-number>.yaml`.

Evidence collection must not assign classification, confidence, availability,
admission, registry changes, formal Issue records, or public actions.

### Deep Audit — Terra

Consume completed evidence and a bounded target binding. Verify only the
specified Issue/PR/source facts, build the smallest relevant code map, and
record feasibility and risks in `RESULT.yaml`. Add a short `REPORT.md` or
`DECISION.yaml` only when the task contract requires it.

Run the full ecosystem audit only when the task explicitly requires it or when
new discussion, PR, CI, ownership, or scope evidence could change the result.

### Code Verification — Terra

Verify only the listed paths, symbols, baseline, tests, and commands. Do not
expand into Issue ownership, complete PR search, classification, or admission.

### Escalation — Sol

Read the supplied evidence and analysis, write an escalation-oriented
`DECISION.yaml`, and identify risks or unresolved gates. Sol does not modify
target source, commit facts, Push, or publish.

## Evidence rules

- No assignee or empty Development does not prove availability.
- A keyword hit is not proof of an implementation or owner.
- Inaccessible required evidence becomes a limitation, not an inference.
- Quick Filter is metadata-only and cannot carry Deep Audit classification.
- Every `available` result must have the required checks and current-base
  evidence for its conclusion.

## Admission boundary

Screening only recommends. Candidate Admission, registry mutation, formal Issue
initialization, implementation authorization, facts Push, target fork Push,
PR creation, and public GitHub actions are independent permissions. User
approval is required for protected actions.

## Outputs and handoff

Write only the task result and any explicitly required optional artifact.
Commit facts only when the current task explicitly authorizes it; Push and
public actions require separate User approval. Handoff text is optional; the
next stage starts only from a new bounded task.
