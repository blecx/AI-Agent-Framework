#!/bin/bash
# Intelligent Setup Script for ISO 21500 AI-Agent Framework
# Detects available Python versions, prompts user to select, and creates virtual environment

set -e  # Exit on error

echo "========================================="
echo "ISO 21500 AI-Agent Framework Setup"
echo "========================================="
echo ""

REQUIRED_PYTHON="python3.12"

echo "🔍 Detecting Python 3.12..."
echo ""
if ! command -v "$REQUIRED_PYTHON" &> /dev/null; then
    echo "❌ Error: Python 3.12 is required but was not found on PATH."
    echo ""
    echo "Install Python 3.12 and try again:"
    echo "  • Ubuntu/Debian: sudo apt install python3.12 python3.12-venv"
    echo "  • Fedora/RHEL:   sudo dnf install python3.12"
    echo "  • macOS:         brew install python@3.12"
    echo ""
    exit 1
fi

SELECTED_PYTHON="$(command -v "$REQUIRED_PYTHON")"
SELECTED_VERSION=$("$REQUIRED_PYTHON" --version 2>&1 | awk '{print $2}')

echo ""
echo "✅ Selected: Python $SELECTED_VERSION"
echo "   Path: $SELECTED_PYTHON"
echo ""

# Check if .venv already exists
if [ -d ".venv" ]; then
    echo "⚠️  Warning: .venv directory already exists."
    read -p "Remove existing .venv and recreate? [y/N]: " recreate
    recreate=${recreate:-N}
    
    if [[ "$recreate" =~ ^[Yy]$ ]]; then
        echo "Removing existing .venv..."
        rm -rf .venv
    else
        echo "Setup cancelled. Remove .venv manually if you want to recreate it."
        exit 0
    fi
fi

# Create virtual environment
echo "Creating virtual environment in .venv/ ..."
"$SELECTED_PYTHON" -m venv .venv

# Activate virtual environment
echo "Activating virtual environment..."
source .venv/bin/activate

# Verify activation
echo "Using Python: $(which python)"
echo "Python version: $(python --version)"
echo ""

# Upgrade pip
echo "Upgrading pip..."
pip install --upgrade pip --quiet

# Install dependencies
echo ""
echo "Installing dependencies from requirements.txt..."
echo "(This may take a few minutes...)"
pip install -r requirements.txt --quiet

# Success message
echo ""
echo "========================================="
echo "✅ Setup completed successfully!"
echo "========================================="
echo ""
echo "Virtual environment created with Python $SELECTED_VERSION"
echo ""
echo "Next steps:"
echo ""
echo "  1. Activate the virtual environment:"
echo "     source .venv/bin/activate"
echo ""
echo "  2. Create the projectDocs directory (if not exists):"
echo "     (created automatically by this setup script and Docker)"
# Ensure projectDocs exists so Docker and local runs work without manual steps
if [ ! -d "projectDocs" ]; then
    echo "Creating projectDocs directory..."
    mkdir -p projectDocs
    echo "Created projectDocs/"
fi
echo ""
echo "  3. Configure LLM settings (optional):"
echo "     cp configs/llm.default.json configs/llm.json"
echo "     # Then edit configs/llm.json with your LLM endpoint"
echo ""
echo "  4. Run the API server:"
echo "     cd apps/api"
echo "     PROJECT_DOCS_PATH=../../projectDocs uvicorn main:app --reload"
echo ""
echo "  5. Access the API at:"
echo "     • API: http://localhost:8000"
echo "     • Interactive docs: http://localhost:8000/docs"
echo ""
echo "For Docker deployment, see QUICKSTART.md"
echo ""
