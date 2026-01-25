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
import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from agents.autonomous_workflow_agent import AutonomousWorkflowAgent


async def main():
    """Main entry point."""
    import argparse
    
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
  
  # Dry run - analyze and plan without changes
  ./scripts/work-issue.py --issue 26 --dry-run
  
  # Interactive - pause for approval between phases
  ./scripts/work-issue.py --issue 26 --interactive

Requirements:
  - Python 3.10+ with agent-framework-azure-ai installed
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
    
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Analyze and plan but don't make actual changes"
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
            dry_run=args.dry_run
        )
        
        await agent.initialize()
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
    if version.major == 3 and version.minor >= 10:
        checks.append((f"Python {version.major}.{version.minor}", "✅"))
    else:
        checks.append((f"Python {version.major}.{version.minor}", "❌ Need Python 3.10+"))
    
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


async def _interactive_mode(agent: AutonomousWorkflowAgent):
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
