@echo off
echo ========================================
echo Starting Backend Server
echo ========================================

cd /d "%~dp0backend"

REM Check if virtual environment exists
if not exist "venv\" (
    echo Creating virtual environment...
    py -m venv venv
    if errorlevel 1 (
        echo ERROR: Failed to create virtual environment
        echo Make sure Python is installed: https://www.python.org/downloads/
        pause
        exit /b 1
    )
    echo Virtual environment created!
    echo.
)

REM Activate virtual environment
echo Activating virtual environment...
call venv\Scripts\activate.bat

REM Check if .env exists
if not exist ".env" (
    echo Creating .env file from template...
    copy .env.example .env
    echo.
    echo NOTE: Using default configuration (Ollama for LLM)
    echo.
)

REM Install dependencies
echo Installing dependencies (this may take a few minutes on first run)...
py -m pip install -r requirements.txt --quiet
if errorlevel 1 (
    echo Installing dependencies with verbose output...
    py -m pip install -r requirements.txt
)

REM Run database migrations
echo.
echo Running database migrations...
py -m alembic upgrade head
if errorlevel 1 (
    echo WARNING: Migration failed. Database might not be ready yet.
    echo Make sure PostgreSQL is running (start-database.bat)
    echo.
)

REM Start the server
echo.
echo ========================================
echo Backend Server Starting...
echo ========================================
echo API: http://localhost:8000
echo Docs: http://localhost:8000/docs
echo ========================================
echo.
echo Press Ctrl+C to stop the server
echo.

py -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
