# How to Restore Chat Sessions and Create Custom Agents

## Overview

This guide explains how to restore exported chat sessions and use them as foundation for creating custom AI agents. Chat exports serve as complete knowledge bases capturing workflows, decisions, commands, and context from successful project implementations.

## Table of Contents

1. [Restoring an Exported Chat Session](#restoring-an-exported-chat-session)
2. [Using Chat Exports as Agent Context](#using-chat-exports-as-agent-context)
3. [Creating a Custom Agent](#creating-a-custom-agent)
4. [Agent Development Best Practices](#agent-development-best-practices)
5. [Example: Workflow Agent](#example-workflow-agent)

---

## Restoring an Exported Chat Session

### What is a Chat Export?

Chat exports are comprehensive Markdown documents that capture:

- Complete conversation history with all phases
- Exact commands used (reproducible syntax)
- All decisions, corrections, and learnings
- Technical context (files changed, commits, metrics)
- Problem resolution details with root causes and solutions

**Example:** [2026-01-18-step1-hybrid-workflow-creation.md](../chat/2026-01-18-step1-hybrid-workflow-creation.md)

### Restoration Methods

#### Method 1: Direct Context Injection (Recommended)

Use the chat export as context in a new conversation:

```bash
# Copy the export to your workspace
cp docs/chat/2026-01-18-step1-hybrid-workflow-creation.md /tmp/context.md

# Start a new agent session with the context
# In GitHub Copilot Chat or similar:
# @workspace Review /tmp/context.md and help me [your goal]
```

**Pros:**

- Immediate access to complete context
- No parsing or preprocessing required
- Full conversation history available

**Cons:**

- Large context window usage (487 lines = ~15KB)
- May need to reference specific sections

#### Method 2: Section-Based Restoration

Extract specific sections for targeted context:

```bash
# Extract specific phase
sed -n '/## Phase 2: Issue #25 Implementation/,/## Phase 3:/p' \
    docs/chat/2026-01-18-step1-hybrid-workflow-creation.md \
  > /tmp/phase2-context.md

# Extract commands reference
sed -n '/## Commands Reference/,/## Final Summary/p' \
    docs/chat/2026-01-18-step1-hybrid-workflow-creation.md \
  > /tmp/commands-context.md
```

**Use cases:**

- Learning specific workflow phases
- Reproducing exact command sequences
- Understanding problem resolution approaches

#### Method 3: Knowledge Base Integration

Convert chat export into structured knowledge base:

````python
# scripts/extract_learnings.py
import re
import json

def extract_learnings(export_file):
    """Extract structured learnings from chat export."""
    learnings = {
        "workflow_phases": [],
        "commands": [],
        "problems_solved": [],
        "time_metrics": {},
        "key_principles": []
    }

    with open(export_file, 'r') as f:
        content = f.read()

    # Extract workflow phases
    phases = re.findall(r'## (Phase \d+: .*?)\n', content)
    learnings["workflow_phases"] = phases

    # Extract commands (look for bash/shell code blocks)
    commands = re.findall(r'```(?:bash|shell)\n(.*?)\n```', content, re.DOTALL)
    learnings["commands"] = [cmd.strip() for cmd in commands]

    # Extract problems and solutions
    problems = re.findall(r'\*\*Problem:\*\* (.*?)\n.*?\*\*Solution:\*\* (.*?)\n',
                          content, re.DOTALL)
    learnings["problems_solved"] = [
        {"problem": p[0].strip(), "solution": p[1].strip()}
        for p in problems
    ]

    # Extract time metrics
    time_match = re.search(r'(\d+\.?\d*) hours actual vs (\d+\.?\d*) estimated', content)
    if time_match:
        learnings["time_metrics"] = {
            "actual": float(time_match.group(1)),
            "estimated": float(time_match.group(2)),
            "variance": float(time_match.group(1)) - float(time_match.group(2))
        }

    return learnings

# Usage
learnings = extract_learnings('docs/chat/2026-01-18-step1-hybrid-workflow-creation.md')
with open('.issue-resolution-knowledge.json', 'r') as f:
    kb = json.load(f)
    kb['structured_learnings'] = learnings

with open('.issue-resolution-knowledge.json', 'w') as f:
    json.dump(kb, f, indent=2)
````

---

## Using Chat Exports as Agent Context

### Context Window Strategies

**Full Context (542 lines = ~15KB):**

- Use for: Complete workflow recreation, comprehensive understanding
- Best for: Claude Sonnet 4.5 (200K context), GPT-4 Turbo (128K context)
- Command: `@workspace #file:docs/chat/2026-01-18-step1-hybrid-workflow-creation.md`

**Selective Context (50-200 lines):**

- Use for: Specific phase learning, targeted problem solving
- Best for: Smaller models or focused tasks
- Extract: Phase sections, Commands Reference, specific problems

**Hybrid Approach (Recommended):**

```
1. Start with summary section (50 lines)
2. Reference full export for details as needed
3. Extract specific commands when reproducing actions
```

### Context Preparation Template

````markdown
# Agent Context: [Task Name]

## Goal

[What you want to accomplish]

## Relevant Experience

Based on: docs/chat/2026-01-18-step1-hybrid-workflow-creation.md

### Key Learnings Applied

1. [Principle 1 from export]
2. [Principle 2 from export]

### Commands to Reuse

```bash
[Exact commands from export]
```
````

### Problems to Avoid

- [Problem 1 from export and its solution]
- [Problem 2 from export and its solution]

## Specific Request

[Your detailed instructions]

````

---

## Creating a Custom Agent

### Agent Types from Chat Exports

#### 1. Workflow Agent
**Purpose:** Automate the 6-phase issue resolution workflow

**Context Required:**
- Complete workflow phases (Phase 1-6)
- Checkpoint definitions
- Key principles (no hallucinations, approval required, complete all phases)

**Implementation:**
```python
# scripts/workflow-agent.py
import json
from pathlib import Path

class WorkflowAgent:
    """Agent that follows 6-phase workflow from Issue #25 learnings."""

    def __init__(self, chat_export_path):
        self.phases = self._load_phases(chat_export_path)
        self.current_phase = 1
        self.checkpoints = {}

    def _load_phases(self, export_path):
        """Extract workflow phases from chat export."""
        with open(export_path) as f:
            content = f.read()

        phases = {}
        # Parse phases from export
        import re
        phase_pattern = r'## Phase (\d+): (.*?)\n\n(.*?)(?=\n## Phase|\Z)'
        matches = re.findall(phase_pattern, content, re.DOTALL)

        for num, name, description in matches:
            phases[int(num)] = {
                "name": name,
                "description": description.strip(),
                "completed": False
            }

        return phases

    def execute_phase(self, phase_num, context):
        """Execute specific workflow phase with context."""
        phase = self.phases.get(phase_num)
        if not phase:
            raise ValueError(f"Phase {phase_num} not found")

        print(f"\n=== Phase {phase_num}: {phase['name']} ===")
        print(f"{phase['description'][:200]}...")

        # Phase-specific logic
        if phase_num == 1:
            self._phase1_context_gathering(context)
        elif phase_num == 2:
            self._phase2_planning(context)
        # ... implement remaining phases

        self.checkpoints[phase_num] = {
            "completed": True,
            "timestamp": datetime.now().isoformat()
        }

    def _phase1_context_gathering(self, context):
        """Implement Phase 1 based on export learnings."""
        print("📖 Reading issue details...")
        print("🔍 Gathering codebase context...")
        # Use commands from export

    def _phase2_planning(self, context):
        """Implement Phase 2 with planning document creation."""
        print("📝 Creating planning document...")
        print("⏱️  Estimating time (using multiplier 0.875 from Issue #25)...")
        # Apply learnings from export

    def resume_from_checkpoint(self, phase_num):
        """Resume workflow from checkpoint."""
        if phase_num in self.checkpoints:
            self.current_phase = phase_num
            print(f"▶️  Resuming from Phase {phase_num}")

# Usage
agent = WorkflowAgent('docs/chat/2026-01-18-step1-hybrid-workflow-creation.md')
agent.execute_phase(1, {"issue_number": 26})
````

#### 2. Code Review Agent

**Purpose:** Perform self-review and Copilot review (Steps 7-8)

**Context Required:**

- Review cycle learnings (chat removal, breadcrumb fix)
- Acceptance criteria validation
- Build/test verification commands

**Implementation:**

```python
# scripts/review-agent.py
class ReviewAgent:
    """Agent that performs comprehensive code review."""

    def __init__(self, chat_export_path):
        self.review_checklist = self._load_review_patterns(chat_export_path)

    def _load_review_patterns(self, export_path):
        """Extract review patterns from chat export."""
        # Parse problems caught during review from export
        patterns = {
            "removed_functionality": {
                "pattern": r"removed|deleted",
                "severity": "critical",
                "example": "Chat functionality removed by mistake (Issue #25)"
            },
            "layout_issues": {
                "pattern": r"breadcrumb|navigation",
                "severity": "medium",
                "example": "Breadcrumb above chat (Issue #25)"
            }
        }
        return patterns

    def review_changes(self, files_changed):
        """Review changed files for common issues."""
        issues = []

        for file_path in files_changed:
            with open(file_path) as f:
                content = f.read()

            # Check against learned patterns
            for pattern_name, pattern_data in self.review_checklist.items():
                if re.search(pattern_data["pattern"], content, re.IGNORECASE):
                    issues.append({
                        "file": file_path,
                        "pattern": pattern_name,
                        "severity": pattern_data["severity"],
                        "example": pattern_data["example"]
                    })

        return issues

    def validate_acceptance_criteria(self, criteria_file):
        """Validate all acceptance criteria met."""
        # Use approach from Issue #25 Phase 3
        print("✅ Validating acceptance criteria...")
        # Check each criterion

# Usage
review_agent = ReviewAgent('docs/chat/2026-01-18-step1-hybrid-workflow-creation.md')
issues = review_agent.review_changes(['src/pages/Chat.tsx', 'src/App.tsx'])
```

#### 3. PR Merge Agent

**Purpose:** Automate PR validation, merge, and verification

**Context Required:**

- Complete prmerge command logic
- Validation functions (validate_pr_template)
- Verification steps
- Lessons learned display

**Implementation:**

```bash
#!/bin/bash
# scripts/pr-merge-agent.sh
# Agent that automates PR merge with learnings from a known-good export

source_chat_export() {
    # Extract prmerge logic from chat export
    EXPORT_FILE="docs/chat/2026-01-18-step1-hybrid-workflow-creation.md"

    # Parse validation rules
    VALIDATION_RULES=$(sed -n '/validate_pr_template/,/^}/p' "$EXPORT_FILE")

    # Parse verification steps
    VERIFICATION_STEPS=$(sed -n '/## Verification/,/^##/p' "$EXPORT_FILE")
}

validate_pr_template_agent() {
    local pr_num=$1

    echo "🔍 Agent: Validating PR template (learned from export)..."

    # Get PR body
    PR_BODY=$(gh pr view "$pr_num" --json body --jq '.body')

    # Check required sections (from Issue #25 learning)
    local required_sections=(
        "## What changed"
        "## Why"
        "## How to verify"
        "## Pre-merge checklist"
    )

    for section in "${required_sections[@]}"; do
        if ! echo "$PR_BODY" | grep -q "^$section"; then
            echo "❌ Missing section: $section"
            return 1
        fi
    done

    # Check evidence format (critical learning from exports)
    if echo "$PR_BODY" | grep -q "^- Evidence.*:$"; then
        echo "⚠️  Evidence on separate line (will fail CI)"
        echo "   Fix: Move evidence summary to same line as field"
        return 1
    fi

    echo "✅ PR template valid"
}

verify_merge_agent() {
    local pr_num=$1
    local issue_num=$2

    echo "🔍 Agent: Verifying merge completion..."

    # Verify PR merged (from Issue #25 Phase 5)
    PR_STATE=$(gh pr view "$pr_num" --json state --jq '.state')
    if [[ "$PR_STATE" != "MERGED" ]]; then
        echo "❌ PR not merged: $PR_STATE"
        return 1
    fi
    echo "✅ PR #$pr_num is MERGED"

    # Verify issue closed
    ISSUE_STATE=$(gh issue view "$issue_num" --json state --jq '.state')
    if [[ "$ISSUE_STATE" != "CLOSED" ]]; then
        echo "❌ Issue not closed: $ISSUE_STATE"
        return 1
    fi
    echo "✅ Issue #$issue_num is CLOSED"

    # Display lessons learned (from Issue #25)
    echo ""
    echo "📚 Lessons Learned (applied during this merge):"
    echo "  • PR template validated before CI"
    echo "  • Evidence kept inline (not in code blocks)"
    echo "  • Fresh CI run triggered with commit"
    echo "  • Verification confirmed PR merged and issue closed"
}

# Usage
source_chat_export
validate_pr_template_agent 61
verify_merge_agent 61 25
```

---

## Agent Development Best Practices

### 1. Extract Principles First

**From Chat Export → Agent Rules:**

```python
# Extract key principles from export
principles = {
    "no_hallucinations": "Never invent facts or features not in context",
    "approval_required": "Get user approval for major decisions",
    "complete_all_phases": "Never skip phases 1-6, even if tempted",
    "verify_everything": "Don't assume tests pass, builds succeed",
    "planning_document": "Always create planning doc in Phase 2"
}

# Convert to agent prompts
agent_instructions = f"""
You are a workflow agent trained on successful Issue #25 completion.

KEY PRINCIPLES (must follow):
{chr(10).join(f'- {k}: {v}' for k, v in principles.items())}

Your goal: Apply these principles to Issue #{{issue_num}}
"""
```

### 2. Capture Command Sequences

**Reproducible Workflows:**

```json
{
  "workflow_commands": {
    "phase1_context": [
      "gh issue view {{issue_num}} --json title,body,labels",
      "git grep -n 'related_pattern' src/",
      "semantic_search '{{search_query}}'"
    ],
    "phase3_validation": [
            "cd ../AI-Agent-Framework-Client",
      "npm run build",
      "npx vitest run --reporter=verbose"
    ],
    "phase5_merge": [
      "gh pr create --fill",
      "./scripts/prmerge",
      "gh issue close {{issue_num}}"
    ]
  }
}
```

### 3. Learn from Problems

**Problem Pattern Database:**

```python
class ProblemPatternAgent:
    """Agent that learns from past problems."""

    def __init__(self):
        self.patterns = self._load_from_export()

    def _load_from_export(self):
        return {
            "ci_validation_failure": {
                "symptoms": ["Build passes: Evidence must be filled"],
                "root_cause": "Evidence in code blocks, not inline",
                "solution": "Keep evidence summary on same line as field label",
                "prevention": "Run validate_pr_template before CI"
            },
            "removed_functionality": {
                "symptoms": ["User says 'X should not be removed'"],
                "root_cause": "Misinterpreted existing feature as demo code",
                "solution": "Ask user before removing any existing functionality",
                "prevention": "Mandatory self-review (Step 7)"
            }
        }

    def check_for_known_issue(self, error_message):
        """Check if error matches known pattern from export."""
        for pattern_name, pattern in self.patterns.items():
            if any(symptom in error_message for symptom in pattern["symptoms"]):
                return {
                    "pattern": pattern_name,
                    "solution": pattern["solution"],
                    "prevention": pattern["prevention"]
                }
        return None

# Usage
agent = ProblemPatternAgent()
result = agent.check_for_known_issue("Build passes: Evidence must be filled")
# Returns solution: "Keep evidence summary on same line..."
```

### 4. Time Estimation Learning

**Apply Historical Data:**

```python
class TimeEstimationAgent:
    """Agent that estimates time using historical data."""

    def __init__(self, knowledge_base_path='.issue-resolution-knowledge.json'):
        with open(knowledge_base_path) as f:
            self.kb = json.load(f)

    def estimate_time(self, issue_data):
        """Estimate time based on Issue #25 learnings."""
        # Get base estimate
        base_estimate = self._estimate_base(issue_data)

        # Apply multiplier from historical data
        multiplier = self.kb.get('avg_time_multiplier', 1.0)  # 0.875 from Issue #25

        # Adjust for complexity factors
        if issue_data.get('has_planning_doc'):
            multiplier *= 0.85  # Planning saves time

        if issue_data.get('test_first_approach'):
            multiplier *= 0.90  # Test-first prevents rework

        adjusted_estimate = base_estimate * multiplier

        return {
            "base": base_estimate,
            "adjusted": adjusted_estimate,
            "confidence": "high" if len(self.kb.get('completed_issues', [])) > 5 else "medium"
        }
```

### 5. Multi-Repo Coordination

**For Client-Server Projects:**

```python
class MultiRepoAgent:
    """Agent that coordinates changes across repositories."""

    def __init__(self, main_repo, client_repo):
        self.main_repo = main_repo
        self.client_repo = client_repo

    def plan_cross_repo_change(self, api_changes):
        """Plan coordinated changes (from Issue #25 approach)."""
        plan = {
            "main_repo_changes": [],
            "client_repo_changes": [],
            "coordination": {}
        }

        # Identify API contract changes
        if api_changes.get('new_endpoints'):
            plan["main_repo_changes"].append("Add API endpoints")
            plan["client_repo_changes"].append("Add client API calls")
            plan["coordination"]["merge_order"] = "main_first"

        if api_changes.get('breaking_changes'):
            plan["coordination"]["merge_order"] = "both_together"
            plan["coordination"]["requires_coordination"] = True

        return plan

    def validate_integration(self):
        """Validate both repos work together (from Issue #25 testing)."""
        # Start backend
        # Start frontend
        # Run integration tests
        pass
```

---

## Example: Workflow Agent

### Complete Implementation

```python
#!/usr/bin/env python3
"""
workflow_agent.py - AI agent trained on Issue #25 workflow

This agent automates a strict issue resolution workflow learned from
docs/chat/2026-01-18-step1-hybrid-workflow-creation.md

Usage:
    ./scripts/workflow_agent.py --issue 26
"""

import argparse
import json
import subprocess
import sys
from datetime import datetime
from pathlib import Path

class WorkflowAgent:
    """
    Agent that executes 6-phase workflow with learnings from Issue #25.

    Principles (from export):
    - No hallucinations (verify all facts)
    - Get approval for major decisions
    - Complete all phases (no shortcuts)
    - Create planning document in Phase 2
    - Use test-first approach
    - Mandatory self-review (Step 7)
    """

    def __init__(self, issue_num, export_path='docs/chat/2026-01-18-step1-hybrid-workflow-creation.md'):
        self.issue_num = issue_num
        self.export_path = Path(export_path)
        self.checkpoint_file = Path(f'.workflow-checkpoint-{issue_num}.json')
        self.state = self._load_checkpoint()

        # Load learnings from export
        self.principles = self._load_principles()
        self.commands = self._load_commands()
        self.problems = self._load_problem_patterns()

    def _load_checkpoint(self):
        """Load checkpoint if exists, else start fresh."""
        if self.checkpoint_file.exists():
            with open(self.checkpoint_file) as f:
                return json.load(f)
        return {
            "current_phase": 1,
            "completed_phases": [],
            "start_time": datetime.now().isoformat(),
            "checkpoints": {}
        }

    def _save_checkpoint(self):
        """Save current state to checkpoint file."""
        with open(self.checkpoint_file, 'w') as f:
            json.dump(self.state, f, indent=2)
        print(f"💾 Checkpoint saved: {self.checkpoint_file}")

    def _load_principles(self):
        """Extract key principles from export."""
        # Would parse export file for principles section
        return [
            "No hallucinations - verify all facts",
            "Get approval for major decisions",
            "Complete all 6 phases",
            "Create planning document in Phase 2",
            "Use test-first approach",
            "Mandatory self-review"
        ]

    def _load_commands(self):
        """Extract reusable command sequences from export."""
        # Would parse Commands Reference section
        return {
            "phase1": ["gh issue view {issue_num}", "git grep pattern"],
            "phase3": ["npm run build", "npx vitest run"],
            "phase5": ["gh pr create --fill", "./scripts/prmerge"]
        }

    def _load_problem_patterns(self):
        """Extract known problems and solutions from export."""
        # Would parse Problem Resolution section
        return {
            "ci_failure": "Check evidence format - must be inline",
            "removed_functionality": "Get user approval before removing features"
        }

    def execute(self):
        """Execute workflow starting from current phase."""
        print(f"\n{'='*60}")
        print(f"🤖 Workflow Agent - Issue #{self.issue_num}")
        print(f"📚 Trained on: {self.export_path.name}")
        print(f"{'='*60}\n")

        # Display principles
        print("📋 Key Principles:")
        for i, principle in enumerate(self.principles, 1):
            print(f"   {i}. {principle}")
        print()

        # Execute phases
        phases = [
            self.phase1_context,
            self.phase2_planning,
            self.phase3_implementation,
            self.phase4_testing,
            self.phase5_review,
            self.phase6_merge
        ]

        for phase_num, phase_func in enumerate(phases, 1):
            if phase_num < self.state["current_phase"]:
                print(f"✅ Phase {phase_num} already completed (checkpoint)")
                continue

            print(f"\n{'='*60}")
            print(f"Phase {phase_num}: {phase_func.__name__.replace('phase', '').replace('_', ' ').title()}")
            print(f"{'='*60}\n")

            try:
                phase_func()
                self.state["completed_phases"].append(phase_num)
                self.state["current_phase"] = phase_num + 1
                self._save_checkpoint()
            except Exception as e:
                print(f"❌ Phase {phase_num} failed: {e}")
                self._save_checkpoint()
                sys.exit(1)

        # Cleanup checkpoint
        self.checkpoint_file.unlink()
        print(f"\n✅ All phases complete! Issue #{self.issue_num} resolved.")

    def phase1_context(self):
        """Phase 1: Context & Exploration (from export Phase 1)."""
        print("📖 Reading issue details...")
        result = subprocess.run(
            ['gh', 'issue', 'view', str(self.issue_num), '--json', 'title,body,labels'],
            capture_output=True, text=True
        )
        issue_data = json.loads(result.stdout)
        print(f"   Title: {issue_data['title']}")
        print(f"   Labels: {', '.join([l['name'] for l in issue_data['labels']])}")

        print("\n🔍 Gathering codebase context...")
        print("   (Would use semantic_search, grep_search, read_file here)")

        self.state["checkpoints"]["phase1"] = {
            "completed": True,
            "issue_title": issue_data['title']
        }

    def phase2_planning(self):
        """Phase 2: Planning (CRITICAL - learned from Issue #25)."""
        print("📝 Creating planning document...")
        print("   Lesson from Issue #25: Planning saves 1-2 hours implementation time")

        planning_doc = f"docs/issues/issue-{self.issue_num}-plan.md"
        print(f"   Document: {planning_doc}")

        print("\n⏱️  Estimating time...")
        # Use avg_time_multiplier from knowledge base (0.875 from Issue #25)
        with open('.issue-resolution-knowledge.json') as f:
            kb = json.load(f)
        multiplier = kb.get('avg_time_multiplier', 1.0)
        base_estimate = 4.0  # hours
        adjusted = base_estimate * multiplier
        print(f"   Base: {base_estimate}h, Adjusted: {adjusted:.1f}h (multiplier: {multiplier})")

        self.state["checkpoints"]["phase2"] = {
            "completed": True,
            "planning_doc": planning_doc,
            "estimate": adjusted
        }

    def phase3_implementation(self):
        """Phase 3: Implementation (test-first from export)."""
        print("🔨 Implementing changes...")
        print("   Using test-first approach (learned from Issue #25)")
        print("   1. Write tests first")
        print("   2. Implement features")
        print("   3. Validate tests pass")

        self.state["checkpoints"]["phase3"] = {"completed": True}

    def phase4_testing(self):
        """Phase 4: Validation (comprehensive from export)."""
        print("🧪 Running validation...")

        # Build check
        print("   Building...")
        subprocess.run(['npm', 'run', 'build'], cwd='../AI-Agent-Framework-Client')

        # Test check
        print("   Running tests...")
        subprocess.run(['npx', 'vitest', 'run'], cwd='../AI-Agent-Framework-Client')

        self.state["checkpoints"]["phase4"] = {"completed": True}

    def phase5_review(self):
        """Phase 5: Review (mandatory self-review from export)."""
        print("👀 Self-review (MANDATORY - learned from Issue #25)...")
        print("   Check:")
        print("   • No functionality removed without approval")
        print("   • Layout makes sense")
        print("   • All acceptance criteria met")

        approval = input("\n   Self-review complete? (yes/no): ")
        if approval.lower() != 'yes':
            raise Exception("Self-review not approved")

        self.state["checkpoints"]["phase5"] = {"completed": True}

    def phase6_merge(self):
        """Phase 6: PR & Merge (automated with prmerge from export)."""
        print("🚀 Creating PR and merging...")

        # Create PR
        print("   Creating PR...")
        subprocess.run(['gh', 'pr', 'create', '--fill'])

        # Use enhanced prmerge (with validation from Issue #25)
        print("   Running prmerge (with template validation)...")
        subprocess.run(['./scripts/prmerge'])

        self.state["checkpoints"]["phase6"] = {"completed": True}

def main():
    parser = argparse.ArgumentParser(description='Workflow agent trained on Issue #25')
    parser.add_argument('--issue', type=int, required=True, help='Issue number')
    parser.add_argument('--resume', action='store_true', help='Resume from checkpoint')
    args = parser.parse_args()

    agent = WorkflowAgent(args.issue)
    agent.execute()

if __name__ == '__main__':
    main()
```

### Running the Agent

```bash
# Make executable
chmod +x scripts/workflow_agent.py

# Run for Issue #26
./scripts/workflow_agent.py --issue 26

# If interrupted, resume from checkpoint
./scripts/workflow_agent.py --issue 26 --resume
```

---

## Summary

**Key Takeaways:**

1. **Chat exports are complete knowledge bases** - They capture not just what was done, but why and how
2. **Restoration is flexible** - Use full context, selective sections, or structured extraction
3. **Agents learn from experience** - Problem patterns, time estimates, command sequences all preserved
4. **Principles before code** - Extract and codify principles first, then implement agent logic
5. **Validation is critical** - Agents should verify everything, just like the original workflow

**Next Steps:**

1. Review the example export [2026-01-18-step1-hybrid-workflow-creation.md](../chat/2026-01-18-step1-hybrid-workflow-creation.md)
2. Extract principles relevant to your use case
3. Start with simple command automation
4. Build up to full workflow agents
5. Continuously refine based on new learnings

**Resources:**

- [Example Export](../chat/2026-01-18-step1-hybrid-workflow-creation.md)
- [Workflow Documentation](../WORK-ISSUE-WORKFLOW.md)
- [Next Issue Command](../NEXT-ISSUE-COMMAND.md)
- [prmerge Enhancements](../prmerge-enhancements-issue25.md)
