"""
LLM service with HTTP adapter for OpenAI-compatible endpoints.
"""
import os
import json
import httpx
from pathlib import Path
from typing import Dict, Any, List, Optional
from jinja2 import Environment, FileSystemLoader


class LLMService:
    """Service for interacting with LLM via HTTP."""
    
    def __init__(self):
        """Initialize LLM service with config."""
        self.config = self._load_config()
        self.client = httpx.AsyncClient(timeout=self.config.get("timeout", 120))
        
        # Set up Jinja2 for prompt templates
        # Resolve templates relative to the installed app layout inside container.
        # When the API is copied into /app, templates are placed at /app/templates.
        # Use parent.parent to reach /app from /app/services
        template_path = Path(__file__).resolve().parent.parent / "templates"
        # Fallback: if templates not found there, try repository-root style (/templates)
        if not template_path.exists():
            template_path = Path(__file__).resolve().parent.parent.parent.parent / "templates"
        self.jinja_env = Environment(loader=FileSystemLoader(str(template_path)))
        
    def _load_config(self) -> Dict[str, Any]:
        """Load LLM configuration from mounted file or use defaults."""
        config_path = os.getenv("LLM_CONFIG_PATH", "/config/llm.json")
        
        # Default LM Studio compatible config
        default_config = {
            "provider": "lmstudio",
            "base_url": "http://host.docker.internal:1234/v1",
            "api_key": "lm-studio",
            "model": "local-model",
            "temperature": 0.7,
            "max_tokens": 4096,
            "timeout": 120
        }
        
        if os.path.exists(config_path):
            try:
                with open(config_path) as f:
                    config = json.load(f)
                    # Merge with defaults
                    return {**default_config, **config}
            except Exception as e:
                print(f"Failed to load config from {config_path}: {e}")
                return default_config
        
        return default_config
    
    async def chat_completion(
        self, 
        messages: List[Dict[str, str]], 
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None
    ) -> str:
        """Make a chat completion request to the LLM."""
        url = f"{self.config['base_url']}/chat/completions"
        
        payload = {
            "model": self.config["model"],
            "messages": messages,
            "temperature": temperature or self.config["temperature"],
            "max_tokens": max_tokens or self.config["max_tokens"]
        }
        
        headers = {
            "Authorization": f"Bearer {self.config['api_key']}",
            "Content-Type": "application/json"
        }
        
        try:
            response = await self.client.post(url, json=payload, headers=headers)
            response.raise_for_status()
            data = response.json()
            return data["choices"][0]["message"]["content"]
        except Exception as e:
            print(f"LLM request failed: {e}")
            # Return a fallback message
            return f"[LLM unavailable: {str(e)}]"
    
    def render_prompt(self, template_name: str, context: Dict[str, Any]) -> str:
        """Render a prompt template with given context."""
        template = self.jinja_env.get_template(f"prompts/iso21500/{template_name}")
        return template.render(**context)
    
    def render_output(self, template_name: str, context: Dict[str, Any]) -> str:
        """Render an output template with given context."""
        template = self.jinja_env.get_template(f"output/iso21500/{template_name}")
        return template.render(**context)
    
    async def close(self):
        """Close HTTP client."""
        await self.client.aclose()
