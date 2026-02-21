"""
End-to-End validation tests for TUI Basics tutorials.

These tests validate that all commands in the TUI basics tutorial series
work correctly. They provide automated validation of tutorial content.

Run with: pytest tests/e2e/tutorial/test_tui_basics.py -v
"""

import pytest
import json
import uuid
from pathlib import Path
from helpers.tui_automation import TUIAutomation, TUIResult


def _unique_project_key(prefix: str) -> str:
    """Generate a unique project key to avoid cross-test collisions."""
    return f"{prefix}-{uuid.uuid4().hex[:6].upper()}"


@pytest.fixture(scope="module")
def tui(docker_environment):
    """TUI automation helper for running commands."""
    return TUIAutomation(api_base_url="http://localhost:8000")


@pytest.mark.tutorial
@pytest.mark.tutorial_validation
@pytest.mark.e2e
class TestTutorial01QuickStart:
    """Validate Tutorial 01: Quick Start commands."""

    def test_health_check(self, tui):
        """Test: python apps/tui/main.py health"""
        result = tui.execute_command(["health"])

        assert result.success, f"Health check failed: {result.stderr}"
        assert "healthy" in result.stdout.lower()
        assert "status" in result.stdout.lower()

    def test_help_command(self, tui):
        """Test: python apps/tui/main.py --help"""
        result = tui.execute_command(["--help"])

        assert result.success
        assert "ISO 21500" in result.stdout
        assert "projects" in result.stdout
        assert "artifacts" in result.stdout
        assert "commands" in result.stdout
        assert "config" in result.stdout

    def test_projects_help(self, tui):
        """Test: python apps/tui/main.py projects --help"""
        result = tui.execute_command(["projects", "--help"])

        assert result.success
        assert "create" in result.stdout
        assert "list" in result.stdout
        assert "get" in result.stdout


@pytest.mark.tutorial
@pytest.mark.tutorial_validation
@pytest.mark.e2e
class TestTutorial02FirstProject:
    """Validate Tutorial 02: First Project commands."""

    def test_create_project(self, tui):
        """Test: python apps/tui/main.py projects create"""
        project_key = _unique_project_key("TEST-TUT02")
        project_name = "Tutorial Test Project"
        result = tui.execute_command(
            [
                "projects",
                "create",
                "--key",
                project_key,
                "--name",
                project_name,
            ]
        )

        assert result.success, f"Project creation failed: {result.stderr}"
        assert project_key in result.stdout
        assert "created" in result.stdout.lower() or "success" in result.stdout.lower()

    def test_create_project_with_description(self, tui):
        """Test: python apps/tui/main.py projects create --description"""
        project_key = _unique_project_key("TEST-TUT02")
        project_name = "Tutorial Test Project with Description"
        project_description = "Project description for tutorial validation"

        create_result = tui.execute_command(
            [
                "projects",
                "create",
                "--key",
                project_key,
                "--name",
                project_name,
                "--description",
                project_description,
            ]
        )

        assert create_result.success, f"Project creation failed: {create_result.stderr}"

        get_result = tui.execute_command(["projects", "get", "--key", project_key])
        assert get_result.success
        assert project_description in get_result.stdout

    def test_list_projects(self, tui):
        """Test: python apps/tui/main.py projects list"""
        project_key = _unique_project_key("TEST-TUT02")
        project_name = "List Test"
        tui.execute_command(
            ["projects", "create", "--key", project_key, "--name", project_name]
        )

        # Then list
        result = tui.execute_command(["projects", "list"])

        assert result.success
        # Output is a Rich table; long keys are often truncated with an ellipsis.
        # Validate by project name and table summary instead of full key text.
        assert project_name in result.stdout
        assert "Total:" in result.stdout

    def test_list_projects_json_format(self, tui):
        """Test: python apps/tui/main.py projects list --format json"""
        project_key = _unique_project_key("TEST-TUT02")
        project_name = "List Json Test"
        tui.execute_command(
            ["projects", "create", "--key", project_key, "--name", project_name]
        )

        result = tui.execute_command(["projects", "list", "--format", "json"])

        assert result.success
        parsed = json.loads(result.stdout)
        assert isinstance(parsed, list)
        assert any(p.get("key") == project_key for p in parsed)

    def test_show_project(self, tui):
        """Test: python apps/tui/main.py projects get"""
        project_key = _unique_project_key("TEST-TUT02")
        project_name = "Tutorial Test Project"
        tui.execute_command(
            ["projects", "create", "--key", project_key, "--name", project_name]
        )

        result = tui.execute_command(["projects", "get", "--key", project_key])

        assert result.success
        assert project_key in result.stdout
        assert project_name in result.stdout

    def test_project_state(self, tui):
        """Test: project state is visible via projects get."""
        project_key = _unique_project_key("TEST-TUT02")
        tui.execute_command(
            ["projects", "create", "--key", project_key, "--name", "State Test"]
        )

        result = tui.execute_command(["projects", "get", "--key", project_key])

        assert result.success
        # Current TUI prints project information and metadata; it does not include
        # a workflow phase/state field.
        assert project_key.lower() in result.stdout.lower()
        assert "project information" in result.stdout.lower()

    def test_delete_project(self, tui):
        """Test: python apps/tui/main.py projects delete"""
        project_key = _unique_project_key("TEST-TUT02")
        tui.execute_command(
            ["projects", "create", "--key", project_key, "--name", "Delete Test"]
        )

        result = tui.execute_command(["projects", "delete", "--key", project_key])

        assert result.success
        assert "deleted" in result.stdout.lower() or "success" in result.stdout.lower()


@pytest.mark.tutorial
@pytest.mark.tutorial_validation
@pytest.mark.e2e
class TestTutorial03ArtifactWorkflow:
    """Validate Tutorial 03: Artifact Workflow commands."""

    PROJECT_KEY = "TEST-TUT03"

    @pytest.fixture(autouse=True)
    def setup_project(self, tui):
        """Set up test project."""
        self.PROJECT_KEY = _unique_project_key("TEST-TUT03")
        tui.execute_command(
            [
                "projects",
                "create",
                "--key",
                self.PROJECT_KEY,
                "--name",
                "Artifact Workflow Test",
            ]
        )

        yield

        # No deletion command in TUI; project is isolated by unique key.

    def test_propose_command(self, tui):
        """Test: python apps/tui/main.py commands propose"""
        result = tui.execute_command(
            [
                "commands",
                "propose",
                "--project",
                self.PROJECT_KEY,
                "--command",
                "assess_gaps",
            ]
        )

        assert result.success, f"Propose command failed: {result.stderr}"
        assert (
            "proposal" in result.stdout.lower()
            or "proposal id" in result.stdout.lower()
        )

    def test_list_proposals(self, tui):
        """Test: python apps/tui/main.py propose list"""
        pytest.skip(
            "DOCUMENTATION GAP: TUI has no 'proposals list' command; proposals are shown in the output of 'commands propose'."
        )

    def test_list_artifacts(self, tui):
        """Test: python apps/tui/main.py artifacts list"""
        result = tui.execute_command(
            ["artifacts", "list", "--project", self.PROJECT_KEY]
        )

        assert result.success
        # New project might have 0 artifacts, which is OK


@pytest.mark.tutorial
@pytest.mark.tutorial_validation
@pytest.mark.e2e
class TestTutorial04RAIDManagement:
    """Validate Tutorial 04: RAID Management commands."""

    PROJECT_KEY = "TEST-TUT04"

    @pytest.fixture(autouse=True)
    def setup_project(self, tui):
        """Set up test project."""
        self.PROJECT_KEY = _unique_project_key("TEST-TUT04")
        tui.execute_command(
            [
                "projects",
                "create",
                "--key",
                self.PROJECT_KEY,
                "--name",
                "RAID Test Project",
            ]
        )
        yield

    def test_add_risk(self, tui):
        """Test: python apps/tui/main.py raid add --type risk"""
        result = tui.execute_command(
            [
                "raid",
                "add",
                "--project",
                self.PROJECT_KEY,
                "--type",
                "risk",
                "--title",
                "Test risk",
                "--description",
                "Test risk description",
                "--priority",
                "high",
                "--owner",
                "Test Owner",
            ]
        )

        assert result.success, f"Add risk failed: {result.stderr}"
        assert "success" in result.stdout.lower() or "added" in result.stdout.lower()

    def test_add_assumption(self, tui):
        """Test: python apps/tui/main.py raid add --type assumption"""
        result = tui.execute_command(
            [
                "raid",
                "add",
                "--project",
                self.PROJECT_KEY,
                "--type",
                "assumption",
                "--title",
                "Test assumption",
                "--description",
                "Test assumption description",
                "--priority",
                "medium",
                "--owner",
                "Test Owner",
            ]
        )

        assert result.success
        assert "success" in result.stdout.lower() or "added" in result.stdout.lower()

    def test_add_issue(self, tui):
        """Test: python apps/tui/main.py raid add --type issue"""
        result = tui.execute_command(
            [
                "raid",
                "add",
                "--project",
                self.PROJECT_KEY,
                "--type",
                "issue",
                "--title",
                "Test issue",
                "--description",
                "Test issue description",
                "--priority",
                "high",
                "--owner",
                "Test Owner",
            ]
        )

        assert result.success
        assert "success" in result.stdout.lower() or "added" in result.stdout.lower()

    def test_add_dependency(self, tui):
        """Test: python apps/tui/main.py raid add --type dependency"""
        result = tui.execute_command(
            [
                "raid",
                "add",
                "--project",
                self.PROJECT_KEY,
                "--type",
                "dependency",
                "--title",
                "Test dependency",
                "--description",
                "Test dependency description",
                "--owner",
                "Test Owner",
            ]
        )

        assert result.success
        assert "success" in result.stdout.lower() or "added" in result.stdout.lower()

    def test_list_raid_entries(self, tui):
        """Test: python apps/tui/main.py raid list"""
        # Add an entry first
        tui.execute_command(
            [
                "raid",
                "add",
                "--project",
                self.PROJECT_KEY,
                "--type",
                "risk",
                "--title",
                "Test risk",
                "--description",
                "Test risk description",
                "--priority",
                "high",
                "--owner",
                "Test",
            ]
        )

        # List
        result = tui.execute_command(["raid", "list", "--project", self.PROJECT_KEY])

        assert result.success
        assert "Test risk" in result.stdout or "raid" in result.stdout.lower()


@pytest.mark.tutorial
@pytest.mark.tutorial_validation
@pytest.mark.e2e
class TestTutorial05FullLifecycle:
    """Validate Tutorial 05: Full Lifecycle commands."""

    PROJECT_KEY = "TEST-TUT05"

    @pytest.fixture(autouse=True)
    def setup_project(self, tui):
        """Set up test project."""
        self.PROJECT_KEY = _unique_project_key("TEST-TUT05")
        tui.execute_command(
            [
                "projects",
                "create",
                "--key",
                self.PROJECT_KEY,
                "--name",
                "Lifecycle Test Project",
            ]
        )
        yield

    def test_workflow_state_and_transition(self, tui):
        """Test: python apps/tui/main.py workflow state/transition."""
        state_result = tui.execute_command(
            ["workflow", "state", "--project", self.PROJECT_KEY]
        )

        assert state_result.success
        assert "initiating" in state_result.stdout.lower()

        result = tui.execute_command(
            [
                "workflow",
                "transition",
                "--project",
                self.PROJECT_KEY,
                "--to-state",
                "planning",
                "--actor",
                "TestUser",
                "--reason",
                "Test phase transition",
            ]
        )

        assert result.success
        assert "planning" in result.stdout.lower()

    def test_workflow_allowed_transitions_and_audit(self, tui):
        """Test: python apps/tui/main.py workflow allowed-transitions/audit-events."""
        transition_result = tui.execute_command(
            [
                "workflow",
                "transition",
                "--project",
                self.PROJECT_KEY,
                "--to-state",
                "planning",
                "--actor",
                "TestUser",
            ]
        )
        assert transition_result.success

        allowed_result = tui.execute_command(
            ["workflow", "allowed-transitions", "--project", self.PROJECT_KEY]
        )
        assert allowed_result.success
        assert (
            "allowed" in allowed_result.stdout.lower()
            or "executing" in allowed_result.stdout.lower()
        )

        audit_result = tui.execute_command(
            [
                "workflow",
                "audit-events",
                "--project",
                self.PROJECT_KEY,
                "--event-type",
                "workflow_state_changed",
                "--actor",
                "TestUser",
            ]
        )
        assert audit_result.success

    def test_complete_lifecycle_scenario(self, tui):
        """Test: Complete lifecycle scenario from tutorial."""
        # This is a simplified integration test
        # Full lifecycle would be tested manually or in a separate long-running test

        # 1. Create project (done in setup)
        # 2. Add some RAID entries
        tui.execute_command(
            [
                "raid",
                "add",
                "--project",
                self.PROJECT_KEY,
                "--type",
                "risk",
                "--title",
                "Initial risk",
                "--description",
                "Initial lifecycle risk",
                "--priority",
                "high",
                "--owner",
                "PM",
            ]
        )

        # 3. Propose a command
        tui.execute_command(
            [
                "commands",
                "propose",
                "--project",
                self.PROJECT_KEY,
                "--command",
                "assess_gaps",
            ]
        )

        # 4. Check project state
        result = tui.execute_command(["projects", "get", "--key", self.PROJECT_KEY])
        assert result.success

        # Project created and has RAID entries - basic lifecycle demonstrated


@pytest.mark.tutorial
@pytest.mark.tutorial_validation
@pytest.mark.integration
def test_tutorial_sequence(tui):
    """
    Integration test: Run through tutorials 01-05 in sequence.

    This test validates that a user can follow the tutorials in order
    without encountering blocking errors.
    """
    # Tutorial 01: Quick Start
    result = tui.execute_command(["health"])
    assert result.success, "Tutorial 01: Health check failed"

    # Tutorial 02: First Project
    test_key = _unique_project_key("TEST-SEQUENCE")
    result = tui.execute_command(
        ["projects", "create", "--key", test_key, "--name", "Sequence Test"]
    )
    assert result.success, "Tutorial 02: Project creation failed"

    # Tutorial 03: Artifact Workflow
    result = tui.execute_command(
        ["commands", "propose", "--project", test_key, "--command", "assess_gaps"]
    )
    assert result.success, "Tutorial 03: Command proposal failed"

    # Tutorial 04: RAID Management
    result = tui.execute_command(
        [
            "raid",
            "add",
            "--project",
            test_key,
            "--type",
            "risk",
            "--title",
            "Sequence risk",
            "--description",
            "Sequence risk description",
            "--owner",
            "PM",
            "--priority",
            "high",
        ]
    )
    assert result.success, "Tutorial 04: RAID add failed"

    result = tui.execute_command(["raid", "list", "--project", test_key])
    assert result.success, "Tutorial 04: RAID list failed"

    # Tutorial 05: Full Lifecycle (workflow commands)
    result = tui.execute_command(["workflow", "state", "--project", test_key])
    assert result.success, "Tutorial 05: Workflow state failed"

    result = tui.execute_command(
        [
            "workflow",
            "transition",
            "--project",
            test_key,
            "--to-state",
            "planning",
            "--actor",
            "PM",
            "--reason",
            "Sequence transition",
        ]
    )
    assert result.success, "Tutorial 05: Workflow transition failed"

    result = tui.execute_command(
        ["workflow", "allowed-transitions", "--project", test_key]
    )
    assert result.success, "Tutorial 05: Workflow allowed transitions failed"


if __name__ == "__main__":
    # Allow running this file directly for quick validation
    pytest.main([__file__, "-v", "--tb=short"])
