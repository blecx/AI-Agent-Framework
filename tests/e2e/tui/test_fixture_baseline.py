"""Deterministic fixture baseline tests for TUI E2E infrastructure."""

import json
from pathlib import Path

import pytest

from e2e.tui.helpers import (
    build_tui_workspace,
    reset_tui_workspace,
    wait_for_http_ok,
    write_json,
)


@pytest.mark.tui
def test_fixture_workspace_is_deterministic(temp_docs_dir, tui_workspace):
    workspace_a = tui_workspace
    workspace_b = build_tui_workspace(temp_docs_dir, tui_workspace.project_key)

    assert workspace_a.project_dir == workspace_b.project_dir
    assert workspace_a.metadata_path == workspace_b.metadata_path
    assert workspace_a.project_dir.exists()
    assert workspace_a.project_dir == Path(temp_docs_dir) / tui_workspace.project_key


@pytest.mark.tui
def test_fixture_backend_health_endpoint_stable(backend_server):
    for _ in range(3):
        wait_for_http_ok(f"{backend_server}/health", timeout_seconds=5.0)


@pytest.mark.tui
def test_write_json_creates_file_with_correct_content(tui_workspace):
    """write_json must create parent dirs and write valid JSON."""
    payload = {"key": tui_workspace.project_key, "phase": "planning", "score": 42}
    target = tui_workspace.artifact_path("pmp")

    assert not target.exists(), "Artifact file should not exist before write"
    write_json(target, payload)

    assert target.exists(), "write_json must create the file"
    loaded = json.loads(target.read_text(encoding="utf-8"))
    assert loaded == payload, "write_json must round-trip JSON exactly"


@pytest.mark.tui
def test_write_json_overwrites_existing_file(tui_workspace):
    """write_json must overwrite when file already exists."""
    target = tui_workspace.metadata_path

    write_json(target, {"version": 1})
    write_json(target, {"version": 2})

    loaded = json.loads(target.read_text(encoding="utf-8"))
    assert loaded["version"] == 2, "write_json must overwrite with latest payload"


@pytest.mark.tui
def test_reset_tui_workspace_removes_project_dir(temp_docs_dir):
    """reset_tui_workspace must delete the project directory."""
    from fixtures.factories import ProjectFactory

    key = ProjectFactory.random_key()
    workspace = build_tui_workspace(temp_docs_dir, key)

    write_json(workspace.metadata_path, {"key": key})
    assert workspace.project_dir.exists()

    reset_tui_workspace(workspace)
    assert not workspace.project_dir.exists(), "reset must remove the project dir"


@pytest.mark.tui
def test_tui_workspace_artifact_and_workflow_paths(tui_workspace):
    """TuiE2EWorkspace path helpers must resolve under the project dir."""
    pmp_path = tui_workspace.artifact_path("pmp")
    raid_path = tui_workspace.artifact_path("raid")
    workflow_path = tui_workspace.workflow_path("state")

    assert pmp_path.parent == tui_workspace.project_dir / "artifacts"
    assert raid_path.parent == tui_workspace.project_dir / "artifacts"
    assert workflow_path.parent == tui_workspace.project_dir / "workflow"
    assert pmp_path.name == "pmp.json"
    assert raid_path.name == "raid.json"
    assert workflow_path.name == "state.json"
