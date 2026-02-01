"""Unit tests for TUI automation service."""

import pytest
from unittest.mock import Mock, patch, MagicMock
import subprocess
import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from helpers.tui_automation import TUIAutomation, TUIResult, TUIAssertions


class TestTUIResult:
    """Test TUIResult dataclass."""

    def test_success_property(self):
        """Test success property returns correct value."""
        result = TUIResult(exit_code=0, stdout="ok", stderr="", duration=0.5)
        assert result.success is True

        result = TUIResult(exit_code=1, stdout="", stderr="error", duration=0.5)
        assert result.success is False

    def test_contains_method(self):
        """Test contains method checks stdout and stderr."""
        result = TUIResult(exit_code=0, stdout="hello world", stderr="", duration=0.5)
        assert result.contains("hello") is True
        assert result.contains("missing") is False

        result = TUIResult(exit_code=0, stdout="", stderr="error message", duration=0.5)
        assert result.contains("error") is True

    def test_match_method(self):
        """Test match method uses regex."""
        result = TUIResult(
            exit_code=0, stdout="Project TEST-001 created", stderr="", duration=0.5
        )
        match = result.match(r"Project (TEST-\d+) created")
        assert match is not None
        assert match.group(1) == "TEST-001"


class TestTUIAutomation:
    """Test TUIAutomation service."""

    def test_init_sets_defaults(self):
        """Test initialization sets correct defaults."""
        tui = TUIAutomation()
        assert tui.api_base_url == "http://localhost:8000"
        assert tui.env["API_BASE_URL"] == "http://localhost:8000"
        assert tui.env["API_TIMEOUT"] == "30"

    def test_init_accepts_custom_values(self):
        """Test initialization accepts custom values."""
        tui = TUIAutomation(
            tui_path="custom/path/main.py", api_base_url="http://custom:9000"
        )
        assert str(tui.tui_path) == "custom/path/main.py"
        assert tui.api_base_url == "http://custom:9000"
        assert tui.env["API_BASE_URL"] == "http://custom:9000"

    @patch("subprocess.run")
    def test_execute_command_success(self, mock_run):
        """Test execute_command handles successful execution."""
        mock_run.return_value = Mock(returncode=0, stdout="success output", stderr="")

        tui = TUIAutomation()
        result = tui.execute_command("projects list")

        assert result.success is True
        assert result.stdout == "success output"
        assert result.exit_code == 0
        mock_run.assert_called_once()

    @patch("subprocess.run")
    def test_execute_command_with_inputs(self, mock_run):
        """Test execute_command passes inputs correctly."""
        mock_run.return_value = Mock(returncode=0, stdout="ok", stderr="")

        tui = TUIAutomation()
        tui.execute_command("projects create", inputs=["TEST-001", "My Project"])

        call_args = mock_run.call_args
        assert call_args[1]["input"] == "TEST-001\nMy Project"

    @patch("subprocess.run")
    def test_execute_command_timeout(self, mock_run):
        """Test execute_command handles timeout."""
        mock_run.side_effect = subprocess.TimeoutExpired(cmd="test", timeout=5.0)

        tui = TUIAutomation()
        with pytest.raises(TimeoutError, match="timed out"):
            tui.execute_command("slow command", timeout=5.0)

    @patch("subprocess.run")
    def test_execute_command_failure(self, mock_run):
        """Test execute_command raises on failure by default."""
        mock_run.return_value = Mock(returncode=1, stdout="", stderr="error occurred")

        tui = TUIAutomation()
        with pytest.raises(RuntimeError, match="TUI command failed"):
            tui.execute_command("invalid command")

    @patch("subprocess.run")
    def test_execute_command_expect_failure(self, mock_run):
        """Test execute_command with expect_failure=True."""
        mock_run.return_value = Mock(returncode=1, stdout="", stderr="expected error")

        tui = TUIAutomation()
        result = tui.execute_command("invalid command", expect_failure=True)

        assert result.success is False
        assert result.exit_code == 1

    @patch.object(TUIAutomation, "execute_command")
    def test_expect_output_success(self, mock_execute):
        """Test expect_output returns True when pattern matches."""
        mock_execute.return_value = TUIResult(
            exit_code=0,
            stdout="Project TEST-001 created successfully",
            stderr="",
            duration=0.5,
        )

        tui = TUIAutomation()
        result = tui.expect_output("projects create", r"created successfully")

        assert result is True

    @patch.object(TUIAutomation, "execute_command")
    def test_expect_output_failure(self, mock_execute):
        """Test expect_output returns False when pattern doesn't match."""
        mock_execute.return_value = TUIResult(
            exit_code=0, stdout="Some other output", stderr="", duration=0.5
        )

        tui = TUIAutomation()
        result = tui.expect_output("projects create", r"created successfully")

        assert result is False

    @patch.object(TUIAutomation, "execute_command")
    def test_get_json_output_success(self, mock_execute):
        """Test get_json_output parses JSON correctly."""
        mock_execute.return_value = TUIResult(
            exit_code=0,
            stdout='{"key": "TEST-001", "name": "Project"}',
            stderr="",
            duration=0.5,
        )

        tui = TUIAutomation()
        data = tui.get_json_output("projects get --key TEST-001")

        assert data["key"] == "TEST-001"
        assert data["name"] == "Project"

    @patch.object(TUIAutomation, "execute_command")
    def test_get_json_output_invalid_json(self, mock_execute):
        """Test get_json_output raises on invalid JSON."""
        mock_execute.return_value = TUIResult(
            exit_code=0, stdout="not json", stderr="", duration=0.5
        )

        tui = TUIAutomation()
        with pytest.raises(ValueError, match="Failed to parse JSON"):
            tui.get_json_output("projects list")

    @patch("urllib.request.urlopen")
    def test_wait_for_api_success(self, mock_urlopen):
        """Test wait_for_api returns True when API is available."""
        # Mock successful HTTP response
        mock_response = MagicMock()
        mock_response.status = 200
        mock_response.__enter__ = MagicMock(return_value=mock_response)
        mock_response.__exit__ = MagicMock(return_value=False)
        mock_urlopen.return_value = mock_response

        tui = TUIAutomation()
        result = tui.wait_for_api(max_retries=3, retry_delay=0.1)

        assert result is True

    @patch("urllib.request.urlopen")
    def test_wait_for_api_timeout(self, mock_urlopen):
        """Test wait_for_api returns False after max retries."""
        from urllib.error import URLError

        mock_urlopen.side_effect = URLError("Connection refused")

        tui = TUIAutomation()
        result = tui.wait_for_api(max_retries=2, retry_delay=0.01)

        assert result is False
        assert mock_urlopen.call_count == 2


class TestTUIAssertions:
    """Test TUIAssertions helper."""

    def test_assert_success_passes(self):
        """Test assert_success passes for successful result."""
        result = TUIResult(exit_code=0, stdout="ok", stderr="", duration=0.5)
        TUIAssertions.assert_success(result)  # Should not raise

    def test_assert_success_fails(self):
        """Test assert_success fails for failed result."""
        result = TUIResult(exit_code=1, stdout="", stderr="error", duration=0.5)
        with pytest.raises(AssertionError, match="Command should succeed"):
            TUIAssertions.assert_success(result)

    def test_assert_contains_passes(self):
        """Test assert_contains passes when pattern found."""
        result = TUIResult(exit_code=0, stdout="hello world", stderr="", duration=0.5)
        TUIAssertions.assert_contains(result, "hello")  # Should not raise

    def test_assert_contains_fails(self):
        """Test assert_contains fails when pattern not found."""
        result = TUIResult(exit_code=0, stdout="hello world", stderr="", duration=0.5)
        with pytest.raises(AssertionError, match="should contain"):
            TUIAssertions.assert_contains(result, "missing")

    def test_assert_matches_passes(self):
        """Test assert_matches passes when regex matches."""
        result = TUIResult(
            exit_code=0, stdout="Project TEST-001 created", stderr="", duration=0.5
        )
        match = TUIAssertions.assert_matches(result, r"TEST-\d+")
        assert match is not None
        assert "TEST-001" in match.group(0)

    def test_assert_matches_fails(self):
        """Test assert_matches fails when regex doesn't match."""
        result = TUIResult(exit_code=0, stdout="No match here", stderr="", duration=0.5)
        with pytest.raises(AssertionError, match="should match"):
            TUIAssertions.assert_matches(result, r"TEST-\d+")

    def test_assert_duration_passes(self):
        """Test assert_duration passes when under limit."""
        result = TUIResult(exit_code=0, stdout="ok", stderr="", duration=0.5)
        TUIAssertions.assert_duration(result, 1.0)  # Should not raise

    def test_assert_duration_fails(self):
        """Test assert_duration fails when over limit."""
        result = TUIResult(exit_code=0, stdout="ok", stderr="", duration=2.0)
        with pytest.raises(AssertionError, match="should complete"):
            TUIAssertions.assert_duration(result, 1.0)
