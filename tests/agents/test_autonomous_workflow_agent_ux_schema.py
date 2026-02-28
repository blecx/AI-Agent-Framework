#!/usr/bin/env python3
"""Unit tests for strict UX authority output schema validation."""

from agents.autonomous_workflow_agent import AutonomousWorkflowAgent


def test_validate_ux_gate_output_pass_when_required_sections_present():
    text = """UX_DECISION: PASS
Navigation Plan:
Responsive Rules:
Grouping Decisions:
A11y Baseline:
Requirement Check:
Requirement Gaps:
Risk Notes:
"""

    decision, missing, errors = AutonomousWorkflowAgent._validate_ux_gate_output(text)

    assert decision == "PASS"
    assert missing == []
    assert errors == []


def test_validate_ux_gate_output_changes_when_section_missing():
    text = """UX_DECISION: PASS
Navigation Plan:
Responsive Rules:
Grouping Decisions:
A11y Baseline:
Requirement Check:
Requirement Gaps:
"""

    decision, missing, errors = AutonomousWorkflowAgent._validate_ux_gate_output(text)

    assert decision == "CHANGES"
    assert "Risk Notes:" in missing
    assert any("missing required sections" in error for error in errors)


def test_validate_ux_gate_output_invalid_header_reports_error_and_changes():
    text = """DECISION: PASS
Navigation Plan:
Responsive Rules:
Grouping Decisions:
A11y Baseline:
Requirement Check:
Requirement Gaps:
Risk Notes:
"""

    decision, missing, errors = AutonomousWorkflowAgent._validate_ux_gate_output(text)

    assert decision == "CHANGES"
    assert missing == ["Required Changes:"]
    assert any("invalid first line" in error for error in errors)
