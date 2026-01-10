#!/bin/bash
# Intelligent Setup Script for ISO 21500 AI-Agent Framework
# Detects available Python versions, prompts user to select, and creates virtual environment

set -e  # Exit on error

echo "========================================="
echo "ISO 21500 AI-Agent Framework Setup"
echo "========================================="
echo ""

# Minimum required Python version
MIN_PYTHON_MAJOR=3
MIN_PYTHON_MINOR=10

# Function to compare version numbers
version_compare() {
    local version=$1
    local major minor
    IFS='.' read -r major minor <<< "$version"
    
    if [ "$major" -gt "$MIN_PYTHON_MAJOR" ]; then
        return 0
    elif [ "$major" -eq "$MIN_PYTHON_MAJOR" ] && [ "$minor" -ge "$MIN_PYTHON_MINOR" ]; then
        return 0
    else
        return 1
    fi
}

# Detect available Python versions
echo "🔍 Detecting available Python versions..."
echo ""

declare -a PYTHON_VERSIONS
declare -a PYTHON_PATHS
declare -a PYTHON_FULL_VERSIONS

# Check for python3.X versions (3.10 through 3.15 - realistic range)
for ver in {10..15}; do
    cmd="python3.$ver"
    if command -v "$cmd" &> /dev/null; then
        full_version=$("$cmd" --version 2>&1 | awk '{print $2}')
        short_version=$(echo "$full_version" | cut -d. -f1,2)
        
        if version_compare "$short_version"; then
            PYTHON_VERSIONS+=("$short_version")
            PYTHON_PATHS+=("$(command -v "$cmd")")
            PYTHON_FULL_VERSIONS+=("$full_version")
        fi
    fi
done

# Check generic python3
if command -v python3 &> /dev/null; then
    full_version=$(python3 --version 2>&1 | awk '{print $2}')
    short_version=$(echo "$full_version" | cut -d. -f1,2)
    path=$(command -v python3)
    
    # Add if not already in list and meets requirements
    if version_compare "$short_version"; then
        # Check if this path is already in the list
        found=0
        for existing_path in "${PYTHON_PATHS[@]}"; do
            if [ "$existing_path" = "$path" ]; then
                found=1
                break
            fi
        done
        
        if [ $found -eq 0 ]; then
            PYTHON_VERSIONS+=("$short_version")
            PYTHON_PATHS+=("$path")
            PYTHON_FULL_VERSIONS+=("$full_version")
        fi
    fi
fi

# Check if any compatible Python versions were found
if [ ${#PYTHON_VERSIONS[@]} -eq 0 ]; then
    echo "❌ Error: No compatible Python version found!"
    echo ""
    echo "This project requires Python $MIN_PYTHON_MAJOR.$MIN_PYTHON_MINOR or higher."
    echo ""
    echo "📥 Download Python from:"
    echo "  - https://www.python.org/downloads/"
    echo "  - Or use your system package manager:"
    echo "    • Ubuntu/Debian: sudo apt install python3.12"
    echo "    • macOS (Homebrew): brew install python@3.12"
    echo "    • Fedora/RHEL: sudo dnf install python3.12"
    echo ""
    exit 1
fi

# Display found Python versions
echo "✅ Found ${#PYTHON_VERSIONS[@]} compatible Python version(s):"
echo ""
for i in "${!PYTHON_VERSIONS[@]}"; do
    echo "  [$((i+1))] Python ${PYTHON_FULL_VERSIONS[$i]}"
    echo "      Path: ${PYTHON_PATHS[$i]}"
    echo ""
done

# Select Python version
SELECTED_INDEX=-1

if [ ${#PYTHON_VERSIONS[@]} -eq 1 ]; then
    # Only one version found, ask for confirmation
    echo "Only one compatible version found: Python ${PYTHON_FULL_VERSIONS[0]}"
    read -p "Use this version? [Y/n]: " confirm
    confirm=${confirm:-Y}
    
    if [[ "$confirm" =~ ^[Yy]$ ]]; then
        SELECTED_INDEX=0
    else
        echo "Setup cancelled."
        exit 0
    fi
else
    # Multiple versions found, let user choose
    while true; do
        read -p "Select Python version [1-${#PYTHON_VERSIONS[@]}]: " selection
        
        if [[ "$selection" =~ ^[0-9]+$ ]] && [ "$selection" -ge 1 ] && [ "$selection" -le "${#PYTHON_VERSIONS[@]}" ]; then
            SELECTED_INDEX=$((selection-1))
            break
        else
            echo "Invalid selection. Please enter a number between 1 and ${#PYTHON_VERSIONS[@]}."
        fi
    done
fi

SELECTED_PYTHON="${PYTHON_PATHS[$SELECTED_INDEX]}"
SELECTED_VERSION="${PYTHON_FULL_VERSIONS[$SELECTED_INDEX]}"

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
