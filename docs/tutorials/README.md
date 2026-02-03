# Tutorials

Welcome to the ISO 21500 AI-Agent Framework tutorials! These hands-on guides teach you how to manage projects using international project management standards with AI assistance.

## 🎯 What You'll Learn

- **Project Management**: Create and manage ISO 21500-compliant projects
- **RAID Management**: Track Risks, Assumptions, Issues, and Dependencies
- **Workflow States**: Navigate the five ISO 21500 phases
- **Artifact Generation**: Produce project documents with AI assistance
- **TUI + GUI**: Master both command-line and web interfaces
- **Automation**: Script repetitive tasks for efficiency

## 📚 Learning Paths

### 🌱 Beginner Path (60 minutes)

Perfect for first-time users. Learn TUI basics and web interface.

1. **[TUI Quick Start](tui-basics/01-quick-start.md)** (5 min)
   - Docker setup, API health check, basic commands
2. **[First Project](tui-basics/02-first-project.md)** (10 min)
   - Create project, understand projectDocs structure
3. **[Artifact Workflow](tui-basics/03-artifact-workflow.md)** (15 min)
   - Generate artifacts, propose/apply changes
4. **[RAID Management](tui-basics/04-raid-management.md)** (15 min)
   - Add risks, assumptions, issues, dependencies
5. **[Web Interface Basics](gui-basics/01-web-interface.md)** (5 min)
   - Navigate web UI, understand components
6. **[GUI Project Creation](gui-basics/02-project-creation.md)** (10 min)
   - Create projects via web form

**Total: 60 minutes** | **What You'll Build**: A Todo Application project with RAID entries and artifacts

### 🚀 Intermediate Path (110 minutes)

Build on basics with workflow management and full lifecycle.

1. **Complete Beginner Path** (60 min)
2. **[Full Lifecycle TUI](tui-basics/05-full-lifecycle.md)** (30 min)
   - Navigate all 5 ISO 21500 phases
   - Produce 10+ different artifacts
3. **[RAID Entry Management GUI](gui-basics/03-raid-entry-management.md)** (10 min)
   - Add/edit/view RAID entries via web UI
4. **[Proposal Workflow GUI](gui-basics/04-proposal-workflow.md)** (10 min)
   - Review diffs, apply changes, manage state

**Total: 110 minutes** | **What You'll Learn**: Complete ISO 21500 lifecycle, state management, GUI workflows

### 🎯 Advanced Path (220 minutes)

Master hybrid workflows, automation, and complete ISO 21500 implementation.

1. **Complete Intermediate Path** (110 min)
2. **[TUI + GUI Hybrid Workflows](advanced/01-tui-gui-hybrid.md)** (20 min)
   - Decision matrix for TUI vs GUI
   - Hybrid workflow patterns
   - When to use which interface
3. **[Complete ISO 21500 Lifecycle](advanced/02-complete-iso21500.md)** (60 min)
   - 9-week Todo App project
   - All 5 phases: Initiating → Planning → Executing → Monitoring → Closing
   - 19 artifacts generated
   - Full compliance tracking
4. **[Automation & Scripting](advanced/03-automation-scripting.md)** (30 min)
   - Bash scripts for batch operations
   - CI/CD integration examples
   - External tool integration (JIRA, Slack)

**Total: 220 minutes (3.7 hours)** | **What You'll Master**: Complete project lifecycle, automation, hybrid workflows

## 📖 Tutorial Catalog

### TUI Basics (5 tutorials, 75 minutes)

| Tutorial | Duration | Difficulty | Topics |
|----------|----------|------------|--------|
| [01. TUI Quick Start](tui-basics/01-quick-start.md) | 5 min | Beginner | Docker, API health, TUI basics |
| [02. First Project](tui-basics/02-first-project.md) | 10 min | Beginner | Project creation, Git structure |
| [03. Artifact Workflow](tui-basics/03-artifact-workflow.md) | 15 min | Beginner | Generate artifacts, propose/apply |
| [04. RAID Management](tui-basics/04-raid-management.md) | 15 min | Beginner | Risk, Assumption, Issue, Dependency |
| [05. Full Lifecycle](tui-basics/05-full-lifecycle.md) | 30 min | Intermediate | All 5 ISO phases, 10+ artifacts |

### GUI Basics (5 tutorials, 50 minutes)

| Tutorial | Duration | Difficulty | Topics |
|----------|----------|------------|--------|
| [01. Web Interface Basics](gui-basics/01-web-interface.md) | 5 min | Beginner | UI navigation, components |
| [02. Project Creation GUI](gui-basics/02-project-creation.md) | 10 min | Beginner | Web forms, validation |
| [03. RAID Entry Management](gui-basics/03-raid-entry-management.md) | 10 min | Beginner | Add/edit RAID via GUI |
| [04. Proposal Workflow GUI](gui-basics/04-proposal-workflow.md) | 10 min | Intermediate | Review diffs, apply changes |
| [05. Workflow States GUI](gui-basics/05-workflow-states.md) | 15 min | Intermediate | State transitions, navigation |

### Advanced Workflows (3 tutorials, 110 minutes)

| Tutorial | Duration | Difficulty | Topics |
|----------|----------|------------|--------|
| [01. TUI + GUI Hybrid](advanced/01-tui-gui-hybrid.md) | 20 min | Advanced | Interface selection, hybrid patterns |
| [02. Complete ISO 21500](advanced/02-complete-iso21500.md) | 60 min | Advanced | Full lifecycle, 9-week project |
| [03. Automation & Scripting](advanced/03-automation-scripting.md) | 30 min | Advanced | Bash scripts, CI/CD, integrations |

## 🛠️ Prerequisites

Before starting any tutorial, complete the [Setup Guide](shared/00-setup-guide.md) to install and verify:

- Docker 28+ and Docker Compose
- Git 2.23+
- Web browser (Chrome/Firefox/Safari)
- Terminal (bash/zsh/PowerShell)

**Quick Setup:**

```bash
# Clone repository
git clone https://github.com/blecx/AI-Agent-Framework.git
cd AI-Agent-Framework

# Start services
docker compose up -d

# Verify health
curl http://localhost:8000/health
# Expected: {"status":"healthy",...}

# Open web UI
open http://localhost:8080
```

## 🎓 Skill Progression Matrix

| Skill | Beginner | Intermediate | Advanced |
|-------|----------|--------------|----------|
| **Project Creation** | TUI/GUI basics | Template selection | Scripted batch creation |
| **RAID Management** | Add single entries | Manage full register | Automated gap detection |
| **Artifact Generation** | Single artifacts | Lifecycle sequence | AI-assisted generation |
| **Workflow States** | View current state | Navigate transitions | Automate state changes |
| **Interface Usage** | TUI or GUI only | TUI + GUI awareness | Hybrid workflows |
| **Automation** | Manual commands | Simple scripts | CI/CD integration |

## 📊 Success Stories

### Use Case 1: Compliance Officer

**Need**: Generate ISO 21500-compliant artifacts for audit
**Path**: Beginner → Intermediate
**Result**: 10+ artifacts generated in 30 minutes (vs. 2+ days manual)

### Use Case 2: Project Manager

**Need**: Track risks across 5 projects
**Path**: Beginner → Advanced (RAID focus)
**Result**: Centralized RAID register, automated gap detection

### Use Case 3: DevOps Engineer

**Need**: Integrate project management into CI/CD pipeline
**Path**: Advanced (Automation)
**Result**: Automated artifact generation on git push

## 🚦 Getting Started

**New to ISO 21500?** Start with [TUI Quick Start](tui-basics/01-quick-start.md) (5 min)

**Prefer visual interfaces?** Start with [Web Interface Basics](gui-basics/01-web-interface.md) (5 min)

**Want the complete experience?** Follow the [Beginner Path](#-beginner-path-60-minutes)

## 📋 Tutorial Conventions

All tutorials follow consistent patterns:

- **Example Project**: Todo Application (simple, relatable)
- **Time Estimates**: Approximate, assuming prerequisites met
- **Commands**: Copy-pasteable, tested in Docker environment
- **Expected Outputs**: JSON/HTML snippets show correct results
- **Troubleshooting**: Common issues and solutions included

### Todo Application

Our example project tracks a simple Todo application with these features:

- User authentication
- Task CRUD operations
- Task categorization
- Due date tracking
- Email notifications

This provides a realistic context for learning ISO 21500 concepts.

## 🆘 Getting Help

### Troubleshooting

Stuck? Check the [Troubleshooting Guide](shared/troubleshooting.md) for:

- Docker issues (ports, volumes, networking)
- API connection problems
- TUI command failures
- GUI not loading
- Git conflicts in projectDocs

### Community Support

- **GitHub Issues**: [Report bugs or ask questions](https://github.com/blecx/AI-Agent-Framework/issues)
- **API Documentation**: [http://localhost:8000/docs](http://localhost:8000/docs) (when services running)
- **Development Guide**: [docs/development.md](../development.md)

## ✅ Validation

All tutorials are validated with automated tests. See [Validation Report](VALIDATION-REPORT.md) for test results.

**Run validation yourself:**

```bash
# Full tutorial validation
./docs/tutorials/validation/test-runner.sh

# Individual tutorial
pytest tests/e2e/tutorial/test_tui_basics.py::test_tutorial_01 -v
```

## 📦 What's Next?

After completing tutorials:

1. **Build Your Own Project**: Apply learnings to real projects
2. **Explore API**: [http://localhost:8000/docs](http://localhost:8000/docs)
3. **Contribute**: [docs/CONTRIBUTING.md](../CONTRIBUTING.md)
4. **Read Specs**: [docs/spec/](../spec/) for detailed requirements

## 🔄 Tutorial Updates

**Last Updated**: 2024-01-15
**Version**: 1.0.0
**Status**: Complete (13 tutorials)

Tutorials are maintained alongside codebase. If you find outdated content:

1. Check latest commit date
2. Verify against current API version
3. Report issue with "tutorial" label

## 📚 Additional Resources

### Documentation

- **[API Reference](../api/)**: Complete endpoint documentation
- **[Architecture](../architecture/)**: System design and ADRs
- **[Development Guide](../development.md)**: Setup for contributors
- **[Deployment Guide](../deployment/)**: Production deployment

### External Resources

- **[ISO 21500:2021](https://www.iso.org/standard/74947.html)**: Official standard
- **[Project Management Body of Knowledge](https://www.pmi.org/pmbok-guide-standards)**: PMI guidelines
- **[FastAPI Documentation](https://fastapi.tiangolo.com/)**: Backend framework
- **[React Documentation](https://react.dev/)**: Frontend framework

## 🎉 Happy Learning!

These tutorials are designed to get you productive quickly while teaching best practices. Start with the Beginner Path and progress at your own pace.

Questions? Open an issue or reach out to maintainers.
