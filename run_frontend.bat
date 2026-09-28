@echo off
echo ========================================================
echo Starting SIH26122 Modern Web Dashboard (React + Vite)
echo ========================================================
cd /d "%~dp0frontend"
start chrome "http://localhost:5173"
npm run dev
pause
