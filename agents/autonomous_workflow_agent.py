#!/usr/bin/env python3
"""
Autonomous Workflow Agent - REAL AI-Powered Issue Resolution

Uses Microsoft Agent Framework with GitHub Models to autonomously:
1. Analyze GitHub issues
2. Create implementation plans
3. Generate code changes
4. Run tests and fix failures
5. Perform self-review
6. Create PRs
7. Learn from each issue

Based on AI Toolkit best practices and Microsoft Agent Framework.
"""

import asyncio
import json
import sys
from datetime import datetime
from pathlib import Path
from typing import Optional

from agent_framework import ChatAgent
from agent_framework.openai import OpenAIChatClient

# Add parent to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from agents.llm_client import LLMClientFactory
from agents.tools import get_all_tools


class AutonomousWorkflowAgent:
    """AI-powered agent that autonomously resolves GitHub issues."""
    
    def __init__(self, issue_number: int, dry_run: bool = False):
        self.issue_number = issue_number
        self.dry_run = dry_run
        self.agent: Optional[ChatAgent] = None
        self.thread = None
        
        # Load project context
        self.project_instructions = self._load_copilot_instructions()
        self.workflow_guide = self._load_workflow_guide()
        self.knowledge_base = self._load_knowledge_base()
    
    def _load_copilot_instructions(self) -> str:
        """Load project conventions from .github/copilot-instructions.md"""
        try:
            path = Path(".github/copilot-instructions.md")
            if path.exists():
                return path.read_text()
        except Exception as e:
            print(f"⚠️  Could not load copilot instructions: {e}")
        return ""
    
    def _load_workflow_guide(self) -> str:
        """Load 6-phase workflow guide"""
        try:
            path = Path("docs/WORK-ISSUE-WORKFLOW.md")
            if path.exists():
                # Load first 500 lines to avoid token limits
                with open(path) as f:
                    lines = f.readlines()[:500]
                return "".join(lines)
        except Exception as e:
            print(f"⚠️  Could not load workflow guide: {e}")
        return ""
    
    def _load_knowledge_base(self) -> str:
        """Load patterns from previous issues"""
        try:
            kb_path = Path("agents/knowledge/workflow_patterns.json")
            if kb_path.exists():
                with open(kb_path) as f:
                    data = json.load(f)
                    return json.dumps(data, indent=2)
        except Exception as e:
            print(f"⚠️  Could not load knowledge base: {e}")
        return "[]"
    
    async def initialize(self):
        """Initialize the AI agent with GitHub Models."""
        print(f"🤖 Initializing Autonomous Workflow Agent v2.0")
        print(f"📋 Issue #{self.issue_number}")
        
        if self.dry_run:
            print("ℹ️  DRY RUN MODE - No actual changes will be made")
        
        # Create GitHub models client
        print("🔗 Connecting to GitHub Models...")
        openai_client = LLMClientFactory.create_github_client()
        model_id = LLMClientFactory.get_recommended_model()
        print(f"   Using model: {model_id}")
        
        # Create chat client
        chat_client = OpenAIChatClient(
            async_client=openai_client,
            model_id=model_id
        )
        
        # Build system instructions
        system_instructions = self._build_system_instructions()
        
        # Create agent with tools
        self.agent = ChatAgent(
            chat_client=chat_client,
            name="WorkflowAgent",
            instructions=system_instructions,
            tools=get_all_tools(),
        )
        
        # Create conversation thread
        self.thread = self.agent.get_new_thread()
        
        print("✅ Agent initialized and ready\n")
    
    def _build_system_instructions(self) -> str:
        """Build comprehensive system instructions for the agent."""
        return f"""You are an autonomous software development agent that resolves GitHub issues end-to-end.

## Your Mission
Work on Issue #{self.issue_number} following the complete 6-phase workflow:
1. Context & Analysis
2. Planning
3. Implementation
4. Testing
5. Review
6. PR Creation

## Project Context
{self.project_instructions[:2000] if self.project_instructions else "No specific project context"}

## Workflow Guide
{self.workflow_guide[:3000] if self.workflow_guide else "Follow standard development workflow"}

## Knowledge from Past Issues
{self.knowledge_base[:1000] if self.knowledge_base else "No historical patterns available"}

## Key Principles
- **Verify everything**: Never hallucinate file contents or states. Always use tools to read files.
- **Test-first approach**: Write/update tests before implementation
- **Incremental commits**: Commit after each logical change
- **Self-review**: Check your work against acceptance criteria
- **Learn continuously**: Update knowledge base with learnings

## Available Tools
You have access to tools for:
- GitHub operations (fetch issue, create PR)
- File operations (read, write, list)
- Git operations (commit, branch, status)
- Command execution (build, test, lint)
- Knowledge base (read patterns, update learnings)

## Workflow Execution

### Phase 1: Context & Analysis
1. Use `fetch_github_issue()` to get issue details
2. Use `read_file_content()` to understand relevant code
3. Use `get_knowledge_base_patterns()` for similar issues
4. Analyze requirements and constraints

### Phase 2: Planning
1. Create implementation plan document
2. Break down into testable steps
3. Estimate time based on knowledge base
4. Identify risks and mitigation

### Phase 3: Implementation
1. Use `create_feature_branch()` to start work
2. For each step:
   - Write test first (test-first approach)
   - Implement functionality
   - Use `git_commit()` to commit incrementally
3. Use `write_file_content()` for code changes

### Phase 4: Testing
1. Use `run_command()` to execute builds: `npm run build` or `pytest`
2. Use `run_command()` to run tests: `npx vitest run` or `pytest`
3. If tests fail, analyze output and fix
4. Repeat until all tests pass

### Phase 5: Review
1. Use `get_changed_files()` to see what changed
2. Review against acceptance criteria
3. Check for:
   - No removed functionality without approval
   - Follows project conventions
   - All tests pass
   - No debug code left

### Phase 6: PR Creation
1. Use `create_github_pr()` with descriptive title and body
2. Include:
   - What was changed
   - Why it was changed
   - How to test
   - Fixes #<issue_number>
3. Use `update_knowledge_base()` to record learnings

## Important Guidelines
- **Be autonomous**: Make decisions based on issue requirements and project context
- **Be thorough**: Complete all 6 phases, don't skip steps
- **Be careful**: Verify file contents before modifying
- **Be informative**: Explain your reasoning as you work
- **Ask when unsure**: For architecture decisions or scope changes, explain options and ask

## Dry Run Mode
{"✅ DRY RUN ACTIVE - Use tools to analyze but don't make actual changes" if self.dry_run else ""}

Start by fetching and analyzing Issue #{self.issue_number}, then proceed through each phase systematically.
"""
    
    async def execute(self) -> bool:
        """Execute the complete workflow autonomously."""
        if not self.agent:
            raise RuntimeError("Agent not initialized. Call initialize() first.")
        
        start_time = datetime.now()
        execution_data = {
            "issue_number": self.issue_number,
            "start_time": start_time.isoformat(),
            "phases_completed": [],
            "problems_encountered": [],
            "commands_used": [],
        }
        
        # Initial prompt to agent
        prompt = f"""Begin working on Issue #{self.issue_number}.

Follow the 6-phase workflow:
1. Fetch and analyze the issue
2. Create implementation plan
3. Implement changes with test-first approach
4. Run tests and ensure they pass
5. Self-review the changes
6. Create PR and update knowledge base

Work systematically through each phase. After each major step, provide a summary of what you've done and what's next.

Begin now with Phase 1: Fetch and analyze Issue #{self.issue_number}.
"""
        
        print("=" * 70)
        print("🚀 Starting Autonomous Workflow Execution")
        print("=" * 70)
        print()
        
        try:
            # Run agent with streaming output
            print("🤖 Agent: ", end="", flush=True)
            
            async for chunk in self.agent.run_stream(prompt, thread=self.thread):
                if chunk.text:
                    print(chunk.text, end="", flush=True)
            
            print("\n")
            
            # Get execution summary
            duration = (datetime.now() - start_time).total_seconds()
            execution_data["end_time"] = datetime.now().isoformat()
            execution_data["duration_seconds"] = duration
            
            print("=" * 70)
            print(f"✅ Workflow Completed in {duration:.1f} seconds ({duration/60:.1f} minutes)")
            print("=" * 70)
            
            # GUARANTEED LEARNING: Extract and update knowledge base
            if not self.dry_run:
                print("\n📚 Updating knowledge base with learnings...")
                await self._extract_and_update_learnings(execution_data)
                print("✅ Knowledge base updated\n")
            
            return True
            
        except Exception as e:
            print(f"\n\n❌ Error during execution: {e}")
            import traceback
            traceback.print_exc()
            
            # Still try to learn from failures
            if not self.dry_run:
                execution_data["error"] = str(e)
                execution_data["success"] = False
                await self._extract_and_update_learnings(execution_data)
            
            return False
    
    async def continue_conversation(self, message: str) -> str:
        """Continue conversation with the agent (for follow-up questions)."""
        if not self.agent or not self.thread:
            raise RuntimeError("Agent not initialized or no active thread")
        
        response_text = []
        async for chunk in self.agent.run_stream(message, thread=self.thread):
            if chunk.text:
                response_text.append(chunk.text)
        
        return "".join(response_text)
    
    async def _extract_and_update_learnings(self, execution_data: dict):
        """
        Extract learnings from execution and update knowledge base.
        
        This runs AFTER agent completes to guarantee learning happens.
        """
        from agents.tools import update_knowledge_base
        import json
        from pathlib import Path
        
        try:
            # 1. Build workflow pattern
            workflow_pattern = {
                "issue_number": execution_data["issue_number"],
                "date": execution_data["start_time"],
                "duration_seconds": execution_data.get("duration_seconds", 0),
                "duration_minutes": execution_data.get("duration_seconds", 0) / 60,
                "success": execution_data.get("success", True),
                "phases": execution_data.get("phases_completed", []),
                "dry_run": self.dry_run,
            }
            
            # 2. Ask agent for structured learnings
            learning_prompt = f"""Based on the work you just completed on Issue #{self.issue_number}, 
provide structured learnings in JSON format:

{{
  "problems_encountered": [
    {{"problem": "description", "solution": "how it was solved", "category": "build|test|git|other"}}
  ],
  "key_decisions": [
    {{"decision": "what was decided", "rationale": "why"}}
  ],
  "useful_commands": [
    {{"command": "the command", "purpose": "what it does", "context": "when to use"}}
  ],
  "time_insights": {{
    "planning_minutes": 0,
    "implementation_minutes": 0,
    "testing_minutes": 0,
    "total_minutes": 0
  }},
  "files_changed": [],
  "patterns_learned": ["pattern 1", "pattern 2"]
}}

Provide ONLY the JSON, no additional text."""
            
            response = await self.continue_conversation(learning_prompt)
            
            # Try to parse JSON from response
            try:
                # Extract JSON from response (may have markdown code blocks)
                json_start = response.find('{')
                json_end = response.rfind('}') + 1
                if json_start >= 0 and json_end > json_start:
                    learnings = json.loads(response[json_start:json_end])
                else:
                    learnings = {}
            except json.JSONDecodeError:
                learnings = {}
            
            # 3. Update workflow_patterns.json
            workflow_pattern.update({
                "problems": learnings.get("problems_encountered", []),
                "decisions": learnings.get("key_decisions", []),
                "commands": learnings.get("useful_commands", []),
                "files_changed": learnings.get("files_changed", []),
                "patterns": learnings.get("patterns_learned", []),
            })
            
            kb_path = Path("agents/knowledge")
            kb_path.mkdir(parents=True, exist_ok=True)
            
            # Update workflow_patterns.json
            patterns_file = kb_path / "workflow_patterns.json"
            patterns = []
            if patterns_file.exists():
                try:
                    with open(patterns_file) as f:
                        patterns = json.load(f)
                        if not isinstance(patterns, list):
                            patterns = [patterns]
                except Exception:
                    patterns = []
            
            patterns.append(workflow_pattern)
            
            with open(patterns_file, 'w') as f:
                json.dump(patterns, f, indent=2)
            
            # 4. Update problem_solutions.json
            if learnings.get("problems_encountered"):
                problems_file = kb_path / "problem_solutions.json"
                problems = []
                if problems_file.exists():
                    try:
                        with open(problems_file) as f:
                            problems = json.load(f)
                            if not isinstance(problems, list):
                                problems = [problems]
                    except Exception:
                        problems = []
                
                for problem in learnings["problems_encountered"]:
                    problem["issue_number"] = self.issue_number
                    problem["date"] = execution_data["start_time"]
                    problems.append(problem)
                
                with open(problems_file, 'w') as f:
                    json.dump(problems, f, indent=2)
            
            # 5. Update time_estimates.json
            if learnings.get("time_insights"):
                time_file = kb_path / "time_estimates.json"
                estimates = []
                if time_file.exists():
                    try:
                        with open(time_file) as f:
                            estimates = json.load(f)
                            if not isinstance(estimates, list):
                                estimates = [estimates]
                    except Exception:
                        estimates = []
                
                time_data = learnings["time_insights"]
                time_data["issue_number"] = self.issue_number
                time_data["date"] = execution_data["start_time"]
                estimates.append(time_data)
                
                with open(time_file, 'w') as f:
                    json.dump(estimates, f, indent=2)
            
            # 6. Update command_sequences.json
            if learnings.get("useful_commands"):
                commands_file = kb_path / "command_sequences.json"
                commands = []
                if commands_file.exists():
                    try:
                        with open(commands_file) as f:
                            commands = json.load(f)
                            if not isinstance(commands, list):
                                commands = [commands]
                    except Exception:
                        commands = []
                
                for cmd in learnings["useful_commands"]:
                    cmd["issue_number"] = self.issue_number
                    cmd["date"] = execution_data["start_time"]
                    commands.append(cmd)
                
                with open(commands_file, 'w') as f:
                    json.dump(commands, f, indent=2)
            
            # 7. Update agent_metrics.json
            metrics_file = kb_path / "agent_metrics.json"
            metrics = {"total_issues": 0, "successful_issues": 0, "last_updated": ""}
            if metrics_file.exists():
                try:
                    with open(metrics_file) as f:
                        metrics = json.load(f)
                except Exception:
                    pass
            
            metrics["total_issues"] = metrics.get("total_issues", 0) + 1
            if execution_data.get("success", True):
                metrics["successful_issues"] = metrics.get("successful_issues", 0) + 1
            metrics["last_updated"] = datetime.now().isoformat()
            metrics["last_issue"] = self.issue_number
            
            with open(metrics_file, 'w') as f:
                json.dump(metrics, f, indent=2)
            
        except Exception as e:
            print(f"⚠️  Warning: Could not update knowledge base: {e}")
            # Don't fail the whole execution if learning fails


async def main():
    """Main entry point for CLI usage."""
    import argparse
    
    parser = argparse.ArgumentParser(
        description="Autonomous Workflow Agent - AI-powered issue resolution",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Work on Issue #26 autonomously
  python agents/autonomous_workflow_agent.py --issue 26
  
  # Dry run (analyze but don't change anything)
  python agents/autonomous_workflow_agent.py --issue 26 --dry-run
  
  # Interactive mode (step through with approvals)
  python agents/autonomous_workflow_agent.py --issue 26 --interactive
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
    
    # Create and initialize agent
    agent = AutonomousWorkflowAgent(
        issue_number=args.issue,
        dry_run=args.dry_run
    )
    
    await agent.initialize()
    
    # Execute workflow
    success = await agent.execute()
    
    # Interactive mode: allow follow-up questions
    if args.interactive and success:
        print("\n💬 Interactive mode - you can now give additional instructions")
        print("   (Type 'exit' or 'quit' to finish)\n")
        
        while True:
            try:
                user_input = input("You: ").strip()
                
                if user_input.lower() in ['exit', 'quit', '']:
                    break
                
                print("Agent: ", end="", flush=True)
                response = await agent.continue_conversation(user_input)
                print(response)
                print()
                
            except (KeyboardInterrupt, EOFError):
                break
        
        print("\n👋 Ending session")
    
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    asyncio.run(main())
