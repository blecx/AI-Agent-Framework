"""Model routing: map hub-level policy tiers to concrete Copilot model IDs.

Policy tiers (case-insensitive):
    small   – fast, cheap model suitable for classification / summarization
    medium  – balanced capability/cost (default)
    large   – most capable model for complex reasoning tasks

The mapping can be overridden per-tier with environment variables:
    COPILOT_MODEL_SMALL   (default: gpt-4o-mini)
    COPILOT_MODEL_MEDIUM  (default: gpt-4o)
    COPILOT_MODEL_LARGE   (default: o3-mini)

An explicit model name passed in a request always takes precedence over the
policy-based mapping.

Example explicit model names accepted by the Copilot API:
    gpt-4o, gpt-4o-mini, o3-mini, o1-mini, o1-preview, claude-3.5-sonnet
"""

import os
from typing import Dict

# --- Defaults ----------------------------------------------------------------

_DEFAULT_SMALL = "gpt-4o-mini"
_DEFAULT_MEDIUM = "gpt-4o"
_DEFAULT_LARGE = "o3-mini"

POLICY_TIERS = ("small", "medium", "large")


def get_model_map() -> Dict[str, str]:
    """Return the active tier → model-id mapping (respecting env overrides)."""
    return {
        "small": os.environ.get("COPILOT_MODEL_SMALL", _DEFAULT_SMALL),
        "medium": os.environ.get("COPILOT_MODEL_MEDIUM", _DEFAULT_MEDIUM),
        "large": os.environ.get("COPILOT_MODEL_LARGE", _DEFAULT_LARGE),
    }


def resolve_model(model: str) -> str:
    """Resolve *model* to a concrete Copilot model ID.

    Resolution order:
    1. If *model* matches a known policy tier (small / medium / large),
       return the mapped model ID.
    2. Otherwise pass *model* through unchanged (explicit model name).

    Args:
        model: Policy tier name or explicit Copilot model identifier.

    Returns:
        Concrete model ID string to send to the upstream API.
    """
    mapping = get_model_map()
    tier = model.strip().lower()
    if tier in mapping:
        return mapping[tier]
    # Explicit model name – return as-is
    return model.strip()
