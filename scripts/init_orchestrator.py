#!/usr/bin/env python3
"""
Script de Inicialización del Orquestador
========================================

Verifica y configura todos los componentes del orquestador
"""

import os
import sys
import json
import logging
from datetime import datetime
from pathlib import Path

# Agregar el directorio raíz al path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


def setup_logging():
    """Configurar logging para el script"""
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(levelname)s - %(message)s",
        handlers=[
            logging.FileHandler("logs/orchestrator_init.log"),
            logging.StreamHandler(),
        ],
    )
    return logging.getLogger(__name__)


def check_dependencies():
    """Verificar dependencias necesarias"""
    logger = logging.getLogger(__name__)
    logger.info("🔍 Verificando dependencias...")

    required_packages = [
        "torch",
        "transformers",
        "peft",
        "scikit-learn",
        "numpy",
        "pandas",
        "faiss-cpu",
        "duckdb",
        "flask",
        "flask-cors",
    ]

    missing_packages = []

    for package in required_packages:
        try:
            __import__(package.replace("-", "_"))
            logger.info(f"✅ {package}")
        except ImportError:
            missing_packages.append(package)
            logger.error(f"❌ {package} - NO ENCONTRADO")

    if missing_packages:
        logger.error(f"❌ Faltan dependencias: {', '.join(missing_packages)}")
        logger.info("💡 Instala las dependencias con: pip install -r requirements.txt")
        return False

    logger.info("✅ Todas las dependencias están disponibles")
    return True


def check_model_files():
    """Verificar archivos del modelo base"""
    logger = logging.getLogger(__name__)
    logger.info("🔍 Verificando archivos del modelo...")

    model_path = "models/custom/sheily-personal-model"

    if not os.path.exists(model_path):
        logger.error(f"❌ Modelo no encontrado en: {model_path}")
        logger.info("💡 Asegúrate de que el modelo esté descargado y configurado")
        return False

    # Verificar archivos esenciales del modelo
    required_files = [
        "config.json",
        "pytorch_model.bin",
        "tokenizer.json",
        "tokenizer_config.json",
    ]

    missing_files = []
    for file in required_files:
        file_path = os.path.join(model_path, file)
        if not os.path.exists(file_path):
            missing_files.append(file)
            logger.error(f"❌ {file} - NO ENCONTRADO")
        else:
            logger.info(f"✅ {file}")

    if missing_files:
        logger.error(f"❌ Faltan archivos del modelo: {', '.join(missing_files)}")
        return False

    logger.info("✅ Modelo base verificado correctamente")
    return True


def check_branches_structure():
    """Verificar estructura de ramas"""
    logger = logging.getLogger(__name__)
    logger.info("🔍 Verificando estructura de ramas...")

    branches_path = "branches"
    if not os.path.exists(branches_path):
        logger.error(f"❌ Directorio de ramas no encontrado: {branches_path}")
        return False

    # Verificar ramas principales
    expected_branches = [
        "matemáticas",
        "computación_y_programación",
        "física",
        "química",
        "biología",
        "medicina_y_salud",
        "ingeniería",
        "economía_y_finanzas",
        "educación_y_pedagogía",
        "historia",
        "arte_música_y_cultura",
        "literatura_y_escritura",
        "deportes_y_esports",
        "cocina_y_nutrición",
        "viajes_e_idiomas",
        "vida_diaria_legal_práctico_y_trámites",
    ]

    missing_branches = []
    for branch in expected_branches:
        branch_path = os.path.join(branches_path, branch)
        if not os.path.exists(branch_path):
            missing_branches.append(branch)
            logger.warning(f"⚠️  Rama no encontrada: {branch}")
        else:
            logger.info(f"✅ Rama: {branch}")

    if missing_branches:
        logger.warning(f"⚠️  Algunas ramas faltan: {', '.join(missing_branches)}")
        logger.info("💡 Las ramas faltantes se crearán automáticamente")

    logger.info("✅ Estructura de ramas verificada")
    return True


def create_missing_directories():
    """Crear directorios faltantes"""
    logger = logging.getLogger(__name__)
    logger.info("🔧 Creando directorios faltantes...")

    directories = [
        "logs",
        "data/embedding_cache",
        "data/best_corpus",
        "cache",
        "adapter_cache",
    ]

    for directory in directories:
        os.makedirs(directory, exist_ok=True)
        logger.info(f"✅ Directorio creado/verificado: {directory}")


def test_orchestrator_components():
    """Probar componentes del orquestador"""
    logger = logging.getLogger(__name__)
    logger.info("🧪 Probando componentes del orquestador...")

    try:
        # Importar componentes
        from modules.orchestrator.main_orchestrator import MainOrchestrator

        # Crear instancia de prueba
        test_config = {
            "enable_domain_classification": True,
            "enable_semantic_routing": True,
            "enable_branch_management": True,
            "enable_rag": True,
            "enable_adapter_policy": True,
            "log_level": "INFO",
        }

        orchestrator = MainOrchestrator(test_config)
        logger.info("✅ Orquestador creado correctamente")

        # Probar consulta simple
        test_query = "¿Qué es la inteligencia artificial?"
        response = orchestrator.process_query(test_query)

        if response and "text" in response:
            logger.info("✅ Procesamiento de consulta exitoso")
            logger.info(f"📝 Respuesta de prueba: {response['text'][:100]}...")
        else:
            logger.error("❌ Error en procesamiento de consulta")
            return False

        # Probar estado del sistema
        status = orchestrator.get_system_status()
        if status:
            logger.info("✅ Estado del sistema obtenido correctamente")
        else:
            logger.error("❌ Error obteniendo estado del sistema")
            return False

        return True

    except Exception as e:
        logger.error(f"❌ Error probando orquestador: {e}")
        return False


def generate_init_report():
    """Generar reporte de inicialización"""
    logger = logging.getLogger(__name__)
    logger.info("📊 Generando reporte de inicialización...")

    report = {
        "timestamp": datetime.now().isoformat(),
        "system_info": {"python_version": sys.version, "platform": sys.platform},
        "checks": {
            "dependencies": check_dependencies(),
            "model_files": check_model_files(),
            "branches_structure": check_branches_structure(),
            "orchestrator_components": test_orchestrator_components(),
        },
        "directories_created": [
            "logs",
            "data/embedding_cache",
            "data/best_corpus",
            "cache",
            "adapter_cache",
        ],
    }

    # Guardar reporte
    report_path = "logs/orchestrator_init_report.json"
    os.makedirs(os.path.dirname(report_path), exist_ok=True)

    with open(report_path, "w", encoding="utf-8") as f:
        json.dump(report, f, indent=2, ensure_ascii=False)

    logger.info(f"📄 Reporte guardado en: {report_path}")

    # Mostrar resumen
    checks = report["checks"]
    passed = sum(checks.values())
    total = len(checks)

    logger.info(f"📊 Resumen: {passed}/{total} verificaciones exitosas")

    if passed == total:
        logger.info("🎉 ¡Inicialización completada exitosamente!")
        return True
    else:
        logger.error("❌ Algunas verificaciones fallaron")
        return False


def main():
    """Función principal"""
    print("🚀 Inicializando Orquestador de Sheily-AI")
    print("=" * 50)

    # Configurar logging
    logger = setup_logging()

    try:
        # Crear directorios necesarios
        create_missing_directories()

        # Ejecutar verificaciones
        success = generate_init_report()

        if success:
            print("\n✅ ¡Inicialización completada exitosamente!")
            print("🎯 El orquestador está listo para usar")
            print("\n📋 Próximos pasos:")
            print("   1. Iniciar el servidor backend")
            print("   2. Verificar endpoints en /api/orchestrator/health")
            print("   3. Probar procesamiento de consultas")
        else:
            print("\n❌ La inicialización encontró problemas")
            print("🔧 Revisa los logs para más detalles")
            sys.exit(1)

    except Exception as e:
        logger.error(f"❌ Error crítico durante la inicialización: {e}")
        print(f"\n❌ Error crítico: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
