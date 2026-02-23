"""
Root conftest.py for all tests.

Provides fixtures and configuration that apply to all test directories.
"""

import os
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
