#!/usr/bin/env python3
"""
workflow_agent.py - 6-Phase Workflow Agent

This agent automates the standard 6-phase issue resolution workflow:
1. Context Gathering
2. Planning
3. Implementation
4. Testing
5. Review
6. PR & Merge

Trained on Issues #24, #25 and continuously learning.
"""

import sys
from pathlib import Path
from typing import List, Optional

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from agents.base_agent import BaseAgent, AgentPhase  # noqa: E402


class WorkflowAgent(BaseAgent):
    """Agent that follows the 6-phase workflow from successful issue completions."""

    def __init__(self, kb_dir: Path = Path("agents/knowledge")):
        super().__init__(name="workflow_agent", version="1.0.0", kb_dir=kb_dir)

        # Define workflow phases
        self.phases = [
            AgentPhase("Phase 1: Context", "Read issue and gather context"),
            AgentPhase("Phase 2: Planning", "Create planning document"),
            AgentPhase(
                "Phase 3: Implementation", "Implement changes with test-first approach"
            ),
            AgentPhase("Phase 4: Testing", "Build and test changes"),
            AgentPhase("Phase 5: Review", "Self-review and Copilot review"),
            AgentPhase("Phase 6: PR & Merge", "Create PR and merge"),
        ]

    def _validate_issue_number(self, issue_num: int) -> None:
        """Validate issue number to prevent command injection.

        Args:
            issue_num: Issue number to validate

        Raises:
            ValueError: If issue number is invalid
        """
        if not isinstance(issue_num, int):
            raise ValueError(f"Issue number must be an integer, got {type(issue_num)}")
        if issue_num < self.MIN_ISSUE_NUMBER or issue_num > self.MAX_ISSUE_NUMBER:
            raise ValueError(
                f"Issue number must be between {self.MIN_ISSUE_NUMBER} and {self.MAX_ISSUE_NUMBER}"
            )

    def execute(self, issue_num: int, **kwargs) -> bool:
        """Execute the complete 6-phase workflow.

        Args:
            issue_num: GitHub issue number to process
            **kwargs: Additional parameters

        Returns:
            True if all phases completed successfully

        Raises:
            ValueError: If issue number is invalid
        """
        # Validate inputs
        self._validate_issue_number(issue_num)

        self.log(f"🎯 Executing workflow for Issue #{issue_num}", "info")

        # Load principles
        principles = self._load_principles()
        self.log(f"Loaded {len(principles)} guiding principles", "info")

        # Execute each phase
        for phase in self.phases:
            success = self._execute_phase(phase, issue_num)

            if not success and not phase.skipped:
                self.log(f"Phase failed: {phase.name}", "error")
                return False

        # Display summary
        self._display_summary()

        return all(p.completed or p.skipped for p in self.phases)

    def _execute_phase(self, phase: AgentPhase, issue_num: int) -> bool:
        """Execute a single phase."""
        self.log(f"\n{'='*60}", "info")
        self.log(f"{phase.name}: {phase.description}", "info")
        self.log(f"{'='*60}", "info")

        phase.start()

        try:
            if "Phase 1" in phase.name:
                success = self._phase1_context(issue_num)
            elif "Phase 2" in phase.name:
                success = self._phase2_planning(issue_num)
            elif "Phase 3" in phase.name:
                success = self._phase3_implementation(issue_num)
            elif "Phase 4" in phase.name:
                success = self._phase4_testing(issue_num)
            elif "Phase 5" in phase.name:
                success = self._phase5_review(issue_num)
            elif "Phase 6" in phase.name:
                success = self._phase6_merge(issue_num)
            else:
                success = False

            if success:
                phase.complete()
                self.log(
                    f"✅ {phase.name} completed in {phase.duration_minutes():.1f} minutes",
                    "success",
                )
            else:
                phase.fail("Phase execution returned False")

            return success

        except Exception as e:
            phase.fail(str(e))
            self.log(f"❌ {phase.name} failed: {e}", "error")
            return False

    def _phase1_context(self, issue_num: int) -> bool:
        """Phase 1: Context Gathering.

        Args:
            issue_num: Validated issue number

        Returns:
            True if phase completed successfully
        """
        self.log("📖 Reading issue details", "progress")

        # Validate and safely construct command (issue_num already validated as int)
        # Get issue details
        result = self.run_command(
            f"gh issue view {issue_num}", "Fetching issue from GitHub"
        )

        if result.returncode != 0:
            self.log("Failed to fetch issue", "error")
            return False

        # Display issue summary
        lines = result.stdout.split("\n")
        title_line = next((line for line in lines if line.strip()), "")
        self.log(f"Issue: {title_line}", "info")

        # Gather related files
        self.log("📂 Analyzing codebase context", "progress")

        # Search for related files mentioned in issue
        # (In real implementation, this would analyze issue body for file mentions)

        if not self.dry_run:
            print("\n" + "=" * 60)
            print(result.stdout)
            print("=" * 60)
            print("\n⏸️  Review the issue context above.")
            input("Press Enter when ready to continue to Planning phase...")

        return True

    def _phase2_planning(self, issue_num: int) -> bool:
        """Phase 2: Planning."""
        self.log("📝 Creating planning document", "progress")

        plan_file = Path(f"docs/issues/issue-{issue_num}-plan.md")
        plan_file.parent.mkdir(parents=True, exist_ok=True)

        # Estimate time
        estimated_hours = self.estimate_time("planning")
        self.log(f"Estimated time for this issue: {estimated_hours:.1f} hours", "info")

        # Key principles from knowledge base
        principles = [
            "✓ No hallucinations - verify everything against actual code",
            "✓ Test-first approach - write/update tests before implementation",
            "✓ Get approval before removing functionality",
            "✓ Complete all 6 phases - no shortcuts",
        ]

        if self.dry_run:
            self.log(f"Would create: {plan_file}", "info")
            for principle in principles:
                self.log(principle, "info")
        else:
            # Create basic planning template
            plan_content = f"""# Issue #{issue_num} - Implementation Plan

**Created:** {self._get_timestamp()}
**Estimated Time:** {estimated_hours:.1f} hours

## Objective

[Describe the goal based on issue]

## Approach

1. **Analysis**
   - [ ] Read issue requirements
   - [ ] Identify affected components
   - [ ] Review existing code

2. **Design**
   - [ ] Plan implementation approach
   - [ ] Identify test cases
   - [ ] Consider edge cases

3. **Implementation**
   - [ ] Write/update tests first
   - [ ] Implement changes
   - [ ] Update documentation

## Acceptance Criteria

[From issue description]

## Key Principles

{chr(10).join(f'- {p}' for p in principles)}

## Risks & Mitigation

- [List potential risks]

## Time Tracking

- Planning: [Actual time]
- Implementation: [Actual time]
- Testing: [Actual time]
- Total: [Sum]
"""

            plan_file.write_text(plan_content)
            self.log(f"Created planning document: {plan_file}", "success")

            print(f"\n📄 Planning document created at: {plan_file}")
            print("\n⏸️  Fill in the planning document with details from the issue.")
            input("Press Enter when planning is complete...")

        return True

    def _phase3_implementation(self, issue_num: int) -> bool:
        """Phase 3: Implementation."""
        self.log("🔨 Implementation phase", "progress")

        self.log("Key principle: Test-first approach", "info")
        self.log("Write or update tests before implementing changes", "info")

        if not self.dry_run:
            print("\n📋 Implementation Checklist:")
            print("  1. Write/update tests first")
            print("  2. Run tests (should fail for new features)")
            print("  3. Implement changes")
            print("  4. Run tests (should pass)")
            print("  5. Commit changes with descriptive message")
            print("\n⚠️  Important: Get approval before removing any functionality")
            print("\n⏸️  Complete the implementation.")
            input("Press Enter when implementation is complete...")

        return True

    def _phase4_testing(self, issue_num: int) -> bool:
        """Phase 4: Testing."""
        self.log("🧪 Running tests and build", "progress")

        # Check if this is a client-side issue
        client_dir = Path("_external/AI-Agent-Framework-Client")

        if client_dir.exists():
            self.log("Detected client-side repository", "info")

            # Build
            self.log("Running build...", "progress")
            result = self.run_command(
                f"cd {client_dir} && npm run build",
                "Building client application",
                check=False,
            )

            if result.returncode != 0:
                # Check for known problems
                known_problem = self.check_known_problem(result.stderr or result.stdout)
                if known_problem:
                    self.log(
                        f"Known problem detected: {known_problem['problem']}", "warning"
                    )
                    self.log(f"Solution: {known_problem['solution']}", "info")

                    if not self.dry_run:
                        print(f"\n💡 Suggested solution: {known_problem['solution']}")
                        response = input("Apply suggested fix? (y/n): ")
                        if response.lower() != "y":
                            return False
                else:
                    self.log("Build failed", "error")
                    return False

            # Tests
            self.log("Running tests...", "progress")
            result = self.run_command(
                f"cd {client_dir} && npx vitest run", "Running test suite", check=False
            )

            if result.returncode != 0:
                self.log("Tests failed", "error")
                return False

            self.log("All tests passed", "success")

        else:
            # Backend tests
            self.log("Running backend tests...", "progress")
            result = self.run_command("pytest", "Running pytest", check=False)

            if result.returncode != 0:
                self.log("Tests failed", "error")
                return False

        return True

    def _phase5_review(self, issue_num: int) -> bool:
        """Phase 5: Review."""
        self.log("👀 Review phase", "progress")

        self.log("Step 7: Self-review", "info")
        self.log("Step 8: Copilot review", "info")

        # Get changed files
        result = self.run_command(
            "git diff --name-only HEAD", "Getting changed files", check=False
        )

        if result.returncode == 0 and result.stdout:
            changed_files = result.stdout.strip().split("\n")
            self.log(f"Changed files: {len(changed_files)}", "info")
            for f in changed_files:
                self.log(f"  - {f}", "info")

        if not self.dry_run:
            print("\n📋 Review Checklist:")
            print("  Step 7 - Self-Review:")
            print("    • No functionality removed without approval")
            print("    • Code follows project conventions")
            print("    • All acceptance criteria met")
            print("    • No debug code or console.logs left")
            print("\n  Step 8 - Copilot Review:")
            print(
                "    • Ask: '@workspace review these changes for Issue #{}'".format(
                    issue_num
                )
            )
            print("    • Address any issues found")
            print("\n⏸️  Complete both review steps.")
            input("Press Enter when reviews are complete...")

        return True

    def _phase6_merge(self, issue_num: int) -> bool:
        """Phase 6: PR & Merge."""
        self.log("🚀 Creating PR and merging", "progress")

        # Check for prmerge script
        prmerge_script = Path("scripts/prmerge")

        if self.dry_run:
            self.log("Would create PR with gh pr create --fill", "info")
            self.log("Would run prmerge validation and merge", "info")
            return True

        # Create PR
        print("\n📋 Creating Pull Request...")
        print("Next step: gh pr create --fill")

        input("Press Enter to create PR...")

        result = self.run_command(
            "gh pr create --fill", "Creating pull request", check=False
        )

        if result.returncode != 0:
            self.log("Failed to create PR", "error")
            return False

        # Extract PR number
        pr_num = self._extract_pr_number(result.stdout)
        if pr_num:
            self.log(f"Created PR #{pr_num}", "success")

        # Run prmerge if available
        if prmerge_script.exists():
            print("\n🔍 Running prmerge validation...")
            input("Press Enter to run prmerge...")

            result = self.run_command(
                str(prmerge_script), "Running prmerge workflow", check=False
            )

            if result.returncode != 0:
                self.log("prmerge validation failed", "error")
                self.log("Review the output and fix any issues", "warning")
                return False

            self.log("PR merged successfully", "success")
        else:
            self.log("prmerge script not found, manual merge required", "warning")
            print("\nManual merge steps:")
            print("  1. Wait for CI checks to pass")
            print("  2. Get approval from reviewers")
            print("  3. Merge PR")
            input("Press Enter when PR is merged...")

        return True

    def _load_principles(self) -> List[str]:
        """Load key principles from knowledge base."""
        principles = [
            "No hallucinations - verify everything",
            "Complete all 6 phases",
            "Test-first approach",
            "Get approval before removing functionality",
        ]

        # Principles from knowledge base could be loaded here
        # workflow_patterns = self.knowledge_base.get("workflow_patterns", {})

        return principles

    def _extract_pr_number(self, gh_output: str) -> Optional[int]:
        """Extract PR number from gh pr create output."""
        import re

        match = re.search(r"/pull/(\d+)", gh_output)
        if match:
            return int(match.group(1))
        return None

    def _get_timestamp(self) -> str:
        """Get formatted timestamp."""
        from datetime import datetime

        return datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    def _display_summary(self):
        """Display workflow summary."""
        self.log("\n" + "=" * 60, "info")
        self.log("WORKFLOW SUMMARY", "info")
        self.log("=" * 60, "info")

        for phase in self.phases:
            self.log(str(phase), "info")

        total_time = sum(p.duration_minutes() for p in self.phases)
        self.log(
            f"\n📊 Total time: {total_time:.1f} minutes ({total_time/60:.1f} hours)",
            "info",
        )


def main():
    import argparse

    parser = argparse.ArgumentParser(
        description="6-Phase Workflow Agent for Issue Resolution",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  Run workflow for Issue #26:
    ./agents/workflow_agent.py --issue 26

  Dry run (no actual commands):
    ./agents/workflow_agent.py --issue 26 --dry-run
        """,
    )

    parser.add_argument(
        "--issue", type=int, required=True, help="Issue number to process"
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Run in dry-run mode (no actual commands)",
    )
    parser.add_argument(
        "--kb-dir",
        type=str,
        default="agents/knowledge",
        help="Knowledge base directory",
    )

    args = parser.parse_args()

    agent = WorkflowAgent(kb_dir=Path(args.kb_dir))
    success = agent.run(dry_run=args.dry_run, issue_num=args.issue)

    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
