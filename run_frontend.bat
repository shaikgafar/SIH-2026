@echo off
echo ========================================================
echo Starting SIH26122 Modern Web Dashboard (React + Vite)
echo ========================================================
cd /d "%~dp0frontend"
npm run dev -- --host
pause
