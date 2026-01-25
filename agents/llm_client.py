"""
LLM Client for GitHub Models

Provides GitHub models connection for AI agents.
Configuration loaded from configs/llm.json or configs/llm.default.json
"""

import json
from pathlib import Path
from typing import Optional, Dict
from openai import AsyncOpenAI

try:
    # Optional: available when using Azure OpenAI / Foundry endpoints
    from openai import AsyncAzureOpenAI  # type: ignore
except Exception:  # pragma: no cover
    AsyncAzureOpenAI = None


class LLMClientFactory:
    """Factory for creating LLM clients based on configuration."""

    @staticmethod
    def get_config_path() -> Path:
        """Return the active LLM config path (prefers configs/llm.json)."""
        config_path = Path("configs/llm.json")
        if config_path.exists():
            return config_path
        config_path = Path("configs/llm.default.json")
        if config_path.exists():
            return config_path
        raise FileNotFoundError(
            "No LLM configuration found. Create configs/llm.json or use configs/llm.default.json"
        )
    
    @staticmethod
    def load_config() -> dict:
        """Load LLM configuration from configs/llm.json or default."""
        config_path = LLMClientFactory.get_config_path()

        with open(config_path) as f:
            return json.load(f)

    @staticmethod
    def get_model_roles() -> Dict[str, str]:
        """Return configured model IDs for planning/coding/review.

        Supports either a single `model` or per-role keys:
        - `planning_model`
        - `coding_model`
        - `review_model`
        """
        try:
            return {
                "planning": LLMClientFactory.get_model_id_for_role("planning"),
                "coding": LLMClientFactory.get_model_id_for_role("coding"),
                "review": LLMClientFactory.get_model_id_for_role("review"),
            }
        except Exception:
            return {
                "planning": "openai/gpt-5.1-codex",
                "coding": "openai/gpt-5.1-codex",
                "review": "openai/gpt-5.1-codex",
            }

    @staticmethod
    def get_startup_report() -> dict:
        """Safe, non-secret model/config info suitable for printing at startup."""
        try:
            config_path = str(LLMClientFactory.get_config_path())
        except Exception:
            config_path = "(missing)"

        try:
            config = LLMClientFactory.load_config()
        except Exception:
            config = {}

        models = LLMClientFactory.get_model_roles()

        role_endpoints = {}
        for role in ["planning", "coding", "review"]:
            try:
                role_cfg = LLMClientFactory.get_role_config(role)
                role_endpoints[role] = {
                    "provider": role_cfg.get("provider", ""),
                    "base_url": role_cfg.get("base_url", ""),
                    "azure_endpoint": role_cfg.get("azure_endpoint", ""),
                }
            except Exception:
                role_endpoints[role] = {}
        return {
            "config_path": config_path,
            "provider": config.get("provider", ""),
            "configured_base_url": config.get("base_url", ""),
            "models": models,
            "role_endpoints": role_endpoints,
        }

    @staticmethod
    def get_role_config(role: str) -> dict:
        """Return the merged config dict for a given role.

        Supported shapes:
        - roles: { planning: {...}, coding: {...}, review: {...} }
        - prefixed keys: planning_model, planning_provider, planning_base_url, ...
        - fallback to top-level keys.
        """
        config = LLMClientFactory.load_config()

        roles = config.get("roles")
        if isinstance(roles, dict) and isinstance(roles.get(role), dict):
            merged = dict(config)
            merged.update(roles.get(role, {}))
            merged.pop("roles", None)
            return merged

        prefix = f"{role}_"
        role_overrides = {
            k[len(prefix):]: v
            for k, v in config.items()
            if isinstance(k, str) and k.startswith(prefix)
        }
        merged = dict(config)
        merged.update(role_overrides)
        return merged

    @staticmethod
    def get_model_id_for_role(role: str) -> str:
        role_config = LLMClientFactory.get_role_config(role)
        model = role_config.get("model", "")
        return model or "openai/gpt-5.1-codex"

    @staticmethod
    def create_client_for_role(role: str) -> AsyncOpenAI:
        """Create an OpenAI-compatible async client for a given role.

        - GitHub Models: provider=github OR base_url contains models.github.ai
        - Foundry/Azure: provider in {foundry, azure, azure_openai} and either:
          - azure_endpoint + api_version (preferred, uses AsyncAzureOpenAI when available)
          - base_url (OpenAI-compatible)
        - Generic OpenAI-compatible: base_url + api_key
        """
        role_config = LLMClientFactory.get_role_config(role)
        provider = (role_config.get("provider") or "").lower()
        base_url = role_config.get("base_url") or ""
        api_key = role_config.get("api_key") or ""

        # GitHub Models
        if provider == "github" or "models.github.ai" in base_url:
            if not api_key or api_key == "your-api-key-here":
                raise ValueError(
                    "GitHub PAT token required for GitHub Models. Set api_key in configs/llm.json."
                )
            return AsyncOpenAI(base_url="https://models.github.ai/inference", api_key=api_key)

        # Foundry / Azure OpenAI
        if provider in {"foundry", "azure", "azure_openai"}:
            azure_endpoint = role_config.get("azure_endpoint") or ""
            api_version = role_config.get("api_version") or ""

            if AsyncAzureOpenAI is not None and azure_endpoint and api_version:
                if not api_key:
                    raise ValueError("Azure OpenAI api_key required for Foundry/Azure provider")
                return AsyncAzureOpenAI(
                    azure_endpoint=azure_endpoint,
                    api_key=api_key,
                    api_version=api_version,
                )

            if base_url:
                if not api_key:
                    raise ValueError("api_key required for OpenAI-compatible base_url")
                return AsyncOpenAI(base_url=base_url, api_key=api_key)

            raise ValueError(
                "Foundry/Azure provider requires either azure_endpoint+api_version or base_url"
            )

        # Generic OpenAI-compatible
        if base_url:
            if not api_key:
                raise ValueError("api_key required for configured base_url")
            return AsyncOpenAI(base_url=base_url, api_key=api_key)

        # Back-compat fallback: GitHub client with existing config values
        return LLMClientFactory.create_github_client(api_key=api_key or None)
    
    @staticmethod
    def create_github_client(api_key: Optional[str] = None) -> AsyncOpenAI:
        """
        Create OpenAI client configured for GitHub Models.
        
        Args:
            api_key: GitHub PAT token. If None, loads from config.
            
        Returns:
            Configured AsyncOpenAI client
        """
        if api_key is None:
            config = LLMClientFactory.load_config()
            api_key = config.get("api_key", "")
            
            if not api_key or api_key == "your-api-key-here":
                raise ValueError(
                    "GitHub PAT token required. Set in configs/llm.json or pass as parameter.\n"
                    "Get your token at: https://github.com/settings/tokens"
                )
        
        return AsyncOpenAI(
            base_url="https://models.github.ai/inference",
            api_key=api_key,
        )
    
    @staticmethod
    def get_recommended_model() -> str:
        """
        Get recommended model for autonomous agent work.
        
        For code generation and reasoning, we recommend:
        - gpt-5.1-codex (DEFAULT) - Advanced coding, repo-aware intelligence (Quality: 0.899)
        - gpt-4.1 - Balanced performance (Quality: 0.844)
        - gpt-4o - Faster operations (Quality: 0.749)
        
        Returns:
            Model ID string
        """
        # Try to load from config first
        try:
            config = LLMClientFactory.load_config()
            model = config.get("model", "")
            if model and model != "your-model-name":
                return model
        except Exception:
            pass
        
        # Default to gpt-5.1-codex (best free model for coding: 0.899 quality)
        return "openai/gpt-5.1-codex"
