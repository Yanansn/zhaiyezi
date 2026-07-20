#!/usr/bin/env python3
"""Initialize a lightweight zhaiyezi candidate-screening record."""

from __future__ import annotations

import argparse
import re
from pathlib import Path


REPOSITORY_RE = re.compile(r"^(?P<owner>[^/\s]+)/(?P<repo>[^/\s]+)$")
SCAN_ID_RE = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._-]*$")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--repository", required=True, help="repository as owner/name")
    parser.add_argument("--scan-id", required=True, help="bounded scan identifier")
    parser.add_argument("--candidate-limit", required=True, type=int)
    parser.add_argument(
        "--screenings-root",
        type=Path,
        default=Path(__file__).resolve().parents[1] / "screenings",
        help="directory in which screening records are created",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    repository_match = REPOSITORY_RE.fullmatch(args.repository)
    if not repository_match:
        raise SystemExit("repository must use owner/name")
    if not SCAN_ID_RE.fullmatch(args.scan_id):
        raise SystemExit("scan-id may contain only letters, digits, dot, underscore, and hyphen")
    if args.candidate_limit < 1:
        raise SystemExit("candidate-limit must be a positive integer")

    repository_root = Path(__file__).resolve().parents[1]
    template_root = repository_root / "templates" / "screening"
    if not template_root.is_dir():
        raise SystemExit(f"screening templates not found: {template_root}")

    parts = repository_match.groupdict()
    repository_slug = f"{parts['owner']}-{parts['repo']}"
    destination = args.screenings_root.resolve() / repository_slug / args.scan_id
    if destination.exists():
        raise SystemExit(f"refusing to overwrite existing record: {destination}")

    replacements = {
        "{{REPOSITORY}}": args.repository,
        "{{SCAN_ID}}": args.scan_id,
        "{{CANDIDATE_LIMIT}}": str(args.candidate_limit),
    }
    destination.mkdir(parents=True)
    try:
        for template in sorted(template_root.iterdir()):
            if not template.is_file():
                continue
            content = template.read_text(encoding="utf-8")
            for marker, value in replacements.items():
                content = content.replace(marker, value)
            (destination / template.name).write_text(content, encoding="utf-8")
    except Exception:
        for generated in destination.iterdir():
            generated.unlink()
        destination.rmdir()
        raise

    print(destination)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
