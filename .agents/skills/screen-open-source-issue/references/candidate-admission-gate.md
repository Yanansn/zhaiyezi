# Candidate Admission Gate

The Gate separates completed Deep Audit from the formal contribution lifecycle. `screening_classification: available` only makes a candidate eligible for evaluation; it does not mean the Gate passed, the Issue was selected, or any repository mutation was authorized.

The persisted `admission` mapping and its allowed values are defined by [output-schema.md](output-schema.md).

## Required conditions for `passed`

All must be true:

1. The complete fourteen-stage audit and all mandatory searches are recorded.
2. Classification is `available`; confidence is `high`, or is `medium` with the user's explicit acceptance of named limitations.
3. Volatile ownership, Issue/PR state, discussion, searches, and current-base facts were refreshed and `evidence_refreshed_at` records when.
4. No known owner, implementation conflict, current fix, blocking design ambiguity, third-party attribution, or inaccessible infrastructure dependency remains.
5. The problem and feasible independent contribution boundary are sufficiently clear.
6. `user_decision` is `continue`, and `admitted_at` records the Gate decision time.

When evidence changes or becomes stale, use `stale-recheck-required`; refresh and re-evaluate rather than retaining `passed` by assumption. A declined candidate cannot pass.

## Medium-confidence decision

For medium confidence, Gate passage additionally requires:

```yaml
medium_confidence_limitations_accepted: true
accepted_limitations:
  - "the specific limitation the user accepted"
```

High confidence does not require a non-empty accepted-limitations list.

## Independent authorization boundaries

These fields are independent of `gate_status`:

```yaml
registry_mutation_authorized: false
issue_initialization_authorized: false
contribution_brief_authorized: false
```

A passed Gate with all three values `false` is valid. Only explicit user authorization may change each value. Gate evaluation never performs or infers a registry edit, Issue initialization, contribution Brief, Commit, Push, assignment, comment, label change, or other public action.

After a passed Gate and the relevant separate authorizations, Codex may add the registry entry, initialize the formal record with status `candidate` or `screening`, and prepare the handoff to `harvest-open-source-issue`.
