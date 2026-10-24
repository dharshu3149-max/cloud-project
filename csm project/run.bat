@echo off
title Cloud Backup Tracker - College CSM Project
color 0b

echo ========================================================
echo   Cloud Backup Tracker - College CSM Project
echo ========================================================
echo.
echo [1/3] Checking Python installation...
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERROR] Python is not installed or not in PATH!
    echo Please install Python 3.8+ and ensure "Add Python to PATH" is checked.
    pause
    exit /b
)
python --version

echo.
echo [2/3] Checking required libraries (Flask)...
python -c "import flask" >nul 2>&1
if %errorlevel% neq 0 (
    echo Installing Flask and dependencies...
    pip install -r requirements.txt
) else (
    echo Flask is already installed.
)

echo.
echo [3/3] Launching Cloud Backup Tracker website...
echo Opening website at http://127.0.0.1:5000 in Google Chrome...
echo.
echo --------------------------------------------------------
echo The Cloud Backup Tracker server is now LIVE!
echo Local Address : http://127.0.0.1:5000
echo Press Ctrl+C in this terminal window to stop the server.
echo --------------------------------------------------------
python app.py

pause
