# Node 1 - Validator
$env:NODE_ID = "node1"
$env:PORT = "3010"
$env:P2P_PORT = "6001"
$env:ENABLE_DISTRIBUTED = "true"

Write-Host "🚀 Starting Node 1 (Validator)" -ForegroundColor Green
Write-Host "   HTTP Port: 3010" -ForegroundColor Cyan
Write-Host "   P2P Port: 6001" -ForegroundColor Cyan
Write-Host ""

node app.js
