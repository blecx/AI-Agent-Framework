"""
LLM service with HTTP adapter for OpenAI-compatible endpoints.
Includes circuit breaker pattern for resilient external API handling.
"""

import os
import json
import httpx
import time
from enum import Enum
from pathlib import Path
from typing import Dict, Any, List, Optional
from jinja2 import Environment, FileSystemLoader
from tenacity import (
    retry,
    stop_after_attempt,
    wait_exponential,
    retry_if_exception_type,
)

try:
    from .monitoring_service import MetricsCollector
except ImportError:
    from monitoring_service import MetricsCollector


class CircuitState(Enum):
    """Circuit breaker states."""

    CLOSED = "closed"  # Normal operation
    OPEN = "open"  # Failures threshold exceeded, rejecting requests
    HALF_OPEN = "half_open"  # Testing if service recovered


class CircuitBreaker:
    """
    Lightweight circuit breaker implementation.

    States:
    - CLOSED: Normal operation, allows all requests
    - OPEN: After failure_threshold failures, rejects requests for recovery_timeout
    - HALF_OPEN: After recovery_timeout, allows 1 test request

    Transitions:
    - CLOSED -> OPEN: After failure_threshold consecutive failures
    - OPEN -> HALF_OPEN: After recovery_timeout seconds
    - HALF_OPEN -> CLOSED: If test request succeeds
    - HALF_OPEN -> OPEN: If test request fails
    """

    def __init__(
        self,
        failure_threshold: int = 5,
        recovery_timeout: int = 60,
        expected_exception: type = Exception,
    ):
        """
        Initialize circuit breaker.

        Args:
            failure_threshold: Number of consecutive failures before opening circuit
            recovery_timeout: Seconds to wait before attempting recovery
            expected_exception: Exception type to catch
        """
        self.failure_threshold = failure_threshold
        self.recovery_timeout = recovery_timeout
        self.expected_exception = expected_exception

        # State tracking
        self.state = CircuitState.CLOSED
        self.failure_count = 0
        self.success_count = 0
        self.last_failure_time = None
        self.last_success_time = None

    def call(self, func):
        """Decorator to wrap function with circuit breaker logic."""

        async def wrapper(*args, **kwargs):
            # Check if circuit should transition from OPEN to HALF_OPEN
            if self.state == CircuitState.OPEN:
                if self._should_attempt_reset():
                    self.state = CircuitState.HALF_OPEN
                else:
                    # Circuit still open, raise exception immediately
                    raise CircuitBreakerOpenError(
                        f"Circuit breaker is OPEN. "
                        f"Last failure: {self.last_failure_time}. "
                        f"Wait {self.recovery_timeout}s before retry."
                    )

            # Attempt the call
            try:
                result = await func(*args, **kwargs)
                self._on_success()
                return result
            except self.expected_exception as e:
                self._on_failure()
                raise e

        return wrapper

    def _should_attempt_reset(self) -> bool:
        """Check if enough time has passed to attempt reset."""
        if self.last_failure_time is None:
            return False
        return (time.time() - self.last_failure_time) >= self.recovery_timeout

    def _on_success(self):
        """Handle successful call."""
        self.success_count += 1
        self.last_success_time = time.time()

        # Reset failure count and close circuit
        self.failure_count = 0
        if self.state == CircuitState.HALF_OPEN:
            self.state = CircuitState.CLOSED

    def _on_failure(self):
        """Handle failed call."""
        self.failure_count += 1
        self.last_failure_time = time.time()

        # Open circuit if threshold exceeded
        if self.failure_count >= self.failure_threshold:
            self.state = CircuitState.OPEN

    def get_metrics(self) -> Dict[str, Any]:
        """Get circuit breaker metrics."""
        return {
            "state": self.state.value,
            "failure_count": self.failure_count,
            "success_count": self.success_count,
            "last_failure_time": self.last_failure_time,
            "last_success_time": self.last_success_time,
            "failure_threshold": self.failure_threshold,
            "recovery_timeout": self.recovery_timeout,
        }


class CircuitBreakerOpenError(Exception):
    """Raised when circuit breaker is open and rejecting requests."""

    pass


class LLMService:
    """Service for interacting with LLM via HTTP with circuit breaker protection."""

    def __init__(self):
        """Initialize LLM service with config and circuit breaker."""
        self.config = self._load_config()
        self.client = httpx.AsyncClient(timeout=self.config.get("timeout", 120))

        # Initialize circuit breaker
        self.circuit_breaker = CircuitBreaker(
            failure_threshold=5,
            recovery_timeout=60,
            expected_exception=Exception,
        )

        # Set up Jinja2 for prompt templates
        # Resolve templates relative to the installed app layout inside container.
        # When the API is copied into /app, templates are placed at /app/templates.
        # Use parent.parent to reach /app from /app/services
        template_path = Path(__file__).resolve().parent.parent / "templates"
        # Fallback: if templates not found there, try repository-root style (/templates)
        if not template_path.exists():
            template_path = (
                Path(__file__).resolve().parent.parent.parent.parent / "templates"
            )
        self.jinja_env = Environment(
            loader=FileSystemLoader(str(template_path)), autoescape=True
        )

    def _load_config(self) -> Dict[str, Any]:
        """Load LLM configuration from mounted file or use defaults."""
        config_path = os.getenv("LLM_CONFIG_PATH", "/config/llm.json")

        # Default LM Studio compatible config
        # Note: "lm-studio" is a placeholder API key, not a real secret.
        # LM Studio uses this as a dummy value for local development.
        # Production deployments can override via mounted config file.
        default_config = {
            "provider": "lmstudio",
            "base_url": "http://host.docker.internal:1234/v1",
            "api_key": "lm-studio",  # Placeholder for LM Studio (not a real secret)
            "model": "local-model",
            "temperature": 0.7,
            "max_tokens": 4096,
            "timeout": 120,
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

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=1, max=4),
        retry=retry_if_exception_type((httpx.HTTPError, httpx.TimeoutException)),
        reraise=True,
    )
    async def _chat_completion_with_retry(
        self,
        messages: List[Dict[str, str]],
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None,
    ) -> str:
        """
        Make a chat completion request with retry logic.

        Retries 3 times with exponential backoff: 1s, 2s, 4s.
        Only retries on HTTP errors and timeouts.
        """
        url = f"{self.config['base_url']}/chat/completions"

        payload = {
            "model": self.config["model"],
            "messages": messages,
            "temperature": temperature or self.config["temperature"],
            "max_tokens": max_tokens or self.config["max_tokens"],
        }

        headers = {
            "Authorization": f"Bearer {self.config['api_key']}",
            "Content-Type": "application/json",
        }

        response = await self.client.post(url, json=payload, headers=headers)
        response.raise_for_status()
        data = response.json()
        return data["choices"][0]["message"]["content"]

    async def chat_completion(
        self,
        messages: List[Dict[str, str]],
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None,
    ) -> str:
        """
        Make a chat completion request to the LLM with circuit breaker protection.

        Features:
        - Retry logic: 3 attempts with exponential backoff (1s, 2s, 4s)
        - Circuit breaker: Opens after 5 consecutive failures
        - Graceful degradation: Returns fallback message if circuit open

        Args:
            messages: List of message dicts with 'role' and 'content'
            temperature: Optional temperature override
            max_tokens: Optional max tokens override

        Returns:
            LLM response content or fallback message
        """
        start_time = time.time()
        provider = self.config.get("model", "unknown")
        status = "success"

        try:
            # Wrap with circuit breaker
            protected_call = self.circuit_breaker.call(self._chat_completion_with_retry)
            result = await protected_call(messages, temperature, max_tokens)

            # Record successful metrics
            duration = time.time() - start_time
            MetricsCollector.record_llm_call(provider, duration, status)

            return result

        except CircuitBreakerOpenError as e:
            # Circuit is open, return fallback immediately
            duration = time.time() - start_time
            status = "circuit_breaker_open"
            MetricsCollector.record_llm_call(provider, duration, status)

            print(f"Circuit breaker OPEN: {e}")
            return f"[LLM unavailable - circuit breaker open: {str(e)}]"

        except Exception as e:
            # Other errors (after retries exhausted)
            duration = time.time() - start_time
            status = "error"
            MetricsCollector.record_llm_call(provider, duration, status)

            print(f"LLM request failed after retries: {e}")
            return f"[LLM unavailable: {str(e)}]"

    def render_prompt(self, template_name: str, context: Dict[str, Any]) -> str:
        """Render a prompt template with given context."""
        template = self.jinja_env.get_template(f"prompts/iso21500/{template_name}")
        return template.render(**context)

    def render_output(self, template_name: str, context: Dict[str, Any]) -> str:
        """Render an output template with given context."""
        template = self.jinja_env.get_template(f"output/iso21500/{template_name}")
        return template.render(**context)

    def get_circuit_breaker_metrics(self) -> Dict[str, Any]:
        """
        Get circuit breaker metrics for monitoring.

        Returns:
            Dict with state, failure/success counts, timestamps, and config
        """
        return self.circuit_breaker.get_metrics()

    async def close(self):
        """Close HTTP client."""
        await self.client.aclose()
