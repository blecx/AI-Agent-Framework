# Intelligent Setup Script for ISO 21500 AI-Agent Framework (PowerShell)
# Detects available Python versions, prompts user to select, and creates virtual environment

# Stop on errors
$ErrorActionPreference = "Stop"

Write-Host "=========================================" -ForegroundColor Cyan
Write-Host "ISO 21500 AI-Agent Framework Setup" -ForegroundColor Cyan
Write-Host "=========================================" -ForegroundColor Cyan
Write-Host ""

$RequiredPython = "3.12"

Write-Host "🔍 Detecting Python $RequiredPython..." -ForegroundColor Yellow
Write-Host ""
try {
    $output = & py "-$RequiredPython" --version 2>&1 | Out-String
    if ($LASTEXITCODE -ne 0) { throw "py launcher did not return a version" }
} catch {
    Write-Host "❌ Error: Python $RequiredPython is required but was not found via the Windows py launcher." -ForegroundColor Red
    Write-Host "" 
    Write-Host "Install Python $RequiredPython and ensure 'py' is available." -ForegroundColor Yellow
    Write-Host "" 
    Read-Host "Press Enter to exit"
    exit 1
}

$fullVersion = ($output -replace 'Python ', '').Trim()
$selectedPython = [PSCustomObject]@{
    FullVersion = $fullVersion
    Command = "py -$RequiredPython"
}

Write-Host ""
Write-Host "✅ Selected: Python $($selectedPython.FullVersion)" -ForegroundColor Green
Write-Host "   Command: $($selectedPython.Command)" -ForegroundColor Gray
Write-Host ""

# Check if .venv already exists
if (Test-Path ".venv") {
    Write-Host "⚠️  Warning: .venv directory already exists." -ForegroundColor Yellow
    $recreate = Read-Host "Remove existing .venv and recreate? [y/N]"
    if ([string]::IsNullOrWhiteSpace($recreate)) { $recreate = "N" }
    
    if ($recreate -match '^[Yy]$') {
        Write-Host "Removing existing .venv..." -ForegroundColor Yellow
        Remove-Item -Recurse -Force .venv
    }
    else {
        Write-Host "Setup cancelled. Remove .venv manually if you want to recreate it." -ForegroundColor Yellow
        Read-Host "Press Enter to exit"
        exit 0
    }
}

# Create virtual environment
Write-Host "Creating virtual environment in .venv\ ..." -ForegroundColor Yellow

# Execute the selected Python command to create venv
$pythonCmd = $selectedPython.Command.Split(' ')
if ($pythonCmd.Count -eq 1) {
    & $pythonCmd[0] -m venv .venv
}
else {
    & $pythonCmd[0] $pythonCmd[1] -m venv .venv
}

if ($LASTEXITCODE -ne 0) {
    Write-Host "❌ Failed to create virtual environment." -ForegroundColor Red
    Read-Host "Press Enter to exit"
    exit 1
}

# Activate virtual environment
Write-Host "Activating virtual environment..." -ForegroundColor Yellow
& .\.venv\Scripts\Activate.ps1

# Verify activation
Write-Host "Using Python: $(Get-Command python | Select-Object -ExpandProperty Source)" -ForegroundColor Gray
$verifyVersion = & python --version 2>&1 | Out-String
Write-Host "Python version: $verifyVersion" -ForegroundColor Gray
Write-Host ""

# Upgrade pip
Write-Host "Upgrading pip..." -ForegroundColor Yellow
& python -m pip install --upgrade pip --quiet

# Install dependencies
Write-Host ""
Write-Host "Installing dependencies from requirements.txt..." -ForegroundColor Yellow
Write-Host "(This may take a few minutes...)" -ForegroundColor Gray
& pip install -r requirements.txt --quiet

if ($LASTEXITCODE -ne 0) {
    Write-Host "❌ Failed to install dependencies." -ForegroundColor Red
    Read-Host "Press Enter to exit"
    exit 1
}

# Success message
Write-Host ""
Write-Host "=========================================" -ForegroundColor Green
Write-Host "✅ Setup completed successfully!" -ForegroundColor Green
Write-Host "=========================================" -ForegroundColor Green
Write-Host ""
Write-Host "Virtual environment created with Python $($selectedPython.FullVersion)" -ForegroundColor White
Write-Host ""
Write-Host "Next steps:" -ForegroundColor Cyan
Write-Host ""
Write-Host "  1. Activate the virtual environment:" -ForegroundColor White
Write-Host "     .\.venv\Scripts\Activate.ps1" -ForegroundColor Yellow
Write-Host ""
Write-Host "  2. Create the projectDocs directory (if not exists):" -ForegroundColor White
Write-Host "     mkdir projectDocs" -ForegroundColor Yellow
Write-Host ""
Write-Host "  3. Configure LLM settings (optional):" -ForegroundColor White
Write-Host "     Copy-Item configs\llm.default.json configs\llm.json" -ForegroundColor Yellow
Write-Host "     # Then edit configs\llm.json with your LLM endpoint" -ForegroundColor Gray
Write-Host ""
Write-Host "  4. Run the API server:" -ForegroundColor White
Write-Host "     cd apps\api" -ForegroundColor Yellow
Write-Host "     `$env:PROJECT_DOCS_PATH='..\..\projectDocs'" -ForegroundColor Yellow
Write-Host "     uvicorn main:app --reload" -ForegroundColor Yellow
Write-Host ""
Write-Host "  5. Access the API at:" -ForegroundColor White
Write-Host "     • API: http://localhost:8000" -ForegroundColor Cyan
Write-Host "     • Interactive docs: http://localhost:8000/docs" -ForegroundColor Cyan
Write-Host ""
Write-Host "For Docker deployment, see QUICKSTART.md" -ForegroundColor Gray
Write-Host ""
Read-Host "Press Enter to exit"
