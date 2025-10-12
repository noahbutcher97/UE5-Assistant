@echo off
setlocal enabledelayedexpansion
color 0A

echo ================================================
echo    UE5 AI Assistant - Quick Installer
echo ================================================
echo.

REM Show folder picker GUI
echo Please select your UE5 project folder in the dialog...
echo.

for /f "delims=" %%i in ('powershell -command "Add-Type -AssemblyName System.Windows.Forms; $folder = New-Object System.Windows.Forms.FolderBrowserDialog; $folder.Description = 'Select your UE5 Project folder'; $folder.ShowNewFolderButton = $false; if($folder.ShowDialog() -eq 'OK'){$folder.SelectedPath}"') do set "PROJECT_PATH=%%i"

if "%PROJECT_PATH%"=="" (
    color 0C
    echo ERROR: No folder selected
    echo.
    pause
    exit /b 1
)

echo Selected: %PROJECT_PATH%
echo.

REM Download enhanced PowerShell installer
set "PS_INSTALLER=%TEMP%\install_ue5_assistant.ps1"
set "BACKEND_URL=https://ue5-assistant-noahbutcher97.replit.app"

echo Downloading enhanced installer...
powershell -Command "& {[Net.ServicePointManager]::SecurityProtocol = [Net.SecurityProtocolType]::Tls12; Invoke-WebRequest -Uri '%BACKEND_URL%/api/installer_script' -Method POST -OutFile '%PS_INSTALLER%' -UseBasicParsing}"

if not exist "%PS_INSTALLER%" (
    color 0C
    echo ERROR: Failed to download installer
    pause
    exit /b 1
)

echo.
echo ================================================
echo   Running Enhanced Installer...
echo ================================================
echo.

REM Execute enhanced PowerShell installer with selected project path
powershell -ExecutionPolicy Bypass -File "%PS_INSTALLER%" -ProjectPath "%PROJECT_PATH%" -BackendURL "%BACKEND_URL%"

REM Cleanup
del "%PS_INSTALLER%" >nul 2>&1

echo.
pause
