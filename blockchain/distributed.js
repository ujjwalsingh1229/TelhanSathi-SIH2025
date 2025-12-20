// ==========================================
// DISTRIBUTED COORDINATOR MODULE
// ==========================================
const P2PNetwork = require('./network');
const NodeRegistry = require('./nodeRegistry');
const Consensus = require('./consensus');
const LocalStorage = require('./storage');

class DistributedCoordinator {
    constructor(blockchain, nodeId, p2pPort, firebaseModule) {
        this.blockchain = blockchain;
        this.nodeId = nodeId;
        this.p2pPort = p2pPort;
        this.firebaseModule = firebaseModule;

        // Initialize components
        this.network = new P2PNetwork(p2pPort, nodeId);
        this.nodeRegistry = new NodeRegistry();
        this.consensus = new Consensus(this.nodeRegistry);
        this.localStorage = new LocalStorage();

        this.syncInProgress = false;
        this.initialized = false;
    }

    async initialize() {
        try {
            console.log('\n🚀 Initializing Distributed Blockchain System...');
            console.log(`   Node ID: ${this.nodeId}`);
            console.log(`   P2P Port: ${this.p2pPort}`);

            // 1. Initialize local storage
            await this.localStorage.initialize();

            // 2. Load node registry from storage
            const savedNodes = await this.localStorage.loadNodes();
            if (savedNodes && savedNodes.length > 0) {
                this.nodeRegistry.importData({
                    nodes: savedNodes.nodes || [],
                    validators: savedNodes.validators || [],
                    pendingNodes: savedNodes.pendingNodes || [],
                    blacklist: savedNodes.blacklist || []
                });
            }

            // 3. Start P2P network
            await this.network.start();

            // 4. Setup event handlers
            this.setupEventHandlers();

            // 5. Enable distributed mode on blockchain
            this.blockchain.enableDistributedMode(this.nodeId);

            // 6. Auto-save registry periodically
            this.startAutoSave();

            // 7. Start health checks
            this.network.startHealthCheck();

            this.initialized = true;
            console.log('✅ Distributed system initialized successfully\n');

            return true;
        } catch (error) {
            console.error('❌ Failed to initialize distributed system:', error.message);
            return false;
        }
    }

    setupEventHandlers() {
        // Handle new blocks from network
        this.network.on('new-block', async (block, fromNode) => {
            console.log(`\n📨 Received new block from ${fromNode}`);
            await this.handleNewBlock(block, fromNode);
        });

        // Handle new transactions
        this.network.on('new-transaction', async (transaction, fromNode) => {
            console.log(`\n📨 Received new transaction from ${fromNode}`);
            // Transaction will be included in next block
        });

        // Handle chain requests
        this.network.on('chain-request', (fromNode, ws) => {
            console.log(`\n📨 Chain request from ${fromNode}`);
            this.network.sendToPeer(ws, {
                type: 'CHAIN_RESPONSE',
                chain: this.blockchain.chain
            });
        });

        // Handle chain responses (for sync)
        this.network.on('chain-response', async (chain, fromNode) => {
            console.log(`\n📨 Received chain from ${fromNode} (${chain.length} blocks)`);
            await this.synchronizeChain(chain, fromNode);
        });

        // Handle node list requests
        this.network.on('node-list-request', (fromNode, ws) => {
            console.log(`\n📨 Node list request from ${fromNode}`);
            this.network.sendToPeer(ws, {
                type: 'NODE_LIST_RESPONSE',
                nodes: this.nodeRegistry.getActiveNodes()
            });
        });

        // Handle peer connections/disconnections
        this.network.on('peer-connected', (nodeId) => {
            this.nodeRegistry.updateLastSeen(nodeId);
            console.log(`✅ Peer ${nodeId} connected`);
        });

        this.network.on('peer-disconnected', (nodeId) => {
            console.log(`👋 Peer ${nodeId} disconnected`);
        });

        // Handle blockchain events
        this.blockchain.on('block-added', (block) => {
            // Broadcast new block to all peers
            this.broadcastBlock(block);
        });

        this.blockchain.on('chain-replaced', async (newChain) => {
            // Save to both storages
            await this.saveChain();
        });
    }

    async handleNewBlock(block, fromNode) {
        if (this.syncInProgress) {
            console.log('⏳ Sync in progress, queuing block...');
            return;
        }

        // Validate block using consensus
        const previousBlock = this.blockchain.getLatestBlock();
        const validation = this.consensus.validateNewBlock(block, previousBlock, fromNode);

        if (!validation.isValid) {
            console.log('❌ Block validation failed:');
            validation.validations.filter(v => !v.valid).forEach(v => {
                console.log(`   - ${v.rule}: ${v.message}`);
            });

            // Penalize sending node
            this.consensus.penalizeNode(fromNode, 'Sent invalid block', 'medium');
            return;
        }

        // Add block to chain
        try {
            this.blockchain.chain.push(block);

            // Update transaction pool
            if (block.data.transactionId) {
                this.blockchain.transactionPool.set(block.data.transactionId, {
                    blockIndex: block.index,
                    blockHash: block.hash,
                    timestamp: block.timestamp
                });
            }

            console.log(`✅ Block ${block.index} added from network`);

            // Reward validator
            this.consensus.rewardNode(fromNode, 'Created valid block');

            // Save chain
            await this.saveChain();

        } catch (error) {
            console.error('❌ Failed to add block:', error.message);
        }
    }

    async synchronizeChain(remoteChain, fromNode) {
        if (this.syncInProgress) {
            console.log('⏳ Sync already in progress');
            return;
        }

        this.syncInProgress = true;

        try {
            console.log('\n🔄 Synchronizing blockchain...');

            // Use consensus to decide if we should replace chain
            const decision = this.consensus.resolveConflict(
                this.blockchain.chain,
                remoteChain,
                fromNode
            );

            if (decision.shouldReplace) {
                console.log(`✅ ${decision.reason}`);
                this.blockchain.replaceChain(remoteChain, decision.reason);

                // Save to both storages
                await this.saveChain();

                console.log(`✅ Chain synchronized successfully`);
            } else {
                console.log(`ℹ️  ${decision.reason}`);
            }

        } catch (error) {
            console.error('❌ Chain sync failed:', error.message);
        } finally {
            this.syncInProgress = false;
        }
    }

    broadcastBlock(block) {
        const sent = this.network.broadcast({
            type: 'NEW_BLOCK',
            block: block
        });

        console.log(`📡 Block ${block.index} broadcast to ${sent} peers`);
    }

    async connectToNode(url, nodeId) {
        try {
            await this.network.connectToPeer(url, nodeId);
            console.log(`✅ Connected to node: ${nodeId}`);

            // Request their blockchain for sync
            setTimeout(() => {
                this.requestChainSync(nodeId);
            }, 1000);

            return true;
        } catch (error) {
            console.error(`❌ Failed to connect to ${nodeId}:`, error.message);
            return false;
        }
    }

    requestChainSync(nodeId = null) {
        if (nodeId) {
            // Request from specific node
            const ws = this.network.peers.get(nodeId);
            if (ws) {
                this.network.sendToPeer(ws, { type: 'CHAIN_REQUEST' });
                console.log(`📨 Chain sync requested from ${nodeId}`);
            }
        } else {
            // Broadcast to all peers
            this.network.broadcast({ type: 'CHAIN_REQUEST' });
            console.log(`📨 Chain sync requested from all peers`);
        }
    }

    async saveChain() {
        const chainData = this.blockchain.exportChain();

        // Save to local storage
        await this.localStorage.saveBlockchain(chainData);

        // Save to Firebase
        if (this.firebaseModule) {
            await this.firebaseModule.saveToFirebase('blockchain', chainData);
        }
    }

    async loadChain() {
        // Try local storage first
        let chainData = await this.localStorage.loadBlockchain();

        // If no local data, try Firebase
        if (!chainData && this.firebaseModule) {
            chainData = await this.firebaseModule.loadFromFirebase('blockchain');
        }

        if (chainData && chainData.blocks) {
            return this.blockchain.importChain(chainData);
        }

        return false;
    }

    startAutoSave() {
        // Save registry every 2 minutes
        setInterval(async () => {
            const registryData = this.nodeRegistry.exportData();
            await this.localStorage.saveNodes(registryData);
        }, 120000);

        // Check for inactive nodes every 5 minutes
        setInterval(() => {
            this.nodeRegistry.checkInactiveNodes();
        }, 300000);
    }

    async shutdown() {
        console.log('\n🔌 Shutting down distributed system...');

        // Save current state
        await this.saveChain();
        const registryData = this.nodeRegistry.exportData();
        await this.localStorage.saveNodes(registryData);

        // Shutdown network
        await this.network.shutdown();

        console.log('✅ Distributed system shut down successfully');
    }

    getNetworkStats() {
        return {
            node: {
                id: this.nodeId,
                p2pPort: this.p2pPort,
                isValidator: this.nodeRegistry.isValidator(this.nodeId)
            },
            network: this.network.getStats(),
            consensus: this.consensus.getStats(),
            registry: this.nodeRegistry.getStats(),
            blockchain: {
                length: this.blockchain.chain.length,
                isValid: this.blockchain.isChainValid(),
                isDistributed: this.blockchain.isDistributed
            }
        };
    }
}

module.exports = DistributedCoordinator;
