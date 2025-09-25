#!/usr/bin/env python3
"""
Script de migración de datos de DuckDB a PostgreSQL
"""

import os
import json
import logging
import duckdb
import sqlalchemy as sa
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime
import numpy as np
from pathlib import Path

# Configurar logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s: %(message)s"
)
logger = logging.getLogger(__name__)

# Configuración de bases de datos
DUCKDB_PATHS = {
    "user_interactions": "data/user_data.duckdb",
    "learning_data": "data/user_data.duckdb",
    "rag_memory": "data/rag_memory.duckdb",
}

POSTGRES_URL = "postgresql://user:password@localhost/sheily_db"

# Definir modelos SQLAlchemy
Base = declarative_base()


class UserInteraction(Base):
    __tablename__ = "user_interactions"

    id = sa.Column(sa.String, primary_key=True)
    user_id = sa.Column(sa.String)
    session_id = sa.Column(sa.String)
    interaction_type = sa.Column(sa.String)
    content = sa.Column(sa.Text)
    response = sa.Column(sa.Text)
    timestamp = sa.Column(sa.DateTime, default=datetime.now)
    duration_ms = sa.Column(sa.Integer)
    metadata = sa.Column(sa.JSON)


class LearningData(Base):
    __tablename__ = "learning_data"

    id = sa.Column(sa.String, primary_key=True)
    branch_name = sa.Column(sa.String)
    question = sa.Column(sa.Text)
    answer = sa.Column(sa.Text)
    difficulty = sa.Column(sa.Float)
    category = sa.Column(sa.String)
    created_at = sa.Column(sa.DateTime, default=datetime.now)
    usage_count = sa.Column(sa.Integer, default=0)
    success_rate = sa.Column(sa.Float, default=0.0)


class RAGMemory(Base):
    __tablename__ = "rag_memory"

    id = sa.Column(sa.String, primary_key=True)
    content = sa.Column(sa.Text, nullable=False)
    embedding_path = sa.Column(sa.String)
    source = sa.Column(sa.String)
    domain = sa.Column(sa.String)
    relevance_score = sa.Column(sa.Float, default=1.0)
    access_count = sa.Column(sa.Integer, default=0)
    last_accessed = sa.Column(sa.DateTime, default=datetime.now)
    created_at = sa.Column(sa.DateTime, default=datetime.now)
    metadata = sa.Column(sa.JSON)


def migrate_table(duckdb_path: str, table_name: str, model_class, postgres_url: str):
    """
    Migrar datos de una tabla de DuckDB a PostgreSQL

    Args:
        duckdb_path (str): Ruta de la base de datos DuckDB
        table_name (str): Nombre de la tabla a migrar
        model_class: Clase del modelo SQLAlchemy
        postgres_url (str): URL de conexión a PostgreSQL
    """
    logger.info(f"Migrando tabla {table_name} de {duckdb_path}")

    # Conexión a DuckDB
    duckdb_conn = duckdb.connect(duckdb_path)

    # Conexión a PostgreSQL
    pg_engine = sa.create_engine(postgres_url)
    Base.metadata.create_all(pg_engine)
    Session = sessionmaker(bind=pg_engine)
    session = Session()

    try:
        # Extraer datos de DuckDB
        query = f"SELECT * FROM {table_name}"
        duckdb_data = duckdb_conn.execute(query).fetchall()

        # Obtener nombres de columnas
        columns = [desc[0] for desc in duckdb_conn.execute(query).description]

        # Migrar datos
        for row_data in duckdb_data:
            # Convertir datos a diccionario
            row_dict = dict(zip(columns, row_data))

            # Convertir JSON si es necesario
            if "metadata" in row_dict and isinstance(row_dict["metadata"], str):
                row_dict["metadata"] = json.loads(row_dict["metadata"])

            # Crear instancia del modelo
            model_instance = model_class(**row_dict)
            session.merge(model_instance)

        # Confirmar cambios
        session.commit()
        logger.info(
            f"✅ Migración de {table_name} completada: {len(duckdb_data)} registros"
        )

    except Exception as e:
        session.rollback()
        logger.error(f"❌ Error migrando {table_name}: {e}")

    finally:
        session.close()
        duckdb_conn.close()


def main():
    """
    Ejecutar migración de todas las tablas
    """
    logger.info("🚀 Iniciando migración de datos de DuckDB a PostgreSQL")

    # Migrar tablas
    migrate_table(
        DUCKDB_PATHS["user_interactions"],
        "user_interactions",
        UserInteraction,
        POSTGRES_URL,
    )

    migrate_table(
        DUCKDB_PATHS["learning_data"], "learning_data", LearningData, POSTGRES_URL
    )

    migrate_table(DUCKDB_PATHS["rag_memory"], "rag_memory", RAGMemory, POSTGRES_URL)

    logger.info("✅ Migración completada")


if __name__ == "__main__":
    main()
