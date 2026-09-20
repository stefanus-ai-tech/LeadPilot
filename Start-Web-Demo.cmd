@echo off
cd /d "%~dp0"
echo Optional single-lead web demo: http://127.0.0.1:8001
".venv\Scripts\python.exe" -m uvicorn app.main:app --host 127.0.0.1 --port 8001
pause
