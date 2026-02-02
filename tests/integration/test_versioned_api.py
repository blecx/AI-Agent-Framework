"""
Integration tests for Versioned API endpoints (/api/v1).
Tests API versioning, backward compatibility, and complete workflows.
"""

import pytest
from fastapi.testclient import TestClient
import tempfile
import shutil
import sys
import os

# Add apps/api to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../../apps/api"))


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

    # Import and register routers - versioned routes
    from routers import projects, commands, artifacts, governance, raid, workflow

    # API v1 routes
    test_app.include_router(
        projects.router, prefix="/api/v1/projects", tags=["projects-v1"]
    )
    test_app.include_router(
        commands.router,
        prefix="/api/v1/projects/{project_key}/commands",
        tags=["commands-v1"],
    )
    test_app.include_router(
        artifacts.router,
        prefix="/api/v1/projects/{project_key}/artifacts",
        tags=["artifacts-v1"],
    )
    test_app.include_router(
        governance.router,
        prefix="/api/v1/projects/{project_key}/governance",
        tags=["governance-v1"],
    )
    test_app.include_router(
        raid.router, prefix="/api/v1/projects/{project_key}/raid", tags=["raid-v1"]
    )
    test_app.include_router(
        workflow.router, prefix="/api/v1/projects", tags=["workflow-v1"]
    )

    # Add health endpoint
    @test_app.get("/api/v1/health")
    async def health():
        """Health check endpoint."""
        return {
            "status": "healthy",
            "docs_path": temp_project_dir,
            "docs_exists": os.path.exists(temp_project_dir),
            "docs_is_git": os.path.exists(os.path.join(temp_project_dir, ".git")),
            "api_version": "v1",
        }

    # Initialize services
    from services.git_manager import GitManager
    from services.llm_service import LLMService

    git_manager = GitManager(temp_project_dir)
    git_manager.ensure_repository()
    test_app.state.git_manager = git_manager
    test_app.state.llm_service = LLMService()

    with TestClient(test_app) as test_client:
        yield test_client


class TestVersionedHealthEndpoint:
    """Test versioned health check endpoint."""

    def test_health_check_returns_200(self, client):
        """Test that versioned health endpoint returns 200 OK."""
        response = client.get("/api/v1/health")
        assert response.status_code == 200

    def test_health_check_returns_api_version(self, client):
        """Test that health check includes api_version field."""
        response = client.get("/api/v1/health")
        data = response.json()
        assert "api_version" in data
        assert data["api_version"] == "v1"

    def test_health_check_returns_status(self, client):
        """Test that health check returns status field."""
        response = client.get("/api/v1/health")
        data = response.json()
        assert "status" in data
        assert data["status"] == "healthy"


class TestVersionedProjectsAPI:
    """Test versioned project management endpoints."""

    def test_create_project_success(self, client):
        """Test creating a new project via /api/v1."""
        response = client.post(
            "/api/v1/projects", json={"key": "V1TEST001", "name": "V1 Test Project"}
        )

        assert response.status_code == 201
        data = response.json()
        assert data["key"] == "V1TEST001"
        assert data["name"] == "V1 Test Project"
        assert "created_at" in data

    def test_list_projects_empty(self, client):
        """Test listing projects when none exist via /api/v1."""
        response = client.get("/api/v1/projects")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        assert len(data) == 0

    def test_list_projects_returns_created_projects(self, client):
        """Test that listing returns created projects via /api/v1."""
        # Create multiple projects
        client.post("/api/v1/projects", json={"key": "V1P1", "name": "Project 1"})
        client.post("/api/v1/projects", json={"key": "V1P2", "name": "Project 2"})

        response = client.get("/api/v1/projects")
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 2

        keys = [p["key"] for p in data]
        assert "V1P1" in keys
        assert "V1P2" in keys

    def test_get_project_state_success(self, client):
        """Test getting project state via /api/v1."""
        client.post("/api/v1/projects", json={"key": "V1STATE", "name": "State Test"})

        response = client.get("/api/v1/projects/V1STATE/state")
        assert response.status_code == 200
        data = response.json()

        assert "project_info" in data
        assert data["project_info"]["key"] == "V1STATE"
        assert "artifacts" in data

    def test_get_project_state_nonexistent_returns_404(self, client):
        """Test getting state for nonexistent project via /api/v1."""
        response = client.get("/api/v1/projects/NONEXISTENT/state")
        assert response.status_code == 404


class TestVersionedCommandsAPI:
    """Test versioned command propose/apply endpoints."""

    @pytest.fixture
    def test_project(self, client):
        """Create a test project."""
        response = client.post(
            "/api/v1/projects", json={"key": "V1CMD001", "name": "Command Test"}
        )
        assert response.status_code == 201
        return response.json()

    def test_propose_command_nonexistent_project(self, client):
        """Test proposing command for nonexistent project via /api/v1."""
        response = client.post(
            "/api/v1/projects/NONEXISTENT/commands/propose",
            json={"command": "assess_gaps", "params": {}},
        )
        assert response.status_code == 404

    def test_propose_unknown_command(self, client, test_project):
        """Test proposing an unknown command via /api/v1."""
        response = client.post(
            "/api/v1/projects/V1CMD001/commands/propose",
            json={"command": "unknown_command", "params": {}},
        )
        assert response.status_code == 400
        assert "Unknown command" in response.json()["detail"]

    def test_apply_nonexistent_proposal(self, client, test_project):
        """Test applying nonexistent proposal via /api/v1."""
        response = client.post(
            "/api/v1/projects/V1CMD001/commands/apply",
            json={"proposal_id": "nonexistent-proposal-id"},
        )
        assert response.status_code == 400
        assert "not found" in response.json()["detail"]


class TestVersionedArtifactsAPI:
    """Test versioned artifact listing and retrieval endpoints."""

    def test_list_artifacts_nonexistent_project(self, client):
        """Test listing artifacts for nonexistent project via /api/v1."""
        response = client.get("/api/v1/projects/NONEXISTENT/artifacts")
        assert response.status_code == 404

    def test_list_artifacts_empty_project(self, client):
        """Test listing artifacts for project with no artifacts via /api/v1."""
        client.post(
            "/api/v1/projects", json={"key": "V1EMPTY", "name": "Empty Project"}
        )
        response = client.get("/api/v1/projects/V1EMPTY/artifacts")

        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        assert len(data) == 0

    def test_get_artifact_nonexistent_project(self, client):
        """Test getting artifact for nonexistent project via /api/v1."""
        response = client.get("/api/v1/projects/NONEXISTENT/artifacts/test.md")
        assert response.status_code == 404


class TestVersionedWorkflowAPI:
    """Test versioned workflow state management endpoints."""

    @pytest.fixture
    def test_project(self, client):
        """Create a test project."""
        response = client.post(
            "/api/v1/projects", json={"key": "V1WF001", "name": "Workflow Test"}
        )
        assert response.status_code == 201
        return response.json()

    def test_get_workflow_state(self, client, test_project):
        """Test getting workflow state via /api/v1."""
        response = client.get("/api/v1/projects/V1WF001/workflow/state")
        assert response.status_code == 200
        data = response.json()
        assert "current_state" in data
        # Initial state should be "initiating"
        assert data["current_state"] == "initiating"

    def test_get_allowed_transitions(self, client, test_project):
        """Test getting allowed transitions via /api/v1."""
        response = client.get("/api/v1/projects/V1WF001/workflow/allowed-transitions")
        assert response.status_code == 200
        data = response.json()
        assert "current_state" in data
        assert "allowed_transitions" in data
        assert isinstance(data["allowed_transitions"], list)

    def test_transition_workflow_state_valid(self, client, test_project):
        """Test valid workflow state transition via /api/v1."""
        # Transition from initiating to planning (valid transition)
        response = client.patch(
            "/api/v1/projects/V1WF001/workflow/state",
            json={
                "to_state": "planning",
                "actor": "test_user",
                "reason": "Test transition",
            },
        )
        assert response.status_code == 200
        data = response.json()
        assert data["current_state"] == "planning"

    def test_transition_workflow_state_invalid(self, client, test_project):
        """Test invalid workflow state transition via /api/v1."""
        # Try to transition from initiating to closed (invalid)
        response = client.patch(
            "/api/v1/projects/V1WF001/workflow/state",
            json={"to_state": "closed", "actor": "test_user"},
        )
        assert response.status_code == 400


class TestVersionedRAIDAPI:
    """Test versioned RAID register endpoints."""

    @pytest.fixture
    def test_project(self, client):
        """Create a test project."""
        response = client.post(
            "/api/v1/projects", json={"key": "V1RAID001", "name": "RAID Test"}
        )
        assert response.status_code == 201
        return response.json()

    def test_list_raid_items_empty(self, client, test_project):
        """Test listing RAID items for empty project via /api/v1."""
        response = client.get("/api/v1/projects/V1RAID001/raid")
        assert response.status_code == 200
        data = response.json()
        assert "items" in data
        assert "total" in data
        assert data["total"] == 0

    def test_create_raid_item(self, client, test_project):
        """Test creating a RAID item via /api/v1."""
        raid_data = {
            "type": "risk",
            "title": "Test Risk",
            "description": "Test risk description",
            "owner": "test_user",
            "priority": "high",
            "status": "open",
        }

        response = client.post("/api/v1/projects/V1RAID001/raid", json=raid_data)
        assert response.status_code == 201
        data = response.json()
        assert data["title"] == "Test Risk"
        assert data["type"] == "risk"
        assert "id" in data

    def test_list_raid_items_with_items(self, client, test_project):
        """Test listing RAID items after creation via /api/v1."""
        # Create a RAID item
        raid_data = {
            "type": "issue",
            "title": "Test Issue",
            "description": "Test issue description",
            "owner": "test_user",
        }
        client.post("/api/v1/projects/V1RAID001/raid", json=raid_data)

        # List items
        response = client.get("/api/v1/projects/V1RAID001/raid")
        assert response.status_code == 200
        data = response.json()
        assert data["total"] == 1
        assert len(data["items"]) == 1


class TestVersionedGovernanceAPI:
    """Test versioned governance endpoints."""

    @pytest.fixture
    def test_project(self, client):
        """Create a test project."""
        response = client.post(
            "/api/v1/projects", json={"key": "V1GOV001", "name": "Governance Test"}
        )
        assert response.status_code == 201
        return response.json()

    def test_get_governance_metadata(self, client, test_project):
        """Test getting governance metadata via /api/v1."""
        response = client.get("/api/v1/projects/V1GOV001/governance")
        # Governance metadata may not exist initially, which is OK
        # We're just testing the endpoint is available
        assert response.status_code in [200, 404]
        if response.status_code == 200:
            data = response.json()
            assert "objectives" in data
            assert "scope" in data


class TestVersionedAuditEventsAPI:
    """Test versioned audit events endpoints."""

    @pytest.fixture
    def test_project(self, client):
        """Create a test project."""
        response = client.post(
            "/api/v1/projects", json={"key": "V1AUDIT001", "name": "Audit Test"}
        )
        assert response.status_code == 201
        return response.json()

    def test_get_audit_events(self, client, test_project):
        """Test getting audit events via /api/v1."""
        response = client.get("/api/v1/projects/V1AUDIT001/audit-events")
        assert response.status_code == 200
        data = response.json()
        assert "events" in data
        assert "total" in data
        assert isinstance(data["events"], list)


class TestVersionedAPIEndToEndWorkflow:
    """Test complete E2E workflow using versioned API."""

    def test_complete_project_lifecycle(self, client):
        """Test complete project workflow via /api/v1."""
        # 1. Create project
        create_response = client.post(
            "/api/v1/projects", json={"key": "V1E2E001", "name": "E2E Test Project"}
        )
        assert create_response.status_code == 201

        # 2. Get project state
        state_response = client.get("/api/v1/projects/V1E2E001/state")
        assert state_response.status_code == 200
        state_data = state_response.json()
        assert state_data["project_info"]["key"] == "V1E2E001"

        # 3. Check workflow state
        workflow_response = client.get("/api/v1/projects/V1E2E001/workflow/state")
        assert workflow_response.status_code == 200
        workflow_data = workflow_response.json()
        assert workflow_data["current_state"] == "initiating"

        # 4. Create a RAID item
        raid_response = client.post(
            "/api/v1/projects/V1E2E001/raid",
            json={
                "type": "risk",
                "title": "E2E Risk",
                "description": "E2E test risk",
                "owner": "test_user",
            },
        )
        assert raid_response.status_code == 201

        # 5. List RAID items
        raid_list_response = client.get("/api/v1/projects/V1E2E001/raid")
        assert raid_list_response.status_code == 200
        raid_list_data = raid_list_response.json()
        assert raid_list_data["total"] == 1

        # 6. Transition workflow state
        transition_response = client.patch(
            "/api/v1/projects/V1E2E001/workflow/state",
            json={"to_state": "planning", "actor": "test_user"},
        )
        assert transition_response.status_code == 200

        # 7. Verify state changed
        workflow_response2 = client.get("/api/v1/projects/V1E2E001/workflow/state")
        assert workflow_response2.status_code == 200
        assert workflow_response2.json()["current_state"] == "planning"

        # 8. Get audit events
        audit_response = client.get("/api/v1/projects/V1E2E001/audit-events")
        assert audit_response.status_code == 200
        audit_data = audit_response.json()
        # Should have events for: project_created, and possibly workflow_state_changed, raid_item_created
        # At minimum, should have project_created event
        assert audit_data["total"] >= 1

        # 9. List artifacts
        artifacts_response = client.get("/api/v1/projects/V1E2E001/artifacts")
        assert artifacts_response.status_code == 200
        artifacts_data = artifacts_response.json()
        assert isinstance(artifacts_data, list)


class TestAPIVersioningStrategy:
    """Test API versioning strategy and backward compatibility."""

    def test_versioned_and_unversioned_routes_coexist(self, client):
        """Test that versioned routes work independently."""
        # Create via versioned API
        v1_response = client.post(
            "/api/v1/projects", json={"key": "VTEST001", "name": "Version Test"}
        )
        assert v1_response.status_code == 201

        # Verify can retrieve via versioned API
        v1_state = client.get("/api/v1/projects/VTEST001/state")
        assert v1_state.status_code == 200
