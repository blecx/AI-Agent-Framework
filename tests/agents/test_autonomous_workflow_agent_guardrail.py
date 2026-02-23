#!/usr/bin/env python3
"""Unit tests for autonomous planning 20-minute guardrail behavior."""

from agents.autonomous_workflow_agent import AutonomousWorkflowAgent


def test_extract_estimated_manual_minutes_parses_integer_field():
    plan_text = """
PLANNING_GUARDRAIL:
ESTIMATED_MANUAL_MINUTES: 18
SPLIT_REQUIRED: NO
"""
    assert AutonomousWorkflowAgent._extract_estimated_manual_minutes(plan_text) == 18


def test_extract_estimated_manual_minutes_returns_none_when_missing():
    plan_text = "HANDOFF_TO_CODING:\n- Steps: ..."
    assert AutonomousWorkflowAgent._extract_estimated_manual_minutes(plan_text) is None


def test_evaluate_manual_plan_guardrail_blocks_when_over_limit():
    agent = AutonomousWorkflowAgent(issue_number=401, dry_run=True)
    ok, estimate, message = agent._evaluate_manual_plan_guardrail(
        "ESTIMATED_MANUAL_MINUTES: 35"
    )

    assert ok is False
    assert estimate == 35
    assert "exceeding 20-minute limit" in message


def test_evaluate_manual_plan_guardrail_blocks_when_missing_estimate():
    agent = AutonomousWorkflowAgent(issue_number=401, dry_run=True)
    ok, estimate, message = agent._evaluate_manual_plan_guardrail("SPLIT_REQUIRED: NO")

    assert ok is False
    assert estimate is None
    assert "missing ESTIMATED_MANUAL_MINUTES" in message


def test_evaluate_manual_plan_guardrail_allows_within_limit():
    agent = AutonomousWorkflowAgent(issue_number=401, dry_run=True)
    ok, estimate, message = agent._evaluate_manual_plan_guardrail(
        "ESTIMATED_MANUAL_MINUTES: 20"
    )

    assert ok is True
    assert estimate == 20
    assert "within 20-minute limit" in message


def test_build_split_recommendation_prefers_planner_block():
    agent = AutonomousWorkflowAgent(issue_number=401, dry_run=True)
    plan_text = """
ESTIMATED_MANUAL_MINUTES: 28
SPLIT_RECOMMENDATION:
- Create issue 401A for parser prep.
- Create issue 401B for implementation.
HANDOFF_TO_CODING:
- Summary: ...
"""

    recommendation = agent._build_split_recommendation(plan_text, estimate=28)

    assert "401A" in recommendation
    assert "401B" in recommendation


def test_build_split_recommendation_falls_back_when_missing():
    agent = AutonomousWorkflowAgent(issue_number=401, dry_run=True)
    recommendation = agent._build_split_recommendation(
        "ESTIMATED_MANUAL_MINUTES: 30", estimate=30
    )

    assert "Current plan estimate: 30 minutes" in recommendation
    assert "Create issue A" in recommendation
