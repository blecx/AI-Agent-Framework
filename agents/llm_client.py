"""LLM Client for GitHub Models.

This project standardizes on GitHub Models (Copilot) for all agent roles.
Configuration is loaded from the active config (see LLMClientFactory.get_config_path).
"""

import json
import os
import subprocess
from pathlib import Path
from typing import Optional, Dict
from openai import AsyncOpenAI


class LLMClientFactory:
    """Factory for creating LLM clients based on configuration."""

    _cached_github_token: Optional[str] = None

    @staticmethod
    def _looks_like_placeholder(key: str) -> bool:
        if not key:
            return True
        lowered = key.lower().strip()
        return (
            lowered in {"your-api-key-here", "your-token-here", "changeme"}
            or "your_token_here" in lowered
            or "your token here" in lowered
        )

    @staticmethod
    def _get_github_token_from_env() -> str:
        return (
            os.environ.get("GITHUB_TOKEN")
            or os.environ.get("GITHUB_PAT")
            or os.environ.get("GH_TOKEN")
            or ""
        )

    @staticmethod
    def _get_github_token_from_gh_cli() -> str:
        if LLMClientFactory._cached_github_token is not None:
            return LLMClientFactory._cached_github_token

        try:
            result = subprocess.run(
                ["gh", "auth", "token"],
                capture_output=True,
                text=True,
                timeout=5,
            )
            token = (result.stdout or "").strip() if result.returncode == 0 else ""
            if token:
                LLMClientFactory._cached_github_token = token
                return token
        except Exception:
            pass

        LLMClientFactory._cached_github_token = ""
        return ""

    @staticmethod
    def resolve_github_api_key(config_key: str = "") -> str:
        """Resolve GitHub Models API key from config/env/gh-cli in that order."""
        if not LLMClientFactory._looks_like_placeholder(config_key):
            return config_key

        env_token = LLMClientFactory._get_github_token_from_env()
        if env_token:
            return env_token

        cli_token = LLMClientFactory._get_github_token_from_gh_cli()
        if cli_token:
            os.environ.setdefault("GH_TOKEN", cli_token)
            return cli_token

        return config_key

    @staticmethod
    def get_config_path() -> Path:
        """Return the active LLM config path.

        Resolution order:
        1) LLM_CONFIG_PATH env var (recommended; keeps secrets out of git)
        2) /config/llm.json (Docker convention)
        3) configs/llm.json (local override; should remain gitignored)
        4) configs/llm.default.json (repo default)
        """
        env_path = (Path(str(p)).expanduser() if (p := (os.environ.get("LLM_CONFIG_PATH") or "").strip()) else None)
        if env_path is not None:
            resolved = env_path if env_path.is_absolute() else Path.cwd() / env_path
            if resolved.exists():
                return resolved
            raise FileNotFoundError(
                f"LLM_CONFIG_PATH was set but file does not exist: {resolved}"
            )

        docker_path = Path("/config/llm.json")
        if docker_path.exists():
            return docker_path

        config_path = Path("configs/llm.json")
        if config_path.exists():
            return config_path

        config_path = Path("configs/llm.default.json")
        if config_path.exists():
            return config_path

        raise FileNotFoundError(
            "No LLM configuration found. Set LLM_CONFIG_PATH, create configs/llm.json, or use configs/llm.default.json"
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

        Supported:
        - GitHub Models: provider=github OR base_url contains models.github.ai
        """
        role_config = LLMClientFactory.get_role_config(role)
        provider = (role_config.get("provider") or "").lower()
        base_url = role_config.get("base_url") or ""
        api_key = role_config.get("api_key") or ""

        # Allow secrets via environment variables (preferred; avoids writing configs/llm.json).
        # Only override when config is missing/placeholder.
        if LLMClientFactory._looks_like_placeholder(api_key) and (
            provider == "github" or "models.github.ai" in base_url
        ):
            api_key = LLMClientFactory.resolve_github_api_key(api_key)

        # GitHub Models
        if provider == "github" or "models.github.ai" in base_url:
            if LLMClientFactory._looks_like_placeholder(api_key):
                raise ValueError(
                    "GitHub PAT token required for GitHub Models. Set api_key in the active config, export GITHUB_TOKEN/GH_TOKEN, or run `gh auth login` so `gh auth token` can be used automatically."
                )
            return AsyncOpenAI(base_url="https://models.github.ai/inference", api_key=api_key)

        # Everything else is intentionally unsupported in this repo.
        raise ValueError(
            "Unsupported LLM provider/config. This project only supports GitHub Models (provider=github)."
        )
    
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
            api_key = LLMClientFactory.resolve_github_api_key(config.get("api_key", ""))
            
            if LLMClientFactory._looks_like_placeholder(api_key):
                raise ValueError(
                    "GitHub PAT token required. Set in configs/llm.json, export GITHUB_TOKEN/GH_TOKEN, or run `gh auth login`.\n"
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
