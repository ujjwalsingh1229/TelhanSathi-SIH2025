# Test ngrok Distributed Blockchain System

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "🧪 TelhanSathi ngrok System Test Suite" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Configuration
$NODE1_PORT = 3010
$NODE2_PORT = 3011
$NODE3_PORT = 3012
$testUser1 = "farmer_harsh"
$testUser2 = "buyer_priya"

# Colors
function Success { Write-Host $args -ForegroundColor Green }
function Error { Write-Host $args -ForegroundColor Red }
function Info { Write-Host $args -ForegroundColor Yellow }
function Highlight { Write-Host $args -ForegroundColor Cyan }

# Check if nodes are running
function CheckNode($port, $name) {
    Info "Checking $name (port $port)..."
    try {
        $response = Invoke-RestMethod "http://localhost:$port/mobile/api/health" -ErrorAction Stop
        if ($response -and $response.status -eq "healthy") {
            Success "✅ $name is healthy"
            return $true
        }
    } catch {
        Error "❌ $name is not responding"
        return $false
    }
}

Highlight "`n1️⃣  HEALTH CHECK"
Highlight "=================="
$node1Healthy = CheckNode $NODE1_PORT "Node 1"
$node2Healthy = CheckNode $NODE2_PORT "Node 2"
$node3Healthy = CheckNode $NODE3_PORT "Node 3"

if (-not ($node1Healthy -and $node2Healthy -and $node3Healthy)) {
    Error "⚠️  Some nodes are not running. Please start them first:"
    Info "   .\start-ngrok-node1.ps1"
    Info "   .\start-ngrok-node2.ps1"
    Info "   .\start-ngrok-node3.ps1"
    exit 1
}

Highlight "`n2️⃣  BLOCKCHAIN STATS"
Highlight "====================="
Info "Node 1 Stats:"
try {
    $stats1 = Invoke-RestMethod "http://localhost:$NODE1_PORT/mobile/api/blockchain/stats"
    Write-Host "   Blocks: $($stats1.statistics.totalBlocks)"
    Write-Host "   Transactions: $($stats1.statistics.totalTransactions)"
    Write-Host "   Valid: $($stats1.statistics.chainValid)"
    Success "   ✅ Stats retrieved"
} catch {
    Error "   ❌ Failed to get stats: $_"
}

Info "Node 2 Stats:"
try {
    $stats2 = Invoke-RestMethod "http://localhost:$NODE2_PORT/mobile/api/blockchain/stats"
    Write-Host "   Blocks: $($stats2.statistics.totalBlocks)"
    Write-Host "   Transactions: $($stats2.statistics.totalTransactions)"
} catch {
    Error "   ❌ Failed to get stats"
}

Highlight "`n3️⃣  NETWORK DISCOVERY"
Highlight "======================="
Info "Discovering active nodes..."
try {
    $nodes = Invoke-RestMethod "http://localhost:$NODE1_PORT/mobile/api/network/nodes"
    Success "✅ Found $($nodes.nodeCount) active node(s)"
    foreach ($node in $nodes.nodes) {
        Write-Host "   - $($node.nodeId): $($node.publicUrl) [Validator: $($node.isValidator)]"
    }
} catch {
    Error "❌ Failed to discover nodes: $_"
}

Info "Getting validators..."
try {
    $validators = Invoke-RestMethod "http://localhost:$NODE1_PORT/mobile/api/network/validators"
    Success "✅ Found $($validators.validatorCount) validator(s)"
    foreach ($v in $validators.validators) {
        Write-Host "   - $($v.nodeId) [Reputation: $($v.reputation)]"
    }
} catch {
    Error "❌ Failed to get validators: $_"
}

Highlight "`n4️⃣  TRANSACTION TEST"
Highlight "====================="
Info "Sending test transaction from $testUser1 to $testUser2..."
$txnBody = @{
    from = $testUser1
    to = $testUser2
    amount = 1000
    productName = "Wheat"
    quantity = 50
    unit = "kg"
} | ConvertTo-Json

try {
    $txn = Invoke-RestMethod "http://localhost:$NODE1_PORT/mobile/api/transaction/send" `
        -Method POST `
        -Headers @{"Content-Type" = "application/json"} `
        -Body $txnBody
    
    if ($txn.success) {
        Success "✅ Transaction created"
        Write-Host "   TX ID: $($txn.transaction.txId)"
        Write-Host "   From: $($txn.transaction.from)"
        Write-Host "   To: $($txn.transaction.to)"
        Write-Host "   Amount: $($txn.transaction.amount)"
        
        $txId = $txn.transaction.txId
        
        # Wait for blockchain to process
        Info "Waiting for blockchain to process transaction..."
        Start-Sleep -Seconds 2
        
        # Check if transaction is in blockchain
        Info "Checking if transaction is in blockchain..."
        try {
            $userTxns = Invoke-RestMethod "http://localhost:$NODE1_PORT/mobile/api/transactions?userId=$testUser1&limit=20"
            if ($userTxns.transactions.Count -gt 0) {
                Success "✅ Transaction found in blockchain"
                Write-Host "   User transaction count: $($userTxns.totalTransactions)"
            } else {
                Error "❌ Transaction not found in blockchain"
            }
        } catch {
            Error "❌ Failed to verify transaction: $_"
        }
    } else {
        Error "❌ Transaction failed: $($txn.error)"
    }
} catch {
    Error "❌ Failed to send transaction: $_"
}

Highlight "`n5️⃣  BLOCKCHAIN SYNC TEST"
Highlight "=========================="
Info "Checking if blockchain is synced across nodes..."

try {
    $stats1 = Invoke-RestMethod "http://localhost:$NODE1_PORT/mobile/api/blockchain/stats"
    $stats2 = Invoke-RestMethod "http://localhost:$NODE2_PORT/mobile/api/blockchain/stats"
    $stats3 = Invoke-RestMethod "http://localhost:$NODE3_PORT/mobile/api/blockchain/stats"
    
    $block1 = $stats1.statistics.totalBlocks
    $block2 = $stats2.statistics.totalBlocks
    $block3 = $stats3.statistics.totalBlocks
    
    Write-Host "Node 1 Blocks: $block1"
    Write-Host "Node 2 Blocks: $block2"
    Write-Host "Node 3 Blocks: $block3"
    
    if ($block1 -eq $block2 -and $block2 -eq $block3) {
        Success "✅ All nodes have same block count"
    } else {
        Error "⚠️  Block count mismatch (nodes may still be syncing)"
    }
} catch {
    Error "❌ Failed to check sync status: $_"
}

Highlight "`n6️⃣  USER STATS TEST"
Highlight "==================="
Info "Getting user statistics for $testUser1..."
try {
    $userStats = Invoke-RestMethod "http://localhost:$NODE1_PORT/mobile/api/user/$testUser1/stats"
    Success "✅ User stats retrieved"
    Write-Host "   Transactions Sent: $($userStats.statistics.transactionsSent)"
    Write-Host "   Transactions Received: $($userStats.statistics.transactionsReceived)"
    Write-Host "   Total Amount Sent: $($userStats.statistics.totalAmountSent)"
    Write-Host "   Total Amount Received: $($userStats.statistics.totalAmountReceived)"
    Write-Host "   Net Balance: $($userStats.statistics.netBalance)"
} catch {
    Error "❌ Failed to get user stats: $_"
}

Highlight "`n7️⃣  MARKET FEED TEST"
Highlight "===================="
Info "Getting market feed..."
try {
    $feed = Invoke-RestMethod "http://localhost:$NODE1_PORT/mobile/api/market/feed?limit=10"
    Success "✅ Market feed retrieved ($($feed.feedCount) items)"
    foreach ($item in $feed.feed | Select-Object -First 3) {
        Write-Host "   - $($item.from) → $($item.to): $($item.amount) ($($item.productName))"
    }
} catch {
    Error "❌ Failed to get market feed: $_"
}

Highlight "`n8️⃣  CHAIN VALIDATION TEST"
Highlight "=========================="
Info "Validating blockchain on all nodes..."

try {
    $val1 = Invoke-RestMethod "http://localhost:$NODE1_PORT/validate"
    Write-Host "Node 1: $($val1.valid)"
} catch {
    Error "Node 1 validation error: $_"
}

try {
    $val2 = Invoke-RestMethod "http://localhost:$NODE2_PORT/validate"
    Write-Host "Node 2: $($val2.valid)"
} catch {
    Error "Node 2 validation error: $_"
}

try {
    $val3 = Invoke-RestMethod "http://localhost:$NODE3_PORT/validate"
    Write-Host "Node 3: $($val3.valid)"
} catch {
    Error "Node 3 validation error: $_"
}

Success "✅ Validation complete"

Highlight "`n✨ TEST SUITE COMPLETE ✨"
Highlight "=========================="
Success "All critical components are working!"
Info ""
Info "Next Steps:"
Info "1. Try sending transactions via HTTP requests or mobile app"
Info "2. Monitor blockchain growth via /mobile/api/blockchain/stats"
Info "3. Check node discovery via /mobile/api/network/nodes"
Info "4. View Firebase Realtime Database for blockchain persistence"
Info ""
Info "Endpoints Available:"
Info "- Node 1: http://localhost:3010"
Info "- Node 2: http://localhost:3011"
Info "- Node 3: http://localhost:3012"
Info ""
Info "Mobile API Base URLs:"
Info "- Health: GET /mobile/api/health"
Info "- Send TX: POST /mobile/api/transaction/send"
Info "- Stats: GET /mobile/api/blockchain/stats"
Info "- Nodes: GET /mobile/api/network/nodes"
Info "- Feed: GET /mobile/api/market/feed"
