# Test adding a transaction to the blockchain
# Run this after starting at least one node

Write-Host "🧪 Testing Blockchain Transaction" -ForegroundColor Cyan
Write-Host ""

$nodeUrl = "http://localhost:3010"

# Test 1: Add Transaction
Write-Host "📝 Adding transaction to Node 1..." -ForegroundColor Yellow

$transaction = @{
    from = "farmer1"
    to = "buyer1"
    amount = 5000
    crop = "Wheat"
    quantity = "100 kg"
    location = "Mandi ABC"
} | ConvertTo-Json

try {
    $response = Invoke-RestMethod -Uri "$nodeUrl/transaction/add" -Method Post -Body $transaction -ContentType "application/json"
    
    Write-Host "✅ Transaction added successfully!" -ForegroundColor Green
    Write-Host "   Block Hash: $($response.blockHash)" -ForegroundColor Cyan
    Write-Host "   Block Index: $($response.blockIndex)" -ForegroundColor Cyan
    Write-Host "   Transaction ID: $($response.transactionId)" -ForegroundColor Cyan
    
    if ($response.distributed) {
        Write-Host "   📡 Broadcasted to network: $($response.broadcasted)" -ForegroundColor Green
    }
} catch {
    Write-Host "❌ Failed to add transaction" -ForegroundColor Red
    Write-Host "   Error: $($_.Exception.Message)" -ForegroundColor Red
    exit 1
}

Write-Host ""

# Test 2: Get Blockchain Stats
Write-Host "📊 Getting blockchain statistics..." -ForegroundColor Yellow

try {
    $stats = Invoke-RestMethod -Uri "$nodeUrl/stats" -Method Get
    
    Write-Host "✅ Blockchain Stats:" -ForegroundColor Green
    Write-Host "   Total Blocks: $($stats.stats.totalBlocks)" -ForegroundColor Cyan
    Write-Host "   Total Transactions: $($stats.stats.totalTransactions)" -ForegroundColor Cyan
    Write-Host "   Chain Valid: $($stats.stats.chainValid)" -ForegroundColor Cyan
    
    if ($stats.stats.distributed.enabled) {
        Write-Host "   🌐 Distributed Mode: Enabled" -ForegroundColor Green
        Write-Host "   Connected Peers: $($stats.stats.distributed.connectedPeers)" -ForegroundColor Cyan
        Write-Host "   Validators: $($stats.stats.distributed.validators)" -ForegroundColor Cyan
    }
} catch {
    Write-Host "❌ Failed to get stats" -ForegroundColor Red
    Write-Host "   Error: $($_.Exception.Message)" -ForegroundColor Red
}

Write-Host ""

# Test 3: View Blockchain
Write-Host "⛓️  Viewing blockchain..." -ForegroundColor Yellow

try {
    $blockchain = Invoke-RestMethod -Uri "$nodeUrl/chain" -Method Get
    
    Write-Host "✅ Blockchain retrieved:" -ForegroundColor Green
    Write-Host "   Total Blocks: $($blockchain.length)" -ForegroundColor Cyan
    Write-Host "   Latest Block Hash: $($blockchain.latestBlockHash)" -ForegroundColor Cyan
    Write-Host "   Chain Valid: $($blockchain.isValid)" -ForegroundColor Cyan
} catch {
    Write-Host "❌ Failed to get blockchain" -ForegroundColor Red
    Write-Host "   Error: $($_.Exception.Message)" -ForegroundColor Red
}

Write-Host ""
Write-Host "✅ Testing complete!" -ForegroundColor Green
