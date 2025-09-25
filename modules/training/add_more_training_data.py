#!/usr/bin/env python3
"""
Script para agregar más datos de entrenamiento a las ramas con pocos ejemplos
"""

import logging
import sqlite3
import uuid

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def add_training_data(domain, examples):
    """Agregar datos de entrenamiento a una base de datos SQLite"""
    try:
        # Conectar a base de datos
        conn = sqlite3.connect("training_data.db")
        cursor = conn.cursor()

        # Crear tabla si no existe
        cursor.execute(
            """
        CREATE TABLE IF NOT EXISTS training_examples (
            id TEXT PRIMARY KEY,
            domain TEXT,
            input_text TEXT,
            target_text TEXT,
            quality_score REAL
        )
        """
        )

        # Agregar ejemplos
        for example in examples:
            cursor.execute(
                """
            INSERT INTO training_examples 
            (id, domain, input_text, target_text, quality_score)
            VALUES (?, ?, ?, ?, ?)
            """,
                (
                    str(uuid.uuid4()),
                    domain,
                    example["input"],
                    example["output"],
                    example.get("quality_score", 0.9),
                ),
            )

        # Confirmar cambios
        conn.commit()
        conn.close()

        logger.info(f"✅ {len(examples)} ejemplos agregados para dominio {domain}")
        return True

    except Exception as e:
        logger.error(f"❌ Error agregando datos de entrenamiento: {e}")
        return False


def main():
    """Demostración de adición de datos de entrenamiento"""
    try:
        # Ejemplos de entrenamiento por dominio
        training_data = {
            "medical": [
                {
                    "input": "¿Cuáles son los síntomas de la hipertensión?",
                    "output": "Los síntomas incluyen dolor de cabeza, mareos, falta de aliento y sangrado nasal.",
                    "quality_score": 0.9,
                }
            ],
            "technical": [
                {
                    "input": "¿Qué es machine learning?",
                    "output": "Machine learning es una rama de la inteligencia artificial que permite a las computadoras aprender de datos sin ser programadas explícitamente.",
                    "quality_score": 0.95,
                }
            ],
        }

        # Agregar datos de entrenamiento
        for domain, examples in training_data.items():
            success = add_training_data(domain, examples)
            print(f"Dominio {domain}: {success}")

        return {
            "status": "ok",
            "message": "Módulo de adición de datos de entrenamiento funcionando",
            "domains_added": len(training_data),
        }

    except Exception as e:
        logger.error(f"❌ Error en el módulo: {e}")
        return {"status": "error", "message": str(e)}


if __name__ == "__main__":
    result = main()
    print(result)
