"""Designer skill: design guidelines.

Produces concise, deterministic Markdown guidelines after a mockup is approved.
"""

from __future__ import annotations

from typing import Any, Dict

from .base import SkillResult


class DesignGuidelinesSkill:
    name = "design_guidelines"
    version = "1.0.0"
    description = "Generate concise UI design guidelines (deterministic markdown)."

    def execute(self, agent_id: str, params: Dict[str, Any], **kwargs) -> SkillResult:
        context = (params.get("context") or "").strip()
        platform = (params.get("platform") or "web").strip() or "web"
        constraints = params.get("constraints") or []

        constraints_md = ""
        if isinstance(constraints, list) and constraints:
            items = "\n".join([f"- {c}" for c in constraints if str(c).strip()])
            if items:
                constraints_md = f"\n\nConstraints:\n{items}"

        markdown = (
            "# Design Guidelines\n\n"
            "## Goals\n"
            "- Preserve approved mockup intent\n"
            "- Prioritize clarity, accessibility, and consistency\n\n"
            "## Layout\n"
            "- Use consistent spacing and alignment\n"
            "- Keep key actions visible without scrolling where possible\n\n"
            "## Typography\n"
            "- Use existing design system text styles\n"
            "- Avoid introducing new fonts or weights\n\n"
            "## Color & Contrast\n"
            "- Use existing theme tokens only\n"
            "- Meet WCAG contrast where applicable\n\n"
            "## Components\n"
            "- Prefer existing components; avoid new bespoke UI\n"
            "- Keep interactions predictable and keyboard-friendly\n\n"
            "## Notes\n"
            f"- Platform: {platform}\n"
        )

        if context:
            markdown += f"- Context: {context}\n"

        if constraints_md:
            markdown += constraints_md + "\n"

        return SkillResult(
            success=True,
            data={
                "markdown": markdown,
                "platform": platform,
            },
            message="Design guidelines generated",
            metadata={"skill": self.name, "agent_id": agent_id},
        )
