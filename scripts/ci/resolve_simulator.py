#!/usr/bin/env python3
"""Resolve the newest iOS runtime and ensure the requested simulator exists."""

from __future__ import annotations

import json
import os
import subprocess
import sys
from typing import Any


DEFAULT_DEVICE = "iPhone 16e"


def tool_environment() -> dict[str, str]:
    """Use the runner's default Xcode rather than a stale workflow override."""
    environment = os.environ.copy()
    environment.pop("DEVELOPER_DIR", None)
    return environment


def simctl_json(*arguments: str) -> dict[str, Any]:
    try:
        result = subprocess.run(
            ["xcrun", "simctl", "list", "-j", *arguments],
            check=True,
            capture_output=True,
            text=True,
            env=tool_environment(),
        )
        payload = json.loads(result.stdout)
    except (OSError, subprocess.CalledProcessError, json.JSONDecodeError):
        return {}

    return payload if isinstance(payload, dict) else {}


def version_key(version: str) -> tuple[int, ...]:
    parts: list[int] = []
    for component in version.split("."):
        try:
            parts.append(int(component))
        except ValueError:
            parts.append(0)
    return tuple(parts)


def newest_ios_runtime() -> tuple[str, str]:
    payload = simctl_json("runtimes")
    runtimes = payload.get("runtimes", [])
    candidates: list[tuple[tuple[int, ...], str, str]] = []

    if not isinstance(runtimes, list):
        return "", ""

    for runtime in runtimes:
        if not isinstance(runtime, dict):
            continue

        identifier = str(runtime.get("identifier", ""))
        version = str(runtime.get("version", ""))
        if "SimRuntime.iOS" not in identifier or not version:
            continue
        if runtime.get("isAvailable") is False:
            continue

        candidates.append((version_key(version), version, identifier))

    if not candidates:
        return "", ""

    _, version, identifier = max(candidates)
    return version, identifier


def device_type_identifier(target_device: str) -> str:
    payload = simctl_json("devicetypes")
    device_types = payload.get("devicetypes", [])
    if not isinstance(device_types, list):
        return ""

    for device_type in device_types:
        if not isinstance(device_type, dict):
            continue
        if str(device_type.get("name", "")) == target_device:
            return str(device_type.get("identifier", ""))

    return ""


def device_exists(target_device: str, runtime_identifier: str) -> bool:
    payload = simctl_json("devices", "available")
    devices_by_runtime = payload.get("devices", {})
    if not isinstance(devices_by_runtime, dict):
        return False

    devices = devices_by_runtime.get(runtime_identifier, [])
    if not isinstance(devices, list):
        return False

    return any(
        isinstance(device, dict)
        and device.get("name") == target_device
        and device.get("isAvailable", True) is not False
        for device in devices
    )


def create_simulator(
    target_device: str,
    device_type: str,
    runtime_identifier: str,
) -> bool:
    result = subprocess.run(
        [
            "xcrun",
            "simctl",
            "create",
            target_device,
            device_type,
            runtime_identifier,
        ],
        check=False,
        capture_output=True,
        text=True,
        env=tool_environment(),
    )
    if result.returncode == 0:
        return True

    message = result.stderr.strip() or result.stdout.strip()
    print(f"Unable to create simulator: {message}", file=sys.stderr)
    return False


def main() -> int:
    target_device = os.environ.get("SIMULATOR_DEVICE", DEFAULT_DEVICE).strip()
    target_device = target_device or DEFAULT_DEVICE

    version, runtime_identifier = newest_ios_runtime()
    if not version or not runtime_identifier:
        print("No available iOS simulator runtime was found.", file=sys.stderr)
        return 1

    if not device_exists(target_device, runtime_identifier):
        device_type = device_type_identifier(target_device)
        if not device_type:
            print(
                f"Simulator device type '{target_device}' is not installed.",
                file=sys.stderr,
            )
            return 1

        if not create_simulator(target_device, device_type, runtime_identifier):
            return 1

        print(
            f"Created {target_device} on iOS {version}.",
            file=sys.stderr,
        )

    print(version)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
