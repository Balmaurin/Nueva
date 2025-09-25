"""
Evaluador de Calidad para Ejercicios de IA
Sistema inteligente que evalúa la calidad de respuestas y determina su valor para datasets
"""

import re
import nltk
from typing import Dict, Any, List, Tuple
from datetime import datetime
import logging
from collections import Counter

logger = logging.getLogger(__name__)


class QualityEvaluator:
    """
    Evaluador inteligente de calidad para respuestas de ejercicios de IA
    """

    def __init__(self):
        self.min_length = 50
        self.max_length = 5000

        # Criterios de evaluación
        self.criteria_weights = {
            "length_appropriate": 0.15,
            "vocabulary_richness": 0.20,
            "grammar_correctness": 0.15,
            "content_relevance": 0.25,
            "creativity_originality": 0.15,
            "structure_coherence": 0.10,
        }

        # Palabras de baja calidad (frecuentes pero poco informativas)
        self.low_quality_words = {
            "el",
            "la",
            "los",
            "las",
            "un",
            "una",
            "unos",
            "unas",
            "y",
            "o",
            "pero",
            "que",
            "de",
            "en",
            "a",
            "por",
            "para",
            "con",
            "sin",
            "sobre",
            "entre",
            "hasta",
            "desde",
            "durante",
            "es",
            "son",
            "era",
            "eran",
            "fue",
            "fueron",
            "ser",
            "estar",
            "tener",
            "hacer",
            "ir",
            "ver",
            "dar",
            "saber",
            "querer",
            "llegar",
            "pasar",
            "deber",
            "poner",
            "parecer",
            "quedar",
            "creer",
            "hablar",
            "llevar",
            "dejar",
            "seguir",
            "encontrar",
            "llamar",
            "venir",
            "pensar",
            "salir",
            "volver",
            "tomar",
            "conocer",
            "vivir",
            "sentir",
            "tratar",
            "mirar",
            "contar",
            "empezar",
            "esperar",
            "buscar",
            "existir",
            "entrar",
            "trabajar",
            "escribir",
            "perder",
            "producir",
            "ocurrir",
            "entender",
            "pedir",
            "recibir",
            "recordar",
            "terminar",
            "permitir",
            "aparecer",
            "conseguir",
            "comenzar",
            "servir",
            "sacar",
            "necesitar",
            "mantener",
            "resultar",
            "leer",
            "caer",
            "cambiar",
            "presentar",
            "crear",
            "abrir",
            "considerar",
            "oír",
            "acabar",
            "convertir",
            "ganar",
            "formar",
            "traer",
            "partir",
            "morir",
            "aceptar",
            "realizar",
            "suponer",
            "comprender",
            "lograr",
            "explicar",
            "preguntar",
            "tocar",
            "reconocer",
            "estudiar",
            "alcanzar",
            "nacer",
            "dirigir",
            "correr",
            "utilizar",
            "pagar",
            "ayudar",
            "gustar",
        }

    def evaluate_response(
        self, response: str, exercise_config: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Evalúa la calidad de una respuesta completa

        Args:
            response: La respuesta del usuario
            exercise_config: Configuración del ejercicio

        Returns:
            Dict con score, feedback y metadata
        """
        try:
            # Preprocesamiento
            cleaned_response = self._preprocess_text(response)

            # Evaluación de criterios individuales
            scores = {
                "length_appropriate": self._evaluate_length(
                    cleaned_response, exercise_config
                ),
                "vocabulary_richness": self._evaluate_vocabulary(cleaned_response),
                "grammar_correctness": self._evaluate_grammar(cleaned_response),
                "content_relevance": self._evaluate_relevance(
                    cleaned_response, exercise_config
                ),
                "creativity_originality": self._evaluate_creativity(cleaned_response),
                "structure_coherence": self._evaluate_structure(cleaned_response),
            }

            # Calcular score final ponderado
            final_score = sum(
                scores[criterion] * self.criteria_weights[criterion]
                for criterion in scores
            )

            # Redondear a entero
            final_score = round(final_score)

            # Generar feedback
            feedback = self._generate_feedback(scores, exercise_config)

            # Determinar si califica para dataset
            qualifies_for_dataset = final_score >= exercise_config.get(
                "minQualityScore", 90
            )

            # Calcular tokens a otorgar
            tokens_earned = (
                exercise_config.get("datasetValue", 10) if qualifies_for_dataset else 0
            )

            return {
                "qualityScore": final_score,
                "scores": scores,
                "feedback": feedback,
                "qualifiesForDataset": qualifies_for_dataset,
                "tokensEarned": tokens_earned,
                "evaluationTimestamp": datetime.now().isoformat(),
                "metadata": {
                    "responseLength": len(cleaned_response),
                    "wordCount": len(cleaned_response.split()),
                    "sentenceCount": len(re.split(r"[.!?]+", cleaned_response.strip())),
                    "criteriaEvaluated": len(scores),
                },
            }

        except Exception as e:
            logger.error(f"Error evaluando respuesta: {e}")
            return {
                "qualityScore": 0,
                "scores": {},
                "feedback": "Error en la evaluación automática. Respuesta será revisada manualmente.",
                "qualifiesForDataset": False,
                "tokensEarned": 0,
                "evaluationTimestamp": datetime.now().isoformat(),
                "error": str(e),
            }

    def _preprocess_text(self, text: str) -> str:
        """Preprocesa el texto para evaluación"""
        # Convertir a minúsculas
        text = text.lower()

        # Remover caracteres especiales pero mantener puntuación básica
        text = re.sub(r"[^\w\s.,!?;:-]", "", text)

        # Normalizar espacios
        text = re.sub(r"\s+", " ", text).strip()

        return text

    def _evaluate_length(self, response: str, config: Dict[str, Any]) -> float:
        """Evalúa si la longitud es apropiada"""
        length = len(response)
        max_length = config.get("maxLength", 500)

        if length < self.min_length:
            return 20  # Muy corta
        elif length > max_length * 1.2:
            return 60  # Demasiado larga
        elif length > max_length:
            return 80  # Un poco larga pero aceptable
        elif length >= max_length * 0.8:
            return 100  # Longitud ideal
        else:
            return 85  # Longitud aceptable

    def _evaluate_vocabulary(self, response: str) -> float:
        """Evalúa la riqueza del vocabulario"""
        words = re.findall(r"\b\w+\b", response.lower())
        if not words:
            return 0

        # Contar palabras únicas vs total
        unique_words = set(words)
        uniqueness_ratio = len(unique_words) / len(words)

        # Penalizar uso excesivo de palabras de baja calidad
        low_quality_count = sum(1 for word in words if word in self.low_quality_words)
        low_quality_ratio = low_quality_count / len(words)

        # Puntaje basado en diversidad y calidad
        diversity_score = min(100, uniqueness_ratio * 150)  # Máximo 100
        quality_score = max(0, 100 - (low_quality_ratio * 200))  # Penalización

        return (diversity_score + quality_score) / 2

    def _evaluate_grammar(self, response: str) -> float:
        """Evalúa la corrección gramatical básica"""
        score = 100

        # Penalizaciones por errores comunes
        sentences = re.split(r"[.!?]+", response.strip())

        for sentence in sentences:
            sentence = sentence.strip()
            if not sentence:
                continue

            # Primera letra mayúscula
            if sentence and not sentence[0].isupper():
                score -= 5

            # Evitar frases demasiado cortas (1-2 palabras)
            words_in_sentence = len(sentence.split())
            if words_in_sentence <= 2:
                score -= 3

        # Penalización por uso excesivo de mayúsculas
        uppercase_ratio = (
            sum(1 for c in response if c.isupper()) / len(response) if response else 0
        )
        if uppercase_ratio > 0.3:
            score -= 20

        return max(0, score)

    def _evaluate_relevance(self, response: str, config: Dict[str, Any]) -> float:
        """Evalúa la relevancia del contenido (básica)"""
        # Análisis básico basado en palabras clave del ejercicio
        exercise_title = config.get("title", "").lower()
        exercise_description = config.get("description", "").lower()

        # Extraer palabras clave del ejercicio
        keywords = set()
        for text in [exercise_title, exercise_description]:
            words = re.findall(r"\b\w+\b", text)
            keywords.update(words)

        # Contar coincidencias en la respuesta
        response_words = set(re.findall(r"\b\w+\b", response.lower()))
        matches = len(keywords.intersection(response_words))

        # Calcular ratio de relevancia
        if not keywords:
            return 80  # Sin keywords específicas, asumir relevancia moderada

        relevance_ratio = matches / len(keywords)
        return min(100, relevance_ratio * 150)

    def _evaluate_creativity(self, response: str) -> float:
        """Evalúa creatividad y originalidad"""
        # Análisis de diversidad de estructuras
        sentences = re.split(r"[.!?]+", response.strip())

        if len(sentences) < 2:
            return 50  # Respuesta muy corta

        # Analizar longitud de oraciones
        sentence_lengths = [len(s.split()) for s in sentences if s.strip()]

        if not sentence_lengths:
            return 0

        # Variabilidad en longitud de oraciones (creatividad en estructura)
        avg_length = sum(sentence_lengths) / len(sentence_lengths)
        variance = sum((length - avg_length) ** 2 for length in sentence_lengths) / len(
            sentence_lengths
        )
        variability_score = min(100, variance * 2)  # Máximo 100

        # Presencia de conectores lógicos (y, pero, porque, aunque, etc.)
        connectors = [
            "y",
            "pero",
            "porque",
            "aunque",
            "sin embargo",
            "además",
            "también",
            "entonces",
            "por lo tanto",
            "es decir",
            "o sea",
            "es decir",
        ]

        connector_count = sum(
            1 for word in re.findall(r"\b\w+\b", response.lower()) if word in connectors
        )

        connector_score = min(100, connector_count * 10)

        return (variability_score + connector_score) / 2

    def _evaluate_structure(self, response: str) -> float:
        """Evalúa la estructura y coherencia"""
        sentences = re.split(r"[.!?]+", response.strip())

        if len(sentences) < 2:
            return 30  # Muy poca estructura

        score = 100

        # Penalizar oraciones demasiado largas (>50 palabras)
        for sentence in sentences:
            words = sentence.split()
            if len(words) > 50:
                score -= 10

        # Bonificación por párrafos (si hay saltos de línea)
        if "\n" in response:
            score += 10

        # Verificar puntuación al final
        last_sentence = sentences[-1].strip()
        if last_sentence and not last_sentence.endswith((".", "!", "?", ":")):
            score -= 5

        return max(0, score)

    def _generate_feedback(
        self, scores: Dict[str, float], config: Dict[str, Any]
    ) -> str:
        """Genera feedback constructivo basado en los scores"""
        feedback_parts = []

        # Feedback por criterio
        if scores.get("length_appropriate", 0) < 70:
            feedback_parts.append(
                "Considera expandir tu respuesta para proporcionar más detalle."
            )

        if scores.get("vocabulary_richness", 0) < 70:
            feedback_parts.append(
                "Intenta usar un vocabulario más variado y específico."
            )

        if scores.get("grammar_correctness", 0) < 80:
            feedback_parts.append("Revisa la gramática y estructura de tus oraciones.")

        if scores.get("content_relevance", 0) < 70:
            feedback_parts.append(
                "Asegúrate de que tu respuesta sea relevante para el ejercicio solicitado."
            )

        if scores.get("creativity_originality", 0) < 70:
            feedback_parts.append(
                "Agrega más creatividad y ejemplos originales a tu respuesta."
            )

        if scores.get("structure_coherence", 0) < 70:
            feedback_parts.append(
                "Mejora la estructura y organización de tu respuesta."
            )

        # Si todo está bien
        if not feedback_parts and all(score >= 80 for score in scores.values()):
            feedback_parts.append(
                "¡Excelente respuesta! Muestra creatividad y cumple con todos los criterios."
            )

        return " ".join(feedback_parts)


# Instancia global del evaluador
quality_evaluator = QualityEvaluator()
