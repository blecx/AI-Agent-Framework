#!/usr/bin/env python3
"""Prompt quality checks for .github/prompts markdown files."""

from __future__ import annotations

import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PROMPTS_DIR = ROOT / ".github" / "prompts"

AGENTS_DIR = PROMPTS_DIR / "agents"

KEY_PROMPTS = [
    AGENTS_DIR / "create-issue.md",
    AGENTS_DIR / "resolve-issue-dev.md",
    AGENTS_DIR / "pr-merge.md",
    AGENTS_DIR / "tutorial.md",
    PROMPTS_DIR / "multi-step-planning.md",
    PROMPTS_DIR / "cross-repo-coordination.md",
]

REQUIRED_HEADERS = [
    "## Objective",
    "## When to Use",
    "## When Not to Use",
    "## Output Format",
    "## Completion Criteria",
]

LINK_RE = re.compile(r"\[[^\]]+\]\(([^)]+)\)")


def _read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def _check_agent_line_limits(errors: list[str]) -> None:
    for file in sorted(AGENTS_DIR.glob("*.md")):
        if file.name == "README.md":
            continue
        line_count = len(_read_text(file).splitlines())
        if line_count > 100 and "Line limit exception:" not in _read_text(file):
            errors.append(f"{file}: {line_count} lines (>100) without explicit exception")


def _check_required_sections(errors: list[str]) -> None:
    for file in KEY_PROMPTS:
        text = _read_text(file)
        missing = [header for header in REQUIRED_HEADERS if header not in text]
        if missing:
            errors.append(f"{file}: missing required sections: {', '.join(missing)}")


def _check_broken_local_links(errors: list[str]) -> None:
    all_prompt_files = list(PROMPTS_DIR.rglob("*.md"))
    for file in all_prompt_files:
        text = _read_text(file)
        for target in LINK_RE.findall(text):
            if target.startswith(("http://", "https://", "mailto:", "#")):
                continue
            target_path = target.split("#", 1)[0].strip()
            if not target_path:
                continue
            if any(token in target_path for token in ("STEP-N", "step-N", "[", "]", "<", ">")):
                continue
            candidates = [
                (file.parent / target_path).resolve(),
                (ROOT / target_path).resolve(),
            ]
            if not any(candidate.exists() for candidate in candidates):
                errors.append(f"{file}: broken link -> {target}")


def _is_strict_mode() -> bool:
    return "--strict" in sys.argv


def main() -> int:
    errors: list[str] = []

    _check_agent_line_limits(errors)
    _check_required_sections(errors)
    _check_broken_local_links(errors)

    if errors:
        mode = "strict" if _is_strict_mode() else "baseline"
        print(f"⚠️ Prompt quality findings ({mode} mode):")
        for err in errors:
            print(f"- {err}")
        if _is_strict_mode():
            return 1
        print("✅ Baseline mode: findings reported, non-blocking exit")
        return 0

    print("✅ Prompt quality checks passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
