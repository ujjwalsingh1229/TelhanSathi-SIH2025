// ==========================================
// BLOCKCHAIN CORE MODULE - DISTRIBUTED VERSION
// ==========================================
const crypto = require('crypto');
const EventEmitter = require('events');
const stringify = require('fast-json-stable-stringify');

class Block {
    constructor(timestamp, data, previousHash = '', validatorId = null) {
        this.index = 0;
        this.timestamp = timestamp;
        this.data = data;
        this.previousHash = previousHash;
        this.validatorId = validatorId; // Who created this block
        this.hash = this.calculateHash();
        this.nonce = 0;
        this.merkleRoot = this.calculateMerkleRoot();
    }

    calculateHash() {
        // Use deterministic JSON serialization to ensure consistent hashes across nodes
        const hashInput = `${this.index}${this.previousHash}${this.timestamp}${stringify(this.data)}${this.nonce}${this.merkleRoot}`;
        return crypto.createHash('sha256')
            .update(hashInput)
            .digest('hex');
    }

    calculateMerkleRoot() {
        // Use deterministic JSON serialization
        return crypto.createHash('sha256')
            .update(stringify(this.data))
            .digest('hex');
    }

    // Pure PoA: No mining needed - Authority comes from validator identity
    // Kept for backward compatibility but now instant
    mineBlock(difficulty) {
        // In pure PoA, the block is sealed immediately by the validator
        // No computation-based proof of work needed
        this.hash = this.calculateHash();
        console.log(`🔏 Block #${this.index} sealed by Authority | Hash: ${this.hash.substring(0, 20)}... | Validator: ${this.validatorId}`);
    }

    // Sign block with validator's private key (PoA security mechanism)
    signBlock(validatorPrivateKey) {
        const blockHash = this.hash || this.calculateHash();
        const sign = crypto.createSign('SHA256');
        sign.update(blockHash);
        sign.end();
        this.validatorSignature = sign.sign(validatorPrivateKey, 'hex');
        console.log(`✅ Block #${this.index} digitally signed by validator`);
    }

    // Verify block was signed by validator (PoA verification)
    verifyBlockSignature(validatorPublicKey) {
        if (!this.validatorSignature || !validatorPublicKey) {
            return false;
        }
        const blockHash = this.hash || this.calculateHash();
        const verify = crypto.createVerify('SHA256');
        verify.update(blockHash);
        verify.end();
        return verify.verify(validatorPublicKey, this.validatorSignature, 'hex');
    }
}

class Blockchain extends EventEmitter {
    constructor(difficulty = 2, miningReward = 50, saveThrottle = 5000, nodeId = null) {
        super();
        this.chain = [this.createGenesisBlock()];
        this.difficulty = difficulty;
        this.pendingTransactions = [];
        this.miningReward = miningReward;
        this.transactionPool = new Map();
        this.contractCache = new Map();
        this.lastSaveTime = Date.now();
        this.saveThrottle = saveThrottle;
        this.nodeId = nodeId; // This node's ID
        this.isDistributed = false; // Set to true when P2P is enabled
    }

    createGenesisBlock() {
        const genesis = new Block(Date.now(), {
            message: "🌾 Genesis Block - TelhanSathi Agri-Marketplace Initialized",
            type: "GENESIS",
            version: "1.0.0"
        }, "0");
        genesis.index = 0;
        return genesis;
    }

    getLatestBlock() {
        return this.chain[this.chain.length - 1];
    }

    // Add transaction with signature verification
    addTransaction(transaction) {
        // Verify transaction has required fields
        if (!transaction.from) {
            throw new Error('❌ Transaction missing "from" field');
        }

        // If transaction includes signature, verify it
        if (transaction.signature && transaction.senderPublicKey) {
            if (!this.verifyTransactionSignature(transaction)) {
                throw new Error('❌ Invalid transaction signature!');
            }
            console.log(`✅ Transaction signature verified for ${transaction.from}`);
        } else if (transaction.signature || transaction.senderPublicKey) {
            // Warn if only partial signature info provided
            console.warn(`⚠️  Warning: Incomplete signature information in transaction`);
        }

        // Transaction is valid, will be added as a block
        return true;
    }

    // Verify transaction signature using sender's public key
    verifyTransactionSignature(transaction) {
        if (!transaction.signature || !transaction.senderPublicKey) {
            return false;
        }

        try {
            const { signTransaction } = require('./blockchain');

            // Create a copy without signature for verification
            const txData = { ...transaction };
            delete txData.signature;
            delete txData.senderPublicKey;

            // Verify using crypto module
            const verify = crypto.createVerify('SHA256');
            verify.update(stringify(txData));
            verify.end();

            return verify.verify(transaction.senderPublicKey, transaction.signature, 'hex');
        } catch (error) {
            console.error('❌ Signature verification error:', error.message);
            return false;
        }
    }

    addBlock(newBlock, validatorId = null) {
        console.log(`\n📦 Adding new block to chain...`);
        newBlock.index = this.chain.length;
        newBlock.previousHash = this.getLatestBlock().hash;
        newBlock.validatorId = validatorId || this.nodeId;
        console.log(`   Index: ${newBlock.index}`);
        console.log(`   Previous Hash: ${newBlock.previousHash.substring(0, 20)}...`);
        console.log(`   Validator: ${newBlock.validatorId || 'None'}`);

        newBlock.mineBlock(this.difficulty);
        this.chain.push(newBlock);
        console.log(`   Chain length now: ${this.chain.length} blocks`);

        if (newBlock.data.transactionId) {
            this.transactionPool.set(newBlock.data.transactionId, {
                blockIndex: newBlock.index,
                blockHash: newBlock.hash,
                timestamp: newBlock.timestamp
            });
            console.log(`   Transaction stored in pool: ${newBlock.data.transactionId}`);
        }

        if (newBlock.data.contractId) {
            this.contractCache.delete(newBlock.data.contractId);
        }

        // Emit event for distributed network
        if (this.isDistributed) {
            this.emit('block-added', newBlock);
        }

        console.log(``);
        return newBlock;
    }

    isChainValid() {
        for (let i = 1; i < this.chain.length; i++) {
            const currentBlock = this.chain[i];
            const previousBlock = this.chain[i - 1];

            if (currentBlock.hash !== currentBlock.calculateHash()) {
                console.log(`❌ Block #${i} hash mismatch`);
                return false;
            }

            if (currentBlock.merkleRoot !== currentBlock.calculateMerkleRoot()) {
                console.log(`❌ Block #${i} merkle root mismatch`);
                return false;
            }

            if (currentBlock.previousHash !== previousBlock.hash) {
                console.log(`❌ Block #${i} chain broken`);
                return false;
            }

            // PoA: No PoW check needed - validator identity provides security
            // Block signatures are verified separately in consensus.js
        }
        return true;
    }

    getTransaction(transactionId) {
        const txRef = this.transactionPool.get(transactionId);
        if (!txRef) return null;

        const block = this.chain[txRef.blockIndex];
        return {
            transaction: block.data,
            block: {
                index: block.index,
                hash: block.hash,
                timestamp: block.timestamp,
                confirmations: this.chain.length - block.index
            }
        };
    }

    getUserTransactions(userId, role = 'farmer') {
        const field = role === 'farmer' ? 'farmerId' : 'buyerId';
        const transactions = [];

        for (const block of this.chain) {
            if (block.data[field] === userId || block.data.from === userId || block.data.to === userId) {
                transactions.push({
                    blockIndex: block.index,
                    timestamp: block.timestamp,
                    data: block.data,
                    hash: block.hash
                });
            }
        }
        return transactions;
    }

    getContractState(contractId) {
        if (this.contractCache.has(contractId)) {
            return this.contractCache.get(contractId);
        }

        let state = {
            exists: false,
            history: [],
            payments: [],
            totalAmount: 0
        };

        for (const block of this.chain) {
            const tx = block.data;

            if (tx.contractId === contractId) {
                state.exists = true;
                state.history.push({
                    blockIndex: block.index,
                    action: tx.action,
                    timestamp: block.timestamp,
                    details: tx.payload,
                    hash: block.hash
                });

                if (tx.action === 'PAYMENT' && tx.payload.amount) {
                    state.payments.push(tx.payload);
                    state.totalAmount += parseFloat(tx.payload.amount);
                }

                if (tx.payload && tx.payload.status) {
                    state.currentStatus = tx.payload.status;
                    state.latestDetails = tx.payload;
                }

                if (tx.action === 'CREATE_CONTRACT') {
                    state.contractDetails = tx.payload;
                }
            }
        }

        if (state.exists) {
            this.contractCache.set(contractId, state);
        }

        return state;
    }

    getStatistics() {
        let totalContracts = 0;
        let totalTransactions = 0;
        let totalValue = 0;
        const cropStats = new Map();
        const farmerStats = new Map();
        const buyerStats = new Map();

        for (const block of this.chain.slice(1)) {
            const tx = block.data;

            if (tx.action === 'CREATE_CONTRACT') {
                totalContracts++;

                if (tx.payload.crop) {
                    cropStats.set(tx.payload.crop, (cropStats.get(tx.payload.crop) || 0) + 1);
                }

                if (tx.farmerId) {
                    farmerStats.set(tx.farmerId, (farmerStats.get(tx.farmerId) || 0) + 1);
                }

                if (tx.buyerId) {
                    buyerStats.set(tx.buyerId, (buyerStats.get(tx.buyerId) || 0) + 1);
                }
            }

            if (tx.action === 'PAYMENT' && tx.payload.amount) {
                totalTransactions++;
                totalValue += parseFloat(tx.payload.amount);
            }
        }

        return {
            totalBlocks: this.chain.length,
            totalContracts,
            totalTransactions,
            totalValue: totalValue.toFixed(2),
            topCrops: Array.from(cropStats.entries()).sort((a, b) => b[1] - a[1]).slice(0, 5),
            activeFarmers: farmerStats.size,
            activeBuyers: buyerStats.size,
            chainValid: this.isChainValid()
        };
    }

    exportChain() {
        return {
            metadata: {
                length: this.chain.length,
                difficulty: this.difficulty,
                lastUpdated: new Date().toISOString(),
                isValid: this.isChainValid()
            },
            blocks: this.chain.map(block => ({
                index: block.index,
                timestamp: block.timestamp,
                data: block.data,
                hash: block.hash,
                previousHash: block.previousHash,
                nonce: block.nonce,
                merkleRoot: block.merkleRoot
            }))
        };
    }

    importChain(chainData) {
        if (!chainData || !chainData.blocks || chainData.blocks.length === 0) {
            return false;
        }

        const loadedChain = chainData.blocks.map(blockData => {
            const block = new Block(
                blockData.timestamp,
                blockData.data,
                blockData.previousHash,
                blockData.validatorId
            );
            block.index = blockData.index;
            block.hash = blockData.hash;
            block.nonce = blockData.nonce;
            block.merkleRoot = blockData.merkleRoot;
            return block;
        });

        this.chain = loadedChain;
        if (this.isChainValid()) {
            this.chain.forEach(block => {
                if (block.data.transactionId) {
                    this.transactionPool.set(block.data.transactionId, {
                        blockIndex: block.index,
                        blockHash: block.hash,
                        timestamp: block.timestamp
                    });
                }
            });
            return true;
        } else {
            this.chain = [this.createGenesisBlock()];
            return false;
        }
    }

    // Replace local chain with remote chain (after consensus)
    replaceChain(newChain, reason = 'Consensus') {
        console.log(`\n🔄 Replacing local chain...`);
        console.log(`   Reason: ${reason}`);
        console.log(`   Old length: ${this.chain.length}`);
        console.log(`   New length: ${newChain.length}`);

        this.chain = newChain;

        // Rebuild transaction pool and cache
        this.transactionPool.clear();
        this.contractCache.clear();

        for (const block of this.chain) {
            if (block.data.transactionId) {
                this.transactionPool.set(block.data.transactionId, {
                    blockIndex: block.index,
                    blockHash: block.hash,
                    timestamp: block.timestamp
                });
            }
        }

        console.log(`✅ Chain replaced successfully`);

        // Emit event
        if (this.isDistributed) {
            this.emit('chain-replaced', newChain);
        }

        return true;
    }

    // Enable distributed mode
    enableDistributedMode(nodeId) {
        this.isDistributed = true;
        this.nodeId = nodeId;
        console.log(`🌐 Distributed mode enabled for node: ${nodeId}`);
    }
}

// ==========================================
// CRYPTOGRAPHIC SIGNATURE MODULE
// ==========================================

// 1. Generate Wallet (User does this once)
// Returns public and private keys using ECDSA (secp256k1)
function generateWallet() {
    return crypto.generateKeyPairSync('ec', {
        namedCurve: 'secp256k1',
        publicKeyEncoding: { type: 'spki', format: 'pem' },
        privateKeyEncoding: { type: 'pkcs8', format: 'pem' }
    });
}

// 2. Sign Transaction Data
// Creates a digital signature using private key and SHA256 hash
function signTransaction(transactionData, privateKey) {
    const sign = crypto.createSign('SHA256');
    sign.update(JSON.stringify(transactionData));
    sign.end();
    return sign.sign(privateKey, 'hex');
}

// 3. Verify Transaction Signature
// Validates a signature using public key and original data
function verifySignature(transactionData, signature, publicKey) {
    try {
        const verify = crypto.createVerify('SHA256');
        verify.update(JSON.stringify(transactionData));
        verify.end();
        return verify.verify(publicKey, signature, 'hex');
    } catch (error) {
        console.error('❌ Signature verification error:', error.message);
        return false;
    }
}

module.exports = { Block, Blockchain, generateWallet, signTransaction, verifySignature };
