// ==========================================
// FIREBASE MODULE
// ==========================================
require('dotenv').config();

// Firebase Configuration
const firebaseConfig = {
    apiKey: process.env.FIREBASE_API_KEY || "AIzaSyAiKojN1cx2x4BsrFN2UI13hvh49KVZxcw",
    authDomain: process.env.FIREBASE_AUTH_DOMAIN || "sih2025-72065.firebaseapp.com",
    projectId: process.env.FIREBASE_PROJECT_ID || "sih2025-72065",
    storageBucket: process.env.FIREBASE_STORAGE_BUCKET || "sih2025-72065.firebasestorage.app",
    messagingSenderId: process.env.FIREBASE_MESSAGING_SENDER_ID || "299544551392",
    appId: process.env.FIREBASE_APP_ID || "1:299544551392:web:90e19ad01a4a803c96d585",
    databaseURL: process.env.FIREBASE_DATABASE_URL || "https://sih2025-72065-default-rtdb.asia-southeast1.firebasedatabase.app"
};

const FIREBASE_DB_URL = firebaseConfig.databaseURL;

// Retry helper for network resilience
async function fetchWithRetry(url, options = {}, retries = 3) {
    for (let i = 0; i < retries; i++) {
        try {
            return await fetch(url, {
                ...options,
                timeout: 10000
            });
        } catch (error) {
            if (i === retries - 1) throw error;
            await new Promise(resolve => setTimeout(resolve, 1000 * (i + 1)));
        }
    }
}

async function saveToFirebase(path, data) {
    try {
        const url = `${FIREBASE_DB_URL}/${path}.json`;
        const response = await fetchWithRetry(url, {
            method: 'PUT',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(data)
        });

        if (!response.ok) {
            const errorText = await response.text();
            throw new Error(`HTTP ${response.status}: ${errorText}`);
        }

        const result = await response.json();
        return result;
    } catch (error) {
        console.error(`   ❌ Firebase save error:`, error.message);
        return null;
    }
}

async function loadFromFirebase(path) {
    try {
        const url = `${FIREBASE_DB_URL}/${path}.json`;
        const response = await fetchWithRetry(url);

        if (!response.ok && response.status !== 404) {
            throw new Error(`HTTP ${response.status}`);
        }

        // Return empty object if no data (404 or null)
        if (response.status === 404 || !response.ok) {
            return null;
        }

        const data = await response.json();
        return data;
    } catch (error) {
        console.error(`   ❌ Firebase load error:`, error.message);
        return null;
    }
}

console.log('🔥 Firebase REST API initialized!');
console.log(`   Database: ${FIREBASE_DB_URL}`);

module.exports = {
    saveToFirebase,
    loadFromFirebase,
    firebaseConfig,
    FIREBASE_DB_URL
};
