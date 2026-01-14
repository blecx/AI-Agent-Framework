"""
Base skill protocol and result types for cognitive skills.
"""

from typing import Protocol, Any, Dict, Optional
from pydantic import BaseModel
from datetime import datetime


class SkillResult(BaseModel):
    """Standardized skill execution result."""

    success: bool
    data: Optional[Any] = None
    message: str = ""
    timestamp: str = datetime.utcnow().isoformat()
    metadata: Dict[str, Any] = {}


class Skill(Protocol):
    """Protocol defining the interface for cognitive skills."""

    name: str
    version: str
    description: str

    def execute(self, agent_id: str, params: Dict[str, Any], **kwargs) -> SkillResult:
        """
        Execute the skill with given parameters.

        Args:
            agent_id: Unique identifier for the agent
            params: Skill-specific parameters
            **kwargs: Additional context (e.g., git_manager)

        Returns:
            SkillResult with execution outcome
        """
        ...
