#!/usr/bin/env python3
"""Initialize a repository-agnostic issue contribution record."""

from __future__ import annotations

import argparse
from datetime import date
from pathlib import Path


DOCUMENTS = {
    "ISSUE.md": "# Issue\n\n## Source facts\n\n## Requirement summary\n\n## Acceptance signals\n",
    "ANALYSIS.md": "# Analysis\n\n## Plain-language explanation\n\n## Current behavior\n\n## Expected behavior\n\n## Scope and non-goals\n\n## Root cause or hypotheses\n",
    "CODE-MAP.md": "# Code map\n\n## Entry points\n\n## Relevant files\n\n## Call flow\n\n## Existing tests and analogues\n",
    "PLAN.md": "# Plan\n\n## Preferred solution\n\n## Alternatives\n\n## Risks\n\n## Validation plan\n",
    "IMPLEMENTATION.md": "# Implementation\n\n## Changes\n\n## Reasoning\n\n## Deviations from plan\n",
    "TESTING.md": "# Testing\n\n## Environment\n\n## Commands and results\n\n## Limitations\n\n## CI results\n",
    "LEARNING.md": "# Learning\n\n## Concepts\n\n## Reusable methods\n\n## Open questions\n",
    "PR.md": "# Pull request\n\n## Branch\n\n## Commits\n\n## Draft\n\n## Review and outcome\n",
}


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("issue", help="Issue identifier, for example owner/repo#123")
    parser.add_argument("--root", default="issues", help="Issue records root")
    args = parser.parse_args()

    repo, number = args.issue.split("#", 1)
    owner, name = repo.split("/", 1)
    slug = f"{owner}-{name}-{number}".lower()
    target = Path(args.root) / slug
    target.mkdir(parents=True, exist_ok=False)

    status = f'''issue: "{args.issue}"
status: candidate
recommendation: pending
branch: null
pull_request: null
last_verified: "{date.today().isoformat()}"
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
