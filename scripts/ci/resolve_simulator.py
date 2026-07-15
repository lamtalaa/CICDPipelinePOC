#!/usr/bin/env python3
"""Resolve or create the requested iOS simulator on the CI runner."""

from __future__ import annotations

import json
import os
import subprocess
import sys
import time
from typing import Any


DEFAULT_DEVICE = "iPhone 16e"


def select_configured_xcode() -> bool:
    developer_dir = os.environ.get("DEVELOPER_DIR", "").strip()
    if not developer_dir:
        return True

    result = subprocess.run(
        ["sudo", "xcode-select", "--switch", developer_dir],
        check=False,
        capture_output=True,
        text=True,
    )
    if result.returncode != 0:
        message = result.stderr.strip() or result.stdout.strip()
        print(
            f"Unable to select Xcode at '{developer_dir}': {message}",
            file=sys.stderr,
        )
        return False

    # CoreSimulator can remain bound to the Xcode version selected when the
    # runner image started. Restart it so the newly selected Xcode reloads its
    # own supported runtimes and destinations.
    subprocess.run(
        ["killall", "-9", "com.apple.CoreSimulator.CoreSimulatorService"],
        check=False,
        capture_output=True,
        text=True,
    )
    time.sleep(2)
    return True


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


def available_ios_runtimes() -> list[tuple[tuple[int, ...], str, str]]:
    payload = simctl_json("runtimes")
    runtimes = payload.get("runtimes", [])
    candidates: list[tuple[tuple[int, ...], str, str]] = []

    if not isinstance(runtimes, list):
        return candidates

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

    return sorted(candidates, reverse=True)


def existing_device_runtime(target_device: str) -> str:
    device_payload = simctl_json("devices", "available")
    devices_by_runtime = device_payload.get("devices", {})
    if not isinstance(devices_by_runtime, dict):
        return ""

    candidates: list[tuple[tuple[int, ...], str]] = []
    for _, version, runtime_identifier in available_ios_runtimes():
        runtime_devices = devices_by_runtime.get(runtime_identifier, [])
        if not isinstance(runtime_devices, list):
            continue

        device_exists = any(
            isinstance(device, dict)
            and device.get("name") == target_device
            and device.get("isAvailable", True) is not False
            for device in runtime_devices
        )
        if device_exists:
            candidates.append((version_key(version), version))

    return max(candidates)[1] if candidates else ""


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


def create_simulator(target_device: str, device_type: str) -> str:
    for _, version, runtime_identifier in available_ios_runtimes():
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
        )
        if result.returncode == 0:
            print(
                f"Created {target_device} simulator with iOS {version}.",
                file=sys.stderr,
            )
            return version

    return ""


def main() -> int:
    if not select_configured_xcode():
        return 1

    target_device = os.environ.get("SIMULATOR_DEVICE", DEFAULT_DEVICE).strip()
    target_device = target_device or DEFAULT_DEVICE

    runtime = existing_device_runtime(target_device)
    if runtime:
        print(runtime)
        return 0

    device_type = device_type_identifier(target_device)
    if not device_type:
        print(
            f"Simulator device type '{target_device}' is not installed in the selected Xcode.",
            file=sys.stderr,
        )
        return 1

    runtime = create_simulator(target_device, device_type)
    if runtime:
        print(runtime)
        return 0

    print(
        f"Unable to create '{target_device}' on any installed iOS runtime.",
        file=sys.stderr,
    )
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
