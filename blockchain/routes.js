// ==========================================
// API ROUTES MODULE - DISTRIBUTED VERSION
// ==========================================
const jwt = require('jsonwebtoken');
const {
    app,
    telhanChain,
    distributedCoordinator,
    schemas,
    validateInput,
    authenticateToken,
    optionalAuth,
    sanitizeString,
    JWT_SECRET,
    JWT_EXPIRY,
    NODE_ID,
    ENABLE_DISTRIBUTED,
    Block
} = require('./server');
const { saveToFirebase, loadFromFirebase } = require('./firebase');
const { verifySignature } = require('./blockchain');
const NodeRegistry = require('./nodeRegistry');

// ==========================================
// AUTHENTICATION ENDPOINTS
// ==========================================

app.post('/auth/login', (req, res) => {
    const { userId, role, name } = req.body;

    if (!userId || !role) {
        return res.status(400).json({ error: 'userId and role required' });
    }

    const user = {
        userId: sanitizeString(userId),
        role: role,
        name: sanitizeString(name || userId)
    };

    const token = jwt.sign(user, JWT_SECRET, { expiresIn: JWT_EXPIRY });

    console.log(`✅ JWT issued for user: ${userId} (${role})`);
    res.json({
        success: true,
        token,
        user,
        expiresIn: JWT_EXPIRY
    });
});

app.get('/auth/verify', authenticateToken, (req, res) => {
    res.json({
        valid: true,
        user: req.user
    });
});

// ==========================================
// PUBLIC ENDPOINTS
// ==========================================

app.get('/', (req, res) => {
    res.sendFile(__dirname + '/index.html');
});

app.get('/chain', (req, res) => {
    console.log('🔗 GET /chain - Request received');
    res.json({
        length: telhanChain.chain.length,
        isValid: telhanChain.isChainValid(),
        chain: telhanChain.chain
    });
});

// ==========================================
// TRANSACTION ENDPOINTS
// ==========================================

app.post('/transaction/add', validateInput(schemas.transaction), optionalAuth, async (req, res) => {
    console.log('\n' + '='.repeat(60));
    console.log('📥 NEW TRANSACTION REQUEST');
    console.log('='.repeat(60));

    const { from, to, amount, crop, quantity, upiTransactionId, location, signature, senderPublicKey } = req.validatedBody;

    const transactionId = upiTransactionId || `TXN-${Date.now()}`;
    const contractId = `CONTRACT-${Date.now()}`;

    const transactionData = {
        transactionId,
        contractId,
        action: "DIRECT_PAYMENT",
        from: sanitizeString(from),
        to: sanitizeString(to),
        crop: sanitizeString(crop) || 'General',
        quantity: sanitizeString(quantity) || '-',
        amount: parseFloat(amount),
        upiTransactionId: sanitizeString(upiTransactionId || ''),
        location: sanitizeString(location) || '-',
        payload: {
            amount: parseFloat(amount),
            crop: sanitizeString(crop) || 'General',
            quantity: sanitizeString(quantity) || '-',
            paymentMode: 'UPI',
            upiTransactionId: sanitizeString(upiTransactionId || ''),
            location: sanitizeString(location) || '-',
            status: 'COMPLETED',
            timestamp: new Date().toISOString(),
            remarks: 'Direct payment recorded'
        }
    };

    // Optional: Verify transaction signature if provided
    if (signature && senderPublicKey) {
        try {
            if (!verifySignature(transactionData, signature, senderPublicKey)) {
                console.log(`⚠️  Signature verification failed for transaction from ${from}`);
                return res.status(400).json({
                    success: false,
                    error: 'Invalid transaction signature'
                });
            }
            console.log(`✅ Transaction signature verified for ${from}`);
        } catch (error) {
            console.error(`❌ Signature verification error: ${error.message}`);
            return res.status(400).json({
                success: false,
                error: 'Signature verification failed'
            });
        }
    }

    try {
        // Verify transaction using blockchain's addTransaction method
        telhanChain.addTransaction(transactionData);
    } catch (error) {
        console.log(`❌ Transaction validation failed: ${error.message}`);
        return res.status(400).json({
            success: false,
            error: error.message
        });
    }

    const newBlock = new Block(Date.now(), transactionData);
    telhanChain.addBlock(newBlock);

    // Save to Firebase
    await saveToFirebase(`transactions/${transactionId}`, {
        ...transactionData,
        blockHash: newBlock.hash,
        blockIndex: newBlock.index,
        signatureVerified: !!(signature && senderPublicKey)
    });

    console.log(`💰 Transaction added: ${from} → ${to} | ₹${amount}`);
    console.log('='.repeat(60) + '\n');

    res.json({
        success: true,
        message: "Transaction added to blockchain",
        transactionId,
        contractId,
        blockHash: newBlock.hash,
        blockIndex: newBlock.index,
        signatureVerified: !!(signature && senderPublicKey)
    });
});

app.get('/transaction/:id', (req, res) => {
    const tx = telhanChain.getTransaction(req.params.id);
    if (!tx) return res.status(404).json({ error: "Transaction not found" });
    res.json({
        success: true,
        transaction: tx
    });
});

// ==========================================
// CONTRACT ENDPOINTS
// ==========================================

app.post('/contract/create', validateInput(schemas.contract), optionalAuth, async (req, res) => {
    const {
        contractId, farmerId, farmerName, farmerPhone,
        buyerId, buyerName, buyerPhone, crop, variety,
        quantity, unit, pricePerUnit, totalAmount,
        advanceAmount, expectedDeliveryDate,
        qualityParameters, location
    } = req.validatedBody;

    const currentState = telhanChain.getContractState(contractId);
    if (currentState.exists) {
        return res.status(400).json({ error: "Contract ID already exists on blockchain" });
    }

    const contractData = {
        transactionId: `TXN-${contractId}-CREATE`,
        contractId,
        action: "CREATE_CONTRACT",
        farmerId,
        farmerName,
        farmerPhone,
        buyerId,
        buyerName,
        buyerPhone,
        payload: {
            crop,
            variety: variety || 'Standard',
            quantity,
            unit: unit || 'kg',
            pricePerUnit,
            totalAmount,
            advanceAmount: advanceAmount || 0,
            balanceAmount: totalAmount - (advanceAmount || 0),
            expectedDeliveryDate,
            qualityParameters: qualityParameters || {},
            location: location || 'Not specified',
            status: "CREATED",
            createdAt: new Date().toISOString()
        }
    };

    const newBlock = new Block(Date.now(), contractData);
    telhanChain.addBlock(newBlock);

    await saveToFirebase(`contracts/${contractId}`, {
        ...contractData,
        blockHash: newBlock.hash,
        blockIndex: newBlock.index
    });

    console.log(`✅ Contract created: ${contractId}`);
    res.json({
        success: true,
        message: "Contract locked on blockchain",
        contractId,
        blockHash: newBlock.hash,
        blockIndex: newBlock.index
    });
});

app.post('/contract/accept', (req, res) => {
    const { contractId, buyerId } = req.body;

    const state = telhanChain.getContractState(contractId);
    if (!state.exists) return res.status(404).json({ error: "Contract not found" });
    if (state.currentStatus !== "CREATED") return res.status(400).json({ error: "Contract not in CREATED state" });

    const newBlock = new Block(Date.now(), {
        contractId,
        action: "BUYER_ACCEPT",
        buyerId,
        payload: { status: "ACCEPTED" }
    });
    telhanChain.addBlock(newBlock);

    res.json({ message: "Buyer acceptance recorded immutably", status: "ACCEPTED" });
});

app.post('/contract/deliver', (req, res) => {
    const { contractId, actualQuantity, qualityGrade } = req.body;

    const state = telhanChain.getContractState(contractId);
    if (!state.currentStatus === "ACCEPTED") return res.status(400).json({ error: "Contract must be ACCEPTED first" });

    const newBlock = new Block(Date.now(), {
        contractId,
        action: "DELIVERY_VERIFIED",
        payload: {
            status: "DELIVERED",
            actualQuantity,
            qualityGrade,
            notes: "Verified at Mandi Collection Center"
        }
    });
    telhanChain.addBlock(newBlock);

    res.json({ message: "Delivery recorded", status: "DELIVERED" });
});

app.post('/contract/pay', validateInput(schemas.payment), optionalAuth, async (req, res) => {
    const { contractId, amount, paymentMode, upiTransactionId, bankReferenceNo } = req.validatedBody;

    const state = telhanChain.getContractState(contractId);
    if (!state.exists) {
        return res.status(404).json({ error: "Contract not found" });
    }

    const from = state.contractDetails?.buyerId || 'Unknown';
    const to = state.contractDetails?.farmerId || 'Unknown';

    const paymentData = {
        transactionId: upiTransactionId || bankReferenceNo || `TXN-${Date.now()}`,
        contractId,
        action: "PAYMENT",
        from: sanitizeString(from),
        to: sanitizeString(to),
        payload: {
            amount: parseFloat(amount),
            paymentMode: paymentMode,
            upiTransactionId: sanitizeString(upiTransactionId || ''),
            bankReferenceNo: sanitizeString(bankReferenceNo || ''),
            paymentType: 'FULL_PAYMENT',
            status: state.currentStatus === 'DELIVERED' ? 'COMPLETED' : 'PAID',
            paidAt: new Date().toISOString(),
            remarks: 'Payment processed successfully'
        }
    };

    const newBlock = new Block(Date.now(), paymentData);
    telhanChain.addBlock(newBlock);

    await saveToFirebase(`transactions/${paymentData.transactionId}`, {
        ...paymentData,
        blockHash: newBlock.hash,
        blockIndex: newBlock.index
    });

    console.log(`💰 Payment recorded: ${amount} INR (${contractId})`);
    res.json({
        success: true,
        message: "Payment recorded on blockchain",
        transactionId: paymentData.transactionId,
        amount,
        blockHash: newBlock.hash,
        status: paymentData.payload.status
    });
});

app.get('/contract/:id', (req, res) => {
    const state = telhanChain.getContractState(req.params.id);
    if (!state.exists) return res.status(404).json({ error: "Contract not found on ledger" });
    res.json({
        success: true,
        contract: state
    });
});

// ==========================================
// UTILITY ENDPOINTS
// ==========================================

app.get('/user/:userId/transactions', (req, res) => {
    const { userId } = req.params;
    const { role } = req.query;

    const transactions = telhanChain.getUserTransactions(userId, role);
    res.json({
        success: true,
        userId,
        role,
        count: transactions.length,
        transactions
    });
});

app.get('/stats', (req, res) => {
    const stats = telhanChain.getStatistics();

    // Add distributed network info if available
    if (ENABLE_DISTRIBUTED && distributedCoordinator) {
        stats.distributed = {
            enabled: true,
            nodeId: NODE_ID,
            connectedPeers: distributedCoordinator.network?.peers?.size || 0,
            validators: distributedCoordinator.nodeRegistry?.validators?.size || 0,
            totalNodes: distributedCoordinator.nodeRegistry?.nodes?.size || 0
        };
    } else {
        stats.distributed = {
            enabled: false,
            nodeId: NODE_ID,
            connectedPeers: 0,
            validators: 1,
            totalNodes: 1
        };
    }

    res.json({
        success: true,
        statistics: stats
    });
});

app.get('/validate', (req, res) => {
    const isValid = telhanChain.isChainValid();
    res.json({
        success: true,
        valid: isValid,
        message: isValid ? 'Blockchain is valid' : 'Blockchain validation failed'
    });
});

app.get('/search/crop/:cropName', (req, res) => {
    const { cropName } = req.params;
    const contracts = [];

    for (const block of telhanChain.chain.slice(1)) {
        if (block.data.action === 'CREATE_CONTRACT' &&
            block.data.payload.crop.toLowerCase().includes(cropName.toLowerCase())) {
            contracts.push({
                contractId: block.data.contractId,
                crop: block.data.payload.crop,
                quantity: block.data.payload.quantity,
                amount: block.data.payload.totalAmount,
                timestamp: block.timestamp,
                blockHash: block.hash
            });
        }
    }

    res.json({
        success: true,
        crop: cropName,
        count: contracts.length,
        contracts
    });
});

app.get('/contracts/pending', (req, res) => {
    const pending = [];

    for (const block of telhanChain.chain.slice(1)) {
        if (block.data.contractId) {
            const state = telhanChain.getContractState(block.data.contractId);
            if (state.exists && state.currentStatus !== 'COMPLETED' && state.currentStatus !== 'PAID') {
                pending.push({
                    contractId: block.data.contractId,
                    status: state.currentStatus,
                    details: state.contractDetails
                });
            }
        }
    }

    res.json({
        success: true,
        count: pending.length,
        contracts: pending
    });
});

app.get('/export', (req, res) => {
    res.json({
        success: true,
        blockchain: telhanChain.exportChain()
    });
});

// ==========================================
// MOBILE API ENDPOINTS
// ==========================================

app.get('/api/health', (req, res) => {
    res.json({
        status: 'online',
        blockchain: {
            blocks: telhanChain.chain.length,
            valid: telhanChain.isChainValid()
        },
        firebase: {
            connected: true
        },
        timestamp: new Date().toISOString()
    });
});

app.get('/api/mobile/transactions', async (req, res) => {
    try {
        const { userId, limit = 20, offset = 0 } = req.query;

        if (!userId) {
            return res.status(400).json({ error: 'userId is required' });
        }

        const userTx = telhanChain.getUserTransactions(userId, 'farmer');
        const buyerTx = telhanChain.getUserTransactions(userId, 'buyer');
        const allTx = [...userTx, ...buyerTx];

        res.json({
            success: true,
            total: allTx.length,
            transactions: allTx.slice(parseInt(offset), parseInt(offset) + parseInt(limit))
        });
    } catch (error) {
        res.status(500).json({ error: error.message });
    }
});

app.get('/api/mobile/stats/:userId', (req, res) => {
    try {
        const userId = req.params.userId;
        const farmerTx = telhanChain.getUserTransactions(userId, 'farmer');
        const buyerTx = telhanChain.getUserTransactions(userId, 'buyer');

        let totalSales = 0;
        let totalPurchases = 0;
        let cropsSold = new Set();
        let cropsBought = new Set();

        farmerTx.forEach(tx => {
            if (tx.data.payload && tx.data.payload.amount) {
                totalSales += parseFloat(tx.data.payload.amount);
            }
            if (tx.data.payload && tx.data.payload.crop) {
                cropsSold.add(tx.data.payload.crop);
            }
        });

        buyerTx.forEach(tx => {
            if (tx.data.payload && tx.data.payload.amount) {
                totalPurchases += parseFloat(tx.data.payload.amount);
            }
            if (tx.data.payload && tx.data.payload.crop) {
                cropsBought.add(tx.data.payload.crop);
            }
        });

        res.json({
            success: true,
            stats: {
                totalTransactions: farmerTx.length + buyerTx.length,
                asFarmer: {
                    transactions: farmerTx.length,
                    totalEarnings: totalSales.toFixed(2),
                    cropsSold: Array.from(cropsSold)
                },
                asBuyer: {
                    transactions: buyerTx.length,
                    totalSpent: totalPurchases.toFixed(2),
                    cropsBought: Array.from(cropsBought)
                }
            }
        });
    } catch (error) {
        res.status(500).json({ error: error.message });
    }
});

app.get('/api/mobile/verify/:transactionId', async (req, res) => {
    try {
        const transactionId = req.params.transactionId;
        const tx = telhanChain.getTransaction(transactionId);

        if (!tx) {
            return res.status(404).json({ error: 'Transaction not found' });
        }

        res.json({
            success: true,
            verified: true,
            transaction: tx.transaction,
            block: tx.block
        });
    } catch (error) {
        res.status(500).json({ error: error.message });
    }
});

app.get('/api/mobile/feed', (req, res) => {
    try {
        const { limit = 10 } = req.query;
        const recentBlocks = telhanChain.chain.slice(-parseInt(limit)).reverse();

        const feed = recentBlocks
            .filter(block => block.data.type !== 'GENESIS')
            .map(block => ({
                id: block.data.transactionId || block.data.contractId,
                type: block.data.action,
                from: block.data.from || block.data.farmerId,
                to: block.data.to || block.data.buyerId,
                crop: block.data.payload?.crop || block.data.crop,
                amount: block.data.payload?.amount || block.data.amount,
                timestamp: new Date(block.timestamp).toISOString(),
                verified: true
            }));

        res.json({
            success: true,
            feed: feed
        });
    } catch (error) {
        res.status(500).json({ error: error.message });
    }
});

// ==========================================
// DISTRIBUTED NETWORK ADMIN ENDPOINTS
// ==========================================

// Admin middleware - require admin API key
const requireAdmin = (req, res, next) => {
    const apiKey = req.headers['x-admin-key'];
    const adminKey = process.env.ADMIN_API_KEY;

    if (!adminKey) {
        return res.status(500).json({ error: 'Admin API key not configured' });
    }

    if (!apiKey || apiKey !== adminKey) {
        return res.status(403).json({ error: 'Unauthorized - Admin access required' });
    }

    next();
};

// Get network status
app.get('/admin/network/status', requireAdmin, (req, res) => {
    if (!ENABLE_DISTRIBUTED || !distributedCoordinator) {
        return res.json({
            distributed: false,
            message: 'Distributed mode is not enabled'
        });
    }

    const stats = distributedCoordinator.getNetworkStats();
    res.json({
        success: true,
        distributed: true,
        stats
    });
});

// Register new node
app.post('/admin/nodes/register', requireAdmin, (req, res) => {
    if (!ENABLE_DISTRIBUTED || !distributedCoordinator) {
        return res.status(400).json({ error: 'Distributed mode not enabled' });
    }

    const { url, host, port, publicKey, nodeType, metadata } = req.body;

    if (!url || !host || !port) {
        return res.status(400).json({ error: 'url, host, and port are required' });
    }

    const nodeId = NodeRegistry.generateNodeId(host, port);
    const result = distributedCoordinator.nodeRegistry.registerNode({
        nodeId,
        url,
        host,
        port,
        publicKey,
        nodeType: nodeType || 'peer',
        metadata: metadata || {}
    });

    res.json(result);
});

// Approve pending node
app.post('/admin/nodes/approve/:nodeId', requireAdmin, (req, res) => {
    if (!ENABLE_DISTRIBUTED || !distributedCoordinator) {
        return res.status(400).json({ error: 'Distributed mode not enabled' });
    }

    const { nodeId } = req.params;
    const adminId = req.headers['x-admin-id'] || 'admin';

    const result = distributedCoordinator.nodeRegistry.approveNode(nodeId, adminId);
    res.json(result);
});

// Reject pending node
app.post('/admin/nodes/reject/:nodeId', requireAdmin, (req, res) => {
    if (!ENABLE_DISTRIBUTED || !distributedCoordinator) {
        return res.status(400).json({ error: 'Distributed mode not enabled' });
    }

    const { nodeId } = req.params;
    const { reason } = req.body;
    const adminId = req.headers['x-admin-id'] || 'admin';

    const result = distributedCoordinator.nodeRegistry.rejectNode(nodeId, adminId, reason || 'No reason provided');
    res.json(result);
});

// Promote node to validator
app.post('/admin/nodes/promote/:nodeId', requireAdmin, (req, res) => {
    if (!ENABLE_DISTRIBUTED || !distributedCoordinator) {
        return res.status(400).json({ error: 'Distributed mode not enabled' });
    }

    const { nodeId } = req.params;
    const adminId = req.headers['x-admin-id'] || 'admin';

    const result = distributedCoordinator.nodeRegistry.promoteToValidator(nodeId, adminId);
    res.json(result);
});

// Demote validator to peer
app.post('/admin/nodes/demote/:nodeId', requireAdmin, (req, res) => {
    if (!ENABLE_DISTRIBUTED || !distributedCoordinator) {
        return res.status(400).json({ error: 'Distributed mode not enabled' });
    }

    const { nodeId } = req.params;
    const adminId = req.headers['x-admin-id'] || 'admin';

    const result = distributedCoordinator.nodeRegistry.demoteValidator(nodeId, adminId);
    res.json(result);
});

// Remove node from network
app.delete('/admin/nodes/:nodeId', requireAdmin, (req, res) => {
    if (!ENABLE_DISTRIBUTED || !distributedCoordinator) {
        return res.status(400).json({ error: 'Distributed mode not enabled' });
    }

    const { nodeId } = req.params;
    const { reason } = req.body;
    const adminId = req.headers['x-admin-id'] || 'admin';

    const result = distributedCoordinator.nodeRegistry.removeNode(nodeId, adminId, reason || 'No reason provided');

    // Also disconnect from peer
    if (result.success) {
        distributedCoordinator.network.disconnectPeer(nodeId);
    }

    res.json(result);
});

// Get all nodes
app.get('/admin/nodes', requireAdmin, (req, res) => {
    if (!ENABLE_DISTRIBUTED || !distributedCoordinator) {
        return res.status(400).json({ error: 'Distributed mode not enabled' });
    }

    const { status } = req.query;

    let nodes;
    if (status === 'active') {
        nodes = distributedCoordinator.nodeRegistry.getActiveNodes();
    } else if (status === 'pending') {
        nodes = distributedCoordinator.nodeRegistry.getPendingNodes();
    } else if (status === 'validators') {
        nodes = distributedCoordinator.nodeRegistry.getValidators();
    } else {
        nodes = Array.from(distributedCoordinator.nodeRegistry.nodes.values());
    }

    res.json({
        success: true,
        count: nodes.length,
        nodes
    });
});

// Connect to a peer node
app.post('/admin/network/connect', requireAdmin, async (req, res) => {
    if (!ENABLE_DISTRIBUTED || !distributedCoordinator) {
        return res.status(400).json({ error: 'Distributed mode not enabled' });
    }

    const { url, nodeId } = req.body;

    if (!url || !nodeId) {
        return res.status(400).json({ error: 'url and nodeId are required' });
    }

    try {
        const connected = await distributedCoordinator.connectToNode(url, nodeId);
        res.json({
            success: connected,
            message: connected ? 'Connected successfully' : 'Failed to connect'
        });
    } catch (error) {
        res.status(500).json({
            success: false,
            error: error.message
        });
    }
});

// Request chain synchronization
app.post('/admin/network/sync', requireAdmin, (req, res) => {
    if (!ENABLE_DISTRIBUTED || !distributedCoordinator) {
        return res.status(400).json({ error: 'Distributed mode not enabled' });
    }

    const { nodeId } = req.body;

    distributedCoordinator.requestChainSync(nodeId || null);

    res.json({
        success: true,
        message: nodeId ? `Sync requested from ${nodeId}` : 'Sync requested from all peers'
    });
});

// Force save blockchain to all storages
app.post('/admin/blockchain/save', requireAdmin, async (req, res) => {
    try {
        if (ENABLE_DISTRIBUTED && distributedCoordinator) {
            await distributedCoordinator.saveChain();
        } else {
            await saveToFirebase('blockchain', telhanChain.exportChain());
        }

        res.json({
            success: true,
            message: 'Blockchain saved successfully'
        });
    } catch (error) {
        res.status(500).json({
            success: false,
            error: error.message
        });
    }
});

module.exports = app;
module.exports = app;
