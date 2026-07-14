#!/usr/bin/env python3
"""Collect SwiftLint, XCTest, and Xcode coverage metrics for GitHub Actions."""

from __future__ import annotations

import glob
import json
import os
import subprocess
import sys
import xml.etree.ElementTree as ET
from pathlib import Path
from typing import Any

RESULTS_DIRECTORY = Path("ci-results")
TEST_OUTPUT_DIRECTORY = Path("fastlane/test_output")
LINT_REPORT = RESULTS_DIRECTORY / "swiftlint.json"
METRICS_FILE = RESULTS_DIRECTORY / "metrics.json"
SUMMARY_FILE = RESULTS_DIRECTORY / "summary.md"
COVERAGE_REPORT = RESULTS_DIRECTORY / "coverage.json"


def env(name: str, default: str = "") -> str:
    value = os.environ.get(name, "").strip()
    return value or default


def parse_int(value: Any, default: int = 0) -> int:
    try:
        return int(value)
    except (TypeError, ValueError):
        return default


def parse_float(value: Any, default: float = 0.0) -> float:
    try:
        return float(value)
    except (TypeError, ValueError):
        return default


def parse_junit() -> tuple[int, int]:
    junit_path = TEST_OUTPUT_DIRECTORY / "junit.xml"
    if not junit_path.exists():
        return 0, 0

    try:
        root = ET.parse(junit_path).getroot()
    except ET.ParseError:
        return 0, 0

    if "tests" in root.attrib:
        return (
            parse_int(root.attrib.get("tests")),
            parse_int(root.attrib.get("failures"))
            + parse_int(root.attrib.get("errors")),
        )

    suites = root.findall(".//testsuite")
    tests = sum(parse_int(suite.attrib.get("tests")) for suite in suites)
    failures = sum(
        parse_int(suite.attrib.get("failures"))
        + parse_int(suite.attrib.get("errors"))
        for suite in suites
    )
    return tests, failures


def parse_fastlane_metrics() -> tuple[int, int]:
    path = TEST_OUTPUT_DIRECTORY / "fastlane_metrics.json"
    if not path.exists():
        return 0, 0

    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError):
        return 0, 0

    return (
        parse_int(data.get("number_of_tests")),
        parse_int(data.get("number_of_failures")),
    )


def parse_lint_violations() -> int:
    if not LINT_REPORT.exists() or LINT_REPORT.stat().st_size == 0:
        return 0

    try:
        data = json.loads(LINT_REPORT.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError):
        return 0

    return len(data) if isinstance(data, list) else 0


def find_result_bundle() -> Path | None:
    paths = sorted(
        Path(path)
        for path in glob.glob(
            str(TEST_OUTPUT_DIRECTORY / "**" / "*.xcresult"),
            recursive=True,
        )
    )
    return paths[0] if paths else None


def extract_coverage(target_name: str) -> float | None:
    result_bundle = find_result_bundle()
    if result_bundle is None:
        return None

    command = [
        "xcrun",
        "xccov",
        "view",
        "--report",
        "--json",
        str(result_bundle),
    ]

    try:
        completed = subprocess.run(
            command,
            check=True,
            capture_output=True,
            text=True,
        )
        report = json.loads(completed.stdout)
    except (subprocess.CalledProcessError, json.JSONDecodeError, OSError):
        return None

    COVERAGE_REPORT.write_text(
        json.dumps(report, indent=2),
        encoding="utf-8",
    )

    targets = report.get("targets", [])
    if not isinstance(targets, list):
        return None

    matching_target = next(
        (
            target
            for target in targets
            if str(target.get("name", "")) == target_name
        ),
        None,
    )

    if matching_target is None:
        matching_target = next(
            (
                target
                for target in targets
                if str(target.get("name", "")).startswith(target_name)
                and "Tests" not in str(target.get("name", ""))
            ),
            None,
        )

    if matching_target is None:
        return None

    coverage = parse_float(matching_target.get("lineCoverage"), -1.0)
    if coverage < 0:
        return None

    return coverage * 100.0 if coverage <= 1.0 else coverage


def write_github_output(values: dict[str, str]) -> None:
    output_path = env("GITHUB_OUTPUT")
    if not output_path:
        return

    with Path(output_path).open("a", encoding="utf-8") as output:
        for key, value in values.items():
            output.write(f"{key}={value}\n")


def display_percentage(value: float | None) -> str:
    return "Unavailable" if value is None else f"{value:.2f}%"


def main() -> int:
    RESULTS_DIRECTORY.mkdir(parents=True, exist_ok=True)

    junit_tests, junit_failures = parse_junit()
    fastlane_tests, fastlane_failures = parse_fastlane_metrics()
    tests = max(junit_tests, fastlane_tests)
    failures = max(junit_failures, fastlane_failures)

    lint_outcome = env("LINT_STEP_OUTCOME", "unknown")
    test_outcome = env("TEST_STEP_OUTCOME", "unknown")
    threshold = parse_float(env("COVERAGE_THRESHOLD", "70"), 70.0)
    target_name = env("COVERAGE_TARGET", "CICDPipelinePOC")

    lint_violations = parse_lint_violations()
    coverage = extract_coverage(target_name)

    lint_passed = lint_outcome == "success" and lint_violations == 0
    tests_passed = test_outcome == "success" and tests > 0 and failures == 0
    coverage_passed = coverage is not None and coverage >= threshold
    quality_passed = lint_passed and tests_passed and coverage_passed

    metrics = {
        "quality_status": "passed" if quality_passed else "failed",
        "lint_status": "passed" if lint_passed else "failed",
        "lint_violations": lint_violations,
        "test_status": "passed" if tests_passed else "failed",
        "tests": tests,
        "failures": failures,
        "coverage": None if coverage is None else round(coverage, 2),
        "coverage_threshold": threshold,
        "coverage_status": "passed" if coverage_passed else "failed",
        "branch": env("CI_BRANCH", "unknown"),
        "commit": env("CI_COMMIT_SHA", "unknown"),
        "version": env("APP_VERSION", "unknown"),
        "build": env("CI_BUILD_NUMBER", "unknown"),
        "xcode": env("XCODE_VERSION", "unknown"),
    }

    METRICS_FILE.write_text(
        json.dumps(metrics, indent=2),
        encoding="utf-8",
    )

    overall_icon = "✅" if quality_passed else "❌"
    lint_icon = "✅" if lint_passed else "❌"
    tests_icon = "✅" if tests_passed else "❌"
    coverage_icon = "✅" if coverage_passed else "❌"

    summary = f"""## {overall_icon} iOS CI Quality Report

| Quality gate | Result | Details |
|---|---:|---|
| SwiftLint | {lint_icon} | {lint_violations} violation(s) |
| Unit tests | {tests_icon} | {tests} executed, {failures} failed |
| Code coverage | {coverage_icon} | {display_percentage(coverage)} / {threshold:.0f}% required |

| Build metadata | Value |
|---|---|
| Branch | `{metrics['branch']}` |
| Commit | `{metrics['commit']}` |
| Version | `{metrics['version']}` |
| Build | `{metrics['build']}` |
| Xcode | `{metrics['xcode']}` |
"""
    SUMMARY_FILE.write_text(summary, encoding="utf-8")

    write_github_output(
        {
            "quality_status": metrics["quality_status"],
            "lint_status": metrics["lint_status"],
            "lint_violations": str(lint_violations),
            "test_status": metrics["test_status"],
            "tests": str(tests),
            "failures": str(failures),
            "coverage": display_percentage(coverage),
            "coverage_value": "" if coverage is None else f"{coverage:.2f}",
            "coverage_status": metrics["coverage_status"],
        }
    )

    print(summary)
    return 0


if __name__ == "__main__":
    sys.exit(main())
