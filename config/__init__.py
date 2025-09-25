#!/usr/bin/env python3
"""
Módulo de Configuración del Sistema NeuroFusion
Proporciona acceso centralizado a todas las configuraciones del sistema
"""

import os
import sys
from pathlib import Path

# Agregar el directorio actual al path para importaciones
current_dir = Path(__file__).parent
if str(current_dir) not in sys.path:
    sys.path.insert(0, str(current_dir))

# Importar los gestores de configuración
try:
    from .config_manager import ConfigManager, get_config_manager
    from .config_validator import ConfigValidator
    from .dynamic_config_manager import (
        DynamicConfigManager,
        get_dynamic_config_manager,
        ConfigChangeEvent,
    )
except ImportError as e:
    print(f"Error importando módulos de configuración: {e}")

    # Crear versiones mínimas si no se pueden importar
    class ConfigManager:
        def __init__(self):
            pass

        def get_config(self, name):
            return {}

    class ConfigValidator:
        def __init__(self):
            pass

        def validate_all_configs(self):
            return []

    class DynamicConfigManager:
        def __init__(self):
            pass

        def get_config(self, name):
            return {}

    class ConfigChangeEvent:
        def __init__(self):
            pass


# Versión del módulo
__version__ = "3.1.0"
__author__ = "NeuroFusion Team"
__description__ = "Sistema de Configuración NeuroFusion"

# Configuración por defecto
DEFAULT_CONFIG_DIR = "config"
DEFAULT_CONFIG_FILES = [
    "neurofusion_config.json",
    "module_initialization.json",
    "rate_limits.json",
    "monitoring_config.json",
    "training_token_config.json",
    "sheily_token_config.json",
    "sheily_token_metadata.json",
    "advanced_training_config.json",
    "docker-compose.yml",
    "docker-compose.dev.yml",
]

# Instancias globales
_config_manager = None
_dynamic_config_manager = None
_config_validator = None


def get_config_manager_instance() -> ConfigManager:
    """Obtiene la instancia global del gestor de configuración"""
    global _config_manager
    if _config_manager is None:
        _config_manager = ConfigManager()
    return _config_manager


def get_dynamic_config_manager_instance() -> DynamicConfigManager:
    """Obtiene la instancia global del gestor de configuración dinámica"""
    global _dynamic_config_manager
    if _dynamic_config_manager is None:
        _dynamic_config_manager = DynamicConfigManager()
    return _dynamic_config_manager


def get_config_validator_instance() -> ConfigValidator:
    """Obtiene la instancia global del validador de configuración"""
    global _config_validator
    if _config_validator is None:
        _config_validator = ConfigValidator()
    return _config_validator


def load_config(config_name: str) -> dict:
    """Carga una configuración específica"""
    manager = get_config_manager_instance()
    return manager.get_config(config_name)


def get_system_config() -> dict:
    """Obtiene la configuración principal del sistema"""
    return load_config("main")


def get_branch_config() -> list:
    """Obtiene la configuración de ramas"""
    manager = get_config_manager_instance()
    return manager.get_branch_config()


def get_model_config() -> dict:
    """Obtiene la configuración de modelos"""
    manager = get_config_manager_instance()
    return manager.get_model_config()


def get_database_config() -> dict:
    """Obtiene la configuración de base de datos"""
    manager = get_config_manager_instance()
    return manager.get_database_config()


def get_redis_config() -> dict:
    """Obtiene la configuración de Redis"""
    manager = get_config_manager_instance()
    return manager.get_redis_config()


def validate_all_configs() -> list:
    """Valida todas las configuraciones del sistema"""
    validator = get_config_validator_instance()
    return validator.validate_all_configs()


def update_config(config_name: str, updates: dict) -> bool:
    """Actualiza una configuración específica"""
    manager = get_config_manager_instance()
    return manager.update_config(config_name, updates)


def register_config_callback(config_name: str, callback):
    """Registra un callback para cambios de configuración"""
    dynamic_manager = get_dynamic_config_manager_instance()
    dynamic_manager.register_config_callback(config_name, callback)


def get_config_summary() -> dict:
    """Obtiene un resumen de todas las configuraciones"""
    manager = get_config_manager_instance()
    return manager.get_config_summary()


def backup_configs(backup_dir: str = None) -> str:
    """Crea un backup de todas las configuraciones"""
    manager = get_config_manager_instance()
    return manager.backup_configs(backup_dir)


def restore_configs(backup_dir: str) -> bool:
    """Restaura configuraciones desde un backup"""
    manager = get_config_manager_instance()
    return manager.restore_configs(backup_dir)


def get_config_file_path(config_name: str) -> str:
    """Obtiene la ruta de un archivo de configuración"""
    config_dir = Path(DEFAULT_CONFIG_DIR)
    return str(config_dir / f"{config_name}.json")


def list_available_configs() -> list:
    """Lista todas las configuraciones disponibles"""
    manager = get_config_manager_instance()
    return manager.get_all_config_names()


def is_config_valid(config_name: str) -> bool:
    """Verifica si una configuración es válida"""
    validator = get_config_validator_instance()
    results = validator.validate_all_configs()
    for result in results:
        if result.config_type == config_name:
            return result.is_valid
    return False


def get_config_errors(config_name: str = None) -> list:
    """Obtiene errores de configuración"""
    validator = get_config_validator_instance()
    results = validator.validate_all_configs()
    errors = []

    for result in results:
        if config_name is None or result.config_type == config_name:
            errors.extend(result.errors)

    return errors


def get_config_warnings(config_name: str = None) -> list:
    """Obtiene advertencias de configuración"""
    validator = get_config_validator_instance()
    results = validator.validate_all_configs()
    warnings = []

    for result in results:
        if config_name is None or result.config_type == config_name:
            warnings.extend(result.warnings)

    return warnings


def reload_configs():
    """Recarga todas las configuraciones"""
    global _config_manager, _dynamic_config_manager, _config_validator
    _config_manager = None
    _dynamic_config_manager = None
    _config_validator = None


# Funciones de utilidad para configuraciones específicas
def get_embedding_config() -> dict:
    """Obtiene la configuración de embeddings"""
    config = get_system_config()
    return config.get("components", {}).get("embeddings", {})


def get_branch_system_config() -> dict:
    """Obtiene la configuración del sistema de ramas"""
    config = get_system_config()
    return config.get("components", {}).get("branch_system", {})


def get_learning_config() -> dict:
    """Obtiene la configuración de aprendizaje"""
    config = get_system_config()
    return config.get("components", {}).get("learning", {})


def get_memory_config() -> dict:
    """Obtiene la configuración de memoria"""
    config = get_system_config()
    return config.get("components", {}).get("memory", {})


def get_security_config() -> dict:
    """Obtiene la configuración de seguridad"""
    config = get_system_config()
    return config.get("security", {})


def get_performance_config() -> dict:
    """Obtiene la configuración de rendimiento"""
    config = get_system_config()
    return config.get("performance", {})


def get_blockchain_config() -> dict:
    """Obtiene la configuración de blockchain"""
    config = get_system_config()
    return config.get("components", {}).get("blockchain", {})


def get_monitoring_config() -> dict:
    """Obtiene la configuración de monitoreo"""
    return load_config("monitoring")


def get_rate_limits_config() -> dict:
    """Obtiene la configuración de rate limits"""
    return load_config("rate_limits")


def get_training_config() -> dict:
    """Obtiene la configuración de entrenamiento"""
    return load_config("training")


def get_sheily_token_config() -> dict:
    """Obtiene la configuración del token Sheily"""
    return load_config("sheily_token")


def get_advanced_training_config() -> dict:
    """Obtiene la configuración avanzada de entrenamiento"""
    return load_config("advanced_training")


# Funciones de configuración de Docker
def get_docker_config() -> dict:
    """Obtiene la configuración de Docker"""
    manager = get_config_manager_instance()
    return manager.get_config("docker")


def get_docker_dev_config() -> dict:
    """Obtiene la configuración de Docker para desarrollo"""
    manager = get_config_manager_instance()
    return manager.get_config("docker_dev")


# Funciones de validación específicas
def validate_main_config() -> bool:
    """Valida la configuración principal"""
    return is_config_valid("main_config")


def validate_module_init_config() -> bool:
    """Valida la configuración de inicialización de módulos"""
    return is_config_valid("module_init")


def validate_rate_limits_config() -> bool:
    """Valida la configuración de rate limits"""
    return is_config_valid("rate_limits")


def validate_monitoring_config() -> bool:
    """Valida la configuración de monitoreo"""
    return is_config_valid("monitoring_config")


def validate_training_config() -> bool:
    """Valida la configuración de entrenamiento"""
    return is_config_valid("training_config")


def validate_sheily_token_config() -> bool:
    """Valida la configuración del token Sheily"""
    return is_config_valid("sheily_token_config")


# Funciones de configuración dinámica
def get_dynamic_config(config_name: str) -> dict:
    """Obtiene una configuración dinámica"""
    dynamic_manager = get_dynamic_config_manager_instance()
    return dynamic_manager.get_config(config_name)


def set_dynamic_config(config_name: str, config_data: dict) -> bool:
    """Establece una configuración dinámica"""
    dynamic_manager = get_dynamic_config_manager_instance()
    return dynamic_manager.set_config(config_name, config_data)


def update_dynamic_config(config_name: str, updates: dict) -> bool:
    """Actualiza una configuración dinámica"""
    dynamic_manager = get_dynamic_config_manager_instance()
    return dynamic_manager.update_config_partial(config_name, updates)


def get_config_hash(config_name: str) -> str:
    """Obtiene el hash de una configuración"""
    dynamic_manager = get_dynamic_config_manager_instance()
    return dynamic_manager.get_config_hash(config_name)


def is_config_changed(config_name: str, previous_hash: str) -> bool:
    """Verifica si una configuración ha cambiado"""
    dynamic_manager = get_dynamic_config_manager_instance()
    return dynamic_manager.is_config_changed(config_name, previous_hash)


# Funciones de utilidad para el sistema
def get_system_info() -> dict:
    """Obtiene información del sistema"""
    config = get_system_config()
    return {
        "name": config.get("system_name", "NeuroFusion"),
        "version": config.get("version", "1.0.0"),
        "debug_mode": config.get("debug_mode", False),
        "host": config.get("host", "127.0.0.1"),
        "frontend_port": config.get("frontend_port", 3000),
        "backend_port": config.get("backend_port", 8000),
        "log_level": config.get("log_level", "INFO"),
        "enable_monitoring": config.get("enable_monitoring", True),
        "blockchain_enabled": config.get("blockchain_enabled", False),
        "solana_network": config.get("solana_network", "devnet"),
    }


def get_paths() -> dict:
    """Obtiene las rutas del sistema"""
    config = get_system_config()
    return {
        "base_path": config.get("base_path", "./"),
        "data_path": config.get("data_path", "./data"),
        "models_path": config.get("models_path", "./models"),
        "cache_path": config.get("cache_path", "./cache"),
        "logs_path": config.get("logs_path", "./logs"),
    }


def get_model_info() -> dict:
    """Obtiene información de los modelos"""
    config = get_system_config()
    return {
        "embedding_model": config.get("default_embedding_model", "all-MiniLM-L6-v2"),
        "llm_model_4bit": "modules/core/model",  # Modelo de 4-bit para inferencia
        "llm_model_16bit": "models/custom/shaili-personal-model",  # Modelo de 16-bit para entrenamiento
        "default_llm_model": config.get(
            "default_llm_model", "models/custom/shaili-personal-model"
        ),
    }


def get_performance_info() -> dict:
    """Obtiene información de rendimiento"""
    config = get_system_config()
    return {
        "max_concurrent_operations": config.get("max_concurrent_operations", 20),
        "cache_enabled": config.get("cache_enabled", True),
        "cache_size": config.get("cache_size", 15000),
        "max_response_time": config.get("performance", {}).get(
            "max_response_time", 3.0
        ),
        "concurrent_queries": config.get("performance", {}).get(
            "concurrent_queries", 20
        ),
        "memory_limit_mb": config.get("performance", {}).get("memory_limit_mb", 4096),
        "cpu_limit_percent": config.get("performance", {}).get("cpu_limit_percent", 90),
    }


# Función de inicialización del módulo
def initialize_config_module():
    """Inicializa el módulo de configuración"""
    try:
        # Verificar que las configuraciones básicas estén disponibles
        system_config = get_system_config()
        if not system_config:
            print(
                "⚠️  Advertencia: No se pudo cargar la configuración principal del sistema"
            )

        # Validar configuraciones críticas
        if not validate_main_config():
            print("⚠️  Advertencia: La configuración principal tiene errores")

        print(f"✅ Módulo de configuración NeuroFusion v{__version__} inicializado")

    except Exception as e:
        print(f"❌ Error inicializando módulo de configuración: {e}")


# Inicializar el módulo al importarlo
initialize_config_module()

# Exportar funciones y clases principales
__all__ = [
    "ConfigManager",
    "ConfigValidator",
    "DynamicConfigManager",
    "ConfigChangeEvent",
    "get_config_manager",
    "get_dynamic_config_manager",
    "load_config",
    "get_system_config",
    "get_branch_config",
    "get_model_config",
    "get_database_config",
    "get_redis_config",
    "validate_all_configs",
    "update_config",
    "register_config_callback",
    "get_config_summary",
    "backup_configs",
    "restore_configs",
    "list_available_configs",
    "is_config_valid",
    "get_config_errors",
    "get_config_warnings",
    "reload_configs",
    "get_embedding_config",
    "get_branch_system_config",
    "get_learning_config",
    "get_memory_config",
    "get_security_config",
    "get_performance_config",
    "get_blockchain_config",
    "get_monitoring_config",
    "get_rate_limits_config",
    "get_training_config",
    "get_sheily_token_config",
    "get_advanced_training_config",
    "get_docker_config",
    "get_docker_dev_config",
    "validate_main_config",
    "validate_module_init_config",
    "validate_rate_limits_config",
    "validate_monitoring_config",
    "validate_training_config",
    "validate_sheily_token_config",
    "get_dynamic_config",
    "set_dynamic_config",
    "update_dynamic_config",
    "get_config_hash",
    "is_config_changed",
    "get_system_info",
    "get_paths",
    "get_model_info",
    "get_performance_info",
    "__version__",
    "__author__",
    "__description__",
]
