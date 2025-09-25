"""
Script de Inicialización de Módulos para Shaili AI
=================================================

Este script inicializa y valida todos los módulos del sistema,
asegurando que estén disponibles para el LLM.
"""

import asyncio
import logging
import json
import sys
from pathlib import Path
from typing import Dict, Any, List
from datetime import datetime

# Configurar logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

# Importar el sistema de módulos
try:
    from . import UnifiedModuleSystem, initialize_modules, get_module, list_modules
    from .module_router import (
        LLMModuleInterface,
        call_module,
        get_modules,
        get_module_docs,
    )
except ImportError as e:
    logger.error(f"Error importando módulos: {e}")
    sys.exit(1)


class ModuleInitializer:
    """Inicializador y validador de módulos"""

    def __init__(self):
        self.system = UnifiedModuleSystem()
        self.llm_interface = LLMModuleInterface()
        self.initialization_report = {
            "timestamp": datetime.now().isoformat(),
            "total_modules": 0,
            "successful_modules": 0,
            "failed_modules": 0,
            "module_details": {},
            "categories": {},
            "errors": [],
        }

    async def initialize_all_modules(self) -> Dict[str, Any]:
        """Inicializar todos los módulos del sistema"""
        logger.info("🚀 Iniciando inicialización completa del sistema de módulos...")

        start_time = datetime.now()

        try:
            # Inicializar el sistema principal
            await self.system.initialize()

            # Inicializar la interfaz del LLM
            await self.llm_interface.initialize()

            # Generar reporte de inicialización
            await self._generate_initialization_report()

            # Validar módulos críticos
            await self._validate_critical_modules()

            # Probar funcionalidad básica
            await self._test_basic_functionality()

            end_time = datetime.now()
            initialization_time = (end_time - start_time).total_seconds()

            self.initialization_report["initialization_time"] = initialization_time
            self.initialization_report["status"] = "completed"

            logger.info(
                f"✅ Inicialización completada en {initialization_time:.2f} segundos"
            )
            logger.info(
                f"📊 Módulos cargados: {self.initialization_report['successful_modules']}/{self.initialization_report['total_modules']}"
            )

            return self.initialization_report

        except Exception as e:
            logger.error(f"❌ Error durante la inicialización: {e}")
            self.initialization_report["status"] = "failed"
            self.initialization_report["errors"].append(str(e))
            return self.initialization_report

    async def _generate_initialization_report(self):
        """Generar reporte detallado de inicialización"""
        logger.info("📋 Generando reporte de inicialización...")

        # Obtener información de todos los módulos
        all_modules = self.system.registry.modules
        categories = self.system.registry.categories

        self.initialization_report["total_modules"] = len(all_modules)
        self.initialization_report["categories"] = categories

        for module_name, module_info in all_modules.items():
            try:
                # Verificar que el módulo se puede instanciar
                module_instance = self.system.get_module(module_name)

                if module_instance:
                    self.initialization_report["successful_modules"] += 1
                    status = "active"
                else:
                    self.initialization_report["failed_modules"] += 1
                    status = "failed"

                self.initialization_report["module_details"][module_name] = {
                    "category": module_info.category,
                    "description": module_info.description,
                    "class": module_info.class_name,
                    "status": status,
                    "dependencies": module_info.dependencies,
                    "is_async": module_info.is_async,
                }

            except Exception as e:
                self.initialization_report["failed_modules"] += 1
                self.initialization_report["module_details"][module_name] = {
                    "category": module_info.category,
                    "description": module_info.description,
                    "class": module_info.class_name,
                    "status": "error",
                    "error": str(e),
                }
                self.initialization_report["errors"].append(
                    f"Error en {module_name}: {e}"
                )

    async def _validate_critical_modules(self):
        """Validar módulos críticos del sistema"""
        logger.info("🔍 Validando módulos críticos...")

        critical_modules = [
            "text_processor",
            "semantic_analyzer",
            "llm_manager",
            "response_generator",
            "rag_retriever",
            "data_management",
        ]

        for module_name in critical_modules:
            try:
                module_info = self.system.get_module_info(module_name)
                if module_info and module_info["status"] == "active":
                    logger.info(f"✅ Módulo crítico '{module_name}' validado")
                else:
                    logger.warning(f"⚠️ Módulo crítico '{module_name}' no disponible")
                    self.initialization_report["errors"].append(
                        f"Módulo crítico '{module_name}' no disponible"
                    )
            except Exception as e:
                logger.error(f"❌ Error validando módulo crítico '{module_name}': {e}")
                self.initialization_report["errors"].append(
                    f"Error validando '{module_name}': {e}"
                )

    async def _test_basic_functionality(self):
        """Probar funcionalidad básica de los módulos"""
        logger.info("🧪 Probando funcionalidad básica...")

        # Probar procesamiento de texto
        try:
            result = await call_module(
                "text_processor", "clean_text", text="  Hola mundo!  "
            )
            if result["success"]:
                logger.info("✅ Procesamiento de texto funcionando")
            else:
                logger.warning(f"⚠️ Error en procesamiento de texto: {result['error']}")
        except Exception as e:
            logger.warning(f"⚠️ No se pudo probar procesamiento de texto: {e}")

        # Probar análisis semántico
        try:
            result = await call_module(
                "semantic_analyzer",
                "calculate_similarity",
                text1="Hola mundo",
                text2="Hello world",
            )
            if result["success"]:
                logger.info("✅ Análisis semántico funcionando")
            else:
                logger.warning(f"⚠️ Error en análisis semántico: {result['error']}")
        except Exception as e:
            logger.warning(f"⚠️ No se pudo probar análisis semántico: {e}")

    def save_report(self, output_path: str = "module_initialization_report.json"):
        """Guardar reporte de inicialización"""
        try:
            with open(output_path, "w", encoding="utf-8") as f:
                json.dump(
                    self.initialization_report,
                    f,
                    indent=2,
                    default=str,
                    ensure_ascii=False,
                )
            logger.info(f"📄 Reporte guardado en: {output_path}")
        except Exception as e:
            logger.error(f"❌ Error guardando reporte: {e}")

    def print_summary(self):
        """Imprimir resumen de inicialización"""
        report = self.initialization_report

        print("\n" + "=" * 60)
        print("📊 RESUMEN DE INICIALIZACIÓN DE MÓDULOS")
        print("=" * 60)
        print(f"🕒 Timestamp: {report['timestamp']}")
        print(f"📦 Total de módulos: {report['total_modules']}")
        print(f"✅ Módulos exitosos: {report['successful_modules']}")
        print(f"❌ Módulos fallidos: {report['failed_modules']}")
        print(
            f"⏱️ Tiempo de inicialización: {report.get('initialization_time', 'N/A')} segundos"
        )

        if report["categories"]:
            print(f"\n📂 Categorías disponibles ({len(report['categories'])}):")
            for category, modules in report["categories"].items():
                print(f"  • {category}: {len(modules)} módulos")

        if report["errors"]:
            print(f"\n❌ Errores encontrados ({len(report['errors'])}):")
            for error in report["errors"][:5]:  # Mostrar solo los primeros 5
                print(f"  • {error}")
            if len(report["errors"]) > 5:
                print(f"  ... y {len(report['errors']) - 5} errores más")

        print("=" * 60)

    def get_module_status(self, module_name: str) -> Dict[str, Any]:
        """Obtener estado de un módulo específico"""
        return self.initialization_report["module_details"].get(module_name, {})

    def get_category_modules(self, category: str) -> List[Dict[str, Any]]:
        """Obtener módulos de una categoría específica"""
        modules = []
        for module_name, details in self.initialization_report[
            "module_details"
        ].items():
            if details.get("category") == category:
                modules.append({"name": module_name, **details})
        return modules


async def main():
    """Función principal de inicialización"""
    print("🚀 Inicializando Sistema de Módulos Shaili AI")
    print("=" * 50)

    # Crear inicializador
    initializer = ModuleInitializer()

    # Inicializar todos los módulos
    report = await initializer.initialize_all_modules()

    # Imprimir resumen
    initializer.print_summary()

    # Guardar reporte
    initializer.save_report()

    # Verificar si la inicialización fue exitosa
    if report["status"] == "completed" and report["failed_modules"] == 0:
        print("\n🎉 ¡Inicialización completada exitosamente!")
        return True
    elif report["status"] == "completed":
        print(
            f"\n⚠️ Inicialización completada con {report['failed_modules']} módulos fallidos"
        )
        return False
    else:
        print("\n❌ La inicialización falló")
        return False


def quick_status():
    """Función rápida para verificar el estado del sistema"""
    try:
        # Verificar si el sistema está disponible
        modules = get_modules()
        total_modules = sum(len(module_list) for module_list in modules.values())

        print(f"📦 Sistema de módulos disponible")
        print(f"📊 Total de módulos: {total_modules}")
        print(f"📂 Categorías: {list(modules.keys())}")

        return True
    except Exception as e:
        print(f"❌ Sistema de módulos no disponible: {e}")
        return False


if __name__ == "__main__":
    # Ejecutar inicialización completa
    success = asyncio.run(main())

    if success:
        print("\n✅ El sistema está listo para usar")
        sys.exit(0)
    else:
        print("\n❌ El sistema tiene problemas")
        sys.exit(1)
