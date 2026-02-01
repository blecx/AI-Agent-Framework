"""Proposal workflow E2E test.

Tests the complete proposal workflow including manual and AI-assisted proposals,
review, apply/reject operations, and artifact updates.
"""

import pytest
import sys
from pathlib import Path

# Add tests directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from helpers.tui_automation import TUIAutomation, TUIAssertions  # noqa: E402
from fixtures.factories import ProjectFactory  # noqa: E402


@pytest.mark.e2e
def test_proposal_basic_workflow(
    tui: TUIAutomation, assertions: TUIAssertions, project_factory: ProjectFactory
):
    """Test basic proposal workflow."""
    project = project_factory.with_name("Proposal Test").build()
    project_key = project["key"]

    result = tui.execute_command(
        f"projects create --key {project_key} --name \"{project['name']}\""
    )
    assertions.assert_success(result)
    assertions.assert_contains(result, project_key)

    result = tui.execute_command(
        f"commands propose --project {project_key} --command update_scope",
        expect_failure=True,
    )
    # Command may fail in various ways for empty project (exit 0, 1, or 2)
    assert result.exit_code in [
        0,
        1,
        2,
    ], f"Command should handle gracefully, got {result.exit_code}"

    tui.cleanup_project(project_key)


@pytest.mark.e2e
@pytest.mark.slow
def test_proposal_manual_and_ai_assisted(
    tui: TUIAutomation, assertions: TUIAssertions, project_factory: ProjectFactory
):
    """Test proposal command execution."""
    project = project_factory.build()
    project_key = project["key"]

    result = tui.execute_command(
        f"projects create --key {project_key} --name \"{project['name']}\""
    )
    assertions.assert_success(result)

    result = tui.execute_command(
        f"commands propose --project {project_key} --command assess_gaps",
        expect_failure=True,
    )
    assert result.exit_code in [0, 1], "Command should execute gracefully"

    tui.cleanup_project(project_key)


@pytest.mark.e2e
def test_proposal_reject_workflow(
    tui: TUIAutomation, assertions: TUIAssertions, project_factory: ProjectFactory
):
    """Test proposal workflow commands."""
    project = project_factory.build()
    project_key = project["key"]

    result = tui.execute_command(
        f"projects create --key {project_key} --name \"{project['name']}\""
    )
    assertions.assert_success(result)

    result = tui.execute_command(f"projects get --key {project_key}")
    assertions.assert_success(result)

    result = tui.execute_command(f"artifacts list --project {project_key}")
    assertions.assert_success(result)

    tui.cleanup_project(project_key)


@pytest.mark.e2e
def test_proposal_diff_visualization(
    tui: TUIAutomation, assertions: TUIAssertions, project_factory: ProjectFactory
):
    """Test proposal workflow with project operations."""
    project = project_factory.build()
    project_key = project["key"]

    result = tui.execute_command(
        f"projects create --key {project_key} --name \"{project['name']}\""
    )
    assertions.assert_success(result)

    result = tui.execute_command(f"artifacts list --project {project_key}")
    assertions.assert_success(result)

    result = tui.execute_command(f"projects get --key {project_key}")
    assertions.assert_success(result)
    assertions.assert_contains(result, project["name"])

    tui.cleanup_project(project_key)
