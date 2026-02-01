"""Pytest fixtures for TUI E2E tests.

Provides test fixtures for TUI automation, API setup, and test data management.
"""

import pytest
import subprocess
import os
import sys
from pathlib import Path
from typing import Generator

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from helpers.tui_automation import TUIAutomation, TUIAssertions  # noqa: E402
from fixtures.factories import (  # noqa: E402
    ProjectFactory,
    ArtifactFactory,
    ProposalFactory,
    RAIDItemFactory,
    AuditResultFactory,
)


@pytest.fixture(scope="session")
def api_base_url() -> str:
    """Get API base URL from environment or default."""
    return os.getenv("API_BASE_URL", "http://localhost:8000")


@pytest.fixture(scope="session")
def api_server(api_base_url: str) -> Generator[subprocess.Popen | None, None, None]:
    """Start API server for E2E tests (if not already running).

    This fixture attempts to start the API server. If the server is already
    running, it will be reused. The fixture will wait for the server to be
    ready before yielding.
    """
    # Check if server is already running
    tui = TUIAutomation(api_base_url=api_base_url)
    if tui.wait_for_api(max_retries=2, retry_delay=0.5):
        # Server already running, don't start a new one
        yield None
        return

    # Start API server
    api_dir = Path(__file__).parent.parent.parent / "apps" / "api"
    project_docs = Path(__file__).parent.parent.parent / "projectDocs"
    project_docs.mkdir(exist_ok=True)

    env = os.environ.copy()
    env["PROJECT_DOCS_PATH"] = str(project_docs)

    # Use python from venv if available, otherwise system python
    venv_python = Path(__file__).parent.parent.parent / ".venv" / "bin" / "python"
    python_cmd = str(venv_python) if venv_python.exists() else "python"

    process = subprocess.Popen(
        [
            python_cmd,
            "-m",
            "uvicorn",
            "main:app",
            "--host",
            "0.0.0.0",
            "--port",
            "8000",
        ],
        cwd=str(api_dir),
        env=env,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )

    # Wait for API to be ready
    tui = TUIAutomation(api_base_url=api_base_url)
    if not tui.wait_for_api(max_retries=30, retry_delay=1.0):
        process.terminate()
        process.wait()
        raise RuntimeError("API server failed to start within 30 seconds")

    yield process

    # Cleanup
    process.terminate()
    process.wait(timeout=5)


@pytest.fixture
def tui(api_base_url: str, api_server) -> TUIAutomation:
    """Get TUI automation instance."""
    return TUIAutomation(api_base_url=api_base_url)


@pytest.fixture
def assertions() -> TUIAssertions:
    """Get TUI assertions helper."""
    return TUIAssertions()


@pytest.fixture
def project_factory() -> ProjectFactory:
    """Get project factory."""
    return ProjectFactory()


@pytest.fixture
def artifact_factory() -> ArtifactFactory:
    """Get artifact factory."""
    return ArtifactFactory()


@pytest.fixture
def proposal_factory() -> ProposalFactory:
    """Get proposal factory."""
    return ProposalFactory()


@pytest.fixture
def raid_factory() -> RAIDItemFactory:
    """Get RAID item factory."""
    return RAIDItemFactory()


@pytest.fixture
def audit_factory() -> AuditResultFactory:
    """Get audit result factory."""
    return AuditResultFactory()


@pytest.fixture
def test_project(tui: TUIAutomation, project_factory: ProjectFactory):
    """Create a test project and clean up after test.

    Returns the project key for use in tests.
    """
    project_data = project_factory.build()
    project_key = project_data["key"]

    # Create project via TUI
    result = tui.execute_command(
        f"projects create --key {project_key} "
        f"--name \"{project_data['name']}\" "
        f"--description \"{project_data['description']}\""
    )

    assert result.success, f"Failed to create test project: {result.stderr}"

    yield project_key

    # Cleanup (best effort)
    tui.cleanup_project(project_key)


@pytest.fixture(autouse=True)
def reset_test_environment():
    """Reset test environment before each test.

    This fixture runs automatically before each test to ensure
    a clean state. It's currently a placeholder for future cleanup logic.
    """
    # Pre-test setup
    yield
    # Post-test cleanup
    pass
