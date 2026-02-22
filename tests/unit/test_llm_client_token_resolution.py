from types import SimpleNamespace

from agents.llm_client import LLMClientFactory


def test_resolve_github_api_key_prefers_non_placeholder_config(monkeypatch):
    monkeypatch.delenv("GITHUB_TOKEN", raising=False)
    monkeypatch.delenv("GH_TOKEN", raising=False)
    monkeypatch.delenv("GITHUB_PAT", raising=False)
    LLMClientFactory._cached_github_token = None

    resolved = LLMClientFactory.resolve_github_api_key("ghp_config_token")

    assert resolved == "ghp_config_token"


def test_resolve_github_api_key_uses_env_when_placeholder(monkeypatch):
    monkeypatch.setenv("GH_TOKEN", "ghp_env_token")
    monkeypatch.delenv("GITHUB_TOKEN", raising=False)
    monkeypatch.delenv("GITHUB_PAT", raising=False)
    LLMClientFactory._cached_github_token = None

    resolved = LLMClientFactory.resolve_github_api_key("your-api-key-here")

    assert resolved == "ghp_env_token"


def test_resolve_github_api_key_falls_back_to_gh_auth_token(monkeypatch):
    monkeypatch.delenv("GITHUB_TOKEN", raising=False)
    monkeypatch.delenv("GH_TOKEN", raising=False)
    monkeypatch.delenv("GITHUB_PAT", raising=False)
    LLMClientFactory._cached_github_token = None

    def fake_run(*args, **kwargs):
        return SimpleNamespace(returncode=0, stdout="ghp_cli_token\n")

    monkeypatch.setattr("agents.llm_client.subprocess.run", fake_run)

    resolved = LLMClientFactory.resolve_github_api_key("your-api-key-here")

    assert resolved == "ghp_cli_token"
