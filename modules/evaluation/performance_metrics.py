"""
Métricas de Rendimiento - Performance Metrics
============================================

Componentes para cálculo y análisis de métricas de rendimiento.
"""

import logging
from typing import List, Dict, Any, Optional, Union
from dataclasses import dataclass
import numpy as np
import time
import psutil
from sklearn.metrics import (
    accuracy_score,
    precision_score,
    recall_score,
    f1_score,
    mean_squared_error,
    mean_absolute_error,
    r2_score,
    confusion_matrix,
    classification_report,
)

logger = logging.getLogger(__name__)


@dataclass
class PerformanceMetrics:
    """Métricas de rendimiento completas"""

    accuracy: float
    precision: float
    recall: float
    f1_score: float
    mse: float
    mae: float
    r2_score: float
    processing_time: float
    memory_usage: float
    cpu_usage: float


@dataclass
class SystemMetrics:
    """Métricas del sistema"""

    cpu_percent: float
    memory_percent: float
    disk_usage: float
    network_io: Dict[str, float]
    timestamp: float


class PerformanceMonitor:
    """Monitor de rendimiento del sistema"""

    def __init__(self):
        self.metrics_history: List[SystemMetrics] = []
        self.start_time = time.time()

    def get_system_metrics(self) -> SystemMetrics:
        """Obtiene métricas actuales del sistema"""
        try:
            cpu_percent = psutil.cpu_percent(interval=1)
            memory = psutil.virtual_memory()
            disk = psutil.disk_usage("/")
            network = psutil.net_io_counters()

            metrics = SystemMetrics(
                cpu_percent=cpu_percent,
                memory_percent=memory.percent,
                disk_usage=disk.percent,
                network_io={
                    "bytes_sent": network.bytes_sent,
                    "bytes_recv": network.bytes_recv,
                    "packets_sent": network.packets_sent,
                    "packets_recv": network.packets_recv,
                },
                timestamp=time.time(),
            )

            self.metrics_history.append(metrics)

            # Mantener solo los últimos 100 registros
            if len(self.metrics_history) > 100:
                self.metrics_history = self.metrics_history[-100:]

            return metrics

        except Exception as e:
            logger.error(f"❌ Error obteniendo métricas del sistema: {e}")
            return SystemMetrics(0.0, 0.0, 0.0, {}, time.time())

    def get_average_metrics(self, window_minutes: int = 5) -> SystemMetrics:
        """Obtiene métricas promedio en una ventana de tiempo"""
        if not self.metrics_history:
            return SystemMetrics(0.0, 0.0, 0.0, {}, time.time())

        current_time = time.time()
        window_seconds = window_minutes * 60

        # Filtrar métricas dentro de la ventana
        recent_metrics = [
            m
            for m in self.metrics_history
            if current_time - m.timestamp <= window_seconds
        ]

        if not recent_metrics:
            return SystemMetrics(0.0, 0.0, 0.0, {}, time.time())

        # Calcular promedios
        avg_cpu = np.mean([m.cpu_percent for m in recent_metrics])
        avg_memory = np.mean([m.memory_percent for m in recent_metrics])
        avg_disk = np.mean([m.disk_usage for m in recent_metrics])

        # Promedio de métricas de red
        avg_network = {}
        if recent_metrics:
            network_keys = recent_metrics[0].network_io.keys()
            for key in network_keys:
                avg_network[key] = np.mean([m.network_io[key] for m in recent_metrics])

        return SystemMetrics(
            cpu_percent=avg_cpu,
            memory_percent=avg_memory,
            disk_usage=avg_disk,
            network_io=avg_network,
            timestamp=current_time,
        )


class MetricsCalculator:
    """Calculador de métricas de rendimiento"""

    def __init__(self):
        self.monitor = PerformanceMonitor()

    def calculate_classification_metrics(
        self,
        y_true: Union[List, np.ndarray],
        y_pred: Union[List, np.ndarray],
        processing_time: float = 0.0,
    ) -> PerformanceMetrics:
        """Calcula métricas para clasificación"""
        try:
            y_true = np.array(y_true)
            y_pred = np.array(y_pred)

            # Métricas básicas
            accuracy = accuracy_score(y_true, y_pred)
            precision = precision_score(
                y_true, y_pred, average="weighted", zero_division=0
            )
            recall = recall_score(y_true, y_pred, average="weighted", zero_division=0)
            f1 = f1_score(y_true, y_pred, average="weighted", zero_division=0)

            # Métricas de error
            mse = mean_squared_error(y_true, y_pred)
            mae = mean_absolute_error(y_true, y_pred)

            # R² score (para clasificación, puede no ser muy útil)
            r2 = r2_score(y_true, y_pred)

            # Métricas del sistema
            system_metrics = self.monitor.get_system_metrics()

            return PerformanceMetrics(
                accuracy=accuracy,
                precision=precision,
                recall=recall,
                f1_score=f1,
                mse=mse,
                mae=mae,
                r2_score=r2,
                processing_time=processing_time,
                memory_usage=system_metrics.memory_percent,
                cpu_usage=system_metrics.cpu_percent,
            )

        except Exception as e:
            logger.error(f"❌ Error calculando métricas de clasificación: {e}")
            return PerformanceMetrics(0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0)

    def calculate_regression_metrics(
        self,
        y_true: Union[List, np.ndarray],
        y_pred: Union[List, np.ndarray],
        processing_time: float = 0.0,
    ) -> PerformanceMetrics:
        """Calcula métricas para regresión"""
        try:
            y_true = np.array(y_true)
            y_pred = np.array(y_pred)

            # Métricas de regresión
            mse = mean_squared_error(y_true, y_pred)
            mae = mean_absolute_error(y_true, y_pred)
            r2 = r2_score(y_true, y_pred)

            # Para regresión, accuracy no es aplicable
            accuracy = r2  # Usar R² como proxy de accuracy
            precision = 0.0  # No aplicable para regresión
            recall = 0.0  # No aplicable para regresión
            f1 = 0.0  # No aplicable para regresión

            # Métricas del sistema
            system_metrics = self.monitor.get_system_metrics()

            return PerformanceMetrics(
                accuracy=accuracy,
                precision=precision,
                recall=recall,
                f1_score=f1,
                mse=mse,
                mae=mae,
                r2_score=r2,
                processing_time=processing_time,
                memory_usage=system_metrics.memory_percent,
                cpu_usage=system_metrics.cpu_percent,
            )

        except Exception as e:
            logger.error(f"❌ Error calculando métricas de regresión: {e}")
            return PerformanceMetrics(0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0)

    def calculate_custom_metrics(
        self,
        y_true: Union[List, np.ndarray],
        y_pred: Union[List, np.ndarray],
        custom_metrics: Dict[str, callable],
        processing_time: float = 0.0,
    ) -> Dict[str, float]:
        """Calcula métricas personalizadas"""
        try:
            y_true = np.array(y_true)
            y_pred = np.array(y_pred)

            results = {}
            for metric_name, metric_func in custom_metrics.items():
                try:
                    results[metric_name] = metric_func(y_true, y_pred)
                except Exception as e:
                    logger.warning(f"⚠️ Error calculando métrica {metric_name}: {e}")
                    results[metric_name] = 0.0

            return results

        except Exception as e:
            logger.error(f"❌ Error calculando métricas personalizadas: {e}")
            return {}

    def get_detailed_classification_report(
        self,
        y_true: Union[List, np.ndarray],
        y_pred: Union[List, np.ndarray],
        target_names: Optional[List[str]] = None,
    ) -> Dict[str, Any]:
        """Obtiene reporte detallado de clasificación"""
        try:
            y_true = np.array(y_true)
            y_pred = np.array(y_pred)

            # Reporte de clasificación
            report = classification_report(
                y_true,
                y_pred,
                target_names=target_names,
                output_dict=True,
                zero_division=0,
            )

            # Matriz de confusión
            cm = confusion_matrix(y_true, y_pred)

            # Métricas adicionales
            metrics = self.calculate_classification_metrics(y_true, y_pred)

            return {
                "classification_report": report,
                "confusion_matrix": cm.tolist(),
                "performance_metrics": {
                    "accuracy": metrics.accuracy,
                    "precision": metrics.precision,
                    "recall": metrics.recall,
                    "f1_score": metrics.f1_score,
                },
                "system_metrics": {
                    "processing_time": metrics.processing_time,
                    "memory_usage": metrics.memory_usage,
                    "cpu_usage": metrics.cpu_usage,
                },
            }

        except Exception as e:
            logger.error(f"❌ Error generando reporte de clasificación: {e}")
            return {}

    def benchmark_performance(
        self, func: callable, *args, iterations: int = 10, **kwargs
    ) -> Dict[str, float]:
        """Realiza benchmark de rendimiento de una función"""
        try:
            times = []
            memory_usage = []
            cpu_usage = []

            for i in range(iterations):
                # Métricas antes
                start_metrics = self.monitor.get_system_metrics()
                start_time = time.time()

                # Ejecutar función
                result = func(*args, **kwargs)

                # Métricas después
                end_time = time.time()
                end_metrics = self.monitor.get_system_metrics()

                # Calcular diferencias
                execution_time = end_time - start_time
                memory_diff = end_metrics.memory_percent - start_metrics.memory_percent
                cpu_diff = end_metrics.cpu_percent - start_metrics.cpu_percent

                times.append(execution_time)
                memory_usage.append(memory_diff)
                cpu_usage.append(cpu_diff)

            return {
                "avg_execution_time": np.mean(times),
                "min_execution_time": np.min(times),
                "max_execution_time": np.max(times),
                "std_execution_time": np.std(times),
                "avg_memory_usage": np.mean(memory_usage),
                "avg_cpu_usage": np.mean(cpu_usage),
                "iterations": iterations,
            }

        except Exception as e:
            logger.error(f"❌ Error en benchmark: {e}")
            return {}
