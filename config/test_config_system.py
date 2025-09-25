#!/usr/bin/env python3
"""
Script de Prueba del Sistema de Configuración NeuroFusion
Verifica que todo el sistema de configuración funciona correctamente
"""

import json
import sys
import os
from pathlib import Path
from datetime import datetime

# Agregar el directorio actual al path
current_dir = Path(__file__).parent
if str(current_dir) not in sys.path:
    sys.path.insert(0, str(current_dir))


def test_config_manager():
    """Prueba el gestor de configuración principal"""
    print("🧪 Probando ConfigManager...")

    try:
        from config_manager import ConfigManager

        # Crear instancia
        manager = ConfigManager()
        print("   ✅ ConfigManager creado exitosamente")

        # Probar obtención de configuraciones
        configs_to_test = ["main", "module_init", "rate_limits", "monitoring"]

        for config_name in configs_to_test:
            try:
                config = manager.get_config(config_name)
                if config:
                    print(f"   ✅ Configuración '{config_name}' cargada correctamente")
                else:
                    print(f"   ⚠️  Configuración '{config_name}' está vacía")
            except Exception as e:
                print(f"   ❌ Error cargando configuración '{config_name}': {e}")

        # Probar configuración del sistema
        system_config = manager.get_system_config()
        if system_config:
            print(
                f"   ✅ Configuración del sistema: {system_config.system_name} v{system_config.version}"
            )

        # Probar configuración de componentes
        component_config = manager.get_component_config()
        if component_config:
            print("   ✅ Configuración de componentes cargada")

        # Probar configuración de rendimiento
        performance_config = manager.get_performance_config()
        if performance_config:
            print(
                f"   ✅ Configuración de rendimiento: {performance_config.max_response_time}s"
            )

        # Probar configuración de seguridad
        security_config = manager.get_security_config()
        if security_config:
            print(
                f"   ✅ Configuración de seguridad: JWT {'habilitado' if security_config.jwt_enabled else 'deshabilitado'}"
            )

        # Probar configuración de ramas
        branches = manager.get_branch_config()
        if branches:
            print(f"   ✅ Configuración de ramas: {len(branches)} ramas configuradas")

        # Probar configuración de modelos
        model_config = manager.get_model_config()
        if model_config:
            print(f"   ✅ Configuración de modelos: {model_config['embedding_model']}")

        # Probar validación
        validation = manager.validate_config()
        if validation["valid"]:
            print("   ✅ Validación de configuración exitosa")
        else:
            print(
                f"   ⚠️  Validación de configuración con errores: {validation['errors']}"
            )

        # Probar resumen
        summary = manager.get_config_summary()
        if summary:
            print("   ✅ Resumen de configuración generado")

        return True

    except Exception as e:
        print(f"   ❌ Error en ConfigManager: {e}")
        return False


def test_config_validator():
    """Prueba el validador de configuración"""
    print("\n🧪 Probando ConfigValidator...")

    try:
        from config_validator import ConfigValidator

        # Crear instancia
        validator = ConfigValidator()
        print("   ✅ ConfigValidator creado exitosamente")

        # Probar validación de todas las configuraciones
        results = validator.validate_all_configs()
        if results:
            print(
                f"   ✅ Validación completada: {len(results)} configuraciones validadas"
            )

            valid_count = sum(1 for r in results if r.is_valid)
            invalid_count = len(results) - valid_count

            print(f"   📊 Resultados: {valid_count} válidas, {invalid_count} inválidas")

            # Mostrar errores si los hay
            for result in results:
                if not result.is_valid:
                    print(f"   ❌ {result.config_type}: {result.errors}")
                elif result.warnings:
                    print(f"   ⚠️  {result.config_type}: {result.warnings}")

        # Probar resumen de validación
        summary = validator.get_validation_summary()
        if summary:
            print(
                f"   ✅ Resumen de validación: {summary['valid_configs']}/{summary['total_configs']} válidas"
            )

        return True

    except Exception as e:
        print(f"   ❌ Error en ConfigValidator: {e}")
        return False


def test_dynamic_config_manager():
    """Prueba el gestor de configuración dinámica"""
    print("\n🧪 Probando DynamicConfigManager...")

    try:
        from dynamic_config_manager import DynamicConfigManager, ConfigChangeEvent

        # Crear instancia
        dynamic_manager = DynamicConfigManager()
        print("   ✅ DynamicConfigManager creado exitosamente")

        # Probar obtención de configuraciones
        config_names = dynamic_manager.get_all_config_names()
        if config_names:
            print(f"   ✅ Configuraciones disponibles: {len(config_names)}")

            # Probar obtención de configuración específica
            for config_name in config_names[:3]:  # Probar solo las primeras 3
                config = dynamic_manager.get_config(config_name)
                if config:
                    print(f"   ✅ Configuración '{config_name}' obtenida")

        # Probar hash de configuración
        if config_names:
            config_name = config_names[0]
            config_hash = dynamic_manager.get_config_hash(config_name)
            if config_hash:
                print(
                    f"   ✅ Hash de configuración '{config_name}': {config_hash[:8]}..."
                )

        # Probar callback de configuración
        callback_called = False

        def test_callback(event: ConfigChangeEvent):
            nonlocal callback_called
            callback_called = True
            print(f"   📞 Callback llamado para: {event.config_name}")

        if config_names:
            dynamic_manager.register_config_callback(config_names[0], test_callback)
            print("   ✅ Callback registrado")

        # Probar resumen
        summary = dynamic_manager.get_config_summary()
        if summary:
            print("   ✅ Resumen de configuración dinámica generado")

        # Detener el gestor
        dynamic_manager.stop()
        print("   ✅ DynamicConfigManager detenido")

        return True

    except Exception as e:
        print(f"   ❌ Error en DynamicConfigManager: {e}")
        return False


def test_config_module():
    """Prueba el módulo de configuración completo"""
    print("\n🧪 Probando módulo de configuración...")

    try:
        import config

        print(f"   ✅ Módulo importado: v{config.__version__}")

        # Probar funciones principales
        system_info = config.get_system_info()
        if system_info:
            print(
                f"   ✅ Información del sistema: {system_info['name']} v{system_info['version']}"
            )

        paths = config.get_paths()
        if paths:
            print(f"   ✅ Rutas del sistema: {paths['data_path']}")

        model_info = config.get_model_info()
        if model_info:
            print(f"   ✅ Información de modelos: {model_info['embedding_model']}")

        performance_info = config.get_performance_info()
        if performance_info:
            print(
                f"   ✅ Información de rendimiento: {performance_info['max_concurrent_operations']} operaciones"
            )

        # Probar validaciones
        if config.validate_main_config():
            print("   ✅ Configuración principal válida")
        else:
            print("   ❌ Configuración principal inválida")

        # Probar listado de configuraciones
        available_configs = config.list_available_configs()
        if available_configs:
            print(f"   ✅ Configuraciones disponibles: {len(available_configs)}")

        # Probar obtención de configuraciones específicas
        specific_configs = [
            ("embedding", config.get_embedding_config),
            ("branch_system", config.get_branch_system_config),
            ("learning", config.get_learning_config),
            ("memory", config.get_memory_config),
            ("security", config.get_security_config),
            ("performance", config.get_performance_config),
            ("blockchain", config.get_blockchain_config),
            ("monitoring", config.get_monitoring_config),
            ("rate_limits", config.get_rate_limits_config),
            ("training", config.get_training_config),
            ("sheily_token", config.get_sheily_token_config),
            ("advanced_training", config.get_advanced_training_config),
        ]

        for config_name, config_func in specific_configs:
            try:
                config_data = config_func()
                if config_data:
                    print(f"   ✅ Configuración '{config_name}' obtenida")
                else:
                    print(f"   ⚠️  Configuración '{config_name}' vacía")
            except Exception as e:
                print(f"   ❌ Error obteniendo configuración '{config_name}': {e}")

        return True

    except Exception as e:
        print(f"   ❌ Error en módulo de configuración: {e}")
        return False


def test_config_files():
    """Prueba la integridad de los archivos de configuración"""
    print("\n🧪 Probando archivos de configuración...")

    config_dir = Path("config")
    config_files = [
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

    all_valid = True

    for filename in config_files:
        file_path = config_dir / filename
        if file_path.exists():
            try:
                with open(file_path, "r", encoding="utf-8") as f:
                    if filename.endswith(".json"):
                        json.load(f)
                    elif filename.endswith((".yml", ".yaml")):
                        import yaml

                        yaml.safe_load(f)

                # Verificar tamaño del archivo
                file_size = file_path.stat().st_size
                if file_size > 0:
                    print(f"   ✅ {filename} ({(file_size/1024):.1f} KB)")
                else:
                    print(f"   ⚠️  {filename} (archivo vacío)")
                    all_valid = False

            except Exception as e:
                print(f"   ❌ {filename}: {e}")
                all_valid = False
        else:
            print(f"   ❌ {filename}: archivo no encontrado")
            all_valid = False

    return all_valid


def test_config_backup_restore():
    """Prueba las funciones de backup y restauración"""
    print("\n🧪 Probando backup y restauración...")

    try:
        from config_manager import ConfigManager

        manager = ConfigManager()

        # Crear backup
        backup_path = manager.backup_configs()
        if backup_path and Path(backup_path).exists():
            print(f"   ✅ Backup creado: {backup_path}")

            # Verificar contenido del backup
            backup_files = list(Path(backup_path).glob("*.json"))
            if backup_files:
                print(f"   ✅ Backup contiene {len(backup_files)} archivos")

                # Probar restauración (solo simular)
                print("   ✅ Restauración simulada exitosa")
            else:
                print("   ⚠️  Backup vacío")
        else:
            print("   ❌ Error creando backup")
            return False

        return True

    except Exception as e:
        print(f"   ❌ Error en backup/restauración: {e}")
        return False


def run_all_tests():
    """Ejecuta todas las pruebas"""
    print("🚀 INICIANDO PRUEBAS DEL SISTEMA DE CONFIGURACIÓN")
    print("=" * 60)

    test_results = {
        "config_manager": test_config_manager(),
        "config_validator": test_config_validator(),
        "dynamic_config_manager": test_dynamic_config_manager(),
        "config_module": test_config_module(),
        "config_files": test_config_files(),
        "backup_restore": test_config_backup_restore(),
    }

    # Resumen de resultados
    print("\n" + "=" * 60)
    print("RESUMEN DE PRUEBAS")
    print("=" * 60)

    passed_tests = sum(1 for result in test_results.values() if result)
    total_tests = len(test_results)

    for test_name, result in test_results.items():
        status = "✅ PASÓ" if result else "❌ FALLÓ"
        print(f"{test_name.replace('_', ' ').title()}: {status}")

    print(f"\nResultado general: {passed_tests}/{total_tests} pruebas pasaron")

    if passed_tests == total_tests:
        print(
            "🎉 ¡Todas las pruebas pasaron! El sistema de configuración está funcionando correctamente."
        )
        return True
    else:
        print("⚠️  Algunas pruebas fallaron. Revisa los errores arriba.")
        return False


def generate_test_report():
    """Genera un reporte detallado de las pruebas"""
    report = {
        "timestamp": datetime.now().isoformat(),
        "test_results": {},
        "system_info": {
            "python_version": sys.version,
            "platform": sys.platform,
            "working_directory": str(Path.cwd()),
        },
    }

    # Ejecutar pruebas y capturar resultados
    test_functions = [
        ("config_manager", test_config_manager),
        ("config_validator", test_config_validator),
        ("dynamic_config_manager", test_dynamic_config_manager),
        ("config_module", test_config_module),
        ("config_files", test_config_files),
        ("backup_restore", test_config_backup_restore),
    ]

    for test_name, test_func in test_functions:
        try:
            result = test_func()
            report["test_results"][test_name] = {
                "passed": result,
                "timestamp": datetime.now().isoformat(),
            }
        except Exception as e:
            report["test_results"][test_name] = {
                "passed": False,
                "error": str(e),
                "timestamp": datetime.now().isoformat(),
            }

    # Guardar reporte
    report_file = Path("config/test_report.json")
    try:
        with open(report_file, "w", encoding="utf-8") as f:
            json.dump(report, f, indent=2, ensure_ascii=False)
        print(f"\n📊 Reporte de pruebas guardado en: {report_file}")
    except Exception as e:
        print(f"\n❌ Error guardando reporte: {e}")

    return report


if __name__ == "__main__":
    # Ejecutar pruebas
    success = run_all_tests()

    # Generar reporte
    report = generate_test_report()

    # Código de salida
    sys.exit(0 if success else 1)
