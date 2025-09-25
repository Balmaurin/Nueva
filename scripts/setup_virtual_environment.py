#!/usr/bin/env python3
"""
Script de Configuración de Entorno Virtual
==========================================

Configura un entorno virtual para el proyecto y maneja las dependencias
correctamente para evitar problemas con PEP 668.
"""

import os
import sys
import subprocess
import json
from pathlib import Path
from datetime import datetime


class VirtualEnvironmentSetup:
    def __init__(self):
        self.project_root = Path.cwd()
        self.venv_path = self.project_root / "venv"
        self.venv_python = self.venv_path / "bin" / "python"
        self.venv_pip = self.venv_path / "bin" / "pip"

    def check_python_version(self):
        """Verifica la versión de Python"""
        print("🐍 Verificando versión de Python...")

        try:
            result = subprocess.run(
                [sys.executable, "--version"], capture_output=True, text=True
            )

            if result.returncode == 0:
                version = result.stdout.strip()
                print(f"✅ {version}")

                # Verificar que es Python 3.8+
                version_parts = version.split()[1].split(".")
                major, minor = int(version_parts[0]), int(version_parts[1])

                if major >= 3 and minor >= 8:
                    print("✅ Versión de Python compatible")
                    return True
                else:
                    print("❌ Se requiere Python 3.8 o superior")
                    return False
            else:
                print("❌ No se pudo obtener la versión de Python")
                return False

        except Exception as e:
            print(f"❌ Error verificando Python: {e}")
            return False

    def check_venv_module(self):
        """Verifica que el módulo venv esté disponible"""
        print("📦 Verificando módulo venv...")

        try:
            result = subprocess.run(
                [sys.executable, "-m", "venv", "--help"], capture_output=True, text=True
            )

            if result.returncode == 0:
                print("✅ Módulo venv disponible")
                return True
            else:
                print("❌ Módulo venv no disponible")
                return False

        except Exception as e:
            print(f"❌ Error verificando venv: {e}")
            return False

    def create_virtual_environment(self):
        """Crea el entorno virtual"""
        print("🔧 Creando entorno virtual...")

        if self.venv_path.exists():
            print("⚠️ El entorno virtual ya existe")
            return True

        try:
            result = subprocess.run(
                [sys.executable, "-m", "venv", str(self.venv_path)],
                capture_output=True,
                text=True,
            )

            if result.returncode == 0:
                print("✅ Entorno virtual creado exitosamente")
                return True
            else:
                print(f"❌ Error creando entorno virtual: {result.stderr}")
                return False

        except Exception as e:
            print(f"❌ Error creando entorno virtual: {e}")
            return False

    def verify_virtual_environment(self):
        """Verifica que el entorno virtual esté funcionando"""
        print("🔍 Verificando entorno virtual...")

        if not self.venv_path.exists():
            print("❌ El entorno virtual no existe")
            return False

        if not self.venv_python.exists():
            print("❌ Python del entorno virtual no encontrado")
            return False

        if not self.venv_pip.exists():
            print("❌ Pip del entorno virtual no encontrado")
            return False

        try:
            # Verificar que el Python del venv funciona
            result = subprocess.run(
                [str(self.venv_python), "--version"], capture_output=True, text=True
            )

            if result.returncode == 0:
                print(f"✅ Entorno virtual funcionando: {result.stdout.strip()}")
                return True
            else:
                print("❌ El entorno virtual no funciona correctamente")
                return False

        except Exception as e:
            print(f"❌ Error verificando entorno virtual: {e}")
            return False

    def upgrade_pip(self):
        """Actualiza pip en el entorno virtual"""
        print("⬆️ Actualizando pip...")

        try:
            result = subprocess.run(
                [str(self.venv_pip), "install", "--upgrade", "pip"],
                capture_output=True,
                text=True,
            )

            if result.returncode == 0:
                print("✅ Pip actualizado")
                return True
            else:
                print(f"❌ Error actualizando pip: {result.stderr}")
                return False

        except Exception as e:
            print(f"❌ Error actualizando pip: {e}")
            return False

    def install_critical_dependencies(self):
        """Instala dependencias críticas en el entorno virtual"""
        print("📦 Instalando dependencias críticas...")

        critical_deps = [
            "torch",
            "transformers",
            "numpy",
            "pandas",
            "fastapi",
            "uvicorn",
            "sqlalchemy",
            "redis",
            "psutil",
            "requests",
            "aiohttp",
            "pydantic",
            "python-multipart",
            "python-jose",
            "passlib",
            "bcrypt",
            "prometheus_client",
            "faiss-cpu",
            # sentence-transformers removido
            "scikit-learn",
        ]

        installed_count = 0
        failed_deps = []

        for dep in critical_deps:
            try:
                print(f"🔧 Instalando {dep}...")
                result = subprocess.run(
                    [str(self.venv_pip), "install", dep],
                    capture_output=True,
                    text=True,
                    timeout=300,
                )

                if result.returncode == 0:
                    print(f"✅ {dep} instalado")
                    installed_count += 1
                else:
                    print(f"❌ Error instalando {dep}: {result.stderr}")
                    failed_deps.append(dep)

            except subprocess.TimeoutExpired:
                print(f"⏰ Timeout instalando {dep}")
                failed_deps.append(dep)
            except Exception as e:
                print(f"❌ Error instalando {dep}: {e}")
                failed_deps.append(dep)

        return installed_count, failed_deps

    def install_optional_dependencies(self):
        """Instala dependencias opcionales"""
        print("📦 Instalando dependencias opcionales...")

        optional_deps = [
            "dash",
            "plotly",
            "matplotlib",
            "seaborn",
            "jupyter",
            "ipython",
        ]

        installed_count = 0

        for dep in optional_deps:
            try:
                print(f"🔧 Instalando {dep}...")
                result = subprocess.run(
                    [str(self.venv_pip), "install", dep],
                    capture_output=True,
                    text=True,
                    timeout=300,
                )

                if result.returncode == 0:
                    print(f"✅ {dep} instalado")
                    installed_count += 1
                else:
                    print(f"⚠️ Error instalando {dep} (opcional): {result.stderr}")

            except subprocess.TimeoutExpired:
                print(f"⏰ Timeout instalando {dep} (opcional)")
            except Exception as e:
                print(f"⚠️ Error instalando {dep} (opcional): {e}")

        return installed_count

    def install_backend_dependencies(self):
        """Instala dependencias específicas del backend"""
        print("🔧 Instalando dependencias del backend...")

        backend_dir = self.project_root / "interface" / "backend"
        requirements_file = backend_dir / "requirements.txt"

        if not requirements_file.exists():
            print("❌ requirements.txt no encontrado en backend")
            return False

        try:
            result = subprocess.run(
                [str(self.venv_pip), "install", "-r", str(requirements_file)],
                capture_output=True,
                text=True,
                timeout=600,
            )

            if result.returncode == 0:
                print("✅ Dependencias del backend instaladas")
                return True
            else:
                print(f"❌ Error instalando dependencias del backend: {result.stderr}")
                return False

        except Exception as e:
            print(f"❌ Error instalando dependencias del backend: {e}")
            return False

    def create_activation_script(self):
        """Crea un script de activación"""
        print("📝 Creando script de activación...")

        activation_script = self.project_root / "activate_venv.sh"

        script_content = f"""#!/bin/bash
# Script de activación del entorno virtual
echo "🔧 Activando entorno virtual..."
source {self.venv_path}/bin/activate
echo "✅ Entorno virtual activado"
echo "🐍 Python: $(python --version)"
echo "📦 Pip: $(pip --version)"
echo ""
echo "Para desactivar: deactivate"
"""

        try:
            with open(activation_script, "w") as f:
                f.write(script_content)

            os.chmod(activation_script, 0o755)
            print("✅ Script de activación creado: activate_venv.sh")
            return True

        except Exception as e:
            print(f"❌ Error creando script de activación: {e}")
            return False

    def generate_setup_report(
        self, installed_critical, failed_deps, installed_optional, backend_success
    ):
        """Genera un reporte de la configuración"""
        print("📊 Generando reporte de configuración...")

        report = {
            "timestamp": datetime.now().isoformat(),
            "project_root": str(self.project_root),
            "venv_path": str(self.venv_path),
            "python_version": str(self.venv_python),
            "pip_version": str(self.venv_pip),
            "installed_critical": installed_critical,
            "failed_dependencies": failed_deps,
            "installed_optional": installed_optional,
            "backend_dependencies": backend_success,
            "activation_script": "activate_venv.sh",
        }

        report_path = self.project_root / "VENV_SETUP_REPORT.json"
        with open(report_path, "w") as f:
            json.dump(report, f, indent=2)

        print(f"✅ Reporte guardado en: {report_path}")
        return report

    def print_summary(self, report):
        """Imprime un resumen de la configuración"""
        print("\n" + "=" * 60)
        print("🎯 RESUMEN DE CONFIGURACIÓN DE ENTORNO VIRTUAL")
        print("=" * 60)

        print(f"📅 Fecha: {report['timestamp']}")
        print(f"📁 Proyecto: {report['project_root']}")
        print(f"🐍 Entorno virtual: {report['venv_path']}")
        print()

        print("📊 DEPENDENCIAS:")
        print(f"   ✅ Críticas instaladas: {report['installed_critical']}")
        print(f"   ❌ Fallidas: {len(report['failed_dependencies'])}")
        print(f"   📦 Opcionales instaladas: {report['installed_optional']}")
        print(f"   🔧 Backend: {'✅' if report['backend_dependencies'] else '❌'}")

        if report["failed_dependencies"]:
            print("\n⚠️ DEPENDENCIAS FALLIDAS:")
            for dep in report["failed_dependencies"]:
                print(f"   - {dep}")

        print(f"\n🔧 SCRIPT DE ACTIVACIÓN: {report['activation_script']}")
        print("\n📋 PRÓXIMOS PASOS:")
        print("1. Activar el entorno virtual: source activate_venv.sh")
        print("2. Verificar instalación: python -c 'import torch; print(\"OK\")'")
        print("3. Ejecutar scripts del proyecto")

        print("\n" + "=" * 60)

    def run_setup(self):
        """Ejecuta toda la configuración del entorno virtual"""
        print("🚀 Iniciando configuración de entorno virtual...")
        print("=" * 60)

        # Verificar Python
        if not self.check_python_version():
            return False

        # Verificar módulo venv
        if not self.check_venv_module():
            return False

        # Crear entorno virtual
        if not self.create_virtual_environment():
            return False

        # Verificar entorno virtual
        if not self.verify_virtual_environment():
            return False

        # Actualizar pip
        if not self.upgrade_pip():
            return False

        # Instalar dependencias críticas
        installed_critical, failed_deps = self.install_critical_dependencies()

        # Instalar dependencias opcionales
        installed_optional = self.install_optional_dependencies()

        # Instalar dependencias del backend
        backend_success = self.install_backend_dependencies()

        # Crear script de activación
        self.create_activation_script()

        # Generar reporte
        report = self.generate_setup_report(
            installed_critical, failed_deps, installed_optional, backend_success
        )

        # Mostrar resumen
        self.print_summary(report)

        return len(failed_deps) == 0


def main():
    setup = VirtualEnvironmentSetup()
    success = setup.run_setup()

    if success:
        print("\n🎉 ¡Configuración completada exitosamente!")
        sys.exit(0)
    else:
        print("\n⚠️ Configuración completada con algunos errores")
        sys.exit(1)


if __name__ == "__main__":
    main()
