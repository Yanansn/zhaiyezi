#!/usr/bin/env python3
"""Initialize a repository-agnostic issue contribution record."""

from __future__ import annotations

import argparse
from datetime import date
import json
from pathlib import Path


DOCUMENTS = {
    "ISSUE.md": "# Issue\n\n## Source facts\n\n## Requirement summary\n\n## Acceptance signals\n",
    "KNOWLEDGE.md": "# Knowledge\n\n<!-- Add only the background needed to understand this Issue. -->\n",
    "ANALYSIS.md": "# Analysis\n\n## Plain-language explanation\n\n## Current behavior\n\n## Expected behavior\n\n## Scope and non-goals\n\n## Root cause or hypotheses\n",
    "CODE-MAP.md": "# Code map\n\n## Entry points\n\n## Relevant files\n\n## Call flow\n\n## Existing tests and analogues\n",
    "PLAN.md": "# Plan\n\n## Preferred solution\n\n## Alternatives\n\n## Risks\n\n## Validation plan\n",
    "IMPLEMENTATION.md": "# Implementation\n\n## Changes\n\n## Reasoning\n\n## Deviations from plan\n",
    "TESTING.md": "# Testing\n\n## Environment\n\n## Commands and results\n\n## Limitations\n\n## CI results\n",
    "LEARNING.md": "# Learning\n\n## Concepts\n\n## Reusable methods\n\n## Open questions\n",
    "PR.md": "# Pull request\n\n## Publication status\n\n- Current status: Draft\n- Target repository: not-set\n- Expected GitHub identity: user-must-specify-before-publication\n- Authenticated GitHub identity: verify-before-publish\n- Identity verified: no\n- Reviewed by Chat: no\n- User approved: no\n- Publication authorized: no\n- Published at: not-published\n- GitHub URL: not-published\n\n## Repositories\n\n- Official upstream:\n- User fork:\n\n## Branches and commits\n\n- Base branch:\n- Head branch:\n- Commits:\n\n## Draft\n\n- Title:\n- Body:\n- Issue linkage:\n- Test summary:\n\n## Submission\n\n- Number:\n- URL:\n- State: not-created\n\n## CI status\n\n## Review feedback\n\n## Final outcome\n",
}


def yaml_value(value: str | None) -> str:
    return "null" if value is None else json.dumps(value)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("issue", help="Issue identifier, for example owner/repo#123")
    parser.add_argument("--root", default="issues", help="Issue records root")
    parser.add_argument("--facts-repository", help="Facts repository, for example user/zhaiyezi")
    parser.add_argument("--facts-branch", default="main", help="Facts repository branch")
    parser.add_argument("--base-branch", default="main", help="Official upstream base branch")
    parser.add_argument("--fork-repository", help="User fork, for example user/project")
    parser.add_argument("--working-branch", help="Upstream working branch")
    args = parser.parse_args()

    repo, number = args.issue.split("#", 1)
    owner, name = repo.split("/", 1)
    slug = f"{owner}-{name}-{number}".lower()
    target = Path(args.root) / slug
    target.mkdir(parents=True, exist_ok=False)

    status = f'''issue: "{args.issue}"
status: candidate
recommendation: pending
last_verified: "{date.today().isoformat()}"
facts_repository:
  repository: {yaml_value(args.facts_repository)}
  branch: {yaml_value(args.facts_branch)}
  commit: null
upstream:
  repository: {yaml_value(repo)}
  base_branch: {yaml_value(args.base_branch)}
  base_commit: null
fork:
  repository: {yaml_value(args.fork_repository)}
  branch: {yaml_value(args.working_branch)}
  commit: null
pull_request:
  number: null
  url: null
  state: not-created
public_communication:
  draft_ready: false
  reviewed: false
  user_approved: false
  published: false
  expected_identity: null
  identity_verified: false
blockers: []
next_actions:
  - verify live issue state
'''
    (target / "STATUS.yaml").write_text(status, encoding="utf-8")
    for filename, content in DOCUMENTS.items():
        (target / filename).write_text(content, encoding="utf-8")
    (target / "JOURNAL.md").write_text(
        f"# Journal\n\n## {date.today().isoformat()}\n\n- Issue record initialized.\n",
        encoding="utf-8",
    )
    print(target)


if __name__ == "__main__":
    main()
