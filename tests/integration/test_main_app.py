"""Coverage-focused integration tests for the FastAPI app in `apps/api/main.py`.

The backend CI uses a strict *changed-files* coverage gate. This file ensures
basic request flows (middleware + key endpoints) are exercised so edits to
`apps/api/main.py` don't get blocked due to missing coverage.
"""

import os
import sys

from fastapi.testclient import TestClient

# Import app via the repo's established pattern (apps/api on sys.path)
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../../apps/api"))

from main import app  # noqa: E402
import main as main_module  # noqa: E402


def test_root_endpoint_has_correlation_id_header():
    client = TestClient(app)

    res = client.get("/")

    assert res.status_code == 200
    assert res.headers.get("X-Correlation-ID")
    payload = res.json()
    assert payload["status"] == "healthy"
    assert payload["api_version"] == "v1"


def test_info_endpoints_work_and_are_version_consistent():
    client = TestClient(app)

    res = client.get("/info")
    assert res.status_code == 200
    assert res.json()["name"]

    res_v1 = client.get("/api/v1/info")
    assert res_v1.status_code == 200
    assert res_v1.json()["api_version"] == "v1"


def test_metrics_endpoint_returns_prometheus_format():
    client = TestClient(app)

    res = client.get("/metrics")

    assert res.status_code == 200
    assert "text/plain" in res.headers.get("content-type", "")
    # Content may be empty if no collectors are registered in a given test run.
    assert isinstance(res.content, (bytes, bytearray))


def test_lifespan_startup_initializes_services_successfully(monkeypatch, tmp_path):
    class DummyLLMService:
        pass

    class DummyAuditService:
        pass

    class FakeGitManager:
        def __init__(self, base_path: str):
            self.base_path = base_path
            self.ensure_called = False

        def ensure_repository(self):
            self.ensure_called = True

    monkeypatch.setenv("PROJECT_DOCS_PATH", str(tmp_path))
    monkeypatch.setattr(main_module, "GitManager", FakeGitManager)
    monkeypatch.setattr(main_module, "LLMService", DummyLLMService)
    monkeypatch.setattr(main_module, "AuditService", DummyAuditService)

    with TestClient(app):
        assert isinstance(app.state.git_manager, FakeGitManager)
        assert app.state.git_manager.ensure_called is True
        assert isinstance(app.state.llm_service, DummyLLMService)
        assert isinstance(app.state.audit_service, DummyAuditService)


def test_lifespan_startup_handles_git_manager_failure(monkeypatch, tmp_path):
    class DummyLLMService:
        pass

    class DummyAuditService:
        pass

    class FailingGitManager:
        def __init__(self, base_path: str):
            self.base_path = base_path

        def ensure_repository(self):
            raise RuntimeError("boom")

    monkeypatch.setenv("PROJECT_DOCS_PATH", str(tmp_path))
    monkeypatch.setattr(main_module, "GitManager", FailingGitManager)
    monkeypatch.setattr(main_module, "LLMService", DummyLLMService)
    monkeypatch.setattr(main_module, "AuditService", DummyAuditService)

    with TestClient(app):
        assert app.state.git_manager is None
        # Startup should continue even if GitManager fails.
        assert isinstance(app.state.llm_service, DummyLLMService)
        assert isinstance(app.state.audit_service, DummyAuditService)
