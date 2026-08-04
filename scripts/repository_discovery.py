#!/usr/bin/env python3
"""Discover configured target repositories from local Git remotes."""

from __future__ import annotations

import argparse
import os
from pathlib import Path
import subprocess
from typing import Any

import yaml


ROOT = Path(__file__).resolve().parents[1]
REGISTRY_PATH = ROOT / "repositories" / "registry.yaml"
DISCOVERY_PATH = ROOT / "repositories" / "discovery.yaml"


def load_documents(
    registry_path: Path = REGISTRY_PATH,
    discovery_path: Path = DISCOVERY_PATH,
) -> tuple[dict[str, Any], dict[str, Any]]:
    with registry_path.open(encoding="utf-8") as stream:
        registry = yaml.safe_load(stream) or {}
    with discovery_path.open(encoding="utf-8") as stream:
        discovery = yaml.safe_load(stream) or {}
    return registry, discovery


def canonical_remote(url: str) -> str:
    """Return ``owner/name`` for common HTTPS and SCP-style GitHub URLs."""
    value = url.strip()
    if value.endswith(".git"):
        value = value[:-4]
    if value.startswith("git@") and ":" in value:
        value = value.split(":", 1)[1]
    elif "://" in value:
        value = value.split("://", 1)[1]
        value = value.split("/", 1)[1] if "/" in value else value
    parts = [part for part in value.rstrip("/").split("/") if part]
    return "/".join(parts[-2:]) if len(parts) >= 2 else ""


def git_remotes(path: Path) -> dict[str, str]:
    completed = subprocess.run(
        ["git", "-C", str(path), "remote", "-v"],
        check=True,
        capture_output=True,
        text=True,
    )
    remotes: dict[str, str] = {}
    for line in completed.stdout.splitlines():
        fields = line.split()
        if len(fields) >= 2:
            remotes.setdefault(fields[0], fields[1])
    return remotes


def git_identity(path: Path) -> dict[str, str | None]:
    """Read the local repository Git identity without changing configuration."""
    identity: dict[str, str | None] = {}
    for key in ("user.name", "user.email"):
        completed = subprocess.run(
            ["git", "-C", str(path), "config", "--get", key],
            check=False,
            capture_output=True,
            text=True,
        )
        identity[key.removeprefix("user.")] = completed.stdout.strip() or None
    return identity


def identity_matches(path: Path, expected: dict[str, Any]) -> bool:
    actual = git_identity(path)
    return actual.get("name") == expected.get("name") and actual.get("email") == expected.get("email")


def find_git_repositories(roots: list[Path]) -> list[Path]:
    found: set[Path] = set()
    for root in roots:
        if not root.is_dir():
            continue
        for current, directories, _ in os.walk(root):
            current_path = Path(current)
            if ".git" in directories or (current_path / ".git").is_file():
                found.add(current_path)
                directories[:] = []
            else:
                directories[:] = sorted(
                    directory for directory in directories if directory != ".git"
                )
    return sorted(found)


def discover(
    registry: dict[str, Any],
    discovery: dict[str, Any],
    *,
    home: Path | None = None,
) -> list[dict[str, str | None]]:
    home_path = home or Path.home()
    roots = [home_path / relative for relative in discovery.get("scan_roots", [])]
    local_repositories: list[tuple[Path, dict[str, str]]] = []
    for path in find_git_repositories(roots):
        try:
            local_repositories.append((path, git_remotes(path)))
        except (OSError, subprocess.CalledProcessError):
            continue

    results: list[dict[str, str | None]] = []
    for repository, configuration in registry.get("repositories", {}).items():
        upstream_url = configuration.get("upstream", {}).get("url")
        upstream_name = canonical_remote(upstream_url or repository)
        for path, remotes in local_repositories:
            matching = [
                (remote, url)
                for remote, url in remotes.items()
                if canonical_remote(url) == upstream_name
                or canonical_remote(url).split("/", 1)[-1]
                == repository.split("/", 1)[-1]
            ]
            if not matching:
                continue
            fork = next(
                (
                    url
                    for remote, url in matching
                    if remote == "origin" and canonical_remote(url) != upstream_name
                ),
                None,
            )
            results.append(
                {
                    "repository": repository,
                    "upstream": upstream_url,
                    "fork": fork,
                    "local_path": str(path),
                }
            )
            break
    return results


def print_results(results: list[dict[str, str | None]]) -> None:
    for result in results:
        print(result["repository"])
        print(f"upstream:\n{result['upstream']}")
        print(f"fork:\n{result['fork'] or ''}")
        print(f"local:\n{result['local_path']}")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    subparsers = parser.add_subparsers(dest="command", required=True)
    subparsers.add_parser("list", help="list discovered target repositories")
    args = parser.parse_args()
    if args.command == "list":
        registry, discovery = load_documents()
        print_results(discover(registry, discovery))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
