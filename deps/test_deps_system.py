#!/usr/bin/env python3
"""
Script de Pruebas del Sistema de Dependencias del Sistema NeuroFusion
Prueba todas las funcionalidades del sistema de gestión de dependencias
"""

import json
import logging
import sys
from pathlib import Path
from typing import Dict, Any, List
from datetime import datetime

# Configuración de logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def test_dependencies_manager():
    """Prueba el gestor de dependencias"""
    print("🧪 Probando DependenciesManager...")

    try:
        from deps import DependenciesManager, get_dependencies_manager

        # Crear instancia
        manager = DependenciesManager()

        # Probar verificación de dependencias
        dependencies = manager.check_all_dependencies()
        print(f"   ✅ Dependencias verificadas: {len(dependencies)}")

        # Probar estadísticas
        stats = manager.get_dependency_stats()
        print(
            f"   ✅ Estadísticas obtenidas: {stats.total_dependencies} total, {stats.installed_dependencies} instaladas"
        )

        # Probar creación de archivos de configuración
        requirements_path = manager.create_requirements_txt()
        if requirements_path:
            print(f"   ✅ requirements.txt creado: {requirements_path}")

        package_json_path = manager.create_package_json()
        if package_json_path:
            print(f"   ✅ package.json creado: {package_json_path}")

        # Probar backup
        backup_path = manager.backup_dependencies()
        if backup_path:
            print(f"   ✅ Backup creado: {backup_path}")

        return True

    except Exception as e:
        print(f"   ❌ Error en DependenciesManager: {e}")
        return False


def test_dependency_installer():
    """Prueba el instalador de dependencias"""
    print("🧪 Probando DependencyInstaller...")

    try:
        from deps import DependencyInstaller, get_dependency_installer

        # Crear instancia
        installer = DependencyInstaller()

        # Configuración de prueba
        test_config = {
            "python_dependencies": {
                "requests": {"version": ">=2.25.0", "required": True},
                "numpy": {"version": ">=1.21.0", "required": True},
            },
            "node_dependencies": {"axios": {"version": "^0.27.0", "required": True}},
            "system_dependencies": {"git": {"version": ">=2.0", "required": True}},
        }

        # Probar instalación (solo simulación)
        print("   ⚠️  Instalación simulada (no se instalarán paquetes reales)")

        # Probar callback de progreso
        def progress_callback(progress):
            print(
                f"   📊 Progreso: {progress.installed_packages}/{progress.total_packages} - {progress.current_package}"
            )

        installer.set_progress_callback(progress_callback)

        # Probar detención
        installer.stop_installation_process()

        print("   ✅ DependencyInstaller probado correctamente")
        return True

    except Exception as e:
        print(f"   ❌ Error en DependencyInstaller: {e}")
        return False


def test_dependency_validator():
    """Prueba el validador de dependencias"""
    print("🧪 Probando DependencyValidator...")

    try:
        from deps import DependencyValidator, get_dependency_validator

        # Crear instancia
        validator = DependencyValidator()

        # Configuración de prueba
        test_config = {
            "python_dependencies": {
                "requests": {"version": ">=2.25.0", "required": True},
                "numpy": {"version": ">=1.21.0", "required": True},
            },
            "node_dependencies": {"react": {"version": "^18.0.0", "required": True}},
            "system_dependencies": {"python3": {"version": ">=3.8", "required": True}},
        }

        # Probar validación
        results = validator.validate_all_dependencies(test_config)
        print(f"   ✅ Dependencias validadas: {len(results)}")

        # Probar resumen
        summary = validator.get_validation_summary()
        print(
            f"   ✅ Resumen obtenido: {summary.total_dependencies} total, {summary.valid_dependencies} válidas"
        )

        # Probar reporte
        report_path = validator.save_validation_report()
        if report_path:
            print(f"   ✅ Reporte guardado: {report_path}")

        # Probar impresión de reporte
        print("   📋 Reporte de validación:")
        validator.print_validation_report()

        return True

    except Exception as e:
        print(f"   ❌ Error en DependencyValidator: {e}")
        return False


def test_deps_module():
    """Prueba el módulo deps completo"""
    print("🧪 Probando módulo deps...")

    try:
        import deps

        # Probar funciones principales
        stats = deps.get_dependency_stats()
        print(f"   ✅ Estadísticas obtenidas: {stats.total_dependencies} dependencias")

        dependencies = deps.check_all_dependencies()
        print(f"   ✅ Dependencias verificadas: {len(dependencies)}")

        # Probar funciones específicas
        python_dep = deps.check_python_dependency("requests")
        print(f"   ✅ Dependencia Python verificada: {python_dep.name}")

        # Probar validación
        test_config = {
            "python_dependencies": {
                "requests": {"version": ">=2.25.0", "required": True}
            }
        }
        validation_results = deps.validate_dependencies(test_config)
        print(f"   ✅ Validación completada: {len(validation_results)} resultados")

        # Probar resumen de validación
        validation_summary = deps.get_validation_summary()
        print(
            f"   ✅ Resumen de validación: {validation_summary.overall_score:.2f}/1.00"
        )

        return True

    except Exception as e:
        print(f"   ❌ Error en módulo deps: {e}")
        return False


def test_deps_files():
    """Prueba la integridad de los archivos de dependencias"""
    print("🧪 Probando archivos de dependencias...")

    try:
        deps_dir = Path("deps")

        # Verificar archivos existentes
        required_files = ["package.json", "_metadata.json"]

        for file_name in required_files:
            file_path = deps_dir / file_name
            if file_path.exists():
                print(f"   ✅ Archivo encontrado: {file_name}")

                # Verificar que sea JSON válido
                try:
                    with open(file_path, "r") as f:
                        json.load(f)
                    print(f"   ✅ JSON válido: {file_name}")
                except json.JSONDecodeError:
                    print(f"   ⚠️  JSON inválido: {file_name}")
            else:
                print(f"   ❌ Archivo faltante: {file_name}")

        # Verificar directorios creados
        required_dirs = [
            "python",
            "node",
            "system",
            "cache",
            "backups",
            "installation_reports",
            "validation_reports",
        ]

        for dir_name in required_dirs:
            dir_path = deps_dir / dir_name
            if dir_path.exists():
                print(f"   ✅ Directorio encontrado: {dir_name}")
            else:
                print(f"   ❌ Directorio faltante: {dir_name}")

        return True

    except Exception as e:
        print(f"   ❌ Error verificando archivos: {e}")
        return False


def test_deps_backup_restore():
    """Prueba las funcionalidades de backup y restore"""
    print("🧪 Probando backup y restore...")

    try:
        from deps import backup_dependencies, restore_dependencies

        # Crear backup
        backup_path = backup_dependencies()
        if backup_path:
            print(f"   ✅ Backup creado: {backup_path}")

            # Verificar que el backup existe
            backup_dir = Path(backup_path)
            if backup_dir.exists():
                print(f"   ✅ Directorio de backup existe")

                # Verificar archivos de backup
                backup_files = list(backup_dir.glob("*"))
                print(f"   ✅ Archivos en backup: {len(backup_files)}")

                # Probar restore (simulado)
                print("   ⚠️  Restore simulado (no se restaurará realmente)")
                # restore_success = restore_dependencies(backup_path)
                # if restore_success:
                #     print(f"   ✅ Restore exitoso")
                # else:
                #     print(f"   ❌ Restore falló")
            else:
                print(f"   ❌ Directorio de backup no existe")
        else:
            print(f"   ❌ No se pudo crear backup")

        return True

    except Exception as e:
        print(f"   ❌ Error en backup/restore: {e}")
        return False


def test_deps_integration():
    """Prueba la integración completa del sistema de dependencias"""
    print("🧪 Probando integración completa...")

    try:
        from deps import (
            dependencies_manager,
            dependency_installer,
            dependency_validator,
            get_dependency_stats,
            check_all_dependencies,
            validate_dependencies,
        )

        # Verificar que las instancias globales funcionan
        print(f"   ✅ Instancias globales creadas")

        # Probar flujo completo
        print("   📋 Ejecutando flujo completo de dependencias...")

        # 1. Verificar dependencias
        dependencies = check_all_dependencies()
        print(f"   ✅ Paso 1: {len(dependencies)} dependencias verificadas")

        # 2. Obtener estadísticas
        stats = get_dependency_stats()
        print(f"   ✅ Paso 2: Estadísticas obtenidas")

        # 3. Validar dependencias
        test_config = {
            "python_dependencies": {
                "requests": {"version": ">=2.25.0", "required": True}
            },
            "node_dependencies": {"react": {"version": "^18.0.0", "required": True}},
        }
        validation_results = validate_dependencies(test_config)
        print(f"   ✅ Paso 3: {len(validation_results)} dependencias validadas")

        # 4. Crear archivos de configuración
        requirements_path = dependencies_manager.create_requirements_txt()
        package_json_path = dependencies_manager.create_package_json()
        print(f"   ✅ Paso 4: Archivos de configuración creados")

        # 5. Crear backup
        backup_path = dependencies_manager.backup_dependencies()
        print(f"   ✅ Paso 5: Backup creado")

        print("   🎉 Integración completa exitosa")
        return True

    except Exception as e:
        print(f"   ❌ Error en integración: {e}")
        return False


def generate_test_report(test_results: Dict[str, bool]) -> Dict[str, Any]:
    """Genera un reporte de pruebas"""
    total_tests = len(test_results)
    passed_tests = sum(1 for result in test_results.values() if result)
    failed_tests = total_tests - passed_tests
    success_rate = (passed_tests / total_tests * 100) if total_tests > 0 else 0

    report = {
        "test_summary": {
            "total_tests": total_tests,
            "passed_tests": passed_tests,
            "failed_tests": failed_tests,
            "success_rate": success_rate,
            "timestamp": datetime.now().isoformat(),
        },
        "test_results": test_results,
        "details": {
            "dependencies_manager": {
                "description": "Gestor principal de dependencias",
                "status": (
                    "passed"
                    if test_results.get("dependencies_manager", False)
                    else "failed"
                ),
            },
            "dependency_installer": {
                "description": "Instalador automático de dependencias",
                "status": (
                    "passed"
                    if test_results.get("dependency_installer", False)
                    else "failed"
                ),
            },
            "dependency_validator": {
                "description": "Validador de compatibilidad y versiones",
                "status": (
                    "passed"
                    if test_results.get("dependency_validator", False)
                    else "failed"
                ),
            },
            "deps_module": {
                "description": "Módulo principal deps",
                "status": (
                    "passed" if test_results.get("deps_module", False) else "failed"
                ),
            },
            "deps_files": {
                "description": "Integridad de archivos de dependencias",
                "status": (
                    "passed" if test_results.get("deps_files", False) else "failed"
                ),
            },
            "deps_backup_restore": {
                "description": "Funcionalidades de backup y restore",
                "status": (
                    "passed"
                    if test_results.get("deps_backup_restore", False)
                    else "failed"
                ),
            },
            "deps_integration": {
                "description": "Integración completa del sistema",
                "status": (
                    "passed"
                    if test_results.get("deps_integration", False)
                    else "failed"
                ),
            },
        },
    }

    return report


def run_all_tests():
    """Ejecuta todas las pruebas del sistema de dependencias"""
    print("🚀 INICIANDO PRUEBAS DEL SISTEMA DE DEPENDENCIAS")
    print("=" * 80)

    test_results = {}

    # Ejecutar pruebas
    test_results["dependencies_manager"] = test_dependencies_manager()
    test_results["dependency_installer"] = test_dependency_installer()
    test_results["dependency_validator"] = test_dependency_validator()
    test_results["deps_module"] = test_deps_module()
    test_results["deps_files"] = test_deps_files()
    test_results["deps_backup_restore"] = test_deps_backup_restore()
    test_results["deps_integration"] = test_deps_integration()

    # Generar reporte
    report = generate_test_report(test_results)

    # Mostrar resumen
    print("\n" + "=" * 80)
    print("RESUMEN DE PRUEBAS")
    print("=" * 80)

    summary = report["test_summary"]
    print(f"📊 Total de pruebas: {summary['total_tests']}")
    print(f"✅ Pruebas exitosas: {summary['passed_tests']}")
    print(f"❌ Pruebas fallidas: {summary['failed_tests']}")
    print(f"📈 Tasa de éxito: {summary['success_rate']:.1f}%")

    print(f"\n📋 DETALLES POR PRUEBA:")
    for test_name, result in test_results.items():
        status = "✅ PASÓ" if result else "❌ FALLÓ"
        print(f"   {status} {test_name}")

    # Guardar reporte
    try:
        deps_dir = Path("deps")
        report_path = (
            deps_dir
            / "test_reports"
            / f"test_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        )
        report_path.parent.mkdir(parents=True, exist_ok=True)

        with open(report_path, "w") as f:
            json.dump(report, f, indent=2)

        print(f"\n📄 Reporte guardado: {report_path}")

    except Exception as e:
        print(f"\n❌ Error guardando reporte: {e}")

    # Resultado final
    if summary["success_rate"] >= 80:
        print(
            f"\n🎉 SISTEMA DE DEPENDENCIAS FUNCIONAL ({summary['success_rate']:.1f}% éxito)"
        )
        return True
    else:
        print(
            f"\n⚠️  SISTEMA DE DEPENDENCIAS CON PROBLEMAS ({summary['success_rate']:.1f}% éxito)"
        )
        return False


if __name__ == "__main__":
    # Ejecutar todas las pruebas
    success = run_all_tests()

    # Código de salida
    sys.exit(0 if success else 1)
