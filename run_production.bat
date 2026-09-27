@echo off
title LunaAlign (SIH26166) - Production Server
color 0B

echo ========================================================
echo        LunaAlign (SIH26166) - Unified Production Build
echo ========================================================
echo.

cd /d "%~dp0"

echo [1/3] Building production React frontend bundle...
cd frontend
call npm run build
if %errorlevel% neq 0 (
    echo [ERROR] Frontend build failed!
    pause
    exit /b %errorlevel%
)
cd ..

echo.
echo [2/3] Verifying Python backend virtual environment...
if not exist "lunar_align\backend\venv\Scripts\python.exe" (
    echo [ERROR] Python venv not found at lunar_align\backend\venv!
    pause
    exit /b 1
)

echo.
echo [3/3] Launching unified production server on http://localhost:8001...
echo Both React Frontend and FastAPI Backend will run from this single port.
echo.
start http://localhost:8001

cd lunar_align\backend
venv\Scripts\python.exe -m uvicorn app.main:app --host 0.0.0.0 --port 8001
pause
