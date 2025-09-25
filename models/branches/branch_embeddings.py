#!/usr/bin/env python3
"""
Branch Embeddings System
========================

Sistema de embeddings para las ramas de conocimiento especializadas.
"""

import numpy as np
import logging
from typing import Dict, List, Any, Optional
from dataclasses import dataclass

logger = logging.getLogger(__name__)


@dataclass
class BranchEmbedding:
    """Representa un embedding de una rama específica"""

    branch_id: str
    embedding_vector: np.ndarray
    metadata: Dict[str, Any]
    created_at: str


class BranchEmbeddings:
    """Gestor de embeddings para ramas de conocimiento"""

    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.embeddings_cache = {}
        self.initialized = False

        try:
            self._initialize_embeddings()
            self.initialized = True
            self.logger.info("✅ BranchEmbeddings inicializado")
        except Exception as e:
            self.logger.error(f"❌ Error inicializando BranchEmbeddings: {e}")
            self.initialized = False

    def _initialize_embeddings(self):
        """Inicializar sistema de embeddings"""
        # Crear embeddings simulados para las ramas principales
        branch_domains = [
            "programming",
            "ai",
            "database",
            "general",
            "science",
            "mathematics",
            "literature",
            "history",
        ]

        for domain in branch_domains:
            # Crear embedding simulado (768 dimensiones, típico para modelos)
            embedding_vector = np.random.normal(0, 1, 768)

            self.embeddings_cache[domain] = BranchEmbedding(
                branch_id=domain,
                embedding_vector=embedding_vector,
                metadata={
                    "domain": domain,
                    "vector_size": 768,
                    "model_type": "simulated",
                    "created_method": "random_normal",
                },
                created_at="2025-09-17T22:52:00Z",
            )

    def get_embedding(self, branch_id: str) -> Optional[BranchEmbedding]:
        """Obtener embedding de una rama específica"""
        return self.embeddings_cache.get(branch_id)

    def get_available_branches(self) -> List[str]:
        """Obtener lista de ramas con embeddings disponibles"""
        return list(self.embeddings_cache.keys())

    def compute_similarity(self, branch_a: str, branch_b: str) -> float:
        """Calcular similitud entre dos ramas"""
        if not self.initialized:
            return 0.0

        embedding_a = self.get_embedding(branch_a)
        embedding_b = self.get_embedding(branch_b)

        if not embedding_a or not embedding_b:
            return 0.0

        # Calcular similitud coseno
        dot_product = np.dot(embedding_a.embedding_vector, embedding_b.embedding_vector)
        norm_a = np.linalg.norm(embedding_a.embedding_vector)
        norm_b = np.linalg.norm(embedding_b.embedding_vector)

        if norm_a == 0 or norm_b == 0:
            return 0.0

        similarity = dot_product / (norm_a * norm_b)
        return float(similarity)

    def find_similar_branches(self, target_branch: str, top_k: int = 5) -> List[tuple]:
        """Encontrar ramas similares a la target"""
        if not self.initialized or target_branch not in self.embeddings_cache:
            return []

        similarities = []
        for branch_id in self.embeddings_cache:
            if branch_id != target_branch:
                similarity = self.compute_similarity(target_branch, branch_id)
                similarities.append((branch_id, similarity))

        # Ordenar por similitud descendente
        similarities.sort(key=lambda x: x[1], reverse=True)
        return similarities[:top_k]

    def get_branch_info(self, branch_id: str) -> Dict[str, Any]:
        """Obtener información detallada de una rama"""
        embedding = self.get_embedding(branch_id)
        if not embedding:
            return {"error": f"Branch {branch_id} not found"}

        return {
            "branch_id": embedding.branch_id,
            "vector_dimensions": len(embedding.embedding_vector),
            "metadata": embedding.metadata,
            "created_at": embedding.created_at,
            "similar_branches": self.find_similar_branches(branch_id, 3),
        }
