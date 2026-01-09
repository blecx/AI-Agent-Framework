@echo off
REM Setup script for ISO 21500 AI-Agent Framework (Windows)
REM Creates a Python virtual environment and installs dependencies

echo =========================================
echo ISO 21500 AI-Agent Framework Setup
echo =========================================
echo.

REM Check if Python is available
python --version >nul 2>&1
if errorlevel 1 (
    echo Error: Python is not installed or not in PATH
    echo Please install Python 3.10 or higher
    exit /b 1
)

REM Display Python version
for /f "tokens=2" %%i in ('python --version 2^>^&1') do set PYTHON_VERSION=%%i
echo Found Python version: %PYTHON_VERSION%

REM Create virtual environment
echo.
echo Creating virtual environment in .venv\ ...
python -m venv .venv

REM Activate virtual environment
echo Activating virtual environment...
call .venv\Scripts\activate.bat

REM Upgrade pip
echo.
echo Upgrading pip...
python -m pip install --upgrade pip

REM Install dependencies
echo.
echo Installing dependencies from requirements.txt...
pip install -r requirements.txt

REM Success message
echo.
echo =========================================
echo Setup completed successfully!
echo =========================================
echo.
echo Next steps:
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
echo   5. Access the API at http://localhost:8000
echo      API docs at http://localhost:8000/docs
echo.
echo For Docker deployment, see QUICKSTART.md
echo.
pause
