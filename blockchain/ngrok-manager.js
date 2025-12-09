// ==========================================
// NGROK TUNNEL MANAGER - MULTI-PC DISTRIBUTION
// ==========================================
require('dotenv').config();
const axios = require('axios');
const ngrok = require('ngrok');

class NgrokTunnelManager {
    constructor(httpPort, nodeId) {
        this.httpPort = httpPort;
        this.nodeId = nodeId;
        this.publicUrl = null;
        this.authToken = process.env.NGROK_AUTH_TOKEN;
        this.ngrokRegion = process.env.NGROK_REGION || 'in'; // India region, change as needed
        this.isConnected = false;
    }

    // Connect to ngrok
    async connect() {
        try {
            if (this.authToken) {
                await ngrok.authtoken(this.authToken);
                console.log('🔐 ngrok authentication token loaded');
            }

            this.publicUrl = await ngrok.connect({
                proto: 'http',
                addr: this.httpPort,
                region: this.ngrokRegion,
                onStatusChange: (status) => {
                    console.log(`ngrok status: ${status}`);
                }
            });

            this.isConnected = true;
            console.log(`🌐 ngrok tunnel created: ${this.publicUrl}`);
            console.log(`   Node ID: ${this.nodeId}`);
            console.log(`   Local: http://localhost:${this.httpPort}`);
            console.log(`   Public: ${this.publicUrl}`);

            return this.publicUrl;
        } catch (error) {
            console.error('❌ ngrok connection failed:', error.message);
            console.log('   Make sure NGROK_AUTH_TOKEN is set in .env');
            throw error;
        }
    }

    // Disconnect from ngrok
    async disconnect() {
        try {
            if (this.isConnected) {
                await ngrok.disconnect();
                this.isConnected = false;
                console.log('✅ ngrok tunnel closed');
            }
        } catch (error) {
            console.error('❌ ngrok disconnect error:', error.message);
        }
    }

    // Get public URL
    getPublicUrl() {
        return this.publicUrl;
    }

    // Get ngrok status
    async getStatus() {
        try {
            const response = await axios.get('http://localhost:4040/api/tunnels');
            return response.data;
        } catch (error) {
            return null;
        }
    }

    // Test tunnel connectivity
    async testTunnel() {
        try {
            if (!this.publicUrl) {
                return { status: 'NOT_CONNECTED', error: 'Tunnel not established' };
            }

            const response = await axios.get(`${this.publicUrl}/stats`, { timeout: 5000 });
            return { status: 'CONNECTED', data: response.data };
        } catch (error) {
            return { status: 'ERROR', error: error.message };
        }
    }
}

module.exports = NgrokTunnelManager;
