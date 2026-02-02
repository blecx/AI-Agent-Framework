"""GeneratePlan command handler."""

from typing import Dict, Any
from datetime import datetime, timezone
from .base import CommandHandler


class GeneratePlanHandler(CommandHandler):
    """Handler for generate_plan command."""

    async def propose(
        self, project_key: str, params: Dict[str, Any], llm_service, git_manager
    ) -> Dict[str, Any]:
        """Propose project plan generation."""
        # Get project info
        project_info = git_manager.read_project_json(project_key)

        # Render prompt
        prompt = llm_service.render_prompt(
            "generate_plan.j2",
            {
                "project_key": project_key,
                "project_name": project_info.get("name", "Unknown"),
            },
        )

        # Get LLM response
        messages = [
            {
                "role": "system",
                "content": "You are an ISO 21500 project management expert. Create detailed project schedules.",
            },
            {"role": "user", "content": prompt},
        ]
        llm_response = await llm_service.chat_completion(messages, max_tokens=2048)

        # Generate plan with Mermaid gantt
        plan_content = llm_service.render_output(
            "project_plan.md",
            {
                "project_key": project_key,
                "project_name": project_info.get("name", "Unknown"),
                "llm_schedule": llm_response,
                "timestamp": datetime.now(timezone.utc)
                .isoformat()
                .replace("+00:00", "Z"),
            },
        )

        file_path = "artifacts/schedule.md"
        file_changes = [
            {
                "path": file_path,
                "operation": "create",
                "diff": git_manager.get_diff(project_key, file_path, plan_content),
                "content": plan_content,
            }
        ]

        return {
            "assistant_message": "Project schedule generated with timeline and milestones.",
            "file_changes": file_changes,
            "draft_commit_message": f"[{project_key}] Generate project schedule",
        }
