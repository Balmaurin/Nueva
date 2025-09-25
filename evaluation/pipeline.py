import numpy as np
from typing import Dict, Any, List
from .coherence import CoherenceEvaluator
from .diversity import DiversityEvaluator
from .toxicity import ToxicityEvaluator
import logging
import json
import os
from datetime import datetime


class QualityEvaluationPipeline:
    def __init__(
        self,
        log_dir: str = "logs/quality_evaluation",
        coherence_weight: float = 0.4,
        diversity_weight: float = 0.3,
        toxicity_weight: float = 0.3,
        coherence_threshold: float = 0.6,
        diversity_threshold: float = 0.5,
        toxicity_threshold: float = 0.3,
    ):
        """
        Inicializar pipeline de evaluación de calidad

        Args:
            log_dir: Directorio para guardar logs de evaluación
            coherence_weight: Peso de la coherencia
            diversity_weight: Peso de la diversidad
            toxicity_weight: Peso de la toxicidad
            coherence_threshold: Umbral de coherencia
            diversity_threshold: Umbral de diversidad
            toxicity_threshold: Umbral de toxicidad
        """
        # Inicializar evaluadores
        self.coherence_evaluator = CoherenceEvaluator()
        self.diversity_evaluator = DiversityEvaluator()
        self.toxicity_evaluator = ToxicityEvaluator()

        # Configurar pesos y umbrales
        self.weights = {
            "coherence": coherence_weight,
            "diversity": diversity_weight,
            "toxicity": toxicity_weight,
        }

        self.thresholds = {
            "coherence": coherence_threshold,
            "diversity": diversity_threshold,
            "toxicity": toxicity_threshold,
        }

        # Configurar logging
        os.makedirs(log_dir, exist_ok=True)
        self.log_dir = log_dir

        # Configurar logger
        logging.basicConfig(
            level=logging.INFO,
            format="%(asctime)s - %(levelname)s: %(message)s",
            handlers=[
                logging.FileHandler(f"{log_dir}/quality_evaluation.log"),
                logging.StreamHandler(),
            ],
        )
        self.logger = logging.getLogger(__name__)

    def _log_evaluation(
        self, query: str, response: str, evaluation_result: Dict[str, Any]
    ):
        """
        Registrar resultados de evaluación

        Args:
            query: Consulta original
            response: Respuesta generada
            evaluation_result: Resultados de evaluación
        """
        log_entry = {
            "timestamp": datetime.now().isoformat(),
            "query": query,
            "response": response,
            "evaluation": evaluation_result,
        }

        # Guardar log en archivo JSON
        log_filename = (
            f"{self.log_dir}/evaluation_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        )
        with open(log_filename, "w", encoding="utf-8") as f:
            json.dump(log_entry, f, ensure_ascii=False, indent=2)

    def evaluate_response(
        self, query: str, response: str, domain: str = None
    ) -> Dict[str, Any]:
        """
        Evaluar calidad de una respuesta

        Args:
            query: Consulta original
            response: Respuesta generada
            domain: Dominio opcional

        Returns:
            Diccionario con métricas de calidad
        """
        # Evaluar coherencia
        coherence_metrics = self.coherence_evaluator.calculate_coherence(
            query, response
        )

        # Evaluar diversidad
        diversity_metrics = self.diversity_evaluator.evaluate_diversity(response)

        # Evaluar toxicidad
        toxicity_metrics = self.toxicity_evaluator.evaluate_toxicity(response)

        # Calcular puntuaciones normalizadas
        coherence_score = coherence_metrics
        diversity_score = diversity_metrics["diversity_score"]
        toxicity_score = (
            1 - toxicity_metrics["toxicity_score"]
        )  # Invertir para que 1 sea bueno

        # Calcular puntuación compuesta
        composite_score = (
            self.weights["coherence"] * coherence_score
            + self.weights["diversity"] * diversity_score
            + self.weights["toxicity"] * toxicity_score
        )

        # Verificar umbrales
        passes_quality = all(
            [
                coherence_score >= self.thresholds["coherence"],
                diversity_score >= self.thresholds["diversity"],
                toxicity_score >= self.thresholds["toxicity"],
            ]
        )

        # Preparar resultado de evaluación
        evaluation_result = {
            "composite_score": composite_score,
            "passes_quality": passes_quality,
            "metrics": {
                "coherence": {
                    "score": coherence_score,
                    "passes_threshold": coherence_score >= self.thresholds["coherence"],
                },
                "diversity": {
                    "score": diversity_score,
                    "passes_threshold": diversity_score >= self.thresholds["diversity"],
                },
                "toxicity": {
                    "score": toxicity_score,
                    "passes_threshold": toxicity_score >= self.thresholds["toxicity"],
                },
            },
            "domain": domain,
        }

        # Registrar evaluación
        self._log_evaluation(query, response, evaluation_result)

        # Registrar métricas en log
        self.logger.info(f"Evaluación de respuesta - Dominio: {domain}")
        self.logger.info(f"Puntuación compuesta: {composite_score}")
        self.logger.info(f"Pasa calidad: {passes_quality}")

        return evaluation_result

    def evaluate_conversation(
        self, conversation: List[Dict], domain: str = None
    ) -> Dict[str, Any]:
        """
        Evaluar calidad de una conversación completa

        Args:
            conversation: Lista de mensajes con 'role' y 'content'
            domain: Dominio opcional

        Returns:
            Diccionario con métricas de calidad de la conversación
        """
        # Filtrar mensajes de usuario y asistente
        user_messages = [
            msg["content"] for msg in conversation if msg["role"] == "user"
        ]
        assistant_messages = [
            msg["content"] for msg in conversation if msg["role"] == "assistant"
        ]

        # Evaluar cada par de mensajes
        response_evaluations = []
        for query, response in zip(user_messages, assistant_messages):
            evaluation = self.evaluate_response(query, response, domain)
            response_evaluations.append(evaluation)

        # Calcular métricas agregadas
        composite_scores = [eval["composite_score"] for eval in response_evaluations]
        passes_quality = all(eval["passes_quality"] for eval in response_evaluations)

        # Preparar resultado de evaluación de conversación
        conversation_evaluation = {
            "mean_composite_score": np.mean(composite_scores),
            "min_composite_score": np.min(composite_scores),
            "max_composite_score": np.max(composite_scores),
            "passes_quality": passes_quality,
            "response_evaluations": response_evaluations,
            "domain": domain,
        }

        # Registrar métricas en log
        self.logger.info(f"Evaluación de conversación - Dominio: {domain}")
        self.logger.info(
            f"Puntuación compuesta promedio: {conversation_evaluation['mean_composite_score']}"
        )
        self.logger.info(f"Pasa calidad: {passes_quality}")

        return conversation_evaluation


def main():
    # Ejemplo de uso
    pipeline = QualityEvaluationPipeline()

    # Ejemplo de conversación
    conversation = [
        {"role": "user", "content": "¿Qué es la fotosíntesis?"},
        {
            "role": "assistant",
            "content": "La fotosíntesis es un proceso biológico donde las plantas transforman luz solar en energía química.",
        },
        {"role": "user", "content": "¿Cómo funciona exactamente?"},
        {
            "role": "assistant",
            "content": "En la fotosíntesis, las plantas utilizan clorofila para capturar energía solar, que luego convierten en glucosa a través de complejas reacciones metabólicas que ocurren en los cloroplastos, permitiendo la producción de oxígeno como subproducto esencial para la vida en el planeta.",
        },
    ]

    # Evaluar respuesta individual
    response_eval = pipeline.evaluate_response(
        conversation[0]["content"], conversation[1]["content"], domain="Biología"
    )
    print("Evaluación de Respuesta:")
    print(json.dumps(response_eval, indent=2, ensure_ascii=False))

    # Evaluar conversación completa
    conversation_eval = pipeline.evaluate_conversation(conversation, domain="Biología")
    print("\nEvaluación de Conversación:")
    print(json.dumps(conversation_eval, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
