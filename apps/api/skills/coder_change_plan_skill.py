"""Designer skill: coder-facing change plan.

Produces Markdown plus a machine-parsable YAML stub describing issue slices.
"""

from __future__ import annotations

from typing import Any, Dict, List

from .base import SkillResult


class CoderChangePlanSkill:
    name = "coder_change_plan"
    version = "1.1.0"
    description = "Generate a coder-facing change plan (markdown + YAML stubs)."

    def execute(self, agent_id: str, params: Dict[str, Any], **kwargs) -> SkillResult:
        feature = (params.get("feature") or "UI update").strip() or "UI update"
        goal = (params.get("goal") or "Implement approved mockups").strip()
        touched_files = params.get("touched_files") or []

        files_list: List[str] = []
        if isinstance(touched_files, list):
            files_list = [str(f).strip() for f in touched_files if str(f).strip()]

        files_md = ""
        if files_list:
            files_md = "\n" + "\n".join([f"- {p}" for p in files_list])

        yaml_stub = (
            "issues:\n"
            f"  - title: \"{feature}: implementation slice\"\n"
            "    size: S\n"
            "    labels:\n"
            "      - enhancement\n"
            "      - agents\n"
            "      - webui/ux\n"
            "      - size:S\n"
            "    scope_in:\n"
            "      - Implement the UI changes required by the approved mockups\n"
            "      - Keep diff small and reviewable\n"
            "    scope_out:\n"
            "      - New features not in the mockups\n"
            "      - Design system changes\n"
            "    acceptance_criteria:\n"
            "      - UI matches mockup intent\n"
            "      - A11y basics validated (keyboard + labels)\n"
            "      - UX requirement gaps are documented and blocking gaps resolved\n"
            "    validation:\n"
            "      - npm test/lint/build (if frontend)\n"
            "      - pytest (if backend)\n"
        )

        gap_audit = [
            "Map UX requirements to changed files/components",
            "Mark each requirement as pass/gap/unknown",
            "Classify gaps as blocking/non-blocking",
            "Create one issue per blocking gap",
            "Require UX_DECISION: PASS before merge",
        ]

        markdown = (
            f"# Coder Change Plan\n\n"
            f"## Goal\n{goal}\n\n"
            f"## Feature\n{feature}\n\n"
            "## Suggested Approach\n"
            "1. Identify the minimal set of files to touch\n"
            "2. Implement changes in a single small PR\n"
            "3. Run UX requirement gap audit before coding complete\n"
            "4. Add/adjust tests only where required\n\n"
            "## Requirement Gap Audit Checklist\n"
            + "\n".join([f"- {item}" for item in gap_audit])
            + "\n\n"
            "## Likely Files\n"
            f"{files_md if files_md else '- (not specified)'}\n\n"
            "## Issue YAML Stub\n"
            "```yaml\n"
            f"{yaml_stub}"
            "```\n"
        )

        return SkillResult(
            success=True,
            data={
                "markdown": markdown,
                "yaml": yaml_stub,
                "requirement_gap_audit": gap_audit,
            },
            message="Coder change plan generated",
            metadata={"skill": self.name, "agent_id": agent_id},
        )
