"""
Pytest configuration for TUI E2E tests.

Provides fixtures for backend API server, TUI automation, and test data cleanup.
"""

import pytest
import tempfile
import shutil
import sys
from pathlib import Path

# Add helpers to path (before local imports)
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "tests"))

from helpers.tui_automation import TUIAutomation  # noqa: E402
from fixtures.factories import ProjectFactory  # noqa: E402
from e2e.tui.helpers import (  # noqa: E402
    build_tui_workspace,
    reset_tui_workspace,
    start_backend_server,
    stop_backend_server,
)


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

    project_root = Path(__file__).resolve().parent.parent.parent.parent
    try:
        proc, api_url = start_backend_server(
            api_dir=api_dir,
            docs_dir=Path(temp_docs_dir),
            project_root=project_root,
            startup_timeout_seconds=60.0,
        )
        print(f"\n✓ Backend server started at {api_url}")
    except TimeoutError:
        # If startup timed out, try to capture process output when available.
        stdout = ""
        stderr = ""
        if "proc" in locals() and proc is not None:
            proc.terminate()
            stdout, stderr = proc.communicate(timeout=2)
        details = ""
        if stdout:
            details += f"\n--- stdout ---\n{stdout.strip()}"
        if stderr:
            details += f"\n--- stderr ---\n{stderr.strip()}"
        pytest.fail("Backend server failed to start within 60s" + details)

    yield api_url

    # Cleanup
    stop_backend_server(proc, timeout_seconds=5.0)


@pytest.fixture
def tui(backend_server: str) -> TUIAutomation:
    """Create TUI automation instance connected to backend server.

    Skips the test gracefully when the TUI binary is not present so that CI
    environments without the CLI do not produce hard failures.
    """
    try:
        return TUIAutomation(api_base_url=backend_server, timeout=30)
    except FileNotFoundError as exc:
        pytest.skip(f"TUI binary not available: {exc}")


@pytest.fixture
def project_factory() -> ProjectFactory:
    """Provide ProjectFactory for creating test projects."""
    return ProjectFactory()


@pytest.fixture
def unique_project_key() -> str:
    """Generate a unique project key for each test."""
    return ProjectFactory.random_key()


@pytest.fixture
def tui_workspace(temp_docs_dir: str, unique_project_key: str):
    """Provide deterministic project workspace setup/teardown for TUI E2E tests."""
    workspace = build_tui_workspace(temp_docs_dir, unique_project_key)
    yield workspace
    reset_tui_workspace(workspace)
