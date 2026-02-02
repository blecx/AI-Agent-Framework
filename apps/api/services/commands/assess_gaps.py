"""AssessGaps command handler."""

from typing import Dict, Any
from datetime import datetime, timezone
from .base import CommandHandler


class AssessGapsHandler(CommandHandler):
    """Handler for assess_gaps command."""

    async def propose(
        self, project_key: str, params: Dict[str, Any], llm_service, git_manager
    ) -> Dict[str, Any]:
        """Propose gap assessment."""
        # Check what artifacts exist
        artifacts = git_manager.list_artifacts(project_key)

        # Define required ISO21500 artifacts
        required_artifacts = [
            "project_charter.md",
            "stakeholder_register.md",
            "scope_statement.md",
            "wbs.md",
            "schedule.md",
            "budget.md",
            "quality_plan.md",
            "risk_register.md",
            "communication_plan.md",
            "procurement_plan.md",
        ]

        existing_names = [a["name"] for a in artifacts]
        missing = [name for name in required_artifacts if name not in existing_names]
        present = [name for name in required_artifacts if name in existing_names]

        # Render prompt
        prompt = llm_service.render_prompt(
            "assess_gaps.j2",
            {
                "project_key": project_key,
                "missing_artifacts": missing,
                "present_artifacts": present,
            },
        )

        # Get LLM response
        messages = [
            {
                "role": "system",
                "content": "You are an ISO 21500 project management expert.",
            },
            {"role": "user", "content": prompt},
        ]
        llm_response = await llm_service.chat_completion(messages)

        # Generate gap report
        gap_report = llm_service.render_output(
            "gap_report.md",
            {
                "project_key": project_key,
                "missing_artifacts": missing,
                "present_artifacts": present,
                "llm_analysis": llm_response,
                "timestamp": datetime.now(timezone.utc)
                .isoformat()
                .replace("+00:00", "Z"),
            },
        )

        # Prepare file change
        file_changes = [
            {
                "path": "reports/gap_assessment.md",
                "operation": "create",
                "diff": git_manager.get_diff(
                    project_key, "reports/gap_assessment.md", gap_report
                ),
                "content": gap_report,
            }
        ]

        return {
            "assistant_message": f"Gap assessment completed. Found {len(missing)} missing artifacts out of {len(required_artifacts)} required.",
            "file_changes": file_changes,
            "draft_commit_message": f"[{project_key}] Add gap assessment report",
        }
