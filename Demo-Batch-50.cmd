@echo off
cd /d "%~dp0"
".venv\Scripts\python.exe" batch_process.py samples\dummy-leads-50.csv
pause
