#!/usr/bin/env python3
"""
Gestor Completo de Base de Datos - Sheily AI
===========================================
Sistema híbrido que soporta PostgreSQL y SQLite con failover automático
"""

import os
import logging
import sqlite3
import json
from pathlib import Path
from typing import Dict, Any, Optional, List, Union
from datetime import datetime
import hashlib
import secrets

logger = logging.getLogger(__name__)

class HybridDatabaseManager:
    """Gestor híbrido de base de datos con soporte PostgreSQL y SQLite"""

    def __init__(self, config_path: str = None):
        self.config_path = config_path or "config/unified_config.json"
        self.config = self._load_config()
        self.db_type = self._determine_db_type()
        self.connection = None
        self._setup_database()

    def _load_config(self) -> Dict[str, Any]:
        """Cargar configuración desde archivo"""
        try:
            if os.path.exists(self.config_path):
                with open(self.config_path, 'r', encoding='utf-8') as f:
                    return json.load(f).get("database", {})
            else:
                # Configuración por defecto - SOLO POSTGRESQL
                return {
                    "type": "postgres",
                    "postgres_host": "localhost",
                    "postgres_port": 5432,
                    "postgres_name": "sheily_ai_db",
                    "postgres_user": "sheily_ai_user",
                    "postgres_password": "",
                    "pool_size": 5,
                    "timeout": 30000
                }
        except Exception as e:
            logger.error(f"Error cargando configuración: {e}")
            # SOLO POSTGRESQL - NO FALLBACK A SQLITE
            raise RuntimeError("CRÍTICO: No se puede cargar configuración. PostgreSQL es requerido.")

    def _determine_db_type(self) -> str:
        """SOLO POSTGRESQL - SQLite está BLOQUEADO permanentemente"""
        logger.info("🔒 Verificando conexión PostgreSQL (SQLite está bloqueado)")

        try:
            import psycopg2
            # Verificar si PostgreSQL está disponible
            conn = psycopg2.connect(
                host=self.config.get("host", "localhost"),
                port=self.config.get("port", 5432),
                database=self.config.get("name", "sheily_ai_db"),
                user=self.config.get("user", "sheily_ai_user"),
                password=self.config.get("password", ""),
                connect_timeout=5
            )
            conn.close()
            logger.info("✅ PostgreSQL conectado correctamente")
            return "postgres"
        except Exception as e:
            logger.error(f"❌ PostgreSQL no disponible: {e}")
            logger.error("🔒 SQLite está BLOQUEADO permanentemente. PostgreSQL es requerido.")
            raise RuntimeError("CRÍTICO: PostgreSQL es requerido. SQLite está bloqueado permanentemente.")

    def _setup_database(self):
        """Configurar la base de datos - SOLO POSTGRESQL"""
        logger.info("🔒 Configurando PostgreSQL (SQLite bloqueado)")
        self._setup_postgres()

        # Crear tablas si no existen
        self._create_tables()

        # Inicializar datos básicos
        self._initialize_data()

# FUNCIONES SQLITE ELIMINADAS - BLOQUEADAS PERMANENTEMENTE

    def _setup_postgres(self):
        """Configurar PostgreSQL"""
        try:
            import psycopg2
            from psycopg2 import pool

            self.connection = psycopg2.connect(
                host=self.config.get("host", "localhost"),
                port=self.config.get("port", 5432),
                database=self.config.get("name", "sheily_ai_db"),
                user=self.config.get("user", "sheily_ai_user"),
                password=self.config.get("password", ""),
                connect_timeout=30
            )

            # Configurar conexión
            self.connection.autocommit = True
            logger.info("✅ PostgreSQL configurado")

        except Exception as e:
            logger.error(f"❌ Error configurando PostgreSQL: {e}")
            raise

    def _create_tables(self):
        """Crear todas las tablas necesarias"""
        if self.db_type == "sqlite":
            self._create_sqlite_tables()
        else:
            self._create_postgres_tables()

    def _create_sqlite_tables(self):
        """Crear tablas para SQLite"""
        tables_sql = """
        -- Tabla de usuarios
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            email TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            full_name TEXT,
            role TEXT DEFAULT 'user',
            tokens INTEGER DEFAULT 100,
            level INTEGER DEFAULT 1,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            last_login DATETIME,
            is_active BOOLEAN DEFAULT 1,
            email_verified BOOLEAN DEFAULT 0
        );

        -- Tabla de sesiones de chat
        CREATE TABLE IF NOT EXISTS chat_sessions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            session_id TEXT UNIQUE NOT NULL,
            branch_name TEXT NOT NULL,
            status TEXT DEFAULT 'active',
            total_messages INTEGER DEFAULT 0,
            total_tokens INTEGER DEFAULT 0,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            last_activity DATETIME DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users(id)
        );

        -- Tabla de mensajes de chat
        CREATE TABLE IF NOT EXISTS chat_messages (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            session_id TEXT,
            user_id INTEGER,
            message TEXT NOT NULL,
            is_user BOOLEAN NOT NULL,
            tokens_used INTEGER DEFAULT 0,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (session_id) REFERENCES chat_sessions(session_id),
            FOREIGN KEY (user_id) REFERENCES users(id)
        );

        -- Tabla de ramas
        CREATE TABLE IF NOT EXISTS branches (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT UNIQUE NOT NULL,
            description TEXT,
            keywords TEXT, -- JSON string
            enabled BOOLEAN DEFAULT 1,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP
        );

        -- Tabla de ejercicios de ramas
        CREATE TABLE IF NOT EXISTS branch_exercises (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            branch_name TEXT NOT NULL,
            question TEXT NOT NULL,
            answer TEXT NOT NULL,
            difficulty TEXT DEFAULT 'medium',
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP
        );

        -- Tabla de progreso de usuario
        CREATE TABLE IF NOT EXISTS user_progress (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            branch_name TEXT NOT NULL,
            level INTEGER DEFAULT 1,
            score INTEGER DEFAULT 0,
            exercises_completed INTEGER DEFAULT 0,
            tokens_earned INTEGER DEFAULT 0,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users(id)
        );

        -- Tabla de tokens SHEILY
        CREATE TABLE IF NOT EXISTS sheily_tokens (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            amount INTEGER NOT NULL,
            token_type TEXT DEFAULT 'training',
            reason TEXT,
            blockchain_tx TEXT,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users(id)
        );

        -- Índices para rendimiento
        CREATE INDEX IF NOT EXISTS idx_users_username ON users(username);
        CREATE INDEX IF NOT EXISTS idx_users_email ON users(email);
        CREATE INDEX IF NOT EXISTS idx_chat_sessions_user ON chat_sessions(user_id);
        CREATE INDEX IF NOT EXISTS idx_chat_messages_session ON chat_messages(session_id);
        CREATE INDEX IF NOT EXISTS idx_user_progress_user ON user_progress(user_id);
        """

        try:
            self.connection.executescript(tables_sql)
            self.connection.commit()
            logger.info("✅ Tablas SQLite creadas exitosamente")
        except Exception as e:
            logger.error(f"❌ Error creando tablas SQLite: {e}")
            raise

    def _create_postgres_tables(self):
        """Crear tablas para PostgreSQL usando el esquema existente"""
        # Usar el archivo init.sql existente
        init_sql_path = Path(__file__).parent / "init.sql"
        if init_sql_path.exists():
            try:
                with open(init_sql_path, 'r', encoding='utf-8') as f:
                    sql_content = f.read()

                # Ejecutar el SQL
                cursor = self.connection.cursor()
                cursor.execute(sql_content)
                self.connection.commit()
                cursor.close()
                logger.info("✅ Tablas PostgreSQL creadas exitosamente")
            except Exception as e:
                logger.error(f"❌ Error creando tablas PostgreSQL: {e}")
                raise
        else:
            logger.warning("Archivo init.sql no encontrado, usando esquema básico")
            self._create_basic_postgres_tables()

    def _create_basic_postgres_tables(self):
        """Crear esquema básico de PostgreSQL"""
        tables_sql = """
        CREATE TABLE IF NOT EXISTS users (
            id SERIAL PRIMARY KEY,
            username VARCHAR(50) UNIQUE NOT NULL,
            email VARCHAR(100) UNIQUE NOT NULL,
            password_hash VARCHAR(255) NOT NULL,
            full_name VARCHAR(100),
            role VARCHAR(20) DEFAULT 'user',
            tokens INTEGER DEFAULT 100,
            level INTEGER DEFAULT 1,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            last_login TIMESTAMP,
            is_active BOOLEAN DEFAULT TRUE,
            email_verified BOOLEAN DEFAULT FALSE
        );

        CREATE TABLE IF NOT EXISTS chat_sessions (
            id SERIAL PRIMARY KEY,
            user_id INTEGER REFERENCES users(id),
            session_id VARCHAR(255) UNIQUE NOT NULL,
            branch_name VARCHAR(100) NOT NULL,
            status VARCHAR(20) DEFAULT 'active',
            total_messages INTEGER DEFAULT 0,
            total_tokens INTEGER DEFAULT 0,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            last_activity TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );

        CREATE TABLE IF NOT EXISTS branches (
            id SERIAL PRIMARY KEY,
            name VARCHAR(255) UNIQUE NOT NULL,
            description TEXT,
            keywords TEXT[],
            enabled BOOLEAN DEFAULT TRUE,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        """

        try:
            cursor = self.connection.cursor()
            cursor.execute(tables_sql)
            self.connection.commit()
            cursor.close()
            logger.info("✅ Tablas básicas PostgreSQL creadas")
        except Exception as e:
            logger.error(f"❌ Error creando tablas básicas PostgreSQL: {e}")
            raise

    def _initialize_data(self):
        """Inicializar datos básicos"""
        try:
            # Inicializar ramas si no existen
            self._initialize_branches()
            logger.info("✅ Datos iniciales cargados")
        except Exception as e:
            logger.error(f"❌ Error inicializando datos: {e}")

    def _initialize_branches(self):
        """Inicializar las 35 ramas especializadas"""
        branches = [
            ("lengua_y_lingüística", "Rama especializada en lengua y lingüística", ["gramática", "sintaxis", "semántica"]),
            ("matemáticas", "Rama especializada en matemáticas", ["álgebra", "cálculo", "geometría"]),
            ("computación_y_programación", "Rama especializada en computación y programación", ["algoritmos", "desarrollo", "software"]),
            ("medicina_y_salud", "Rama especializada en medicina y salud", ["diagnóstico", "tratamientos", "anatomía"]),
            ("física", "Rama especializada en física", ["mecánica", "electromagnetismo", "cuántica"]),
            ("química", "Rama especializada en química", ["reacciones", "compuestos", "laboratorio"]),
            ("biología", "Rama especializada en biología", ["celular", "genética", "ecología"]),
            ("historia", "Rama especializada en historia", ["civilizaciones", "eventos", "cronología"]),
            ("geografía_y_geo_política", "Rama especializada en geografía y geo-política", ["mapas", "países", "geopolítica"]),
            ("economía_y_finanzas", "Rama especializada en economía y finanzas", ["mercado", "inversión", "presupuesto"]),
            ("derecho_y_políticas_públicas", "Rama especializada en derecho y políticas públicas", ["leyes", "justicia", "políticas"]),
            ("educación_y_pedagogía", "Rama especializada en educación y pedagogía", ["enseñanza", "aprendizaje", "didáctica"]),
            ("ingeniería", "Rama especializada en ingeniería", ["diseño", "construcción", "tecnología"]),
            ("empresa_y_emprendimiento", "Rama especializada en empresa y emprendimiento", ["negocios", "gestión", "liderazgo"]),
            ("arte_música_y_cultura", "Rama especializada en arte, música y cultura", ["creatividad", "expresión", "cultura"]),
            ("literatura_y_escritura", "Rama especializada en literatura y escritura", ["novelas", "poesía", "redacción"]),
            ("medios_y_comunicación", "Rama especializada en medios y comunicación", ["periodismo", "audiovisual", "marketing"]),
            ("deportes_y_esports", "Rama especializada en deportes y esports", ["atletismo", "competición", "gaming"]),
            ("juegos_y_entretenimiento", "Rama especializada en juegos y entretenimiento", ["videojuegos", "diversión", "gaming"]),
            ("cocina_y_nutrición", "Rama especializada en cocina y nutrición", ["recetas", "alimentación", "gastronomía"]),
            ("hogar_diy_y_reparaciones", "Rama especializada en hogar, DIY y reparaciones", ["bricolaje", "mantenimiento", "construcción"]),
            ("viajes_e_idiomas", "Rama especializada en viajes e idiomas", ["turismo", "culturas", "idiomas"]),
            ("vida_diaria_legal_práctico_y_trámites", "Rama especializada en vida diaria legal y trámites", ["práctico", "administrativo", "legal"]),
            ("sociología_y_antropología", "Rama especializada en sociología y antropología", ["sociedad", "cultura", "comportamiento"]),
            ("neurociencia_y_psicología", "Rama especializada en neurociencia y psicología", ["mente", "comportamiento", "cerebro"]),
            ("astronomía_y_espacio", "Rama especializada en astronomía y espacio", ["estrellas", "galaxias", "cosmos"]),
            ("ciencias_de_la_tierra_y_clima", "Rama especializada en ciencias de la tierra y clima", ["geología", "clima", "medio ambiente"]),
            ("ciencia_de_datos_e_ia", "Rama especializada en ciencia de datos e IA", ["datos", "machine learning", "estadística"]),
            ("ciberseguridad_y_criptografía", "Rama especializada en ciberseguridad y criptografía", ["seguridad", "privacidad", "criptografía"]),
            ("electrónica_y_iot", "Rama especializada en electrónica y IoT", ["dispositivos", "sensores", "conectividad"]),
            ("sistemas_devops_redes", "Rama especializada en sistemas, DevOps y redes", ["infraestructura", "automatización", "redes"]),
            ("diseño_y_ux", "Rama especializada en diseño y UX", ["ui", "ux", "experiencia", "interfaz"]),
            ("general", "Rama general para conversaciones cotidianas", ["general", "conversación", "básico"]),
            ("maestros_de_los_números", "Rama especializada en matemáticas avanzadas", ["matemáticas puras", "estadística avanzada"]),
            ("sanadores_del_cuerpo_y_alma", "Rama especializada en medicina holística", ["salud holística", "bienestar", "medicina alternativa"])
        ]

        for name, description, keywords in branches:
            try:
                if self.db_type == "sqlite":
                    keywords_json = json.dumps(keywords)
                    self.connection.execute("""
                        INSERT OR IGNORE INTO branches (name, description, keywords, enabled)
                        VALUES (?, ?, ?, 1)
                    """, (name, description, keywords_json))
                else:
                    self.connection.execute("""
                        INSERT INTO branches (name, description, keywords, enabled)
                        VALUES (%s, %s, %s, %s)
                        ON CONFLICT (name) DO NOTHING
                    """, (name, description, keywords, True))

            except Exception as e:
                logger.warning(f"Error insertando rama {name}: {e}")

        if self.db_type == "sqlite":
            self.connection.commit()

        logger.info(f"✅ {len(branches)} ramas inicializadas")

    # Métodos públicos para operaciones CRUD

    def create_user(self, username: str, email: str, password_hash: str, **kwargs) -> int:
        """Crear un nuevo usuario"""
        try:
            if self.db_type == "sqlite":
                cursor = self.connection.execute("""
                    INSERT INTO users (username, email, password_hash, full_name, role)
                    VALUES (?, ?, ?, ?, ?)
                """, (username, email, password_hash,
                      kwargs.get('full_name'), kwargs.get('role', 'user')))
                user_id = cursor.lastrowid
                self.connection.commit()
            else:
                cursor = self.connection.cursor()
                cursor.execute("""
                    INSERT INTO users (username, email, password_hash, full_name, role)
                    VALUES (%s, %s, %s, %s, %s) RETURNING id
                """, (username, email, password_hash,
                      kwargs.get('full_name'), kwargs.get('role', 'user')))
                user_id = cursor.fetchone()[0]
                self.connection.commit()
                cursor.close()

            logger.info(f"✅ Usuario creado: {username} (ID: {user_id})")
            return user_id

        except Exception as e:
            logger.error(f"❌ Error creando usuario: {e}")
            raise

    def get_user(self, user_id: int = None, username: str = None, email: str = None) -> Optional[Dict[str, Any]]:
        """Obtener información de usuario"""
        try:
            if self.db_type == "sqlite":
                if user_id:
                    cursor = self.connection.execute("SELECT * FROM users WHERE id = ?", (user_id,))
                elif username:
                    cursor = self.connection.execute("SELECT * FROM users WHERE username = ?", (username,))
                elif email:
                    cursor = self.connection.execute("SELECT * FROM users WHERE email = ?", (email,))
                else:
                    return None

                row = cursor.fetchone()
                if row:
                    columns = [desc[0] for desc in cursor.description]
                    return dict(zip(columns, row))
            else:
                cursor = self.connection.cursor()
                if user_id:
                    cursor.execute("SELECT * FROM users WHERE id = %s", (user_id,))
                elif username:
                    cursor.execute("SELECT * FROM users WHERE username = %s", (username,))
                elif email:
                    cursor.execute("SELECT * FROM users WHERE email = %s", (email,))
                else:
                    cursor.close()
                    return None

                row = cursor.fetchone()
                if row:
                    columns = [desc[0] for desc in cursor.description]
                    result = dict(zip(columns, row))
                    cursor.close()
                    return result
                cursor.close()

        except Exception as e:
            logger.error(f"❌ Error obteniendo usuario: {e}")

        return None

    def create_chat_session(self, user_id: int, branch_name: str, session_id: str = None) -> str:
        """Crear una nueva sesión de chat"""
        if not session_id:
            session_id = f"chat_{user_id}_{int(datetime.now().timestamp())}"

        try:
            if self.db_type == "sqlite":
                self.connection.execute("""
                    INSERT INTO chat_sessions (user_id, session_id, branch_name, status)
                    VALUES (?, ?, ?, 'active')
                """, (user_id, session_id, branch_name))
                self.connection.commit()
            else:
                cursor = self.connection.cursor()
                cursor.execute("""
                    INSERT INTO chat_sessions (user_id, session_id, branch_name, status)
                    VALUES (%s, %s, %s, 'active')
                """, (user_id, session_id, branch_name))
                self.connection.commit()
                cursor.close()

            logger.info(f"✅ Sesión de chat creada: {session_id} para rama {branch_name}")
            return session_id

        except Exception as e:
            logger.error(f"❌ Error creando sesión de chat: {e}")
            raise

    def save_chat_message(self, session_id: str, user_id: int, message: str, is_user: bool, tokens_used: int = 0):
        """Guardar un mensaje de chat"""
        try:
            if self.db_type == "sqlite":
                self.connection.execute("""
                    INSERT INTO chat_messages (session_id, user_id, message, is_user, tokens_used)
                    VALUES (?, ?, ?, ?, ?)
                """, (session_id, user_id, message, is_user, tokens_used))

                # Actualizar estadísticas de la sesión
                self.connection.execute("""
                    UPDATE chat_sessions
                    SET total_messages = total_messages + 1,
                        total_tokens = total_tokens + ?,
                        last_activity = CURRENT_TIMESTAMP
                    WHERE session_id = ?
                """, (tokens_used, session_id))

                self.connection.commit()
            else:
                cursor = self.connection.cursor()
                cursor.execute("""
                    INSERT INTO chat_messages (session_id, user_id, message, is_user, tokens_used)
                    VALUES (%s, %s, %s, %s, %s)
                """, (session_id, user_id, message, is_user, tokens_used))

                # Actualizar estadísticas de la sesión
                cursor.execute("""
                    UPDATE chat_sessions
                    SET total_messages = total_messages + 1,
                        total_tokens = total_tokens + %s,
                        last_activity = CURRENT_TIMESTAMP
                    WHERE session_id = %s
                """, (tokens_used, session_id))

                self.connection.commit()
                cursor.close()

        except Exception as e:
            logger.error(f"❌ Error guardando mensaje: {e}")
            raise

    def get_chat_history(self, session_id: str, limit: int = 50) -> List[Dict[str, Any]]:
        """Obtener historial de chat de una sesión"""
        try:
            if self.db_type == "sqlite":
                cursor = self.connection.execute("""
                    SELECT * FROM chat_messages
                    WHERE session_id = ?
                    ORDER BY created_at DESC
                    LIMIT ?
                """, (session_id, limit))

                messages = []
                for row in cursor.fetchall():
                    columns = [desc[0] for desc in cursor.description]
                    messages.append(dict(zip(columns, row)))

                return messages[::-1]  # Revertir para orden cronológico

            else:
                cursor = self.connection.cursor()
                cursor.execute("""
                    SELECT * FROM chat_messages
                    WHERE session_id = %s
                    ORDER BY created_at DESC
                    LIMIT %s
                """, (session_id, limit))

                messages = []
                for row in cursor.fetchall():
                    columns = [desc[0] for desc in cursor.description]
                    messages.append(dict(zip(columns, row)))

                cursor.close()
                return messages[::-1]  # Revertir para orden cronológico

        except Exception as e:
            logger.error(f"❌ Error obteniendo historial: {e}")
            return []

    def get_database_info(self) -> Dict[str, Any]:
        """Obtener información completa de la base de datos"""
        try:
            info = {
                "type": self.db_type,
                "status": "connected",
                "timestamp": datetime.now().isoformat()
            }

            if self.db_type == "sqlite":
                # Información de SQLite
                cursor = self.connection.execute("SELECT COUNT(*) as count FROM users")
                info["users_count"] = cursor.fetchone()[0]

                cursor = self.connection.execute("SELECT COUNT(*) as count FROM chat_sessions")
                info["chat_sessions_count"] = cursor.fetchone()[0]

                cursor = self.connection.execute("SELECT COUNT(*) as count FROM branches")
                info["branches_count"] = cursor.fetchone()[0]

                # Tamaño del archivo
                db_path = self.config.get("sqlite_path", "data/sheily_ai.db")
                if os.path.exists(db_path):
                    info["database_size_mb"] = round(os.path.getsize(db_path) / (1024 * 1024), 2)

            else:
                # Información de PostgreSQL
                cursor = self.connection.cursor()

                cursor.execute("SELECT COUNT(*) FROM users")
                info["users_count"] = cursor.fetchone()[0]

                cursor.execute("SELECT COUNT(*) FROM chat_sessions")
                info["chat_sessions_count"] = cursor.fetchone()[0]

                cursor.execute("SELECT COUNT(*) FROM branches")
                info["branches_count"] = cursor.fetchone()[0]

                cursor.close()

            return info

        except Exception as e:
            logger.error(f"❌ Error obteniendo info de BD: {e}")
            return {"type": self.db_type, "status": "error", "error": str(e)}

    def close(self):
        """Cerrar conexión a la base de datos"""
        try:
            if self.connection:
                if self.db_type == "sqlite":
                    self.connection.close()
                else:
                    self.connection.close()
                logger.info("✅ Conexión a base de datos cerrada")
        except Exception as e:
            logger.error(f"❌ Error cerrando conexión: {e}")


# Instancia global
_db_manager = None

def get_db_manager() -> HybridDatabaseManager:
    """Obtener instancia global del gestor de base de datos"""
    global _db_manager
    if _db_manager is None:
        _db_manager = HybridDatabaseManager()
    return _db_manager


if __name__ == "__main__":
    # Configurar logging
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

    # Probar el gestor
    try:
        manager = get_db_manager()
        info = manager.get_database_info()
        print("✅ Base de datos configurada correctamente")
        print(f"📊 Información: {info}")

        # Crear usuario de prueba
        user_id = manager.create_user(
            username="test_user",
            email="test@example.com",
            password_hash=hashlib.sha256("test_password".encode()).hexdigest(),
            full_name="Usuario de Prueba"
        )
        print(f"✅ Usuario de prueba creado con ID: {user_id}")

        # Crear sesión de chat de prueba
        session_id = manager.create_chat_session(user_id, "matematicas")
        print(f"✅ Sesión de chat creada: {session_id}")

        # Guardar mensaje de prueba
        manager.save_chat_message(session_id, user_id, "Hola, ¿qué es un número primo?", True, 10)
        manager.save_chat_message(session_id, user_id, "Un número primo es un número natural mayor que 1 que solo es divisible por 1 y por sí mismo.", False, 25)

        # Obtener historial
        history = manager.get_chat_history(session_id)
        print(f"✅ Historial de chat: {len(history)} mensajes")

        print("\n🎉 ¡Sistema de base de datos funcionando correctamente!")

    except Exception as e:
        print(f"❌ Error probando el sistema: {e}")
        import traceback
        traceback.print_exc()

    finally:
        if _db_manager:
            _db_manager.close()
