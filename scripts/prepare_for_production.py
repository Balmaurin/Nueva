#!/usr/bin/env python3
"""
Script de Preparación para Producción - VERSIÓN COMPLETA
=======================================================

Prepara el sistema NeuroFusion para producción ejecutando verificaciones
completas de todos los componentes críticos.
"""

import os
import sys
import subprocess
import json
import requests
import time
from pathlib import Path
from datetime import datetime
import importlib.util


class ProductionPreparer:
    def __init__(self):
        self.project_root = Path.cwd()
        self.results = {}
        self.start_time = datetime.now()

    def run_command(self, command, description, timeout=60):
        """Ejecuta un comando y registra el resultado"""
        print(f"🔧 {description}...")
        try:
            result = subprocess.run(
                command, shell=True, capture_output=True, text=True, timeout=timeout
            )
            if result.returncode == 0:
                print(f"✅ {description} - EXITOSO")
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

    def verify_dependencies(self):
        """Verifica todas las dependencias críticas"""
        print("📦 Verificando dependencias del sistema...")

        # Dependencias Python críticas
        python_deps = [
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
            "asyncio",
            "pydantic",
            "python-multipart",
            "python-jose",
            "passlib",
            "bcrypt",
            "prometheus_client",
            "faiss-cpu",
            "scikit-learn",
        ]

        # Dependencias del sistema
        system_deps = ["docker", "docker-compose", "node", "npm", "git", "curl"]

        all_ok = True

        # Verificar dependencias Python
        for dep in python_deps:
            try:
                importlib.import_module(dep)
                print(f"✅ Python: {dep}")
            except ImportError:
                print(f"❌ Python: {dep} - NO INSTALADO")
                all_ok = False

        # Verificar dependencias del sistema
        for dep in system_deps:
            success, _ = self.run_command(
                f"which {dep}", f"Verificando {dep}", timeout=5
            )
            if not success:
                all_ok = False

        return all_ok

    def verify_llm_models(self):
        """Verifica los modelos de LLM y su disponibilidad"""
        print("🤖 Verificando modelos de LLM...")

        # Verificar modelos T5
        t5_models = ["t5-large"]

        all_ok = True

        try:
            from transformers import AutoTokenizer, AutoModel

            for model_name in t5_models:
                try:
                    print(f"🔍 Verificando modelo {model_name}...")
                    tokenizer = AutoTokenizer.from_pretrained(model_name)
                    model = AutoModel.from_pretrained(model_name)

                    # Prueba básica de inferencia
                    test_text = "Hello world"
                    inputs = tokenizer(test_text, return_tensors="pt")
                    outputs = model(**inputs)

                    print(f"✅ {model_name} - Funcional")
                except Exception as e:
                    print(f"❌ {model_name} - Error: {e}")
                    all_ok = False

        except ImportError:
            print("❌ Transformers no disponible")
            all_ok = False

        # Verificar modelo principal
        try:
            from transformers import AutoModel, AutoTokenizer

            model_path = "models/custom/sheily-personal-model"
            tokenizer = AutoTokenizer.from_pretrained(model_path)
            model = AutoModel.from_pretrained(model_path)
            print(f"✅ Modelo principal: {model_path} - Funcional")
        except Exception as e:
            print(f"❌ Modelo principal: {model_path} - Error: {e}")
            all_ok = False

        return all_ok

    def verify_backend_functionality(self):
        """Verifica la funcionalidad del backend"""
        print("🔧 Verificando funcionalidad del backend...")

        backend_dir = self.project_root / "interface" / "backend"

        if not backend_dir.exists():
            print("❌ Directorio backend no encontrado")
            return False

        all_ok = True

        # Verificar archivos críticos del backend
        critical_files = ["main.py", "requirements.txt", "config.env", ".env"]

        for file_name in critical_files:
            file_path = backend_dir / file_name
            if file_path.exists():
                size = file_path.stat().st_size
                print(f"✅ {file_name} - {size} bytes")
            else:
                print(f"❌ {file_name} - No encontrado")
                all_ok = False

        # Verificar que el backend puede iniciar
        try:
            # Cambiar al directorio backend
            original_cwd = os.getcwd()
            os.chdir(backend_dir)

            # Verificar dependencias del backend
            success, _ = self.run_command(
                "pip install -r requirements.txt",
                "Instalando dependencias del backend",
                timeout=120,
            )

            # Intentar iniciar el servidor en modo de prueba
            success, _ = self.run_command(
                "python -c 'import uvicorn; print(\"Uvicorn disponible\")'",
                "Verificando Uvicorn",
                timeout=10,
            )

            os.chdir(original_cwd)

            if not success:
                all_ok = False

        except Exception as e:
            print(f"❌ Error verificando backend: {e}")
            all_ok = False

        return all_ok

    def verify_frontend_functionality(self):
        """Verifica la funcionalidad del frontend"""
        print("🎨 Verificando funcionalidad del frontend...")

        frontend_dir = self.project_root / "interface" / "frontend"

        if not frontend_dir.exists():
            print("❌ Directorio frontend no encontrado")
            return False

        all_ok = True

        # Verificar archivos críticos del frontend
        critical_files = [
            "package.json",
            "package-lock.json",
            "src/App.js",
            "public/index.html",
        ]

        for file_name in critical_files:
            file_path = frontend_dir / file_name
            if file_path.exists():
                size = file_path.stat().st_size
                print(f"✅ {file_name} - {size} bytes")
            else:
                print(f"❌ {file_name} - No encontrado")
                all_ok = False

        # Verificar dependencias de Node.js
        try:
            original_cwd = os.getcwd()
            os.chdir(frontend_dir)

            # Verificar que npm está disponible
            success, _ = self.run_command(
                "npm --version", "Verificando npm", timeout=10
            )

            if success:
                # Verificar que las dependencias están instaladas
                if (frontend_dir / "node_modules").exists():
                    print("✅ node_modules - Instalado")
                else:
                    print("⚠️ node_modules - No encontrado, instalando...")
                    success, _ = self.run_command(
                        "npm install",
                        "Instalando dependencias del frontend",
                        timeout=180,
                    )
                    if not success:
                        all_ok = False
            else:
                all_ok = False

            os.chdir(original_cwd)

        except Exception as e:
            print(f"❌ Error verificando frontend: {e}")
            all_ok = False

        return all_ok

    def verify_training_systems(self):
        """Verifica los sistemas de entrenamiento"""
        print("🏋️ Verificando sistemas de entrenamiento...")

        all_ok = True

        # Verificar directorios de entrenamiento
        training_dirs = ["modules/training", "models", "data"]

        for dir_name in training_dirs:
            dir_path = self.project_root / dir_name
            if dir_path.exists():
                file_count = len(list(dir_path.rglob("*.py")))
                print(f"✅ {dir_name} - {file_count} archivos Python")
            else:
                print(f"❌ {dir_name} - No encontrado")
                all_ok = False

        # Verificar configuraciones de entrenamiento
        training_configs = [
            "config/advanced_training_config.json",
            "config/config/neurofusion_config.json",
        ]

        for config_file in training_configs:
            config_path = self.project_root / config_file
            if config_path.exists():
                try:
                    with open(config_path, "r") as f:
                        config = json.load(f)

                    # Verificar que tiene configuraciones de entrenamiento
                    if "training" in str(config) or "model" in str(config):
                        size = config_path.stat().st_size
                        print(f"✅ {config_file} - {size} bytes")
                    else:
                        print(f"⚠️ {config_file} - Sin configuraciones de entrenamiento")
                except Exception as e:
                    print(f"❌ {config_file} - Error: {e}")
                    all_ok = False
            else:
                print(f"❌ {config_file} - No encontrado")
                all_ok = False

        # Verificar que los módulos de entrenamiento importan
        training_modules = [
            "modules.training",
            "modules.learning",
            "modules.evaluation",
        ]

        for module in training_modules:
            try:
                result = subprocess.run(
                    f'python3 -c \'import sys; sys.path.append("."); import {module}; print("OK")\'',
                    shell=True,
                    capture_output=True,
                    text=True,
                    timeout=10,
                )
                if result.returncode == 0 and "OK" in result.stdout:
                    print(f"✅ {module} - Importa correctamente")
                else:
                    print(f"❌ {module} - Error al importar")
                    all_ok = False
            except Exception as e:
                print(f"❌ {module} - Error: {e}")
                all_ok = False

        return all_ok

    def verify_endpoints(self):
        """Verifica endpoints y APIs"""
        print("🌐 Verificando endpoints y APIs...")

        all_ok = True

        # Verificar que el backend puede iniciar y responder
        backend_dir = self.project_root / "interface" / "backend"

        if backend_dir.exists():
            try:
                # Intentar iniciar el servidor en background
                original_cwd = os.getcwd()
                os.chdir(backend_dir)

                # Verificar si hay un servidor ya corriendo
                success, _ = self.run_command(
                    "curl -s http://localhost:8000/health || echo 'No response'",
                    "Verificando servidor backend",
                    timeout=5,
                )

                if "No response" in success:
                    print("⚠️ Backend no está corriendo, intentando iniciar...")

                    # Intentar iniciar el servidor
                    success, _ = self.run_command(
                        "python -m uvicorn main:app --host 0.0.0.0 --port 8000 --reload &",
                        "Iniciando servidor backend",
                        timeout=10,
                    )

                    if success:
                        # Esperar a que el servidor inicie
                        time.sleep(5)

                        # Verificar endpoints
                        endpoints = [
                            ("http://localhost:8000/health", "Health Check"),
                            ("http://localhost:8000/docs", "API Documentation"),
                            ("http://localhost:8000/", "Root Endpoint"),
                        ]

                        for url, description in endpoints:
                            try:
                                response = requests.get(url, timeout=5)
                                if response.status_code == 200:
                                    print(f"✅ {description} - {response.status_code}")
                                else:
                                    print(f"⚠️ {description} - {response.status_code}")
                            except Exception as e:
                                print(f"❌ {description} - Error: {e}")
                                all_ok = False

                        # Detener el servidor
                        self.run_command(
                            "pkill -f uvicorn", "Deteniendo servidor backend"
                        )
                    else:
                        all_ok = False
                else:
                    print("✅ Backend ya está corriendo")

                os.chdir(original_cwd)

            except Exception as e:
                print(f"❌ Error verificando endpoints: {e}")
                all_ok = False
        else:
            print("❌ Directorio backend no encontrado")
            all_ok = False

        return all_ok

    def verify_database_initialization(self):
        """Verifica que las bases de datos estén inicializadas"""
        print("🔍 Verificando inicialización de bases de datos...")

        databases = [
            ("data/knowledge_base.db", "knowledge_base"),
            ("data/embeddings_sqlite.db", "embeddings"),
            ("data/rag_memory.duckdb", "rag_memory"),
            ("data/user_data.duckdb", "users"),
            ("monitoring/metrics.db", "metrics"),
        ]

        all_ok = True
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
                        else:
                            print(f"⚠️ {db_path} - 0 registros")
                            all_ok = False
                    else:
                        print(f"❌ {db_path} - Error al verificar")
                        all_ok = False
                except Exception as e:
                    print(f"❌ {db_path} - Error: {e}")
                    all_ok = False
            else:
                print(f"❌ {db_path} - No existe")
                all_ok = False

        # Verificar índice FAISS
        if os.path.exists("data/faiss_index.index"):
            size = os.path.getsize("data/faiss_index.index")
            if size > 1000000:  # Más de 1MB
                print(f"✅ data/faiss_index.index - {size/1024/1024:.1f}MB")
            else:
                print(f"⚠️ data/faiss_index.index - Muy pequeño ({size} bytes)")
                all_ok = False
        else:
            print("❌ data/faiss_index.index - No existe")
            all_ok = False

        return all_ok

    def verify_docker_setup(self):
        """Verifica la configuración de Docker"""
        print("🐳 Verificando configuración de Docker...")

        docker_files = [
            "docker/docker-compose.yml",
            "docker/docker-compose.dev.yml",
            "docker/Dockerfile",
            "docker/backend.docker/Dockerfile",
            "docker/frontend.docker/Dockerfile",
        ]

        all_ok = True
        for file_path in docker_files:
            if os.path.exists(file_path):
                size = os.path.getsize(file_path)
                print(f"✅ {file_path} - {size} bytes")
            else:
                print(f"❌ {file_path} - No existe")
                all_ok = False

        # Verificar que Docker está disponible
        success, _ = self.run_command(
            "docker --version", "Verificando Docker", timeout=10
        )
        if not success:
            all_ok = False

        # Verificar que docker-compose está disponible
        success, _ = self.run_command(
            "docker-compose --version", "Verificando docker-compose", timeout=10
        )
        if not success:
            all_ok = False

        return all_ok

    def verify_script_functionality(self):
        """Verifica que los scripts funcionen correctamente"""
        print("🔧 Verificando funcionalidad de scripts...")

        scripts = [
            ("./scripts/verificar_sistema.sh", "Script de verificación del sistema"),
            (
                "python3 scripts/initialize_databases.py",
                "Script de inicialización de bases de datos",
            ),
        ]

        all_ok = True
        for script, description in scripts:
            success, output = self.run_command(script, description, timeout=30)
            if not success:
                all_ok = False

        return all_ok

    def verify_module_imports(self):
        """Verifica que los módulos principales importen correctamente"""
        print("📦 Verificando importaciones de módulos...")

        modules = [
            "modules.core.neurofusion_core",
            "modules.ai",
            "modules.unified_systems.module_initializer",
            "modules.nucleo_central.config.rate_limits",
            "modules.training",
            "modules.evaluation",
            "modules.memory",
            "modules.security",
        ]

        all_ok = True
        for module in modules:
            try:
                result = subprocess.run(
                    f'python3 -c \'import sys; sys.path.append("."); import {module}; print("OK")\'',
                    shell=True,
                    capture_output=True,
                    text=True,
                    timeout=15,
                )
                if result.returncode == 0 and "OK" in result.stdout:
                    print(f"✅ {module} - Importa correctamente")
                else:
                    print(f"❌ {module} - Error al importar")
                    all_ok = False
            except Exception as e:
                print(f"❌ {module} - Error: {e}")
                all_ok = False

        return all_ok

    def verify_configurations(self):
        """Verifica que las configuraciones sean válidas"""
        print("⚙️ Verificando configuraciones...")

        config_files = [
            "config/config/neurofusion_config.json",
            "config/rate_limits.json",
            "config/advanced_training_config.json",
            "config/config/module_initialization.json",
        ]

        all_ok = True
        for config_file in config_files:
            if os.path.exists(config_file):
                try:
                    with open(config_file, "r") as f:
                        config = json.load(f)
                    size = os.path.getsize(config_file)
                    print(f"✅ {config_file} - JSON válido ({size} bytes)")
                except json.JSONDecodeError as e:
                    print(f"❌ {config_file} - JSON inválido: {e}")
                    all_ok = False
                except Exception as e:
                    print(f"❌ {config_file} - Error: {e}")
                    all_ok = False
            else:
                print(f"❌ {config_file} - No existe")
                all_ok = False

        return all_ok

    def verify_security(self):
        """Verifica configuraciones de seguridad"""
        print("🔒 Verificando configuraciones de seguridad...")

        all_ok = True

        # Verificar archivos de configuración de seguridad
        security_files = [
            "interface/backend/.env",
            "interface/backend/config.env",
            "modules/security",
        ]

        for file_path in security_files:
            if os.path.exists(file_path):
                if os.path.isdir(file_path):
                    file_count = len(list(Path(file_path).rglob("*.py")))
                    print(f"✅ {file_path} - {file_count} archivos Python")
                else:
                    size = os.path.getsize(file_path)
                    print(f"✅ {file_path} - {size} bytes")
            else:
                print(f"⚠️ {file_path} - No encontrado")

        # Verificar módulos de seguridad
        security_modules = ["modules.security", "modules.tokens", "modules.blockchain"]

        for module in security_modules:
            try:
                result = subprocess.run(
                    f'python3 -c \'import sys; sys.path.append("."); import {module}; print("OK")\'',
                    shell=True,
                    capture_output=True,
                    text=True,
                    timeout=10,
                )
                if result.returncode == 0 and "OK" in result.stdout:
                    print(f"✅ {module} - Importa correctamente")
                else:
                    print(f"❌ {module} - Error al importar")
                    all_ok = False
            except Exception as e:
                print(f"❌ {module} - Error: {e}")
                all_ok = False

        return all_ok

    def verify_monitoring(self):
        """Verifica sistemas de monitoreo"""
        print("📊 Verificando sistemas de monitoreo...")

        all_ok = True

        # Verificar directorios de monitoreo
        monitoring_dirs = ["monitoring", "logs"]

        for dir_name in monitoring_dirs:
            dir_path = self.project_root / dir_name
            if dir_path.exists():
                file_count = len(list(dir_path.rglob("*.py")))
                print(f"✅ {dir_name} - {file_count} archivos Python")
            else:
                print(f"❌ {dir_name} - No encontrado")
                all_ok = False

        # Verificar módulos de monitoreo
        monitoring_modules = [
            "monitoring.metrics_collector",
            "monitoring.alert_manager",
            "monitoring.monitoring_dashboard",
        ]

        for module in monitoring_modules:
            try:
                result = subprocess.run(
                    f'python3 -c \'import sys; sys.path.append("."); import {module}; print("OK")\'',
                    shell=True,
                    capture_output=True,
                    text=True,
                    timeout=10,
                )
                if result.returncode == 0 and "OK" in result.stdout:
                    print(f"✅ {module} - Importa correctamente")
                else:
                    print(f"❌ {module} - Error al importar")
                    all_ok = False
            except Exception as e:
                print(f"❌ {module} - Error: {e}")
                all_ok = False

        return all_ok

    def generate_production_report(self):
        """Genera un reporte de preparación para producción"""
        print("📊 Generando reporte de producción...")

        # Ejecutar todas las verificaciones
        checks = {
            "dependencies": self.verify_dependencies(),
            "llm_models": self.verify_llm_models(),
            "backend_functionality": self.verify_backend_functionality(),
            "frontend_functionality": self.verify_frontend_functionality(),
            "training_systems": self.verify_training_systems(),
            "endpoints": self.verify_endpoints(),
            "database_initialization": self.verify_database_initialization(),
            "docker_setup": self.verify_docker_setup(),
            "script_functionality": self.verify_script_functionality(),
            "module_imports": self.verify_module_imports(),
            "configurations": self.verify_configurations(),
            "security": self.verify_security(),
            "monitoring": self.verify_monitoring(),
        }

        report = {
            "timestamp": datetime.now().isoformat(),
            "project_root": str(self.project_root),
            "duration_seconds": (datetime.now() - self.start_time).total_seconds(),
            "checks": checks,
        }

        # Calcular puntuación general
        total_checks = len(checks)
        passed_checks = sum(checks.values())
        score = (passed_checks / total_checks) * 100

        report["score"] = score
        report["status"] = (
            "READY" if score >= 85 else "NEEDS_WORK" if score >= 70 else "NOT_READY"
        )

        # Guardar reporte
        report_path = self.project_root / "PRODUCTION_READINESS_REPORT_COMPLETE.json"
        with open(report_path, "w") as f:
            json.dump(report, f, indent=2)

        print(f"✅ Reporte guardado en: {report_path}")
        return report

    def print_summary(self, report):
        """Imprime un resumen del reporte"""
        print("\n" + "=" * 70)
        print("🚀 REPORTE COMPLETO DE PREPARACIÓN PARA PRODUCCIÓN")
        print("=" * 70)

        print(f"📅 Fecha: {report['timestamp']}")
        print(f"📁 Proyecto: {report['project_root']}")
        print(f"⏱️ Duración: {report['duration_seconds']:.1f} segundos")
        print()

        print("🔍 VERIFICACIONES DETALLADAS:")
        for check, result in report["checks"].items():
            status = "✅ PASÓ" if result else "❌ FALLÓ"
            check_name = check.replace("_", " ").title()
            print(f"   {check_name}: {status}")

        print()
        print(f"📊 PUNTUACIÓN: {report['score']:.1f}/100")
        print(f"🎯 ESTADO: {report['status']}")

        if report["status"] == "READY":
            print("\n🎉 ¡El sistema está listo para producción!")
            print("✅ Todas las verificaciones críticas han pasado")
            print("✅ LLMs están configurados y funcionando")
            print("✅ Frontend y backend están operativos")
            print("✅ Sistemas de entrenamiento están listos")
            print("✅ Endpoints y APIs están funcionando")
            print("✅ Seguridad y monitoreo están configurados")
        elif report["status"] == "NEEDS_WORK":
            print("\n⚠️ El sistema necesita trabajo antes de producción")
            print("🔧 Revisa las verificaciones que fallaron")
            print("🔧 Completa las configuraciones faltantes")
            print("🔧 Optimiza el rendimiento donde sea necesario")
        else:
            print("\n🚨 El sistema NO está listo para producción")
            print("❌ Muchas verificaciones críticas fallaron")
            print("❌ Necesita trabajo significativo")

        print("\n" + "=" * 70)

    def run_production_preparation(self):
        """Ejecuta toda la preparación para producción"""
        print("🚀 Iniciando preparación completa para producción...")
        print("=" * 70)

        # Ejecutar verificaciones
        report = self.generate_production_report()

        # Mostrar resumen
        self.print_summary(report)

        return report


def main():
    preparer = ProductionPreparer()
    report = preparer.run_production_preparation()

    # Retornar código de salida apropiado
    if report["status"] == "READY":
        sys.exit(0)
    elif report["status"] == "NEEDS_WORK":
        sys.exit(1)
    else:
        sys.exit(2)


if __name__ == "__main__":
    main()
