@echo off
title Instagram Asset Grabber - Enterprise Edition
color 0b

echo ========================================================
echo    Instagram Asset Grabber - Environment Setup
echo ========================================================
echo.

REM Check Python
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERROR] Python is not installed or not in PATH.
    echo Please install Python 3.8+ from python.org
    pause
    exit /b
)

echo [INFO] Installing/Updating Dependencies...
pip install -r requirements.txt
if %errorlevel% neq 0 (
    echo [ERROR] Failed to install requirements.
    pause
    exit /b
)

echo.
echo [INFO] Installing Playwright Browsers...
python -m playwright install chromium
if %errorlevel% neq 0 (
    echo [WARNING] Playwright install encountered an issue. continuing...
)

echo.
echo [SUCCESS] Setup Complete. Launching Application...
echo.
python grabber_browser.py

pause
