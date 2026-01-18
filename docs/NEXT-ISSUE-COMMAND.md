# Next Issue Command - Documentation

## Overview

The `./next-issue` command intelligently selects the next Step 1 issue to work on with a **two-phase workflow**:

### Phase 1: Reconciliation (GitHub as Source of Truth)

- Checks GitHub for merged PRs and closes associated issues
- Verifies closed PRs have closed issues
- Updates local tracking documentation to match GitHub state
- Commits and syncs changes automatically
- Loops until everything is reconciled

### Phase 2: Selection

- Uses **sequential order from tracking file** (issues 24-58)
- Checks which blockers are resolved via GitHub API
- Selects the highest priority unblocked issue
- Adjusts time estimates based on historical learning

**Important:** GitHub is the single source of truth. Local tracking files are updated to match GitHub, never the other way around.

## Installation

The command is already installed in the repository root. No setup needed.

## Usage

### Basic Usage

```bash
# From repository root
./next-issue
```

This will:

1. **Reconcile** - Sync local docs with GitHub state
2. **Select** - Find next available issue
3. Display full issue details and next steps
4. Update the knowledge base with the selection

### Command Options

```bash
# Dry run (don't update knowledge base or commit changes)
./next-issue --dry-run

# Verbose output (show detailed GitHub API calls)
./next-issue --verbose

# Skip reconciliation (not recommended)
./next-issue --skip-reconcile

# Custom timeout (default: 180 seconds)
./next-issue --timeout 120
```

### Internal Timeout Handling

The script has **built-in timeout protection**:

- Default: 180 seconds for entire operation
- Configurable via `--timeout` flag
- Individual operations have sub-timeouts (10-15s)
- Graceful error handling on timeout
- No need for external `timeout` command

## Output Format

### Non-Verbose Mode (Default)

```
Phase 1: Reconciliation
🔄 Reconciling with GitHub...
✅ Everything in sync

Phase 2: Issue Selection
================================================================================
NEXT ISSUE RECOMMENDATION
================================================================================

🎯 Selected Issue: #25
📋 Title: Add project management routing
📋 Phase: Phase 1: Infrastructure
⚡ Priority: High
⏱️  Estimated Time: 4.0 hours
📊 Adjusted Estimate: 4.0 hours (based on 0 completed issues)
✅ GitHub State: OPEN (verified via GitHub API)

✅ No Blockers

📝 Issue Details:
[Full issue details from tracking file]

🚀 Next Steps:
   1. Read the full issue on GitHub
   2. Create feature branch
   3. Follow 10-step protocol
================================================================================
```

### Verbose Mode

Shows detailed GitHub API calls, caching hits, and reconciliation steps for debugging.

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

### Step 1: Reconciliation Phase

1. **Check Merged PRs**
   - Query GitHub for recently merged PRs (last 20)
   - Extract issue numbers from PR titles
   - Close issues if PRs are merged but issues still open

2. **Update Tracking File**
   - Query GitHub for all Step 1 issues (24-58)
   - Compare GitHub state with local tracking file
   - Update local file to match GitHub (source of truth)
   - Don't overwrite "In Progress" or "Complete" statuses

3. **Commit and Sync**
   - Commit tracking file changes to git
   - Push to remote repository
   - Loop until no changes detected

### Step 2: Issue Selection

1. **Parse Issues from GitHub**
   - Query issues 24-58 individually (no label assumptions)
   - Sequential order defined by tracking file
   - Uses caching to avoid repeated API calls

2. **Parse Tracking Metadata**
   - Extract estimated hours, blockers, phase from tracking file
   - Use fast, optimized regex patterns
   - Individual section parsing (not complex multi-line regex)

3. **Filter Available Issues**
   - Status must be "Open" on GitHub
   - All blockers must be resolved (verified via GitHub)
   - Blockers checked using merged PR verification

4. **Priority Sorting**
   - High/CRITICAL priority first
   - Then sequential order (24, 25, 26...)
   - Respects dependency chain

5. **Context Enrichment**
   - Extract full issue section from tracking file
   - Add historical insights from knowledge base
   - Calculate adjusted time estimates

6. **Display Recommendation**
   - Show selected issue with full context
   - Provide GitHub-verified next steps
   - Include learning insights

## Key Features

### 1. Reconciliation-First Approach

The command always reconciles before selection:

- **Why?** Ensures local docs match GitHub reality
- **How?** Queries GitHub for PR/issue states
- **Result:** No stale data, no manual sync needed

### 2. GitHub as Source of Truth

Never assumes local files are correct:

- Issue state comes from GitHub API
- Blocker resolution verified via merged PRs
- Tracking file updated to match GitHub

### 3. No Label Assumptions

Uses **sequential order** from tracking file (24-58):

- No reliance on GitHub labels
- Follows documented plan order exactly
- Resilient to label changes

### 4. Performance Optimizations

- **API caching**: Avoids repeated queries
- **Optimized regex**: Fast tracking file parsing
- **Progress indicators**: Shows status during long operations
- **Individual queries**: More reliable than bulk queries

### 5. Production-Ready Error Handling

- Internal timeout protection (default 180s)
- Graceful degradation on network errors
- Clear error messages
- Proper exit codes (124=timeout, 130=interrupt)

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
