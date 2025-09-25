#!/usr/bin/env python3
"""
Script de Limpieza del Núcleo Central
=====================================

Script para mantener el directorio nucleo_central optimizado:
- Eliminar archivos de caché
- Verificar integridad de configuraciones
- Validar importaciones
"""

import os
import sys
import shutil
import logging
from pathlib import Path
from typing import List, Dict, Any

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class NucleoCentralCleaner:
    """Limpiador del núcleo central"""

    def __init__(self, base_path: str = "modules/nucleo_central"):
        self.base_path = Path(base_path)
        self.cleaned_files = []
        self.errors = []

    def cleanup_cache_files(self) -> bool:
        """Eliminar archivos de caché"""
        logger.info("🧹 Limpiando archivos de caché...")

        cache_patterns = [
            "__pycache__",
            "*.pyc",
            "*.pyo",
            "*.pyd",
            ".pytest_cache",
            ".coverage",
        ]

        for pattern in cache_patterns:
            if pattern == "__pycache__":
                # Eliminar directorios __pycache__
                for cache_dir in self.base_path.rglob(pattern):
                    try:
                        shutil.rmtree(cache_dir)
                        self.cleaned_files.append(str(cache_dir))
                        logger.info(f"✅ Eliminado: {cache_dir}")
                    except Exception as e:
                        self.errors.append(f"Error eliminando {cache_dir}: {e}")
            else:
                # Eliminar archivos de caché
                for cache_file in self.base_path.rglob(pattern):
                    try:
                        cache_file.unlink()
                        self.cleaned_files.append(str(cache_file))
                        logger.info(f"✅ Eliminado: {cache_file}")
                    except Exception as e:
                        self.errors.append(f"Error eliminando {cache_file}: {e}")

        return len(self.errors) == 0

    def verify_configurations(self) -> Dict[str, bool]:
        """Verificar integridad de configuraciones"""
        logger.info("🔍 Verificando configuraciones...")

        results = {}

        # Verificar archivos de configuración centralizados (desde directorio raíz)
        config_files = [
            ("config/rate_limits.json", "Rate Limits"),
            ("config/advanced_training_config.json", "Advanced Training"),
            ("config/config/neurofusion_config.json", "NeuroFusion Config"),
        ]

        for config_path, name in config_files:
            full_path = Path(config_path)
            if full_path.exists():
                results[name] = True
                logger.info(f"✅ {name}: OK")
            else:
                results[name] = False
                logger.warning(f"⚠️ {name}: No encontrado en {config_path}")

        return results

    def validate_imports(self) -> Dict[str, bool]:
        """Validar importaciones del núcleo central"""
        logger.info("🔍 Validando importaciones...")

        results = {}

        # Verificar módulos que se importan
        modules_to_check = [
            ("modules.core.neurofusion_core", "NeuroFusionCore"),
            ("modules.unified_systems.module_initializer", "ModuleInitializer"),
            ("modules.unified_systems.module_integrator", "ModuleIntegrator"),
            ("modules.unified_systems.module_plugin_system", "ModulePluginManager"),
            ("modules.unified_systems.module_monitor", "ModuleMonitor"),
        ]

        for module_path, module_name in modules_to_check:
            try:
                # Intentar importar el módulo
                __import__(module_path, fromlist=[module_name])
                results[module_name] = True
                logger.info(f"✅ {module_name}: Importable")
            except ImportError as e:
                results[module_name] = False
                logger.warning(f"⚠️ {module_name}: Error de importación - {e}")
            except Exception as e:
                results[module_name] = False
                logger.error(f"❌ {module_name}: Error inesperado - {e}")

        return results

    def generate_report(self) -> Dict[str, Any]:
        """Generar reporte de limpieza"""
        logger.info("📊 Generando reporte...")

        cache_clean = self.cleanup_cache_files()
        config_status = self.verify_configurations()
        import_status = self.validate_imports()

        report = {
            "timestamp": str(Path().cwd()),
            "base_path": str(self.base_path),
            "cache_cleanup": {
                "success": cache_clean,
                "files_cleaned": len(self.cleaned_files),
                "errors": len(self.errors),
            },
            "configurations": config_status,
            "imports": import_status,
            "summary": {
                "total_configs_ok": sum(config_status.values()),
                "total_imports_ok": sum(import_status.values()),
                "overall_status": (
                    "OK" if cache_clean and all(config_status.values()) else "WARNING"
                ),
            },
        }

        return report

    def print_report(self, report: Dict[str, Any]):
        """Imprimir reporte de forma legible"""
        print("\n" + "=" * 60)
        print("📋 REPORTE DE LIMPIEZA - NÚCLEO CENTRAL")
        print("=" * 60)

        print(f"\n📍 Directorio: {report['base_path']}")
        print(f"⏰ Timestamp: {report['timestamp']}")

        # Limpieza de caché
        cache_info = report["cache_cleanup"]
        print(f"\n🧹 Limpieza de caché:")
        print(f"   ✅ Éxito: {cache_info['success']}")
        print(f"   📁 Archivos eliminados: {cache_info['files_cleaned']}")
        print(f"   ❌ Errores: {cache_info['errors']}")

        # Configuraciones
        print(f"\n⚙️ Configuraciones:")
        for name, status in report["configurations"].items():
            status_icon = "✅" if status else "❌"
            print(f"   {status_icon} {name}")

        # Importaciones
        print(f"\n📦 Importaciones:")
        for name, status in report["imports"].items():
            status_icon = "✅" if status else "❌"
            print(f"   {status_icon} {name}")

        # Resumen
        summary = report["summary"]
        print(f"\n📊 Resumen:")
        print(
            f"   Configuraciones OK: {summary['total_configs_ok']}/{len(report['configurations'])}"
        )
        print(
            f"   Importaciones OK: {summary['total_imports_ok']}/{len(report['imports'])}"
        )
        print(f"   Estado general: {summary['overall_status']}")

        print("\n" + "=" * 60)


def main():
    """Función principal"""
    cleaner = NucleoCentralCleaner()
    report = cleaner.generate_report()
    cleaner.print_report(report)

    # Retornar código de salida basado en el estado
    if report["summary"]["overall_status"] == "OK":
        return 0
    else:
        return 1


if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)
