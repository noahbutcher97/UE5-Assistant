# UE5 AI Assistant - One-Click Installer
# Downloads and installs the client to your UE5 project

param(
    [string]$ProjectPath = "",
    [string]$BackendURL = "https://ue5-assistant-noahbutcher97.replit.app"
)

Write-Host "=" -NoNewline -ForegroundColor Cyan
Write-Host "================================================" -ForegroundColor Cyan
Write-Host "🚀 UE5 AI Assistant - One-Click Installer" -ForegroundColor Cyan
Write-Host "=" -NoNewline -ForegroundColor Cyan
Write-Host "================================================" -ForegroundColor Cyan
Write-Host ""

# Prompt for project path if not provided
if ([string]::IsNullOrWhiteSpace($ProjectPath)) {
    Write-Host "📁 Enter your UE5 project path:" -ForegroundColor Cyan
    Write-Host "   Example: D:\UnrealProjects\5.6\MyProject" -ForegroundColor Gray
    Write-Host "" -NoNewline
    $ProjectPath = Read-Host "   Path"
    Write-Host ""
}

# Validate project path
if (-not (Test-Path $ProjectPath)) {
    Write-Host "❌ Error: Project path not found: $ProjectPath" -ForegroundColor Red
    Write-Host "💡 Make sure the path exists and is correct" -ForegroundColor Yellow
    Write-Host "   Press any key to exit..." -ForegroundColor Gray
    $null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")
    exit 1
}

$TargetPath = Join-Path $ProjectPath "Content\Python\AIAssistant"
$DownloadURL = "$BackendURL/api/download_client"
$TempZip = Join-Path $env:TEMP "ue5_assistant_client.zip"

Write-Host "📁 Project: $ProjectPath" -ForegroundColor White
Write-Host "📥 Download URL: $DownloadURL" -ForegroundColor White
Write-Host "📂 Install to: $TargetPath" -ForegroundColor White
Write-Host ""

try {
    # Download client
    Write-Host "⬇️  Downloading latest client..." -ForegroundColor Yellow
    Invoke-WebRequest -Uri $DownloadURL -OutFile $TempZip -UseBasicParsing
    Write-Host "✅ Downloaded successfully" -ForegroundColor Green
    
    # Extract
    Write-Host "📦 Extracting files..." -ForegroundColor Yellow
    if (Test-Path $TargetPath) {
        Write-Host "⚠️  Existing installation found - backing up..." -ForegroundColor Yellow
        $BackupPath = "$TargetPath.backup_$(Get-Date -Format 'yyyyMMdd_HHmmss')"
        Move-Item $TargetPath $BackupPath -Force
        Write-Host "💾 Backup created: $BackupPath" -ForegroundColor Cyan
    }
    
    Expand-Archive -Path $TempZip -DestinationPath (Join-Path $ProjectPath "Content\Python") -Force
    Write-Host "✅ Files extracted" -ForegroundColor Green
    
    # Cleanup
    Remove-Item $TempZip -Force
    
    # Count files
    $FileCount = (Get-ChildItem -Path $TargetPath -Recurse -File).Count
    
    # Create init_unreal.py for FULLY AUTOMATED startup on next UE5 launch
    Write-Host "🔧 Configuring fully automated startup..." -ForegroundColor Yellow
    
    $PythonDir = Join-Path $ProjectPath "Content\Python"
    $InitUnrealFile = Join-Path $PythonDir "init_unreal.py"
    
    # Create init_unreal.py with our startup configuration
    $InitUnrealScript = @"
# init_unreal.py - UE5 AI Assistant Auto-Startup
# This file is automatically executed by UE5 on editor startup

import unreal

try:
    unreal.log("=" * 60)
    unreal.log("🤖 UE5 AI Assistant - Auto-initializing...")
    unreal.log("=" * 60)
    
    # Import and run auto-configured startup
    import AIAssistant.startup
    AIAssistant.startup.configure_and_start('$BackendURL')
    
except Exception as e:
    unreal.log_error(f"❌ AI Assistant auto-startup failed: {e}")
    unreal.log("💡 Manual start: import AIAssistant.main")
"@
    
    $InitUnrealScript | Out-File -FilePath $InitUnrealFile -Encoding UTF8 -Force
    Write-Host "✅ Created init_unreal.py for automatic startup" -ForegroundColor Green
    
    # Also create manual startup script as backup
    $ManualStartFile = Join-Path $TargetPath "_manual_start.py"
    $ManualScript = @"
# Manual startup script (backup if init_unreal.py doesn't work)
import AIAssistant.startup
AIAssistant.startup.configure_and_start('$BackendURL')
"@
    $ManualScript | Out-File -FilePath $ManualStartFile -Encoding UTF8 -Force
    
    Write-Host ""
    Write-Host "🎉 Fully Automated Installation Complete!" -ForegroundColor Green
    Write-Host ""
    Write-Host "📋 What happens next:" -ForegroundColor Cyan
    Write-Host "   1. Close this installer" -ForegroundColor White
    Write-Host "   2. Launch/Restart your UE5 Editor" -ForegroundColor White
    Write-Host "   3. AI Assistant will AUTO-START automatically!" -ForegroundColor Green
    Write-Host ""
    Write-Host "✨ init_unreal.py will:" -ForegroundColor Cyan
    Write-Host "   • Auto-configure backend: $BackendURL" -ForegroundColor White
    Write-Host "   • Initialize the AI Assistant" -ForegroundColor White
    Write-Host "   • Connect to the dashboard" -ForegroundColor White
    Write-Host "   • Run every time you open this project" -ForegroundColor White
    Write-Host ""
    Write-Host "🔧 Backup (if auto-start doesn't work):" -ForegroundColor Yellow
    Write-Host "   Run in Python Console: exec(open(r'$ManualStartFile').read())" -ForegroundColor Gray
    
    Write-Host ""
    Write-Host "=" -NoNewline -ForegroundColor Green
    Write-Host "================================================" -ForegroundColor Green
    Write-Host "✅ Installation Complete!" -ForegroundColor Green
    Write-Host "=" -NoNewline -ForegroundColor Green
    Write-Host "================================================" -ForegroundColor Green
    Write-Host "📂 Installed $FileCount files to: $TargetPath" -ForegroundColor White
    Write-Host ""
    Write-Host "🌐 Dashboard: https://ue5-assistant-noahbutcher97.replit.app/dashboard" -ForegroundColor Cyan
    Write-Host ""
    Write-Host "   Press any key to exit..." -ForegroundColor Gray
    $null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")
    
} catch {
    Write-Host ""
    Write-Host "❌ Installation failed: $_" -ForegroundColor Red
    Write-Host "   Press any key to exit..." -ForegroundColor Gray
    $null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")
    exit 1
}
