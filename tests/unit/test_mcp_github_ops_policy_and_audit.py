import json
from pathlib import Path

import pytest

from apps.mcp.github_ops.audit_store import AuditRecord, AuditStore, redact_secrets
from apps.mcp.github_ops.policy import GitHubOpsPolicy


def test_policy_from_env_defaults_allow_expected_repos(monkeypatch: pytest.MonkeyPatch) -> None:
    policy = GitHubOpsPolicy.from_env(
        allowed_repos_env=None,
        default_allowed_repos=[
            "blecx/AI-Agent-Framework",
            "blecx/AI-Agent-Framework-Client",
        ],
    )

    assert "blecx/AI-Agent-Framework" in policy.allowed_repos
    assert "blecx/AI-Agent-Framework-Client" in policy.allowed_repos


def test_policy_from_env_parses_csv(monkeypatch: pytest.MonkeyPatch) -> None:
    policy = GitHubOpsPolicy.from_env(
        allowed_repos_env=" org/repo1 ,org/repo2, ,org/repo3 ",
        default_allowed_repos=["org/ignored"],
    )

    assert policy.allowed_repos == {"org/repo1", "org/repo2", "org/repo3"}


def test_policy_validate_repo_rejects_unlisted_repo() -> None:
    policy = GitHubOpsPolicy(allowed_repos={"org/repo1"})

    with pytest.raises(ValueError) as exc:
        policy.validate_repo("org/repo2")

    assert "not allowed" in str(exc.value).lower()


def test_redact_secrets_redacts_common_token_fields() -> None:
    token = "ghp_" + ("A" * 25)
    text = f"GH_TOKEN={token} use {token} in a string"
    redacted = redact_secrets(text)
    assert token not in redacted
    assert "[REDACTED]" in redacted


def test_audit_store_writes_redacted_json(tmp_path: Path) -> None:
    store = AuditStore(tmp_path)

    token = "ghp_" + ("B" * 30)

    record = AuditRecord(
        run_id="test-run",
        tool="test",
        timestamp_utc="2026-01-01T00:00:00Z",
        status="ok",
        exit_code=0,
        duration_sec=0.0,
        cwd="/tmp",
        command=["echo", "hello"],
        output=f"token={token} GH_TOKEN={token}",
    )

    path = store.save(record)

    loaded = json.loads(path.read_text(encoding="utf-8"))
    assert token not in loaded["output"]
    assert "[REDACTED]" in loaded["output"]
