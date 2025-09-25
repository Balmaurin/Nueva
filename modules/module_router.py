"""
Enrutador Principal de Módulos para Sheily AI
============================================

Este módulo proporciona una interfaz unificada para que el LLM pueda acceder
a todos los módulos del sistema de manera sencilla y organizada.
"""

import asyncio
import logging
from typing import Dict, Any, Optional, List, Union
from dataclasses import dataclass
from datetime import datetime
import json
import inspect

from . import (
    UnifiedModuleSystem,
    get_module,
    list_modules,
    get_module_info,
    execute_module_function,
)

logger = logging.getLogger(__name__)


@dataclass
class ModuleRequest:
    """Solicitud de uso de módulo"""

    module_name: str
    function_name: str
    parameters: Dict[str, Any]
    user_id: Optional[str] = None
    session_id: Optional[str] = None
    priority: str = "normal"  # low, normal, high, critical
    timeout: int = 30


@dataclass
class ModuleResponse:
    """Respuesta de módulo"""

    success: bool
    data: Any
    error_message: Optional[str] = None
    execution_time: float = 0.0
    module_used: str = ""
    function_called: str = ""


class ModuleRouter:
    """Enrutador principal para acceso a módulos"""

    def __init__(self):
        self.system = UnifiedModuleSystem()
        self.initialized = False
        self.usage_stats = {}
        self.error_log = []

    async def initialize(self):
        """Inicializar el sistema de módulos"""
        if not self.initialized:
            await self.system.initialize()
            self.initialized = True
            logger.info("✅ Enrutador de módulos inicializado")

    def get_available_modules(self, category: str = None) -> Dict[str, Any]:
        """Obtener módulos disponibles"""
        return self.system.list_modules(category)

    def get_module_documentation(self, module_name: str) -> Optional[Dict[str, Any]]:
        """Obtener documentación de un módulo"""
        module_info = self.system.get_module_info(module_name)
        if not module_info:
            return None

        module_instance = self.system.get_module(module_name)
        if not module_instance:
            return module_info

        # Obtener métodos disponibles
        methods = []
        for name, method in inspect.getmembers(module_instance, inspect.ismethod):
            if not name.startswith("_"):
                methods.append(
                    {
                        "name": name,
                        "signature": str(inspect.signature(method)),
                        "doc": method.__doc__ or "Sin documentación",
                    }
                )

        return {**module_info, "methods": methods, "total_methods": len(methods)}

    async def execute_module_request(self, request: ModuleRequest) -> ModuleResponse:
        """Ejecutar una solicitud de módulo"""
        start_time = datetime.now()

        try:
            # Verificar que el módulo existe
            module_info = self.system.get_module_info(request.module_name)
            if not module_info:
                return ModuleResponse(
                    success=False,
                    data=None,
                    error_message=f"Módulo '{request.module_name}' no encontrado",
                    module_used=request.module_name,
                    function_called=request.function_name,
                )

            # Ejecutar la función
            result = await self.system.execute_module_function(
                request.module_name, request.function_name, **request.parameters
            )

            execution_time = (datetime.now() - start_time).total_seconds()

            # Registrar uso
            self._log_usage(request.module_name, request.function_name, execution_time)

            return ModuleResponse(
                success=True,
                data=result,
                execution_time=execution_time,
                module_used=request.module_name,
                function_called=request.function_name,
            )

        except Exception as e:
            execution_time = (datetime.now() - start_time).total_seconds()
            error_msg = f"Error ejecutando {request.module_name}.{request.function_name}: {str(e)}"

            # Registrar error
            self._log_error(request.module_name, request.function_name, str(e))

            return ModuleResponse(
                success=False,
                data=None,
                error_message=error_msg,
                execution_time=execution_time,
                module_used=request.module_name,
                function_called=request.function_name,
            )

    def _log_usage(self, module_name: str, function_name: str, execution_time: float):
        """Registrar uso de módulo"""
        key = f"{module_name}.{function_name}"
        if key not in self.usage_stats:
            self.usage_stats[key] = {
                "calls": 0,
                "total_time": 0.0,
                "avg_time": 0.0,
                "last_used": None,
            }

        stats = self.usage_stats[key]
        stats["calls"] += 1
        stats["total_time"] += execution_time
        stats["avg_time"] = stats["total_time"] / stats["calls"]
        stats["last_used"] = datetime.now()

    def _log_error(self, module_name: str, function_name: str, error: str):
        """Registrar error de módulo"""
        self.error_log.append(
            {
                "timestamp": datetime.now(),
                "module": module_name,
                "function": function_name,
                "error": error,
            }
        )

        # Mantener solo los últimos 100 errores
        if len(self.error_log) > 100:
            self.error_log = self.error_log[-100:]

    def get_usage_statistics(self) -> Dict[str, Any]:
        """Obtener estadísticas de uso"""
        return {
            "usage_stats": self.usage_stats,
            "error_count": len(self.error_log),
            "recent_errors": self.error_log[-10:] if self.error_log else [],
        }

    def get_module_categories(self) -> List[str]:
        """Obtener categorías de módulos disponibles"""
        return list(self.system.registry.categories.keys())

    def search_modules(self, query: str) -> List[Dict[str, Any]]:
        """Buscar módulos por nombre o descripción"""
        results = []
        query_lower = query.lower()

        for module_name, module_info in self.system.registry.modules.items():
            if (
                query_lower in module_name.lower()
                or query_lower in module_info.description.lower()
                or query_lower in module_info.category.lower()
            ):
                results.append(
                    {
                        "name": module_name,
                        "category": module_info.category,
                        "description": module_info.description,
                        "class": module_info.class_name,
                    }
                )

        return results


class LLMModuleInterface:
    """Interfaz simplificada para uso desde el LLM"""

    def __init__(self):
        self.router = ModuleRouter()
        self.initialized = False

    async def initialize(self):
        """Inicializar la interfaz"""
        await self.router.initialize()
        self.initialized = True

    async def call_module(
        self, module_name: str, function_name: str, **kwargs
    ) -> Dict[str, Any]:
        """Llamar a un módulo específico"""
        if not self.initialized:
            await self.initialize()

        request = ModuleRequest(
            module_name=module_name, function_name=function_name, parameters=kwargs
        )

        response = await self.router.execute_module_request(request)

        return {
            "success": response.success,
            "data": response.data,
            "error": response.error_message,
            "execution_time": response.execution_time,
            "module": response.module_used,
            "function": response.function_called,
        }

    def list_modules(self, category: str = None) -> Dict[str, Any]:
        """Listar módulos disponibles"""
        return self.router.get_available_modules(category)

    def get_module_info(self, module_name: str) -> Optional[Dict[str, Any]]:
        """Obtener información de un módulo"""
        return self.router.get_module_documentation(module_name)

    def search_modules(self, query: str) -> List[Dict[str, Any]]:
        """Buscar módulos"""
        return self.router.search_modules(query)

    def get_categories(self) -> List[str]:
        """Obtener categorías disponibles"""
        return self.router.get_module_categories()

    def get_usage_stats(self) -> Dict[str, Any]:
        """Obtener estadísticas de uso"""
        return self.router.get_usage_statistics()


# Instancia global para uso directo
llm_interface = LLMModuleInterface()


# Funciones de conveniencia para el LLM
async def call_module(module_name: str, function_name: str, **kwargs) -> Dict[str, Any]:
    """Función de conveniencia para llamar módulos"""
    return await llm_interface.call_module(module_name, function_name, **kwargs)


def get_modules(category: str = None) -> Dict[str, Any]:
    """Función de conveniencia para listar módulos"""
    return llm_interface.list_modules(category)


def get_module_docs(module_name: str) -> Optional[Dict[str, Any]]:
    """Función de conveniencia para obtener documentación"""
    return llm_interface.get_module_info(module_name)


def search_modules(query: str) -> List[Dict[str, Any]]:
    """Función de conveniencia para buscar módulos"""
    return llm_interface.search_modules(query)


def get_categories() -> List[str]:
    """Función de conveniencia para obtener categorías"""
    return llm_interface.get_categories()


def get_stats() -> Dict[str, Any]:
    """Función de conveniencia para obtener estadísticas"""
    return llm_interface.get_usage_stats()


# Ejemplo de uso para el LLM
async def example_usage():
    """Ejemplo de cómo usar la interfaz desde el LLM"""

    # Inicializar
    await llm_interface.initialize()

    # Listar módulos disponibles
    modules = get_modules()
    print("Módulos disponibles:", json.dumps(modules, indent=2, default=str))

    # Buscar módulos específicos
    ai_modules = search_modules("ai")
    print("Módulos de IA:", json.dumps(ai_modules, indent=2, default=str))

    # Obtener información de un módulo
    module_info = get_module_docs("text_processor")
    if module_info:
        print(
            "Info del procesador de texto:",
            json.dumps(module_info, indent=2, default=str),
        )

    # Llamar a un módulo
    try:
        result = await call_module(
            "text_processor", "clean_text", text="  Hola mundo!  "
        )
        print("Resultado:", json.dumps(result, indent=2, default=str))
    except Exception as e:
        print(f"Error: {e}")


if __name__ == "__main__":
    asyncio.run(example_usage())
