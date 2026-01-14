"""
Learning skill for AI agent experience capture and learning.
"""

import json
import os
import uuid
from typing import Dict, Any
from datetime import datetime, timezone

from .base import SkillMetadata


class LearningSkill:
    """
    Learning skill for capturing and storing agent experiences.
    
    Experiences are stored in the project docs directory as NDJSON
    (newline-delimited JSON) for efficient append operations.
    """

    def get_metadata(self) -> SkillMetadata:
        """Get learning skill metadata."""
        return SkillMetadata(
            name="learning",
            version="1.0.0",
            description="Record and learn from agent experiences",
            input_schema={
                "type": "object",
                "properties": {
                    "experience": {
                        "type": "object",
                        "properties": {
                            "input": {
                                "type": "object",
                                "description": "Input that led to experience"
                            },
                            "outcome": {
                                "type": "object",
                                "description": "Observed outcome"
                            },
                            "feedback": {
                                "type": "string",
                                "description": "Feedback on outcome"
                            },
                            "context": {
                                "type": "object",
                                "description": "Context of experience"
                            }
                        },
                        "required": ["input", "outcome"]
                    }
                },
                "required": ["experience"]
            },
            output_schema={
                "type": "object",
                "properties": {
                    "agent_id": {"type": "string"},
                    "experience_id": {"type": "string"},
                    "recorded_at": {"type": "string"},
                    "message": {"type": "string"}
                }
            }
        )

    async def execute(
        self, agent_id: str, input_data: Dict[str, Any], context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Execute learning operation (record experience).
        
        Args:
            agent_id: Agent identifier
            input_data: Contains experience to record
            context: Must contain 'git_manager' for persistence
            
        Returns:
            Confirmation with experience ID
        """
        experience = input_data.get("experience")
        if not experience:
            raise ValueError("experience is required")

        if "input" not in experience or "outcome" not in experience:
            raise ValueError("experience must contain 'input' and 'outcome'")

        git_manager = context.get("git_manager")
        if not git_manager:
            raise ValueError("git_manager required in context")

        # Store experience
        experience_id = str(uuid.uuid4())
        recorded_at = datetime.now(timezone.utc).isoformat()

        experience_entry = {
            "experience_id": experience_id,
            "agent_id": agent_id,
            "recorded_at": recorded_at,
            "input": experience.get("input"),
            "outcome": experience.get("outcome"),
            "feedback": experience.get("feedback"),
            "context": experience.get("context", {})
        }

        self._store_experience(git_manager, agent_id, experience_entry)

        return {
            "agent_id": agent_id,
            "experience_id": experience_id,
            "recorded_at": recorded_at,
            "message": "Experience recorded successfully"
        }

    def _store_experience(
        self, git_manager, agent_id: str, experience: Dict[str, Any]
    ) -> None:
        """Store experience in NDJSON file."""
        experiences_dir = os.path.join(str(git_manager.base_path), "_agents", "experiences")
        os.makedirs(experiences_dir, exist_ok=True)
        
        experiences_file = os.path.join(experiences_dir, f"{agent_id}.ndjson")
        
        # Append to NDJSON file
        with open(experiences_file, 'a') as f:
            f.write(json.dumps(experience) + '\n')
