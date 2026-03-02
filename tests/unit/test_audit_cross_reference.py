"""
Unit tests for the cross_reference_consistency audit rule.

Covers:
- No issues when all referenced RAID items exist (positive case)
- Error reported for each dangling deliverable→risk reference (negative case)
- Empty deliverables list produces no issues
- Missing raid.json treated as empty RAID (all references dangle)
- Missing pmp.json gracefully returns empty list
- Output ordering is deterministic (sorted by item_id / risk_id)
"""

import json
import shutil
import tempfile
from pathlib import Path

import pytest

from apps.api.services.audit.rules_engine import AuditRulesEngine
from apps.api.services.git_manager import GitManager


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------


@pytest.fixture(scope="function")
def temp_dir():
    d = tempfile.mkdtemp()
    yield d
    shutil.rmtree(d)


@pytest.fixture(scope="function")
def git_manager(temp_dir):
    manager = GitManager(temp_dir)
    manager.ensure_repository()
    return manager


@pytest.fixture(scope="function")
def engine():
    return AuditRulesEngine()


@pytest.fixture(scope="function")
def project_key(git_manager):
    key = "XREF001"
    git_manager.create_project(key, {"key": key, "name": "Cross-Ref Test"})
    return key


def _artifacts_path(git_manager, project_key: str) -> Path:
    return git_manager.get_project_path(project_key) / "artifacts"


def _write_json(path: Path, data: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data))


# ---------------------------------------------------------------------------
# Positive cases
# ---------------------------------------------------------------------------


class TestCrossReferenceConsistencyPositive:
    """Rule produces no issues when references are valid."""

    def test_no_issues_when_all_risk_ids_exist(self, engine, git_manager, project_key):
        """Deliverables whose related_risks all exist in raid.json → no issues."""
        artifacts = _artifacts_path(git_manager, project_key)

        _write_json(
            artifacts / "raid.json",
            {"items": [{"id": "R-001"}, {"id": "R-002"}]},
        )
        _write_json(
            artifacts / "pmp.json",
            {
                "deliverables": [
                    {"id": "D-001", "related_risks": ["R-001", "R-002"]},
                ]
            },
        )

        issues = engine._audit_cross_reference_consistency(project_key, git_manager)

        assert issues == []

    def test_no_issues_when_no_related_risks_field(
        self, engine, git_manager, project_key
    ):
        """Deliverables without related_risks generate no issues."""
        artifacts = _artifacts_path(git_manager, project_key)

        _write_json(artifacts / "raid.json", {"items": []})
        _write_json(
            artifacts / "pmp.json",
            {"deliverables": [{"id": "D-001", "name": "Deliverable without risks"}]},
        )

        issues = engine._audit_cross_reference_consistency(project_key, git_manager)

        assert issues == []

    def test_no_issues_when_deliverables_empty(
        self, engine, git_manager, project_key
    ):
        """Empty deliverables list produces no issues."""
        artifacts = _artifacts_path(git_manager, project_key)

        _write_json(artifacts / "raid.json", {"items": [{"id": "R-001"}]})
        _write_json(artifacts / "pmp.json", {"deliverables": []})

        issues = engine._audit_cross_reference_consistency(project_key, git_manager)

        assert issues == []

    def test_no_issues_when_pmp_missing(self, engine, git_manager, project_key):
        """Missing pmp.json → rule skips gracefully (returns [])."""
        # No pmp.json written
        issues = engine._audit_cross_reference_consistency(project_key, git_manager)

        assert issues == []


# ---------------------------------------------------------------------------
# Negative cases
# ---------------------------------------------------------------------------


class TestCrossReferenceConsistencyNegative:
    """Rule raises issues when references are broken."""

    def test_error_for_dangling_risk_reference(
        self, engine, git_manager, project_key
    ):
        """Deliverable referencing a non-existent risk ID produces one error."""
        artifacts = _artifacts_path(git_manager, project_key)

        _write_json(artifacts / "raid.json", {"items": [{"id": "R-001"}]})
        _write_json(
            artifacts / "pmp.json",
            {
                "deliverables": [
                    {"id": "D-001", "related_risks": ["R-001", "R-999"]},
                ]
            },
        )

        issues = engine._audit_cross_reference_consistency(project_key, git_manager)

        assert len(issues) == 1
        issue = issues[0]
        assert issue["rule"] == "cross_reference_consistency"
        assert issue["severity"] == "error"
        assert "R-999" in issue["message"]
        assert "D-001" in issue["message"]
        assert issue["artifact"] == "artifacts/pmp.json"
        assert issue["item_id"] == "D-001"

    def test_multiple_dangling_references_all_reported(
        self, engine, git_manager, project_key
    ):
        """Multiple dangling risk IDs each generate a separate issue."""
        artifacts = _artifacts_path(git_manager, project_key)

        _write_json(artifacts / "raid.json", {"items": []})
        _write_json(
            artifacts / "pmp.json",
            {
                "deliverables": [
                    {"id": "D-001", "related_risks": ["R-001", "R-002"]},
                ]
            },
        )

        issues = engine._audit_cross_reference_consistency(project_key, git_manager)

        assert len(issues) == 2
        referenced_ids = sorted(i["message"].split()[-1] for i in issues)
        assert referenced_ids == ["R-001", "R-002"]

    def test_missing_raid_marks_all_references_as_dangling(
        self, engine, git_manager, project_key
    ):
        """When raid.json is absent every risk reference is dangling."""
        artifacts = _artifacts_path(git_manager, project_key)

        # No raid.json
        _write_json(
            artifacts / "pmp.json",
            {
                "deliverables": [
                    {"id": "D-001", "related_risks": ["R-001"]},
                ]
            },
        )

        issues = engine._audit_cross_reference_consistency(project_key, git_manager)

        assert len(issues) == 1
        assert "R-001" in issues[0]["message"]

    def test_errors_across_multiple_deliverables(
        self, engine, git_manager, project_key
    ):
        """Issues from multiple deliverables are all captured."""
        artifacts = _artifacts_path(git_manager, project_key)

        _write_json(artifacts / "raid.json", {"items": [{"id": "R-001"}]})
        _write_json(
            artifacts / "pmp.json",
            {
                "deliverables": [
                    {"id": "D-001", "related_risks": ["R-999"]},
                    {"id": "D-002", "related_risks": ["R-888"]},
                ]
            },
        )

        issues = engine._audit_cross_reference_consistency(project_key, git_manager)

        assert len(issues) == 2
        item_ids = sorted(i["item_id"] for i in issues)
        assert item_ids == ["D-001", "D-002"]


# ---------------------------------------------------------------------------
# Determinism tests
# ---------------------------------------------------------------------------


class TestCrossReferenceConsistencyDeterminism:
    """Verify output ordering is deterministic (sorted)."""

    def test_output_is_sorted_by_item_id_then_risk_id(
        self, engine, git_manager, project_key
    ):
        """Issues are sorted deterministically regardless of dict insertion order."""
        artifacts = _artifacts_path(git_manager, project_key)

        _write_json(artifacts / "raid.json", {"items": []})
        _write_json(
            artifacts / "pmp.json",
            {
                "deliverables": [
                    {"id": "D-002", "related_risks": ["R-Z", "R-A"]},
                    {"id": "D-001", "related_risks": ["R-B"]},
                ]
            },
        )

        issues = engine._audit_cross_reference_consistency(project_key, git_manager)

        assert len(issues) == 3
        # Deliverables sorted by id, risks sorted within each deliverable
        expected_item_ids = ["D-001", "D-002", "D-002"]
        expected_risk_fragments = ["R-B", "R-A", "R-Z"]  # D-001: R-B; D-002: R-A then R-Z

        for i, (expected_item, expected_risk) in enumerate(
            zip(expected_item_ids, expected_risk_fragments)
        ):
            assert issues[i]["item_id"] == expected_item, (
                f"Issue {i}: expected item_id={expected_item}, got {issues[i]['item_id']}"
            )
            assert expected_risk in issues[i]["message"], (
                f"Issue {i}: expected risk {expected_risk} in message: {issues[i]['message']}"
            )

    def test_run_audit_rules_includes_cross_reference_consistency(
        self, engine, git_manager, project_key
    ):
        """cross_reference_consistency is registered in the audit pipeline."""
        artifacts = _artifacts_path(git_manager, project_key)

        _write_json(artifacts / "raid.json", {"items": []})
        _write_json(
            artifacts / "pmp.json",
            {"deliverables": [{"id": "D-001", "related_risks": ["R-MISSING"]}]},
        )

        result = engine.run_audit_rules(project_key, git_manager)

        assert "cross_reference_consistency" in result["rule_violations"]
        assert result["rule_violations"]["cross_reference_consistency"] == 1

        issue_rules = [i["rule"] for i in result["issues"]]
        assert "cross_reference_consistency" in issue_rules
