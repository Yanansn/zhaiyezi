# Contribution Task Brief

Use one bounded brief for one contribution stage. The assigned Agent owns the
stage and may not infer a later stage or public permission.

```yaml
task_id: example-stage
task_type: ecosystem-analysis | code-map | plan | implementation | validation | publication
assigned_agent: agent:terra | agent:sol
repository: owner/repository
issue: owner/repository#number
stage: one concrete stage
goal: one concrete result
confirmed_facts: []
required_investigation: []
expected_outputs: []
allowed_actions: []
prohibited_actions: []
approval_required: false
```

## Preflight

1. Run `python3 scripts/validate_agent_protocol.py`.
2. Verify facts repository branch, HEAD, remote, and worktree.
3. For code work, independently verify target path, remotes, base, working
   branch, HEAD, and worktree.
4. Resolve official upstream and User fork from URLs, not remote names.
5. Stop on missing scope, stale facts, unknown changes, divergent bases, or
   unauthorized actions.

Fetch, fast-forward, merge, rebase, force-push, upstream modification, facts
Push, target-fork Push, PR creation, and public actions each require separate
authorization.

## Required checks by stage

| Stage | Required checks | Minimum output |
| --- | --- | --- |
| ecosystem-analysis | only when ecosystem facts can affect the decision | `ECOSYSTEM.md` |
| code-map | relevant files, symbols, ownership, tests, and data flow | `CODE-MAP.md` |
| plan | confirmed boundary, non-goals, alternatives, risks, acceptance | `PLAN.md` |
| implementation | bounded local source change | `IMPLEMENTATION.md` |
| validation | targeted checks and proportional integration/CI checks | `TESTING.md` |
| publication | exact reviewed public Draft and live identity check | `PR.md` or communication draft |

`PROJECT.yaml`, `ISSUE.md`, `KNOWLEDGE.md`, `ECOSYSTEM.md`, `ANALYSIS.md`,
`JOURNAL.md`, `LEARNING.md`, and `COMMENT-DRAFT.md` are conditional. Do not
create placeholders merely to satisfy a checklist.

## Scope and discussion gates

Refresh `ECOSYSTEM.md` when new comments, PRs, Timeline events, workarounds, CI,
ownership, or maintainer direction could change scope, feasibility, acceptance,
or implementation. Enter discussion re-analysis and pause coding until the
Confirmed Implementation Boundary is clear. Binding-only, protocol, facts-only,
and narrow code verification may mark ecosystem analysis not applicable.

Implementation requires a new task that explicitly authorizes local
modification. Keep changes focused and do not modify a related repository
without a separate scope confirmation.

## Validation and return

Run the narrowest meaningful checks first. Record exact commands, environment,
results, failures, limitations, and CI-only coverage. Inspect facts and target
repositories separately. Return changed files, validation, Git state, what was
committed or pushed, and one bounded next action.

## Public actions

Prepare an exact Draft before publication. Sol or a human/team reviewer may
perform technical review. User approval and live authenticated-identity
verification are mandatory immediately before any public action. Afterward
record URL, time, actual content, and maintainer feedback.
