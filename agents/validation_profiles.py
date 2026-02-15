"""Canonical validation command profiles for workflow agents.

This module provides a single source of truth for validation command sets used
across workflow orchestration and phase services.
"""

from __future__ import annotations

from typing import List


_PROFILE_MAP = {
    "backend": {
        "full": [
            "python -m black apps/api/",
            "python -m flake8 apps/api/",
            "pytest",
        ],
        "test_only": [
            "python -m black apps/api/",
            "python -m flake8 apps/api/",
            "pytest",
        ],
        "type_only": ["python -m mypy apps/api/"],
        "doc_only": [],
    },
    "client": {
        "full": ["npm run lint", "npm test", "npm run build"],
        "test_only": ["npm run lint", "npm test"],
        "type_only": ["npx tsc --noEmit", "npm run lint"],
        "doc_only": ["npx markdownlint '**/*.md' --ignore node_modules"],
    },
}


def get_validation_commands(repo_type: str, profile: str = "full") -> List[str]:
    """Return validation commands for a repo/profile combination.

    Unknown repo/profile combinations return an empty list.
    """

    repo_profiles = _PROFILE_MAP.get(repo_type)
    if not repo_profiles:
        return []

    commands = repo_profiles.get(profile)
    if not commands:
        return []

    return list(commands)
