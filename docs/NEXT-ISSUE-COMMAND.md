# Next Issue Command - Documentation

## Overview

The `/next-issue` command intelligently selects the next Step 1 issue to work on based on:

- **Dependency resolution** - Blockers must be merged before starting
- **Priority** - CRITICAL issues take precedence
- **Phase sequencing** - Follows the 8-phase implementation plan
- **Historical learning** - Adjusts time estimates based on past completions

## Installation

The command is already installed in the repository root. No setup needed.

## Usage

### Basic Usage

```bash
# From repository root
./next-issue
```

This will:

1. Analyze all 36 Step 1 issues
2. Check which blockers are resolved
3. Select the highest priority issue that's ready to start
4. Display full issue details and next steps
5. Update the knowledge base with the selection

### Advanced Options

```bash
# Dry run (don't update knowledge base)
./next-issue --dry-run

# Verbose output (show detailed analysis)
./next-issue --verbose
```

## Output Format

The command provides a comprehensive recommendation:

```
================================================================================
NEXT ISSUE RECOMMENDATION
================================================================================

🎯 Selected Issue: #24
📋 Phase: Phase 1: Infrastructure
⚡ Priority: CRITICAL
⏱️  Estimated Time: 8.0 hours
📊 Adjusted Estimate: 8.0 hours (based on 0 completed issues)

📝 Issue Details:
--------------------------------------------------------------------------------
**Issue #24:** API Service Layer Infrastructure
Status: Not Started
...
--------------------------------------------------------------------------------

💡 Insights from Previous Issues:
   • Average time multiplier: 1.15x
   • Completed issues: 5
   • Success factors:
     - Clear acceptance criteria defined upfront
     - Thorough self-review before user review (Step 7)
     - Comprehensive test coverage from start

🚀 Next Steps:
   1. Read the full issue on GitHub:
      gh issue view 24 --repo blecx/AI-Agent-Framework-Client

   2. Create feature branch:
      git checkout main && git pull origin main
      git checkout -b issue/24-<description>

   3. Follow STEP-1-IMPLEMENTATION-WORKFLOW.md (10-step protocol)
      • Step 7 (Copilot review) is MANDATORY - never skip!

================================================================================
```

## Recording Completions

After completing an issue, record the actual time spent to improve future estimates:

```bash
./scripts/record-completion.py <issue_number> <actual_hours> [notes]
```

Example:

```bash
./scripts/record-completion.py 24 7.5 "Tests took longer than expected due to mock adapter issues"
```

This will:

1. Record actual vs estimated time
2. Calculate time variance
3. Update the average time multiplier
4. Provide insights on why variance occurred
5. Improve future time estimates

## Learning System

The command uses a JSON knowledge base (`.issue-resolution-knowledge.json`) that tracks:

### Completed Issues

```json
{
  "issue_number": 24,
  "estimated_hours": 8.0,
  "actual_hours": 7.5,
  "multiplier": 0.94,
  "completed_at": "2026-01-18T15:30:00",
  "notes": "Tests took longer than expected"
}
```

### Patterns

```json
{
  "avg_time_multiplier": 1.15,
  "common_blockers": ["API integration issues", "Test setup complexity"],
  "success_factors": [
    "Clear acceptance criteria defined upfront",
    "Thorough self-review before user review (Step 7)"
  ],
  "risk_factors": [
    "Skipping Copilot self-review (Step 7)",
    "Starting work before blockers merged"
  ]
}
```

### Time Estimate Adjustment

The command automatically adjusts estimates based on historical data:

- **Initial estimate**: 8.0 hours (from tracking plan)
- **Historical multiplier**: 1.15x (average actual/estimated)
- **Adjusted estimate**: 9.2 hours (8.0 × 1.15)

This helps set realistic expectations as the project progresses.

## Selection Algorithm

1. **Parse Tracking File**
   - Extract all 36 issues with metadata
   - Identify status, blockers, estimates, phase, priority

2. **Filter Available Issues**
   - Status must be "Not Started" or "In Progress"
   - All blockers must have status "✅ Complete"
   - Double-check merged status via GitHub API

3. **Priority Sorting**
   - CRITICAL issues first (e.g., #24, #59)
   - Then High priority (infrastructure)
   - Then Medium priority (features)
   - Within same priority, use issue number (dependency order)

4. **Context Enrichment**
   - Extract full issue details from tracking file
   - Add historical insights from knowledge base
   - Calculate adjusted time estimates

5. **Display Recommendation**
   - Show selected issue with full context
   - Provide next steps
   - Include learning insights

## Integration with Workflow

The command is designed to work with the 10-step protocol:

```
Step 1: Pre-work Validation
  ↓
./next-issue  ← Use command here to select next issue
  ↓
Step 2: Create Feature Branch
  ↓
Step 3: Implementation
  ↓
...
  ↓
Step 10: Post-merge Validation
  ↓
./scripts/record-completion.py  ← Record completion here
  ↓
./next-issue  ← Select next issue
```

## Knowledge Base Management

### View Knowledge Base

```bash
cat .issue-resolution-knowledge.json | jq
```

### Backup Knowledge Base

```bash
cp .issue-resolution-knowledge.json .issue-resolution-knowledge.backup.json
```

### Reset Knowledge Base

```bash
# Reset to initial state
cat > .issue-resolution-knowledge.json << 'EOF'
{
  "version": "1.0",
  "last_updated": null,
  "completed_issues": [],
  "patterns": {
    "avg_time_multiplier": 1.0,
    "common_blockers": [],
    "success_factors": [],
    "risk_factors": []
  },
  "recommendations": {}
}
EOF
```

## Troubleshooting

### "No issues available to work on"

**Possible causes:**

- All issues are complete (check tracking plan)
- All remaining issues have unresolved blockers
- GitHub API rate limit reached

**Solutions:**

1. Check `STEP-1-IMPLEMENTATION-TRACKING.md` for status
2. Verify blockers are actually merged on GitHub
3. Wait for GitHub API rate limit to reset

### "Issue not found in tracking file"

**Cause:** Issue number doesn't exist in `STEP-1-IMPLEMENTATION-TRACKING.md`

**Solution:** Check issue number is between 24-58 (excluding 59)

### Import errors when running scripts

**Cause:** Python path issues

**Solution:** Run from repository root:

```bash
cd /home/sw/work/AI-Agent-Framework
./next-issue
```

## Best Practices

1. **Run after each merge** - Always use `./next-issue` after completing an issue
2. **Record completions** - Always use `record-completion.py` to track actual time
3. **Review insights** - Pay attention to historical patterns and success factors
4. **Follow recommendations** - The adjusted estimates are based on real data
5. **Update tracking plan** - Keep `STEP-1-IMPLEMENTATION-TRACKING.md` current

## Future Enhancements

Potential improvements to the learning system:

- [ ] Predict likely blockers based on past issues
- [ ] Suggest similar completed issues for reference
- [ ] Track common error patterns and solutions
- [ ] Generate risk assessment for each issue
- [ ] Recommend optimal time of day based on completion patterns
- [ ] Integration with GitHub Issues API for automatic status sync
- [ ] Slack/Discord notifications for next issue recommendations
- [ ] Dashboard showing completion velocity and trends

## Contributing

To improve the selection algorithm or learning system:

1. Modify `scripts/next-issue.py` or `scripts/record-completion.py`
2. Test changes with `--dry-run` flag
3. Update this documentation
4. Commit changes with descriptive message

## Support

For issues or questions:

- Check `STEP-1-IMPLEMENTATION-WORKFLOW.md` for workflow details
- Review `STEP-1-IMPLEMENTATION-TRACKING.md` for current status
- Examine `.issue-resolution-knowledge.json` for historical data

---

**Remember:** The `/next-issue` command is a tool to help, not replace, your judgment. Always review the recommendation and adjust based on current context and priorities.
