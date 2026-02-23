"""
Pytest configuration for TUI E2E tests.

Provides fixtures for backend API server, TUI automation, and test data cleanup.
"""

import pytest
import subprocess
import tempfile
import shutil
import sys
import os
import socket
from pathlib import Path

# Add helpers to path (before local imports)
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "tests"))

from helpers.tui_automation import TUIAutomation  # noqa: E402
from fixtures.factories import ProjectFactory  # noqa: E402
from e2e.tui.helpers import wait_for_http_ok  # noqa: E402


@pytest.fixture(scope="session")
def temp_docs_dir() -> str:
    """Create a temporary directory for project documents (session scope)."""
    temp_dir = tempfile.mkdtemp(prefix="e2e-tui-docs-")
    yield temp_dir
    shutil.rmtree(temp_dir, ignore_errors=True)


@pytest.fixture(scope="session")
def backend_server(temp_docs_dir: str) -> str:
    """Start backend API server for E2E tests (session scope).

    Starts uvicorn server, waits for health check, yields, then terminates.
    """
    api_dir = Path(__file__).resolve().parent.parent.parent.parent / "apps" / "api"

    if not api_dir.exists():
        pytest.skip(f"API directory not found at {api_dir}")

    # Start server
    env = os.environ.copy()
    env["PROJECT_DOCS_PATH"] = temp_docs_dir

    # Pick a free localhost port to avoid conflicts with other tests
    # (e.g. Docker-based tutorial tests that bind host port 8000).
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind(("127.0.0.1", 0))
        s.listen(1)
        port = s.getsockname()[1]

    proc = subprocess.Popen(
        [
            sys.executable,
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

    # Wait for server to be ready (health check)
    api_url = f"http://localhost:{port}"
    try:
        wait_for_http_ok(f"{api_url}/health", timeout_seconds=10.0)
        print(f"\n✓ Backend server started at {api_url}")
    except TimeoutError:
        proc.terminate()
        pytest.fail("Backend server failed to start within 10s")

    yield api_url

    # Cleanup
    proc.terminate()
    try:
        proc.wait(timeout=5)
    except subprocess.TimeoutExpired:
        proc.kill()


@pytest.fixture
def tui(backend_server: str) -> TUIAutomation:
    """Create TUI automation instance connected to backend server."""
    return TUIAutomation(api_base_url=backend_server, timeout=30)


@pytest.fixture
def project_factory() -> ProjectFactory:
    """Provide ProjectFactory for creating test projects."""
    return ProjectFactory()


@pytest.fixture
def unique_project_key() -> str:
    """Generate a unique project key for each test."""
    return ProjectFactory.random_key()
