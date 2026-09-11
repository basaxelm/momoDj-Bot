@echo off
title momoDj Discord Bot
echo ========================================
echo       Iniciando momoDj Discord Bot
echo ========================================
echo.
cd /d "%~dp0"
if exist "venv\Scripts\python.exe" (
    venv\Scripts\python.exe main.py
) else if exist "venv\bin\python.exe" (
    venv\bin\python.exe main.py
) else (
    python main.py
)
pause
