#!/usr/bin/env python3
"""
Branch Adapters System
======================

Sistema de adaptadores para personalizar modelos según las ramas de conocimiento.
"""

import logging
from typing import Dict, List, Any, Optional
from dataclasses import dataclass
from datetime import datetime

logger = logging.getLogger(__name__)


@dataclass
class BranchAdapter:
    """Representa un adaptador de rama específico"""

    adapter_id: str
    branch_domain: str
    adapter_type: str
    parameters: Dict[str, Any]
    created_at: str
    is_active: bool = True


class BranchAdapters:
    """Gestor de adaptadores para ramas de conocimiento"""

    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.adapters_registry = {}
        self.active_adapters = {}
        self.initialized = False

        try:
            self._initialize_adapters()
            self.initialized = True
            self.logger.info("✅ BranchAdapters inicializado")
        except Exception as e:
            self.logger.error(f"❌ Error inicializando BranchAdapters: {e}")
            self.initialized = False

    def _initialize_adapters(self):
        """Inicializar adaptadores por defecto"""
        # Configuraciones de adaptadores para diferentes dominios
        adapter_configs = {
            "programming": {
                "temperature": 0.3,
                "max_tokens": 1024,
                "top_p": 0.9,
                "frequency_penalty": 0.1,
                "presence_penalty": 0.0,
                "special_instructions": "Focus on code accuracy and best practices",
            },
            "ai": {
                "temperature": 0.5,
                "max_tokens": 1536,
                "top_p": 0.8,
                "frequency_penalty": 0.0,
                "presence_penalty": 0.1,
                "special_instructions": "Provide detailed AI concepts and examples",
            },
            "database": {
                "temperature": 0.2,
                "max_tokens": 512,
                "top_p": 0.95,
                "frequency_penalty": 0.2,
                "presence_penalty": 0.0,
                "special_instructions": "Focus on SQL accuracy and data integrity",
            },
            "general": {
                "temperature": 0.7,
                "max_tokens": 1024,
                "top_p": 0.9,
                "frequency_penalty": 0.0,
                "presence_penalty": 0.0,
                "special_instructions": "Provide balanced and informative responses",
            },
        }

        # Crear adaptadores
        for domain, config in adapter_configs.items():
            adapter = BranchAdapter(
                adapter_id=f"adapter_{domain}",
                branch_domain=domain,
                adapter_type="parameter_tuning",
                parameters=config,
                created_at=datetime.now().isoformat(),
                is_active=True,
            )
            self.adapters_registry[domain] = adapter
            self.active_adapters[domain] = adapter

    def get_adapter(self, domain: str) -> Optional[BranchAdapter]:
        """Obtener adaptador para un dominio específico"""
        return self.active_adapters.get(domain)

    def activate_adapter(self, domain: str) -> bool:
        """Activar adaptador para un dominio"""
        if domain in self.adapters_registry:
            self.active_adapters[domain] = self.adapters_registry[domain]
            self.adapters_registry[domain].is_active = True
            self.logger.info(f"✅ Adaptador activado para dominio: {domain}")
            return True
        return False

    def deactivate_adapter(self, domain: str) -> bool:
        """Desactivar adaptador para un dominio"""
        if domain in self.active_adapters:
            self.adapters_registry[domain].is_active = False
            del self.active_adapters[domain]
            self.logger.info(f"🔴 Adaptador desactivado para dominio: {domain}")
            return True
        return False

    def update_adapter_parameters(
        self, domain: str, new_parameters: Dict[str, Any]
    ) -> bool:
        """Actualizar parámetros de un adaptador"""
        if domain in self.adapters_registry:
            adapter = self.adapters_registry[domain]
            adapter.parameters.update(new_parameters)
            self.logger.info(f"🔧 Parámetros actualizados para adaptador: {domain}")
            return True
        return False

    def create_custom_adapter(
        self, domain: str, adapter_type: str, parameters: Dict[str, Any]
    ) -> bool:
        """Crear un adaptador personalizado"""
        try:
            adapter = BranchAdapter(
                adapter_id=f"custom_{domain}_{len(self.adapters_registry)}",
                branch_domain=domain,
                adapter_type=adapter_type,
                parameters=parameters,
                created_at=datetime.now().isoformat(),
                is_active=False,
            )

            self.adapters_registry[f"custom_{domain}"] = adapter
            self.logger.info(f"✨ Adaptador personalizado creado: {adapter.adapter_id}")
            return True

        except Exception as e:
            self.logger.error(f"❌ Error creando adaptador personalizado: {e}")
            return False

    def get_active_adapters(self) -> Dict[str, BranchAdapter]:
        """Obtener todos los adaptadores activos"""
        return self.active_adapters.copy()

    def get_adapter_info(self, domain: str) -> Dict[str, Any]:
        """Obtener información detallada de un adaptador"""
        adapter = self.get_adapter(domain)
        if not adapter:
            return {"error": f"Adapter for domain {domain} not found"}

        return {
            "adapter_id": adapter.adapter_id,
            "branch_domain": adapter.branch_domain,
            "adapter_type": adapter.adapter_type,
            "parameters": adapter.parameters,
            "created_at": adapter.created_at,
            "is_active": adapter.is_active,
            "parameter_count": len(adapter.parameters),
        }

    def get_system_status(self) -> Dict[str, Any]:
        """Obtener estado del sistema de adaptadores"""
        return {
            "initialized": self.initialized,
            "total_adapters": len(self.adapters_registry),
            "active_adapters": len(self.active_adapters),
            "available_domains": list(self.adapters_registry.keys()),
            "active_domains": list(self.active_adapters.keys()),
            "timestamp": datetime.now().isoformat(),
        }

    def apply_adapter_settings(
        self, domain: str, base_config: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Aplicar configuraciones de adaptador a una configuración base"""
        adapter = self.get_adapter(domain)
        if not adapter or not adapter.is_active:
            return base_config

        # Combinar configuración base con parámetros del adaptador
        enhanced_config = base_config.copy()
        enhanced_config.update(adapter.parameters)

        # Agregar metadatos del adaptador
        enhanced_config["_adapter_info"] = {
            "adapter_id": adapter.adapter_id,
            "domain": domain,
            "applied_at": datetime.now().isoformat(),
        }

        return enhanced_config
