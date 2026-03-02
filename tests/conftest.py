"""
Root conftest.py for all tests.

Provides fixtures and configuration that apply to all test directories.
"""

import os
import sys
from pathlib import Path

# Ensure the workspace root is on sys.path so that `import agents.*` and
# `import apps.*` work when pytest is invoked directly (without PYTHONPATH=.).
_WORKSPACE_ROOT = Path(__file__).resolve().parent.parent
if str(_WORKSPACE_ROOT) not in sys.path:
    sys.path.insert(0, str(_WORKSPACE_ROOT))

# Also add apps/api to sys.path so that bare `domain.*` imports used inside
# the API package (e.g. `from domain.audit.constants import ...`) resolve
# correctly when tests are run from the workspace root.
_API_ROOT = _WORKSPACE_ROOT / "apps" / "api"
if str(_API_ROOT) not in sys.path:
    sys.path.insert(0, str(_API_ROOT))

import pytest
from prometheus_client import REGISTRY


def pytest_configure(config):
    """
    Early configuration hook - runs before test collection.
    Clear Prometheus registry to avoid duplicate metric errors across test modules.
    """
    os.environ.pop("PLAYWRIGHT_CONFIG", None)
    # Clear any existing collectors from the registry
    collectors = list(REGISTRY._collector_to_names.keys())
    for collector in collectors:
        try:
            REGISTRY.unregister(collector)
        except Exception:
            pass


@pytest.fixture(autouse=True, scope="session")
def reset_prometheus_registry_session():
    """
    Reset Prometheus registry at the start of the test session.

    This runs once before all tests start, ensuring a clean slate.
    """
    # Clear metrics cache in monitoring_service if it exists
    try:
        from apps.api.services import monitoring_service

        monitoring_service._metrics_cache.clear()
    except (ImportError, AttributeError):
        pass

    # Unregister all collectors from the registry
    collectors = list(REGISTRY._collector_to_names.keys())
    for collector in collectors:
        try:
            REGISTRY.unregister(collector)
        except Exception:
            pass

    yield

    # Cleanup at end of session
    collectors = list(REGISTRY._collector_to_names.keys())
    for collector in collectors:
        try:
            REGISTRY.unregister(collector)
        except Exception:
            pass
