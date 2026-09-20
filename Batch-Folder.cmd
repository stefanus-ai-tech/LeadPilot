@echo off
cd /d "%~dp0"
echo LeadPilot - pilih folder berisi CSV.
".venv\Scripts\python.exe" batch_process.py --pick folder
pause
