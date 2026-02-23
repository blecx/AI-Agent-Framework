"""
Shared pytest fixtures for tutorial E2E tests.

Provides:
- Docker environment management
- TUI automation helpers
- Clean project directory fixtures
- API health check fixtures
- Web driver fixtures (optional)
"""

import os
import pytest
import subprocess
import time
import requests
from pathlib import Path
import shutil


# Test configuration
PROJECT_ROOT = Path(__file__).parent.parent.parent.parent
PROJECT_DOCS_PATH = PROJECT_ROOT / "projectDocs"
API_BASE_URL = "http://localhost:8000"
WEB_BASE_URL = "http://localhost:5173"


def _require_gui_tests() -> None:
    if os.getenv("RUN_GUI_TESTS") != "1":
        pytest.skip("GUI Playwright fixtures require RUN_GUI_TESTS=1.")


@pytest.fixture(scope="session")
def docker_environment():
    """
    Session-scoped fixture to manage Docker environment.
    Starts Docker Compose at the beginning of the test session,
    stops it at the end.
    """
    print("\n🐳 Starting Docker environment...")

    # Ensure we're in project root
    os.chdir(PROJECT_ROOT)

    # Stop any existing services
    subprocess.run(
        ["docker", "compose", "down", "-v"],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )

    # Start services
    result = subprocess.run(
        ["docker", "compose", "up", "-d"], capture_output=True, text=True
    )

    if result.returncode != 0:
        pytest.fail(f"Failed to start Docker services: {result.stderr}")

    # Wait for services to be ready
    print("⏳ Waiting for services to be ready...")
    time.sleep(10)

    # Wait for API health
    max_attempts = 30
    for attempt in range(max_attempts):
        try:
            response = requests.get(f"{API_BASE_URL}/health", timeout=5)
            if response.status_code == 200:
                print("✅ API is healthy")
                break
        except requests.RequestException:
            pass

        if attempt == max_attempts - 1:
            pytest.fail("API failed to become healthy")

        time.sleep(2)

    yield

    # Teardown
    print("\n🛑 Stopping Docker environment...")
    subprocess.run(
        ["docker", "compose", "down"],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )


@pytest.fixture(scope="function")
def clean_project_docs(docker_environment):
    """
    Function-scoped fixture to clean project docs before each test.
    Ensures each test starts with a clean slate.
    """
    # Clean test project directories
    if PROJECT_DOCS_PATH.exists():
        for item in PROJECT_DOCS_PATH.iterdir():
            if item.is_dir() and item.name.startswith("TEST-"):
                shutil.rmtree(item, ignore_errors=True)
    else:
        PROJECT_DOCS_PATH.mkdir(parents=True, exist_ok=True)

    yield PROJECT_DOCS_PATH

    # Cleanup after test (optional - could be disabled for debugging)
    # for item in PROJECT_DOCS_PATH.iterdir():
    #     if item.is_dir() and item.name.startswith("TEST-"):
    #         shutil.rmtree(item, ignore_errors=True)


@pytest.fixture
def api_client(clean_project_docs):
    """
    Provides a requests.Session for API testing.
    """
    session = requests.Session()
    session.headers.update({"Content-Type": "application/json"})
    yield session
    session.close()


@pytest.fixture
def api_health_check(api_client):
    """
    Verifies API is healthy before test runs.
    """
    response = api_client.get(f"{API_BASE_URL}/health")
    assert response.status_code == 200, "API is not healthy"
    data = response.json()
    assert data.get("status") == "healthy", "API status is not healthy"
    return data


@pytest.fixture
def tui_path():
    """
    Returns path to TUI application.
    """
    return PROJECT_ROOT / "apps" / "tui"


@pytest.fixture
def tui_python():
    """
    Returns Python executable to use for TUI commands.
    Prefers venv Python if available.
    """
    venv_python = PROJECT_ROOT / ".venv" / "bin" / "python"
    if venv_python.exists():
        return str(venv_python)
    return "python3"


class TUIAutomation:
    """
    Helper class for automating TUI commands.
    """

    def __init__(self, tui_path: Path, python_exe: str, api_base_url: str):
        self.tui_path = tui_path
        self.python_exe = python_exe
        self.api_base_url = api_base_url

    def run_command(self, *args, check=True, capture_output=True):
        """
        Execute a TUI command.

        Args:
            *args: Command arguments (e.g., "projects", "create", "--key", "TEST")
            check: Raise exception on non-zero exit code
            capture_output: Capture stdout/stderr

        Returns:
            subprocess.CompletedProcess
        """
        cmd = [self.python_exe, "main.py"] + list(args)

        result = subprocess.run(
            cmd,
            cwd=self.tui_path,
            capture_output=capture_output,
            text=True,
            check=False,
        )

        if check and result.returncode != 0:
            raise subprocess.CalledProcessError(
                result.returncode, cmd, output=result.stdout, stderr=result.stderr
            )

        return result

    def create_project(self, key: str, name: str, description: str = ""):
        """Create a project via TUI."""
        args = ["projects", "create", "--key", key, "--name", name]
        if description:
            args.extend(["--description", description])
        return self.run_command(*args)

    def list_projects(self):
        """List all projects."""
        return self.run_command("projects", "list")

    def add_raid_entry(
        self,
        project: str,
        entry_type: str,
        severity: str,
        description: str,
        mitigation: str,
    ):
        """Add a RAID entry."""
        return self.run_command(
            "raid",
            "add",
            "--project",
            project,
            "--type",
            entry_type,
            "--severity",
            severity,
            "--description",
            description,
            "--mitigation",
            mitigation,
        )

    def list_raid_entries(self, project: str):
        """List RAID entries for a project."""
        return self.run_command("raid", "list", "--project", project)

    def update_workflow(self, project: str, state: str):
        """Update workflow state (creates proposal)."""
        return self.run_command(
            "workflow", "update", "--project", project, "--state", state
        )

    def list_proposals(self, project: str):
        """List proposals for a project."""
        return self.run_command("proposals", "list", "--project", project)

    def apply_proposal(self, project: str, proposal_id: str):
        """Apply a proposal."""
        return self.run_command(
            "proposals", "apply", "--project", project, "--id", proposal_id
        )

    def create_artifact(
        self, project: str, artifact_type: str, title: str, prompt: str
    ):
        """Create an artifact."""
        return self.run_command(
            "artifacts",
            "create",
            "--project",
            project,
            "--type",
            artifact_type,
            "--title",
            title,
            "--prompt",
            prompt,
        )

    def assess_gaps(self, project: str):
        """Run gap assessment."""
        return self.run_command("assess-gaps", "--project", project)


@pytest.fixture
def tui_automation(tui_path, tui_python, clean_project_docs):
    """
    Provides TUIAutomation helper for tests.
    """
    return TUIAutomation(tui_path, tui_python, API_BASE_URL)


@pytest.fixture
def fresh_project(tui_automation):
    """
    Creates a fresh test project and returns its key.
    """
    project_key = f"TEST-{int(time.time() * 1000) % 1000000:06d}"

    result = tui_automation.create_project(
        key=project_key,
        name=f"Test Project {project_key}",
        description="Automated test project",
    )

    assert result.returncode == 0, f"Failed to create project: {result.stderr}"

    # Verify project exists
    project_path = PROJECT_DOCS_PATH / project_key
    assert project_path.exists(), f"Project directory not created: {project_path}"

    return project_key


@pytest.fixture
def browser_page(docker_environment):
    """
    Provides a Playwright browser page for GUI testing.
    Requires: pip install playwright && playwright install chromium
    """
    _require_gui_tests()
    from playwright.sync_api import sync_playwright, Error as PlaywrightError

    with sync_playwright() as p:
        try:
            browser = p.chromium.launch(headless=True)
        except PlaywrightError as e:
            msg = str(e)
            if "Executable doesn't exist" in msg or "playwright install" in msg:
                pytest.skip(
                    "Playwright browsers are not installed in this environment. "
                    "Install them with 'playwright install' (or 'playwright install chromium') to run GUI tutorial tests."
                )
            raise
        context = browser.new_context(
            viewport={"width": 1280, "height": 720}, ignore_https_errors=True
        )
        page = context.new_page()
        page.set_default_timeout(10000)  # 10s default timeout

        yield page

        context.close()
        browser.close()


# Test markers configuration (add to pytest.ini)
def pytest_configure(config):
    """
    Register custom markers.
    """
    config.addinivalue_line("markers", "tutorial: Tutorial E2E validation tests")
    config.addinivalue_line(
        "markers", "tutorial_validation: Tutorial validation framework tests"
    )
    config.addinivalue_line("markers", "tui: TUI-specific tests")
    config.addinivalue_line("markers", "gui: GUI-specific tests")
    config.addinivalue_line("markers", "slow: Slow-running tests (>30s)")
