@echo off
echo ========================================
echo Starting Frontend Development Server
echo ========================================

cd frontend

REM Install dependencies if needed
if not exist "node_modules\" (
    echo Installing dependencies...
    npm install
    echo.
)

REM Start the dev server
echo.
echo ========================================
echo Frontend Server Starting...
echo ========================================
echo Application: http://localhost:5173
echo ========================================
echo.

npm run dev
