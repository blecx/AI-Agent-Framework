"""
Integration tests for Governance API endpoints.
"""
import pytest
from fastapi.testclient import TestClient
import tempfile
import shutil
from pathlib import Path
import sys
import os

# Add apps/api to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../../apps/api"))

from main import app


@pytest.fixture
def temp_project_dir():
    """Create a temporary project directory for testing."""
    temp_dir = tempfile.mkdtemp()
    yield temp_dir
    shutil.rmtree(temp_dir)


@pytest.fixture
def client(temp_project_dir):
    """Create a test client with temporary project directory."""
    # Override the PROJECT_DOCS_PATH environment variable
    os.environ["PROJECT_DOCS_PATH"] = temp_project_dir
    
    # Force app to reinitialize with new path
    from services.git_manager import GitManager
    git_manager = GitManager(temp_project_dir)
    git_manager.ensure_repository()
    app.state.git_manager = git_manager
    
    with TestClient(app) as client:
        yield client


@pytest.fixture
def test_project(client):
    """Create a test project."""
    response = client.post(
        "/projects",
        json={"key": "TEST001", "name": "Test Project"}
    )
    assert response.status_code == 201
    return response.json()


class TestGovernanceMetadataAPI:
    """Test governance metadata API endpoints."""

    def test_create_governance_metadata(self, client, test_project):
        """Test creating governance metadata via API."""
        metadata = {
            "objectives": ["Objective 1", "Objective 2"],
            "scope": "Test project scope",
            "stakeholders": [
                {"name": "John Doe", "role": "PM", "responsibilities": "Delivery"}
            ],
            "decision_rights": {"architecture": "Tech Lead"},
            "stage_gates": [{"name": "Gate 1", "status": "pending"}],
            "approvals": [{"type": "budget", "approver": "CFO"}],
            "created_by": "test_user"
        }

        response = client.post(
            "/projects/TEST001/governance/metadata",
            json=metadata
        )

        assert response.status_code == 201
        data = response.json()
        assert data["objectives"] == ["Objective 1", "Objective 2"]
        assert data["scope"] == "Test project scope"
        assert data["created_by"] == "test_user"
        assert "created_at" in data
        assert "updated_at" in data

    def test_get_governance_metadata(self, client, test_project):
        """Test retrieving governance metadata via API."""
        # Create metadata first
        metadata = {
            "objectives": ["Test Objective"],
            "scope": "Test scope",
            "created_by": "test_user"
        }
        client.post("/projects/TEST001/governance/metadata", json=metadata)

        # Retrieve metadata
        response = client.get("/projects/TEST001/governance/metadata")

        assert response.status_code == 200
        data = response.json()
        assert data["objectives"] == ["Test Objective"]
        assert data["scope"] == "Test scope"

    def test_update_governance_metadata(self, client, test_project):
        """Test updating governance metadata via API."""
        # Create initial metadata
        metadata = {
            "objectives": ["Initial Objective"],
            "scope": "Initial scope",
            "created_by": "test_user"
        }
        client.post("/projects/TEST001/governance/metadata", json=metadata)

        # Update metadata
        updates = {
            "objectives": ["Updated Objective"],
            "scope": "Updated scope",
            "updated_by": "another_user"
        }
        response = client.put(
            "/projects/TEST001/governance/metadata",
            json=updates
        )

        assert response.status_code == 200
        data = response.json()
        assert data["objectives"] == ["Updated Objective"]
        assert data["scope"] == "Updated scope"
        assert data["updated_by"] == "another_user"

    def test_create_duplicate_metadata_fails(self, client, test_project):
        """Test that creating duplicate metadata returns 409."""
        metadata = {"objectives": ["Test"], "created_by": "test_user"}
        
        # Create first time - should succeed
        response1 = client.post("/projects/TEST001/governance/metadata", json=metadata)
        assert response1.status_code == 201

        # Create second time - should fail
        response2 = client.post("/projects/TEST001/governance/metadata", json=metadata)
        assert response2.status_code == 409

    def test_get_nonexistent_metadata_returns_404(self, client, test_project):
        """Test that getting nonexistent metadata returns 404."""
        response = client.get("/projects/TEST001/governance/metadata")
        assert response.status_code == 404


class TestDecisionLogAPI:
    """Test decision log API endpoints."""

    def test_create_decision(self, client, test_project):
        """Test creating a decision via API."""
        decision = {
            "title": "Test Decision",
            "description": "Test decision description",
            "decision_maker": "CTO",
            "rationale": "Test rationale",
            "impact": "Test impact",
            "status": "approved",
            "created_by": "test_user"
        }

        response = client.post(
            "/projects/TEST001/governance/decisions",
            json=decision
        )

        assert response.status_code == 201
        data = response.json()
        assert data["title"] == "Test Decision"
        assert data["decision_maker"] == "CTO"
        assert "id" in data
        assert "created_at" in data

    def test_list_decisions(self, client, test_project):
        """Test listing all decisions via API."""
        # Create multiple decisions
        for i in range(3):
            decision = {
                "title": f"Decision {i}",
                "description": f"Description {i}",
                "decision_maker": "CTO",
                "created_by": "test_user"
            }
            client.post("/projects/TEST001/governance/decisions", json=decision)

        # List all decisions
        response = client.get("/projects/TEST001/governance/decisions")

        assert response.status_code == 200
        data = response.json()
        assert len(data) == 3
        assert data[0]["title"] == "Decision 0"

    def test_get_decision_by_id(self, client, test_project):
        """Test retrieving a specific decision via API."""
        # Create a decision
        decision = {
            "title": "Specific Decision",
            "description": "Test description",
            "decision_maker": "CTO",
            "created_by": "test_user"
        }
        create_response = client.post(
            "/projects/TEST001/governance/decisions",
            json=decision
        )
        decision_id = create_response.json()["id"]

        # Retrieve by ID
        response = client.get(f"/projects/TEST001/governance/decisions/{decision_id}")

        assert response.status_code == 200
        data = response.json()
        assert data["id"] == decision_id
        assert data["title"] == "Specific Decision"

    def test_get_nonexistent_decision_returns_404(self, client, test_project):
        """Test that getting nonexistent decision returns 404."""
        response = client.get("/projects/TEST001/governance/decisions/nonexistent-id")
        assert response.status_code == 404


class TestGovernanceTraceability:
    """Test governance traceability API endpoints."""

    def test_link_decision_to_raid(self, client, test_project):
        """Test linking a decision to a RAID item via API."""
        # Create a decision
        decision = {
            "title": "Test Decision",
            "description": "Test",
            "decision_maker": "CTO",
            "created_by": "test_user"
        }
        decision_response = client.post(
            "/projects/TEST001/governance/decisions",
            json=decision
        )
        decision_id = decision_response.json()["id"]

        # Link to a RAID item
        raid_id = "test-raid-id"
        response = client.post(
            f"/projects/TEST001/governance/decisions/{decision_id}/link-raid/{raid_id}"
        )

        assert response.status_code == 200
        assert response.json()["message"] == "Decision linked to RAID item successfully"

        # Verify the link
        decision_response = client.get(
            f"/projects/TEST001/governance/decisions/{decision_id}"
        )
        assert raid_id in decision_response.json()["linked_raid_ids"]


class TestGovernanceErrorHandling:
    """Test error handling in governance API."""

    def test_nonexistent_project_returns_404(self, client):
        """Test that operations on nonexistent project return 404."""
        response = client.get("/projects/NONEXISTENT/governance/metadata")
        assert response.status_code == 404

    def test_invalid_project_key_in_decision_creation(self, client):
        """Test that creating decision for nonexistent project fails."""
        decision = {
            "title": "Test",
            "description": "Test",
            "decision_maker": "CTO",
            "created_by": "test_user"
        }
        response = client.post(
            "/projects/NONEXISTENT/governance/decisions",
            json=decision
        )
        assert response.status_code == 404
