@echo off
echo ======================================================================
echo Starting SIH26166 ISRO Lunar Image Correspondence Backend (FastAPI)
echo ======================================================================
cd /d "%~dp0lunar_align\backend"
call "venv\Scripts\activate"
python -m uvicorn app.main:app --host 0.0.0.0 --port 8001 --reload
pause
