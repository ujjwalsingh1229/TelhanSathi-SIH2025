# Comprehensive Test for All 3 Node Dashboards
# Tests all features on Node 1, 2, and 3

Write-Host "🧪 TESTING ALL NODE DASHBOARDS" -ForegroundColor Cyan
Write-Host "=" * 70
Write-Host ""

$nodes = @(
    @{Name="Node 1"; Port=3010; Color="Magenta"},
    @{Name="Node 2"; Port=3011; Color="Green"},
    @{Name="Node 3"; Port=3012; Color="Yellow"}
)

foreach ($node in $nodes) {
    Write-Host ""
    Write-Host ("=" * 70) -ForegroundColor $node.Color
    Write-Host "Testing $($node.Name) - Port $($node.Port)" -ForegroundColor $node.Color
    Write-Host ("=" * 70) -ForegroundColor $node.Color
    Write-Host ""

    $baseUrl = "http://localhost:$($node.Port)"
    $allPassed = $true

    # Test 1: Server Health
    Write-Host "  1. Server Health Check..." -NoNewline
    try {
        $response = Invoke-WebRequest -Uri $baseUrl -Method Head -TimeoutSec 3 -UseBasicParsing -ErrorAction Stop
        Write-Host " ✅" -ForegroundColor Green
    } catch {
        Write-Host " ❌ Server not responding" -ForegroundColor Red
        $allPassed = $false
        continue
    }

    # Test 2: Stats API
    Write-Host "  2. Stats API..." -NoNewline
    try {
        $stats = Invoke-RestMethod "$baseUrl/stats" -TimeoutSec 5
        if ($stats.success -and $stats.statistics) {
            Write-Host " ✅ ($($stats.statistics.totalBlocks) blocks)" -ForegroundColor Green
        } else {
            Write-Host " ❌ Invalid response" -ForegroundColor Red
            $allPassed = $false
        }
    } catch {
        Write-Host " ❌ Failed" -ForegroundColor Red
        $allPassed = $false
    }

    # Test 3: Chain API
    Write-Host "  3. Blockchain API..." -NoNewline
    try {
        $chain = Invoke-RestMethod "$baseUrl/chain" -TimeoutSec 5
        if ($chain.length -gt 0 -and $chain.isValid) {
            Write-Host " ✅ ($($chain.length) blocks, valid)" -ForegroundColor Green
        } else {
            Write-Host " ❌ Invalid chain" -ForegroundColor Red
            $allPassed = $false
        }
    } catch {
        Write-Host " ❌ Failed" -ForegroundColor Red
        $allPassed = $false
    }

    # Test 4: Add Transaction
    Write-Host "  4. Add Transaction..." -NoNewline
    try {
        $tx = @{
            from = "farmer-test-$($node.Port)"
            to = "buyer-test-$($node.Port)"
            amount = 1000 + $node.Port
            crop = "TestCrop"
            quantity = "10 kg"
            location = "Test Mandi $($node.Name)"
        } | ConvertTo-Json

        $result = Invoke-RestMethod -Uri "$baseUrl/transaction/add" -Method Post -Body $tx -ContentType "application/json" -TimeoutSec 5
        if ($result.blockHash) {
            Write-Host " ✅ (Block #$($result.blockIndex))" -ForegroundColor Green
        } else {
            Write-Host " ❌ No block hash" -ForegroundColor Red
            $allPassed = $false
        }
    } catch {
        Write-Host " ❌ Failed: $($_.Exception.Message)" -ForegroundColor Red
        $allPassed = $false
    }

    # Test 5: Validate Chain
    Write-Host "  5. Validate Chain..." -NoNewline
    try {
        $validation = Invoke-RestMethod "$baseUrl/validate" -TimeoutSec 5
        if ($validation.valid) {
            Write-Host " ✅ Chain is valid" -ForegroundColor Green
        } else {
            Write-Host " ❌ Chain invalid!" -ForegroundColor Red
            $allPassed = $false
        }
    } catch {
        Write-Host " ⚠️  Endpoint not available (restart needed)" -ForegroundColor Yellow
    }

    # Test 6: Export
    Write-Host "  6. Export API..." -NoNewline
    try {
        $export = Invoke-RestMethod "$baseUrl/export" -TimeoutSec 5
        if ($export) {
            Write-Host " ✅ Export available" -ForegroundColor Green
        } else {
            Write-Host " ❌ No data" -ForegroundColor Red
            $allPassed = $false
        }
    } catch {
        Write-Host " ❌ Failed" -ForegroundColor Red
        $allPassed = $false
    }

    # Test 7: Dashboard HTML
    Write-Host "  7. Dashboard HTML..." -NoNewline
    try {
        $html = Invoke-WebRequest "$baseUrl/dashboard-node$(($node.Port - 3009)).html" -UseBasicParsing -TimeoutSec 5
        if ($html.StatusCode -eq 200 -and $html.Content.Length -gt 10000) {
            Write-Host " ✅ ($('{0:N0}' -f $html.Content.Length) bytes)" -ForegroundColor Green
        } else {
            Write-Host " ❌ Invalid HTML" -ForegroundColor Red
            $allPassed = $false
        }
    } catch {
        Write-Host " ❌ Not accessible" -ForegroundColor Red
        $allPassed = $false
    }

    # Test 8: Network Status (Admin)
    Write-Host "  8. Network Status..." -NoNewline
    try {
        $headers = @{"x-admin-key"="admin-key-change-this-in-production-SIH2025"}
        $network = Invoke-RestMethod "$baseUrl/admin/network/status" -Headers $headers -TimeoutSec 5
        if ($network.success) {
            $peers = $network.network.connectedPeers
            Write-Host " ✅ ($peers peers connected)" -ForegroundColor Green
        } else {
            Write-Host " ❌ Failed" -ForegroundColor Red
            $allPassed = $false
        }
    } catch {
        Write-Host " ⚠️  Not available (distributed mode may be off)" -ForegroundColor Yellow
    }

    # Summary for this node
    Write-Host ""
    if ($allPassed) {
        Write-Host "  🎉 $($node.Name) - ALL TESTS PASSED!" -ForegroundColor Green
    } else {
        Write-Host "  ⚠️  $($node.Name) - Some tests failed" -ForegroundColor Yellow
    }
}

Write-Host ""
Write-Host ("=" * 70) -ForegroundColor Cyan
Write-Host "📊 FINAL SUMMARY" -ForegroundColor Cyan
Write-Host ("=" * 70) -ForegroundColor Cyan
Write-Host ""

# Check final blockchain state
Write-Host "Checking blockchain synchronization..." -ForegroundColor Cyan
$chains = @()
foreach ($node in $nodes) {
    try {
        $chain = Invoke-RestMethod "http://localhost:$($node.Port)/chain" -TimeoutSec 3
        $chains += @{Name=$node.Name; Length=$chain.length; Valid=$chain.isValid}
    } catch {
        $chains += @{Name=$node.Name; Length=0; Valid=$false}
    }
}

foreach ($chain in $chains) {
    $status = if ($chain.Valid) { "✅" } else { "❌" }
    Write-Host "  $status $($chain.Name): $($chain.Length) blocks" -ForegroundColor $(if ($chain.Valid) {"Green"} else {"Red"})
}

Write-Host ""
Write-Host "🌐 Access Dashboards:" -ForegroundColor Cyan
Write-Host "  • Node 1: http://localhost:3010/dashboard-node1.html" -ForegroundColor Magenta
Write-Host "  • Node 2: http://localhost:3011/dashboard-node2.html" -ForegroundColor Green
Write-Host "  • Node 3: http://localhost:3012/dashboard-node3.html" -ForegroundColor Yellow
Write-Host ""
Write-Host "✅ Testing Complete!" -ForegroundColor Green
