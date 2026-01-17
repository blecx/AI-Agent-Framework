@echo off
REM Intelligent Setup Script for ISO 21500 AI-Agent Framework (Windows)
REM Detects available Python versions, prompts user to select, and creates virtual environment

setlocal enabledelayedexpansion

echo =========================================
echo ISO 21500 AI-Agent Framework Setup
echo =========================================
echo.

set REQUIRED_PY=3.12

echo Detecting Python %REQUIRED_PY%...
echo.

py -%REQUIRED_PY% --version >nul 2>&1
if not !errorlevel! equ 0 (
    echo [X] Error: Python %REQUIRED_PY% is required but was not found via the Windows py launcher.
    echo.
    echo Install Python %REQUIRED_PY% and ensure the 'py' launcher is available.
    echo.
    pause
    exit /b 1
)

for /f "tokens=2" %%i in ('py -%REQUIRED_PY% --version 2^>^&1') do set "SELECTED_VERSION=%%i"
set "SELECTED_PYTHON=py -%REQUIRED_PY%"

echo.
echo [OK] Selected: Python !SELECTED_VERSION!
echo     Command: !SELECTED_PYTHON!
echo.

REM Check if .venv already exists
if exist ".venv" (
    echo [!] Warning: .venv directory already exists.
    set /p "recreate=Remove existing .venv and recreate? [y/N]: "
    if "!recreate!"=="" set recreate=N
    if /i "!recreate!"=="Y" (
        echo Removing existing .venv...
        rmdir /s /q .venv
    ) else (
        echo Setup cancelled. Remove .venv manually if you want to recreate it.
        pause
        exit /b 0
    )
)

REM Create virtual environment
echo Creating virtual environment in .venv\ ...
!SELECTED_PYTHON! -m venv .venv

REM Activate virtual environment
echo Activating virtual environment...
call .venv\Scripts\activate.bat

REM Verify activation
echo Using Python: 
where python
python --version
echo.

REM Upgrade pip
echo Upgrading pip...
python -m pip install --upgrade pip --quiet

REM Install dependencies
echo.
echo Installing dependencies from requirements.txt...
echo (This may take a few minutes...)
pip install -r requirements.txt --quiet

REM Success message
echo.
echo =========================================
echo [OK] Setup completed successfully!
echo =========================================
echo.
echo Virtual environment created with Python !SELECTED_VERSION!
echo.
echo Next steps:
echo.
echo   1. Activate the virtual environment:
echo      .venv\Scripts\activate.bat
echo.
echo   2. Create the projectDocs directory (if not exists):
echo      mkdir projectDocs
echo.
echo   3. Configure LLM settings (optional):
echo      copy configs\llm.default.json configs\llm.json
echo      REM Then edit configs\llm.json with your LLM endpoint
echo.
echo   4. Run the API server:
echo      cd apps\api
echo      set PROJECT_DOCS_PATH=..\..\projectDocs
echo      uvicorn main:app --reload
echo.
echo   5. Access the API at:
echo      * API: http://localhost:8000
echo      * Interactive docs: http://localhost:8000/docs
echo.
echo For Docker deployment, see QUICKSTART.md
echo.
pause
