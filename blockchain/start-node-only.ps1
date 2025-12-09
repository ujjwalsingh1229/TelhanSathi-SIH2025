# ==========================================
# START BLOCKCHAIN NODE ONLY
# ==========================================
# This script ONLY starts the node
# User should start ngrok tunnel in separate terminal first

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "🚀 TelhanSathi Blockchain - Node 1" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Check Node.js
$nodeVersion = node --version
if ($LASTEXITCODE -ne 0) {
    Write-Host "❌ Node.js not found!" -ForegroundColor Red
    Write-Host "Install from: https://nodejs.org/" -ForegroundColor Yellow
    exit 1
}

Write-Host "✅ Node.js version: $nodeVersion" -ForegroundColor Green
Write-Host ""

# Check if in correct directory
if (-not (Test-Path "package.json")) {
    Write-Host "❌ package.json not found!" -ForegroundColor Red
    Write-Host "Make sure you're in the blockchain folder" -ForegroundColor Yellow
    exit 1
}

Write-Host "📋 Checking dependencies..." -ForegroundColor Yellow
$packages = @("express", "dotenv", "ws", "axios", "firebase")
$missing = @()

foreach ($pkg in $packages) {
    if (-not (Test-Path "node_modules/$pkg")) {
        $missing += $pkg
    }
}

if ($missing.Count -gt 0) {
    Write-Host "⚠️  Missing packages: $($missing -join ', ')" -ForegroundColor Yellow
    Write-Host "Installing dependencies..." -ForegroundColor Cyan
    npm install
    if ($LASTEXITCODE -ne 0) {
        Write-Host "❌ npm install failed!" -ForegroundColor Red
        exit 1
    }
}

Write-Host "✅ All dependencies present" -ForegroundColor Green
Write-Host ""

# Load configuration from .env
Write-Host "📋 Configuration:" -ForegroundColor Yellow

$nodeId = $env:NODE_ID -or "node1"
$port = $env:PORT -or "3010"
$p2pPort = $env:P2P_PORT -or "6001"

Write-Host "   Node ID: $nodeId" -ForegroundColor Cyan
Write-Host "   HTTP Port: $port" -ForegroundColor Cyan
Write-Host "   P2P Port: $p2pPort" -ForegroundColor Cyan
Write-Host ""

Write-Host "💡 IMPORTANT:" -ForegroundColor Yellow
Write-Host "   Make sure ngrok tunnel is running in ANOTHER terminal:" -ForegroundColor Yellow
Write-Host "   > .\start-ngrok-tunnel.ps1" -ForegroundColor Cyan
Write-Host ""

# Set environment variables for this process
$env:ENABLE_NGROK = "false"
$env:ENABLE_DISTRIBUTED = "true"

Write-Host "🚀 Starting blockchain node..." -ForegroundColor Yellow
Write-Host ""

# Start node
node app.js

# If node exits
Write-Host ""
Write-Host "⚠️  Node stopped" -ForegroundColor Yellow
