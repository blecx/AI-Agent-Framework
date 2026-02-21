"""
E2E validation tests for Advanced Workflows tutorials.

Tests validate shipped TUI behavior used in advanced tutorials.

Notes:
- RAID commands are now available directly in TUI.
- Workflow commands are now available directly in TUI.
- Artifact creation still uses propose/apply workflows (no direct
    `artifacts create` command).
"""

import pytest
import subprocess
import tempfile
from pathlib import Path

# API URL for health checks
API_URL = "http://localhost:8000"


@pytest.fixture
def workspace_root():
    """Path to workspace root."""
    return Path(__file__).parent.parent.parent.parent


@pytest.fixture
def tui_path(workspace_root):
    """Path to TUI application."""
    return workspace_root / "apps" / "tui"


@pytest.fixture
def project_docs_path(workspace_root):
    """Path to projectDocs directory."""
    docs_path = workspace_root / "projectDocs"
    docs_path.mkdir(exist_ok=True)
    return docs_path


@pytest.fixture
def clean_project(project_docs_path):
    """Create a clean test project and clean up after."""
    project_key = "TEST-ADV"
    project_path = project_docs_path / project_key

    # Cleanup before test
    if project_path.exists():
        subprocess.run(["rm", "-rf", str(project_path)], check=False)

    yield project_key

    # Cleanup after test
    if project_path.exists():
        subprocess.run(["rm", "-rf", str(project_path)], check=False)


def check_api_running():
    """Check if API is available."""
    try:
        result = subprocess.run(
            ["curl", "-s", "-f", f"{API_URL}/health"],
            capture_output=True,
            text=True,
            timeout=2,
        )
        return result.returncode == 0
    except (subprocess.TimeoutExpired, FileNotFoundError):
        return False


@pytest.mark.tutorial
@pytest.mark.tutorial_validation
@pytest.mark.e2e
@pytest.mark.slow
class TestTutorial01HybridWorkflow:
    """Tests for Tutorial 01: TUI + GUI Hybrid Workflows.

    NOTE: Tutorial documents commands that don't exist. These tests validate
    actual TUI capabilities.
    """

    @pytest.mark.skipif(
        not check_api_running(), reason="API not running (required for TUI)"
    )
    def test_tui_health_check(self, tui_path):
        """Test TUI can check API health (Tutorial 01, Step 1)."""
        result = subprocess.run(
            ["python", "main.py", "health"],
            cwd=tui_path,
            capture_output=True,
            text=True,
        )

        assert result.returncode == 0, f"Health check failed: {result.stderr}"
        assert "healthy" in result.stdout.lower() or "ok" in result.stdout.lower()
        print("✅ TUI health check passed")

    @pytest.mark.skipif(not check_api_running(), reason="API not running")
    def test_create_project_tui_actual_api(
        self, tui_path, clean_project, project_docs_path
    ):
        """Test project creation with ACTUAL TUI API (Tutorial 01, Step 2).

        Tutorial shows: --description flag (doesn't exist)
        Actual API: Only --key and --name supported
        """
        result = subprocess.run(
            [
                "python",
                "main.py",
                "projects",
                "create",
                "--key",
                clean_project,
                "--name",
                "Test Hybrid Workflow",
            ],
            cwd=tui_path,
            capture_output=True,
            text=True,
        )

        # Check success or already exists
        success = (
            result.returncode == 0
            or "already exists" in result.stdout.lower()
            or "already exists" in result.stderr.lower()
        )
        assert (
            success
        ), f"Project creation failed: {result.stderr}\nStdout: {result.stdout}"

        # Verify project directory
        project_path = project_docs_path / clean_project
        assert project_path.exists(), f"Project directory not found: {project_path}"
        print(f"✅ Project {clean_project} created via TUI (actual API)")

    @pytest.mark.skipif(not check_api_running(), reason="API not running")
    def test_list_projects_tui(self, tui_path, clean_project):
        """Test listing projects via TUI (Tutorial 01, verification)."""
        # Create project first
        subprocess.run(
            [
                "python",
                "main.py",
                "projects",
                "create",
                "--key",
                clean_project,
                "--name",
                "Test",
            ],
            cwd=tui_path,
            capture_output=True,
        )

        # List projects
        result = subprocess.run(
            ["python", "main.py", "projects", "list"],
            cwd=tui_path,
            capture_output=True,
            text=True,
        )

        assert result.returncode == 0, f"Projects list failed: {result.stderr}"
        assert len(result.stdout) > 0, "Projects list output is empty"
        print(f"✅ Projects listed via TUI ({len(result.stdout.splitlines())} lines)")

    @pytest.mark.skipif(not check_api_running(), reason="API not running")
    def test_get_project_details(self, tui_path, clean_project):
        """Test getting project details via TUI (Tutorial 01, Step 3 - GUI alternative)."""
        # Create project first
        subprocess.run(
            [
                "python",
                "main.py",
                "projects",
                "create",
                "--key",
                clean_project,
                "--name",
                "Test",
            ],
            cwd=tui_path,
            check=True,
            capture_output=True,
        )

        # Get project details
        result = subprocess.run(
            ["python", "main.py", "projects", "get", "--key", clean_project],
            cwd=tui_path,
            capture_output=True,
            text=True,
        )

        assert result.returncode == 0, f"Project get failed: {result.stderr}"
        assert clean_project in result.stdout
        assert "Test" in result.stdout
        print("✅ Project details retrieved via TUI")

    @pytest.mark.skipif(not check_api_running(), reason="API not running")
    def test_raid_operations_supported(self, tui_path, clean_project):
        """Validate RAID add/list commands used by advanced tutorials."""
        create_result = subprocess.run(
            [
                "python",
                "main.py",
                "projects",
                "create",
                "--key",
                clean_project,
                "--name",
                "Advanced RAID Test",
            ],
            cwd=tui_path,
            capture_output=True,
            text=True,
        )
        assert (
            create_result.returncode == 0
            or "already exists" in (create_result.stdout + create_result.stderr).lower()
        )

        add_result = subprocess.run(
            [
                "python",
                "main.py",
                "raid",
                "add",
                "--project",
                clean_project,
                "--type",
                "risk",
                "--title",
                "Schedule risk",
                "--description",
                "Supplier lead time variance",
                "--owner",
                "PM",
                "--priority",
                "high",
            ],
            cwd=tui_path,
            capture_output=True,
            text=True,
        )
        assert add_result.returncode == 0, f"RAID add failed: {add_result.stderr}"

        list_result = subprocess.run(
            ["python", "main.py", "raid", "list", "--project", clean_project],
            cwd=tui_path,
            capture_output=True,
            text=True,
        )
        assert list_result.returncode == 0, f"RAID list failed: {list_result.stderr}"
        assert "Schedule risk" in list_result.stdout or "RAID" in list_result.stdout
        print("✅ RAID add/list commands validated")

    def test_artifacts_create_not_supported(self):
        """Document remaining unrelated gap: no direct artifacts create in TUI.

        Tutorial shows: python main.py artifacts create --type charter ...
        Reality: No 'artifacts create' - use commands propose with generate_artifact
        """
        pytest.skip(
            "DOCUMENTATION GAP: Tutorial documents 'artifacts create' which doesn't exist. "
            "Artifact generation uses 'commands propose --command generate_artifact'."
        )


@pytest.mark.tutorial
@pytest.mark.tutorial_validation
@pytest.mark.e2e
@pytest.mark.slow
class TestTutorial02CompleteLifecycle:
    """Tests for Tutorial 02: Complete ISO 21500 Lifecycle.

    NOTE: Tutorial documents non-existent commands. Tests validate actual propose/apply workflow.
    """

    @pytest.mark.skipif(not check_api_running(), reason="API not running")
    def test_initiating_phase_project_creation(
        self, tui_path, clean_project, project_docs_path
    ):
        """Test project creation for Initiating phase (Tutorial 02, Part 1, Step 1)."""
        result = subprocess.run(
            [
                "python",
                "main.py",
                "projects",
                "create",
                "--key",
                clean_project,
                "--name",
                "Todo App MVP",
            ],
            cwd=tui_path,
            capture_output=True,
            text=True,
        )

        success = result.returncode == 0 or "already exists" in result.stdout.lower()
        assert success, f"Project creation failed: {result.stderr}"

        # Verify directory structure (Tutorial 02, Step 1 - Verification)
        # Note: Only artifacts/ is created by default; raid/ and workflow/ are created on-demand
        project_path = project_docs_path / clean_project
        assert project_path.exists(), f"Project directory not created: {project_path}"
        assert (project_path / "artifacts").exists(), "artifacts/ directory not created"
        print(
            f"✅ Initiating phase: Project {clean_project} created with basic structure"
        )

    @pytest.mark.skipif(not check_api_running(), reason="API not running")
    def test_propose_assess_gaps_command(self, tui_path, clean_project):
        """Test proposing assess_gaps command (Tutorial 02, Step 5 - actual workflow)."""
        # Create project first
        subprocess.run(
            [
                "python",
                "main.py",
                "projects",
                "create",
                "--key",
                clean_project,
                "--name",
                "Test",
            ],
            cwd=tui_path,
            check=True,
            capture_output=True,
        )

        # Propose assess_gaps (actual command that exists)
        result = subprocess.run(
            [
                "python",
                "main.py",
                "commands",
                "propose",
                "--project",
                clean_project,
                "--command",
                "assess_gaps",
            ],
            cwd=tui_path,
            capture_output=True,
            text=True,
        )

        assert result.returncode == 0, f"Propose failed: {result.stderr}"
        # Should output proposal details or ID
        assert len(result.stdout) > 0
        print("✅ Gap assessment command proposed successfully")

    @pytest.mark.skipif(not check_api_running(), reason="API not running")
    def test_propose_generate_artifact(self, tui_path, clean_project):
        """Test proposing artifact generation (Tutorial 02, Step 2-3 - actual API)."""
        # Create project
        subprocess.run(
            [
                "python",
                "main.py",
                "projects",
                "create",
                "--key",
                clean_project,
                "--name",
                "Test",
            ],
            cwd=tui_path,
            check=True,
            capture_output=True,
        )

        # Propose artifact generation (actual workflow)
        result = subprocess.run(
            [
                "python",
                "main.py",
                "commands",
                "propose",
                "--project",
                clean_project,
                "--command",
                "generate_artifact",
                "--artifact-name",
                "charter",
                "--artifact-type",
                "project-charter",
            ],
            cwd=tui_path,
            capture_output=True,
            text=True,
        )

        assert result.returncode == 0, f"Artifact proposal failed: {result.stderr}"
        assert len(result.stdout) > 0
        print("✅ Artifact generation proposed successfully")


@pytest.mark.tutorial
@pytest.mark.tutorial_validation
@pytest.mark.e2e
@pytest.mark.slow
class TestTutorial03AutomationScripting:
    """Tests for Tutorial 03: Automation Scripting.

    Tests validate scriptable TUI commands (projects create, list, get).
    """

    @pytest.mark.skipif(not check_api_running(), reason="API not running")
    def test_batch_project_creation_script_actual_api(
        self, tui_path, project_docs_path
    ):
        """Test batch project creation script with ACTUAL TUI API (Tutorial 03, Part 2).

        Tutorial shows: --description flag in scripts
        Actual API: Only --key and --name work
        """
        with tempfile.TemporaryDirectory() as tmpdir:
            # Create CSV without description (not supported)
            csv_path = Path(tmpdir) / "projects.csv"
            csv_path.write_text("KEY,NAME\n" "TST-A,Test A\n" "TST-B,Test B\n")

            # Create script with actual TUI API
            script_path = Path(tmpdir) / "create-batch.sh"
            script_content = f"""#!/bin/bash
set -e
while IFS=',' read -r key name || [[ -n "$key" ]]; do
    [[ "$key" == "KEY" ]] && continue
    [[ -z "$key" ]] && continue
    cd {tui_path}
    python main.py projects create --key "$key" --name "$name" || true
done < {csv_path}
"""
            script_path.write_text(script_content)
            script_path.chmod(0o755)

            # Execute script
            result = subprocess.run(
                ["bash", str(script_path)],
                capture_output=True,
                text=True,
            )

            # Script should complete (even if some projects exist)
            assert result.returncode == 0, f"Script failed: {result.stderr}"

            # Verify at least one project was created
            verify_result = subprocess.run(
                ["python", "main.py", "projects", "list"],
                cwd=tui_path,
                capture_output=True,
                text=True,
            )
            assert "TST-A" in verify_result.stdout or "TST-B" in verify_result.stdout
            print("✅ Batch project creation script validated (actual API)")

    @pytest.mark.skipif(not check_api_running(), reason="API not running")
    def test_project_list_script(self, tui_path, clean_project):
        """Test project listing in bash script (Tutorial 03, Part 5 - Status Reports)."""
        # Create test project
        subprocess.run(
            [
                "python",
                "main.py",
                "projects",
                "create",
                "--key",
                clean_project,
                "--name",
                "Test",
            ],
            cwd=tui_path,
            check=True,
            capture_output=True,
        )

        # Create simple status script
        with tempfile.TemporaryDirectory() as tmpdir:
            script_path = Path(tmpdir) / "status.sh"
            script_content = f"""#!/bin/bash
cd {tui_path}
echo "=== Project Status Report ==="
python main.py projects list
exit $?
"""
            script_path.write_text(script_content)
            script_path.chmod(0o755)

            result = subprocess.run(
                ["bash", str(script_path)],
                capture_output=True,
                text=True,
            )

            assert result.returncode == 0
            assert "Project Status Report" in result.stdout
            assert clean_project in result.stdout
            print("✅ Project status script validated")


@pytest.mark.tutorial
@pytest.mark.tutorial_validation
@pytest.mark.e2e
@pytest.mark.slow
class TestActualTUICapabilities:
    """Integration tests covering actual TUI capabilities (not tutorial-specific).

    These tests document what the TUI can actually do today.
    """

    @pytest.mark.skipif(not check_api_running(), reason="API not running")
    def test_full_project_lifecycle_actual_api(
        self, tui_path, clean_project, project_docs_path
    ):
        """Test complete project workflow using actual TUI commands."""
        # 1. Create project
        result = subprocess.run(
            [
                "python",
                "main.py",
                "projects",
                "create",
                "--key",
                clean_project,
                "--name",
                "E2E Test",
            ],
            cwd=tui_path,
            capture_output=True,
            text=True,
        )
        assert result.returncode == 0 or "already exists" in result.stdout.lower()

        # 2. List projects
        result = subprocess.run(
            ["python", "main.py", "projects", "list"],
            cwd=tui_path,
            capture_output=True,
            text=True,
        )
        assert result.returncode == 0
        assert len(result.stdout) > 0

        # 3. Get project details
        result = subprocess.run(
            ["python", "main.py", "projects", "get", "--key", clean_project],
            cwd=tui_path,
            capture_output=True,
            text=True,
        )
        assert result.returncode == 0
        assert clean_project in result.stdout

        # 4. Propose command
        result = subprocess.run(
            [
                "python",
                "main.py",
                "commands",
                "propose",
                "--project",
                clean_project,
                "--command",
                "assess_gaps",
            ],
            cwd=tui_path,
            capture_output=True,
            text=True,
        )
        assert result.returncode == 0

        # 5. Verify git history (all commands create commits)
        project_path = project_docs_path / clean_project
        if project_path.exists():
            result = subprocess.run(
                ["git", "log", "--oneline"],
                cwd=project_path,
                capture_output=True,
                text=True,
            )
            assert result.returncode == 0
            assert (
                len(result.stdout.strip().split("\n")) >= 1
            )  # At least project creation commit

        print("✅ Full project lifecycle completed with actual TUI API")

    @pytest.mark.skipif(not check_api_running(), reason="API not running")
    def test_artifacts_read_only_access(self, tui_path, clean_project):
        """Test that artifacts can be listed (read-only) via TUI."""
        # Create project
        subprocess.run(
            [
                "python",
                "main.py",
                "projects",
                "create",
                "--key",
                clean_project,
                "--name",
                "Test",
            ],
            cwd=tui_path,
            check=True,
            capture_output=True,
        )

        # List artifacts (read-only command that exists)
        result = subprocess.run(
            ["python", "main.py", "artifacts", "list", "--project", clean_project],
            cwd=tui_path,
            capture_output=True,
            text=True,
        )

        # Should succeed even if no artifacts exist
        assert result.returncode == 0
        print("✅ Artifacts list command verified (read-only TUI access)")


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
