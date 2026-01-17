"""
Memory skill for short-term and long-term memory management.
"""

import json
import os
from datetime import datetime, timezone
from typing import Dict, Any
from .base import SkillResult


class MemorySkill:
    """Skill for managing agent memory (short-term and long-term)."""

    name = "memory"
    version = "1.0.0"
    description = "Manage agent short-term and long-term memory"

    def execute(self, agent_id: str, params: Dict[str, Any], **kwargs) -> SkillResult:
        """
        Execute memory operations (get/set).

        Args:
            agent_id: Unique identifier for the agent
            params: {
                "operation": "get" | "set",
                "memory_type": "short_term" | "long_term",
                "data": Optional[dict] - data to set (for "set" operation)
            }
            **kwargs: Must include "docs_path" - base path for document storage

        Returns:
            SkillResult with memory data or operation status
        """
        docs_path = kwargs.get("docs_path")
        if not docs_path:
            return SkillResult(success=False, message="docs_path required in kwargs")

        operation = params.get("operation")
        memory_type = params.get("memory_type")

        if operation not in ["get", "set"]:
            return SkillResult(success=False, message=f"Invalid operation: {operation}")

        if memory_type not in ["short_term", "long_term"]:
            return SkillResult(
                success=False, message=f"Invalid memory_type: {memory_type}"
            )

        memory_dir = os.path.join(docs_path, "agents", agent_id, "memory")
        memory_file = os.path.join(memory_dir, f"{memory_type}.json")

        if operation == "get":
            return self._get_memory(memory_file, memory_type)
        else:  # set
            data = params.get("data")
            if data is None:
                return SkillResult(
                    success=False, message="data required for set operation"
                )
            return self._set_memory(memory_file, memory_type, data, memory_dir)

    def _get_memory(self, memory_file: str, memory_type: str) -> SkillResult:
        """Get memory from file."""
        if not os.path.exists(memory_file):
            return SkillResult(
                success=True,
                data={},
                message=f"No {memory_type} memory found",
            )

        try:
            with open(memory_file, "r") as f:
                memory_data = json.load(f)
            return SkillResult(
                success=True,
                data=memory_data,
                message=f"{memory_type} memory retrieved",
            )
        except Exception as e:
            return SkillResult(success=False, message=f"Error reading memory: {str(e)}")

    def _set_memory(
        self, memory_file: str, memory_type: str, data: dict, memory_dir: str
    ) -> SkillResult:
        """Set memory to file."""
        try:
            os.makedirs(memory_dir, exist_ok=True)

            # Add metadata
            memory_entry = {
                "data": data,
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "updated_at": datetime.now(timezone.utc).isoformat(),
            }

            with open(memory_file, "w") as f:
                json.dump(memory_entry, f, indent=2)

            return SkillResult(
                success=True,
                data=memory_entry,
                message=f"{memory_type} memory updated",
            )
        except Exception as e:
            return SkillResult(success=False, message=f"Error writing memory: {str(e)}")
