"""GitHub Models provider.

Uses the GitHub Models inference endpoint (https://models.github.ai/inference)
which is OpenAI-API-compatible and accessible with a GitHub PAT.

Authentication:
    Set one of the following environment variables:
    - GITHUB_TOKEN   (preferred; set automatically by GitHub Actions)
    - GH_TOKEN
    - GITHUB_PAT

    Alternatively, supply ``api_key`` in the gateway config JSON/env.

Available models (non-exhaustive):
    openai/gpt-4o, openai/gpt-4o-mini, meta/meta-llama-3.1-70b-instruct, …
    Full list: https://github.com/marketplace/models
"""

import os
from typing import Any, Dict, List, Optional

import httpx

from poc.gateway.providers.base import LLMProvider

_DEFAULT_BASE_URL = "https://models.github.ai/inference"
_CHAT_PATH = "/chat/completions"


class GitHubModelsProvider(LLMProvider):
    """GitHub Models inference endpoint (OpenAI-compatible API)."""

    def __init__(
        self,
        api_key: Optional[str] = None,
        base_url: str = _DEFAULT_BASE_URL,
        timeout: float = 60.0,
    ) -> None:
        self._base_url = base_url.rstrip("/")
        self._timeout = timeout
        self._api_key = api_key or self._resolve_token()

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    @staticmethod
    def _resolve_token() -> str:
        """Resolve GitHub token from environment variables."""
        return (
            os.environ.get("GITHUB_TOKEN")
            or os.environ.get("GH_TOKEN")
            or os.environ.get("GITHUB_PAT")
            or ""
        )

    # ------------------------------------------------------------------
    # LLMProvider interface
    # ------------------------------------------------------------------

    @property
    def name(self) -> str:
        return "github"

    def is_configured(self) -> bool:
        """Return True when a non-empty, non-placeholder token is available."""
        token = self._api_key or self._resolve_token()
        return bool(token) and token not in {
            "your-api-key-here",
            "your-token-here",
            "changeme",
        }

    async def complete(
        self, model: str, messages: List[Dict[str, str]], **kwargs: Any
    ) -> Dict[str, Any]:
        if not self.is_configured():
            raise RuntimeError(
                "GitHub Models provider is not configured. "
                "Set GITHUB_TOKEN, GH_TOKEN, or GITHUB_PAT environment variable, "
                "or supply api_key in the gateway config."
            )
        url = f"{self._base_url}{_CHAT_PATH}"
        headers = {
            "Authorization": f"Bearer {self._api_key or self._resolve_token()}",
            "Content-Type": "application/json",
        }
        payload: Dict[str, Any] = {"model": model, "messages": messages}
        payload.update(kwargs)

        async with httpx.AsyncClient(timeout=self._timeout) as client:
            response = await client.post(url, json=payload, headers=headers)
            response.raise_for_status()
            return response.json()

    def health_check(self) -> Dict[str, Any]:
        if self.is_configured():
            return {"status": "ok", "provider": self.name, "base_url": self._base_url}
        return {
            "status": "error",
            "provider": self.name,
            "base_url": self._base_url,
            "error": (
                "No GitHub token found. "
                "Set GITHUB_TOKEN, GH_TOKEN, or GITHUB_PAT."
            ),
        }
