"""Integration tests for projects API optional description support."""

import os
import shutil
import tempfile
import sys

import pytest
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.testclient import TestClient

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
    os.environ["PROJECT_DOCS_PATH"] = temp_project_dir

    test_app = FastAPI(title="Test Projects App")
    test_app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    from routers import projects
    from services.git_manager import GitManager

    test_app.include_router(projects.router, prefix="/projects", tags=["projects"])

    git_manager = GitManager(temp_project_dir)
    git_manager.ensure_repository()
    test_app.state.git_manager = git_manager

    with TestClient(test_app) as test_client:
        yield test_client


class TestProjectsDescriptionAPI:
    """Project API tests covering optional description create/read behavior."""

    def test_create_project_without_description_remains_compatible(self, client):
        """Project creation without description should remain supported."""
        response = client.post(
            "/projects",
            json={"key": "TEST001", "name": "Compatibility Project"},
        )

        assert response.status_code == 201
        payload = response.json()
        assert payload["key"] == "TEST001"
        assert payload["name"] == "Compatibility Project"
        assert payload["description"] is None

    def test_create_and_read_project_with_description(self, client):
        """Project description should persist and be returned by read endpoints."""
        create_response = client.post(
            "/projects",
            json={
                "key": "TEST002",
                "name": "Described Project",
                "description": "A richer project context",
            },
        )

        assert create_response.status_code == 201
        created = create_response.json()
        assert created["description"] == "A richer project context"

        get_response = client.get("/projects/TEST002")
        assert get_response.status_code == 200
        assert get_response.json()["description"] == "A richer project context"

        list_response = client.get("/projects")
        assert list_response.status_code == 200
        listed = list_response.json()
        listed_project = next(
            (item for item in listed if item["key"] == "TEST002"), None
        )
        assert listed_project is not None
        assert listed_project["description"] == "A richer project context"

        state_response = client.get("/projects/TEST002/state")
        assert state_response.status_code == 200
        assert (
            state_response.json()["project_info"]["description"]
            == "A richer project context"
        )

    def test_update_project_description(self, client):
        """Project update should support optional description field."""
        create_response = client.post(
            "/projects",
            json={"key": "TEST003", "name": "Update Description Project"},
        )
        assert create_response.status_code == 201

        update_response = client.put(
            "/projects/TEST003",
            json={"description": "Set after creation"},
        )
        assert update_response.status_code == 200
        assert update_response.json()["description"] == "Set after creation"

        get_response = client.get("/projects/TEST003")
        assert get_response.status_code == 200
        assert get_response.json()["description"] == "Set after creation"
