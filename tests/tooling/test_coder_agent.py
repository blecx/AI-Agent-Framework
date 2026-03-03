"""Unit tests for agents/coder_agent.py (issue #714)."""

from __future__ import annotations

import asyncio
import json
from pathlib import Path
from unittest.mock import AsyncMock, MagicMock, patch, call
import pytest

from agents.coder_agent import CoderAgent, CoderResult, MAX_VALIDATION_RETRIES


# ---------------------------------------------------------------------------
# Fixtures / helpers
# ---------------------------------------------------------------------------

def _make_mcp() -> AsyncMock:
    """Return a mock MCPMultiClient."""
    mcp = AsyncMock()
    return mcp


def _make_llm(response_json: dict | None = None) -> MagicMock:
    """Return a mock AsyncOpenAI client that returns *response_json* as content."""
    content = json.dumps(response_json or {"phase": "planning", "goal": "test", "files": [], "acceptance_criteria": [], "validation_commands": []})
    choice = MagicMock()
    choice.message.content = content
    completion = MagicMock()
    completion.choices = [choice]

    llm = MagicMock()
    llm.chat = MagicMock()
    llm.chat.completions = MagicMock()
    llm.chat.completions.create = AsyncMock(return_value=completion)
    return llm


def _make_packet(
    status: str = "created",
    plan: dict | None = None,
    validation_results: list | None = None,
) -> dict:
    return {
        "run": {
            "run_id": "run-001",
            "issue_number": 42,
            "repo": "blecx/AI-Agent-Framework",
            "status": status,
        },
        "plan": plan,
        "snapshots": [],
        "validation_results": validation_results or [],
    }


# ---------------------------------------------------------------------------
# CoderResult tests
# ---------------------------------------------------------------------------


class TestCoderResult:
    def test_success_property_true_when_no_error_and_tests_passed(self):
        r = CoderResult(run_id="x", tests_passed=True)
        assert r.success is True

    def test_success_property_false_when_error(self):
        r = CoderResult(run_id="x", tests_passed=True, error="boom")
        assert r.success is False

    def test_success_property_false_when_tests_not_passed(self):
        r = CoderResult(run_id="x", tests_passed=False)
        assert r.success is False

    def test_pr_ready_default_false(self):
        r = CoderResult(run_id="x")
        assert r.pr_ready is False

    def test_files_changed_default_empty(self):
        r = CoderResult(run_id="x")
        assert r.files_changed == []


# ---------------------------------------------------------------------------
# CoderAgent instantiation tests
# ---------------------------------------------------------------------------


class TestCoderAgentInit:
    def test_model_mini(self):
        mcp = _make_mcp()
        agent = CoderAgent(mcp, model_tier="mini")
        assert agent._model == "gpt-4o-mini"

    def test_model_full(self):
        mcp = _make_mcp()
        agent = CoderAgent(mcp, model_tier="full")
        assert agent._model == "gpt-4o"

    def test_model_unknown_defaults_to_mini(self):
        mcp = _make_mcp()
        agent = CoderAgent(mcp, model_tier="unknown")
        assert agent._model == "gpt-4o-mini"

    def test_workspace_root_default_is_cwd(self):
        mcp = _make_mcp()
        agent = CoderAgent(mcp)
        assert agent._root == Path.cwd()

    def test_custom_workspace_root(self, tmp_path: Path):
        mcp = _make_mcp()
        agent = CoderAgent(mcp, workspace_root=tmp_path)
        assert agent._root == tmp_path


# ---------------------------------------------------------------------------
# _chat tests
# ---------------------------------------------------------------------------


class TestCoderAgentChat:
    @pytest.mark.asyncio
    async def test_chat_builds_message_history(self):
        mcp = _make_mcp()
        llm = _make_llm({"phase": "planning", "goal": "g", "files": [], "acceptance_criteria": [], "validation_commands": []})
        agent = CoderAgent(mcp, llm_client=llm)
        reply = await agent._chat("hello")
        assert isinstance(reply, str)
        # system + user + assistant
        assert len(agent._messages) == 3
        assert agent._messages[0]["role"] == "system"
        assert agent._messages[1]["role"] == "user"
        assert agent._messages[2]["role"] == "assistant"

    @pytest.mark.asyncio
    async def test_chat_accumulates_history_on_second_call(self):
        mcp = _make_mcp()
        llm = _make_llm()
        agent = CoderAgent(mcp, llm_client=llm)
        await agent._chat("first")
        await agent._chat("second")
        # system + (user + assistant) * 2
        assert len(agent._messages) == 5

    @pytest.mark.asyncio
    async def test_chat_uses_correct_model(self):
        mcp = _make_mcp()
        llm = _make_llm()
        agent = CoderAgent(mcp, model_tier="full", llm_client=llm)
        await agent._chat("msg")
        llm.chat.completions.create.assert_awaited_once()
        kwargs = llm.chat.completions.create.call_args
        assert kwargs.kwargs.get("model") == "gpt-4o" or kwargs.args[0] if kwargs.args else True
        # Check model in call_args
        call_kwargs = llm.chat.completions.create.call_args.kwargs
        assert call_kwargs["model"] == "gpt-4o"


# ---------------------------------------------------------------------------
# _generate_plan tests
# ---------------------------------------------------------------------------


class TestGeneratePlan:
    @pytest.mark.asyncio
    async def test_returns_parsed_json(self):
        mcp = _make_mcp()
        plan_response = {
            "phase": "planning",
            "goal": "Implement X",
            "files": ["agents/x.py"],
            "acceptance_criteria": ["Tests pass"],
            "validation_commands": ["pytest"],
            "estimated_minutes": 20,
        }
        llm = _make_llm(plan_response)
        agent = CoderAgent(mcp, llm_client=llm)
        packet = _make_packet()
        plan = await agent._generate_plan(packet)
        assert plan["goal"] == "Implement X"
        assert plan["files"] == ["agents/x.py"]

    @pytest.mark.asyncio
    async def test_returns_fallback_on_invalid_json(self):
        mcp = _make_mcp()
        # Make LLM return invalid JSON
        choice = MagicMock()
        choice.message.content = "not valid json {{{"
        completion = MagicMock()
        completion.choices = [choice]
        llm = MagicMock()
        llm.chat.completions.create = AsyncMock(return_value=completion)
        agent = CoderAgent(mcp, llm_client=llm)
        packet = _make_packet()
        plan = await agent._generate_plan(packet)
        assert "files" in plan
        assert plan["files"] == []


# ---------------------------------------------------------------------------
# _implement tests
# ---------------------------------------------------------------------------


class TestImplement:
    @pytest.mark.asyncio
    async def test_writes_files_and_calls_snapshot(self, tmp_path: Path):
        mcp = _make_mcp()
        code_response = {
            "phase": "coding",
            "file_edits": [
                {"filepath": "agents/new_file.py", "content": "# new\n"},
            ],
            "validation_commands": ["pytest"],
        }
        llm = _make_llm(code_response)
        agent = CoderAgent(mcp, llm_client=llm, workspace_root=tmp_path)
        packet = _make_packet(status="approved", plan={"validation_cmds": ["pytest"]})
        files = await agent._implement("run-001", packet)
        assert "agents/new_file.py" in files
        assert (tmp_path / "agents" / "new_file.py").exists()
        mcp.call_tool.assert_any_await("bus_write_snapshot", {
            "run_id": "run-001",
            "filepath": "agents/new_file.py",
            "content_before": None,
            "content_after": "# new\n",
        })

    @pytest.mark.asyncio
    async def test_returns_empty_on_invalid_json(self, tmp_path: Path):
        mcp = _make_mcp()
        choice = MagicMock()
        choice.message.content = "not json"
        completion = MagicMock()
        completion.choices = [choice]
        llm = MagicMock()
        llm.chat.completions.create = AsyncMock(return_value=completion)
        agent = CoderAgent(mcp, llm_client=llm, workspace_root=tmp_path)
        packet = _make_packet()
        files = await agent._implement("run-001", packet)
        assert files == []

    @pytest.mark.asyncio
    async def test_skips_edits_with_empty_filepath(self, tmp_path: Path):
        mcp = _make_mcp()
        code_response = {
            "phase": "coding",
            "file_edits": [{"filepath": "", "content": "x"}],
            "validation_commands": [],
        }
        llm = _make_llm(code_response)
        agent = CoderAgent(mcp, llm_client=llm, workspace_root=tmp_path)
        packet = _make_packet()
        files = await agent._implement("run-001", packet)
        assert files == []


# ---------------------------------------------------------------------------
# _run_command tests
# ---------------------------------------------------------------------------


class TestRunCommand:
    @pytest.mark.asyncio
    async def test_passing_command(self, tmp_path: Path):
        mcp = _make_mcp()
        agent = CoderAgent(mcp, workspace_root=tmp_path)
        passed, stdout, stderr, rc = await agent._run_command("echo hello")
        assert passed is True
        assert "hello" in stdout
        assert rc == 0

    @pytest.mark.asyncio
    async def test_failing_command(self, tmp_path: Path):
        mcp = _make_mcp()
        agent = CoderAgent(mcp, workspace_root=tmp_path)
        passed, stdout, stderr, rc = await agent._run_command("exit 1")
        assert passed is False
        assert rc == 1

    @pytest.mark.asyncio
    async def test_timeout_returns_failure(self, tmp_path: Path):
        mcp = _make_mcp()
        agent = CoderAgent(mcp, workspace_root=tmp_path)
        with patch("asyncio.wait_for", side_effect=asyncio.TimeoutError):
            passed, stdout, stderr, rc = await agent._run_command("sleep 9999")
        assert passed is False
        assert "timed out" in stderr.lower()


# ---------------------------------------------------------------------------
# _validate_with_retry tests
# ---------------------------------------------------------------------------


class TestValidateWithRetry:
    @pytest.mark.asyncio
    async def test_returns_true_when_no_commands(self, tmp_path: Path):
        mcp = _make_mcp()
        agent = CoderAgent(mcp, workspace_root=tmp_path)
        result = await agent._validate_with_retry("run-001", [])
        assert result is True

    @pytest.mark.asyncio
    async def test_returns_true_on_passing_command(self, tmp_path: Path):
        mcp = _make_mcp()
        agent = CoderAgent(mcp, workspace_root=tmp_path)
        result = await agent._validate_with_retry("run-001", ["echo ok"])
        assert result is True
        mcp.call_tool.assert_any_await("bus_write_validation", {
            "run_id": "run-001",
            "command": "echo ok",
            "stdout": "ok\n",
            "stderr": "",
            "exit_code": 0,
            "passed": True,
        })

    @pytest.mark.asyncio
    async def test_retries_on_failure_and_reads_packet(self, tmp_path: Path):
        """Should retry up to MAX_VALIDATION_RETRIES times and ask LLM to fix."""
        mcp = _make_mcp()
        mcp.call_tool.side_effect = [
            # First call: bus_write_validation (fail)
            None,
            # Next call: bus_read_context_packet for retry
            _make_packet(status="coding", validation_results=[{"command": "exit 1", "passed": False}]),
            # Second write_validation
            None,
            # Second read_context_packet for retry
            _make_packet(status="coding", validation_results=[{"command": "exit 1", "passed": False}]),
            # Third write_validation
            None,
        ]
        fix_response = {
            "phase": "coding",
            "file_edits": [],
            "validation_commands": ["exit 1"],
        }
        llm = _make_llm(fix_response)
        agent = CoderAgent(mcp, llm_client=llm, workspace_root=tmp_path)
        result = await agent._validate_with_retry("run-001", ["exit 1"])
        assert result is False
        # Should have retried MAX_VALIDATION_RETRIES times
        assert llm.chat.completions.create.call_count == MAX_VALIDATION_RETRIES - 1


# ---------------------------------------------------------------------------
# _wait_for_approval tests
# ---------------------------------------------------------------------------


class TestWaitForApproval:
    @pytest.mark.asyncio
    async def test_returns_true_when_approved(self):
        mcp = _make_mcp()
        mcp.call_tool.return_value = _make_packet(status="approved")
        agent = CoderAgent(mcp)
        with patch("agents.coder_agent.APPROVAL_POLL_INTERVAL_SEC", 0.01), \
             patch("agents.coder_agent.APPROVAL_TIMEOUT_SEC", 0.5):
            result = await agent._wait_for_approval("run-001")
        assert result is True

    @pytest.mark.asyncio
    async def test_returns_false_on_timeout(self):
        mcp = _make_mcp()
        mcp.call_tool.return_value = _make_packet(status="awaiting_approval")
        agent = CoderAgent(mcp)
        with patch("agents.coder_agent.APPROVAL_POLL_INTERVAL_SEC", 0.01), \
             patch("agents.coder_agent.APPROVAL_TIMEOUT_SEC", 0.04):
            result = await agent._wait_for_approval("run-001")
        assert result is False

    @pytest.mark.asyncio
    async def test_returns_false_when_failed(self):
        mcp = _make_mcp()
        mcp.call_tool.return_value = _make_packet(status="failed")
        agent = CoderAgent(mcp)
        with patch("agents.coder_agent.APPROVAL_POLL_INTERVAL_SEC", 0.01), \
             patch("agents.coder_agent.APPROVAL_TIMEOUT_SEC", 0.5):
            result = await agent._wait_for_approval("run-001")
        assert result is False


# ---------------------------------------------------------------------------
# Full run() integration tests
# ---------------------------------------------------------------------------


class TestCoderAgentRun:
    @pytest.mark.asyncio
    async def test_run_captures_exceptions_as_error(self):
        mcp = _make_mcp()
        mcp.call_tool.side_effect = RuntimeError("MCP down")
        agent = CoderAgent(mcp)
        result = await agent.run("run-001")
        assert result.error is not None
        assert "MCP down" in result.error

    @pytest.mark.asyncio
    async def test_run_happy_path(self, tmp_path: Path):
        """Full happy path: plan → approve → code → validate → done."""
        mcp = _make_mcp()

        call_responses = {
            "bus_read_context_packet": [
                _make_packet(status="created", plan=None),  # first read
                _make_packet(status="approved", plan={"validation_cmds": ["echo ok"]}),  # after approval
            ],
            "bus_set_status": None,
            "bus_write_plan": None,
            "bus_write_checkpoint": None,
            "bus_write_snapshot": None,
            "bus_write_validation": None,
        }

        read_packet_calls = iter(call_responses["bus_read_context_packet"])

        async def call_tool_side_effect(tool_name, args):
            if tool_name == "bus_read_context_packet":
                pkt = next(read_packet_calls)
                return pkt
            return None

        mcp.call_tool.side_effect = call_tool_side_effect

        plan_response = {
            "phase": "planning",
            "goal": "Implement feature X",
            "files": ["agents/x.py"],
            "acceptance_criteria": ["tests pass"],
            "validation_commands": ["echo ok"],
            "estimated_minutes": 10,
        }
        code_response = {
            "phase": "coding",
            "file_edits": [{"filepath": "agents/x.py", "content": "x = 1\n"}],
            "validation_commands": ["echo ok"],
        }

        call_count = [0]
        async def create_completion(**kwargs):
            call_count[0] += 1
            resp_data = plan_response if call_count[0] == 1 else code_response
            choice = MagicMock()
            choice.message.content = json.dumps(resp_data)
            completion = MagicMock()
            completion.choices = [choice]
            return completion

        llm = MagicMock()
        llm.chat.completions.create = AsyncMock(side_effect=create_completion)

        # Patch approval wait to return True immediately
        with patch.object(CoderAgent, "_wait_for_approval", AsyncMock(return_value=True)):
            agent = CoderAgent(mcp, llm_client=llm, workspace_root=tmp_path)
            result = await agent.run("run-001")

        assert result.error is None
        assert result.tests_passed is True
        assert result.pr_ready is True
        assert "agents/x.py" in result.files_changed
        assert (tmp_path / "agents" / "x.py").exists()
