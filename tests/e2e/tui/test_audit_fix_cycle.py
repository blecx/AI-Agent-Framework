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

import pytest
import json
import re
from pathlib import Path

import httpx


def _write_json(path: Path, payload: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2), encoding="utf-8")


def _extract_total_issues(output: str) -> int:
    match = re.search(r"Total issues:\s*(\d+)", output)
    assert match, f"Could not parse total issues from audit output:\n{output}"
    return int(match.group(1))


@pytest.mark.tui
def test_audit_fix_cycle_foundation(tui, unique_project_key):
    """Test audit infrastructure foundation."""

    # Create project
    result = tui.create_project(key=unique_project_key, name="Audit Cycle Test")
    assert result.success

    # Verify project created
    result = tui.list_projects()
    assert result.success
    assert unique_project_key in result.stdout

    # Run audit command for existing project
    result = tui.execute_command(["audit", "--project", unique_project_key])
    assert result.success, f"Audit command failed: {result.stderr}"
    assert "Audit completed" in result.stdout
    assert "Issue Counts by" in result.stdout
    assert "Total issues" in result.stdout

    print(f"✓ Audit cycle foundation validated for {unique_project_key}")


@pytest.mark.tui
def test_audit_detects_missing_fields(tui, unique_project_key, temp_docs_dir):
    """Test audit detects missing required fields in artifacts."""
    result = tui.create_project(key=unique_project_key, name="Missing Fields Test")
    assert result.success

    metadata_path = Path(temp_docs_dir) / unique_project_key / "metadata.json"
    _write_json(
        metadata_path,
        {
            "key": unique_project_key,
            "name": "Missing Fields Test",
        },
    )

    result = tui.execute_command(
        ["audit", "--project", unique_project_key, "--rule", "required_fields"]
    )
    assert result.success, f"Audit command failed: {result.stderr}"
    assert "required_fields" in result.stdout, result.stdout
    assert "description" in result.stdout, result.stdout
    assert "start_date" in result.stdout, result.stdout
    assert _extract_total_issues(result.stdout) == 7, result.stdout


@pytest.mark.tui
def test_audit_fix_and_reaudit(tui, unique_project_key, temp_docs_dir):
    """Test full audit → fix → re-audit cycle."""
    result = tui.create_project(key=unique_project_key, name="Audit Re-Audit Test")
    assert result.success

    metadata_path = Path(temp_docs_dir) / unique_project_key / "metadata.json"

    _write_json(
        metadata_path,
        {
            "key": unique_project_key,
            "name": "Audit Re-Audit Test",
        },
    )

    first_audit = tui.execute_command(
        ["audit", "--project", unique_project_key, "--rule", "required_fields"]
    )
    assert first_audit.success, f"Initial audit failed: {first_audit.stderr}"
    assert _extract_total_issues(first_audit.stdout) == 7, first_audit.stdout

    project_path = Path(temp_docs_dir) / unique_project_key
    _write_json(
        metadata_path,
        {
            "key": unique_project_key,
            "name": "Audit Re-Audit Test",
            "description": "Deterministic metadata payload",
            "start_date": "2026-01-15",
            "blueprint": "bp-core-v1",
        },
    )
    _write_json(
        project_path / "artifacts" / "pmp.json",
        {
            "deliverables": [{"id": "DEL-001", "dependencies": []}],
            "milestones": [{"id": "MS-001", "due_date": "2026-02-15"}],
        },
    )
    _write_json(
        project_path / "artifacts" / "raid.json",
        {
            "items": [{"id": "RISK-001", "related_milestones": ["MS-001"]}],
        },
    )
    _write_json(
        project_path / "artifacts" / "governance.json",
        {
            "team": [{"id": "owner-1", "name": "Owner One"}],
            "roles": [{"id": "role-1", "name": "Sponsor"}],
        },
    )
    _write_json(
        project_path / "workflow" / "state.json",
        {
            "current_phase": "planning",
        },
    )

    second_audit = tui.execute_command(
        ["audit", "--project", unique_project_key, "--rule", "required_fields"]
    )
    assert second_audit.success, f"Re-audit failed: {second_audit.stderr}"
    assert _extract_total_issues(second_audit.stdout) == 0, second_audit.stdout


@pytest.mark.tui
def test_audit_validates_cross_references(tui, unique_project_key, temp_docs_dir):
    """Test audit validates cross-references between artifacts."""
    result = tui.create_project(key=unique_project_key, name="Cross Ref Test")
    assert result.success

    project_path = Path(temp_docs_dir) / unique_project_key
    _write_json(project_path / "artifacts" / "pmp.json", {"deliverables": []})
    _write_json(
        project_path / "artifacts" / "raid.json",
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
        ["audit", "--project", unique_project_key, "--rule", "cross_reference"]
    )
    assert result.success, f"Audit command failed: {result.stderr}"
    assert _extract_total_issues(result.stdout) == 2, result.stdout
    assert "D-404" in result.stdout, result.stdout
    assert "cross_reference" in result.stdout, result.stdout

def test_audit_error_handling(tui, unique_project_key):
    """Test audit handles errors gracefully (e.g., project not found)."""

    # Try to audit non-existent project
    result = tui.execute_command(["audit", "--project", "NONEXISTENT-999"], check=False)

    assert result is not None, "Audit command should handle errors gracefully"
    assert result.returncode != 0
    combined_output = f"{result.stdout}\n{result.stderr}".lower()
    assert "not found" in combined_output or "404" in combined_output


@pytest.mark.tui
def test_audit_history_tracking(tui, unique_project_key):
    """Test audit maintains history of runs and results."""
    result = tui.create_project(key=unique_project_key, name="Audit History Test")
    assert result.success

    first_audit = tui.execute_command(["audit", "--project", unique_project_key])
    assert first_audit.success, f"First audit failed: {first_audit.stderr}"

    second_audit = tui.execute_command(["audit", "--project", unique_project_key])
    assert second_audit.success, f"Second audit failed: {second_audit.stderr}"

    response = httpx.get(
        f"{tui.api_base_url}/projects/{unique_project_key}/audit/history",
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
