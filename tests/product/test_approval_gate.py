"""Unit tests for the Approval Gate FastAPI app.

Tests use FastAPI TestClient — no real mcp-agent-bus needed.
BusClient is patched with AsyncMock for all tests.
"""

from __future__ import annotations

from unittest.mock import AsyncMock, patch

import pytest
from fastapi.testclient import TestClient

from apps.approval_gate.main import app

# ---------------------------------------------------------------------------
# Shared fixtures
# ---------------------------------------------------------------------------

PENDING_RUN = {
    "run_id": "run-abc-123",
    "issue_number": 42,
    "repo": "owner/repo",
    "status": "awaiting_approval",
    "created_ts": "2026-03-02T10:00:00+00:00",
    "updated_ts": "2026-03-02T10:00:00+00:00",
}

CONTEXT_PACKET = {
    "run": {
        "run_id": "run-abc-123",
        "issue_number": 42,
        "repo": "owner/repo",
        "status": "awaiting_approval",
        "created_ts": "2026-03-02T10:00:00+00:00",
    },
    "plan": {
        "goal": "Add template CRUD",
        "files": ["apps/api/routers/templates.py"],
        "acceptance_criteria": ["GET /templates returns 200"],
        "validation_cmds": ["pytest tests/unit/"],
        "estimated_minutes": 30,
        "approved": 0,
        "feedback": "",
    },
    "file_snapshots": [],
    "validation_results": [],
    "checkpoints": [{"label": "plan_generated", "metadata": {}, "ts": "2026-03-02T10:00:00+00:00"}],
}


@pytest.fixture
def client():
    with TestClient(app) as c:
        yield c


# ---------------------------------------------------------------------------
# Health
# ---------------------------------------------------------------------------


def test_health(client):
    resp = client.get("/health")
    assert resp.status_code == 200
    assert resp.json()["status"] == "ok"


# ---------------------------------------------------------------------------
# GET /pending
# ---------------------------------------------------------------------------


def test_get_pending_returns_runs(client):
    mock_bus = AsyncMock()
    mock_bus.list_pending.return_value = [PENDING_RUN]

    with patch("apps.approval_gate.main._bus", mock_bus):
        resp = client.get("/pending")

    assert resp.status_code == 200
    data = resp.json()
    assert len(data) == 1
    assert data[0]["run_id"] == "run-abc-123"
    assert data[0]["issue_number"] == 42


def test_get_pending_empty(client):
    mock_bus = AsyncMock()
    mock_bus.list_pending.return_value = []

    with patch("apps.approval_gate.main._bus", mock_bus):
        resp = client.get("/pending")

    assert resp.status_code == 200
    assert resp.json() == []


# ---------------------------------------------------------------------------
# GET /plan/{run_id}
# ---------------------------------------------------------------------------


def test_get_plan_returns_card(client):
    mock_bus = AsyncMock()
    mock_bus.read_context_packet.return_value = CONTEXT_PACKET

    with patch("apps.approval_gate.main._bus", mock_bus):
        resp = client.get("/plan/run-abc-123")

    assert resp.status_code == 200
    card = resp.json()
    assert card["run_id"] == "run-abc-123"
    assert card["goal"] == "Add template CRUD"
    assert "apps/api/routers/templates.py" in card["files"]
    assert card["estimated_minutes"] == 30
    assert "plan_generated" in card["checkpoints"]


def test_get_plan_404_when_bus_errors(client):
    mock_bus = AsyncMock()
    mock_bus.read_context_packet.side_effect = ValueError("Unknown run_id: bad-id")

    with patch("apps.approval_gate.main._bus", mock_bus):
        resp = client.get("/plan/bad-id")

    assert resp.status_code == 404


def test_get_plan_no_plan_returns_empty_goal(client):
    packet_no_plan = {**CONTEXT_PACKET, "plan": None, "checkpoints": []}
    mock_bus = AsyncMock()
    mock_bus.read_context_packet.return_value = packet_no_plan

    with patch("apps.approval_gate.main._bus", mock_bus):
        resp = client.get("/plan/run-abc-123")

    assert resp.status_code == 200
    assert resp.json()["goal"] == ""
    assert resp.json()["files"] == []


# ---------------------------------------------------------------------------
# POST /approve/{run_id}
# ---------------------------------------------------------------------------


def test_approve_approved_true(client):
    mock_bus = AsyncMock()
    mock_bus.approve_run.return_value = None

    with patch("apps.approval_gate.main._bus", mock_bus):
        resp = client.post(
            "/approve/run-abc-123",
            json={"approved": True, "feedback": "LGTM"},
        )

    assert resp.status_code == 200
    assert resp.json()["decision"] == "approved"
    mock_bus.approve_run.assert_awaited_once_with(run_id="run-abc-123", feedback="LGTM")


def test_approve_approved_false_rejects(client):
    mock_bus = AsyncMock()
    mock_bus.reject_run.return_value = None

    with patch("apps.approval_gate.main._bus", mock_bus):
        resp = client.post(
            "/approve/run-abc-123",
            json={"approved": False, "feedback": "Needs more work"},
        )

    assert resp.status_code == 200
    assert resp.json()["decision"] == "rejected"
    mock_bus.reject_run.assert_awaited_once_with(run_id="run-abc-123", feedback="Needs more work")


def test_approve_default_empty_feedback(client):
    mock_bus = AsyncMock()
    mock_bus.approve_run.return_value = None

    with patch("apps.approval_gate.main._bus", mock_bus):
        resp = client.post("/approve/run-abc-123", json={"approved": True})

    assert resp.status_code == 200
    mock_bus.approve_run.assert_awaited_once_with(run_id="run-abc-123", feedback="")


def test_approve_returns_400_on_bus_error(client):
    mock_bus = AsyncMock()
    mock_bus.approve_run.side_effect = ValueError("Invalid transition")

    with patch("apps.approval_gate.main._bus", mock_bus):
        resp = client.post("/approve/run-abc-123", json={"approved": True})

    assert resp.status_code == 400


def test_approve_missing_approved_field_returns_422(client):
    resp = client.post("/approve/run-abc-123", json={"feedback": "no approved field"})
    assert resp.status_code == 422
