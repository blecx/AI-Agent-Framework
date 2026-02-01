"""Unit tests for test data factories."""

import pytest
import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from fixtures.factories import (
    ProjectFactory,
    ArtifactFactory,
    ProposalFactory,
    RAIDItemFactory,
    AuditResultFactory,
)


class TestProjectFactory:
    """Test ProjectFactory builder."""

    def test_default_values(self):
        """Test factory creates project with default values."""
        project = ProjectFactory().build()

        assert "key" in project
        assert project["key"].startswith("TEST-")
        assert project["name"] == "Test Project"
        assert "description" in project

    def test_with_key(self):
        """Test with_key sets custom key."""
        project = ProjectFactory().with_key("CUSTOM-001").build()
        assert project["key"] == "CUSTOM-001"

    def test_with_name(self):
        """Test with_name sets custom name."""
        project = ProjectFactory().with_name("Custom Project").build()
        assert project["name"] == "Custom Project"

    def test_with_description(self):
        """Test with_description sets custom description."""
        project = ProjectFactory().with_description("Custom description").build()
        assert project["description"] == "Custom description"

    def test_fluent_api(self):
        """Test fluent API chaining."""
        project = (
            ProjectFactory()
            .with_key("FLUENT-001")
            .with_name("Fluent Project")
            .with_description("Fluent description")
            .build()
        )

        assert project["key"] == "FLUENT-001"
        assert project["name"] == "Fluent Project"
        assert project["description"] == "Fluent description"

    def test_get_key(self):
        """Test get_key returns project key."""
        factory = ProjectFactory().with_key("GET-001")
        assert factory.get_key() == "GET-001"


class TestArtifactFactory:
    """Test ArtifactFactory builder."""

    def test_default_values(self):
        """Test factory creates artifact with default values."""
        artifact = ArtifactFactory().build()

        assert "id" in artifact
        assert artifact["id"].startswith("artifact-")
        assert artifact["project_key"] == "TEST-001"
        assert artifact["type"] == "pmp"
        assert "content" in artifact
        assert artifact["version"] == 1

    def test_with_type(self):
        """Test with_type sets artifact type."""
        artifact = ArtifactFactory().with_type("raid").build()
        assert artifact["type"] == "raid"

    def test_with_content(self):
        """Test with_content sets artifact content."""
        content = "# Custom Content\n\nTest"
        artifact = ArtifactFactory().with_content(content).build()
        assert artifact["content"] == content

    def test_fluent_api(self):
        """Test fluent API chaining."""
        artifact = (
            ArtifactFactory()
            .with_project("PROJ-001")
            .with_type("schedule")
            .with_content("Schedule content")
            .with_version(2)
            .build()
        )

        assert artifact["project_key"] == "PROJ-001"
        assert artifact["type"] == "schedule"
        assert artifact["content"] == "Schedule content"
        assert artifact["version"] == 2


class TestProposalFactory:
    """Test ProposalFactory builder."""

    def test_default_values(self):
        """Test factory creates proposal with default values."""
        proposal = ProposalFactory().build()

        assert "id" in proposal
        assert proposal["id"].startswith("proposal-")
        assert proposal["project_key"] == "TEST-001"
        assert proposal["artifact_id"] == "artifact-001"
        assert proposal["status"] == "pending"
        assert proposal["type"] == "manual"

    def test_with_status(self):
        """Test with_status sets proposal status."""
        proposal = ProposalFactory().with_status("applied").build()
        assert proposal["status"] == "applied"

    def test_with_type(self):
        """Test with_type sets proposal type."""
        proposal = ProposalFactory().with_type("ai-assisted").build()
        assert proposal["type"] == "ai-assisted"

    def test_fluent_api(self):
        """Test fluent API chaining."""
        proposal = (
            ProposalFactory()
            .with_project("PROJ-002")
            .for_artifact("art-123")
            .with_changes("Add scope section")
            .with_diff("+New line")
            .with_status("applied")
            .build()
        )

        assert proposal["project_key"] == "PROJ-002"
        assert proposal["artifact_id"] == "art-123"
        assert proposal["changes"] == "Add scope section"
        assert proposal["diff"] == "+New line"
        assert proposal["status"] == "applied"


class TestRAIDItemFactory:
    """Test RAIDItemFactory builder."""

    def test_default_values(self):
        """Test factory creates RAID item with default values."""
        raid = RAIDItemFactory().build()

        assert "id" in raid
        assert raid["id"].startswith("raid-")
        assert raid["project_key"] == "TEST-001"
        assert raid["type"] == "risk"
        assert raid["priority"] == "medium"
        assert raid["status"] == "open"

    def test_with_type(self):
        """Test with_type sets RAID type."""
        raid = RAIDItemFactory().with_type("issue").build()
        assert raid["type"] == "issue"

    def test_with_priority(self):
        """Test with_priority sets priority."""
        raid = RAIDItemFactory().with_priority("critical").build()
        assert raid["priority"] == "critical"

    def test_with_status(self):
        """Test with_status sets status."""
        raid = RAIDItemFactory().with_status("resolved").build()
        assert raid["status"] == "resolved"

    def test_fluent_api(self):
        """Test fluent API chaining."""
        raid = (
            RAIDItemFactory()
            .with_project("PROJ-003")
            .with_type("dependency")
            .with_title("External API dependency")
            .with_description("Depends on third-party API")
            .with_priority("high")
            .with_status("in-progress")
            .build()
        )

        assert raid["project_key"] == "PROJ-003"
        assert raid["type"] == "dependency"
        assert raid["title"] == "External API dependency"
        assert raid["priority"] == "high"
        assert raid["status"] == "in-progress"


class TestAuditResultFactory:
    """Test AuditResultFactory builder."""

    def test_default_values(self):
        """Test factory creates audit result with default values."""
        audit = AuditResultFactory().build()

        assert audit["project_key"] == "TEST-001"
        assert audit["passed"] is True
        assert audit["errors"] == []
        assert audit["warnings"] == []
        assert audit["artifact_count"] == 0

    def test_with_passed(self):
        """Test with_passed sets passed status."""
        audit = AuditResultFactory().with_passed(False).build()
        assert audit["passed"] is False

    def test_with_errors(self):
        """Test with_errors sets errors list."""
        errors = ["Missing field: scope", "Invalid reference"]
        audit = AuditResultFactory().with_errors(errors).build()
        assert audit["errors"] == errors

    def test_with_warnings(self):
        """Test with_warnings sets warnings list."""
        warnings = ["Field may be incomplete"]
        audit = AuditResultFactory().with_warnings(warnings).build()
        assert audit["warnings"] == warnings

    def test_fluent_api(self):
        """Test fluent API chaining."""
        audit = (
            AuditResultFactory()
            .with_project("PROJ-004")
            .with_passed(False)
            .with_errors(["Error 1", "Error 2"])
            .with_warnings(["Warning 1"])
            .with_artifact_count(5)
            .build()
        )

        assert audit["project_key"] == "PROJ-004"
        assert audit["passed"] is False
        assert len(audit["errors"]) == 2
        assert len(audit["warnings"]) == 1
        assert audit["artifact_count"] == 5
