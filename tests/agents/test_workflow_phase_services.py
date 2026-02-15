#!/usr/bin/env python3
"""Tests for extracted workflow phase service interfaces and dispatch."""

from pathlib import Path

from agents.base_agent import AgentPhase
from agents.workflow_agent import WorkflowAgent
from agents.workflow_phase_services import (
    ContextPhaseService,
    ImplementationPhaseService,
    MethodDelegatingPhaseService,
    PlanningPhaseService,
    PrMergePhaseService,
    PhaseExecutionResult,
    ReviewPhaseService,
    TestingPhaseService,
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

    assert isinstance(services["Phase 1"], ContextPhaseService)
    assert isinstance(services["Phase 2"], PlanningPhaseService)
    assert isinstance(services["Phase 3"], ImplementationPhaseService)
    assert isinstance(services["Phase 4"], TestingPhaseService)
    assert isinstance(services["Phase 5"], ReviewPhaseService)
    assert isinstance(services["Phase 6"], PrMergePhaseService)


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


def test_workflow_agent_default_phase_delegation_no_longer_uses_phase_methods(tmp_path):
    agent = WorkflowAgent(kb_dir=Path(tmp_path) / "kb")

    assert not hasattr(agent, "_phase1_context")
    assert not hasattr(agent, "_phase2_planning")
    assert not hasattr(agent, "_phase3_implementation")
    assert not hasattr(agent, "_phase4_testing")
    assert not hasattr(agent, "_phase5_review")
    assert not hasattr(agent, "_phase6_merge")


def test_workflow_agent_execute_regression_with_stubbed_phase_services(tmp_path):
    kb_dir = Path(tmp_path) / "kb"
    agent = WorkflowAgent(kb_dir=kb_dir)
    agent.dry_run = True

    class SuccessService:
        def execute(self, workflow_agent: WorkflowAgent, issue_num: int):
            return PhaseExecutionResult(True, {"issue": issue_num})

    agent.phase_services = {
        "Phase 1": SuccessService(),
        "Phase 2": SuccessService(),
        "Phase 3": SuccessService(),
        "Phase 4": SuccessService(),
        "Phase 5": SuccessService(),
        "Phase 6": SuccessService(),
    }

    success = agent.execute(275)

    assert success is True
    assert all(phase.completed for phase in agent.phases)
