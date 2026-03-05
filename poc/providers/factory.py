"""Provider factory and config validation for the PoC gateway.

Selection logic (checked in order):
1. ``GATEWAY_PROVIDER`` env-var   – ``copilot`` | ``stub``
2. If provider is ``copilot`` but ``COPILOT_API_KEY`` is missing/placeholder
   AND ``GATEWAY_FALLBACK_TO_STUB=true``, fall back to ``StubProvider``.
3. If provider is ``copilot`` but key is missing and fallback is disabled,
   raise ``ValueError`` (startup fails with a clear message).
"""

import os
from typing import Tuple

from poc.providers.base import LLMProvider
from poc.providers.copilot import CopilotProvider
from poc.providers.stub import StubProvider


def _env_flag(name: str, default: bool = False) -> bool:
    val = os.environ.get(name, "").strip().lower()
    if val in ("1", "true", "yes"):
        return True
    if val in ("0", "false", "no"):
        return False
    return default


def build_provider() -> Tuple[LLMProvider, str]:
    """Construct and return the active ``LLMProvider`` plus a status message.

    Returns:
        ``(provider, status_message)`` – status_message is suitable for
        logging at startup.

    Raises:
        ``ValueError`` if the requested provider cannot be initialised and
        ``GATEWAY_FALLBACK_TO_STUB`` is *not* enabled.
    """
    requested = os.environ.get("GATEWAY_PROVIDER", "copilot").strip().lower()
    fallback_enabled = _env_flag("GATEWAY_FALLBACK_TO_STUB", default=False)

    if requested == "stub":
        return StubProvider(), "Provider: stub (explicitly requested)"

    if requested == "copilot":
        provider = CopilotProvider()
        if provider.is_configured:
            return provider, "Provider: copilot (configured)"

        if fallback_enabled:
            return (
                StubProvider(),
                "Provider: stub (fallback – Copilot key missing; "
                "set COPILOT_API_KEY to enable Copilot upstream)",
            )

        raise ValueError(
            "Copilot provider requested (GATEWAY_PROVIDER=copilot) but "
            "COPILOT_API_KEY is not set. "
            "Either supply the key or set GATEWAY_FALLBACK_TO_STUB=true to "
            "use the offline stub instead."
        )

    raise ValueError(
        f"Unknown provider '{requested}'. "
        "Supported values for GATEWAY_PROVIDER: copilot, stub."
    )
