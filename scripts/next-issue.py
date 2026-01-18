#!/usr/bin/env python3
"""
Next Issue Selector - Intelligent issue selection with learning

This script analyzes the current state of Step 1 implementation and selects
the next issue to work on based on:
- Dependency resolution (blockers must be merged)
- Priority and phase
- Historical completion data
- Learned patterns from previous issues

Usage:
    ./scripts/next-issue.py [--verbose] [--dry-run]
"""

import json
import re
import subprocess
import sys
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Tuple

# Repository root
REPO_ROOT = Path(__file__).parent.parent
TRACKING_FILE = REPO_ROOT / "STEP-1-IMPLEMENTATION-TRACKING.md"
KNOWLEDGE_FILE = REPO_ROOT / ".issue-resolution-knowledge.json"
STATUS_FILE = REPO_ROOT / "STEP-1-STATUS.md"


class IssueKnowledge:
    """Manages learning from past issue resolutions"""
    
    def __init__(self, knowledge_file: Path):
        self.knowledge_file = knowledge_file
        self.data = self._load_knowledge()
    
    def _load_knowledge(self) -> Dict:
        """Load existing knowledge or create new"""
        if self.knowledge_file.exists():
            with open(self.knowledge_file, 'r') as f:
                return json.load(f)
        return {
            "version": "1.0",
            "last_updated": None,
            "completed_issues": [],
            "patterns": {
                "avg_time_multiplier": 1.0,  # Actual vs estimated
                "common_blockers": [],
                "success_factors": [],
                "risk_factors": []
            },
            "recommendations": {}
        }
    
    def save_knowledge(self):
        """Save knowledge to file"""
        self.data["last_updated"] = datetime.now().isoformat()
        with open(self.knowledge_file, 'w') as f:
            json.dump(self.data, f, indent=2)
    
    def record_completion(self, issue_number: int, estimated_hours: float, 
                         actual_hours: float, notes: str):
        """Record a completed issue"""
        completion = {
            "issue_number": issue_number,
            "estimated_hours": estimated_hours,
            "actual_hours": actual_hours,
            "multiplier": actual_hours / estimated_hours if estimated_hours > 0 else 1.0,
            "completed_at": datetime.now().isoformat(),
            "notes": notes
        }
        self.data["completed_issues"].append(completion)
        
        # Update average multiplier
        multipliers = [c["multiplier"] for c in self.data["completed_issues"]]
        self.data["patterns"]["avg_time_multiplier"] = sum(multipliers) / len(multipliers)
        
        self.save_knowledge()
    
    def get_adjusted_estimate(self, estimated_hours: float) -> float:
        """Get time estimate adjusted by historical data"""
        multiplier = self.data["patterns"]["avg_time_multiplier"]
        return estimated_hours * multiplier
    
    def add_pattern(self, category: str, pattern: str):
        """Add a learned pattern"""
        if category in self.data["patterns"]:
            if pattern not in self.data["patterns"][category]:
                self.data["patterns"][category].append(pattern)
                self.save_knowledge()


class IssueSelector:
    """Selects the next issue to work on"""
    
    def __init__(self, tracking_file: Path, knowledge: IssueKnowledge):
        self.tracking_file = tracking_file
        self.knowledge = knowledge
        self.issues = self._parse_tracking_file()
    
    def _parse_tracking_file(self) -> List[Dict]:
        """Parse tracking file to extract issue data"""
        issues = []
        content = self.tracking_file.read_text()
        
        # Pattern to match issue entries
        pattern = r'\*\*Issue #(\d+):\*\*.*?\n.*?Status: (.*?)\n.*?Blockers: (.*?)\n.*?Estimated: ([\d.]+)(?:-[\d.]+)? hours'
        
        for match in re.finditer(pattern, content, re.DOTALL):
            issue_num = int(match.group(1))
            status = match.group(2).strip()
            blockers_text = match.group(3).strip()
            estimated_hours = float(match.group(4))
            
            # Parse blockers
            blockers = []
            if blockers_text != "None":
                blockers = [int(b.strip('#')) for b in re.findall(r'#(\d+)', blockers_text)]
            
            # Extract phase from context
            phase = self._extract_phase(content, issue_num)
            
            # Extract priority
            priority = self._extract_priority(content, issue_num)
            
            issues.append({
                "number": issue_num,
                "status": status,
                "blockers": blockers,
                "estimated_hours": estimated_hours,
                "adjusted_hours": self.knowledge.get_adjusted_estimate(estimated_hours),
                "phase": phase,
                "priority": priority
            })
        
        return issues
    
    def _extract_phase(self, content: str, issue_num: int) -> str:
        """Extract phase for an issue"""
        phases = {
            (24, 29): "Phase 1: Infrastructure",
            (59, 59): "Phase 2: Chat Integration",
            (30, 36): "Phase 3: RAID Components",
            (37, 42): "Phase 4: Workflow Components",
            (43, 45): "Phase 5: Project Management",
            (46, 51): "Phase 6: UX & Polish",
            (52, 55): "Phase 7: Testing",
            (56, 58): "Phase 8: Documentation"
        }
        
        for (start, end), phase_name in phases.items():
            if start <= issue_num <= end:
                return phase_name
        return "Unknown"
    
    def _extract_priority(self, content: str, issue_num: int) -> str:
        """Extract priority for an issue"""
        # Critical issues
        if issue_num in [24, 59]:
            return "CRITICAL"
        # High priority infrastructure
        elif issue_num in [25, 26, 27, 28, 29]:
            return "High"
        # Medium priority features
        else:
            return "Medium"
    
    def _check_github_status(self, issue_num: int) -> Optional[str]:
        """Check if issue is merged via GitHub API"""
        try:
            # Check if there's a merged PR for this issue
            result = subprocess.run(
                ["gh", "pr", "list", "--repo", "blecx/AI-Agent-Framework-Client",
                 "--state", "merged", "--search", f"Issue #{issue_num}",
                 "--json", "number,title"],
                capture_output=True,
                text=True,
                timeout=5
            )
            
            if result.returncode == 0 and result.stdout.strip():
                data = json.loads(result.stdout)
                if data:
                    return "✅ Merged"
        except (subprocess.TimeoutExpired, FileNotFoundError, json.JSONDecodeError):
            pass
        
        return None
    
    def select_next_issue(self) -> Optional[Dict]:
        """Select the next issue to work on"""
        # Filter to not-started or in-progress issues
        available = [i for i in self.issues if i["status"] in ["Not Started", "In Progress"]]
        
        if not available:
            return None
        
        # Filter by blockers resolved
        ready = []
        for issue in available:
            blockers_resolved = True
            for blocker_num in issue["blockers"]:
                blocker = next((i for i in self.issues if i["number"] == blocker_num), None)
                if blocker:
                    # Check tracking file first
                    if blocker["status"] not in ["✅ Complete", "Complete"]:
                        # Double-check with GitHub
                        gh_status = self._check_github_status(blocker_num)
                        if gh_status != "✅ Merged":
                            blockers_resolved = False
                            break
            
            if blockers_resolved:
                ready.append(issue)
        
        if not ready:
            return None
        
        # Sort by: priority (CRITICAL first), then issue number (dependency order)
        priority_map = {"CRITICAL": 0, "High": 1, "Medium": 2, "Low": 3}
        ready.sort(key=lambda i: (priority_map.get(i["priority"], 99), i["number"]))
        
        return ready[0]
    
    def get_issue_context(self, issue_num: int) -> str:
        """Get full context for an issue from tracking file"""
        content = self.tracking_file.read_text()
        
        # Find the issue section
        pattern = rf'\*\*Issue #{issue_num}:\*\*.*?(?=\n\*\*Issue #|\n###|\Z)'
        match = re.search(pattern, content, re.DOTALL)
        
        if match:
            return match.group(0)
        return f"Issue #{issue_num} not found in tracking file"


def format_issue_recommendation(issue: Dict, context: str, knowledge: IssueKnowledge) -> str:
    """Format the recommendation output"""
    output = []
    output.append("=" * 80)
    output.append("NEXT ISSUE RECOMMENDATION")
    output.append("=" * 80)
    output.append("")
    output.append(f"🎯 Selected Issue: #{issue['number']}")
    output.append(f"📋 Phase: {issue['phase']}")
    output.append(f"⚡ Priority: {issue['priority']}")
    output.append(f"⏱️  Estimated Time: {issue['estimated_hours']:.1f} hours")
    output.append(f"📊 Adjusted Estimate: {issue['adjusted_hours']:.1f} hours "
                 f"(based on {len(knowledge.data['completed_issues'])} completed issues)")
    output.append("")
    
    if issue['blockers']:
        output.append(f"✅ Blockers Resolved: #{', #'.join(map(str, issue['blockers']))}")
        output.append("")
    
    output.append("📝 Issue Details:")
    output.append("-" * 80)
    output.append(context)
    output.append("-" * 80)
    output.append("")
    
    # Learning insights
    if knowledge.data["completed_issues"]:
        output.append("💡 Insights from Previous Issues:")
        avg_mult = knowledge.data["patterns"]["avg_time_multiplier"]
        output.append(f"   • Average time multiplier: {avg_mult:.2f}x")
        output.append(f"   • Completed issues: {len(knowledge.data['completed_issues'])}")
        
        if knowledge.data["patterns"]["success_factors"]:
            output.append("   • Success factors:")
            for factor in knowledge.data["patterns"]["success_factors"][-3:]:
                output.append(f"     - {factor}")
        output.append("")
    
    output.append("🚀 Next Steps:")
    output.append("   1. Read the full issue on GitHub:")
    output.append(f"      gh issue view {issue['number']} --repo blecx/AI-Agent-Framework-Client")
    output.append("")
    output.append("   2. Create feature branch:")
    output.append(f"      git checkout main && git pull origin main")
    output.append(f"      git checkout -b issue/{issue['number']}-<description>")
    output.append("")
    output.append("   3. Follow STEP-1-IMPLEMENTATION-WORKFLOW.md (10-step protocol)")
    output.append("      • Step 7 (Copilot review) is MANDATORY - never skip!")
    output.append("")
    output.append("=" * 80)
    
    return "\n".join(output)


def main():
    """Main entry point"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Select next issue to work on")
    parser.add_argument("--verbose", "-v", action="store_true", 
                       help="Show detailed information")
    parser.add_argument("--dry-run", action="store_true",
                       help="Show what would be selected without updating state")
    args = parser.parse_args()
    
    # Load knowledge
    knowledge = IssueKnowledge(KNOWLEDGE_FILE)
    
    # Create selector
    selector = IssueSelector(TRACKING_FILE, knowledge)
    
    # Select next issue
    next_issue = selector.select_next_issue()
    
    if not next_issue:
        print("❌ No issues available to work on.")
        print("\nPossible reasons:")
        print("   • All issues are complete")
        print("   • All remaining issues have unresolved blockers")
        print("\nCheck STEP-1-IMPLEMENTATION-TRACKING.md for details.")
        return 1
    
    # Get full context
    context = selector.get_issue_context(next_issue["number"])
    
    # Format and display recommendation
    recommendation = format_issue_recommendation(next_issue, context, knowledge)
    print(recommendation)
    
    # Save recommendation if not dry-run
    if not args.dry_run:
        knowledge.data["recommendations"]["last_selected"] = {
            "issue_number": next_issue["number"],
            "selected_at": datetime.now().isoformat(),
            "reason": f"Next in {next_issue['phase']}, all blockers resolved"
        }
        knowledge.save_knowledge()
    
    return 0


if __name__ == "__main__":
    sys.exit(main())
