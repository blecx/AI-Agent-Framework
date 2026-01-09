#!/bin/bash
# Setup script for ISO 21500 AI-Agent Framework
# Creates a Python virtual environment and installs dependencies

set -e  # Exit on error

echo "========================================="
echo "ISO 21500 AI-Agent Framework Setup"
echo "========================================="
echo ""

# Check if Python 3 is available
if ! command -v python3 &> /dev/null; then
    echo "Error: Python 3 is not installed or not in PATH"
    echo "Please install Python 3.10 or higher"
    exit 1
fi

# Check Python version
PYTHON_VERSION=$(python3 -c 'import sys; print(".".join(map(str, sys.version_info[:2])))')
echo "Found Python version: $PYTHON_VERSION"

# Create virtual environment
echo ""
echo "Creating virtual environment in .venv/ ..."
python3 -m venv .venv

# Activate virtual environment
echo "Activating virtual environment..."
source .venv/bin/activate

# Upgrade pip
echo ""
echo "Upgrading pip..."
pip install --upgrade pip

# Install dependencies
echo ""
echo "Installing dependencies from requirements.txt..."
pip install -r requirements.txt

# Success message
echo ""
echo "========================================="
echo "✅ Setup completed successfully!"
echo "========================================="
echo ""
echo "Next steps:"
echo "  1. Activate the virtual environment:"
echo "     source .venv/bin/activate"
echo ""
echo "  2. Create the projectDocs directory (if not exists):"
echo "     mkdir -p projectDocs"
echo ""
echo "  3. Configure LLM settings (optional):"
echo "     cp configs/llm.default.json configs/llm.json"
echo "     # Then edit configs/llm.json with your LLM endpoint"
echo ""
echo "  4. Run the API server:"
echo "     cd apps/api"
echo "     PROJECT_DOCS_PATH=../../projectDocs uvicorn main:app --reload --port 8000"
echo ""
echo "  5. Access the API at http://localhost:8000"
echo "     API docs at http://localhost:8000/docs"
echo ""
echo "For Docker deployment, see QUICKSTART.md"
echo ""
