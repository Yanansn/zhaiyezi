# Screening classifications and confidence

`screening_classification` is independent of the formal Issue `status` and exists only for Deep Audit candidates. Quick Filter exclusions have a `rule`, not a classification. Choose exactly one classification per deeply audited candidate.

| Classification | Definition and required evidence | Admission | Recheck |
| --- | --- | --- | --- |
| `available` | Every mandatory check passed; no known assignee, owner, implementation conflict, current fix, blocking design ambiguity, infrastructure/third-party ownership, or infeasible scope. | Eligible for Gate, but not passed by classification alone | Re-verify immediately before admission |
| `occupied` | A current assignee or explicit accepted owner is actively responsible. | No | When ownership is released or stale by project convention |
| `implicit-owner` | Context shows an unassigned contributor actively investigating, reproducing, fixing, or preparing a PR. | No | When contributor abandons work or maintainers reopen it |
| `author-implementation` | Issue author reports a local/ready implementation or tests. | No | When author abandons or invites another implementation |
| `implementation-pr-exists` | One active PR implements substantially the requested work. | No | On PR closure, merge, or scope change |
| `competing-open-prs` | Multiple active implementations compete or overlap. | No | After maintainers choose or all implementations end |
| `already-implemented` | Verified merged change implements the request on the relevant current base, though Issue state/linkage may lag. | No | Only if evidence suggests incomplete coverage/regression |
| `already-fixed` | Current target branch behavior is verified fixed without remaining requested work. | No | If a reproducible regression appears |
| `blocked-by-design` | Required API, compatibility, UX, or SIG decision is unresolved. | No | After authoritative direction resolves the choice |
| `infrastructure` | Work fundamentally depends on CI/cloud/scale/hardware operations outside the requested contributor scope. | No | If owners provide an accessible bounded path |
| `third-party` | Root cause or required fix belongs to an external project/vendor. | No | If upstream responsibility is later established |
| `not-a-kubernetes-bug` | For Kubernetes scans, evidence shows the reported behavior is not a Kubernetes defect. | No | If new reproduction changes attribution |
| `insufficient-evidence` | A mandatory fact, search, linked item, or current-base conclusion cannot be obtained. | No | Complete the missing audit |
| `watchlist` | Not currently safe to pursue, but an identified event may make it eligible (stale ownership, unresolved PR/review, emerging scope). | No | At the recorded trigger/date |
| `do-not-pursue` | Evidence shows poor fit, excessive risk, duplication, rejection, or no reasonable contribution path. | No | Normally no; state an exceptional trigger if any |

## Availability checklist

`available` requires all of the following:

- no known assignee or valid implicit owner;
- no author implementation, active implementation PR, or competing PR;
- no merged but unlinked implementation and no confirmed current-base fix;
- no unresolved design blocker;
- not primarily third-party or infrastructure work;
- a basically clear problem boundary and plausible independent completion;
- every mandatory audit and evidence flag is complete.

No assignee, several quiet days, or absence of a PR is never sufficient evidence by itself.

## Implicit ownership

Common ownership signals include:

```text
I'd like to investigate
I'll investigate
I'm working on this
I'll reproduce
I reproduced it
I found the root cause
I have a local fix
I have tests ready
I'll send a PR
PR incoming
Happy to work on a fix
Working implementation ready
```

Interpret these in context: distinguish brief interest from active investigation, a local implementation, a submitted PR, long inactivity, explicit abandonment, and maintainer reopening. Prefer respecting an existing contributor when evidence is ambiguous; use `watchlist` or `insufficient-evidence` instead of silently taking over.

## Confidence

- `high`: every mandatory search completed; all comments read; Timeline and relevant relationships available; every related PR opened; source/symbol and current-base checks completed where needed; limitations do not affect ownership, implementation, design, or feasibility; no unresolved conflict.
- `medium`: the classification is supported, but a known non-core limitation remains. A medium-confidence `available` candidate needs explicit user acceptance at the Gate.
- `low`: material evidence is incomplete, stale, inaccessible, or contradictory. It cannot pass the Gate.

Confidence cannot be `high` when comment pagination or Timeline is incomplete; GitHub search, Development, Project, or a relevant PR is inaccessible; core symbol/current-base search is incomplete; or design/ownership remains uncertain.

Bucket rules and the persisted Admission Gate state are defined once in [output-schema.md](output-schema.md).
