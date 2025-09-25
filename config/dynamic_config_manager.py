#!/usr/bin/env python3
"""
Gestor de Configuración Dinámica del Sistema NeuroFusion
Permite actualizar configuraciones en tiempo real sin reiniciar el sistema
"""

import json
import yaml
import logging
import asyncio
import threading
import time
from pathlib import Path
from typing import Dict, Any, List, Optional, Callable
from dataclasses import dataclass, asdict
from datetime import datetime
import hashlib
import os
import signal
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

# Configuración de logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@dataclass
class ConfigChangeEvent:
    """Evento de cambio de configuración"""

    config_name: str
    file_path: str
    old_hash: str
    new_hash: str
    timestamp: datetime
    changes: Dict[str, Any]


class ConfigFileWatcher(FileSystemEventHandler):
    """Observador de cambios en archivos de configuración"""

    def __init__(self, config_manager):
        self.config_manager = config_manager
        self.observer = Observer()

    def on_modified(self, event):
        if not event.is_directory and event.src_path.endswith(
            (".json", ".yml", ".yaml")
        ):
            logger.info(f"Archivo de configuración modificado: {event.src_path}")
            self.config_manager._handle_config_change(event.src_path)

    def start_watching(self, config_dir: str):
        """Inicia la observación de archivos de configuración"""
        self.observer.schedule(self, config_dir, recursive=False)
        self.observer.start()
        logger.info(f"Observador iniciado para: {config_dir}")

    def stop_watching(self):
        """Detiene la observación de archivos"""
        self.observer.stop()
        self.observer.join()
        logger.info("Observador detenido")


class DynamicConfigManager:
    """Gestor de configuración dinámica con capacidad de actualización en tiempo real"""

    def __init__(self, config_dir: str = "config"):
        self.config_dir = Path(config_dir)
        self.config_cache = {}
        self.config_hashes = {}
        self.config_callbacks = {}
        self.config_locks = {}
        self.watcher = ConfigFileWatcher(self)
        self.running = False

        # Cargar configuraciones iniciales
        self._load_all_configs()

        # Iniciar observador de archivos
        self._start_file_watcher()

    def _load_all_configs(self):
        """Carga todas las configuraciones del sistema"""
        try:
            config_files = [
                "neurofusion_config.json",
                "module_initialization.json",
                "rate_limits.json",
                "monitoring_config.json",
                "training_token_config.json",
                "sheily_token_config.json",
                "sheily_token_metadata.json",
                "advanced_training_config.json",
            ]

            for filename in config_files:
                self._load_config_file(filename)

            logger.info("Todas las configuraciones cargadas exitosamente")

        except Exception as e:
            logger.error(f"Error cargando configuraciones: {e}")
            raise

    def _load_config_file(self, filename: str):
        """Carga un archivo de configuración específico"""
        file_path = self.config_dir / filename

        if not file_path.exists():
            logger.warning(f"Archivo de configuración no encontrado: {file_path}")
            return

        try:
            with open(file_path, "r", encoding="utf-8") as f:
                if filename.endswith(".json"):
                    config_data = json.load(f)
                elif filename.endswith((".yml", ".yaml")):
                    config_data = yaml.safe_load(f)
                else:
                    logger.warning(f"Tipo de archivo no soportado: {filename}")
                    return

            # Calcular hash
            config_hash = hashlib.md5(
                json.dumps(config_data, sort_keys=True).encode()
            ).hexdigest()

            # Almacenar configuración
            config_name = (
                filename.replace(".json", "").replace(".yml", "").replace(".yaml", "")
            )
            self.config_cache[config_name] = config_data
            self.config_hashes[config_name] = config_hash

            # Crear lock para esta configuración
            if config_name not in self.config_locks:
                self.config_locks[config_name] = threading.Lock()

            logger.debug(f"Configuración cargada: {config_name}")

        except Exception as e:
            logger.error(f"Error cargando {filename}: {e}")

    def _start_file_watcher(self):
        """Inicia el observador de archivos de configuración"""
        try:
            self.watcher.start_watching(str(self.config_dir))
            self.running = True
            logger.info("Observador de archivos de configuración iniciado")
        except Exception as e:
            logger.error(f"Error iniciando observador: {e}")

    def _handle_config_change(self, file_path: str):
        """Maneja cambios en archivos de configuración"""
        try:
            filename = Path(file_path).name
            config_name = (
                filename.replace(".json", "").replace(".yml", "").replace(".yaml", "")
            )

            # Esperar un momento para asegurar que el archivo esté completamente escrito
            time.sleep(0.1)

            # Recargar configuración
            old_hash = self.config_hashes.get(config_name, "")
            self._load_config_file(filename)
            new_hash = self.config_hashes.get(config_name, "")

            if old_hash != new_hash:
                # Detectar cambios específicos
                changes = self._detect_config_changes(config_name, old_hash, new_hash)

                # Crear evento de cambio
                event = ConfigChangeEvent(
                    config_name=config_name,
                    file_path=file_path,
                    old_hash=old_hash,
                    new_hash=new_hash,
                    timestamp=datetime.now(),
                    changes=changes,
                )

                # Notificar callbacks
                self._notify_config_change(event)

                logger.info(f"Configuración actualizada: {config_name}")

        except Exception as e:
            logger.error(f"Error manejando cambio de configuración: {e}")

    def _detect_config_changes(
        self, config_name: str, old_hash: str, new_hash: str
    ) -> Dict[str, Any]:
        """Detecta cambios específicos en una configuración"""
        changes = {"added": {}, "modified": {}, "removed": {}}

        try:
            # Obtener configuración anterior del cache temporal
            old_config = self.config_cache.get(f"{config_name}_old", {})
            new_config = self.config_cache.get(config_name, {})

            # Comparar configuraciones
            all_keys = set(old_config.keys()) | set(new_config.keys())

            for key in all_keys:
                if key not in old_config:
                    changes["added"][key] = new_config[key]
                elif key not in new_config:
                    changes["removed"][key] = old_config[key]
                elif old_config[key] != new_config[key]:
                    changes["modified"][key] = {
                        "old": old_config[key],
                        "new": new_config[key],
                    }

        except Exception as e:
            logger.error(f"Error detectando cambios: {e}")

        return changes

    def _notify_config_change(self, event: ConfigChangeEvent):
        """Notifica cambios de configuración a los callbacks registrados"""
        if event.config_name in self.config_callbacks:
            callbacks = self.config_callbacks[event.config_name]
            for callback in callbacks:
                try:
                    callback(event)
                except Exception as e:
                    logger.error(f"Error en callback de configuración: {e}")

    def get_config(self, config_name: str) -> Dict[str, Any]:
        """Obtiene una configuración específica con bloqueo thread-safe"""
        if config_name not in self.config_locks:
            logger.warning(f"Configuración no encontrada: {config_name}")
            return {}

        with self.config_locks[config_name]:
            return self.config_cache.get(config_name, {}).copy()

    def set_config(self, config_name: str, config_data: Dict[str, Any]) -> bool:
        """Establece una configuración específica"""
        try:
            with self.config_locks.get(config_name, threading.Lock()):
                # Actualizar cache
                self.config_cache[config_name] = config_data.copy()

                # Calcular nuevo hash
                config_hash = hashlib.md5(
                    json.dumps(config_data, sort_keys=True).encode()
                ).hexdigest()
                old_hash = self.config_hashes.get(config_name, "")
                self.config_hashes[config_name] = config_hash

                # Guardar en archivo
                file_path = self.config_dir / f"{config_name}.json"
                with open(file_path, "w", encoding="utf-8") as f:
                    json.dump(config_data, f, indent=2, ensure_ascii=False)

                # Notificar cambios si el hash cambió
                if old_hash != config_hash:
                    changes = self._detect_config_changes(
                        config_name, old_hash, config_hash
                    )
                    event = ConfigChangeEvent(
                        config_name=config_name,
                        file_path=str(file_path),
                        old_hash=old_hash,
                        new_hash=config_hash,
                        timestamp=datetime.now(),
                        changes=changes,
                    )
                    self._notify_config_change(event)

                logger.info(f"Configuración actualizada: {config_name}")
                return True

        except Exception as e:
            logger.error(f"Error actualizando configuración {config_name}: {e}")
            return False

    def update_config_partial(self, config_name: str, updates: Dict[str, Any]) -> bool:
        """Actualiza parcialmente una configuración"""
        try:
            current_config = self.get_config(config_name)
            current_config.update(updates)
            return self.set_config(config_name, current_config)
        except Exception as e:
            logger.error(f"Error actualizando configuración parcial {config_name}: {e}")
            return False

    def register_config_callback(
        self, config_name: str, callback: Callable[[ConfigChangeEvent], None]
    ):
        """Registra un callback para cambios de configuración"""
        if config_name not in self.config_callbacks:
            self.config_callbacks[config_name] = []

        self.config_callbacks[config_name].append(callback)
        logger.info(f"Callback registrado para configuración: {config_name}")

    def unregister_config_callback(
        self, config_name: str, callback: Callable[[ConfigChangeEvent], None]
    ):
        """Desregistra un callback de configuración"""
        if config_name in self.config_callbacks:
            try:
                self.config_callbacks[config_name].remove(callback)
                logger.info(f"Callback desregistrado para configuración: {config_name}")
            except ValueError:
                logger.warning(
                    f"Callback no encontrado para configuración: {config_name}"
                )

    def get_config_hash(self, config_name: str) -> str:
        """Obtiene el hash de una configuración"""
        return self.config_hashes.get(config_name, "")

    def is_config_changed(self, config_name: str, previous_hash: str) -> bool:
        """Verifica si una configuración ha cambiado"""
        current_hash = self.get_config_hash(config_name)
        return current_hash != previous_hash

    def get_all_config_names(self) -> List[str]:
        """Obtiene la lista de todas las configuraciones disponibles"""
        return list(self.config_cache.keys())

    def get_config_summary(self) -> Dict[str, Any]:
        """Obtiene un resumen de todas las configuraciones"""
        summary = {}
        for config_name in self.config_cache.keys():
            config_data = self.get_config(config_name)
            summary[config_name] = {
                "hash": self.get_config_hash(config_name),
                "size": len(json.dumps(config_data)),
                "last_modified": datetime.now().isoformat(),
                "callbacks_count": len(self.config_callbacks.get(config_name, [])),
            }
        return summary

    def backup_config(self, config_name: str, backup_dir: str = None) -> str:
        """Crea un backup de una configuración específica"""
        if backup_dir is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_dir = f"config/backups/{config_name}_backup_{timestamp}"

        backup_path = Path(backup_dir)
        backup_path.mkdir(parents=True, exist_ok=True)

        try:
            config_data = self.get_config(config_name)
            backup_file = backup_path / f"{config_name}.json"

            with open(backup_file, "w", encoding="utf-8") as f:
                json.dump(config_data, f, indent=2, ensure_ascii=False)

            logger.info(f"Backup creado: {backup_file}")
            return str(backup_file)

        except Exception as e:
            logger.error(f"Error creando backup: {e}")
            raise

    def restore_config(self, config_name: str, backup_file: str) -> bool:
        """Restaura una configuración desde un backup"""
        try:
            backup_path = Path(backup_file)
            if not backup_path.exists():
                logger.error(f"Archivo de backup no encontrado: {backup_file}")
                return False

            with open(backup_path, "r", encoding="utf-8") as f:
                config_data = json.load(f)

            return self.set_config(config_name, config_data)

        except Exception as e:
            logger.error(f"Error restaurando configuración: {e}")
            return False

    def validate_config(self, config_name: str) -> Dict[str, Any]:
        """Valida una configuración específica"""
        validation_result = {"valid": True, "errors": [], "warnings": []}

        try:
            config_data = self.get_config(config_name)

            # Validaciones básicas
            if not config_data:
                validation_result["errors"].append("Configuración vacía")
                validation_result["valid"] = False

            # Validaciones específicas por tipo de configuración
            if config_name == "neurofusion_config":
                self._validate_main_config(config_data, validation_result)
            elif config_name == "module_initialization":
                self._validate_module_init_config(config_data, validation_result)
            elif config_name == "rate_limits":
                self._validate_rate_limits_config(config_data, validation_result)

        except Exception as e:
            validation_result["errors"].append(f"Error durante la validación: {e}")
            validation_result["valid"] = False

        return validation_result

    def _validate_main_config(self, config: Dict[str, Any], result: Dict[str, Any]):
        """Validaciones específicas para la configuración principal"""
        required_fields = ["system_name", "version", "components"]
        for field in required_fields:
            if field not in config:
                result["errors"].append(f"Campo requerido faltante: {field}")
                result["valid"] = False

    def _validate_module_init_config(
        self, config: Dict[str, Any], result: Dict[str, Any]
    ):
        """Validaciones específicas para la configuración de inicialización de módulos"""
        for module_name, module_config in config.items():
            if "dependencies" not in module_config:
                result["errors"].append(
                    f"Dependencias faltantes en módulo: {module_name}"
                )
                result["valid"] = False

    def _validate_rate_limits_config(
        self, config: Dict[str, Any], result: Dict[str, Any]
    ):
        """Validaciones específicas para la configuración de rate limits"""
        if "rules" not in config:
            result["errors"].append("Reglas de rate limit faltantes")
            result["valid"] = False

    def stop(self):
        """Detiene el gestor de configuración dinámica"""
        self.running = False
        self.watcher.stop_watching()
        logger.info("Gestor de configuración dinámica detenido")

    def __enter__(self):
        """Context manager entry"""
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit"""
        self.stop()


# Instancia global del gestor de configuración dinámica
dynamic_config_manager = DynamicConfigManager()


def get_dynamic_config_manager() -> DynamicConfigManager:
    """Obtiene la instancia global del gestor de configuración dinámica"""
    return dynamic_config_manager


# Ejemplo de uso de callbacks
def config_change_handler(event: ConfigChangeEvent):
    """Ejemplo de manejador de cambios de configuración"""
    logger.info(f"Configuración cambiada: {event.config_name}")
    logger.info(f"Cambios detectados: {event.changes}")


if __name__ == "__main__":
    # Ejemplo de uso
    manager = DynamicConfigManager()

    # Registrar callback para cambios
    manager.register_config_callback("neurofusion_config", config_change_handler)

    try:
        # Obtener configuración
        config = manager.get_config("neurofusion_config")
        print(f"Configuración actual: {config.get('system_name', 'N/A')}")

        # Actualizar configuración
        updates = {"debug_mode": True}
        success = manager.update_config_partial("neurofusion_config", updates)
        print(f"Actualización exitosa: {success}")

        # Mantener el sistema corriendo
        print("Gestor de configuración dinámica ejecutándose...")
        while manager.running:
            time.sleep(1)

    except KeyboardInterrupt:
        print("\nDeteniendo gestor de configuración...")
        manager.stop()
