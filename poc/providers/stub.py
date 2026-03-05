"""Stub LLM provider – returns deterministic canned responses.

Used when ``GATEWAY_FALLBACK_TO_STUB=true`` and the configured upstream
(e.g. Copilot) is unavailable, or as the primary provider when no upstream
is configured.
"""

from typing import Any, Dict, List
import time

from poc.providers.base import LLMProvider


class StubProvider(LLMProvider):
    """Offline stub that echoes a fixed completion message.

    Useful for local development and CI without credentials.
    """

    def __init__(self) -> None:
        self._call_count = 0

    async def chat_completion(
        self,
        messages: List[Dict[str, str]],
        model: str,
        temperature: float = 0.7,
        max_tokens: int = 4096,
        **kwargs: Any,
    ) -> Dict[str, Any]:
        self._call_count += 1
        last_user = next(
            (m["content"] for m in reversed(messages) if m.get("role") == "user"),
            "(no user message)",
        )
        content = (
            f"[stub] Received {len(messages)} message(s). "
            f'Last user turn: "{last_user}". '
            f"Requested model: {model}."
        )
        return _openai_response(content, model)

    def health(self) -> Dict[str, Any]:
        return {
            "configured": True,
            "available": True,
            "message": "Stub provider is always available (offline mode).",
            "call_count": self._call_count,
        }


def _openai_response(content: str, model: str) -> Dict[str, Any]:
    """Wrap *content* in a minimal OpenAI-compatible response envelope."""
    return {
        "id": f"chatcmpl-stub-{int(time.time())}",
        "object": "chat.completion",
        "created": int(time.time()),
        "model": model,
        "choices": [
            {
                "index": 0,
                "message": {"role": "assistant", "content": content},
                "finish_reason": "stop",
            }
        ],
        "usage": {"prompt_tokens": 0, "completion_tokens": 0, "total_tokens": 0},
    }
