"""Unit tests for the PoC LLM Gateway.

Covers:
- Provider selection / factory logic
- Config validation (Copilot key presence)
- Model routing (policy tier → concrete model ID)
- StubProvider behaviour
- CopilotProvider health reporting
- Gateway /health and /v1/chat/completions endpoints (via TestClient)
"""

from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from fastapi.testclient import TestClient


# ---------------------------------------------------------------------------
# Helpers / fixtures
# ---------------------------------------------------------------------------


@pytest.fixture(autouse=True)
def _clear_provider_env(monkeypatch):
    """Ensure provider-related env vars are clean before every test."""
    for var in (
        "GATEWAY_PROVIDER",
        "GATEWAY_FALLBACK_TO_STUB",
        "COPILOT_API_KEY",
        "COPILOT_BASE_URL",
        "COPILOT_TIMEOUT",
        "COPILOT_MODEL_SMALL",
        "COPILOT_MODEL_MEDIUM",
        "COPILOT_MODEL_LARGE",
    ):
        monkeypatch.delenv(var, raising=False)


# ---------------------------------------------------------------------------
# StubProvider
# ---------------------------------------------------------------------------


class TestStubProvider:
    """Tests for the offline stub provider."""

    def test_health_always_available(self):
        from poc.providers.stub import StubProvider

        provider = StubProvider()
        h = provider.health()
        assert h["configured"] is True
        assert h["available"] is True
        assert "offline" in h["message"].lower() or "always" in h["message"].lower()

    @pytest.mark.asyncio
    async def test_chat_completion_returns_openai_envelope(self):
        from poc.providers.stub import StubProvider

        provider = StubProvider()
        messages = [{"role": "user", "content": "Hello"}]
        result = await provider.chat_completion(
            messages=messages, model="gpt-4o-mini"
        )
        assert "choices" in result
        assert result["choices"][0]["message"]["role"] == "assistant"
        assert "gpt-4o-mini" in result["choices"][0]["message"]["content"]

    @pytest.mark.asyncio
    async def test_chat_completion_increments_call_count(self):
        from poc.providers.stub import StubProvider

        provider = StubProvider()
        await provider.chat_completion(messages=[], model="gpt-4o")
        await provider.chat_completion(messages=[], model="gpt-4o")
        assert provider._call_count == 2

    @pytest.mark.asyncio
    async def test_chat_completion_echoes_last_user_message(self):
        from poc.providers.stub import StubProvider

        provider = StubProvider()
        messages = [
            {"role": "system", "content": "Be helpful."},
            {"role": "user", "content": "What is 2+2?"},
        ]
        result = await provider.chat_completion(messages=messages, model="m")
        content = result["choices"][0]["message"]["content"]
        assert "What is 2+2?" in content


# ---------------------------------------------------------------------------
# CopilotProvider
# ---------------------------------------------------------------------------


class TestCopilotProviderConfig:
    """Tests for CopilotProvider configuration and health reporting."""

    def test_not_configured_when_key_missing(self):
        from poc.providers.copilot import CopilotProvider

        provider = CopilotProvider()
        assert provider.is_configured is False

    def test_not_configured_when_placeholder_key(self, monkeypatch):
        from poc.providers.copilot import CopilotProvider

        monkeypatch.setenv("COPILOT_API_KEY", "your-api-key-here")
        provider = CopilotProvider()
        assert provider.is_configured is False

    def test_configured_when_real_key(self, monkeypatch):
        from poc.providers.copilot import CopilotProvider

        monkeypatch.setenv("COPILOT_API_KEY", "ghp_abc123realtoken")
        provider = CopilotProvider()
        assert provider.is_configured is True

    def test_health_not_configured(self):
        from poc.providers.copilot import CopilotProvider

        provider = CopilotProvider()
        h = provider.health()
        assert h["configured"] is False
        assert h["available"] is False
        assert "COPILOT_API_KEY" in h["message"]

    def test_health_configured(self, monkeypatch):
        from poc.providers.copilot import CopilotProvider

        monkeypatch.setenv("COPILOT_API_KEY", "ghp_realtoken")
        provider = CopilotProvider()
        h = provider.health()
        assert h["configured"] is True
        assert h["available"] is True
        assert h["last_error"] is None

    def test_custom_base_url(self, monkeypatch):
        from poc.providers.copilot import CopilotProvider

        monkeypatch.setenv("COPILOT_API_KEY", "tok")
        monkeypatch.setenv("COPILOT_BASE_URL", "https://custom.example.com/")
        provider = CopilotProvider()
        assert provider._base_url == "https://custom.example.com"  # trailing / stripped

    def test_custom_timeout(self, monkeypatch):
        from poc.providers.copilot import CopilotProvider

        monkeypatch.setenv("COPILOT_API_KEY", "tok")
        monkeypatch.setenv("COPILOT_TIMEOUT", "30")
        provider = CopilotProvider()
        assert provider._timeout == 30.0

    @pytest.mark.asyncio
    async def test_raises_value_error_when_not_configured(self):
        from poc.providers.copilot import CopilotProvider

        provider = CopilotProvider()
        with pytest.raises(ValueError, match="COPILOT_API_KEY"):
            await provider.chat_completion(
                messages=[{"role": "user", "content": "Hi"}], model="gpt-4o"
            )

    @pytest.mark.asyncio
    async def test_successful_completion(self, monkeypatch):
        """CopilotProvider forwards request and returns upstream response."""
        from poc.providers.copilot import CopilotProvider

        monkeypatch.setenv("COPILOT_API_KEY", "ghp_realtoken")
        provider = CopilotProvider()

        fake_response = {
            "id": "chatcmpl-xyz",
            "object": "chat.completion",
            "choices": [
                {"index": 0, "message": {"role": "assistant", "content": "42"}}
            ],
        }
        mock_resp = MagicMock()
        mock_resp.json.return_value = fake_response
        mock_resp.raise_for_status = MagicMock()

        mock_client = AsyncMock()
        mock_client.__aenter__ = AsyncMock(return_value=mock_client)
        mock_client.__aexit__ = AsyncMock(return_value=False)
        mock_client.post = AsyncMock(return_value=mock_resp)

        with patch("poc.providers.copilot.httpx.AsyncClient", return_value=mock_client):
            result = await provider.chat_completion(
                messages=[{"role": "user", "content": "what is 6*7?"}],
                model="gpt-4o",
            )

        assert result["choices"][0]["message"]["content"] == "42"
        assert provider._last_error == ""

    @pytest.mark.asyncio
    async def test_http_error_raises_runtime_error(self, monkeypatch):
        import httpx
        from poc.providers.copilot import CopilotProvider

        monkeypatch.setenv("COPILOT_API_KEY", "ghp_realtoken")
        provider = CopilotProvider()

        mock_client = AsyncMock()
        mock_client.__aenter__ = AsyncMock(return_value=mock_client)
        mock_client.__aexit__ = AsyncMock(return_value=False)
        mock_resp = MagicMock()
        mock_resp.status_code = 401
        mock_resp.text = "Unauthorized"
        mock_client.post = AsyncMock(
            side_effect=httpx.HTTPStatusError(
                "401", request=MagicMock(), response=mock_resp
            )
        )

        with patch("poc.providers.copilot.httpx.AsyncClient", return_value=mock_client):
            with pytest.raises(RuntimeError, match="Copilot API returned an error"):
                await provider.chat_completion(
                    messages=[{"role": "user", "content": "hi"}],
                    model="gpt-4o",
                )

        assert provider._last_error != ""


# ---------------------------------------------------------------------------
# Provider factory
# ---------------------------------------------------------------------------


class TestProviderFactory:
    """Tests for build_provider() selection logic."""

    def test_explicit_stub_returns_stub(self, monkeypatch):
        from poc.providers.factory import build_provider
        from poc.providers.stub import StubProvider

        monkeypatch.setenv("GATEWAY_PROVIDER", "stub")
        provider, msg = build_provider()
        assert isinstance(provider, StubProvider)
        assert "stub" in msg.lower()

    def test_copilot_with_key_returns_copilot(self, monkeypatch):
        from poc.providers.copilot import CopilotProvider
        from poc.providers.factory import build_provider

        monkeypatch.setenv("GATEWAY_PROVIDER", "copilot")
        monkeypatch.setenv("COPILOT_API_KEY", "ghp_realtoken")
        provider, msg = build_provider()
        assert isinstance(provider, CopilotProvider)
        assert "copilot" in msg.lower()

    def test_copilot_without_key_raises_when_no_fallback(self, monkeypatch):
        from poc.providers.factory import build_provider

        monkeypatch.setenv("GATEWAY_PROVIDER", "copilot")
        # No COPILOT_API_KEY, no fallback
        with pytest.raises(ValueError, match="COPILOT_API_KEY"):
            build_provider()

    def test_copilot_without_key_falls_back_to_stub(self, monkeypatch):
        from poc.providers.factory import build_provider
        from poc.providers.stub import StubProvider

        monkeypatch.setenv("GATEWAY_PROVIDER", "copilot")
        monkeypatch.setenv("GATEWAY_FALLBACK_TO_STUB", "true")
        provider, msg = build_provider()
        assert isinstance(provider, StubProvider)
        assert "fallback" in msg.lower()

    def test_default_provider_is_copilot_when_key_set(self, monkeypatch):
        from poc.providers.copilot import CopilotProvider
        from poc.providers.factory import build_provider

        # No GATEWAY_PROVIDER set → defaults to 'copilot'
        monkeypatch.setenv("COPILOT_API_KEY", "ghp_tok")
        provider, _ = build_provider()
        assert isinstance(provider, CopilotProvider)

    def test_unknown_provider_raises(self, monkeypatch):
        from poc.providers.factory import build_provider

        monkeypatch.setenv("GATEWAY_PROVIDER", "azure-openai")
        with pytest.raises(ValueError, match="Unknown provider"):
            build_provider()

    def test_fallback_flag_false_with_no_key_raises(self, monkeypatch):
        from poc.providers.factory import build_provider

        monkeypatch.setenv("GATEWAY_PROVIDER", "copilot")
        monkeypatch.setenv("GATEWAY_FALLBACK_TO_STUB", "false")
        with pytest.raises(ValueError):
            build_provider()


# ---------------------------------------------------------------------------
# Model routing
# ---------------------------------------------------------------------------


class TestModelRouting:
    """Tests for policy-tier → model-id resolution."""

    def test_small_tier_default(self):
        from poc.routing import resolve_model

        assert resolve_model("small") == "gpt-4o-mini"

    def test_medium_tier_default(self):
        from poc.routing import resolve_model

        assert resolve_model("medium") == "gpt-4o"

    def test_large_tier_default(self):
        from poc.routing import resolve_model

        assert resolve_model("large") == "o3-mini"

    def test_tier_case_insensitive(self):
        from poc.routing import resolve_model

        assert resolve_model("SMALL") == "gpt-4o-mini"
        assert resolve_model("Medium") == "gpt-4o"
        assert resolve_model("LARGE") == "o3-mini"

    def test_explicit_model_passthrough(self):
        from poc.routing import resolve_model

        assert resolve_model("claude-3.5-sonnet") == "claude-3.5-sonnet"
        assert resolve_model("o1-mini") == "o1-mini"

    def test_env_override_small(self, monkeypatch):
        from poc.routing import resolve_model

        monkeypatch.setenv("COPILOT_MODEL_SMALL", "my-custom-small")
        assert resolve_model("small") == "my-custom-small"

    def test_env_override_large(self, monkeypatch):
        from poc.routing import resolve_model

        monkeypatch.setenv("COPILOT_MODEL_LARGE", "o1-preview")
        assert resolve_model("large") == "o1-preview"

    def test_get_model_map_keys(self):
        from poc.routing import get_model_map

        m = get_model_map()
        assert set(m.keys()) == {"small", "medium", "large"}

    def test_whitespace_is_stripped(self):
        from poc.routing import resolve_model

        assert resolve_model("  medium  ") == "gpt-4o"


# ---------------------------------------------------------------------------
# Gateway HTTP endpoints (TestClient)
# ---------------------------------------------------------------------------


@pytest.fixture()
def stub_client():
    """TestClient with the gateway wired to StubProvider (no credentials needed)."""
    from poc.providers.stub import StubProvider
    from poc.main import app

    with patch(
        "poc.main.build_provider",
        return_value=(StubProvider(), "Provider: stub (test)"),
    ):
        with TestClient(app, raise_server_exceptions=True) as client:
            yield client


@pytest.fixture()
def unconfigured_copilot_client():
    """TestClient with an unconfigured CopilotProvider (no COPILOT_API_KEY)."""
    from poc.providers.copilot import CopilotProvider
    from poc.main import app

    with patch(
        "poc.main.build_provider",
        return_value=(CopilotProvider(), "Provider: copilot (test)"),
    ):
        with TestClient(app, raise_server_exceptions=False) as client:
            yield client


class TestGatewayHealth:
    """Integration-style tests for the /health endpoint."""

    def test_health_returns_200(self, stub_client):
        resp = stub_client.get("/health")
        assert resp.status_code == 200

    def test_health_contains_required_keys(self, stub_client):
        data = stub_client.get("/health").json()
        assert "status" in data
        assert "provider" in data
        assert "provider_health" in data
        assert "model_routing" in data

    def test_health_stub_is_healthy(self, stub_client):
        data = stub_client.get("/health").json()
        assert data["status"] == "healthy"
        assert data["provider"] == "StubProvider"

    def test_health_model_routing_keys(self, stub_client):
        data = stub_client.get("/health").json()
        assert set(data["model_routing"].keys()) == {"small", "medium", "large"}


class TestGatewayChatCompletions:
    """Integration-style tests for POST /v1/chat/completions."""

    def test_basic_completion_200(self, stub_client):
        resp = stub_client.post(
            "/v1/chat/completions",
            json={
                "model": "medium",
                "messages": [{"role": "user", "content": "Hello"}],
            },
        )
        assert resp.status_code == 200

    def test_completion_returns_openai_envelope(self, stub_client):
        resp = stub_client.post(
            "/v1/chat/completions",
            json={
                "model": "small",
                "messages": [{"role": "user", "content": "Test"}],
            },
        )
        data = resp.json()
        assert "choices" in data
        assert data["choices"][0]["message"]["role"] == "assistant"

    def test_policy_tier_is_resolved_to_model_id(self, stub_client):
        """'small' tier should be resolved to gpt-4o-mini in stub response content."""
        resp = stub_client.post(
            "/v1/chat/completions",
            json={
                "model": "small",
                "messages": [{"role": "user", "content": "Ping"}],
            },
        )
        data = resp.json()
        content = data["choices"][0]["message"]["content"]
        # StubProvider echoes the resolved model name
        assert "gpt-4o-mini" in content

    def test_missing_messages_returns_422(self, stub_client):
        resp = stub_client.post("/v1/chat/completions", json={"model": "medium"})
        assert resp.status_code == 422

    def test_copilot_unconfigured_returns_503(self, unconfigured_copilot_client):
        """When CopilotProvider raises ValueError, gateway should return 503."""
        resp = unconfigured_copilot_client.post(
            "/v1/chat/completions",
            json={
                "model": "medium",
                "messages": [{"role": "user", "content": "hi"}],
            },
        )
        assert resp.status_code == 503
        assert "COPILOT_API_KEY" in resp.json()["detail"]
