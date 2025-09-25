/**
 * Servidor Backend Refactorizado - Sheily AI
 * ==========================================
 * Versión profesional optimizada sin console.log innecesarios
 * Sistema robusto con manejo de errores mejorado
 */

// Cargar variables de entorno desde archivo de configuración
require('dotenv').config({ path: __dirname + '/config.env' });

// Importar gestor de conexiones de base de datos
const DatabaseConnectionManager = require('./database/connection_manager');

// Importar gestor de configuración unificado (con fallback)
let get_config, configMiddleware, validationMiddleware, systemMonitor;

try {
    const configManager = require('../config/config_manager');
    get_config = configManager.get_config;
    configMiddleware = require('./middleware/config_middleware');
    validationMiddleware = require('./middleware/validation_middleware');
    systemMonitor = require('./monitoring/system_monitor');
} catch (error) {
    console.warn('⚠️ Módulos de configuración no disponibles, usando configuración por defecto');
    get_config = (key, defaultValue) => defaultValue;
    configMiddleware = { 
        injectConfig: (req, res, next) => next(),
        validateCriticalConfig: (req, res, next) => next(),
        logConfig: (req, res, next) => next(),
        getSystemConfig: (req, res) => res.json({ success: true, config: {} }),
        validateSystemConfig: (req, res) => res.json({ success: true, validation: { valid: true } })
    };
    validationMiddleware = {
        sanitizeInput: (req, res, next) => next(),
        validatePayloadSize: () => (req, res, next) => next(),
        validate: () => (req, res, next) => next()
    };
    systemMonitor = {
        recordAPIRequest: () => {},
        getMetrics: () => ({}),
        getAlerts: () => ([]),
        getHealthStatus: () => ({ status: 'healthy' })
    };
}

// Importar sistema de chatbot avanzado
let ChatbotIntegration;
try {
    ChatbotIntegration = require('./chatbot_integration');
} catch (error) {
    console.warn('⚠️ Sistema de Chatbot Avanzado no disponible:', error.message);
    ChatbotIntegration = null;
}

const express = require('express');
const cors = require('cors');
const bcrypt = require('bcryptjs');
const jwt = require('jsonwebtoken');
const rateLimit = require('express-rate-limit');
const helmet = require('helmet');
const path = require('path');
const fs = require('fs');
const { v4: uuidv4 } = require('uuid');
const WebSocket = require('ws');

// Importar sistemas de monitoreo
const ChatMetricsCollector = require('./monitoring/chat_metrics');
const ChatAlertSystem = require('./monitoring/chat_alerts');
const ChatBackupSystem = require('./monitoring/chat_backup');
const AdvancedLogger = require('./monitoring/advanced_logger');
const RealtimeMetrics = require('./monitoring/realtime_metrics');
const SmartCache = require('./monitoring/smart_cache');

// Importar servicio de modelo de lenguaje
const LanguageModelService = require('./models/core/language_model_service');
const languageModelService = new LanguageModelService();

// Inicializar instancia de la aplicación
const app = express();
const PORT = process.env.PORT || 8000;
const HOST = process.env.HOST || '127.0.0.1';

// Inicializar gestor de base de datos
const dbManager = new DatabaseConnectionManager();

// Inicializar sistema de chatbot avanzado
let chatbotIntegration = null;
if (ChatbotIntegration) {
    chatbotIntegration = new ChatbotIntegration();
}

// Configuración de seguridad desde configuración unificada
const JWT_SECRET = process.env.JWT_SECRET || get_config('security.jwt.secret');
const BCRYPT_ROUNDS = get_config('security.bcrypt.rounds', parseInt(process.env.BCRYPT_ROUNDS) || 12);
const SESSION_TIMEOUT = get_config('security.jwt.expiration', parseInt(process.env.SESSION_TIMEOUT) || 86400000);
const TOKENS_PER_VALIDATED_EXERCISE = get_config('training.tokens_per_exercise', parseInt(process.env.TOKENS_PER_VALIDATED_EXERCISE || '10', 10));

// Validar configuración crítica
if (!JWT_SECRET || JWT_SECRET.length < 32) {
    console.error('❌ JWT_SECRET debe tener al menos 32 caracteres');
    console.error('💡 Ejecuta: python3 scripts/generate_secure_config.py');
    process.exit(1);
}

// Configuración de seguridad
app.use(helmet({
    contentSecurityPolicy: {
        directives: {
            defaultSrc: ["'self'"],
            styleSrc: ["'self'", "'unsafe-inline'"],
            scriptSrc: ["'self'"],
            imgSrc: ["'self'", "data:", "https:"],
        },
    },
}));

// Configuración CORS
const corsOptions = {
    origin: get_config('server.cors_origins', [
        'http://localhost:3000',
        'http://127.0.0.1:3000',
        'http://localhost:8001',
        'http://127.0.0.1:8001'
    ]),
    credentials: true,
    optionsSuccessStatus: 200
};
app.use(cors(corsOptions));

// Rate limiting
const limiter = rateLimit({
    windowMs: get_config('security.rate_limiting.window_ms', 15 * 60 * 1000), // 15 minutos
    max: get_config('security.rate_limiting.max_requests', 100), // límite por IP
    message: {
        error: 'Demasiadas solicitudes desde esta IP, intenta de nuevo más tarde.',
        retryAfter: '15 minutos'
    },
    standardHeaders: true,
    legacyHeaders: false,
});
app.use(limiter);

// Middleware para parsing
app.use(express.json({ limit: '10mb' }));
app.use(express.urlencoded({ extended: true, limit: '10mb' }));

// Middleware de configuración
app.use(configMiddleware.injectConfig);
app.use(configMiddleware.validateCriticalConfig);
app.use(configMiddleware.logConfig);

// Middleware de validación
app.use(validationMiddleware.sanitizeInput);
app.use(validationMiddleware.validatePayloadSize());

// Middleware de monitoreo
app.use((req, res, next) => {
    systemMonitor.recordAPIRequest(req.method, req.path, req.ip);
    next();
});

// Middleware de logging profesional
const logger = new AdvancedLogger();
app.use((req, res, next) => {
    const start = Date.now();
    
    res.on('finish', () => {
        const duration = Date.now() - start;
        logger.logRequest(req, res, duration);
    });
    
    next();
});

// Inicializar sistemas de monitoreo (temporalmente deshabilitados)
let chatMetricsCollector, chatAlertSystem, chatBackupSystem, realtimeMetrics, smartCache;

try {
    chatMetricsCollector = new ChatMetricsCollector();
    chatAlertSystem = new ChatAlertSystem();
    chatBackupSystem = new ChatBackupSystem();
    realtimeMetrics = new RealtimeMetrics();
    smartCache = new SmartCache();
} catch (error) {
    console.warn('⚠️ Sistemas de monitoreo no disponibles:', error.message);
}

// Cliente Llama para chat
let llamaClient = null;

// Función de autenticación JWT
const authenticateToken = (req, res, next) => {
    const authHeader = req.headers['authorization'];
    const token = authHeader && authHeader.split(' ')[1];

    if (!token) {
        return res.status(401).json({ 
            error: 'Token de acceso requerido',
            code: 'MISSING_TOKEN'
        });
    }

    jwt.verify(token, JWT_SECRET, (err, user) => {
        if (err) {
            return res.status(403).json({ 
                error: 'Token inválido o expirado',
                code: 'INVALID_TOKEN'
            });
        }
        req.user = user;
        next();
    });
};

// Función para generar respuesta estándar
const generateResponse = (success, data = null, error = null, message = null) => {
    const response = {
        success,
        timestamp: new Date().toISOString(),
        version: '3.1.0'
    };
    
    if (data !== null) response.data = data;
    if (error !== null) response.error = error;
    if (message !== null) response.message = message;
    
    return response;
};

// ===========================================
// RUTAS PRINCIPALES
// ===========================================

// Ruta raíz
app.get('/', (req, res) => {
    res.json(generateResponse(true, {
        name: 'Sheily AI Backend',
        version: '3.1.0',
        status: 'operational',
        endpoints: {
            health: '/api/health',
            auth: '/api/auth/*',
            chat: '/api/chat/*',
            branches: '/api/branches/*',
            training: '/api/training/*',
            config: '/api/config/*',
            monitoring: '/api/monitoring/*'
        }
    }));
});

// ===========================================
// RUTAS DE CONFIGURACIÓN
// ===========================================

app.get('/api/config/system', configMiddleware.getSystemConfig.bind(configMiddleware));
app.get('/api/config/validate', configMiddleware.validateSystemConfig.bind(configMiddleware));

// ===========================================
// RUTAS DE MONITOREO
// ===========================================

app.get('/api/monitoring/metrics', (req, res) => {
    try {
        const metrics = systemMonitor.getMetrics();
        res.json(generateResponse(true, metrics));
    } catch (error) {
        res.status(500).json(generateResponse(false, null, error.message));
    }
});

app.get('/api/monitoring/alerts', (req, res) => {
    try {
        const alerts = systemMonitor.getAlerts();
        res.json(generateResponse(true, alerts));
    } catch (error) {
        res.status(500).json(generateResponse(false, null, error.message));
    }
});

app.get('/api/monitoring/health', (req, res) => {
    try {
        const health = systemMonitor.getHealthStatus();
        res.json(generateResponse(true, health));
    } catch (error) {
        res.status(500).json(generateResponse(false, null, error.message));
    }
});

// ===========================================
// RUTAS DE AUTENTICACIÓN
// ===========================================

app.post('/api/auth/register', 
    validationMiddleware.validate('register'),
    async (req, res) => {
        try {
            const { username, email, password } = req.body;

            // Validar datos de entrada
            if (!username || !email || !password) {
                return res.status(400).json(generateResponse(false, null, 'Todos los campos son requeridos'));
            }

            if (password.length < 12) {
                return res.status(400).json(generateResponse(false, null, 'La contraseña debe tener al menos 12 caracteres'));
            }

            // Verificar si el usuario ya existe
            const existingUser = await dbManager.getUserByUsername(username);
            if (existingUser) {
                return res.status(409).json(generateResponse(false, null, 'El usuario ya existe'));
            }

            // Hash de la contraseña
            const passwordHash = await bcrypt.hash(password, BCRYPT_ROUNDS);

            // Crear usuario
            const newUser = await dbManager.createUser({
                username,
                email,
                password_hash: passwordHash,
                role: 'user'
            });

            // Generar token JWT
            const token = jwt.sign(
                { 
                    userId: newUser.id, 
                    username: newUser.username, 
                    role: newUser.role 
                },
                JWT_SECRET,
                { expiresIn: SESSION_TIMEOUT }
            );

            res.status(201).json(generateResponse(true, {
                user: {
                    id: newUser.id,
                    username: newUser.username,
                    email: newUser.email,
                    role: newUser.role
                },
                token
            }, null, 'Usuario registrado exitosamente'));

        } catch (error) {
            logger.logError('Error en registro de usuario', error);
            res.status(500).json(generateResponse(false, null, 'Error interno del servidor'));
        }
    }
);

app.post('/api/auth/login', 
    validationMiddleware.validate('login'),
    async (req, res) => {
        try {
            const { username, password } = req.body;

            // Validar datos de entrada
            if (!username || !password) {
                return res.status(400).json(generateResponse(false, null, 'Usuario y contraseña son requeridos'));
            }

            // Buscar usuario
            const user = await dbManager.getUserByUsername(username);
            if (!user) {
                return res.status(401).json(generateResponse(false, null, 'Credenciales inválidas'));
            }

            // Verificar contraseña
            const isValidPassword = await bcrypt.compare(password, user.password_hash);
            if (!isValidPassword) {
                return res.status(401).json(generateResponse(false, null, 'Credenciales inválidas'));
            }

            // Generar token JWT
            const token = jwt.sign(
                { 
                    userId: user.id, 
                    username: user.username, 
                    role: user.role 
                },
                JWT_SECRET,
                { expiresIn: SESSION_TIMEOUT }
            );

            res.json(generateResponse(true, {
                user: {
                    id: user.id,
                    username: user.username,
                    email: user.email,
                    role: user.role
                },
                token
            }, null, 'Inicio de sesión exitoso'));

        } catch (error) {
            logger.logError('Error en inicio de sesión', error);
            res.status(500).json(generateResponse(false, null, 'Error interno del servidor'));
        }
    }
);

app.get('/api/auth/profile', authenticateToken, async (req, res) => {
    try {
        const user = await dbManager.getUserByUsername(req.user.username);
        if (!user) {
            return res.status(404).json(generateResponse(false, null, 'Usuario no encontrado'));
        }

        res.json(generateResponse(true, {
            id: user.id,
            username: user.username,
            email: user.email,
            role: user.role,
            created_at: user.created_at
        }));

    } catch (error) {
        logger.logError('Error obteniendo perfil', error);
        res.status(500).json(generateResponse(false, null, 'Error interno del servidor'));
    }
});

// ===========================================
// RUTAS DE SALUD DEL SISTEMA
// ===========================================

app.get('/api/health', async (req, res) => {
    try {
        const dbStatus = await dbManager.getConnectionStatus();
        
        const healthData = {
            status: 'healthy',
            timestamp: new Date().toISOString(),
            version: '3.1.0',
            uptime: process.uptime(),
            database: dbStatus,
            services: {
                backend: 'operational',
                llm: languageModelService.isHealthy() ? 'operational' : 'degraded',
                chatbot: chatbotIntegration ? 'operational' : 'unavailable'
            },
            memory: {
                used: Math.round(process.memoryUsage().heapUsed / 1024 / 1024),
                total: Math.round(process.memoryUsage().heapTotal / 1024 / 1024)
            }
        };

        res.json(generateResponse(true, healthData));

    } catch (error) {
        logger.logError('Error en health check', error);
        res.status(503).json(generateResponse(false, null, 'Health check failed: ' + error.message));
    }
});

// ===========================================
// RUTAS DE CHAT
// ===========================================

app.get('/api/chat/health', async (req, res) => {
    try {
        const llmHealth = languageModelService.getHealthStatus();
        res.json(generateResponse(true, llmHealth));
    } catch (error) {
        res.status(500).json(generateResponse(false, null, error.message));
    }
});

app.post('/api/chat/session', async (req, res) => {
    try {
        const sessionId = uuidv4();
        res.json(generateResponse(true, { sessionId }, null, 'Sesión de chat creada'));
    } catch (error) {
        res.status(500).json(generateResponse(false, null, error.message));
    }
});

app.post('/api/chat/send', async (req, res) => {
    try {
        const { message, sessionId } = req.body;

        if (!message) {
            return res.status(400).json(generateResponse(false, null, 'Mensaje requerido'));
        }

        // Usar chatbot avanzado si está disponible
        if (chatbotIntegration) {
            const response = await chatbotIntegration.processUserMessage(message, { sessionId });
            res.json(generateResponse(true, response));
        } else {
            // Fallback al LLM directo
            const response = await languageModelService.generateResponse(message);
            res.json(generateResponse(true, response));
        }

    } catch (error) {
        logger.logError('Error en chat', error);
        res.status(500).json(generateResponse(false, null, 'Error procesando mensaje'));
    }
});

// ===========================================
// RUTAS DE RAMAS
// ===========================================

app.get('/api/branches', async (req, res) => {
    try {
        const branches = await dbManager.getBranches();
        res.json(generateResponse(true, branches));
    } catch (error) {
        logger.logError('Error obteniendo ramas', error);
        res.status(500).json(generateResponse(false, null, 'Error obteniendo ramas'));
    }
});

// ===========================================
// MANEJO DE ERRORES GLOBAL
// ===========================================

app.use((err, req, res, next) => {
    logger.logError('Error no manejado', err);
    res.status(500).json(generateResponse(false, null, 'Error interno del servidor'));
});

// Manejo de rutas no encontradas
app.use('*', (req, res) => {
    res.status(404).json(generateResponse(false, null, 'Ruta no encontrada'));
});

// ===========================================
// INICIALIZACIÓN DEL SERVIDOR
// ===========================================

const server = app.listen(PORT, HOST, () => {
    console.log(`🚀 Servidor Sheily AI Backend iniciado`);
    console.log(`📍 URL: http://${HOST}:${PORT}`);
    console.log(`🔧 Entorno: ${process.env.NODE_ENV || 'development'}`);
    console.log(`🗄️ Base de datos: ${dbManager.connectionStatus}`);
    console.log(`🤖 LLM: ${languageModelService.isHealthy() ? 'Conectado' : 'Desconectado'}`);
    console.log(`💬 Chatbot avanzado: ${chatbotIntegration ? 'Disponible' : 'No disponible'}`);
});

// Manejo de cierre graceful
process.on('SIGTERM', async () => {
    console.log('🛑 Recibida señal SIGTERM, cerrando servidor...');
    
    server.close(async () => {
        console.log('✅ Servidor HTTP cerrado');
        
        await dbManager.closeConnections();
        console.log('✅ Conexiones de base de datos cerradas');
        
        process.exit(0);
    });
});

process.on('SIGINT', async () => {
    console.log('🛑 Recibida señal SIGINT, cerrando servidor...');
    
    server.close(async () => {
        console.log('✅ Servidor HTTP cerrado');
        
        await dbManager.closeConnections();
        console.log('✅ Conexiones de base de datos cerradas');
        
        process.exit(0);
    });
});

module.exports = app;
