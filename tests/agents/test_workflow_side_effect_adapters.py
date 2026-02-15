#!/usr/bin/env python3
"""Tests for workflow side-effect adapters and failure mapping."""

from pathlib import Path

from agents.workflow_agent import (
    CrossRepoContext,
    ParallelValidator,
    SmartValidation,
    WorkflowAgent,
)
from agents.validation_profiles import get_validation_commands
from agents.workflow_side_effect_adapters import (
    CommandExecutionResult,
    SubprocessWorkflowSideEffectAdapter,
    WorkflowSideEffectError,
)


class _FailingAdapter:
    def run(self, command, *, cwd=None, check=True, shell=False):
        raise WorkflowSideEffectError("boom", command=str(command))

    async def run_async_shell(self, command: str, *, cwd=None):
        raise WorkflowSideEffectError("async boom", command=command)


class _StubAdapter:
    def __init__(self, *, stdout: str = "", returncode: int = 0):
        self.stdout = stdout
        self.returncode = returncode

    def run(self, command, *, cwd=None, check=True, shell=False):
        return CommandExecutionResult(
            returncode=self.returncode,
            stdout=self.stdout,
            stderr="",
        )

    async def run_async_shell(self, command: str, *, cwd=None):
        return CommandExecutionResult(returncode=0, stdout="ok", stderr="")


class _RecordingAdapter:
    def __init__(self):
        self.calls = []

    def run(self, command, *, cwd=None, check=True, shell=False):
        self.calls.append(
            {
                "command": command,
                "cwd": cwd,
                "check": check,
                "shell": shell,
            }
        )
        return CommandExecutionResult(returncode=0, stdout="via-adapter", stderr="")

    async def run_async_shell(self, command: str, *, cwd=None):
        return CommandExecutionResult(returncode=0, stdout="ok", stderr="")


class _ErroringAdapter:
    def run(self, command, *, cwd=None, check=True, shell=False):
        raise WorkflowSideEffectError(
            "forced adapter failure",
            command=str(command),
            returncode=7,
            stderr="boom",
        )

    async def run_async_shell(self, command: str, *, cwd=None):
        raise WorkflowSideEffectError("async failure", command=command)


def test_subprocess_adapter_run_success_returns_normalized_result():
    adapter = SubprocessWorkflowSideEffectAdapter()

    result = adapter.run(["python3", "-c", "print('ok')"], check=True)

    assert result.returncode == 0
    assert result.stdout.strip() == "ok"
    assert result.stderr == ""


def test_subprocess_adapter_run_failure_raises_standardized_error():
    adapter = SubprocessWorkflowSideEffectAdapter()

    try:
        adapter.run(["python3", "-c", "import sys; sys.exit(3)"], check=True)
        assert False, "Expected WorkflowSideEffectError"
    except WorkflowSideEffectError as exc:
        assert exc.returncode == 3
        assert "python3 -c import sys; sys.exit(3)" in (exc.command or "")


def test_subprocess_adapter_run_failure_with_check_false_preserves_behavior():
    adapter = SubprocessWorkflowSideEffectAdapter()

    result = adapter.run(["python3", "-c", "import sys; sys.exit(4)"], check=False)

    assert result.returncode == 4


def test_cross_repo_context_maps_adapter_errors_to_unknown_repo():
    context = CrossRepoContext(side_effects=_FailingAdapter())

    assert context.current_repo == "unknown"
    assert context.pr_repo == "unknown"


def test_smart_validation_defaults_to_full_when_adapter_fails():
    validator = SmartValidation(
        workspace_root=Path("."),
        side_effects=_FailingAdapter(),
    )

    assert validator.analyze_changes() == {
        "doc_only": False,
        "test_only": False,
        "type_only": False,
        "full": True,
    }


async def test_parallel_validator_maps_async_adapter_errors_to_failure_result():
    results = await ParallelValidator.validate_pr_parallel(
        Path("."), ["echo ok"], side_effects=_FailingAdapter()
    )

    assert "echo ok" in results
    code, _stdout, stderr = results["echo ok"]
    assert code == 1
    assert "async boom" in stderr


def test_cross_repo_context_uses_adapter_output_when_available():
    context = CrossRepoContext(
        side_effects=_StubAdapter(stdout="git@github.com:blecx/AI-Agent-Framework.git")
    )

    assert context.current_repo == "backend"
    assert context.pr_repo == "blecx/AI-Agent-Framework"


def test_cross_repo_context_validation_commands_use_canonical_profile():
    context = CrossRepoContext(
        side_effects=_StubAdapter(stdout="git@github.com:blecx/AI-Agent-Framework.git")
    )

    assert context.get_validation_commands() == get_validation_commands(
        "backend", "full"
    )


def test_smart_validation_uses_canonical_profiles_for_change_modes():
    validator = SmartValidation(workspace_root=Path("."), side_effects=_StubAdapter())

    validator.analyze_changes = lambda: {
        "doc_only": True,
        "test_only": False,
        "type_only": False,
        "full": False,
    }
    assert validator.get_validation_commands("client") == get_validation_commands(
        "client", "doc_only"
    )

    validator.analyze_changes = lambda: {
        "doc_only": False,
        "test_only": True,
        "type_only": False,
        "full": False,
    }
    assert validator.get_validation_commands("backend") == get_validation_commands(
        "backend", "test_only"
    )

    validator.analyze_changes = lambda: {
        "doc_only": False,
        "test_only": False,
        "type_only": True,
        "full": False,
    }
    assert validator.get_validation_commands("client") == get_validation_commands(
        "client", "type_only"
    )

    validator.analyze_changes = lambda: {
        "doc_only": False,
        "test_only": False,
        "type_only": False,
        "full": True,
    }
    assert validator.get_validation_commands("backend") == get_validation_commands(
        "backend", "full"
    )


def test_workflow_agent_run_command_delegates_to_side_effect_adapter(tmp_path):
    agent = WorkflowAgent(kb_dir=tmp_path / "kb")
    adapter = _RecordingAdapter()
    agent.side_effects = adapter

    result = agent.run_command("echo test", check=True)

    assert result.returncode == 0
    assert result.stdout == "via-adapter"
    assert len(adapter.calls) == 1
    assert adapter.calls[0]["command"] == "echo test"
    assert adapter.calls[0]["shell"] is True
    assert adapter.calls[0]["check"] is True


def test_workflow_agent_run_command_maps_adapter_failure_when_check_false(tmp_path):
    agent = WorkflowAgent(kb_dir=tmp_path / "kb")
    agent.side_effects = _ErroringAdapter()

    result = agent.run_command("echo test", check=False)

    assert result.returncode == 7
    assert result.stderr == "boom"


def test_workflow_agent_run_command_raises_standardized_error_when_check_true(
    tmp_path,
):
    agent = WorkflowAgent(kb_dir=tmp_path / "kb")
    agent.side_effects = _ErroringAdapter()

    try:
        agent.run_command("echo test", check=True)
        assert False, "Expected WorkflowSideEffectError"
    except WorkflowSideEffectError as exc:
        assert exc.returncode == 7
        assert exc.stderr == "boom"
