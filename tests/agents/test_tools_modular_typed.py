#!/usr/bin/env python3
"""Tests for modular agent tools and typed contracts."""

import subprocess
from pathlib import Path

from agents.tools import (
    fetch_github_issue,
    list_github_issues,
    read_file_content,
)
from agents.tooling.filesystem_tools import read_file_content_typed
from agents.tooling.git_tools import create_feature_branch_typed
from agents.tooling.github_tools import (
    fetch_github_issue_typed,
    list_github_issues_typed,
)


class _FakeCalledProcess:
    def __init__(self):
        self.calls = []

    def __call__(self, command, **kwargs):
        self.calls.append({"command": command, "kwargs": kwargs})
        return subprocess.CompletedProcess(command, 0, stdout="", stderr="")


def test_fetch_github_issue_typed_returns_structured_failure(monkeypatch):
    def _fail(*args, **kwargs):
        return subprocess.CompletedProcess(args[0], 1, stdout="", stderr="no auth")

    monkeypatch.setattr(subprocess, "run", _fail)

    result = fetch_github_issue_typed(280, repo="blecx/AI-Agent-Framework")

    assert result.ok is False
    assert result.error is not None
    assert result.error.code == "COMMAND_FAILED"
    assert result.error.message == "Failed to fetch GitHub issue"


def test_fetch_github_issue_legacy_wrapper_keeps_string_compatibility(monkeypatch):
    def _fail(*args, **kwargs):
        return subprocess.CompletedProcess(args[0], 1, stdout="", stderr="denied")

    monkeypatch.setattr(subprocess, "run", _fail)

    result = fetch_github_issue(280, repo="blecx/AI-Agent-Framework")

    assert isinstance(result, str)
    assert result.startswith("Error fetching issue: ")


def test_list_github_issues_typed_rejects_invalid_state():
    result = list_github_issues_typed(
        repo="blecx/AI-Agent-Framework",
        state="invalid",
    )

    assert result.ok is False
    assert result.error is not None
    assert result.error.code == "INVALID_ARGUMENT"
    assert result.error.message == "state must be 'open' or 'closed'"


def test_list_github_issues_legacy_wrapper_keeps_invalid_state_contract():
    result = list_github_issues(
        repo="blecx/AI-Agent-Framework",
        state="invalid",
    )

    assert result == "Error: state must be 'open' or 'closed'"


def test_read_file_content_typed_returns_structured_not_found(tmp_path: Path):
    result = read_file_content_typed(
        "missing.txt",
        base_directory=str(tmp_path),
    )

    assert result.ok is False
    assert result.error is not None
    assert result.error.code == "FILE_NOT_FOUND"


def test_read_file_content_legacy_wrapper_keeps_not_found_string(tmp_path: Path):
    result = read_file_content("missing.txt", base_directory=str(tmp_path))

    assert result == "Error: File missing.txt does not exist"


def test_create_feature_branch_typed_uses_modern_git_switch(monkeypatch):
    fake_run = _FakeCalledProcess()
    monkeypatch.setattr(subprocess, "run", fake_run)

    result = create_feature_branch_typed("feat/issue-280")

    assert result.ok is True
    assert result.value == "Created and checked out branch: feat/issue-280"
    assert fake_run.calls[0]["command"] == ["git", "switch", "main"]
    assert fake_run.calls[2]["command"] == ["git", "switch", "-c", "feat/issue-280"]
