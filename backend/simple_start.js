#!/usr/bin/env node

// Script de inicio simple para el backend de Sheily AI
console.log('🚀 Iniciando backend de Sheily AI (modo simple)...');

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
  'uuid'
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

// Crear servidor Express simple
const express = require('express');
const cors = require('cors');
const helmet = require('helmet');
const rateLimit = require('express-rate-limit');

const app = express();
const PORT = process.env.PORT || 3001;

// Middleware básico
app.use(helmet());
app.use(cors());
app.use(express.json({ limit: '10mb' }));
app.use(express.urlencoded({ extended: true }));

// Rate limiting
const limiter = rateLimit({
  windowMs: 15 * 60 * 1000, // 15 minutos
  max: 100 // límite de 100 requests por IP por ventana
});
app.use('/api/', limiter);

// Ruta de health check
app.get('/api/health', (req, res) => {
  res.json({
    status: 'OK',
    timestamp: new Date().toISOString(),
    uptime: process.uptime(),
    port: PORT
  });
});

// Ruta básica
app.get('/', (req, res) => {
  res.json({
    message: 'Sheily AI Backend - Servidor funcionando correctamente',
    version: '1.0.0',
    timestamp: new Date().toISOString()
  });
});

// Iniciar servidor
const server = app.listen(PORT, '0.0.0.0', () => {
  console.log(`🎉 Backend iniciado exitosamente en puerto ${PORT}`);
  console.log(`🌐 URL: http://localhost:${PORT}`);
  console.log(`📊 Health check: http://localhost:${PORT}/api/health`);
  console.log('');
  console.log('📋 Servicios disponibles:');
  console.log('  🔧 API REST básica');
  console.log('  📊 Health check');
  console.log('');
  console.log('🛑 Presiona Ctrl+C para detener');
});

// Manejo de señales para cierre limpio
process.on('SIGINT', () => {
  console.log('\n🛑 Recibida señal SIGINT, cerrando servidor...');
  server.close(() => {
    console.log('✅ Servidor cerrado correctamente');
    process.exit(0);
  });
});

process.on('SIGTERM', () => {
  console.log('\n🛑 Recibida señal SIGTERM, cerrando servidor...');
  server.close(() => {
    console.log('✅ Servidor cerrado correctamente');
    process.exit(0);
  });
});

