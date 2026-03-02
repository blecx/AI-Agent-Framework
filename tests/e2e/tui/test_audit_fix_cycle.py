"""
TUI E2E Test: Audit Fix Cycle

Tests audit execution, issue detection, fix application, and re-audit validation.

Scenarios:
- Run audit and detect issues (missing fields, invalid cross-references)
- Create proposals to fix audit issues
- Apply fixes
- Re-run audit and verify clean results
- Validate audit history and compliance tracking
"""

import re

import httpx
import pytest

from e2e.tui.fixture_helper import write_json


def _extract_total_issues(output: str) -> int:
    match = re.search(r"Total issues:\s*(\d+)", output)
    assert match, f"Could not parse total issues from audit output:\n{output}"
    return int(match.group(1))


@pytest.mark.tui
@pytest.mark.e2e
def test_audit_fix_cycle_foundation(tui, unique_project_key):
    """Test audit infrastructure foundation."""

    result = tui.create_project(key=unique_project_key, name="Audit Cycle Test")
    assert result.success

    result = tui.list_projects()
    assert result.success
    assert unique_project_key in result.stdout

    result = tui.execute_command(["audit", "--project", unique_project_key])
    assert result.success, f"Audit command failed: {result.stderr}"
    assert "Audit completed" in result.stdout
    assert "Issue Counts by" in result.stdout
    assert "Total issues" in result.stdout


@pytest.mark.tui
@pytest.mark.e2e
def test_audit_detects_missing_fields(tui, tui_workspace):
    """Test audit detects missing required fields in artifacts."""
    result = tui.create_project(key=tui_workspace.project_key, name="Missing Fields Test")
    assert result.success

    write_json(
        tui_workspace.metadata_path,
        {
            "key": tui_workspace.project_key,
            "name": "Missing Fields Test",
        },
    )

    result = tui.execute_command(
        ["audit", "--project", tui_workspace.project_key, "--rule", "required_fields"]
    )
    assert result.success, f"Audit command failed: {result.stderr}"
    assert "required_fields" in result.stdout, result.stdout
    assert "description" in result.stdout, result.stdout
    assert "start_date" in result.stdout, result.stdout
    assert _extract_total_issues(result.stdout) == 7, result.stdout


@pytest.mark.tui
@pytest.mark.e2e
def test_audit_fix_and_reaudit(tui, tui_workspace):
    """Test full audit → fix → re-audit cycle."""
    result = tui.create_project(key=tui_workspace.project_key, name="Audit Re-Audit Test")
    assert result.success

    write_json(
        tui_workspace.metadata_path,
        {
            "key": tui_workspace.project_key,
            "name": "Audit Re-Audit Test",
        },
    )

    first_audit = tui.execute_command(
        ["audit", "--project", tui_workspace.project_key, "--rule", "required_fields"]
    )
    assert first_audit.success, f"Initial audit failed: {first_audit.stderr}"
    assert _extract_total_issues(first_audit.stdout) == 7, first_audit.stdout

    write_json(
        tui_workspace.metadata_path,
        {
            "key": tui_workspace.project_key,
            "name": "Audit Re-Audit Test",
            "description": "Deterministic metadata payload",
            "start_date": "2026-01-15",
            "blueprint": "bp-core-v1",
        },
    )
    write_json(
        tui_workspace.artifact_path("pmp"),
        {
            "deliverables": [{"id": "DEL-001", "dependencies": []}],
            "milestones": [{"id": "MS-001", "due_date": "2026-02-15"}],
        },
    )
    write_json(
        tui_workspace.artifact_path("raid"),
        {
            "items": [{"id": "RISK-001", "related_milestones": ["MS-001"]}],
        },
    )
    write_json(
        tui_workspace.artifact_path("governance"),
        {
            "team": [{"id": "owner-1", "name": "Owner One"}],
            "roles": [{"id": "role-1", "name": "Sponsor"}],
        },
    )
    write_json(
        tui_workspace.workflow_path("state"),
        {
            "current_phase": "planning",
        },
    )

    second_audit = tui.execute_command(
        ["audit", "--project", tui_workspace.project_key, "--rule", "required_fields"]
    )
    assert second_audit.success, f"Re-audit failed: {second_audit.stderr}"
    assert _extract_total_issues(second_audit.stdout) == 0, second_audit.stdout


@pytest.mark.tui
@pytest.mark.e2e
def test_audit_validates_cross_references(tui, tui_workspace):
    """Test audit validates cross-references between artifacts."""
    result = tui.create_project(key=tui_workspace.project_key, name="Cross Ref Test")
    assert result.success

    write_json(tui_workspace.artifact_path("pmp"), {"deliverables": []})
    write_json(
        tui_workspace.artifact_path("raid"),
        {
            "items": [
                {
                    "id": "RISK-001",
                    "related_deliverables": ["D-404"],
                }
            ]
        },
    )

    result = tui.execute_command(
        ["audit", "--project", tui_workspace.project_key, "--rule", "cross_reference"]
    )
    assert result.success, f"Audit command failed: {result.stderr}"
    assert _extract_total_issues(result.stdout) == 2, result.stdout
    assert "D-404" in result.stdout, result.stdout
    assert "cross_reference" in result.stdout, result.stdout


@pytest.mark.tui
@pytest.mark.e2e
def test_audit_error_handling(tui, unique_project_key):
    """Test audit handles errors gracefully (e.g., project not found)."""

    result = tui.execute_command(["audit", "--project", "NONEXISTENT-999"], check=False)

    assert result is not None, "Audit command should handle errors gracefully"
    assert result.returncode != 0
    combined_output = f"{result.stdout}\n{result.stderr}".lower()
    assert "not found" in combined_output or "404" in combined_output


@pytest.mark.tui
@pytest.mark.e2e
def test_audit_history_tracking(tui, unique_project_key):
    """Test audit maintains history of runs and results."""
    result = tui.create_project(key=unique_project_key, name="Audit History Test")
    assert result.success

    first_audit = tui.execute_command(["audit", "--project", unique_project_key])
    assert first_audit.success, f"First audit failed: {first_audit.stderr}"

    second_audit = tui.execute_command(["audit", "--project", unique_project_key])
    assert second_audit.success, f"Second audit failed: {second_audit.stderr}"

    response = httpx.get(
        f"{tui.api_base_url}/api/v1/projects/{unique_project_key}/audit/history",
        params={"limit": 10},
        timeout=10.0,
    )
    assert response.status_code == 200, response.text

    payload = response.json()
    audits = payload.get("audits", [])
    assert len(audits) >= 2, payload

    latest = audits[0]
    for field in ("timestamp", "total_issues", "completeness_score", "rule_violations"):
        assert field in latest, payload
