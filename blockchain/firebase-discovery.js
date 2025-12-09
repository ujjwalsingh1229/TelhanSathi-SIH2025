// ==========================================
// NODE DISCOVERY & REGISTRY - FIREBASE BASED
// ==========================================
require('dotenv').config();
const { saveToFirebase, loadFromFirebase } = require('./firebase');

class FirebaseNodeDiscovery {
    constructor(nodeId, publicUrl, nodeInfo = {}) {
        this.nodeId = nodeId;
        this.publicUrl = publicUrl;
        this.nodeInfo = {
            nodeId: nodeId,
            publicUrl: publicUrl,
            timestamp: Date.now(),
            isValidator: nodeInfo.isValidator || false,
            reputation: nodeInfo.reputation || 100,
            port: nodeInfo.port || 3000,
            version: '1.0.0',
            ...nodeInfo
        };
        this.discoveryPath = 'nodes/registry';
        this.heartbeatInterval = null;
        this.heartbeatRate = 30000; // 30 seconds
    }

    // Register node in Firebase
    async registerNode() {
        try {
            const nodePath = `${this.discoveryPath}/${this.nodeId}`;
            await saveToFirebase(nodePath, this.nodeInfo);
            console.log(`✅ Node registered in Firebase: ${this.nodeId}`);
            console.log(`   Public URL: ${this.publicUrl}`);

            // Start heartbeat
            this.startHeartbeat();
            return true;
        } catch (error) {
            console.error('❌ Node registration failed:', error.message);
            return false;
        }
    }

    // Unregister node
    async unregisterNode() {
        try {
            await this.stopHeartbeat();
            const nodePath = `${this.discoveryPath}/${this.nodeId}`;
            await saveToFirebase(nodePath, null); // Delete by setting to null
            console.log(`✅ Node unregistered from Firebase`);
            return true;
        } catch (error) {
            console.error('❌ Node unregistration failed:', error.message);
            return false;
        }
    }

    // Start periodic heartbeat
    startHeartbeat() {
        this.heartbeatInterval = setInterval(async () => {
            try {
                const nodePath = `${this.discoveryPath}/${this.nodeId}`;
                this.nodeInfo.timestamp = Date.now();
                await saveToFirebase(nodePath, this.nodeInfo);
            } catch (error) {
                console.error('❌ Heartbeat failed:', error.message);
            }
        }, this.heartbeatRate);
    }

    // Stop heartbeat
    async stopHeartbeat() {
        if (this.heartbeatInterval) {
            clearInterval(this.heartbeatInterval);
            this.heartbeatInterval = null;
        }
    }

    // Discover all active nodes
    async discoverNodes() {
        try {
            const allNodes = await loadFromFirebase(this.discoveryPath);
            if (!allNodes) return [];

            const now = Date.now();
            const activeNodes = [];

            for (const [nodeId, nodeData] of Object.entries(allNodes)) {
                // Consider node active if heartbeat within 60 seconds
                if (now - nodeData.timestamp < 60000) {
                    activeNodes.push(nodeData);
                }
            }

            return activeNodes;
        } catch (error) {
            console.error('❌ Node discovery failed:', error.message);
            return [];
        }
    }

    // Get specific node info
    async getNodeInfo(nodeId) {
        try {
            const nodePath = `${this.discoveryPath}/${nodeId}`;
            return await loadFromFirebase(nodePath);
        } catch (error) {
            console.error(`❌ Failed to get node info for ${nodeId}:`, error.message);
            return null;
        }
    }

    // Update node reputation
    async updateReputation(nodeId, reputationChange) {
        try {
            const nodeData = await this.getNodeInfo(nodeId);
            if (!nodeData) return false;

            nodeData.reputation = Math.max(0, (nodeData.reputation || 100) + reputationChange);
            nodeData.timestamp = Date.now();

            const nodePath = `${this.discoveryPath}/${nodeId}`;
            await saveToFirebase(nodePath, nodeData);
            console.log(`✅ Node reputation updated: ${nodeId} -> ${nodeData.reputation}`);
            return true;
        } catch (error) {
            console.error('❌ Failed to update reputation:', error.message);
            return false;
        }
    }

    // Get active validators
    async getValidators() {
        try {
            const allNodes = await this.discoverNodes();
            return allNodes.filter(node => node.isValidator);
        } catch (error) {
            console.error('❌ Failed to get validators:', error.message);
            return [];
        }
    }

    // Update current node info
    async updateNodeInfo(updates) {
        try {
            this.nodeInfo = { ...this.nodeInfo, ...updates, timestamp: Date.now() };
            const nodePath = `${this.discoveryPath}/${this.nodeId}`;
            await saveToFirebase(nodePath, this.nodeInfo);
            return true;
        } catch (error) {
            console.error('❌ Failed to update node info:', error.message);
            return false;
        }
    }
}

module.exports = FirebaseNodeDiscovery;
