#!/usr/bin/env python3
"""
Test script to verify agent setup is complete and functional.

Usage:
    ./tests/agents/test_setup.py
"""

import json
import sys
from pathlib import Path


def test_directory_structure():
    """Verify all required directories exist."""
    print("🔍 Checking directory structure...")

    required_dirs = [
        "agents",
        "agents/config",
        "agents/knowledge",
        "agents/training",
        "agents/training/learnings",
        "agents/training/logs",
        "scripts/agents",
        "docs/agents",
        "tests/agents",
    ]

    missing = []
    for dir_path in required_dirs:
        if not Path(dir_path).exists():
            missing.append(dir_path)

    if missing:
        print(f"  ❌ Missing directories: {', '.join(missing)}")
        return False

    print(f"  ✅ All {len(required_dirs)} directories exist")
    return True


def test_knowledge_base_files():
    """Verify knowledge base files are initialized."""
    print("\n🔍 Checking knowledge base files...")

    required_files = [
        "agents/knowledge/workflow_patterns.json",
        "agents/knowledge/problem_solutions.json",
        "agents/knowledge/time_estimates.json",
        "agents/knowledge/command_sequences.json",
        "agents/knowledge/agent_metrics.json",
    ]

    missing = []
    invalid = []

    for file_path in required_files:
        path = Path(file_path)
        if not path.exists():
            missing.append(file_path)
            continue

        # Verify it's valid JSON
        try:
            with open(path) as f:
                json.load(f)
        except json.JSONDecodeError:
            invalid.append(file_path)

    if missing:
        print(f"  ❌ Missing files: {', '.join(missing)}")
        return False

    if invalid:
        print(f"  ❌ Invalid JSON files: {', '.join(invalid)}")
        return False

    print(f"  ✅ All {len(required_files)} knowledge base files valid")
    return True


def test_scripts_exist():
    """Verify all required scripts exist and are executable."""
    print("\n🔍 Checking scripts...")

    required_scripts = [
        "scripts/export_chat.py",
        "scripts/extract_learnings.py",
        "scripts/train_agent.py",
        "scripts/agents/workflow",
    ]

    # Python module files don't need to be executable
    optional_executable = [
        "agents/base_agent.py",
        "agents/workflow_agent.py",
    ]

    missing = []
    not_executable = []

    for script_path in required_scripts:
        path = Path(script_path)
        if not path.exists():
            missing.append(script_path)
            continue

        # Check if executable
        if not path.stat().st_mode & 0o111:
            not_executable.append(script_path)

    # Check optional files exist but don't require executable
    for script_path in optional_executable:
        path = Path(script_path)
        if not path.exists():
            missing.append(script_path)

    if missing:
        print(f"  ❌ Missing scripts: {', '.join(missing)}")
        return False

    if not_executable:
        print(f"  ⚠️  Some scripts not executable: {', '.join(not_executable)}")
        print(f"     (Optional) Run: chmod +x {' '.join(not_executable)}")

    total_scripts = len(required_scripts) + len(optional_executable)
    print(f"  ✅ All {total_scripts} scripts exist")
    return True


def test_documentation_exists():
    """Verify documentation files exist."""
    print("\n🔍 Checking documentation...")

    required_docs = [
        "agents/README.md",
        "docs/agents/workflow-agent.md",
        "docs/agents/QUICKSTART.md",
    ]

    missing = []
    for doc_path in required_docs:
        if not Path(doc_path).exists():
            missing.append(doc_path)

    if missing:
        print(f"  ❌ Missing docs: {', '.join(missing)}")
        return False

    print(f"  ✅ All {len(required_docs)} documentation files exist")
    return True


def test_agent_imports():
    """Test that agent modules can be imported."""
    print("\n🔍 Testing agent imports...")

    try:
        sys.path.insert(0, str(Path.cwd()))
        from agents.base_agent import BaseAgent, AgentPhase
        from agents.workflow_agent import WorkflowAgent

        print("  ✅ Agent modules import successfully")
        return True
    except ImportError as e:
        print(f"  ❌ Import failed: {e}")
        return False


def test_knowledge_base_initialized():
    """Verify knowledge base has proper initial structure."""
    print("\n🔍 Checking knowledge base initialization...")

    kb_dir = Path("agents/knowledge")

    # Check workflow_patterns
    with open(kb_dir / "workflow_patterns.json") as f:
        wp = json.load(f)

    required_keys = ["version", "last_updated", "issues", "common_phases"]
    if not all(key in wp for key in required_keys):
        print(f"  ❌ workflow_patterns.json missing required keys")
        return False

    # Check agent_metrics
    with open(kb_dir / "agent_metrics.json") as f:
        am = json.load(f)

    if "workflow_agent" not in am.get("agents", {}):
        print(f"  ❌ agent_metrics.json missing workflow_agent")
        return False

    print("  ✅ Knowledge base properly initialized")
    return True


def test_export_format_support():
    """Test that extraction can handle actual export formats."""
    print("\n🔍 Testing export format support...")

    # Check if any exports exist
    chat_dir = Path("docs/chat")
    if not chat_dir.exists():
        print("  ⚠️  No docs/chat directory - skipping export format test")
        return True

    export_files = list(chat_dir.glob("*.md"))

    if not export_files:
        print("  ⚠️  No export files found - skipping export format test")
        return True

    # Test reading a sample export
    sample_export = export_files[0]

    try:
        content = sample_export.read_text(encoding="utf-8")

        # Check it's readable markdown/text
        if len(content) < 100:
            print(f"  ⚠️  Export file seems too small: {sample_export.name}")
            return True

        # Check for common chat export markers
        has_content = any(
            marker in content.lower()
            for marker in [
                "chat",
                "conversation",
                "issue",
                "phase",
                "step",
                "user:",
                "assistant:",
            ]
        )

        if has_content:
            print(
                f"  ✅ Export format validated ({len(export_files)} files, {len(content):,} chars in sample)"
            )
        else:
            print(f"  ⚠️  Export format unusual but readable ({sample_export.name})")

        return True

    except Exception as e:
        print(f"  ❌ Error reading export: {e}")
        return False


def test_extraction_functionality():
    """Test that extraction script can process exports."""
    print("\n🔍 Testing extraction functionality...")

    # Check if learnings extractor can be imported
    try:
        sys.path.insert(0, str(Path.cwd()))
        from scripts.extract_learnings import LearningsExtractor

        # Create extractor instance
        extractor = LearningsExtractor()

        # Check if it has the required methods
        required_methods = ["extract_from_export", "merge_into_knowledge_base"]
        for method in required_methods:
            if not hasattr(extractor, method):
                print(f"  ❌ LearningsExtractor missing method: {method}")
                return False

        print("  ✅ Extraction functionality available")
        return True

    except Exception as e:
        print(f"  ❌ Error loading extractor: {e}")
        return False


def main():
    """Run all tests."""
    print("🧪 Testing Custom AI Agent Setup\n")
    print("=" * 60)

    tests = [
        test_directory_structure,
        test_knowledge_base_files,
        test_scripts_exist,
        test_documentation_exists,
        test_agent_imports,
        test_knowledge_base_initialized,
        test_export_format_support,
        test_extraction_functionality,
    ]

    results = []
    for test_func in tests:
        try:
            result = test_func()
            results.append(result)
        except Exception as e:
            print(f"  ❌ Test crashed: {e}")
            results.append(False)

    print("\n" + "=" * 60)
    print(f"📊 Test Results: {sum(results)}/{len(results)} passed")

    if all(results):
        print("\n✅ All tests passed! Agent system is ready to use.")
        print("\nNext steps:")
        print("  1. Train agent from existing issues:")
        print("     ./scripts/extract_learnings.py --export docs/chat/*-issue24-*.md")
        print("     ./scripts/extract_learnings.py --export docs/chat/*-issue25-*.md")
        print("  2. Check agent status:")
        print("     ./scripts/train_agent.py --analyze-all")
        print("  3. Run workflow on new issue:")
        print("     ./scripts/agents/workflow --issue 26 --dry-run")
        print("\nSee: docs/agents/QUICKSTART.md for complete guide")
        return 0
    else:
        print("\n❌ Some tests failed. Please fix the issues above.")
        return 1


if __name__ == "__main__":
    sys.exit(main())
