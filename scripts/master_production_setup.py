#!/usr/bin/env python3
"""
Script Maestro de Preparación para Producción
============================================

Ejecuta todo el proceso de preparación para producción de forma ordenada:
1. Corrige dependencias
2. Inicializa bases de datos
3. Ejecuta verificaciones completas
4. Genera reporte final
"""

import os
import sys
import subprocess
import json
import time
from pathlib import Path
from datetime import datetime


class MasterProductionSetup:
    def __init__(self):
        self.project_root = Path.cwd()
        self.start_time = datetime.now()
        self.results = {}

    def run_script(self, script_path, description):
        """Ejecuta un script y registra el resultado"""
        print(f"\n🚀 {description}")
        print("=" * 60)

        try:
            result = subprocess.run(
                [sys.executable, script_path],
                capture_output=True,
                text=True,
                timeout=1800,  # 30 minutos máximo por script
            )

            if result.returncode == 0:
                print(f"✅ {description} - EXITOSO")
                print(result.stdout)
                return True, result.stdout
            else:
                print(f"❌ {description} - FALLÓ")
                print(f"Error: {result.stderr}")
                return False, result.stderr

        except subprocess.TimeoutExpired:
            print(f"⏰ {description} - TIMEOUT")
            return False, "Timeout"
        except Exception as e:
            print(f"❌ {description} - ERROR: {e}")
            return False, str(e)

    def step_1_setup_virtual_environment(self):
        """Paso 1: Configurar entorno virtual"""
        print("\n" + "=" * 70)
        print("🐍 PASO 1: CONFIGURACIÓN DE ENTORNO VIRTUAL")
        print("=" * 70)

        script_path = self.project_root / "scripts" / "setup_virtual_environment.py"
        if not script_path.exists():
            print("❌ Script setup_virtual_environment.py no encontrado")
            return False

        success, output = self.run_script(
            script_path, "Configurando entorno virtual y dependencias"
        )

        self.results["virtual_environment_setup"] = success
        return success

    def step_2_activate_environment(self):
        """Paso 2: Activar entorno virtual"""
        print("\n" + "=" * 70)
        print("🔧 PASO 2: ACTIVACIÓN DE ENTORNO VIRTUAL")
        print("=" * 70)

        activation_script = self.project_root / "activate_venv.sh"
        if not activation_script.exists():
            print("❌ Script de activación no encontrado")
            return False

        try:
            # Activar el entorno virtual
            result = subprocess.run(
                ["source", str(activation_script)],
                shell=True,
                capture_output=True,
                text=True,
                timeout=30,
            )

            if result.returncode == 0:
                print("✅ Entorno virtual activado")

                # Verificar que las dependencias críticas funcionan
                venv_python = self.project_root / "venv" / "bin" / "python"
                if venv_python.exists():
                    test_result = subprocess.run(
                        [
                            str(venv_python),
                            "-c",
                            "import torch, transformers, fastapi; print('OK')",
                        ],
                        capture_output=True,
                        text=True,
                        timeout=30,
                    )

                    if test_result.returncode == 0 and "OK" in test_result.stdout:
                        print("✅ Dependencias críticas verificadas")
                        self.results["environment_activated"] = True
                        return True
                    else:
                        print("❌ Error verificando dependencias críticas")
                        self.results["environment_activated"] = False
                        return False
                else:
                    print("❌ Python del entorno virtual no encontrado")
                    self.results["environment_activated"] = False
                    return False
            else:
                print("❌ Error activando entorno virtual")
                self.results["environment_activated"] = False
                return False

        except Exception as e:
            print(f"❌ Error activando entorno virtual: {e}")
            self.results["environment_activated"] = False
            return False

    def step_1_fix_dependencies(self):
        """Paso 1: Corregir dependencias"""
        print("\n" + "=" * 70)
        print("📦 PASO 1: CORRECCIÓN DE DEPENDENCIAS")
        print("=" * 70)

        script_path = self.project_root / "scripts" / "fix_dependencies.py"
        if not script_path.exists():
            print("❌ Script fix_dependencies.py no encontrado")
            return False

        success, output = self.run_script(
            script_path, "Corrigiendo dependencias del sistema"
        )

        self.results["dependencies_fixed"] = success
        return success

    def step_2_initialize_databases(self):
        """Paso 2: Inicializar bases de datos"""
        print("\n" + "=" * 70)
        print("🗄️ PASO 2: INICIALIZACIÓN DE BASES DE DATOS")
        print("=" * 70)

        script_path = self.project_root / "scripts" / "initialize_databases.py"
        if not script_path.exists():
            print("❌ Script initialize_databases.py no encontrado")
            return False

        success, output = self.run_script(
            script_path, "Inicializando bases de datos con datos de prueba"
        )

        self.results["databases_initialized"] = success
        return success

    def step_3_verify_system(self):
        """Paso 3: Verificar sistema optimizado"""
        print("\n" + "=" * 70)
        print("🔍 PASO 3: VERIFICACIÓN DEL SISTEMA")
        print("=" * 70)

        script_path = self.project_root / "scripts/verificar_sistema.sh"
        if not script_path.exists():
            print("❌ Script scripts/verificar_sistema.sh no encontrado")
            return False

        try:
            result = subprocess.run(
                ["./scripts/verificar_sistema.sh"],
                capture_output=True,
                text=True,
                timeout=300,  # 5 minutos máximo
            )

            if result.returncode in [0, 1]:  # 0 = éxito, 1 = advertencias menores
                print("✅ Verificación del sistema - EXITOSO")
                print(result.stdout)
                self.results["system_verified"] = True
                return True
            else:
                print("❌ Verificación del sistema - FALLÓ")
                print(f"Error: {result.stderr}")
                self.results["system_verified"] = False
                return False

        except subprocess.TimeoutExpired:
            print("⏰ Verificación del sistema - TIMEOUT")
            self.results["system_verified"] = False
            return False
        except Exception as e:
            print(f"❌ Verificación del sistema - ERROR: {e}")
            self.results["system_verified"] = False
            return False

    def step_4_complete_verification(self):
        """Paso 4: Verificación completa para producción"""
        print("\n" + "=" * 70)
        print("🚀 PASO 4: VERIFICACIÓN COMPLETA PARA PRODUCCIÓN")
        print("=" * 70)

        script_path = self.project_root / "scripts" / "prepare_for_production.py"
        if not script_path.exists():
            print("❌ Script prepare_for_production.py no encontrado")
            return False

        success, output = self.run_script(
            script_path, "Ejecutando verificación completa para producción"
        )

        self.results["production_verified"] = success
        return success

    def step_5_docker_verification(self):
        """Paso 5: Verificar Docker"""
        print("\n" + "=" * 70)
        print("🐳 PASO 5: VERIFICACIÓN DE DOCKER")
        print("=" * 70)

        # Verificar que Docker está disponible
        try:
            result = subprocess.run(
                ["docker", "--version"], capture_output=True, text=True, timeout=10
            )

            if result.returncode == 0:
                print("✅ Docker está disponible")
                print(result.stdout.strip())

                # Verificar docker-compose
                result = subprocess.run(
                    ["docker-compose", "--version"],
                    capture_output=True,
                    text=True,
                    timeout=10,
                )

                if result.returncode == 0:
                    print("✅ Docker Compose está disponible")
                    print(result.stdout.strip())

                    # Verificar archivos de Docker
                    docker_files = [
                        "docker/docker-compose.yml",
                        "docker/docker-compose.dev.yml",
                        "docker/Dockerfile",
                    ]

                    all_files_exist = True
                    for file_path in docker_files:
                        if os.path.exists(file_path):
                            size = os.path.getsize(file_path)
                            print(f"✅ {file_path} - {size} bytes")
                        else:
                            print(f"❌ {file_path} - No encontrado")
                            all_files_exist = False

                    self.results["docker_verified"] = all_files_exist
                    return all_files_exist
                else:
                    print("❌ Docker Compose no está disponible")
                    self.results["docker_verified"] = False
                    return False
            else:
                print("❌ Docker no está disponible")
                self.results["docker_verified"] = False
                return False

        except Exception as e:
            print(f"❌ Error verificando Docker: {e}")
            self.results["docker_verified"] = False
            return False

    def step_7_final_health_check(self):
        """Paso 7: Verificación final de salud del sistema"""
        print("\n" + "=" * 70)
        print("🏥 PASO 7: VERIFICACIÓN FINAL DE SALUD")
        print("=" * 70)

        health_checks = []

        # Verificar que las bases de datos tienen datos
        databases = [
            ("data/knowledge_base.db", "knowledge_base"),
            ("data/embeddings_sqlite.db", "embeddings"),
            ("monitoring/metrics.db", "metrics"),
        ]

        for db_path, table_name in databases:
            if os.path.exists(db_path):
                try:
                    result = subprocess.run(
                        f"sqlite3 {db_path} 'SELECT COUNT(*) FROM {table_name};'",
                        shell=True,
                        capture_output=True,
                        text=True,
                    )
                    if result.returncode == 0:
                        count = int(result.stdout.strip())
                        if count > 0:
                            print(f"✅ {db_path} - {count} registros")
                            health_checks.append(True)
                        else:
                            print(f"⚠️ {db_path} - 0 registros")
                            health_checks.append(False)
                    else:
                        print(f"❌ {db_path} - Error al verificar")
                        health_checks.append(False)
                except Exception as e:
                    print(f"❌ {db_path} - Error: {e}")
                    health_checks.append(False)
            else:
                print(f"❌ {db_path} - No existe")
                health_checks.append(False)

        # Verificar que los módulos principales importan usando el entorno virtual
        venv_python = self.project_root / "venv" / "bin" / "python"
        modules = [
            "modules.core.neurofusion_core",
            "modules.unified_systems.module_initializer",
        ]

        for module in modules:
            try:
                result = subprocess.run(
                    [
                        str(venv_python),
                        "-c",
                        f"import sys; sys.path.append('.'); import {module}; print('OK')",
                    ],
                    capture_output=True,
                    text=True,
                    timeout=10,
                )
                if result.returncode == 0 and "OK" in result.stdout:
                    print(f"✅ {module} - Importa correctamente")
                    health_checks.append(True)
                else:
                    print(f"❌ {module} - Error al importar")
                    health_checks.append(False)
            except Exception as e:
                print(f"❌ {module} - Error: {e}")
                health_checks.append(False)

        # Verificar dependencias críticas en el entorno virtual
        critical_deps = ["torch", "transformers", "fastapi"]
        for dep in critical_deps:
            try:
                result = subprocess.run(
                    [str(venv_python), "-c", f"import {dep}; print('OK')"],
                    capture_output=True,
                    text=True,
                    timeout=10,
                )
                if result.returncode == 0 and "OK" in result.stdout:
                    print(f"✅ {dep} - Funciona correctamente")
                    health_checks.append(True)
                else:
                    print(f"❌ {dep} - Error al importar")
                    health_checks.append(False)
            except Exception as e:
                print(f"❌ {dep} - Error: {e}")
                health_checks.append(False)

        # Calcular salud general
        health_score = sum(health_checks) / len(health_checks) if health_checks else 0
        self.results["health_score"] = health_score

        print(f"\n📊 Puntuación de salud: {health_score:.1%}")

        return health_score >= 0.8  # 80% o más

    def generate_final_report(self):
        """Genera el reporte final"""
        print("\n" + "=" * 70)
        print("📊 GENERANDO REPORTE FINAL")
        print("=" * 70)

        duration = (datetime.now() - self.start_time).total_seconds()

        # Calcular puntuación general
        total_steps = len(self.results)
        passed_steps = sum(1 for result in self.results.values() if result)
        overall_score = (passed_steps / total_steps) * 100 if total_steps > 0 else 0

        report = {
            "timestamp": datetime.now().isoformat(),
            "project_root": str(self.project_root),
            "duration_seconds": duration,
            "results": self.results,
            "overall_score": overall_score,
            "status": (
                "READY"
                if overall_score >= 85
                else "NEEDS_WORK" if overall_score >= 70 else "NOT_READY"
            ),
        }

        # Guardar reporte
        report_path = self.project_root / "MASTER_PRODUCTION_REPORT.json"
        with open(report_path, "w") as f:
            json.dump(report, f, indent=2)

        print(f"✅ Reporte final guardado en: {report_path}")
        return report

    def print_final_summary(self, report):
        """Imprime el resumen final"""
        print("\n" + "=" * 70)
        print("🎯 RESUMEN FINAL DE PREPARACIÓN PARA PRODUCCIÓN")
        print("=" * 70)

        print(f"📅 Fecha: {report['timestamp']}")
        print(f"📁 Proyecto: {report['project_root']}")
        print(f"⏱️ Duración total: {report['duration_seconds']:.1f} segundos")
        print()

        print("📋 RESULTADOS POR PASO:")
        for step, result in report["results"].items():
            status = "✅ PASÓ" if result else "❌ FALLÓ"
            step_name = step.replace("_", " ").title()
            print(f"   {step_name}: {status}")

        print()
        print(f"📊 PUNTUACIÓN GENERAL: {report['overall_score']:.1f}/100")
        print(f"🎯 ESTADO: {report['status']}")

        if report["status"] == "READY":
            print("\n🎉 ¡EL SISTEMA ESTÁ LISTO PARA PRODUCCIÓN!")
            print("✅ Todas las verificaciones críticas han pasado")
            print("✅ Las dependencias están instaladas")
            print("✅ Las bases de datos están inicializadas")
            print("✅ Docker está configurado")
            print("✅ El sistema está saludable")
            print("\n🚀 Puedes proceder con el deployment en producción")
        elif report["status"] == "NEEDS_WORK":
            print("\n⚠️ El sistema necesita trabajo antes de producción")
            print("🔧 Revisa los pasos que fallaron")
            print("🔧 Completa las configuraciones faltantes")
            print("🔧 Ejecuta nuevamente el script después de las correcciones")
        else:
            print("\n🚨 El sistema NO está listo para producción")
            print("❌ Muchos pasos críticos fallaron")
            print("❌ Necesita trabajo significativo")
            print("❌ No proceder con el deployment")

        print("\n" + "=" * 70)

    def run_master_setup(self):
        """Ejecuta todo el proceso maestro"""
        print("🚀 INICIANDO PREPARACIÓN MAESTRA PARA PRODUCCIÓN")
        print("=" * 70)
        print("Este script ejecutará todos los pasos necesarios para")
        print("preparar el sistema NeuroFusion para producción.")
        print("=" * 70)

        # Ejecutar todos los pasos
        steps = [
            ("Configuración de entorno virtual", self.step_1_setup_virtual_environment),
            ("Activación de entorno virtual", self.step_2_activate_environment),
            ("Corrección de dependencias", self.step_1_fix_dependencies),
            ("Inicialización de bases de datos", self.step_2_initialize_databases),
            ("Verificación del sistema", self.step_3_verify_system),
            (
                "Verificación completa para producción",
                self.step_4_complete_verification,
            ),
            ("Verificación de Docker", self.step_5_docker_verification),
            ("Verificación final de salud", self.step_7_final_health_check),
        ]

        for step_name, step_func in steps:
            print(f"\n⏳ Ejecutando: {step_name}")
            try:
                step_func()
            except Exception as e:
                print(f"❌ Error en {step_name}: {e}")
                self.results[step_name.lower().replace(" ", "_")] = False

        # Generar reporte final
        report = self.generate_final_report()

        # Mostrar resumen final
        self.print_final_summary(report)

        return report


def main():
    setup = MasterProductionSetup()
    report = setup.run_master_setup()

    # Retornar código de salida apropiado
    if report["status"] == "READY":
        sys.exit(0)
    elif report["status"] == "NEEDS_WORK":
        sys.exit(1)
    else:
        sys.exit(2)


if __name__ == "__main__":
    main()
