// ==========================================
// TEST NGROK TOKEN
// ==========================================
require('dotenv').config();
const ngrok = require('ngrok');

async function testNgrok() {
    try {
        const token = process.env.NGROK_AUTH_TOKEN;

        if (!token) {
            console.log('❌ NGROK_AUTH_TOKEN not set in .env');
            return;
        }

        console.log('Testing ngrok token...');
        console.log(`Token (first 20 chars): ${token.substring(0, 20)}...`);

        // Try to authenticate
        await ngrok.authtoken(token);
        console.log('✅ Token authentication successful!');

        // Try to connect
        console.log('\nAttempting to create tunnel...');
        const url = await ngrok.connect(3000);
        console.log('✅ Tunnel created:', url);

        // List tunnels
        const tunnels = await ngrok.getApi().get('/api/tunnels');
        console.log('✅ Tunnels:', tunnels.data);

        // Disconnect
        await ngrok.disconnect();
        console.log('✅ Disconnected');

    } catch (error) {
        console.error('❌ Error:', error.message);
        console.error('Stack:', error.stack);
    }
}

testNgrok();
