from __future__ import annotations

import io
import json
import tempfile
import time
import unittest
import urllib.error
import urllib.parse
from pathlib import Path
from typing import Any
from unittest import mock

from scripts import discover_github_issues as discovery


REPOSITORY = "example/project"


def issue(number: int, *, body: str = "", assignees: list[dict[str, str]] | None = None) -> dict:
    return {
        "number": number,
        "html_url": f"https://github.com/{REPOSITORY}/issues/{number}",
        "repository_url": f"https://api.github.com/repos/{REPOSITORY}",
        "title": f"Issue {number}",
        "body": body,
        "state": "open",
        "created_at": "2026-07-01T00:00:00Z",
        "updated_at": "2026-07-02T00:00:00Z",
        "labels": [{"name": "help wanted"}],
        "assignees": [] if assignees is None else assignees,
    }


def pr_item(repository: str, number: int) -> dict:
    return {
        "number": number,
        "repository_url": f"https://api.github.com/repos/{repository}",
        "html_url": f"https://github.com/{repository}/pull/{number}",
        "title": f"PR {number}",
        "state": "open",
        "pull_request": {"url": f"https://api.github.com/repos/{repository}/pulls/{number}"},
    }


def pr_detail(repository: str, number: int, *, merged: bool = False) -> dict:
    return {
        "number": number,
        "html_url": f"https://github.com/{repository}/pull/{number}",
        "title": f"PR {number}",
        "state": "closed" if merged else "open",
        "draft": False,
        "merged_at": "2026-07-03T00:00:00Z" if merged else None,
        "base": {"ref": "main", "repo": {"full_name": repository}},
        "head": {"ref": f"fix-{number}"},
    }


class FakeAPI:
    def __init__(self) -> None:
        self.issue_search_pages: dict[int, dict[str, Any]] = {
            1: {"total_count": 0, "incomplete_results": False, "items": []}
        }
        self.pr_search_results: dict[str, list[dict[str, Any]]] = {}
        self.issue_objects: dict[str, dict[str, Any]] = {}
        self.pull_objects: dict[str, dict[str, Any]] = {}
        self.paginated: dict[str, list[Any]] = {}
        self.fail_get: set[str] = set()
        self.fail_paginate: set[str] = set()
        self.auth_fail_get: set[str] = set()
        self.auth_fail_paginate: set[str] = set()
        self.calls: list[tuple[str, str, dict[str, Any]]] = []
        self.rate_limit = {"remaining": "4999"}

    def get(self, path: str, params: dict[str, Any] | None = None) -> Any:
        params = params or {}
        self.calls.append(("get", path, params))
        if path in self.auth_fail_get:
            raise discovery.GitHubAuthorizationError(f"forced authorization failure for {path}")
        if path in self.fail_get:
            raise discovery.GitHubError(f"forced GET failure for {path}")
        if path == f"/repos/{REPOSITORY}":
            return {"full_name": REPOSITORY}
        if path == "/search/issues":
            query = str(params.get("q") or "")
            if "is:issue" in query:
                return self.issue_search_pages.get(
                    int(params.get("page") or 1),
                    {"total_count": 0, "incomplete_results": False, "items": []},
                )
            matches = [
                item
                for needle, items in self.pr_search_results.items()
                if needle in query
                for item in items
            ]
            return {"total_count": len(matches), "incomplete_results": False, "items": matches}
        if "/pulls/" in path:
            return self.pull_objects[path]
        if "/issues/" in path:
            return self.issue_objects[path]
        raise AssertionError(f"unexpected GET {path} {params}")

    def paginate(self, path: str, params: dict[str, Any] | None = None) -> list[Any]:
        self.calls.append(("paginate", path, params or {}))
        if path in self.auth_fail_paginate:
            raise discovery.GitHubAuthorizationError(
                f"forced authorization failure for {path}"
            )
        if path in self.fail_paginate:
            raise discovery.GitHubError(f"forced pagination failure for {path}")
        return self.paginated.get(path, [])

    def add_pr(self, repository: str, number: int, *, merged: bool = False) -> None:
        repository_path = f"/repos/{repository}"
        self.issue_objects[f"{repository_path}/issues/{number}"] = pr_item(repository, number)
        self.pull_objects[f"{repository_path}/pulls/{number}"] = pr_detail(
            repository, number, merged=merged
        )


class FakeResponse:
    def __init__(self, payload: Any, headers: dict[str, str] | None = None) -> None:
        self._body = json.dumps(payload).encode()
        self.headers = headers or {}

    def __enter__(self) -> "FakeResponse":
        return self

    def __exit__(self, *args: object) -> None:
        return None

    def read(self) -> bytes:
        return self._body


class DiscoveryTests(unittest.TestCase):
    def test_reference_parser_handles_urls_cross_repo_and_local_refs(self) -> None:
        references = discovery.references_from_text(
            "See https://github.com/acme/widgets/pull/7, acme/other#8, and #9.",
            REPOSITORY,
        )
        self.assertEqual(
            {
                discovery.ItemReference("acme", "widgets", 7),
                discovery.ItemReference("acme", "other", 8),
                discovery.ItemReference("example", "project", 9),
            },
            references,
        )

    def test_discovery_query_and_local_filter_keep_only_unassigned_issues(self) -> None:
        api = FakeAPI()
        assigned = issue(2, assignees=[{"login": "owner"}])
        pull = pr_item(REPOSITORY, 3)
        api.issue_search_pages[1] = {
            "total_count": 3,
            "incomplete_results": False,
            "items": [issue(1), assigned, pull],
        }
        issues, total, limitations = discovery.discover_issues(
            api, REPOSITORY, 3, ["help wanted"], ["kind/feature"]
        )
        self.assertEqual([1], [item["number"] for item in issues])
        self.assertEqual(3, total)
        self.assertEqual([], limitations)
        query = api.calls[0][2]["q"]
        self.assertIn("is:issue is:open no:assignee", query)
        self.assertIn('label:"help wanted"', query)
        self.assertIn('-label:"kind/feature"', query)

    def test_discovery_keeps_page_size_stable_after_defensive_filtering(self) -> None:
        api = FakeAPI()
        api.issue_search_pages = {
            1: {
                "total_count": 4,
                "incomplete_results": False,
                "items": [issue(1), issue(2, assignees=[{"login": "owner"}])],
            },
            2: {
                "total_count": 4,
                "incomplete_results": False,
                "items": [issue(3), issue(4)],
            },
        }
        issues, _, _ = discovery.discover_issues(api, REPOSITORY, 3, [], [])
        self.assertEqual([1, 3, 4], [item["number"] for item in issues])
        search_calls = [call for call in api.calls if call[1] == "/search/issues"]
        self.assertEqual([3, 3], [call[2]["per_page"] for call in search_calls])

    def test_discovery_excludes_locally_known_issue_and_reports_source(self) -> None:
        api = FakeAPI()
        api.issue_search_pages[1] = {
            "total_count": 2,
            "incomplete_results": False,
            "items": [issue(1), issue(2)],
        }
        known = {
            1: discovery.KnownIssue(
                issue=f"{REPOSITORY}#1",
                reasons={"active-task"},
                sources={"agent-work/tasks/example/REQUEST.yaml"},
            )
        }
        result = discovery.run_discovery(api, REPOSITORY, 2, [], [], local_exclusions=known)
        self.assertEqual([f"{REPOSITORY}#2"], [item["issue"] for item in result["issues"]])
        self.assertEqual(1, result["local_exclusion"]["excluded_total"])
        self.assertEqual("active-task", result["local_exclusion"]["excluded"][0]["reasons"][0])

    def test_local_issue_index_distinguishes_evidence_from_terminal_screening(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            evidence = root / "screenings" / "example-project" / "evidence"
            evidence.mkdir(parents=True)
            (evidence / "evidence.yaml").write_text(
                "issue: example/project#7\n", encoding="utf-8"
            )
            issue_status = root / "issues" / "example-project-8"
            issue_status.mkdir(parents=True)
            (issue_status / "STATUS.yaml").write_text(
                "issue: example/project#8\nstatus: superseded\n", encoding="utf-8"
            )
            index = discovery.build_index(root, REPOSITORY)
            self.assertEqual({"known-evidence"}, index["example/project#7"].reasons)
            self.assertEqual({"formal-issue-terminal"}, index["example/project#8"].reasons)

    def test_cross_reference_is_resolved_and_pr_state_is_recorded(self) -> None:
        api = FakeAPI()
        api.add_pr(REPOSITORY, 44, merged=True)
        api.paginated[f"/repos/{REPOSITORY}/issues/1/timeline"] = [
            {"event": "cross-referenced", "source": {"issue": pr_item(REPOSITORY, 44)}}
        ]
        result = discovery.audit_issue(api, REPOSITORY, issue(1))
        self.assertEqual("related_pr_found", result["related_pr_status"])
        self.assertEqual(f"{REPOSITORY}#44", result["related_pr_evidence"][0]["pr"])
        self.assertTrue(result["related_pr_evidence"][0]["merged"])
        self.assertEqual(
            "timeline-cross-reference",
            result["related_pr_evidence"][0]["sources"][0]["kind"],
        )

    def test_issue_body_and_comment_refs_are_verified_as_prs(self) -> None:
        api = FakeAPI()
        api.add_pr(REPOSITORY, 50)
        api.add_pr("other/repo", 7)
        api.paginated[f"/repos/{REPOSITORY}/issues/1/comments"] = [
            {
                "body": "A cross-repo implementation: https://github.com/other/repo/pull/7",
                "html_url": f"https://github.com/{REPOSITORY}/issues/1#issuecomment-1",
            }
        ]
        result = discovery.audit_issue(
            api, REPOSITORY, issue(1, body="Possible implementation in #50")
        )
        self.assertEqual("related_pr_found", result["related_pr_status"])
        self.assertEqual(
            [f"{REPOSITORY}#50", "other/repo#7"],
            [value["pr"] for value in result["related_pr_evidence"]],
        )
        kinds = {
            source["kind"]
            for value in result["related_pr_evidence"]
            for source in value["sources"]
        }
        self.assertEqual({"issue-body", "issue-comment"}, kinds)

    def test_commit_reference_maps_full_pull_objects(self) -> None:
        api = FakeAPI()
        api.add_pr(REPOSITORY, 61)
        commit_url = f"https://api.github.com/repos/{REPOSITORY}/commits/abc123"
        api.paginated[f"/repos/{REPOSITORY}/issues/1/timeline"] = [
            {"event": "referenced", "commit_url": commit_url, "commit_id": "abc123"}
        ]
        api.paginated[f"/repos/{REPOSITORY}/commits/abc123/pulls"] = [
            pr_detail(REPOSITORY, 61)
        ]
        result = discovery.audit_issue(api, REPOSITORY, issue(1))
        self.assertEqual("related_pr_found", result["related_pr_status"])
        self.assertEqual("timeline-commit", result["related_pr_evidence"][0]["sources"][0]["kind"])

    def test_reference_search_result_is_verified(self) -> None:
        api = FakeAPI()
        api.add_pr(REPOSITORY, 70)
        api.pr_search_results["#1"] = [pr_item(REPOSITORY, 70)]
        result = discovery.audit_issue(api, REPOSITORY, issue(1))
        self.assertEqual("related_pr_found", result["related_pr_status"])
        self.assertEqual("reference-search", result["related_pr_evidence"][0]["sources"][0]["kind"])

    def test_non_pr_reference_is_discarded(self) -> None:
        api = FakeAPI()
        api.issue_objects[f"/repos/{REPOSITORY}/issues/80"] = issue(80)
        result = discovery.audit_issue(api, REPOSITORY, issue(1, body="Related discussion: #80"))
        self.assertEqual("no_known_related_pr", result["related_pr_status"])
        self.assertEqual([], result["related_pr_evidence"])

    def test_required_source_failure_produces_insufficient_evidence(self) -> None:
        api = FakeAPI()
        timeline_path = f"/repos/{REPOSITORY}/issues/1/timeline"
        api.fail_paginate.add(timeline_path)
        result = discovery.audit_issue(api, REPOSITORY, issue(1))
        self.assertEqual("insufficient_evidence", result["related_pr_status"])
        self.assertTrue(
            any("forced pagination failure" in value for value in result["limitations"])
        )

    def test_unresolved_connected_event_produces_insufficient_evidence(self) -> None:
        api = FakeAPI()
        api.paginated[f"/repos/{REPOSITORY}/issues/1/timeline"] = [
            {"event": "connected", "created_at": "2026-07-01T00:00:00Z"}
        ]
        result = discovery.audit_issue(api, REPOSITORY, issue(1))
        self.assertEqual("insufficient_evidence", result["related_pr_status"])
        self.assertTrue(any("did not expose" in value for value in result["limitations"]))

    def test_found_pr_wins_while_retaining_limitations(self) -> None:
        api = FakeAPI()
        api.add_pr(REPOSITORY, 90)
        api.fail_paginate.add(f"/repos/{REPOSITORY}/issues/1/timeline")
        result = discovery.audit_issue(api, REPOSITORY, issue(1, body="Fix in #90"))
        self.assertEqual("related_pr_found", result["related_pr_status"])
        self.assertTrue(result["limitations"])

    def test_run_discovery_summarizes_statuses(self) -> None:
        api = FakeAPI()
        api.issue_search_pages[1] = {
            "total_count": 1,
            "incomplete_results": False,
            "items": [issue(1)],
        }
        result = discovery.run_discovery(api, REPOSITORY, 1, [], [])
        self.assertEqual(1, result["summary"]["no_known_related_pr"])
        self.assertEqual({"remaining": "4999"}, result["rate_limit"])

    def test_run_discovery_reports_progress_without_polluting_result(self) -> None:
        api = FakeAPI()
        api.issue_search_pages[1] = {
            "total_count": 1,
            "incomplete_results": False,
            "items": [issue(1)],
        }
        messages: list[str] = []
        result = discovery.run_discovery(api, REPOSITORY, 1, [], [], messages.append)
        self.assertEqual("no_known_related_pr", result["issues"][0]["related_pr_status"])
        self.assertTrue(any("Checking read access" in message for message in messages))
        self.assertTrue(any("[1/1]" in message for message in messages))

    def test_run_discovery_keeps_candidate_order_with_multiple_workers(self) -> None:
        api = FakeAPI()
        api.issue_search_pages[1] = {
            "total_count": 3,
            "incomplete_results": False,
            "items": [issue(1), issue(2), issue(3)],
        }

        def audit_with_out_of_order_completion(
            _api: Any,
            repository: str,
            value: dict[str, Any],
            _resolver: Any,
        ) -> dict[str, Any]:
            number = int(value["number"])
            time.sleep((4 - number) * 0.01)
            return {
                "issue": f"{repository}#{number}",
                "related_pr_status": "no_known_related_pr",
            }

        with mock.patch.object(
            discovery, "audit_issue", side_effect=audit_with_out_of_order_completion
        ):
            result = discovery.run_discovery(api, REPOSITORY, 3, [], [], workers=3)
        self.assertEqual(
            [f"{REPOSITORY}#1", f"{REPOSITORY}#2", f"{REPOSITORY}#3"],
            [value["issue"] for value in result["issues"]],
        )

    def test_reference_resolver_deduplicates_pr_verification(self) -> None:
        api = FakeAPI()
        api.add_pr(REPOSITORY, 44)
        resolver = discovery.ReferenceResolver(api)
        reference = discovery.ItemReference("example", "project", 44)
        self.assertIsNotNone(resolver.resolve(reference))
        self.assertIsNotNone(resolver.resolve(reference))
        verification_calls = [
            call
            for call in api.calls
            if call[1]
            in {
                f"/repos/{REPOSITORY}/issues/44",
                f"/repos/{REPOSITORY}/pulls/44",
            }
        ]
        self.assertEqual(2, len(verification_calls))

    def test_repository_authorization_failure_stops_before_candidate_search(self) -> None:
        api = FakeAPI()
        api.auth_fail_get.add(f"/repos/{REPOSITORY}")
        with self.assertRaises(discovery.GitHubAuthorizationError):
            discovery.run_discovery(api, REPOSITORY, 1, [], [])
        self.assertFalse(
            any(path == "/search/issues" for _, path, _ in api.calls),
            api.calls,
        )

    def test_timeline_authorization_failure_is_not_downgraded(self) -> None:
        api = FakeAPI()
        timeline_path = f"/repos/{REPOSITORY}/issues/1/timeline"
        api.auth_fail_paginate.add(timeline_path)
        with self.assertRaises(discovery.GitHubAuthorizationError):
            discovery.audit_issue(api, REPOSITORY, issue(1))

    def test_client_paginates_and_does_not_put_token_in_url(self) -> None:
        requests: list[Any] = []

        def opener(request: Any, timeout: float) -> FakeResponse:
            requests.append(request)
            query = urllib.parse.parse_qs(urllib.parse.urlparse(request.full_url).query)
            page = int(query["page"][0])
            if page == 1:
                return FakeResponse(
                    list(range(100)),
                    {
                        "Link": '<https://api.github.com/example?page=2>; rel="next"',
                        "X-RateLimit-Remaining": "42",
                    },
                )
            return FakeResponse([100])

        client = discovery.GitHubClient("secret-token", opener=opener)
        self.assertEqual(list(range(101)), client.paginate("/example"))
        self.assertEqual(2, len(requests))
        self.assertNotIn("secret-token", requests[0].full_url)
        self.assertEqual("Bearer secret-token", requests[0].get_header("Authorization"))
        self.assertEqual("42", client.rate_limit["unknown"]["remaining"])

    def test_client_retries_server_failure(self) -> None:
        attempts = 0
        sleeps: list[float] = []

        def opener(request: Any, timeout: float) -> FakeResponse:
            nonlocal attempts
            attempts += 1
            if attempts == 1:
                raise urllib.error.HTTPError(
                    request.full_url,
                    503,
                    "unavailable",
                    {},
                    io.BytesIO(b'{"message":"try later"}'),
                )
            return FakeResponse({"ok": True})

        client = discovery.GitHubClient(
            "token", opener=opener, sleeper=sleeps.append, max_retries=1
        )
        self.assertEqual({"ok": True}, client.get("/example"))
        self.assertEqual(2, attempts)
        self.assertEqual([1.0], sleeps)

    def test_client_honors_bounded_secondary_rate_limit_retry(self) -> None:
        attempts = 0
        sleeps: list[float] = []

        def opener(request: Any, timeout: float) -> FakeResponse:
            nonlocal attempts
            attempts += 1
            if attempts == 1:
                raise urllib.error.HTTPError(
                    request.full_url,
                    403,
                    "rate limited",
                    {"Retry-After": "2", "X-RateLimit-Resource": "search"},
                    io.BytesIO(b'{"message":"secondary rate limit"}'),
                )
            return FakeResponse({"ok": True})

        client = discovery.GitHubClient(
            "token", opener=opener, sleeper=sleeps.append, max_retries=1
        )
        self.assertEqual({"ok": True}, client.get("/example"))
        self.assertEqual([2.0], sleeps)

    def test_client_classifies_policy_403_as_authorization_failure(self) -> None:
        def opener(request: Any, timeout: float) -> FakeResponse:
            raise urllib.error.HTTPError(
                request.full_url,
                403,
                "forbidden",
                {"X-RateLimit-Remaining": "4999"},
                io.BytesIO(b'{"message":"organization policy rejected this token"}'),
            )

        client = discovery.GitHubClient("token", opener=opener, max_retries=0)
        with self.assertRaisesRegex(
            discovery.GitHubAuthorizationError, "organization policy"
        ):
            client.get("/repos/example/project")

    def test_conflicting_label_filters_are_rejected(self) -> None:
        args = discovery.parse_args(
            [
                "--repository",
                REPOSITORY,
                "--limit",
                "1",
                "--include-label",
                "bug",
                "--exclude-label",
                "bug",
            ]
        )
        with self.assertRaisesRegex(SystemExit, "both included and excluded"):
            discovery._validate_args(args)

    def test_worker_limit_is_validated(self) -> None:
        args = discovery.parse_args(
            ["--repository", REPOSITORY, "--limit", "1", "--workers", "0"]
        )
        with self.assertRaisesRegex(SystemExit, "workers must be between"):
            discovery._validate_args(args)

    def test_json_and_summary_output_cannot_share_stdout(self) -> None:
        args = discovery.parse_args(
            [
                "--repository",
                REPOSITORY,
                "--limit",
                "1",
                "--output",
                "-",
                "--summary-output",
                "-",
            ]
        )
        with self.assertRaisesRegex(SystemExit, "cannot both use standard output"):
            discovery._validate_args(args)

    def test_main_requires_environment_token(self) -> None:
        stderr = io.StringIO()
        with mock.patch.dict("os.environ", {}, clear=True), mock.patch("sys.stderr", stderr):
            result = discovery.main(["--repository", REPOSITORY, "--limit", "1"])
        self.assertEqual(2, result)
        self.assertIn("GITHUB_TOKEN is required", stderr.getvalue())

    def test_output_is_valid_utf8_json(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            destination = Path(temporary) / "result.json"
            discovery._write_output({"title": "测试"}, str(destination))
            self.assertEqual({"title": "测试"}, json.loads(destination.read_text()))

    def test_candidate_summary_contains_only_no_known_pr_candidates(self) -> None:
        output = {
            "repository": REPOSITORY,
            "generated_at": "2026-07-31T08:00:00Z",
            "query": {
                "candidate_limit": 3,
                "include_labels": [],
                "exclude_labels": ["kind/feature"],
            },
            "summary": {
                "matched_total": 100,
                "inspected": 3,
                "related_pr_found": 1,
                "no_known_related_pr": 1,
                "insufficient_evidence": 1,
            },
            "limitations": [],
            "issues": [
                {
                    "issue": f"{REPOSITORY}#1",
                    "url": f"https://github.com/{REPOSITORY}/issues/1",
                    "title": "Candidate issue",
                    "labels": ["kind/bug"],
                    "related_pr_status": "no_known_related_pr",
                },
                {
                    "issue": f"{REPOSITORY}#2",
                    "url": f"https://github.com/{REPOSITORY}/issues/2",
                    "title": "Occupied issue",
                    "labels": [],
                    "related_pr_status": "related_pr_found",
                },
                {
                    "issue": f"{REPOSITORY}#3",
                    "url": f"https://github.com/{REPOSITORY}/issues/3",
                    "title": "Incomplete issue",
                    "labels": [],
                    "related_pr_status": "insufficient_evidence",
                },
            ],
        }
        rendered = discovery.render_candidate_summary(output)
        self.assertIn("Candidate issue", rendered)
        self.assertNotIn("Occupied issue", rendered)
        self.assertNotIn("Incomplete issue", rendered)
        self.assertIn("1 with PR evidence; 1 insufficient-evidence", rendered)
        self.assertIn("does not mean `available`", rendered)


if __name__ == "__main__":
    unittest.main()
