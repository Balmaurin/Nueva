import time
import logging
import threading
import psutil
import torch
import numpy as np
from typing import Dict, Any, List
from prometheus_client import start_http_server, Gauge, Counter


class SheilyMetrics:
    def __init__(self, metrics_port: int = 8000, update_interval: float = 5.0):
        """
        Inicializar sistema de métricas para Sheily-AI

        Args:
            metrics_port (int): Puerto para servidor de métricas Prometheus
            update_interval (float): Intervalo de actualización de métricas
        """
        self.logger = logging.getLogger(__name__)
        logging.basicConfig(
            level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
        )

        # Configuración de métricas Prometheus
        self.metrics_port = metrics_port
        self.update_interval = update_interval

        # Métricas de sistema
        self.system_metrics = {
            "cpu_usage": Gauge("sheily_cpu_usage_percent", "Uso de CPU del sistema"),
            "memory_usage": Gauge(
                "sheily_memory_usage_bytes", "Uso de memoria del sistema"
            ),
            "vram_usage": Gauge("sheily_vram_usage_bytes", "Uso de VRAM de GPU"),
        }

        # Métricas de modelo
        self.model_metrics = {
            "generation_latency": Gauge(
                "sheily_generation_latency_seconds", "Latencia de generación de texto"
            ),
            "tokens_generated": Counter(
                "sheily_tokens_generated_total", "Número total de tokens generados"
            ),
            "domain_classification_accuracy": Gauge(
                "sheily_domain_classification_accuracy",
                "Precisión de clasificación de dominio",
            ),
            "rag_hit_rate": Gauge(
                "sheily_rag_hit_rate", "Tasa de acierto de recuperación semántica"
            ),
        }

        # Métricas de memoria
        self.memory_metrics = {
            "memory_interactions": Counter(
                "sheily_memory_interactions_total",
                "Número total de interacciones en memoria",
            ),
            "documents_indexed": Gauge(
                "sheily_documents_indexed", "Número de documentos indexados en RAG"
            ),
        }

        # Hilo de actualización de métricas
        self.metrics_thread = threading.Thread(target=self._update_metrics, daemon=True)

    def start_metrics_server(self):
        """
        Iniciar servidor de métricas Prometheus
        """
        try:
            start_http_server(self.metrics_port)
            self.logger.info(
                f"Servidor de métricas iniciado en puerto {self.metrics_port}"
            )

            # Iniciar hilo de actualización
            self.metrics_thread.start()
        except Exception as e:
            self.logger.error(f"Error iniciando servidor de métricas: {e}")

    def _update_metrics(self):
        """
        Actualizar métricas del sistema periódicamente
        """
        while True:
            try:
                # Métricas de sistema
                self.system_metrics["cpu_usage"].set(psutil.cpu_percent())
                self.system_metrics["memory_usage"].set(psutil.virtual_memory().used)

                # Métricas de VRAM
                if torch.cuda.is_available():
                    total_vram = torch.cuda.get_device_properties(0).total_memory
                    reserved_vram = torch.cuda.memory_reserved(0)
                    self.system_metrics["vram_usage"].set(reserved_vram)

                time.sleep(self.update_interval)

            except Exception as e:
                self.logger.error(f"Error actualizando métricas: {e}")
                time.sleep(self.update_interval)

    def track_generation_metrics(
        self, prompt: str, response: str, generation_time: float
    ):
        """
        Registrar métricas de generación de texto

        Args:
            prompt (str): Texto de entrada
            response (str): Texto generado
            generation_time (float): Tiempo de generación
        """
        try:
            # Latencia de generación
            self.model_metrics["generation_latency"].set(generation_time)

            # Tokens generados
            tokens_generated = len(response.split())
            self.model_metrics["tokens_generated"].inc(tokens_generated)

        except Exception as e:
            self.logger.error(f"Error registrando métricas de generación: {e}")

    def track_domain_classification(
        self, query: str, predicted_domain: str, confidence: float
    ):
        """
        Registrar métricas de clasificación de dominio

        Args:
            query (str): Consulta de entrada
            predicted_domain (str): Dominio predicho
            confidence (float): Confianza de predicción
        """
        try:
            # Precisión de clasificación
            self.model_metrics["domain_classification_accuracy"].set(confidence)

        except Exception as e:
            self.logger.error(f"Error registrando métricas de clasificación: {e}")

    def track_rag_metrics(self, query: str, retrieved_documents: List[Dict[str, Any]]):
        """
        Registrar métricas de recuperación semántica

        Args:
            query (str): Consulta de entrada
            retrieved_documents (list): Documentos recuperados
        """
        try:
            # Tasa de acierto de RAG
            hit_rate = 1.0 if retrieved_documents else 0.0
            self.model_metrics["rag_hit_rate"].set(hit_rate)

            # Documentos indexados
            self.memory_metrics["documents_indexed"].set(len(retrieved_documents))

        except Exception as e:
            self.logger.error(f"Error registrando métricas de RAG: {e}")

    def track_memory_interaction(self, interaction_type: str):
        """
        Registrar interacciones de memoria

        Args:
            interaction_type (str): Tipo de interacción
        """
        try:
            self.memory_metrics["memory_interactions"].inc()

        except Exception as e:
            self.logger.error(f"Error registrando interacción de memoria: {e}")


# Configuración de logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)


def main():
    """
    Ejemplo de uso del sistema de métricas
    """
    metrics = SheilyMetrics()
    metrics.start_metrics_server()

    # Mantener el hilo principal activo
    metrics.metrics_thread.join()


if __name__ == "__main__":
    main()
