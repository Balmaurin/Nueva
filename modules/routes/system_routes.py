#!/usr/bin/env python3
"""
Sistema de Rutas y Órdenes
Conecta todos los módulos del sistema con rutas y comandos funcionales
"""

import os
import json
import logging
from datetime import datetime
from typing import Dict, Any, List, Optional, Tuple
from pathlib import Path
import asyncio
import threading
from dataclasses import dataclass, asdict

# Importar todos los gestores
from modules.cache.adapter_cache_manager import adapter_cache_manager
from modules.analysis.analysis_results_manager import analysis_results_manager
from modules.backup.backup_manager import backup_manager
from modules.branches.branch_manager import branch_manager
from modules.cache.cache_manager import cache_manager
from modules.config.config_manager import config_manager
from modules.data.data_manager import data_manager
from modules.datasets.dataset_manager import dataset_manager


@dataclass
class SystemCommand:
    """Estructura de datos para un comando del sistema"""

    id: str
    name: str
    description: str
    module: str
    function: str
    parameters: Dict[str, Any]
    created_at: datetime
    status: str = "pending"
    result: Any = None
    error: str = None


class SystemRoutes:
    """Sistema de rutas y órdenes para conectar todos los módulos"""

    def __init__(self):
        # Configurar logging
        self.logger = logging.getLogger(__name__)
        self.logger.setLevel(logging.INFO)

        # Inicializar gestores
        self.managers = {
            "adapter_cache": adapter_cache_manager,
            "analysis": analysis_results_manager,
            "backup": backup_manager,
            "branches": branch_manager,
            "cache": cache_manager,
            "config": config_manager,
            "data": data_manager,
            "datasets": dataset_manager,
        }

        # Comandos disponibles
        self.available_commands = self._register_commands()

        # Historial de comandos ejecutados
        self.command_history = []

        self.logger.info("✅ SystemRoutes inicializado")

    def _register_commands(self) -> Dict[str, Dict[str, Any]]:
        """Registrar todos los comandos disponibles"""
        commands = {
            # Comandos de Adapter Cache
            "adapter_cache_store": {
                "module": "adapter_cache",
                "function": "store_adapter",
                "description": "Almacenar adaptador en cache",
                "parameters": [
                    "adapter_id",
                    "adapter_data",
                    "model_name",
                    "branch_name",
                ],
            },
            "adapter_cache_get": {
                "module": "adapter_cache",
                "function": "get_adapter",
                "description": "Obtener adaptador del cache",
                "parameters": ["adapter_id"],
            },
            "adapter_cache_list": {
                "module": "adapter_cache",
                "function": "list_adapters",
                "description": "Listar adaptadores en cache",
                "parameters": ["model_name", "branch_name", "limit"],
            },
            "adapter_cache_clear": {
                "module": "adapter_cache",
                "function": "clear_cache",
                "description": "Limpiar cache de adaptadores",
                "parameters": ["model_name", "branch_name"],
            },
            # Comandos de Análisis
            "analysis_create": {
                "module": "analysis",
                "function": "create_analysis",
                "description": "Crear nuevo análisis",
                "parameters": [
                    "analysis_type",
                    "model_name",
                    "branch_name",
                    "data",
                    "metrics",
                ],
            },
            "analysis_get": {
                "module": "analysis",
                "function": "get_analysis",
                "description": "Obtener análisis por ID",
                "parameters": ["analysis_id"],
            },
            "analysis_list": {
                "module": "analysis",
                "function": "list_analyses",
                "description": "Listar análisis",
                "parameters": ["analysis_type", "model_name", "limit"],
            },
            "analysis_export": {
                "module": "analysis",
                "function": "export_analysis",
                "description": "Exportar análisis",
                "parameters": ["analysis_id", "format", "export_path"],
            },
            # Comandos de Backup
            "backup_create": {
                "module": "backup",
                "function": "create_backup",
                "description": "Crear backup del sistema",
                "parameters": [
                    "backup_type",
                    "custom_paths",
                    "compression",
                    "description",
                ],
            },
            "backup_list": {
                "module": "backup",
                "function": "list_backups",
                "description": "Listar backups disponibles",
                "parameters": ["backup_type", "limit"],
            },
            "backup_restore": {
                "module": "backup",
                "function": "restore_backup",
                "description": "Restaurar backup",
                "parameters": ["backup_id", "restore_path", "verify_checksum"],
            },
            "backup_verify": {
                "module": "backup",
                "function": "verify_backup",
                "description": "Verificar integridad de backup",
                "parameters": ["backup_id"],
            },
            # Comandos de Branches
            "branch_create": {
                "module": "branches",
                "function": "create_branch",
                "description": "Crear nueva rama de conocimiento",
                "parameters": [
                    "name",
                    "description",
                    "category",
                    "keywords",
                    "model_name",
                    "config",
                    "metadata",
                ],
            },
            "branch_get": {
                "module": "branches",
                "function": "get_branch",
                "description": "Obtener rama por ID",
                "parameters": ["branch_id"],
            },
            "branch_list": {
                "module": "branches",
                "function": "list_branches",
                "description": "Listar ramas",
                "parameters": ["category", "status", "limit"],
            },
            "branch_update": {
                "module": "branches",
                "function": "update_branch",
                "description": "Actualizar rama",
                "parameters": ["branch_id", "updates"],
            },
            "branch_delete": {
                "module": "branches",
                "function": "delete_branch",
                "description": "Eliminar rama",
                "parameters": ["branch_id", "permanent"],
            },
            # Comandos de Cache
            "cache_set": {
                "module": "cache",
                "function": "set",
                "description": "Almacenar en cache",
                "parameters": ["key", "value", "cache_type", "ttl_hours", "metadata"],
            },
            "cache_get": {
                "module": "cache",
                "function": "get",
                "description": "Obtener de cache",
                "parameters": ["key", "cache_type"],
            },
            "cache_delete": {
                "module": "cache",
                "function": "delete",
                "description": "Eliminar de cache",
                "parameters": ["key", "cache_type"],
            },
            "cache_clear": {
                "module": "cache",
                "function": "clear",
                "description": "Limpiar cache",
                "parameters": ["cache_type"],
            },
            "cache_stats": {
                "module": "cache",
                "function": "get_cache_stats",
                "description": "Obtener estadísticas de cache",
                "parameters": [],
            },
            # Comandos de Configuración
            "config_get": {
                "module": "config",
                "function": "get_config",
                "description": "Obtener configuración",
                "parameters": ["section", "key"],
            },
            "config_set": {
                "module": "config",
                "function": "set_config",
                "description": "Establecer configuración",
                "parameters": ["section", "key", "value", "save_to_file"],
            },
            "config_load": {
                "module": "config",
                "function": "load_config_file",
                "description": "Cargar archivo de configuración",
                "parameters": ["file_path", "config_type"],
            },
            "config_export": {
                "module": "config",
                "function": "export_config",
                "description": "Exportar configuración",
                "parameters": ["section", "format", "export_path"],
            },
            "config_validate": {
                "module": "config",
                "function": "validate_config",
                "description": "Validar configuración",
                "parameters": ["section"],
            },
            # Comandos de Datos
            "data_store": {
                "module": "data",
                "function": "store_data",
                "description": "Almacenar datos",
                "parameters": [
                    "content",
                    "data_type",
                    "source",
                    "embedding",
                    "metadata",
                ],
            },
            "data_get": {
                "module": "data",
                "function": "get_data",
                "description": "Obtener datos por ID",
                "parameters": ["record_id"],
            },
            "data_search": {
                "module": "data",
                "function": "search_data",
                "description": "Buscar datos por texto",
                "parameters": ["query", "limit", "data_type"],
            },
            "data_search_similar": {
                "module": "data",
                "function": "search_similar",
                "description": "Buscar datos similares",
                "parameters": ["embedding", "limit"],
            },
            "data_store_embedding": {
                "module": "data",
                "function": "store_embedding",
                "description": "Almacenar embedding",
                "parameters": [
                    "content",
                    "embedding",
                    "model_type",
                    "domain",
                    "quality_score",
                    "metadata",
                ],
            },
            "data_store_interaction": {
                "module": "data",
                "function": "store_user_interaction",
                "description": "Almacenar interacción de usuario",
                "parameters": [
                    "user_id",
                    "session_id",
                    "interaction_type",
                    "content",
                    "response",
                    "duration_ms",
                    "metadata",
                ],
            },
            "data_stats": {
                "module": "data",
                "function": "get_data_stats",
                "description": "Obtener estadísticas de datos",
                "parameters": [],
            },
            # Comandos de Datasets
            "dataset_load": {
                "module": "datasets",
                "function": "load_dataset",
                "description": "Cargar dataset desde archivo",
                "parameters": [
                    "file_path",
                    "name",
                    "description",
                    "target_dir",
                    "metadata",
                ],
            },
            "dataset_get": {
                "module": "datasets",
                "function": "get_dataset",
                "description": "Obtener dataset por ID",
                "parameters": ["dataset_id"],
            },
            "dataset_list": {
                "module": "datasets",
                "function": "list_datasets",
                "description": "Listar datasets",
                "parameters": ["format", "status", "limit"],
            },
            "dataset_read": {
                "module": "datasets",
                "function": "read_dataset",
                "description": "Leer dataset como DataFrame",
                "parameters": ["dataset_id", "limit", "columns"],
            },
            "dataset_process": {
                "module": "datasets",
                "function": "process_dataset",
                "description": "Procesar dataset",
                "parameters": ["dataset_id", "processing_config"],
            },
            "dataset_split": {
                "module": "datasets",
                "function": "split_dataset",
                "description": "Dividir dataset",
                "parameters": ["dataset_id", "split_config"],
            },
            "dataset_export": {
                "module": "datasets",
                "function": "export_dataset",
                "description": "Exportar dataset",
                "parameters": ["dataset_id", "format", "export_path"],
            },
            "dataset_create_conversations": {
                "module": "datasets",
                "function": "create_conversation_dataset",
                "description": "Crear dataset de conversaciones",
                "parameters": ["conversations", "name", "description"],
            },
        }

        return commands

    def execute_command(self, command_name: str, **kwargs) -> Dict[str, Any]:
        """Ejecutar comando específico"""
        try:
            if command_name not in self.available_commands:
                raise ValueError(f"Comando no encontrado: {command_name}")

            command_info = self.available_commands[command_name]
            module_name = command_info["module"]
            function_name = command_info["function"]

            if module_name not in self.managers:
                raise ValueError(f"Módulo no encontrado: {module_name}")

            manager = self.managers[module_name]

            if not hasattr(manager, function_name):
                raise ValueError(
                    f"Función no encontrada: {function_name} en {module_name}"
                )

            function = getattr(manager, function_name)

            # Ejecutar función
            result = function(**kwargs)

            # Registrar comando ejecutado
            command = SystemCommand(
                id=f"cmd_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
                name=command_name,
                description=command_info["description"],
                module=module_name,
                function=function_name,
                parameters=kwargs,
                created_at=datetime.now(),
                status="completed",
                result=result,
            )

            self.command_history.append(command)

            self.logger.info(f"✅ Comando ejecutado: {command_name}")

            return {
                "success": True,
                "command_id": command.id,
                "result": result,
                "execution_time": datetime.now().isoformat(),
            }

        except Exception as e:
            self.logger.error(f"❌ Error ejecutando comando {command_name}: {e}")

            # Registrar comando fallido
            command = SystemCommand(
                id=f"cmd_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
                name=command_name,
                description=command_info.get("description", ""),
                module=command_info.get("module", ""),
                function=command_info.get("function", ""),
                parameters=kwargs,
                created_at=datetime.now(),
                status="failed",
                error=str(e),
            )

            self.command_history.append(command)

            return {
                "success": False,
                "command_id": command.id,
                "error": str(e),
                "execution_time": datetime.now().isoformat(),
            }

    def get_available_commands(self) -> Dict[str, Dict[str, Any]]:
        """Obtener lista de comandos disponibles"""
        return self.available_commands

    def get_command_history(self, limit: int = 100) -> List[Dict[str, Any]]:
        """Obtener historial de comandos"""
        history = []
        for command in self.command_history[-limit:]:
            history.append(asdict(command))
        return history

    def get_system_status(self) -> Dict[str, Any]:
        """Obtener estado general del sistema"""
        status = {
            "timestamp": datetime.now().isoformat(),
            "modules": {},
            "total_commands_executed": len(self.command_history),
            "successful_commands": len(
                [c for c in self.command_history if c.status == "completed"]
            ),
            "failed_commands": len(
                [c for c in self.command_history if c.status == "failed"]
            ),
        }

        # Obtener estado de cada módulo
        for module_name, manager in self.managers.items():
            try:
                if hasattr(manager, "get_stats"):
                    stats = manager.get_stats()
                    status["modules"][module_name] = {
                        "status": "active",
                        "stats": stats,
                    }
                else:
                    status["modules"][module_name] = {"status": "active", "stats": {}}
            except Exception as e:
                status["modules"][module_name] = {"status": "error", "error": str(e)}

        return status

    def run_system_health_check(self) -> Dict[str, Any]:
        """Ejecutar verificación de salud del sistema"""
        health_check = {
            "timestamp": datetime.now().isoformat(),
            "overall_status": "healthy",
            "checks": {},
        }

        # Verificar cada módulo
        for module_name, manager in self.managers.items():
            try:
                # Verificar que el módulo responde
                if hasattr(manager, "get_stats"):
                    stats = manager.get_stats()
                    health_check["checks"][module_name] = {
                        "status": "healthy",
                        "stats": stats,
                    }
                else:
                    health_check["checks"][module_name] = {
                        "status": "warning",
                        "message": "No tiene método get_stats",
                    }
            except Exception as e:
                health_check["checks"][module_name] = {
                    "status": "unhealthy",
                    "error": str(e),
                }
                health_check["overall_status"] = "unhealthy"

        return health_check

    def execute_batch_commands(
        self, commands: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """Ejecutar múltiples comandos en lote"""
        results = []

        for command_data in commands:
            command_name = command_data.get("command")
            parameters = command_data.get("parameters", {})

            if command_name:
                result = self.execute_command(command_name, **parameters)
                results.append(
                    {
                        "command": command_name,
                        "parameters": parameters,
                        "result": result,
                    }
                )

        return results

    def get_module_commands(self, module_name: str) -> Dict[str, Dict[str, Any]]:
        """Obtener comandos disponibles para un módulo específico"""
        module_commands = {}

        for command_name, command_info in self.available_commands.items():
            if command_info["module"] == module_name:
                module_commands[command_name] = command_info

        return module_commands

    def search_commands(self, query: str) -> Dict[str, Dict[str, Any]]:
        """Buscar comandos por texto"""
        matching_commands = {}
        query_lower = query.lower()

        for command_name, command_info in self.available_commands.items():
            if (
                query_lower in command_name.lower()
                or query_lower in command_info["description"].lower()
                or query_lower in command_info["module"].lower()
            ):
                matching_commands[command_name] = command_info

        return matching_commands


# Instancia global del sistema de rutas
system_routes = SystemRoutes()
