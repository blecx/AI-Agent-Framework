"""Unit tests for MCP Bash Gateway implementation."""

from pathlib import Path

import pytest

from apps.mcp.bash_gateway.policy import BashGatewayPolicy, PolicyViolationError
from apps.mcp.bash_gateway.server import BashGatewayServer


@pytest.fixture
def temp_repo(tmp_path: Path) -> Path:
    """Create temp repo root with scripts and .tmp dirs."""
    scripts = tmp_path / "scripts"
    scripts.mkdir(parents=True, exist_ok=True)

    ok_script = scripts / "ok.sh"
    ok_script.write_text("#!/usr/bin/env bash\necho OK\n")

    fail_script = scripts / "fail.sh"
    fail_script.write_text("#!/usr/bin/env bash\necho FAIL >&2\nexit 3\n")

    slow_script = scripts / "slow.sh"
    slow_script.write_text("#!/usr/bin/env bash\nsleep 2\necho DONE\n")

    return tmp_path


@pytest.fixture
def policy() -> BashGatewayPolicy:
    """Build test policy with two profiles."""
    return BashGatewayPolicy.from_dict(
        {
            "profiles": {
                "issue": {
                    "scripts": ["scripts/ok.sh", "scripts/fail.sh", "scripts/slow.sh"],
                    "default_timeout_sec": 3,
                    "max_timeout_sec": 5,
                    "default_dry_run": True,
                },
                "ci": {
                    "scripts": ["scripts/ok.sh"],
                    "default_timeout_sec": 30,
                    "max_timeout_sec": 60,
                    "default_dry_run": False,
                },
            }
        }
    )


def test_list_project_scripts_returns_profiles(
    temp_repo: Path, policy: BashGatewayPolicy
):
    """Server lists scripts for all profiles."""
    server = BashGatewayServer(repo_root=temp_repo, policy=policy)
    result = server.list_project_scripts()
    assert "profiles" in result
    assert "issue" in result["profiles"]
    assert "scripts/ok.sh" in result["profiles"]["issue"]


def test_describe_script_validates_allowlist(
    temp_repo: Path, policy: BashGatewayPolicy
):
    """Describe should fail for non-allowlisted script."""
    server = BashGatewayServer(repo_root=temp_repo, policy=policy)

    with pytest.raises(PolicyViolationError):
        server.describe_script(profile="ci", script_path="scripts/fail.sh")


def test_run_project_script_dry_run_default(temp_repo: Path, policy: BashGatewayPolicy):
    """Issue profile defaults to dry-run and logs simulated status."""
    server = BashGatewayServer(repo_root=temp_repo, policy=policy)

    result = server.run_project_script(profile="issue", script_path="scripts/ok.sh")
    assert result["status"] == "simulated"
    assert result["exit_code"] == 0
    assert "DRY-RUN" in result["output"]

    log = server.get_script_run_log(result["run_id"])
    assert log is not None
    assert log["dry_run"] is True
    assert log["status"] == "simulated"


def test_run_project_script_executes_when_dry_run_disabled(
    temp_repo: Path, policy: BashGatewayPolicy
):
    """Explicit dry_run=False executes script and captures output."""
    server = BashGatewayServer(repo_root=temp_repo, policy=policy)

    result = server.run_project_script(
        profile="issue",
        script_path="scripts/ok.sh",
        dry_run=False,
    )
    assert result["status"] == "success"
    assert result["exit_code"] == 0
    assert "OK" in result["output"]


def test_timeout_is_enforced(temp_repo: Path, policy: BashGatewayPolicy):
    """Slow script should time out with timeout status."""
    server = BashGatewayServer(repo_root=temp_repo, policy=policy)

    result = server.run_project_script(
        profile="issue",
        script_path="scripts/slow.sh",
        dry_run=False,
        timeout_sec=1,
    )
    assert result["status"] == "timeout"
    assert result["exit_code"] == 124


def test_timeout_over_max_is_rejected(temp_repo: Path, policy: BashGatewayPolicy):
    """Policy should reject timeout values above profile max."""
    server = BashGatewayServer(repo_root=temp_repo, policy=policy)

    with pytest.raises(PolicyViolationError):
        server.run_project_script(
            profile="issue",
            script_path="scripts/ok.sh",
            timeout_sec=999,
        )


def test_path_traversal_denied(temp_repo: Path, policy: BashGatewayPolicy):
    """Path traversal should always be denied."""
    server = BashGatewayServer(repo_root=temp_repo, policy=policy)

    with pytest.raises(PolicyViolationError):
        server.run_project_script(
            profile="issue",
            script_path="../scripts/ok.sh",
        )
