#!/usr/bin/env python3
"""
Paquete de Pruebas End-to-End del Sistema NeuroFusion
Proporciona herramientas completas para pruebas E2E automatizadas
"""

from .e2e_test_manager import (
    E2ETestManager,
    get_e2e_test_manager,
    TestResult,
    TestSuite,
    E2EConfig,
)
from .test_generator import (
    E2ETestGenerator,
    get_e2e_test_generator,
    TestCase,
    TestTemplate,
)

# Metadatos del módulo
__version__ = "3.1.0"
__author__ = "NeuroFusion Team"
__description__ = "Sistema completo de pruebas end-to-end para NeuroFusion"

# Instancias globales
e2e_test_manager = get_e2e_test_manager()
e2e_test_generator = get_e2e_test_generator()


# API pública del módulo
def run_all_e2e_tests() -> Dict[str, List[TestResult]]:
    """Ejecuta todas las pruebas E2E"""
    return e2e_test_manager.run_all_tests()


def run_test_suite(suite_name: str) -> List[TestResult]:
    """Ejecuta una suite de pruebas específica"""
    return e2e_test_manager.run_test_suite(suite_name)


def check_environment() -> Dict[str, bool]:
    """Verifica que el entorno esté listo para las pruebas"""
    return e2e_test_manager.check_environment()


def get_test_summary() -> Dict[str, Any]:
    """Obtiene un resumen de las pruebas ejecutadas"""
    return e2e_test_manager.get_test_summary()


def cleanup_test_artifacts() -> int:
    """Limpia artefactos de pruebas antiguos"""
    return e2e_test_manager.cleanup_test_artifacts()


def generate_all_tests() -> List[str]:
    """Genera todas las pruebas E2E basadas en plantillas"""
    return e2e_test_generator.generate_all_tests()


def generate_custom_test(
    test_name: str,
    description: str,
    steps: List[Dict],
    template_name: str = "api_integration",
    variables: Dict[str, Any] = None,
) -> str:
    """Genera una prueba personalizada"""
    return e2e_test_generator.generate_custom_test(
        test_name, description, steps, template_name, variables
    )


def generate_playwright_config() -> str:
    """Genera la configuración de Playwright"""
    return e2e_test_generator.generate_playwright_config()


def generate_global_setup() -> str:
    """Genera el archivo de configuración global"""
    return e2e_test_generator.generate_global_setup()


def generate_global_teardown() -> str:
    """Genera el archivo de limpieza global"""
    return e2e_test_generator.generate_global_teardown()


def generate_package_json() -> str:
    """Genera el package.json para las pruebas E2E"""
    return e2e_test_generator.generate_package_json()


def get_generation_summary() -> Dict[str, Any]:
    """Obtiene un resumen de la generación de pruebas"""
    return e2e_test_generator.get_generation_summary()


# Funciones de utilidad
def setup_e2e_environment() -> bool:
    """Configura el entorno para pruebas E2E"""
    try:
        # Verificar entorno
        env_status = check_environment()
        if not all(env_status.values()):
            logger.warning("Algunos componentes del entorno no están disponibles")

        # Generar archivos de configuración
        generate_playwright_config()
        generate_global_setup()
        generate_global_teardown()
        generate_package_json()

        # Generar pruebas
        generate_all_tests()

        logger.info("Entorno E2E configurado correctamente")
        return True

    except Exception as e:
        logger.error(f"Error configurando entorno E2E: {e}")
        return False


def run_e2e_test_workflow() -> Dict[str, Any]:
    """Ejecuta el flujo completo de pruebas E2E"""
    try:
        # 1. Configurar entorno
        setup_success = setup_e2e_environment()

        # 2. Verificar entorno
        env_status = check_environment()

        # 3. Ejecutar pruebas
        test_results = run_all_e2e_tests()

        # 4. Obtener resumen
        test_summary = get_test_summary()

        # 5. Limpiar artefactos
        cleaned_count = cleanup_test_artifacts()

        return {
            "setup_success": setup_success,
            "environment_status": env_status,
            "test_results": test_results,
            "test_summary": test_summary,
            "artifacts_cleaned": cleaned_count,
            "timestamp": datetime.now().isoformat(),
        }

    except Exception as e:
        logger.error(f"Error en flujo de pruebas E2E: {e}")
        return {"error": str(e), "timestamp": datetime.now().isoformat()}


# Funciones específicas por tipo de prueba
def run_authentication_tests() -> List[TestResult]:
    """Ejecuta pruebas de autenticación"""
    return run_test_suite("authentication")


def run_chat_interaction_tests() -> List[TestResult]:
    """Ejecuta pruebas de interacción con chat"""
    return run_test_suite("chat_interaction")


def run_training_system_tests() -> List[TestResult]:
    """Ejecuta pruebas del sistema de entrenamiento"""
    return run_test_suite("training_system")


def run_vault_system_tests() -> List[TestResult]:
    """Ejecuta pruebas del sistema de caja fuerte"""
    return run_test_suite("vault_system")


def run_api_integration_tests() -> List[TestResult]:
    """Ejecuta pruebas de integración con APIs"""
    return run_test_suite("api_integration")


def run_performance_tests() -> List[TestResult]:
    """Ejecuta pruebas de rendimiento"""
    return run_test_suite("performance")


def run_error_handling_tests() -> List[TestResult]:
    """Ejecuta pruebas de manejo de errores"""
    return run_test_suite("error_handling")


# Funciones de generación específicas
def generate_authentication_tests() -> str:
    """Genera pruebas de autenticación"""
    return e2e_test_generator.generate_test_from_template(
        "authentication",
        TestCase(
            name="Authentication Tests",
            description="Pruebas de autenticación",
            steps=[],
            assertions=[],
            timeout=30000,
            retries=2,
            dependencies=[],
            tags=["authentication"],
        ),
    )


def generate_chat_tests() -> str:
    """Genera pruebas de chat"""
    return e2e_test_generator.generate_test_from_template(
        "chat_interaction",
        TestCase(
            name="Chat Interaction Tests",
            description="Pruebas de interacción con chat",
            steps=[],
            assertions=[],
            timeout=45000,
            retries=3,
            dependencies=["authentication"],
            tags=["chat", "interaction"],
        ),
    )


def generate_training_tests() -> str:
    """Genera pruebas de entrenamiento"""
    return e2e_test_generator.generate_test_from_template(
        "training_system",
        TestCase(
            name="Training System Tests",
            description="Pruebas del sistema de entrenamiento",
            steps=[],
            assertions=[],
            timeout=60000,
            retries=2,
            dependencies=["authentication"],
            tags=["training", "session"],
        ),
    )


def generate_vault_tests() -> str:
    """Genera pruebas del vault"""
    return e2e_test_generator.generate_test_from_template(
        "vault_system",
        TestCase(
            name="Vault System Tests",
            description="Pruebas del sistema de caja fuerte",
            steps=[],
            assertions=[],
            timeout=30000,
            retries=2,
            dependencies=["authentication"],
            tags=["vault", "statistics"],
        ),
    )


# Funciones de inicialización y configuración
def initialize_e2e_module():
    """Inicializa el módulo de pruebas E2E"""
    try:
        # Crear directorios necesarios
        e2e_dir = Path("e2e")
        directories = [
            e2e_dir / "tests",
            e2e_dir / "config",
            e2e_dir / "reports",
            e2e_dir / "screenshots",
            e2e_dir / "videos",
            e2e_dir / "traces",
            e2e_dir / "logs",
            e2e_dir / "fixtures",
            e2e_dir / "utils",
            e2e_dir / "generated",
            e2e_dir / "templates",
            e2e_dir / "test_cases",
        ]

        for directory in directories:
            directory.mkdir(parents=True, exist_ok=True)

        # Configurar entorno
        setup_success = setup_e2e_environment()

        logger.info("Módulo de pruebas E2E inicializado correctamente")
        return setup_success

    except Exception as e:
        logger.error(f"Error inicializando módulo de pruebas E2E: {e}")
        return False


def close_e2e_system():
    """Cierra el sistema de pruebas E2E"""
    try:
        # Limpiar recursos si es necesario
        cleanup_test_artifacts()
        logger.info("Sistema de pruebas E2E cerrado")
        return True
    except Exception as e:
        logger.error(f"Error cerrando sistema de pruebas E2E: {e}")
        return False


# Inicialización automática del módulo
import logging
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, List

logger = logging.getLogger(__name__)

# Inicializar el módulo al importarlo
initialize_e2e_module()

# Configuración de logging para el módulo
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)

# Exportar todas las clases y funciones principales
__all__ = [
    # Clases principales
    "E2ETestManager",
    "E2ETestGenerator",
    "TestResult",
    "TestSuite",
    "E2EConfig",
    "TestCase",
    "TestTemplate",
    # Funciones de gestión de pruebas
    "run_all_e2e_tests",
    "run_test_suite",
    "check_environment",
    "get_test_summary",
    "cleanup_test_artifacts",
    # Funciones de generación
    "generate_all_tests",
    "generate_custom_test",
    "generate_playwright_config",
    "generate_global_setup",
    "generate_global_teardown",
    "generate_package_json",
    "get_generation_summary",
    # Funciones de utilidad
    "setup_e2e_environment",
    "run_e2e_test_workflow",
    # Funciones específicas por tipo
    "run_authentication_tests",
    "run_chat_interaction_tests",
    "run_training_system_tests",
    "run_vault_system_tests",
    "run_api_integration_tests",
    "run_performance_tests",
    "run_error_handling_tests",
    # Funciones de generación específicas
    "generate_authentication_tests",
    "generate_chat_tests",
    "generate_training_tests",
    "generate_vault_tests",
    # Funciones de inicialización
    "initialize_e2e_module",
    "close_e2e_system",
    # Instancias globales
    "e2e_test_manager",
    "e2e_test_generator",
]
