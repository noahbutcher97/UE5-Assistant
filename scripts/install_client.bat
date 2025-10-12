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

REM Create PowerShell installer directly
set "PS_INSTALLER=%TEMP%\install_ue5_assistant.ps1"
set "BACKEND_URL=https://ue5-assistant-noahbutcher97.replit.app"

echo Creating installer...

(
echo param^(
echo     [string]$ProjectPath = "",
echo     [string]$BackendURL = "https://ue5-assistant-noahbutcher97.replit.app"
echo ^)
echo.
echo $TargetPath = Join-Path $ProjectPath "Content\Python\AIAssistant"
echo $DownloadURL = "$BackendURL/api/download_client_bundle"
echo $TempZip = Join-Path $env:TEMP "ue5_assistant_client.zip"
echo.
echo Write-Host "Downloading from: $DownloadURL (POST method)..." -ForegroundColor Cyan
echo Invoke-WebRequest -Uri $DownloadURL -Method Post -OutFile $TempZip -UseBasicParsing
echo.
echo Write-Host "Extracting..." -ForegroundColor Cyan
echo if ^(Test-Path $TargetPath^) { Remove-Item $TargetPath -Recurse -Force }
echo Expand-Archive -Path $TempZip -DestinationPath (Join-Path $ProjectPath "Content\Python"^) -Force
echo Remove-Item $TempZip -Force
echo.
echo Write-Host "Installation complete!" -ForegroundColor Green
echo Write-Host "Restart Unreal Engine to activate the AI Assistant" -ForegroundColor Yellow
echo pause
) > "%PS_INSTALLER%"

if not exist "%PS_INSTALLER%" (
    color 0C
    echo ERROR: Failed to create installer
    pause
    exit /b 1
)

echo.
echo ================================================
echo   Running Installer...
echo ================================================
echo.

REM Execute PowerShell installer
powershell -ExecutionPolicy Bypass -File "%PS_INSTALLER%" -ProjectPath "%PROJECT_PATH%" -BackendURL "%BACKEND_URL%"

REM Cleanup
del "%PS_INSTALLER%" >nul 2>&1

echo.
pause
