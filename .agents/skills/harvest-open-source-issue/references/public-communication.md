# Public communication contract

Every GitHub-facing action is published under the user's account and represents the user. ChatGPT and Codex have no independent community identity.

## Lifecycle

```text
Research
→ Draft
→ Chat Review
→ Awaiting User Approval
→ Publish
→ Awaiting Maintainer Feedback
```

This lifecycle applies to issue and PR comments, replies, PR titles and descriptions, reviews, Discussions, RFCs, assignment or label commands, reviewer requests, and Commit messages or descriptions that will become public on GitHub.

## Gates

1. Research establishes the facts and risks.
2. Draft records the exact proposed public text and target without publishing it.
3. Chat Review checks technical accuracy, tone, scope and community risk.
4. Awaiting User Approval means the reviewed text is frozen and publication is still prohibited.
5. Publish requires an Execution Brief or later user message that explicitly authorizes the exact public action.
6. After publication, record the URL, time, actual text and the maintainer-feedback state.

Preparing, reviewing, committing or pushing a Draft to the facts repository never authorizes publication. Material edits after Review or approval return the artifact to Draft and require new Review and approval.

## Required artifact metadata

Public Draft records must state:

- current publication status: `Draft`, `Reviewed by Chat`, `Awaiting user approval`, `Published`, or `Superseded`;
- whether Chat Review is complete;
- whether user approval and publication authorization are present;
- expected and authenticated GitHub identities plus whether they match;
- publication time and GitHub URL after publication;
- the exact target Issue, PR, Discussion or repository.

Before publishing, re-verify live community state, user identity, target and exact approved text. Authorization to prepare, publish, reply and update existing public content is separate and non-transferable.

## Identity verification

Before any Issue comment or reply, Pull Request, Pull Request Review, Discussion, RFC, reviewer request, assignment or label command is published, record and verify:

```text
Expected GitHub identity
Authenticated GitHub identity
Identity verified (yes/no)
```

- The user explicitly specifies the expected GitHub identity.
- Obtain the authenticated GitHub identity in real time immediately before publication, for example from `gh auth status` or equivalent actual authentication evidence.
- Stop publication when the authenticated identity does not match the expected identity.
- Never infer identity from an SSH key name, Git remote URL or historical record.
- Identity Verification is a mandatory Publish Gate, not a lifecycle or Issue status.

> Identity verification is a mandatory publication gate. Publication must stop if the authenticated GitHub identity does not match the expected identity.
