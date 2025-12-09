// ==========================================
// LOCAL STORAGE MODULE
// ==========================================
const fs = require('fs').promises;
const path = require('path');

class LocalStorage {
    constructor(storagePath = './blockchain-data') {
        this.storagePath = storagePath;
        this.chainFile = path.join(storagePath, 'blockchain.json');
        this.nodesFile = path.join(storagePath, 'nodes.json');
        this.transactionsFile = path.join(storagePath, 'transactions.json');
        this.initialized = false;
    }

    async initialize() {
        try {
            // Create storage directory if it doesn't exist
            await fs.mkdir(this.storagePath, { recursive: true });
            console.log(`📁 Local storage initialized at: ${this.storagePath}`);
            this.initialized = true;
            return true;
        } catch (error) {
            console.error('❌ Failed to initialize local storage:', error.message);
            return false;
        }
    }

    async saveBlockchain(chainData) {
        try {
            if (!this.initialized) await this.initialize();

            const data = JSON.stringify(chainData, null, 2);
            await fs.writeFile(this.chainFile, data, 'utf8');

            // Also save a timestamped backup
            const backupFile = path.join(
                this.storagePath,
                `blockchain-backup-${Date.now()}.json`
            );
            await fs.writeFile(backupFile, data, 'utf8');

            // Keep only last 5 backups
            await this.cleanupBackups();

            console.log(`💾 Blockchain saved locally (${chainData.metadata.length} blocks)`);
            return true;
        } catch (error) {
            console.error('❌ Failed to save blockchain locally:', error.message);
            return false;
        }
    }

    async loadBlockchain() {
        try {
            if (!this.initialized) await this.initialize();

            const data = await fs.readFile(this.chainFile, 'utf8');
            const chainData = JSON.parse(data);

            console.log(`📥 Blockchain loaded from local storage (${chainData.metadata?.length || 0} blocks)`);
            return chainData;
        } catch (error) {
            if (error.code === 'ENOENT') {
                console.log('ℹ️  No local blockchain file found');
                return null;
            }
            console.error('❌ Failed to load blockchain locally:', error.message);
            return null;
        }
    }

    async saveNodes(nodes) {
        try {
            if (!this.initialized) await this.initialize();

            const data = JSON.stringify(nodes, null, 2);
            await fs.writeFile(this.nodesFile, data, 'utf8');

            console.log(`💾 Nodes saved locally (${nodes.length} nodes)`);
            return true;
        } catch (error) {
            console.error('❌ Failed to save nodes locally:', error.message);
            return false;
        }
    }

    async loadNodes() {
        try {
            if (!this.initialized) await this.initialize();

            const data = await fs.readFile(this.nodesFile, 'utf8');
            const nodes = JSON.parse(data);

            console.log(`📥 Nodes loaded from local storage (${nodes.length} nodes)`);
            return nodes;
        } catch (error) {
            if (error.code === 'ENOENT') {
                console.log('ℹ️  No nodes file found, starting fresh');
                return [];
            }
            console.error('❌ Failed to load nodes locally:', error.message);
            return [];
        }
    }

    async saveTransactions(transactions) {
        try {
            if (!this.initialized) await this.initialize();

            const data = JSON.stringify(Array.from(transactions.entries()), null, 2);
            await fs.writeFile(this.transactionsFile, data, 'utf8');

            return true;
        } catch (error) {
            console.error('❌ Failed to save transactions locally:', error.message);
            return false;
        }
    }

    async loadTransactions() {
        try {
            if (!this.initialized) await this.initialize();

            const data = await fs.readFile(this.transactionsFile, 'utf8');
            const txArray = JSON.parse(data);

            return new Map(txArray);
        } catch (error) {
            if (error.code === 'ENOENT') {
                return new Map();
            }
            console.error('❌ Failed to load transactions locally:', error.message);
            return new Map();
        }
    }

    async cleanupBackups() {
        try {
            const files = await fs.readdir(this.storagePath);
            const backups = files
                .filter(f => f.startsWith('blockchain-backup-'))
                .map(f => ({
                    name: f,
                    path: path.join(this.storagePath, f),
                    time: parseInt(f.match(/\d+/)[0])
                }))
                .sort((a, b) => b.time - a.time);

            // Keep only last 5 backups
            for (let i = 5; i < backups.length; i++) {
                await fs.unlink(backups[i].path);
            }
        } catch (error) {
            // Silent fail for cleanup
        }
    }

    async getStats() {
        try {
            const stats = {
                storagePath: this.storagePath,
                initialized: this.initialized,
                files: {}
            };

            try {
                const chainStat = await fs.stat(this.chainFile);
                stats.files.blockchain = {
                    size: chainStat.size,
                    modified: chainStat.mtime
                };
            } catch (e) {
                stats.files.blockchain = null;
            }

            try {
                const nodesStat = await fs.stat(this.nodesFile);
                stats.files.nodes = {
                    size: nodesStat.size,
                    modified: nodesStat.mtime
                };
            } catch (e) {
                stats.files.nodes = null;
            }

            return stats;
        } catch (error) {
            return null;
        }
    }
}

module.exports = LocalStorage;
