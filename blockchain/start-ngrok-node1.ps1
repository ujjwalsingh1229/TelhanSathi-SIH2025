# TelhanSathi Blockchain - ngrok Multi-PC Setup Script
# Node 1 - With ngrok Tunnel (Validator)

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "🚀 TelhanSathi Blockchain - Node 1 Setup" -ForegroundColor Cyan
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

# Check for .env file
if (-not (Test-Path ".env")) {
    Write-Host "⚠️  .env file not found. Creating with defaults..." -ForegroundColor Yellow
    @"
# Node Configuration
NODE_ID=node1
PORT=3010
P2P_PORT=6001
IS_VALIDATOR=true

# ngrok Configuration
ENABLE_NGROK=true
NGROK_AUTH_TOKEN=2FJsXEfAwU9gt5pjCvure8ftLmN_3KoCk1HQfshvSLbd8of6X
NGROK_REGION=in

# Firebase Configuration
FIREBASE_API_KEY=AIzaSyAiKojN1cx2x4BsrFN2UI13hvh49KVZxcw
FIREBASE_AUTH_DOMAIN=sih2025-72065.firebaseapp.com
FIREBASE_PROJECT_ID=sih2025-72065
FIREBASE_DATABASE_URL=https://sih2025-72065-default-rtdb.asia-southeast1.firebasedatabase.app

# Distributed Mode
ENABLE_DISTRIBUTED=true

# Bootstrap Nodes (optional - for connecting to other nodes)
# BOOTSTRAP_NODES=ws://node2-public-url:6001,node2;ws://node3-public-url:6001,node3

# JWT Configuration
JWT_SECRET=super-secret-key-change-this
JWT_EXPIRY=24h

# Rate Limiting
RATE_LIMIT_WINDOW_MS=900000
RATE_LIMIT_MAX_REQUESTS=100

# Mining
MINING_DIFFICULTY=2
MINING_REWARD=50
"@ | Out-File ".env" -Encoding UTF8
    Write-Host "✅ .env file created" -ForegroundColor Green
    Write-Host "⚠️  Update NGROK_AUTH_TOKEN in .env file!" -ForegroundColor Yellow
    Write-Host ""
}

Write-Host "📋 Configuration:" -ForegroundColor Yellow
Write-Host "   Node ID: node1" 
Write-Host "   HTTP Port: 3010"
Write-Host "   P2P Port: 6001"
Write-Host "   ngrok: ENABLED"
Write-Host "   Distributed Mode: ENABLED"
Write-Host ""

# Check Node.js
$nodeVersion = node -v
Write-Host "✅ Node.js version: $nodeVersion" -ForegroundColor Green

# Check npm packages
Write-Host ""
Write-Host "Checking npm packages..." -ForegroundColor Yellow
if (-not (Test-Path "node_modules")) {
    Write-Host "Installing dependencies..." -ForegroundColor Cyan
    npm install
}

Write-Host ""
Write-Host "🚀 Starting Node 1 with ngrok tunnel..." -ForegroundColor Green
Write-Host ""

# Set environment and start node
$env:NODE_ID = "node1"
$env:PORT = "3010"
$env:P2P_PORT = "6001"
$env:ENABLE_DISTRIBUTED = "true"
$env:IS_VALIDATOR = "true"
$env:ENABLE_NGROK = "true"

node app.js
