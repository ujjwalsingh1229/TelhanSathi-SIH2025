// ==========================================
// MOBILE API ENDPOINTS MODULE
// ==========================================
const express = require('express');

function createMobileAPIRoutes(blockchain, discovery, ngrokManager) {
    const router = express.Router();

    // ========== BLOCKCHAIN STATUS ==========

    /**
     * GET /mobile/api/health
     * Check mobile app connectivity and blockchain status
     */
    router.get('/mobile/api/health', (req, res) => {
        try {
            const stats = {
                status: 'healthy',
                timestamp: Date.now(),
                node: {
                    id: process.env.NODE_ID || 'unknown',
                    isValidator: process.env.IS_VALIDATOR === 'true',
                    publicUrl: ngrokManager?.getPublicUrl() || 'unknown'
                },
                blockchain: {
                    totalBlocks: blockchain.chain.length,
                    totalTransactions: blockchain.pendingTransactions.length,
                    isValid: blockchain.isChainValid()
                },
                network: {
                    version: '1.0.0',
                    ngrokConnected: ngrokManager?.isConnected || false
                }
            };

            res.json(stats);
        } catch (error) {
            res.status(500).json({ error: error.message });
        }
    });

    // ========== TRANSACTION ENDPOINTS ==========

    /**
     * POST /mobile/api/transaction/send
     * Mobile app sends a transaction to the blockchain
     * 
     * Body:
     * {
     *   from: "farmer_id",
     *   to: "buyer_id",
     *   amount: 100,
     *   productName: "Wheat",
     *   quantity: 50,
     *   unit: "kg",
     *   signature: "hexstring",
     *   senderPublicKey: "hexstring"
     * }
     */
    router.post('/mobile/api/transaction/send', (req, res) => {
        try {
            const { from, to, amount, productName, quantity, unit, signature, senderPublicKey } = req.body;

            // Validation
            if (!from || !to || !amount) {
                return res.status(400).json({
                    success: false,
                    error: 'Missing required fields: from, to, amount'
                });
            }

            // Create transaction
            const transaction = {
                from,
                to,
                amount,
                timestamp: Date.now(),
                productName: productName || 'Unknown',
                quantity: quantity || 0,
                unit: unit || 'unit',
                signature: signature || null,
                senderPublicKey: senderPublicKey || null,
                txId: `TXN-${Date.now()}-${Math.random().toString(36).substring(7)}`
            };

            // Add to blockchain
            blockchain.addTransaction(transaction);

            res.status(201).json({
                success: true,
                message: 'Transaction added to pending pool',
                transaction: {
                    txId: transaction.txId,
                    from: transaction.from,
                    to: transaction.to,
                    amount: transaction.amount,
                    timestamp: transaction.timestamp
                }
            });
        } catch (error) {
            res.status(500).json({
                success: false,
                error: error.message
            });
        }
    });

    /**
     * GET /mobile/api/transaction/:txId
     * Get transaction details by ID
     */
    router.get('/mobile/api/transaction/:txId', (req, res) => {
        try {
            const { txId } = req.params;
            const txData = blockchain.getTransaction(txId);

            if (!txData) {
                return res.status(404).json({
                    success: false,
                    error: 'Transaction not found'
                });
            }

            res.json({
                success: true,
                transaction: txData.transaction,
                block: txData.block
            });
        } catch (error) {
            res.status(500).json({
                success: false,
                error: error.message
            });
        }
    });

    /**
     * GET /mobile/api/transactions?userId=farmer_123&limit=20
     * Get user's transactions (paginated)
     */
    router.get('/mobile/api/transactions', (req, res) => {
        try {
            const { userId, limit = 20, offset = 0 } = req.query;

            if (!userId) {
                return res.status(400).json({
                    success: false,
                    error: 'Missing userId parameter'
                });
            }

            const transactions = [];
            let count = 0;

            // Search through all blocks for transactions
            for (let i = blockchain.chain.length - 1; i >= 0 && count < limit; i--) {
                const block = blockchain.chain[i];
                if (Array.isArray(block.data) || (block.data && typeof block.data === 'object')) {
                    const blockTxns = Array.isArray(block.data) ? block.data : [block.data];

                    for (const txn of blockTxns) {
                        if ((txn.from === userId || txn.to === userId) && count < limit) {
                            transactions.push({
                                ...txn,
                                blockIndex: i,
                                blockHash: block.hash,
                                confirmations: blockchain.chain.length - i
                            });
                            count++;
                        }
                    }
                }
            }

            res.json({
                success: true,
                userId,
                totalTransactions: transactions.length,
                transactions: transactions.slice(offset, offset + limit)
            });
        } catch (error) {
            res.status(500).json({
                success: false,
                error: error.message
            });
        }
    });

    // ========== BLOCKCHAIN QUERY ENDPOINTS ==========

    /**
     * GET /mobile/api/blockchain/latest
     * Get latest blocks
     */
    router.get('/mobile/api/blockchain/latest', (req, res) => {
        try {
            const count = Math.min(parseInt(req.query.count || 10), 100);
            const latestBlocks = blockchain.chain.slice(-count).reverse();

            res.json({
                success: true,
                blocks: latestBlocks.map(block => ({
                    index: block.index,
                    hash: block.hash,
                    previousHash: block.previousHash,
                    timestamp: block.timestamp,
                    transactionCount: Array.isArray(block.data) ? block.data.length : 1,
                    validatorId: block.validatorId
                }))
            });
        } catch (error) {
            res.status(500).json({
                success: false,
                error: error.message
            });
        }
    });

    /**
     * GET /mobile/api/blockchain/stats
     * Get blockchain statistics
     */
    router.get('/mobile/api/blockchain/stats', (req, res) => {
        try {
            const totalTransactions = blockchain.chain.reduce((sum, block) => {
                return sum + (Array.isArray(block.data) ? block.data.length : 1);
            }, 0);

            res.json({
                success: true,
                statistics: {
                    totalBlocks: blockchain.chain.length,
                    totalTransactions: totalTransactions,
                    chainValid: blockchain.isChainValid(),
                    pendingTransactions: blockchain.pendingTransactions.length,
                    averageBlockTime: blockchain.chain.length > 1
                        ? (blockchain.getLatestBlock().timestamp - blockchain.chain[0].timestamp) / (blockchain.chain.length - 1)
                        : 0
                }
            });
        } catch (error) {
            res.status(500).json({
                success: false,
                error: error.message
            });
        }
    });

    /**
     * GET /mobile/api/blockchain/verify/:blockHash
     * Verify a block in the chain
     */
    router.get('/mobile/api/blockchain/verify/:blockHash', (req, res) => {
        try {
            const { blockHash } = req.params;
            const block = blockchain.chain.find(b => b.hash === blockHash);

            if (!block) {
                return res.status(404).json({
                    success: false,
                    error: 'Block not found'
                });
            }

            const blockValid = block.hash === block.calculateHash();
            const chainValid = blockchain.isChainValid();

            res.json({
                success: true,
                blockValid: blockValid,
                chainValid: chainValid,
                block: {
                    index: block.index,
                    hash: block.hash,
                    timestamp: block.timestamp,
                    transactionCount: Array.isArray(block.data) ? block.data.length : 1
                }
            });
        } catch (error) {
            res.status(500).json({
                success: false,
                error: error.message
            });
        }
    });

    // ========== NETWORK DISCOVERY ==========

    /**
     * GET /mobile/api/network/nodes
     * Get all active nodes in the network
     */
    router.get('/mobile/api/network/nodes', async (req, res) => {
        try {
            if (!discovery) {
                return res.status(503).json({
                    success: false,
                    error: 'Node discovery not available'
                });
            }

            const nodes = await discovery.discoverNodes();
            res.json({
                success: true,
                nodeCount: nodes.length,
                nodes: nodes.map(node => ({
                    nodeId: node.nodeId,
                    publicUrl: node.publicUrl,
                    isValidator: node.isValidator,
                    reputation: node.reputation,
                    lastSeen: node.timestamp
                }))
            });
        } catch (error) {
            res.status(500).json({
                success: false,
                error: error.message
            });
        }
    });

    /**
     * GET /mobile/api/network/validators
     * Get all active validators
     */
    router.get('/mobile/api/network/validators', async (req, res) => {
        try {
            if (!discovery) {
                return res.status(503).json({
                    success: false,
                    error: 'Node discovery not available'
                });
            }

            const validators = await discovery.getValidators();
            res.json({
                success: true,
                validatorCount: validators.length,
                validators: validators.map(v => ({
                    nodeId: v.nodeId,
                    publicUrl: v.publicUrl,
                    reputation: v.reputation,
                    lastSeen: v.timestamp
                }))
            });
        } catch (error) {
            res.status(500).json({
                success: false,
                error: error.message
            });
        }
    });

    // ========== USER PROFILE ==========

    /**
     * GET /mobile/api/user/:userId/stats
     * Get user statistics
     */
    router.get('/mobile/api/user/:userId/stats', (req, res) => {
        try {
            const { userId } = req.params;
            let sentCount = 0;
            let receivedCount = 0;
            let sentAmount = 0;
            let receivedAmount = 0;

            // Search all blocks
            for (const block of blockchain.chain) {
                const blockTxns = Array.isArray(block.data) ? block.data : [block.data];

                for (const txn of blockTxns) {
                    if (txn.from === userId) {
                        sentCount++;
                        sentAmount += txn.amount || 0;
                    }
                    if (txn.to === userId) {
                        receivedCount++;
                        receivedAmount += txn.amount || 0;
                    }
                }
            }

            res.json({
                success: true,
                userId,
                statistics: {
                    transactionsSent: sentCount,
                    transactionsReceived: receivedCount,
                    totalAmountSent: sentAmount,
                    totalAmountReceived: receivedAmount,
                    netBalance: receivedAmount - sentAmount
                }
            });
        } catch (error) {
            res.status(500).json({
                success: false,
                error: error.message
            });
        }
    });

    // ========== MARKET FEED ==========

    /**
     * GET /mobile/api/market/feed
     * Get recent market activity
     */
    router.get('/mobile/api/market/feed', (req, res) => {
        try {
            const limit = Math.min(parseInt(req.query.limit || 50), 200);
            const feed = [];

            // Get latest transactions across blocks
            for (let i = blockchain.chain.length - 1; i >= 0 && feed.length < limit; i--) {
                const block = blockchain.chain[i];
                const blockTxns = Array.isArray(block.data) ? block.data : [block.data];

                for (const txn of blockTxns) {
                    if (feed.length < limit) {
                        feed.push({
                            type: 'transaction',
                            from: txn.from,
                            to: txn.to,
                            amount: txn.amount,
                            productName: txn.productName,
                            quantity: txn.quantity,
                            unit: txn.unit,
                            timestamp: txn.timestamp || block.timestamp,
                            blockIndex: i,
                            blockHash: block.hash
                        });
                    }
                }
            }

            res.json({
                success: true,
                feedCount: feed.length,
                feed: feed
            });
        } catch (error) {
            res.status(500).json({
                success: false,
                error: error.message
            });
        }
    });

    return router;
}

module.exports = createMobileAPIRoutes;
