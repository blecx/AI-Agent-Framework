# Custom AI Agents

This directory contains custom AI agents trained on chat exports and project knowledge.

## Available Agents

### 1. Workflow Agent

**Purpose:** Automates the 6-phase issue resolution workflow

**Usage:**

```bash
# Run workflow for an issue
./scripts/agents/workflow --issue 26

# Dry run (preview without executing)
./scripts/agents/workflow --issue 26 --dry-run
```

**Workflow Phases:**

1. **Context** - Read issue and gather relevant files
2. **Planning** - Create planning document with estimates
3. **Implementation** - Test-first development approach
4. **Testing** - Build and run tests
5. **Review** - Self-review and Copilot review
6. **PR & Merge** - Create PR and merge with validation

**Trained On:** Issues #24, #25

## Agent Training Process

### After Completing an Issue

1. **Export Chat** (with timeout protection):

   ```bash
   ./scripts/export_chat.py --issue 25 --output docs/chat/
   ```

2. **Extract Learnings**:

   ```bash
   ./scripts/extract_learnings.py --export docs/chat/2026-01-19-issue25-complete-workflow.md
   ```

3. **Analyze & Update Agent**:

   ```bash
   ./scripts/train_agent.py --issue 25
   ```

4. **Review Recommendations**:
   ```bash
   ./scripts/train_agent.py --recommend
   ```

### Continuous Improvement

The agent automatically:

- **Learns from problems** - Catalogs issues and solutions
- **Improves time estimates** - Refines predictions based on actuals
- **Expands command library** - Adds new proven command patterns
- **Self-analyzes** - Detects when updates are needed

### When to Update Agent

The agent will recommend updates when:

- **2+ new problems** discovered (high priority)
- **Time variance >10%** from predictions (medium priority)
- **5+ new commands** could be automated (low priority)
- **Workflow pattern changes** significantly (critical - may need new agent)

## Knowledge Base Structure

```
agents/knowledge/
├── workflow_patterns.json      # Successful workflows from all issues
├── problem_solutions.json      # Known problems and solutions
├── time_estimates.json         # Historical time data
├── command_sequences.json      # Reusable command patterns
└── agent_metrics.json          # Agent performance and recommendations
```

## Agent Maturity Levels

- **Nascent** (0-2 issues): Basic functionality, low confidence
- **Initial** (2-5 issues): Learning patterns, medium-low confidence
- **Learning** (5-10 issues): Recognizing patterns, medium confidence
- **Developing** (10-20 issues): Reliable for common cases, high confidence
- **Mature** (20+ issues): Production-ready, very high confidence

**Current Status:** Run `./scripts/train_agent.py --analyze-all` to see current maturity

## Creating New Agents

When to create a new specialized agent:

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
