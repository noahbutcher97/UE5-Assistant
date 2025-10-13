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

set "PS_INSTALLER=%TEMP%\install_ue5_assistant.ps1"
set "BACKEND_URL=https://ue5-assistant-noahbutcher97.replit.app"

echo Creating installer script...

REM Create PowerShell script - init_unreal content with NO EMOJIS
(
echo param^(
echo     [string]$ProjectPath = "",
echo     [string]$BackendURL = "https://ue5-assistant-noahbutcher97.replit.app"
echo ^)
echo.
echo Write-Host "================================================" -ForegroundColor Cyan
echo Write-Host "UE5 AI Assistant - One-Click Installer" -ForegroundColor Cyan
echo Write-Host "================================================" -ForegroundColor Cyan
echo Write-Host ""
echo.
echo if ^(-not ^(Test-Path $ProjectPath^)^) {
echo     Write-Host "Error: Project path not found" -ForegroundColor Red
echo     Write-Host "Press any key to exit..." -ForegroundColor Gray
echo     $null = $Host.UI.RawUI.ReadKey^("NoEcho,IncludeKeyDown"^)
echo     exit 1
echo }
echo.
echo $TargetPath = Join-Path $ProjectPath "Content\Python\AIAssistant"
echo $DownloadURL = "$BackendURL/api/download_client"
echo $TempZip = Join-Path $env:TEMP "ue5_assistant_client.zip"
echo.
echo Write-Host "Project: $ProjectPath" -ForegroundColor White
echo Write-Host "Download URL: $DownloadURL" -ForegroundColor White
echo Write-Host "Install to: $TargetPath" -ForegroundColor White
echo Write-Host ""
echo.
echo try {
echo     if ^(Test-Path $TempZip^) {
echo         Remove-Item $TempZip -Force
echo     }
echo.
echo     Write-Host "Downloading client files..." -ForegroundColor Yellow
echo.
echo     $DownloadStartTime = Get-Date
echo.
echo     try {
echo         $webClient = New-Object System.Net.WebClient
echo         $webClient.Headers.Add^("User-Agent", "PowerShell-UE5-Installer"^)
echo         $webClient.DownloadFile^($DownloadURL, $TempZip^)
echo         $webClient.Dispose^(^)
echo     } catch {
echo         Write-Host "Trying alternative method..." -ForegroundColor Yellow
echo         Invoke-WebRequest -Uri $DownloadURL -OutFile $TempZip -UseBasicParsing -ErrorAction Stop
echo     }
echo.
echo     $DownloadDuration = ^(Get-Date^) - $DownloadStartTime
echo.
echo     if ^(-not ^(Test-Path $TempZip^)^) {
echo         throw "Download failed"
echo     }
echo.
echo     $FileSize = ^(Get-Item $TempZip^).Length
echo     $FileSizeMB = [math]::Round^($FileSize / 1MB, 2^)
echo.
echo     if ^($FileSize -lt 10000^) {
echo         throw "Downloaded file too small"
echo     }
echo.
echo     Write-Host "Downloaded: $FileSizeMB MB" -ForegroundColor Green
echo.
echo     Write-Host "Validating ZIP..." -ForegroundColor Yellow
echo     $bytes = [System.IO.File]::ReadAllBytes^($TempZip^)
echo     $zipHeader = [System.Text.Encoding]::ASCII.GetString^($bytes[0..1]^)
echo.
echo     if ^($zipHeader -ne "PK"^) {
echo         throw "Not a valid ZIP"
echo     }
echo.
echo     Write-Host "Valid ZIP detected" -ForegroundColor Green
echo.
echo     Add-Type -AssemblyName System.IO.Compression.FileSystem
echo     $zip = [System.IO.Compression.ZipFile]::OpenRead^($TempZip^)
echo     $entryCount = $zip.Entries.Count
echo     $zip.Dispose^(^)
echo.
echo     if ^($entryCount -eq 0^) {
echo         throw "ZIP file is empty"
echo     }
echo.
echo     Write-Host "Extracting $entryCount files..." -ForegroundColor Yellow
echo.
echo     if ^(Test-Path $TargetPath^) {
echo         $BackupPath = "$TargetPath.backup_$^(Get-Date -Format 'yyyyMMdd_HHmmss'^)"
echo         Move-Item $TargetPath $BackupPath -Force
echo         Write-Host "Backup created" -ForegroundColor Cyan
echo     }
echo.
echo     $ExtractDestination = Join-Path $ProjectPath "Content\Python"
echo.
echo     if ^(-not ^(Test-Path $ExtractDestination^)^) {
echo         New-Item -ItemType Directory -Path $ExtractDestination -Force ^| Out-Null
echo     }
echo.
echo     try {
echo         Expand-Archive -Path $TempZip -DestinationPath $ExtractDestination -Force -ErrorAction Stop
echo     } catch {
echo         [System.IO.Compression.ZipFile]::ExtractToDirectory^($TempZip, $ExtractDestination, $true^)
echo     }
echo.
echo     if ^(-not ^(Test-Path $TargetPath^)^) {
echo         throw "Extraction failed"
echo     }
echo.
echo     $AllFiles = Get-ChildItem -Path $TargetPath -Recurse -File
echo     $FileCount = $AllFiles.Count
echo.
echo     if ^($FileCount -eq 0^) {
echo         throw "No files found"
echo     }
echo.
echo     Write-Host "Extracted $FileCount files" -ForegroundColor Green
echo.
echo     Remove-Item $TempZip -Force
echo.
echo     Write-Host "Creating init_unreal.py..." -ForegroundColor Yellow
echo     $PythonDir = Join-Path $ProjectPath "Content\Python"
echo     $InitUnrealFile = Join-Path $PythonDir "init_unreal.py"
echo.
echo     $InitUnrealScript = @'
echo """
echo UE5 AI Assistant - Auto-Initialization Script
echo This script is automatically run by Unreal Engine on startup.
echo Place this file in: YourProject/Content/Python/init_unreal.py
echo """
echo print^(""^)
echo print^("=" * 60^)
echo print^("UE5 AI Assistant - Auto-initializing..."^)
echo print^("=" * 60^)
echo # Force production server by default for stability
echo FORCE_PRODUCTION = True
echo try:
echo     # Import and run the startup configuration
echo     from AIAssistant.startup import configure_and_start
echo.    
echo     # Use production server by default
echo     configure_and_start^(force_production=FORCE_PRODUCTION^)
echo.    
echo except ImportError as e:
echo     print^(f"Failed to load AI Assistant: {e}"^)
echo     print^(""^)
echo     print^("Make sure AIAssistant is installed in Content/Python/"^)
echo     print^("   Run the bootstrap script to install it automatically"^)
echo     print^(""^)
echo except Exception as e:
echo     print^(f"AI Assistant initialization error: {e}"^)
echo     import traceback
echo     traceback.print_exc^(^)
echo '@
echo.
echo     $InitUnrealScript ^| Out-File -FilePath $InitUnrealFile -Encoding UTF8 -Force
echo.
echo     if ^(Test-Path $InitUnrealFile^) {
echo         Write-Host "init_unreal.py created" -ForegroundColor Green
echo     }
echo.
echo     Write-Host ""
echo     Write-Host "================================================" -ForegroundColor Green
echo     Write-Host "INSTALLATION COMPLETE!" -ForegroundColor Green
echo     Write-Host "================================================" -ForegroundColor Green
echo     Write-Host ""
echo     Write-Host "Files installed: $FileCount" -ForegroundColor White
echo     Write-Host "Location: $TargetPath" -ForegroundColor White
echo     Write-Host "Auto-startup: ENABLED" -ForegroundColor Green
echo     Write-Host ""
echo     Write-Host "Next Steps:" -ForegroundColor Cyan
echo     Write-Host "1. Launch/Restart UE5 Editor" -ForegroundColor White
echo     Write-Host "2. Check Output Log for auto-startup" -ForegroundColor White
echo     Write-Host ""
echo     Write-Host "Press any key to exit..." -ForegroundColor Gray
echo     $null = $Host.UI.RawUI.ReadKey^("NoEcho,IncludeKeyDown"^)
echo.
echo } catch {
echo     Write-Host ""
echo     Write-Host "================================================" -ForegroundColor Red
echo     Write-Host "INSTALLATION FAILED" -ForegroundColor Red
echo     Write-Host "================================================" -ForegroundColor Red
echo     Write-Host ""
echo     Write-Host "Error: $^($_.Exception.Message^)" -ForegroundColor Yellow
echo     Write-Host ""
echo     Write-Host "Press any key to exit..." -ForegroundColor Gray
echo     $null = $Host.UI.RawUI.ReadKey^("NoEcho,IncludeKeyDown"^)
echo     exit 1
echo }
) > "%PS_INSTALLER%"

if not exist "%PS_INSTALLER%" (
    color 0C
    echo ERROR: Failed to create installer script
    pause
    exit /b 1
)

echo Done.
echo.

REM Execute PowerShell installer
powershell -ExecutionPolicy Bypass -File "%PS_INSTALLER%" -ProjectPath "%PROJECT_PATH%" -BackendURL "%BACKEND_URL%"

set INSTALL_RESULT=%ERRORLEVEL%

REM Cleanup
del "%PS_INSTALLER%" >nul 2>&1

if %INSTALL_RESULT% NEQ 0 (
    color 0C
    echo Installation failed
)

pause