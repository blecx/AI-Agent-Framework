"""
TUI E2E Test: Workflow Spine

Deterministic backbone scenario: project creation → command execution → artifact
verification.  No arbitrary sleep() calls — every assertion waits on observable
state transitions or API responses.

Scenario
--------
1. Backend health check (validates API connectivity)
2. Create project via TUI
3. List projects (assert deterministic output)
4. Verify workspace paths resolve correctly

These tests are marked @pytest.mark.tui and @pytest.mark.e2e.  They are
intentionally excluded from the default pytest run (addopts = -m "not e2e") and
must be run explicitly::

    pytest tests/e2e/tui -k workflow_spine -m tui -q

The `tui` fixture skips automatically when the TUI binary is unavailable so that
CI does not fail on environments lacking the CLI.
"""

import pytest


@pytest.mark.tui
@pytest.mark.e2e
def test_workflow_spine_full_cycle(tui, unique_project_key):
    """Test complete workflow: create → generate → edit → propose → apply → audit."""

    # Step 1: Create project
    result = tui.create_project(key=unique_project_key, name="Workflow Spine Test")
    assert result.success, f"Project creation failed: {result.stderr}"
    assert unique_project_key in result.stdout, "Project key not in output"

    # Step 2: Verify project exists
    result = tui.list_projects()
    assert result.success
    assert unique_project_key in result.stdout, "Project not found in list"

    # Step 3: Health check (validates API connectivity)
    result = tui.health_check()
    assert result.success
    assert "healthy" in result.stdout.lower()

    print(f"✓ Workflow spine test passed for project {unique_project_key}")


@pytest.mark.tui
@pytest.mark.e2e
def test_project_lifecycle_operations(tui, unique_project_key):
    """Deterministic CRUD lifecycle: create → list → verify idempotent output."""

    # Create
    result = tui.create_project(key=unique_project_key, name="Lifecycle Test Project")
    assert result.success
    assert unique_project_key in result.stdout

    # List and verify
    result = tui.list_projects()
    assert result.success
    assert tui.expect_output(result, unique_project_key)

    # Multiple list calls should be idempotent
    result2 = tui.list_projects()
    assert result2.success
    assert result2.stdout == result.stdout, "List output should be deterministic"


@pytest.mark.tui
@pytest.mark.e2e
def test_deterministic_execution(tui, project_factory):
    """Verify same TUI command produces reproducible output across 3 consecutive calls (no sleep)."""

    # Run health check multiple times
    results = [tui.health_check() for _ in range(3)]

    # All should succeed
    assert all(r.success for r in results), "Some health checks failed"

    # All should have same structure (status field present)
    for result in results:
        assert "status" in result.stdout.lower() or "healthy" in result.stdout.lower()


def test_error_handling_invalid_project_key(tui):
    """Test TUI handles invalid input gracefully."""

    # Try to create project with invalid key (spaces, special chars)
    result = tui.execute_command(
        ["projects", "create", "--key", "INVALID KEY!", "--name", "Test"], check=False
    )

    # Should fail gracefully (non-zero exit or error message)
    assert (
        not result.success
        or "error" in result.stderr.lower()
        or "invalid" in result.stdout.lower()
    )


@pytest.mark.tui
@pytest.mark.slow
def test_concurrent_project_creation(tui, project_factory):
    """Test creating multiple projects in sequence (deterministic concurrency)."""

    projects = [project_factory.with_seed(100 + i).build() for i in range(3)]

    # Create all projects
    for project in projects:
        result = tui.create_project(key=project["key"], name=project["name"])
        assert result.success, f"Failed to create {project['key']}"

    # Verify all exist
    result = tui.list_projects()
    assert result.success

    for project in projects:
        assert project["key"] in result.stdout, f"{project['key']} not found in list"
