# Candidate Admission Gate

The Gate separates lightweight screening from the formal contribution lifecycle. Passing it does not select an Issue or authorize public action.

## Required conditions

All must be true:

1. The complete fourteen-stage audit and all mandatory searches are recorded with timestamps.
2. `screening_classification` is `available`.
3. `screening_confidence` is `high`, or the user explicitly accepts the stated limitations of `medium` confidence.
4. No known assignee, implicit owner, author implementation, implementation PR, competing PR, merged implementation, or current-base fix conflicts with pursuit.
5. No blocking design ambiguity, third-party attribution, or inaccessible infrastructure dependency remains.
6. The problem and feasible independent contribution boundary are sufficiently clear.
7. The user explicitly decides to continue with this candidate.

Immediately before admission, refresh volatile ownership, Issue/PR state, discussion, searches, and base facts. A changed fact returns the candidate to audit/classification.

## Separately approved admission actions

Only after the Gate and explicit authorization may Codex:

1. add the Issue to `registry/issues.yaml`;
2. initialize `issues/<owner>-<repo>-<number>/`;
3. set formal `status` to `candidate` or `screening`;
4. prepare a contribution Execution Brief for `harvest-open-source-issue`.

Each repository mutation, Commit, Push, assignment, comment, label change, or other public action keeps its own approval boundary. Default to prohibited.

```text
screening_classification: available ≠ status: selected
```

Record `admitted`, `awaiting-user-decision`, or `not-admitted`, the decision time, evidence refresh time, user decision, and which mutations were authorized.
