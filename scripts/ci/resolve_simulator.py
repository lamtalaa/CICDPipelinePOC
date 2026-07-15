#!/usr/bin/env python3
"""Resolve the newest available iOS runtime for the configured simulator."""

from __future__ import annotations

import json
import os
import subprocess
from typing import Any


def simctl_json(*arguments: str) -> dict[str, Any]:
    try:
        result = subprocess.run(
            ["xcrun", "simctl", "list", "-j", *arguments],
            check=True,
            capture_output=True,
            text=True,
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


def main() -> int:
    target_device = os.environ.get("SIMULATOR_DEVICE", "iPhone 16e").strip()
    target_device = target_device or "iPhone 16e"

    runtime_payload = simctl_json("runtimes")
    device_payload = simctl_json("devices", "available")
    runtimes = runtime_payload.get("runtimes", [])
    devices_by_runtime = device_payload.get("devices", {})

    candidates: list[tuple[tuple[int, ...], str]] = []
    if not isinstance(runtimes, list) or not isinstance(devices_by_runtime, dict):
        return 0

    for runtime in runtimes:
        if not isinstance(runtime, dict):
            continue

        identifier = str(runtime.get("identifier", ""))
        version = str(runtime.get("version", ""))
        if "SimRuntime.iOS" not in identifier or not version:
            continue
        if runtime.get("isAvailable") is False:
            continue

        runtime_devices = devices_by_runtime.get(identifier, [])
        if not isinstance(runtime_devices, list):
            continue

        device_is_available = any(
            isinstance(device, dict)
            and device.get("name") == target_device
            and device.get("isAvailable", True) is not False
            for device in runtime_devices
        )
        if device_is_available:
            candidates.append((version_key(version), version))

    if candidates:
        print(max(candidates)[1])

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
