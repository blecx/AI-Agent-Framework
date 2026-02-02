"""
Integration tests for TemplateService.

Tests full CRUD workflow with real GitManager and temporary file system.
"""

import pytest
import json
import tempfile
import shutil
import sys
import os

# Add apps/api to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../../../apps/api"))

from domain.templates.models import TemplateCreate, TemplateUpdate
from services.template_service import TemplateService
from services.git_manager import GitManager


@pytest.fixture
def temp_project_docs():
    """Create temporary projectDocs directory."""
    temp_dir = tempfile.mkdtemp()
    yield temp_dir
    shutil.rmtree(temp_dir)


@pytest.fixture
def git_manager(temp_project_docs):
    """Create GitManager with temporary storage."""
    manager = GitManager(base_path=temp_project_docs)
    manager.ensure_repository()
    return manager


@pytest.fixture
def template_service(git_manager):
    """Create TemplateService instance."""
    return TemplateService(git_manager=git_manager, project_key="test-project")


@pytest.fixture
def sample_template_create():
    """Sample template creation data."""
    return TemplateCreate(
        name="PMP Template",
        description="Project Management Plan template",
        schema={
            "type": "object",
            "properties": {
                "title": {"type": "string"},
                "version": {"type": "string"},
            },
            "required": ["title"],
        },
        markdown_template="# {{title}}\n\nVersion: {{version}}",
        artifact_type="pmp",
        version="1.0.0",
    )


class TestTemplateServiceCreate:
    """Test template creation."""

    def test_create_template_success(self, template_service, sample_template_create):
        """Test successful template creation."""
        template = template_service.create_template(sample_template_create)

        assert template.id.startswith("tpl-")
        assert template.name == "PMP Template"
        assert template.description == "Project Management Plan template"
        assert template.artifact_type == "pmp"
        assert template.version == "1.0.0"
        assert "title" in template.schema["properties"]

    def test_create_template_persists_to_storage(
        self, template_service, sample_template_create, git_manager
    ):
        """Test template is persisted to .templates/ directory."""
        template = template_service.create_template(sample_template_create)

        # Verify file exists
        template_path = (
            git_manager.get_project_path("test-project")
            / ".templates"
            / f"{template.id}.json"
        )
        assert template_path.exists()

        # Verify content
        content = json.loads(template_path.read_text())
        assert content["id"] == template.id
        assert content["name"] == "PMP Template"
        assert content["artifact_type"] == "pmp"

    def test_create_template_commits_to_git(
        self, template_service, sample_template_create, git_manager
    ):
        """Test template creation commits to git."""
        _ = template_service.create_template(sample_template_create)

        # Check git log
        commits = list(git_manager.repo.iter_commits(max_count=1))
        assert len(commits) > 0
        assert "[TEMPLATE] Create template:" in commits[0].message
        assert "PMP Template" in commits[0].message

    def test_create_template_invalid_artifact_type(self, template_service):
        """Test creating template with invalid artifact_type raises error."""
        invalid_template = TemplateCreate(
            name="Invalid Template",
            description="Should fail",
            schema={"type": "object"},
            markdown_template="# Test",
            artifact_type="invalid_type",
        )

        with pytest.raises(ValueError, match="Invalid artifact_type:"):
            # Expect ValueError from domain model validation
            template_service.create_template(invalid_template)

    def test_create_template_invalid_schema(self, template_service):
        """Test creating template with invalid schema raises error."""
        invalid_template = TemplateCreate(
            name="Invalid Schema",
            description="Missing type field",
            schema={"properties": {}},  # Missing 'type' field
            markdown_template="# Test",
            artifact_type="pmp",
        )

        with pytest.raises(ValueError, match="Invalid schema:"):
            template_service.create_template(invalid_template)


class TestTemplateServiceGet:
    """Test template retrieval."""

    def test_get_template_exists(self, template_service, sample_template_create):
        """Test retrieving existing template."""
        created = template_service.create_template(sample_template_create)
        retrieved = template_service.get_template(created.id)

        assert retrieved is not None
        assert retrieved.id == created.id
        assert retrieved.name == created.name
        assert retrieved.artifact_type == created.artifact_type

    def test_get_template_not_found(self, template_service):
        """Test retrieving non-existent template returns None."""
        result = template_service.get_template("non-existent-id")
        assert result is None


class TestTemplateServiceList:
    """Test template listing."""

    def test_list_templates_empty(self, template_service):
        """Test listing templates when none exist."""
        templates = template_service.list_templates()
        assert templates == []

    def test_list_templates_multiple(self, template_service):
        """Test listing multiple templates."""
        # Create multiple templates
        template1 = TemplateCreate(
            name="PMP Template",
            description="Test 1",
            schema={"type": "object"},
            markdown_template="# PMP",
            artifact_type="pmp",
        )
        template2 = TemplateCreate(
            name="RAID Template",
            description="Test 2",
            schema={"type": "object"},
            markdown_template="# RAID",
            artifact_type="raid",
        )
        template3 = TemplateCreate(
            name="Blueprint Template",
            description="Test 3",
            schema={"type": "object"},
            markdown_template="# Blueprint",
            artifact_type="blueprint",
        )

        created1 = template_service.create_template(template1)
        created2 = template_service.create_template(template2)
        created3 = template_service.create_template(template3)

        templates = template_service.list_templates()
        assert len(templates) == 3

        template_ids = [t.id for t in templates]
        assert created1.id in template_ids
        assert created2.id in template_ids
        assert created3.id in template_ids

    def test_list_templates_filtered_by_artifact_type(self, template_service):
        """Test listing templates filtered by artifact type."""
        # Create templates with different artifact types
        pmp_template = TemplateCreate(
            name="PMP Template",
            description="PMP",
            schema={"type": "object"},
            markdown_template="# PMP",
            artifact_type="pmp",
        )
        raid_template = TemplateCreate(
            name="RAID Template",
            description="RAID",
            schema={"type": "object"},
            markdown_template="# RAID",
            artifact_type="raid",
        )

        created_pmp = template_service.create_template(pmp_template)
        template_service.create_template(raid_template)

        # Filter by pmp
        pmp_templates = template_service.list_templates(artifact_type="pmp")
        assert len(pmp_templates) == 1
        assert pmp_templates[0].id == created_pmp.id
        assert pmp_templates[0].artifact_type == "pmp"

        # Filter by raid
        raid_templates = template_service.list_templates(artifact_type="raid")
        assert len(raid_templates) == 1
        assert raid_templates[0].artifact_type == "raid"


class TestTemplateServiceUpdate:
    """Test template updates."""

    def test_update_template_success(self, template_service, sample_template_create):
        """Test updating template fields."""
        created = template_service.create_template(sample_template_create)

        # Update template
        update_data = TemplateUpdate(
            name="Updated PMP Template",
            description="Updated description",
        )
        updated = template_service.update_template(created.id, update_data)

        assert updated is not None
        assert updated.id == created.id
        assert updated.name == "Updated PMP Template"
        assert updated.description == "Updated description"
        assert updated.artifact_type == "pmp"  # Unchanged

    def test_update_template_partial(self, template_service, sample_template_create):
        """Test partial update (only some fields)."""
        created = template_service.create_template(sample_template_create)

        # Update only name
        update_data = TemplateUpdate(name="Only Name Updated")
        updated = template_service.update_template(created.id, update_data)

        assert updated.name == "Only Name Updated"
        assert updated.description == created.description  # Unchanged

    def test_update_template_not_found(self, template_service):
        """Test updating non-existent template returns None."""
        update_data = TemplateUpdate(name="Updated")
        result = template_service.update_template("non-existent-id", update_data)
        assert result is None

    def test_update_template_commits_to_git(
        self, template_service, sample_template_create, git_manager
    ):
        """Test template update commits to git."""
        created = template_service.create_template(sample_template_create)
        update_data = TemplateUpdate(name="Updated Name")
        template_service.update_template(created.id, update_data)

        # Check git log
        commits = list(git_manager.repo.iter_commits(max_count=1))
        assert "[TEMPLATE] Update template:" in commits[0].message
        assert "Updated Name" in commits[0].message


class TestTemplateServiceDelete:
    """Test template deletion."""

    def test_delete_template_success(self, template_service, sample_template_create):
        """Test deleting existing template."""
        created = template_service.create_template(sample_template_create)

        result = template_service.delete_template(created.id)
        assert result is True

        # Verify template no longer retrievable
        retrieved = template_service.get_template(created.id)
        assert retrieved is None

    def test_delete_template_not_found(self, template_service):
        """Test deleting non-existent template returns False."""
        result = template_service.delete_template("non-existent-id")
        assert result is False

    def test_delete_template_removes_file(
        self, template_service, sample_template_create, git_manager
    ):
        """Test deletion removes file from storage."""
        created = template_service.create_template(sample_template_create)
        template_path = (
            git_manager.get_project_path("test-project")
            / ".templates"
            / f"{created.id}.json"
        )

        # Verify file exists before delete
        assert template_path.exists()

        template_service.delete_template(created.id)

        # Verify file removed
        assert not template_path.exists()

    def test_delete_template_commits_to_git(
        self, template_service, sample_template_create, git_manager
    ):
        """Test template deletion commits to git."""
        created = template_service.create_template(sample_template_create)
        template_service.delete_template(created.id)

        # Check git log
        commits = list(git_manager.repo.iter_commits(max_count=1))
        assert "[TEMPLATE] Delete template:" in commits[0].message
        assert created.name in commits[0].message


class TestTemplateServiceEndToEnd:
    """End-to-end workflow tests."""

    def test_full_crud_workflow(self, template_service, sample_template_create):
        """Test complete CRUD workflow: create → read → update → delete."""
        # Create
        created = template_service.create_template(sample_template_create)
        assert created.id.startswith("tpl-")

        # Read
        retrieved = template_service.get_template(created.id)
        assert retrieved.name == "PMP Template"

        # List
        all_templates = template_service.list_templates()
        assert len(all_templates) == 1

        # Update
        update_data = TemplateUpdate(name="Modified PMP")
        updated = template_service.update_template(created.id, update_data)
        assert updated.name == "Modified PMP"

        # Delete
        deleted = template_service.delete_template(created.id)
        assert deleted is True

        # Verify deleted
        not_found = template_service.get_template(created.id)
        assert not_found is None

        all_templates = template_service.list_templates()
        assert len(all_templates) == 0
