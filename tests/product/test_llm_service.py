"""
Unit tests for LLM Service.
"""

import pytest
import json
import time
import tempfile
from pathlib import Path
from unittest.mock import Mock, AsyncMock, patch
from apps.api.services.llm_service import (
    LLMService,
    CircuitBreaker,
    CircuitState,
    CircuitBreakerOpenError,
)


class TestLLMServiceInit:
    """Test LLM service initialization."""

    def test_init_loads_config(self):
        """Test that initialization loads config."""
        service = LLMService()
        assert service.config is not None
        assert isinstance(service.config, dict)

    def test_init_creates_client(self):
        """Test that initialization creates HTTP client."""
        service = LLMService()
        assert service.client is not None

    def test_init_creates_jinja_env(self):
        """Test that initialization creates Jinja environment."""
        service = LLMService()
        assert service.jinja_env is not None


class TestLoadConfig:
    """Test configuration loading."""

    def test_load_config_uses_defaults_when_file_missing(self):
        """Test that defaults are used when config file doesn't exist."""
        with patch.dict("os.environ", {"LLM_CONFIG_PATH": "/nonexistent/config.json"}):
            service = LLMService()
            config = service.config

            assert config["provider"] == "lmstudio"
            assert config["base_url"] == "http://host.docker.internal:1234/v1"
            assert config["api_key"] == "lm-studio"
            assert config["model"] == "local-model"
            assert config["temperature"] == 0.7
            assert config["max_tokens"] == 4096

    def test_load_config_from_file(self):
        """Test loading config from file."""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
            custom_config = {
                "provider": "openai",
                "base_url": "https://api.openai.com/v1",
                "api_key": "test-key",
                "model": "gpt-4",
            }
            json.dump(custom_config, f)
            config_path = f.name

        try:
            with patch.dict("os.environ", {"LLM_CONFIG_PATH": config_path}):
                service = LLMService()
                config = service.config

                assert config["provider"] == "openai"
                assert config["base_url"] == "https://api.openai.com/v1"
                assert config["api_key"] == "test-key"
                assert config["model"] == "gpt-4"
                # Defaults should still be present for missing keys
                assert config["temperature"] == 0.7
        finally:
            Path(config_path).unlink()

    def test_load_config_merges_with_defaults(self):
        """Test that loaded config is merged with defaults."""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
            partial_config = {"model": "custom-model"}
            json.dump(partial_config, f)
            config_path = f.name

        try:
            with patch.dict("os.environ", {"LLM_CONFIG_PATH": config_path}):
                service = LLMService()
                config = service.config

                # Custom value
                assert config["model"] == "custom-model"
                # Default values still present
                assert config["provider"] == "lmstudio"
                assert config["temperature"] == 0.7
        finally:
            Path(config_path).unlink()


class TestChatCompletion:
    """Test chat completion functionality."""

    @pytest.fixture
    def mock_httpx_client(self):
        """Create a mock httpx client."""
        mock_client = AsyncMock()
        mock_response = Mock()
        mock_response.json.return_value = {
            "choices": [{"message": {"content": "Test LLM response"}}]
        }
        mock_response.raise_for_status = Mock()
        mock_client.post.return_value = mock_response
        return mock_client

    @pytest.mark.asyncio
    async def test_chat_completion_success(self, mock_httpx_client):
        """Test successful chat completion."""
        with patch("httpx.AsyncClient", return_value=mock_httpx_client):
            service = LLMService()
            messages = [
                {"role": "system", "content": "You are a helpful assistant."},
                {"role": "user", "content": "Hello!"},
            ]

            result = await service.chat_completion(messages)

            assert result == "Test LLM response"
            mock_httpx_client.post.assert_called_once()

    @pytest.mark.asyncio
    async def test_chat_completion_with_custom_params(self, mock_httpx_client):
        """Test chat completion with custom temperature and max_tokens."""
        with patch("httpx.AsyncClient", return_value=mock_httpx_client):
            service = LLMService()
            messages = [{"role": "user", "content": "Test"}]

            await service.chat_completion(messages, temperature=0.5, max_tokens=1000)

            # Verify payload contains custom params
            call_kwargs = mock_httpx_client.post.call_args[1]
            payload = call_kwargs["json"]
            assert payload["temperature"] == 0.5
            assert payload["max_tokens"] == 1000

    @pytest.mark.asyncio
    async def test_chat_completion_uses_default_params(self, mock_httpx_client):
        """Test that default params are used when not specified."""
        with patch("httpx.AsyncClient", return_value=mock_httpx_client):
            service = LLMService()
            messages = [{"role": "user", "content": "Test"}]

            await service.chat_completion(messages)

            call_kwargs = mock_httpx_client.post.call_args[1]
            payload = call_kwargs["json"]
            assert payload["temperature"] == 0.7  # default
            assert payload["max_tokens"] == 4096  # default

    @pytest.mark.asyncio
    async def test_chat_completion_handles_error(self):
        """Test that chat completion handles errors gracefully."""
        mock_client = AsyncMock()
        mock_client.post.side_effect = Exception("Network error")

        with patch("httpx.AsyncClient", return_value=mock_client):
            service = LLMService()
            messages = [{"role": "user", "content": "Test"}]

            result = await service.chat_completion(messages)

            # Should return fallback message
            assert "[LLM unavailable:" in result
            assert "Network error" in result

    @pytest.mark.asyncio
    async def test_chat_completion_includes_auth_header(self, mock_httpx_client):
        """Test that auth header is included in request."""
        with patch("httpx.AsyncClient", return_value=mock_httpx_client):
            service = LLMService()
            messages = [{"role": "user", "content": "Test"}]

            await service.chat_completion(messages)

            call_kwargs = mock_httpx_client.post.call_args[1]
            headers = call_kwargs["headers"]
            assert "Authorization" in headers
            assert headers["Authorization"].startswith("Bearer ")


class TestRenderPrompt:
    """Test prompt template rendering."""

    @pytest.fixture
    def service_with_mock_jinja(self):
        """Create service with mocked Jinja environment."""
        service = LLMService()
        mock_template = Mock()
        mock_template.render.return_value = "Rendered prompt"
        service.jinja_env.get_template = Mock(return_value=mock_template)
        return service

    def test_render_prompt(self, service_with_mock_jinja):
        """Test rendering a prompt template."""
        context = {"project_key": "TEST001", "artifacts": ["charter.md"]}

        result = service_with_mock_jinja.render_prompt("test_template.j2", context)

        assert result == "Rendered prompt"
        service_with_mock_jinja.jinja_env.get_template.assert_called_once_with(
            "prompts/iso21500/test_template.j2"
        )

    def test_render_prompt_passes_context(self, service_with_mock_jinja):
        """Test that context is passed to template rendering."""
        context = {"key": "value", "number": 42}

        service_with_mock_jinja.render_prompt("test.j2", context)

        mock_template = service_with_mock_jinja.jinja_env.get_template.return_value
        mock_template.render.assert_called_once_with(key="value", number=42)


class TestRenderOutput:
    """Test output template rendering."""

    @pytest.fixture
    def service_with_mock_jinja(self):
        """Create service with mocked Jinja environment."""
        service = LLMService()
        mock_template = Mock()
        mock_template.render.return_value = "Rendered output"
        service.jinja_env.get_template = Mock(return_value=mock_template)
        return service

    def test_render_output(self, service_with_mock_jinja):
        """Test rendering an output template."""
        context = {"project_name": "Test Project", "content": "Test content"}

        result = service_with_mock_jinja.render_output("test_output.md", context)

        assert result == "Rendered output"
        service_with_mock_jinja.jinja_env.get_template.assert_called_once_with(
            "output/iso21500/test_output.md"
        )

    def test_render_output_passes_context(self, service_with_mock_jinja):
        """Test that context is passed to output template rendering."""
        context = {"title": "Report", "data": [1, 2, 3]}

        service_with_mock_jinja.render_output("report.md", context)

        mock_template = service_with_mock_jinja.jinja_env.get_template.return_value
        mock_template.render.assert_called_once_with(title="Report", data=[1, 2, 3])


class TestClose:
    """Test client cleanup."""

    @pytest.mark.asyncio
    async def test_close(self):
        """Test closing the HTTP client."""
        mock_client = AsyncMock()
        with patch("httpx.AsyncClient", return_value=mock_client):
            service = LLMService()
            await service.close()

            mock_client.aclose.assert_called_once()


class TestCircuitBreaker:
    """Test circuit breaker functionality."""

    def test_circuit_breaker_init(self):
        """Test circuit breaker initialization."""
        cb = CircuitBreaker(failure_threshold=3, recovery_timeout=30)

        assert cb.state == CircuitState.CLOSED
        assert cb.failure_count == 0
        assert cb.success_count == 0
        assert cb.failure_threshold == 3
        assert cb.recovery_timeout == 30

    @pytest.mark.asyncio
    async def test_circuit_breaker_closed_state_allows_calls(self):
        """Test that closed circuit allows calls through."""
        cb = CircuitBreaker()

        async def success_func():
            return "success"

        wrapped = cb.call(success_func)
        result = await wrapped()

        assert result == "success"
        assert cb.state == CircuitState.CLOSED
        assert cb.success_count == 1
        assert cb.failure_count == 0

    @pytest.mark.asyncio
    async def test_circuit_breaker_opens_after_threshold(self):
        """Test that circuit opens after failure threshold."""
        cb = CircuitBreaker(failure_threshold=3)

        async def failing_func():
            raise Exception("Test failure")

        wrapped = cb.call(failing_func)

        # First 2 failures - circuit still closed
        for i in range(2):
            with pytest.raises(Exception):
                await wrapped()
            assert cb.state == CircuitState.CLOSED
            assert cb.failure_count == i + 1

        # 3rd failure - circuit opens
        with pytest.raises(Exception):
            await wrapped()
        assert cb.state == CircuitState.OPEN
        assert cb.failure_count == 3

    @pytest.mark.asyncio
    async def test_circuit_breaker_rejects_when_open(self):
        """Test that open circuit rejects calls immediately."""
        cb = CircuitBreaker(failure_threshold=2)

        async def failing_func():
            raise Exception("Test failure")

        wrapped = cb.call(failing_func)

        # Trigger failures to open circuit
        for _ in range(2):
            with pytest.raises(Exception):
                await wrapped()

        assert cb.state == CircuitState.OPEN

        # Next call should be rejected immediately
        with pytest.raises(CircuitBreakerOpenError) as exc_info:
            await wrapped()

        assert "Circuit breaker is OPEN" in str(exc_info.value)

    @pytest.mark.asyncio
    async def test_circuit_breaker_half_open_after_timeout(self):
        """Test that circuit transitions to half-open after recovery timeout."""
        cb = CircuitBreaker(failure_threshold=2, recovery_timeout=1)

        async def failing_func():
            raise Exception("Test failure")

        wrapped = cb.call(failing_func)

        # Open the circuit
        for _ in range(2):
            with pytest.raises(Exception):
                await wrapped()

        assert cb.state == CircuitState.OPEN

        # Wait for recovery timeout
        time.sleep(1.1)

        # Next call should transition to half-open (but still fail)
        with pytest.raises(Exception):
            await wrapped()

        # Circuit should have been in half-open before failing again
        assert cb.state == CircuitState.OPEN  # Back to open after failure

    @pytest.mark.asyncio
    async def test_circuit_breaker_closes_after_success_in_half_open(self):
        """Test that circuit closes after successful call in half-open state."""
        cb = CircuitBreaker(failure_threshold=2, recovery_timeout=1)

        call_count = [0]

        async def sometimes_failing_func():
            call_count[0] += 1
            if call_count[0] <= 2:
                raise Exception("Fail first 2 calls")
            return "success"

        wrapped = cb.call(sometimes_failing_func)

        # Open the circuit
        for _ in range(2):
            with pytest.raises(Exception):
                await wrapped()

        assert cb.state == CircuitState.OPEN

        # Wait for recovery timeout
        time.sleep(1.1)

        # Successful call in half-open should close circuit
        result = await wrapped()
        assert result == "success"
        assert cb.state == CircuitState.CLOSED
        assert cb.failure_count == 0

    @pytest.mark.asyncio
    async def test_circuit_breaker_resets_failure_count_on_success(self):
        """Test that failure count resets on successful call."""
        cb = CircuitBreaker(failure_threshold=5)

        async def sometimes_failing_func(should_fail):
            if should_fail:
                raise Exception("Test failure")
            return "success"

        # Partial failures (below threshold)
        for _ in range(3):
            with pytest.raises(Exception):
                await cb.call(lambda: sometimes_failing_func(True))()

        assert cb.failure_count == 3
        assert cb.state == CircuitState.CLOSED

        # Success resets counter
        await cb.call(lambda: sometimes_failing_func(False))()

        assert cb.failure_count == 0
        assert cb.success_count == 1
        assert cb.state == CircuitState.CLOSED

    def test_circuit_breaker_get_metrics(self):
        """Test getting circuit breaker metrics."""
        cb = CircuitBreaker(failure_threshold=5, recovery_timeout=60)
        cb.failure_count = 2
        cb.success_count = 10
        cb.last_failure_time = 1234567890.0
        cb.last_success_time = 1234567900.0

        metrics = cb.get_metrics()

        assert metrics["state"] == "closed"
        assert metrics["failure_count"] == 2
        assert metrics["success_count"] == 10
        assert metrics["last_failure_time"] == 1234567890.0
        assert metrics["last_success_time"] == 1234567900.0
        assert metrics["failure_threshold"] == 5
        assert metrics["recovery_timeout"] == 60


class TestLLMServiceCircuitBreaker:
    """Test LLM service integration with circuit breaker."""

    def test_llm_service_has_circuit_breaker(self):
        """Test that LLM service initializes with circuit breaker."""
        service = LLMService()

        assert hasattr(service, "circuit_breaker")
        assert isinstance(service.circuit_breaker, CircuitBreaker)
        assert service.circuit_breaker.failure_threshold == 5
        assert service.circuit_breaker.recovery_timeout == 60

    def test_get_circuit_breaker_metrics(self):
        """Test getting circuit breaker metrics from service."""
        service = LLMService()

        metrics = service.get_circuit_breaker_metrics()

        assert "state" in metrics
        assert "failure_count" in metrics
        assert "success_count" in metrics
        assert metrics["state"] == "closed"

    @pytest.mark.asyncio
    async def test_chat_completion_with_circuit_breaker_success(self):
        """Test successful chat completion updates circuit breaker."""
        mock_client = AsyncMock()
        mock_response = Mock()
        mock_response.json.return_value = {
            "choices": [{"message": {"content": "Success response"}}]
        }
        mock_response.raise_for_status = Mock()
        mock_client.post.return_value = mock_response

        with patch("httpx.AsyncClient", return_value=mock_client):
            service = LLMService()
            messages = [{"role": "user", "content": "Test"}]

            result = await service.chat_completion(messages)

            assert result == "Success response"
            assert service.circuit_breaker.success_count == 1
            assert service.circuit_breaker.failure_count == 0
            assert service.circuit_breaker.state == CircuitState.CLOSED

    @pytest.mark.asyncio
    async def test_chat_completion_circuit_breaker_opens_on_failures(self):
        """Test that circuit breaker opens after multiple failures."""
        mock_client = AsyncMock()
        mock_client.post.side_effect = Exception("Network error")

        with patch("httpx.AsyncClient", return_value=mock_client):
            service = LLMService()
            messages = [{"role": "user", "content": "Test"}]

            # Trigger failures to open circuit (5 failures needed)
            for i in range(5):
                result = await service.chat_completion(messages)
                assert "[LLM unavailable:" in result
                assert service.circuit_breaker.failure_count == i + 1

            # Circuit should now be open
            assert service.circuit_breaker.state == CircuitState.OPEN

            # Next call should be rejected immediately (no HTTP call)
            mock_client.post.reset_mock()
            result = await service.chat_completion(messages)

            assert "[LLM unavailable - circuit breaker open:" in result
            mock_client.post.assert_not_called()  # No HTTP call made

    @pytest.mark.asyncio
    async def test_chat_completion_returns_fallback_when_circuit_open(self):
        """Test that fallback message is returned when circuit is open."""
        service = LLMService()

        # Manually open the circuit
        service.circuit_breaker.state = CircuitState.OPEN
        service.circuit_breaker.failure_count = 5
        service.circuit_breaker.last_failure_time = time.time()

        messages = [{"role": "user", "content": "Test"}]
        result = await service.chat_completion(messages)

        assert "[LLM unavailable - circuit breaker open:" in result
        assert "Circuit breaker is OPEN" in result
