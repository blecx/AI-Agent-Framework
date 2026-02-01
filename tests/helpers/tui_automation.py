"""TUI automation service for E2E tests.

Provides utilities for executing TUI commands programmatically,
parsing outputs, and asserting on results in a deterministic way.
"""

import subprocess
import re
import time
import shlex
from typing import List, Optional, Any
from pathlib import Path
from dataclasses import dataclass


@dataclass
class TUIResult:
    """Result of a TUI command execution."""

    exit_code: int
    stdout: str
    stderr: str
    duration: float

    @property
    def success(self) -> bool:
        """Check if command succeeded."""
        return self.exit_code == 0

    def contains(self, pattern: str) -> bool:
        """Check if output contains pattern."""
        return pattern in self.stdout or pattern in self.stderr

    def match(self, pattern: str) -> Optional[re.Match]:
        """Match regex pattern in output."""
        return re.search(pattern, self.stdout + "\n" + self.stderr)


class TUIAutomation:
    """Service for automated TUI command execution."""

    def __init__(
        self,
        tui_path: str = "apps/tui/main.py",
        api_base_url: str = "http://localhost:8000",
    ):
        """Initialize TUI automation.

        Args:
            tui_path: Path to TUI main.py
            api_base_url: API endpoint URL
        """
        self.tui_path = Path(tui_path)
        self.api_base_url = api_base_url
        self.env = {
            "API_BASE_URL": api_base_url,
            "API_TIMEOUT": "30",
            "PYTHONUNBUFFERED": "1",
        }

    def execute_command(
        self,
        command: str,
        inputs: Optional[List[str]] = None,
        timeout: float = 30.0,
        expect_failure: bool = False,
    ) -> TUIResult:
        """Execute TUI command with optional inputs.

        Args:
            command: TUI command (e.g., "projects list")
            inputs: Optional list of input strings to send
            timeout: Command timeout in seconds
            expect_failure: If True, don't raise on non-zero exit

        Returns:
            TUIResult with execution details
        """
        import os

        cmd_parts = ["python", str(self.tui_path)] + shlex.split(command)

        start_time = time.time()
        try:
            result = subprocess.run(
                cmd_parts,
                input="\n".join(inputs) if inputs else None,
                capture_output=True,
                text=True,
                timeout=timeout,
                env={**os.environ, **self.env},
                check=False,
            )
            duration = time.time() - start_time

            tui_result = TUIResult(
                exit_code=result.returncode,
                stdout=result.stdout,
                stderr=result.stderr,
                duration=duration,
            )

            if not expect_failure and not tui_result.success:
                raise RuntimeError(
                    f"TUI command failed (exit {result.returncode}):\n"
                    f"Command: {' '.join(cmd_parts)}\n"
                    f"Stdout: {result.stdout}\n"
                    f"Stderr: {result.stderr}"
                )

            return tui_result

        except subprocess.TimeoutExpired as e:
            duration = time.time() - start_time
            raise TimeoutError(
                f"TUI command timed out after {timeout}s:\n"
                f"Command: {' '.join(cmd_parts)}"
            ) from e

    def expect_output(
        self,
        command: str,
        pattern: str,
        timeout: float = 5.0,
        inputs: Optional[List[str]] = None,
    ) -> bool:
        """Execute command and wait for expected output pattern.

        Args:
            command: TUI command to execute
            pattern: Regex pattern to match in output
            timeout: Command timeout
            inputs: Optional input strings

        Returns:
            True if pattern found, False otherwise
        """
        result = self.execute_command(command, inputs=inputs, timeout=timeout)
        return bool(re.search(pattern, result.stdout + "\n" + result.stderr))

    def get_json_output(self, command: str, timeout: float = 30.0) -> Any:
        """Execute command and parse JSON output.

        Args:
            command: TUI command that returns JSON
            timeout: Command timeout

        Returns:
            Parsed JSON data
        """
        import json

        result = self.execute_command(command, timeout=timeout)
        try:
            return json.loads(result.stdout)
        except json.JSONDecodeError as e:
            raise ValueError(f"Failed to parse JSON output:\n{result.stdout}") from e

    def wait_for_api(self, max_retries: int = 10, retry_delay: float = 1.0) -> bool:
        """Wait for API to be available.

        Args:
            max_retries: Maximum number of retry attempts
            retry_delay: Delay between retries in seconds

        Returns:
            True if API is available, False otherwise
        """
        import urllib.request
        import urllib.error

        for attempt in range(max_retries):
            try:
                with urllib.request.urlopen(
                    f"{self.api_base_url}/health", timeout=5
                ) as response:
                    if response.status == 200:
                        return True
            except (urllib.error.URLError, urllib.error.HTTPError, OSError):
                pass

            if attempt < max_retries - 1:
                time.sleep(retry_delay)

        return False

    def cleanup_project(self, project_key: str) -> None:
        """Clean up test project (best effort).

        Args:
            project_key: Project key to delete
        """
        try:
            # Note: TUI doesn't have delete command yet
            # This is a placeholder for future implementation
            pass
        except Exception:
            # Ignore cleanup failures
            pass


class TUIAssertions:
    """Custom assertions for TUI test results."""

    @staticmethod
    def assert_success(result: TUIResult, message: str = "Command should succeed"):
        """Assert command succeeded."""
        assert (
            result.success
        ), f"{message}\nStdout: {result.stdout}\nStderr: {result.stderr}"

    @staticmethod
    def assert_contains(result: TUIResult, pattern: str, message: Optional[str] = None):
        """Assert output contains pattern."""
        msg = message or f"Output should contain: {pattern}"
        assert result.contains(
            pattern
        ), f"{msg}\nStdout: {result.stdout}\nStderr: {result.stderr}"

    @staticmethod
    def assert_matches(result: TUIResult, pattern: str, message: Optional[str] = None):
        """Assert output matches regex pattern."""
        msg = message or f"Output should match: {pattern}"
        match = result.match(pattern)
        assert match, f"{msg}\nStdout: {result.stdout}\nStderr: {result.stderr}"
        return match

    @staticmethod
    def assert_duration(
        result: TUIResult, max_duration: float, message: Optional[str] = None
    ):
        """Assert command completed within time limit."""
        msg = message or f"Command should complete in < {max_duration}s"
        assert result.duration < max_duration, f"{msg}\nActual: {result.duration:.2f}s"
