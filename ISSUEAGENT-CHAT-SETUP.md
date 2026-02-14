# /issueagent Chat Command - Quick Setup

## What This Does

Type `@issueagent` in VS Code chat to:

1. ✅ Auto-select next GitHub issue
2. ✅ Run autonomous AI agent
3. ✅ See real-time progress
4. ✅ Get success/failure report

## Setup (One Time - 2 minutes)

### Step 1: Install the Extension

The extension is already in your workspace! Just reload VS Code:

```bash
# In VS Code, press Ctrl+Shift+P
# Type: Developer: Reload Window
# Press Enter
```

Or manually install:

1. Open Command Palette: `Ctrl+Shift+P`
2. Type: `Developer: Install Extension from Location...`
3. Navigate to: `.vscode/extensions/issueagent`
4. Click "Install"

## Create-Issue Workflow (optional)

If you want the **create-issue** workflow to be discoverable in the VS Code chat agent menu, you can also use:

```text
@create-issue
```

This opens the workflow prompt (`.github/prompts/agents/create-issue.md`) and shows a copy/paste command to run the existing `create-issue` workflow via Copilot subagents.

### Step 2: Verify It Works

1. Open VS Code Chat (sidebar or `Ctrl+Alt+I`)
2. Type: `@issueagent`
3. You should see the participant respond!

## Usage

### Basic Command

```text
@issueagent
```

That's it! The agent will:

- Select next issue from GitHub
- Run autonomous workflow
- Stream progress to chat
- Report results when done

### What You'll See

```text
🤖 Autonomous Issue Agent Starting...

📋 Phase 1: Issue Selection
→ Next issue: #26
✅ Selected issue: #26

🚀 Phase 2: Autonomous Agent Execution

🔍 Analysis Phase
→ Fetching issue #26 from GitHub
✅ Issue analyzed

📋 Planning Phase
✅ Plan created

🧪 Testing Phase
✅ Tests written

⚙️ Implementation Phase
✅ Implementation complete

✓ Validation Phase
✅ All tests pass

👀 Review Phase
✅ Review complete

📤 PR Creation
✅ PR created

---

✅ Issue Completed Successfully!

Check GitHub for the new PR!
```

## Troubleshooting

### "Extension not found"

Reload VS Code: `Ctrl+Shift+P` → `Developer: Reload Window`

### "Python not found"

Run setup first:

```bash
./setup.sh
source .venv/bin/activate
```

### "GitHub authentication required"

Authenticate once:

```bash
gh auth login
```

### "LLM config not found"

Copy and configure:

```bash
cp configs/llm.github.json.example configs/llm.json
# Edit configs/llm.json and add your GitHub PAT token
```

## Comparison

| Method   | How to Run                           | Best For               |
| -------- | ------------------------------------ | ---------------------- |
| **Chat** | `@issueagent`                        | Interactive monitoring |
| **Task** | `Ctrl+Shift+P` → Run Task            | Keyboard shortcuts     |
| **CLI**  | `./scripts/work-issue.py --issue 26` | Automation/scripting   |

## Full Documentation

See [.vscode/extensions/issueagent/README.md](.vscode/extensions/issueagent/README.md) for:

- Complete feature list
- Architecture details
- Advanced configuration
- Cancellation support
- Error handling

---

**Ready?** Open chat and type: `@issueagent` 🚀
