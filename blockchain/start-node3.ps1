# Node 3 - Validator (connects to Node 1)
$env:NODE_ID = "node3"
$env:PORT = "3012"
$env:P2P_PORT = "6003"
$env:ENABLE_DISTRIBUTED = "true"
$env:BOOTSTRAP_NODES = "ws://localhost:6001,node1"

Write-Host "🚀 Starting Node 3 (Validator)" -ForegroundColor Green
Write-Host "   HTTP Port: 3012" -ForegroundColor Cyan
Write-Host "   P2P Port: 6003" -ForegroundColor Cyan
Write-Host "   Connecting to: ws://localhost:6001 (node1)" -ForegroundColor Yellow
Write-Host ""

node app.js
