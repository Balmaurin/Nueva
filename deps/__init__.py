#!/usr/bin/env python3
"""
Paquete de Gestión de Dependencias del Sistema NeuroFusion
Proporciona herramientas completas para manejar todas las dependencias del proyecto
"""

from .dependencies_manager import (
    DependenciesManager,
    get_dependencies_manager,
    DependencyInfo,
    DependencyStats,
)
from .dependency_installer import (
    DependencyInstaller,
    get_dependency_installer,
    InstallationResult,
    InstallationProgress,
)
from .dependency_validator import (
    DependencyValidator,
    get_dependency_validator,
    DependencyValidationResult,
    ValidationSummary,
)

# Metadatos del módulo
__version__ = "3.1.0"
__author__ = "NeuroFusion Team"
__description__ = "Sistema completo de gestión de dependencias para NeuroFusion"

# Instancias globales
dependencies_manager = get_dependencies_manager()
dependency_installer = get_dependency_installer()
dependency_validator = get_dependency_validator()


# API pública del módulo
def get_dependency_stats() -> DependencyStats:
    """Obtiene estadísticas de todas las dependencias"""
    return dependencies_manager.get_dependency_stats()


def check_all_dependencies() -> List[DependencyInfo]:
    """Verifica el estado de todas las dependencias"""
    return dependencies_manager.check_all_dependencies()


def install_missing_dependencies() -> Dict[str, List[str]]:
    """Instala todas las dependencias faltantes"""
    return dependencies_manager.install_missing_dependencies()


def validate_dependencies(
    dependencies_config: Dict[str, Any],
) -> List[DependencyValidationResult]:
    """Valida todas las dependencias según la configuración"""
    return dependency_validator.validate_all_dependencies(dependencies_config)


def get_validation_summary() -> ValidationSummary:
    """Obtiene un resumen de la validación de dependencias"""
    return dependency_validator.get_validation_summary()


def create_requirements_txt() -> str:
    """Crea un archivo requirements.txt con todas las dependencias de Python"""
    return dependencies_manager.create_requirements_txt()


def create_package_json() -> str:
    """Crea un archivo package.json con todas las dependencias de Node.js"""
    return dependencies_manager.create_package_json()


def backup_dependencies() -> str:
    """Crea un backup de las configuraciones de dependencias"""
    return dependencies_manager.backup_dependencies()


def restore_dependencies(backup_path: str) -> bool:
    """Restaura dependencias desde un backup"""
    return dependencies_manager.restore_dependencies(backup_path)


def update_dependency_versions() -> Dict[str, List[str]]:
    """Actualiza las versiones de las dependencias"""
    return dependencies_manager.update_dependency_versions()


def cleanup_cache() -> int:
    """Limpia el caché de dependencias"""
    return dependencies_manager.cleanup_cache()


def install_all_dependencies(
    dependencies_config: Dict[str, Any],
) -> List[InstallationResult]:
    """Instala todas las dependencias según la configuración"""
    return dependency_installer.install_all_dependencies(dependencies_config)


def get_installation_summary() -> Dict[str, Any]:
    """Obtiene un resumen de la instalación de dependencias"""
    return dependency_installer.get_installation_summary()


def save_installation_report(filepath: str = None) -> str:
    """Guarda un reporte de instalación"""
    return dependency_installer.save_installation_report(filepath)


def save_validation_report(filepath: str = None) -> str:
    """Guarda un reporte de validación"""
    return dependency_validator.save_validation_report(filepath)


def print_validation_report():
    """Imprime un reporte de validación en consola"""
    dependency_validator.print_validation_report()


def stop_installation_process():
    """Detiene el proceso de instalación"""
    dependency_installer.stop_installation_process()


def set_progress_callback(callback):
    """Establece un callback para el progreso de instalación"""
    dependency_installer.set_progress_callback(callback)


# Funciones específicas por tipo de dependencia
def check_python_dependency(package_name: str) -> DependencyInfo:
    """Verifica una dependencia específica de Python"""
    return dependencies_manager.check_python_dependency(package_name)


def check_node_dependency(package_name: str) -> DependencyInfo:
    """Verifica una dependencia específica de Node.js"""
    return dependencies_manager.check_node_dependency(package_name)


def check_system_dependency(package_name: str) -> DependencyInfo:
    """Verifica una dependencia específica del sistema"""
    return dependencies_manager.check_system_dependency(package_name)


def install_python_dependency(package_name: str, version: str = None) -> bool:
    """Instala una dependencia específica de Python"""
    return dependencies_manager.install_python_dependency(package_name, version)


def install_node_dependency(package_name: str, version: str = None) -> bool:
    """Instala una dependencia específica de Node.js"""
    return dependencies_manager.install_node_dependency(package_name, version)


def install_system_dependency(package_name: str) -> InstallationResult:
    """Instala una dependencia específica del sistema"""
    return dependency_installer.install_system_dependency(package_name)


def validate_python_dependency(
    package_name: str, required_version: str
) -> DependencyValidationResult:
    """Valida una dependencia específica de Python"""
    return dependency_validator.validate_python_dependency(
        package_name, required_version
    )


def validate_node_dependency(
    package_name: str, required_version: str
) -> DependencyValidationResult:
    """Valida una dependencia específica de Node.js"""
    return dependency_validator.validate_node_dependency(package_name, required_version)


def validate_system_dependency(
    package_name: str, required_version: str
) -> DependencyValidationResult:
    """Valida una dependencia específica del sistema"""
    return dependency_validator.validate_system_dependency(
        package_name, required_version
    )


# Funciones de inicialización y configuración
def initialize_deps_module():
    """Inicializa el módulo de dependencias"""
    try:
        # Crear directorios necesarios
        deps_dir = Path("deps")
        directories = [
            deps_dir / "python",
            deps_dir / "node",
            deps_dir / "system",
            deps_dir / "cache",
            deps_dir / "backups",
            deps_dir / "installation_reports",
            deps_dir / "validation_reports",
        ]

        for directory in directories:
            directory.mkdir(parents=True, exist_ok=True)

        # Crear archivos de configuración si no existen
        if not (deps_dir / "requirements.txt").exists():
            create_requirements_txt()

        if not (deps_dir / "package.json").exists():
            create_package_json()

        logger.info("Módulo de dependencias inicializado correctamente")
        return True

    except Exception as e:
        logger.error(f"Error inicializando módulo de dependencias: {e}")
        return False


def close_deps_system():
    """Cierra el sistema de dependencias"""
    try:
        # Limpiar recursos si es necesario
        logger.info("Sistema de dependencias cerrado")
        return True
    except Exception as e:
        logger.error(f"Error cerrando sistema de dependencias: {e}")
        return False


# Inicialización automática del módulo
import logging

logger = logging.getLogger(__name__)

# Inicializar el módulo al importarlo
initialize_deps_module()

# Configuración de logging para el módulo
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)

# Exportar todas las clases y funciones principales
__all__ = [
    # Clases principales
    "DependenciesManager",
    "DependencyInstaller",
    "DependencyValidator",
    "DependencyInfo",
    "DependencyStats",
    "InstallationResult",
    "InstallationProgress",
    "DependencyValidationResult",
    "ValidationSummary",
    # Funciones de gestión
    "get_dependency_stats",
    "check_all_dependencies",
    "install_missing_dependencies",
    "create_requirements_txt",
    "create_package_json",
    "backup_dependencies",
    "restore_dependencies",
    "update_dependency_versions",
    "cleanup_cache",
    # Funciones de instalación
    "install_all_dependencies",
    "get_installation_summary",
    "save_installation_report",
    "stop_installation_process",
    "set_progress_callback",
    # Funciones de validación
    "validate_dependencies",
    "get_validation_summary",
    "save_validation_report",
    "print_validation_report",
    # Funciones específicas por tipo
    "check_python_dependency",
    "check_node_dependency",
    "check_system_dependency",
    "install_python_dependency",
    "install_node_dependency",
    "install_system_dependency",
    "validate_python_dependency",
    "validate_node_dependency",
    "validate_system_dependency",
    # Funciones de inicialización
    "initialize_deps_module",
    "close_deps_system",
    # Instancias globales
    "dependencies_manager",
    "dependency_installer",
    "dependency_validator",
]
