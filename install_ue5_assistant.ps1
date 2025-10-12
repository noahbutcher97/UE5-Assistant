# UE5 AI Assistant - One-Click Installer
# Downloads and installs the client to your UE5 project

param(
    [string]$ProjectPath = "D:/UnrealProjects/5.6/UE5_Assistant",
    [string]$BackendURL = "https://ue5-assistant-noahbutcher97.replit.app"
)

Write-Host "=" -NoNewline -ForegroundColor Cyan
Write-Host "================================================" -ForegroundColor Cyan
Write-Host "🚀 UE5 AI Assistant - One-Click Installer" -ForegroundColor Cyan
Write-Host "=" -NoNewline -ForegroundColor Cyan
Write-Host "================================================" -ForegroundColor Cyan
Write-Host ""

# Validate project path
if (-not (Test-Path $ProjectPath)) {
    Write-Host "❌ Error: Project path not found: $ProjectPath" -ForegroundColor Red
    Write-Host "💡 Usage: .\install_ue5_assistant.ps1 -ProjectPath 'D:\YourProject'" -ForegroundColor Yellow
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
    
    Write-Host ""
    Write-Host "=" -NoNewline -ForegroundColor Green
    Write-Host "================================================" -ForegroundColor Green
    Write-Host "✅ Installation Complete!" -ForegroundColor Green
    Write-Host "=" -NoNewline -ForegroundColor Green
    Write-Host "================================================" -ForegroundColor Green
    Write-Host "📂 Installed $FileCount files to: $TargetPath" -ForegroundColor White
    Write-Host ""
    Write-Host "📋 Next Steps:" -ForegroundColor Cyan
    Write-Host "   1. Open Unreal Editor" -ForegroundColor White
    Write-Host "   2. Open Python Console (Tools → Python Console)" -ForegroundColor White
    Write-Host "   3. Run: import AIAssistant.main" -ForegroundColor White
    Write-Host "   4. Check Output Log for registration confirmation" -ForegroundColor White
    Write-Host ""
    Write-Host "🌐 Optional - Enable Command Center:" -ForegroundColor Cyan
    Write-Host "   Run: import AIAssistant.local_server" -ForegroundColor White
    Write-Host "   Then: AIAssistant.local_server.start_server()" -ForegroundColor White
    Write-Host ""
    
} catch {
    Write-Host ""
    Write-Host "❌ Installation failed: $_" -ForegroundColor Red
    exit 1
}
