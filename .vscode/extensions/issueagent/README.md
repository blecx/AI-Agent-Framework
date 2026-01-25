# Issue Agent - VS Code Chat Integration

## Overview

The `/issueagent` chat command provides an interactive way to run the autonomous AI agent directly from VS Code chat. It automatically:

1. **Selects the next issue** from GitHub using the priority order defined in documentation
2. **Runs the autonomous agent** on that issue
3. **Streams progress** to the chat window in real-time
4. **Reports results** when complete (success or failure)

## Quick Start

### Prerequisites

1. **Workspace open:** AI-Agent-Framework must be open in VS Code
2. **Python environment:** `.venv` must be set up (`./setup.sh`)
3. **GitHub authentication:** `gh auth login` must be complete
4. **Extension installed:** The issueagent extension must be loaded

### Installing the Extension

The extension is included in the workspace. To enable it:

```bash
# The extension is in .vscode/extensions/issueagent/
# VS Code should auto-detect it when you open the workspace
```

Or manually install:

1. Open Command Palette (`Ctrl+Shift+P`)
2. Run: `Developer: Install Extension from Location...`
3. Select: `.vscode/extensions/issueagent`

## Usage

### Basic Command

In the VS Code chat panel, type:

```
@issueagent /run
```

or simply:

```
@issueagent
```

The agent will:

- Select the next issue from GitHub
- Run the autonomous workflow
- Stream updates to chat
- Show final success/failure status

### What You'll See

**Phase 1: Issue Selection**

```
🤖 Autonomous Issue Agent Starting...

📋 Phase 1: Issue Selection
Running next-issue.py to find the next issue...

🔄 Reconciling with GitHub...
✅ Everything in sync
→ Next issue: #26
✅ Selected issue: #26
```

**Phase 2: Agent Execution**

```
🚀 Phase 2: Autonomous Agent Execution
Running agent on issue #26...

🔍 Analysis Phase
→ Fetching issue #26 from GitHub
✅ Issue analyzed

📋 Planning Phase
→ Creating implementation plan
✅ Plan created

🧪 Testing Phase
→ Writing test cases
✅ Tests written

⚙️ Implementation Phase
→ Writing code
✅ Implementation complete

✓ Validation Phase
→ Running tests
✅ All tests pass

👀 Review Phase
→ Self-reviewing code
✅ Review complete

📤 PR Creation
→ Creating pull request
✅ PR created

🎓 Learning Phase
→ Updating knowledge base
✅ Knowledge base updated
```

**Final Report**

```
---

✅ Issue Completed Successfully!

The agent has successfully:
- ✅ Analyzed issue #26
- ✅ Created implementation plan
- ✅ Written tests and code
- ✅ Verified all tests pass
- ✅ Created pull request
- ✅ Updated knowledge base

Check GitHub for the new PR!
```

## Features

### Real-time Streaming

The chat command streams output from both:

- `next-issue.py` - Issue selection and reconciliation
- `work-issue.py` - Autonomous agent execution

You see progress as it happens, not just at the end.

### Cancellation Support

Click the stop button in chat to cancel the agent:

- Kills Python processes
- Cleans up gracefully
- Shows cancellation message

### Error Handling

If something goes wrong, you'll see:

- Clear error messages
- Relevant log output
- Troubleshooting hints

Example failure message:

```
❌ Issue Resolution Failed

The agent encountered errors while working on issue #26.

Please check:
- Agent logs in the terminal
- GitHub issue for any automated comments
- Local git status for uncommitted changes
```

## Architecture

### Extension Structure

```
.vscode/extensions/issueagent/
├── package.json          # Extension manifest (chat participant registration)
├── extension.js          # Main extension code
└── README.md            # This file
```

### How It Works

1. **Chat Participant Registration**
   - Registers `@issueagent` participant
   - Provides `/run` command
   - Sets up chat handler

2. **Issue Selection** (`selectNextIssue`)
   - Spawns `scripts/next-issue.py`
   - Streams progress to chat
   - Parses issue number from output
   - Handles errors gracefully

3. **Agent Execution** (`runAgent`)
   - Spawns `scripts/work-issue.py --issue N`
   - Detects phase transitions (Analysis, Planning, etc.)
   - Streams important messages to chat
   - Returns success/failure status

4. **Progress Streaming**
   - Captures stdout/stderr from Python processes
   - Filters for meaningful messages (✓, ✅, →, etc.)
   - Formats with Markdown for readability
   - Shows phase emoji indicators

## Comparison with Other Methods

| Method                 | Interactive | Progress Visible   | IDE Integrated | Best For                             |
| ---------------------- | ----------- | ------------------ | -------------- | ------------------------------------ |
| **Chat `/issueagent`** | ✅ Yes      | ✅ Real-time       | ✅ Yes         | Interactive use, monitoring progress |
| **VS Code Task**       | ❌ No       | ⚠️ Terminal only   | ✅ Yes         | Quick automation, keyboard shortcuts |
| **CLI Script**         | ⚠️ Optional | ✅ Terminal output | ❌ No          | Scripting, automation                |

### When to Use Chat Command

✅ **Use chat when:**

- You want to see progress interactively
- You might need to cancel mid-execution
- You prefer GUI over terminal
- You want formatted, easy-to-read output

❌ **Use CLI/tasks when:**

- Running in CI/CD pipeline
- Scripting multiple issues
- You prefer terminal workflow
- No human monitoring needed

## Configuration

### Extension Settings

The extension uses your workspace configuration:

- Python path: `.venv/bin/python3` (auto-detected)
- Scripts: `scripts/next-issue.py` and `scripts/work-issue.py`
- Repository root: Current workspace folder

No additional configuration required!

### Agent Configuration

The agent itself uses:

- `configs/llm.json` - GitHub Models API token
- `agents/knowledge/` - Learning database
- `.github/copilot-instructions.md` - Project conventions

See [docs/agents/AUTONOMOUS-AGENT-GUIDE.md](../../docs/agents/AUTONOMOUS-AGENT-GUIDE.md) for agent configuration.

## Troubleshooting

### Extension Not Found

**Problem:** `@issueagent` doesn't appear in chat

**Solution:**

1. Check workspace has `.vscode/extensions/issueagent/` folder
2. Reload VS Code: `Ctrl+Shift+P` → `Developer: Reload Window`
3. Check extension is enabled: `Ctrl+Shift+X` → Search "issueagent"

### Python Environment Issues

**Problem:** "No such file or directory: python3"

**Solution:**

```bash
# Set up Python environment
./setup.sh
source .venv/bin/activate

# Verify it works
python3 --version
```

### GitHub Authentication

**Problem:** "gh: authentication required"

**Solution:**

```bash
# Authenticate with GitHub
gh auth login

# Verify it works
gh auth status
```

### Agent Configuration

**Problem:** "LLM configuration not found"

**Solution:**

```bash
# Copy example config
cp configs/llm.github.json.example configs/llm.json

# Edit and add your GitHub PAT token
# Get token from: https://github.com/settings/tokens
```

### No Issues Available

**Problem:** "No issues found" or "All issues completed"

**Solution:**

- Check GitHub for open issues in your repository
- Verify issue numbers in tracking file
- Run `./scripts/next-issue.py --verbose` for details

## Technical Details

### Dependencies

**Required Node.js modules:**

- `vscode` - VS Code API (provided by VS Code)
- `child_process` - For spawning Python processes (built-in)
- `path` - Path utilities (built-in)

No `npm install` required - uses only built-in Node.js modules!

**Required Python:**

- Python 3.10+ with `.venv` environment
- All agent dependencies (see `requirements.txt`)

### API Usage

**VS Code Chat API:**

```javascript
vscode.chat.createChatParticipant(id, handler);
```

**Handler signature:**

```javascript
async (request, chatContext, stream, token) => {
  stream.markdown('Text to display');
  // Process request
};
```

**Streaming:**

````javascript
stream.markdown('# Heading\n');
stream.markdown('Regular text\n');
stream.markdown('**Bold** and *italic*\n');
stream.markdown('```python\ncode\n```\n');
````

### Process Management

**Spawning Python:**

```javascript
const proc = spawn(pythonPath, [scriptPath, ...args], {
  cwd: repoRoot,
  env: process.env,
});
```

**Handling cancellation:**

```javascript
token.onCancellationRequested(() => {
  proc.kill();
});
```

**Reading output:**

```javascript
proc.stdout.on('data', (data) => {
  stream.markdown(data.toString());
});
```

## Future Enhancements

Possible improvements:

- **Interactive mode:** Pause for user input during phases
- **Issue selection:** Let user specify issue number in chat
- **Progress bar:** Visual progress indicator
- **History:** Show recent agent runs
- **Analytics:** Display success rates and metrics
- **Multi-issue:** Queue multiple issues

## Related Documentation

- **[AUTONOMOUS-AGENT-GUIDE.md](../../docs/agents/AUTONOMOUS-AGENT-GUIDE.md)** - Complete agent documentation
- **[WORK-ISSUE-WORKFLOW.md](../../docs/WORK-ISSUE-WORKFLOW.md)** - 6-phase workflow details
- **[agents/README.md](../../agents/README.md)** - Agent system overview

## Support

For issues or questions:

1. Check [AUTONOMOUS-AGENT-GUIDE.md](../../docs/agents/AUTONOMOUS-AGENT-GUIDE.md) troubleshooting section
2. Run agent manually to isolate the issue: `./scripts/work-issue.py --issue N --dry-run`
3. Check Python environment: `source .venv/bin/activate && python3 --version`
4. Verify GitHub auth: `gh auth status`

---

**Ready to start?** Open chat and type: `@issueagent` 🚀
