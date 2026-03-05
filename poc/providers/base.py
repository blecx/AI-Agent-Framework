"""Abstract base interface for LLM upstream providers."""

from abc import ABC, abstractmethod
from typing import Any, Dict, List


class LLMProvider(ABC):
    """Abstract LLM provider interface.

    All upstream providers (Copilot, stub, …) must implement this interface.
    The gateway selects a concrete provider at startup based on configuration.
    """

    @abstractmethod
    async def chat_completion(
        self,
        messages: List[Dict[str, str]],
        model: str,
        temperature: float = 0.7,
        max_tokens: int = 4096,
        **kwargs: Any,
    ) -> Dict[str, Any]:
        """Perform a chat-completion request.

        Returns an OpenAI-compatible response dict
        (``choices[0].message.content`` populated).
        """

    @abstractmethod
    def health(self) -> Dict[str, Any]:
        """Return a health/status snapshot for this provider.

        The dict MUST include at least:
        - ``configured``  (bool): provider is minimally configured
        - ``available``   (bool): provider is reachable / functional
        - ``message``     (str):  human-readable status summary
        """
