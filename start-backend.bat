@echo off
echo ========================================
echo Starting Backend Server
echo ========================================

cd backend

REM Check if virtual environment exists
if not exist "venv\" (
    echo Creating virtual environment...
    python -m venv venv
    echo.
)

REM Activate virtual environment
call venv\Scripts\activate.bat

REM Check if .env exists
if not exist ".env" (
    echo Creating .env file from template...
    copy .env.example .env
    echo.
    echo IMPORTANT: Edit .env file and configure your settings!
    pause
)

REM Install dependencies if needed
echo Checking dependencies...
pip install -q -r requirements.txt

REM Run database migrations
echo Running database migrations...
alembic upgrade head

REM Start the server
echo.
echo ========================================
echo Backend Server Starting...
echo ========================================
echo API: http://localhost:8000
echo Docs: http://localhost:8000/docs
echo ========================================
echo.

uvicorn app.main:app --reload
