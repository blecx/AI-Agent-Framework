"""Unit tests for LLM gateway provider selection and routing logic.

These tests exercise:
  - Provider instantiation from config
  - Fallback to stub when provider is unknown
  - Model resolution (explicit, role-based, default)
  - Routing via GatewayRouter.complete
  - Health check responses per provider
  - Config loading from env vars and dicts
"""

import pytest

from poc.gateway.config import GatewayConfig
from poc.gateway.providers.copilot import CopilotProvider
from poc.gateway.providers.github_models import GitHubModelsProvider
from poc.gateway.providers.stub import StubProvider
from poc.gateway.router import GatewayRouter, _build_provider


# ---------------------------------------------------------------------------
# Config tests
# ---------------------------------------------------------------------------


def test_config_defaults_to_stub_provider():
    cfg = GatewayConfig()
    assert cfg.provider == "stub"


def test_config_from_dict_reads_provider_and_model():
    cfg = GatewayConfig.from_dict(
        {"provider": "github", "model": "openai/gpt-4o", "api_key": "tok"}
    )
    assert cfg.provider == "github"
    assert cfg.default_model == "openai/gpt-4o"
    assert cfg.api_key == "tok"


def test_config_from_dict_reads_model_policy_from_roles():
    cfg = GatewayConfig.from_dict(
        {
            "provider": "github",
            "roles": {
                "planning": {"model": "openai/gpt-4o"},
                "coding": {"model": "openai/gpt-4o-mini"},
            },
        }
    )
    assert cfg.model_policy["planning"] == "openai/gpt-4o"
    assert cfg.model_policy["coding"] == "openai/gpt-4o-mini"


def test_config_from_env_reads_env_vars(monkeypatch):
    monkeypatch.setenv("LLM_GATEWAY_PROVIDER", "github")
    monkeypatch.setenv("LLM_GATEWAY_MODEL", "openai/gpt-4o")
    monkeypatch.setenv("LLM_GATEWAY_API_KEY", "env-token")
    monkeypatch.setenv("LLM_GATEWAY_TIMEOUT", "30")

    cfg = GatewayConfig.from_env()
    assert cfg.provider == "github"
    assert cfg.default_model == "openai/gpt-4o"
    assert cfg.api_key == "env-token"
    assert cfg.timeout == 30.0


def test_config_from_env_uses_defaults_when_env_absent(monkeypatch):
    for var in ("LLM_GATEWAY_PROVIDER", "LLM_GATEWAY_MODEL", "LLM_GATEWAY_API_KEY"):
        monkeypatch.delenv(var, raising=False)

    cfg = GatewayConfig.from_env()
    assert cfg.provider == "stub"
    assert cfg.api_key == ""


def test_config_timeout_invalid_env_falls_back_to_default(monkeypatch):
    monkeypatch.setenv("LLM_GATEWAY_TIMEOUT", "not-a-number")
    cfg = GatewayConfig.from_env()
    assert cfg.timeout == 60.0


def test_config_model_for_role_returns_policy_entry():
    cfg = GatewayConfig(
        default_model="openai/gpt-4o-mini",
        model_policy={"planning": "openai/gpt-4o"},
    )
    assert cfg.model_for_role("planning") == "openai/gpt-4o"
    assert cfg.model_for_role("coding") == "openai/gpt-4o-mini"


def test_config_resolved_base_url_github_default():
    cfg = GatewayConfig(provider="github", base_url="")
    assert cfg.resolved_base_url() == "https://models.github.ai/inference"


def test_config_resolved_base_url_respects_explicit():
    cfg = GatewayConfig(provider="github", base_url="https://custom.example.com")
    assert cfg.resolved_base_url() == "https://custom.example.com"


# ---------------------------------------------------------------------------
# Provider selection tests
# ---------------------------------------------------------------------------


def test_build_provider_stub():
    cfg = GatewayConfig(provider="stub")
    provider = _build_provider(cfg)
    assert isinstance(provider, StubProvider)
    assert provider.name == "stub"


def test_build_provider_github(monkeypatch):
    monkeypatch.setenv("GITHUB_TOKEN", "test-token")
    cfg = GatewayConfig(provider="github")
    provider = _build_provider(cfg)
    assert isinstance(provider, GitHubModelsProvider)
    assert provider.name == "github"


def test_build_provider_copilot():
    cfg = GatewayConfig(provider="copilot")
    provider = _build_provider(cfg)
    assert isinstance(provider, CopilotProvider)
    assert provider.name == "copilot"


def test_build_provider_unknown_falls_back_to_stub():
    cfg = GatewayConfig(provider="nonexistent-provider")
    with pytest.warns(RuntimeWarning, match="Unknown LLM provider"):
        provider = _build_provider(cfg)
    assert isinstance(provider, StubProvider)


# ---------------------------------------------------------------------------
# Provider health checks
# ---------------------------------------------------------------------------


def test_stub_provider_is_always_configured():
    p = StubProvider()
    assert p.is_configured() is True


def test_stub_provider_health_ok():
    health = StubProvider().health_check()
    assert health["status"] == "ok"
    assert health["provider"] == "stub"


def test_github_provider_not_configured_without_token(monkeypatch):
    for var in ("GITHUB_TOKEN", "GH_TOKEN", "GITHUB_PAT"):
        monkeypatch.delenv(var, raising=False)
    p = GitHubModelsProvider(api_key="")
    assert p.is_configured() is False


def test_github_provider_configured_with_token(monkeypatch):
    monkeypatch.setenv("GITHUB_TOKEN", "ghp_test")
    p = GitHubModelsProvider(api_key="")
    assert p.is_configured() is True


def test_github_provider_health_error_without_token(monkeypatch):
    for var in ("GITHUB_TOKEN", "GH_TOKEN", "GITHUB_PAT"):
        monkeypatch.delenv(var, raising=False)
    health = GitHubModelsProvider(api_key="").health_check()
    assert health["status"] == "error"
    assert "GITHUB_TOKEN" in health["error"]


def test_github_provider_health_ok_with_token(monkeypatch):
    monkeypatch.setenv("GITHUB_TOKEN", "ghp_test")
    health = GitHubModelsProvider(api_key="").health_check()
    assert health["status"] == "ok"


def test_copilot_provider_not_configured():
    p = CopilotProvider()
    assert p.is_configured() is False


def test_copilot_provider_health_error():
    health = CopilotProvider().health_check()
    assert health["status"] == "error"
    assert "copilot" in health["provider"]


@pytest.mark.asyncio
async def test_copilot_provider_complete_raises_not_implemented():
    p = CopilotProvider()
    with pytest.raises(NotImplementedError, match="programmatic"):
        await p.complete("any-model", [{"role": "user", "content": "hi"}])


# ---------------------------------------------------------------------------
# GatewayRouter model resolution
# ---------------------------------------------------------------------------


def test_router_resolve_model_explicit():
    cfg = GatewayConfig(default_model="openai/gpt-4o-mini")
    router = GatewayRouter(cfg)
    assert router.resolve_model("openai/gpt-4o") == "openai/gpt-4o"


def test_router_resolve_model_by_role():
    cfg = GatewayConfig(
        default_model="openai/gpt-4o-mini",
        model_policy={"planning": "openai/gpt-4o"},
    )
    router = GatewayRouter(cfg)
    assert router.resolve_model(role="planning") == "openai/gpt-4o"


def test_router_resolve_model_default():
    cfg = GatewayConfig(default_model="openai/gpt-4o-mini")
    router = GatewayRouter(cfg)
    assert router.resolve_model() == "openai/gpt-4o-mini"


def test_router_explicit_model_overrides_role():
    cfg = GatewayConfig(
        default_model="default-model",
        model_policy={"coding": "policy-model"},
    )
    router = GatewayRouter(cfg)
    # Explicit model should win over role policy
    assert (
        router.resolve_model(requested_model="override-model", role="coding")
        == "override-model"
    )


# ---------------------------------------------------------------------------
# GatewayRouter provider selection
# ---------------------------------------------------------------------------


def test_router_selects_stub_by_default():
    cfg = GatewayConfig(provider="stub")
    router = GatewayRouter(cfg)
    provider = router.select_provider()
    assert isinstance(provider, StubProvider)


def test_router_selects_github_when_configured(monkeypatch):
    monkeypatch.setenv("GITHUB_TOKEN", "ghp_test")
    cfg = GatewayConfig(provider="github")
    router = GatewayRouter(cfg)
    provider = router.select_provider()
    assert isinstance(provider, GitHubModelsProvider)


def test_router_falls_back_to_stub_when_github_not_configured(monkeypatch):
    """If github provider has no token, router falls back to stub."""
    for var in ("GITHUB_TOKEN", "GH_TOKEN", "GITHUB_PAT"):
        monkeypatch.delenv(var, raising=False)
    cfg = GatewayConfig(provider="github", api_key="")
    router = GatewayRouter(cfg)
    with pytest.warns(RuntimeWarning, match="not configured"):
        provider = router.select_provider()
    assert isinstance(provider, StubProvider)


def test_router_reuses_provider_instance():
    """Provider should be lazily created and cached."""
    cfg = GatewayConfig(provider="stub")
    router = GatewayRouter(cfg)
    first = router.select_provider()
    second = router.select_provider()
    assert first is second


# ---------------------------------------------------------------------------
# GatewayRouter.complete (integration with stub)
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_router_complete_stub_returns_response():
    cfg = GatewayConfig(provider="stub", default_model="test-model")
    router = GatewayRouter(cfg)
    messages = [{"role": "user", "content": "Hello"}]
    result = await router.complete(messages=messages)
    assert result["choices"][0]["message"]["role"] == "assistant"
    assert "Hello" in result["choices"][0]["message"]["content"]


@pytest.mark.asyncio
async def test_router_complete_for_role_uses_policy_model():
    cfg = GatewayConfig(
        provider="stub",
        default_model="default-model",
        model_policy={"planning": "planning-model"},
    )
    router = GatewayRouter(cfg)
    messages = [{"role": "user", "content": "Plan something"}]
    result = await router.complete_for_role("planning", messages=messages)
    # Stub echoes the model name back in the response
    assert result["model"] == "planning-model"


# ---------------------------------------------------------------------------
# GatewayRouter.health
# ---------------------------------------------------------------------------


def test_router_health_stub_ok():
    cfg = GatewayConfig(provider="stub", default_model="m", model_policy={"x": "y"})
    router = GatewayRouter(cfg)
    health = router.health()
    assert health["status"] == "ok"
    assert health["default_model"] == "m"
    assert health["model_policy"] == {"x": "y"}


def test_router_health_github_error_without_token(monkeypatch):
    for var in ("GITHUB_TOKEN", "GH_TOKEN", "GITHUB_PAT"):
        monkeypatch.delenv(var, raising=False)
    cfg = GatewayConfig(provider="github", api_key="")
    router = GatewayRouter(cfg)
    # Router falls back to stub when github is unconfigured; stub is always healthy
    with pytest.warns(RuntimeWarning, match="not configured"):
        health = router.health()
    assert health["status"] == "ok"
    assert health["provider"] == "stub"
