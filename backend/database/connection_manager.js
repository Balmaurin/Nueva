/**
 * Gestor Profesional de Conexiones de Base de Datos
 * ================================================
 * Sistema robusto de conexión con fallback automático y monitoreo
 */

const { Pool } = require('pg');
const sqlite3 = require('sqlite3').verbose();
const path = require('path');
const fs = require('fs');

class DatabaseConnectionManager {
    constructor() {
        this.primaryDB = null;
        this.fallbackDB = null;
        this.connectionStatus = 'unknown';
        this.retryCount = 0;
        this.maxRetries = 3;
        this.retryDelay = 2000;
        
        this.initializeConnections();
    }

    async initializeConnections() {
        console.log('🔌 Inicializando gestor de conexiones de base de datos...');
        
        // Intentar conectar a PostgreSQL primero
        await this.initializePostgreSQL();
        
        // Si PostgreSQL falla, inicializar SQLite como fallback
        if (this.connectionStatus !== 'connected') {
            await this.initializeSQLite();
        }
        
        console.log(`✅ Estado de conexión: ${this.connectionStatus}`);
    }

    async initializePostgreSQL() {
        try {
            const config = {
                host: process.env.DB_HOST || 'localhost',
                port: process.env.DB_PORT || 5432,
                database: process.env.DB_NAME || 'sheily_ai_db',
                user: process.env.DB_USER || 'sheily_ai_user',
                password: process.env.DB_PASSWORD || 'aLntLq1vjQ^*t#H0Lxfwz5!B',
                max: 20,
                idleTimeoutMillis: 30000,
                connectionTimeoutMillis: 10000,
                ssl: process.env.DB_SSL === 'true' ? { rejectUnauthorized: false } : false
            };

            this.primaryDB = new Pool(config);
            
            // Probar conexión
            const client = await this.primaryDB.connect();
            await client.query('SELECT 1');
            client.release();
            
            this.connectionStatus = 'connected';
            console.log('✅ PostgreSQL conectado exitosamente');
            
        } catch (error) {
            console.warn('⚠️ Error conectando a PostgreSQL:', error.message);
            this.connectionStatus = 'postgres_failed';
            
            if (this.primaryDB) {
                await this.primaryDB.end();
                this.primaryDB = null;
            }
        }
    }

    async initializeSQLite() {
        try {
            const dbPath = path.join(__dirname, '../../data/sheily_ai.db');
            
            // Crear directorio si no existe
            const dbDir = path.dirname(dbPath);
            if (!fs.existsSync(dbDir)) {
                fs.mkdirSync(dbDir, { recursive: true });
            }

            this.fallbackDB = new sqlite3.Database(dbPath, (err) => {
                if (err) {
                    console.error('❌ Error inicializando SQLite:', err.message);
                    this.connectionStatus = 'sqlite_failed';
                } else {
                    console.log('✅ SQLite conectado como fallback');
                    this.connectionStatus = 'sqlite_connected';
                }
            });

            // Crear tablas básicas si no existen
            if (this.connectionStatus === 'sqlite_connected') {
                await this.createSQLiteTables();
            }
            
        } catch (error) {
            console.error('❌ Error crítico inicializando SQLite:', error.message);
            this.connectionStatus = 'all_failed';
        }
    }

    async createSQLiteTables() {
        const createTablesSQL = `
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE NOT NULL,
                email TEXT UNIQUE NOT NULL,
                password_hash TEXT NOT NULL,
                role TEXT DEFAULT 'user',
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
            );
            
            CREATE TABLE IF NOT EXISTS branches (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT UNIQUE NOT NULL,
                description TEXT,
                keywords TEXT,
                enabled BOOLEAN DEFAULT 1,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP
            );
            
            CREATE TABLE IF NOT EXISTS branch_exercises (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                branch_id INTEGER,
                type TEXT NOT NULL,
                level INTEGER NOT NULL,
                question TEXT NOT NULL,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (branch_id) REFERENCES branches (id)
            );
            
            CREATE TABLE IF NOT EXISTS user_branch_progress (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER,
                branch_id INTEGER,
                level INTEGER NOT NULL,
                tokens_awarded INTEGER DEFAULT 0,
                verification_status TEXT DEFAULT 'pending',
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users (id),
                FOREIGN KEY (branch_id) REFERENCES branches (id)
            );
        `;

        return new Promise((resolve, reject) => {
            this.fallbackDB.exec(createTablesSQL, (err) => {
                if (err) {
                    console.error('❌ Error creando tablas SQLite:', err.message);
                    reject(err);
                } else {
                    console.log('✅ Tablas SQLite creadas/verificadas');
                    resolve();
                }
            });
        });
    }

    async query(sql, params = []) {
        if (this.connectionStatus === 'connected' && this.primaryDB) {
            return this.queryPostgreSQL(sql, params);
        } else if (this.connectionStatus === 'sqlite_connected' && this.fallbackDB) {
            return this.querySQLite(sql, params);
        } else {
            throw new Error('No hay conexión de base de datos disponible');
        }
    }

    async queryPostgreSQL(sql, params) {
        try {
            const client = await this.primaryDB.connect();
            try {
                const result = await client.query(sql, params);
                return result.rows;
            } finally {
                client.release();
            }
        } catch (error) {
            console.error('❌ Error en consulta PostgreSQL:', error.message);
            
            // Intentar reconectar
            if (this.retryCount < this.maxRetries) {
                this.retryCount++;
                console.log(`🔄 Reintentando conexión PostgreSQL (${this.retryCount}/${this.maxRetries})...`);
                
                await new Promise(resolve => setTimeout(resolve, this.retryDelay));
                await this.initializePostgreSQL();
                
                if (this.connectionStatus === 'connected') {
                    return this.queryPostgreSQL(sql, params);
                }
            }
            
            throw error;
        }
    }

    async querySQLite(sql, params) {
        return new Promise((resolve, reject) => {
            // Convertir SQL de PostgreSQL a SQLite
            const sqliteSQL = this.convertPostgreSQLToSQLite(sql);
            
            this.fallbackDB.all(sqliteSQL, params, (err, rows) => {
                if (err) {
                    console.error('❌ Error en consulta SQLite:', err.message);
                    reject(err);
                } else {
                    resolve(rows || []);
                }
            });
        });
    }

    convertPostgreSQLToSQLite(sql) {
        // Conversiones básicas de PostgreSQL a SQLite
        return sql
            .replace(/SERIAL PRIMARY KEY/g, 'INTEGER PRIMARY KEY AUTOINCREMENT')
            .replace(/TIMESTAMP DEFAULT CURRENT_TIMESTAMP/g, 'DATETIME DEFAULT CURRENT_TIMESTAMP')
            .replace(/BOOLEAN DEFAULT TRUE/g, 'BOOLEAN DEFAULT 1')
            .replace(/BOOLEAN DEFAULT FALSE/g, 'BOOLEAN DEFAULT 0')
            .replace(/ON CONFLICT \(([^)]+)\) DO NOTHING/g, 'OR IGNORE')
            .replace(/INSERT INTO/g, 'INSERT OR IGNORE INTO');
    }

    async getConnectionStatus() {
        return {
            status: this.connectionStatus,
            primary: this.primaryDB ? 'available' : 'unavailable',
            fallback: this.fallbackDB ? 'available' : 'unavailable',
            retryCount: this.retryCount
        };
    }

    async closeConnections() {
        console.log('🔌 Cerrando conexiones de base de datos...');
        
        if (this.primaryDB) {
            await this.primaryDB.end();
            this.primaryDB = null;
        }
        
        if (this.fallbackDB) {
            this.fallbackDB.close();
            this.fallbackDB = null;
        }
        
        console.log('✅ Conexiones cerradas');
    }

    // Métodos de utilidad específicos
    async getBranches() {
        return this.query('SELECT * FROM branches ORDER BY name');
    }

    async getUserByUsername(username) {
        const result = await this.query('SELECT * FROM users WHERE username = $1', [username]);
        return result[0] || null;
    }

    async createUser(userData) {
        const { username, email, password_hash, role = 'user' } = userData;
        const result = await this.query(
            'INSERT INTO users (username, email, password_hash, role) VALUES ($1, $2, $3, $4) RETURNING *',
            [username, email, password_hash, role]
        );
        return result[0];
    }

    async updateUserProgress(userId, branchId, level, tokens) {
        return this.query(
            'INSERT INTO user_branch_progress (user_id, branch_id, level, tokens_awarded) VALUES ($1, $2, $3, $4) ON CONFLICT (user_id, branch_id) DO UPDATE SET level = $3, tokens_awarded = $4, updated_at = CURRENT_TIMESTAMP',
            [userId, branchId, level, tokens]
        );
    }
}

module.exports = DatabaseConnectionManager;
