-- Script para configurar la base de datos de Sheily AI

-- Crear usuario si no existe
DO $$
BEGIN
    IF NOT EXISTS (SELECT FROM pg_catalog.pg_roles WHERE rolname = 'sheily_ai_user') THEN
        CREATE USER sheily_ai_user WITH PASSWORD 'SheilyAI2025SecurePassword!';
    END IF;
END
$$;

-- Crear base de datos si no existe
SELECT 'CREATE DATABASE sheily_ai_db OWNER sheily_ai_user'
WHERE NOT EXISTS (SELECT FROM pg_database WHERE datname = 'sheily_ai_db')\gexec

-- Conceder privilegios al usuario
GRANT ALL PRIVILEGES ON DATABASE sheily_ai_db TO sheily_ai_user;

-- Conectar a la base de datos y crear tablas
\c sheily_ai_db;

-- Crear tabla de usuarios
CREATE TABLE IF NOT EXISTS users (
    id SERIAL PRIMARY KEY,
    username VARCHAR(50) UNIQUE NOT NULL,
    email VARCHAR(100) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Crear tabla de sesiones
CREATE TABLE IF NOT EXISTS user_sessions (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
    token_hash VARCHAR(255) NOT NULL,
    expires_at TIMESTAMP NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Crear tabla de conversaciones
CREATE TABLE IF NOT EXISTS conversations (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
    title VARCHAR(255),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Crear tabla de mensajes
CREATE TABLE IF NOT EXISTS messages (
    id SERIAL PRIMARY KEY,
    conversation_id INTEGER REFERENCES conversations(id) ON DELETE CASCADE,
    role VARCHAR(20) NOT NULL, -- 'user' o 'assistant'
    content TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Conceder privilegios en las tablas
GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO sheily_ai_user;
GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA public TO sheily_ai_user;

-- Crear índices para mejorar el rendimiento
CREATE INDEX IF NOT EXISTS idx_users_username ON users(username);
CREATE INDEX IF NOT EXISTS idx_users_email ON users(email);
CREATE INDEX IF NOT EXISTS idx_sessions_user_id ON user_sessions(user_id);
CREATE INDEX IF NOT EXISTS idx_sessions_token_hash ON user_sessions(token_hash);
CREATE INDEX IF NOT EXISTS idx_conversations_user_id ON conversations(user_id);
CREATE INDEX IF NOT EXISTS idx_messages_conversation_id ON messages(conversation_id);

-- Insertar usuario de prueba
INSERT INTO users (username, email, password_hash) 
VALUES ('admin', 'admin@sheily.ai', '$2a$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewdBPj4J/8KzKz2K')
ON CONFLICT (username) DO NOTHING;

-- Mostrar información de la configuración
SELECT 'Base de datos configurada correctamente' as status;
SELECT 'Usuario: sheily_ai_user' as user_info;
SELECT 'Base de datos: sheily_ai_db' as database_info;
