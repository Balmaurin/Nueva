#!/usr/bin/env python3
"""
Gestor de Base de Datos Unificado - Sheily AI
=============================================
Maneja conexiones y operaciones de base de datos de forma unificada
"""

import os
import logging
import asyncio
from typing import Dict, Any, Optional, List, Union
from pathlib import Path
try:
    import asyncpg
    import psycopg2
    ASYNC_AVAILABLE = True
except ImportError:
    ASYNC_AVAILABLE = False
    import psycopg2
from contextlib import asynccontextmanager, contextmanager
import json

logger = logging.getLogger(__name__)

class DatabaseManager:
    """Gestor unificado de base de datos"""
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        self.config = config or self._load_config()
        self.db_type = self.config.get("type", "postgres")
        self.connection_pool = None
        self._setup_database()
    
    def _load_config(self) -> Dict[str, Any]:
        """Cargar configuración de base de datos PostgreSQL"""
        return {
            "type": "postgres",  # Solo PostgreSQL
            "host": os.getenv("DB_HOST", "localhost"),
            "port": int(os.getenv("DB_PORT", "5432")),
            "name": os.getenv("DB_NAME", "sheily_ai_db"),
            "user": os.getenv("DB_USER", "sheily_ai_user"),
            "password": os.getenv("DB_PASSWORD", ""),
            "pool_size": int(os.getenv("DB_POOL_SIZE", "20")),
            "timeout": int(os.getenv("DB_TIMEOUT", "30000")),
            "ssl": os.getenv("DB_SSL", "false").lower() == "true"
        }
    
    def _setup_database(self) -> None:
        """Configurar base de datos PostgreSQL"""
        self._setup_postgres()
    
    def _setup_postgres(self) -> None:
        """Configurar PostgreSQL"""
        try:
            # Verificar conexión
            conn = psycopg2.connect(
                host=self.config["host"],
                port=self.config["port"],
                database=self.config["name"],
                user=self.config["user"],
                password=self.config["password"]
            )
            conn.close()
            logger.info("✅ Conexión PostgreSQL verificada")
            
        except Exception as e:
            logger.error(f"❌ Error conectando a PostgreSQL: {e}")
            raise RuntimeError(f"No se pudo conectar a PostgreSQL: {e}")
    
    
    def get_connection_string(self) -> str:
        """Obtener string de conexión PostgreSQL"""
        return f"postgresql://{self.config['user']}:{self.config['password']}@{self.config['host']}:{self.config['port']}/{self.config['name']}"
    
    @contextmanager
    def get_connection(self):
        """Obtener conexión de base de datos PostgreSQL"""
        conn = psycopg2.connect(
            host=self.config["host"],
            port=self.config["port"],
            database=self.config["name"],
            user=self.config["user"],
            password=self.config["password"]
        )
        
        try:
            yield conn
        finally:
            conn.close()
    
    async def get_async_connection(self):
        """Obtener conexión asíncrona PostgreSQL"""
        if not ASYNC_AVAILABLE:
            raise RuntimeError("Módulos asíncronos no disponibles. Instale asyncpg.")
        
        return await asyncpg.connect(
            host=self.config["host"],
            port=self.config["port"],
            database=self.config["name"],
            user=self.config["user"],
            password=self.config["password"]
        )
    
    def execute_query(self, query: str, params: Optional[tuple] = None) -> List[Dict[str, Any]]:
        """Ejecutar consulta SQL"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            
            try:
                if params:
                    cursor.execute(query, params)
                else:
                    cursor.execute(query)
                
                if query.strip().upper().startswith(('SELECT', 'SHOW', 'DESCRIBE', 'EXPLAIN')):
                    columns = [desc[0] for desc in cursor.description] if cursor.description else []
                    results = cursor.fetchall()
                    return [dict(zip(columns, row)) for row in results]
                else:
                    conn.commit()
                    return [{"affected_rows": cursor.rowcount}]
                    
            except Exception as e:
                conn.rollback()
                logger.error(f"❌ Error ejecutando consulta: {e}")
                raise
            finally:
                cursor.close()
    
    async def execute_async_query(self, query: str, params: Optional[tuple] = None) -> List[Dict[str, Any]]:
        """Ejecutar consulta SQL asíncrona PostgreSQL"""
        if not ASYNC_AVAILABLE:
            raise RuntimeError("Módulos asíncronos no disponibles. Instale asyncpg.")
        
        conn = await self.get_async_connection()
        
        try:
            if params:
                results = await conn.fetch(query, *params)
            else:
                results = await conn.fetch(query)
            
            if query.strip().upper().startswith(('SELECT', 'SHOW', 'DESCRIBE', 'EXPLAIN')):
                return [dict(row) for row in results]
            else:
                return [{"affected_rows": len(results)}]
                
        except Exception as e:
            logger.error(f"❌ Error ejecutando consulta asíncrona: {e}")
            raise
        finally:
            await conn.close()
    
    def create_tables(self) -> bool:
        """Crear tablas de base de datos PostgreSQL"""
        try:
            return self._create_postgres_tables()
        except Exception as e:
            logger.error(f"❌ Error creando tablas: {e}")
            return False
    
    def _create_postgres_tables(self) -> bool:
        """Crear tablas PostgreSQL"""
        tables_sql = """
        -- Tabla de usuarios
        CREATE TABLE IF NOT EXISTS users (
            id SERIAL PRIMARY KEY,
            username VARCHAR(50) UNIQUE NOT NULL,
            email VARCHAR(100) UNIQUE NOT NULL,
            password_hash VARCHAR(255) NOT NULL,
            role VARCHAR(20) DEFAULT 'user',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        
        -- Tabla de ramas
        CREATE TABLE IF NOT EXISTS branches (
            id SERIAL PRIMARY KEY,
            name VARCHAR(100) UNIQUE NOT NULL,
            description TEXT,
            keywords TEXT[],
            enabled BOOLEAN DEFAULT true,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        
        -- Tabla de ejercicios
        CREATE TABLE IF NOT EXISTS branch_exercises (
            id SERIAL PRIMARY KEY,
            branch_id INTEGER REFERENCES branches(id),
            type VARCHAR(20) NOT NULL,
            level INTEGER NOT NULL,
            question TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        
        -- Tabla de respuestas
        CREATE TABLE IF NOT EXISTS branch_exercise_answers (
            id SERIAL PRIMARY KEY,
            exercise_id INTEGER REFERENCES branch_exercises(id),
            answer TEXT NOT NULL,
            is_correct BOOLEAN NOT NULL,
            explanation TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        
        -- Tabla de progreso de usuario
        CREATE TABLE IF NOT EXISTS user_branch_progress (
            id SERIAL PRIMARY KEY,
            user_id INTEGER REFERENCES users(id),
            branch_id INTEGER REFERENCES branches(id),
            level INTEGER NOT NULL,
            tokens_awarded INTEGER DEFAULT 0,
            verification_status VARCHAR(20) DEFAULT 'pending',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        
        -- Tabla de intentos de usuario
        CREATE TABLE IF NOT EXISTS user_branch_attempts (
            id SERIAL PRIMARY KEY,
            user_id INTEGER REFERENCES users(id),
            exercise_id INTEGER REFERENCES branch_exercises(id),
            answer TEXT NOT NULL,
            is_correct BOOLEAN NOT NULL,
            accuracy FLOAT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        """
        
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(tables_sql)
            conn.commit()
            cursor.close()
        
        logger.info("✅ Tablas PostgreSQL creadas exitosamente")
        return True
    
    
    def initialize_branches(self) -> bool:
        """Inicializar ramas en la base de datos"""
        try:
            # Cargar ramas desde configuración
            config_path = Path("config/unified_config.json")
            if config_path.exists():
                with open(config_path, 'r') as f:
                    config = json.load(f)
                    branches = config.get("branches", {}).get("list", [])
            else:
                branches = [
                    "lengua_y_lingüística", "matemáticas", "computación_y_programación",
                    "medicina_y_salud", "física", "química", "biología", "historia",
                    "geografía_y_geo_política", "economía_y_finanzas", "derecho_y_políticas_públicas",
                    "educación_y_pedagogía", "ingeniería", "empresa_y_emprendimiento",
                    "arte_música_y_cultura", "literatura_y_escritura", "medios_y_comunicación",
                    "deportes_y_esports", "juegos_y_entretenimiento", "cocina_y_nutrición",
                    "hogar_diy_y_reparaciones", "viajes_e_idiomas", "vida_diaria_legal_práctico_y_trámites",
                    "sociología_y_antropología", "neurociencia_y_psicología", "astronomía_y_espacio",
                    "ciencias_de_la_tierra_y_clima", "ciencia_de_datos_e_ia", "ciberseguridad_y_criptografía",
                    "electrónica_y_iot", "sistemas_devops_redes", "diseño_y_ux", "general",
                    "maestros_de_los_números", "sanadores_del_cuerpo_y_alma"
                ]
            
            # Insertar ramas
            for branch_name in branches:
                self.execute_query(
                    "INSERT INTO branches (name, description, enabled) VALUES (%s, %s, %s) ON CONFLICT (name) DO NOTHING",
                    (branch_name, f"Rama especializada en {branch_name}", True)
                )
            
            logger.info(f"✅ {len(branches)} ramas inicializadas en la base de datos")
            return True
            
        except Exception as e:
            logger.error(f"❌ Error inicializando ramas: {e}")
            return False
    
    def get_database_info(self) -> Dict[str, Any]:
        """Obtener información de la base de datos"""
        try:
            info = {
                "type": self.db_type,
                "connection_string": self.get_connection_string(),
                "tables": [],
                "branches_count": 0,
                "users_count": 0
            }
            
            # Obtener lista de tablas
            if self.db_type == "postgres":
                tables = self.execute_query(
                    "SELECT table_name FROM information_schema.tables WHERE table_schema = 'public'"
                )
            else:  # SQLite
                tables = self.execute_query("SELECT name FROM sqlite_master WHERE type='table'")
            
            info["tables"] = [table["table_name" if self.db_type == "postgres" else "name"] for table in tables]
            
            # Contar registros
            try:
                branches_count = self.execute_query("SELECT COUNT(*) as count FROM branches")
                info["branches_count"] = branches_count[0]["count"] if branches_count else 0
            except:
                info["branches_count"] = 0
            
            try:
                users_count = self.execute_query("SELECT COUNT(*) as count FROM users")
                info["users_count"] = users_count[0]["count"] if users_count else 0
            except:
                info["users_count"] = 0
            
            return info
            
        except Exception as e:
            logger.error(f"❌ Error obteniendo información de base de datos: {e}")
            return {"type": self.db_type, "error": str(e)}

# Instancia global del gestor de base de datos
db_manager = DatabaseManager()

def get_db_manager() -> DatabaseManager:
    """Obtener instancia del gestor de base de datos"""
    return db_manager

if __name__ == "__main__":
    # Configurar logging
    logging.basicConfig(level=logging.INFO)
    
    # Crear instancia del gestor
    manager = DatabaseManager()
    
    # Mostrar información
    info = manager.get_database_info()
    print(f"Información de base de datos: {info}")
    
    # Crear tablas
    if manager.create_tables():
        print("✅ Tablas creadas exitosamente")
        
        # Inicializar ramas
        if manager.initialize_branches():
            print("✅ Ramas inicializadas exitosamente")
        else:
            print("❌ Error inicializando ramas")
    else:
        print("❌ Error creando tablas")
