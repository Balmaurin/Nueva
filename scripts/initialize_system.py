#!/usr/bin/env python3
"""
Script de Inicialización del Sistema
Inicializa y prueba todos los módulos implementados
"""

import os
import sys
import json
import logging
from datetime import datetime
from pathlib import Path

# Añadir el directorio raíz al path
sys.path.append(str(Path(__file__).parent.parent))

# Importar todos los gestores
from modules.cache.adapter_cache_manager import adapter_cache_manager
from modules.analysis.analysis_results_manager import analysis_results_manager
from modules.backup.backup_manager import backup_manager
from modules.branches.branch_manager import branch_manager
from modules.cache.cache_manager import cache_manager
from modules.config.config_manager import config_manager
from modules.data.data_manager import data_manager
from modules.datasets.dataset_manager import dataset_manager
from modules.routes.system_routes import system_routes


def setup_logging():
    """Configurar logging"""
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        handlers=[
            logging.FileHandler("logs/system_initialization.log"),
            logging.StreamHandler(),
        ],
    )
    return logging.getLogger(__name__)


def create_test_data():
    """Crear datos de prueba para los módulos"""
    test_data = {
        "adapter_data": {
            "adapter_id": "test_adapter_001",
            "model_name": "models/custom/sheily-personal-model",
            "branch_name": "test_branch",
            "config": {"learning_rate": 0.001, "epochs": 10},
        },
        "analysis_data": {
            "analysis_type": "performance",
            "model_name": "models/custom/sheily-personal-model",
            "branch_name": "test_branch",
            "data": {"accuracy": 0.95, "loss": 0.05},
            "metrics": {"coherence": 0.8, "diversity": 0.7},
        },
        "branch_data": {
            "name": "test_branch",
            "description": "Rama de prueba para testing",
            "category": "testing",
            "keywords": ["test", "prueba", "testing"],
            "model_name": "models/custom/sheily-personal-model",
        },
        "cache_data": {
            "key": "test_cache_key",
            "value": "test_cache_value",
            "cache_type": "test",
            "ttl_hours": 1,
        },
        "config_data": {"section": "test", "key": "test_key", "value": "test_value"},
        "data_content": {
            "content": "Este es un contenido de prueba para el sistema de datos",
            "data_type": "text",
            "source": "test",
        },
        "dataset_data": {
            "name": "test_dataset",
            "description": "Dataset de prueba",
            "content": [
                {
                    "question": "¿Qué es Python?",
                    "answer": "Python es un lenguaje de programación",
                },
                {"question": "¿Qué es AI?", "answer": "AI es Inteligencia Artificial"},
            ],
        },
    }
    return test_data


def test_adapter_cache():
    """Probar módulo de cache de adaptadores"""
    print("\n🧪 Probando Adapter Cache Manager...")

    try:
        # Probar almacenamiento
        adapter_id = adapter_cache_manager.store_adapter(
            adapter_id="test_adapter_001",
            adapter_data={"config": {"lr": 0.001}},
            model_name="models/custom/sheily-personal-model",
            branch_name="test_branch",
        )
        print(f"✅ Adaptador almacenado: {adapter_id}")

        # Probar recuperación
        adapter = adapter_cache_manager.get_adapter("test_adapter_001")
        if adapter:
            print(f"✅ Adaptador recuperado: {adapter['adapter_id']}")

        # Probar listado
        adapters = adapter_cache_manager.list_adapters(limit=10)
        print(f"✅ Adaptadores listados: {len(adapters)} encontrados")

        # Probar estadísticas
        stats = adapter_cache_manager.get_cache_stats()
        print(f"✅ Estadísticas: {stats['total_adapters']} adaptadores")

        return True

    except Exception as e:
        print(f"❌ Error en Adapter Cache: {e}")
        return False


def test_analysis_results():
    """Probar módulo de análisis de resultados"""
    print("\n🧪 Probando Analysis Results Manager...")

    try:
        # Probar creación de análisis
        analysis_id = analysis_results_manager.create_analysis(
            analysis_type="performance",
            model_name="models/custom/sheily-personal-model",
            branch_name="test_branch",
            data={"accuracy": 0.95, "loss": 0.05},
            metrics={"coherence": 0.8, "diversity": 0.7},
        )
        print(f"✅ Análisis creado: {analysis_id}")

        # Probar recuperación
        analysis = analysis_results_manager.get_analysis(analysis_id)
        if analysis:
            print(f"✅ Análisis recuperado: {analysis['analysis_type']}")

        # Probar listado
        analyses = analysis_results_manager.list_analyses(limit=10)
        print(f"✅ Análisis listados: {len(analyses)} encontrados")

        # Probar estadísticas
        stats = analysis_results_manager.get_analysis_stats()
        print(f"✅ Estadísticas: {stats['total_analyses']} análisis")

        return True

    except Exception as e:
        print(f"❌ Error en Analysis Results: {e}")
        return False


def test_backup_manager():
    """Probar módulo de backup"""
    print("\n🧪 Probando Backup Manager...")

    try:
        # Probar creación de backup
        backup_id = backup_manager.create_backup(
            backup_type="test", description="Backup de prueba del sistema"
        )
        print(f"✅ Backup creado: {backup_id}")

        # Probar listado
        backups = backup_manager.list_backups(limit=10)
        print(f"✅ Backups listados: {len(backups)} encontrados")

        # Probar verificación
        if backups:
            verification = backup_manager.verify_backup(backups[0]["backup_id"])
            print(f"✅ Verificación: {verification['valid']}")

        # Probar estadísticas
        stats = backup_manager.get_backup_stats()
        print(f"✅ Estadísticas: {stats['total_backups']} backups")

        return True

    except Exception as e:
        print(f"❌ Error en Backup Manager: {e}")
        return False


def test_branch_manager():
    """Probar módulo de branches"""
    print("\n🧪 Probando Branch Manager...")

    try:
        # Probar creación de rama
        branch_id = branch_manager.create_branch(
            name="test_branch",
            description="Rama de prueba para testing",
            category="testing",
            keywords=["test", "prueba", "testing"],
            model_name="models/custom/sheily-personal-model",
        )
        print(f"✅ Rama creada: {branch_id}")

        # Probar recuperación
        branch = branch_manager.get_branch(branch_id)
        if branch:
            print(f"✅ Rama recuperada: {branch.name}")

        # Probar listado
        branches = branch_manager.list_branches(limit=10)
        print(f"✅ Ramas listadas: {len(branches)} encontradas")

        # Probar estadísticas
        stats = branch_manager.get_branch_stats()
        print(f"✅ Estadísticas: {stats['total_branches']} ramas")

        return True

    except Exception as e:
        print(f"❌ Error en Branch Manager: {e}")
        return False


def test_cache_manager():
    """Probar módulo de cache general"""
    print("\n🧪 Probando Cache Manager...")

    try:
        # Probar almacenamiento
        cache_key = cache_manager.set(
            key="test_cache_key",
            value="test_cache_value",
            cache_type="test",
            ttl_hours=1,
        )
        print(f"✅ Cache almacenado: {cache_key}")

        # Probar recuperación
        value = cache_manager.get("test_cache_key", "test")
        if value:
            print(f"✅ Cache recuperado: {value}")

        # Probar estadísticas
        stats = cache_manager.get_cache_stats()
        print(f"✅ Estadísticas: {stats['total_entries']} entradas")

        return True

    except Exception as e:
        print(f"❌ Error en Cache Manager: {e}")
        return False


def test_config_manager():
    """Probar módulo de configuración"""
    print("\n🧪 Probando Config Manager...")

    try:
        # Probar establecimiento de configuración
        success = config_manager.set_config(
            section="test", key="test_key", value="test_value"
        )
        print(f"✅ Configuración establecida: {success}")

        # Probar obtención de configuración
        value = config_manager.get_config("test", "test_key")
        print(f"✅ Configuración obtenida: {value}")

        # Probar validación
        validation = config_manager.validate_config()
        print(f"✅ Validación: {validation['valid']}")

        # Probar estadísticas
        stats = config_manager.get_config_stats()
        print(f"✅ Estadísticas: {stats['total_configs']} configuraciones")

        return True

    except Exception as e:
        print(f"❌ Error en Config Manager: {e}")
        return False


def test_data_manager():
    """Probar módulo de datos"""
    print("\n🧪 Probando Data Manager...")

    try:
        # Probar almacenamiento de datos
        record_id = data_manager.store_data(
            content="Este es un contenido de prueba para el sistema de datos",
            data_type="text",
            source="test",
        )
        print(f"✅ Datos almacenados: {record_id}")

        # Probar recuperación
        record = data_manager.get_data(record_id)
        if record:
            print(f"✅ Datos recuperados: {record.content[:50]}...")

        # Probar búsqueda
        results = data_manager.search_data("prueba", limit=5)
        print(f"✅ Búsqueda: {len(results)} resultados")

        # Probar estadísticas
        stats = data_manager.get_data_stats()
        print(f"✅ Estadísticas: {stats['total_records']} registros")

        return True

    except Exception as e:
        print(f"❌ Error en Data Manager: {e}")
        return False


def test_dataset_manager():
    """Probar módulo de datasets"""
    print("\n🧪 Probando Dataset Manager...")

    try:
        # Crear dataset de prueba
        test_data = [
            {
                "question": "¿Qué es Python?",
                "answer": "Python es un lenguaje de programación",
            },
            {"question": "¿Qué es AI?", "answer": "AI es Inteligencia Artificial"},
        ]

        dataset_id = dataset_manager.create_conversation_dataset(
            conversations=test_data,
            name="test_dataset",
            description="Dataset de prueba",
        )
        print(f"✅ Dataset creado: {dataset_id}")

        # Probar recuperación
        dataset = dataset_manager.get_dataset(dataset_id)
        if dataset:
            print(f"✅ Dataset recuperado: {dataset.name}")

        # Probar lectura
        df = dataset_manager.read_dataset(dataset_id, limit=5)
        if df is not None:
            print(f"✅ Dataset leído: {len(df)} filas")

        # Probar listado
        datasets = dataset_manager.list_datasets(limit=10)
        print(f"✅ Datasets listados: {len(datasets)} encontrados")

        # Probar estadísticas
        stats = dataset_manager.get_dataset_stats()
        print(f"✅ Estadísticas: {stats['total_datasets']} datasets")

        return True

    except Exception as e:
        print(f"❌ Error en Dataset Manager: {e}")
        return False


def test_system_routes():
    """Probar sistema de rutas"""
    print("\n🧪 Probando System Routes...")

    try:
        # Probar comandos disponibles
        commands = system_routes.get_available_commands()
        print(f"✅ Comandos disponibles: {len(commands)}")

        # Probar ejecución de comando
        result = system_routes.execute_command(
            "cache_set",
            key="test_route_key",
            value="test_route_value",
            cache_type="test",
        )
        print(f"✅ Comando ejecutado: {result['success']}")

        # Probar estado del sistema
        status = system_routes.get_system_status()
        print(
            f"✅ Estado del sistema: {status['total_commands_executed']} comandos ejecutados"
        )

        # Probar health check
        health = system_routes.run_system_health_check()
        print(f"✅ Health check: {health['overall_status']}")

        return True

    except Exception as e:
        print(f"❌ Error en System Routes: {e}")
        return False


def main():
    """Función principal"""
    print("🚀 Iniciando Sistema Sheily AI")
    print("=" * 50)

    # Configurar logging
    logger = setup_logging()

    # Crear directorio de logs si no existe
    Path("logs").mkdir(exist_ok=True)

    # Resultados de las pruebas
    test_results = {}

    try:
        # Probar cada módulo
        test_results["adapter_cache"] = test_adapter_cache()
        test_results["analysis_results"] = test_analysis_results()
        test_results["backup"] = test_backup_manager()
        test_results["branches"] = test_branch_manager()
        test_results["cache"] = test_cache_manager()
        test_results["config"] = test_config_manager()
        test_results["data"] = test_data_manager()
        test_results["datasets"] = test_dataset_manager()
        test_results["system_routes"] = test_system_routes()

        # Resumen de resultados
        print("\n" + "=" * 50)
        print("📊 RESUMEN DE PRUEBAS")
        print("=" * 50)

        passed = 0
        total = len(test_results)

        for module, result in test_results.items():
            status = "✅ PASÓ" if result else "❌ FALLÓ"
            print(f"{module:20} {status}")
            if result:
                passed += 1

        print(f"\nTotal: {passed}/{total} módulos funcionando correctamente")

        if passed == total:
            print("🎉 ¡Todos los módulos están funcionando correctamente!")
        else:
            print("⚠️ Algunos módulos tienen problemas que necesitan atención")

        # Guardar resultados
        results_file = Path("logs/initialization_results.json")
        with open(results_file, "w", encoding="utf-8") as f:
            json.dump(
                {
                    "timestamp": datetime.now().isoformat(),
                    "results": test_results,
                    "summary": {
                        "passed": passed,
                        "total": total,
                        "success_rate": passed / total if total > 0 else 0,
                    },
                },
                f,
                indent=2,
                ensure_ascii=False,
            )

        print(f"\n📄 Resultados guardados en: {results_file}")

    except Exception as e:
        logger.error(f"Error durante la inicialización: {e}")
        print(f"❌ Error crítico: {e}")
        return False

    return passed == total


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
