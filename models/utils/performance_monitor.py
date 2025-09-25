"""
Monitor de Rendimiento de Modelos
================================

Este módulo proporciona monitoreo de rendimiento para modelos y operaciones.
"""

import time
import logging
import threading
from typing import Dict, Any, Optional, List, Callable
from dataclasses import dataclass, field
from contextlib import contextmanager
from collections import defaultdict, deque
import statistics


@dataclass
class PerformanceMetric:
    """Métrica de rendimiento"""

    operation: str
    duration: float
    timestamp: float
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class PerformanceStats:
    """Estadísticas de rendimiento"""

    operation: str
    count: int
    total_time: float
    avg_time: float
    min_time: float
    max_time: float
    median_time: float
    std_dev: float
    success_rate: float
    last_execution: Optional[float] = None


class PerformanceMonitor:
    """
    Monitor de rendimiento para modelos y operaciones

    Proporciona:
    - Medición de tiempo de operaciones
    - Estadísticas de rendimiento
    - Alertas de rendimiento lento
    - Monitoreo en tiempo real
    """

    def __init__(self, max_history: int = 1000):
        """
        Inicializar monitor de rendimiento

        Args:
            max_history: Número máximo de métricas a mantener
        """
        self.logger = logging.getLogger(self.__class__.__name__)
        self.max_history = max_history

        # Almacenamiento de métricas
        self.metrics: Dict[str, deque] = defaultdict(lambda: deque(maxlen=max_history))
        self.active_operations: Dict[str, float] = {}

        # Umbrales de rendimiento
        self.slow_threshold = 5.0  # segundos
        self.critical_threshold = 30.0  # segundos

        # Estadísticas en tiempo real
        self.stats_cache: Dict[str, PerformanceStats] = {}
        self.cache_valid = False

        # Thread safety
        self._lock = threading.Lock()

    @contextmanager
    def track(self, operation: str, metadata: Optional[Dict[str, Any]] = None):
        """
        Context manager para medir tiempo de operación

        Args:
            operation: Nombre de la operación
            metadata: Metadatos adicionales
        """
        start_time = time.time()
        metadata = metadata or {}

        try:
            yield
            success = True
        except Exception as e:
            success = False
            metadata["error"] = str(e)
            raise
        finally:
            duration = time.time() - start_time
            self.record_metric(operation, duration, metadata, success)

    def record_metric(
        self,
        operation: str,
        duration: float,
        metadata: Optional[Dict[str, Any]] = None,
        success: bool = True,
    ):
        """
        Registrar una métrica de rendimiento

        Args:
            operation: Nombre de la operación
            duration: Duración en segundos
            metadata: Metadatos adicionales
            success: Si la operación fue exitosa
        """
        with self._lock:
            metric = PerformanceMetric(
                operation=operation,
                duration=duration,
                timestamp=time.time(),
                metadata=metadata or {},
            )

            self.metrics[operation].append(metric)
            self.cache_valid = False

            # Verificar umbrales
            if duration > self.critical_threshold:
                self.logger.critical(
                    f"Operación crítica lenta: {operation} tomó {duration:.2f}s"
                )
            elif duration > self.slow_threshold:
                self.logger.warning(
                    f"Operación lenta: {operation} tomó {duration:.2f}s"
                )

    def start_operation(self, operation: str) -> str:
        """
        Iniciar medición de operación

        Args:
            operation: Nombre de la operación

        Returns:
            str: ID de la operación
        """
        with self._lock:
            operation_id = f"{operation}_{int(time.time() * 1000)}"
            self.active_operations[operation_id] = time.time()
            return operation_id

    def end_operation(
        self,
        operation_id: str,
        metadata: Optional[Dict[str, Any]] = None,
        success: bool = True,
    ):
        """
        Finalizar medición de operación

        Args:
            operation_id: ID de la operación
            metadata: Metadatos adicionales
            success: Si la operación fue exitosa
        """
        with self._lock:
            if operation_id in self.active_operations:
                start_time = self.active_operations.pop(operation_id)
                duration = time.time() - start_time
                operation = operation_id.split("_")[0]
                self.record_metric(operation, duration, metadata, success)

    def get_operation_stats(self, operation: str) -> Optional[PerformanceStats]:
        """
        Obtener estadísticas de una operación

        Args:
            operation: Nombre de la operación

        Returns:
            PerformanceStats: Estadísticas de la operación
        """
        with self._lock:
            if not self.cache_valid:
                self._update_stats_cache()

            return self.stats_cache.get(operation)

    def get_all_stats(self) -> Dict[str, PerformanceStats]:
        """
        Obtener estadísticas de todas las operaciones

        Returns:
            Dict: Estadísticas por operación
        """
        with self._lock:
            if not self.cache_valid:
                self._update_stats_cache()

            return self.stats_cache.copy()

    def _update_stats_cache(self):
        """Actualizar caché de estadísticas"""
        self.stats_cache.clear()

        for operation, metrics in self.metrics.items():
            if not metrics:
                continue

            durations = [m.duration for m in metrics]
            success_count = sum(1 for m in metrics if m.metadata.get("error") is None)

            stats = PerformanceStats(
                operation=operation,
                count=len(metrics),
                total_time=sum(durations),
                avg_time=statistics.mean(durations),
                min_time=min(durations),
                max_time=max(durations),
                median_time=statistics.median(durations),
                std_dev=statistics.stdev(durations) if len(durations) > 1 else 0,
                success_rate=success_count / len(metrics),
                last_execution=metrics[-1].timestamp if metrics else None,
            )

            self.stats_cache[operation] = stats

        self.cache_valid = True

    def get_slow_operations(
        self, threshold: Optional[float] = None
    ) -> List[Dict[str, Any]]:
        """
        Obtener operaciones lentas

        Args:
            threshold: Umbral de tiempo (usa el umbral por defecto si no se especifica)

        Returns:
            List: Lista de operaciones lentas
        """
        threshold = threshold or self.slow_threshold
        slow_ops = []

        for operation, metrics in self.metrics.items():
            slow_metrics = [m for m in metrics if m.duration > threshold]
            if slow_metrics:
                slow_ops.append(
                    {
                        "operation": operation,
                        "count": len(slow_metrics),
                        "avg_duration": statistics.mean(
                            [m.duration for m in slow_metrics]
                        ),
                        "max_duration": max([m.duration for m in slow_metrics]),
                        "last_slow": slow_metrics[-1].timestamp,
                    }
                )

        return sorted(slow_ops, key=lambda x: x["avg_duration"], reverse=True)

    def get_performance_alerts(self) -> List[Dict[str, Any]]:
        """
        Obtener alertas de rendimiento

        Returns:
            List: Lista de alertas
        """
        alerts = []
        all_stats = self.get_all_stats()

        for operation, stats in all_stats.items():
            # Alertas por operaciones lentas
            if stats.avg_time > self.critical_threshold:
                alerts.append(
                    {
                        "type": "critical_slow",
                        "operation": operation,
                        "message": f"Operación críticamente lenta: {operation} promedio {stats.avg_time:.2f}s",
                        "avg_time": stats.avg_time,
                        "threshold": self.critical_threshold,
                    }
                )
            elif stats.avg_time > self.slow_threshold:
                alerts.append(
                    {
                        "type": "slow",
                        "operation": operation,
                        "message": f"Operación lenta: {operation} promedio {stats.avg_time:.2f}s",
                        "avg_time": stats.avg_time,
                        "threshold": self.slow_threshold,
                    }
                )

            # Alertas por tasa de éxito baja
            if stats.success_rate < 0.9:
                alerts.append(
                    {
                        "type": "low_success",
                        "operation": operation,
                        "message": f"Tasa de éxito baja: {operation} {stats.success_rate:.1%}",
                        "success_rate": stats.success_rate,
                    }
                )

        return alerts

    def get_performance_summary(self) -> Dict[str, Any]:
        """
        Obtener resumen de estadísticas de rendimiento

        Returns:
            Dict: Resumen de estadísticas
        """
        summary = {
            "total_operations": 0,
            "avg_time": 0.0,
            "min_time": 0.0,
            "max_time": 0.0,
            "median_time": 0.0,
            "std_dev": 0.0,
            "total_time": 0.0,
        }

        if not self.metrics:
            return summary

        # Calcular estadísticas
        all_times = []
        for operation_metrics in self.metrics.values():
            for metric in operation_metrics:
                all_times.append(metric.duration)

        if all_times:
            summary["total_operations"] = len(all_times)
            summary["avg_time"] = sum(all_times) / len(all_times)
            summary["min_time"] = min(all_times)
            summary["max_time"] = max(all_times)
            summary["total_time"] = sum(all_times)

            # Calcular mediana
            sorted_times = sorted(all_times)
            n = len(sorted_times)
            if n % 2 == 0:
                summary["median_time"] = (
                    sorted_times[n // 2 - 1] + sorted_times[n // 2]
                ) / 2
            else:
                summary["median_time"] = sorted_times[n // 2]

            # Calcular desviación estándar
            if n > 1:
                mean = summary["avg_time"]
                variance = sum((x - mean) ** 2 for x in all_times) / (n - 1)
                summary["std_dev"] = variance**0.5

        return summary

    def set_thresholds(self, slow: float = 5.0, critical: float = 30.0):
        """
        Establecer umbrales de rendimiento

        Args:
            slow: Umbral de operación lenta en segundos
            critical: Umbral de operación crítica en segundos
        """
        if slow > 0 and critical > slow:
            self.slow_threshold = slow
            self.critical_threshold = critical
            self.logger.info(
                f"Umbrales actualizados: slow={slow}s, critical={critical}s"
            )
        else:
            raise ValueError("Umbrales inválidos: critical > slow > 0")

    def clear_metrics(self, operation: Optional[str] = None):
        """
        Limpiar métricas

        Args:
            operation: Operación específica (None para todas)
        """
        with self._lock:
            if operation:
                if operation in self.metrics:
                    self.metrics[operation].clear()
                    self.logger.info(f"Métricas limpiadas para {operation}")
            else:
                self.metrics.clear()
                self.logger.info("Todas las métricas limpiadas")

            self.cache_valid = False

    def export_metrics(self, operation: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        Exportar métricas

        Args:
            operation: Operación específica (None para todas)

        Returns:
            List: Lista de métricas exportadas
        """
        with self._lock:
            if operation:
                metrics = self.metrics.get(operation, [])
            else:
                metrics = []
                for op_metrics in self.metrics.values():
                    metrics.extend(op_metrics)

            return [
                {
                    "operation": m.operation,
                    "duration": m.duration,
                    "timestamp": m.timestamp,
                    "metadata": m.metadata,
                }
                for m in metrics
            ]

    def get_active_operations(self) -> Dict[str, float]:
        """
        Obtener operaciones activas

        Returns:
            Dict: Operaciones activas con tiempo de inicio
        """
        with self._lock:
            return self.active_operations.copy()

    def __str__(self) -> str:
        """Representación en string del monitor"""
        summary = self.get_performance_summary()
        return f"PerformanceMonitor(operations={summary['total_operations']}, avg_time={summary['avg_time']:.2f}s)"
