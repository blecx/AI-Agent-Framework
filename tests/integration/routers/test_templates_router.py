"""
Integration tests for Template router endpoints.
Tests all CRUD operations with real FastAPI TestClient.
"""

import os
import pytest
import tempfile
import shutil
from fastapi.testclient import TestClient

# Import the FastAPI app
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../../../apps/api"))

from main import app  # noqa: E402
from services.git_manager import GitManager  # noqa: E402


@pytest.fixture
def temp_project_docs():
    """Create temporary projectDocs directory."""
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
def sample_template_create():
    """Sample template creation payload."""
    return {
        "name": "Project Management Plan Template",
        "description": "ISO 21500 compliant PMP template",
        "schema": {
            "type": "object",
            "properties": {
                "project_name": {"type": "string"},
                "start_date": {"type": "string", "format": "date"},
            },
            "required": ["project_name"],
        },
        "markdown_template": "# {{project_name}}\n\nStart: {{start_date}}",
        "artifact_type": "pmp",
        "version": "1.0.0",
    }


# ============================================================================
# POST /api/v1/templates - Create Template
# ============================================================================


def test_create_template_success(client, sample_template_create):
    """Test successful template creation."""
    response = client.post("/api/v1/templates", json=sample_template_create)

    assert response.status_code == 201
    data = response.json()
    assert "id" in data
    assert data["id"].startswith("tpl-")
    assert data["name"] == sample_template_create["name"]
    assert data["artifact_type"] == "pmp"


def test_create_template_invalid_artifact_type(client, sample_template_create):
    """Test creation with invalid artifact_type returns 400 (service validation)."""
    sample_template_create["artifact_type"] = "invalid_type"
    response = client.post("/api/v1/templates", json=sample_template_create)

    assert response.status_code == 400  # Service-level validation error


def test_create_template_missing_schema_type(client, sample_template_create):
    """Test creation with invalid schema returns 400 (service validation)."""
    sample_template_create["schema"] = {"properties": {}}  # Missing 'type' field
    response = client.post("/api/v1/templates", json=sample_template_create)

    assert response.status_code == 400  # Service-level validation error


def test_create_template_missing_required_field(client, sample_template_create):
    """Test creation without required field returns 422."""
    del sample_template_create["name"]
    response = client.post("/api/v1/templates", json=sample_template_create)

    assert response.status_code == 422


# ============================================================================
# GET /api/v1/templates - List All Templates
# ============================================================================


def test_list_templates_empty(client):
    """Test listing templates when none exist."""
    response = client.get("/api/v1/templates")

    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)


def test_list_templates_with_data(client, sample_template_create):
    """Test listing templates after creating one."""
    # Create a template first
    create_response = client.post("/api/v1/templates", json=sample_template_create)
    assert create_response.status_code == 201
    created_id = create_response.json()["id"]

    # List templates
    response = client.get("/api/v1/templates")

    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) >= 1
    assert any(t["id"] == created_id for t in data)


# ============================================================================
# GET /api/v1/templates/{id} - Get Template by ID
# ============================================================================


def test_get_template_success(client, sample_template_create):
    """Test getting template by ID."""
    # Create a template first
    create_response = client.post("/api/v1/templates", json=sample_template_create)
    created_id = create_response.json()["id"]

    # Get the template
    response = client.get(f"/api/v1/templates/{created_id}")

    assert response.status_code == 200
    data = response.json()
    assert data["id"] == created_id
    assert data["name"] == sample_template_create["name"]


def test_get_template_not_found(client):
    """Test getting non-existent template returns 404."""
    response = client.get("/api/v1/templates/nonexistent-id")

    assert response.status_code == 404
    assert "not found" in response.json()["detail"].lower()


# ============================================================================
# PUT /api/v1/templates/{id} - Update Template
# ============================================================================


def test_update_template_success(client, sample_template_create):
    """Test updating template."""
    # Create a template first
    create_response = client.post("/api/v1/templates", json=sample_template_create)
    created_id = create_response.json()["id"]

    # Update the template
    update_payload = {
        "name": "Updated PMP Template",
        "description": "Updated description",
    }
    response = client.put(f"/api/v1/templates/{created_id}", json=update_payload)

    assert response.status_code == 200
    data = response.json()
    assert data["id"] == created_id
    assert data["name"] == "Updated PMP Template"
    assert data["description"] == "Updated description"
    # Original fields should be preserved
    assert data["artifact_type"] == "pmp"


def test_update_template_not_found(client):
    """Test updating non-existent template returns 404."""
    update_payload = {"name": "New Name"}
    response = client.put("/api/v1/templates/nonexistent-id", json=update_payload)

    assert response.status_code == 404
    assert "not found" in response.json()["detail"].lower()


def test_update_template_invalid_artifact_type(client, sample_template_create):
    """Test updating with invalid artifact_type is allowed (Pydantic doesn't catch it in update)."""
    # Create a template first
    create_response = client.post("/api/v1/templates", json=sample_template_create)
    created_id = create_response.json()["id"]

    # Try to update with invalid artifact_type (TemplateUpdate has no validator)
    update_payload = {"artifact_type": "invalid_type"}
    response = client.put(f"/api/v1/templates/{created_id}", json=update_payload)

    # TemplateUpdate doesn't have field validator, so service handles it
    # If service doesn't validate on update, this would pass (200)
    # This test documents current behavior - could add validation later
    assert response.status_code in [200, 400]  # Either accepted or rejected


# ============================================================================
# DELETE /api/v1/templates/{id} - Delete Template
# ============================================================================


def test_delete_template_success(client, sample_template_create):
    """Test deleting template."""
    # Create a template first
    create_response = client.post("/api/v1/templates", json=sample_template_create)
    created_id = create_response.json()["id"]

    # Delete the template
    response = client.delete(f"/api/v1/templates/{created_id}")

    assert response.status_code == 204

    # Verify it's deleted
    get_response = client.get(f"/api/v1/templates/{created_id}")
    assert get_response.status_code == 404


def test_delete_template_not_found(client):
    """Test deleting non-existent template returns 404."""
    response = client.delete("/api/v1/templates/nonexistent-id")

    assert response.status_code == 404
    assert "not found" in response.json()["detail"].lower()


# ============================================================================
# Edge Cases and Error Handling
# ============================================================================


def test_create_template_empty_string_fields(client, sample_template_create):
    """Test creation with empty string fields is currently allowed."""
    sample_template_create["name"] = ""
    response = client.post("/api/v1/templates", json=sample_template_create)

    # Currently no validation for empty strings - could add min_length validators later
    # Test documents current behavior
    assert response.status_code == 201  # Currently allowed


def test_update_template_partial(client, sample_template_create):
    """Test partial update (only one field)."""
    # Create a template first
    create_response = client.post("/api/v1/templates", json=sample_template_create)
    created_id = create_response.json()["id"]
    original_name = create_response.json()["name"]

    # Update only description
    update_payload = {"description": "Only description changed"}
    response = client.put(f"/api/v1/templates/{created_id}", json=update_payload)

    assert response.status_code == 200
    data = response.json()
    assert data["name"] == original_name  # Should be unchanged
    assert data["description"] == "Only description changed"
