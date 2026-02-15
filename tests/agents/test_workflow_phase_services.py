#!/usr/bin/env python3
"""Tests for extracted workflow phase service interfaces and dispatch."""

from pathlib import Path

from agents.base_agent import AgentPhase
from agents.workflow_agent import WorkflowAgent
from agents.workflow_phase_services import (
    MethodDelegatingPhaseService,
    PhaseExecutionResult,
    build_default_phase_services,
)


class _BoolAgent:
    def run_phase(self, issue_num: int) -> bool:  # pragma: no cover - simple helper
        return issue_num > 0


class _TupleAgent:
    def run_phase(self, issue_num: int):  # pragma: no cover - simple helper
        return (issue_num > 0, {"issue": issue_num})


def test_method_delegating_phase_service_normalizes_bool_result():
    service = MethodDelegatingPhaseService("Phase 1", "run_phase")
    result = service.execute(_BoolAgent(), 273)

    assert isinstance(result, PhaseExecutionResult)
    assert result.success is True
    assert result.output == {}


def test_method_delegating_phase_service_normalizes_tuple_result():
    service = MethodDelegatingPhaseService("Phase 4", "run_phase")
    result = service.execute(_TupleAgent(), 273)

    assert isinstance(result, PhaseExecutionResult)
    assert result.success is True
    assert result.output == {"issue": 273}


def test_build_default_phase_services_contains_all_six_phases():
    services = build_default_phase_services()

    assert set(services.keys()) == {
        "Phase 1",
        "Phase 2",
        "Phase 3",
        "Phase 4",
        "Phase 5",
        "Phase 6",
    }


def test_workflow_agent_executes_phase_using_phase_service(tmp_path):
    kb_dir = Path(tmp_path) / "kb"
    agent = WorkflowAgent(kb_dir=kb_dir)

    class StubService:
        phase_key = "Phase 1"

        def execute(self, workflow_agent: WorkflowAgent, issue_num: int):
            return PhaseExecutionResult(True, {"source": "stub"})

    agent.phase_services = {"Phase 1": StubService()}
    phase = AgentPhase("Phase 1: Context", "Read issue and gather context")

    success = agent._execute_phase(phase, 273)

    assert success is True
    assert phase.completed is True
