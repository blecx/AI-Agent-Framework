"""Provider selection and request routing logic for the LLM gateway.

The ``GatewayRouter`` is responsible for:
  1. Instantiating the correct ``LLMProvider`` based on the active config.
  2. Resolving which model to use for a given request (hub model policy).
  3. Delegating ``complete()`` calls to the selected provider.
"""

from typing import Any, Dict, List, Optional

from poc.gateway.config import GatewayConfig
from poc.gateway.providers.base import LLMProvider
from poc.gateway.providers.copilot import CopilotProvider
from poc.gateway.providers.github_models import GitHubModelsProvider
from poc.gateway.providers.stub import StubProvider


def _build_provider(config: GatewayConfig) -> LLMProvider:
    """Instantiate the correct provider for the given config."""
    provider_id = config.provider.lower()

    if provider_id == "github":
        return GitHubModelsProvider(
            api_key=config.api_key or None,
            base_url=config.resolved_base_url(),
            timeout=config.timeout,
        )

    if provider_id == "copilot":
        return CopilotProvider()

    if provider_id == "stub":
        return StubProvider()

    # Unknown provider – fall back to stub with a warning
    import warnings

    warnings.warn(
        f"Unknown LLM provider '{provider_id}'. Falling back to stub provider. "
        "Set LLM_GATEWAY_PROVIDER to 'github', 'copilot', or 'stub'.",
        RuntimeWarning,
        stacklevel=2,
    )
    return StubProvider()


class GatewayRouter:
    """Routes LLM requests to the appropriate upstream provider.

    Usage::

        config = GatewayConfig.load()
        router = GatewayRouter(config)

        # Simple completion
        response = await router.complete(messages=[{"role": "user", "content": "Hello"}])

        # Role-based routing (uses model_policy from config)
        response = await router.complete_for_role("planning", messages=[...])
    """

    def __init__(self, config: GatewayConfig) -> None:
        self._config = config
        self._provider: Optional[LLMProvider] = None

    # ------------------------------------------------------------------
    # Provider selection
    # ------------------------------------------------------------------

    def select_provider(self) -> LLMProvider:
        """Return the active provider, lazily instantiated.

        If the configured provider reports ``is_configured() == False``
        (e.g. missing credentials), the router transparently falls back
        to the ``StubProvider`` so the gateway remains operational for
        local development without any credentials.
        """
        if self._provider is None:
            candidate = _build_provider(self._config)
            if not candidate.is_configured():
                import warnings

                warnings.warn(
                    f"Provider '{candidate.name}' is not configured "
                    "(missing credentials). Falling back to stub provider for "
                    "local development. Set the required credentials or "
                    "LLM_GATEWAY_PROVIDER=stub to silence this warning.",
                    RuntimeWarning,
                    stacklevel=2,
                )
                self._provider = StubProvider()
            else:
                self._provider = candidate
        return self._provider

    def select_provider_for_request(
        self, requested_model: Optional[str] = None
    ) -> LLMProvider:
        """Select provider, optionally checking that *requested_model* is reachable.

        Currently the gateway uses a single provider at a time, so the
        model is passed through to the provider unchanged.  The
        ``requested_model`` parameter is reserved for future multi-provider
        routing where different models might be served by different backends.
        """
        return self.select_provider()

    # ------------------------------------------------------------------
    # Model resolution
    # ------------------------------------------------------------------

    def resolve_model(
        self,
        requested_model: Optional[str] = None,
        role: Optional[str] = None,
    ) -> str:
        """Return the effective model ID for a request.

        Priority:
        1. ``requested_model`` – explicit caller override
        2. ``role`` – lookup in model_policy (e.g. "planning" → gpt-4o)
        3. config default_model
        """
        if requested_model:
            return requested_model
        if role:
            return self._config.model_for_role(role)
        return self._config.default_model

    # ------------------------------------------------------------------
    # Completion helpers
    # ------------------------------------------------------------------

    async def complete(
        self,
        messages: List[Dict[str, str]],
        model: Optional[str] = None,
        role: Optional[str] = None,
        **kwargs: Any,
    ) -> Dict[str, Any]:
        """Route a completion request to the selected provider.

        Args:
            messages: Conversation history as list of role/content dicts.
            model: Optional explicit model ID override.
            role: Optional logical role (``planning``, ``coding``, ``review``).
                  Used to look up the hub model policy when *model* is not given.
            **kwargs: Extra args forwarded to the provider (temperature, etc.).
        """
        provider = self.select_provider_for_request(model)
        effective_model = self.resolve_model(model, role)
        return await provider.complete(effective_model, messages, **kwargs)

    async def complete_for_role(
        self,
        role: str,
        messages: List[Dict[str, str]],
        **kwargs: Any,
    ) -> Dict[str, Any]:
        """Convenience wrapper: route by agent role.

        Equivalent to ``complete(messages, role=role, **kwargs)``.
        """
        return await self.complete(messages, role=role, **kwargs)

    # ------------------------------------------------------------------
    # Health
    # ------------------------------------------------------------------

    def health(self) -> Dict[str, Any]:
        """Return health information for the currently selected provider."""
        provider = self.select_provider()
        result = provider.health_check()
        result["default_model"] = self._config.default_model
        result["model_policy"] = self._config.model_policy
        return result
