# Knowledge, Inventory and code-map contract

Use the smallest research depth that makes the issue understandable and prevents a wrong engineering boundary.

## Document responsibilities

- `ISSUE.md`: external facts and the problem contract—state, discussion, scope and acceptance.
- `KNOWLEDGE.md`: background a new reader needs—terms, relationships, mental models, exceptions and misconceptions. Do not put issue root-cause conclusions or a chosen implementation here.
- `CODE-MAP.md`: source facts—definitions, files, Inventory, registration, calls, data flow, lifecycle, history and test seams.
- `ANALYSIS.md`: inferences from the above—hypotheses, evidence, confidence, qualification, risks and solution comparison.
- `PLAN.md`: the direction to implement after required confirmation—change boundary, alternatives and validation.

## Knowledge decision

Create `KNOWLEDGE.md` for every new record, but fill only what the issue needs. Explain a domain term before it becomes essential to reasoning. Prefer a link to stable shared knowledge when it is sufficient, while keeping issue-specific prerequisites local so a cold start remains understandable.

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
