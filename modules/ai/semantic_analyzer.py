"""
Análisis Semántico - Semantic Analyzer
======================================

Componentes para análisis semántico y comprensión de significado.
"""

import logging
from typing import List, Dict, Any, Optional, Tuple
from dataclasses import dataclass
import numpy as np
from sentence_transformers import SentenceTransformer, util
import torch

logger = logging.getLogger(__name__)


@dataclass
class SemanticSimilarity:
    """Resultado de similitud semántica"""

    score: float
    confidence: float
    explanation: str


@dataclass
class SemanticAnalysis:
    """Resultado del análisis semántico"""

    main_topics: List[str]
    semantic_clusters: List[List[str]]
    key_concepts: List[str]
    context_understanding: Dict[str, Any]
    semantic_similarity: Dict[str, float]


class SemanticAnalyzer:
    """Analizador semántico principal"""

    def __init__(self, model_name: str = "paraphrase-multilingual-MiniLM-L12-v2"):
        self.model_name = model_name
        self.model = None
        self._load_model()

    def _load_model(self):
        """Carga el modelo de embeddings"""
        try:
            logger.info(f"🔄 Cargando modelo semántico: {self.model_name}")
            self.model = SentenceTransformer(self.model_name)
            logger.info(f"✅ Modelo semántico {self.model_name} cargado exitosamente")
        except Exception as e:
            logger.error(f"❌ Error cargando modelo semántico: {e}")
            self.model = None

    def get_embeddings(self, texts: List[str]) -> np.ndarray:
        """Obtiene embeddings para una lista de textos"""
        if not self.model:
            logger.warning("⚠️ Modelo no disponible, usando embeddings aleatorios")
            return np.random.rand(len(texts), 384)  # Dimensión típica

        try:
            embeddings = self.model.encode(texts, convert_to_tensor=True)
            return embeddings.cpu().numpy()
        except Exception as e:
            logger.error(f"❌ Error generando embeddings: {e}")
            return np.random.rand(len(texts), 384)

    def calculate_similarity(self, text1: str, text2: str) -> float:
        """Calcula similitud semántica entre dos textos"""
        if not self.model:
            return 0.0

        try:
            embeddings = self.model.encode([text1, text2], convert_to_tensor=True)
            similarity = util.pytorch_cos_sim(embeddings[0], embeddings[1])
            return float(similarity[0][0])
        except Exception as e:
            logger.error(f"❌ Error calculando similitud: {e}")
            return 0.0

    def find_similar_texts(
        self, query: str, texts: List[str], threshold: float = 0.5
    ) -> List[Tuple[int, float]]:
        """Encuentra textos similares a una consulta"""
        if not self.model or not texts:
            return []

        try:
            query_embedding = self.model.encode(query, convert_to_tensor=True)
            text_embeddings = self.model.encode(texts, convert_to_tensor=True)

            similarities = util.pytorch_cos_sim(query_embedding, text_embeddings)[0]

            similar_texts = []
            for i, similarity in enumerate(similarities):
                if similarity > threshold:
                    similar_texts.append((i, float(similarity)))

            # Ordenar por similitud descendente
            similar_texts.sort(key=lambda x: x[1], reverse=True)
            return similar_texts

        except Exception as e:
            logger.error(f"❌ Error buscando textos similares: {e}")
            return []

    def cluster_texts(self, texts: List[str], n_clusters: int = 3) -> List[List[int]]:
        """Agrupa textos por similitud semántica"""
        if not self.model or len(texts) < n_clusters:
            return []

        try:
            embeddings = self.model.encode(texts, convert_to_tensor=True)

            # Calcular matriz de similitud
            similarity_matrix = util.pytorch_cos_sim(embeddings, embeddings)

            # Clustering simple basado en similitud
            clusters = []
            used_indices = set()

            for _ in range(n_clusters):
                if len(used_indices) >= len(texts):
                    break

                # Encontrar el texto más similar a los no usados
                best_cluster = []
                best_similarity = -1

                for i in range(len(texts)):
                    if i in used_indices:
                        continue

                    cluster_similarity = 0
                    cluster_members = [i]

                    for j in range(len(texts)):
                        if j != i and j not in used_indices:
                            sim = similarity_matrix[i][j]
                            if sim > 0.7:  # Umbral de similitud
                                cluster_members.append(j)
                                cluster_similarity += sim

                    if cluster_similarity > best_similarity:
                        best_similarity = cluster_similarity
                        best_cluster = cluster_members

                if best_cluster:
                    clusters.append(best_cluster)
                    used_indices.update(best_cluster)

            return clusters

        except Exception as e:
            logger.error(f"❌ Error en clustering: {e}")
            return []

    def extract_key_concepts(self, text: str, max_concepts: int = 10) -> List[str]:
        """Extrae conceptos clave del texto"""
        if not text:
            return []

        # Dividir en oraciones
        sentences = text.split(".")
        sentences = [s.strip() for s in sentences if s.strip()]

        if not sentences:
            return []

        try:
            # Obtener embeddings de oraciones
            embeddings = self.model.encode(sentences, convert_to_tensor=True)

            # Calcular similitud entre oraciones
            similarity_matrix = util.pytorch_cos_sim(embeddings, embeddings)

            # Encontrar oraciones más representativas
            sentence_scores = []
            for i in range(len(sentences)):
                score = torch.mean(similarity_matrix[i]).item()
                sentence_scores.append((i, score))

            # Ordenar por score y tomar las mejores
            sentence_scores.sort(key=lambda x: x[1], reverse=True)
            top_sentences = sentence_scores[:max_concepts]

            # Extraer palabras clave de las mejores oraciones
            concepts = []
            for idx, _ in top_sentences:
                sentence = sentences[idx]
                words = sentence.split()
                # Filtrar palabras largas (probablemente conceptos importantes)
                important_words = [w for w in words if len(w) > 4]
                concepts.extend(important_words[:3])  # Máximo 3 por oración

            return list(set(concepts))[:max_concepts]

        except Exception as e:
            logger.error(f"❌ Error extrayendo conceptos: {e}")
            return []

    def understand_context(
        self, text: str, context_texts: List[str] = None
    ) -> Dict[str, Any]:
        """Analiza el contexto del texto"""
        if not text:
            return {}

        analysis = {
            "main_theme": "",
            "context_relevance": 0.0,
            "semantic_coherence": 0.0,
            "topic_consistency": 0.0,
        }

        try:
            # Análisis básico del tema principal
            sentences = text.split(".")
            if sentences:
                # Usar la primera oración como tema principal
                analysis["main_theme"] = sentences[0].strip()

            # Calcular coherencia semántica
            if len(sentences) > 1:
                embeddings = self.model.encode(sentences, convert_to_tensor=True)
                similarities = []
                for i in range(len(sentences) - 1):
                    sim = util.pytorch_cos_sim(embeddings[i], embeddings[i + 1])
                    similarities.append(float(sim[0][0]))

                if similarities:
                    analysis["semantic_coherence"] = np.mean(similarities)

            # Análisis de relevancia con contexto
            if context_texts:
                text_embedding = self.model.encode(text, convert_to_tensor=True)
                context_embeddings = self.model.encode(
                    context_texts, convert_to_tensor=True
                )

                similarities = util.pytorch_cos_sim(text_embedding, context_embeddings)[
                    0
                ]
                analysis["context_relevance"] = float(torch.mean(similarities))

            return analysis

        except Exception as e:
            logger.error(f"❌ Error analizando contexto: {e}")
            return analysis

    def analyze_semantics(
        self, text: str, context_texts: List[str] = None
    ) -> SemanticAnalysis:
        """Realiza análisis semántico completo"""
        if not text:
            return SemanticAnalysis([], [], [], {}, {})

        try:
            # Extraer conceptos clave
            key_concepts = self.extract_key_concepts(text)

            # Identificar temas principales
            main_topics = key_concepts[:3] if key_concepts else []

            # Clustering de oraciones
            sentences = text.split(".")
            sentences = [s.strip() for s in sentences if s.strip()]
            clusters = self.cluster_texts(sentences, min(3, len(sentences)))

            semantic_clusters = []
            for cluster in clusters:
                cluster_texts = [sentences[i] for i in cluster if i < len(sentences)]
                semantic_clusters.append(cluster_texts)

            # Análisis de contexto
            context_understanding = self.understand_context(text, context_texts)

            # Similitud semántica con conceptos clave
            semantic_similarity = {}
            if key_concepts:
                for concept in key_concepts[:5]:
                    similarity = self.calculate_similarity(text, concept)
                    semantic_similarity[concept] = similarity

            return SemanticAnalysis(
                main_topics=main_topics,
                semantic_clusters=semantic_clusters,
                key_concepts=key_concepts,
                context_understanding=context_understanding,
                semantic_similarity=semantic_similarity,
            )

        except Exception as e:
            logger.error(f"❌ Error en análisis semántico: {e}")
            return SemanticAnalysis([], [], [], {}, {})

    def semantic_search(
        self, query: str, documents: List[str], top_k: int = 5
    ) -> List[Tuple[int, float]]:
        """Búsqueda semántica en documentos"""
        if not self.model or not documents:
            return []

        try:
            query_embedding = self.model.encode(query, convert_to_tensor=True)
            doc_embeddings = self.model.encode(documents, convert_to_tensor=True)

            similarities = util.pytorch_cos_sim(query_embedding, doc_embeddings)[0]

            # Obtener top-k resultados
            top_results = []
            for i, similarity in enumerate(similarities):
                top_results.append((i, float(similarity)))

            top_results.sort(key=lambda x: x[1], reverse=True)
            return top_results[:top_k]

        except Exception as e:
            logger.error(f"❌ Error en búsqueda semántica: {e}")
            return []
