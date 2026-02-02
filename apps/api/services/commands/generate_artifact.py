"""GenerateArtifact command handler."""

from typing import Dict, Any
from datetime import datetime, timezone
from .base import CommandHandler


class GenerateArtifactHandler(CommandHandler):
    """Handler for generate_artifact command."""

    async def propose(
        self, project_key: str, params: Dict[str, Any], llm_service, git_manager
    ) -> Dict[str, Any]:
        """Propose artifact generation."""
        artifact_name = params.get("artifact_name", "project_charter.md")
        artifact_type = params.get("artifact_type", "project_charter")

        # Get project info
        project_info = git_manager.read_project_json(project_key)

        # Render prompt
        prompt = llm_service.render_prompt(
            "generate_artifact.j2",
            {
                "project_key": project_key,
                "project_name": project_info.get("name", "Unknown"),
                "artifact_name": artifact_name,
                "artifact_type": artifact_type,
            },
        )

        # Get LLM response
        messages = [
            {
                "role": "system",
                "content": "You are an ISO 21500 project management expert. Generate comprehensive project management artifacts.",
            },
            {"role": "user", "content": prompt},
        ]
        llm_response = await llm_service.chat_completion(messages, max_tokens=2048)

        # Use output template as base and incorporate LLM content
        try:
            template_name = f"{artifact_type}.md"
            artifact_content = llm_service.render_output(
                template_name,
                {
                    "project_key": project_key,
                    "project_name": project_info.get("name", "Unknown"),
                    "generated_content": llm_response,
                    "timestamp": datetime.now(timezone.utc)
                    .isoformat()
                    .replace("+00:00", "Z"),
                },
            )
        except Exception:
            # Fallback if template doesn't exist
            artifact_content = f"""# {artifact_name}

Project: {project_info.get("name", "Unknown")}
Key: {project_key}
Generated: {datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")}

{llm_response}
"""

        file_path = f"artifacts/{artifact_name}"
        file_changes = [
            {
                "path": file_path,
                "operation": "create",
                "diff": git_manager.get_diff(project_key, file_path, artifact_content),
                "content": artifact_content,
            }
        ]

        return {
            "assistant_message": f"Generated artifact: {artifact_name}",
            "file_changes": file_changes,
            "draft_commit_message": f"[{project_key}] Generate {artifact_name}",
        }
