"""
TUI Automation Helper for E2E Testing

Provides utilities to execute TUI commands programmatically in E2E tests.
Supports non-interactive, deterministic command execution with output validation.
"""

import subprocess
import sys
import os
from pathlib import Path
from typing import List, Optional, Dict, Any, Callable
import time
import re


class TUIResult:
    """Result of a TUI command execution."""

    def __init__(self, stdout: str, stderr: str, returncode: int):
        self.stdout = stdout
        self.stderr = stderr
        self.returncode = returncode
        self.success = returncode == 0

    def __repr__(self):
        return f"TUIResult(success={self.success}, returncode={self.returncode})"


class TUIAutomation:
    """Service for automated TUI command execution in E2E tests."""

    def __init__(self, api_base_url: str = "http://localhost:8000", timeout: int = 30):
        """Initialize TUI automation.

        Args:
            api_base_url: Base URL for the API backend
            timeout: Default timeout for commands in seconds
        """
        self.api_base_url = api_base_url
        self.timeout = timeout

        # Locate TUI main.py
        self.tui_path = (
            Path(__file__).resolve().parent.parent.parent / "apps" / "tui" / "main.py"
        )
        if not self.tui_path.exists():
            raise FileNotFoundError(f"TUI not found at {self.tui_path}")

        # Get Python interpreter
        self.python_exec = sys.executable

    def execute_command(
        self,
        command: List[str],
        timeout: Optional[float] = None,
        env: Optional[Dict[str, str]] = None,
        check: bool = True,
    ) -> TUIResult:
        """Execute a TUI command with optional inputs.

        Args:
            command: Command parts (e.g., ["projects", "list"])
            timeout: Command timeout (defaults to self.timeout)
            env: Additional environment variables
            check: Whether to raise exception on non-zero exit

        Returns:
            TUIResult with stdout, stderr, and exit code

        Example:
            result = tui.execute_command(["projects", "create", "--key", "TEST-01", "--name", "Test"])
        """
        timeout = timeout or self.timeout

        # Build command
        cmd = [self.python_exec, str(self.tui_path)] + command

        # Set up environment
        cmd_env = os.environ.copy()
        cmd_env["API_BASE_URL"] = self.api_base_url
        cmd_env["API_TIMEOUT"] = str(self.timeout)
        if env:
            cmd_env.update(env)

        try:
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=timeout,
                env=cmd_env,
                check=False,
            )

            tui_result = TUIResult(result.stdout, result.stderr, result.returncode)

            if check and not tui_result.success:
                raise subprocess.CalledProcessError(
                    result.returncode, cmd, result.stdout, result.stderr
                )

            return tui_result

        except subprocess.TimeoutExpired as e:
            raise TimeoutError(
                f"Command timed out after {timeout}s: {' '.join(cmd)}"
            ) from e

    def expect_output(
        self, result: TUIResult, pattern: str, timeout: float = 5.0
    ) -> bool:
        """Check if output matches expected pattern.

        Args:
            result: TUI command result
            pattern: Regex pattern to match in stdout
            timeout: Not used (kept for compatibility with issue spec)

        Returns:
            True if pattern found in output

        Example:
            result = tui.execute_command(["projects", "list"])
            assert tui.expect_output(result, r"TEST-\\d+")
        """
        return bool(re.search(pattern, result.stdout))

    def wait_for_condition(
        self,
        check_fn: Callable[[], Any],
        timeout: float = 10.0,
        interval: float = 0.5,
        error_msg: str = "Condition not met",
    ) -> Any:
        """Wait for a condition to become true (polling pattern).

        Args:
            check_fn: Function that returns truthy value when condition met
            timeout: Maximum wait time in seconds
            interval: Time between checks in seconds
            error_msg: Error message if timeout reached

        Returns:
            Return value of check_fn when condition met

        Raises:
            TimeoutError: If condition not met within timeout
        """
        start_time = time.time()
        last_exception = None

        while time.time() - start_time < timeout:
            try:
                result = check_fn()
                if result:
                    return result
            except Exception as e:
                last_exception = e

            time.sleep(interval)

        if last_exception:
            raise TimeoutError(f"{error_msg}: {last_exception}") from last_exception
        raise TimeoutError(error_msg)

    def create_project(self, key: str, name: str) -> TUIResult:
        """Convenience method to create a project.

        Args:
            key: Project key (e.g., "TEST-01")
            name: Project name

        Returns:
            TUIResult from project creation
        """
        return self.execute_command(
            ["projects", "create", "--key", key, "--name", name]
        )

    def list_projects(self) -> TUIResult:
        """Convenience method to list projects.

        Returns:
            TUIResult with project list
        """
        return self.execute_command(["projects", "list"])

    def health_check(self) -> TUIResult:
        """Check API health via TUI.

        Returns:
            TUIResult with health status
        """
        return self.execute_command(["health"])
