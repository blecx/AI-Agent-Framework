# Development Guide

Complete guide for local development of the ISO 21500 AI-Agent Framework.

---

## Table of Contents

1. [Development Environment Setup](#development-environment-setup)
2. [Project Structure](#project-structure)
3. [Running the Application](#running-the-application)
4. [Development Workflow](#development-workflow)
5. [Adding Dependencies](#adding-dependencies)
6. [Testing](#testing)
7. [Docker Integration](#docker-integration)
8. [Troubleshooting](#troubleshooting)

---

## Development Environment Setup

### Prerequisites

- **Python 3.10+** (Python 3.12 recommended)
- **Git**
- **Node.js 18+** (for web UI development)
- **Docker & Docker Compose** (optional, for containerized development)
- **IDE** (VS Code, PyCharm, or your preferred editor)

### Initial Setup

1. **Clone the repository:**
   ```bash
   git clone https://github.com/blecx/AI-Agent-Framework.git
   cd AI-Agent-Framework
   ```

2. **Create Python virtual environment using the intelligent setup script:**

   **Using the setup script (recommended):**
   
   The intelligent setup script detects all available Python versions on your system and helps you choose the best one.
   
   **Linux/macOS:**
   ```bash
   ./setup.sh
   ```
   
   **Windows (PowerShell - Recommended):**
   ```powershell
   .\setup.ps1
   ```
   
   **Windows (Command Prompt):**
   ```cmd
   setup.bat
   ```
   
   **How the setup script works:**
   
   1. **Detection Phase:**
      - Scans your system for all Python 3.x installations
      - Checks versions using `python3.X`, `python3`, `python`, and `py -X.Y` commands
      - Filters out versions below Python 3.10 (minimum requirement)
   
   2. **Selection Phase:**
      - Displays a numbered list of compatible Python versions with full paths
      - If multiple versions found: prompts you to select one
      - If only one version found: asks for confirmation to use it
      - If no compatible version found: displays download links and exits
   
   3. **Validation Phase:**
      - Validates selected version meets minimum requirements (Python 3.10+)
      - Checks if `.venv/` already exists and prompts to recreate if needed
   
   4. **Setup Phase:**
      - Creates virtual environment: `python-X.Y -m venv .venv`
      - Activates the environment
      - Upgrades pip: `pip install --upgrade pip`
      - Installs all dependencies: `pip install -r requirements.txt`
      - Shows success message with next steps
   
   **Manual setup (alternative):**
   
   If you prefer to set up manually or the script doesn't work for your system:
   
   ```bash
   # Check your Python version (must be 3.10+)
   python3 --version
   
   # Create virtual environment with specific version
   python3 -m venv .venv          # Uses default python3
   # OR
   python3.12 -m venv .venv       # Uses specific version
   
   # Activate the environment
   source .venv/bin/activate      # Linux/macOS
   # OR
   .venv\Scripts\activate.bat     # Windows (Command Prompt)
   # OR
   .\.venv\Scripts\Activate.ps1   # Windows (PowerShell)
   
   # Upgrade pip and install dependencies
   pip install --upgrade pip
   pip install -r requirements.txt
   ```

3. **Create project documents directory:**
   ```bash
   mkdir -p projectDocs
   ```

4. **Configure LLM (optional):**
   ```bash
   cp configs/llm.default.json configs/llm.json
   # Edit configs/llm.json with your settings
   ```

---

## Project Structure

```
AI-Agent-Framework/
├── .venv/                      # Python virtual environment (created by setup)
├── apps/
│   ├── api/                    # FastAPI backend
│   │   ├── main.py            # Application entry point
│   │   ├── models.py          # Pydantic data models
│   │   ├── requirements.txt   # Docker-specific dependencies
│   │   ├── services/          # Core business logic
│   │   │   ├── __init__.py
│   │   │   ├── command_service.py  # Command orchestration
│   │   │   ├── git_manager.py      # Git operations
│   │   │   └── llm_service.py      # LLM integration
│   │   └── routers/           # API endpoints
│   │       ├── __init__.py
│   │       ├── artifacts.py   # Artifact endpoints
│   │       ├── commands.py    # Command endpoints
│   │       └── projects.py    # Project endpoints
│   └── web/                   # React/Vite frontend
│       ├── src/
│       │   ├── components/    # React components
│       │   └── services/      # API client services
│       ├── package.json
│       └── vite.config.js
├── configs/
│   ├── llm.default.json       # Default LLM configuration
│   └── llm.json              # User-specific LLM config (gitignored)
├── docker/
│   ├── api/
│   │   └── Dockerfile        # API container definition
│   └── web/
│       ├── Dockerfile        # Web container definition
│       └── nginx.conf        # Nginx configuration
├── docs/                      # Documentation
│   ├── README.md             # Documentation index
│   ├── adr/                  # Architecture Decision Records
│   ├── chat/                 # Development transcripts
│   ├── howto/                # How-to guides
│   └── spec/                 # Specifications
├── projectDocs/              # Generated project documents (gitignored)
├── templates/
│   ├── prompts/iso21500/     # Jinja2 LLM prompt templates
│   └── output/iso21500/      # Markdown output templates
├── .gitignore                # Git ignore rules
├── docker-compose.yml        # Docker orchestration
├── requirements.txt          # Python dependencies (for local dev)
├── setup.sh                  # Setup script for Linux/macOS
├── setup.bat                 # Setup script for Windows
├── README.md                 # Project overview
└── QUICKSTART.md            # Quick start guide
```

### Key Directories

- **`.venv/`**: Python virtual environment (excluded from git)
- **`apps/api/`**: Backend FastAPI application
- **`apps/web/`**: Frontend React application
- **`projectDocs/`**: Separate git repository for project documents (excluded from git)
- **`templates/`**: Jinja2 templates for prompts and outputs
- **`configs/`**: Configuration files (llm.json is gitignored)
- **`docs/`**: Project documentation

---

## Running the Application

### Backend (FastAPI API)

1. **Activate virtual environment:**
   ```bash
   source .venv/bin/activate  # Linux/macOS
   # or
   .venv\Scripts\activate.bat  # Windows
   ```

2. **Run the API server:**
   ```bash
   cd apps/api
   PROJECT_DOCS_PATH=../../projectDocs uvicorn main:app --reload
   ```

3. **Access the API:**
   - API: http://localhost:8000
   - Interactive docs: http://localhost:8000/docs
   - Alternative docs: http://localhost:8000/redoc

### Frontend (React Web UI)

1. **Install dependencies:**
   ```bash
   cd apps/web
   npm install
   ```

2. **Run the development server:**
   ```bash
   npm run dev
   ```

3. **Access the UI:**
   - Web UI: http://localhost:5173 (or the port shown in terminal)

### Using Docker

For a complete containerized setup:

```bash
docker compose up --build
```

Access points:
- Web UI: http://localhost:8080
- API: http://localhost:8000
- API Docs: http://localhost:8000/docs

---

## Development Workflow

### Standard Workflow: Plan → Issues → PRs

**ALWAYS follow this workflow for features, bug fixes, and cross-repo changes:**

See **[../.github/copilot-instructions.md](../.github/copilot-instructions.md)** for complete guidance and **[../.github/prompts/](../.github/prompts/)** for templates.

#### 1. Planning Phase
- Start with a clear specification (goal, scope, acceptance criteria, constraints)
- Consider impact on [AI-Agent-Framework-Client](https://github.com/blecx/AI-Agent-Framework-Client)
- Use [planning template](../.github/prompts/planning-feature.md) to structure your plan
- Break work into small issues (< 200 lines changed per PR)

#### 2. Issue Creation
- Create focused issues using [issue template](../.github/prompts/drafting-issue.md)
- Include specific acceptance criteria and validation steps
- Link related issues across repositories for cross-repo work
- One issue = one PR

#### 3. Implementation
- Create feature branch from `main`
- Make minimal, focused changes
- Follow existing code patterns and conventions
- Never commit `projectDocs/` or `configs/llm.json`

#### 4. Validation (Before PR)
Run these validation steps locally:

```bash
# Activate environment
source .venv/bin/activate

# Lint code (optional but recommended)
python -m black apps/api/
python -m flake8 apps/api/

# Test API
cd apps/api
PROJECT_DOCS_PATH=../../projectDocs uvicorn main:app --reload
# In another terminal:
curl http://localhost:8000/health

# Test frontend (if changed)
cd apps/web
npm run lint
npm run build

# Verify git status
git status  # Ensure no unwanted files staged
```

#### 5. Pull Request
- Use [PR template](../.github/prompts/drafting-pr.md) for description
- Include copy-pasteable validation steps for reviewers
- Reference issue with "Fixes #123" or "Closes #123"
- Keep PR size small (prefer < 200 lines)
- Add screenshots for UI changes

#### 6. Review & Merge
- Address review feedback
- Squash merge preferred (keeps history clean)
- Delete branch after merge

### Cross-Repository Coordination

When changes span backend and frontend:
- Use [cross-repo coordination template](../.github/prompts/cross-repo-coordination.md)
- Document API contract explicitly
- Create issues in both repos with cross-references
- Plan implementation order (usually backend first)
- Test integration before final merge

### Making Code Changes

1. **Activate virtual environment:**
   ```bash
   source .venv/bin/activate
   ```

2. **Make your changes** in the appropriate files

3. **Test locally:**
   ```bash
   cd apps/api
   PROJECT_DOCS_PATH=../../projectDocs uvicorn main:app --reload
   ```

4. **Verify changes** via API docs or web UI

### Hot Reload

The development servers support hot reload:
- **Backend**: `uvicorn` with `--reload` flag automatically reloads on code changes
- **Frontend**: Vite dev server automatically reloads on file changes

### Directory Structure Best Practices

- **Backend logic**: Add new services to `apps/api/services/`
- **API endpoints**: Add new routers to `apps/api/routers/`
- **Data models**: Define in `apps/api/models.py`
- **Templates**: Add Jinja2 templates to `templates/`
- **Documentation**: Add to `docs/` with appropriate subdirectory

---

## Adding Dependencies

### Python Dependencies

1. **Add to `requirements.txt`** with a pinned version:
   ```
   new-package==1.2.3
   ```

2. **Install in virtual environment:**
   ```bash
   source .venv/bin/activate
   pip install -r requirements.txt
   ```

3. **Update Docker dependencies** if needed:
   - Add to `apps/api/requirements.txt` for Docker builds
   - Rebuild Docker images:
     ```bash
     docker compose build --no-cache api
     ```

### JavaScript Dependencies

1. **Add to frontend:**
   ```bash
   cd apps/web
   npm install package-name
   ```

2. **Commit `package.json` and `package-lock.json`**

### Keeping Dependencies in Sync

The project maintains two Python requirements files:

- **`requirements.txt`** (root): For local development with `.venv` - includes all dependencies plus testing and dev tools
- **`apps/api/requirements.txt`**: For Docker builds - includes only runtime dependencies

**Key Differences:**
- Root `requirements.txt` includes: pytest, pytest-asyncio, black, flake8 (for local development)
- Docker `apps/api/requirements.txt` includes: only runtime dependencies (smaller image size)

**Best Practice:** When adding a new runtime dependency:
1. Add it to both `requirements.txt` and `apps/api/requirements.txt`
2. When adding a dev-only dependency (like a linter), add it only to root `requirements.txt`

### Understanding the Setup Script vs Docker

**Setup Script (`.venv`):**
- Used for **local development**
- Detects and uses Python versions installed on your system
- Creates virtual environment in project root
- Fast iteration and debugging
- Direct access to code and dependencies

**Docker:**
- Used for **production deployment** and team consistency
- Uses Python version specified in Dockerfile (currently 3.12)
- Self-contained environment with its own Python installation
- Isolated from system Python
- Reads dependencies from `apps/api/requirements.txt`

**Key Differences:**

| Aspect | Setup Script (.venv) | Docker |
|--------|---------------------|--------|
| Python Version | Detected from system | Fixed in Dockerfile |
| Dependencies File | `requirements.txt` | `apps/api/requirements.txt` |
| Setup Time | Fast (uses system Python) | Slower (builds image) |
| Isolation | Process-level | Container-level |
| Best For | Development, debugging | Production, testing |

**Workflow Integration:**

```bash
# Development workflow with .venv
./setup.sh                          # One-time setup
source .venv/bin/activate           # Each session
cd apps/api
PROJECT_DOCS_PATH=../../projectDocs uvicorn main:app --reload

# Production workflow with Docker
docker compose up --build           # Builds and runs
docker compose logs -f api          # View logs
```

Both setups use the same codebase and can access the same `projectDocs/` directory, so you can easily switch between them.

---

## Testing

### Manual Testing

1. **Start the API:**
   ```bash
   cd apps/api
   PROJECT_DOCS_PATH=../../projectDocs uvicorn main:app --reload
   ```

2. **Test via interactive API docs:**
   - Open http://localhost:8000/docs
   - Test endpoints directly in the Swagger UI

3. **Test via Web UI:**
   - Start the web dev server
   - Create a test project
   - Run commands and verify outputs

### Testing with pytest

Currently, there's no automated test suite, but the framework is ready for pytest:

```bash
# Install test dependencies (already in requirements.txt)
pip install pytest pytest-asyncio

# Run tests (when implemented)
pytest
```

### Testing the Setup Scripts

**Test scenarios to verify:**

1. **Single Python version installed:**
   ```bash
   # Script should auto-detect and ask for confirmation
   ./setup.sh
   # Expected: Shows 1 version, asks "Use this version? [Y/n]:"
   ```

2. **Multiple Python versions installed:**
   ```bash
   # Script should list all versions and prompt for selection
   ./setup.sh
   # Expected: Shows numbered list, asks "Select Python version [1-N]:"
   ```

3. **Existing .venv directory:**
   ```bash
   # Script should detect and ask to recreate
   ./setup.sh
   # Expected: Shows warning, asks "Remove existing .venv and recreate? [y/N]:"
   ```

4. **No compatible Python version:**
   ```bash
   # Script should show error and download links
   # (Can only test this on a system without Python 3.10+)
   ```

### Testing LLM Integration

1. **Without LLM** (template fallback):
   - Remove or don't configure `configs/llm.json`
   - System will use template-based generation

2. **With LM Studio:**
   - Start LM Studio and load a model
   - Start the local server (port 1234)
   - Configure `configs/llm.json`:
     ```json
     {
       "provider": "lmstudio",
       "base_url": "http://localhost:1234/v1",
       "api_key": "lm-studio",
       "model": "local-model"
     }
     ```

3. **With OpenAI:**
   - Configure `configs/llm.json`:
     ```json
     {
       "provider": "openai",
       "base_url": "https://api.openai.com/v1",
       "api_key": "your-api-key",
       "model": "gpt-4"
     }
     ```

---

## Docker Integration

### How `.venv` and Docker Work Together

The project supports both local development and Docker deployment:

- **Local development** uses `.venv/` with `requirements.txt`
- **Docker** uses `apps/api/requirements.txt` and builds its own environment

### Building Docker Images

```bash
# Build all services
docker compose build

# Build without cache
docker compose build --no-cache

# Build specific service
docker compose build api
```

### Running Containers

```bash
# Start all services
docker compose up

# Start in detached mode
docker compose up -d

# View logs
docker compose logs -f api
docker compose logs -f web

# Stop services
docker compose down
```

### Switching Between Local and Docker

**To Local Development:**
```bash
docker compose down
source .venv/bin/activate
cd apps/api
PROJECT_DOCS_PATH=../../projectDocs uvicorn main:app --reload
```

**To Docker:**
```bash
deactivate  # Exit virtual environment
docker compose up --build
```

---

## Troubleshooting

### Setup Script Issues

**Problem:** Script says "No compatible Python version found"
- **Solution:** Install Python 3.10 or higher:
  - Ubuntu/Debian: `sudo apt install python3.12`
  - macOS (Homebrew): `brew install python@3.12`
  - Windows: Download from https://www.python.org/downloads/
  - Ensure "Add Python to PATH" is checked during Windows installation

**Problem:** Setup script doesn't detect my Python installation
- **Solution:** Check your Python is accessible:
  ```bash
  python3 --version     # Should show Python 3.x
  which python3         # Should show path to Python
  ```
  If not found, add Python to your PATH or use manual setup

**Problem:** Script fails with "python3 -m venv .venv" error
- **Solution:** Install python3-venv package:
  ```bash
  # Ubuntu/Debian
  sudo apt install python3.12-venv
  
  # Fedora/RHEL
  sudo dnf install python3-virtualenv
  ```

**Problem:** "Permission denied" when running setup script
- **Solution:** Make the script executable:
  ```bash
  chmod +x setup.sh
  ./setup.sh
  ```

**Problem:** PowerShell script execution is disabled (Windows)
- **Solution:** Enable script execution:
  ```powershell
  Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
  .\setup.ps1
  ```

**Problem:** Script creates .venv but pip install fails
- **Solution:** 
  1. Delete .venv: `rm -rf .venv` (or `rmdir /s .venv` on Windows)
  2. Ensure you have internet connection
  3. Try manual setup with `pip install --no-cache-dir -r requirements.txt`

### Virtual Environment Issues

**Problem:** `python3: command not found`
- **Solution:** Install Python 3.10+ and ensure it's in PATH

**Problem:** `pip install` fails
- **Solution:** Upgrade pip: `pip install --upgrade pip`

**Problem:** Dependencies conflict
- **Solution:** Remove `.venv/` and recreate:
  ```bash
  rm -rf .venv
  ./setup.sh
  ```

### API Issues

**Problem:** `PROJECT_DOCS_PATH not set` error
- **Solution:** Set the environment variable:
  ```bash
  export PROJECT_DOCS_PATH=/path/to/projectDocs  # Linux/macOS
  set PROJECT_DOCS_PATH=C:\path\to\projectDocs   # Windows
  ```

**Problem:** Git operations fail
- **Solution:** Ensure git is installed and configured:
  ```bash
  git config --global user.email "you@example.com"
  git config --global user.name "Your Name"
  ```

**Problem:** LLM connection fails
- **Solution:** 
  - Check LLM server is running
  - Verify `configs/llm.json` configuration
  - System will fall back to templates if LLM is unavailable

### Docker Issues

**Problem:** Port already in use
- **Solution:** Stop conflicting services or change ports in `docker-compose.yml`

**Problem:** Volume mount fails
- **Solution:** Ensure `projectDocs/` directory exists:
  ```bash
  mkdir -p projectDocs
  ```

**Problem:** Build fails with SSL errors
- **Solution:** The Dockerfile includes trusted host flags. Try building with no cache:
  ```bash
  docker compose build --no-cache
  ```

### Frontend Issues

**Problem:** `npm install` fails
- **Solution:** Clear npm cache and retry:
  ```bash
  npm cache clean --force
  rm -rf node_modules package-lock.json
  npm install
  ```

**Problem:** API connection fails
- **Solution:** Check the API base URL in frontend code (should point to `http://localhost:8000`)

---

## IDE Configuration

### VS Code

Recommended extensions:
- Python
- Pylance
- Docker
- ES7+ React/Redux/React-Native snippets

**Settings for Python:**
```json
{
  "python.defaultInterpreterPath": "${workspaceFolder}/.venv/bin/python",
  "python.linting.enabled": true,
  "python.linting.pylintEnabled": false,
  "python.linting.flake8Enabled": true,
  "python.formatting.provider": "black"
}
```

### PyCharm

1. Set Python interpreter to `.venv/bin/python`
2. Mark `apps/api` as sources root
3. Enable FastAPI support in settings

---

## Additional Resources

- [README.md](../README.md) - Project overview
- [QUICKSTART.md](../QUICKSTART.md) - Quick start guide
- [docs/README.md](README.md) - Documentation index
- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [React Documentation](https://react.dev/)
- [Docker Documentation](https://docs.docker.com/)

---

**Last Updated:** 2026-01-09  
**Maintained By:** Development Team  
**Status:** Active
