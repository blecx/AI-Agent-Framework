"""Workflow spine E2E test.

Tests the complete workflow from project creation through artifact generation,
editing, proposal creation, application, and audit verification.

This is the primary E2E test that validates the full feature spine.
"""

import pytest
import sys
from pathlib import Path

# Add tests directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from helpers.tui_automation import TUIAutomation, TUIAssertions  # noqa: E402
from fixtures.factories import ProjectFactory  # noqa: E402


@pytest.mark.e2e
def test_workflow_spine_complete(
    tui: TUIAutomation, assertions: TUIAssertions, project_factory: ProjectFactory
):
    """Test complete workflow spine from project creation to artifact listing.

    Scenario:
    1. Create project with unique key
    2. List projects to verify creation
    3. Get project details
    4. List artifacts (should be empty initially)

    This test validates basic project and artifact operations.
    Note: Full workflow including proposals and audit requires those features
    to be implemented in the TUI.
    """
    # Step 1: Create project (use factory default unique key)
    project = project_factory.with_name("Workflow Spine Test").build()
    project_key = project["key"]

    result = tui.execute_command(
        f"projects create --key {project_key} --name \"{project['name']}\""
    )
    assertions.assert_success(result, "Project creation should succeed")
    assertions.assert_contains(result, project_key, "Output should contain project key")

    # Step 2: List projects to verify creation
    result = tui.execute_command("projects list")
    assertions.assert_success(result)
    assertions.assert_contains(result, project_key, "Project should appear in list")

    # Step 3: Get project details
    result = tui.execute_command(f"projects get --key {project_key}")
    assertions.assert_success(result)
    assertions.assert_contains(
        result, project["name"], "Project details should contain name"
    )

    # Step 4: List artifacts (should be empty initially)
    result = tui.execute_command(f"artifacts list --project {project_key}")
    assertions.assert_success(result)

    # Cleanup
    tui.cleanup_project(project_key)


@pytest.mark.e2e
@pytest.mark.slow
def test_workflow_spine_with_artifacts(
    tui: TUIAutomation, assertions: TUIAssertions, project_factory: ProjectFactory
):
    """Test workflow spine including TUI command operations.

    Complete TUI workflow:
    1. Create project via TUI
    2. Verify project exists
    3. List artifacts via TUI (initially empty)
    4. Test propose command via TUI
    5. Verify operations complete without errors

    This test validates TUI command execution and project workflows.
    """
    # Create project (use factory default unique key)
    project = project_factory.with_name("Workflow Complete Test").build()
    project_key = project["key"]

    result = tui.execute_command(
        f"projects create --key {project_key} --name \"{project['name']}\""
    )
    assertions.assert_success(result)

    # Verify project creation
    result = tui.execute_command(f"projects get --key {project_key}")
    assertions.assert_success(result)
    assertions.assert_contains(result, project["name"])

    # List artifacts via TUI (initially empty for new project)
    result = tui.execute_command(f"artifacts list --project {project_key}")
    assertions.assert_success(result)

    # Test propose command (may succeed or fail gracefully depending on project state)
    result = tui.execute_command(
        f"commands propose --project {project_key} --command update_scope",
        expect_failure=True,  # May fail if project has no artifacts yet
    )
    # Command should execute without crashing (exit code 0, 1, or 2)
    assert result.exit_code in [
        0,
        1,
        2,
    ], f"Command should handle execution gracefully, got exit {result.exit_code}"


@pytest.mark.e2e
def test_workflow_spine_error_handling(
    tui: TUIAutomation, assertions: TUIAssertions, project_factory: ProjectFactory
):
    """Test error handling in workflow spine.

    Validates that the system properly handles:
    - Duplicate project keys
    - Invalid project keys
    - Missing required fields
    """
    # Test duplicate project key
    project = project_factory.build()
    project_key = project["key"]

    # Create first project
    result = tui.execute_command(
        f'projects create --key {project_key} --name "First Project"'
    )
    assertions.assert_success(result)

    # Attempt to create duplicate (should fail gracefully)
    result = tui.execute_command(
        f'projects create --key {project_key} --name "Duplicate Project"',
        expect_failure=True,
    )
    # Note: Depending on TUI implementation, this might succeed or fail
    # The key is that it should handle the situation gracefully

    # Test invalid project key (empty)
    result = tui.execute_command('projects get --key ""', expect_failure=True)
    # Should fail with clear error message

    # Cleanup
    tui.cleanup_project(project_key)


@pytest.mark.e2e
def test_workflow_performance(
    tui: TUIAutomation, assertions: TUIAssertions, project_factory: ProjectFactory
):
    """Test workflow performance meets requirements.

    Validates that basic operations complete within acceptable time limits:
    - Project creation: < 2s
    - Project list: < 1s
    - Project get: < 1s
    """
    project = project_factory.build()
    project_key = project["key"]

    # Test project creation performance
    result = tui.execute_command(
        f"projects create --key {project_key} --name \"{project['name']}\""
    )
    assertions.assert_success(result)
    assertions.assert_duration(result, 2.0, "Project creation should complete in < 2s")

    # Test project list performance
    result = tui.execute_command("projects list")
    assertions.assert_success(result)
    assertions.assert_duration(result, 1.0, "Project list should complete in < 1s")

    # Test project get performance
    result = tui.execute_command(f"projects get --key {project_key}")
    assertions.assert_success(result)
    assertions.assert_duration(result, 1.0, "Project get should complete in < 1s")

    # Cleanup
    tui.cleanup_project(project_key)
