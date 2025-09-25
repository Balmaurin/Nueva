#!/usr/bin/env python3
"""
Gestor de Memoria Semántica para Sheily AI
Sistema para almacenar y gestionar conocimientos conceptuales y relacionales
"""

import json
import os
import time
import sqlite3
from pathlib import Path
from typing import List, Dict, Optional, Any, Tuple
from dataclasses import dataclass, asdict
import logging
import threading
import hashlib
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity


@dataclass
class SemanticMemoryConfig:
    """Configuración de la memoria semántica"""

    max_concepts: int = 10000
    database_path: str = "semantic/memory.db"
    memory_dir: str = "semantic/memory"
    backup_enabled: bool = True
    cleanup_interval: int = 86400  # 24 horas
    similarity_threshold: float = 0.7


class SemanticMemoryManager:
    """Gestor principal de memoria semántica"""

    def __init__(self, config: Optional[SemanticMemoryConfig] = None):
        self.config = config or SemanticMemoryConfig()
        self.logger = logging.getLogger(__name__)

        # Crear directorios necesarios
        self._create_directories()

        # Base de datos
        self.db_path = Path(self.config.database_path)
        self._init_database()

        # Vectorizador TF-IDF
        self.vectorizer = TfidfVectorizer()

        # Threading
        self.lock = threading.RLock()

        # Iniciar limpieza automática
        self._start_cleanup_thread()

    def _create_directories(self):
        """Crear directorios necesarios"""
        directories = [self.config.memory_dir, Path(self.config.database_path).parent]

        for directory in directories:
            Path(directory).mkdir(parents=True, exist_ok=True)

    def _init_database(self):
        """Inicializar base de datos SQLite"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute(
                """
                CREATE TABLE IF NOT EXISTS semantic_memory (
                    id TEXT PRIMARY KEY,
                    domain TEXT,
                    concept TEXT,
                    description TEXT,
                    embedding TEXT,
                    metadata TEXT,
                    created_at REAL,
                    last_accessed REAL,
                    access_count INTEGER
                )
            """
            )
            conn.commit()

    def add_concept(
        self,
        domain: str,
        concept: str,
        description: str,
        metadata: Dict[str, Any] = None,
    ) -> str:
        """Añadir un nuevo concepto a la memoria semántica"""
        with self.lock:
            # Generar ID único
            concept_id = f"sem_{int(time.time())}_{hashlib.md5(concept.encode()).hexdigest()[:8]}"

            # Generar embedding
            embedding = self._generate_embedding(description)

            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute(
                    """
                    INSERT INTO semantic_memory 
                    (id, domain, concept, description, embedding, metadata, created_at, last_accessed, access_count)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                    (
                        concept_id,
                        domain,
                        concept,
                        description,
                        json.dumps(embedding.tolist()),
                        json.dumps(metadata or {}),
                        time.time(),
                        time.time(),
                        1,
                    ),
                )
                conn.commit()

            self.logger.debug(f"Concepto semántico añadido: {concept_id}")
            return concept_id

    def find_similar_concepts(
        self, query: str, domain: str = None, top_k: int = 5
    ) -> List[Dict[str, Any]]:
        """Encontrar conceptos similares semánticamente"""
        with self.lock:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()

                # Construir consulta base
                query_base = "SELECT id, domain, concept, description, embedding, metadata FROM semantic_memory"
                conditions = []
                params = []

                if domain:
                    conditions.append("domain = ?")
                    params.append(domain)

                if conditions:
                    query_base += " WHERE " + " AND ".join(conditions)

                cursor.execute(query_base, params)

                # Generar embedding de la consulta
                query_embedding = self._generate_embedding(query)

                # Calcular similitudes
                similar_concepts = []
                for row in cursor.fetchall():
                    concept_embedding = np.array(json.loads(row[4]))
                    similarity = cosine_similarity(
                        query_embedding.reshape(1, -1), concept_embedding.reshape(1, -1)
                    )[0][0]

                    if similarity >= self.config.similarity_threshold:
                        similar_concepts.append(
                            {
                                "id": row[0],
                                "domain": row[1],
                                "concept": row[2],
                                "description": row[3],
                                "metadata": json.loads(row[5]),
                                "similarity": similarity,
                            }
                        )

                # Ordenar por similitud descendente y limitar
                similar_concepts.sort(key=lambda x: x["similarity"], reverse=True)
                return similar_concepts[:top_k]

    def _generate_embedding(self, text: str) -> np.ndarray:
        """Generar embedding usando TF-IDF"""
        # Entrenar vectorizador si es necesario
        if not hasattr(self.vectorizer, "idf_"):
            self.vectorizer.fit([text])

        # Generar embedding
        return self.vectorizer.transform([text]).toarray()[0]

    def _start_cleanup_thread(self):
        """Iniciar hilo de limpieza periódica"""

        def cleanup():
            while True:
                time.sleep(self.config.cleanup_interval)
                self._cleanup_old_concepts()

        cleanup_thread = threading.Thread(target=cleanup, daemon=True)
        cleanup_thread.start()

    def _cleanup_old_concepts(self):
        """Limpiar conceptos antiguos con poco uso"""
        with self.lock:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                # Eliminar conceptos antiguos con poco uso
                cursor.execute(
                    """
                    DELETE FROM semantic_memory 
                    WHERE access_count < 2 AND last_accessed < ?
                """,
                    (time.time() - 180 * 24 * 3600,),
                )  # 180 días
                conn.commit()

            self.logger.info("Limpieza de memoria semántica completada")


def create_semantic_memory_manager(
    config: SemanticMemoryConfig = None,
) -> SemanticMemoryManager:
    """Crear una instancia del gestor de memoria semántica"""
    return SemanticMemoryManager(config)
