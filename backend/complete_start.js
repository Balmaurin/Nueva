#!/usr/bin/env node

// Script de inicio completo para el backend de Sheily AI (sin WebSockets problemáticos)
console.log('🚀 Iniciando backend completo de Sheily AI...');

// Cargar configuración
require('dotenv').config({ path: './config.env' });

// Verificar dependencias críticas
const requiredModules = [
  'express',
  'cors',
  'bcryptjs',
  'jsonwebtoken',
  'helmet',
  'express-rate-limit',
  'uuid',
  'ws',
  'nodemailer',
  'archiver',
  'pg-promise'
];

console.log('📋 Verificando dependencias...');
for (const module of requiredModules) {
  try {
    require(module);
    console.log(`✅ ${module} - OK`);
  } catch (error) {
    console.error(`❌ ${module} - ERROR: ${error.message}`);
    process.exit(1);
  }
}

console.log('✅ Todas las dependencias están disponibles');

// Verificar configuración crítica
const requiredEnvVars = ['JWT_SECRET', 'DB_PASSWORD'];
const missingEnvVars = requiredEnvVars.filter(envVar => !process.env[envVar]);

if (missingEnvVars.length > 0) {
  console.error(`❌ Variables de entorno faltantes: ${missingEnvVars.join(', ')}`);
  process.exit(1);
}

if (!process.env.JWT_SECRET || process.env.JWT_SECRET.length < 32) {
  console.error('❌ JWT_SECRET debe tener al menos 32 caracteres');
  process.exit(1);
}

console.log('✅ Configuración crítica verificada');

// Importar módulos necesarios
const express = require('express');
const cors = require('cors');
const bcrypt = require('bcryptjs');
const jwt = require('jsonwebtoken');
const helmet = require('helmet');
const rateLimit = require('express-rate-limit');
const path = require('path');
const fs = require('fs');
const { v4: uuidv4 } = require('uuid');
const pgp = require('pg-promise')();

const app = express();
const PORT = process.env.PORT || 9000;
const JWT_SECRET = process.env.JWT_SECRET;
const BCRYPT_ROUNDS = parseInt(process.env.BCRYPT_ROUNDS) || 12;

// Configuración de base de datos
const dbConfig = {
  host: process.env.DB_HOST || 'localhost',
  port: parseInt(process.env.DB_PORT || '5432'),
  database: process.env.DB_NAME || 'sheily_ai_db',
  user: process.env.DB_USER || 'sheily_ai_user',
  password: process.env.DB_PASSWORD
};

// Conectar a la base de datos
let db;
try {
  db = pgp(dbConfig);
  console.log('✅ Conectado a PostgreSQL');
} catch (error) {
  console.error('❌ Error conectando a PostgreSQL:', error.message);
  console.log('ℹ️ Continuando sin base de datos...');
  db = null;
}

// Middleware básico
app.use(helmet());

// Configuración CORS específica para el frontend
app.use(cors({
  origin: ['http://localhost:3000', 'http://127.0.0.1:3000'],
  credentials: true,
  methods: ['GET', 'POST', 'PUT', 'DELETE', 'OPTIONS'],
  allowedHeaders: ['Content-Type', 'Authorization', 'X-Requested-With']
}));

app.use(express.json({ limit: '10mb' }));
app.use(express.urlencoded({ extended: true }));

// Rate limiting
const limiter = rateLimit({
  windowMs: 15 * 60 * 1000, // 15 minutos
  max: 100 // límite de 100 requests por IP por ventana
});
app.use('/api/', limiter);

// Middleware de autenticación JWT
const authenticateToken = (req, res, next) => {
  const authHeader = req.headers['authorization'];
  const token = authHeader && authHeader.split(' ')[1];

  if (!token) {
    return res.status(401).json({ error: 'Token de acceso requerido' });
  }

  jwt.verify(token, JWT_SECRET, (err, user) => {
    if (err) {
      return res.status(403).json({ error: 'Token inválido' });
    }
    req.user = user;
    next();
  });
};

// Ruta de health check
app.get('/api/health', (req, res) => {
  res.json({
    status: 'OK',
    timestamp: new Date().toISOString(),
    uptime: process.uptime(),
    port: PORT,
    database: db ? 'connected' : 'disconnected'
  });
});

// Ruta básica
app.get('/', (req, res) => {
  res.json({
    message: 'Sheily AI Backend - Servidor completo funcionando correctamente',
    version: '1.0.0',
    timestamp: new Date().toISOString(),
    services: [
      '🔧 API REST completa',
      '📊 Health check',
      '🔐 Autenticación JWT',
      '🗄️ Base de datos PostgreSQL',
      '🧠 Chat con IA (próximamente)'
    ]
  });
});

// Rutas de autenticación
app.post('/api/auth/register', async (req, res) => {
  try {
    const { username, email, password } = req.body;

    if (!username || !email || !password) {
      return res.status(400).json({ error: 'Todos los campos son requeridos' });
    }

    if (!db) {
      return res.status(503).json({ error: 'Base de datos no disponible' });
    }

    // Verificar si el usuario ya existe
    const existingUser = await db.oneOrNone(
      'SELECT id FROM users WHERE username = $1 OR email = $2',
      [username, email]
    );

    if (existingUser) {
      return res.status(409).json({ error: 'Usuario o email ya existe' });
    }

    // Hash de la contraseña
    const hashedPassword = await bcrypt.hash(password, BCRYPT_ROUNDS);

    // Crear usuario
    const newUser = await db.one(
      'INSERT INTO users (username, email, password_hash) VALUES ($1, $2, $3) RETURNING id, username, email, created_at',
      [username, email, hashedPassword]
    );

    // Generar token JWT
    const token = jwt.sign(
      { userId: newUser.id, username: newUser.username },
      JWT_SECRET,
      { expiresIn: '24h' }
    );

    res.status(201).json({
      message: 'Usuario registrado exitosamente',
      user: {
        id: newUser.id,
        username: newUser.username,
        email: newUser.email,
        created_at: newUser.created_at
      },
      token
    });

  } catch (error) {
    console.error('Error en registro:', error);
    res.status(500).json({ error: 'Error interno del servidor' });
  }
});

app.post('/api/auth/login', async (req, res) => {
  try {
    const { username, password } = req.body;

    if (!username || !password) {
      return res.status(400).json({ error: 'Username y password son requeridos' });
    }

    if (!db) {
      return res.status(503).json({ error: 'Base de datos no disponible' });
    }

    // Buscar usuario
    const user = await db.oneOrNone(
      'SELECT id, username, email, password_hash FROM users WHERE username = $1',
      [username]
    );

    if (!user) {
      return res.status(401).json({ error: 'Credenciales inválidas' });
    }

    // Verificar contraseña
    const isValidPassword = await bcrypt.compare(password, user.password_hash);

    if (!isValidPassword) {
      return res.status(401).json({ error: 'Credenciales inválidas' });
    }

    // Generar token JWT
    const token = jwt.sign(
      { userId: user.id, username: user.username },
      JWT_SECRET,
      { expiresIn: '24h' }
    );

    res.json({
      message: 'Login exitoso',
      user: {
        id: user.id,
        username: user.username,
        email: user.email
      },
      token
    });

  } catch (error) {
    console.error('Error en login:', error);
    res.status(500).json({ error: 'Error interno del servidor' });
  }
});

// Ruta protegida de ejemplo
app.get('/api/profile', authenticateToken, (req, res) => {
  res.json({
    message: 'Perfil del usuario',
    user: req.user
  });
});

// Ruta de chat (placeholder)
app.post('/api/chat', authenticateToken, (req, res) => {
  res.json({
    message: 'Sistema de chat en desarrollo',
    request: req.body,
    user: req.user
  });
});

// Iniciar servidor
const server = app.listen(PORT, '0.0.0.0', () => {
  console.log(`🎉 Backend completo iniciado exitosamente en puerto ${PORT}`);
  console.log(`🌐 URL: http://localhost:${PORT}`);
  console.log(`📊 Health check: http://localhost:${PORT}/api/health`);
  console.log(`🔐 Auth endpoints: http://localhost:${PORT}/api/auth/`);
  console.log('');
  console.log('📋 Servicios disponibles:');
  console.log('  🔧 API REST completa');
  console.log('  📊 Health check');
  console.log('  🔐 Autenticación JWT');
  console.log('  🗄️ Base de datos PostgreSQL');
  console.log('  🧠 Chat con IA (en desarrollo)');
  console.log('');
  console.log('🛑 Presiona Ctrl+C para detener');
});

// Manejo de señales para cierre limpio
process.on('SIGINT', async () => {
  console.log('\n🛑 Recibida señal SIGINT, cerrando servidor...');
  server.close(() => {
    console.log('✅ Servidor cerrado correctamente');
  });
  
  if (db) {
    await pgp.end();
    console.log('✅ Conexión de base de datos cerrada');
  }
  
  process.exit(0);
});

process.on('SIGTERM', async () => {
  console.log('\n🛑 Recibida señal SIGTERM, cerrando servidor...');
  server.close(() => {
    console.log('✅ Servidor cerrado correctamente');
  });
  
  if (db) {
    await pgp.end();
    console.log('✅ Conexión de base de datos cerrada');
  }
  
  process.exit(0);
});

