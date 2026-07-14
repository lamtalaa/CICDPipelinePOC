#!/usr/bin/env python3
"""Generate clean TestFlight release notes from the merged PR or recent commits."""

from __future__ import annotations

import json
import os
import subprocess
import sys
import urllib.error
import urllib.request
from pathlib import Path

OUTPUT_PATH = Path(os.environ.get("RELEASE_NOTES_PATH", "build/release_notes.txt"))
MAX_LENGTH = 3500


def env(name: str, default: str = "") -> str:
    value = os.environ.get(name, "").strip()
    return value or default


def associated_pull_request() -> str | None:
    repository = env("GITHUB_REPOSITORY")
    sha = env("GITHUB_SHA")
    token = env("GITHUB_TOKEN")
    api_url = env("GITHUB_API_URL", "https://api.github.com")

    if not repository or not sha or not token:
        return None

    request = urllib.request.Request(
        f"{api_url}/repos/{repository}/commits/{sha}/pulls",
        headers={
            "Accept": "application/vnd.github+json",
            "Authorization": f"Bearer {token}",
            "X-GitHub-Api-Version": "2022-11-28",
            "User-Agent": "CICDPipelinePOC-release-notes",
        },
    )

    try:
        with urllib.request.urlopen(request, timeout=20) as response:
            pulls = json.loads(response.read().decode("utf-8"))
    except (urllib.error.URLError, json.JSONDecodeError, TimeoutError):
        return None

    if not pulls:
        return None

    merged = next((pull for pull in pulls if pull.get("merged_at")), pulls[0])
    title = str(merged.get("title", "")).strip()
    number = merged.get("number")

    if not title:
        return None

    return f"• {title} (#{number})" if number else f"• {title}"


def recent_commit_messages() -> list[str]:
    before = env("GITHUB_EVENT_BEFORE")
    sha = env("GITHUB_SHA", "HEAD")

    if before and before != "0" * 40:
        revision = f"{before}..{sha}"
    else:
        revision = f"{sha}~10..{sha}"

    try:
        completed = subprocess.run(
            ["git", "log", revision, "--pretty=format:%s"],
            check=True,
            capture_output=True,
            text=True,
        )
        messages = completed.stdout.splitlines()
    except subprocess.CalledProcessError:
        try:
            completed = subprocess.run(
                ["git", "log", "-10", "--pretty=format:%s"],
                check=True,
                capture_output=True,
                text=True,
            )
            messages = completed.stdout.splitlines()
        except subprocess.CalledProcessError:
            return []

    cleaned: list[str] = []
    seen: set[str] = set()

    for message in messages:
        message = message.strip()
        if not message or message.startswith("Merge pull request"):
            continue
        if message in seen:
            continue
        seen.add(message)
        cleaned.append(f"• {message}")

    return cleaned[:10]


def main() -> int:
    change = associated_pull_request()
    changes = [change] if change else recent_commit_messages()

    if not changes:
        changes = ["• Automated CI/CD pipeline build"]

    version = env("CI_VERSION", "unknown")
    build = env("CI_BUILD_NUMBER", "unknown")
    branch = env("CI_BRANCH", "unknown")
    commit = env("CI_COMMIT_SHA", "unknown")

    notes = "\n".join(
        [
            "What to Test",
            "",
            *changes,
            "",
            f"Version: {version} ({build})",
            f"Branch: {branch}",
            f"Commit: {commit}",
        ]
    )

    if len(notes) > MAX_LENGTH:
        notes = notes[: MAX_LENGTH - 1].rstrip() + "…"

    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT_PATH.write_text(notes + "\n", encoding="utf-8")
    print(notes)
    return 0


if __name__ == "__main__":
    sys.exit(main())
