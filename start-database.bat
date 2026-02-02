@echo off
echo ========================================
echo Starting PostgreSQL Database
echo ========================================
cd docker
docker compose up -d
echo.
echo Database started!
echo - PostgreSQL: localhost:5432
echo - pgAdmin: http://localhost:5050
echo.
pause
