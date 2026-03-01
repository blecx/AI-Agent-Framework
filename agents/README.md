# AI Agents

This directory contains two agent systems for issue resolution.

---

## 🤖 Autonomous Workflow Agent (NEW - Recommended)

**AI-powered agent using Microsoft Agent Framework + GPT-5.1-codex**

### Files
- `autonomous_workflow_agent.py` - Main AI agent implementation
- `tools.py` - 13 tool functions (GitHub, Git, Files, Testing, Coverage, KB, ML)
- `command_cache.py` - Command result caching (saves 8-12s per issue)
- `time_estimator.py` - ML-based time estimation (RandomForest model)
- `coverage_analyzer.py` - Test coverage analysis and quality gates
- `commit_strategy.py` - Multi-stage commit strategy for better Git history
- `learning_scorer.py` - Learning relevance scoring and filtering (NEW)
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
- ✅ **Caches command results** (1-hour TTL, saves 8-12s per issue)
- ✅ **ML-based time estimation** (RandomForest with confidence scoring)
- ✅ **Coverage analysis** (enforces 80%+ threshold, detects regressions)

### Coverage Analysis (NEW)

Agents automatically analyze test coverage to maintain quality:

- **Analyzer:** CoverageAnalyzer enforces coverage quality gates
- **Features:** Before/after comparison, regression detection, threshold enforcement
- **Output:** Pass/fail status + low coverage warnings + metrics
- **Metrics:** `coverage_regressions_prevented`, `average_coverage_delta`

**How it works:**

```python
# Analyze coverage impact of changes
result = analyze_coverage_impact(
    changed_files=["apps/api/main.py", "apps/api/models.py"],
    coverage_threshold=80.0
)
# Returns: {"passed": true, "total_coverage": 85.5, "low_coverage_files": []}
```

**Benefits:**
- ✅ Prevents coverage regressions
- ✅ Warns about files below 80% threshold
- ✅ Catches untested code early
- ✅ Maintains/improves overall coverage

### Multi-Stage Commit Strategy (NEW)

Agents can organize changes into logical, reviewable commits instead of one large commit:

**How it works:**

```python
# Execute multi-stage commit strategy
strategy = get_commit_strategy(working_directory=".")
result = strategy.execute_strategy(message_template="Implement feature", dry_run=False)
# Returns: {"success": true, "commits_created": 3, "stages_executed": ["tests", "implementation", "documentation"]}
```

**Stages (in order):**
1. **Tests (red):** Test files first (test-driven development)
2. **Implementation (green):** Core implementation files
3. **Documentation:** README, docs, comments
4. **Refactoring:** Code cleanup and optimization

**Benefits:**
- ✅ Better Git history (logical progression)
- ✅ Easier code review (smaller, focused commits)
- ✅ Safer rollbacks (revert individual stages)
- ✅ Enforces TDD workflow (tests before implementation)
- ✅ Tracks metrics: commits_per_pr (target 2-4), pr_review_time_minutes

### Learning Relevance Scoring (NEW)

Agents score and filter learnings by relevance to avoid applying outdated or irrelevant patterns:

**Scoring factors:**
- **Recency:** 90-day half-life decay (newer = more relevant)
- **Domain match:** 1.0 for exact match, 0.3 for cross-domain
- **Repository match:** 1.0 for same repo, 0.5 for cross-repo
- **Success rate:** Historical success of this learning
- **Application frequency:** Number of successful applications

**Usage:**

```python
# Score and filter learnings for current context
scorer = get_learning_scorer(relevance_threshold=0.3)
relevant = scorer.get_relevant_learnings(
    learnings=all_learnings,
    current_domain="backend",
    current_repository="AI-Agent-Framework"
)
# Returns: List of ScoredLearning sorted by relevance (highest first)
```

**Benefits:**
- ✅ Apply only relevant learnings to current issue
- ✅ Reduce false positives from outdated patterns
- ✅ Faster problem solving (less noise)
- ✅ Tracks metrics: learning_relevance_score_avg, irrelevant_learnings_filtered

### ML Time Estimation

Agents use machine learning to predict issue resolution times more accurately:

- **Model:** RandomForestRegressor trained on historical data
- **Features:** files_to_change, lines_estimate, domain, multi-repo, dependencies, complexity
- **Output:** Estimated hours + confidence % + reasoning
- **Metrics:** Mean Absolute Error (MAE) tracked

**How it works:**

```python
# Get estimate for backend work
estimate = get_time_estimate(
    files_to_change=5,
    lines_estimate=200,
    domain="backend",
    complexity_score=3
)
# Returns: "Time Estimate: 2.8 hours (Confidence: 75%)"
```

**Improves over time:** As more issues are resolved and added to the knowledge base, predictions become more accurate.

### Command Caching (NEW)

Agents automatically cache idempotent command results to avoid redundant operations:

- **Cached commands:** npm install, pip install, linting, builds
- **Cache TTL:** 1 hour per command+directory
- **Impact:** Saves 8-12 seconds per issue (3 npm installs → 1 actual run)
- **Metrics:** Use `get_cache_metrics()` tool to view cache performance

**How it works:**

```python
# First call: runs npm install (takes 4s)
run_command("npm install", "/path/to/app")

# Second call within 1 hour: uses cache (instant)
run_command("npm install", "/path/to/app")  # [CACHED] Exit code: 0
```

**Disable caching for non-idempotent commands:**

```python
# Commands that modify state should not be cached
run_command("git commit -m 'msg'", "/path", use_cache=False)
```

### Documentation

**📖 Complete Guide:** [docs/agents/AUTONOMOUS-AGENT-GUIDE.md](../docs/agents/AUTONOMOUS-AGENT-GUIDE.md)

---

## 🧠 Ralph Agent (Spec-Kit strict profile)

Ralph is a high-discipline profile built on the autonomous runtime with:

- Skill-based acceptance criteria
- Specialist reviewer gates (architecture, quality, security, UX when needed)
- Bounded review/fix iteration loop

### Files

- `ralph_agent.py` - Ralph profile overlay
- `agent_registry.py` - Alias/spec resolver (`ralph`, `autonomous`, `module:Class`)
- `.github/prompts/agents/ralph-agent.md` - Spec-Kit style workflow prompt
- `.github/prompts/modules/ralph-skills-review.md` - Skills + review matrix

### Usage

```bash
./scripts/work-issue.py --issue 26 --agent ralph
```

VS Code chat:

```text
@ralph /run
```

**📖 Guide:** [docs/agents/ralph-agent.md](../docs/agents/ralph-agent.md)

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
