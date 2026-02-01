"""
Integration tests for Artifacts router endpoints.
Tests artifact generation from templates and blueprints.
"""

import os
import pytest
import tempfile
import shutil
from fastapi.testclient import TestClient

# Import the FastAPI app
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../../../apps/api"))

from main import app
from services.git_manager import GitManager


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
def test_project(client):
    """Create test project."""
    project_data = {"key": "TEST", "name": "Test Project"}
    response = client.post("/api/v1/projects", json=project_data)
    assert response.status_code == 201
    return project_data


@pytest.fixture
def test_template(client):
    """Create test template."""
    template_data = {
        "name": "Test Template",
        "description": "Simple test template",
        "schema": {
            "type": "object",
            "properties": {
                "title": {"type": "string"},
                "author": {"type": "string"},
            },
            "required": ["title"],
        },
        "markdown_template": "# {{title}}\n\nAuthor: {{author}}",
        "artifact_type": "report",  # Use allowed type
        "version": "1.0.0",
    }
    response = client.post("/api/v1/templates", json=template_data)
    if response.status_code != 201:
        print(f"Template creation failed: {response.status_code}")
        print(f"Response: {response.json()}")
    assert response.status_code == 201
    return response.json()


@pytest.fixture
def test_blueprint(client, test_template):
    """Create test blueprint."""
    blueprint_data = {
        "id": "bp-test",
        "name": "Test Blueprint",
        "description": "Simple test blueprint",
        "required_templates": [test_template["id"]],
        "version": "1.0.0",
    }
    response = client.post("/api/v1/blueprints", json=blueprint_data)
    if response.status_code != 201:
        print(f"Blueprint creation failed: {response.status_code}")
        print(f"Response: {response.json()}")
    assert response.status_code == 201
    return response.json()


# ============================================================================
# POST /artifacts/generate - Generate from Template
# ============================================================================


def test_generate_artifact_success(client, test_project, test_template):
    """Test successful artifact generation from template."""
    request_data = {
        "template_id": test_template["id"],
        "context": {"title": "My Document", "author": "Jane Doe"},
    }

    response = client.post(
        f"/api/v1/projects/{test_project['key']}/artifacts/generate",
        json=request_data,
    )

    assert response.status_code == 201
    data = response.json()
    assert "artifact_path" in data
    assert data["artifact_path"] == "artifacts/report.md"
    assert "content" in data
    assert "# My Document" in data["content"]
    assert "Author: Jane Doe" in data["content"]
    assert data["template_id"] == test_template["id"]
    assert data["artifact_type"] == "report"


def test_generate_artifact_missing_required_field(client, test_project, test_template):
    """Test artifact generation fails with missing required field."""
    request_data = {
        "template_id": test_template["id"],
        "context": {"author": "John Smith"},  # Missing 'title'
    }

    response = client.post(
        f"/api/v1/projects/{test_project['key']}/artifacts/generate",
        json=request_data,
    )

    assert response.status_code == 400
    assert "validation" in response.json()["detail"].lower()


def test_generate_artifact_template_not_found(client, test_project):
    """Test artifact generation with non-existent template."""
    request_data = {
        "template_id": "tpl-nonexistent",
        "context": {"title": "Test"},
    }

    response = client.post(
        f"/api/v1/projects/{test_project['key']}/artifacts/generate",
        json=request_data,
    )

    assert response.status_code == 404
    assert "not found" in response.json()["detail"].lower()


def test_generate_artifact_project_not_found(client, test_template):
    """Test artifact generation with non-existent project."""
    request_data = {
        "template_id": test_template["id"],
        "context": {"title": "Test"},
    }

    response = client.post(
        "/api/v1/projects/NONEXISTENT/artifacts/generate", json=request_data
    )

    assert response.status_code == 404
    assert "project" in response.json()["detail"].lower()


def test_generate_artifact_invalid_request_body(client, test_project):
    """Test artifact generation with invalid request body."""
    # Missing required fields
    request_data = {"context": {"title": "Test"}}

    response = client.post(
        f"/api/v1/projects/{test_project['key']}/artifacts/generate",
        json=request_data,
    )

    assert response.status_code == 422  # Pydantic validation error


# ============================================================================
# POST /artifacts/generate-from-blueprint - Generate from Blueprint
# ============================================================================


def test_generate_from_blueprint_success(client, test_project, test_blueprint):
    """Test successful artifact generation from blueprint."""
    request_data = {
        "blueprint_id": test_blueprint["id"],
        "context": {"title": "Blueprint Doc", "author": "Team Lead"},
    }

    response = client.post(
        f"/api/v1/projects/{test_project['key']}/artifacts/generate-from-blueprint",
        json=request_data,
    )

    assert response.status_code == 201
    data = response.json()
    assert data["blueprint_id"] == test_blueprint["id"]
    assert "generated_artifacts" in data
    assert len(data["generated_artifacts"]) > 0

    # Check first generated artifact
    artifact = data["generated_artifacts"][0]
    assert "artifact_path" in artifact
    assert "content" in artifact


def test_generate_from_blueprint_with_empty_context(
    client, test_project, test_blueprint
):
    """Test blueprint generation with empty context (optional context field)."""
    request_data = {"blueprint_id": test_blueprint["id"]}

    response = client.post(
        f"/api/v1/projects/{test_project['key']}/artifacts/generate-from-blueprint",
        json=request_data,
    )

    # Should succeed but may have validation errors in individual artifacts
    assert response.status_code == 201
    data = response.json()
    assert data["blueprint_id"] == test_blueprint["id"]
    assert "generated_artifacts" in data


def test_generate_from_blueprint_not_found(client, test_project):
    """Test blueprint generation with non-existent blueprint."""
    request_data = {
        "blueprint_id": "bp-nonexistent",
        "context": {"title": "Test"},
    }

    response = client.post(
        f"/api/v1/projects/{test_project['key']}/artifacts/generate-from-blueprint",
        json=request_data,
    )

    assert response.status_code == 404
    assert "not found" in response.json()["detail"].lower()


def test_generate_from_blueprint_project_not_found(client, test_blueprint):
    """Test blueprint generation with non-existent project."""
    request_data = {
        "blueprint_id": test_blueprint["id"],
        "context": {"title": "Test"},
    }

    response = client.post(
        "/api/v1/projects/NONEXISTENT/artifacts/generate-from-blueprint",
        json=request_data,
    )

    assert response.status_code == 404
    assert "project" in response.json()["detail"].lower()


def test_generate_from_blueprint_invalid_request_body(client, test_project):
    """Test blueprint generation with invalid request body."""
    # Missing required field
    request_data = {}

    response = client.post(
        f"/api/v1/projects/{test_project['key']}/artifacts/generate-from-blueprint",
        json=request_data,
    )

    assert response.status_code == 422  # Pydantic validation error
