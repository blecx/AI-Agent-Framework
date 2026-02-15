#!/usr/bin/env python3
"""Unit tests for explicit and deterministic ErrorRecovery behavior."""

from pathlib import Path

from agents.workflow_agent import ErrorRecovery
from agents.workflow_side_effect_adapters import CommandExecutionResult


class _SideEffectsSuccess:
    def run(self, _command, *, cwd=None, check=True, shell=False):
        return CommandExecutionResult(returncode=0, stdout="", stderr="")


class _SideEffectsFail:
    def run(self, _command, *, cwd=None, check=True, shell=False):
        return CommandExecutionResult(returncode=7, stdout="", stderr="install failed")


def test_attempt_recovery_returns_explicit_message_for_unknown_pattern():
    recovery = ErrorRecovery(
        workspace_root=Path("."), side_effects=_SideEffectsSuccess()
    )

    success, message = recovery.attempt_recovery("unmatched random error", {})

    assert success is False
    assert message == "No known recovery pattern found"


def test_attempt_recovery_returns_explicit_message_for_unsupported_recovery_command():
    recovery = ErrorRecovery(
        workspace_root=Path("."), side_effects=_SideEffectsSuccess()
    )

    success, message = recovery.attempt_recovery("No tests found", {})

    assert success is False
    assert message == (
        "Unsupported recovery command: create_test_file " "(error_type=missing_tests)"
    )


def test_attempt_recovery_returns_explicit_noop_when_handler_returns_false(monkeypatch):
    recovery = ErrorRecovery(
        workspace_root=Path("."), side_effects=_SideEffectsSuccess()
    )
    monkeypatch.setattr(
        recovery, "_remove_unused_import", lambda _error, _context: False
    )

    success, message = recovery.attempt_recovery(
        "'useState' is declared but its value is never read", {}
    )

    assert success is False
    assert message == "Recovery handler explicit no-op: auto_remove_unused_import"
    assert recovery.metrics["auto_recoveries_successful"] == 0
    assert recovery.metrics["user_interventions_avoided"] == 0


def test_attempt_recovery_success_updates_metrics_for_handler_path(monkeypatch):
    recovery = ErrorRecovery(
        workspace_root=Path("."), side_effects=_SideEffectsSuccess()
    )
    monkeypatch.setattr(recovery, "_add_null_to_type", lambda _error, _context: True)

    success, message = recovery.attempt_recovery(
        "Type 'null' is not assignable to type 'string'", {}
    )

    assert success is True
    assert message == "Added | null to type"
    assert recovery.metrics["auto_recoveries_successful"] == 1
    assert recovery.metrics["user_interventions_avoided"] == 1


def test_attempt_recovery_success_updates_metrics_for_install_path():
    recovery = ErrorRecovery(
        workspace_root=Path("."), side_effects=_SideEffectsSuccess()
    )

    success, message = recovery.attempt_recovery("Cannot find module 'axios'", {})

    assert success is True
    assert message == "Installed module: axios"
    assert recovery.metrics["auto_recoveries_successful"] == 1
    assert recovery.metrics["user_interventions_avoided"] == 1


def test_attempt_recovery_maps_install_failure_deterministically():
    recovery = ErrorRecovery(workspace_root=Path("."), side_effects=_SideEffectsFail())

    success, message = recovery.attempt_recovery("Cannot find module 'axios'", {})

    assert success is False
    assert message == "Recovery command failed: npm install axios (exit 7)"
    assert recovery.metrics["auto_recoveries_successful"] == 0


def test_attempt_recovery_maps_handler_exception_deterministically(monkeypatch):
    recovery = ErrorRecovery(
        workspace_root=Path("."), side_effects=_SideEffectsSuccess()
    )

    def _raise(_error, _context):
        raise RuntimeError("boom")

    monkeypatch.setattr(recovery, "_add_null_to_type", _raise)

    success, message = recovery.attempt_recovery(
        "Type 'null' is not assignable to type 'string'", {}
    )

    assert success is False
    assert message == "Recovery handler exception for add_null_to_type: boom"
