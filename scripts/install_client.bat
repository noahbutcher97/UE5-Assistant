@echo off
setlocal enabledelayedexpansion
color 0A

echo ================================================
echo    UE5 AI Assistant - Quick Installer
echo ================================================
echo.

REM Prompt for project path
set /p "PROJECT_PATH=Enter your UE5 project path (e.g., D:\UnrealProjects\MyProject): "
echo.

REM Validate path exists
if not exist "%PROJECT_PATH%" (
    color 0C
    echo ERROR: Project path does not exist: %PROJECT_PATH%
    echo.
    pause
    exit /b 1
)

set "TARGET_PATH=%PROJECT_PATH%\Content\Python\AIAssistant"
set "TEMP_ZIP=%TEMP%\ue5_assistant_client.zip"
set "DOWNLOAD_URL=https://ue5-assistant-noahbutcher97.replit.app/api/download_client"

echo [1/3] Downloading latest client...
echo From: %DOWNLOAD_URL%
echo.

REM Download using PowerShell (no admin needed)
powershell -Command "& {[Net.ServicePointManager]::SecurityProtocol = [Net.SecurityProtocolType]::Tls12; Invoke-WebRequest -Uri '%DOWNLOAD_URL%' -OutFile '%TEMP_ZIP%' -UseBasicParsing}"

if not exist "%TEMP_ZIP%" (
    color 0C
    echo ERROR: Download failed
    echo.
    pause
    exit /b 1
)

echo SUCCESS: Downloaded to %TEMP_ZIP%
echo.

echo [2/3] Extracting files...
echo To: %TARGET_PATH%
echo.

REM Backup existing installation
if exist "%TARGET_PATH%" (
    echo Found existing installation - creating backup...
    if exist "%TARGET_PATH%.backup" rmdir /s /q "%TARGET_PATH%.backup"
    move "%TARGET_PATH%" "%TARGET_PATH%.backup" >nul 2>&1
    echo Backup created: %TARGET_PATH%.backup
    echo.
)

REM Extract using PowerShell (no admin needed)
powershell -Command "& {Expand-Archive -Path '%TEMP_ZIP%' -DestinationPath '%PROJECT_PATH%\Content\Python' -Force}"

if not exist "%TARGET_PATH%" (
    color 0C
    echo ERROR: Extraction failed
    echo.
    pause
    exit /b 1
)

echo SUCCESS: Files extracted
echo.

echo [3/3] Cleanup...
del "%TEMP_ZIP%" >nul 2>&1
echo.

color 0A
echo ================================================
echo          INSTALLATION COMPLETE!
echo ================================================
echo.
echo Next steps:
echo 1. Open your Unreal Engine project
echo 2. Open Python Console (Tools ^> Python Console)
echo 3. Run: import AIAssistant.main
echo.
echo Installation location:
echo %TARGET_PATH%
echo.
pause
