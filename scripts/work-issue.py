#!/usr/bin/env python3
"""
Work Issue - Main CLI for autonomous issue resolution

This is the primary interface for invoking the autonomous workflow agent.

Usage:
    ./scripts/work-issue.py --issue 26
    ./scripts/work-issue.py --issue 26 --dry-run
    ./scripts/work-issue.py --issue 26 --interactive
"""

import asyncio
import os
import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))


async def main():
    """Main entry point."""
    import argparse

    _ensure_venv_and_reexec()

    # Import after venv re-exec so dependencies are available
    from agents.autonomous_workflow_agent import AutonomousWorkflowAgent
    
    parser = argparse.ArgumentParser(
        description="Autonomous AI Agent for Issue Resolution",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
The agent will:
  ✅ Fetch and analyze the issue
  ✅ Create implementation plan
  ✅ Write tests first, then implementation
  ✅ Run tests and fix failures
  ✅ Perform self-review
  ✅ Create pull request
  ✅ Update knowledge base

Examples:
  # Fully autonomous - agent works independently
  ./scripts/work-issue.py --issue 26
  
    # Dry run - initialize only (no LLM calls, no changes)
  ./scripts/work-issue.py --issue 26 --dry-run

    # Plan-only - Phase 1-2 planning only (LLM required, no changes)
    ./scripts/work-issue.py --issue 26 --plan-only
  
  # Interactive - pause for approval between phases
  ./scripts/work-issue.py --issue 26 --interactive

Requirements:
    - Python 3.12+ (this repo enforces .venv via ./setup.sh)
  - GitHub CLI (gh) authenticated
  - Git configured
  - GitHub PAT token in configs/llm.json
        """
    )
    
    parser.add_argument(
        "--issue",
        type=int,
        required=True,
        help="GitHub issue number to work on"
    )

    mode_group = parser.add_mutually_exclusive_group()
    mode_group.add_argument(
        "--dry-run",
        action="store_true",
        help="Initialize only (no LLM calls, no repo changes)"
    )

    mode_group.add_argument(
        "--plan-only",
        action="store_true",
        help="Run Phase 1-2 planning only (LLM required, no repo changes)"
    )
    
    parser.add_argument(
        "--interactive",
        action="store_true",
        help="Pause for approval between phases"
    )
    
    args = parser.parse_args()
    
    print("""
╔══════════════════════════════════════════════════════════════════╗
║        Autonomous Workflow Agent - AI-Powered Development        ║
║                  Powered by Microsoft Agent Framework            ║
╚══════════════════════════════════════════════════════════════════╝
""")
    
    # Check prerequisites
    if not _check_prerequisites():
        sys.exit(1)
    
    # Create and run agent
    try:
        agent = AutonomousWorkflowAgent(
            issue_number=args.issue,
            # plan-only should also behave as read-only inside the agent
            dry_run=bool(args.dry_run or args.plan_only)
        )
        
        await agent.initialize()

        if args.dry_run:
            print("✅ Dry run complete: initialization succeeded (no LLM calls executed).")
            sys.exit(0)

        if args.plan_only:
            _ = await agent.plan_only()
            print("✅ Plan-only complete: planning finished (no repo changes executed).")
            sys.exit(0)

        success = await agent.execute()
        
        # Interactive mode
        if args.interactive and success:
            await _interactive_mode(agent)
        
        sys.exit(0 if success else 1)
        
    except KeyboardInterrupt:
        print("\n\n⚠️  Interrupted by user")
        sys.exit(130)
    except Exception as e:
        print(f"\n❌ Fatal error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


def _check_prerequisites() -> bool:
    """Check that required tools are available."""
    import subprocess
    import shutil
    
    checks = []
    
    # Check gh CLI
    if shutil.which("gh"):
        checks.append(("GitHub CLI (gh)", "✅"))
    else:
        checks.append(("GitHub CLI (gh)", "❌ Not found - install from https://cli.github.com"))
    
    # Check git
    if shutil.which("git"):
        checks.append(("Git", "✅"))
    else:
        checks.append(("Git", "❌ Not found"))
    
    # Check Python version
    import sys
    version = sys.version_info
    py_exec = sys.executable
    if version.major == 3 and version.minor >= 12:
        checks.append((f"Python {version.major}.{version.minor} ({py_exec})", "✅"))
    else:
        checks.append((f"Python {version.major}.{version.minor} ({py_exec})", "❌ Need Python 3.12+"))
    
    # Check LLM config
    config_path = Path("configs/llm.json")
    if not config_path.exists():
        config_path = Path("configs/llm.default.json")
    
    if config_path.exists():
        checks.append(("LLM config", "✅"))
    else:
        checks.append(("LLM config", "❌ Create configs/llm.json"))

    # Check Python virtual environment
    if Path(".venv").exists():
        checks.append(("Python virtualenv (.venv)", "✅"))
    else:
        checks.append(("Python virtualenv (.venv)", "❌ Run ./setup.sh to create"))

    # Check Node/npm if frontend or client repo exists
    client_repo = Path("_external/AI-Agent-Framework-Client")
    frontend_repo = Path("apps/web")
    if client_repo.exists() or frontend_repo.exists():
        if shutil.which("node"):
            checks.append(("Node.js", "✅"))
        else:
            checks.append(("Node.js", "❌ Not found"))

        if shutil.which("npm"):
            checks.append(("npm", "✅"))
        else:
            checks.append(("npm", "❌ Not found"))
    
    # Print results
    print("Prerequisites:")
    for name, status in checks:
        print(f"  {name:.<40} {status}")
    print()
    
    # Return True if all checks passed
    return all("✅" in status for _, status in checks)


def _ensure_venv_and_reexec() -> None:
    """Ensure .venv exists and re-exec this script under the .venv interpreter.

    This keeps agent runs reproducible and guarantees Python 3.12 for this repo.
    """
    project_root = Path(__file__).parent.parent
    venv_python = project_root / ".venv" / "bin" / "python"
    venv_dir = project_root / ".venv"

    # Avoid infinite loops
    if os.environ.get("WORK_ISSUE_REEXEC") == "1":
        return

    # If venv is missing, bootstrap it
    if not venv_python.exists():
        setup_script = project_root / "setup.sh"
        if not setup_script.exists():
            return

        print("⚙️  .venv not found. Bootstrapping environment via ./setup.sh ...")
        import subprocess

        result = subprocess.run(["bash", str(setup_script)], cwd=str(project_root))
        if result.returncode != 0:
            print("❌ setup.sh failed; cannot continue.")
            sys.exit(result.returncode)

    # If we're not already running inside the venv, re-exec
    in_venv = False
    try:
        # VIRTUAL_ENV is the most reliable indicator.
        if os.environ.get("VIRTUAL_ENV"):
            in_venv = Path(os.environ["VIRTUAL_ENV"]).resolve() == venv_dir.resolve()
        else:
            # Fallback: sys.prefix points at venv when active.
            in_venv = Path(sys.prefix).resolve() == venv_dir.resolve()
    except Exception:
        in_venv = False

    if not in_venv and venv_python.exists():
        print(f"🔁 Re-executing under .venv Python: {venv_python}")
        os.environ["WORK_ISSUE_REEXEC"] = "1"
        os.execv(str(venv_python), [str(venv_python), str(Path(__file__).resolve()), *sys.argv[1:]])


async def _interactive_mode(agent):
    """Run interactive mode for follow-up instructions."""
    print("\n" + "=" * 70)
    print("💬 Interactive Mode - Give additional instructions to the agent")
    print("   Type 'exit' or 'quit' to finish")
    print("=" * 70)
    print()
    
    while True:
        try:
            user_input = input("\n You: ").strip()
            
            if not user_input or user_input.lower() in ['exit', 'quit', 'q']:
                break
            
            print("Agent: ", end="", flush=True)
            response = await agent.continue_conversation(user_input)
            print(response)
            
        except (KeyboardInterrupt, EOFError):
            break
    
    print("\n👋 Ending interactive session")


if __name__ == "__main__":
    asyncio.run(main())
