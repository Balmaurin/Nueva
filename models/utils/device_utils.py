"""
Utilidades de Gestión de Dispositivos
====================================

Este módulo proporciona utilidades para la gestión de dispositivos (CPU, GPU, etc.).
"""

import torch
import logging
from typing import Optional, Dict, Any
from dataclasses import dataclass


@dataclass
class DeviceInfo:
    """Información de un dispositivo"""

    name: str
    type: str
    memory_total: float  # GB
    memory_available: float  # GB
    memory_used: float  # GB
    is_available: bool
    compute_capability: Optional[str] = None


class DeviceUtils:
    """
    Utilidades para gestión de dispositivos

    Proporciona:
    - Detección automática de dispositivos
    - Gestión de memoria
    - Optimización de dispositivos
    - Información de dispositivos
    """

    def __init__(self):
        """Inicializar utilidades de dispositivos"""
        self.logger = logging.getLogger(self.__class__.__name__)
        self.devices = self._detect_devices()

    def _detect_devices(self) -> Dict[str, DeviceInfo]:
        """Detectar dispositivos disponibles"""
        devices = {}

        # CPU
        devices["cpu"] = DeviceInfo(
            name="CPU",
            type="cpu",
            memory_total=self._get_cpu_memory(),
            memory_available=self._get_cpu_memory(),
            memory_used=0.0,
            is_available=True,
        )

        # CUDA GPU
        if torch.cuda.is_available():
            for i in range(torch.cuda.device_count()):
                device_name = f"cuda:{i}"
                device_props = torch.cuda.get_device_properties(i)

                devices[device_name] = DeviceInfo(
                    name=device_props.name,
                    type="cuda",
                    memory_total=device_props.total_memory / (1024**3),
                    memory_available=torch.cuda.get_device_properties(i).total_memory
                    / (1024**3),
                    memory_used=0.0,
                    is_available=True,
                    compute_capability=f"{device_props.major}.{device_props.minor}",
                )

        # MPS (Apple Silicon)
        elif hasattr(torch.backends, "mps") and torch.backends.mps.is_available():
            devices["mps"] = DeviceInfo(
                name="MPS",
                type="mps",
                memory_total=self._get_mps_memory(),
                memory_available=self._get_mps_memory(),
                memory_used=0.0,
                is_available=True,
            )

        self.logger.info(f"Dispositivos detectados: {list(devices.keys())}")
        return devices

    def _get_cpu_memory(self) -> float:
        """Obtener memoria total de CPU en GB"""
        try:
            import psutil

            return psutil.virtual_memory().total / (1024**3)
        except ImportError:
            return 16.0  # Valor por defecto

    def _get_mps_memory(self) -> float:
        """Obtener memoria total de MPS en GB"""
        try:
            import psutil

            return psutil.virtual_memory().total / (1024**3)
        except ImportError:
            return 16.0  # Valor por defecto

    def get_optimal_device(self, device_preference: str = "auto") -> str:
        """
        Obtener el dispositivo óptimo

        Args:
            device_preference: Preferencia de dispositivo ("auto", "cuda", "mps", "cpu")

        Returns:
            str: Dispositivo óptimo
        """
        if device_preference == "auto":
            # Prioridad: CUDA > MPS > CPU
            if "cuda:0" in self.devices:
                return "cuda:0"
            elif "mps" in self.devices:
                return "mps"
            else:
                return "cpu"
        elif device_preference in self.devices:
            return device_preference
        else:
            self.logger.warning(
                f"Dispositivo {device_preference} no disponible, usando CPU"
            )
            return "cpu"

    def get_device_info(self, device: str) -> Optional[DeviceInfo]:
        """
        Obtener información de un dispositivo

        Args:
            device: Nombre del dispositivo

        Returns:
            DeviceInfo: Información del dispositivo
        """
        if device in self.devices:
            device_info = self.devices[device]

            # Actualizar información de memoria
            if device.startswith("cuda:"):
                device_id = int(device.split(":")[1])
                device_info.memory_used = torch.cuda.memory_allocated(device_id) / (
                    1024**3
                )
                device_info.memory_available = (
                    device_info.memory_total - device_info.memory_used
                )

            return device_info
        return None

    def get_available_devices(self) -> Dict[str, DeviceInfo]:
        """Obtener todos los dispositivos disponibles"""
        return self.devices.copy()

    def get_best_device_for_model(self, model_size_gb: float) -> str:
        """
        Obtener el mejor dispositivo para un modelo de cierto tamaño

        Args:
            model_size_gb: Tamaño del modelo en GB

        Returns:
            str: Mejor dispositivo disponible
        """
        for device_name, device_info in self.devices.items():
            if (
                device_info.is_available
                and device_info.memory_available >= model_size_gb * 1.5
            ):
                return device_name

        # Si no hay dispositivo con suficiente memoria, usar el que más tenga
        best_device = "cpu"
        max_memory = 0

        for device_name, device_info in self.devices.items():
            if device_info.is_available and device_info.memory_available > max_memory:
                max_memory = device_info.memory_available
                best_device = device_name

        self.logger.warning(
            f"No hay dispositivo con suficiente memoria para modelo de {model_size_gb}GB"
        )
        return best_device

    def optimize_device_memory(self, device: str) -> bool:
        """
        Optimizar memoria de un dispositivo

        Args:
            device: Dispositivo a optimizar

        Returns:
            bool: True si se optimizó exitosamente
        """
        try:
            if device.startswith("cuda:"):
                device_id = int(device.split(":")[1])
                torch.cuda.empty_cache()
                torch.cuda.synchronize(device_id)
            elif device == "mps":
                # MPS no tiene métodos específicos de limpieza
                pass

            # Forzar garbage collection
            import gc

            gc.collect()

            self.logger.info(f"Memoria optimizada para dispositivo {device}")
            return True
        except Exception as e:
            self.logger.error(f"Error optimizando memoria de {device}: {e}")
            return False

    def get_memory_usage(self, device: str) -> Dict[str, float]:
        """
        Obtener uso de memoria de un dispositivo

        Args:
            device: Dispositivo

        Returns:
            Dict: Información de uso de memoria
        """
        device_info = self.get_device_info(device)
        if not device_info:
            return {"total": 0, "used": 0, "available": 0}

        return {
            "total": device_info.memory_total,
            "used": device_info.memory_used,
            "available": device_info.memory_available,
        }

    def is_device_available(self, device: str) -> bool:
        """
        Verificar si un dispositivo está disponible

        Args:
            device: Dispositivo a verificar

        Returns:
            bool: True si está disponible
        """
        return device in self.devices and self.devices[device].is_available

    def get_device_capabilities(self, device: str) -> Dict[str, Any]:
        """
        Obtener capacidades de un dispositivo

        Args:
            device: Dispositivo

        Returns:
            Dict: Capacidades del dispositivo
        """
        device_info = self.get_device_info(device)
        if not device_info:
            return {}

        capabilities = {
            "type": device_info.type,
            "memory_total_gb": device_info.memory_total,
            "compute_capability": device_info.compute_capability,
        }

        if device.startswith("cuda:"):
            device_id = int(device.split(":")[1])
            device_props = torch.cuda.get_device_properties(device_id)
            capabilities.update(
                {
                    "multi_processor_count": device_props.multi_processor_count,
                    "max_threads_per_block": device_props.max_threads_per_block,
                    "max_shared_memory_per_block": device_props.max_shared_memory_per_block,
                }
            )

        return capabilities

    def set_device_memory_fraction(self, device: str, fraction: float) -> bool:
        """
        Establecer fracción de memoria a usar en un dispositivo

        Args:
            device: Dispositivo
            fraction: Fracción de memoria (0.0 - 1.0)

        Returns:
            bool: True si se estableció exitosamente
        """
        try:
            if device.startswith("cuda:"):
                device_id = int(device.split(":")[1])
                torch.cuda.set_per_process_memory_fraction(fraction, device_id)
                self.logger.info(
                    f"Fracción de memoria establecida en {fraction} para {device}"
                )
                return True
            else:
                self.logger.warning(
                    f"No se puede establecer fracción de memoria para {device}"
                )
                return False
        except Exception as e:
            self.logger.error(f"Error estableciendo fracción de memoria: {e}")
            return False

    def get_recommended_batch_size(self, device: str, model_size_gb: float) -> int:
        """
        Obtener tamaño de batch recomendado para un dispositivo y modelo

        Args:
            device: Dispositivo
            model_size_gb: Tamaño del modelo en GB

        Returns:
            int: Tamaño de batch recomendado
        """
        device_info = self.get_device_info(device)
        if not device_info:
            return 1

        # Estimación simple basada en memoria disponible
        available_memory = device_info.memory_available - model_size_gb
        if available_memory <= 0:
            return 1

        # Estimación: 1GB por batch
        recommended_batch_size = max(1, int(available_memory))

        # Límites por tipo de dispositivo
        if device.startswith("cuda:"):
            recommended_batch_size = min(recommended_batch_size, 32)
        elif device == "mps":
            recommended_batch_size = min(recommended_batch_size, 16)
        else:  # CPU
            recommended_batch_size = min(recommended_batch_size, 8)

        return recommended_batch_size
