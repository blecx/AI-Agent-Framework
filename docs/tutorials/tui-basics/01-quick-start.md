# TUI Quick Start

**Duration:** 5 minutes | **Difficulty:** Beginner | **Interface:** Command-Line (TUI)

## Overview

Get started with the ISO 21500 AI-Agent Framework's Text User Interface (TUI). Learn how to start the system using Docker, verify it's running, and execute your first health check command.

## Learning Objectives

By the end of this tutorial, you will:
- Start the AI-Agent Framework using Docker Compose
- Verify the API and TUI are running correctly
- Execute basic TUI commands
- Understand the TUI command structure
- Check system health status

## Prerequisites

- **Docker 28+** and **Docker Compose** installed
- **Terminal** access (bash, zsh, or PowerShell)
- **Git** installed
- Basic command-line knowledge
- No prior ISO 21500 knowledge required

**Note:** If you haven't installed Docker yet, see the [Setup Guide](../shared/00-setup-guide.md).

## 🎥 Video Walkthrough

> **Coming Soon:** A video walkthrough of this tutorial will be available.
> 
> **What to expect:**
> - Live demonstration of all commands
> - Docker startup and verification
> - Common pitfalls and solutions
> - Tips for efficient TUI usage
> 
> **Interested in contributing?** See [VIDEO-PLAN.md](../VIDEO-PLAN.md) for recording guidelines.

## What is the TUI?

The TUI (Text User Interface) is a command-line client for the AI-Agent Framework. It provides:
- **Scriptable commands** for automation
- **Fast execution** without GUI overhead
- **Batch operations** for bulk tasks
- **CI/CD integration** capabilities
- **Remote access** via SSH

The TUI is perfect for:
- Developers who prefer command-line tools
- Automation scripts and CI/CD pipelines
- Bulk operations (creating multiple projects, batch RAID entries)
- Remote server management

## Setup

### Step 1: Clone the Repository (If Not Done)

```bash
# Clone the repository
git clone https://github.com/blecx/AI-Agent-Framework.git
cd AI-Agent-Framework
```

**Expected Output:**
```
Cloning into 'AI-Agent-Framework'...
remote: Enumerating objects: ...
```

✅ **Checkpoint:** You should now be in the `AI-Agent-Framework` directory.

### Step 2: Start Docker Services

Start the backend API and web services using Docker Compose:

```bash
docker compose up -d
```

**Expected Output:**
```
[+] Running 3/3
 ✔ Network ai-agent-framework_default    Created
 ✔ Container ai-agent-framework-api-1    Started
 ✔ Container ai-agent-framework-web-1    Started
```

**What's happening:**
- `-d` flag runs containers in detached mode (background)
- Two containers start: `api` (backend) and `web` (frontend)
- API runs on `http://localhost:8000`
- Web UI runs on `http://localhost:8080`

✅ **Checkpoint:** Containers should be running. Verify with `docker ps` (you should see 2 containers).

### Step 3: Wait for Services to Start

Give the services 10-15 seconds to fully initialize:

```bash
sleep 15
```

**Why wait?** The API needs time to:
- Initialize the FastAPI application
- Set up the Git repository for project documents
- Start the LLM service
- Configure CORS and middleware

## Using the TUI

### Understanding TUI Command Structure

The TUI follows a hierarchical command structure:

```
python apps/tui/main.py <group> <command> [options]
```

**Command groups:**
- `projects` - Project management (create, list, delete)
- `commands` - Command execution (propose, apply)
- `artifacts` - Artifact browsing and export
- `config` - Configuration management
- `health` - System health checks

**Example:**
```bash
python apps/tui/main.py projects list
#      ^^^^ TUI entry  ^^^^^^^ ^^^^^
#                      group   command
```

### Step 4: Run Your First Command (Health Check)

Test the TUI by checking the API health:

```bash
python apps/tui/main.py health
```

**Expected Output:**
```json
✅ API is healthy!

Health Status
{
  "status": "healthy",
  "docs_path": "/projectDocs",
  "timestamp": "2026-02-03T12:34:56.789Z",
  "version": "1.0.0"
}
```

✅ **Checkpoint:** If you see the green "✅ API is healthy!" message, the system is ready to use!

**Troubleshooting:**
- **Connection refused:** API may not be fully started yet. Wait 10 more seconds and retry.
- **Command not found:** Ensure you're in the correct directory (`AI-Agent-Framework`).
- **Python error:** Ensure Python 3.10+ is installed: `python --version`

### Step 5: Explore Available Commands

See all available TUI commands:

```bash
python apps/tui/main.py --help
```

**Expected Output:**
```
Usage: main.py [OPTIONS] COMMAND [ARGS]...

  ISO 21500 AI-Agent Framework - TUI Client

  A command-line interface for managing ISO 21500 projects via the AI Agent API.

Options:
  --version   Show the version and exit.
  --help      Show this message and exit.

Commands:
  artifacts  Artifact management commands
  config     Configuration management commands
  health     Check API health status.
  projects   Project management commands
  propose    Command proposal and execution
```

**Key commands you'll use:**
- `health` - Check system status
- `projects create` - Create new projects
- `projects list` - List all projects
- `propose propose` - Propose commands for execution
- `artifacts list` - Browse project artifacts

### Step 6: Get Help for Specific Commands

See detailed help for any command:

```bash
# Get help for projects command group
python apps/tui/main.py projects --help
```

**Expected Output:**
```
Usage: main.py projects [OPTIONS] COMMAND [ARGS]...

  Project management commands

Commands:
  create  Create a new project
  delete  Delete a project
  list    List all projects
  show    Show project details
  state   Get project state
```

```bash
# Get help for project creation
python apps/tui/main.py projects create --help
```

**Expected Output:**
```
Usage: main.py projects create [OPTIONS]

  Create a new project

Options:
  --key TEXT          Project key (e.g., PROJ001)  [required]
  --name TEXT         Project name  [required]
  --description TEXT  Project description
  --help              Show this message and exit.
```

## What You've Learned

Congratulations! You've completed the TUI Quick Start tutorial. You now know:

✅ How to start the AI-Agent Framework with Docker Compose  
✅ How to execute TUI commands from the terminal  
✅ The structure of TUI commands (`<group> <command> [options]`)  
✅ How to check API health status  
✅ How to get help for any command using `--help`  
✅ Which command groups are available (projects, commands, artifacts, config)

## Key Concepts Review

| Concept | Description |
|---------|-------------|
| **TUI** | Text User Interface - command-line client for automation |
| **Docker Compose** | Tool to run multi-container applications |
| **API** | Backend service running on port 8000 |
| **Command Groups** | Hierarchical organization (projects, commands, artifacts) |
| **Health Check** | Verifies API is running and accessible |

## Next Steps

Now that you have the TUI running, continue your learning journey:

1. **[Tutorial 02: First Project](02-first-project.md)** - Create your first ISO 21500 project (10 min)
2. **[Tutorial 03: Artifact Workflow](03-artifact-workflow.md)** - Learn the propose/apply pattern (15 min)
3. **[GUI Quick Start](../gui-basics/01-web-interface.md)** - Explore the web interface alternative (5 min)

**Recommended next:** Tutorial 02 - First Project

## Reference

### Environment Variables

The TUI supports these environment variables:

```bash
# Customize API endpoint (default: http://localhost:8000)
export API_BASE_URL=http://localhost:8000

# Customize request timeout (default: 30 seconds)
export API_TIMEOUT=60

# Optional API key for authentication
export API_KEY=your-api-key
```

**Example with custom settings:**
```bash
API_BASE_URL=http://api.example.com:8080 python apps/tui/main.py health
```

### Quick Command Reference

```bash
# Health check
python apps/tui/main.py health

# Get help
python apps/tui/main.py --help
python apps/tui/main.py projects --help
python apps/tui/main.py projects create --help

# Check Docker status
docker ps
docker compose logs api
docker compose logs web

# Stop services
docker compose down

# Restart services
docker compose restart
```

### Common Docker Commands

```bash
# View running containers
docker ps

# View logs
docker compose logs -f api    # Follow API logs
docker compose logs -f web    # Follow web logs

# Restart services
docker compose restart

# Stop services
docker compose down

# Stop and remove volumes (clean reset)
docker compose down -v

# Rebuild and restart
docker compose up -d --build
```

## Troubleshooting

### API Connection Issues

**Problem:** `Connection refused` or `Failed to connect`

**Solutions:**
1. Verify containers are running: `docker ps`
2. Check API logs: `docker compose logs api`
3. Wait longer (API may still be starting): `sleep 10 && python apps/tui/main.py health`
4. Restart services: `docker compose restart`

### Port Already in Use

**Problem:** `port is already allocated`

**Solutions:**
1. Find and kill the process using port 8000:
   ```bash
   # Linux/Mac
   lsof -i :8000
   kill -9 <PID>
   
   # Windows
   netstat -ano | findstr :8000
   taskkill /PID <PID> /F
   ```
2. Or change the port in `docker-compose.yml`

### Python Command Not Found

**Problem:** `python: command not found`

**Solutions:**
1. Use `python3` instead: `python3 apps/tui/main.py health`
2. Install Python: See [Setup Guide](../shared/00-setup-guide.md)
3. Verify Python version: `python --version` or `python3 --version`

### Docker Not Running

**Problem:** `Cannot connect to the Docker daemon`

**Solutions:**
1. Start Docker Desktop (Mac/Windows)
2. Start Docker service (Linux): `sudo systemctl start docker`
3. Verify Docker is running: `docker info`

## Additional Resources

- [Setup Guide](../shared/00-setup-guide.md) - Detailed installation instructions
- [Troubleshooting Guide](../shared/troubleshooting.md) - Complete troubleshooting reference
- [API Documentation](http://localhost:8000/docs) - Interactive API docs (when running)
- [GitHub Issues](https://github.com/blecx/AI-Agent-Framework/issues) - Report bugs or ask questions

## Success Checklist

Before moving to the next tutorial, ensure you can:

- [ ] Start Docker Compose successfully
- [ ] Execute `python apps/tui/main.py health` without errors
- [ ] See "API is healthy!" message
- [ ] Use `--help` to explore available commands
- [ ] Understand the command structure (`<group> <command>`)

If all checkboxes are complete, you're ready for [Tutorial 02: First Project](02-first-project.md)!

---

**Tutorial Series:** [TUI Basics](../README.md#tui-basics) | **Next:** [02 - First Project](02-first-project.md)
