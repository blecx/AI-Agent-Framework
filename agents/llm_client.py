"""
LLM Client for GitHub Models

Provides GitHub models connection for AI agents.
Configuration loaded from configs/llm.json or configs/llm.default.json
"""

import json
from pathlib import Path
from typing import Optional
from openai import AsyncOpenAI


class LLMClientFactory:
    """Factory for creating LLM clients based on configuration."""
    
    @staticmethod
    def load_config() -> dict:
        """Load LLM configuration from configs/llm.json or default."""
        config_path = Path("configs/llm.json")
        if not config_path.exists():
            config_path = Path("configs/llm.default.json")
        
        if not config_path.exists():
            raise FileNotFoundError(
                "No LLM configuration found. Create configs/llm.json or use configs/llm.default.json"
            )
        
        with open(config_path) as f:
            return json.load(f)
    
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
