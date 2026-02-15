#!/usr/bin/env python3
"""Tests for centralized validation command profiles."""

from agents.validation_profiles import get_validation_commands


def test_get_validation_commands_returns_backend_full_profile():
    assert get_validation_commands("backend", "full") == [
        "python -m black apps/api/",
        "python -m flake8 apps/api/",
        "pytest",
    ]


def test_get_validation_commands_returns_client_full_profile():
    assert get_validation_commands("client", "full") == [
        "npm run lint",
        "npm test",
        "npm run build",
    ]


def test_get_validation_commands_handles_unknown_repo_or_profile():
    assert get_validation_commands("unknown", "full") == []
    assert get_validation_commands("backend", "unknown") == []
