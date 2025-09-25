import logging
from dataclasses import dataclass, field
from typing import Dict, Any, Optional, List
import numpy as np
import difflib
import time

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@dataclass
class QualityEvaluationConfig:
    """Configuración unificada para evaluación de calidad"""

    similarity_threshold: float = 0.6
    toxicity_threshold: float = 0.1
    hallucination_threshold: float = 0.3
    keyword_coverage_threshold: float = 0.7


class UnifiedQualityEvaluator:
    """Evaluador de calidad unificado con múltiples métricas"""

    def __init__(self, config: QualityEvaluationConfig = None):
        self.config = config or QualityEvaluationConfig()
        self.evaluation_history: List[Dict[str, Any]] = []

    def evaluate_response(
        self,
        query: str,
        response: str,
        reference: Optional[str] = None,
        context: Optional[str] = None,
        domain: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Evaluar calidad de respuesta con métricas múltiples"""
        start_time = time.time()

        metrics = {
            "similarity": (
                self._calculate_similarity(response, reference) if reference else 1.0
            ),
            "toxicity": self._detect_toxicity(response),
            "hallucination": (
                self._detect_hallucination(response, context) if context else 0.0
            ),
            "keyword_coverage": self._calculate_keyword_coverage(query, response),
            "response_length": len(response.split()),
        }

        quality_score = self._calculate_quality_score(metrics)

        evaluation_result = {
            "query": query,
            "response": response,
            "reference": reference,
            "context": context,
            "domain": domain or "General",
            "metrics": metrics,
            "quality_score": quality_score,
            "processing_time": time.time() - start_time,
        }

        self.evaluation_history.append(evaluation_result)
        return evaluation_result

    def _calculate_similarity(self, response: str, reference: str) -> float:
        """Calcular similitud entre respuesta y referencia"""
        return difflib.SequenceMatcher(None, response, reference).ratio()

    def _detect_toxicity(self, text: str) -> float:
        """Detectar toxicidad en el texto"""
        toxic_words = [
            "odio",
            "muerte",
            "matar",
            "violencia",
            "estúpido",
            "idiota",
            "imbécil",
        ]

        words = text.lower().split()
        toxic_count = sum(1 for word in words if word in toxic_words)

        return min(toxic_count / len(words), 1.0)

    def _detect_hallucination(self, response: str, context: str) -> float:
        """Detectar alucinaciones comparando con contexto"""
        similarity = difflib.SequenceMatcher(None, response, context).ratio()
        return 1.0 - similarity

    def _calculate_keyword_coverage(self, query: str, response: str) -> float:
        """Calcular cobertura de palabras clave"""
        query_words = set(query.lower().split())
        response_words = set(response.lower().split())

        common_words = query_words.intersection(response_words)
        return len(common_words) / len(query_words) if query_words else 1.0

    def _calculate_quality_score(self, metrics: Dict[str, float]) -> float:
        """Calcular puntuación de calidad"""
        weights = {
            "similarity": 0.3,
            "toxicity": -0.2,
            "hallucination": -0.2,
            "keyword_coverage": 0.2,
            "response_length": 0.1,
        }

        quality_score = sum(
            metrics.get(metric, 0) * weight for metric, weight in weights.items()
        )

        return max(min(quality_score, 1.0), 0.0)

    def get_evaluation_summary(self) -> Dict[str, Any]:
        """Obtener resumen de evaluaciones"""
        if not self.evaluation_history:
            return {"message": "No hay evaluaciones disponibles"}

        domain_stats = {}
        for result in self.evaluation_history:
            domain = result["domain"]
            if domain not in domain_stats:
                domain_stats[domain] = {
                    "count": 0,
                    "avg_quality": 0.0,
                    "total_processing_time": 0.0,
                }

            domain_stats[domain]["count"] += 1
            domain_stats[domain]["avg_quality"] += result["quality_score"]
            domain_stats[domain]["total_processing_time"] += result["processing_time"]

        # Calcular promedios
        for domain in domain_stats:
            stats = domain_stats[domain]
            stats["avg_quality"] /= stats["count"]
            stats["avg_processing_time"] = (
                stats["total_processing_time"] / stats["count"]
            )

        return {
            "total_evaluations": len(self.evaluation_history),
            "domain_statistics": domain_stats,
        }


def main():
    """Demostración del evaluador de calidad unificado"""
    evaluator = UnifiedQualityEvaluator()

    # Ejemplos de evaluación con diferentes dominios
    test_cases = [
        {
            "query": "Análisis sintáctico del español",
            "response": "El análisis sintáctico estudia la estructura gramatical de las oraciones, identificando sujetos, predicados y complementos.",
            "reference": "La sintaxis analiza cómo se organizan las palabras y frases en una oración para formar estructuras gramaticales significativas.",
            "context": "Lingüística descriptiva",
            "domain": "Lingüística",
        },
        {
            "query": "Teorema de Pitágoras",
            "response": "En un triángulo rectángulo, el cuadrado de la hipotenusa es igual a la suma de los cuadrados de los catetos.",
            "reference": "El teorema de Pitágoras establece que a² + b² = c², donde c es la hipotenusa y a, b son los catetos.",
            "domain": "Matemáticas",
        },
        {
            "query": "Ejemplo de evaluación genérica",
            "response": "Esta es una respuesta de ejemplo para demostrar la flexibilidad del evaluador de calidad.",
            "domain": "General",
        },
    ]

    for case in test_cases:
        result = evaluator.evaluate_response(**case)
        print("Resultado de Evaluación:")
        print(f"Consulta: {result['query']}")
        print(f"Respuesta: {result['response']}")
        print(f"Dominio: {result['domain']}")
        print(f"Puntuación de Calidad: {result['quality_score']:.3f}")
        print("Métricas:")
        for metric, value in result["metrics"].items():
            print(f"  - {metric}: {value:.3f}")
        print()

    # Resumen de evaluaciones
    summary = evaluator.get_evaluation_summary()
    print("Resumen de Evaluaciones:")
    print(summary)


if __name__ == "__main__":
    main()
