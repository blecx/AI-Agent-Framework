"""Stub / mock LLM provider for local development.

Used automatically when no real provider credentials are present.
Returns canned responses so the gateway can be exercised without
any external API calls.
"""

from typing import Any, Dict, List

from poc.gateway.providers.base import LLMProvider


class StubProvider(LLMProvider):
    """In-process stub that returns pre-canned responses.

    This is the default provider used for local development when no
    upstream credentials are configured.  It never makes network
    requests and is always considered "configured".
    """

    @property
    def name(self) -> str:
        return "stub"

    def is_configured(self) -> bool:
        return True

    async def complete(
        self, model: str, messages: List[Dict[str, str]], **kwargs: Any
    ) -> Dict[str, Any]:
        last_user = next(
            (m["content"] for m in reversed(messages) if m.get("role") == "user"),
            "(no user message)",
        )
        return {
            "id": "stub-completion",
            "object": "chat.completion",
            "model": model,
            "choices": [
                {
                    "index": 0,
                    "message": {
                        "role": "assistant",
                        "content": (
                            f"[stub] Received {len(messages)} message(s). "
                            f'Last user message: "{last_user}"'
                        ),
                    },
                    "finish_reason": "stop",
                }
            ],
            "usage": {"prompt_tokens": 0, "completion_tokens": 0, "total_tokens": 0},
        }

    def health_check(self) -> Dict[str, Any]:
        return {"status": "ok", "provider": self.name, "note": "stub – no real LLM"}
