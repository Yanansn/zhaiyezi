#!/usr/bin/env python3
"""Initialize a zhaiyezi issue record from the repository templates."""

from __future__ import annotations

import argparse
import re
import shutil
from pathlib import Path


ISSUE_RE = re.compile(r"^(?P<owner>[^/]+)/(?P<repo>[^#]+)#(?P<number>[1-9][0-9]*)$")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("issue", help="issue identifier, for example owner/repository#123")
    parser.add_argument("--title", default="", help="upstream issue title")
    parser.add_argument(
        "--issues-root",
        type=Path,
        default=Path(__file__).resolve().parents[1] / "issues",
        help="directory in which the issue record directory is created",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    match = ISSUE_RE.fullmatch(args.issue)
    if not match:
        raise SystemExit("issue must use owner/repository#number")

    values = match.groupdict()
    values["issue"] = args.issue
    values["title"] = args.title or "TODO: record the upstream issue title"
    values["record_slug"] = f"{values['owner']}-{values['repo']}-{values['number']}"

    repository_root = Path(__file__).resolve().parents[1]
    template_root = repository_root / "templates" / "issue-record"
    destination = args.issues_root.resolve() / values["record_slug"]
    if destination.exists():
        raise SystemExit(f"refusing to overwrite existing record: {destination}")

    destination.mkdir(parents=True)
    replacements = {f"{{{{{key.upper()}}}}}": value for key, value in values.items()}
    for template in sorted(template_root.iterdir()):
        if not template.is_file():
            continue
        content = template.read_text(encoding="utf-8")
        for marker, value in replacements.items():
            content = content.replace(marker, value)
        (destination / template.name).write_text(content, encoding="utf-8")

    print(destination)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
