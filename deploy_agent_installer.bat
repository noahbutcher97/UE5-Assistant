@echo off
title UE5 Deploy Agent Installer
color 0B

echo ============================================================
echo        UE5 AI Assistant - Deploy Agent Installer
echo ============================================================
echo.

:: Check for Python
python --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Python is not installed or not in PATH.
    echo Please install Python 3.8+ from https://python.org
    pause
    exit /b 1
)

:: Get project path from user
set /p PROJECT_PATH="Enter your UE5 project path (e.g., D:\UnrealProjects\5.6\UE5_Assistant): "

if not exist "%PROJECT_PATH%" (
    echo [ERROR] Project path does not exist: %PROJECT_PATH%
    pause
    exit /b 1
)

echo.
echo Project: %PROJECT_PATH%
echo.

:: Download deploy agent
echo [1/3] Downloading Deploy Agent...
powershell -Command "Invoke-WebRequest -Uri 'https://ue5-assistant-noahbutcher97.replit.app/api/deploy_agent' -OutFile 'deploy_agent.py'"

if not exist deploy_agent.py (
    echo [ERROR] Failed to download deploy_agent.py
    pause
    exit /b 1
)

echo [2/3] Starting Deploy Agent...
echo.
echo ============================================================
echo     Deploy Agent is starting on http://localhost:7865
echo     Keep this window open while using the dashboard!
echo ============================================================
echo.

:: Run the agent
python deploy_agent.py --ue5-project "%PROJECT_PATH%"

pause