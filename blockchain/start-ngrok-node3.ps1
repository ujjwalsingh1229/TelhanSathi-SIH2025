# TelhanSathi Blockchain - ngrok Multi-PC Setup Script
# Node 3 - With ngrok Tunnel

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "🚀 TelhanSathi Blockchain - Node 3 Setup" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Check if ngrok is installed
$ngrokPath = Get-Command ngrok -ErrorAction SilentlyContinue
if (-not $ngrokPath) {
    Write-Host "❌ ngrok not found! Install it with:" -ForegroundColor Red
    Write-Host "   npm install -g ngrok" -ForegroundColor Yellow
    Write-Host "   OR download from https://ngrok.com/download" -ForegroundColor Yellow
    exit 1
}

Write-Host "✅ ngrok found at: $($ngrokPath.Source)" -ForegroundColor Green
Write-Host ""

Write-Host "📋 Configuration:" -ForegroundColor Yellow
Write-Host "   Node ID: node3" 
Write-Host "   HTTP Port: 3012"
Write-Host "   P2P Port: 6003"
Write-Host "   ngrok: ENABLED"
Write-Host "   Distributed Mode: ENABLED"
Write-Host ""

# Check Node.js
$nodeVersion = node -v
Write-Host "✅ Node.js version: $nodeVersion" -ForegroundColor Green

Write-Host ""
Write-Host "🚀 Starting Node 3 with ngrok tunnel..." -ForegroundColor Green
Write-Host ""

# Set environment and start node
$env:NODE_ID = "node3"
$env:PORT = "3012"
$env:P2P_PORT = "6003"
$env:ENABLE_DISTRIBUTED = "true"
$env:IS_VALIDATOR = "false"
$env:ENABLE_NGROK = "true"

# Optional: Connect to Node 1 bootstrap
# $env:BOOTSTRAP_NODES = "ws://localhost:6001,node1"

node app.js
