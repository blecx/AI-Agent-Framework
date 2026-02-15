#!/usr/bin/env python3
"""Workflow phase service interfaces and default implementations.

This module extracts phase orchestration interfaces from ``WorkflowAgent`` while
preserving existing phase method behavior.
"""

from dataclasses import dataclass, field
from typing import Any, Dict, Protocol


@dataclass
class PhaseExecutionResult:
    """Normalized result for a workflow phase execution."""

    success: bool
    output: Dict[str, Any] = field(default_factory=dict)


class WorkflowPhaseService(Protocol):
    """Interface for workflow phase execution services."""

    phase_key: str

    def execute(self, agent: Any, issue_num: int) -> PhaseExecutionResult:
        """Execute a phase using the provided agent and issue number."""


class MethodDelegatingPhaseService:
    """Default phase service that delegates to an existing WorkflowAgent method."""

    def __init__(self, phase_key: str, method_name: str):
        self.phase_key = phase_key
        self.method_name = method_name

    def execute(self, agent: Any, issue_num: int) -> PhaseExecutionResult:
        method = getattr(agent, self.method_name)
        result = method(issue_num)

        if isinstance(result, tuple):
            success, output = result
            return PhaseExecutionResult(bool(success), output or {})

        return PhaseExecutionResult(bool(result), {})


def build_default_phase_services() -> Dict[str, WorkflowPhaseService]:
    """Build default phase services using existing WorkflowAgent phase methods."""
    return {
        "Phase 1": MethodDelegatingPhaseService("Phase 1", "_phase1_context"),
        "Phase 2": MethodDelegatingPhaseService("Phase 2", "_phase2_planning"),
        "Phase 3": MethodDelegatingPhaseService(
            "Phase 3", "_phase3_implementation"
        ),
        "Phase 4": MethodDelegatingPhaseService("Phase 4", "_phase4_testing"),
        "Phase 5": MethodDelegatingPhaseService("Phase 5", "_phase5_review"),
        "Phase 6": MethodDelegatingPhaseService("Phase 6", "_phase6_merge"),
    }
