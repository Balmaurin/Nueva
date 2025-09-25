import logging
from dataclasses import dataclass, field
from typing import Dict, Any, List, Optional
import sqlite3
from pathlib import Path
import numpy as np
from datetime import datetime

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@dataclass
class LearningSystemConfig:
    """Configuración del sistema de aprendizaje unificado"""

    database_path: str = "./data/learning_system.db"
    max_knowledge_entries: int = 10000
    learning_rate: float = 0.01


class UnifiedLearningSystem:
    """Sistema de aprendizaje continuo unificado"""

    def __init__(self, config: LearningSystemConfig = None):
        self.config = config or LearningSystemConfig()
        self._initialize_database()
        self._initialize_performance_metrics()

    def _initialize_database(self):
        """Inicializar base de datos de conocimiento"""
        Path(self.config.database_path).parent.mkdir(parents=True, exist_ok=True)

        with sqlite3.connect(self.config.database_path) as conn:
            cursor = conn.cursor()

            # Tabla de conocimiento
            cursor.execute(
                """
                CREATE TABLE IF NOT EXISTS knowledge_base (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    domain TEXT NOT NULL,
                    input_text TEXT NOT NULL,
                    target_text TEXT NOT NULL,
                    quality_score REAL DEFAULT 0.9,
                    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
                )
            """
            )

            # Tabla de métricas de rendimiento
            cursor.execute(
                """
                CREATE TABLE IF NOT EXISTS performance_metrics (
                    domain TEXT PRIMARY KEY,
                    total_entries INTEGER DEFAULT 0,
                    average_quality REAL DEFAULT 0.9,
                    last_updated DATETIME DEFAULT CURRENT_TIMESTAMP
                )
            """
            )

            conn.commit()

    def _initialize_performance_metrics(self):
        """Inicializar métricas de rendimiento"""
        with sqlite3.connect(self.config.database_path) as conn:
            cursor = conn.cursor()

            # No hay dominios predefinidos, solo insertar si no existe
            cursor.execute(
                """
                INSERT OR IGNORE INTO performance_metrics (domain) 
                VALUES (?)
            """,
                ("general",),
            )  # Insertar un dominio por defecto

            conn.commit()

    def learn(
        self,
        input_text: str,
        target_text: str,
        domain: str = "general",
        quality_score: float = 0.9,
    ) -> bool:
        """Método unificado de aprendizaje"""
        try:
            with sqlite3.connect(self.config.database_path) as conn:
                cursor = conn.cursor()

                # Insertar entrada de conocimiento
                cursor.execute(
                    """
                    INSERT INTO knowledge_base 
                    (domain, input_text, target_text, quality_score) 
                    VALUES (?, ?, ?, ?)
                """,
                    (domain, input_text, target_text, quality_score),
                )

                # Actualizar métricas de rendimiento
                cursor.execute(
                    """
                    UPDATE performance_metrics 
                    SET total_entries = total_entries + 1, 
                        average_quality = (average_quality * (total_entries) + ?) / (total_entries + 1),
                        last_updated = CURRENT_TIMESTAMP
                    WHERE domain = ?
                """,
                    (quality_score, domain),
                )

                # Gestionar límite de entradas
                self._manage_knowledge_base_size(cursor)

                conn.commit()

            logger.info(f"✅ Aprendizaje completado en dominio {domain}")
            return True

        except Exception as e:
            logger.error(f"❌ Error en proceso de aprendizaje: {e}")
            return False

    def _manage_knowledge_base_size(self, cursor):
        """Gestionar tamaño de la base de conocimiento"""
        cursor.execute("SELECT COUNT(*) FROM knowledge_base")
        total_entries = cursor.fetchone()[0]

        if total_entries > self.config.max_knowledge_entries:
            # Eliminar entradas más antiguas
            cursor.execute(
                """
                DELETE FROM knowledge_base 
                WHERE id IN (
                    SELECT id FROM knowledge_base 
                    ORDER BY timestamp ASC 
                    LIMIT ?
                )
            """,
                (total_entries - self.config.max_knowledge_entries,),
            )

    def get_performance_summary(self, domain: Optional[str] = None) -> Dict[str, Any]:
        """Obtener resumen de rendimiento"""
        with sqlite3.connect(self.config.database_path) as conn:
            cursor = conn.cursor()

            if domain:
                cursor.execute(
                    """
                    SELECT * FROM performance_metrics 
                    WHERE domain = ?
                """,
                    (domain,),
                )
            else:
                cursor.execute("SELECT * FROM performance_metrics")

            columns = [column[0] for column in cursor.description]
            results = [dict(zip(columns, row)) for row in cursor.fetchall()]

        return results

    def query_knowledge_base(
        self, query: str, domain: Optional[str] = None, top_k: int = 5
    ) -> List[Dict[str, Any]]:
        """Consultar base de conocimiento"""
        with sqlite3.connect(self.config.database_path) as conn:
            cursor = conn.cursor()

            if domain:
                cursor.execute(
                    """
                    SELECT input_text, target_text, quality_score 
                    FROM knowledge_base 
                    WHERE domain = ? 
                    ORDER BY quality_score DESC 
                    LIMIT ?
                """,
                    (domain, top_k),
                )
            else:
                cursor.execute(
                    """
                    SELECT input_text, target_text, quality_score 
                    FROM knowledge_base 
                    ORDER BY quality_score DESC 
                    LIMIT ?
                """,
                    (top_k,),
                )

            columns = ["input_text", "target_text", "quality_score"]
            return [dict(zip(columns, row)) for row in cursor.fetchall()]


def main():
    """Demostración del sistema de aprendizaje unificado"""
    learning_system = UnifiedLearningSystem()

    # Demostrar la flexibilidad de aprendizaje en diferentes dominios
    ejemplos_aprendizaje = [
        {
            "input_text": "Análisis sintáctico del español",
            "target_text": "El análisis sintáctico estudia la estructura gramatical de las oraciones, identificando sujetos, predicados y complementos.",
            "domain": "Lingüística",
            "quality_score": 0.95,
        },
        {
            "input_text": "Teorema de Pitágoras",
            "target_text": "En un triángulo rectángulo, el cuadrado de la hipotenusa es igual a la suma de los cuadrados de los catetos.",
            "domain": "Matemáticas",
            "quality_score": 0.97,
        },
        {
            "input_text": "Ejemplo de aprendizaje genérico",
            "target_text": "Este es un ejemplo de cómo se puede aprender en cualquier dominio.",
            "domain": "General",
            "quality_score": 0.90,
        },
    ]

    # Aprender ejemplos
    for datos in ejemplos_aprendizaje:
        learning_system.learn(**datos)

    # Consultar base de conocimiento
    print("Consulta de base de conocimiento:")
    dominios_a_consultar = ["Lingüística", "Matemáticas", "General"]

    for dominio in dominios_a_consultar:
        print(f"\nDominio: {dominio}")
        resultados = learning_system.query_knowledge_base(domain=dominio)
        for resultado in resultados:
            print(f"Entrada: {resultado['input_text']}")
            print(f"Respuesta: {resultado['target_text']}")
            print(f"Calidad: {resultado['quality_score']}\n")

    # Obtener resumen de rendimiento
    print("Resumen de Rendimiento:")
    resumen_rendimiento = learning_system.get_performance_summary()
    for resumen in resumen_rendimiento:
        print(resumen)


if __name__ == "__main__":
    main()
