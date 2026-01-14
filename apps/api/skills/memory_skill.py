"""
Memory skill for AI agent short-term and long-term memory management.
"""

import json
import os
from typing import Dict, Any
from datetime import datetime, timezone

from .base import SkillMetadata


class MemorySkill:
    """
    Memory skill providing short-term and long-term memory capabilities.
    
    Memory is persisted in the project docs directory using JSON files.
    Each agent has its own memory file.
    """

    def get_metadata(self) -> SkillMetadata:
        """Get memory skill metadata."""
        return SkillMetadata(
            name="memory",
            version="1.0.0",
            description="Manage agent short-term and long-term memory",
            input_schema={
                "type": "object",
                "properties": {
                    "operation": {
                        "type": "string",
                        "enum": ["get", "set"],
                        "description": "Operation to perform"
                    },
                    "short_term": {
                        "type": "object",
                        "description": "Short-term memory data (for set operation)"
                    },
                    "long_term": {
                        "type": "object",
                        "description": "Long-term memory data (for set operation)"
                    }
                },
                "required": ["operation"]
            },
            output_schema={
                "type": "object",
                "properties": {
                    "agent_id": {"type": "string"},
                    "short_term": {"type": "object"},
                    "long_term": {"type": "object"},
                    "metadata": {"type": "object"}
                }
            }
        )

    async def execute(
        self, agent_id: str, input_data: Dict[str, Any], context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Execute memory operation (get or set).
        
        Args:
            agent_id: Agent identifier
            input_data: Contains operation type and optional memory data
            context: Must contain 'git_manager' for persistence
            
        Returns:
            Current memory state
        """
        operation = input_data.get("operation")
        if operation not in ["get", "set"]:
            raise ValueError(f"Invalid operation: {operation}")

        git_manager = context.get("git_manager")
        if not git_manager:
            raise ValueError("git_manager required in context")

        memory_dir = os.path.join(str(git_manager.base_path), "_agents", "memory")
        os.makedirs(memory_dir, exist_ok=True)
        memory_file = os.path.join(memory_dir, f"{agent_id}.json")

        if operation == "get":
            return self._get_memory(agent_id, memory_file)
        else:  # set
            return self._set_memory(
                agent_id,
                memory_file,
                input_data.get("short_term"),
                input_data.get("long_term")
            )

    def _get_memory(self, agent_id: str, memory_file: str) -> Dict[str, Any]:
        """Get current memory state."""
        if not os.path.exists(memory_file):
            return {
                "agent_id": agent_id,
                "short_term": {},
                "long_term": {},
                "metadata": {
                    "created_at": datetime.now(timezone.utc).isoformat(),
                    "updated_at": datetime.now(timezone.utc).isoformat()
                }
            }

        with open(memory_file, 'r') as f:
            return json.load(f)

    def _set_memory(
        self,
        agent_id: str,
        memory_file: str,
        short_term: Dict[str, Any],
        long_term: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Set/merge memory state."""
        current = self._get_memory(agent_id, memory_file)
        
        # Merge updates
        if short_term is not None:
            current["short_term"].update(short_term)
        if long_term is not None:
            current["long_term"].update(long_term)
        
        # Update metadata
        current["metadata"]["updated_at"] = datetime.now(timezone.utc).isoformat()
        
        # Persist
        with open(memory_file, 'w') as f:
            json.dump(current, f, indent=2)
        
        return current
