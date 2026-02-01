"""Test data factories for creating test objects with fluent API.

Factories provide a convenient way to create test data with sensible defaults
and the ability to override specific fields for test scenarios.
"""

import uuid
from typing import Dict, Any, List
from datetime import datetime


class ProjectFactory:
    """Fluent builder for test projects."""

    def __init__(self):
        self._key: str = f"TEST-{uuid.uuid4().hex[:6].upper()}"
        self._name: str = "Test Project"
        self._description: str = "A test project for E2E testing"

    def with_key(self, key: str) -> "ProjectFactory":
        """Set project key."""
        self._key = key
        return self

    def with_name(self, name: str) -> "ProjectFactory":
        """Set project name."""
        self._name = name
        return self

    def with_description(self, description: str) -> "ProjectFactory":
        """Set project description."""
        self._description = description
        return self

    def build(self) -> Dict[str, Any]:
        """Build project data dict."""
        return {"key": self._key, "name": self._name, "description": self._description}

    def get_key(self) -> str:
        """Get the project key."""
        return self._key


class ArtifactFactory:
    """Fluent builder for test artifacts."""

    def __init__(self):
        self._id: str = f"artifact-{uuid.uuid4().hex[:8]}"
        self._project_key: str = "TEST-001"
        self._type: str = "pmp"
        self._content: str = "# Project Management Plan\n\nTest content"
        self._version: int = 1

    def with_id(self, artifact_id: str) -> "ArtifactFactory":
        """Set artifact ID."""
        self._id = artifact_id
        return self

    def with_project(self, project_key: str) -> "ArtifactFactory":
        """Set project key."""
        self._project_key = project_key
        return self

    def with_type(self, artifact_type: str) -> "ArtifactFactory":
        """Set artifact type (pmp, raid, schedule, etc.)."""
        self._type = artifact_type
        return self

    def with_content(self, content: str) -> "ArtifactFactory":
        """Set artifact content."""
        self._content = content
        return self

    def with_version(self, version: int) -> "ArtifactFactory":
        """Set artifact version."""
        self._version = version
        return self

    def build(self) -> Dict[str, Any]:
        """Build artifact data dict."""
        return {
            "id": self._id,
            "project_key": self._project_key,
            "type": self._type,
            "content": self._content,
            "version": self._version,
            "created_at": datetime.utcnow().isoformat(),
        }


class ProposalFactory:
    """Fluent builder for test proposals."""

    def __init__(self):
        self._id: str = f"proposal-{uuid.uuid4().hex[:8]}"
        self._project_key: str = "TEST-001"
        self._artifact_id: str = "artifact-001"
        self._changes: str = "Test changes"
        self._diff: str = "+Added line\n-Removed line"
        self._status: str = "pending"
        self._type: str = "manual"

    def with_id(self, proposal_id: str) -> "ProposalFactory":
        """Set proposal ID."""
        self._id = proposal_id
        return self

    def with_project(self, project_key: str) -> "ProposalFactory":
        """Set project key."""
        self._project_key = project_key
        return self

    def for_artifact(self, artifact_id: str) -> "ProposalFactory":
        """Set target artifact ID."""
        self._artifact_id = artifact_id
        return self

    def with_changes(self, changes: str) -> "ProposalFactory":
        """Set proposal changes description."""
        self._changes = changes
        return self

    def with_diff(self, diff: str) -> "ProposalFactory":
        """Set proposal diff content."""
        self._diff = diff
        return self

    def with_status(self, status: str) -> "ProposalFactory":
        """Set proposal status (pending, applied, rejected)."""
        self._status = status
        return self

    def with_type(self, proposal_type: str) -> "ProposalFactory":
        """Set proposal type (manual, ai-assisted)."""
        self._type = proposal_type
        return self

    def build(self) -> Dict[str, Any]:
        """Build proposal data dict."""
        return {
            "id": self._id,
            "project_key": self._project_key,
            "artifact_id": self._artifact_id,
            "changes": self._changes,
            "diff": self._diff,
            "status": self._status,
            "type": self._type,
            "created_at": datetime.utcnow().isoformat(),
        }


class RAIDItemFactory:
    """Fluent builder for test RAID items."""

    def __init__(self):
        self._id: str = f"raid-{uuid.uuid4().hex[:8]}"
        self._project_key: str = "TEST-001"
        self._type: str = "risk"
        self._title: str = "Test RAID item"
        self._description: str = "Test description"
        self._priority: str = "medium"
        self._status: str = "open"

    def with_id(self, item_id: str) -> "RAIDItemFactory":
        """Set RAID item ID."""
        self._id = item_id
        return self

    def with_project(self, project_key: str) -> "RAIDItemFactory":
        """Set project key."""
        self._project_key = project_key
        return self

    def with_type(self, item_type: str) -> "RAIDItemFactory":
        """Set RAID type (risk, assumption, issue, dependency)."""
        self._type = item_type
        return self

    def with_title(self, title: str) -> "RAIDItemFactory":
        """Set RAID item title."""
        self._title = title
        return self

    def with_description(self, description: str) -> "RAIDItemFactory":
        """Set RAID item description."""
        self._description = description
        return self

    def with_priority(self, priority: str) -> "RAIDItemFactory":
        """Set priority (low, medium, high, critical)."""
        self._priority = priority
        return self

    def with_status(self, status: str) -> "RAIDItemFactory":
        """Set status (open, in-progress, resolved, closed)."""
        self._status = status
        return self

    def build(self) -> Dict[str, Any]:
        """Build RAID item data dict."""
        return {
            "id": self._id,
            "project_key": self._project_key,
            "type": self._type,
            "title": self._title,
            "description": self._description,
            "priority": self._priority,
            "status": self._status,
            "created_at": datetime.utcnow().isoformat(),
        }


class AuditResultFactory:
    """Fluent builder for test audit results."""

    def __init__(self):
        self._project_key: str = "TEST-001"
        self._passed: bool = True
        self._errors: List[str] = []
        self._warnings: List[str] = []
        self._artifact_count: int = 0

    def with_project(self, project_key: str) -> "AuditResultFactory":
        """Set project key."""
        self._project_key = project_key
        return self

    def with_passed(self, passed: bool) -> "AuditResultFactory":
        """Set audit passed status."""
        self._passed = passed
        return self

    def with_errors(self, errors: List[str]) -> "AuditResultFactory":
        """Set audit errors."""
        self._errors = errors
        return self

    def with_warnings(self, warnings: List[str]) -> "AuditResultFactory":
        """Set audit warnings."""
        self._warnings = warnings
        return self

    def with_artifact_count(self, count: int) -> "AuditResultFactory":
        """Set number of artifacts audited."""
        self._artifact_count = count
        return self

    def build(self) -> Dict[str, Any]:
        """Build audit result data dict."""
        return {
            "project_key": self._project_key,
            "passed": self._passed,
            "errors": self._errors,
            "warnings": self._warnings,
            "artifact_count": self._artifact_count,
            "timestamp": datetime.utcnow().isoformat(),
        }
