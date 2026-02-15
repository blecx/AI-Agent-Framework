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
    _detect_validation_repo_type,
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


class _RepoContextStub:
    def __init__(self, current_repo):
        self.current_repo = current_repo


class _SmartValidationStub:
    def __init__(self):
        self.repo_type = None

    def get_validation_commands(self, repo_type: str):
        self.repo_type = repo_type
        return ["echo validate"]


class _RecoveryStub:
    def attempt_recovery(self, _error_output, _context):
        return False, ""


class _AgentStub:
    def __init__(self, repo_type):
        self.cross_repo_context = _RepoContextStub(repo_type)
        self.smart_validation = _SmartValidationStub()
        self.error_recovery = _RecoveryStub()
        self.commands = []

    def log(self, _message, _level):
        return None

    def run_command(self, command, _description, check=False):
        self.commands.append(command)

        class _Result:
            returncode = 0
            stdout = ""
            stderr = ""

        return _Result()

    def check_known_problem(self, _error_output):
        return None


class _IssuePreflightStub:
    def fetch_issue_data(self, _issue_num):
        return None

    def validate_issue(self, _issue_data):
        return True, []


class _ContextAgentStub:
    def __init__(self, interactive=False):
        self.dry_run = False
        self.interactive = interactive
        self.issue_preflight = _IssuePreflightStub()
        self.prompt_count = 0

    def log(self, _message, _level):
        return None

    def run_command(self, _command, _description):
        class _Result:
            returncode = 0
            stdout = "Issue title\nIssue body"
            stderr = ""

        return _Result()


def test_detect_validation_repo_type_uses_cross_repo_context_when_client():
    agent = _AgentStub("client")

    assert _detect_validation_repo_type(agent) == "client"


def test_detect_validation_repo_type_defaults_to_backend_when_unknown():
    agent = _AgentStub("unknown")

    assert _detect_validation_repo_type(agent) == "backend"


def test_testing_phase_service_uses_client_repo_context_for_validation_scope():
    service = TestingPhaseService()
    agent = _AgentStub("client")

    result = service.execute(agent, 294)

    assert result.success is True
    assert agent.smart_validation.repo_type == "client"
    assert any(
        command.startswith("cd _external/AI-Agent-Framework-Client &&")
        for command in agent.commands
    )


def test_testing_phase_service_uses_backend_repo_context_for_validation_scope():
    service = TestingPhaseService()
    agent = _AgentStub("backend")

    result = service.execute(agent, 294)

    assert result.success is True
    assert agent.smart_validation.repo_type == "backend"
    assert all(
        not command.startswith("cd _external/AI-Agent-Framework-Client &&")
        for command in agent.commands
    )


def test_context_phase_service_skips_prompts_in_non_interactive_mode(monkeypatch):
    service = ContextPhaseService()
    agent = _ContextAgentStub(interactive=False)

    def _failing_input(_message):
        raise AssertionError("input() should not be called in non-interactive mode")

    monkeypatch.setattr("builtins.input", _failing_input)

    result = service.execute(agent, 295)

    assert result.success is True


def test_context_phase_service_prompts_when_interactive_mode_enabled(monkeypatch):
    service = ContextPhaseService()
    agent = _ContextAgentStub(interactive=True)
    prompts = []

    def _recording_input(message):
        prompts.append(message)
        return ""

    monkeypatch.setattr("builtins.input", _recording_input)

    result = service.execute(agent, 295)

    assert result.success is True
    assert prompts == ["Press Enter when ready to continue to Planning phase..."]
