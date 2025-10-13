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

REM Write PowerShell script (using proper escaping)
powershell -Command "$script = @'
# UE5 AI Assistant - One-Click Installer
param(
    [string]$ProjectPath = '',
    [string]$BackendURL = 'https://ue5-assistant-noahbutcher97.replit.app'
)

Write-Host '================================================' -ForegroundColor Cyan
Write-Host '🚀 UE5 AI Assistant - One-Click Installer' -ForegroundColor Cyan
Write-Host '================================================' -ForegroundColor Cyan
Write-Host ''

if (-not (Test-Path $ProjectPath)) {
    Write-Host '❌ Error: Project path not found: ' -NoNewline -ForegroundColor Red
    Write-Host $ProjectPath -ForegroundColor Red
    Write-Host '   Press any key to exit...' -ForegroundColor Gray
    $null = $Host.UI.RawUI.ReadKey('NoEcho,IncludeKeyDown')
    exit 1
}

$TargetPath = Join-Path $ProjectPath 'Content\Python\AIAssistant'
$DownloadURL = \"$BackendURL/api/download_client\"
$TempZip = Join-Path $env:TEMP 'ue5_assistant_client.zip'

Write-Host '📁 Project: ' -NoNewline -ForegroundColor White
Write-Host $ProjectPath -ForegroundColor White
Write-Host '📥 Download URL: ' -NoNewline -ForegroundColor White
Write-Host $DownloadURL -ForegroundColor White
Write-Host '📂 Install to: ' -NoNewline -ForegroundColor White
Write-Host $TargetPath -ForegroundColor White
Write-Host ''

try {
    # Clean up old temp file
    if (Test-Path $TempZip) {
        Remove-Item $TempZip -Force
    }

    Write-Host '⬇️  Downloading client files...' -ForegroundColor Yellow
    Write-Host '   Source: ' -NoNewline -ForegroundColor Gray
    Write-Host $DownloadURL -ForegroundColor Gray

    $DownloadStartTime = Get-Date

    # Download with proper error handling
    try {
        $webClient = New-Object System.Net.WebClient
        $webClient.Headers.Add('User-Agent', 'PowerShell-UE5-Installer')
        $webClient.DownloadFile($DownloadURL, $TempZip)
        $webClient.Dispose()
    } catch {
        Write-Host '   Trying alternative method...' -ForegroundColor Yellow
        Invoke-WebRequest -Uri $DownloadURL -OutFile $TempZip -UseBasicParsing -ErrorAction Stop
    }

    $DownloadDuration = (Get-Date) - $DownloadStartTime

    if (-not (Test-Path $TempZip)) {
        throw 'Download failed - file not created'
    }

    $FileSize = (Get-Item $TempZip).Length
    $FileSizeMB = [math]::Round($FileSize / 1MB, 2)

    # Validate file size
    if ($FileSize -lt 10000) {
        $content = Get-Content $TempZip -Raw -ErrorAction SilentlyContinue
        Write-Host '❌ Downloaded file too small: ' -NoNewline -ForegroundColor Red
        Write-Host \"$FileSize bytes\" -ForegroundColor Red
        if ($content) {
            $preview = $content.Substring(0, [Math]::Min(200, $content.Length))
            Write-Host '   Content: ' -NoNewline -ForegroundColor Yellow
            Write-Host $preview -ForegroundColor Yellow
        }
        throw 'Downloaded file too small - expected ZIP, got error response'
    }

    Write-Host '✅ Downloaded: ' -NoNewline -ForegroundColor Green
    Write-Host \"$FileSizeMB MB in $($DownloadDuration.TotalSeconds.ToString('0.0'))s\" -ForegroundColor Green
    Write-Host '   File size: ' -NoNewline -ForegroundColor Gray
    Write-Host \"$FileSize bytes\" -ForegroundColor Gray

    # Validate ZIP format
    Write-Host ''
    Write-Host '🔍 Validating ZIP file...' -ForegroundColor Yellow
    $bytes = [System.IO.File]::ReadAllBytes($TempZip)
    $zipHeader = [System.Text.Encoding]::ASCII.GetString($bytes[0..1])

    if ($zipHeader -ne 'PK') {
        Write-Host '❌ File is not a valid ZIP archive!' -ForegroundColor Red
        Write-Host '   Expected PK, got: ' -NoNewline -ForegroundColor Yellow
        Write-Host $zipHeader -ForegroundColor Yellow
        $preview = [System.Text.Encoding]::UTF8.GetString($bytes[0..[Math]::Min(200, $bytes.Length-1)])
        Write-Host '   Content preview: ' -NoNewline -ForegroundColor Gray
        Write-Host $preview -ForegroundColor Gray
        throw 'Downloaded file is not a valid ZIP archive'
    }

    Write-Host '   ✅ Valid ZIP header detected' -ForegroundColor Green

    # Verify ZIP can be opened
    Add-Type -AssemblyName System.IO.Compression.FileSystem
    $zip = [System.IO.Compression.ZipFile]::OpenRead($TempZip)
    $entryCount = $zip.Entries.Count
    $zip.Dispose()

    Write-Host '   ✅ ZIP contains ' -NoNewline -ForegroundColor Green
    Write-Host \"$entryCount entries\" -ForegroundColor Green

    if ($entryCount -eq 0) {
        throw 'ZIP file is empty!'
    }

    # Extract
    Write-Host ''
    Write-Host '📦 Extracting files...' -ForegroundColor Yellow

    # Backup existing installation
    if (Test-Path $TargetPath) {
        Write-Host '⚠️  Existing installation found!' -ForegroundColor Yellow
        $BackupPath = \"$TargetPath.backup_\" + (Get-Date -Format 'yyyyMMdd_HHmmss')
        Write-Host '   Creating backup at: ' -NoNewline -ForegroundColor Yellow
        Write-Host $BackupPath -ForegroundColor Yellow
        Move-Item $TargetPath $BackupPath -Force
        Write-Host '💾 Backup created successfully' -ForegroundColor Cyan
    } else {
        Write-Host '   Fresh installation' -ForegroundColor Gray
    }

    $ExtractDestination = Join-Path $ProjectPath 'Content\Python'
    Write-Host '   Extracting to: ' -NoNewline -ForegroundColor Gray
    Write-Host $ExtractDestination -ForegroundColor Gray

    if (-not (Test-Path $ExtractDestination)) {
        New-Item -ItemType Directory -Path $ExtractDestination -Force | Out-Null
    }

    try {
        Expand-Archive -Path $TempZip -DestinationPath $ExtractDestination -Force -ErrorAction Stop
    } catch {
        Write-Host '   Trying alternative extraction...' -ForegroundColor Yellow
        [System.IO.Compression.ZipFile]::ExtractToDirectory($TempZip, $ExtractDestination, $true)
    }

    if (-not (Test-Path $TargetPath)) {
        throw 'Extraction failed - AIAssistant directory not found'
    }

    $AllFiles = Get-ChildItem -Path $TargetPath -Recurse -File
    $FileCount = $AllFiles.Count

    if ($FileCount -eq 0) {
        throw 'No files found after extraction'
    }

    Write-Host '✅ Extracted ' -NoNewline -ForegroundColor Green
    Write-Host \"$FileCount files successfully\" -ForegroundColor Green

    # Cleanup
    Write-Host ''
    Write-Host '🧹 Cleaning up...' -ForegroundColor Yellow
    Remove-Item $TempZip -Force

    # Create init_unreal.py
    Write-Host '🔧 Creating auto-startup configuration...' -ForegroundColor Yellow
    $PythonDir = Join-Path $ProjectPath 'Content\Python'
    $InitUnrealFile = Join-Path $PythonDir 'init_unreal.py'

    $InitUnrealScript = @\"
# init_unreal.py - UE5 AI Assistant Auto-Startup
import unreal
try:
    unreal.log('=' * 60)
    unreal.log('🤖 UE5 AI Assistant - Auto-initializing...')
    unreal.log('=' * 60)
    import AIAssistant.startup
    AIAssistant.startup.configure_and_start('$BackendURL')
except Exception as e:
    unreal.log_error(f'❌ AI Assistant startup failed: {e}')
    unreal.log('💡 Manual start: import AIAssistant.main')
\"@

    $InitUnrealScript | Out-File -FilePath $InitUnrealFile -Encoding UTF8 -Force

    if (Test-Path $InitUnrealFile) {
        Write-Host '   ✅ init_unreal.py created' -ForegroundColor Green
    }

    Write-Host ''
    Write-Host '================================================' -ForegroundColor Green
    Write-Host '🎉 INSTALLATION COMPLETE!' -ForegroundColor Green
    Write-Host '================================================' -ForegroundColor Green
    Write-Host ''
    Write-Host '📊 Summary:' -ForegroundColor Cyan
    Write-Host '   Files installed: ' -NoNewline -ForegroundColor White
    Write-Host $FileCount -ForegroundColor White
    Write-Host '   Location: ' -NoNewline -ForegroundColor White
    Write-Host $TargetPath -ForegroundColor White
    Write-Host '   Backend: ' -NoNewline -ForegroundColor White
    Write-Host $BackendURL -ForegroundColor White
    Write-Host '   Auto-startup: ✅ ENABLED' -ForegroundColor Green
    Write-Host ''
    Write-Host '🚀 Next Steps:' -ForegroundColor Cyan
    Write-Host '   1. Launch/Restart UE5 Editor' -ForegroundColor White
    Write-Host '   2. Check Output Log for auto-startup message' -ForegroundColor White
    Write-Host '   3. AI Assistant will connect automatically' -ForegroundColor White
    Write-Host ''
    Write-Host '🌐 Dashboard: ' -NoNewline -ForegroundColor Cyan
    Write-Host \"$BackendURL/dashboard\" -ForegroundColor Cyan
    Write-Host ''
    Write-Host '   Press any key to exit...' -ForegroundColor Gray
    $null = $Host.UI.RawUI.ReadKey('NoEcho,IncludeKeyDown')

} catch {
    Write-Host ''
    Write-Host '================================================' -ForegroundColor Red
    Write-Host '❌ INSTALLATION FAILED' -ForegroundColor Red
    Write-Host '================================================' -ForegroundColor Red
    Write-Host ''
    Write-Host 'Error: ' -NoNewline -ForegroundColor Yellow
    Write-Host $_.Exception.Message -ForegroundColor Yellow
    Write-Host ''
    Write-Host '🔍 Debug Info:' -ForegroundColor Cyan
    Write-Host '   Download URL: ' -NoNewline -ForegroundColor Gray
    Write-Host $DownloadURL -ForegroundColor Gray
    Write-Host '   Temp ZIP: ' -NoNewline -ForegroundColor Gray
    Write-Host $TempZip -ForegroundColor Gray
    Write-Host '   Target: ' -NoNewline -ForegroundColor Gray
    Write-Host $TargetPath -ForegroundColor Gray

    if (Test-Path $TempZip) {
        $zipSize = (Get-Item $TempZip).Length
        Write-Host '   Downloaded file size: ' -NoNewline -ForegroundColor Gray
        Write-Host \"$zipSize bytes\" -ForegroundColor Gray
    }

    Write-Host ''
    Write-Host '   Press any key to exit...' -ForegroundColor Gray
    $null = $Host.UI.RawUI.ReadKey('NoEcho,IncludeKeyDown')
    exit 1
}
'@; $script | Out-File -FilePath '%PS_INSTALLER%' -Encoding UTF8"

if not exist "%PS_INSTALLER%" (
    color 0C
    echo ERROR: Failed to create installer script
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