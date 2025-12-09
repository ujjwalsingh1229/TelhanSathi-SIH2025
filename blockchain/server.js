// ==========================================
// EXPRESS SERVER MODULE - DISTRIBUTED VERSION
// ==========================================
require('dotenv').config();
const express = require('express');
const bodyParser = require('body-parser');
const cors = require('cors');
const helmet = require('helmet');
const rateLimit = require('express-rate-limit');
const Joi = require('joi');
const jwt = require('jsonwebtoken');
const validator = require('validator');
const os = require('os');
const { Block, Blockchain } = require('./blockchain');
const firebaseModule = require('./firebase');
const { saveToFirebase, loadFromFirebase } = firebaseModule;
const DistributedCoordinator = require('./distributed');
const NodeRegistry = require('./nodeRegistry');
const NgrokTunnelManager = require('./ngrok-manager');
const FirebaseNodeDiscovery = require('./firebase-discovery');
const createMobileAPIRoutes = require('./mobile-api');

// Configuration
const PORT = parseInt(process.env.PORT) || 3000;
const P2P_PORT = parseInt(process.env.P2P_PORT) || 6001;
const NODE_ID = process.env.NODE_ID || NodeRegistry.generateNodeId(os.hostname(), P2P_PORT);
const ENABLE_DISTRIBUTED = process.env.ENABLE_DISTRIBUTED === 'true';
const JWT_SECRET = process.env.JWT_SECRET || 'fallback-secret-key-change-this';
const JWT_EXPIRY = process.env.JWT_EXPIRY || '24h';
const MINING_DIFFICULTY = parseInt(process.env.MINING_DIFFICULTY) || 2;
const ALLOWED_ORIGINS = process.env.ALLOWED_ORIGINS ? process.env.ALLOWED_ORIGINS.split(',') : ['http://localhost:3000'];

// Initialize Blockchain
const telhanChain = new Blockchain(
    MINING_DIFFICULTY,
    parseInt(process.env.MINING_REWARD) || 50,
    parseInt(process.env.SAVE_THROTTLE_MS) || 5000,
    NODE_ID
);

// Initialize Distributed Coordinator
let distributedCoordinator = null;

// Initialize ngrok and discovery
let ngrokManager = null;
let firebaseDiscovery = null;

// Load blockchain and setup distributed system
(async () => {
    try {
        console.log('\n🚀 Initializing TelhanSathi Blockchain...');
        console.log(`   Node ID: ${NODE_ID}`);
        console.log(`   HTTP Port: ${PORT}`);
        console.log(`   P2P Port: ${P2P_PORT}`);
        console.log(`   Distributed Mode: ${ENABLE_DISTRIBUTED ? 'ENABLED' : 'DISABLED'}`);

        // Initialize ngrok if enabled
        const ENABLE_NGROK = process.env.ENABLE_NGROK === 'true';
        if (ENABLE_NGROK) {
            try {
                ngrokManager = new NgrokTunnelManager(PORT, NODE_ID);
                const publicUrl = await ngrokManager.connect();
                console.log(`🌐 ngrok tunnel established: ${publicUrl}`);
            } catch (error) {
                console.warn('⚠️  ngrok initialization skipped:', error.message);
                ngrokManager = null;
            }
        }

        if (ENABLE_DISTRIBUTED) {
            // Initialize distributed system
            distributedCoordinator = new DistributedCoordinator(
                telhanChain,
                NODE_ID,
                P2P_PORT,
                firebaseModule
            );

            await distributedCoordinator.initialize();

            // Try to load from local storage or Firebase
            const loaded = await distributedCoordinator.loadChain();
            if (!loaded) {
                console.log('🆕 Starting with fresh Genesis block');
                await distributedCoordinator.saveChain();
            }

            // Initialize Firebase node discovery
            const publicUrl = ngrokManager?.getPublicUrl() || `http://localhost:${PORT}`;
            firebaseDiscovery = new FirebaseNodeDiscovery(NODE_ID, publicUrl, {
                isValidator: process.env.IS_VALIDATOR === 'true',
                reputation: 100,
                port: PORT
            });

            await firebaseDiscovery.registerNode();
            console.log(`📍 Node registered in Firebase network`);

            // Connect to bootstrap nodes if specified
            const bootstrapNodes = process.env.BOOTSTRAP_NODES;
            if (bootstrapNodes) {
                // Format: "ws://localhost:6001,node1" or "ws://localhost:6001,node1;ws://localhost:6002,node2"
                const nodeEntries = bootstrapNodes.split(';');
                for (const entry of nodeEntries) {
                    const [url, id] = entry.split(',');
                    if (url && id && url.trim() && id.trim()) {
                        console.log(`🔗 Connecting to bootstrap node: ${url.trim()} (${id.trim()})`);
                        await distributedCoordinator.connectToNode(url.trim(), id.trim());
                    }
                }
            }

        } else {
            // Single node mode - load from Firebase only
            const data = await loadFromFirebase('blockchain');
            if (data && data.blocks) {
                const loaded = telhanChain.importChain(data);
                if (loaded) {
                    console.log(`✅ Loaded ${telhanChain.chain.length} blocks from Firebase`);
                } else {
                    console.log('🆕 Starting with fresh Genesis block');
                    await saveToFirebase('blockchain', telhanChain.exportChain());
                }
            } else {
                console.log('🆕 Starting with fresh Genesis block');
                await saveToFirebase('blockchain', telhanChain.exportChain());
            }

            // Initialize Firebase node discovery even in single node mode
            const publicUrl = ngrokManager?.getPublicUrl() || `http://localhost:${PORT}`;
            firebaseDiscovery = new FirebaseNodeDiscovery(NODE_ID, publicUrl, {
                isValidator: process.env.IS_VALIDATOR === 'true',
                reputation: 100,
                port: PORT
            });

            await firebaseDiscovery.registerNode();
            console.log(`📍 Node registered in Firebase network`);

            // Auto-save to Firebase in single node mode
            setInterval(async () => {
                try {
                    await saveToFirebase('blockchain', telhanChain.exportChain());
                } catch (error) {
                    console.error('⚠️  Auto-save failed:', error.message);
                }
            }, parseInt(process.env.SAVE_THROTTLE_MS) || 30000);
        }

        console.log('✅ Blockchain initialized successfully\n');

    } catch (error) {
        console.error('❌ Initialization error:', error.message);
        console.log('Starting with in-memory blockchain only');
    }
})();

// Joi Validation Schemas
const schemas = {
    transaction: Joi.object({
        from: Joi.string().min(3).max(100).required(),
        to: Joi.string().min(3).max(100).required(),
        amount: Joi.number().positive().required(),
        crop: Joi.string().min(2).max(50).required(),
        quantity: Joi.string().max(50).required(),
        upiTransactionId: Joi.string().max(100).optional(),
        location: Joi.string().max(200).optional()
    }),

    contract: Joi.object({
        contractId: Joi.string().required(),
        farmerId: Joi.string().required(),
        farmerName: Joi.string().min(2).max(100).required(),
        farmerPhone: Joi.string().pattern(/^[0-9]{10}$/).optional(),
        buyerId: Joi.string().required(),
        buyerName: Joi.string().min(2).max(100).required(),
        buyerPhone: Joi.string().pattern(/^[0-9]{10}$/).optional(),
        crop: Joi.string().required(),
        variety: Joi.string().optional(),
        quantity: Joi.number().positive().required(),
        unit: Joi.string().optional(),
        pricePerUnit: Joi.number().positive().required(),
        totalAmount: Joi.number().positive().required(),
        advanceAmount: Joi.number().min(0).optional(),
        expectedDeliveryDate: Joi.string().optional(),
        qualityParameters: Joi.object().optional(),
        location: Joi.string().optional()
    }),

    payment: Joi.object({
        contractId: Joi.string().required(),
        amount: Joi.number().positive().required(),
        paymentMode: Joi.string().valid('UPI', 'BANK_TRANSFER', 'CASH', 'CHEQUE').required(),
        upiTransactionId: Joi.string().optional(),
        bankReferenceNo: Joi.string().optional()
    })
};

// Middleware
const validateInput = (schema) => {
    return (req, res, next) => {
        const { error, value } = schema.validate(req.body, { abortEarly: false });

        if (error) {
            const errors = error.details.map(detail => ({
                field: detail.path.join('.'),
                message: detail.message
            }));

            console.log('❌ Validation failed:', errors);
            return res.status(400).json({
                success: false,
                error: 'Validation failed',
                details: errors
            });
        }

        req.validatedBody = value;
        next();
    };
};

const authenticateToken = (req, res, next) => {
    const authHeader = req.headers['authorization'];
    const token = authHeader && authHeader.split(' ')[1];

    if (!token) {
        return res.status(401).json({ error: 'Access token required' });
    }

    jwt.verify(token, JWT_SECRET, (err, user) => {
        if (err) {
            return res.status(403).json({ error: 'Invalid or expired token' });
        }
        req.user = user;
        next();
    });
};

const optionalAuth = (req, res, next) => {
    const authHeader = req.headers['authorization'];
    const token = authHeader && authHeader.split(' ')[1];

    if (token) {
        jwt.verify(token, JWT_SECRET, (err, user) => {
            if (!err) {
                req.user = user;
            }
        });
    }
    next();
};

const sanitizeString = (str) => {
    if (typeof str !== 'string') return str;
    return validator.escape(str.trim());
};

// Express App
const app = express();

// Security
app.use(helmet({
    contentSecurityPolicy: {
        directives: {
            defaultSrc: ["'self'"],
            styleSrc: ["'self'", "'unsafe-inline'", "https://cdn.jsdelivr.net"],
            scriptSrc: ["'self'", "'unsafe-inline'", "https://cdn.jsdelivr.net"],
            imgSrc: ["'self'", "data:", "https:"],
        },
    },
    crossOriginEmbedderPolicy: false
}));

app.use(cors({
    origin: function (origin, callback) {
        if (!origin) return callback(null, true);
        if (origin.includes('localhost') || origin.includes('127.0.0.1')) {
            return callback(null, true);
        }
        if (ALLOWED_ORIGINS.indexOf(origin) !== -1) {
            callback(null, true);
        } else {
            console.log('⚠️ CORS blocked origin:', origin);
            callback(new Error('Not allowed by CORS'));
        }
    },
    credentials: true,
    methods: ['GET', 'POST', 'PUT', 'DELETE', 'OPTIONS'],
    allowedHeaders: ['Content-Type', 'Authorization', 'X-API-Key']
}));

// Rate Limiting
const apiLimiter = rateLimit({
    windowMs: parseInt(process.env.RATE_LIMIT_WINDOW_MS) || 15 * 60 * 1000,
    max: parseInt(process.env.RATE_LIMIT_MAX_REQUESTS) || 100,
    message: {
        error: 'Too many requests from this IP, please try again later.',
        retryAfter: '15 minutes'
    },
    standardHeaders: true,
    legacyHeaders: false,
});

const strictLimiter = rateLimit({
    windowMs: 60 * 1000,
    max: 10,
    message: { error: 'Too many transaction requests, please slow down.' }
});

app.use('/api/', apiLimiter);
app.use(['/transaction/', '/contract/'], strictLimiter);

app.use(bodyParser.json({ limit: '10mb' }));
app.use(bodyParser.urlencoded({ extended: true, limit: '10mb' }));

app.use((req, res, next) => {
    const timestamp = new Date().toISOString();
    console.log(`[${timestamp}] ${req.method} ${req.path} - IP: ${req.ip}`);
    next();
});

app.use(express.static(__dirname));

// Mount mobile API routes
const mobileRoutes = createMobileAPIRoutes(telhanChain, firebaseDiscovery, ngrokManager);
app.use(mobileRoutes);

app.use((err, req, res, next) => {
    if (err.message === 'Not allowed by CORS') {
        return res.status(403).json({ error: 'CORS policy violation' });
    }
    next(err);
});

// Export for use in routes
module.exports = {
    app,
    telhanChain,
    distributedCoordinator,
    ngrokManager,
    firebaseDiscovery,
    schemas,
    validateInput,
    authenticateToken,
    optionalAuth,
    sanitizeString,
    JWT_SECRET,
    JWT_EXPIRY,
    PORT,
    P2P_PORT,
    NODE_ID,
    ENABLE_DISTRIBUTED,
    Block
};
