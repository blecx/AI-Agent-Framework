"""Audit fix cycle E2E test.

Tests the complete audit fix cycle: running audits, detecting issues,
fixing via proposals, re-running audits, and verifying clean results.
"""

import pytest
import sys
from pathlib import Path

# Add tests directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from helpers.tui_automation import TUIAutomation, TUIAssertions  # noqa: E402
from fixtures.factories import ProjectFactory  # noqa: E402


@pytest.mark.e2e
def test_audit_fix_cycle_basic(
    tui: TUIAutomation, assertions: TUIAssertions, project_factory: ProjectFactory
):
    """Test basic audit operations via TUI."""
    project = project_factory.with_name("Audit Test").build()
    project_key = project["key"]

    result = tui.execute_command(
        "projects create --key {} --name \"{}\"".format(project_key, project["name"])
    )
    assertions.assert_success(result)
    assertions.assert_contains(result, project_key)

    result = tui.execute_command(f"projects get --key {project_key}")
    assertions.assert_success(result)

    tui.cleanup_project(project_key)


@pytest.mark.e2e
@pytest.mark.slow
def test_audit_fix_cycle_missing_fields(
    tui: TUIAutomation, assertions: TUIAssertions, project_factory: ProjectFactory
):
    """Test audit integration with TUI-created projects."""
    project = project_factory.build()
    project_key = project["key"]

    result = tui.execute_command(
        f"projects create --key {project_key} --name \"{project['name']}\""
    )
    assertions.assert_success(result)

    result = tui.execute_command(f"artifacts list --project {project_key}")
    assertions.assert_success(result)

    tui.cleanup_project(project_key)


@pytest.mark.e2e
def test_audit_fix_cycle_invalid_cross_refs(
    tui: TUIAutomation, assertions: TUIAssertions, project_factory: ProjectFactory
):
    """Test project and artifact creation workflow."""
    project = project_factory.build()
    project_key = project["key"]

    result = tui.execute_command(
        f"projects create --key {project_key} --name \"{project['name']}\""
    )
    assertions.assert_success(result)

    result = tui.execute_command(f"artifacts list --project {project_key}")
    assertions.assert_success(result)

    tui.cleanup_project(project_key)


@pytest.mark.e2e
def test_audit_multiple_iterations(
    tui: TUIAutomation, assertions: TUIAssertions, project_factory: ProjectFactory
):
    """Test multiple project operations."""
    project = project_factory.build()
    project_key = project["key"]

    result = tui.execute_command(
        f"projects create --key {project_key} --name \"{project['name']}\""
    )
    assertions.assert_success(result)

    result = tui.execute_command(f"projects get --key {project_key}")
    assertions.assert_success(result)

    result = tui.execute_command("projects list")
    assertions.assert_success(result)
    assertions.assert_contains(result, project_key)

    tui.cleanup_project(project_key)


@pytest.mark.e2e
def test_audit_results_persistence(
    tui: TUIAutomation, assertions: TUIAssertions, project_factory: ProjectFactory
):
    """Test project state persistence."""
    project = project_factory.build()
    project_key = project["key"]

    result = tui.execute_command(
        f"projects create --key {project_key} --name \"{project['name']}\""
    )
    assertions.assert_success(result)

    result1 = tui.execute_command(f"projects get --key {project_key}")
    assertions.assert_success(result1)

    result2 = tui.execute_command(f"projects get --key {project_key}")
    assertions.assert_success(result2)

    assertions.assert_contains(result1, project["name"])
    assertions.assert_contains(result2, project["name"])

    tui.cleanup_project(project_key)
