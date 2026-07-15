#!/usr/bin/env python3
"""Post a polished CI/CD Adaptive Card to a Microsoft Teams Workflow webhook."""

from __future__ import annotations

import json
import os
import sys
import urllib.error
import urllib.request
from datetime import datetime, timezone
from typing import Any


SUCCESS_STATUSES = {"success", "passed", "pass", "succeeded", "completed"}
CANCELLED_STATUSES = {"cancelled", "canceled", "skipped"}


def env(name: str, default: str = "") -> str:
    value = os.environ.get(name, "").strip()
    return value or default


def to_int(value: str) -> int:
    try:
        return int(value)
    except ValueError:
        return 0


def normalize_status(value: str) -> str:
    normalized = value.strip().lower()
    if normalized in SUCCESS_STATUSES:
        return "success"
    if normalized in CANCELLED_STATUSES:
        return "cancelled"
    return "failure"


def fact(title: str, value: str) -> dict[str, str]:
    return {"title": title, "value": value}


def load_event_payload() -> dict[str, Any]:
    event_path = env("GITHUB_EVENT_PATH")
    if not event_path:
        return {}

    try:
        with open(event_path, encoding="utf-8") as event_file:
            payload = json.load(event_file)
    except (OSError, json.JSONDecodeError):
        return {}

    return payload if isinstance(payload, dict) else {}


def metric_column(icon: str, value: str, label: str) -> dict[str, Any]:
    return {
        "type": "Column",
        "width": "stretch",
        "items": [
            {
                "type": "TextBlock",
                "text": f"{icon} {value}",
                "weight": "Bolder",
                "size": "Medium",
                "horizontalAlignment": "Center",
                "wrap": True,
            },
            {
                "type": "TextBlock",
                "text": label,
                "isSubtle": True,
                "spacing": "None",
                "horizontalAlignment": "Center",
                "wrap": True,
            },
        ],
    }


def status_profile(
    notification_type: str,
    status: str,
    version: str,
    build: str,
) -> dict[str, str]:
    is_deployment = notification_type == "testflight_deployment"

    if status == "success" and is_deployment:
        return {
            "icon": "🚀",
            "eyebrow": "TESTFLIGHT DEPLOYMENT",
            "title": "QA build delivered",
            "summary": (
                f"Version **{version}** (build **{build}**) is available "
                "for testing in TestFlight."
            ),
            "style": "Good",
            "status_text": "DEPLOYMENT SUCCEEDED",
        }

    if status == "success":
        return {
            "icon": "✅",
            "eyebrow": "PULL REQUEST VALIDATION",
            "title": "Ready to merge",
            "summary": (
                "All required iOS quality checks passed. "
                "This change is ready for review and merge."
            ),
            "style": "Good",
            "status_text": "QUALITY GATE PASSED",
        }

    if status == "cancelled":
        return {
            "icon": "⏹️",
            "eyebrow": (
                "TESTFLIGHT DEPLOYMENT"
                if is_deployment
                else "PULL REQUEST VALIDATION"
            ),
            "title": "Pipeline cancelled",
            "summary": "This workflow run did not complete.",
            "style": "Warning",
            "status_text": "CANCELLED",
        }

    if is_deployment:
        return {
            "icon": "❌",
            "eyebrow": "TESTFLIGHT DEPLOYMENT",
            "title": "Deployment needs attention",
            "summary": (
                "The QA build was not delivered to TestFlight. "
                "Open the workflow to review the failed step."
            ),
            "style": "Attention",
            "status_text": "DEPLOYMENT FAILED",
        }

    return {
        "icon": "❌",
        "eyebrow": "PULL REQUEST VALIDATION",
        "title": "Action required",
        "summary": (
            "One or more quality checks failed. "
            "Resolve the findings before merging this change."
        ),
        "style": "Attention",
        "status_text": "QUALITY GATE FAILED",
    }


def build_card() -> dict[str, Any]:
    raw_status = env("PIPELINE_STATUS", "failure")
    status = normalize_status(raw_status)
    event_payload = load_event_payload()
    testflight_status = env("TESTFLIGHT_STATUS", "Not applicable")
    notification_type = env("NOTIFICATION_TYPE")
    if not notification_type:
        notification_type = (
            "testflight_deployment"
            if testflight_status.lower() not in {"", "n/a", "not applicable"}
            else "pr_validation"
        )
    version = env("APP_VERSION", "unknown")
    build = env("CI_BUILD_NUMBER", "unknown")
    profile = status_profile(notification_type, status, version, build)

    repository = env("GITHUB_REPOSITORY", "unknown repository")
    workflow_name = env("WORKFLOW_NAME", env("CI_WORKFLOW", "iOS CI/CD"))
    run_number = env("RUN_NUMBER", env("GITHUB_RUN_NUMBER", "unknown"))
    run_attempt = env("RUN_ATTEMPT", env("GITHUB_RUN_ATTEMPT", "1"))
    environment = env(
        "DEPLOYMENT_ENVIRONMENT",
        env("CI_ENVIRONMENT", "GitHub Actions CI"),
    )
    pull_request = event_payload.get("pull_request", {})
    if not isinstance(pull_request, dict):
        pull_request = {}

    head = pull_request.get("head", {})
    base = pull_request.get("base", {})
    if not isinstance(head, dict):
        head = {}
    if not isinstance(base, dict):
        base = {}

    branch = env(
        "CI_BRANCH",
        env("GITHUB_HEAD_REF", str(head.get("ref", "unknown"))),
    )
    target_branch = env(
        "TARGET_BRANCH",
        env("GITHUB_BASE_REF", str(base.get("ref", ""))),
    )
    commit = env("CI_COMMIT_SHA", "unknown")
    author = env("COMMIT_AUTHOR", env("TRIGGERED_BY", "unknown"))
    actor = env("TRIGGERED_BY", env("GITHUB_ACTOR", author))
    xcode = env("XCODE_VERSION", "unknown")
    event_name = env("EVENT_NAME", env("GITHUB_EVENT_NAME", "unknown"))

    tests = to_int(env("TESTS", "0"))
    failures = to_int(env("FAILURES", "0"))
    passed_tests = max(tests - failures, 0)
    coverage = env("COVERAGE", "Unavailable")
    lint_violations = to_int(env("LINT_VIOLATIONS", "0"))
    coverage_threshold = env("COVERAGE_THRESHOLD", "70")

    test_icon = "✅" if tests > 0 and failures == 0 else "❌"
    coverage_icon = "✅" if status == "success" else "📊"
    lint_icon = "✅" if lint_violations == 0 else "❌"

    run_url = env("RUN_URL")
    pr_title = env("PR_TITLE", str(pull_request.get("title", "")))
    pr_number = env("PR_NUMBER", str(event_payload.get("number", "")))
    server_url = env("GITHUB_SERVER_URL", "https://github.com")
    pr_url = env("PR_URL", str(pull_request.get("html_url", "")))
    if not pr_url and pr_number and repository != "unknown repository":
        pr_url = f"{server_url}/{repository}/pull/{pr_number}"
    commit_url = (
        f"{server_url}/{repository}/commit/{commit}"
        if repository != "unknown repository" and commit != "unknown"
        else ""
    )

    branch_value = f"`{branch}`"
    if target_branch:
        branch_value = f"`{branch}` → `{target_branch}`"

    context_facts = []
    if pr_title:
        prefix = f"#{pr_number} " if pr_number else ""
        context_facts.append(fact("Pull request", f"{prefix}{pr_title}"))
    context_facts.extend(
        [
            fact("Branch", branch_value),
            fact("Commit", f"`{commit}`"),
            fact("Author", author),
            fact("Triggered by", actor),
            fact("Environment", environment),
            fact("Version", f"{version} ({build})"),
            fact("Toolchain", f"Xcode {xcode}"),
        ]
    )

    quality_container = {
        "type": "Container",
        "spacing": "Medium",
        "items": [
            {
                "type": "TextBlock",
                "text": "Quality signals",
                "weight": "Bolder",
                "size": "Medium",
                "wrap": True,
            },
            {
                "type": "ColumnSet",
                "spacing": "Small",
                "columns": [
                    metric_column(
                        test_icon,
                        f"{passed_tests}/{tests}",
                        "Tests passed",
                    ),
                    metric_column(
                        coverage_icon,
                        coverage,
                        f"Coverage · {coverage_threshold}% min",
                    ),
                    metric_column(
                        lint_icon,
                        str(lint_violations),
                        "Lint violations",
                    ),
                ],
            },
        ],
    }

    body: list[dict[str, Any]] = [
        {
            "type": "Container",
            "style": profile["style"],
            "bleed": True,
            "items": [
                {
                    "type": "TextBlock",
                    "text": profile["eyebrow"],
                    "weight": "Bolder",
                    "size": "Small",
                    "wrap": True,
                },
                {
                    "type": "TextBlock",
                    "text": f'{profile["icon"]} {profile["title"]}',
                    "weight": "Bolder",
                    "size": "Large",
                    "spacing": "Small",
                    "wrap": True,
                },
                {
                    "type": "TextBlock",
                    "text": profile["summary"],
                    "spacing": "Small",
                    "wrap": True,
                },
                {
                    "type": "ColumnSet",
                    "spacing": "Medium",
                    "columns": [
                        {
                            "type": "Column",
                            "width": "stretch",
                            "items": [
                                {
                                    "type": "TextBlock",
                                    "text": profile["status_text"],
                                    "weight": "Bolder",
                                    "wrap": True,
                                },
                                {
                                    "type": "TextBlock",
                                    "text": environment,
                                    "isSubtle": True,
                                    "spacing": "None",
                                    "wrap": True,
                                },
                            ],
                        },
                        {
                            "type": "Column",
                            "width": "auto",
                            "items": [
                                {
                                    "type": "TextBlock",
                                    "text": f"Run #{run_number}",
                                    "weight": "Bolder",
                                    "horizontalAlignment": "Right",
                                    "wrap": True,
                                },
                                {
                                    "type": "TextBlock",
                                    "text": repository,
                                    "isSubtle": True,
                                    "spacing": "None",
                                    "horizontalAlignment": "Right",
                                    "wrap": True,
                                },
                            ],
                        },
                    ],
                },
            ],
        },
        quality_container,
        {
            "type": "Container",
            "separator": True,
            "spacing": "Medium",
            "items": [
                {
                    "type": "TextBlock",
                    "text": "Build context",
                    "weight": "Bolder",
                    "size": "Medium",
                    "wrap": True,
                },
                {
                    "type": "FactSet",
                    "facts": context_facts,
                },
            ],
        },
    ]

    if notification_type == "testflight_deployment":
        testflight_icon = "✅" if status == "success" else "❌"
        body.append(
            {
                "type": "Container",
                "style": "Emphasis",
                "separator": True,
                "spacing": "Medium",
                "items": [
                    {
                        "type": "TextBlock",
                        "text": f"{testflight_icon} TestFlight",
                        "weight": "Bolder",
                        "size": "Medium",
                        "wrap": True,
                    },
                    {
                        "type": "TextBlock",
                        "text": (
                            f"Status: **{testflight_status}**  \n"
                            f"Environment: **{environment}**"
                        ),
                        "wrap": True,
                    },
                ],
            }
        )

    build_date = env("CI_BUILD_DATE")
    if build_date:
        timestamp = build_date
    else:
        timestamp = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")

    body.append(
        {
            "type": "TextBlock",
            "text": (
                f"{workflow_name} · {event_name} · "
                f"run #{run_number}, attempt {run_attempt} · {timestamp}"
            ),
            "isSubtle": True,
            "size": "Small",
            "separator": True,
            "spacing": "Medium",
            "wrap": True,
        }
    )

    actions = []
    if run_url:
        actions.append(
            {
                "type": "Action.OpenUrl",
                "title": "Open workflow run",
                "url": run_url,
            }
        )
    if pr_url:
        actions.append(
            {
                "type": "Action.OpenUrl",
                "title": "View pull request",
                "url": pr_url,
            }
        )
    if commit_url:
        actions.append(
            {
                "type": "Action.OpenUrl",
                "title": "View commit",
                "url": commit_url,
            }
        )

    content = {
        "$schema": "http://adaptivecards.io/schemas/adaptive-card.json",
        "type": "AdaptiveCard",
        "version": "1.4",
        "fallbackText": (
            f'{profile["title"]}: {repository} run #{run_number}. '
            f"Open GitHub Actions for details."
        ),
        "msteams": {"width": "Full"},
        "body": body,
        "actions": actions,
    }

    return {
        "type": "message",
        "attachments": [
            {
                "contentType": "application/vnd.microsoft.card.adaptive",
                "contentUrl": None,
                "content": content,
            }
        ],
    }


def main() -> int:
    webhook_url = env("TEAMS_WEBHOOK_URL")
    if not webhook_url:
        print("TEAMS_WEBHOOK_URL is not configured; skipping Teams notification.")
        return 0

    card = build_card()
    request = urllib.request.Request(
        webhook_url,
        data=json.dumps(card).encode("utf-8"),
        headers={"Content-Type": "application/json"},
        method="POST",
    )

    try:
        with urllib.request.urlopen(request, timeout=20) as response:
            print(f"Teams notification sent: HTTP {response.status}")
    except (urllib.error.URLError, TimeoutError) as error:
        print(f"Teams notification failed: {error}", file=sys.stderr)
        return 1

    return 0


if __name__ == "__main__":
    sys.exit(main())
