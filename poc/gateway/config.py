"""Gateway configuration.

Config is loaded from (in order of priority):
1. Environment variable ``LLM_GATEWAY_CONFIG`` – path to a JSON file.
2. ``configs/llm.default.json`` in the repository root (fallback).
3. Hard-coded defaults (stub provider, no credentials needed).

Environment variables (all optional):
    LLM_GATEWAY_PROVIDER   – ``github`` | ``copilot`` | ``stub``
    LLM_GATEWAY_BASE_URL   – base URL for the upstream provider
    LLM_GATEWAY_API_KEY    – API key / token (prefer env token vars)
    LLM_GATEWAY_MODEL      – default model to use
    LLM_GATEWAY_TIMEOUT    – HTTP timeout in seconds (default: 60)
    GITHUB_TOKEN / GH_TOKEN / GITHUB_PAT – preferred GitHub token sources
"""

from __future__ import annotations

import json
import os
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, Optional


_DEFAULT_PROVIDER = "stub"
_DEFAULT_MODEL = "openai/gpt-4o-mini"
_DEFAULT_TIMEOUT = 60.0
_DEFAULT_GITHUB_BASE_URL = "https://models.github.ai/inference"


@dataclass
class GatewayConfig:
    """Holds all runtime configuration for the LLM gateway."""

    # Provider identifier: "stub" | "github" | "copilot"
    provider: str = _DEFAULT_PROVIDER

    # Upstream base URL (provider-specific default if empty)
    base_url: str = ""

    # API key / token.  Prefer env variables; avoid writing secrets to disk.
    api_key: str = ""

    # Default model used when the caller does not specify one
    default_model: str = _DEFAULT_MODEL

    # HTTP timeout (seconds)
    timeout: float = _DEFAULT_TIMEOUT

    # Model policy: maps logical roles to model IDs
    # e.g. {"planning": "openai/gpt-4o", "coding": "openai/gpt-4o-mini"}
    model_policy: Dict[str, str] = field(default_factory=dict)

    # ---------------------------------------------------------------------------
    # Factory helpers
    # ---------------------------------------------------------------------------

    @classmethod
    def from_env(cls) -> "GatewayConfig":
        """Build config from environment variables (no file I/O)."""
        provider = os.environ.get("LLM_GATEWAY_PROVIDER", _DEFAULT_PROVIDER).lower()
        base_url = os.environ.get("LLM_GATEWAY_BASE_URL", "")
        api_key = os.environ.get("LLM_GATEWAY_API_KEY", "")
        model = os.environ.get("LLM_GATEWAY_MODEL", _DEFAULT_MODEL)
        timeout_str = os.environ.get("LLM_GATEWAY_TIMEOUT", str(_DEFAULT_TIMEOUT))
        try:
            timeout = float(timeout_str)
            if timeout <= 0:
                timeout = _DEFAULT_TIMEOUT
        except ValueError:
            timeout = _DEFAULT_TIMEOUT

        return cls(
            provider=provider,
            base_url=base_url,
            api_key=api_key,
            default_model=model,
            timeout=timeout,
        )

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "GatewayConfig":
        """Build config from a plain dict (e.g. loaded from JSON)."""
        provider = str(data.get("provider", _DEFAULT_PROVIDER)).lower()
        base_url = str(data.get("base_url", ""))
        api_key = str(data.get("api_key", ""))
        model = str(data.get("model", _DEFAULT_MODEL))
        try:
            timeout = float(data.get("timeout", _DEFAULT_TIMEOUT))
            if timeout <= 0:
                timeout = _DEFAULT_TIMEOUT
        except (TypeError, ValueError):
            timeout = _DEFAULT_TIMEOUT

        model_policy: Dict[str, str] = {}
        roles = data.get("roles")
        if isinstance(roles, dict):
            for role, role_cfg in roles.items():
                if isinstance(role_cfg, dict) and "model" in role_cfg:
                    model_policy[role] = str(role_cfg["model"])

        return cls(
            provider=provider,
            base_url=base_url,
            api_key=api_key,
            default_model=model,
            timeout=timeout,
            model_policy=model_policy,
        )

    @classmethod
    def load(cls, config_path: Optional[str] = None) -> "GatewayConfig":
        """Load config with the full resolution chain.

        Priority:
        1. Explicit ``config_path`` argument
        2. ``LLM_GATEWAY_CONFIG`` environment variable
        3. ``LLM_CONFIG_PATH`` environment variable (shared with agents)
        4. ``configs/llm.default.json`` repo-root fallback
        5. Pure env-var config (``from_env``)
        """
        path = _resolve_config_path(config_path)
        if path is not None and path.exists():
            with open(path) as fh:
                data = json.load(fh)
            cfg = cls.from_dict(data)
            # env var overrides always win over file values
            _apply_env_overrides(cfg)
            return cfg

        # Fall back to env-only config
        cfg = cls.from_env()
        return cfg

    # ---------------------------------------------------------------------------
    # Convenience
    # ---------------------------------------------------------------------------

    def resolved_base_url(self) -> str:
        """Return the effective base URL for the configured provider."""
        if self.base_url:
            return self.base_url
        if self.provider == "github":
            return _DEFAULT_GITHUB_BASE_URL
        return ""

    def model_for_role(self, role: str) -> str:
        """Return the model ID for a logical role, falling back to default."""
        return self.model_policy.get(role, self.default_model)


# ---------------------------------------------------------------------------
# Internal helpers
# ---------------------------------------------------------------------------


def _resolve_config_path(explicit: Optional[str]) -> Optional[Path]:
    if explicit:
        return Path(explicit)

    env_path = os.environ.get("LLM_GATEWAY_CONFIG") or os.environ.get("LLM_CONFIG_PATH")
    if env_path:
        return Path(env_path)

    # Try repo-root default (works when running from workspace root)
    default = Path("configs/llm.default.json")
    if default.exists():
        return default

    return None


def _apply_env_overrides(cfg: GatewayConfig) -> None:
    """Mutate *cfg* in-place with any env var overrides present."""
    if v := os.environ.get("LLM_GATEWAY_PROVIDER"):
        cfg.provider = v.lower()
    if v := os.environ.get("LLM_GATEWAY_BASE_URL"):
        cfg.base_url = v
    if v := os.environ.get("LLM_GATEWAY_API_KEY"):
        cfg.api_key = v
    if v := os.environ.get("LLM_GATEWAY_MODEL"):
        cfg.default_model = v
    if v := os.environ.get("LLM_GATEWAY_TIMEOUT"):
        try:
            t = float(v)
            if t > 0:
                cfg.timeout = t
        except ValueError:
            pass
