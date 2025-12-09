// ==========================================
// MAIN APPLICATION ENTRY POINT
// ==========================================

// Start server after a short delay to allow async initialization
setTimeout(() => {
    const app = require('./routes');
    const { PORT } = require('./server');

    // Start Server
    app.listen(PORT, () => {
        console.log(`\n${'='.repeat(60)}`);
        console.log(`🌾 TelhanSathi Agricultural Blockchain Network`);
        console.log(`${'='.repeat(60)}`);
        console.log(`📡 Server running on: http://localhost:${PORT}`);
        console.log(`\n📊 Web Dashboard Endpoints:`);
        console.log(`   POST /transaction/add    - Add new transaction`);
        console.log(`   POST /contract/create    - Create new contract`);
        console.log(`   POST /contract/accept    - Buyer accepts contract`);
        console.log(`   POST /contract/deliver   - Record delivery`);
        console.log(`   POST /contract/pay       - Record payment (UPI/Bank)`);
        console.log(`   GET  /contract/:id       - View contract details`);
        console.log(`   GET  /transaction/:id    - View transaction`);
        console.log(`   GET  /user/:id/transactions - User history`);
        console.log(`   GET  /chain              - View entire blockchain`);
        console.log(`   GET  /stats              - Blockchain statistics`);
        console.log(`   GET  /export             - Export blockchain data`);
        console.log(`\n📱 Mobile App API Endpoints:`);
        console.log(`   GET  /api/health         - System health check`);
        console.log(`   GET  /api/mobile/transactions?userId=xxx - User transactions (paginated)`);
        console.log(`   GET  /api/mobile/stats/:userId - User statistics`);
        console.log(`   GET  /api/mobile/verify/:txId - Verify transaction`);
        console.log(`   GET  /api/mobile/feed    - Recent market activity`);
        console.log(`${'='.repeat(60)}\n`);
    }).on('error', (err) => {
        console.error('❌ Server failed to start:', err.message);
        process.exit(1);
    });
}, 2000); // Wait 2 seconds for initialization to complete

