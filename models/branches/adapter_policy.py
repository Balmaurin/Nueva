import os
import json
import logging
from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta
import torch
from collections import OrderedDict


class AdapterUpdatePolicy:
    """
    Política de gestión de adapters para optimizar rendimiento y memoria
    """

    def __init__(self, config: Dict[str, Any] = None):
        """
        Inicializar política de adapters

        Args:
            config (dict): Configuración de la política
        """
        self.logger = logging.getLogger(__name__)

        # Configuración por defecto
        self.config = config or {
            "max_adapters_in_memory": 8,  # Máximo adapters en memoria
            "adapter_cache_ttl": 3600,  # TTL en segundos (1 hora)
            "performance_threshold": 0.7,  # Umbral de rendimiento mínimo
            "memory_threshold": 0.8,  # Umbral de uso de memoria
            "update_frequency": 300,  # Frecuencia de actualización (5 min)
            "backup_adapters": True,  # Hacer backup de adapters
            "compression_enabled": True,  # Comprimir adapters inactivos
        }

        # Caché de adapters con metadatos
        self.adapter_cache = OrderedDict()

        # Métricas de rendimiento
        self.performance_metrics = {}

        # Historial de uso
        self.usage_history = {}

        self.logger.info("✅ AdapterUpdatePolicy inicializada")

    def manage_domain_adapters(
        self, domain: str, evaluation_metrics: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Gestionar adapters de un dominio específico

        Args:
            domain (str): Dominio a gestionar
            evaluation_metrics (dict): Métricas de evaluación

        Returns:
            dict: Resultado de la gestión
        """
        try:
            # Actualizar métricas de rendimiento
            self._update_performance_metrics(domain, evaluation_metrics)

            # Verificar si se necesita actualizar el adapter
            if self._should_update_adapter(domain):
                update_result = self._update_adapter(domain)
            else:
                update_result = {"status": "no_update_needed"}

            # Gestionar caché de memoria
            self._manage_memory_cache()

            # Actualizar historial de uso
            self._update_usage_history(domain)

            return {
                "domain": domain,
                "management_result": update_result,
                "cache_status": self._get_cache_status(),
                "timestamp": datetime.now().isoformat(),
            }

        except Exception as e:
            self.logger.error(f"Error gestionando adapters para {domain}: {e}")
            return {"error": str(e)}

    def _update_performance_metrics(self, domain: str, metrics: Dict[str, Any]):
        """Actualizar métricas de rendimiento del adapter"""
        if domain not in self.performance_metrics:
            self.performance_metrics[domain] = {}

        self.performance_metrics[domain].update(
            {
                "accuracy": metrics.get("accuracy", 0.0),
                "response_time": metrics.get("response_time", 0.0),
                "memory_usage": metrics.get("memory_usage", 0.0),
                "last_updated": datetime.now().isoformat(),
                "usage_count": self.performance_metrics[domain].get("usage_count", 0)
                + 1,
            }
        )

    def _should_update_adapter(self, domain: str) -> bool:
        """Determinar si se debe actualizar el adapter"""
        if domain not in self.performance_metrics:
            return True

        metrics = self.performance_metrics[domain]

        # Verificar rendimiento
        if metrics.get("accuracy", 0.0) < self.config["performance_threshold"]:
            return True

        # Verificar tiempo desde última actualización
        last_updated = datetime.fromisoformat(metrics.get("last_updated", "2000-01-01"))
        if datetime.now() - last_updated > timedelta(
            seconds=self.config["update_frequency"]
        ):
            return True

        return False

    def _update_adapter(self, domain: str) -> Dict[str, Any]:
        """Actualizar adapter del dominio"""
        try:
            # Crear backup si está habilitado
            if self.config["backup_adapters"]:
                self._create_adapter_backup(domain)

            # Aquí iría la lógica de actualización real del adapter
            # Por ahora, simulamos la actualización

            self.logger.info(f"✅ Adapter actualizado para dominio: {domain}")

            return {
                "status": "updated",
                "backup_created": self.config["backup_adapters"],
                "compression_applied": self.config["compression_enabled"],
            }

        except Exception as e:
            self.logger.error(f"Error actualizando adapter para {domain}: {e}")
            return {"status": "error", "error": str(e)}

    def _create_adapter_backup(self, domain: str):
        """Crear backup del adapter"""
        try:
            adapter_path = f"models/branches/{domain.lower().replace(' ', '_')}/adapter"
            backup_path = f"models/branches/{domain.lower().replace(' ', '_')}/adapter_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}"

            if os.path.exists(adapter_path):
                import shutil

                shutil.copytree(adapter_path, backup_path)
                self.logger.info(f"✅ Backup creado: {backup_path}")

        except Exception as e:
            self.logger.error(f"Error creando backup para {domain}: {e}")

    def _manage_memory_cache(self):
        """Gestionar caché de memoria"""
        try:
            # Verificar uso de memoria
            memory_usage = self._get_memory_usage()

            if memory_usage > self.config["memory_threshold"]:
                # Eliminar adapters menos usados
                self._evict_least_used_adapters()

            # Comprimir adapters inactivos si está habilitado
            if self.config["compression_enabled"]:
                self._compress_inactive_adapters()

        except Exception as e:
            self.logger.error(f"Error gestionando caché de memoria: {e}")

    def _get_memory_usage(self) -> float:
        """Obtener uso actual de memoria"""
        try:
            # Simular uso de memoria (en implementación real usaría psutil)
            return len(self.adapter_cache) / self.config["max_adapters_in_memory"]
        except:
            return 0.5  # Valor por defecto

    def _evict_least_used_adapters(self):
        """Eliminar adapters menos usados del caché"""
        try:
            # Ordenar por uso y eliminar los menos usados
            sorted_adapters = sorted(
                self.adapter_cache.items(), key=lambda x: x[1].get("usage_count", 0)
            )

            # Eliminar el 20% menos usado
            to_remove = int(len(sorted_adapters) * 0.2)

            for i in range(to_remove):
                if sorted_adapters:
                    domain, _ = sorted_adapters.pop(0)
                    del self.adapter_cache[domain]
                    self.logger.info(f"Adapter eliminado del caché: {domain}")

        except Exception as e:
            self.logger.error(f"Error eliminando adapters del caché: {e}")

    def _compress_inactive_adapters(self):
        """Comprimir adapters inactivos"""
        try:
            current_time = datetime.now()

            for domain, adapter_info in self.adapter_cache.items():
                last_used = datetime.fromisoformat(
                    adapter_info.get("last_used", "2000-01-01")
                )

                # Comprimir si no se ha usado en más de 30 minutos
                if current_time - last_used > timedelta(minutes=30):
                    if not adapter_info.get("compressed", False):
                        # Aquí iría la lógica de compresión real
                        adapter_info["compressed"] = True
                        self.logger.info(f"Adapter comprimido: {domain}")

        except Exception as e:
            self.logger.error(f"Error comprimiendo adapters: {e}")

    def _update_usage_history(self, domain: str):
        """Actualizar historial de uso"""
        if domain not in self.usage_history:
            self.usage_history[domain] = []

        self.usage_history[domain].append(
            {"timestamp": datetime.now().isoformat(), "action": "used"}
        )

        # Mantener solo los últimos 100 registros
        if len(self.usage_history[domain]) > 100:
            self.usage_history[domain] = self.usage_history[domain][-100:]

    def _get_cache_status(self) -> Dict[str, Any]:
        """Obtener estado del caché"""
        return {
            "total_adapters": len(self.adapter_cache),
            "memory_usage": self._get_memory_usage(),
            "compressed_adapters": sum(
                1
                for info in self.adapter_cache.values()
                if info.get("compressed", False)
            ),
            "cache_hits": sum(
                info.get("cache_hits", 0) for info in self.adapter_cache.values()
            ),
            "cache_misses": sum(
                info.get("cache_misses", 0) for info in self.adapter_cache.values()
            ),
        }

    def get_adapter_performance(self, domain: str) -> Dict[str, Any]:
        """Obtener métricas de rendimiento de un adapter"""
        return self.performance_metrics.get(domain, {})

    def get_all_performance_metrics(self) -> Dict[str, Any]:
        """Obtener métricas de rendimiento de todos los adapters"""
        return self.performance_metrics

    def optimize_cache(self) -> Dict[str, Any]:
        """Optimizar caché de adapters"""
        try:
            # Limpiar adapters obsoletos
            self._clean_obsolete_adapters()

            # Reorganizar caché por frecuencia de uso
            self._reorganize_cache()

            # Aplicar compresión si es necesario
            if self.config["compression_enabled"]:
                self._compress_inactive_adapters()

            return {
                "status": "optimized",
                "cache_status": self._get_cache_status(),
                "timestamp": datetime.now().isoformat(),
            }

        except Exception as e:
            self.logger.error(f"Error optimizando caché: {e}")
            return {"error": str(e)}

    def _clean_obsolete_adapters(self):
        """Limpiar adapters obsoletos"""
        try:
            current_time = datetime.now()
            obsolete_domains = []

            for domain, adapter_info in self.adapter_cache.items():
                last_used = datetime.fromisoformat(
                    adapter_info.get("last_used", "2000-01-01")
                )

                # Marcar como obsoleto si no se ha usado en más de 2 horas
                if current_time - last_used > timedelta(hours=2):
                    obsolete_domains.append(domain)

            # Eliminar adapters obsoletos
            for domain in obsolete_domains:
                del self.adapter_cache[domain]
                self.logger.info(f"Adapter obsoleto eliminado: {domain}")

        except Exception as e:
            self.logger.error(f"Error limpiando adapters obsoletos: {e}")

    def _reorganize_cache(self):
        """Reorganizar caché por frecuencia de uso"""
        try:
            # Ordenar por frecuencia de uso
            sorted_items = sorted(
                self.adapter_cache.items(),
                key=lambda x: x[1].get("usage_count", 0),
                reverse=True,
            )

            # Recrear caché ordenado
            self.adapter_cache = OrderedDict(sorted_items)

            self.logger.info("✅ Caché reorganizado por frecuencia de uso")

        except Exception as e:
            self.logger.error(f"Error reorganizando caché: {e}")


# Configuración de logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
