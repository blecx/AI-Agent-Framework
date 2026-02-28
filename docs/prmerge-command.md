# PR Merge Workflow Command

## Overview

`prmerge` is a comprehensive command-line tool that automates the entire PR merge workflow, from validation to issue closure and learning system recording.

## Location

```
scripts/prmerge
```

## Usage

```bash
prmerge <issue_number> [<actual_hours>]
```

### Arguments

- `issue_number` (required): The issue number to merge and close (e.g., 24, 25, 30)
- `actual_hours` (optional): Actual hours spent on the issue for learning system

### Examples

```bash
# Basic usage - merge PR and close issue
prmerge 24

# With completion time tracking
prmerge 24 7.5

# From any directory (uses absolute paths)
cd /home/sw/work/AI-Agent-Framework
./scripts/prmerge 25 6.0
```

## Workflow Steps

The `prmerge` command automates these steps:

### 1. **Validate PR and CI Status** ✨ ENHANCED

- Automatically finds PR associated with issue number
- Verifies PR state (open, merged, closed)
- Watches required CI checks until completion (no blind snapshot merge)
- Enforces that all required checks are `PASS` before merge
- Uses timeout-based watchdog protection for long-running checks
- **Policy guard:** Blocks PRs that modify `.github/workflows/*.yml` by default
  - This avoids standard-loop merge failures when elevated workflow token scope is unavailable
  - Use a dedicated workflow-change merge path, or explicit override for exceptions:
    - `PRMERGE_ALLOW_WORKFLOW_FILES=1 ./scripts/prmerge <issue_number>`
- **Domain-specific validation guidance:** prints targeted checks based on changed files
  - Backend scope: focused `pytest` in touched domain(s)
  - Frontend scope: `npm run lint` / `npm run build` or focused UI tests
  - Docs-only scope: lightweight policy/documentation checks
- **NEW:** Validates PR description follows template requirements
  - Checks for required sections (Summary, Acceptance Criteria, Validation, etc.)
  - Uses CI-aligned section detection for backend/client contracts with summary heading compatibility (`#` or `##`)
  - Verifies "Fixes: #N" line exists (where N is issue number)
  - **Cross-repo support:** Accepts `Fixes: #N` for same-repo or `Fixes: owner/repo#N` for cross-repo
  - Ensures acceptance criteria checkboxes are checked
  - Validates automated checks evidence is filled (inline format)
  - Reports missing sections or warnings before merge
- Fails fast if required checks fail, timeout, or template validation fails
- Displays PR details (number, title, branch, URL)

**Strict CI gate behavior:**

- Uses `gh pr checks --required --watch --fail-fast`
- Default timeout: `1200s` (20m)
- Default watch interval: `8s`
- Optional watchdog cancellation for stale in-progress branch runs older than `25m`
- Prints CI health summary (`total/pass/fail/pending/skipped/elapsed`) before merge decision

**⚠️ CI Re-run Behavior:**

- **Workflow reruns use cached PR payload** - updating PR description won't affect existing workflow runs
- To trigger fresh CI with updated PR description:
  1. Push a new commit (e.g., empty commit: `git commit --allow-empty -m "chore: trigger CI"`), OR
  2. Close and reopen the PR to force a fresh `pull_request` event
- Avoid using `gh run rerun` if you've updated the PR description - it will validate the OLD description

### 2. **Review PR**

- Opens PR in browser for visual review
- Prompts user to confirm review completion
- Validates acceptance criteria are met
- Ensures code quality standards
- Checks documentation completeness

### 3. **Handle Branch Protection**

- Detects branch protection blocks
- Offers three resolution strategies:
  - **Option A:** Manual approval via GitHub UI
  - **Option B:** Temporarily disable branch protection
  - **Option C:** Manual git merge (bypass PR)
- Guides user through chosen option

### 4. **Merge PR**

- Attempts squash merge with branch deletion
- Falls back to `--admin` flag if needed
- Captures merge commit SHA
- Verifies merge success
- Handles merge conflicts gracefully

### 5. **Generate Issue Closing Message** ✨ ENHANCED

- **Detects issue type** automatically (infrastructure/feature/bugfix/docs)
- **Captures enhanced metrics**:
  - PR complexity score (low/medium/high)
  - Commit count
  - Test coverage ratio
  - CI iteration count
- **Selects appropriate template** based on issue type
- Extracts PR details (files, additions, deletions)
- Parses acceptance criteria from PR body
- Creates comprehensive closing message with:
  - Issue-specific formatting
  - Merge commit reference
  - Implementation summary
  - Acceptance criteria checklist
  - Enhanced metrics and statistics
  - CI validation results
  - Next steps guidance

### 6. **Close Issue**

- Verifies issue exists and is open
- Posts comprehensive closing message with appropriate template
- Links to PR and commit
- Marks issue as completed

### 7. **Record Completion (Optional)** ✨ ENHANCED

- Records actual hours in learning system
- **Captures optional learning data**:
  - Unexpected challenges encountered
  - Main time sinks
  - Key learnings and insights
- **Stores enhanced metrics**:
  - PR complexity, commits, test ratio
  - CI iterations, workflow efficiency
  - All data in JSON format
- Updates `.issue-resolution-knowledge.json`
- Tracks estimation accuracy

### 8. **Verification and Summary** ✨ NEW

- **Verifies PR merge status** - Confirms PR is in MERGED state
- **Verifies issue closure** - Confirms issue is CLOSED with timestamp
- **Verifies closing message** - Checks comprehensive message was posted
- **Displays lessons learned** - Shows key insights from similar issues (e.g., Issue #25 pattern)
- **Provides summary** with:
  - Issue type and PR details
  - Merge commit SHA
  - Files changed statistics
  - Complexity and CI iteration metrics
  - Completion recording status
- **Suggests next steps** - Offers to run `./next-issue` automatically

## Lessons Learned (Built-in Knowledge)

The command includes lessons learned from Issue #25 (routing infrastructure):

### PR Template Lessons

- **Evidence format matters**: Use inline summaries, not code blocks
- **CI validation is strict**: All checkboxes must be checked, no placeholders allowed
- **Fix PR description BEFORE pushing**: Avoids multiple CI re-runs

### Process Improvements

- Always create `docs/issues/issue-N-context.md` planning document in Phase 2
- Never remove existing features without explicit user confirmation
- Verify everything with actual command output (never assume success)
- Build frequently during development, not just at the end
- Self-review (Step 7) is MANDATORY - catches critical mistakes

### What Works Well

- Detailed planning documents save 1-2 hours implementation time
- Test-first approach catches issues early
- Self-review catches critical mistakes before user review
- Copilot review improves UX beyond functional correctness
- Phase commits enable clear progress tracking and easy rollback
- Builds patterns for future estimates

📖 **[Read Full Enhancement Story →](prmerge-enhancements-issue25.md)** - Detailed analysis of Issue #25 learnings and how they were built into the command

### 8. **Next Issue Suggestion**

- Offers to run `./next-issue` automatically
- Selects next issue based on:
  - Unblocked dependencies
  - Priority and phase
  - Historical patterns
  - Learning system recommendations

## Features

### 🔍 **Smart PR Detection**

- Searches by issue number in PR title
- Falls back to manual PR number input if needed
- Handles multiple search patterns

### 🎯 **Issue Type Templates** ✨ NEW

- Automatically detects issue type (infrastructure, feature, bugfix, docs)
- Uses specialized closing message templates
- Improves message clarity and relevance
- Detection based on title keywords, file patterns, and content analysis
- Four template types:
  - **Infrastructure**: Setup, configuration, foundational code
  - **Feature**: New functionality, components, integrations
  - **Bugfix**: Bug fixes, hotfixes, patches
  - **Documentation**: Guides, API docs, READMEs

### 📊 **Enhanced Metrics Capture** ✨ NEW

- **PR Complexity**: Automatic classification (low/medium/high based on file count)
- **Commit Tracking**: Records commit count for analysis
- **Test Coverage**: Calculates test file ratio
- **CI Efficiency**: Tracks CI iteration count
- **Learning Prompts**: Optional capture of challenges, time sinks, and insights
- **Metrics Storage**: All data saved to learning system for future estimate improvements
- **Automated Analysis**: No manual calculation needed

### ✅ **CI Validation**

- Checks all status checks
- Identifies failing checks
- Prevents merge if CI fails
- Clear error messages with fix guidance

### 🔒 **Branch Protection Handling**

- Detects protection blocks
- Offers multiple resolution strategies
- Guides manual steps when needed
- Supports admin override

### 📝 **Comprehensive Documentation**

- Generates detailed closing messages
- Extracts data from PR body
- Links commits, PRs, and issues
- Records completion for learning

### 🎯 **Error Recovery**

- Graceful failure handling
- Clear error messages
- Suggests corrective actions
- Preserves state on failure

### 🚀 **Learning Integration**

- Records completion times
- Tracks estimation accuracy
- Builds knowledge base
- Improves future estimates

## Output Example

```
=========================================
Step 1: Validate PR and CI Status
=========================================

ℹ Finding PR for Issue #24...
✅ Found PR #60

ℹ Checking PR status...

PR Details:
  Number: #60
  Title: [Issue #24] API Service Layer Infrastructure
  State: OPEN
  Branch: issue/24-api-service-layer
  URL: https://github.com/blecx/AI-Agent-Framework-Client/pull/60

ℹ Validating required checks for PR #60
ℹ Waiting for required checks to complete (timeout=1200s, watch-interval=8s)
✅ All required CI checks are complete and passing

=========================================
Step 2: Review PR
=========================================

ℹ Opening PR in browser for review...

Please review the PR:
  - Check code quality and architecture
  - Verify tests are comprehensive
  - Ensure documentation is complete
  - Validate acceptance criteria are met

Has the PR been reviewed and approved? (y/N): y

=========================================
Step 3: Merge PR
=========================================

ℹ Attempting to merge PR #60...
✅ PR merged successfully!
✅ Merge commit: 532e5a6

=========================================
Step 4: Generate Issue Closing Message
=========================================

ℹ Analyzing PR changes...
ℹ Capturing PR metrics...
ℹ Metrics: complexity=high,commits=7,test_ratio=0.45,ci_iterations=4
ℹ Detecting issue type...
✅ Detected type: infrastructure
✅ Generated infrastructure closing message with enhanced metrics

=========================================
Step 5: Close Issue
=========================================

ℹ Closing Issue #24...
✅ Issue #24 closed with infrastructure template

=========================================
Step 6: Record Completion
=========================================

ℹ Recording completion time: 7.5 hours

ℹ Optional: Provide learning data for future estimates (press Enter to skip)
Unexpected challenges encountered (optional): Vitest config path resolution
Main time sink if any (optional): CI debugging (2 hours)
Key learning/insight (optional): Always use absolute paths in monorepo

✅ Completion recorded in learning system with enhanced metrics
=========================================

ℹ Recording completion time: 7.5 hours
✅ Completion recorded in learning system

=========================================
Step 7: Summary and Next Steps
=========================================

✅ PR Merge Workflow Complete!

Summary:
  - Issue Type: infrastructure
  - PR #60 merged: https://github.com/blecx/AI-Agent-Framework-Client/pull/60
  - Merge commit: 532e5a6
  - Issue #24 closed with infrastructure template
  - Files changed: 17 (+1701/-42)
  - Complexity: high
  - CI iterations: 4
  - Completion recorded: 7.5 hours with enhanced metrics

Next steps:
  1. Run './next-issue' to select next issue
  2. Review unblocked dependencies
  3. Continue Step 1 implementation

Run './next-issue' now? (Y/n):
```

## Error Handling

### CI Failures

```
❌ CI checks are failing! Cannot merge.

Failed checks:
  - Build: FAILURE
  - Tests: FAILURE

⚠️  Please fix CI failures before merging
⚠️  PR URL: https://github.com/blecx/AI-Agent-Framework-Client/pull/60
```

### PR Not Found

```
❌ No PR found for Issue #24
ℹ Attempting alternate search pattern...
If no PR exists for the issue, `prmerge` will now exit cleanly without prompting ("Nothing to merge").

If you need to merge a PR with a non-standard title (so it isn't discoverable by issue number), you can override discovery:

- Set `PRMERGE_PR_NUMBER=<pr>` and re-run `./scripts/prmerge <issue>`
```

### Branch Protection Block

```
⚠️  PR is blocked by branch protection

Options to unblock:
  A) Approve via GitHub UI: https://github.com/...
  B) Temporarily disable branch protection
  C) Manual git merge (bypass GitHub PR)

Which option? (A/B/C):
```

### Merge Failure

```
❌ Merge failed even with admin flag
❌ Please merge manually at: https://github.com/...
```

## Prerequisites

### Required Tools

- **git** - Version control
- **gh** (GitHub CLI) - PR and issue management
- **jq** - JSON processing
- **bash** 4.0+ - Script execution

### Authentication

Ensure GitHub CLI is authenticated:

```bash
gh auth login
gh auth status
```

### Repository Structure

Expected structure:

```
AI-Agent-Framework/
├── scripts/
│   ├── prmerge                    # This script
│   ├── record-completion.py       # Completion tracking
│   └── next-issue.py             # Issue selection
├── _external/
│   └── AI-Agent-Framework-Client/ # Client repository
└── .issue-resolution-knowledge.json  # Learning data
```

## Integration with Other Scripts

### `record-completion.py`

Records completion data for learning:

```bash
./scripts/record-completion.py <issue> <hours> "<notes>"
```

Called automatically by `prmerge` if hours provided.

### `next-issue.py`

Selects next issue based on dependencies and learning:

```bash
./scripts/next-issue.py [--verbose] [--dry-run]
```

Offered automatically after `prmerge` completes.

## Configuration

### Environment Variables

- `GITHUB_TOKEN` - GitHub API authentication (optional if gh authenticated)
- `VISUAL` / `EDITOR` - Editor for manual edits (optional)
- `PRMERGE_CI_WAIT_TIMEOUT_SECONDS` - Timeout for required check watch (default: `1200`)
- `PRMERGE_CI_WATCH_INTERVAL_SECONDS` - Check watch refresh interval (default: `8`)
- `PRMERGE_LONGRUNNER_MAX_MINUTES` - Age threshold for stale in-progress runs (default: `25`)
- `PRMERGE_CANCEL_LONGRUNNERS` - Cancel stale runs after timeout (`1` enabled, `0` disabled)
- `PRMERGE_ALLOW_NO_REQUIRED_CHECKS` - Allow merge when no required checks exist (`0` default, `1` override)

### Color Output

Disable colors if terminal doesn't support:

```bash
NO_COLOR=1 prmerge 24
```

## Troubleshooting

### Permission Denied

```bash
chmod +x /home/sw/work/AI-Agent-Framework/scripts/prmerge
```

### GitHub CLI Not Installed

```bash
# Ubuntu/Debian
sudo apt install gh

# macOS
brew install gh

# Windows
winget install --id GitHub.cli
```

### jq Not Installed

```bash
# Ubuntu/Debian
sudo apt install jq

# macOS
brew install jq

# Windows
winget install jqlang.jq
```

### Branch Protection Cannot Disable

If you can't disable branch protection:

1. Use Option C (manual git merge)
2. Or have another user with admin access approve
3. Or temporarily add exception for your user

### Merge Conflicts

If merge has conflicts:

1. Script will abort
2. Manually resolve conflicts:
   ```bash
   git checkout main
   git pull origin main
   git merge origin/issue/24-api-service-layer
   # Resolve conflicts in editor
   git add .
   git commit
   git push origin main
   ```
3. Run `prmerge` again (will detect already merged)

## Best Practices

### 1. Always Run CI First

Ensure CI passes before running prmerge:

```bash
gh pr checks <pr_number> --required --watch --fail-fast
```

### 2. Review Before Merging

Don't skip the review step. Check:

- Code quality and architecture
- Test coverage and quality
- Documentation completeness
- Security considerations
- Breaking changes

### 3. Track Actual Hours

Always provide actual hours for learning:

```bash
prmerge 24 7.5  # Better than: prmerge 24
```

### 4. Run from Repository Root

While script works from any directory, running from root is clearer:

```bash
cd /home/sw/work/AI-Agent-Framework
./scripts/prmerge 24 7.5
```

### 5. Check Dependencies After

After closing an issue, check what was unblocked:

```bash
./scripts/next-issue.py --verbose
```

## Advanced Usage

### Dry Run (Feature Request)

To see what would happen without merging:

```bash
# Not yet implemented - future enhancement
prmerge 24 --dry-run
```

### Custom Closing Message (Feature Request)

To use custom closing message:

```bash
# Not yet implemented - future enhancement
prmerge 24 --message-file closing-message.md
```

### Batch Merge (Feature Request)

To merge multiple PRs in sequence:

```bash
# Not yet implemented - future enhancement
prmerge 24 25 26 --batch
```

## Related Documentation

- [GitHub CLI Manual](https://cli.github.com/manual/)
- [Issue Tracking System](../STEP-1-IMPLEMENTATION-TRACKING.md)
- [Learning System](./record-completion.py)
- [Issue Selection](./next-issue.py)
- [Development Workflow](../docs/development.md)

## Changelog

### Version 1.0.0 (2026-01-18)

Initial release with features:

- Automatic PR detection
- CI validation
- Branch protection handling
- Comprehensive closing messages
- Learning system integration
- Next issue suggestion

## Contributing

To improve this script:

1. Test your changes thoroughly
2. Update this documentation
3. Add error handling for new cases
4. Maintain backward compatibility
5. Follow bash best practices

## Enhancement Roadmap

See **[prmerge Best Practices & Enhancement Recommendations](prmerge-best-practices.md)** for detailed analysis and implementation recommendations.

### Summary of Recommendations

| Enhancement               | Priority  | Status      | Recommendation                                                         |
| ------------------------- | --------- | ----------- | ---------------------------------------------------------------------- |
| **Issue Type Templates**  | 🟢 HIGH   | Recommended | ✅ Implement - 4 templates for infrastructure/feature/bugfix/docs      |
| **Enhanced Metrics**      | 🟢 HIGH   | Recommended | ✅ Implement - Track PR complexity, CI iterations, workflow efficiency |
| **API Protection Toggle** | 🟡 MEDIUM | Conditional | ⚠️ Implement with safeguards - Auto-disable/enable branch protection   |
| **Rollback Support**      | 🟡 MEDIUM | Alternative | 📖 Document procedures - Do NOT automate (too risky)                   |
| **Batch Merge**           | 🔴 LOW    | Rejected    | ❌ Do not implement - Violates quality-first principle                 |

### Key Insights

**IMPLEMENT (High Priority):**

- Issue-specific closing message templates improve clarity and relevance
- Enhanced metrics strengthen the learning system for better future estimates
- API-based protection toggle streamlines workflow but requires safety features

**DOCUMENT (Not Automate):**

- Rollback procedures are critical but require human judgment
- Comprehensive guide covers when/how to rollback safely

**SKIP (Against Project Principles):**

- Batch merge undermines individual PR review quality
- Goes against "small diffs" and learning system philosophy

📖 **[Read Full Analysis →](prmerge-best-practices.md)**
