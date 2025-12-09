// ==========================================
// P2P NETWORK MODULE
// ==========================================
const WebSocket = require('ws');
const EventEmitter = require('events');

class P2PNetwork extends EventEmitter {
    constructor(port, nodeId) {
        super();
        this.port = port;
        this.nodeId = nodeId;
        this.server = null;
        this.peers = new Map(); // nodeId -> websocket
        this.peerInfo = new Map(); // nodeId -> {url, lastSeen, isValidator}
    }

    // Start WebSocket server for this node
    async start() {
        return new Promise((resolve, reject) => {
            try {
                this.server = new WebSocket.Server({ port: this.port });

                this.server.on('connection', (ws, req) => {
                    this.handleConnection(ws, req);
                });

                this.server.on('error', (error) => {
                    console.error('❌ P2P Server error:', error.message);
                    reject(error);
                });

                this.server.on('listening', () => {
                    console.log(`🌐 P2P Network started on port ${this.port}`);
                    console.log(`📍 Node ID: ${this.nodeId}`);
                    resolve();
                });

            } catch (error) {
                reject(error);
            }
        });
    }

    handleConnection(ws, req) {
        console.log(`🔗 New peer connection from ${req.socket.remoteAddress}`);

        ws.on('message', (data) => {
            try {
                const message = JSON.parse(data.toString());
                this.handleMessage(ws, message);
            } catch (error) {
                console.error('❌ Invalid message received:', error.message);
            }
        });

        ws.on('close', () => {
            // Remove peer from active connections
            for (const [nodeId, socket] of this.peers.entries()) {
                if (socket === ws) {
                    this.peers.delete(nodeId);
                    console.log(`👋 Peer ${nodeId} disconnected`);
                    this.emit('peer-disconnected', nodeId);
                    break;
                }
            }
        });

        ws.on('error', (error) => {
            console.error('❌ WebSocket error:', error.message);
        });

        // Send handshake
        this.sendToPeer(ws, {
            type: 'HANDSHAKE',
            nodeId: this.nodeId,
            timestamp: Date.now()
        });
    }

    handleMessage(ws, message) {
        switch (message.type) {
            case 'HANDSHAKE':
                this.handleHandshake(ws, message);
                break;

            case 'HANDSHAKE_ACK':
                this.handleHandshakeAck(ws, message);
                break;

            case 'NEW_BLOCK':
                this.emit('new-block', message.block, message.fromNode);
                break;

            case 'NEW_TRANSACTION':
                this.emit('new-transaction', message.transaction, message.fromNode);
                break;

            case 'CHAIN_REQUEST':
                this.emit('chain-request', message.fromNode, ws);
                break;

            case 'CHAIN_RESPONSE':
                this.emit('chain-response', message.chain, message.fromNode);
                break;

            case 'NODE_LIST_REQUEST':
                this.emit('node-list-request', message.fromNode, ws);
                break;

            case 'NODE_LIST_RESPONSE':
                this.emit('node-list-response', message.nodes, message.fromNode);
                break;

            case 'PING':
                this.sendToPeer(ws, { type: 'PONG', timestamp: Date.now() });
                break;

            case 'PONG':
                // Update last seen time
                if (message.nodeId) {
                    const info = this.peerInfo.get(message.nodeId);
                    if (info) {
                        info.lastSeen = Date.now();
                    }
                }
                break;

            default:
                console.log('⚠️  Unknown message type:', message.type);
        }
    }

    handleHandshake(ws, message) {
        const { nodeId, timestamp } = message;

        // Store peer connection
        this.peers.set(nodeId, ws);

        if (!this.peerInfo.has(nodeId)) {
            this.peerInfo.set(nodeId, {
                nodeId,
                connectedAt: timestamp,
                lastSeen: Date.now(),
                isValidator: false
            });
        }

        console.log(`✅ Handshake complete with node: ${nodeId}`);
        this.emit('peer-connected', nodeId);

        // Send handshake response
        this.sendToPeer(ws, {
            type: 'HANDSHAKE_ACK',
            nodeId: this.nodeId,
            timestamp: Date.now()
        });
    }

    handleHandshakeAck(ws, message) {
        const { nodeId, timestamp } = message;

        // Update peer info with acknowledgment
        const info = this.peerInfo.get(nodeId);
        if (info) {
            info.lastSeen = Date.now();
            info.handshakeComplete = true;
        }

        console.log(`✅ Handshake acknowledged by node: ${nodeId}`);
    }

    // Connect to a peer node
    async connectToPeer(url, nodeId) {
        return new Promise((resolve, reject) => {
            try {
                const ws = new WebSocket(url);

                ws.on('open', () => {
                    console.log(`🔗 Connected to peer: ${url}`);
                    this.peers.set(nodeId, ws);
                    this.peerInfo.set(nodeId, {
                        url,
                        nodeId,
                        lastSeen: Date.now(),
                        isValidator: false
                    });

                    // Setup message handlers
                    ws.on('message', (data) => {
                        try {
                            const message = JSON.parse(data.toString());
                            this.handleMessage(ws, message);
                        } catch (error) {
                            console.error('❌ Invalid message:', error.message);
                        }
                    });

                    ws.on('close', () => {
                        this.peers.delete(nodeId);
                        console.log(`👋 Disconnected from peer: ${nodeId}`);
                        this.emit('peer-disconnected', nodeId);
                    });

                    ws.on('error', (error) => {
                        console.error(`❌ Peer ${nodeId} error:`, error.message);
                    });

                    resolve(ws);
                });

                ws.on('error', (error) => {
                    console.error(`❌ Failed to connect to ${url}:`, error.message);
                    reject(error);
                });

            } catch (error) {
                reject(error);
            }
        });
    }

    // Broadcast to all connected peers
    broadcast(message) {
        const data = JSON.stringify({
            ...message,
            fromNode: this.nodeId,
            timestamp: Date.now()
        });

        let sent = 0;
        for (const [nodeId, ws] of this.peers.entries()) {
            if (ws.readyState === WebSocket.OPEN) {
                try {
                    ws.send(data);
                    sent++;
                } catch (error) {
                    console.error(`❌ Failed to send to ${nodeId}:`, error.message);
                }
            }
        }

        console.log(`📡 Broadcasted ${message.type} to ${sent} peers`);
        return sent;
    }

    // Send message to specific peer
    sendToPeer(ws, message) {
        if (ws.readyState === WebSocket.OPEN) {
            try {
                ws.send(JSON.stringify({
                    ...message,
                    fromNode: this.nodeId,
                    timestamp: Date.now()
                }));
                return true;
            } catch (error) {
                console.error('❌ Failed to send message:', error.message);
                return false;
            }
        }
        return false;
    }

    // Get list of connected peers
    getPeers() {
        return Array.from(this.peerInfo.values());
    }

    // Check peer health
    startHealthCheck(interval = 30000) {
        setInterval(() => {
            for (const [nodeId, ws] of this.peers.entries()) {
                if (ws.readyState === WebSocket.OPEN) {
                    this.sendToPeer(ws, { type: 'PING' });
                }
            }
        }, interval);
    }

    // Disconnect from peer
    disconnectPeer(nodeId) {
        const ws = this.peers.get(nodeId);
        if (ws) {
            ws.close();
            this.peers.delete(nodeId);
            this.peerInfo.delete(nodeId);
            console.log(`🔌 Disconnected from peer: ${nodeId}`);
            return true;
        }
        return false;
    }

    // Shutdown P2P network
    async shutdown() {
        console.log('🔌 Shutting down P2P network...');

        // Close all peer connections
        for (const ws of this.peers.values()) {
            ws.close();
        }
        this.peers.clear();

        // Close server
        if (this.server) {
            return new Promise((resolve) => {
                this.server.close(() => {
                    console.log('✅ P2P network shut down');
                    resolve();
                });
            });
        }
    }

    getStats() {
        return {
            nodeId: this.nodeId,
            port: this.port,
            connectedPeers: this.peers.size,
            peers: this.getPeers(),
            serverRunning: this.server !== null
        };
    }
}

module.exports = P2PNetwork;
