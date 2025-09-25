#!/usr/bin/env node

// Script de inicio para el backend de Sheily AI
console.log('🚀 Iniciando backend de Sheily AI...');

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

// Importar y configurar el servidor
try {
  const app = require('./server.js');
  
  const PORT = process.env.PORT || 8000;
  const WEBSOCKET_PORT = process.env.WEBSOCKET_PORT || 8002;
  
  // Iniciar servidor
  const server = app.listen(PORT, '0.0.0.0', () => {
    console.log(`🎉 Backend iniciado exitosamente en puerto ${PORT}`);
    console.log(`🌐 URL: http://localhost:${PORT}`);
    console.log(`📊 Health check: http://localhost:${PORT}/api/health`);
    console.log(`🔌 WebSocket: puerto ${WEBSOCKET_PORT}`);
    console.log('');
    console.log('📋 Servicios disponibles:');
    console.log('  🔧 API REST');
    console.log('  🧠 Chat con IA (4-bit y 16-bit)');
    console.log('  👤 Autenticación JWT segura');
    console.log('  📊 Monitoreo en tiempo real');
    console.log('  💾 Backup automático');
    console.log('  🚨 Sistema de alertas');
    console.log('  🗄️ Base de datos PostgreSQL');
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
  
} catch (error) {
  console.error('❌ Error iniciando el servidor:', error);
  process.exit(1);
}
