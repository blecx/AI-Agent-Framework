"""
Integration tests for RAID API endpoints.
"""
import pytest
from fastapi.testclient import TestClient
import tempfile
import shutil
import sys
import os

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
    from routers import projects, commands, artifacts, governance, raid
    test_app.include_router(projects.router, prefix="/projects", tags=["projects"])
    test_app.include_router(commands.router, prefix="/projects/{project_key}/commands", tags=["commands"])
    test_app.include_router(artifacts.router, prefix="/projects/{project_key}/artifacts", tags=["artifacts"])
    test_app.include_router(governance.router, prefix="/projects/{project_key}/governance", tags=["governance"])
    test_app.include_router(raid.router, prefix="/projects/{project_key}/raid", tags=["raid"])
    
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
    response = client.post(
        "/projects",
        json={"key": "TEST001", "name": "Test Project"}
    )
    assert response.status_code == 201
    return response.json()


class TestRAIDItemCRUDAPI:
    """Test RAID item CRUD API endpoints."""

    def test_create_raid_item(self, client, test_project):
        """Test creating a RAID item via API."""
        item = {
            "type": "risk",
            "title": "Test Risk",
            "description": "Test risk description",
            "owner": "John Doe",
            "priority": "high",
            "impact": "high",
            "likelihood": "possible",
            "mitigation_plan": "Test mitigation",
            "next_actions": ["Action 1", "Action 2"],
            "created_by": "test_user"
        }

        response = client.post("/projects/TEST001/raid", json=item)

        assert response.status_code == 201
        data = response.json()
        assert data["type"] == "risk"
        assert data["title"] == "Test Risk"
        assert data["owner"] == "John Doe"
        assert "id" in data
        assert "created_at" in data

    def test_list_raid_items(self, client, test_project):
        """Test listing all RAID items via API."""
        # Create multiple items
        for i in range(3):
            item = {
                "type": "risk" if i % 2 == 0 else "issue",
                "title": f"Item {i}",
                "description": f"Description {i}",
                "owner": "Test Owner",
                "created_by": "test_user"
            }
            client.post("/projects/TEST001/raid", json=item)

        # List all items
        response = client.get("/projects/TEST001/raid")

        assert response.status_code == 200
        data = response.json()
        assert data["total"] == 3
        assert len(data["items"]) == 3

    def test_get_raid_item_by_id(self, client, test_project):
        """Test retrieving a specific RAID item via API."""
        # Create an item
        item = {
            "type": "issue",
            "title": "Specific Issue",
            "description": "Test description",
            "owner": "Test Owner",
            "created_by": "test_user"
        }
        create_response = client.post("/projects/TEST001/raid", json=item)
        item_id = create_response.json()["id"]

        # Retrieve by ID
        response = client.get(f"/projects/TEST001/raid/{item_id}")

        assert response.status_code == 200
        data = response.json()
        assert data["id"] == item_id
        assert data["title"] == "Specific Issue"

    def test_update_raid_item(self, client, test_project):
        """Test updating a RAID item via API."""
        # Create an item
        item = {
            "type": "risk",
            "title": "Original Title",
            "description": "Original description",
            "owner": "Original Owner",
            "created_by": "test_user"
        }
        create_response = client.post("/projects/TEST001/raid", json=item)
        item_id = create_response.json()["id"]

        # Update the item
        updates = {
            "title": "Updated Title",
            "status": "in_progress",
            "next_actions": ["New Action"],
            "updated_by": "another_user"
        }
        response = client.put(f"/projects/TEST001/raid/{item_id}", json=updates)

        assert response.status_code == 200
        data = response.json()
        assert data["title"] == "Updated Title"
        assert data["status"] == "in_progress"
        assert data["updated_by"] == "another_user"

    def test_delete_raid_item(self, client, test_project):
        """Test deleting a RAID item via API."""
        # Create an item
        item = {
            "type": "issue",
            "title": "To Be Deleted",
            "description": "Test description",
            "owner": "Test Owner",
            "created_by": "test_user"
        }
        create_response = client.post("/projects/TEST001/raid", json=item)
        item_id = create_response.json()["id"]

        # Delete the item
        response = client.delete(f"/projects/TEST001/raid/{item_id}")

        assert response.status_code == 200
        assert response.json()["message"] == "RAID item deleted successfully"

        # Verify it's gone
        get_response = client.get(f"/projects/TEST001/raid/{item_id}")
        assert get_response.status_code == 404


class TestRAIDItemFilteringAPI:
    """Test RAID item filtering API."""

    def test_filter_by_type(self, client):
        """Test filtering RAID items by type via API."""
        # Create a fresh project for this test
        client.post("/projects", json={"key": "FILT001", "name": "Filter Test 1"})
        
        # Create test data
        client.post("/projects/FILT001/raid", json={
            "type": "risk", "title": "Risk 1", "description": "Risk 1",
            "owner": "Alice", "created_by": "test_user"
        })
        client.post("/projects/FILT001/raid", json={
            "type": "issue", "title": "Issue 1", "description": "Issue 1",
            "owner": "Bob", "created_by": "test_user"
        })
        client.post("/projects/FILT001/raid", json={
            "type": "risk", "title": "Risk 2", "description": "Risk 2",
            "owner": "Alice", "created_by": "test_user"
        })
        
        response = client.get("/projects/FILT001/raid?type=risk")

        assert response.status_code == 200
        data = response.json()
        assert data["total"] == 2
        assert all(item["type"] == "risk" for item in data["items"])

    def test_filter_by_status(self, client):
        """Test filtering RAID items by status via API."""
        # Create a fresh project for this test
        client.post("/projects", json={"key": "FILT002", "name": "Filter Test 2"})
        
        # Create test data with different statuses
        client.post("/projects/FILT002/raid", json={
            "type": "risk", "title": "Risk 1", "description": "Risk 1",
            "owner": "Alice", "status": "open", "created_by": "test_user"
        })
        client.post("/projects/FILT002/raid", json={
            "type": "issue", "title": "Issue 1", "description": "Issue 1",
            "owner": "Bob", "status": "in_progress", "created_by": "test_user"
        })
        client.post("/projects/FILT002/raid", json={
            "type": "risk", "title": "Risk 2", "description": "Risk 2",
            "owner": "Alice", "status": "closed", "created_by": "test_user"
        })
        
        response = client.get("/projects/FILT002/raid?status=open")

        assert response.status_code == 200
        data = response.json()
        assert data["total"] == 1
        assert all(item["status"] == "open" for item in data["items"])

    def test_filter_by_owner(self, client):
        """Test filtering RAID items by owner via API."""
        # Create a fresh project for this test
        client.post("/projects", json={"key": "FILT003", "name": "Filter Test 3"})
        
        # Create test data
        client.post("/projects/FILT003/raid", json={
            "type": "risk", "title": "Risk 1", "description": "Risk 1",
            "owner": "Alice", "created_by": "test_user"
        })
        client.post("/projects/FILT003/raid", json={
            "type": "issue", "title": "Issue 1", "description": "Issue 1",
            "owner": "Bob", "created_by": "test_user"
        })
        client.post("/projects/FILT003/raid", json={
            "type": "risk", "title": "Risk 2", "description": "Risk 2",
            "owner": "Alice", "created_by": "test_user"
        })
        
        response = client.get("/projects/FILT003/raid?owner=Alice")

        assert response.status_code == 200
        data = response.json()
        assert data["total"] == 2
        assert all(item["owner"] == "Alice" for item in data["items"])

    def test_filter_by_priority(self, client):
        """Test filtering RAID items by priority via API."""
        # Create a fresh project for this test
        client.post("/projects", json={"key": "FILT004", "name": "Filter Test 4"})
        
        # Create test data with different priorities
        client.post("/projects/FILT004/raid", json={
            "type": "risk", "title": "Risk 1", "description": "Risk 1",
            "owner": "Alice", "priority": "high", "created_by": "test_user"
        })
        client.post("/projects/FILT004/raid", json={
            "type": "issue", "title": "Issue 1", "description": "Issue 1",
            "owner": "Bob", "priority": "medium", "created_by": "test_user"
        })
        
        response = client.get("/projects/FILT004/raid?priority=high")

        assert response.status_code == 200
        data = response.json()
        assert data["total"] == 1
        assert data["items"][0]["priority"] == "high"

    def test_filter_multiple_criteria(self, client):
        """Test filtering with multiple criteria via API."""
        # Create a fresh project for this test
        client.post("/projects", json={"key": "FILT005", "name": "Filter Test 5"})
        
        # Create test data
        client.post("/projects/FILT005/raid", json={
            "type": "risk", "title": "Risk 1", "description": "Risk 1",
            "owner": "Alice", "status": "open", "created_by": "test_user"
        })
        client.post("/projects/FILT005/raid", json={
            "type": "risk", "title": "Risk 2", "description": "Risk 2",
            "owner": "Alice", "status": "closed", "created_by": "test_user"
        })
        client.post("/projects/FILT005/raid", json={
            "type": "issue", "title": "Issue 1", "description": "Issue 1",
            "owner": "Bob", "status": "open", "created_by": "test_user"
        })
        
        response = client.get("/projects/FILT005/raid?type=risk&owner=Alice&status=open")

        assert response.status_code == 200
        data = response.json()
        assert data["total"] == 1
        item = data["items"][0]
        assert item["type"] == "risk"
        assert item["owner"] == "Alice"
        assert item["status"] == "open"


class TestRAIDTraceabilityAPI:
    """Test RAID traceability API endpoints."""

    def test_link_raid_to_decision(self, client, test_project):
        """Test linking a RAID item to a decision via API."""
        # Create a RAID item
        item = {
            "type": "risk",
            "title": "Test Risk",
            "description": "Test description",
            "owner": "Test Owner",
            "created_by": "test_user"
        }
        raid_response = client.post("/projects/TEST001/raid", json=item)
        raid_id = raid_response.json()["id"]

        # Link to a decision
        decision_id = "test-decision-id"
        response = client.post(
            f"/projects/TEST001/raid/{raid_id}/link-decision/{decision_id}"
        )

        assert response.status_code == 200
        assert response.json()["message"] == "RAID item linked to decision successfully"

        # Verify the link
        raid_response = client.get(f"/projects/TEST001/raid/{raid_id}")
        assert decision_id in raid_response.json()["linked_decisions"]

    def test_get_raid_items_by_decision(self, client, test_project):
        """Test retrieving RAID items linked to a decision via API."""
        decision_id = "test-decision-id"

        # Create RAID items with links
        for i in range(3):
            item = {
                "type": "risk",
                "title": f"Risk {i}",
                "description": f"Description {i}",
                "owner": "Test Owner",
                "created_by": "test_user"
            }
            if i < 2:  # Link first two items
                item["linked_decisions"] = [decision_id]

            client.post("/projects/TEST001/raid", json=item)

        # Get items by decision
        response = client.get(f"/projects/TEST001/raid/by-decision/{decision_id}")

        assert response.status_code == 200
        data = response.json()
        assert data["total"] == 2
        assert all(decision_id in item["linked_decisions"] for item in data["items"])


class TestRAIDErrorHandling:
    """Test error handling in RAID API."""

    def test_nonexistent_project_returns_404(self, client):
        """Test that operations on nonexistent project return 404."""
        response = client.get("/projects/NONEXISTENT/raid")
        assert response.status_code == 404

    def test_get_nonexistent_raid_item_returns_404(self, client, test_project):
        """Test that getting nonexistent RAID item returns 404."""
        response = client.get("/projects/TEST001/raid/nonexistent-id")
        assert response.status_code == 404

    def test_update_nonexistent_raid_item_returns_404(self, client, test_project):
        """Test that updating nonexistent RAID item returns 404."""
        updates = {"status": "in_progress", "updated_by": "test_user"}
        response = client.put("/projects/TEST001/raid/nonexistent-id", json=updates)
        assert response.status_code == 404

    def test_delete_nonexistent_raid_item_returns_404(self, client, test_project):
        """Test that deleting nonexistent RAID item returns 404."""
        response = client.delete("/projects/TEST001/raid/nonexistent-id")
        assert response.status_code == 404


class TestRAIDValidation:
    """Test request validation in RAID API."""

    def test_create_raid_item_missing_required_fields(self, client, test_project):
        """Test that creating RAID item without required fields fails."""
        item = {
            "type": "risk",
            # Missing title, description, owner
        }
        response = client.post("/projects/TEST001/raid", json=item)
        assert response.status_code == 422  # Unprocessable Entity

    def test_create_raid_item_invalid_type(self, client, test_project):
        """Test that creating RAID item with invalid type fails."""
        item = {
            "type": "invalid_type",
            "title": "Test",
            "description": "Test",
            "owner": "Test Owner"
        }
        response = client.post("/projects/TEST001/raid", json=item)
        assert response.status_code == 422
