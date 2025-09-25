import os
import time
import logging
import threading
import psutil
import tracemalloc
import asyncio
import json
import traceback
from typing import Dict, Any, Optional, List, Callable
from dataclasses import dataclass, field
from datetime import datetime, timedelta


class ModulePerformanceMetrics:
    """
    Métricas de rendimiento detalladas para un módulo

    Rastrea:
    - Uso de CPU
    - Uso de memoria
    - Tiempo de procesamiento
    - Número de llamadas
    - Errores
    """

    def __init__(self, module_name: str):
        """
        Inicializar métricas de rendimiento

        Args:
            module_name (str): Nombre del módulo
        """
        self.module_name = module_name
        self.total_calls = 0
        self.total_processing_time = 0.0
        self.max_processing_time = 0.0
        self.min_processing_time = float("inf")
        self.error_count = 0
        self.last_error: Optional[Dict[str, Any]] = None

        # Métricas de recursos
        self.peak_memory_usage = 0
        self.total_memory_usage = 0
        self.cpu_usage_history: List[float] = []

    def record_call(self, processing_time: float):
        """
        Registrar llamada al módulo

        Args:
            processing_time (float): Tiempo de procesamiento
        """
        self.total_calls += 1
        self.total_processing_time += processing_time

        # Actualizar tiempos extremos
        self.max_processing_time = max(self.max_processing_time, processing_time)
        self.min_processing_time = min(self.min_processing_time, processing_time)

    def record_error(self, error: Exception):
        """
        Registrar error en el módulo

        Args:
            error (Exception): Excepción ocurrida
        """
        self.error_count += 1
        self.last_error = {
            "type": type(error).__name__,
            "message": str(error),
            "traceback": traceback.format_exc(),
            "timestamp": datetime.now().isoformat(),
        }

    def update_memory_usage(self, memory_usage: int):
        """
        Actualizar uso de memoria

        Args:
            memory_usage (int): Uso de memoria en bytes
        """
        self.peak_memory_usage = max(self.peak_memory_usage, memory_usage)
        self.total_memory_usage += memory_usage

    def update_cpu_usage(self, cpu_usage: float):
        """
        Actualizar uso de CPU

        Args:
            cpu_usage (float): Porcentaje de uso de CPU
        """
        self.cpu_usage_history.append(cpu_usage)

        # Mantener solo los últimos 100 registros
        if len(self.cpu_usage_history) > 100:
            self.cpu_usage_history.pop(0)

    def get_performance_summary(self) -> Dict[str, Any]:
        """
        Obtener resumen de rendimiento

        Returns:
            Diccionario con métricas de rendimiento
        """
        return {
            "module_name": self.module_name,
            "total_calls": self.total_calls,
            "avg_processing_time": (
                self.total_processing_time / self.total_calls
                if self.total_calls > 0
                else 0
            ),
            "max_processing_time": self.max_processing_time,
            "min_processing_time": self.min_processing_time,
            "error_count": self.error_count,
            "last_error": self.last_error,
            "peak_memory_usage": self.peak_memory_usage,
            "avg_memory_usage": (
                self.total_memory_usage / self.total_calls
                if self.total_calls > 0
                else 0
            ),
            "avg_cpu_usage": (
                sum(self.cpu_usage_history) / len(self.cpu_usage_history)
                if self.cpu_usage_history
                else 0
            ),
        }


class ModuleMonitor:
    """
    Monitor de módulos para NeuroFusion

    Características:
    - Seguimiento de rendimiento en tiempo real
    - Monitoreo de recursos
    - Detección de problemas
    - Generación de informes
    """

    def __init__(
        self, log_dir: str = "logs/module_monitor", monitoring_interval: float = 5.0
    ):
        """
        Inicializar monitor de módulos

        Args:
            log_dir (str): Directorio para guardar logs
            monitoring_interval (float): Intervalo de monitoreo en segundos
        """
        self.logger = logging.getLogger(__name__)
        self.log_dir = log_dir
        self.monitoring_interval = monitoring_interval

        # Crear directorio de logs si no existe
        os.makedirs(log_dir, exist_ok=True)

        # Registro de métricas de módulos
        self.module_metrics: Dict[str, ModulePerformanceMetrics] = {}

        # Configuración de monitoreo
        self.monitoring_thread: Optional[threading.Thread] = None
        self.stop_monitoring = threading.Event()

    def register_module(self, module_name: str):
        """
        Registrar un módulo para monitoreo

        Args:
            module_name (str): Nombre del módulo
        """
        if module_name not in self.module_metrics:
            self.module_metrics[module_name] = ModulePerformanceMetrics(module_name)

    def track_module_call(
        self,
        module_name: str,
        processing_time: float,
        input_data: Any = None,
        output_data: Any = None,
    ):
        """
        Registrar llamada a un módulo

        Args:
            module_name (str): Nombre del módulo
            processing_time (float): Tiempo de procesamiento
            input_data (Any, opcional): Datos de entrada
            output_data (Any, opcional): Datos de salida
        """
        if module_name not in self.module_metrics:
            self.register_module(module_name)

        # Registrar métricas de llamada
        self.module_metrics[module_name].record_call(processing_time)

        # Opcional: Registrar datos de entrada/salida para diagnóstico
        self._log_module_call(module_name, processing_time, input_data, output_data)

    def track_module_error(self, module_name: str, error: Exception):
        """
        Registrar error en un módulo

        Args:
            module_name (str): Nombre del módulo
            error (Exception): Excepción ocurrida
        """
        if module_name not in self.module_metrics:
            self.register_module(module_name)

        # Registrar error
        self.module_metrics[module_name].record_error(error)

        # Registrar error en log
        self._log_module_error(module_name, error)

    def _log_module_call(
        self,
        module_name: str,
        processing_time: float,
        input_data: Any = None,
        output_data: Any = None,
    ):
        """
        Registrar llamada a módulo en archivo de log

        Args:
            module_name (str): Nombre del módulo
            processing_time (float): Tiempo de procesamiento
            input_data (Any, opcional): Datos de entrada
            output_data (Any, opcional): Datos de salida
        """
        log_file = os.path.join(self.log_dir, f"{module_name}_calls.jsonl")

        log_entry = {
            "timestamp": datetime.now().isoformat(),
            "module_name": module_name,
            "processing_time": processing_time,
            "input_data": str(input_data)[:500] if input_data is not None else None,
            "output_data": str(output_data)[:500] if output_data is not None else None,
        }

        with open(log_file, "a", encoding="utf-8") as f:
            f.write(json.dumps(log_entry) + "\n")

    def _log_module_error(self, module_name: str, error: Exception):
        """
        Registrar error de módulo en archivo de log

        Args:
            module_name (str): Nombre del módulo
            error (Exception): Excepción ocurrida
        """
        log_file = os.path.join(self.log_dir, f"{module_name}_errors.jsonl")

        error_entry = {
            "timestamp": datetime.now().isoformat(),
            "module_name": module_name,
            "error_type": type(error).__name__,
            "error_message": str(error),
            "traceback": traceback.format_exc(),
        }

        with open(log_file, "a", encoding="utf-8") as f:
            f.write(json.dumps(error_entry) + "\n")

    def start_system_monitoring(self):
        """
        Iniciar monitoreo continuo de recursos del sistema
        """

        def monitor_system_resources():
            """Función de monitoreo de recursos"""
            while not self.stop_monitoring.is_set():
                # Monitorear uso de CPU y memoria para cada módulo
                for module_name, metrics in self.module_metrics.items():
                    try:
                        # Obtener uso de CPU y memoria del proceso actual
                        process = psutil.Process()
                        cpu_usage = process.cpu_percent()
                        memory_usage = process.memory_info().rss

                        # Actualizar métricas del módulo
                        metrics.update_cpu_usage(cpu_usage)
                        metrics.update_memory_usage(memory_usage)

                    except Exception as e:
                        self.logger.error(f"Error monitoreando {module_name}: {e}")

                # Esperar intervalo de monitoreo
                time.sleep(self.monitoring_interval)

        # Iniciar hilo de monitoreo
        self.monitoring_thread = threading.Thread(target=monitor_system_resources)
        self.monitoring_thread.daemon = True
        self.monitoring_thread.start()

    def stop_system_monitoring(self):
        """
        Detener monitoreo de recursos del sistema
        """
        if self.monitoring_thread:
            self.stop_monitoring.set()
            self.monitoring_thread.join()

    def generate_module_report(
        self, module_name: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Generar informe de rendimiento de módulos

        Args:
            module_name (str, opcional): Nombre del módulo específico

        Returns:
            Informe de rendimiento
        """
        if module_name:
            # Informe de un módulo específico
            if module_name not in self.module_metrics:
                return {"error": f"Módulo {module_name} no encontrado"}

            return self.module_metrics[module_name].get_performance_summary()

        # Informe de todos los módulos
        return {
            name: metrics.get_performance_summary()
            for name, metrics in self.module_metrics.items()
        }

    def export_module_logs(
        self, module_name: str, log_type: str = "calls", days: int = 1
    ) -> List[Dict[str, Any]]:
        """
        Exportar logs de un módulo

        Args:
            module_name (str): Nombre del módulo
            log_type (str): Tipo de log ('calls' o 'errors')
            days (int): Número de días de logs a exportar

        Returns:
            Lista de entradas de log
        """
        log_file = os.path.join(self.log_dir, f"{module_name}_{log_type}.jsonl")

        if not os.path.exists(log_file):
            return []

        # Filtrar logs por fecha
        cutoff_time = datetime.now() - timedelta(days=days)

        logs = []
        with open(log_file, "r", encoding="utf-8") as f:
            for line in f:
                entry = json.loads(line)
                entry_time = datetime.fromisoformat(entry["timestamp"])

                if entry_time >= cutoff_time:
                    logs.append(entry)

        return logs


def main():
    """Demostración del sistema de monitoreo de módulos"""
    logging.basicConfig(level=logging.INFO)

    # Crear monitor de módulos
    module_monitor = ModuleMonitor(monitoring_interval=2.0)

    # Iniciar monitoreo de sistema
    module_monitor.start_system_monitoring()

    # Simular módulo de ejemplo
    def example_module_process(data):
        """Módulo de ejemplo para demostración"""
        time.sleep(0.1)  # Simular procesamiento
        return data.upper()

    # Simular llamadas al módulo
    for i in range(10):
        start_time = time.time()
        try:
            result = example_module_process(f"prueba {i}")
            processing_time = time.time() - start_time

            module_monitor.track_module_call(
                "ExampleModule",
                processing_time,
                input_data=f"prueba {i}",
                output_data=result,
            )
        except Exception as e:
            module_monitor.track_module_error("ExampleModule", e)

    # Esperar un momento para recopilar métricas
    time.sleep(5)

    # Detener monitoreo
    module_monitor.stop_system_monitoring()

    # Generar informe
    module_report = module_monitor.generate_module_report("ExampleModule")
    print("Informe de módulo:")
    print(json.dumps(module_report, indent=2))

    # Exportar logs
    module_logs = module_monitor.export_module_logs("ExampleModule")
    print("\nLogs del módulo:")
    print(json.dumps(module_logs, indent=2))


if __name__ == "__main__":
    main()
