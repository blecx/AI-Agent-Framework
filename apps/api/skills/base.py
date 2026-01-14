"""
Base skill protocol and interfaces for extensible AI agent skills.
"""

from typing import Protocol, Dict, Any, Optional
from pydantic import BaseModel


class SkillMetadata(BaseModel):
    """Metadata describing a skill."""

    name: str
    version: str
    description: str
    input_schema: Dict[str, Any]
    output_schema: Dict[str, Any]


class Skill(Protocol):
    """
    Protocol defining the interface that all skills must implement.
    
    Skills are modular capabilities that can be executed by AI agents.
    Each skill has metadata describing its capabilities and schemas,
    and an execute method that performs the skill's functionality.
    """

    def get_metadata(self) -> SkillMetadata:
        """
        Get skill metadata.
        
        Returns:
            SkillMetadata: Metadata describing the skill's capabilities
        """
        ...

    async def execute(
        self, agent_id: str, input_data: Dict[str, Any], context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Execute the skill with given input.
        
        Args:
            agent_id: Identifier of the agent executing the skill
            input_data: Input parameters for skill execution (validated against input_schema)
            context: Execution context including git_manager, llm_service, etc.
            
        Returns:
            Dict containing execution results (conforms to output_schema)
            
        Raises:
            ValueError: If input validation fails or execution parameters are invalid
            Exception: For other execution failures
        """
        ...
