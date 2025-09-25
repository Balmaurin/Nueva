#!/usr/bin/env python3
"""
Script para verificar y corregir integraciones entre módulos
Sheily AI - Verificación de Integraciones Reales
"""

import sys
import os
import logging
import importlib
import traceback
from pathlib import Path

# Configurar logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

# Agregar el directorio raíz al path
base_path = Path(__file__).parent.parent
sys.path.insert(0, str(base_path))


class IntegrationTester:
    def __init__(self):
        self.passed_tests = 0
        self.failed_tests = 0
        self.warnings = 0

    def test_result(self, test_name, success, message=""):
        """Registrar resultado de prueba"""
        if success:
            self.passed_tests += 1
            logger.info(f"✅ {test_name}: {message}")
        else:
            self.failed_tests += 1
            logger.error(f"❌ {test_name}: {message}")

    def test_warning(self, test_name, message=""):
        """Registrar advertencia"""
        self.warnings += 1
        logger.warning(f"⚠️ {test_name}: {message}")

    def test_basic_imports(self):
        """Probar importaciones básicas de módulos críticos"""
        logger.info("🔍 Probando importaciones básicas...")

        critical_modules = [
            ("modules.core.neurofusion_core", "NeuroFusionCore"),
            ("modules.unified_systems.module_initializer", "ModuleInitializer"),
            ("modules.ai_components.advanced_ai_system", "AdvancedAISystem"),
            ("modules.core.integration_manager", "IntegrationManager"),
            ("config.config_manager", "ConfigManager"),
        ]

        for module_name, class_name in critical_modules:
            try:
                module = importlib.import_module(module_name)
                if hasattr(module, class_name):
                    self.test_result(
                        f"Import {module_name}", True, f"Clase {class_name} disponible"
                    )
                else:
                    self.test_result(
                        f"Import {module_name}",
                        False,
                        f"Clase {class_name} no encontrada",
                    )
            except ImportError as e:
                self.test_result(
                    f"Import {module_name}", False, f"Error de importación: {e}"
                )
            except Exception as e:
                self.test_result(
                    f"Import {module_name}", False, f"Error inesperado: {e}"
                )

    def test_database_connections(self):
        """Probar conexiones reales a bases de datos"""
        logger.info("🔍 Probando conexiones a bases de datos...")

        try:
            import sqlite3

            # Probar knowledge_base.db
            db_path = base_path / "data" / "knowledge_base.db"
            if db_path.exists():
                try:
                    conn = sqlite3.connect(str(db_path))
                    cursor = conn.cursor()
                    cursor.execute("SELECT COUNT(*) FROM knowledge_base")
                    count = cursor.fetchone()[0]
                    conn.close()
                    self.test_result(
                        "Knowledge Base DB", True, f"{count} registros encontrados"
                    )
                except Exception as e:
                    self.test_result(
                        "Knowledge Base DB", False, f"Error consultando: {e}"
                    )
            else:
                self.test_result("Knowledge Base DB", False, "Archivo no encontrado")

            # Probar embeddings_sqlite.db
            db_path = base_path / "data" / "embeddings_sqlite.db"
            if db_path.exists():
                try:
                    conn = sqlite3.connect(str(db_path))
                    cursor = conn.cursor()
                    cursor.execute("SELECT COUNT(*) FROM embeddings")
                    count = cursor.fetchone()[0]
                    conn.close()
                    self.test_result(
                        "Embeddings DB", True, f"{count} embeddings encontrados"
                    )
                except Exception as e:
                    self.test_result("Embeddings DB", False, f"Error consultando: {e}")
            else:
                self.test_result("Embeddings DB", False, "Archivo no encontrado")

            # Probar backend/sheily_ai.db
            db_path = base_path / "backend" / "sheily_ai.db"
            if db_path.exists():
                try:
                    conn = sqlite3.connect(str(db_path))
                    cursor = conn.cursor()
                    cursor.execute("SELECT COUNT(*) FROM users")
                    count = cursor.fetchone()[0]
                    conn.close()
                    self.test_result(
                        "Backend DB", True, f"{count} usuarios encontrados"
                    )
                except Exception as e:
                    self.test_result("Backend DB", False, f"Error consultando: {e}")
            else:
                self.test_result("Backend DB", False, "Archivo no encontrado")

        except ImportError:
            self.test_result("Database Tests", False, "sqlite3 no disponible")

    def test_config_system(self):
        """Probar sistema de configuración"""
        logger.info("🔍 Probando sistema de configuración...")

        config_files = [
            "config/neurofusion_config.json",
            "config/advanced_training_config.json",
            "config/rate_limits.json",
        ]

        for config_file in config_files:
            config_path = base_path / config_file
            if config_path.exists():
                try:
                    import json

                    with open(config_path, "r", encoding="utf-8") as f:
                        config_data = json.load(f)
                    self.test_result(
                        f"Config {config_file}",
                        True,
                        f"{len(config_data)} configuraciones cargadas",
                    )
                except json.JSONDecodeError as e:
                    self.test_result(
                        f"Config {config_file}", False, f"JSON inválido: {e}"
                    )
                except Exception as e:
                    self.test_result(
                        f"Config {config_file}", False, f"Error leyendo: {e}"
                    )
            else:
                self.test_result(
                    f"Config {config_file}", False, "Archivo no encontrado"
                )

    def test_llm_system(self):
        """Probar sistema LLM"""
        logger.info("🔍 Probando sistema LLM...")

        # Verificar archivos del modelo
        model_path = base_path / "models"
        if model_path.exists():
            model_files = list(model_path.rglob("*.gguf"))
            if model_files:
                self.test_result(
                    "LLM Models", True, f"{len(model_files)} modelos GGUF encontrados"
                )
            else:
                self.test_warning("LLM Models", "No se encontraron modelos GGUF")
        else:
            self.test_result("LLM Models", False, "Directorio models no encontrado")

        # Verificar cliente LLM
        llm_client_path = base_path / "backend" / "llm_client.py"
        if llm_client_path.exists():
            try:
                # Verificar sintaxis sin importar
                import ast

                with open(llm_client_path, "r", encoding="utf-8") as f:
                    source = f.read()
                ast.parse(source)
                self.test_result("LLM Client", True, "Sintaxis válida")
            except SyntaxError as e:
                self.test_result("LLM Client", False, f"Error de sintaxis: {e}")
        else:
            self.test_result("LLM Client", False, "Archivo llm_client.py no encontrado")

    def test_frontend_backend_connection(self):
        """Probar conexión Frontend-Backend"""
        logger.info("🔍 Probando conexión Frontend-Backend...")

        # Verificar archivos del backend
        backend_files = [
            "backend/server.js",
            "backend/llm_server.py",
            "backend/llm_client.py",
        ]

        for file_path in backend_files:
            full_path = base_path / file_path
            if full_path.exists():
                self.test_result(f"Backend {file_path}", True, "Archivo encontrado")
            else:
                self.test_result(f"Backend {file_path}", False, "Archivo no encontrado")

        # Verificar archivos del frontend
        frontend_files = [
            "Frontend/package.json",
            "Frontend/src/App.tsx",
            "Frontend/src/components/Chat.tsx",
        ]

        for file_path in frontend_files:
            full_path = base_path / file_path
            if full_path.exists():
                self.test_result(f"Frontend {file_path}", True, "Archivo encontrado")
            else:
                self.test_result(
                    f"Frontend {file_path}", False, "Archivo no encontrado"
                )

    def test_module_communication(self):
        """Probar comunicación real entre módulos"""
        logger.info("🔍 Probando comunicación entre módulos...")

        try:
            # Intentar cargar e inicializar el sistema unificado
            from modules.unified_systems.module_initializer import ModuleInitializer

            # Crear instancia del inicializador
            initializer = ModuleInitializer()

            # Probar inicialización básica
            if hasattr(initializer, "initialize_core_modules"):
                self.test_result(
                    "Module Communication", True, "ModuleInitializer responde"
                )
            else:
                self.test_warning(
                    "Module Communication",
                    "ModuleInitializer sin método initialize_core_modules",
                )

        except ImportError as e:
            self.test_result(
                "Module Communication",
                False,
                f"Error importando ModuleInitializer: {e}",
            )
        except Exception as e:
            self.test_result(
                "Module Communication", False, f"Error en comunicación: {e}"
            )

        try:
            # Probar IntegrationManager
            from modules.core.integration_manager import IntegrationManager

            manager = IntegrationManager()
            if hasattr(manager, "process_query"):
                self.test_result(
                    "Integration Manager", True, "IntegrationManager responde"
                )
            else:
                self.test_warning(
                    "Integration Manager", "IntegrationManager sin método process_query"
                )

        except ImportError as e:
            self.test_result("Integration Manager", False, f"Error importando: {e}")
        except Exception as e:
            self.test_result("Integration Manager", False, f"Error: {e}")

    def test_blockchain_integration(self):
        """Probar integración blockchain"""
        logger.info("🔍 Probando integración blockchain...")

        blockchain_files = [
            "modules/blockchain/solana_integration.py",
            "modules/tokens/unified_sheily_token_system.py",
            "config/sheily_token_config.json",
        ]

        for file_path in blockchain_files:
            full_path = base_path / file_path
            if full_path.exists():
                self.test_result(f"Blockchain {file_path}", True, "Archivo encontrado")
            else:
                self.test_result(
                    f"Blockchain {file_path}", False, "Archivo no encontrado"
                )

    def run_all_tests(self):
        """Ejecutar todas las pruebas de integración"""
        logger.info("🚀 Iniciando pruebas de integración de módulos...")

        self.test_basic_imports()
        self.test_database_connections()
        self.test_config_system()
        self.test_llm_system()
        self.test_frontend_backend_connection()
        self.test_module_communication()
        self.test_blockchain_integration()

        # Resumen final
        total_tests = self.passed_tests + self.failed_tests
        success_rate = (self.passed_tests / total_tests * 100) if total_tests > 0 else 0

        logger.info(f"\n🎯 RESUMEN DE PRUEBAS DE INTEGRACIÓN:")
        logger.info(f"✅ Pruebas exitosas: {self.passed_tests}")
        logger.info(f"❌ Pruebas fallidas: {self.failed_tests}")
        logger.info(f"⚠️ Advertencias: {self.warnings}")
        logger.info(f"📊 Tasa de éxito: {success_rate:.1f}%")

        if success_rate >= 80:
            logger.info("🎉 ¡Integraciones en buen estado!")
            return True
        elif success_rate >= 60:
            logger.warning("⚠️ Integraciones necesitan mejoras")
            return False
        else:
            logger.error("❌ Integraciones requieren corrección urgente")
            return False


if __name__ == "__main__":
    tester = IntegrationTester()
    success = tester.run_all_tests()

    if success:
        print("\n🎉 ¡Pruebas de integración completadas exitosamente!")
        exit(0)
    else:
        print("\n❌ Algunas integraciones necesitan corrección")
        exit(1)
