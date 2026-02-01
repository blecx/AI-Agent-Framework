"""
Integration tests for enhanced audit rules.
Tests cross-artifact validation scenarios.
"""

import pytest
import tempfile
import shutil
import json
import sys
import os

# Add apps/api to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../../apps/api"))

from services.audit_service import AuditService  # noqa: E402
from services.git_manager import GitManager  # noqa: E402


@pytest.fixture(scope="function")
def temp_project_dir():
    """Create a temporary project directory for testing."""
    temp_dir = tempfile.mkdtemp()
    yield temp_dir
    shutil.rmtree(temp_dir)


@pytest.fixture(scope="function")
def git_manager(temp_project_dir):
    """Create a git manager with temporary directory."""
    manager = GitManager(temp_project_dir)
    manager.ensure_repository()
    return manager


@pytest.fixture(scope="function")
def audit_service():
    """Create an audit service instance."""
    return AuditService()


@pytest.fixture
def test_project(git_manager):
    """Create a test project with basic structure."""
    project_key = "TEST-AUDIT"
    project_path = git_manager.get_project_path(project_key)
    project_path.mkdir(parents=True, exist_ok=True)

    # Create metadata
    metadata = {
        "key": project_key,
        "name": "Test Audit Project",
        "description": "Project for testing audit rules",
        "start_date": "2026-03-01",
        "end_date": "2026-06-01",
    }
    (project_path / "metadata.json").write_text(json.dumps(metadata))

    return project_key


class TestCrossArtifactValidation:
    """Integration tests for cross-artifact validation."""

    def test_raid_to_pmp_cross_reference(
        self, audit_service, git_manager, test_project
    ):
        """Test RAID items correctly reference PMP deliverables."""
        project_path = git_manager.get_project_path(test_project)
        artifacts_path = project_path / "artifacts"
        artifacts_path.mkdir(parents=True, exist_ok=True)

        # Create PMP with deliverables
        pmp_data = {
            "deliverables": [
                {"id": "D-001", "name": "Design Document", "status": "in_progress"},
                {"id": "D-002", "name": "Implementation", "status": "not_started"},
            ],
            "milestones": [],
        }
        (artifacts_path / "pmp.json").write_text(json.dumps(pmp_data))

        # Create RAID with both valid and invalid references
        raid_data = {
            "items": [
                {
                    "id": "R-001",
                    "type": "risk",
                    "description": "Technical risk",
                    "related_deliverables": ["D-001"],  # Valid
                },
                {
                    "id": "R-002",
                    "type": "risk",
                    "description": "Schedule risk",
                    "related_deliverables": ["D-999"],  # Invalid
                },
            ]
        }
        (artifacts_path / "raid.json").write_text(json.dumps(raid_data))

        # Run audit
        result = audit_service.run_audit_rules(
            project_key=test_project,
            git_manager=git_manager,
            rule_set=["cross_reference"],
        )

        # Verify results
        assert result["total_issues"] >= 1
        cross_ref_issues = [
            i for i in result["issues"] if i["rule"] == "cross_reference"
        ]
        assert len(cross_ref_issues) >= 1
        assert any("D-999" in str(issue) for issue in cross_ref_issues)

    def test_milestone_date_consistency(self, audit_service, git_manager, test_project):
        """Test milestone dates are consistent with project timeline."""
        project_path = git_manager.get_project_path(test_project)
        artifacts_path = project_path / "artifacts"
        artifacts_path.mkdir(parents=True, exist_ok=True)

        # Create PMP with invalid milestone dates
        pmp_data = {
            "deliverables": [],
            "milestones": [
                {
                    "id": "M-001",
                    "name": "Kickoff",
                    "due_date": "2026-02-15",  # Before project start (2026-03-01)
                },
                {
                    "id": "M-002",
                    "name": "Mid-point Review",
                    "due_date": "2026-04-15",  # Valid
                },
                {
                    "id": "M-003",
                    "name": "Late Milestone",
                    "due_date": "2026-07-01",  # After project end (2026-06-01)
                },
            ],
        }
        (artifacts_path / "pmp.json").write_text(json.dumps(pmp_data))

        # Run audit
        result = audit_service.run_audit_rules(
            project_key=test_project,
            git_manager=git_manager,
            rule_set=["date_consistency"],
        )

        # Verify results
        assert result["total_issues"] >= 2  # M-001 and M-003
        date_issues = [i for i in result["issues"] if i["rule"] == "date_consistency"]
        assert len(date_issues) >= 2

    def test_owner_validation_with_governance(
        self, audit_service, git_manager, test_project
    ):
        """Test that referenced owners exist in governance/team."""
        project_path = git_manager.get_project_path(test_project)
        artifacts_path = project_path / "artifacts"
        artifacts_path.mkdir(parents=True, exist_ok=True)

        # Create governance with team members
        governance_data = {
            "team": [
                {"id": "user1", "name": "Alice", "role": "PM"},
                {"id": "user2", "name": "Bob", "role": "Dev"},
            ],
            "roles": [],
        }
        (artifacts_path / "governance.json").write_text(json.dumps(governance_data))

        # Create RAID with valid and invalid owners
        raid_data = {
            "items": [
                {
                    "id": "R-001",
                    "type": "risk",
                    "description": "Risk 1",
                    "owner": "user1",  # Valid
                },
                {
                    "id": "R-002",
                    "type": "issue",
                    "description": "Issue 1",
                    "owner": "user99",  # Invalid
                },
            ]
        }
        (artifacts_path / "raid.json").write_text(json.dumps(raid_data))

        # Run audit
        result = audit_service.run_audit_rules(
            project_key=test_project,
            git_manager=git_manager,
            rule_set=["owner_validation"],
        )

        # Verify results
        assert result["total_issues"] >= 1
        owner_issues = [i for i in result["issues"] if i["rule"] == "owner_validation"]
        assert len(owner_issues) >= 1
        assert any("user99" in str(issue) for issue in owner_issues)

    def test_dependency_cycle_detection_complex(
        self, audit_service, git_manager, test_project
    ):
        """Test detecting complex dependency cycles (A→B→C→A)."""
        project_path = git_manager.get_project_path(test_project)
        artifacts_path = project_path / "artifacts"
        artifacts_path.mkdir(parents=True, exist_ok=True)

        # Create PMP with circular dependencies
        pmp_data = {
            "deliverables": [
                {
                    "id": "D-001",
                    "name": "Design",
                    "dependencies": ["D-003"],
                },  # Depends on Implementation
                {
                    "id": "D-002",
                    "name": "Testing",
                    "dependencies": ["D-001"],
                },  # Depends on Design
                {
                    "id": "D-003",
                    "name": "Implementation",
                    "dependencies": ["D-002"],
                },  # Depends on Testing → Cycle!
            ],
            "milestones": [],
        }
        (artifacts_path / "pmp.json").write_text(json.dumps(pmp_data))

        # Run audit
        result = audit_service.run_audit_rules(
            project_key=test_project,
            git_manager=git_manager,
            rule_set=["dependency_cycles"],
        )

        # Verify results
        assert result["total_issues"] >= 1
        cycle_issues = [i for i in result["issues"] if i["rule"] == "dependency_cycles"]
        assert len(cycle_issues) >= 1

    def test_completeness_scoring_partial_project(
        self, audit_service, git_manager, test_project
    ):
        """Test completeness scoring for partially completed project."""
        project_path = git_manager.get_project_path(test_project)
        artifacts_path = project_path / "artifacts"
        artifacts_path.mkdir(parents=True, exist_ok=True)

        # Create only some artifacts
        (artifacts_path / "pmp.json").write_text(
            json.dumps(
                {"deliverables": [{"id": "D-001", "name": "Test"}], "milestones": []}
            )
        )
        (artifacts_path / "raid.json").write_text(json.dumps({"items": []}))

        # Run audit
        result = audit_service.run_audit_rules(
            project_key=test_project,
            git_manager=git_manager,
            rule_set=["completeness"],
        )

        # Verify completeness score
        assert "completeness_score" in result
        score = result["completeness_score"]
        assert 0 <= score <= 100
        assert score < 100  # Not fully complete

    def test_multi_artifact_scenario(self, audit_service, git_manager, test_project):
        """Test complex scenario with multiple artifacts and relationships."""
        project_path = git_manager.get_project_path(test_project)
        artifacts_path = project_path / "artifacts"
        artifacts_path.mkdir(parents=True, exist_ok=True)

        # Create full artifact set
        governance_data = {
            "team": [{"id": "pm1", "name": "PM", "role": "manager"}],
            "roles": [],
        }
        (artifacts_path / "governance.json").write_text(json.dumps(governance_data))

        pmp_data = {
            "deliverables": [
                {"id": "D-001", "name": "Deliverable 1", "dependencies": []}
            ],
            "milestones": [
                {"id": "M-001", "name": "Milestone 1", "due_date": "2026-04-01"}
            ],
        }
        (artifacts_path / "pmp.json").write_text(json.dumps(pmp_data))

        raid_data = {
            "items": [
                {
                    "id": "R-001",
                    "type": "risk",
                    "description": "Risk",
                    "owner": "pm1",
                    "related_deliverables": ["D-001"],
                    "related_milestones": ["M-001"],
                }
            ]
        }
        (artifacts_path / "raid.json").write_text(json.dumps(raid_data))

        # Run all audit rules
        result = audit_service.run_audit_rules(
            project_key=test_project,
            git_manager=git_manager,
        )

        # Verify comprehensive audit
        assert "issues" in result
        assert "completeness_score" in result
        assert "rule_violations" in result
        assert len(result["rule_violations"]) > 0  # Multiple rules ran


class TestAuditHistory:
    """Integration tests for audit history tracking."""

    def test_audit_history_persistence(self, audit_service, git_manager, test_project):
        """Test that audit history is persisted and retrievable."""
        # Run audit multiple times
        for i in range(3):
            result = audit_service.run_audit_rules(
                project_key=test_project,
                git_manager=git_manager,
            )
            audit_service.save_audit_history(test_project, result, git_manager)

        # Retrieve history
        history = audit_service.get_audit_history(
            project_key=test_project,
            git_manager=git_manager,
            limit=10,
        )

        # Verify
        assert len(history) == 3
        for entry in history:
            assert "timestamp" in entry
            assert "total_issues" in entry
            assert "completeness_score" in entry
            assert "rule_violations" in entry

    def test_audit_history_newest_first(self, audit_service, git_manager, test_project):
        """Test that audit history is returned newest first."""
        # Run audits with delays
        import time

        for i in range(3):
            result = audit_service.run_audit_rules(
                project_key=test_project,
                git_manager=git_manager,
            )
            audit_service.save_audit_history(test_project, result, git_manager)
            time.sleep(0.1)  # Small delay

        # Retrieve history
        history = audit_service.get_audit_history(
            project_key=test_project,
            git_manager=git_manager,
        )

        # Verify newest first
        assert len(history) == 3
        timestamps = [entry["timestamp"] for entry in history]
        assert timestamps == sorted(timestamps, reverse=True)
