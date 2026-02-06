# Agent Workflow Prompts

This directory contains optimized workflow prompts for AI agents that resolve issues, merge PRs, and plan implementations.

## How to Use

These prompts are automatically referenced by agents when running in their respective modes:

1. **VS Code Copilot Integration**: Agents are invoked via `chat.tools.subagent.autoApprove` settings
   - Configuration: See `docs/VSCODE-GLOBAL-SETTINGS.md`
   - Settings file: `.vscode/settings.json`
   - Auto-approved agents: `resolve-issue-dev`, `close-issue`, `pr-merge`, `Plan`

2. **Copilot Instructions**: These workflows are referenced in `.github/copilot-instructions.md`
   - Agents automatically follow these patterns when in their respective modes
   - No additional configuration needed

3. **Manual Reference**: Use these as guides when running agents manually
   - Copy workflow steps into agent instructions
   - Follow optimization patterns documented here

## Available Agents

### Core Workflow Agents

- **[close-issue.md](close-issue.md)** - Close GitHub issues with traceability
- **[pr-merge.md](pr-merge.md)** - Merge PRs, close linked issues, clean workspace
- **[resolve-issue-dev.md](resolve-issue-dev.md)** - Implement solutions following DDD architecture
- **[Plan.md](Plan.md)** - Research and outline multi-step implementation plans

## Design Principles

All agent prompts follow these optimization principles:

### 1. **Early Exit Conditions**
- Check state before processing (e.g., issue already closed, PR already merged)
- Avoid redundant operations
- Example: `If already merged, skip to cleanup`

### 2. **Single-Pass Operations**
- No polling loops (check once, then decide)
- No repeated API calls for same data
- Batch operations where possible
- Example: `git add -A && git commit && git push` (not 3 separate commands)

### 3. **Limited Search Scope**
- Max 5 results for file searches
- Specific keywords, not broad scans
- Shallow analysis over deep dives
- Example: `rg -l "pattern" --max-count 5`

### 4. **Clear Success Criteria**
- Specific, testable conditions
- No ambiguous decision trees
- Sequential steps (no parallel uncertainty)
- Example: "Issue state = CLOSED with comment posted"

### 5. **Optimization Notes**
- Each agent documents its optimizations
- Explains why steps are minimal
- Notes where common bottlenecks were removed

## Performance Improvements

These optimized prompts reduce typical issue resolution time from **30-45 minutes** to **5-10 minutes** by:

- Eliminating CI polling loops (15s sleeps removed)
- Batching git operations (3 commands → 1)
- Adding early-exit conditions (skip completed work)
- Limiting file searches (no full codebase scans)
- Using admin merge to bypass non-blocking CI waits

## Usage

Agents reference these prompts as standard operating procedures. When invoked, they follow the workflow exactly as documented here.

Example:
```bash
# Invoke resolve-issue-dev agent
runSubagent resolve-issue-dev --issue 123

# Agent follows .github/prompts/agents/resolve-issue-dev.md workflow
```

## Maintenance

When updating agent workflows:
1. Keep prompts concise (< 100 lines)
2. Maintain early-exit conditions
3. Document optimizations
4. Test with real issues before committing
5. Update README when adding new agents
