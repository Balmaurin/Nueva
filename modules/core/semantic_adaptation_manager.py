import logging
from typing import Dict, Any, List, Optional
import numpy as np
import torch
from sklearn.cluster import DBSCAN
from transformers import AutoModel, AutoTokenizer
from datetime import datetime


class SemanticAdaptationManager:
    def __init__(
        self,
        base_model_path: str = "models/custom/sheily-personal-model",
        config_path: str = "utils/semantic_adaptation_config.yaml",
    ):
        """
        Gestor de adaptación semántica multidominio

        Args:
            base_model_path (str): Ruta del modelo base
            config_path (str): Ruta de configuración
        """
        self.logger = logging.getLogger(__name__)

        # Cargar modelo de embeddings
        self.tokenizer = AutoTokenizer.from_pretrained(base_model_path)
        self.embedding_model = AutoModel.from_pretrained(base_model_path)

        # Configuración de adaptación
        self.adaptation_config = {
            "clustering_eps": 0.5,
            "clustering_min_samples": 3,
            "similarity_threshold": 0.75,
        }

        # Almacén de dominios y sus características
        self.domain_knowledge_base: Dict[str, Dict[str, Any]] = {}

    def generate_domain_embedding(self, text: str) -> np.ndarray:
        """
        Generar embedding semántico para un texto

        Args:
            text (str): Texto para generar embedding

        Returns:
            Embedding semántico del texto
        """
        # Tokenizar y generar embedding
        inputs = self.tokenizer(
            text, return_tensors="pt", truncation=True, max_length=512
        )

        with torch.no_grad():
            outputs = self.embedding_model(**inputs)
            embedding = outputs.last_hidden_state.mean(dim=1).squeeze().numpy()

        return embedding

    def cluster_semantic_domains(self, texts: List[str]) -> Dict[int, List[str]]:
        """
        Agrupar textos en dominios semánticos

        Args:
            texts (List[str]): Lista de textos para agrupar

        Returns:
            Diccionario de clusters con sus textos
        """
        # Generar embeddings
        embeddings = np.array([self.generate_domain_embedding(text) for text in texts])

        # Clustering con DBSCAN
        clustering = DBSCAN(
            eps=self.adaptation_config["clustering_eps"],
            min_samples=self.adaptation_config["clustering_min_samples"],
        ).fit(embeddings)

        # Organizar resultados por cluster
        clustered_domains = {}
        for idx, cluster_label in enumerate(clustering.labels_):
            if cluster_label not in clustered_domains:
                clustered_domains[cluster_label] = []
            clustered_domains[cluster_label].append(texts[idx])

        return clustered_domains

    def adapt_semantic_context(
        self, query: str, domain_contexts: Dict[str, List[str]]
    ) -> str:
        """
        Adaptar consulta al contexto semántico más apropiado

        Args:
            query (str): Consulta original
            domain_contexts (dict): Contextos de diferentes dominios

        Returns:
            Consulta adaptada al dominio más relevante
        """
        # Generar embedding de la consulta
        query_embedding = self.generate_domain_embedding(query)

        # Encontrar dominio más similar
        best_domain = None
        max_similarity = 0

        for domain, context_texts in domain_contexts.items():
            domain_embeddings = [
                self.generate_domain_embedding(text) for text in context_texts
            ]

            # Calcular similitud promedio
            avg_similarity = np.mean(
                [
                    np.dot(query_embedding, domain_emb)
                    / (np.linalg.norm(query_embedding) * np.linalg.norm(domain_emb))
                    for domain_emb in domain_embeddings
                ]
            )

            if avg_similarity > max_similarity:
                max_similarity = avg_similarity
                best_domain = domain

        # Si la similitud supera el umbral, adaptar consulta
        if max_similarity >= self.adaptation_config["similarity_threshold"]:
            adapted_query = f"[{best_domain}] {query}"
            return adapted_query

        return query

    def update_domain_knowledge(self, domain: str, new_knowledge: List[str]):
        """
        Actualizar conocimiento de un dominio

        Args:
            domain (str): Dominio a actualizar
            new_knowledge (List[str]): Nuevo conocimiento
        """
        if domain not in self.domain_knowledge_base:
            self.domain_knowledge_base[domain] = {
                "texts": [],
                "last_updated": datetime.now(),
            }

        # Agregar nuevos textos
        self.domain_knowledge_base[domain]["texts"].extend(new_knowledge)
        self.domain_knowledge_base[domain]["last_updated"] = datetime.now()
