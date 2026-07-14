#!/usr/bin/env python3
"""Post a CI/CD Adaptive Card to a Microsoft Teams Workflow webhook."""

from __future__ import annotations

import json
import os
import sys
import urllib.error
import urllib.request


def env(name: str, default: str = "") -> str:
    value = os.environ.get(name, "").strip()
    return value or default


def fact(title: str, value: str) -> dict[str, str]:
    return {"title": title, "value": value}


def main() -> int:
    webhook_url = env("TEAMS_WEBHOOK_URL")
    if not webhook_url:
        print("TEAMS_WEBHOOK_URL is not configured; skipping Teams notification.")
        return 0

    status = env("PIPELINE_STATUS", "unknown").lower()
    succeeded = status == "success"
    icon = "✅" if succeeded else "❌"
    title = f"{icon} iOS CI/CD Pipeline {status.title()}"

    run_url = env("RUN_URL")
    tests = env("TESTS", "0")
    failures = env("FAILURES", "0")
    coverage = env("COVERAGE", "Unavailable")
    lint_violations = env("LINT_VIOLATIONS", "0")

    card = {
        "type": "message",
        "attachments": [
            {
                "contentType": "application/vnd.microsoft.card.adaptive",
                "contentUrl": None,
                "content": {
                    "$schema": "http://adaptivecards.io/schemas/adaptive-card.json",
                    "type": "AdaptiveCard",
                    "version": "1.4",
                    "body": [
                        {
                            "type": "TextBlock",
                            "size": "Large",
                            "weight": "Bolder",
                            "text": title,
                            "wrap": True,
                        },
                        {
                            "type": "TextBlock",
                            "text": env("GITHUB_REPOSITORY", "unknown"),
                            "isSubtle": True,
                            "wrap": True,
                        },
                        {
                            "type": "FactSet",
                            "facts": [
                                fact("Branch", env("CI_BRANCH", "unknown")),
                                fact("Commit", env("CI_COMMIT_SHA", "unknown")),
                                fact("Author", env("COMMIT_AUTHOR", "unknown")),
                                fact("Environment", env("CI_ENVIRONMENT", "GitHub Actions")),
                                fact("Version", env("APP_VERSION", "unknown")),
                                fact("Build", env("CI_BUILD_NUMBER", "unknown")),
                                fact("Tests", f"{tests} run, {failures} failed"),
                                fact("Coverage", coverage),
                                fact("SwiftLint", f"{lint_violations} violation(s)"),
                                fact("TestFlight", env("TESTFLIGHT_STATUS", "Not applicable")),
                            ],
                        },
                    ],
                    "actions": ([
                        {
                            "type": "Action.OpenUrl",
                            "title": "Open GitHub Actions Run",
                            "url": run_url,
                        }
                    ] if run_url else []),
                },
            }
        ],
    }

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
