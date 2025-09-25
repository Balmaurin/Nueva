import os
import json
import logging
from datetime import datetime
from typing import Dict, Any, List, Optional


class ModuleRegistry:
    """
    Sistema de registro y monitoreo de módulos de NeuroFusion

    Características:
    - Registro de módulos con metadatos
    - Seguimiento de versiones
    - Registro de eventos de módulos
    - Generación de informes de estado
    """

    def __init__(self, registry_path: str = "module_registry.json"):
        """
        Inicializar registro de módulos

        Args:
            registry_path (str): Ruta para guardar el registro de módulos
        """
        self.registry_path = registry_path
        self.logger = logging.getLogger(__name__)
        self.modules: Dict[str, Dict[str, Any]] = {}
        self.event_log: List[Dict[str, Any]] = []

        # Cargar registro existente
        self._load_registry()

    def _load_registry(self):
        """Cargar registro de módulos desde archivo"""
        try:
            if os.path.exists(self.registry_path):
                with open(self.registry_path, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    self.modules = data.get("modules", {})
                    self.event_log = data.get("event_log", [])
        except Exception as e:
            self.logger.warning(f"No se pudo cargar el registro: {e}")

    def _save_registry(self):
        """Guardar registro de módulos en archivo"""
        try:
            data = {
                "modules": self.modules,
                "event_log": self.event_log,
                "last_updated": datetime.now().isoformat(),
            }
            with open(self.registry_path, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
        except Exception as e:
            self.logger.error(f"Error guardando registro: {e}")

    def register_module(
        self,
        module_name: str,
        module_path: str,
        module_type: str = "generic",
        version: str = "1.0.0",
        dependencies: Optional[List[str]] = None,
    ):
        """
        Registrar un nuevo módulo

        Args:
            module_name (str): Nombre del módulo
            module_path (str): Ruta del módulo
            module_type (str): Tipo de módulo
            version (str): Versión del módulo
            dependencies (List[str], opcional): Dependencias del módulo
        """
        module_info = {
            "name": module_name,
            "path": module_path,
            "type": module_type,
            "version": version,
            "dependencies": dependencies or [],
            "registered_at": datetime.now().isoformat(),
            "last_loaded": None,
            "load_count": 0,
            "status": "registered",
        }

        self.modules[module_name] = module_info
        self._log_event("module_registered", module_info)
        self._save_registry()

    def update_module_status(
        self,
        module_name: str,
        status: str = "active",
        additional_info: Optional[Dict[str, Any]] = None,
    ):
        """
        Actualizar estado de un módulo

        Args:
            module_name (str): Nombre del módulo
            status (str): Nuevo estado del módulo
            additional_info (dict, opcional): Información adicional
        """
        if module_name in self.modules:
            self.modules[module_name]["status"] = status
            self.modules[module_name]["last_updated"] = datetime.now().isoformat()

            if additional_info:
                self.modules[module_name].update(additional_info)

            self._log_event(
                "module_status_updated",
                {
                    "module": module_name,
                    "status": status,
                    "additional_info": additional_info,
                },
            )
            self._save_registry()

    def log_module_load(self, module_name: str):
        """
        Registrar carga de un módulo

        Args:
            module_name (str): Nombre del módulo
        """
        if module_name in self.modules:
            self.modules[module_name]["last_loaded"] = datetime.now().isoformat()
            self.modules[module_name]["load_count"] = (
                self.modules[module_name].get("load_count", 0) + 1
            )

            self._log_event(
                "module_loaded",
                {
                    "module": module_name,
                    "load_count": self.modules[module_name]["load_count"],
                },
            )
            self._save_registry()

    def _log_event(self, event_type: str, event_data: Dict[str, Any]):
        """
        Registrar un evento en el registro de eventos

        Args:
            event_type (str): Tipo de evento
            event_data (dict): Datos del evento
        """
        event = {
            "type": event_type,
            "timestamp": datetime.now().isoformat(),
            "data": event_data,
        }
        self.event_log.append(event)

        # Limitar tamaño del registro de eventos
        if len(self.event_log) > 1000:
            self.event_log = self.event_log[-1000:]

    def get_module_info(self, module_name: str) -> Optional[Dict[str, Any]]:
        """
        Obtener información de un módulo

        Args:
            module_name (str): Nombre del módulo

        Returns:
            Información del módulo o None
        """
        return self.modules.get(module_name)

    def get_modules_by_type(self, module_type: str) -> List[Dict[str, Any]]:
        """
        Obtener módulos por tipo

        Args:
            module_type (str): Tipo de módulo

        Returns:
            Lista de módulos del tipo especificado
        """
        return [
            module_info
            for module_info in self.modules.values()
            if module_info["type"] == module_type
        ]

    def generate_module_report(self) -> Dict[str, Any]:
        """
        Generar informe de estado de módulos

        Returns:
            Informe de estado de módulos
        """
        report = {
            "total_modules": len(self.modules),
            "module_types": {},
            "module_status": {},
            "recent_events": self.event_log[-10:],  # Últimos 10 eventos
        }

        for module_info in self.modules.values():
            # Contar tipos de módulos
            report["module_types"][module_info["type"]] = (
                report["module_types"].get(module_info["type"], 0) + 1
            )

            # Contar estados de módulos
            report["module_status"][module_info["status"]] = (
                report["module_status"].get(module_info["status"], 0) + 1
            )

        return report

    def clear_registry(self):
        """Limpiar registro de módulos"""
        self.modules.clear()
        self.event_log.clear()
        self._save_registry()
        self.logger.info("Registro de módulos limpiado")


def main():
    """Demostración del registro de módulos"""
    registry = ModuleRegistry()

    # Registrar algunos módulos de ejemplo
    registry.register_module(
        "ContextualReasoningEngine",
        "shaili-ai/modules/core/neurofusion_core.py",
        module_type="ai_component",
        version="2.1.0",
        dependencies=["embedding_system"],
    )

    registry.register_module(
        "EmbeddingSystem",
        "shaili-ai/modules/embeddings/semantic_search_engine.py",
        module_type="embedding",
        version="1.5.0",
    )

    # Simular carga de módulos
    registry.log_module_load("ContextualReasoningEngine")
    registry.log_module_load("EmbeddingSystem")

    # Actualizar estado de un módulo
    registry.update_module_status(
        "ContextualReasoningEngine",
        status="active",
        additional_info={"performance": 0.95},
    )

    # Generar informe
    report = registry.generate_module_report()
    print("Informe de módulos:", json.dumps(report, indent=2))


if __name__ == "__main__":
    main()
