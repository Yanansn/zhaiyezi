#!/usr/bin/env python3
"""Discover unassigned GitHub issues and collect known related-PR evidence."""

from __future__ import annotations

import argparse
import json
import os
import re
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Callable, Iterable, Protocol


API_VERSION = "2026-03-10"
DEFAULT_API_URL = "https://api.github.com"
REPOSITORY_RE = re.compile(
    r"^(?P<owner>[A-Za-z0-9_.-]+)/(?P<repo>[A-Za-z0-9_.-]+)$"
)
PR_URL_RE = re.compile(
    r"https://github\.com/(?P<owner>[A-Za-z0-9_.-]+)/"
    r"(?P<repo>[A-Za-z0-9_.-]+)/pull/(?P<number>[1-9][0-9]*)"
)
FULL_REFERENCE_RE = re.compile(
    r"(?<![A-Za-z0-9_.-])(?P<owner>[A-Za-z0-9_.-]+)/"
    r"(?P<repo>[A-Za-z0-9_.-]+)#(?P<number>[1-9][0-9]*)"
)
LOCAL_REFERENCE_RE = re.compile(r"(?<![A-Za-z0-9_])#(?P<number>[1-9][0-9]*)")
COMMIT_API_RE = re.compile(
    r"https://api\.github\.com/repos/(?P<owner>[^/]+)/(?P<repo>[^/]+)/"
    r"commits/(?P<sha>[0-9a-fA-F]+)"
)
REFERENCE_EXPRESSIONS = (
    "#{number}",
    "Fixes #{number}",
    "Closes #{number}",
    "Related-to #{number}",
    "Refs #{number}",
)


class GitHubError(RuntimeError):
    """A safe-to-display GitHub API error."""


class GitHubAuthorizationError(GitHubError):
    """A credential or organization-policy error that invalidates the scan."""


class GitHubAPI(Protocol):
    def get(self, path: str, params: dict[str, Any] | None = None) -> Any: ...

    def paginate(
        self, path: str, params: dict[str, Any] | None = None
    ) -> list[Any]: ...


@dataclass(frozen=True, order=True)
class ItemReference:
    owner: str
    repo: str
    number: int

    @property
    def repository(self) -> str:
        return f"{self.owner}/{self.repo}"

    @property
    def key(self) -> str:
        return f"{self.repository}#{self.number}"


class GitHubClient:
    """Small versioned REST client with bounded retries and pagination."""

    def __init__(
        self,
        token: str,
        *,
        api_url: str = DEFAULT_API_URL,
        timeout: float = 20.0,
        max_retries: int = 2,
        opener: Callable[..., Any] = urllib.request.urlopen,
        sleeper: Callable[[float], None] = time.sleep,
    ) -> None:
        self._token = token
        self._api_url = api_url.rstrip("/")
        self._timeout = timeout
        self._max_retries = max_retries
        self._opener = opener
        self._sleeper = sleeper
        self.rate_limit: dict[str, dict[str, str]] = {}

    def get(self, path: str, params: dict[str, Any] | None = None) -> Any:
        data, _ = self._request(path, params)
        return data

    def paginate(
        self, path: str, params: dict[str, Any] | None = None
    ) -> list[Any]:
        page = 1
        values: list[Any] = []
        while True:
            query = dict(params or {})
            query.update({"per_page": 100, "page": page})
            data, headers = self._request(path, query)
            if not isinstance(data, list):
                raise GitHubError(f"GitHub returned a non-list response for {path}")
            values.extend(data)
            if len(data) < 100 or not _has_next_link(headers.get("Link", "")):
                return values
            page += 1

    def _request(
        self, path: str, params: dict[str, Any] | None
    ) -> tuple[Any, Any]:
        encoded = urllib.parse.urlencode(params or {}, doseq=True)
        url = f"{self._api_url}{path}"
        if encoded:
            url = f"{url}?{encoded}"
        request = urllib.request.Request(
            url,
            headers={
                "Accept": "application/vnd.github+json",
                "Authorization": f"Bearer {self._token}",
                "User-Agent": "zhaiyezi-issue-discovery",
                "X-GitHub-Api-Version": API_VERSION,
            },
        )

        for attempt in range(self._max_retries + 1):
            try:
                with self._opener(request, timeout=self._timeout) as response:
                    body = response.read().decode("utf-8")
                    self._record_rate_limit(response.headers)
                    return json.loads(body), response.headers
            except urllib.error.HTTPError as error:
                self._record_rate_limit(error.headers)
                retryable = (
                    error.code == 429
                    or (error.code == 403 and error.headers.get("Retry-After") is not None)
                    or 500 <= error.code < 600
                )
                if retryable and attempt < self._max_retries:
                    self._sleeper(_retry_delay(error.headers, attempt))
                    continue
                message = _github_error_message(error)
                error_type = (
                    GitHubAuthorizationError
                    if error.code in {401, 403} and not retryable
                    else GitHubError
                )
                raise error_type(
                    f"GitHub API {error.code} for {path}: {message}"
                ) from None
            except (urllib.error.URLError, TimeoutError) as error:
                if attempt < self._max_retries:
                    self._sleeper(2**attempt)
                    continue
                raise GitHubError(f"GitHub request failed for {path}: {error}") from None
            except (UnicodeError, json.JSONDecodeError) as error:
                raise GitHubError(f"GitHub returned invalid JSON for {path}: {error}") from None
        raise AssertionError("retry loop exhausted without returning")

    def _record_rate_limit(self, headers: Any) -> None:
        resource = str(headers.get("X-RateLimit-Resource") or "unknown")
        values = self.rate_limit.setdefault(resource, {})
        for header, output_key in (
            ("X-RateLimit-Limit", "limit"),
            ("X-RateLimit-Remaining", "remaining"),
            ("X-RateLimit-Reset", "reset"),
            ("X-RateLimit-Resource", "resource"),
        ):
            value = headers.get(header)
            if value is not None:
                values[output_key] = str(value)


def _retry_delay(headers: Any, attempt: int) -> float:
    retry_after = headers.get("Retry-After")
    if retry_after:
        try:
            return min(float(retry_after), 10.0)
        except ValueError:
            pass
    return float(2**attempt)


def _github_error_message(error: urllib.error.HTTPError) -> str:
    try:
        payload = json.loads(error.read().decode("utf-8"))
        message = payload.get("message")
        if isinstance(message, str) and message:
            return message
    except (UnicodeError, json.JSONDecodeError, OSError):
        pass
    return error.reason or "request failed"


def _has_next_link(link_header: str) -> bool:
    return any('rel="next"' in part for part in link_header.split(","))


def _repository_path(repository: str) -> str:
    owner, repo = repository.split("/", 1)
    return f"/repos/{urllib.parse.quote(owner)}/{urllib.parse.quote(repo)}"


def _labels(item: dict[str, Any]) -> list[str]:
    labels: list[str] = []
    for label in item.get("labels") or []:
        if isinstance(label, str):
            labels.append(label)
        elif isinstance(label, dict) and isinstance(label.get("name"), str):
            labels.append(label["name"])
    return labels


def _build_discovery_query(
    repository: str, include_labels: Iterable[str], exclude_labels: Iterable[str]
) -> str:
    parts = [f"repo:{repository}", "is:issue", "is:open", "no:assignee"]
    parts.extend(f'label:"{label}"' for label in include_labels)
    parts.extend(f'-label:"{label}"' for label in exclude_labels)
    return " ".join(parts)


def discover_issues(
    api: GitHubAPI,
    repository: str,
    limit: int,
    include_labels: list[str],
    exclude_labels: list[str],
) -> tuple[list[dict[str, Any]], int, list[str]]:
    query = _build_discovery_query(repository, include_labels, exclude_labels)
    issues: list[dict[str, Any]] = []
    total_count = 0
    limitations: list[str] = []
    page = 1
    seen = 0
    page_size = min(100, limit)
    while len(issues) < limit:
        data = api.get(
            "/search/issues",
            {
                "q": query,
                "sort": "created",
                "order": "desc",
                "per_page": page_size,
                "page": page,
            },
        )
        if not isinstance(data, dict) or not isinstance(data.get("items"), list):
            raise GitHubError("GitHub returned an invalid issue-search response")
        if page == 1:
            total_count = int(data.get("total_count") or 0)
        if data.get("incomplete_results"):
            limitations.append("GitHub marked the candidate search as incomplete.")
        seen += len(data["items"])
        batch = [
            item
            for item in data["items"]
            if "pull_request" not in item and not item.get("assignees")
        ]
        issues.extend(batch[: limit - len(issues)])
        if len(data["items"]) == 0 or seen >= total_count:
            break
        page += 1
    return issues, total_count, limitations


def verify_repository_access(api: GitHubAPI, repository: str) -> None:
    data = api.get(_repository_path(repository))
    if not isinstance(data, dict) or not isinstance(data.get("full_name"), str):
        raise GitHubError("GitHub returned invalid repository metadata")
    if data["full_name"].casefold() != repository.casefold():
        raise GitHubError(
            f"GitHub resolved {repository} as unexpected repository {data['full_name']}"
        )


def _reference_from_issue_object(value: Any) -> ItemReference | None:
    if not isinstance(value, dict) or "pull_request" not in value:
        return None
    repository_url = value.get("repository_url")
    number = value.get("number")
    if not isinstance(repository_url, str) or not isinstance(number, int):
        return None
    match = re.search(r"/repos/([^/]+)/([^/]+)$", repository_url)
    if not match:
        return None
    return ItemReference(match.group(1), match.group(2), number)


def _reference_from_pull_object(value: Any) -> ItemReference | None:
    reference = _reference_from_issue_object(value)
    if reference:
        return reference
    if not isinstance(value, dict) or not isinstance(value.get("number"), int):
        return None
    html_url = value.get("html_url")
    if isinstance(html_url, str):
        match = PR_URL_RE.fullmatch(html_url.rstrip("/"))
        if match:
            return ItemReference(
                match.group("owner"), match.group("repo"), int(match.group("number"))
            )
    full_name = ((value.get("base") or {}).get("repo") or {}).get("full_name")
    if isinstance(full_name, str) and REPOSITORY_RE.fullmatch(full_name):
        owner, repo = full_name.split("/", 1)
        return ItemReference(owner, repo, value["number"])
    return None


def references_from_text(text: str, repository: str) -> set[ItemReference]:
    references = {
        ItemReference(match.group("owner"), match.group("repo"), int(match.group("number")))
        for match in PR_URL_RE.finditer(text)
    }
    references.update(
        ItemReference(match.group("owner"), match.group("repo"), int(match.group("number")))
        for match in FULL_REFERENCE_RE.finditer(text)
    )
    owner, repo = repository.split("/", 1)
    references.update(
        ItemReference(owner, repo, int(match.group("number")))
        for match in LOCAL_REFERENCE_RE.finditer(text)
    )
    return references


def _add_source(
    sources: dict[ItemReference, list[dict[str, str]]],
    reference: ItemReference,
    kind: str,
    detail: str,
) -> None:
    source = {"kind": kind, "detail": detail}
    values = sources.setdefault(reference, [])
    if source not in values:
        values.append(source)


def _timeline_sources(
    events: list[Any], repository: str
) -> tuple[
    dict[ItemReference, list[dict[str, str]]], list[tuple[str, str]], list[str]
]:
    sources: dict[ItemReference, list[dict[str, str]]] = {}
    commits: list[tuple[str, str]] = []
    limitations: list[str] = []
    for event in events:
        if not isinstance(event, dict):
            continue
        event_name = str(event.get("event") or "")
        if event_name == "cross-referenced":
            reference = _reference_from_issue_object(
                (event.get("source") or {}).get("issue")
                if isinstance(event.get("source"), dict)
                else None
            )
            if reference:
                _add_source(sources, reference, "timeline-cross-reference", event_name)
        elif event_name == "connected":
            connected_reference_found = False
            for key in ("subject", "source"):
                candidate = event.get(key)
                if isinstance(candidate, dict) and "issue" in candidate:
                    candidate = candidate["issue"]
                reference = _reference_from_issue_object(candidate)
                if reference:
                    _add_source(sources, reference, "timeline-connected", event_name)
                    connected_reference_found = True
            if not connected_reference_found:
                limitations.append(
                    "A connected Timeline event did not expose its linked target."
                )
        if event_name in {"referenced", "closed"}:
            commit_url = event.get("commit_url")
            commit_id = event.get("commit_id")
            if isinstance(commit_url, str) and isinstance(commit_id, str):
                commits.append((commit_url, event_name))
        if event_name == "commented" and isinstance(event.get("body"), str):
            for reference in references_from_text(event["body"], repository):
                _add_source(sources, reference, "issue-comment", event.get("html_url", ""))
    return sources, commits, limitations


def _commit_pr_sources(
    api: GitHubAPI,
    commits: list[tuple[str, str]],
    sources: dict[ItemReference, list[dict[str, str]]],
    limitations: list[str],
) -> None:
    for commit_url, event_name in sorted(set(commits)):
        match = COMMIT_API_RE.fullmatch(commit_url)
        if not match:
            limitations.append(f"Could not parse referenced commit URL: {commit_url}")
            continue
        path = (
            f"/repos/{match.group('owner')}/{match.group('repo')}/"
            f"commits/{match.group('sha')}/pulls"
        )
        try:
            pulls = api.paginate(path)
        except GitHubAuthorizationError:
            raise
        except GitHubError as error:
            limitations.append(str(error))
            continue
        for pull in pulls:
            reference = _reference_from_pull_object(pull)
            if reference:
                _add_source(
                    sources,
                    reference,
                    "timeline-commit",
                    f"{event_name}:{match.group('sha')}",
                )


def _comment_sources(
    api: GitHubAPI,
    repository: str,
    issue_number: int,
    sources: dict[ItemReference, list[dict[str, str]]],
    limitations: list[str],
) -> None:
    path = f"{_repository_path(repository)}/issues/{issue_number}/comments"
    try:
        comments = api.paginate(path)
    except GitHubAuthorizationError:
        raise
    except GitHubError as error:
        limitations.append(str(error))
        return
    for comment in comments:
        if not isinstance(comment, dict) or not isinstance(comment.get("body"), str):
            continue
        for reference in references_from_text(comment["body"], repository):
            _add_source(
                sources,
                reference,
                "issue-comment",
                str(comment.get("html_url") or ""),
            )


def _search_sources(
    api: GitHubAPI,
    repository: str,
    issue_number: int,
    sources: dict[ItemReference, list[dict[str, str]]],
    limitations: list[str],
) -> None:
    reference_query = f"#{issue_number}"
    covered_expressions = ", ".join(
        template.format(number=issue_number) for template in REFERENCE_EXPRESSIONS
    )
    query = f'repo:{repository} is:pr in:body,comments "{reference_query}"'
    try:
        data = api.get(
            "/search/issues",
            {"q": query, "sort": "updated", "order": "desc", "per_page": 100},
        )
    except GitHubAuthorizationError:
        raise
    except GitHubError as error:
        limitations.append(f"Reference search {reference_query!r} failed: {error}")
        return
    if not isinstance(data, dict) or not isinstance(data.get("items"), list):
        limitations.append(f"Reference search {reference_query!r} returned invalid data.")
        return
    if data.get("incomplete_results"):
        limitations.append(f"Reference search {reference_query!r} was incomplete.")
    for item in data["items"]:
        reference = _reference_from_issue_object(item)
        if reference:
            _add_source(
                sources,
                reference,
                "reference-search",
                f"broad {reference_query} search; covered expressions: {covered_expressions}",
            )
    if int(data.get("total_count") or 0) > len(data["items"]):
        limitations.append(
            f"Reference search {reference_query!r} exceeded its 100-result evidence cap."
        )


def _resolve_reference(
    api: GitHubAPI,
    reference: ItemReference,
    sources: list[dict[str, str]],
) -> dict[str, Any] | None:
    try:
        issue_like = api.get(
            f"{_repository_path(reference.repository)}/issues/{reference.number}"
        )
    except GitHubError:
        raise
    if not isinstance(issue_like, dict) or "pull_request" not in issue_like:
        return None
    pull = api.get(f"{_repository_path(reference.repository)}/pulls/{reference.number}")
    if not isinstance(pull, dict):
        raise GitHubError(f"GitHub returned invalid PR data for {reference.key}")
    return {
        "pr": reference.key,
        "url": pull.get("html_url") or issue_like.get("html_url"),
        "title": pull.get("title") or issue_like.get("title"),
        "state": pull.get("state") or issue_like.get("state"),
        "draft": bool(pull.get("draft")),
        "merged": pull.get("merged_at") is not None,
        "merged_at": pull.get("merged_at"),
        "base": (pull.get("base") or {}).get("ref"),
        "head": (pull.get("head") or {}).get("ref"),
        "relationship": "unclassified",
        "sources": sources,
    }


def audit_issue(
    api: GitHubAPI, repository: str, issue: dict[str, Any]
) -> dict[str, Any]:
    number = int(issue["number"])
    limitations: list[str] = []
    sources: dict[ItemReference, list[dict[str, str]]] = {}

    try:
        timeline = api.paginate(
            f"{_repository_path(repository)}/issues/{number}/timeline"
        )
    except GitHubAuthorizationError:
        raise
    except GitHubError as error:
        timeline = []
        limitations.append(str(error))
    if len(timeline) >= 300:
        limitations.append(
            "The GitHub Timeline API may cap results at 300 events; completeness is uncertain."
        )
    timeline_sources, commits, timeline_limitations = _timeline_sources(
        timeline, repository
    )
    limitations.extend(timeline_limitations)
    for reference, values in timeline_sources.items():
        for value in values:
            _add_source(sources, reference, value["kind"], value["detail"])
    _commit_pr_sources(api, commits, sources, limitations)
    if isinstance(issue.get("body"), str):
        for reference in references_from_text(issue["body"], repository):
            _add_source(sources, reference, "issue-body", str(issue.get("html_url") or ""))
    _comment_sources(api, repository, number, sources, limitations)
    _search_sources(api, repository, number, sources, limitations)

    related_prs: list[dict[str, Any]] = []
    for reference in sorted(sources):
        try:
            resolved = _resolve_reference(api, reference, sources[reference])
        except GitHubAuthorizationError:
            raise
        except GitHubError as error:
            limitations.append(f"Could not verify {reference.key}: {error}")
            continue
        if resolved:
            related_prs.append(resolved)

    if related_prs:
        status = "related_pr_found"
    elif limitations:
        status = "insufficient_evidence"
    else:
        status = "no_known_related_pr"
    return {
        "issue": f"{repository}#{number}",
        "url": issue.get("html_url"),
        "title": issue.get("title"),
        "created_at": issue.get("created_at"),
        "updated_at": issue.get("updated_at"),
        "labels": _labels(issue),
        "assignees": [
            assignee.get("login")
            for assignee in issue.get("assignees") or []
            if isinstance(assignee, dict) and assignee.get("login")
        ],
        "related_pr_status": status,
        "related_pr_evidence": related_prs,
        "limitations": sorted(set(limitations)),
    }


def run_discovery(
    api: GitHubAPI,
    repository: str,
    limit: int,
    include_labels: list[str],
    exclude_labels: list[str],
    progress: Callable[[str], None] | None = None,
) -> dict[str, Any]:
    notify = progress or (lambda _: None)
    notify(f"Checking read access to {repository}...")
    verify_repository_access(api, repository)
    notify(f"Searching for up to {limit} open, unassigned Issues...")
    issues, total_count, scan_limitations = discover_issues(
        api, repository, limit, include_labels, exclude_labels
    )
    notify(f"Found {len(issues)} candidates ({total_count} total query matches).")
    results: list[dict[str, Any]] = []
    for index, issue in enumerate(issues, start=1):
        issue_name = f"{repository}#{issue['number']}"
        notify(f"[{index}/{len(issues)}] Inspecting {issue_name}...")
        result = audit_issue(api, repository, issue)
        results.append(result)
        notify(f"[{index}/{len(issues)}] {issue_name}: {result['related_pr_status']}")
    counts = {
        status: sum(1 for issue in results if issue["related_pr_status"] == status)
        for status in (
            "related_pr_found",
            "no_known_related_pr",
            "insufficient_evidence",
        )
    }
    output: dict[str, Any] = {
        "schema_version": 1,
        "repository": repository,
        "generated_at": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
        "query": {
            "state": "open",
            "assignee": "none",
            "candidate_limit": limit,
            "include_labels": include_labels,
            "exclude_labels": exclude_labels,
        },
        "summary": {
            "matched_total": total_count,
            "inspected": len(results),
            **counts,
        },
        "limitations": scan_limitations,
        "issues": results,
    }
    rate_limit = getattr(api, "rate_limit", None)
    if rate_limit:
        output["rate_limit"] = rate_limit
    return output


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Find bounded open, unassigned Issues and collect known related-PR evidence."
        )
    )
    parser.add_argument("--repository", required=True, help="repository as owner/name")
    parser.add_argument("--limit", required=True, type=int, help="Issues to inspect (1-1000)")
    parser.add_argument(
        "--include-label", action="append", default=[], help="required label; repeatable"
    )
    parser.add_argument(
        "--exclude-label", action="append", default=[], help="excluded label; repeatable"
    )
    parser.add_argument(
        "--output", default="-", help="JSON output path, or - for standard output"
    )
    parser.add_argument(
        "--chat-output",
        help="compact candidate Markdown path, or - for standard output",
    )
    parser.add_argument("--timeout", type=float, default=20.0, help="request timeout seconds")
    parser.add_argument("--max-retries", type=int, default=2, help="bounded retry count")
    parser.add_argument(
        "--quiet", action="store_true", help="suppress progress messages on standard error"
    )
    return parser.parse_args(argv)


def _validate_args(args: argparse.Namespace) -> None:
    if not REPOSITORY_RE.fullmatch(args.repository):
        raise SystemExit("repository must use owner/name")
    if not 1 <= args.limit <= 1000:
        raise SystemExit("limit must be between 1 and 1000")
    if args.timeout <= 0:
        raise SystemExit("timeout must be positive")
    if not 0 <= args.max_retries <= 5:
        raise SystemExit("max-retries must be between 0 and 5")
    if args.output == "-" and args.chat_output == "-":
        raise SystemExit("JSON output and chat output cannot both use standard output")
    if any(not label.strip() for label in (*args.include_label, *args.exclude_label)):
        raise SystemExit("labels must not be empty")
    overlap = set(args.include_label) & set(args.exclude_label)
    if overlap:
        raise SystemExit(
            "labels cannot be both included and excluded: " + ", ".join(sorted(overlap))
        )


def render_chat_summary(output: dict[str, Any]) -> str:
    summary = output["summary"]
    query = output["query"]
    candidates = [
        issue
        for issue in output["issues"]
        if issue["related_pr_status"] == "no_known_related_pr"
    ]
    include_labels = ", ".join(query["include_labels"]) or "none"
    exclude_labels = ", ".join(query["exclude_labels"]) or "none"
    lines = [
        "# GitHub Issue Candidate Discovery",
        "",
        f"- Repository: `{output['repository']}`",
        f"- Generated: `{output['generated_at']}`",
        (
            f"- Scope: open, unassigned, latest {query['candidate_limit']}; "
            f"include labels: {include_labels}; exclude labels: {exclude_labels}"
        ),
        (
            f"- Query matches: {summary['matched_total']}; inspected: "
            f"{summary['inspected']}"
        ),
        (
            f"- Results: {len(candidates)} candidates without known PR evidence; "
            f"{summary['related_pr_found']} with PR evidence; "
            f"{summary['insufficient_evidence']} insufficient-evidence"
        ),
        "",
        f"## Candidate Issues ({len(candidates)})",
        "",
    ]
    if candidates:
        for issue in candidates:
            title = " ".join(str(issue.get("title") or "").split())
            labels = ", ".join(issue.get("labels") or []) or "none"
            lines.append(
                f"- [{issue['issue']}]({issue['url']}) — {title} — labels: {labels}"
            )
    else:
        lines.append("- None.")
    lines.extend(
        [
            "",
            "## Interpretation",
            "",
            (
                "This is Candidate Discovery evidence only. `no_known_related_pr` "
                "does not mean `available`; Chat must continue Deep Audit, ownership, "
                "semantic PR, design, and feasibility checks."
            ),
        ]
    )
    limitations = output.get("limitations") or []
    if limitations:
        lines.extend(["", "Top-level limitations: " + "; ".join(limitations)])
    return "\n".join(lines) + "\n"


def _write_text(rendered: str, destination: str) -> None:
    if destination == "-":
        sys.stdout.write(rendered)
        return
    path = Path(destination)
    temporary = path.with_name(f".{path.name}.tmp")
    try:
        temporary.write_text(rendered, encoding="utf-8")
        temporary.replace(path)
    except Exception:
        temporary.unlink(missing_ok=True)
        raise


def _write_output(output: dict[str, Any], destination: str) -> None:
    rendered = json.dumps(output, ensure_ascii=False, indent=2) + "\n"
    _write_text(rendered, destination)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    _validate_args(args)
    token = os.environ.get("GITHUB_TOKEN")
    if not token:
        print("ERROR: GITHUB_TOKEN is required", file=sys.stderr)
        return 2
    client = GitHubClient(
        token,
        timeout=args.timeout,
        max_retries=args.max_retries,
    )
    progress = None if args.quiet else lambda message: print(message, file=sys.stderr)
    try:
        output = run_discovery(
            client,
            args.repository,
            args.limit,
            args.include_label,
            args.exclude_label,
            progress,
        )
        _write_output(output, args.output)
        if args.chat_output:
            _write_text(render_chat_summary(output), args.chat_output)
    except (GitHubError, OSError) as error:
        print(f"ERROR: {error}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
