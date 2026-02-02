"""Integration tests for Blueprints router."""

import pytest
from fastapi.testclient import TestClient
import tempfile
import shutil

from apps.api.main import app
from apps.api.services.git_manager import GitManager
from apps.api.domain.templates.models import TemplateCreate
from apps.api.services.template_service import TemplateService


@pytest.fixture
def temp_project_docs():
    """Create temporary project docs directory."""
    temp_dir = tempfile.mkdtemp()
    yield temp_dir
    shutil.rmtree(temp_dir)


@pytest.fixture
def client(temp_project_docs):
    """Create test client with initialized app state."""
    # Initialize git_manager in app state (mimics lifespan startup)
    git_manager = GitManager(base_path=temp_project_docs)
    git_manager.ensure_repository()
    app.state.git_manager = git_manager

    return TestClient(app)


@pytest.fixture
def template_service(temp_project_docs):
    """Create TemplateService for test setup."""
    git_manager = GitManager(base_path=temp_project_docs)
    git_manager.ensure_repository()
    return TemplateService(git_manager=git_manager, project_key="system")


class TestBlueprintsRouter:
    """Test Blueprints router endpoints."""

    def test_create_blueprint_success(self, client):
        """Test POST /api/v1/blueprints creates blueprint."""
        blueprint_data = {
            "id": "test-bp",
            "name": "Test Blueprint",
            "description": "A test blueprint",
            "required_templates": [],
            "optional_templates": [],
            "workflow_requirements": ["initiating"],
        }

        response = client.post("/api/v1/blueprints", json=blueprint_data)

        assert response.status_code == 201
        data = response.json()
        assert data["id"] == "test-bp"
        assert data["name"] == "Test Blueprint"

    def test_create_blueprint_duplicate_id(self, client):
        """Test creating blueprint with duplicate ID returns 400."""
        blueprint_data = {
            "id": "test-bp",
            "name": "Test Blueprint",
            "description": "First blueprint",
        }

        # Create first blueprint
        client.post("/api/v1/blueprints", json=blueprint_data)

        # Try to create duplicate
        duplicate_data = {
            "id": "test-bp",
            "name": "Duplicate",
            "description": "Should fail",
        }

        response = client.post("/api/v1/blueprints", json=duplicate_data)

        assert response.status_code == 400
        assert "already exists" in response.json()["detail"]

    def test_create_blueprint_invalid_template(self, client):
        """Test creating blueprint with non-existent template returns 400."""
        blueprint_data = {
            "id": "test-bp",
            "name": "Test Blueprint",
            "description": "Invalid template reference",
            "required_templates": ["non-existent-template"],
        }

        response = client.post("/api/v1/blueprints", json=blueprint_data)

        assert response.status_code == 400
        assert "does not exist" in response.json()["detail"]

    def test_list_blueprints_empty(self, client):
        """Test GET /api/v1/blueprints returns empty list."""
        response = client.get("/api/v1/blueprints")

        assert response.status_code == 200
        assert response.json() == []

    def test_list_blueprints_multiple(self, client):
        """Test listing multiple blueprints."""
        # Create multiple blueprints
        for i in range(3):
            blueprint_data = {
                "id": f"bp-{i}",
                "name": f"Blueprint {i}",
                "description": f"Blueprint number {i}",
            }
            client.post("/api/v1/blueprints", json=blueprint_data)

        response = client.get("/api/v1/blueprints")

        assert response.status_code == 200
        data = response.json()
        assert len(data) == 3

    def test_get_blueprint_success(self, client):
        """Test GET /api/v1/blueprints/{id} returns blueprint."""
        blueprint_data = {
            "id": "test-bp",
            "name": "Test Blueprint",
            "description": "A test blueprint",
        }
        client.post("/api/v1/blueprints", json=blueprint_data)

        response = client.get("/api/v1/blueprints/test-bp")

        assert response.status_code == 200
        data = response.json()
        assert data["id"] == "test-bp"

    def test_get_blueprint_not_found(self, client):
        """Test GET /api/v1/blueprints/{id} returns 404 for non-existent blueprint."""
        response = client.get("/api/v1/blueprints/non-existent")

        assert response.status_code == 404
        assert "not found" in response.json()["detail"]

    def test_update_blueprint_success(self, client):
        """Test PUT /api/v1/blueprints/{id} updates blueprint."""
        # Create blueprint
        blueprint_data = {
            "id": "test-bp",
            "name": "Original Name",
            "description": "Original description",
        }
        client.post("/api/v1/blueprints", json=blueprint_data)

        # Update it
        update_data = {"name": "Updated Name", "description": "Updated description"}

        response = client.put("/api/v1/blueprints/test-bp", json=update_data)

        assert response.status_code == 200
        data = response.json()
        assert data["name"] == "Updated Name"
        assert data["description"] == "Updated description"

    def test_update_blueprint_not_found(self, client):
        """Test PUT /api/v1/blueprints/{id} returns 404 for non-existent blueprint."""
        update_data = {"name": "New Name"}

        response = client.put("/api/v1/blueprints/non-existent", json=update_data)

        assert response.status_code == 404
        assert "not found" in response.json()["detail"]

    def test_delete_blueprint_success(self, client):
        """Test DELETE /api/v1/blueprints/{id} deletes blueprint."""
        # Create blueprint
        blueprint_data = {
            "id": "test-bp",
            "name": "Test Blueprint",
            "description": "To be deleted",
        }
        client.post("/api/v1/blueprints", json=blueprint_data)

        # Delete it
        response = client.delete("/api/v1/blueprints/test-bp")

        assert response.status_code == 204

        # Verify it's gone
        get_response = client.get("/api/v1/blueprints/test-bp")
        assert get_response.status_code == 404

    def test_delete_blueprint_not_found(self, client):
        """Test DELETE /api/v1/blueprints/{id} returns 404 for non-existent blueprint."""
        response = client.delete("/api/v1/blueprints/non-existent")

        assert response.status_code == 404
        assert "not found" in response.json()["detail"]

    def test_blueprint_with_valid_template_reference(self, client, template_service):
        """Test creating blueprint with valid template reference."""
        # Create a template first
        template_create = TemplateCreate(
            name="Test Template",
            description="A test template",
            schema={"type": "object"},
            markdown_template="# Test",
            artifact_type="pmp",
            version="1.0.0",
        )
        template = template_service.create_template(template_create)

        # Create blueprint with template reference
        blueprint_data = {
            "id": "test-bp",
            "name": "Test Blueprint",
            "description": "Blueprint with valid template",
            "required_templates": [template.id],
        }

        response = client.post("/api/v1/blueprints", json=blueprint_data)

        assert response.status_code == 201
        data = response.json()
        assert template.id in data["required_templates"]
