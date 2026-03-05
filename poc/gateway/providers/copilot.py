"""GitHub Copilot provider adapter (stub).

GitHub Copilot does **not** expose a stable, public REST API for
programmatic chat/completion requests outside of IDE plug-ins and
the official GitHub Copilot Extensions framework.

This module provides a clearly-documented adapter stub so that:
  1. The gateway interface is complete and can be extended later.
  2. Callers receive a descriptive error instead of a cryptic failure.
  3. TODOs mark every point where a real implementation must go once
     a supported API surface becomes available.

When a programmatic Copilot API is available
--------------------------------------------
TODO: Replace the stub body in ``complete()`` with real HTTP calls once
GitHub exposes a stable endpoint.  Expected auth flow:

  - Obtain an OAuth token via the GitHub Device-Flow or use a GitHub App
    Installation token with the ``copilot`` scope (if/when that scope is
    made generally available).
  - Exchange the token at:
      POST https://api.github.com/copilot_internal/v2/token
    (This endpoint is **internal/undocumented** and subject to change.)
  - Use the resulting token to call the Copilot proxy endpoint:
      POST https://copilot-proxy.githubusercontent.com/v1/engines/<engine>/completions
  - Required environment variable (once available):
      GITHUB_COPILOT_TOKEN  – a valid Copilot session/API token

References:
  - https://docs.github.com/en/copilot
  - https://github.com/features/copilot
"""

from typing import Any, Dict, List

from poc.gateway.providers.base import LLMProvider


class CopilotProvider(LLMProvider):
    """Stub adapter for GitHub Copilot.

    This provider is **not yet functional** because GitHub Copilot does
    not provide a documented public API for programmatic completions.

    The stub allows the gateway router to recognise ``provider=copilot``
    and return a clear, actionable error instead of failing silently.
    """

    @property
    def name(self) -> str:
        return "copilot"

    def is_configured(self) -> bool:
        # TODO: When a real Copilot API is available, check for
        # GITHUB_COPILOT_TOKEN (or equivalent) here and return True.
        return False

    async def complete(
        self, model: str, messages: List[Dict[str, str]], **kwargs: Any
    ) -> Dict[str, Any]:
        # TODO: Implement using the GitHub Copilot API once it is publicly
        # available.  See module docstring for the expected auth flow.
        raise NotImplementedError(
            "GitHub Copilot does not currently expose a public API for "
            "programmatic completions.\n"
            "  • For model access, use provider='github' which routes through "
            "GitHub Models (https://models.github.ai).\n"
            "  • Set GITHUB_TOKEN / GH_TOKEN in the environment.\n"
            "  • See poc/README.md for full configuration instructions."
        )

    def health_check(self) -> Dict[str, Any]:
        return {
            "status": "error",
            "provider": self.name,
            "error": (
                "GitHub Copilot programmatic API is not yet available. "
                "Use provider='github' (GitHub Models) instead. "
                "See poc/README.md."
            ),
        }
