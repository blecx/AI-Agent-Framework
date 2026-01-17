"""
Learning skill for capturing and managing experience/learning data.
"""

import json
import os
from datetime import datetime, timezone
from typing import Dict, Any
from .base import SkillResult


class LearningSkill:
    """Skill for capturing experiences and learning from outcomes."""

    name = "learning"
    version = "1.0.0"
    description = "Capture and learn from experience events"

    def execute(self, agent_id: str, params: Dict[str, Any], **kwargs) -> SkillResult:
        """
        Execute learning operations (log experience or get summary).

        Args:
            agent_id: Unique identifier for the agent
            params: {
                "operation": "log" | "summary",
                "context": Optional[str] - Context of the experience,
                "action": Optional[str] - Action taken,
                "outcome": Optional[str] - Outcome observed,
                "feedback": Optional[str] - Feedback or reflection,
                "tags": Optional[List[str]] - Tags for categorization
            }
            **kwargs: Must include "docs_path" - base path for document storage

        Returns:
            SkillResult with operation status or summary
        """
        docs_path = kwargs.get("docs_path")
        if not docs_path:
            return SkillResult(success=False, message="docs_path required in kwargs")

        operation = params.get("operation", "log")

        if operation == "log":
            return self._log_experience(agent_id, params, docs_path)
        elif operation == "summary":
            return self._get_summary(agent_id, docs_path)
        else:
            return SkillResult(success=False, message=f"Invalid operation: {operation}")

    def _log_experience(
        self, agent_id: str, params: Dict[str, Any], docs_path: str
    ) -> SkillResult:
        """Log an experience event to NDJSON."""
        context = params.get("context", "")
        action = params.get("action", "")
        outcome = params.get("outcome", "")
        feedback = params.get("feedback", "")
        tags = params.get("tags", [])

        if not context or not action or not outcome:
            return SkillResult(
                success=False,
                message="context, action, and outcome are required for logging",
            )

        learning_dir = os.path.join(docs_path, "agents", agent_id, "learning")
        experience_file = os.path.join(learning_dir, "experience.ndjson")

        try:
            os.makedirs(learning_dir, exist_ok=True)

            experience_entry = {
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "context": context,
                "action": action,
                "outcome": outcome,
                "feedback": feedback,
                "tags": tags,
            }

            # Append to NDJSON file
            with open(experience_file, "a") as f:
                f.write(json.dumps(experience_entry) + "\n")

            return SkillResult(
                success=True,
                data=experience_entry,
                message="Experience logged successfully",
            )
        except Exception as e:
            return SkillResult(
                success=False, message=f"Error logging experience: {str(e)}"
            )

    def _get_summary(self, agent_id: str, docs_path: str) -> SkillResult:
        """Get a summary of learning experiences."""
        learning_dir = os.path.join(docs_path, "agents", agent_id, "learning")
        experience_file = os.path.join(learning_dir, "experience.ndjson")

        if not os.path.exists(experience_file):
            return SkillResult(
                success=True,
                data={
                    "total_experiences": 0,
                    "tags": [],
                    "recent_experiences": [],
                },
                message="No experiences logged yet",
            )

        try:
            experiences = []
            tag_counts = {}

            with open(experience_file, "r") as f:
                for line in f:
                    if line.strip():
                        exp = json.loads(line)
                        experiences.append(exp)

                        # Count tags
                        for tag in exp.get("tags", []):
                            tag_counts[tag] = tag_counts.get(tag, 0) + 1

            # Get most recent 10 experiences
            recent = experiences[-10:] if len(experiences) > 10 else experiences

            summary = {
                "total_experiences": len(experiences),
                "tags": [
                    {"tag": tag, "count": count}
                    for tag, count in sorted(
                        tag_counts.items(), key=lambda x: x[1], reverse=True
                    )
                ],
                "recent_experiences": recent,
            }

            return SkillResult(
                success=True,
                data=summary,
                message=f"Summary of {len(experiences)} experiences",
            )
        except Exception as e:
            return SkillResult(
                success=False, message=f"Error generating summary: {str(e)}"
            )
