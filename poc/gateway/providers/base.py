"""Abstract base interface for LLM providers in the gateway PoC."""

from abc import ABC, abstractmethod
from typing import Any, Dict, List


class LLMProvider(ABC):
    """Abstract interface that every upstream LLM provider must implement."""

    @property
    @abstractmethod
    def name(self) -> str:
        """Short identifier for this provider (e.g. 'stub', 'github', 'copilot')."""

    @abstractmethod
    def is_configured(self) -> bool:
        """Return True when the provider has valid credentials / can accept requests."""

    @abstractmethod
    async def complete(
        self, model: str, messages: List[Dict[str, str]], **kwargs: Any
    ) -> Dict[str, Any]:
        """Send a chat-completion request and return the raw response dict.

        Args:
            model: Model identifier to use for the completion.
            messages: List of ``{"role": ..., "content": ...}`` dicts.
            **kwargs: Provider-specific keyword arguments (temperature, max_tokens, …).

        Returns:
            A dict that resembles the OpenAI chat-completion response schema.
        """

    @abstractmethod
    def health_check(self) -> Dict[str, Any]:
        """Return a health-status dict with at least ``{"status": "ok"|"error", "provider": name}``."""
