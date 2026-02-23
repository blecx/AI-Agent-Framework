# Autonomous AI Agent - Complete Guide

**REAL AI-Powered Agent using Microsoft Agent Framework + GitHub Models**

**Last Updated:** January 19, 2026

---

## Overview

A **fully autonomous AI agent** that resolves GitHub issues end-to-end using GPT-5.1-codex for reasoning and code generation.

### What This Agent Does

✅ **Analyzes GitHub issues** with LLM reasoning (GPT-5.1-codex)  
✅ **Creates implementation plans** based on project context  
✅ **Writes code** following test-first development  
✅ **Runs tests** and fixes failures automatically  
✅ **Self-reviews** changes against acceptance criteria  
✅ **Creates pull requests** with generated descriptions  
✅ **Learns continuously** - updates knowledge base after each issue

**This is NOT a checklist script** - it's a real AI agent that makes autonomous decisions!

---

## Quick Start (5 Minutes)

### 1. Configure GitHub PAT Token

```bash
# Copy example config
cp configs/llm.github.json.example configs/llm.json

# Edit and add your GitHub PAT token
nano configs/llm.json
```

**Get your token:** https://github.com/settings/tokens (needs `repo` scope)

### 2. Run the Agent

```bash
# Activate Python environment
source .venv/bin/activate

# Select next issue
./next-issue

# Let agent work on it autonomously
./scripts/work-issue.py --issue 26
```

### 3. VS Code Chat (Interactive)

Open VS Code chat and type:

```
@issueagent
```

This will automatically select the next issue and run the agent with real-time progress streaming.

See [.vscode/extensions/issueagent/README.md](../../.vscode/extensions/issueagent/README.md) for details.

### 4. Or Use VS Code Tasks

Press `Ctrl+Shift+P` → **Tasks: Run Task** → **🤖 Work on Issue (Autonomous)**

---

## How It Works

### Architecture

```
User → CLI (work-issue.py)
         ↓
     Agent (Microsoft Agent Framework)
         ├─ System Instructions (project context + workflow guide)
         ├─ LLM (GitHub Models: GPT-5.1-codex)
         └─ 11 Tools (GitHub, Git, Files, Testing, KB)
              ↓
     6-Phase Workflow
         ├─ 1. Context & Analysis
         ├─ 2. Planning
         ├─ 3. Implementation (test-first)
         ├─ 4. Testing
         ├─ 5. Review
         └─ 6. PR Creation
              ↓
     Guaranteed Learning (post-execution)
         └─ Updates agents/knowledge/*.json
```

### The 6-Phase Workflow

**Phase 1: Context & Analysis**

- Fetches issue from GitHub
- Analyzes requirements using LLM
- Gathers relevant code files
- Loads patterns from knowledge base

**Phase 2: Planning**

- Creates implementation plan document
- Breaks down into testable steps
- Estimates time based on historical data
- Identifies risks and mitigation

**Phase 3: Implementation**

- Creates feature branch
- Writes tests first (TDD approach)
- Implements code changes
- Commits incrementally with descriptive messages

**Phase 4: Testing**

- Runs build commands
- Executes test suites
- Analyzes failures with LLM
- Fixes issues automatically
- Retries until tests pass

**Phase 5: Review**

- Self-reviews against acceptance criteria
- Checks for removed functionality
- Verifies code conventions
- Ensures no debug code remains

**Phase 6: PR Creation**

- Generates PR title and description
- Creates pull request via GitHub CLI
- Updates knowledge base with learnings

### Guaranteed Learning System

After EVERY issue (success or failure), the agent:

1. **Asks itself for structured learnings:**
   - Problems encountered + solutions
   - Key decisions made
   - Useful commands discovered
   - Time breakdown by phase
   - Files changed
   - Patterns learned

2. **Updates knowledge base files:**
   - `workflow_patterns.json` - Complete execution records
   - `problem_solutions.json` - Problems and their solutions
   - `time_estimates.json` - Time insights for estimation
   - `command_sequences.json` - Useful command patterns
   - `agent_metrics.json` - Success rate, total issues

3. **Makes learnings available for next issue:**
   - Future issues load this knowledge
   - Agent gets smarter over time
   - No manual training steps needed!

---

## Usage Modes

### Fully Autonomous

```bash
./scripts/work-issue.py --issue 26
```

Agent works independently through all 6 phases. You just wait for the PR!

### Dry Run (Analysis Only)

```bash
./scripts/work-issue.py --issue 26 --dry-run
```

Agent analyzes and plans but doesn't make actual changes. Perfect for:

- Understanding what agent will do
- Verifying approach before committing
- Testing with unfamiliar issues

### Interactive (Guided)

```bash
./scripts/work-issue.py --issue 26 --interactive
```

Agent works through phases, then you can:

- Give additional instructions
- Ask questions about the implementation
- Request changes or improvements
- Continue conversation until satisfied

---

## Configuration

### Model Selection

Edit `configs/llm.json`:

```json
{
  "api_key": "github_pat_YOUR_TOKEN",
  "model": "openai/gpt-5.1-codex",
  "base_url": "https://models.github.ai/inference",
  "temperature": 0.2,
  "max_tokens": 16384,
  "timeout": 300
}
```

### Request Throttle (Rate-Limit Protection)

The agent applies a process-local throttle to **all outbound LLM calls** (planning, coding, review) by default.

- `WORK_ISSUE_MAX_RPS` (default: `0.2`) → hard max requests/second (5 seconds minimum spacing)
- `WORK_ISSUE_RPS_JITTER` (default: `0.1`) → adds up to 10% positive jitter per request to reduce burst alignment

Example:

```bash
export WORK_ISSUE_MAX_RPS=0.25
export WORK_ISSUE_RPS_JITTER=0.15
```

**Available Models (all free on GitHub):**

---

## Multi-Repo & Environment Parity

This agent may operate across multiple repos:

- **Backend repo (this workspace)**: AI-Agent-Framework (Python)
- **UX repo**: \_external/AI-Agent-Framework-Client (React/TypeScript)

Use the repo-native environment for every command:

- Backend: activate `.venv` before Python commands.
- UX repo: run npm commands inside `_external/AI-Agent-Framework-Client`.

### Validation (Best-Practice Test Suites)

Run the suite that matches the repo(s) you changed:

- **Backend changes**: `python -m black apps/api/`, `python -m flake8 apps/api/`, `pytest`
- **apps/web changes**: `npm install`, `npm run lint`, `npm run build`
- **UX repo changes**: `npm install`, `npm run build`, `npm run test`

| Model                  | Quality | Best For                                   |
| ---------------------- | ------- | ------------------------------------------ |
| `openai/gpt-5.1-codex` | 0.899   | **Advanced coding** (default, recommended) |
| `openai/gpt-4.1`       | 0.844   | Balanced performance                       |
| `openai/gpt-4o`        | 0.749   | Faster operations                          |

**Why GPT-5.1-codex?**

- Specialized for programming tasks
- Repo-aware intelligence
- 272K context window
- Better code generation quality

### Custom System Instructions

Edit `agents/autonomous_workflow_agent.py`, method `_build_system_instructions()` to:

- Add project-specific guidelines
- Change workflow phases
- Add custom validation rules
- Modify tool usage patterns

---

## Available Tools

The agent has access to 11 tools (defined in `agents/tools.py`):

### GitHub Operations

- `fetch_github_issue(issue_number)` - Get issue details as JSON
- `create_github_pr(title, body)` - Create pull request

### File Operations

- `read_file_content(file_path)` - Read file contents
- `write_file_content(file_path, content)` - Write/create files
- `list_directory_contents(directory_path)` - List directory

### Git Operations

- `git_commit(message)` - Stage and commit changes
- `get_changed_files()` - See what's modified
- `create_feature_branch(branch_name)` - Create branch from main

### Testing & Build

- `run_command(command, working_directory)` - Execute shell commands
  - Used for: `npm run build`, `npx vitest run`, `pytest`, etc.

### Knowledge Base

- `get_knowledge_base_patterns()` - Load historical patterns
- `update_knowledge_base(category, data)` - Save learnings

---

## VS Code Integration

### Available Tasks

Press `Ctrl+Shift+P` → **Tasks: Run Task**:

- 🤖 **Work on Issue (Autonomous)** - Full automation
- 🔍 **Work on Issue (Dry Run)** - Analysis only
- 💬 **Work on Issue (Interactive)** - With conversation
- 📋 **Select Next Issue** - Use next-issue selector

### Task Configuration

Tasks are defined in `.vscode/tasks.json` and automatically:

- Activate Python virtual environment
- Pass issue number as input
- Show output in dedicated terminal
- Allow easy re-running

---

## Example Session

```bash
$ source .venv/bin/activate
$ ./scripts/work-issue.py --issue 26

╔══════════════════════════════════════════════════════════════════╗
║        Autonomous Workflow Agent - AI-Powered Development        ║
║                  Powered by Microsoft Agent Framework            ║
╚══════════════════════════════════════════════════════════════════╝

Prerequisites:
  GitHub CLI (gh)......................... ✅
  Git..................................... ✅
  Python 3.12............................. ✅
  LLM config.............................. ✅

🤖 Initializing Autonomous Workflow Agent v2.0
📋 Issue #26
🔗 Connecting to GitHub Models...
   Using model: openai/gpt-5.1-codex
✅ Agent initialized and ready

══════════════════════════════════════════════════════════════════════
🚀 Starting Autonomous Workflow Execution
══════════════════════════════════════════════════════════════════════

🤖 Agent: I'll start by fetching Issue #26 from GitHub...

[Agent works through all 6 phases autonomously]

...

✅ Pull request created: #27
📚 Updating knowledge base with learnings...
✅ Knowledge base updated

══════════════════════════════════════════════════════════════════════
✅ Workflow Completed in 245.3 seconds (4.1 minutes)
══════════════════════════════════════════════════════════════════════
```

---

## Troubleshooting

### "GitHub PAT token required"

Create `configs/llm.json` with your GitHub token:

```bash
cp configs/llm.github.json.example configs/llm.json
# Edit and add your token
```

### "gh CLI not found"

Install GitHub CLI:

```bash
# Ubuntu/Debian
sudo apt install gh

# macOS
brew install gh

# Then authenticate
gh auth login
```

### "ModuleNotFoundError: No module named 'agent_framework'"

Activate the virtual environment first:

```bash
source .venv/bin/activate
./scripts/work-issue.py --issue 26
```

The agent framework is installed in `.venv`, not globally.

### Agent Made Mistakes

1. **Try dry-run first:** `--dry-run` shows what agent plans to do
2. **Use interactive mode:** `--interactive` to guide the agent
3. **Check project context:** Ensure `.github/copilot-instructions.md` is clear
4. **Review system instructions:** May need project-specific adjustments

### Tests Failing

Agent automatically retries test failures with LLM analysis. If persistent:

1. Check test output in agent's terminal
2. Run tests manually: `cd apps/web && npx vitest run`
3. Review code changes: `git diff`
4. Use interactive mode to debug with agent

---

## Files & Structure

### Core Agent Files

```text
agents/
├── autonomous_workflow_agent.py    # Main agent implementation
├── tools.py                        # 11 tool functions
├── llm_client.py                   # GitHub Models client
├── README.md                       # Agent system overview
└── knowledge/                      # Knowledge base (auto-updated)
    ├── workflow_patterns.json
    ├── problem_solutions.json
    ├── time_estimates.json
    ├── command_sequences.json
    └── agent_metrics.json

scripts/
├── work-issue.py                   # CLI entry point (main interface)
└── next-issue.py                   # Issue selector

configs/
├── llm.json                        # Your config (gitignored)
└── llm.github.json.example         # Example config

.vscode/
└── tasks.json                      # VS Code task integration

docs/agents/
└── AUTONOMOUS-AGENT-GUIDE.md       # This file
```

### Old Agent System (Manual)

```text
agents/
├── workflow_agent.py               # OLD: Manual checklist agent
└── base_agent.py                   # OLD: Base class for manual agent
```

**Note:** The old `workflow_agent.py` is kept for reference but superseded by `autonomous_workflow_agent.py`.

---

## Technical Details

**Built With:**

- Microsoft Agent Framework (Python)
- GitHub Models (GPT-5.1-codex)
- OpenAI-compatible API
- Tool-based function calling
- Async/await pattern

**Model Used:**

- **Default:** `openai/gpt-5.1-codex`
- **Quality:** 0.899 (high)
- **Context:** 272K tokens
- **Cost:** Free on GitHub Models (rate limited)
- **Specialization:** Advanced coding, repo-aware

**Learning System:**

- Post-execution automatic extraction
- Structured JSON knowledge base
- Guaranteed updates after each issue
- Progressive improvement over time

---

## Comparison: Before vs After

### Before (Manual workflow_agent.py)

- ❌ Just a checklist with pause buttons
- ❌ No AI reasoning or decisions
- ❌ No code generation
- ❌ User does all implementation
- ❌ Learning happens AFTER (separate step)
- ❌ Manual knowledge base updates

### After (Autonomous autonomous_workflow_agent.py)

- ✅ Real GPT-5.1-codex AI reasoning
- ✅ Autonomous decision making
- ✅ Generates code automatically
- ✅ Runs tests and fixes failures
- ✅ Learning happens DURING work
- ✅ Automatic knowledge base updates
- ✅ Gets smarter with each issue

---

## Next Steps

### First Time Using

1. **Configure:** `cp configs/llm.github.json.example configs/llm.json`
2. **Add token:** Edit `configs/llm.json` with GitHub PAT
3. **Test:** `./scripts/work-issue.py --issue 26 --dry-run`
4. **Run:** `./scripts/work-issue.py --issue 26`
5. **Review:** Check the PR created by the agent

### Regular Usage

```bash
# Daily workflow
./next-issue                              # Select next
./scripts/work-issue.py --issue <N>       # Let agent work
# Agent creates PR automatically
# Review and merge PR
# Repeat!
```

### Monitoring Learning

```bash
# View accumulated knowledge
cat agents/knowledge/workflow_patterns.json | jq .
cat agents/knowledge/problem_solutions.json | jq .
cat agents/knowledge/agent_metrics.json | jq .
```

### Improving the Agent

1. Review `agents/knowledge/problem_solutions.json` for recurring issues
2. Update system instructions if needed
3. Add project-specific patterns to knowledge base
4. Adjust temperature/model if output quality varies

---

## Support

### Getting Help

1. Check `./scripts/work-issue.py --help`
2. Try `--dry-run` to understand behavior
3. Use `--interactive` to work with the agent
4. Review agent code in `agents/` directory
5. Check knowledge base for patterns

### Reporting Issues

If the agent consistently fails on certain issue types:

1. Capture the failure in `--dry-run` mode
2. Check system instructions relevance
3. Verify tools are working (`gh`, `git`, etc.)
4. Review knowledge base for similar past issues

---

## Summary

You have a **production-ready autonomous AI agent** that:

✅ Takes GitHub issue numbers as input  
✅ Analyzes and understands requirements  
✅ Creates implementation plans  
✅ Writes tests and code  
✅ Runs tests and fixes failures  
✅ Self-reviews changes  
✅ Creates pull requests  
✅ Learns from each issue automatically

**The agent improves with every issue completed!** 🚀

---

_Built with Microsoft Agent Framework + GitHub Models_  
_GPT-5.1-codex (Quality: 0.899)_  
_Last Updated: January 19, 2026_
