"""
Embedding Performance Monitor - Módulo de Monitoreo de Rendimiento de Embeddings
===============================================================================

Módulo para monitorear y analizar el rendimiento de sistemas de embeddings
en el contexto de NeuroFusion.
"""

import logging
import time
from typing import Dict, Any, List, Optional
import numpy as np
from dataclasses import dataclass, field
from datetime import datetime

logger = logging.getLogger(__name__)


@dataclass
class EmbeddingPerformanceMetrics:
    """
    Métricas detalladas de rendimiento para embeddings
    """

    model_name: str
    total_embeddings_generated: int = 0
    total_generation_time: float = 0.0
    avg_generation_time: float = 0.0
    max_generation_time: float = 0.0
    min_generation_time: float = float("inf")
    embedding_dimensions: Optional[int] = None
    timestamp: datetime = field(default_factory=datetime.now)


class EmbeddingPerformanceMonitor:
    """
    Monitor de rendimiento para sistemas de embeddings
    """

    def __init__(self, model_name: str):
        """
        Inicializar monitor de rendimiento de embeddings

        Args:
            model_name (str): Nombre del modelo de embeddings
        """
        self.metrics = EmbeddingPerformanceMetrics(model_name=model_name)
        self.performance_history: List[EmbeddingPerformanceMetrics] = []

    def track_embedding_generation(self, embedding: np.ndarray, generation_time: float):
        """
        Registrar métricas de generación de embedding

        Args:
            embedding (np.ndarray): Vector de embedding generado
            generation_time (float): Tiempo de generación en segundos
        """
        self.metrics.total_embeddings_generated += 1
        self.metrics.total_generation_time += generation_time
        self.metrics.avg_generation_time = (
            self.metrics.total_generation_time / self.metrics.total_embeddings_generated
        )

        # Actualizar tiempos extremos
        self.metrics.max_generation_time = max(
            self.metrics.max_generation_time, generation_time
        )
        self.metrics.min_generation_time = min(
            self.metrics.min_generation_time, generation_time
        )

        # Registrar dimensiones del embedding
        if self.metrics.embedding_dimensions is None:
            self.metrics.embedding_dimensions = embedding.shape[0]

    def generate_performance_report(self) -> Dict[str, Any]:
        """
        Generar informe de rendimiento de embeddings

        Returns:
            Diccionario con métricas de rendimiento
        """
        return {
            "model_name": self.metrics.model_name,
            "total_embeddings_generated": self.metrics.total_embeddings_generated,
            "avg_generation_time": round(self.metrics.avg_generation_time, 4),
            "max_generation_time": round(self.metrics.max_generation_time, 4),
            "min_generation_time": round(self.metrics.min_generation_time, 4),
            "embedding_dimensions": self.metrics.embedding_dimensions,
            "timestamp": self.metrics.timestamp.isoformat(),
        }

    def reset_metrics(self):
        """
        Reiniciar métricas y guardar historial
        """
        self.performance_history.append(self.metrics)
        self.metrics = EmbeddingPerformanceMetrics(model_name=self.metrics.model_name)

    def monitor_embedding_performance(
        self, text: str, model_name: str = "default"
    ) -> Dict[str, Any]:
        """
        Monitorear rendimiento de generación de embeddings REAL

        Args:
            text: Texto para generar embedding
            model_name: Nombre del modelo a usar

        Returns:
            Dict: Métricas de rendimiento
        """
        try:
            start_time = time.time()

            # Generar embedding REAL usando el modelo cargado
            if model_name in self.models and self.models[model_name].is_ready():
                embedding = self.models[model_name].get_embeddings([text])[0]
                generation_time = time.time() - start_time
            else:
                raise ValueError(f"Modelo {model_name} no está disponible")

            # Calcular métricas
            metrics = {
                "embedding_dimension": len(embedding),
                "generation_time": generation_time,
                "model_used": model_name,
                "text_length": len(text),
                "words_count": len(text.split()),
                "embedding_norm": np.linalg.norm(embedding),
                "timestamp": datetime.now().isoformat(),
            }

            # Registrar métricas
            self.performance_history.append(metrics)

            # Mantener solo las últimas 1000 métricas
            if len(self.performance_history) > 1000:
                self.performance_history = self.performance_history[-1000:]

            self.logger.info(
                f"Embedding generado en {generation_time:.4f}s para texto de {len(text)} caracteres"
            )

            return metrics

        except Exception as e:
            self.logger.error(f"Error monitoreando rendimiento de embeddings: {e}")
            raise


def main():
    """Función principal de demostración del monitor de embeddings"""
    logging.basicConfig(level=logging.INFO)

    # Crear monitor de rendimiento
    monitor = EmbeddingPerformanceMonitor("embedding_model_v1")

    # Textos de prueba reales
    test_texts = [
        "Hola mundo",
        "Inteligencia artificial",
        "Procesamiento de lenguaje natural",
        "Aprendizaje automático",
    ]

    # Monitorear rendimiento real
    for text in test_texts:
        try:
            metrics = monitor.monitor_embedding_performance(text, "default")
            logger.info(f"Métricas para '{text}': {metrics}")
        except Exception as e:
            logger.error(f"Error procesando '{text}': {e}")

    # Generar informe de rendimiento
    performance_report = monitor.generate_performance_report()
    print("Informe de rendimiento de embeddings:")
    print(performance_report)

    return {
        "status": "ok",
        "message": "Monitor de rendimiento de embeddings funcionando",
        "performance_report": performance_report,
    }


if __name__ == "__main__":
    result = main()
    print(result)
