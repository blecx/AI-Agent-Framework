#!/usr/bin/env python3
"""Validate Context7 guardrails in prompt policy and workspace MCP settings."""

from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

SETTINGS_FILE = ROOT / ".vscode" / "settings.json"
PROMPT_BASELINE_FILE = ROOT / ".github" / "prompts" / "modules" / "prompt-quality-baseline.md"
CREATE_ISSUE_PROMPT = ROOT / ".github" / "prompts" / "agents" / "create-issue.md"
RESOLVE_ISSUE_PROMPT = ROOT / ".github" / "prompts" / "agents" / "resolve-issue-dev.md"

REQUIRED_BASELINE_SNIPPETS = [
    "Context7",
    "external API",
]

REQUIRED_AGENT_SNIPPETS = {
    CREATE_ISSUE_PROMPT: [
        "Context7",
        "docs-grounding",
    ],
    RESOLVE_ISSUE_PROMPT: [
        "Context7",
        "external API",
    ],
}


def _must_contain(path: Path, snippets: list[str], errors: list[str]) -> None:
    if not path.exists():
        errors.append(f"{path}: file missing")
        return
    text = path.read_text(encoding="utf-8")
    missing = [snippet for snippet in snippets if snippet not in text]
    if missing:
        errors.append(f"{path}: missing required snippets: {', '.join(missing)}")


def _check_settings(errors: list[str]) -> None:
    if not SETTINGS_FILE.exists():
        errors.append(f"{SETTINGS_FILE}: file missing")
        return

    try:
        settings = json.loads(SETTINGS_FILE.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        errors.append(f"{SETTINGS_FILE}: invalid JSON ({exc})")
        return

    mcp = settings.get("mcp")
    if not isinstance(mcp, dict):
        errors.append(f"{SETTINGS_FILE}: missing top-level 'mcp' object")
        return

    servers = mcp.get("servers")
    if not isinstance(servers, dict):
        errors.append(f"{SETTINGS_FILE}: missing 'mcp.servers' object")
        return

    context7 = servers.get("context7")
    if not isinstance(context7, dict):
        errors.append(f"{SETTINGS_FILE}: missing 'mcp.servers.context7' entry")
        return

    if context7.get("url") != "http://127.0.0.1:3010/mcp":
        errors.append(
            f"{SETTINGS_FILE}: context7 url must be http://127.0.0.1:3010/mcp"
        )

    headers = context7.get("headers")
    if not isinstance(headers, dict) or headers.get("CONTEXT7_API_KEY") != "${env:CONTEXT7_API_KEY}":
        errors.append(
            f"{SETTINGS_FILE}: context7 headers must map CONTEXT7_API_KEY to ${'{env:CONTEXT7_API_KEY}'}"
        )


def main() -> int:
    errors: list[str] = []

    _check_settings(errors)
    _must_contain(PROMPT_BASELINE_FILE, REQUIRED_BASELINE_SNIPPETS, errors)
    for path, snippets in REQUIRED_AGENT_SNIPPETS.items():
        _must_contain(path, snippets, errors)

    if errors:
        print("❌ Context7 guardrail checks failed:")
        for error in errors:
            print(f"- {error}")
        return 1

    print("✅ Context7 guardrail checks passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
