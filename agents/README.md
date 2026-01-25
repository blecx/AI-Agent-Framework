# AI Agents

This directory contains two agent systems for issue resolution.

---

## 🤖 Autonomous Workflow Agent (NEW - Recommended)

**AI-powered agent using Microsoft Agent Framework + GPT-5.1-codex**

### Files
- `autonomous_workflow_agent.py` - Main AI agent implementation
- `tools.py` - 11 tool functions (GitHub, Git, Files, Testing, KB)
- `llm_client.py` - GitHub Models client factory
- `knowledge/` - Knowledge base (auto-updated after each issue)

### Usage

```bash
# Activate environment
source .venv/bin/activate

# Run agent on an issue
./scripts/work-issue.py --issue 26

# Or use VS Code: Ctrl+Shift+P → Run Task → "🤖 Work on Issue (Autonomous)"
```

### What It Does

- ✅ Fetches and analyzes issues with LLM reasoning
- ✅ Creates implementation plans
- ✅ Generates code (test-first approach)
- ✅ Runs tests and fixes failures automatically
- ✅ Self-reviews changes
- ✅ Creates pull requests
- ✅ **Learns from each issue** (guaranteed post-execution)

### Documentation

**📖 Complete Guide:** [docs/agents/AUTONOMOUS-AGENT-GUIDE.md](../docs/agents/AUTONOMOUS-AGENT-GUIDE.md)

---

## 📋 Manual Workflow Agent (OLD - Deprecated)

**Manual checklist-based workflow tracker**

### Files
- `workflow_agent.py` - Old manual workflow implementation
- `base_agent.py` - Base class for manual agent

### Status

⚠️ **Deprecated** - Superseded by `autonomous_workflow_agent.py`

The old agent was a manual checklist that paused at each phase requiring user input. It has been replaced by the autonomous agent which actually uses AI for reasoning and code generation.

**Kept for reference only.** Use the new autonomous agent instead.

---

## 📚 Knowledge Base

Located in `agents/knowledge/`:

- **workflow_patterns.json** - Complete execution records from all issues
- **problem_solutions.json** - Problems encountered and their solutions  
- **time_estimates.json** - Time insights for estimation
- **command_sequences.json** - Useful command patterns
- **agent_metrics.json** - Success rate, total issues completed

**Auto-updated** by autonomous agent after each issue.

---

## 🎯 Quick Comparison

| Feature | Autonomous Agent | Manual Agent |
|---------|-----------------|--------------|
| **AI Reasoning** | ✅ GPT-5.1-codex | ❌ None |
| **Code Generation** | ✅ Automatic | ❌ Manual |
| **Test Execution** | ✅ Automatic | ❌ Manual |
| **PR Creation** | ✅ Automatic | ❌ Manual |
| **Learning** | ✅ Guaranteed after each issue | ❌ Manual export/train |
| **Recommended** | ✅ **Use This** | ❌ Deprecated |

---

## 🚀 Getting Started

1. **Configure GitHub PAT token:**
   ```bash
   cp configs/llm.github.json.example configs/llm.json
   # Edit configs/llm.json and add your token
   ```

2. **Run the agent:**
   ```bash
   source .venv/bin/activate
   ./scripts/work-issue.py --issue 26
   ```

3. **Read the guide:**
   See [docs/agents/AUTONOMOUS-AGENT-GUIDE.md](../docs/agents/AUTONOMOUS-AGENT-GUIDE.md) for complete documentation.

---

**The autonomous agent improves with every issue!** 🎉


1. **Different workflow** - Issue requires steps not in 6-phase workflow
2. **Different domain** - Deployment, security, infrastructure work
3. **Specialized task** - Release management, dependency updates

See [restore-chat-and-create-custom-agent.md](../docs/howto/restore-chat-and-create-custom-agent.md) for detailed guide.

## Development

### Agent Structure

All agents inherit from `BaseAgent` and implement:

- `execute()` - Main workflow logic
- `validate_prerequisites()` - Check requirements
- Phase execution methods

### Testing

```bash
# Test agent with dry run
./scripts/agents/workflow --issue 26 --dry-run

# View agent logs
cat agents/training/logs/issue-26-workflow_agent-*.json
```

### Debugging

Set environment variable for verbose output:

```bash
export AGENT_DEBUG=1
./scripts/agents/workflow --issue 26
```

## Best Practices

1. **Always run in dry-run first** for new issues
2. **Review planning doc** before starting implementation
3. **Track time** to improve estimates
4. **Document problems** encountered for knowledge base
5. **Update agent regularly** (every 5-10 issues)

## Resources

- [How to Restore Chat and Create Custom Agents](../docs/howto/restore-chat-and-create-custom-agent.md)
- [Chat Exports](../docs/chat/)
- [Agent Training Logs](training/logs/)
