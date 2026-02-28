#!/usr/bin/env python3
"""Unit tests for UX requirement matrix artifact generation."""

from pathlib import Path

from agents.autonomous_workflow_agent import AutonomousWorkflowAgent


def test_build_ux_requirement_matrix_pass_rows():
    ux_text = """UX_DECISION: PASS
Navigation Plan:
Responsive Rules:
Grouping Decisions:
A11y Baseline:
Requirement Check:
Requirement Gaps:
Risk Notes:
"""

    rows = AutonomousWorkflowAgent._build_ux_requirement_matrix(ux_text, "PASS")

    assert len(rows) == 5
    assert all(row["status"] == "pass" for row in rows)
    assert all(row["blocking"] == "no" for row in rows)


def test_build_ux_requirement_matrix_marks_blocking_gaps_for_changes_and_missing():
    ux_text = """UX_DECISION: CHANGES
Navigation Plan:
Responsive Rules:
A11y Baseline:
Requirement Check:
Requirement Gaps:
- grouping has unresolved dependency (blocking)
Risk Notes:
Required Changes:
"""

    rows = AutonomousWorkflowAgent._build_ux_requirement_matrix(ux_text, "CHANGES")

    grouping_row = next(row for row in rows if row["requirement"] == "grouping")
    assert grouping_row["status"] == "gap"
    assert grouping_row["blocking"] == "yes"
    assert "missing section" in grouping_row["evidence"]


def test_persist_ux_consultation_writes_matrix_artifact(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    agent = AutonomousWorkflowAgent(issue_number=777, dry_run=False)

    ux_text = """UX_DECISION: PASS
Navigation Plan:
Responsive Rules:
Grouping Decisions:
A11y Baseline:
Requirement Check:
Requirement Gaps:
Risk Notes:
"""
    agent._persist_ux_consultation("Phase 2.5", ux_text, "PASS")

    matrix_path = Path(".tmp/ux-requirement-matrix-issue-777.md")
    assert matrix_path.exists()
    content = matrix_path.read_text(encoding="utf-8")
    assert "| Requirement | Status | Blocking | Evidence |" in content
    assert "| navigation | pass | no | section present |" in content
