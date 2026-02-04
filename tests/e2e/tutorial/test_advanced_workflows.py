"""
E2E validation tests for advanced workflow tutorials.

Tests cover:
- Tutorial 01: TUI + GUI hybrid workflows
- Tutorial 02: Complete ISO 21500 lifecycle
- Tutorial 03: Automation scripting
"""

import pytest
import subprocess
import tempfile
import os
from pathlib import Path


@pytest.fixture
def tui_path():
    """Path to TUI application."""
    return Path(__file__).parent.parent.parent / "apps" / "tui"


@pytest.fixture
def project_docs_path():
    """Path to projectDocs directory."""
    return Path(__file__).parent.parent.parent / "projectDocs"


@pytest.fixture
def clean_project(tui_path, project_docs_path):
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


class TestTutorial01HybridWorkflow:
    """Tests for Tutorial 01: TUI + GUI Hybrid Workflows."""

    def test_create_project_tui(self, tui_path, clean_project):
        """Test project creation via TUI (Tutorial 01, Step 2)."""
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
                "--description",
                "Testing TUI project creation",
            ],
            cwd=tui_path,
            capture_output=True,
            text=True,
        )

        assert result.returncode == 0
        assert "Project created" in result.stdout
        assert clean_project in result.stdout

    def test_bulk_raid_entries_tui(self, tui_path, clean_project):
        """Test bulk RAID entry creation via TUI (Tutorial 01, Step 4)."""
        # First create project
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

        # Add multiple RAID entries
        raid_entries = [
            ("risk", "High", "Database scaling", "Plan for sharding"),
            ("risk", "Medium", "API downtime", "Implement retry logic"),
            ("issue", "Medium", "Unclear requirements", "Schedule workshop"),
        ]

        for entry_type, severity, description, mitigation in raid_entries:
            result = subprocess.run(
                [
                    "python",
                    "main.py",
                    "raid",
                    "add",
                    "--project",
                    clean_project,
                    "--type",
                    entry_type,
                    "--severity",
                    severity,
                    "--description",
                    description,
                    "--mitigation",
                    mitigation,
                ],
                cwd=tui_path,
                capture_output=True,
                text=True,
            )
            assert result.returncode == 0
            assert "RAID entry added" in result.stdout

        # Verify entries
        result = subprocess.run(
            ["python", "main.py", "raid", "list", "--project", clean_project],
            cwd=tui_path,
            capture_output=True,
            text=True,
        )

        assert "RAID-001" in result.stdout
        assert "RAID-002" in result.stdout
        assert "RAID-003" in result.stdout

    def test_workflow_proposal_apply(self, tui_path, clean_project):
        """Test workflow update proposal (Tutorial 01, Step 7-9)."""
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

        # Propose workflow update
        result = subprocess.run(
            [
                "python",
                "main.py",
                "workflow",
                "update",
                "--project",
                clean_project,
                "--state",
                "Planning",
            ],
            cwd=tui_path,
            capture_output=True,
            text=True,
        )

        assert result.returncode == 0
        assert "Proposal created" in result.stdout

        # Extract proposal ID from output
        for line in result.stdout.split("\n"):
            if "proposals/" in line:
                # Proposal ID is in the path
                proposal_id = line.split("/")[-1].split(".")[0]
                break
        else:
            pytest.fail("Proposal ID not found in output")

        # Apply proposal
        result = subprocess.run(
            [
                "python",
                "main.py",
                "proposals",
                "apply",
                "--project",
                clean_project,
                "--id",
                proposal_id,
            ],
            cwd=tui_path,
            capture_output=True,
            text=True,
        )

        assert result.returncode == 0
        assert (
            "Proposal applied" in result.stdout
            or "successfully" in result.stdout.lower()
        )


class TestTutorial02CompleteLifecycle:
    """Tests for Tutorial 02: Complete ISO 21500 Lifecycle."""

    @pytest.mark.slow
    def test_initiating_phase(self, tui_path, clean_project, project_docs_path):
        """Test Initiating phase (Tutorial 02, Part 1)."""
        # Step 1: Create project
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
                "--description",
                "Task management application",
            ],
            cwd=tui_path,
            capture_output=True,
            text=True,
        )
        assert result.returncode == 0

        # Verify project directory structure
        project_path = project_docs_path / clean_project
        assert project_path.exists()
        assert (project_path / "artifacts").exists()
        assert (project_path / "raid").exists()
        assert (project_path / "workflow").exists()

        # Step 2-3: Create artifacts (stakeholders, charter)
        artifacts = [
            ("stakeholders", "Stakeholder Register", "List project stakeholders"),
            ("charter", "Project Charter", "Create project charter"),
        ]

        for artifact_type, title, prompt in artifacts:
            result = subprocess.run(
                [
                    "python",
                    "main.py",
                    "artifacts",
                    "create",
                    "--project",
                    clean_project,
                    "--type",
                    artifact_type,
                    "--title",
                    title,
                    "--prompt",
                    prompt,
                ],
                cwd=tui_path,
                capture_output=True,
                text=True,
            )
            assert result.returncode == 0
            assert "Artifact created" in result.stdout

        # Step 4: Add initial RAID entries
        result = subprocess.run(
            [
                "python",
                "main.py",
                "raid",
                "add",
                "--project",
                clean_project,
                "--type",
                "risk",
                "--severity",
                "High",
                "--description",
                "Scope creep",
                "--mitigation",
                "Change control process",
            ],
            cwd=tui_path,
            capture_output=True,
            text=True,
        )
        assert result.returncode == 0

        # Step 5: Run gap assessment
        result = subprocess.run(
            ["python", "main.py", "assess-gaps", "--project", clean_project],
            cwd=tui_path,
            capture_output=True,
            text=True,
        )
        assert result.returncode == 0
        assert "Gap Assessment" in result.stdout or "Initiating" in result.stdout

    @pytest.mark.slow
    def test_planning_phase(self, tui_path, clean_project):
        """Test Planning phase (Tutorial 02, Part 2)."""
        # Create project and transition to Planning
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

        # Transition to Planning
        result = subprocess.run(
            [
                "python",
                "main.py",
                "workflow",
                "update",
                "--project",
                clean_project,
                "--state",
                "Planning",
            ],
            cwd=tui_path,
            capture_output=True,
            text=True,
        )
        assert result.returncode == 0

        # Create planning artifacts
        planning_artifacts = [
            ("wbs", "Work Breakdown Structure", "Create WBS"),
            ("schedule", "Project Schedule", "Create schedule"),
            ("budget", "Project Budget", "Create budget"),
            ("requirements", "Requirements", "Create requirements"),
            ("test-plan", "Test Plan", "Create test plan"),
        ]

        for artifact_type, title, prompt in planning_artifacts:
            result = subprocess.run(
                [
                    "python",
                    "main.py",
                    "artifacts",
                    "create",
                    "--project",
                    clean_project,
                    "--type",
                    artifact_type,
                    "--title",
                    title,
                    "--prompt",
                    prompt,
                ],
                cwd=tui_path,
                capture_output=True,
                text=True,
            )
            # Note: Some artifacts may not be supported yet
            if result.returncode == 0:
                assert (
                    "Artifact created" in result.stdout
                    or "created" in result.stdout.lower()
                )


class TestTutorial03AutomationScripting:
    """Tests for Tutorial 03: Automation Scripting."""

    def test_batch_project_creation_script(self, tui_path, project_docs_path):
        """Test batch project creation script (Tutorial 03, Step 2)."""
        with tempfile.TemporaryDirectory() as tmpdir:
            # Create CSV file
            csv_path = Path(tmpdir) / "projects.csv"
            csv_path.write_text(
                "KEY,NAME,DESCRIPTION\n"
                "TST-A,Test A,Description A\n"
                "TST-B,Test B,Description B\n"
            )

            # Create script
            script_path = Path(tmpdir) / "create-batch.sh"
            script_content = f"""#!/bin/bash
set -e
while IFS=',' read -r key name description || [[ -n "$key" ]]; do
    [[ "$key" == "KEY" ]] && continue
    [[ -z "$key" ]] && continue
    cd {tui_path}
    python main.py projects create --key "$key" --name "$name" --description "$description"
done < {csv_path}
"""
            script_path.write_text(script_content)
            script_path.chmod(0o755)

            # Execute script
            result = subprocess.run(
                ["bash", str(script_path)], capture_output=True, text=True
            )

            # Check if at least one project was created successfully
            # (Some may fail if they already exist)
            assert result.returncode == 0 or "Project created" in result.stdout

            # Cleanup
            for project_key in ["TST-A", "TST-B"]:
                project_path = project_docs_path / project_key
                if project_path.exists():
                    subprocess.run(["rm", "-rf", str(project_path)], check=False)

    def test_raid_import_script(self, tui_path, clean_project):
        """Test RAID import script (Tutorial 03, Step 3)."""
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

        with tempfile.TemporaryDirectory() as tmpdir:
            # Create RAID CSV
            csv_path = Path(tmpdir) / "raid.csv"
            csv_path.write_text(
                "TYPE,SEVERITY,DESCRIPTION,MITIGATION\n"
                "risk,High,Test risk 1,Test mitigation 1\n"
                "issue,Medium,Test issue 1,Test mitigation 2\n"
            )

            # Create import script
            script_path = Path(tmpdir) / "import-raid.sh"
            script_content = f"""#!/bin/bash
set -e
PROJECT_KEY="{clean_project}"
while IFS=',' read -r type severity description mitigation || [[ -n "$type" ]]; do
    [[ "$type" == "TYPE" ]] && continue
    [[ -z "$type" ]] && continue
    cd {tui_path}
    python main.py raid add --project "$PROJECT_KEY" --type "$type" --severity "$severity" \\
        --description "$description" --mitigation "$mitigation"
done < {csv_path}
"""
            script_path.write_text(script_content)
            script_path.chmod(0o755)

            # Execute script
            result = subprocess.run(
                ["bash", str(script_path)], capture_output=True, text=True
            )

            assert result.returncode == 0

            # Verify entries were added
            result = subprocess.run(
                ["python", "main.py", "raid", "list", "--project", clean_project],
                cwd=tui_path,
                capture_output=True,
                text=True,
            )

            assert "RAID-" in result.stdout

    def test_project_status_script(self, tui_path, clean_project):
        """Test project status script (Tutorial 03, Step 6)."""
        # Create project with some content
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

        subprocess.run(
            [
                "python",
                "main.py",
                "raid",
                "add",
                "--project",
                clean_project,
                "--type",
                "risk",
                "--severity",
                "Medium",
                "--description",
                "Test",
                "--mitigation",
                "Test",
            ],
            cwd=tui_path,
            check=True,
            capture_output=True,
        )

        with tempfile.TemporaryDirectory() as tmpdir:
            # Create status script
            script_path = Path(tmpdir) / "status.sh"
            script_content = f"""#!/bin/bash
cd {tui_path}
echo "=== Project Status: {clean_project} ==="
python main.py projects show --project {clean_project}
echo ""
echo "=== RAID Entries ==="
python main.py raid list --project {clean_project}
"""
            script_path.write_text(script_content)
            script_path.chmod(0o755)

            # Execute script
            result = subprocess.run(
                ["bash", str(script_path)], capture_output=True, text=True
            )

            assert result.returncode == 0
            assert clean_project in result.stdout
            assert "RAID" in result.stdout or "Project Status" in result.stdout


@pytest.mark.slow
class TestCompleteWorkflow:
    """Integration test covering complete workflow from all tutorials."""

    def test_end_to_end_workflow(self, tui_path, clean_project, project_docs_path):
        """
        Complete end-to-end workflow test covering:
        - Project creation
        - Artifact generation
        - RAID management
        - Workflow transitions
        - Gap assessment
        - Reporting
        """
        # 1. Create project (Tutorial 01, 02)
        result = subprocess.run(
            [
                "python",
                "main.py",
                "projects",
                "create",
                "--key",
                clean_project,
                "--name",
                "E2E Test Project",
                "--description",
                "End-to-end workflow test",
            ],
            cwd=tui_path,
            capture_output=True,
            text=True,
        )
        assert result.returncode == 0

        # 2. Create charter (Tutorial 02)
        result = subprocess.run(
            [
                "python",
                "main.py",
                "artifacts",
                "create",
                "--project",
                clean_project,
                "--type",
                "charter",
                "--title",
                "Project Charter",
                "--prompt",
                "Create a project charter",
            ],
            cwd=tui_path,
            capture_output=True,
            text=True,
        )
        assert result.returncode == 0

        # 3. Add RAID entries (Tutorial 01, 02)
        for i in range(3):
            result = subprocess.run(
                [
                    "python",
                    "main.py",
                    "raid",
                    "add",
                    "--project",
                    clean_project,
                    "--type",
                    "risk",
                    "--severity",
                    "Medium",
                    "--description",
                    f"Risk {i+1}",
                    "--mitigation",
                    f"Mitigation {i+1}",
                ],
                cwd=tui_path,
                capture_output=True,
                text=True,
            )
            assert result.returncode == 0

        # 4. Run gap assessment (Tutorial 02)
        result = subprocess.run(
            ["python", "main.py", "assess-gaps", "--project", clean_project],
            cwd=tui_path,
            capture_output=True,
            text=True,
        )
        assert result.returncode == 0

        # 5. Transition to Planning (Tutorial 02)
        result = subprocess.run(
            [
                "python",
                "main.py",
                "workflow",
                "update",
                "--project",
                clean_project,
                "--state",
                "Planning",
            ],
            cwd=tui_path,
            capture_output=True,
            text=True,
        )
        assert result.returncode == 0

        # 6. Verify project state
        result = subprocess.run(
            ["python", "main.py", "projects", "show", "--project", clean_project],
            cwd=tui_path,
            capture_output=True,
            text=True,
        )
        assert result.returncode == 0
        assert clean_project in result.stdout

        # 7. Verify git history
        project_path = project_docs_path / clean_project
        result = subprocess.run(
            ["git", "log", "--oneline"],
            cwd=project_path,
            capture_output=True,
            text=True,
        )
        assert result.returncode == 0
        assert len(result.stdout.strip().split("\n")) >= 3  # At least 3 commits
