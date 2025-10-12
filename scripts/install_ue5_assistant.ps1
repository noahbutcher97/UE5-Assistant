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
$DownloadURL = "$BackendURL/api/download_client_bundle"
$TempZip = Join-Path $env:TEMP "ue5_assistant_client.zip"

Write-Host "📁 Project: $ProjectPath" -ForegroundColor White
Write-Host "📥 Download URL: $DownloadURL (POST - bypasses cache)" -ForegroundColor White
Write-Host "📂 Install to: $TargetPath" -ForegroundColor White
Write-Host ""

try {
    # Download client using POST to bypass CDN cache
    Write-Host "⬇️  Downloading latest client..." -ForegroundColor Yellow
    Write-Host "   Source: $DownloadURL (POST method)" -ForegroundColor Gray
    
    $DownloadStartTime = Get-Date
    Invoke-WebRequest -Uri $DownloadURL -Method Post -OutFile $TempZip -UseBasicParsing
    $DownloadDuration = (Get-Date) - $DownloadStartTime
    $FileSize = (Get-Item $TempZip).Length
    $FileSizeMB = [math]::Round($FileSize / 1MB, 2)
    
    Write-Host "✅ Downloaded: $FileSizeMB MB in $($DownloadDuration.TotalSeconds.ToString('0.0'))s" -ForegroundColor Green
    Write-Host "   Saved to: $TempZip" -ForegroundColor Gray
    
    # Extract
    Write-Host ""
    Write-Host "📦 Extracting files..." -ForegroundColor Yellow
    
    # Backup existing installation
    if (Test-Path $TargetPath) {
        Write-Host "⚠️  Existing installation found!" -ForegroundColor Yellow
        $OldFiles = (Get-ChildItem -Path $TargetPath -Recurse -File).Count
        Write-Host "   Old installation has $OldFiles files" -ForegroundColor Gray
        
        $BackupPath = "$TargetPath.backup_$(Get-Date -Format 'yyyyMMdd_HHmmss')"
        Write-Host "   Creating backup..." -ForegroundColor Yellow
        Move-Item $TargetPath $BackupPath -Force
        Write-Host "💾 Backup created: $BackupPath" -ForegroundColor Cyan
        Write-Host "   (You can delete this backup folder after confirming the new installation works)" -ForegroundColor Gray
    } else {
        Write-Host "   No existing installation found - fresh install" -ForegroundColor Gray
    }
    
    Write-Host ""
    Write-Host "   Extracting to: $(Join-Path $ProjectPath 'Content\Python')" -ForegroundColor Gray
    Expand-Archive -Path $TempZip -DestinationPath (Join-Path $ProjectPath "Content\Python") -Force
    
    # Count and list files
    $AllFiles = Get-ChildItem -Path $TargetPath -Recurse -File
    $FileCount = $AllFiles.Count
    Write-Host "✅ Extracted $FileCount files successfully" -ForegroundColor Green
    
    # Show file categories
    $PythonFiles = ($AllFiles | Where-Object {$_.Extension -eq ".py"}).Count
    $ConfigFiles = ($AllFiles | Where-Object {$_.Name -like "*.json" -or $_.Name -like "*.txt"}).Count
    $OtherFiles = $FileCount - $PythonFiles - $ConfigFiles
    
    Write-Host ""
    Write-Host "   📄 File breakdown:" -ForegroundColor Cyan
    Write-Host "      • Python files (.py): $PythonFiles" -ForegroundColor White
    Write-Host "      • Config files (.json, .txt): $ConfigFiles" -ForegroundColor White
    Write-Host "      • Other files: $OtherFiles" -ForegroundColor White
    
    # List key files
    Write-Host ""
    Write-Host "   🔑 Key modules installed:" -ForegroundColor Cyan
    $KeyModules = @("main.py", "startup.py", "config.py", "auto_update.py", "websocket_client.py", "http_polling_client.py")
    foreach ($module in $KeyModules) {
        $exists = Test-Path (Join-Path $TargetPath $module)
        if ($exists) {
            Write-Host "      ✅ $module" -ForegroundColor Green
        } else {
            Write-Host "      ❌ $module (MISSING!)" -ForegroundColor Red
        }
    }
    
    # Cleanup
    Write-Host ""
    Write-Host "🧹 Cleaning up..." -ForegroundColor Yellow
    Remove-Item $TempZip -Force
    Write-Host "   Deleted temporary file: $TempZip" -ForegroundColor Gray
    
    # Create init_unreal.py for FULLY AUTOMATED startup on next UE5 launch
    Write-Host ""
    Write-Host "🔧 Configuring fully automated startup..." -ForegroundColor Yellow
    Write-Host ""
    
    $PythonDir = Join-Path $ProjectPath "Content\Python"
    $InitUnrealFile = Join-Path $PythonDir "init_unreal.py"
    
    Write-Host "   📝 Creating init_unreal.py..." -ForegroundColor Cyan
    Write-Host "      Location: $InitUnrealFile" -ForegroundColor Gray
    Write-Host "      Backend URL: $BackendURL" -ForegroundColor Gray
    
    # Check if init_unreal.py already exists
    if (Test-Path $InitUnrealFile) {
        Write-Host "      ⚠️  Overwriting existing init_unreal.py" -ForegroundColor Yellow
    }
    
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
    
    # Verify file was created
    if (Test-Path $InitUnrealFile) {
        $InitFileSize = (Get-Item $InitUnrealFile).Length
        Write-Host "      ✅ init_unreal.py created successfully ($InitFileSize bytes)" -ForegroundColor Green
    } else {
        Write-Host "      ❌ ERROR: Failed to create init_unreal.py!" -ForegroundColor Red
        throw "Failed to create init_unreal.py"
    }
    
    # Also create manual startup script as backup
    Write-Host ""
    Write-Host "   📝 Creating backup manual startup script..." -ForegroundColor Cyan
    $ManualStartFile = Join-Path $TargetPath "_manual_start.py"
    Write-Host "      Location: $ManualStartFile" -ForegroundColor Gray
    
    $ManualScript = @"
# Manual startup script (backup if init_unreal.py doesn't work)
import AIAssistant.startup
AIAssistant.startup.configure_and_start('$BackendURL')
"@
    $ManualScript | Out-File -FilePath $ManualStartFile -Encoding UTF8 -Force
    
    if (Test-Path $ManualStartFile) {
        $ManualFileSize = (Get-Item $ManualStartFile).Length
        Write-Host "      ✅ _manual_start.py created successfully ($ManualFileSize bytes)" -ForegroundColor Green
    } else {
        Write-Host "      ⚠️  Warning: Failed to create backup script" -ForegroundColor Yellow
    }
    
    # Verify configuration
    Write-Host ""
    Write-Host "   🔍 Verifying installation..." -ForegroundColor Cyan
    
    $VerificationChecks = @(
        @{Name = "AIAssistant module directory"; Path = $TargetPath},
        @{Name = "init_unreal.py (auto-startup)"; Path = $InitUnrealFile},
        @{Name = "main.py (core module)"; Path = (Join-Path $TargetPath "main.py")},
        @{Name = "startup.py (configuration)"; Path = (Join-Path $TargetPath "startup.py")},
        @{Name = "config.py (settings)"; Path = (Join-Path $TargetPath "config.py")}
    )
    
    $AllChecksPassed = $true
    foreach ($check in $VerificationChecks) {
        if (Test-Path $check.Path) {
            Write-Host "      ✅ $($check.Name)" -ForegroundColor Green
        } else {
            Write-Host "      ❌ $($check.Name) - MISSING!" -ForegroundColor Red
            $AllChecksPassed = $false
        }
    }
    
    if ($AllChecksPassed) {
        Write-Host ""
        Write-Host "   ✅ All verification checks passed!" -ForegroundColor Green
    } else {
        Write-Host ""
        Write-Host "   ⚠️  Some files are missing - installation may be incomplete!" -ForegroundColor Yellow
    }
    
    Write-Host ""
    Write-Host "=" -NoNewline -ForegroundColor Green
    Write-Host "================================================" -ForegroundColor Green
    Write-Host "🎉 INSTALLATION COMPLETE!" -ForegroundColor Green
    Write-Host "=" -NoNewline -ForegroundColor Green
    Write-Host "================================================" -ForegroundColor Green
    Write-Host ""
    
    # Installation Summary
    Write-Host "📊 Installation Summary:" -ForegroundColor Cyan
    Write-Host "   Project: $ProjectPath" -ForegroundColor White
    Write-Host "   Files Installed: $FileCount" -ForegroundColor White
    Write-Host "      • Python modules: $PythonFiles" -ForegroundColor Gray
    Write-Host "      • Config files: $ConfigFiles" -ForegroundColor Gray
    Write-Host "   Backend URL: $BackendURL" -ForegroundColor White
    Write-Host "   Auto-startup: ✅ ENABLED (init_unreal.py)" -ForegroundColor Green
    Write-Host ""
    
    # Files Created
    Write-Host "📁 Key Files Created:" -ForegroundColor Cyan
    Write-Host "   ✅ $InitUnrealFile" -ForegroundColor Green
    Write-Host "      → Auto-executes on UE5 startup" -ForegroundColor Gray
    Write-Host "   ✅ $TargetPath" -ForegroundColor Green
    Write-Host "      → AIAssistant module ($FileCount files)" -ForegroundColor Gray
    Write-Host "   ✅ $ManualStartFile" -ForegroundColor Green
    Write-Host "      → Backup manual startup script" -ForegroundColor Gray
    
    if (Test-Path $BackupPath) {
        Write-Host "   📦 $BackupPath" -ForegroundColor Cyan
        Write-Host "      → Old installation backup" -ForegroundColor Gray
    }
    
    Write-Host ""
    Write-Host "🚀 Next Steps:" -ForegroundColor Cyan
    Write-Host "   1. Close this installer" -ForegroundColor White
    Write-Host "   2. Launch/Restart your UE5 Editor" -ForegroundColor White
    Write-Host "   3. Watch for auto-startup in Output Log!" -ForegroundColor Green
    Write-Host ""
    Write-Host "✨ What Will Happen Automatically:" -ForegroundColor Cyan
    Write-Host "   • UE5 executes: Content/Python/init_unreal.py" -ForegroundColor White
    Write-Host "   • Backend configured: $BackendURL" -ForegroundColor White
    Write-Host "   • AI Assistant initializes" -ForegroundColor White
    Write-Host "   • Dashboard connection established" -ForegroundColor White
    Write-Host "   • Runs every time you open this project" -ForegroundColor White
    Write-Host ""
    Write-Host "🔧 Troubleshooting (if auto-start fails):" -ForegroundColor Yellow
    Write-Host "   1. Check UE5 Output Log for Python errors" -ForegroundColor Gray
    Write-Host "   2. Verify Python Plugin is enabled in UE5" -ForegroundColor Gray
    Write-Host "   3. Manual backup command:" -ForegroundColor Gray
    Write-Host "      exec(open(r'$ManualStartFile').read())" -ForegroundColor White
    Write-Host ""
    Write-Host "🌐 Dashboard: https://ue5-assistant-noahbutcher97.replit.app/dashboard" -ForegroundColor Cyan
    
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
