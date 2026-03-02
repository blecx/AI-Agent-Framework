"""Deterministic fixture baseline tests for TUI E2E infrastructure."""

from pathlib import Path

import pytest

from e2e.tui.helpers import build_tui_workspace, wait_for_http_ok


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
