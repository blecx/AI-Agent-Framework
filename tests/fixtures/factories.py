"""
Test Data Factories for E2E Testing

Provides fluent builder APIs for creating test data (projects, artifacts, proposals, RAID items).
Ensures deterministic, reproducible test data generation.
"""

import random
from typing import Optional, Dict, Any


class ProjectFactory:
    """Fluent builder for test projects."""

    def __init__(self):
        self._key: Optional[str] = None
        self._name: Optional[str] = None
        self._seed: int = 12345  # Deterministic by default

    def with_key(self, key: str) -> "ProjectFactory":
        """Set project key.

        Args:
            key: Project key (e.g., "TEST-01")
        """
        self._key = key
        return self

    def with_name(self, name: str) -> "ProjectFactory":
        """Set project name."""
        self._name = name
        return self

    def with_seed(self, seed: int) -> "ProjectFactory":
        """Set random seed for deterministic data generation."""
        self._seed = seed
        return self

    def build(self) -> Dict[str, Any]:
        """Build project dictionary.

        Returns:
            Project data ready for API/TUI commands
        """
        random.seed(self._seed)

        key = self._key or f"TEST-{random.randint(1000, 9999):04d}"
        name = self._name or f"Test Project {key}"

        return {"key": key, "name": name}

    @staticmethod
    def random_key() -> str:
        """Generate a random project key for quick tests."""
        return f"TEST-{random.randint(10000, 99999):05d}"


class ArtifactFactory:
    """Fluent builder for test artifacts."""

    def __init__(self):
        self._artifact_id: Optional[str] = None
        self._artifact_type: str = "pmp"
        self._content: Optional[str] = None
        self._seed: int = 12345

    def with_id(self, artifact_id: str) -> "ArtifactFactory":
        """Set artifact ID."""
        self._artifact_id = artifact_id
        return self

    def with_type(self, artifact_type: str) -> "ArtifactFactory":
        """Set artifact type (e.g., 'pmp', 'raid', 'charter')."""
        self._artifact_type = artifact_type
        return self

    def with_content(self, content: str) -> "ArtifactFactory":
        """Set artifact content (Markdown)."""
        self._content = content
        return self

    def with_seed(self, seed: int) -> "ArtifactFactory":
        """Set random seed."""
        self._seed = seed
        return self

    def build(self) -> Dict[str, Any]:
        """Build artifact dictionary."""
        random.seed(self._seed)

        artifact_id = (
            self._artifact_id or f"{self._artifact_type}_{random.randint(1000, 9999)}"
        )
        content = self._content or self._generate_default_content(self._artifact_type)

        return {
            "artifact_id": artifact_id,
            "artifact_type": self._artifact_type,
            "content": content,
        }

    def _generate_default_content(self, artifact_type: str) -> str:
        """Generate default content for artifact type."""
        if artifact_type == "pmp":
            return """# Project Management Plan

## Project Overview
Test project for E2E testing.

## Scope
TBD

## Schedule
TBD
"""
        elif artifact_type == "charter":
            return """# Project Charter

## Purpose
Test charter for E2E testing.
"""
        else:
            return f"# {artifact_type.upper()}\n\nTest content.\n"


class ProposalFactory:
    """Fluent builder for test proposals."""

    def __init__(self):
        self._proposal_id: Optional[str] = None
        self._artifact_id: Optional[str] = None
        self._changes: Optional[str] = None
        self._description: Optional[str] = None
        self._seed: int = 12345

    def with_id(self, proposal_id: str) -> "ProposalFactory":
        """Set proposal ID."""
        self._proposal_id = proposal_id
        return self

    def for_artifact(self, artifact_id: str) -> "ProposalFactory":
        """Set target artifact ID."""
        self._artifact_id = artifact_id
        return self

    def with_changes(self, changes: str) -> "ProposalFactory":
        """Set diff/changes content."""
        self._changes = changes
        return self

    def with_description(self, description: str) -> "ProposalFactory":
        """Set proposal description."""
        self._description = description
        return self

    def with_seed(self, seed: int) -> "ProposalFactory":
        """Set random seed."""
        self._seed = seed
        return self

    def build(self) -> Dict[str, Any]:
        """Build proposal dictionary."""
        random.seed(self._seed)

        proposal_id = self._proposal_id or f"proposal_{random.randint(1000, 9999)}"
        artifact_id = self._artifact_id or "artifact_001"
        description = self._description or "Test proposal"
        changes = (
            self._changes
            or "--- a/artifact\n+++ b/artifact\n@@ -1,1 +1,1 @@\n-old\n+new\n"
        )

        return {
            "proposal_id": proposal_id,
            "artifact_id": artifact_id,
            "description": description,
            "changes": changes,
        }


class RAIDFactory:
    """Fluent builder for test RAID items."""

    def __init__(self):
        self._item_id: Optional[str] = None
        self._item_type: str = "risk"  # risk, assumption, issue, dependency
        self._title: Optional[str] = None
        self._description: Optional[str] = None
        self._priority: str = "medium"
        self._status: str = "open"
        self._seed: int = 12345

    def with_id(self, item_id: str) -> "RAIDFactory":
        """Set RAID item ID."""
        self._item_id = item_id
        return self

    def with_type(self, item_type: str) -> "RAIDFactory":
        """Set RAID type (risk, assumption, issue, dependency)."""
        self._item_type = item_type
        return self

    def with_title(self, title: str) -> "RAIDFactory":
        """Set item title."""
        self._title = title
        return self

    def with_description(self, description: str) -> "RAIDFactory":
        """Set item description."""
        self._description = description
        return self

    def with_priority(self, priority: str) -> "RAIDFactory":
        """Set priority (low, medium, high, critical)."""
        self._priority = priority
        return self

    def with_status(self, status: str) -> "RAIDFactory":
        """Set status (open, closed, mitigated, etc.)."""
        self._status = status
        return self

    def with_seed(self, seed: int) -> "RAIDFactory":
        """Set random seed."""
        self._seed = seed
        return self

    def build(self) -> Dict[str, Any]:
        """Build RAID item dictionary."""
        random.seed(self._seed)

        item_id = (
            self._item_id or f"{self._item_type[0].upper()}{random.randint(1000, 9999)}"
        )
        title = self._title or f"Test {self._item_type} {item_id}"
        description = self._description or f"Test description for {self._item_type}"

        return {
            "item_id": item_id,
            "type": self._item_type,
            "title": title,
            "description": description,
            "priority": self._priority,
            "status": self._status,
        }
