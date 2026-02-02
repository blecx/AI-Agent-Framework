"""Base command handler interface."""

from abc import ABC, abstractmethod
from typing import Dict, Any, TYPE_CHECKING

if TYPE_CHECKING:
    from ..git_manager import GitManager


class CommandHandler(ABC):
    """Abstract base class for command handlers."""

    @abstractmethod
    async def propose(
        self,
        project_key: str,
        params: Dict[str, Any],
        llm_service,
        git_manager: "GitManager",
    ) -> Dict[str, Any]:
        """
        Generate a proposal for this command.

        Args:
            project_key: Project identifier
            params: Command parameters
            llm_service: LLM service instance
            git_manager: Git manager instance

        Returns:
            Dict containing:
                - assistant_message: Human-readable message
                - file_changes: List of file change dicts
                - draft_commit_message: Proposed commit message
        """
        pass
