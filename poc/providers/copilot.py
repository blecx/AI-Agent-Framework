"""GitHub Copilot upstream provider.

Calls the GitHub Copilot chat API, which exposes an OpenAI-compatible surface
at ``https://api.githubcopilot.com``.

Configuration (via environment variables):
    COPILOT_API_KEY   – Required.  GitHub Copilot / Models API token.
                        Can also be supplied as a Docker secret mounted at
                        ``/run/secrets/copilot_api_key``.
    COPILOT_BASE_URL  – Optional.  Defaults to https://api.githubcopilot.com
    COPILOT_TIMEOUT   – Optional.  HTTP timeout in seconds (default: 60).
"""

import os
from pathlib import Path
from typing import Any, Dict, List

import httpx

from poc.providers.base import LLMProvider

_DEFAULT_BASE_URL = "https://api.githubcopilot.com"
_SECRET_PATH = Path("/run/secrets/copilot_api_key")


def _resolve_api_key() -> str:
    """Return the Copilot API key from env-var or Docker secret."""
    key = os.environ.get("COPILOT_API_KEY", "").strip()
    if key:
        return key
    if _SECRET_PATH.exists():
        return _SECRET_PATH.read_text().strip()
    return ""


def _looks_like_placeholder(key: str) -> bool:
    lowered = key.lower()
    return not key or lowered in {
        "your-api-key-here",
        "your-token-here",
        "changeme",
    }


class CopilotProvider(LLMProvider):
    """Upstream provider that forwards requests to the GitHub Copilot API."""

    def __init__(self) -> None:
        self._api_key: str = _resolve_api_key()
        self._base_url: str = os.environ.get(
            "COPILOT_BASE_URL", _DEFAULT_BASE_URL
        ).rstrip("/")
        self._timeout: float = float(os.environ.get("COPILOT_TIMEOUT", "60"))
        self._last_error: str = ""

    @property
    def is_configured(self) -> bool:
        return bool(self._api_key) and not _looks_like_placeholder(self._api_key)

    def _validate_config(self) -> None:
        """Raise ``ValueError`` when the provider is not properly configured."""
        if not self.is_configured:
            raise ValueError(
                "Copilot provider is not configured: COPILOT_API_KEY environment "
                "variable (or Docker secret /run/secrets/copilot_api_key) must be "
                "set to a valid GitHub Copilot / Models API token."
            )

    async def chat_completion(
        self,
        messages: List[Dict[str, str]],
        model: str,
        temperature: float = 0.7,
        max_tokens: int = 4096,
        **kwargs: Any,
    ) -> Dict[str, Any]:
        """Forward *messages* to the Copilot API and return the response."""
        self._validate_config()

        url = f"{self._base_url}/chat/completions"
        headers = {
            "Authorization": f"Bearer {self._api_key}",
            "Content-Type": "application/json",
            "Accept": "application/json",
            # Copilot API version header (mirrors what VS Code sends)
            "Copilot-Integration-Id": "vscode-chat",
        }
        payload: Dict[str, Any] = {
            "model": model,
            "messages": messages,
            "temperature": temperature,
            "max_tokens": max_tokens,
        }
        payload.update(kwargs)

        try:
            async with httpx.AsyncClient(timeout=self._timeout) as client:
                response = await client.post(url, headers=headers, json=payload)
                response.raise_for_status()
                data = response.json()
                self._last_error = ""
                return data
        except httpx.HTTPStatusError as exc:
            self._last_error = (
                f"HTTP {exc.response.status_code}: {exc.response.text[:200]}"
            )
            raise RuntimeError(
                f"Copilot API returned an error – {self._last_error}"
            ) from exc
        except Exception as exc:
            self._last_error = str(exc)
            raise RuntimeError(
                f"Copilot API call failed – {self._last_error}"
            ) from exc

    def health(self) -> Dict[str, Any]:
        configured = self.is_configured
        return {
            "configured": configured,
            "available": configured and not self._last_error,
            "message": (
                "Copilot provider is configured."
                if configured
                else (
                    "Copilot provider is NOT configured: set COPILOT_API_KEY "
                    "or mount Docker secret /run/secrets/copilot_api_key."
                )
            ),
            "base_url": self._base_url,
            "last_error": self._last_error or None,
        }
