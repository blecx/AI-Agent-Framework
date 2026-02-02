"""
Integration tests for Workflow API endpoints.
"""

import pytest
from fastapi.testclient import TestClient
import tempfile
import shutil
import sys
import os
import json

# Add apps/api to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../../apps/api"))

from main import app


@pytest.fixture(scope="function")
def temp_project_dir():
    """Create a temporary project directory for testing."""
    temp_dir = tempfile.mkdtemp()
    yield temp_dir
    shutil.rmtree(temp_dir)


@pytest.fixture(scope="function")
def client(temp_project_dir):
    """Create a test client with temporary project directory."""
    # Override the PROJECT_DOCS_PATH environment variable
    os.environ["PROJECT_DOCS_PATH"] = temp_project_dir

    # Create a new app instance for this test to avoid state sharing
    from fastapi import FastAPI
    from fastapi.middleware.cors import CORSMiddleware

    test_app = FastAPI(title="Test App")
    test_app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Import and register routers
    from routers import projects, commands, artifacts, governance, raid, workflow

    test_app.include_router(projects.router, prefix="/projects", tags=["projects"])
    test_app.include_router(
        commands.router,
        prefix="/projects/{project_key}/commands",
        tags=["commands"],
    )
    test_app.include_router(
        artifacts.router,
        prefix="/projects/{project_key}/artifacts",
        tags=["artifacts"],
    )
    test_app.include_router(
        governance.router,
        prefix="/projects/{project_key}/governance",
        tags=["governance"],
    )
    test_app.include_router(
        raid.router, prefix="/projects/{project_key}/raid", tags=["raid"]
    )
    test_app.include_router(
        workflow.router, prefix="/api/v1/projects", tags=["workflow"]
    )

    # Initialize services
    from services.git_manager import GitManager
    from services.llm_service import LLMService

    git_manager = GitManager(temp_project_dir)
    git_manager.ensure_repository()
    test_app.state.git_manager = git_manager
    test_app.state.llm_service = LLMService()

    with TestClient(test_app) as test_client:
        yield test_client


@pytest.fixture
def test_project(client):
    """Create a test project."""
    response = client.post("/projects", json={"key": "TEST001", "name": "Test Project"})
    assert response.status_code == 201
    return response.json()


class TestWorkflowStateAPI:
    """Test workflow state API endpoints."""

    def test_get_workflow_state_initial(self, client, test_project):
        """Test getting initial workflow state."""
        response = client.get("/api/v1/projects/TEST001/workflow/state")

        assert response.status_code == 200
        data = response.json()
        assert data["current_state"] == "initiating"
        assert data["previous_state"] is None
        assert data["transition_history"] == []
        assert "updated_at" in data
        assert data["updated_by"] == "system"

    def test_transition_workflow_state_valid(self, client, test_project):
        """Test valid workflow state transition."""
        response = client.patch(
            "/api/v1/projects/TEST001/workflow/state",
            json={
                "to_state": "planning",
                "actor": "test_user",
                "reason": "Ready to plan",
            },
        )

        assert response.status_code == 200
        data = response.json()
        assert data["current_state"] == "planning"
        assert data["previous_state"] == "initiating"
        assert data["updated_by"] == "test_user"
        assert len(data["transition_history"]) == 1

        # Verify transition details
        transition = data["transition_history"][0]
        assert transition["from_state"] == "initiating"
        assert transition["to_state"] == "planning"
        assert transition["actor"] == "test_user"
        assert transition["reason"] == "Ready to plan"
        assert "timestamp" in transition

    def test_transition_workflow_state_invalid(self, client, test_project):
        """Test invalid workflow state transition."""
        response = client.patch(
            "/api/v1/projects/TEST001/workflow/state",
            json={"to_state": "closed", "actor": "test_user"},
        )

        assert response.status_code == 400
        assert "Invalid transition" in response.json()["detail"]

    def test_transition_workflow_state_nonexistent_project(self, client):
        """Test transitioning state for nonexistent project."""
        response = client.patch(
            "/api/v1/projects/NONEXISTENT/workflow/state",
            json={"to_state": "planning", "actor": "test_user"},
        )

        assert response.status_code == 404

    def test_multiple_sequential_transitions(self, client, test_project):
        """Test multiple sequential state transitions."""
        # Transition through multiple states
        transitions = [
            ("planning", "user1"),
            ("executing", "user2"),
            ("monitoring", "user3"),
        ]

        for to_state, actor in transitions:
            response = client.patch(
                "/api/v1/projects/TEST001/workflow/state",
                json={"to_state": to_state, "actor": actor},
            )
            assert response.status_code == 200

        # Verify final state
        response = client.get("/api/v1/projects/TEST001/workflow/state")
        data = response.json()
        assert data["current_state"] == "monitoring"
        assert data["previous_state"] == "executing"
        assert len(data["transition_history"]) == 3

    def test_get_allowed_transitions(self, client, test_project):
        """Test getting allowed transitions from current state."""
        response = client.get("/api/v1/projects/TEST001/workflow/allowed-transitions")

        assert response.status_code == 200
        data = response.json()
        assert data["current_state"] == "initiating"
        assert data["allowed_transitions"] == ["planning"]

    def test_get_allowed_transitions_after_transition(self, client, test_project):
        """Test getting allowed transitions after state change."""
        # Transition to planning
        client.patch(
            "/api/v1/projects/TEST001/workflow/state",
            json={"to_state": "planning", "actor": "test_user"},
        )

        # Get allowed transitions
        response = client.get("/api/v1/projects/TEST001/workflow/allowed-transitions")

        assert response.status_code == 200
        data = response.json()
        assert data["current_state"] == "planning"
        assert set(data["allowed_transitions"]) == {"executing", "initiating"}

    def test_workflow_state_persists(self, client, test_project):
        """Test that workflow state persists across API calls."""
        # Transition state
        client.patch(
            "/api/v1/projects/TEST001/workflow/state",
            json={"to_state": "planning", "actor": "test_user"},
        )

        # Get state again
        response = client.get("/api/v1/projects/TEST001/workflow/state")
        data = response.json()

        assert data["current_state"] == "planning"
        assert data["previous_state"] == "initiating"


class TestAuditEventsAPI:
    """Test audit events API endpoints."""

    def test_get_audit_events_empty(self, client, test_project):
        """Test getting audit events when none exist."""
        response = client.get("/api/v1/projects/TEST001/audit-events")

        assert response.status_code == 200
        data = response.json()
        assert data["events"] == []
        assert data["total"] == 0
        assert data["limit"] == 100
        assert data["offset"] == 0

    def test_get_audit_events_after_state_transition(self, client, test_project):
        """Test that state transitions create audit events."""
        # Perform state transition
        client.patch(
            "/api/v1/projects/TEST001/workflow/state",
            json={
                "to_state": "planning",
                "actor": "test_user",
                "reason": "Ready to plan",
            },
        )

        # Get audit events
        response = client.get("/api/v1/projects/TEST001/audit-events")

        assert response.status_code == 200
        data = response.json()
        assert len(data["events"]) >= 1

        # Find workflow state change event
        state_change_events = [
            e for e in data["events"] if e["event_type"] == "workflow_state_changed"
        ]
        assert len(state_change_events) >= 1

        event = state_change_events[0]
        assert event["actor"] == "test_user"
        assert event["payload_summary"]["from_state"] == "initiating"
        assert event["payload_summary"]["to_state"] == "planning"
        assert event["payload_summary"]["reason"] == "Ready to plan"
        assert "timestamp" in event
        assert "event_id" in event

    def test_get_audit_events_with_pagination(self, client, test_project):
        """Test pagination of audit events."""
        # Create multiple state transitions to generate events
        transitions = [
            ("planning", "user1"),
            ("executing", "user2"),
            ("monitoring", "user3"),
        ]

        for to_state, actor in transitions:
            client.patch(
                "/api/v1/projects/TEST001/workflow/state",
                json={"to_state": to_state, "actor": actor},
            )

        # Get first page
        response = client.get("/api/v1/projects/TEST001/audit-events?limit=2&offset=0")

        assert response.status_code == 200
        data = response.json()
        assert len(data["events"]) == 2
        assert data["limit"] == 2
        assert data["offset"] == 0

    def test_filter_audit_events_by_type(self, client, test_project):
        """Test filtering audit events by event type."""
        # Perform state transition
        client.patch(
            "/api/v1/projects/TEST001/workflow/state",
            json={"to_state": "planning", "actor": "test_user"},
        )

        # Filter by workflow_state_changed
        response = client.get(
            "/api/v1/projects/TEST001/audit-events?event_type=workflow_state_changed"
        )

        assert response.status_code == 200
        data = response.json()
        assert all(e["event_type"] == "workflow_state_changed" for e in data["events"])
        assert data["filtered_by"]["event_type"] == "workflow_state_changed"

    def test_filter_audit_events_by_actor(self, client, test_project):
        """Test filtering audit events by actor."""
        # Perform state transitions with different actors
        client.patch(
            "/api/v1/projects/TEST001/workflow/state",
            json={"to_state": "planning", "actor": "user1"},
        )
        client.patch(
            "/api/v1/projects/TEST001/workflow/state",
            json={"to_state": "executing", "actor": "user2"},
        )

        # Filter by user1
        response = client.get("/api/v1/projects/TEST001/audit-events?actor=user1")

        assert response.status_code == 200
        data = response.json()
        user1_events = [e for e in data["events"] if e["actor"] == "user1"]
        assert len(user1_events) > 0

    def test_get_audit_events_nonexistent_project(self, client):
        """Test getting audit events for nonexistent project."""
        response = client.get("/api/v1/projects/NONEXISTENT/audit-events")

        assert response.status_code == 404


class TestWorkflowAuditIntegration:
    """Test integration between workflow and audit systems."""

    def test_workflow_transition_creates_audit_event(self, client, test_project):
        """Test that workflow transitions automatically create audit events."""
        # Perform state transition
        transition_response = client.patch(
            "/api/v1/projects/TEST001/workflow/state",
            json={
                "to_state": "planning",
                "actor": "test_user",
                "reason": "Starting planning phase",
            },
        )
        assert transition_response.status_code == 200

        # Get audit events
        audit_response = client.get("/api/v1/projects/TEST001/audit-events")
        data = audit_response.json()

        # Should have at least one workflow_state_changed event
        state_events = [
            e for e in data["events"] if e["event_type"] == "workflow_state_changed"
        ]
        assert len(state_events) >= 1

        # Verify event details match transition
        event = state_events[0]
        assert event["actor"] == "test_user"
        assert event["payload_summary"]["from_state"] == "initiating"
        assert event["payload_summary"]["to_state"] == "planning"
        assert event["payload_summary"]["reason"] == "Starting planning phase"

    def test_correlation_id_in_audit_events(self, client, test_project):
        """Test that correlation ID from request header appears in audit events."""
        correlation_id = "test-corr-123"

        # Perform state transition with correlation ID header
        client.patch(
            "/api/v1/projects/TEST001/workflow/state",
            json={"to_state": "planning", "actor": "test_user"},
            headers={"X-Correlation-ID": correlation_id},
        )

        # Get audit events
        response = client.get("/api/v1/projects/TEST001/audit-events")
        data = response.json()

        # Find workflow state change event with correlation ID
        state_events = [
            e
            for e in data["events"]
            if e["event_type"] == "workflow_state_changed"
            and e.get("correlation_id") == correlation_id
        ]
        assert len(state_events) >= 1
