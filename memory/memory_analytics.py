#!/usr/bin/env python3
"""
Módulo de Análisis Avanzado de Memoria para Shaili AI

Proporciona herramientas para analizar y extraer insights de los diferentes
tipos de memoria del sistema.
"""

import sqlite3
import logging
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from collections import Counter, defaultdict
import json

from .short_term import ShortTermMemoryManager
from .long_term import LongTermMemoryManager
from .episodic import EpisodicMemoryManager
from .semantic import SemanticMemoryManager


class MemoryAnalytics:
    """
    Clase para realizar análisis avanzados sobre los diferentes tipos de memoria
    """

    def __init__(
        self,
        short_term_memory: Optional[ShortTermMemoryManager] = None,
        long_term_memory: Optional[LongTermMemoryManager] = None,
        episodic_memory: Optional[EpisodicMemoryManager] = None,
        semantic_memory: Optional[SemanticMemoryManager] = None,
    ):
        """
        Inicializar gestor de análisis de memoria

        :param short_term_memory: Gestor de memoria a corto plazo
        :param long_term_memory: Gestor de memoria a largo plazo
        :param episodic_memory: Gestor de memoria episódica
        :param semantic_memory: Gestor de memoria semántica
        """
        self.short_term_memory = short_term_memory
        self.long_term_memory = long_term_memory
        self.episodic_memory = episodic_memory
        self.semantic_memory = semantic_memory

        self.logger = logging.getLogger(__name__)

    def analyze_conversation_patterns(
        self, user_id: Optional[str] = None, days: int = 30
    ) -> Dict[str, Any]:
        """
        Analizar patrones de conversación

        :param user_id: ID del usuario para análisis específico
        :param days: Número de días para el análisis
        :return: Diccionario con insights de patrones de conversación
        """
        if not self.short_term_memory:
            raise ValueError("No se ha proporcionado gestor de memoria a corto plazo")

        try:
            with sqlite3.connect(self.short_term_memory.config.database_path) as conn:
                cursor = conn.cursor()

                # Consulta base para análisis de conversación
                query = """
                SELECT 
                    role, 
                    COUNT(*) as message_count, 
                    AVG(LENGTH(content)) as avg_message_length,
                    MIN(timestamp) as first_message,
                    MAX(timestamp) as last_message
                FROM messages
                WHERE timestamp >= ?
                """
                params = [datetime.now().timestamp() - (days * 24 * 3600)]

                if user_id:
                    query += " AND user_id = ?"
                    params.append(user_id)

                query += " GROUP BY role"

                cursor.execute(query, params)
                results = cursor.fetchall()

                # Procesar resultados
                conversation_analysis = {
                    "total_messages": sum(row[1] for row in results),
                    "message_breakdown": {},
                    "conversation_span": None,
                }

                for row in results:
                    role, count, avg_length, first_msg, last_msg = row
                    conversation_analysis["message_breakdown"][role] = {
                        "count": count,
                        "avg_length": avg_length,
                    }

                # Calcular span de conversación
                if results:
                    first_message = datetime.fromtimestamp(
                        min(row[3] for row in results)
                    )
                    last_message = datetime.fromtimestamp(
                        max(row[4] for row in results)
                    )
                    conversation_analysis["conversation_span"] = {
                        "start": first_message.isoformat(),
                        "end": last_message.isoformat(),
                        "duration": (last_message - first_message).total_seconds(),
                    }

                return conversation_analysis

        except Exception as e:
            self.logger.error(f"Error analizando patrones de conversación: {e}")
            raise

    def find_semantic_clusters(self, top_k: int = 10) -> List[Dict[str, Any]]:
        """
        Encontrar clusters semánticos en la memoria

        :param top_k: Número máximo de clusters a devolver
        :return: Lista de clusters semánticos
        """
        if not self.semantic_memory:
            raise ValueError("No se ha proporcionado gestor de memoria semántica")

        try:
            with sqlite3.connect(self.semantic_memory.config.database_path) as conn:
                cursor = conn.cursor()
                cursor.execute(
                    "SELECT concept, description, embedding FROM semantic_memory"
                )
                concepts = cursor.fetchall()

                # Convertir embeddings
                embeddings = [np.array(json.loads(emb)) for _, _, emb in concepts]

                # Calcular similitudes
                similarity_matrix = cosine_similarity(embeddings)

                # Encontrar clusters
                clusters = []
                used_indices = set()

                for i in range(len(concepts)):
                    if i in used_indices:
                        continue

                    # Encontrar conceptos similares
                    similar_indices = np.where(similarity_matrix[i] > 0.7)[0]

                    # Crear clúster
                    clusters.append(
                        {
                            "central_concept": {
                                "name": concepts[i][0],
                                "description": concepts[i][1],
                            },
                            "similar_concepts": [
                                {
                                    "name": concepts[idx][0],
                                    "description": concepts[idx][1],
                                    "similarity": similarity_matrix[i][idx],
                                }
                                for idx in similar_indices
                                if idx != i
                            ],
                        }
                    )

                    used_indices.update(similar_indices)

                    if len(clusters) >= top_k:
                        break

                return clusters

        except Exception as e:
            self.logger.error(f"Error encontrando clusters semánticos: {e}")
            raise

    def analyze_episodic_memory(
        self, start_date: Optional[datetime] = None, end_date: Optional[datetime] = None
    ) -> Dict[str, Any]:
        """
        Analizar memoria episódica

        :param start_date: Fecha de inicio para el análisis
        :param end_date: Fecha de fin para el análisis
        :return: Diccionario con análisis de memoria episódica
        """
        if not self.episodic_memory:
            raise ValueError("No se ha proporcionado gestor de memoria episódica")

        try:
            with sqlite3.connect(self.episodic_memory.config.database_path) as conn:
                cursor = conn.cursor()

                # Construir consulta con filtros de fecha
                query = "SELECT event_type, tags, importance, timestamp FROM episodic_memory WHERE 1=1"
                params = []

                if start_date:
                    query += " AND timestamp >= ?"
                    params.append(start_date.timestamp())

                if end_date:
                    query += " AND timestamp <= ?"
                    params.append(end_date.timestamp())

                cursor.execute(query, params)
                episodes = cursor.fetchall()

                # Analizar episodios
                analysis = {
                    "total_episodes": len(episodes),
                    "event_type_distribution": Counter(),
                    "tag_distribution": Counter(),
                    "importance_stats": {"mean": 0, "median": 0, "max": 0, "min": 0},
                    "temporal_distribution": defaultdict(int),
                }

                # Procesar episodios
                importances = []
                for event_type, tags_str, importance, timestamp in episodes:
                    analysis["event_type_distribution"][event_type] += 1

                    # Procesar tags
                    tags = json.loads(tags_str) if tags_str else []
                    analysis["tag_distribution"].update(tags)

                    # Calcular estadísticas de importancia
                    importances.append(importance)

                    # Distribución temporal
                    date = datetime.fromtimestamp(timestamp).date()
                    analysis["temporal_distribution"][date.isoformat()] += 1

                # Calcular estadísticas de importancia
                if importances:
                    analysis["importance_stats"] = {
                        "mean": np.mean(importances),
                        "median": np.median(importances),
                        "max": np.max(importances),
                        "min": np.min(importances),
                    }

                return analysis

        except Exception as e:
            self.logger.error(f"Error analizando memoria episódica: {e}")
            raise


def create_memory_analytics(
    short_term_memory: Optional[ShortTermMemoryManager] = None,
    long_term_memory: Optional[LongTermMemoryManager] = None,
    episodic_memory: Optional[EpisodicMemoryManager] = None,
    semantic_memory: Optional[SemanticMemoryManager] = None,
) -> MemoryAnalytics:
    """
    Crear una instancia del gestor de análisis de memoria

    :return: Instancia de MemoryAnalytics
    """
    return MemoryAnalytics(
        short_term_memory, long_term_memory, episodic_memory, semantic_memory
    )
