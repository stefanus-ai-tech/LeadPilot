@echo off
cd /d "%~dp0"
echo LeadPilot - pilih CSV perusahaan untuk diproses dengan Laya lokal.
".venv\Scripts\python.exe" batch_process.py --pick file
pause
