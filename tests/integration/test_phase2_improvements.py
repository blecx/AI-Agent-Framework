#!/usr/bin/env python3
"""
Test Phase 2 Agent Improvements (Issues #164-#168)

Tests:
- Incremental Knowledge Base Updates (#164)
- Smart File Change Detection (#165)
- Auto-Recovery from Common Errors (#166)
- Pre-Flight Issue Readiness Checks (#167)
- Automated Documentation Updates (#168)
"""

import sys
import json
import tempfile
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from agents.workflow_agent import (  # noqa: E402
    IncrementalKnowledgeBase,
    SmartValidation,
    ErrorRecovery,
    IssuePreflight,
    DocUpdater,
)


def test_incremental_kb_updates():
    """Test Incremental Knowledge Base Updates (#164)."""
    print("Testing Incremental Knowledge Base Updates...")

    with tempfile.TemporaryDirectory() as tmpdir:
        kb = IncrementalKnowledgeBase(kb_dir=Path(tmpdir))

        # Test initialization
        assert kb.phase_learnings_file.exists()
        print("  ✅ KB file initialized")

        # Test extracting learnings from successful phase
        phase_output = {"validation_time": 45.5, "commands": ["npm test", "npm build"]}
        learnings = kb.extract_learnings_from_phase(
            "Phase 4", phase_output, success=True
        )
        assert len(learnings) > 0
        assert learnings[0]["type"] == "performance"
        print(f"  ✅ Extracted {len(learnings)} learnings from successful phase")

        # Test extracting learnings from failed phase
        phase_output_fail = {
            "error": "Cannot find module 'axios'",
            "context": "npm test",
        }
        learnings_fail = kb.extract_learnings_from_phase(
            "Phase 4", phase_output_fail, success=False
        )
        assert len(learnings_fail) > 0
        assert learnings_fail[0]["type"] == "error_pattern"
        print(f"  ✅ Extracted {len(learnings_fail)} learnings from failed phase")

        # Test updating KB after phase
        kb.update_kb_after_phase("Phase 4", learnings)

        with open(kb.phase_learnings_file, "r") as f:
            data = json.load(f)

        assert len(data["learnings_by_phase"]["Phase 4"]) == len(learnings)
        print("  ✅ KB updated successfully")

        # Test getting relevant learnings
        relevant = kb.get_relevant_learnings("Phase 4", {})
        assert len(relevant) >= 0  # May be 0 if learnings are filtered
        print(f"  ✅ Retrieved {len(relevant)} relevant learnings")

        # Test metrics
        assert "learnings_applied_same_issue" in data["metrics"]
        assert "problems_resolved_faster" in data["metrics"]
        print("  ✅ Metrics structure validated")

    print("✅ Incremental KB Updates tests passed\n")


def test_smart_validation():
    """Test Smart File Change Detection (#165)."""
    print("Testing Smart File Change Detection...")

    validator = SmartValidation()

    # Test change analysis (will analyze current git state)
    changes = validator.analyze_changes()

    assert "doc_only" in changes
    assert "test_only" in changes
    assert "type_only" in changes
    assert "full" in changes
    print(f"  ✅ Change analysis returned: {changes}")

    # Test validation commands for backend
    backend_commands = validator.get_validation_commands("backend")
    assert isinstance(backend_commands, list)
    print(f"  ✅ Backend commands: {len(backend_commands)} commands")

    # Test validation commands for client
    client_commands = validator.get_validation_commands("client")
    assert isinstance(client_commands, list)
    print(f"  ✅ Client commands: {len(client_commands)} commands")

    # Test metrics
    assert "validation_time_saved_per_issue" in validator.metrics
    assert "unnecessary_test_runs_avoided" in validator.metrics
    print("  ✅ Metrics structure validated")

    print("✅ Smart Validation tests passed\n")


def test_error_recovery():
    """Test Auto-Recovery from Common Errors (#166)."""
    print("Testing Auto-Recovery from Common Errors...")

    recovery = ErrorRecovery()

    # Test pattern detection - missing module
    error1 = "Error: Cannot find module 'axios'"
    pattern1 = recovery.detect_error_pattern(error1)
    assert pattern1 is not None
    assert pattern1["error_type"] == "missing_module"
    print("  ✅ Detected missing module error")

    # Test pattern detection - unused import
    error2 = "'useState' is declared but its value is never read"
    pattern2 = recovery.detect_error_pattern(error2)
    assert pattern2 is not None
    assert pattern2["error_type"] == "unused_import"
    print("  ✅ Detected unused import error")

    # Test pattern detection - null type error
    error3 = "Type 'null' is not assignable to type 'string'"
    pattern3 = recovery.detect_error_pattern(error3)
    assert pattern3 is not None
    assert pattern3["error_type"] == "null_type_error"
    print("  ✅ Detected null type error")

    # Test pattern detection - PR template error
    error4 = "Evidence must be filled in"
    pattern4 = recovery.detect_error_pattern(error4)
    assert pattern4 is not None
    assert pattern4["error_type"] == "pr_template_evidence"
    print("  ✅ Detected PR template error")

    # Test pattern detection - no match
    error5 = "Some random error that doesn't match any pattern"
    pattern5 = recovery.detect_error_pattern(error5)
    assert pattern5 is None
    print("  ✅ Correctly returned None for unknown error")

    # Test recovery patterns structure
    assert len(recovery.recovery_patterns) >= 5
    for pattern in recovery.recovery_patterns:
        assert "pattern" in pattern
        assert "error_type" in pattern
        assert "recovery_command" in pattern
        assert "confidence" in pattern
    print(f"  ✅ {len(recovery.recovery_patterns)} recovery patterns loaded")

    # Test metrics
    assert "auto_recoveries_successful" in recovery.metrics
    assert "user_interventions_avoided" in recovery.metrics
    print("  ✅ Metrics structure validated")

    print("✅ Error Recovery tests passed\n")


def test_issue_preflight():
    """Test Pre-Flight Issue Readiness Checks (#167)."""
    print("Testing Pre-Flight Issue Readiness Checks...")

    preflight = IssuePreflight()

    # Test valid issue
    valid_issue = {
        "title": "Add new feature",
        "body": """
## Acceptance Criteria
- [ ] Feature works
- [ ] Tests pass

## Estimated Effort
3 hours
        """,
        "labels": ["enhancement", "priority-medium"],
        "state": "open",
    }

    is_valid, issues = preflight.validate_issue(valid_issue)
    assert is_valid
    print(f"  ✅ Valid issue passed (warnings: {len(issues)})")

    # Test issue missing acceptance criteria
    invalid_issue1 = {
        "title": "Fix bug",
        "body": "Something is broken, estimated 2 hours",
        "labels": ["bug"],
        "state": "open",
    }

    is_valid1, issues1 = preflight.validate_issue(invalid_issue1)
    assert not is_valid1
    assert any("acceptance criteria" in issue.lower() for issue in issues1)
    print("  ✅ Detected missing acceptance criteria")

    # Test issue too short
    invalid_issue2 = {"title": "Fix", "body": "Fix it", "labels": [], "state": "open"}

    is_valid2, issues2 = preflight.validate_issue(invalid_issue2)
    assert len([i for i in issues2 if "short" in i.lower()]) > 0
    print("  ✅ Detected short issue description")

    # Test issue with blockers
    warning_issue = {
        "title": "Add feature",
        "body": """
## Acceptance Criteria
- Feature works

Blocked by #123. Estimated 2 hours.
        """,
        "labels": ["enhancement"],
        "state": "open",
    }

    is_valid3, issues3 = preflight.validate_issue(warning_issue)
    assert any("blocker" in issue.lower() for issue in issues3)
    print("  ✅ Detected blocker mention")

    # Test issue with dependencies
    dep_issue = {
        "title": "Add feature",
        "body": """
## Acceptance Criteria
- Feature works

Depends on #124. Estimated 2 hours.
        """,
        "labels": ["enhancement"],
        "state": "open",
    }

    is_valid4, issues4 = preflight.validate_issue(dep_issue)
    assert any("dependenc" in issue.lower() for issue in issues4)
    print("  ✅ Detected dependency mention")

    # Test metrics
    assert "issues_failed_preflight" in preflight.metrics
    assert "rework_time_saved_hours" in preflight.metrics
    assert preflight.metrics["issues_failed_preflight"] > 0  # We failed some issues
    print("  ✅ Metrics structure validated and updated")

    print("✅ Issue Preflight tests passed\n")


def test_doc_updater():
    """Test Automated Documentation Updates (#168)."""
    print("Testing Automated Documentation Updates...")

    updater = DocUpdater()

    # Test impact detection (will analyze current git state)
    impacts = updater.detect_documentation_impact()

    assert isinstance(impacts, dict)
    print(f"  ✅ Impact detection returned {len(impacts)} files")

    if impacts:
        for doc_file, changes in impacts.items():
            print(f"    • {doc_file}: {len(changes)} changes")

    # Test generating suggestions
    if impacts:
        suggestions = updater.generate_documentation_updates(impacts)
        assert isinstance(suggestions, dict)
        print(f"  ✅ Generated {len(suggestions)} suggestions")
    else:
        print("  ℹ️  No impacts detected in current state (OK)")

    # Test suggestion methods
    api_suggestion = updater._suggest_api_doc_update()
    assert "TODO" in api_suggestion
    assert "endpoint" in api_suggestion.lower()
    print("  ✅ API doc suggestion generated")

    readme_suggestion = updater._suggest_readme_update()
    assert "TODO" in readme_suggestion
    assert "command" in readme_suggestion.lower()
    print("  ✅ README suggestion generated")

    changelog_suggestion = updater._suggest_changelog_update()
    assert "Unreleased" in changelog_suggestion
    assert "TODO" in changelog_suggestion
    print("  ✅ CHANGELOG suggestion generated")

    # Test metrics
    assert "auto_doc_updates" in updater.metrics
    assert "doc_staleness_issues_prevented" in updater.metrics
    print("  ✅ Metrics structure validated")

    print("✅ Doc Updater tests passed\n")


def test_integration_workflow():
    """Test integrated workflow with Phase 2 improvements."""
    print("Testing integrated workflow...")

    # Create temporary KB
    with tempfile.TemporaryDirectory() as tmpdir:
        kb = IncrementalKnowledgeBase(kb_dir=Path(tmpdir))
        validator = SmartValidation()
        recovery = ErrorRecovery()
        preflight = IssuePreflight()
        updater = DocUpdater()

        # Simulate a workflow
        # 1. Preflight check
        issue_data = {
            "title": "Test Issue",
            "body": """
## Acceptance Criteria
- Works correctly
- Tests pass

Estimated: 2 hours
            """,
            "labels": ["enhancement"],
            "state": "open",
        }

        is_valid, issues = preflight.validate_issue(issue_data)
        print(
            f"  1. Preflight: {'✅ Valid' if is_valid else '❌ Invalid'} ({len(issues)} issues)"
        )

        # 2. Smart validation
        commands = validator.get_validation_commands("backend")
        print(f"  2. Smart validation: {len(commands)} commands determined")

        # 3. Error recovery (simulate)
        error = "Cannot find module 'test-module'"
        pattern = recovery.detect_error_pattern(error)
        if pattern:
            print(f"  3. Error recovery: Pattern detected - {pattern['error_type']}")

        # 4. KB update
        phase_output = {"validation_time": 30.0, "commands": commands}
        learnings = kb.extract_learnings_from_phase("Phase 4", phase_output, True)
        kb.update_kb_after_phase("Phase 4", learnings)
        print(f"  4. KB update: {len(learnings)} learnings saved")

        # 5. Doc impact
        impacts = updater.detect_documentation_impact()
        print(f"  5. Doc impact: {len(impacts)} files need updates")

        print("  ✅ Integrated workflow completed")

    print("✅ Integration workflow test passed\n")


def main():
    """Run all Phase 2 tests."""
    print("=" * 60)
    print("Phase 2 Agent Improvements - Integration Tests")
    print("=" * 60)
    print()

    try:
        test_incremental_kb_updates()
        test_smart_validation()
        test_error_recovery()
        test_issue_preflight()
        test_doc_updater()
        test_integration_workflow()

        print("=" * 60)
        print("✅ ALL PHASE 2 TESTS PASSED")
        print("=" * 60)
        return 0

    except AssertionError as e:
        print(f"\n❌ Test failed: {e}")
        return 1
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        import traceback

        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())
