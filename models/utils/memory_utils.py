"""
Utilidades de Gestión de Memoria
===============================

Este módulo proporciona utilidades para la gestión y optimización de memoria.
"""

import torch
import gc
import logging
import psutil
from typing import Dict, Any, Optional, List
from dataclasses import dataclass
from models.utils.device_utils import DeviceUtils


@dataclass
class MemoryStats:
    """Estadísticas de memoria"""

    total_gb: float
    used_gb: float
    available_gb: float
    percentage_used: float
    device: str


class MemoryManager:
    """
    Gestor de memoria del sistema

    Proporciona:
    - Monitoreo de memoria
    - Optimización automática
    - Gestión de memoria por dispositivo
    - Alertas de memoria baja
    """

    def __init__(self, device_utils: Optional[DeviceUtils] = None):
        """
        Inicializar gestor de memoria

        Args:
            device_utils: Utilidades de dispositivos (opcional)
        """
        self.logger = logging.getLogger(self.__class__.__name__)
        self.device_utils = device_utils or DeviceUtils()

        # Umbrales de memoria
        self.warning_threshold = 0.8  # 80%
        self.critical_threshold = 0.95  # 95%

        # Historial de memoria
        self.memory_history: List[MemoryStats] = []
        self.max_history_size = 100

    def get_system_memory_stats(self) -> MemoryStats:
        """
        Obtener estadísticas de memoria del sistema

        Returns:
            MemoryStats: Estadísticas de memoria del sistema
        """
        try:
            memory = psutil.virtual_memory()
            return MemoryStats(
                total_gb=memory.total / (1024**3),
                used_gb=memory.used / (1024**3),
                available_gb=memory.available / (1024**3),
                percentage_used=memory.percent / 100,
                device="system",
            )
        except Exception as e:
            self.logger.error(
                f"Error obteniendo estadísticas de memoria del sistema: {e}"
            )
            return MemoryStats(0, 0, 0, 0, "system")

    def get_device_memory_stats(self, device: str) -> MemoryStats:
        """
        Obtener estadísticas de memoria de un dispositivo

        Args:
            device: Dispositivo

        Returns:
            MemoryStats: Estadísticas de memoria del dispositivo
        """
        try:
            if device.startswith("cuda:"):
                device_id = int(device.split(":")[1])
                total_memory = torch.cuda.get_device_properties(
                    device_id
                ).total_memory / (1024**3)
                allocated_memory = torch.cuda.memory_allocated(device_id) / (1024**3)
                cached_memory = torch.cuda.memory_reserved(device_id) / (1024**3)
                available_memory = total_memory - allocated_memory
                percentage_used = allocated_memory / total_memory

                return MemoryStats(
                    total_gb=total_memory,
                    used_gb=allocated_memory,
                    available_gb=available_memory,
                    percentage_used=percentage_used,
                    device=device,
                )
            else:
                # Para CPU y otros dispositivos, usar memoria del sistema
                return self.get_system_memory_stats()
        except Exception as e:
            self.logger.error(
                f"Error obteniendo estadísticas de memoria de {device}: {e}"
            )
            return MemoryStats(0, 0, 0, 0, device)

    def get_all_memory_stats(self) -> Dict[str, MemoryStats]:
        """
        Obtener estadísticas de memoria de todos los dispositivos

        Returns:
            Dict: Estadísticas de memoria por dispositivo
        """
        stats = {}

        # Memoria del sistema
        stats["system"] = self.get_system_memory_stats()

        # Memoria de dispositivos
        for device_name in self.device_utils.get_available_devices():
            stats[device_name] = self.get_device_memory_stats(device_name)

        return stats

    def optimize_memory(self, device: str = "all") -> Dict[str, bool]:
        """
        Optimizar memoria de dispositivos

        Args:
            device: Dispositivo a optimizar ("all" para todos)

        Returns:
            Dict: Resultado de optimización por dispositivo
        """
        results = {}

        if device == "all":
            devices = list(self.device_utils.get_available_devices().keys())
            devices.append("system")
        else:
            devices = [device]

        for dev in devices:
            try:
                if dev.startswith("cuda:"):
                    device_id = int(dev.split(":")[1])
                    torch.cuda.empty_cache()
                    torch.cuda.synchronize(device_id)
                    results[dev] = True
                elif dev == "system":
                    # Forzar garbage collection
                    gc.collect()
                    results[dev] = True
                else:
                    # Para otros dispositivos
                    gc.collect()
                    results[dev] = True

                self.logger.info(f"Memoria optimizada para {dev}")
            except Exception as e:
                self.logger.error(f"Error optimizando memoria de {dev}: {e}")
                results[dev] = False

        return results

    def check_memory_status(self, device: str = "system") -> Dict[str, Any]:
        """
        Verificar estado de memoria de un dispositivo

        Args:
            device: Dispositivo a verificar

        Returns:
            Dict: Estado de memoria
        """
        stats = self.get_device_memory_stats(device)

        # Agregar al historial
        self.memory_history.append(stats)
        if len(self.memory_history) > self.max_history_size:
            self.memory_history.pop(0)

        # Determinar estado
        if stats.percentage_used >= self.critical_threshold:
            status = "critical"
        elif stats.percentage_used >= self.warning_threshold:
            status = "warning"
        else:
            status = "normal"

        return {
            "device": device,
            "status": status,
            "percentage_used": stats.percentage_used,
            "used_gb": stats.used_gb,
            "available_gb": stats.available_gb,
            "total_gb": stats.total_gb,
            "needs_optimization": status in ["warning", "critical"],
        }

    def get_memory_alerts(self) -> List[Dict[str, Any]]:
        """
        Obtener alertas de memoria

        Returns:
            List: Lista de alertas
        """
        alerts = []
        all_stats = self.get_all_memory_stats()

        for device, stats in all_stats.items():
            if stats.percentage_used >= self.critical_threshold:
                alerts.append(
                    {
                        "device": device,
                        "level": "critical",
                        "message": f"Memoria crítica en {device}: {stats.percentage_used:.1%} usado",
                        "percentage_used": stats.percentage_used,
                    }
                )
            elif stats.percentage_used >= self.warning_threshold:
                alerts.append(
                    {
                        "device": device,
                        "level": "warning",
                        "message": f"Memoria alta en {device}: {stats.percentage_used:.1%} usado",
                        "percentage_used": stats.percentage_used,
                    }
                )

        return alerts

    def get_memory_trends(
        self, device: str = "system", window: int = 10
    ) -> Dict[str, Any]:
        """
        Obtener tendencias de memoria

        Args:
            device: Dispositivo
            window: Ventana de tiempo (número de muestras)

        Returns:
            Dict: Tendencias de memoria
        """
        if len(self.memory_history) < 2:
            return {"trend": "stable", "change_percentage": 0}

        # Filtrar por dispositivo
        device_history = [s for s in self.memory_history if s.device == device]

        if len(device_history) < 2:
            return {"trend": "stable", "change_percentage": 0}

        # Calcular tendencia
        recent = (
            device_history[-window:]
            if len(device_history) >= window
            else device_history
        )
        old_avg = sum(s.percentage_used for s in recent[: len(recent) // 2]) / (
            len(recent) // 2
        )
        new_avg = sum(s.percentage_used for s in recent[len(recent) // 2 :]) / (
            len(recent) // 2
        )

        change = new_avg - old_avg

        if change > 0.05:
            trend = "increasing"
        elif change < -0.05:
            trend = "decreasing"
        else:
            trend = "stable"

        return {
            "trend": trend,
            "change_percentage": change * 100,
            "old_average": old_avg * 100,
            "new_average": new_avg * 100,
        }

    def estimate_model_memory_usage(
        self, model_size_gb: float, batch_size: int = 1
    ) -> Dict[str, float]:
        """
        Estimar uso de memoria para un modelo

        Args:
            model_size_gb: Tamaño del modelo en GB
            batch_size: Tamaño del batch

        Returns:
            Dict: Estimación de uso de memoria por dispositivo
        """
        estimates = {}
        all_stats = self.get_all_memory_stats()

        for device, stats in all_stats.items():
            # Estimación simple: modelo + batch * 0.5GB
            estimated_usage = model_size_gb + (batch_size * 0.5)
            estimates[device] = estimated_usage

        return estimates

    def can_load_model(
        self, model_size_gb: float, device: str = "auto"
    ) -> Dict[str, Any]:
        """
        Verificar si se puede cargar un modelo en un dispositivo

        Args:
            model_size_gb: Tamaño del modelo en GB
            device: Dispositivo ("auto" para automático)

        Returns:
            Dict: Resultado de la verificación
        """
        if device == "auto":
            # Encontrar el mejor dispositivo
            best_device = self.device_utils.get_best_device_for_model(model_size_gb)
            device = best_device

        stats = self.get_device_memory_stats(device)
        can_load = stats.available_gb >= model_size_gb * 1.2  # 20% de margen

        return {
            "device": device,
            "can_load": can_load,
            "required_gb": model_size_gb,
            "available_gb": stats.available_gb,
            "margin_gb": stats.available_gb - model_size_gb,
            "recommended_batch_size": self.device_utils.get_recommended_batch_size(
                device, model_size_gb
            ),
        }

    def get_memory_summary(self) -> Dict[str, Any]:
        """
        Obtener resumen de memoria del sistema

        Returns:
            Dict: Resumen de memoria
        """
        all_stats = self.get_all_memory_stats()
        alerts = self.get_memory_alerts()

        total_system_memory = all_stats.get("system", MemoryStats(0, 0, 0, 0, "system"))

        return {
            "system_memory": {
                "total_gb": total_system_memory.total_gb,
                "used_gb": total_system_memory.used_gb,
                "available_gb": total_system_memory.available_gb,
                "percentage_used": total_system_memory.percentage_used,
            },
            "device_memory": {
                device: {
                    "total_gb": stats.total_gb,
                    "used_gb": stats.used_gb,
                    "available_gb": stats.available_gb,
                    "percentage_used": stats.percentage_used,
                }
                for device, stats in all_stats.items()
                if device != "system"
            },
            "alerts": alerts,
            "total_alerts": len(alerts),
            "critical_alerts": len([a for a in alerts if a["level"] == "critical"]),
            "warning_alerts": len([a for a in alerts if a["level"] == "warning"]),
        }

    def set_memory_thresholds(self, warning: float = 0.8, critical: float = 0.95):
        """
        Establecer umbrales de memoria

        Args:
            warning: Umbral de advertencia (0.0 - 1.0)
            critical: Umbral crítico (0.0 - 1.0)
        """
        if 0 <= warning <= 1 and 0 <= critical <= 1 and warning < critical:
            self.warning_threshold = warning
            self.critical_threshold = critical
            self.logger.info(
                f"Umbrales de memoria actualizados: warning={warning}, critical={critical}"
            )
        else:
            raise ValueError(
                "Umbrales inválidos: warning < critical y ambos entre 0 y 1"
            )

    def clear_memory_history(self):
        """Limpiar historial de memoria"""
        self.memory_history.clear()
        self.logger.info("Historial de memoria limpiado")
