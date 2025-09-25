#!/usr/bin/env python3
"""
Script de Corrección de Dependencias
====================================

Verifica y corrige dependencias faltantes para preparar el sistema para producción.
"""

import os
import sys
import subprocess
import json
from pathlib import Path


class DependencyFixer:
    def __init__(self):
        self.project_root = Path.cwd()
        self.missing_deps = []

    def check_python_dependency(self, package_name):
        """Verifica si una dependencia Python está instalada"""
        try:
            __import__(package_name)
            return True
        except ImportError:
            return False

    def install_python_dependency(self, package_name):
        """Instala una dependencia Python"""
        try:
            print(f"🔧 Instalando {package_name}...")
            result = subprocess.run(
                [sys.executable, "-m", "pip", "install", package_name],
                capture_output=True,
                text=True,
                timeout=300,
            )
            if result.returncode == 0:
                print(f"✅ {package_name} instalado correctamente")
                return True
            else:
                print(f"❌ Error instalando {package_name}: {result.stderr}")
                return False
        except Exception as e:
            print(f"❌ Error instalando {package_name}: {e}")
            return False

    def check_system_dependency(self, command):
        """Verifica si una dependencia del sistema está disponible"""
        try:
            result = subprocess.run(
                ["which", command], capture_output=True, text=True, timeout=10
            )
            return result.returncode == 0
        except Exception:
            return False

    def install_system_dependency(self, package_name, install_command=None):
        """Instala una dependencia del sistema"""
        if install_command is None:
            install_command = f"sudo apt-get install -y {package_name}"

        try:
            print(f"🔧 Instalando {package_name}...")
            result = subprocess.run(
                install_command, shell=True, capture_output=True, text=True, timeout=300
            )
            if result.returncode == 0:
                print(f"✅ {package_name} instalado correctamente")
                return True
            else:
                print(f"❌ Error instalando {package_name}: {result.stderr}")
                return False
        except Exception as e:
            print(f"❌ Error instalando {package_name}: {e}")
            return False

    def fix_python_dependencies(self):
        """Corrige dependencias Python faltantes"""
        print("📦 Verificando y corrigiendo dependencias Python...")

        # Dependencias críticas para el sistema
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

        # Dependencias opcionales pero recomendadas
        optional_deps = [
            "dash",
            "plotly",
            "matplotlib",
            "seaborn",
            "jupyter",
            "ipython",
        ]

        all_deps = critical_deps + optional_deps
        fixed_count = 0

        for dep in all_deps:
            if not self.check_python_dependency(dep):
                print(f"❌ {dep} - NO INSTALADO")
                if dep in critical_deps:
                    if self.install_python_dependency(dep):
                        fixed_count += 1
                    else:
                        self.missing_deps.append(f"python:{dep}")
                else:
                    print(f"⚠️ {dep} - Opcional, saltando...")
            else:
                print(f"✅ {dep} - Ya instalado")

        return fixed_count

    def fix_system_dependencies(self):
        """Corrige dependencias del sistema faltantes"""
        print("🔧 Verificando y corrigiendo dependencias del sistema...")

        system_deps = [
            ("docker", "docker.io"),
            ("docker-compose", "docker-compose"),
            ("node", "nodejs"),
            ("npm", "npm"),
            ("git", "git"),
            ("curl", "curl"),
            ("sqlite3", "sqlite3"),
            ("jq", "jq"),
        ]

        fixed_count = 0

        for command, package in system_deps:
            if not self.check_system_dependency(command):
                print(f"❌ {command} - NO INSTALADO")
                if self.install_system_dependency(package):
                    fixed_count += 1
                else:
                    self.missing_deps.append(f"system:{command}")
            else:
                print(f"✅ {command} - Ya instalado")

        return fixed_count

    def fix_backend_dependencies(self):
        """Corrige dependencias específicas del backend"""
        print("🔧 Verificando dependencias del backend...")

        backend_dir = self.project_root / "interface" / "backend"
        if not backend_dir.exists():
            print("❌ Directorio backend no encontrado")
            return 0

        requirements_file = backend_dir / "requirements.txt"
        if not requirements_file.exists():
            print("❌ requirements.txt no encontrado en backend")
            return 0

        try:
            print("🔧 Instalando dependencias del backend...")
            original_cwd = os.getcwd()
            os.chdir(backend_dir)

            result = subprocess.run(
                [sys.executable, "-m", "pip", "install", "-r", "requirements.txt"],
                capture_output=True,
                text=True,
                timeout=600,
            )

            os.chdir(original_cwd)

            if result.returncode == 0:
                print("✅ Dependencias del backend instaladas correctamente")
                return 1
            else:
                print(f"❌ Error instalando dependencias del backend: {result.stderr}")
                return 0

        except Exception as e:
            print(f"❌ Error instalando dependencias del backend: {e}")
            return 0

    def fix_frontend_dependencies(self):
        """Corrige dependencias específicas del frontend"""
        print("🎨 Verificando dependencias del frontend...")

        frontend_dir = self.project_root / "interface" / "frontend"
        if not frontend_dir.exists():
            print("❌ Directorio frontend no encontrado")
            return 0

        package_json = frontend_dir / "package.json"
        if not package_json.exists():
            print("❌ package.json no encontrado en frontend")
            return 0

        try:
            print("🔧 Instalando dependencias del frontend...")
            original_cwd = os.getcwd()
            os.chdir(frontend_dir)

            # Verificar si node_modules existe
            if not (frontend_dir / "node_modules").exists():
                result = subprocess.run(
                    ["npm", "install"], capture_output=True, text=True, timeout=600
                )

                if result.returncode == 0:
                    print("✅ Dependencias del frontend instaladas correctamente")
                    os.chdir(original_cwd)
                    return 1
                else:
                    print(
                        f"❌ Error instalando dependencias del frontend: {result.stderr}"
                    )
                    os.chdir(original_cwd)
                    return 0
            else:
                print("✅ node_modules ya existe")
                os.chdir(original_cwd)
                return 1

        except Exception as e:
            print(f"❌ Error instalando dependencias del frontend: {e}")
            return 0

    def generate_dependency_report(self):
        """Genera un reporte de dependencias"""
        report = {
            "timestamp": str(Path.cwd()),
            "missing_dependencies": self.missing_deps,
            "total_missing": len(self.missing_deps),
        }

        report_path = self.project_root / "DEPENDENCY_REPORT.json"
        with open(report_path, "w") as f:
            json.dump(report, f, indent=2)

        print(f"✅ Reporte de dependencias guardado en: {report_path}")
        return report

    def run_dependency_fix(self):
        """Ejecuta toda la corrección de dependencias"""
        print("🚀 Iniciando corrección de dependencias...")
        print("=" * 50)

        total_fixed = 0

        # Corregir dependencias Python
        fixed_python = self.fix_python_dependencies()
        total_fixed += fixed_python

        # Corregir dependencias del sistema
        fixed_system = self.fix_system_dependencies()
        total_fixed += fixed_system

        # Corregir dependencias del backend
        fixed_backend = self.fix_backend_dependencies()
        total_fixed += fixed_backend

        # Corregir dependencias del frontend
        fixed_frontend = self.fix_frontend_dependencies()
        total_fixed += fixed_frontend

        # Generar reporte
        report = self.generate_dependency_report()

        print("=" * 50)
        print("📊 RESUMEN DE CORRECCIÓN DE DEPENDENCIAS")
        print("=" * 50)
        print(f"✅ Dependencias Python corregidas: {fixed_python}")
        print(f"✅ Dependencias del sistema corregidas: {fixed_system}")
        print(f"✅ Dependencias del backend corregidas: {fixed_backend}")
        print(f"✅ Dependencias del frontend corregidas: {fixed_frontend}")
        print(f"📊 Total corregidas: {total_fixed}")
        print(f"❌ Dependencias faltantes: {len(self.missing_deps)}")

        if self.missing_deps:
            print("\n⚠️ DEPENDENCIAS QUE NO SE PUDIERON INSTALAR:")
            for dep in self.missing_deps:
                print(f"   - {dep}")

        if len(self.missing_deps) == 0:
            print("\n🎉 ¡Todas las dependencias están instaladas!")
        else:
            print(
                f"\n⚠️ {len(self.missing_deps)} dependencias no se pudieron instalar automáticamente"
            )
            print("🔧 Instálalas manualmente o revisa los errores")

        return report


def main():
    fixer = DependencyFixer()
    report = fixer.run_dependency_fix()

    if report["total_missing"] == 0:
        sys.exit(0)
    else:
        sys.exit(1)


if __name__ == "__main__":
    main()
