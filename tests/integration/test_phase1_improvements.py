#!/usr/bin/env python3
"""
Test Phase 1 Agent Improvements (Issues #159-#163)

Tests:
- Cross-Repo Context Loader (#160)
- Smart Retry with Exponential Backoff (#162)
- Parallel Validation Execution (#163)
- PR Template Validation Script (#159)
- CI Behavior Knowledge Base (#161)
"""

import sys
import json
import asyncio
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from agents.workflow_agent import CrossRepoContext, SmartRetry, ParallelValidator


def test_cross_repo_context():
    """Test Cross-Repo Context Loader (#160)."""
    print("Testing Cross-Repo Context Loader...")

    context = CrossRepoContext()

    # Test repo detection
    print(f"  Current repo: {context.current_repo}")
    print(f"  PR repo: {context.pr_repo}")
    assert context.current_repo in ["backend", "client", "unknown"]

    # Test validation commands
    commands = context.get_validation_commands()
    print(f"  Validation commands: {len(commands)} commands")
    assert isinstance(commands, list)

    # Test Fixes: format
    fixes_same_repo = context.get_fixes_format(159)
    fixes_cross_repo = context.get_fixes_format(159, "blecx/AI-Agent-Framework-Client")
    print(f"  Same repo format: {fixes_same_repo}")
    print(f"  Cross-repo format: {fixes_cross_repo}")

    assert fixes_same_repo.startswith("Fixes: #")

    if context.current_repo == "backend":
        assert "blecx/AI-Agent-Framework-Client#" in fixes_cross_repo

    print("✅ Cross-Repo Context Loader tests passed\n")


def test_smart_retry():
    """Test Smart Retry with Exponential Backoff (#162)."""
    print("Testing Smart Retry...")

    retry = SmartRetry()

    # Test backoff schedule
    print(f"  Backoff schedule: {retry.backoff_schedule}")
    assert len(retry.backoff_schedule) > 0
    assert retry.backoff_schedule[0] < retry.backoff_schedule[-1]  # Exponential

    # Test CI time estimation
    estimated = retry._estimate_ci_time()
    print(f"  Estimated CI time (default): {estimated}s")
    assert estimated > 0

    # Test recording
    retry._record_ci_time(123, 45.5)
    estimated_after = retry._estimate_ci_time()
    print(f"  Estimated CI time (after recording): {estimated_after}s")
    assert estimated_after == 45.5

    print("✅ Smart Retry tests passed\n")


async def test_parallel_validator():
    """Test Parallel Validation Execution (#163)."""
    print("Testing Parallel Validator...")

    # Test with simple commands
    commands = ["echo 'test1'", "echo 'test2'", "true"]  # Always succeeds

    results = await ParallelValidator.validate_pr_parallel(Path("."), commands)

    print(f"  Ran {len(results)} commands in parallel")

    for cmd, (returncode, stdout, stderr) in results.items():
        print(f"    {cmd}: returncode={returncode}")
        assert returncode == 0  # All should succeed

    print("✅ Parallel Validator tests passed\n")


def test_pr_template_validation_script():
    """Test PR Template Validation Script (#159)."""
    print("Testing PR Template Validation Script...")

    script_path = Path("scripts/validate-pr-template.sh")

    if not script_path.exists():
        print("  ⚠️  Script not found, skipping test")
        return

    # Test help
    import subprocess

    result = subprocess.run(
        [str(script_path), "--help"], capture_output=True, text=True
    )

    assert result.returncode == 0
    assert "Usage:" in result.stdout

    print(f"  Script exists and has help text")
    print("✅ PR Template Validation Script tests passed\n")


def test_ci_behavior_knowledge():
    """Test CI Behavior Knowledge Base (#161)."""
    print("Testing CI Behavior Knowledge Base...")

    kb_path = Path("agents/knowledge/ci_workflows_behavior.json")

    assert kb_path.exists(), "CI behavior KB file missing"

    with open(kb_path, "r") as f:
        data = json.load(f)

    # Verify structure
    assert "github_actions_caching" in data
    caching = data["github_actions_caching"]
    assert "workflow_reruns_use_cached_payload" in caching

    payload_rule = caching["workflow_reruns_use_cached_payload"]
    assert "rule" in payload_rule
    assert "solution_1" in payload_rule
    assert "anti_patterns" in payload_rule

    print(f"  Rule: {payload_rule['rule'][:60]}...")
    print(f"  Solutions: {len([k for k in payload_rule if k.startswith('solution_')])}")
    print(f"  Anti-patterns: {len(payload_rule['anti_patterns'])}")

    print("✅ CI Behavior Knowledge Base tests passed\n")


def main():
    """Run all Phase 1 improvement tests."""
    print("=" * 60)
    print("Phase 1 Agent Improvements Test Suite")
    print("Issues #159-#163")
    print("=" * 60)
    print()

    try:
        test_cross_repo_context()
        test_smart_retry()
        asyncio.run(test_parallel_validator())
        test_pr_template_validation_script()
        test_ci_behavior_knowledge()

        print("=" * 60)
        print("✅ All Phase 1 tests passed!")
        print("=" * 60)
        return 0

    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        import traceback

        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())
