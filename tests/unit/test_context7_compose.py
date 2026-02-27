from __future__ import annotations

from pathlib import Path

import yaml


def test_context7_compose_has_expected_service_config() -> None:
    compose_path = Path("docker-compose.context7.yml")
    assert compose_path.exists(), "docker-compose.context7.yml should exist"

    data = yaml.safe_load(compose_path.read_text(encoding="utf-8"))
    assert isinstance(data, dict)
    services = data.get("services")
    assert isinstance(services, dict)

    context7 = services.get("context7")
    assert isinstance(context7, dict)

    build = context7.get("build")
    assert isinstance(build, dict)
    assert build.get("context") == "."
    assert build.get("dockerfile") == "docker/context7/Dockerfile"

    assert context7.get("container_name") == "context7-mcp"
    assert context7.get("restart") == "unless-stopped"

    env = context7.get("environment")
    assert isinstance(env, list)
    assert "CONTEXT7_PORT=3010" in env
    assert "CONTEXT7_API_KEY=${CONTEXT7_API_KEY:-}" in env

    ports = context7.get("ports")
    assert isinstance(ports, list)
    assert "127.0.0.1:3010:3010" in ports
