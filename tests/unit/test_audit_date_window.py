"""
Unit tests for the date_window_consistency audit rule.

Covers:
- No issues when planned_start <= planned_end and within project lifecycle (positive)
- Error when planned_start > planned_end (inverted window)
- Warning when planned_start is before project start_date
- Warning when planned_end is after project end_date
- Missing planned_start/planned_end fields are ignored (no false positives)
- Missing pmp.json returns empty list
- Missing metadata.json skips lifecycle checks
- Output ordering is deterministic (sorted by item_id)
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
    key = "DW001"
    git_manager.create_project(key, {"key": key, "name": "Date-Window Test"})
    return key


def _artifacts_path(git_manager, project_key: str) -> Path:
    return git_manager.get_project_path(project_key) / "artifacts"


def _write_json(path: Path, data: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data))


def _write_metadata(git_manager, project_key: str, start: str, end: str) -> None:
    meta_path = git_manager.get_project_path(project_key) / "metadata.json"
    meta_path.write_text(json.dumps({"start_date": start, "end_date": end}))


# ---------------------------------------------------------------------------
# Positive cases
# ---------------------------------------------------------------------------


class TestDateWindowConsistencyPositive:
    """Rule produces no issues when date windows are valid."""

    def test_no_issues_when_dates_valid_and_within_lifecycle(
        self, engine, git_manager, project_key
    ):
        """planned_start <= planned_end and both within project lifecycle."""
        _write_metadata(git_manager, project_key, "2025-01-01", "2025-12-31")
        artifacts = _artifacts_path(git_manager, project_key)
        _write_json(
            artifacts / "pmp.json",
            {
                "deliverables": [
                    {
                        "id": "D-001",
                        "planned_start": "2025-03-01",
                        "planned_end": "2025-06-30",
                    }
                ]
            },
        )

        issues = engine._audit_date_window_consistency(project_key, git_manager)

        assert issues == []

    def test_no_issues_when_start_equals_end(self, engine, git_manager, project_key):
        """planned_start == planned_end is a valid single-day window."""
        _write_metadata(git_manager, project_key, "2025-01-01", "2025-12-31")
        artifacts = _artifacts_path(git_manager, project_key)
        _write_json(
            artifacts / "pmp.json",
            {
                "deliverables": [
                    {
                        "id": "D-001",
                        "planned_start": "2025-06-01",
                        "planned_end": "2025-06-01",
                    }
                ]
            },
        )

        issues = engine._audit_date_window_consistency(project_key, git_manager)

        assert issues == []

    def test_no_issues_when_no_date_fields(self, engine, git_manager, project_key):
        """Deliverables without planned_start/planned_end fields generate no issues."""
        artifacts = _artifacts_path(git_manager, project_key)
        _write_json(
            artifacts / "pmp.json",
            {"deliverables": [{"id": "D-001", "name": "No dates"}]},
        )

        issues = engine._audit_date_window_consistency(project_key, git_manager)

        assert issues == []

    def test_no_issues_when_no_metadata(self, engine, git_manager, project_key):
        """Without metadata.json the lifecycle checks are skipped; valid window still passes."""
        artifacts = _artifacts_path(git_manager, project_key)
        _write_json(
            artifacts / "pmp.json",
            {
                "deliverables": [
                    {
                        "id": "D-001",
                        "planned_start": "2025-03-01",
                        "planned_end": "2025-06-30",
                    }
                ]
            },
        )

        issues = engine._audit_date_window_consistency(project_key, git_manager)

        assert issues == []


# ---------------------------------------------------------------------------
# Negative cases
# ---------------------------------------------------------------------------


class TestDateWindowConsistencyNegative:
    """Rule produces issues when date windows are invalid."""

    def test_error_when_planned_start_after_planned_end(
        self, engine, git_manager, project_key
    ):
        """planned_start > planned_end must produce an error."""
        artifacts = _artifacts_path(git_manager, project_key)
        _write_json(
            artifacts / "pmp.json",
            {
                "deliverables": [
                    {
                        "id": "D-001",
                        "planned_start": "2025-09-01",
                        "planned_end": "2025-06-30",
                    }
                ]
            },
        )

        issues = engine._audit_date_window_consistency(project_key, git_manager)

        assert len(issues) == 1
        assert issues[0]["rule"] == "date_window_consistency"
        assert issues[0]["severity"] == "error"
        assert "D-001" in issues[0]["message"]
        assert "planned_start" in issues[0]["message"]
        assert issues[0]["item_id"] == "D-001"

    def test_warning_when_planned_start_before_project_start(
        self, engine, git_manager, project_key
    ):
        """planned_start earlier than project start_date triggers a warning."""
        _write_metadata(git_manager, project_key, "2025-04-01", "2025-12-31")
        artifacts = _artifacts_path(git_manager, project_key)
        _write_json(
            artifacts / "pmp.json",
            {
                "deliverables": [
                    {
                        "id": "D-001",
                        "planned_start": "2025-01-01",
                        "planned_end": "2025-06-30",
                    }
                ]
            },
        )

        issues = engine._audit_date_window_consistency(project_key, git_manager)

        assert len(issues) == 1
        assert issues[0]["severity"] == "warning"
        assert "before project start" in issues[0]["message"]

    def test_warning_when_planned_end_after_project_end(
        self, engine, git_manager, project_key
    ):
        """planned_end later than project end_date triggers a warning."""
        _write_metadata(git_manager, project_key, "2025-01-01", "2025-09-30")
        artifacts = _artifacts_path(git_manager, project_key)
        _write_json(
            artifacts / "pmp.json",
            {
                "deliverables": [
                    {
                        "id": "D-001",
                        "planned_start": "2025-06-01",
                        "planned_end": "2025-12-31",
                    }
                ]
            },
        )

        issues = engine._audit_date_window_consistency(project_key, git_manager)

        assert len(issues) == 1
        assert issues[0]["severity"] == "warning"
        assert "after project end" in issues[0]["message"]

    def test_multiple_issues_across_deliverables(
        self, engine, git_manager, project_key
    ):
        """Multiple deliverables with issues each contribute their own issue."""
        _write_metadata(git_manager, project_key, "2025-04-01", "2025-09-30")
        artifacts = _artifacts_path(git_manager, project_key)
        _write_json(
            artifacts / "pmp.json",
            {
                "deliverables": [
                    {
                        "id": "D-001",
                        "planned_start": "2025-08-01",
                        "planned_end": "2025-07-01",  # inverted
                    },
                    {
                        "id": "D-002",
                        "planned_start": "2025-01-01",  # before project start
                        "planned_end": "2025-05-31",
                    },
                ]
            },
        )

        issues = engine._audit_date_window_consistency(project_key, git_manager)

        assert len(issues) == 2
        item_ids = [i["item_id"] for i in issues]
        assert "D-001" in item_ids
        assert "D-002" in item_ids

    def test_missing_pmp_returns_empty(self, engine, git_manager, project_key):
        """When pmp.json does not exist the rule returns an empty list."""
        issues = engine._audit_date_window_consistency(project_key, git_manager)
        assert issues == []


# ---------------------------------------------------------------------------
# Determinism
# ---------------------------------------------------------------------------


class TestDateWindowConsistencyDeterminism:
    """Rule output ordering is stable regardless of input order."""

    def test_output_is_sorted_deterministically(
        self, engine, git_manager, project_key
    ):
        """Issues are produced in a deterministic order (sorted by item_id)."""
        artifacts = _artifacts_path(git_manager, project_key)
        # Intentionally reverse alphabetical to verify sorting
        _write_json(
            artifacts / "pmp.json",
            {
                "deliverables": [
                    {
                        "id": "D-Z",
                        "planned_start": "2025-09-01",
                        "planned_end": "2025-01-01",
                    },
                    {
                        "id": "D-A",
                        "planned_start": "2025-09-01",
                        "planned_end": "2025-01-01",
                    },
                ]
            },
        )

        issues = engine._audit_date_window_consistency(project_key, git_manager)

        # The method iterates deliverables in sorted id order
        item_ids = [i["item_id"] for i in issues]
        assert item_ids == sorted(item_ids)
