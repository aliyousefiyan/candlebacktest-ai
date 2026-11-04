@echo off
setlocal
cd /d "%~dp0"
echo CandleBacktest AI - local demo
where py >nul 2>&1
if errorlevel 1 (
    echo Python launcher not found. Install Python 3.10 or newer first.
    pause
    exit /b 1
)
if not exist ".venv\Scripts\python.exe" (
    py -3 -m venv .venv
    if errorlevel 1 (echo Failed to create virtual environment & pause & exit /b 1)
)
".venv\Scripts\python.exe" -m pip install -e .
if errorlevel 1 (echo Installation failed & pause & exit /b 1)
".venv\Scripts\python.exe" -m candlebacktest_ai web --browser
pause
