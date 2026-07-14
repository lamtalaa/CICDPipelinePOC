#!/usr/bin/env python3
"""Post a compact CI/CD Adaptive Card to a Microsoft Teams Workflow webhook."""

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
    return