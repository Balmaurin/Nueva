#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
SCRIPT DE PRUEBA PARA EL SISTEMA DE ARRANQUE DEL FRONTEND
=============================================================================
Este script verifica que todos los componentes del sistema de arranque
estén funcionando correctamente antes de iniciar el frontend
=============================================================================
"""

import os
import sys
import json
import subprocess
import platform
from pathlib import Path
from typing import Dict, List, Tuple


class StartupTester:
    """Clase para probar el sistema de arranque del frontend."""

    def __init__(self):
        self.project_dir = Path(__file__).parent
        self.test_results = []

    def log_test(self, test_name: str, success: bool, message: str = ""):
        """Registra el resultado de una prueba."""
        status = "✅ PASÓ" if success else "❌ FALLÓ"
        result = f"{status} {test_name}"
        if message:
            result += f": {message}"

        print(result)
        self.test_results.append(
            {"test": test_name, "success": success, "message": message}
        )

        return success

    def test_project_structure(self) -> bool:
        """Prueba la estructura del proyecto."""
        print("\n🔍 PROBANDO ESTRUCTURA DEL PROYECTO")

        required_files = [
            "package.json",
            "next.config.cjs",
            "tsconfig.json",
            "tailwind.config.ts",
            "postcss.config.cjs",
        ]

        required_dirs = ["app", "components", "contexts", "public"]

        all_passed = True

        # Verificar archivos
        for file_name in required_files:
            file_path = self.project_dir / file_name
            if file_path.exists():
                self.log_test(f"Archivo {file_name}", True)
            else:
                self.log_test(f"Archivo {file_name}", False, "No encontrado")
                all_passed = False

        # Verificar directorios
        for dir_name in required_dirs:
            dir_path = self.project_dir / dir_name
            if dir_path.exists() and dir_path.is_dir():
                self.log_test(f"Directorio {dir_name}", True)
            else:
                self.log_test(f"Directorio {dir_name}", False, "No encontrado")
                all_passed = False

        return all_passed

    def test_package_json(self) -> bool:
        """Prueba la configuración del package.json."""
        print("\n📦 PROBANDO PACKAGE.JSON")

        try:
            package_path = self.project_dir / "package.json"
            with open(package_path, "r") as f:
                package_data = json.load(f)

            # Verificar nombre del proyecto
            if package_data.get("name") == "sheily-landing-next":
                self.log_test("Nombre del proyecto", True)
            else:
                self.log_test(
                    "Nombre del proyecto",
                    False,
                    f"Esperado: sheily-landing-next, Encontrado: {package_data.get('name')}",
                )
                return False

            # Verificar scripts
            scripts = package_data.get("scripts", {})
            required_scripts = ["dev", "build", "start"]

            for script in required_scripts:
                if script in scripts:
                    self.log_test(f"Script {script}", True)
                else:
                    self.log_test(f"Script {script}", False, "No encontrado")
                    return False

            # Verificar dependencias
            dependencies = package_data.get("dependencies", {})
            required_deps = ["next", "react", "react-dom"]

            for dep in required_deps:
                if dep in dependencies:
                    self.log_test(f"Dependencia {dep}", True)
                else:
                    self.log_test(f"Dependencia {dep}", False, "No encontrada")
                    return False

            return True

        except Exception as e:
            self.log_test("Lectura de package.json", False, str(e))
            return False

    def test_system_dependencies(self) -> bool:
        """Prueba las dependencias del sistema."""
        print("\n🖥️ PROBANDO DEPENDENCIAS DEL SISTEMA")

        all_passed = True

        # Verificar Node.js
        try:
            result = subprocess.run(
                ["node", "--version"], capture_output=True, text=True, check=True
            )
            version = result.stdout.strip()
            self.log_test("Node.js", True, f"Versión: {version}")

            # Verificar versión mínima
            major_version = int(version[1:].split(".")[0])
            if major_version >= 18:
                self.log_test(
                    "Versión de Node.js", True, f"Versión {major_version} >= 18"
                )
            else:
                self.log_test(
                    "Versión de Node.js", False, f"Versión {major_version} < 18"
                )
                all_passed = False

        except (subprocess.CalledProcessError, FileNotFoundError):
            self.log_test("Node.js", False, "No instalado o no accesible")
            all_passed = False

        # Verificar npm
        try:
            result = subprocess.run(
                ["npm", "--version"], capture_output=True, text=True, check=True
            )
            version = result.stdout.strip()
            self.log_test("npm", True, f"Versión: {version}")
        except (subprocess.CalledProcessError, FileNotFoundError):
            self.log_test("npm", False, "No instalado o no accesible")
            all_passed = False

        return all_passed

    def test_scripts_permissions(self) -> bool:
        """Prueba los permisos de los scripts de arranque."""
        print("\n🔐 PROBANDO PERMISOS DE SCRIPTS")

        all_passed = True

        scripts = ["start_frontend.sh", "start_frontend.py", "start_frontend.js"]

        for script in scripts:
            script_path = self.project_dir / script
            if script_path.exists():
                # Verificar si es ejecutable
                if os.access(script_path, os.X_OK):
                    self.log_test(f"Permisos de {script}", True)
                else:
                    self.log_test(f"Permisos de {script}", False, "No es ejecutable")
                    all_passed = False
            else:
                self.log_test(f"Script {script}", False, "No encontrado")
                all_passed = False

        return all_passed

    def test_environment_setup(self) -> bool:
        """Prueba la configuración del entorno."""
        print("\n🌍 PROBANDO CONFIGURACIÓN DEL ENTORNO")

        all_passed = True

        # Verificar archivo .env.local
        env_path = self.project_dir / ".env.local"
        if env_path.exists():
            self.log_test("Archivo .env.local", True)
        else:
            self.log_test(
                "Archivo .env.local", False, "No encontrado (se creará automáticamente)"
            )
            # No es crítico, solo informativo

        # Verificar directorio de sonidos
        sounds_dir = self.project_dir / "public" / "sounds"
        if sounds_dir.exists():
            self.log_test("Directorio de sonidos", True)
        else:
            self.log_test(
                "Directorio de sonidos",
                False,
                "No encontrado (se creará automáticamente)",
            )
            # No es crítico, solo informativo

        return all_passed

    def test_port_availability(self) -> bool:
        """Prueba la disponibilidad del puerto 3000."""
        print("\n🔌 PROBANDO DISPONIBILIDAD DE PUERTOS")

        try:
            if platform.system() == "Windows":
                result = subprocess.run(
                    ["netstat", "-ano"], capture_output=True, text=True, check=True
                )
                if ":3000" in result.stdout:
                    self.log_test("Puerto 3000", False, "Puerto en uso")
                    return False
                else:
                    self.log_test("Puerto 3000", True, "Puerto disponible")
                    return True
            else:
                result = subprocess.run(
                    ["lsof", "-ti:3000"], capture_output=True, text=True
                )
                if result.stdout.strip():
                    self.log_test("Puerto 3000", False, "Puerto en uso")
                    return False
                else:
                    self.log_test("Puerto 3000", True, "Puerto disponible")
                    return True

        except Exception as e:
            self.log_test("Verificación de puerto", False, f"Error: {e}")
            return False

    def test_scripts_execution(self) -> bool:
        """Prueba la ejecución de los scripts de arranque."""
        print("\n▶️ PROBANDO EJECUCIÓN DE SCRIPTS")

        all_passed = True

        # Probar script Python (solo verificación, no ejecución completa)
        try:
            script_path = self.project_dir / "start_frontend.py"
            result = subprocess.run(
                [sys.executable, "-m", "py_compile", str(script_path)],
                capture_output=True,
                text=True,
            )
            if result.returncode == 0:
                self.log_test("Script Python", True, "Sintaxis válida")
            else:
                self.log_test("Script Python", False, "Error de sintaxis")
                all_passed = False
        except Exception as e:
            self.log_test("Script Python", False, f"Error: {e}")
            all_passed = False

        # Probar script JavaScript (solo verificación, no ejecución completa)
        try:
            script_path = self.project_dir / "start_frontend.js"
            result = subprocess.run(
                ["node", "--check", str(script_path)], capture_output=True, text=True
            )
            if result.returncode == 0:
                self.log_test("Script JavaScript", True, "Sintaxis válida")
            else:
                self.log_test("Script JavaScript", False, "Error de sintaxis")
                all_passed = False
        except Exception as e:
            self.log_test("Script JavaScript", False, f"Error: {e}")
            all_passed = False

        return all_passed

    def run_all_tests(self) -> bool:
        """Ejecuta todas las pruebas."""
        print("🚀 INICIANDO PRUEBAS DEL SISTEMA DE ARRANQUE")
        print("=" * 60)

        tests = [
            ("Estructura del Proyecto", self.test_project_structure),
            ("Package.json", self.test_package_json),
            ("Dependencias del Sistema", self.test_system_dependencies),
            ("Permisos de Scripts", self.test_scripts_permissions),
            ("Configuración del Entorno", self.test_environment_setup),
            ("Disponibilidad de Puertos", self.test_port_availability),
            ("Ejecución de Scripts", self.test_scripts_execution),
        ]

        all_passed = True

        for test_name, test_func in tests:
            try:
                if not test_func():
                    all_passed = False
            except Exception as e:
                self.log_test(test_name, False, f"Error inesperado: {e}")
                all_passed = False

        return all_passed

    def print_summary(self):
        """Imprime un resumen de los resultados de las pruebas."""
        print("\n" + "=" * 60)
        print("📊 RESUMEN DE PRUEBAS")
        print("=" * 60)

        total_tests = len(self.test_results)
        passed_tests = sum(1 for result in self.test_results if result["success"])
        failed_tests = total_tests - passed_tests

        print(f"Total de pruebas: {total_tests}")
        print(f"✅ Pruebas exitosas: {passed_tests}")
        print(f"❌ Pruebas fallidas: {failed_tests}")

        if failed_tests > 0:
            print(f"\n❌ PRUEBAS FALLIDAS:")
            for result in self.test_results:
                if not result["success"]:
                    print(f"  - {result['test']}: {result['message']}")

        if all_passed:
            print(
                f"\n🎉 ¡TODAS LAS PRUEBAS PASARON! El sistema está listo para arrancar."
            )
        else:
            print(
                f"\n⚠️  Algunas pruebas fallaron. Revisa los errores antes de continuar."
            )

        return all_passed


def main():
    """Función principal."""
    try:
        tester = StartupTester()
        all_passed = tester.run_all_tests()
        tester.print_summary()

        if all_passed:
            print("\n🚀 RECOMENDACIÓN: El frontend está listo para arrancar.")
            print("   Ejecuta uno de estos comandos:")
            print("   - ./start_frontend.sh (Linux/macOS)")
            print("   - python3 start_frontend.py (Universal)")
            print("   - node start_frontend.js (Universal)")
            sys.exit(0)
        else:
            print(
                "\n❌ RECOMENDACIÓN: Corrige los errores antes de arrancar el frontend."
            )
            sys.exit(1)

    except Exception as e:
        print(f"\n💥 ERROR INESPERADO: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
