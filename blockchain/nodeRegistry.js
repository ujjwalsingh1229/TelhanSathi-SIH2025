// ==========================================
// NODE REGISTRY MODULE
// ==========================================
const crypto = require('crypto');

class NodeRegistry {
    constructor() {
        this.nodes = new Map(); // nodeId -> node info
        this.validators = new Set(); // Set of validator nodeIds
        this.pendingNodes = new Map(); // Nodes awaiting admin approval
        this.blacklist = new Set(); // Blocked nodes
    }

    // Generate unique node ID
    static generateNodeId(host, port) {
        const data = `${host}:${port}:${Date.now()}`;
        return crypto.createHash('sha256').update(data).digest('hex').substring(0, 16);
    }

    // Register a new node (requires admin approval for production)
    registerNode(nodeData) {
        const {
            nodeId,
            url,
            host,
            port,
            publicKey,
            nodeType = 'peer', // 'peer' or 'validator'
            metadata = {}
        } = nodeData;

        if (this.blacklist.has(nodeId)) {
            return {
                success: false,
                error: 'Node is blacklisted'
            };
        }

        if (this.nodes.has(nodeId)) {
            return {
                success: false,
                error: 'Node already registered'
            };
        }

        const node = {
            nodeId,
            url,
            host,
            port,
            publicKey,
            nodeType,
            metadata,
            status: 'pending', // pending, active, inactive
            registeredAt: Date.now(),
            lastSeen: Date.now(),
            approvedBy: null,
            reputation: 100 // Node reputation score
        };

        // For now, auto-approve in development
        // In production, require admin approval
        if (process.env.NODE_ENV === 'production') {
            this.pendingNodes.set(nodeId, node);
            console.log(`⏳ Node ${nodeId} pending approval`);

            return {
                success: true,
                status: 'pending',
                message: 'Node registration pending admin approval',
                nodeId
            };
        } else {
            node.status = 'active';
            this.nodes.set(nodeId, node);
            console.log(`✅ Node ${nodeId} registered and activated`);

            return {
                success: true,
                status: 'active',
                message: 'Node registered successfully',
                nodeId
            };
        }
    }

    // Admin approves pending node
    approveNode(nodeId, adminId) {
        const node = this.pendingNodes.get(nodeId);

        if (!node) {
            return {
                success: false,
                error: 'Node not found in pending list'
            };
        }

        node.status = 'active';
        node.approvedBy = adminId;
        node.approvedAt = Date.now();

        this.nodes.set(nodeId, node);
        this.pendingNodes.delete(nodeId);

        console.log(`✅ Node ${nodeId} approved by admin ${adminId}`);

        return {
            success: true,
            message: 'Node approved successfully',
            node
        };
    }

    // Admin rejects pending node
    rejectNode(nodeId, adminId, reason) {
        const node = this.pendingNodes.get(nodeId);

        if (!node) {
            return {
                success: false,
                error: 'Node not found in pending list'
            };
        }

        this.pendingNodes.delete(nodeId);
        this.blacklist.add(nodeId);

        console.log(`❌ Node ${nodeId} rejected by admin ${adminId}: ${reason}`);

        return {
            success: true,
            message: 'Node rejected and blacklisted',
            reason
        };
    }

    // Promote node to validator
    promoteToValidator(nodeId, adminId) {
        const node = this.nodes.get(nodeId);

        if (!node) {
            return {
                success: false,
                error: 'Node not found'
            };
        }

        if (node.status !== 'active') {
            return {
                success: false,
                error: 'Node must be active to become validator'
            };
        }

        node.nodeType = 'validator';
        this.validators.add(nodeId);

        console.log(`⭐ Node ${nodeId} promoted to validator by admin ${adminId}`);

        return {
            success: true,
            message: 'Node promoted to validator',
            node
        };
    }

    // Demote validator to regular peer
    demoteValidator(nodeId, adminId) {
        const node = this.nodes.get(nodeId);

        if (!node) {
            return {
                success: false,
                error: 'Node not found'
            };
        }

        node.nodeType = 'peer';
        this.validators.delete(nodeId);

        console.log(`⬇️  Node ${nodeId} demoted from validator by admin ${adminId}`);

        return {
            success: true,
            message: 'Node demoted from validator',
            node
        };
    }

    // Remove node from network
    removeNode(nodeId, adminId, reason) {
        const node = this.nodes.get(nodeId);

        if (!node) {
            return {
                success: false,
                error: 'Node not found'
            };
        }

        this.nodes.delete(nodeId);
        this.validators.delete(nodeId);
        this.blacklist.add(nodeId);

        console.log(`🚫 Node ${nodeId} removed by admin ${adminId}: ${reason}`);

        return {
            success: true,
            message: 'Node removed from network',
            reason
        };
    }

    // Update node's last seen timestamp
    updateLastSeen(nodeId) {
        const node = this.nodes.get(nodeId);
        if (node) {
            node.lastSeen = Date.now();
            return true;
        }
        return false;
    }

    // Update node reputation
    updateReputation(nodeId, change, reason) {
        const node = this.nodes.get(nodeId);
        if (node) {
            node.reputation = Math.max(0, Math.min(100, node.reputation + change));

            if (node.reputation < 20) {
                console.log(`⚠️  Node ${nodeId} has low reputation (${node.reputation})`);
            }

            return {
                success: true,
                reputation: node.reputation,
                reason
            };
        }
        return {
            success: false,
            error: 'Node not found'
        };
    }

    // Get all active nodes
    getActiveNodes() {
        return Array.from(this.nodes.values())
            .filter(node => node.status === 'active');
    }

    // Get all validator nodes
    getValidators() {
        return Array.from(this.nodes.values())
            .filter(node => this.validators.has(node.nodeId));
    }

    // Get pending nodes (for admin approval)
    getPendingNodes() {
        return Array.from(this.pendingNodes.values());
    }

    // Get node info
    getNode(nodeId) {
        return this.nodes.get(nodeId) || null;
    }

    // Check if node is validator
    isValidator(nodeId) {
        return this.validators.has(nodeId);
    }

    // Check if node is active
    isActive(nodeId) {
        const node = this.nodes.get(nodeId);
        return node && node.status === 'active';
    }

    // Check for inactive nodes
    checkInactiveNodes(timeout = 5 * 60 * 1000) { // 5 minutes default
        const now = Date.now();
        const inactive = [];

        for (const [nodeId, node] of this.nodes.entries()) {
            if (node.status === 'active' && (now - node.lastSeen) > timeout) {
                node.status = 'inactive';
                inactive.push(nodeId);
                console.log(`⚠️  Node ${nodeId} marked as inactive`);
            }
        }

        return inactive;
    }

    // Export registry data
    exportData() {
        return {
            nodes: Array.from(this.nodes.entries()),
            validators: Array.from(this.validators),
            pendingNodes: Array.from(this.pendingNodes.entries()),
            blacklist: Array.from(this.blacklist)
        };
    }

    // Import registry data
    importData(data) {
        if (data.nodes) {
            this.nodes = new Map(data.nodes);
        }
        if (data.validators) {
            this.validators = new Set(data.validators);
        }
        if (data.pendingNodes) {
            this.pendingNodes = new Map(data.pendingNodes);
        }
        if (data.blacklist) {
            this.blacklist = new Set(data.blacklist);
        }

        console.log(`📥 Registry data imported: ${this.nodes.size} nodes, ${this.validators.size} validators`);
    }

    // Get statistics
    getStats() {
        return {
            totalNodes: this.nodes.size,
            activeNodes: this.getActiveNodes().length,
            validators: this.validators.size,
            pendingNodes: this.pendingNodes.size,
            blacklistedNodes: this.blacklist.size
        };
    }
}

module.exports = NodeRegistry;
