@echo off
setlocal enabledelayedexpansion

:: Simple batch script to download and run the UE5 Assistant PowerShell installer.

title UE5 AI Assistant - Quick Installer

echo ================================================
echo    UE5 AI Assistant - Quick Installer
echo ================================================
echo.

:: PowerShell is required
where /q powershell
if %errorlevel% neq 0 (
    echo ❌ ERROR: PowerShell is not installed or not in your PATH.
    echo    Please install PowerShell 5.1 or later and try again.
    pause
    exit /b 1
)

:: Prompt for project path
echo Please select your UE5 project folder in the dialog...
set "psCommand=Add-Type -AssemblyName System.windows.forms; $f=New-Object System.Windows.Forms.FolderBrowserDialog; $f.Description='Select your Unreal Engine 5 project folder'; $f.ShowNewFolderButton=$false; $f.ShowDialog(); $f.SelectedPath"
for /f "delims=" %%I in ('powershell -NoProfile -Command "%psCommand%"') do set "ProjectPath=%%I"

if not defined ProjectPath (
    echo ❌ Canceled. No folder selected.
    pause
    exit /b 1
)

echo Selected: %ProjectPath%
echo.
echo Downloading enhanced installer...
echo.

set "BackendURL=https://ue5-assistant-noahbutcher97.replit.app"
set "InstallerURL=%BackendURL%/api/installer_script"
set "TempInstaller=%TEMP%\install_ue5_assistant.ps1"

:: Cache-busting: Append a unique timestamp to the URL to bypass CDN caching
set "CacheBuster=%RANDOM%%RANDOM%"
set "FullURL=%InstallerURL%?v=%CacheBuster%"

:: Download the latest installer script using PowerShell
powershell -NoProfile -ExecutionPolicy Bypass -Command "try { Invoke-WebRequest -Uri '%FullURL%' -Method POST -OutFile '%TempInstaller%' } catch { Write-Host '❌ Download failed.'; exit 1 }"

if not exist "%TempInstaller%" (
    echo ❌ Failed to download the installer script.
    echo    Please check your internet connection and the backend URL.
    pause
    exit /b 1
)

echo.
echo ================================================
echo   Running Enhanced Installer...
echo ================================================
echo.

:: Run the downloaded PowerShell script
powershell -NoProfile -ExecutionPolicy Bypass -File "%TempInstaller%" -ProjectPath "%ProjectPath%"

del "%TempInstaller%" >nul 2>&1

endlocal
pause