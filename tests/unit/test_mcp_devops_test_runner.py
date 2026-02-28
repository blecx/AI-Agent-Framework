from __future__ import annotations

import subprocess
from pathlib import Path

import pytest

from apps.mcp.devops.test_runner_service import TestRunnerService, TestRunnerServiceError


def _service(tmp_path: Path) -> TestRunnerService:
    return TestRunnerService(
        repo_root=tmp_path,
        audit_dir=tmp_path / ".tmp" / "mcp-test-runner",
    )


def test_profiles_include_backend_and_frontend(tmp_path: Path) -> None:
    service = _service(tmp_path)
    profiles = service.list_profiles()["profiles"]
    names = {profile["name"] for profile in profiles}

    assert "backend.tests" in names
    assert "frontend.build" in names


def test_run_profile_success(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    service = _service(tmp_path)

    def fake_run(*args, **kwargs) -> subprocess.CompletedProcess[str]:
        return subprocess.CompletedProcess(kwargs.get("args", []), 0, stdout="passed\n", stderr="")

    monkeypatch.setattr(subprocess, "run", fake_run)
    result = service.run_profile("backend.tests_quick")

    assert result["status"] == "ok"
    assert result["exit_code"] == 0


def test_run_profile_failure_raises(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    service = _service(tmp_path)

    def fake_run(*args, **kwargs) -> subprocess.CompletedProcess[str]:
        return subprocess.CompletedProcess(kwargs.get("args", []), 1, stdout="", stderr="boom")

    monkeypatch.setattr(subprocess, "run", fake_run)
    with pytest.raises(TestRunnerServiceError):
        service.run_profile("backend.tests")
