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

REM Create PowerShell script using simple redirect
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
echo     Write-Host "Source: $DownloadURL" -ForegroundColor Gray
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
echo         throw "Download failed - file not created"
echo     }
echo.
echo     $FileSize = ^(Get-Item $TempZip^).Length
echo     $FileSizeMB = [math]::Round^($FileSize / 1MB, 2^)
echo.
echo     if ^($FileSize -lt 10000^) {
echo         $content = Get-Content $TempZip -Raw -ErrorAction SilentlyContinue
echo         Write-Host "Downloaded file too small: $FileSize bytes" -ForegroundColor Red
echo         if ^($content^) {
echo             $preview = $content.Substring^(0, [Math]::Min^(200, $content.Length^)^)
echo             Write-Host "Content: $preview" -ForegroundColor Yellow
echo         }
echo         throw "Downloaded file too small"
echo     }
echo.
echo     Write-Host "Downloaded: $FileSizeMB MB in $^($DownloadDuration.TotalSeconds.ToString^('0.0'^)^)s" -ForegroundColor Green
echo     Write-Host "File size: $FileSize bytes" -ForegroundColor Gray
echo.
echo     Write-Host ""
echo     Write-Host "Validating ZIP file..." -ForegroundColor Yellow
echo     $bytes = [System.IO.File]::ReadAllBytes^($TempZip^)
echo     $zipHeader = [System.Text.Encoding]::ASCII.GetString^($bytes[0..1]^)
echo.
echo     if ^($zipHeader -ne "PK"^) {
echo         Write-Host "File is not a valid ZIP archive!" -ForegroundColor Red
echo         Write-Host "Expected PK, got: $zipHeader" -ForegroundColor Yellow
echo         throw "Not a valid ZIP"
echo     }
echo.
echo     Write-Host "Valid ZIP header detected" -ForegroundColor Green
echo.
echo     Add-Type -AssemblyName System.IO.Compression.FileSystem
echo     $zip = [System.IO.Compression.ZipFile]::OpenRead^($TempZip^)
echo     $entryCount = $zip.Entries.Count
echo     $zip.Dispose^(^)
echo.
echo     Write-Host "ZIP contains $entryCount entries" -ForegroundColor Green
echo.
echo     if ^($entryCount -eq 0^) {
echo         throw "ZIP file is empty"
echo     }
echo.
echo     Write-Host ""
echo     Write-Host "Extracting files..." -ForegroundColor Yellow
echo.
echo     if ^(Test-Path $TargetPath^) {
echo         Write-Host "Existing installation found" -ForegroundColor Yellow
echo         $BackupPath = "$TargetPath.backup_$^(Get-Date -Format 'yyyyMMdd_HHmmss'^)"
echo         Write-Host "Creating backup at: $BackupPath" -ForegroundColor Yellow
echo         Move-Item $TargetPath $BackupPath -Force
echo         Write-Host "Backup created" -ForegroundColor Cyan
echo     } else {
echo         Write-Host "Fresh installation" -ForegroundColor Gray
echo     }
echo.
echo     $ExtractDestination = Join-Path $ProjectPath "Content\Python"
echo     Write-Host "Extracting to: $ExtractDestination" -ForegroundColor Gray
echo.
echo     if ^(-not ^(Test-Path $ExtractDestination^)^) {
echo         New-Item -ItemType Directory -Path $ExtractDestination -Force ^| Out-Null
echo     }
echo.
echo     try {
echo         Expand-Archive -Path $TempZip -DestinationPath $ExtractDestination -Force -ErrorAction Stop
echo     } catch {
echo         Write-Host "Trying alternative extraction..." -ForegroundColor Yellow
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
echo         throw "No files found after extraction"
echo     }
echo.
echo     Write-Host "Extracted $FileCount files successfully" -ForegroundColor Green
echo.
echo     Write-Host ""
echo     Write-Host "Cleaning up..." -ForegroundColor Yellow
echo     Remove-Item $TempZip -Force
echo.
echo     Write-Host "Creating auto-startup configuration..." -ForegroundColor Yellow
echo     $PythonDir = Join-Path $ProjectPath "Content\Python"
echo     $InitUnrealFile = Join-Path $PythonDir "init_unreal.py"
echo.
echo     $InitUnrealScript = "# init_unreal.py - UE5 AI Assistant Auto-Startup`nimport unreal`ntry:`n    unreal.log^('=' * 60^)`n    unreal.log^('UE5 AI Assistant - Auto-initializing...'^)`n    unreal.log^('=' * 60^)`n    import AIAssistant.startup`n    AIAssistant.startup.configure_and_start^('$BackendURL'^)`nexcept Exception as e:`n    unreal.log_error^(f'AI Assistant startup failed: {e}'^)`n    unreal.log^('Manual start: import AIAssistant.main'^)"
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
echo     Write-Host "Summary:" -ForegroundColor Cyan
echo     Write-Host "Files installed: $FileCount" -ForegroundColor White
echo     Write-Host "Location: $TargetPath" -ForegroundColor White
echo     Write-Host "Backend: $BackendURL" -ForegroundColor White
echo     Write-Host "Auto-startup: ENABLED" -ForegroundColor Green
echo     Write-Host ""
echo     Write-Host "Next Steps:" -ForegroundColor Cyan
echo     Write-Host "1. Launch/Restart UE5 Editor" -ForegroundColor White
echo     Write-Host "2. Check Output Log for auto-startup message" -ForegroundColor White
echo     Write-Host "3. AI Assistant will connect automatically" -ForegroundColor White
echo     Write-Host ""
echo     Write-Host "Dashboard: $BackendURL/dashboard" -ForegroundColor Cyan
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
echo     Write-Host "Debug Info:" -ForegroundColor Cyan
echo     Write-Host "Download URL: $DownloadURL" -ForegroundColor Gray
echo     Write-Host "Temp ZIP: $TempZip" -ForegroundColor Gray
echo     Write-Host "Target: $TargetPath" -ForegroundColor Gray
echo.
echo     if ^(Test-Path $TempZip^) {
echo         $zipSize = ^(Get-Item $TempZip^).Length
echo         Write-Host "Downloaded file size: $zipSize bytes" -ForegroundColor Gray
echo     }
echo.
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
echo ================================================
echo   Running Installer...
echo ================================================
echo.

REM Execute PowerShell installer
powershell -ExecutionPolicy Bypass -File "%PS_INSTALLER%" -ProjectPath "%PROJECT_PATH%" -BackendURL "%BACKEND_URL%"

set INSTALL_RESULT=%ERRORLEVEL%

REM Cleanup
del "%PS_INSTALLER%" >nul 2>&1

if %INSTALL_RESULT% NEQ 0 (
    color 0C
    echo.
    echo Installation failed with error code: %INSTALL_RESULT%
    echo.
)

pause