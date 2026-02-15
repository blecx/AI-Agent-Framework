#!/usr/bin/env python3
"""Tests for workflow side-effect adapters and failure mapping."""

from pathlib import Path

from agents.workflow_agent import CrossRepoContext, ParallelValidator, SmartValidation
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
