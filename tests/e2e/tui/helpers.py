"""Deterministic helper utilities for TUI E2E tests."""

from __future__ import annotations

import os
import shutil
import socket
import subprocess
import sys
import time
from dataclasses import dataclass
from pathlib import Path
import json

import httpx


def wait_for_http_ok(
    url: str, timeout_seconds: float = 10.0, attempt_timeout: float = 0.5
) -> None:
    """Wait until an HTTP endpoint responds with 200, else raise TimeoutError."""
    start_time = time.monotonic()
    with httpx.Client(timeout=timeout_seconds) as client:
        while True:
            remaining = timeout_seconds - (time.monotonic() - start_time)
            if remaining <= 0:
                break

            timeout = min(attempt_timeout, remaining)
            try:
                response = client.get(url, timeout=timeout)
                if response.status_code == 200:
                    return
            except (httpx.ConnectError, httpx.ReadTimeout):
                pass

    raise TimeoutError(
        f"Endpoint did not become healthy in {timeout_seconds:.1f}s: {url}"
    )


def resolve_python_executable(project_root: Path) -> str:
    venv_python = project_root / ".venv" / "bin" / "python"
    if venv_python.exists():
        return str(venv_python)
    return sys.executable


def reserve_local_port() -> int:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as socket_handle:
        socket_handle.bind(("127.0.0.1", 0))
        socket_handle.listen(1)
        return socket_handle.getsockname()[1]


def start_backend_server(
    *,
    api_dir: Path,
    docs_dir: Path,
    project_root: Path,
    startup_timeout_seconds: float = 60.0,
) -> tuple[subprocess.Popen, str]:
    env = os.environ.copy()
    env["PROJECT_DOCS_PATH"] = str(docs_dir)

    port = reserve_local_port()
    api_url = f"http://localhost:{port}"
    python_executable = resolve_python_executable(project_root)

    process = subprocess.Popen(
        [
            python_executable,
            "-m",
            "uvicorn",
            "main:app",
            "--host",
            "127.0.0.1",
            "--port",
            str(port),
        ],
        cwd=str(api_dir),
        env=env,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
    )

    wait_for_http_ok(f"{api_url}/health", timeout_seconds=startup_timeout_seconds)
    return process, api_url


def stop_backend_server(process: subprocess.Popen, timeout_seconds: float = 5.0) -> None:
    process.terminate()
    try:
        process.wait(timeout=timeout_seconds)
    except subprocess.TimeoutExpired:
        process.kill()


@dataclass(frozen=True)
class TuiE2EWorkspace:
    docs_root: Path
    project_key: str

    @property
    def project_dir(self) -> Path:
        return self.docs_root / self.project_key

    @property
    def metadata_path(self) -> Path:
        return self.project_dir / "metadata.json"

    def artifact_path(self, name: str) -> Path:
        return self.project_dir / "artifacts" / f"{name}.json"

    def workflow_path(self, name: str) -> Path:
        return self.project_dir / "workflow" / f"{name}.json"


def build_tui_workspace(temp_docs_dir: str | Path, project_key: str) -> TuiE2EWorkspace:
    docs_root = Path(temp_docs_dir)
    docs_root.mkdir(parents=True, exist_ok=True)
    workspace = TuiE2EWorkspace(docs_root=docs_root, project_key=project_key)
    workspace.project_dir.mkdir(parents=True, exist_ok=True)
    return workspace


def reset_tui_workspace(workspace: TuiE2EWorkspace) -> None:
    shutil.rmtree(workspace.project_dir, ignore_errors=True)


def write_json(path: Path, payload: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2), encoding="utf-8")

