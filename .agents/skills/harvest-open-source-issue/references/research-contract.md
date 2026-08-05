# Ecosystem, Knowledge, Inventory and code-map contract

Use the smallest research depth that makes the issue understandable and prevents a wrong engineering boundary.

## Document responsibilities

- `ISSUE.md`: external facts and the problem contract—state, discussion, scope and acceptance.
- `ECOSYSTEM.md`: conditional continuous facts when ecosystem state can affect scope, ownership, feasibility, acceptance, or implementation.
- `KNOWLEDGE.md`: background a new reader needs—terms, relationships, mental models, exceptions and misconceptions. Do not put issue root-cause conclusions or a chosen implementation here.
- `CODE-MAP.md`: source facts—definitions, files, Inventory, registration, calls, data flow, lifecycle, history and test seams.
- `ANALYSIS.md`: inferences from the above—hypotheses, evidence, confidence, qualification, risks and solution comparison.
- `PLAN.md`: the direction to implement after required confirmation—change boundary, alternatives and validation.

## Conditional Issue Ecosystem Analysis

Create `ECOSYSTEM.md` when the task or changed ecosystem facts can affect scope, ownership, feasibility, acceptance, or implementation. Refresh it whenever those facts change.

Required sections:

```markdown
# Issue ecosystem

## 1. Issue Timeline
## 2. Timeline Events
## 3. Development
## 4. Downstream
## 5. Related Work
## 6. CI
## 7. Maintainer Position
## 8. Open Questions
## 9. Current Ecosystem Summary
```

The analysis must cover label, project, milestone, assignee and state changes; mention/reference/cross-reference events; linked Issues, branches and PRs; downstream projects and workarounds; related, historical or reverted work; project CI and downstream CI; expressed maintainer positions; and unresolved questions. Apply selected ecosystem Profiles for project-specific CI systems. Classify each linked item as a real upstream implementation, downstream workaround, related evidence, historical work or reference-only event. If Development is empty, state `No linked implementation.`. Record access limitations rather than guessing unavailable metadata.

`ECOSYSTEM.md` is continuous knowledge. `COMMENT-DRAFT.md`, PR descriptions and other public Drafts are snapshots governed by the Public Communication Contract. New ecosystem facts update `ECOSYSTEM.md`; they do not silently mutate a reviewed or published public artifact.

Material community discussion also requires a durable re-analysis entry under `## 7. Maintainer Position`. New records include the following shape. Preserve, rather than overwrite, completed entries:

```text
Previous assumption:
New evidence:
Commenter role and authority:
Evidence classification:
Impact:
Updated conclusion:
Remaining uncertainty:
Next decision gate:
```

Append a new field block for each material re-analysis instead of replacing an earlier completed block; validators evaluate the latest occurrence of each field. The authoritative evidence classes, status transitions, checklist and implementation gate are defined in the repository `AGENTS.md`. This contract defines the record shape, not a second workflow.

## Knowledge decision

Create `KNOWLEDGE.md` only when a domain term or mental model is needed for the current decision. Fill only what the issue needs. Prefer a link to stable shared knowledge when it is sufficient.

Suggested sections may be selected or removed:

```markdown
# Knowledge

## Why this knowledge is needed
## Core concepts
## How the concepts relate
## Simplified mental model
## Important distinctions and common misconceptions
## Knowledge extensions
## Terms used in this issue
## References
```

Knowledge is not an encyclopedia, source-code evidence, root-cause analysis or an implementation proposal.

## Inventory decision

Add an Inventory to `CODE-MAP.md` when a collection—such as an enum, registry, pattern, capability, feature gate, plugin, controller, predicate, driver, flag, API type, state, handler or schema field—can alter root cause, compatibility, test coverage or fix scope.

```markdown
## Inventory

### Scope and counting method
### Complete or relevant object set
### Definitions and locations
### Usage matrix
### Propagation or behavior
### Extensibility
### Relevance to this issue
### Completeness and limitations
```

State whether the result is complete or a relevant subset. Record the search/analysis method, definition and use sites, external/runtime extension points, and limitations. Distinguish at least these sets when applicable:

1. objects named in current source;
2. objects selected by current default registration;
3. values theoretically accepted at runtime or through external configuration.

A keyword search is an investigation input, not proof of a complete set. Stop once the bounded collection is sufficient for the issue decision; Inventory is not a mandate to document the entire upstream project.

## Lifecycle and data flow decision

Add `## Lifecycle and data flow` to `CODE-MAP.md` when an object or value crosses meaningful stages, for example:

```text
input
→ parsing
→ registration
→ filtering
→ resource construction
→ external call
→ observed result
```

Record transformations and ownership boundaries where a bug could be introduced. Keep this in `CODE-MAP.md` by default. Split it out only when it is large and reusable across issues.
