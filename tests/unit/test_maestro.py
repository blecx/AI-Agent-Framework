"""Unit tests for agents/maestro.py (issue #715)."""

from __future__ import annotations

import json
from pathlib import Path
from unittest.mock import AsyncMock, MagicMock, patch
import pytest

from agents.maestro import MaestroOrchestrator, OrchestratorResult, _load_server_urls_from_env


# ---------------------------------------------------------------------------
# OrchestratorResult tests
# ---------------------------------------------------------------------------


class TestOrchestratorResult:
    def test_success_true_when_no_error_and_tests_passed(self):
        r = OrchestratorResult(issue_number=1, repo="x/y", tests_passed=True)
        assert r.success is True

    def test_success_false_when_error(self):
        r = OrchestratorResult(issue_number=1, repo="x/y", tests_passed=True, error="boom")
        assert r.success is False

    def test_success_false_when_tests_fail(self):
        r = OrchestratorResult(issue_number=1, repo="x/y", tests_passed=False)
        assert r.success is False

    def test_default_fields(self):
        r = OrchestratorResult(issue_number=42, repo="a/b")
        assert r.run_id is None
        assert r.pr_url is None
        assert r.files_changed == []
        assert r.complexity_score == 0
        assert r.model_tier == "mini"


# ---------------------------------------------------------------------------
# _load_server_urls_from_env tests
# ---------------------------------------------------------------------------


class TestLoadServerUrlsFromEnv:
    def test_returns_defaults_when_no_env(self, monkeypatch):
        monkeypatch.delenv("MAESTRO_MEMORY_URL", raising=False)
        monkeypatch.delenv("MAESTRO_BUS_URL", raising=False)
        monkeypatch.delenv("MAESTRO_GITHUB_URL", raising=False)
        urls = _load_server_urls_from_env()
        assert "mcp-memory" in urls
        assert "mcp-agent-bus" in urls
        assert "mcp-github-ops" in urls

    def test_overrides_from_env(self, monkeypatch):
        monkeypatch.setenv("MAESTRO_MEMORY_URL", "http://custom:9999")
        urls = _load_server_urls_from_env()
        assert urls["mcp-memory"] == "http://custom:9999"


# ---------------------------------------------------------------------------
# MaestroOrchestrator init tests
# ---------------------------------------------------------------------------


class TestMaestroOrchestratorInit:
    def test_custom_server_urls(self):
        urls = {"mcp-memory": "http://x:1234"}
        orq = MaestroOrchestrator(server_urls=urls)
        assert orq._server_urls == urls

    def test_workspace_root_defaults_to_cwd(self):
        orq = MaestroOrchestrator()
        assert orq._root == Path.cwd()

    def test_custom_workspace_root(self, tmp_path: Path):
        orq = MaestroOrchestrator(workspace_root=tmp_path)
        assert orq._root == tmp_path


# ---------------------------------------------------------------------------
# run_issue — error path
# ---------------------------------------------------------------------------


class TestRunIssueError:
    @pytest.mark.asyncio
    async def test_run_issue_captures_exception(self):
        """If pipeline raises, error is captured in result, no re-raise."""
        orq = MaestroOrchestrator()
        with patch("agents.maestro.MCPMultiClient") as MockMCP:
            MockMCP.return_value.__aenter__ = AsyncMock(side_effect=RuntimeError("connect failed"))
            MockMCP.return_value.__aexit__ = AsyncMock(return_value=False)
            result = await orq.run_issue(42, "x/y", "Title", "Body")
        assert result.error is not None
        assert "connect failed" in result.error
        assert result.issue_number == 42
        assert result.repo == "x/y"


# ---------------------------------------------------------------------------
# _create_pr tests
# ---------------------------------------------------------------------------


class TestCreatePr:
    @pytest.mark.asyncio
    async def test_returns_html_url(self):
        mcp = AsyncMock()
        mcp.call_tool.return_value = {"html_url": "https://github.com/x/y/pull/99"}
        orq = MaestroOrchestrator()
        url = await orq._create_pr(mcp, "run-001", 42, "x/y", "Fix bug", ["file.py"])
        assert url == "https://github.com/x/y/pull/99"

    @pytest.mark.asyncio
    async def test_returns_url_fallback(self):
        mcp = AsyncMock()
        mcp.call_tool.return_value = {"url": "https://github.com/x/y/pull/99"}
        orq = MaestroOrchestrator()
        url = await orq._create_pr(mcp, "run-001", 42, "x/y", "Fix bug", ["file.py"])
        assert url == "https://github.com/x/y/pull/99"

    @pytest.mark.asyncio
    async def test_returns_none_on_exception(self):
        mcp = AsyncMock()
        mcp.call_tool.side_effect = RuntimeError("github-ops down")
        orq = MaestroOrchestrator()
        url = await orq._create_pr(mcp, "run-001", 42, "x/y", "Fix bug", [])
        assert url is None

    @pytest.mark.asyncio
    async def test_pr_title_includes_issue_number(self):
        mcp = AsyncMock()
        mcp.call_tool.return_value = {"html_url": "https://github.com/x/y/pull/1"}
        orq = MaestroOrchestrator()
        await orq._create_pr(mcp, "run-001", 42, "x/y", "My feature", [])
        call_args = mcp.call_tool.call_args
        assert call_args[0][0] == "create_pr"
        payload = call_args[0][1]
        assert "42" in payload["title"]

    @pytest.mark.asyncio
    async def test_pr_body_lists_files(self):
        mcp = AsyncMock()
        mcp.call_tool.return_value = {"html_url": "https://x"}
        orq = MaestroOrchestrator()
        await orq._create_pr(mcp, "run-001", 42, "x/y", "T", ["agents/foo.py"])
        payload = mcp.call_tool.call_args[0][1]
        assert "agents/foo.py" in payload["body"]


# ---------------------------------------------------------------------------
# _store_lesson tests
# ---------------------------------------------------------------------------


class TestStoreLesson:
    @pytest.mark.asyncio
    async def test_calls_memory_store_lesson(self):
        from agents.router_agent import RoutingDecision
        from agents.coder_agent import CoderResult

        mcp = AsyncMock()
        orq = MaestroOrchestrator()
        decision = RoutingDecision(
            run_id="r1", issue_number=5, repo="x/y",
            complexity_score=3, model_tier="mini",
            score_breakdown={},
        )
        coder_result = CoderResult(run_id="r1", tests_passed=True, files_changed=["a.py"])
        await orq._store_lesson(mcp, 5, "x/y", decision, coder_result, "https://pr")
        mcp.call_tool.assert_awaited_once()
        args = mcp.call_tool.call_args[0]
        assert args[0] == "memory_store_lesson"
        payload = args[1]
        assert payload["issue_number"] == 5
        assert payload["outcome"] == "success"

    @pytest.mark.asyncio
    async def test_does_not_raise_on_memory_failure(self):
        from agents.router_agent import RoutingDecision
        from agents.coder_agent import CoderResult

        mcp = AsyncMock()
        mcp.call_tool.side_effect = RuntimeError("memory down")
        orq = MaestroOrchestrator()
        decision = RoutingDecision(
            run_id="r1", issue_number=5, repo="x/y",
            complexity_score=3, model_tier="mini",
            score_breakdown={},
        )
        coder_result = CoderResult(run_id="r1", tests_passed=False)
        # Should NOT raise
        await orq._store_lesson(mcp, 5, "x/y", decision, coder_result, None)


# ---------------------------------------------------------------------------
# Full pipeline integration test
# ---------------------------------------------------------------------------


class TestOrchestratorPipeline:
    @pytest.mark.asyncio
    async def test_full_pipeline_happy_path(self, tmp_path: Path):
        from agents.router_agent import RoutingDecision
        from agents.coder_agent import CoderResult

        routing_decision = RoutingDecision(
            run_id="run-999",
            issue_number=42,
            repo="x/y",
            complexity_score=4,
            model_tier="mini",
            score_breakdown={"file_count_score": 2},
        )
        coder_result = CoderResult(
            run_id="run-999",
            files_changed=["agents/x.py"],
            tests_passed=True,
            pr_ready=True,
        )

        with patch("agents.maestro.MCPMultiClient") as MockMCP, \
             patch("agents.maestro.RouterAgent") as MockRouter, \
             patch("agents.maestro.CoderAgent") as MockCoder:

            # async context manager
            mock_mcp_instance = AsyncMock()
            MockMCP.return_value.__aenter__ = AsyncMock(return_value=mock_mcp_instance)
            MockMCP.return_value.__aexit__ = AsyncMock(return_value=False)

            # RouterAgent.route()
            mock_router_instance = MockRouter.return_value
            mock_router_instance.route = AsyncMock(return_value=routing_decision)

            # CoderAgent.run()
            mock_coder_instance = MockCoder.return_value
            mock_coder_instance.run = AsyncMock(return_value=coder_result)

            # create_pr returns url
            mock_mcp_instance.call_tool = AsyncMock(return_value={"html_url": "https://pr.url"})

            orq = MaestroOrchestrator(workspace_root=tmp_path)
            result = await orq.run_issue(42, "x/y", "Title", "Body")

        assert result.success is True
        assert result.run_id == "run-999"
        assert result.pr_url == "https://pr.url"
        assert result.files_changed == ["agents/x.py"]
        assert result.complexity_score == 4
        assert result.model_tier == "mini"

    @pytest.mark.asyncio
    async def test_pipeline_skips_pr_when_not_ready(self, tmp_path: Path):
        from agents.router_agent import RoutingDecision
        from agents.coder_agent import CoderResult

        routing_decision = RoutingDecision(
            run_id="run-000",
            issue_number=1,
            repo="x/y",
            complexity_score=2,
            model_tier="mini",
            score_breakdown={},
        )
        coder_result = CoderResult(
            run_id="run-000",
            tests_passed=False,
            pr_ready=False,
        )

        with patch("agents.maestro.MCPMultiClient") as MockMCP, \
             patch("agents.maestro.RouterAgent") as MockRouter, \
             patch("agents.maestro.CoderAgent") as MockCoder:

            mock_mcp_instance = AsyncMock()
            MockMCP.return_value.__aenter__ = AsyncMock(return_value=mock_mcp_instance)
            MockMCP.return_value.__aexit__ = AsyncMock(return_value=False)

            MockRouter.return_value.route = AsyncMock(return_value=routing_decision)
            MockCoder.return_value.run = AsyncMock(return_value=coder_result)
            mock_mcp_instance.call_tool = AsyncMock(return_value=None)

            orq = MaestroOrchestrator(workspace_root=tmp_path)
            result = await orq.run_issue(1, "x/y", "Title", "Body")

        assert result.pr_url is None
        assert result.tests_passed is False

    @pytest.mark.asyncio
    async def test_pipeline_returns_error_when_coder_fails(self, tmp_path: Path):
        from agents.router_agent import RoutingDecision
        from agents.coder_agent import CoderResult

        routing_decision = RoutingDecision(
            run_id="run-err",
            issue_number=7,
            repo="x/y",
            complexity_score=5,
            model_tier="mini",
            score_breakdown={},
        )
        coder_result = CoderResult(run_id="run-err", error="LLM quota exceeded")

        with patch("agents.maestro.MCPMultiClient") as MockMCP, \
             patch("agents.maestro.RouterAgent") as MockRouter, \
             patch("agents.maestro.CoderAgent") as MockCoder:

            mock_mcp_instance = AsyncMock()
            MockMCP.return_value.__aenter__ = AsyncMock(return_value=mock_mcp_instance)
            MockMCP.return_value.__aexit__ = AsyncMock(return_value=False)

            MockRouter.return_value.route = AsyncMock(return_value=routing_decision)
            MockCoder.return_value.run = AsyncMock(return_value=coder_result)
            mock_mcp_instance.call_tool = AsyncMock(return_value=None)

            orq = MaestroOrchestrator(workspace_root=tmp_path)
            result = await orq.run_issue(7, "x/y", "Title", "Body")

        assert result.error == "LLM quota exceeded"
        assert result.success is False
