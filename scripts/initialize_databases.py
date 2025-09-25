#!/usr/bin/env python3
"""
Script de Inicialización de Bases de Datos NeuroFusion
"""

import logging
import sqlite3
import psycopg2
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from typing import List, Dict, Any

# Configurar logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s: %(message)s"
)
logger = logging.getLogger(__name__)


class DatabaseInitializer:
    """Inicializador de bases de datos para NeuroFusion"""

    def __init__(
        self,
        postgres_config: Dict[str, str] = None,
        sqlite_path: str = "data/neurofusion.db",
    ):
        """
        Inicializar configuraciones de bases de datos

        Args:
            postgres_config: Configuración de conexión PostgreSQL
            sqlite_path: Ruta de la base de datos SQLite
        """
        self.postgres_config = postgres_config or {
            "host": "localhost",
            "database": "neurofusion_db",
            "user": "neurofusion_user",
            "password": "neurofusion_pass",
        }
        self.sqlite_path = sqlite_path

    def _create_postgres_database(self):
        """Crear base de datos PostgreSQL si no existe"""
        try:
            # Conectar a PostgreSQL por defecto
            conn = psycopg2.connect(
                host=self.postgres_config["host"],
                user=self.postgres_config["user"],
                password=self.postgres_config["password"],
                database="postgres",
            )
            conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)

            with conn.cursor() as cur:
                # Verificar si la base de datos existe
                cur.execute(
                    f"SELECT 1 FROM pg_catalog.pg_database WHERE datname = '{self.postgres_config['database']}'"
                )
                exists = cur.fetchone()

                if not exists:
                    cur.execute(f"CREATE DATABASE {self.postgres_config['database']}")
                    logger.info(
                        f"✅ Base de datos PostgreSQL {self.postgres_config['database']} creada"
                    )
                else:
                    logger.info(
                        f"✅ Base de datos PostgreSQL {self.postgres_config['database']} ya existe"
                    )

            conn.close()
        except Exception as e:
            logger.error(f"❌ Error creando base de datos PostgreSQL: {e}")
            raise

    def _initialize_sqlite(self):
        """Inicializar base de datos SQLite con datos de prueba"""
        try:
            conn = sqlite3.connect(self.sqlite_path)
            cursor = conn.cursor()

            # Crear tablas de ejemplo
            cursor.executescript(
                """
                CREATE TABLE IF NOT EXISTS users (
                    id INTEGER PRIMARY KEY,
                    username TEXT UNIQUE NOT NULL,
                    email TEXT UNIQUE NOT NULL,
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
                );

                CREATE TABLE IF NOT EXISTS chat_sessions (
                    id INTEGER PRIMARY KEY,
                    user_id INTEGER,
                    start_time DATETIME DEFAULT CURRENT_TIMESTAMP,
                    end_time DATETIME,
                    FOREIGN KEY(user_id) REFERENCES users(id)
                );

                CREATE TABLE IF NOT EXISTS training_sessions (
                    id INTEGER PRIMARY KEY,
                    user_id INTEGER,
                    domain TEXT,
                    start_time DATETIME DEFAULT CURRENT_TIMESTAMP,
                    end_time DATETIME,
                    FOREIGN KEY(user_id) REFERENCES users(id)
                );
            """
            )

            # Insertar datos de prueba
            test_users = [
                ("admin", "admin@neurofusion.ai"),
                ("usuario1", "usuario1@neurofusion.ai"),
                ("usuario2", "usuario2@neurofusion.ai"),
            ]

            cursor.executemany(
                "INSERT OR IGNORE INTO users (username, email) VALUES (?, ?)",
                test_users,
            )

            conn.commit()
            conn.close()

            logger.info(f"✅ Base de datos SQLite inicializada en {self.sqlite_path}")
        except Exception as e:
            logger.error(f"❌ Error inicializando base de datos SQLite: {e}")
            raise

    def _initialize_postgres(self):
        """Inicializar base de datos PostgreSQL con tablas y datos"""
        try:
            # Crear conexión a PostgreSQL
            engine = create_engine(
                f"postgresql://{self.postgres_config['user']}:{self.postgres_config['password']}@"
                f"{self.postgres_config['host']}/{self.postgres_config['database']}"
            )

            # Crear sesión
            Session = sessionmaker(bind=engine)
            session = Session()

            # Crear tablas con SQLAlchemy
            session.execute(
                text(
                    """
                CREATE TABLE IF NOT EXISTS knowledge_base (
                    id SERIAL PRIMARY KEY,
                    domain TEXT NOT NULL,
                    content TEXT NOT NULL,
                    embedding BYTEA,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                );

                CREATE TABLE IF NOT EXISTS embeddings (
                    id SERIAL PRIMARY KEY,
                    model_name TEXT NOT NULL,
                    vector BYTEA NOT NULL,
                    metadata JSONB,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                );
            """
                )
            )

            # Insertar datos de prueba
            session.execute(
                text(
                    """
                INSERT INTO knowledge_base (domain, content) 
                VALUES 
                    ('inteligencia_artificial', 'La inteligencia artificial es un campo de la computación que busca crear sistemas inteligentes.'),
                    ('ciencia', 'La ciencia es un sistema de conocimiento basado en métodos empíricos y verificables.')
                ON CONFLICTS DO NOTHING;
            """
                )
            )

            session.commit()
            session.close()

            logger.info("✅ Base de datos PostgreSQL inicializada")
        except Exception as e:
            logger.error(f"❌ Error inicializando base de datos PostgreSQL: {e}")
            raise

    def initialize(self):
        """Inicializar todas las bases de datos"""
        try:
            # Crear base de datos PostgreSQL
            self._create_postgres_database()

            # Inicializar bases de datos
            self._initialize_sqlite()
            self._initialize_postgres()

            logger.info("🎉 Inicialización de bases de datos completada")
        except Exception as e:
            logger.error(f"❌ Error en inicialización de bases de datos: {e}")
            raise


def main():
    """Función principal para ejecutar la inicialización"""
    try:
        initializer = DatabaseInitializer()
        initializer.initialize()
    except Exception as e:
        logger.error(f"Error crítico: {e}")
        exit(1)


if __name__ == "__main__":
    main()
