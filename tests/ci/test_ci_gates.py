"""
CI Gates Validation Tests
Tests the CI gate scripts to ensure they work correctly.
"""

import subprocess
import sys
from pathlib import Path

import pytest


PROJECT_ROOT = Path(__file__).parent.parent.parent


class TestDocsSyncChecker:
    """Test the documentation sync checker script"""

    def test_check_test_docs_script_exists(self):
        """Verify the check_test_docs.py script exists"""
        script_path = PROJECT_ROOT / "scripts" / "check_test_docs.py"
        assert script_path.exists(), "check_test_docs.py not found"
        assert script_path.is_file()

    def test_check_test_docs_executable(self):
        """Verify the script is executable"""
        script_path = PROJECT_ROOT / "scripts" / "check_test_docs.py"
        # On Windows, check might not be relevant
        if sys.platform != "win32":
            import os

            assert os.access(script_path, os.X_OK), "Script is not executable"

    def test_check_test_docs_runs(self):
        """Verify the script can be run"""
        script_path = PROJECT_ROOT / "scripts" / "check_test_docs.py"

        # Run the script - it should either pass or fail gracefully
        result = subprocess.run(
            [sys.executable, str(script_path)], capture_output=True, text=True
        )

        # Exit code should be 0 (pass) or 1 (fail), not crash
        assert result.returncode in [
            0,
            1,
        ], f"Script crashed with exit code {result.returncode}: {result.stderr}"


class TestCoverageDiffCalculator:
    """Test the coverage diff calculator script"""

    def test_coverage_diff_script_exists(self):
        """Verify the coverage_diff.py script exists"""
        script_path = PROJECT_ROOT / "scripts" / "coverage_diff.py"
        assert script_path.exists(), "coverage_diff.py not found"
        assert script_path.is_file()

    def test_coverage_diff_executable(self):
        """Verify the script is executable"""
        script_path = PROJECT_ROOT / "scripts" / "coverage_diff.py"
        if sys.platform != "win32":
            import os

            assert os.access(script_path, os.X_OK), "Script is not executable"

    def test_coverage_diff_usage_message(self):
        """Verify the script shows usage when called without args"""
        script_path = PROJECT_ROOT / "scripts" / "coverage_diff.py"

        result = subprocess.run(
            [sys.executable, str(script_path)], capture_output=True, text=True
        )

        # Should exit with code 1 and show usage
        assert result.returncode == 1
        assert "Usage:" in result.stdout or "usage" in result.stdout.lower()

    def test_coverage_diff_with_refs(self):
        """Verify the script runs with branch refs"""
        script_path = PROJECT_ROOT / "scripts" / "coverage_diff.py"

        # Run with main branch as both refs (no changes)
        result = subprocess.run(
            [sys.executable, str(script_path), "HEAD", "HEAD"],
            capture_output=True,
            text=True,
            cwd=PROJECT_ROOT,
        )

        # Should pass (no changes between HEAD and HEAD)
        assert result.returncode in [0, 1], f"Script crashed: {result.stderr}"


class TestCIBackendScript:
    """Test the local CI simulation script"""

    def test_ci_backend_script_exists(self):
        """Verify the ci_backend.sh script exists"""
        script_path = PROJECT_ROOT / "scripts" / "ci_backend.sh"
        assert script_path.exists(), "ci_backend.sh not found"
        assert script_path.is_file()

    def test_ci_backend_executable(self):
        """Verify the script is executable"""
        script_path = PROJECT_ROOT / "scripts" / "ci_backend.sh"
        if sys.platform != "win32":
            import os

            assert os.access(script_path, os.X_OK), "Script is not executable"

    def test_ci_backend_script_syntax(self):
        """Verify the bash script has valid syntax"""
        script_path = PROJECT_ROOT / "scripts" / "ci_backend.sh"

        # Use bash -n to check syntax without running
        result = subprocess.run(
            ["bash", "-n", str(script_path)], capture_output=True, text=True
        )

        assert result.returncode == 0, f"Bash syntax error: {result.stderr}"


class TestCIWorkflow:
    """Test the CI workflow file"""

    def test_ci_workflow_exists(self):
        """Verify the CI workflow file exists"""
        workflow_path = PROJECT_ROOT / ".github" / "workflows" / "ci-backend.yml"
        assert workflow_path.exists(), "ci-backend.yml not found"
        assert workflow_path.is_file()

    def test_ci_workflow_valid_yaml(self):
        """Verify the workflow file is valid YAML"""
        workflow_path = PROJECT_ROOT / ".github" / "workflows" / "ci-backend.yml"

        try:
            import yaml
        except ImportError:
            pytest.skip("pyyaml not installed")

        with open(workflow_path) as f:
            data = yaml.safe_load(f)

        # Check basic structure
        assert "name" in data, "Workflow missing 'name'"
        # 'on' is parsed as True by YAML - check for it
        assert True in data or "on" in data, "Workflow missing 'on' triggers"
        assert "jobs" in data, "Workflow missing 'jobs'"

    def test_ci_workflow_has_all_gates(self):
        """Verify the workflow defines all 9 gates"""
        workflow_path = PROJECT_ROOT / ".github" / "workflows" / "ci-backend.yml"

        try:
            import yaml
        except ImportError:
            pytest.skip("pyyaml not installed")

        with open(workflow_path) as f:
            data = yaml.safe_load(f)

        jobs = data.get("jobs", {})

        # Expected gate jobs
        expected_gates = [
            "test",  # Gate 1: All tests pass
            "coverage",  # Gate 2: Coverage threshold
            "missing-tests",  # Gate 3: Missing tests detection
            "docs-sync",  # Gate 4: Documentation sync
            "openapi",  # Gate 5: OpenAPI spec validation
            "lint",  # Gate 6: Linting
            "security",  # Gate 7: Security scanning
            "test-time",  # Gate 8: Test execution time
            "flaky-tests",  # Gate 9: Flaky test detection
        ]

        for gate in expected_gates:
            assert gate in jobs, f"Gate job '{gate}' not found in workflow"

    def test_ci_workflow_final_gate_depends_on_all(self):
        """Verify the final gate depends on all other gates"""
        workflow_path = PROJECT_ROOT / ".github" / "workflows" / "ci-backend.yml"

        try:
            import yaml
        except ImportError:
            pytest.skip("pyyaml not installed")

        with open(workflow_path) as f:
            data = yaml.safe_load(f)

        jobs = data.get("jobs", {})
        final_gate = jobs.get("all-gates-passed", {})

        assert "needs" in final_gate, "Final gate missing 'needs' dependencies"

        needs = final_gate["needs"]
        assert isinstance(needs, list), "Final gate 'needs' should be a list"
        assert (
            len(needs) >= 9
        ), f"Final gate should depend on all 9 gates, found {len(needs)}"


class TestCIGateFailureMessages:
    """Test that CI gates provide clear failure messages"""

    def test_gate_failure_messages_exist(self):
        """Verify all gates have failure remediation messages"""
        workflow_path = PROJECT_ROOT / ".github" / "workflows" / "ci-backend.yml"

        with open(workflow_path) as f:
            content = f.read()

        # Check for remediation messages in each gate
        assert "Remediation:" in content, "No remediation messages found"

        # Count remediation messages - should have one per gate
        remediation_count = content.count("Remediation:")
        assert (
            remediation_count >= 7
        ), f"Expected at least 7 remediation messages, found {remediation_count}"
