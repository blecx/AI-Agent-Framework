@echo off
REM Intelligent Setup Script for ISO 21500 AI-Agent Framework (Windows)
REM Detects available Python versions, prompts user to select, and creates virtual environment

setlocal enabledelayedexpansion

echo =========================================
echo ISO 21500 AI-Agent Framework Setup
echo =========================================
echo.

REM Minimum required Python version
set MIN_PYTHON_MAJOR=3
set MIN_PYTHON_MINOR=10

echo Detecting available Python versions...
echo.

REM Initialize arrays (using environment variables with indices)
set PYTHON_COUNT=0

REM Check for py launcher with specific versions (realistic range)
for %%v in (3.10 3.11 3.12 3.13 3.14 3.15) do (
    py -%%v --version >nul 2>&1
    if !errorlevel! equ 0 (
        for /f "tokens=2" %%i in ('py -%%v --version 2^>^&1') do (
            set "FULL_VERSION=%%i"
            for /f "tokens=1,2 delims=." %%a in ("%%i") do (
                set MAJOR=%%a
                set MINOR=%%b
                if !MAJOR! geq %MIN_PYTHON_MAJOR% (
                    if !MAJOR! gtr %MIN_PYTHON_MAJOR% (
                        set "VERSIONS[!PYTHON_COUNT!]=%%v"
                        set "FULL_VERSIONS[!PYTHON_COUNT!]=%%i"
                        set "COMMANDS[!PYTHON_COUNT!]=py -%%v"
                        set /a PYTHON_COUNT+=1
                    ) else if !MINOR! geq %MIN_PYTHON_MINOR% (
                        set "VERSIONS[!PYTHON_COUNT!]=%%v"
                        set "FULL_VERSIONS[!PYTHON_COUNT!]=%%i"
                        set "COMMANDS[!PYTHON_COUNT!]=py -%%v"
                        set /a PYTHON_COUNT+=1
                    )
                )
            )
        )
    )
)

REM Check for python command
python --version >nul 2>&1
if !errorlevel! equ 0 (
    for /f "tokens=2" %%i in ('python --version 2^>^&1') do (
        set "FULL_VERSION=%%i"
        for /f "tokens=1,2 delims=." %%a in ("%%i") do (
            set MAJOR=%%a
            set MINOR=%%b
            if !MAJOR! geq %MIN_PYTHON_MAJOR% (
                if !MAJOR! gtr %MIN_PYTHON_MAJOR% (
                    set "VERSIONS[!PYTHON_COUNT!]=%%a.%%b"
                    set "FULL_VERSIONS[!PYTHON_COUNT!]=%%i"
                    set "COMMANDS[!PYTHON_COUNT!]=python"
                    set /a PYTHON_COUNT+=1
                ) else if !MINOR! geq %MIN_PYTHON_MINOR% (
                    set "VERSIONS[!PYTHON_COUNT!]=%%a.%%b"
                    set "FULL_VERSIONS[!PYTHON_COUNT!]=%%i"
                    set "COMMANDS[!PYTHON_COUNT!]=python"
                    set /a PYTHON_COUNT+=1
                )
            )
        )
    )
)

REM Check if any compatible Python versions were found
if !PYTHON_COUNT! equ 0 (
    echo [X] Error: No compatible Python version found!
    echo.
    echo This project requires Python %MIN_PYTHON_MAJOR%.%MIN_PYTHON_MINOR% or higher.
    echo.
    echo Download Python from:
    echo   - https://www.python.org/downloads/
    echo.
    echo Make sure to check "Add Python to PATH" during installation.
    echo.
    pause
    exit /b 1
)

REM Display found Python versions
echo [OK] Found !PYTHON_COUNT! compatible Python version(s):
echo.
for /l %%i in (0,1,!PYTHON_COUNT!) do (
    if defined VERSIONS[%%i] (
        set /a DISPLAY_NUM=%%i+1
        echo   [!DISPLAY_NUM!] Python !FULL_VERSIONS[%%i]!
        echo       Command: !COMMANDS[%%i]!
        echo.
    )
)

REM Select Python version
set SELECTED_INDEX=-1

if !PYTHON_COUNT! equ 1 (
    REM Only one version found, ask for confirmation
    echo Only one compatible version found: Python !FULL_VERSIONS[0]!
    set /p "confirm=Use this version? [Y/n]: "
    if "!confirm!"=="" set confirm=Y
    if /i "!confirm!"=="Y" (
        set SELECTED_INDEX=0
    ) else (
        echo Setup cancelled.
        pause
        exit /b 0
    )
) else (
    REM Multiple versions found, let user choose
    :SELECT_VERSION
    set /p "selection=Select Python version [1-!PYTHON_COUNT!]: "
    
    REM Validate input
    if "!selection!"=="" goto INVALID_SELECTION
    set /a test_num=!selection! 2>nul
    if "!test_num!"=="0" (
        if not "!selection!"=="0" goto INVALID_SELECTION
    )
    if !selection! lss 1 goto INVALID_SELECTION
    if !selection! gtr !PYTHON_COUNT! goto INVALID_SELECTION
    
    set /a SELECTED_INDEX=!selection!-1
    goto SELECTION_DONE
    
    :INVALID_SELECTION
    echo Invalid selection. Please enter a number between 1 and !PYTHON_COUNT!.
    goto SELECT_VERSION
    
    :SELECTION_DONE
)

set "SELECTED_PYTHON=!COMMANDS[%SELECTED_INDEX%]!"
set "SELECTED_VERSION=!FULL_VERSIONS[%SELECTED_INDEX%]!"

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
