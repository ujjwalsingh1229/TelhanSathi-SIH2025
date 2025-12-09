# ==========================================
# START NGROK TUNNEL ONLY
# ==========================================
# This script ONLY starts the ngrok tunnel
# User will start the node in a separate terminal

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "🌐 TelhanSathi Blockchain - ngrok Tunnel" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Check if ngrok is installed
$ngrokPath = Get-Command ngrok -ErrorAction SilentlyContinue
if (-not $ngrokPath) {
    Write-Host "❌ ngrok not found!" -ForegroundColor Red
    Write-Host ""
    Write-Host "Install ngrok from: https://ngrok.com/download" -ForegroundColor Yellow
    Write-Host "OR run: choco install ngrok" -ForegroundColor Yellow
    Write-Host "OR run: npm install -g ngrok" -ForegroundColor Yellow
    exit 1
}

Write-Host "✅ ngrok found at: $($ngrokPath.Source)" -ForegroundColor Green
Write-Host ""

# Load .env file
if (Test-Path ".env") {
    $envContent = Get-Content ".env" -Raw
    $envLines = $envContent -split "`n" | Where-Object { $_ -and -not $_.StartsWith("#") }
    foreach ($line in $envLines) {
        if ($line -match '^\s*([^=]+)=(.*)$') {
            $key = $matches[1].Trim()
            $value = $matches[2].Trim()
            [System.Environment]::SetEnvironmentVariable($key, $value, "Process")
        }
    }
} else {
    Write-Host "⚠️  .env file not found" -ForegroundColor Yellow
    Write-Host "Create one with ngrok token:" -ForegroundColor Yellow
    Write-Host ""
    Write-Host "   NGROK_AUTH_TOKEN=your_token_here" -ForegroundColor Yellow
    exit 1
}

# Check for ngrok token
if (-not $env:NGROK_AUTH_TOKEN) {
    Write-Host "❌ NGROK_AUTH_TOKEN not set in .env" -ForegroundColor Red
    Write-Host ""
    Write-Host "Steps to fix:" -ForegroundColor Yellow
    Write-Host "1. Go to https://dashboard.ngrok.com" -ForegroundColor Cyan
    Write-Host "2. Sign up or login" -ForegroundColor Cyan
    Write-Host "3. Copy your Auth Token" -ForegroundColor Cyan
    Write-Host "4. Add to .env: NGROK_AUTH_TOKEN=your_token_here" -ForegroundColor Cyan
    exit 1
}

Write-Host "📋 Configuration:" -ForegroundColor Yellow
$port = $env:PORT -or "3010"
$region = $env:NGROK_REGION -or "in"
Write-Host "   Local Port: $port" -ForegroundColor Cyan
Write-Host "   ngrok Region: $region" -ForegroundColor Cyan
Write-Host ""

# Authenticate ngrok
Write-Host "🔐 Authenticating with ngrok..." -ForegroundColor Yellow
ngrok authtoken $env:NGROK_AUTH_TOKEN

if ($LASTEXITCODE -ne 0) {
    Write-Host "❌ Authentication failed!" -ForegroundColor Red
    Write-Host "Check your NGROK_AUTH_TOKEN in .env" -ForegroundColor Yellow
    exit 1
}

Write-Host ""
Write-Host "✅ Authentication successful!" -ForegroundColor Green
Write-Host ""

# Start ngrok tunnel
Write-Host "🚀 Starting ngrok tunnel..." -ForegroundColor Yellow
Write-Host "   Exposing: http://localhost:$port" -ForegroundColor Cyan
Write-Host ""

# Run ngrok
ngrok http $port --region=$region

# If ngrok exits
Write-Host ""
Write-Host "⚠️  ngrok tunnel closed" -ForegroundColor Yellow
