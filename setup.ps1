# Intelligent Setup Script for ISO 21500 AI-Agent Framework (PowerShell)
# Detects available Python versions, prompts user to select, and creates virtual environment

# Stop on errors
$ErrorActionPreference = "Stop"

Write-Host "=========================================" -ForegroundColor Cyan
Write-Host "ISO 21500 AI-Agent Framework Setup" -ForegroundColor Cyan
Write-Host "=========================================" -ForegroundColor Cyan
Write-Host ""

# Minimum required Python version
$MinPythonMajor = 3
$MinPythonMinor = 10

# Function to compare version numbers
function Test-PythonVersion {
    param (
        [string]$Version
    )
    
    $parts = $Version.Split('.')
    $major = [int]$parts[0]
    $minor = [int]$parts[1]
    
    if ($major -gt $MinPythonMajor) {
        return $true
    }
    elseif ($major -eq $MinPythonMajor -and $minor -ge $MinPythonMinor) {
        return $true
    }
    else {
        return $false
    }
}

# Detect available Python versions
Write-Host "🔍 Detecting available Python versions..." -ForegroundColor Yellow
Write-Host ""

$pythonVersions = @()

# Check for py launcher with specific versions
$pyVersionsToCheck = @("3.10", "3.11", "3.12", "3.13", "3.14", "3.15", "3.16", "3.17", "3.18", "3.19", "3.20")

foreach ($ver in $pyVersionsToCheck) {
    try {
        $output = & py "-$ver" --version 2>&1 | Out-String
        if ($LASTEXITCODE -eq 0) {
            $fullVersion = ($output -replace 'Python ', '').Trim()
            $shortVersion = ($fullVersion -split '\.')[0..1] -join '.'
            
            if (Test-PythonVersion $shortVersion) {
                $pythonVersions += [PSCustomObject]@{
                    ShortVersion = $shortVersion
                    FullVersion = $fullVersion
                    Command = "py -$ver"
                }
            }
        }
    }
    catch {
        # Version not available, continue
    }
}

# Check for python command
try {
    $output = & python --version 2>&1 | Out-String
    if ($LASTEXITCODE -eq 0) {
        $fullVersion = ($output -replace 'Python ', '').Trim()
        $shortVersion = ($fullVersion -split '\.')[0..1] -join '.'
        $path = (Get-Command python).Source
        
        if (Test-PythonVersion $shortVersion) {
            # Check if this version is not already in the list
            $exists = $pythonVersions | Where-Object { $_.FullVersion -eq $fullVersion }
            if (-not $exists) {
                $pythonVersions += [PSCustomObject]@{
                    ShortVersion = $shortVersion
                    FullVersion = $fullVersion
                    Command = "python"
                }
            }
        }
    }
}
catch {
    # Python command not available
}

# Check for python3 command
try {
    $output = & python3 --version 2>&1 | Out-String
    if ($LASTEXITCODE -eq 0) {
        $fullVersion = ($output -replace 'Python ', '').Trim()
        $shortVersion = ($fullVersion -split '\.')[0..1] -join '.'
        
        if (Test-PythonVersion $shortVersion) {
            # Check if this version is not already in the list
            $exists = $pythonVersions | Where-Object { $_.FullVersion -eq $fullVersion }
            if (-not $exists) {
                $pythonVersions += [PSCustomObject]@{
                    ShortVersion = $shortVersion
                    FullVersion = $fullVersion
                    Command = "python3"
                }
            }
        }
    }
}
catch {
    # Python3 command not available
}

# Remove duplicates based on FullVersion
$pythonVersions = $pythonVersions | Sort-Object -Property FullVersion -Unique

# Check if any compatible Python versions were found
if ($pythonVersions.Count -eq 0) {
    Write-Host "❌ Error: No compatible Python version found!" -ForegroundColor Red
    Write-Host ""
    Write-Host "This project requires Python $MinPythonMajor.$MinPythonMinor or higher."
    Write-Host ""
    Write-Host "📥 Download Python from:" -ForegroundColor Yellow
    Write-Host "  - https://www.python.org/downloads/"
    Write-Host ""
    Write-Host "Make sure to check 'Add Python to PATH' during installation."
    Write-Host ""
    Read-Host "Press Enter to exit"
    exit 1
}

# Display found Python versions
Write-Host "✅ Found $($pythonVersions.Count) compatible Python version(s):" -ForegroundColor Green
Write-Host ""

for ($i = 0; $i -lt $pythonVersions.Count; $i++) {
    Write-Host "  [$($i + 1)] Python $($pythonVersions[$i].FullVersion)" -ForegroundColor White
    Write-Host "      Command: $($pythonVersions[$i].Command)" -ForegroundColor Gray
    Write-Host ""
}

# Select Python version
$selectedIndex = -1

if ($pythonVersions.Count -eq 1) {
    # Only one version found, ask for confirmation
    Write-Host "Only one compatible version found: Python $($pythonVersions[0].FullVersion)"
    $confirm = Read-Host "Use this version? [Y/n]"
    if ([string]::IsNullOrWhiteSpace($confirm)) { $confirm = "Y" }
    
    if ($confirm -match '^[Yy]$') {
        $selectedIndex = 0
    }
    else {
        Write-Host "Setup cancelled." -ForegroundColor Yellow
        exit 0
    }
}
else {
    # Multiple versions found, let user choose
    $validSelection = $false
    while (-not $validSelection) {
        $selection = Read-Host "Select Python version [1-$($pythonVersions.Count)]"
        
        if ($selection -match '^\d+$') {
            $selectionNum = [int]$selection
            if ($selectionNum -ge 1 -and $selectionNum -le $pythonVersions.Count) {
                $selectedIndex = $selectionNum - 1
                $validSelection = $true
            }
            else {
                Write-Host "Invalid selection. Please enter a number between 1 and $($pythonVersions.Count)." -ForegroundColor Red
            }
        }
        else {
            Write-Host "Invalid input. Please enter a number." -ForegroundColor Red
        }
    }
}

$selectedPython = $pythonVersions[$selectedIndex]

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
