# Node 2 - Peer (connects to Node 1)
$env:NODE_ID = "node2"
$env:PORT = "3011"
$env:P2P_PORT = "6002"
$env:ENABLE_DISTRIBUTED = "true"
$env:BOOTSTRAP_NODES = "ws://localhost:6001,node1"

Write-Host "🚀 Starting Node 2 (Peer)" -ForegroundColor Green
Write-Host "   HTTP Port: 3011" -ForegroundColor Cyan
Write-Host "   P2P Port: 6002" -ForegroundColor Cyan
Write-Host "   Connecting to: ws://localhost:6001 (node1)" -ForegroundColor Yellow
Write-Host ""

node app.js
