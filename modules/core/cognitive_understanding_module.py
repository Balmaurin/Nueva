import logging
from typing import Dict, Any, List, Optional
import numpy as np
import torch
from transformers import AutoModelForSequenceClassification, AutoTokenizer
from sklearn.metrics.pairwise import cosine_similarity
from datetime import datetime


class CognitiveUnderstandingModule:
    def __init__(
        self,
        base_model_path: str = "models/custom/sheily-personal-model",
        config_path: str = "utils/cognitive_understanding_config.yaml",
    ):
        """
        Módulo de comprensión cognitiva con retroalimentación avanzada

        Args:
            base_model_path (str): Ruta del modelo base
            config_path (str): Ruta de configuración
        """
        self.logger = logging.getLogger(__name__)

        # Cargar modelo y tokenizador
        self.tokenizer = AutoTokenizer.from_pretrained(base_model_path)
        self.understanding_model = AutoModelForSequenceClassification.from_pretrained(
            base_model_path
        )

        # Configuración de comprensión
        self.understanding_config = {
            "complexity_threshold": 0.7,
            "coherence_weight": 0.4,
            "novelty_weight": 0.3,
            "depth_weight": 0.3,
        }

        # Almacén de contextos y retroalimentación
        self.cognitive_feedback_store: Dict[str, Dict[str, Any]] = {}

    def analyze_cognitive_complexity(self, text: str) -> Dict[str, float]:
        """
        Analizar la complejidad cognitiva de un texto

        Args:
            text (str): Texto para analizar

        Returns:
            Diccionario de métricas de complejidad
        """
        # Tokenizar texto
        inputs = self.tokenizer(
            text, return_tensors="pt", truncation=True, max_length=512
        )

        # Obtener representaciones internas
        with torch.no_grad():
            outputs = self.understanding_model(**inputs)
            hidden_states = outputs.hidden_states[-1].mean(dim=1)

        # Calcular métricas de complejidad
        complexity_metrics = {
            "linguistic_complexity": self._calculate_linguistic_complexity(text),
            "semantic_depth": self._calculate_semantic_depth(hidden_states),
            "information_density": self._calculate_information_density(text),
            "cognitive_load": self._estimate_cognitive_load(text),
        }

        return complexity_metrics

    def generate_cognitive_feedback(
        self, original_text: str, processed_text: str
    ) -> Dict[str, Any]:
        """
        Generar retroalimentación cognitiva comparativa

        Args:
            original_text (str): Texto original
            processed_text (str): Texto procesado

        Returns:
            Diccionario de retroalimentación cognitiva
        """
        # Analizar complejidad de textos
        original_complexity = self.analyze_cognitive_complexity(original_text)
        processed_complexity = self.analyze_cognitive_complexity(processed_text)

        # Calcular cambios en complejidad
        complexity_delta = {
            metric: processed_complexity[metric] - original_complexity[metric]
            for metric in original_complexity
        }

        # Generar retroalimentación
        feedback = {
            "complexity_changes": complexity_delta,
            "improvement_score": self._calculate_improvement_score(complexity_delta),
            "recommendations": self._generate_improvement_recommendations(
                complexity_delta
            ),
        }

        # Almacenar retroalimentación
        self._store_cognitive_feedback(original_text, feedback)

        return feedback

    def _calculate_linguistic_complexity(self, text: str) -> float:
        """
        Calcular complejidad lingüística

        Args:
            text (str): Texto para analizar

        Returns:
            Puntuación de complejidad lingüística
        """
        # Métricas de complejidad lingüística
        word_lengths = [len(word) for word in text.split()]
        avg_word_length = np.mean(word_lengths)
        sentence_lengths = [len(sentence.split()) for sentence in text.split(".")]
        avg_sentence_length = np.mean(sentence_lengths)

        return (avg_word_length + avg_sentence_length) / 2

    def _calculate_semantic_depth(self, hidden_states: torch.Tensor) -> float:
        """
        Calcular profundidad semántica

        Args:
            hidden_states (torch.Tensor): Estados ocultos del modelo

        Returns:
            Puntuación de profundidad semántica
        """
        # Calcular varianza de estados ocultos
        semantic_variance = torch.var(hidden_states, dim=0).mean().item()
        return semantic_variance

    def _calculate_information_density(self, text: str) -> float:
        """
        Calcular densidad de información

        Args:
            text (str): Texto para analizar

        Returns:
            Puntuación de densidad de información
        """
        # Contar palabras únicas vs total de palabras
        unique_words = set(text.split())
        total_words = len(text.split())

        return len(unique_words) / total_words if total_words > 0 else 0

    def _estimate_cognitive_load(self, text: str) -> float:
        """
        Estimar carga cognitiva

        Args:
            text (str): Texto para analizar

        Returns:
            Puntuación de carga cognitiva
        """
        # Calcular complejidad basada en estructura y vocabulario
        complexity_factors = [
            len(text.split()),  # Longitud total
            len(set(text.split())),  # Vocabulario único
            text.count("."),  # Número de oraciones
        ]

        return np.mean(complexity_factors)

    def _calculate_improvement_score(self, complexity_delta: Dict[str, float]) -> float:
        """
        Calcular puntuación de mejora

        Args:
            complexity_delta (dict): Cambios en métricas de complejidad

        Returns:
            Puntuación de mejora
        """
        weights = self.understanding_config

        improvement_score = sum(
            [
                delta * weights.get(f"{metric}_weight", 0.2)
                for metric, delta in complexity_delta.items()
            ]
        )

        return improvement_score

    def _generate_improvement_recommendations(
        self, complexity_delta: Dict[str, float]
    ) -> List[str]:
        """
        Generar recomendaciones de mejora

        Args:
            complexity_delta (dict): Cambios en métricas de complejidad

        Returns:
            Lista de recomendaciones
        """
        recommendations = []

        if complexity_delta.get("linguistic_complexity", 0) > 0:
            recommendations.append("Considera simplificar la estructura lingüística")

        if complexity_delta.get("semantic_depth", 0) < 0:
            recommendations.append(
                "Explora formas de aumentar la profundidad semántica"
            )

        if complexity_delta.get("information_density", 0) < 0:
            recommendations.append(
                "Busca formas de incrementar la densidad de información"
            )

        return recommendations

    def _store_cognitive_feedback(self, original_text: str, feedback: Dict[str, Any]):
        """
        Almacenar retroalimentación cognitiva

        Args:
            original_text (str): Texto original
            feedback (dict): Retroalimentación generada
        """
        text_hash = hash(original_text)
        self.cognitive_feedback_store[text_hash] = {
            "timestamp": datetime.now(),
            "feedback": feedback,
        }
