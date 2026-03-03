from __future__ import annotations

import subprocess
from pathlib import Path

import pytest

from apps.mcp.devops.docker_compose_service import DockerComposeService


def _service(tmp_path: Path) -> DockerComposeService:
    compose_file = tmp_path / "docker-compose.yml"
    compose_file.write_text("services: {}\n", encoding="utf-8")
    return DockerComposeService(
        repo_root=tmp_path,
        compose_targets={"main": "docker-compose.yml"},
        audit_dir=tmp_path / ".tmp" / "mcp-docker-compose",
    )


def test_compose_up_builds_expected_command(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    service = _service(tmp_path)

    captured: dict[str, list[str]] = {}

    def fake_run(command: list[str], cwd: Path, capture_output: bool, text: bool, check: bool) -> subprocess.CompletedProcess[str]:
        captured["command"] = command
        return subprocess.CompletedProcess(command, 0, stdout="ok\n", stderr="")

    monkeypatch.setattr(subprocess, "run", fake_run)
    result = service.compose_up(target="main", build=True, detach=True)

    assert result["status"] == "ok"
    assert captured["command"] == ["docker", "compose", "-f", "docker-compose.yml", "up", "--build", "-d"]


def test_compose_rejects_unknown_target(tmp_path: Path) -> None:
    service = _service(tmp_path)
    with pytest.raises(ValueError):
        service.compose_ps(target="missing")
