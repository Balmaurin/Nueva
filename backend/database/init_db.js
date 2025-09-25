const { Client } = require('pg');
const fs = require('fs');
const path = require('path');

async function initializeDatabase() {
  const client = new Client({
    host: process.env.DB_HOST || 'localhost',
    port: process.env.DB_PORT || 5432,
    database: process.env.DB_NAME || 'sheily_ai_db',
    user: process.env.DB_USER || 'sheily_ai_user',
    password: process.env.DB_PASSWORD || 'SheilyAI2025SecurePassword!',
    ssl: process.env.NODE_ENV === 'production' ? { rejectUnauthorized: false } : false
  });

  try {
    await client.connect();
    console.log('✅ Conectado a la base de datos PostgreSQL');

    const initSqlPath = path.join(__dirname, 'init.sql');
    const initSql = fs.readFileSync(initSqlPath, 'utf8');

    // Ejecutar script de inicialización
    await client.query(initSql);
    console.log('✅ Tablas y funciones de base de datos inicializadas correctamente');

    // Verificar que las tablas se crearon correctamente
    const tablesQuery = `
      SELECT table_name 
      FROM information_schema.tables 
      WHERE table_schema = 'public' 
      ORDER BY table_name;
    `;
    
    const tables = await client.query(tablesQuery);
    console.log('📋 Tablas creadas:', tables.rows.map(row => row.table_name).join(', '));

    // Verificar que las funciones se crearon correctamente
    const functionsQuery = `
      SELECT routine_name 
      FROM information_schema.routines 
      WHERE routine_schema = 'public' 
      AND routine_type = 'FUNCTION'
      ORDER BY routine_name;
    `;
    
    const functions = await client.query(functionsQuery);
    console.log('🔧 Funciones creadas:', functions.rows.map(row => row.routine_name).join(', '));

    console.log('🎉 Base de datos inicializada exitosamente');

  } catch (error) {
    console.error('❌ Error al inicializar la base de datos:', error);
    throw error;
  } finally {
    await client.end();
  }
}

// Ejecutar si se llama directamente
if (require.main === module) {
  initializeDatabase()
    .then(() => {
      console.log('✅ Script de inicialización completado');
      process.exit(0);
    })
    .catch((error) => {
      console.error('❌ Error en script de inicialización:', error);
      process.exit(1);
    });
}

module.exports = { initializeDatabase };
