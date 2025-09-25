#!/usr/bin/env python3
"""
Script de pruebas para verificar la migración de datos de DuckDB a PostgreSQL
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


def compare_table_data(
    duckdb_path: str, table_name: str, postgres_url: str, model_class
):
    """
    Comparar datos migrados entre DuckDB y PostgreSQL

    Args:
        duckdb_path (str): Ruta de la base de datos DuckDB
        table_name (str): Nombre de la tabla a comparar
        postgres_url (str): URL de conexión a PostgreSQL
        model_class: Clase del modelo SQLAlchemy

    Returns:
        bool: True si los datos coinciden, False en caso de error
    """
    logger.info(f"Comparando tabla {table_name}")

    # Conexión a DuckDB
    duckdb_conn = duckdb.connect(duckdb_path)

    # Conexión a PostgreSQL
    pg_engine = sa.create_engine(postgres_url)
    Session = sessionmaker(bind=pg_engine)
    session = Session()

    try:
        # Extraer datos de DuckDB
        duckdb_query = f"SELECT * FROM {table_name}"
        duckdb_data = duckdb_conn.execute(duckdb_query).fetchall()
        duckdb_columns = [
            desc[0] for desc in duckdb_conn.execute(duckdb_query).description
        ]

        # Extraer datos de PostgreSQL
        pg_data = session.query(model_class).all()

        # Comparar número de registros
        if len(duckdb_data) != len(pg_data):
            logger.error(
                f"Número de registros no coincide: DuckDB {len(duckdb_data)}, PostgreSQL {len(pg_data)}"
            )
            return False

        # Convertir datos de PostgreSQL a formato comparable
        pg_data_dicts = []
        for item in pg_data:
            item_dict = {col: getattr(item, col) for col in duckdb_columns}
            pg_data_dicts.append(item_dict)

        # Comparar datos
        for duckdb_row in duckdb_data:
            duckdb_dict = dict(zip(duckdb_columns, duckdb_row))

            # Convertir JSON si es necesario
            if "metadata" in duckdb_dict and isinstance(duckdb_dict["metadata"], str):
                duckdb_dict["metadata"] = json.loads(duckdb_dict["metadata"])

            # Buscar registro equivalente en PostgreSQL
            matching_pg_record = next(
                (
                    pg_rec
                    for pg_rec in pg_data_dicts
                    if all(
                        duckdb_dict.get(key) == pg_rec.get(key)
                        for key in duckdb_dict.keys()
                    )
                ),
                None,
            )

            if not matching_pg_record:
                logger.error(
                    f"No se encontró registro equivalente en PostgreSQL: {duckdb_dict}"
                )
                return False

        logger.info(f"✅ Tabla {table_name} migrada correctamente")
        return True

    except Exception as e:
        logger.error(f"❌ Error comparando {table_name}: {e}")
        return False

    finally:
        session.close()
        duckdb_conn.close()


def main():
    """
    Ejecutar pruebas de migración de datos
    """
    logger.info("🚀 Iniciando pruebas de migración de datos")

    # Definir pruebas
    tests = [
        {
            "duckdb_path": DUCKDB_PATHS["user_interactions"],
            "table_name": "user_interactions",
            "model_class": UserInteraction,
        },
        {
            "duckdb_path": DUCKDB_PATHS["learning_data"],
            "table_name": "learning_data",
            "model_class": LearningData,
        },
        {
            "duckdb_path": DUCKDB_PATHS["rag_memory"],
            "table_name": "rag_memory",
            "model_class": RAGMemory,
        },
    ]

    # Ejecutar pruebas
    all_tests_passed = True
    for test in tests:
        test_result = compare_table_data(
            test["duckdb_path"], test["table_name"], POSTGRES_URL, test["model_class"]
        )
        all_tests_passed &= test_result

    # Resultado final
    if all_tests_passed:
        logger.info("✅ Todas las pruebas de migración pasaron")
        exit(0)
    else:
        logger.error("❌ Algunas pruebas de migración fallaron")
        exit(1)


if __name__ == "__main__":
    main()
