"""Unit tests for ComplexityScorer and RouterAgent.

ComplexityScorer: purely deterministic, no mocking needed.
RouterAgent: mocks MCPMultiClient.
"""

from __future__ import annotations

from unittest.mock import AsyncMock, MagicMock

import pytest

from agents.complexity_scorer import ComplexityScorer, ScoringBreakdown
from agents.router_agent import RouterAgent, RoutingDecision


# ===========================================================================
# ComplexityScorer tests
# ===========================================================================


@pytest.fixture
def scorer() -> ComplexityScorer:
    return ComplexityScorer()


# ---------------------------------------------------------------------------
# File count dimension
# ---------------------------------------------------------------------------

def test_file_count_low(scorer):
    score, bd = scorer.score("Fix a small bug", ["file_a.py"])
    assert bd.file_count_score == 0


def test_file_count_medium(scorer):
    files = [f"file_{i}.py" for i in range(4)]
    _, bd = scorer.score("some issue", files)
    assert bd.file_count_score == 1


def test_file_count_high(scorer):
    files = [f"file_{i}.py" for i in range(8)]
    _, bd = scorer.score("some issue", files)
    assert bd.file_count_score == 2


# ---------------------------------------------------------------------------
# Cross-service dimension
# ---------------------------------------------------------------------------

def test_cross_service_single(scorer):
    files = ["apps/api/routers/templates.py", "apps/api/services/template_service.py"]
    _, bd = scorer.score("update templates", files)
    assert bd.cross_service_score == 0


def test_cross_service_two(scorer):
    files = ["apps/api/services/template_service.py", "agents/router_agent.py"]
    _, bd = scorer.score("wire agents to api", files)
    assert bd.cross_service_score == 1


def test_cross_service_three(scorer):
    files = [
        "apps/api/services/template_service.py",
        "agents/router_agent.py",
        "client/src/components/TemplateList.tsx",
    ]
    _, bd = scorer.score("full stack change", files)
    assert bd.cross_service_score == 2


# ---------------------------------------------------------------------------
# Domain count dimension
# ---------------------------------------------------------------------------

def test_domain_count_single(scorer):
    _, bd = scorer.score("Fix the template service", [])
    assert bd.domain_count_score == 0


def test_domain_count_two(scorer):
    _, bd = scorer.score("Fix the template and workflow service", [])
    assert bd.domain_count_score == 1


def test_domain_count_three(scorer):
    _, bd = scorer.score("Fix template, blueprint, and raid service", [])
    assert bd.domain_count_score == 2


# ---------------------------------------------------------------------------
# Breaking changes dimension
# ---------------------------------------------------------------------------

def test_breaking_no_keywords(scorer):
    _, bd = scorer.score("Add a new feature to templates", [])
    assert bd.breaking_score == 0


def test_breaking_one_keyword(scorer):
    _, bd = scorer.score("Remove the old template endpoint", [])
    assert bd.breaking_score == 1


def test_breaking_multiple_keywords(scorer):
    _, bd = scorer.score("Breaking: rename and remove deprecated fields", [])
    assert bd.breaking_score == 2


# ---------------------------------------------------------------------------
# Test gap dimension
# ---------------------------------------------------------------------------

def test_test_gap_none(scorer):
    _, bd = scorer.score("Fix bug and update tests", [])
    assert bd.test_gap_score == 0


def test_test_gap_one(scorer):
    _, bd = scorer.score("This code has no test coverage", [])
    assert bd.test_gap_score == 1


def test_test_gap_multiple(scorer):
    _, bd = scorer.score("Missing test for this service, add test coverage gap", [])
    assert bd.test_gap_score == 2


# ---------------------------------------------------------------------------
# Total score & model tier
# ---------------------------------------------------------------------------

def test_low_complexity_gets_mini_tier(scorer):
    score, _ = scorer.score("Fix typo in README", ["README.md"])
    assert score <= 5
    assert ComplexityScorer.model_tier(score) == "mini"


def test_high_complexity_gets_full_tier(scorer):
    # Many files, cross-service, multiple domains, breaking, test gap
    files = [f"apps/api/f{i}.py" for i in range(8)] + ["agents/f.py", "client/f.tsx"]
    body = "Breaking: remove deprecated template, blueprint, workflow, raid fields. Missing test coverage."
    score, _ = scorer.score(body, files)
    assert score >= 6
    assert ComplexityScorer.model_tier(score) == "full"


def test_score_clamped_to_10(scorer):
    files = [f"apps/api/f{i}.py" for i in range(10)] + ["agents/x.py", "client/y.tsx"]
    body = "Breaking: rename and remove deprecated template blueprint workflow raid artifact. Missing test coverage."
    score, _ = scorer.score(body, files, memory_adjustment=5)
    assert score == 10


def test_score_clamped_to_0(scorer):
    score, _ = scorer.score("", [], memory_adjustment=-10)
    assert score == 0


# ---------------------------------------------------------------------------
# Memory adjustment
# ---------------------------------------------------------------------------

def test_memory_adjustment_increases_score(scorer):
    s1, _ = scorer.score("Fix simple bug", [])
    s2, _ = scorer.score("Fix simple bug", [], memory_adjustment=2)
    assert s2 == min(10, s1 + 2)


def test_memory_adjustment_decreases_score(scorer):
    s1, _ = scorer.score("Fix template service", ["apps/api/s.py"] * 6)
    s2, _ = scorer.score("Fix template service", ["apps/api/s.py"] * 6, memory_adjustment=-1)
    assert s2 == max(0, s1 - 1)


# ===========================================================================
# RouterAgent tests
# ===========================================================================


@pytest.fixture
def mock_mcp():
    mcp = MagicMock()
    mcp.call_tool = AsyncMock()
    return mcp


@pytest.mark.asyncio
async def test_route_returns_routing_decision(mock_mcp):
    """route() returns a RoutingDecision with correct run_id and tier."""
    mock_mcp.call_tool.side_effect = [
        {"results": []},                  # memory_search_similar
        {"run_id": "run-abc-123"},         # bus_create_run
        {"ok": True},                      # bus_set_status(routing)
    ]

    agent = RouterAgent(mock_mcp)
    decision = await agent.route(
        issue_number=42,
        issue_title="Fix template service",
        issue_body="Fix a small bug in the template service",
        repo="owner/repo",
    )

    assert isinstance(decision, RoutingDecision)
    assert decision.run_id == "run-abc-123"
    assert decision.issue_number == 42
    assert decision.repo == "owner/repo"
    assert decision.coder_model_tier in ("mini", "full")
    assert 0 <= decision.complexity_score <= 10


@pytest.mark.asyncio
async def test_route_low_complexity_assigns_mini(mock_mcp):
    """Simple single-file issue → mini tier."""
    mock_mcp.call_tool.side_effect = [
        {"results": []},
        {"run_id": "run-mini"},
        {"ok": True},
    ]
    agent = RouterAgent(mock_mcp)
    decision = await agent.route(1, "Fix typo", "Fix typo in README.md", "r/r")
    assert decision.coder_model_tier == "mini"
    assert decision.complexity_score <= 5


@pytest.mark.asyncio
async def test_route_high_complexity_assigns_full(mock_mcp):
    """Complex multi-service issue → full tier."""
    body = (
        "Breaking: remove deprecated template, blueprint, workflow, raid fields.\n"
        "Missing test coverage. Affects `apps/api/f1.py`, `apps/api/f2.py`, "
        "`apps/api/f3.py`, `apps/api/f4.py`, `apps/api/f5.py`, `apps/api/f6.py`, "
        "`apps/api/f7.py`, `agents/router_agent.py`, `client/x.tsx`."
    )
    mock_mcp.call_tool.side_effect = [
        {"results": []},
        {"run_id": "run-full"},
        {"ok": True},
    ]
    agent = RouterAgent(mock_mcp)
    decision = await agent.route(99, "Complex refactor", body, "r/r")
    assert decision.coder_model_tier == "full"
    assert decision.complexity_score >= 6


@pytest.mark.asyncio
async def test_route_memory_failure_does_not_block(mock_mcp):
    """Memory lookup failure is silent — routing still succeeds."""
    async def fail_first_then_succeed(tool_name, args=None):
        if tool_name == "memory_search_similar":
            raise Exception("Connection refused")
        if tool_name == "bus_create_run":
            return {"run_id": "run-fallback"}
        return {"ok": True}

    mock_mcp.call_tool.side_effect = fail_first_then_succeed

    agent = RouterAgent(mock_mcp)
    decision = await agent.route(5, "Simple fix", "Fix a bug", "r/r")
    assert decision.run_id == "run-fallback"
    assert decision.similar_issues == []
    assert decision.memory_adjustment == 0


@pytest.mark.asyncio
async def test_route_calls_bus_create_run(mock_mcp):
    """route() always calls bus_create_run to register the task run."""
    mock_mcp.call_tool.side_effect = [
        {"results": []},
        {"run_id": "run-xyz"},
        {"ok": True},
    ]
    agent = RouterAgent(mock_mcp)
    await agent.route(7, "Test issue", "Some body", "owner/repo")

    calls = [c.args[0] for c in mock_mcp.call_tool.call_args_list]
    assert "bus_create_run" in calls
    assert "bus_set_status" in calls


@pytest.mark.asyncio
async def test_route_memory_many_failures_increases_score(mock_mcp):
    """>50% failures in memory → +1 adjustment → higher score."""
    past_issues = [
        {"outcome": "failure", "summary": "template fix", "learnings": []},
        {"outcome": "failure", "summary": "template fix 2", "learnings": []},
        {"outcome": "success", "summary": "template fix 3", "learnings": []},
    ]
    mock_mcp.call_tool.side_effect = [
        {"results": past_issues},   # memory returns 2 failures, 1 success
        {"run_id": "run-adj"},
        {"ok": True},
    ]

    agent = RouterAgent(mock_mcp)
    decision = await agent.route(10, "template fix", "Fix template service", "r/r")
    assert decision.memory_adjustment == 1   # >50% failure rate → +1


@pytest.mark.asyncio
async def test_route_memory_all_success_decreases_score(mock_mcp):
    """100% success rate in memory with ≥2 results → -1 adjustment."""
    past_success = [
        {"outcome": "success", "summary": "s1", "learnings": []},
        {"outcome": "success", "summary": "s2", "learnings": []},
    ]
    mock_mcp.call_tool.side_effect = [
        {"results": past_success},
        {"run_id": "run-easy"},
        {"ok": True},
    ]

    agent = RouterAgent(mock_mcp)
    decision = await agent.route(11, "easy fix", "Fix simple bug", "r/r")
    assert decision.memory_adjustment == -1  # 100% success → -1
    assert decision.complexity_score == max(0, decision.complexity_score)
