@echo off
echo ========================================================
echo Starting ADAPTIX-FARM Agricultural Intelligence Server
echo ========================================================
cd /d "%~dp0\.."
set PYTHONPATH=%CD%\backend
python backend\app\main.py
pause
