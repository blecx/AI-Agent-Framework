"""Integration/unit coverage tests for Health router.

These tests exist primarily to ensure the health endpoints and helper
functions are covered so the strict CI per-changed-file coverage gate
doesn't fail when health checks evolve.

They are intentionally deterministic (no real network calls; psutil/httpx
are mocked where needed).
"""

import os
import sys
import shutil
import tempfile
from collections import namedtuple
from types import SimpleNamespace

import pytest
from fastapi.testclient import TestClient

# Import the FastAPI app + router module (repo uses apps/api on sys.path)
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../../../apps/api"))

from main import app  # noqa: E402
from routers import health as health_router  # noqa: E402


@pytest.fixture
def temp_docs_dir():
    temp_dir = tempfile.mkdtemp()
    yield temp_dir
    shutil.rmtree(temp_dir)


@pytest.fixture
def client(monkeypatch, temp_docs_dir):
    # Avoid relying on lifespan initialization in tests (other integration tests
    # follow the same approach by setting app.state fields explicitly).
    app.state.llm_service = None
    monkeypatch.setenv("PROJECT_DOCS_PATH", temp_docs_dir)
    return TestClient(app)


def test_health_check_simple_reports_docs_not_initialized(client, temp_docs_dir):
    res = client.get("/health")

    assert res.status_code == 200
    payload = res.json()
    assert payload["status"] == "healthy"
    assert payload["docs_path"] == temp_docs_dir
    assert payload["docs_exists"] is True
    assert payload["docs_is_git"] is False
    assert "docs not initialized" in payload["message"].lower()


def test_health_check_simple_reports_docs_initialized(client, temp_docs_dir):
    os.makedirs(os.path.join(temp_docs_dir, ".git"), exist_ok=True)

    res = client.get("/health")

    assert res.status_code == 200
    payload = res.json()
    assert payload["docs_exists"] is True
    assert payload["docs_is_git"] is True
    assert payload["message"] == "API is running"


def test_health_check_detailed_overall_healthy(client, monkeypatch):
    monkeypatch.setattr(
        health_router,
        "check_git_repository",
        lambda docs_path: {"healthy": True, "message": "ok"},
    )
    monkeypatch.setattr(
        health_router,
        "check_llm_service",
        lambda llm_service: {"healthy": True, "message": "ok"},
    )
    monkeypatch.setattr(
        health_router,
        "check_disk_space",
        lambda path, min_free_gb=1.0: {"healthy": True, "message": "ok"},
    )
    monkeypatch.setattr(
        health_router,
        "check_memory",
        lambda min_free_percent=10.0: {"healthy": True, "message": "ok"},
    )

    res = client.get("/api/v1/health")

    assert res.status_code == 200
    payload = res.json()
    assert payload["status"] == "healthy"
    assert payload["api_version"] == "v1"
    assert "checks" in payload


def test_health_check_detailed_overall_degraded_when_llm_unhealthy(
    client, monkeypatch
):
    monkeypatch.setattr(
        health_router,
        "check_git_repository",
        lambda docs_path: {"healthy": True, "message": "ok"},
    )
    monkeypatch.setattr(
        health_router,
        "check_llm_service",
        lambda llm_service: {"healthy": False, "message": "down"},
    )
    monkeypatch.setattr(
        health_router,
        "check_disk_space",
        lambda path, min_free_gb=1.0: {"healthy": True, "message": "ok"},
    )
    monkeypatch.setattr(
        health_router,
        "check_memory",
        lambda min_free_percent=10.0: {"healthy": True, "message": "ok"},
    )

    res = client.get("/api/v1/health")

    assert res.status_code == 200
    assert res.json()["status"] == "degraded"


def test_health_check_detailed_overall_unhealthy_when_critical_unhealthy(
    client, monkeypatch
):
    monkeypatch.setattr(
        health_router,
        "check_git_repository",
        lambda docs_path: {"healthy": False, "message": "bad"},
    )
    monkeypatch.setattr(
        health_router,
        "check_llm_service",
        lambda llm_service: {"healthy": True, "message": "ok"},
    )
    monkeypatch.setattr(
        health_router,
        "check_disk_space",
        lambda path, min_free_gb=1.0: {"healthy": True, "message": "ok"},
    )
    monkeypatch.setattr(
        health_router,
        "check_memory",
        lambda min_free_percent=10.0: {"healthy": True, "message": "ok"},
    )

    res = client.get("/api/v1/health")

    assert res.status_code == 200
    assert res.json()["status"] == "unhealthy"


# ---------------------------------------------------------------------------
# Helper function tests (mock external deps for determinism)
# ---------------------------------------------------------------------------


def test_check_git_repository_missing_path(tmp_path):
    missing = tmp_path / "does-not-exist"

    status = health_router.check_git_repository(str(missing))

    assert status["healthy"] is False
    assert "does not exist" in status["message"].lower()


def test_check_git_repository_not_git_repo(tmp_path):
    status = health_router.check_git_repository(str(tmp_path))

    assert status["healthy"] is False
    assert "not a git" in status["message"].lower()


def test_check_git_repository_healthy(tmp_path):
    (tmp_path / ".git").mkdir()

    status = health_router.check_git_repository(str(tmp_path))

    assert status["healthy"] is True
    assert status["writable"] is True


def test_check_git_repository_unwritable(tmp_path, monkeypatch):
    (tmp_path / ".git").mkdir()

    def _raise(*_args, **_kwargs):
        raise PermissionError("nope")

    # Patch open used by the module to simulate an unwritable directory
    monkeypatch.setattr(health_router, "open", _raise, raising=False)

    status = health_router.check_git_repository(str(tmp_path))

    assert status["healthy"] is False
    assert "not writable" in status["message"].lower()


def test_check_llm_service_none_is_healthy():
    status = health_router.check_llm_service(None)

    assert status["healthy"] is True
    assert "fallback" in status["message"].lower()


def test_check_llm_service_object_without_config_is_healthy():
    status = health_router.check_llm_service(object())

    assert status["healthy"] is True
    assert "config" in status["message"].lower()


def test_check_llm_service_no_endpoint_configured_is_healthy():
    llm = SimpleNamespace(config={})

    status = health_router.check_llm_service(llm)

    assert status["healthy"] is True
    assert status["endpoint_configured"] is False


def test_check_llm_service_reachable_marks_message(monkeypatch):
    llm = SimpleNamespace(config={"base_url": "http://example.invalid"})

    class _Resp:
        status_code = 200

    monkeypatch.setattr(health_router.httpx, "get", lambda *_a, **_k: _Resp())

    status = health_router.check_llm_service(llm)

    assert status["healthy"] is True
    assert status["endpoint_configured"] is True
    assert "reachable" in status["message"].lower()


def test_check_llm_service_timeout_is_healthy(monkeypatch):
    llm = SimpleNamespace(config={"base_url": "http://example.invalid"})

    def _timeout(*_a, **_k):
        raise health_router.httpx.TimeoutException("timeout")

    monkeypatch.setattr(health_router.httpx, "get", _timeout)

    status = health_router.check_llm_service(llm)

    assert status["healthy"] is True
    assert "timeout" in status["message"].lower()


def test_check_disk_space_healthy(monkeypatch, tmp_path):
    Usage = namedtuple("Usage", ["total", "used", "free", "percent"])
    monkeypatch.setattr(
        health_router.psutil,
        "disk_usage",
        lambda _path: Usage(total=10 * 1024**3, used=1 * 1024**3, free=9 * 1024**3, percent=10.0),
    )

    status = health_router.check_disk_space(str(tmp_path), min_free_gb=1.0)

    assert status["healthy"] is True
    assert "gb free" in status["message"].lower()


def test_check_disk_space_unhealthy(monkeypatch, tmp_path):
    Usage = namedtuple("Usage", ["total", "used", "free", "percent"])
    monkeypatch.setattr(
        health_router.psutil,
        "disk_usage",
        lambda _path: Usage(total=10 * 1024**3, used=9.5 * 1024**3, free=0.5 * 1024**3, percent=95.0),
    )

    status = health_router.check_disk_space(str(tmp_path), min_free_gb=1.0)

    assert status["healthy"] is False
    assert "low disk" in status["message"].lower()


def test_check_memory_healthy(monkeypatch):
    Mem = namedtuple("Mem", ["total", "used", "available", "percent"])
    monkeypatch.setattr(
        health_router.psutil,
        "virtual_memory",
        lambda: Mem(total=10 * 1024**3, used=2 * 1024**3, available=8 * 1024**3, percent=20.0),
    )

    status = health_router.check_memory(min_free_percent=10.0)

    assert status["healthy"] is True
    assert "free" in status["message"].lower()


def test_check_memory_unhealthy(monkeypatch):
    Mem = namedtuple("Mem", ["total", "used", "available", "percent"])
    monkeypatch.setattr(
        health_router.psutil,
        "virtual_memory",
        lambda: Mem(total=10 * 1024**3, used=9.5 * 1024**3, available=0.5 * 1024**3, percent=95.0),
    )

    status = health_router.check_memory(min_free_percent=10.0)

    assert status["healthy"] is False
    assert "low memory" in status["message"].lower()
