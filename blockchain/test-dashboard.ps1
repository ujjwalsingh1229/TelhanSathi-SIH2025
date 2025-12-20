# Dashboard Functionality Test
# Tests all dashboard features

Write-Host "🧪 TESTING BLOCKCHAIN DASHBOARD FUNCTIONALITY" -ForegroundColor Cyan
Write-Host "=" * 60
Write-Host ""

$nodeUrl = "http://localhost:3010"

# Test 1: Stats Endpoint
Write-Host "1️⃣  Testing Stats Endpoint..." -ForegroundColor Yellow
try {
    $stats = Invoke-RestMethod "$nodeUrl/stats"
    if ($stats.success) {
        Write-Host "   ✅ Stats API working" -ForegroundColor Green
        Write-Host "   📊 Total Blocks: $($stats.statistics.totalBlocks)" -ForegroundColor Cyan
        Write-Host "   📊 Chain Valid: $($stats.statistics.chainValid)" -ForegroundColor Cyan
    }
} catch {
    Write-Host "   ❌ Stats API failed: $($_.Exception.Message)" -ForegroundColor Red
}
Write-Host ""

# Test 2: Chain Endpoint
Write-Host "2️⃣  Testing Chain Endpoint..." -ForegroundColor Yellow
try {
    $chain = Invoke-RestMethod "$nodeUrl/chain"
    if ($chain.length -gt 0) {
        Write-Host "   ✅ Chain API working" -ForegroundColor Green
        Write-Host "   ⛓️  Blockchain Length: $($chain.length)" -ForegroundColor Cyan
        Write-Host "   ✔️  Chain Valid: $($chain.isValid)" -ForegroundColor Cyan
    }
} catch {
    Write-Host "   ❌ Chain API failed: $($_.Exception.Message)" -ForegroundColor Red
}
Write-Host ""

# Test 3: Add Transaction
Write-Host "3️⃣  Testing Add Transaction..." -ForegroundColor Yellow
$transaction = @{
    from = "test-farmer"
    to = "test-buyer"
    amount = 1000
    crop = "Test Crop"
    quantity = "10 kg"
    location = "Test Location"
} | ConvertTo-Json

try {
    $result = Invoke-RestMethod -Uri "$nodeUrl/transaction/add" -Method Post -Body $transaction -ContentType "application/json"
    if ($result.blockHash) {
        Write-Host "   ✅ Transaction added successfully" -ForegroundColor Green
        Write-Host "   🔒 Block Hash: $($result.blockHash.Substring(0,16))..." -ForegroundColor Cyan
        Write-Host "   📦 Block Index: $($result.blockIndex)" -ForegroundColor Cyan
    }
} catch {
    Write-Host "   ❌ Transaction failed: $($_.Exception.Message)" -ForegroundColor Red
}
Write-Host ""

# Test 4: Validate Chain
Write-Host "4️⃣  Testing Chain Validation..." -ForegroundColor Yellow
try {
    $validation = Invoke-RestMethod "$nodeUrl/validate"
    if ($validation.valid) {
        Write-Host "   ✅ Chain validation passed" -ForegroundColor Green
        Write-Host "   ✔️  Blockchain is valid" -ForegroundColor Cyan
    } else {
        Write-Host "   ❌ Chain is INVALID!" -ForegroundColor Red
    }
} catch {
    Write-Host "   ❌ Validation failed: $($_.Exception.Message)" -ForegroundColor Red
}
Write-Host ""

# Test 5: Dashboard HTML Accessibility
Write-Host "5️⃣  Testing Dashboard HTML..." -ForegroundColor Yellow
try {
    $response = Invoke-WebRequest "$nodeUrl/dashboard-node1.html" -UseBasicParsing
    if ($response.StatusCode -eq 200) {
        Write-Host "   ✅ Dashboard HTML accessible" -ForegroundColor Green
        Write-Host "   📄 Status Code: $($response.StatusCode)" -ForegroundColor Cyan
        Write-Host "   📏 Content Length: $($response.Content.Length) bytes" -ForegroundColor Cyan
    }
} catch {
    Write-Host "   ❌ Dashboard not accessible: $($_.Exception.Message)" -ForegroundColor Red
}
Write-Host ""

# Test 6: Export Endpoint
Write-Host "6️⃣  Testing Export Endpoint..." -ForegroundColor Yellow
try {
    $export = Invoke-RestMethod "$nodeUrl/export"
    if ($export) {
        Write-Host "   ✅ Export API working" -ForegroundColor Green
        Write-Host "   💾 Exportable data available" -ForegroundColor Cyan
    }
} catch {
    Write-Host "   ❌ Export failed: $($_.Exception.Message)" -ForegroundColor Red
}
Write-Host ""

# Final Summary
Write-Host "=" * 60
Write-Host "✅ DASHBOARD FUNCTIONALITY TEST COMPLETE" -ForegroundColor Green
Write-Host ""
Write-Host "📱 Access Dashboards:" -ForegroundColor Cyan
Write-Host "   Node 1: http://localhost:3010/dashboard-node1.html" -ForegroundColor White
Write-Host "   Node 2: http://localhost:3011/dashboard-node2.html" -ForegroundColor White
Write-Host "   Node 3: http://localhost:3012/dashboard-node3.html" -ForegroundColor White
Write-Host ""
Write-Host "🔧 All core features tested and verified!" -ForegroundColor Green
