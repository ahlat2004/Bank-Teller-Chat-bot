# Bank Teller Chatbot - Unified Launcher
# Starts both backend server and Flutter frontend
# Usage: ./run_app.ps1 [-device windows|web]

param(
    [string]$device = "windows"
)

$projectRoot = Split-Path -Parent $PSCommandPath
$backendDir = Join-Path $projectRoot "backend" "app"
$frontendDir = Join-Path $projectRoot "frontend" "bank_teller_bot_frontend"
$pythonExe = "C:/Users/talha/AppData/Local/Programs/Python/Python310/python.exe"

Write-Host "╔════════════════════════════════════════════════════════╗" -ForegroundColor Cyan
Write-Host "║   Bank Teller Chatbot - Unified Launcher               ║" -ForegroundColor Cyan
Write-Host "╚════════════════════════════════════════════════════════╝" -ForegroundColor Cyan
Write-Host ""

# Check if backend is already running
Write-Host "🔍 Checking if backend is already running on port 8000..." -ForegroundColor Yellow
$portCheck = netstat -ano | Select-String ":8000"
if ($portCheck) {
    Write-Host "✅ Backend already running on port 8000" -ForegroundColor Green
} else {
    Write-Host "🚀 Starting backend server..." -ForegroundColor Cyan
    Start-Process -FilePath $pythonExe -ArgumentList @(
        "-m", "uvicorn", "main:app",
        "--host", "127.0.0.1",
        "--port", "8000"
    ) -WorkingDirectory $backendDir -WindowStyle Minimized
    
    Write-Host "⏳ Waiting for backend to initialize (5 seconds)..." -ForegroundColor Yellow
    Start-Sleep -Seconds 5
    
    Write-Host "✅ Backend server started!" -ForegroundColor Green
}

Write-Host ""
Write-Host "🚀 Launching Flutter app ($device)..." -ForegroundColor Cyan
Write-Host ""

# Launch Flutter app
Set-Location $frontendDir
& flutter run -d $device
