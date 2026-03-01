#!/usr/bin/env python3
"""Validate VS Code subagent auto-approve settings against .github/agents.

Checks the primary workspace settings file and, when present, the external
client workspace settings file:
- .vscode/settings.json (required)
- _external/AI-Agent-Framework-Client/.vscode/settings.json (optional)

Expected names are derived from `.github/agents/*.agent.md` plus required
runtime names that are not represented as `.agent.md` files.
"""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
AGENTS_DIR = ROOT / ".github" / "agents"

SETTINGS_FILES = [
    {"path": ROOT / ".vscode" / "settings.json", "required": True},
    {
        "path": ROOT / "_external" / "AI-Agent-Framework-Client" / ".vscode" / "settings.json",
        "required": False,
    },
]

REQUIRED_RUNTIME_NAMES = {
    "AUTOMATIONS",
}


def _strip_jsonc(text: str) -> str:
    text = re.sub(r"/\*.*?\*/", "", text, flags=re.S)
    text = re.sub(r"^\s*//.*$", "", text, flags=re.M)
    return text


def _load_jsonc(path: Path) -> dict:
    raw = path.read_text(encoding="utf-8")
    return json.loads(_strip_jsonc(raw))


def _expected_subagent_names() -> set[str]:
    names = {
        path.name.removesuffix(".agent.md")
        for path in AGENTS_DIR.glob("*.agent.md")
    }
    names.update(REQUIRED_RUNTIME_NAMES)
    return names


def _approved_names(settings: dict) -> set[str]:
    block = settings.get("chat.tools.subagent.autoApprove", {})
    if not isinstance(block, dict):
        return set()
    return {key for key, value in block.items() if value is True}


def main() -> int:
    expected = _expected_subagent_names()
    errors: list[str] = []

    if not expected:
        print("⚠️ No expected subagent names discovered.")
        return 1

    for settings_meta in SETTINGS_FILES:
        settings_path = settings_meta["path"]
        required = settings_meta["required"]

        if not settings_path.exists():
            if required:
                errors.append(f"Missing settings file: {settings_path}")
            else:
                print(f"ℹ️ Optional settings file not found (skipping): {settings_path}")
            continue

        settings = _load_jsonc(settings_path)
        approved = _approved_names(settings)

        missing = sorted(expected - approved)
        extra = sorted(approved - expected)

        if missing:
            errors.append(
                f"{settings_path}: missing subagent auto-approvals: {', '.join(missing)}"
            )
        if extra:
            print(f"ℹ️ {settings_path}: extra approved names (allowed): {', '.join(extra)}")

    if errors:
        print("❌ Subagent auto-approve consistency check failed")
        for err in errors:
            print(f"- {err}")
        return 1

    print("✅ Subagent auto-approve consistency check passed")
    print(f"Expected names: {', '.join(sorted(expected))}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
