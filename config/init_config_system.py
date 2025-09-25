#!/usr/bin/env python3
"""
Script de Inicialización del Sistema de Configuración NeuroFusion
Configura y verifica todo el sistema de configuración del proyecto
"""

import json
import yaml
import logging
import sys
import os
from pathlib import Path
from typing import Dict, Any, List, Tuple
import subprocess
import shutil
from datetime import datetime

# Configuración de logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


class ConfigSystemInitializer:
    """Inicializador del sistema de configuración"""

    def __init__(self, config_dir: str = "config"):
        self.config_dir = Path(config_dir)
        self.project_root = Path.cwd()
        self.initialization_results = {
            "success": True,
            "errors": [],
            "warnings": [],
            "created_files": [],
            "validated_configs": [],
            "backup_created": False,
        }

    def initialize_config_system(self) -> Dict[str, Any]:
        """Inicializa todo el sistema de configuración"""
        logger.info("🚀 Iniciando sistema de configuración NeuroFusion...")

        try:
            # 1. Verificar estructura de directorios
            self._verify_directory_structure()

            # 2. Crear backup de configuraciones existentes
            self._create_backup()

            # 3. Validar configuraciones existentes
            self._validate_existing_configs()

            # 4. Crear configuraciones faltantes
            self._create_missing_configs()

            # 5. Verificar dependencias
            self._verify_dependencies()

            # 6. Configurar permisos
            self._setup_permissions()

            # 7. Generar reporte de inicialización
            self._generate_initialization_report()

            logger.info("✅ Sistema de configuración inicializado exitosamente")

        except Exception as e:
            logger.error(f"❌ Error durante la inicialización: {e}")
            self.initialization_results["success"] = False
            self.initialization_results["errors"].append(str(e))

        return self.initialization_results

    def _verify_directory_structure(self):
        """Verifica y crea la estructura de directorios necesaria"""
        logger.info("📁 Verificando estructura de directorios...")

        required_dirs = [
            self.config_dir,
            self.config_dir / "backups",
            self.config_dir / "schemas",
            self.config_dir / "templates",
        ]

        for dir_path in required_dirs:
            if not dir_path.exists():
                dir_path.mkdir(parents=True, exist_ok=True)
                logger.info(f"   ✅ Creado directorio: {dir_path}")
                self.initialization_results["created_files"].append(str(dir_path))
            else:
                logger.info(f"   ✅ Directorio existente: {dir_path}")

    def _create_backup(self):
        """Crea un backup de las configuraciones existentes"""
        logger.info("💾 Creando backup de configuraciones existentes...")

        backup_dir = (
            self.config_dir
            / "backups"
            / f"pre_init_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        )
        backup_dir.mkdir(parents=True, exist_ok=True)

        config_files = (
            list(self.config_dir.glob("*.json"))
            + list(self.config_dir.glob("*.yml"))
            + list(self.config_dir.glob("*.yaml"))
        )

        if config_files:
            for config_file in config_files:
                try:
                    shutil.copy2(config_file, backup_dir / config_file.name)
                    logger.info(f"   ✅ Backup creado: {config_file.name}")
                except Exception as e:
                    logger.warning(
                        f"   ⚠️  Error creando backup de {config_file.name}: {e}"
                    )
                    self.initialization_results["warnings"].append(
                        f"Error backup {config_file.name}: {e}"
                    )

            self.initialization_results["backup_created"] = True
            logger.info(f"   ✅ Backup completado en: {backup_dir}")
        else:
            logger.info("   ℹ️  No hay configuraciones existentes para hacer backup")

    def _validate_existing_configs(self):
        """Valida las configuraciones existentes"""
        logger.info("🔍 Validando configuraciones existentes...")

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

        for filename in config_files:
            file_path = self.config_dir / filename
            if file_path.exists():
                try:
                    if filename.endswith(".json"):
                        with open(file_path, "r", encoding="utf-8") as f:
                            json.load(f)  # Validar JSON
                    elif filename.endswith((".yml", ".yaml")):
                        with open(file_path, "r", encoding="utf-8") as f:
                            yaml.safe_load(f)  # Validar YAML

                    logger.info(f"   ✅ Configuración válida: {filename}")
                    self.initialization_results["validated_configs"].append(filename)

                except Exception as e:
                    logger.error(f"   ❌ Configuración inválida: {filename} - {e}")
                    self.initialization_results["errors"].append(
                        f"Configuración inválida {filename}: {e}"
                    )
                    self.initialization_results["success"] = False
            else:
                logger.info(f"   ℹ️  Configuración no encontrada: {filename}")

    def _create_missing_configs(self):
        """Crea configuraciones faltantes con valores por defecto"""
        logger.info("📝 Creando configuraciones faltantes...")

        missing_configs = {
            "system_health.json": {
                "health_check_interval": 30,
                "max_retries": 3,
                "timeout": 10,
                "enabled_checks": [
                    "database_connection",
                    "redis_connection",
                    "model_availability",
                    "disk_space",
                    "memory_usage",
                ],
            },
            "logging_config.json": {
                "version": 1,
                "disable_existing_loggers": False,
                "formatters": {
                    "standard": {
                        "format": "%(asctime)s [%(levelname)s] %(name)s: %(message)s"
                    },
                    "detailed": {
                        "format": "%(asctime)s [%(levelname)s] %(name)s:%(lineno)d: %(message)s"
                    },
                },
                "handlers": {
                    "console": {
                        "class": "logging.StreamHandler",
                        "level": "INFO",
                        "formatter": "standard",
                        "stream": "ext://sys.stdout",
                    },
                    "file": {
                        "class": "logging.handlers.RotatingFileHandler",
                        "level": "DEBUG",
                        "formatter": "detailed",
                        "filename": "logs/neurofusion.log",
                        "maxBytes": 10485760,
                        "backupCount": 5,
                    },
                },
                "loggers": {
                    "": {
                        "handlers": ["console", "file"],
                        "level": "INFO",
                        "propagate": False,
                    }
                },
            },
            "api_config.json": {
                "version": "1.0",
                "title": "NeuroFusion API",
                "description": "API del sistema NeuroFusion",
                "contact": {
                    "name": "NeuroFusion Team",
                    "email": "support@neurofusion.ai",
                },
                "license": {
                    "name": "MIT",
                    "url": "https://opensource.org/licenses/MIT",
                },
                "servers": [
                    {
                        "url": "http://localhost:8000",
                        "description": "Servidor de desarrollo",
                    },
                    {
                        "url": "https://api.neurofusion.ai",
                        "description": "Servidor de producción",
                    },
                ],
                "security": {
                    "jwt_secret": "your-secret-key-here",
                    "jwt_algorithm": "HS256",
                    "jwt_expiration": 3600,
                    "rate_limit_enabled": True,
                    "rate_limit_requests": 100,
                    "rate_limit_window": 60,
                },
            },
        }

        for filename, config_data in missing_configs.items():
            file_path = self.config_dir / filename
            if not file_path.exists():
                try:
                    with open(file_path, "w", encoding="utf-8") as f:
                        json.dump(config_data, f, indent=2, ensure_ascii=False)

                    logger.info(f"   ✅ Configuración creada: {filename}")
                    self.initialization_results["created_files"].append(str(file_path))

                except Exception as e:
                    logger.error(f"   ❌ Error creando configuración {filename}: {e}")
                    self.initialization_results["errors"].append(
                        f"Error creando {filename}: {e}"
                    )
                    self.initialization_results["success"] = False
            else:
                logger.info(f"   ℹ️  Configuración ya existe: {filename}")

    def _verify_dependencies(self):
        """Verifica las dependencias necesarias para el sistema de configuración"""
        logger.info("🔧 Verificando dependencias...")

        required_packages = ["pyyaml", "jsonschema", "watchdog", "pathlib"]

        for package in required_packages:
            try:
                __import__(package)
                logger.info(f"   ✅ Dependencia disponible: {package}")
            except ImportError:
                logger.warning(f"   ⚠️  Dependencia faltante: {package}")
                self.initialization_results["warnings"].append(
                    f"Dependencia faltante: {package}"
                )

        # Verificar herramientas del sistema
        system_tools = ["python3", "pip", "git"]
        for tool in system_tools:
            try:
                result = subprocess.run(
                    [tool, "--version"], capture_output=True, text=True
                )
                if result.returncode == 0:
                    logger.info(f"   ✅ Herramienta disponible: {tool}")
                else:
                    logger.warning(f"   ⚠️  Herramienta no disponible: {tool}")
                    self.initialization_results["warnings"].append(
                        f"Herramienta no disponible: {tool}"
                    )
            except FileNotFoundError:
                logger.warning(f"   ⚠️  Herramienta no encontrada: {tool}")
                self.initialization_results["warnings"].append(
                    f"Herramienta no encontrada: {tool}"
                )

    def _setup_permissions(self):
        """Configura los permisos adecuados para los archivos de configuración"""
        logger.info("🔐 Configurando permisos...")

        try:
            # Configurar permisos para archivos de configuración
            config_files = (
                list(self.config_dir.glob("*.json"))
                + list(self.config_dir.glob("*.yml"))
                + list(self.config_dir.glob("*.yaml"))
            )

            for config_file in config_files:
                # Establecer permisos 644 (rw-r--r--)
                os.chmod(config_file, 0o644)
                logger.info(f"   ✅ Permisos configurados: {config_file.name}")

            # Configurar permisos para directorios
            for dir_path in [self.config_dir, self.config_dir / "backups"]:
                # Establecer permisos 755 (rwxr-xr-x)
                os.chmod(dir_path, 0o755)
                logger.info(f"   ✅ Permisos configurados: {dir_path}")

        except Exception as e:
            logger.warning(f"   ⚠️  Error configurando permisos: {e}")
            self.initialization_results["warnings"].append(
                f"Error configurando permisos: {e}"
            )

    def _generate_initialization_report(self):
        """Genera un reporte detallado de la inicialización"""
        logger.info("📊 Generando reporte de inicialización...")

        report = {
            "timestamp": datetime.now().isoformat(),
            "project_root": str(self.project_root),
            "config_dir": str(self.config_dir),
            "initialization_results": self.initialization_results,
            "system_info": {
                "python_version": sys.version,
                "platform": sys.platform,
                "working_directory": str(Path.cwd()),
            },
        }

        report_file = self.config_dir / "initialization_report.json"
        try:
            with open(report_file, "w", encoding="utf-8") as f:
                json.dump(report, f, indent=2, ensure_ascii=False)

            logger.info(f"   ✅ Reporte generado: {report_file}")
            self.initialization_results["created_files"].append(str(report_file))

        except Exception as e:
            logger.error(f"   ❌ Error generando reporte: {e}")
            self.initialization_results["errors"].append(
                f"Error generando reporte: {e}"
            )

    def print_summary(self):
        """Imprime un resumen de la inicialización"""
        print("\n" + "=" * 60)
        print("RESUMEN DE INICIALIZACIÓN DEL SISTEMA DE CONFIGURACIÓN")
        print("=" * 60)

        if self.initialization_results["success"]:
            print("✅ Estado: EXITOSO")
        else:
            print("❌ Estado: FALLIDO")

        print(f"\n📁 Directorio de configuración: {self.config_dir}")
        print(
            f"💾 Backup creado: {'Sí' if self.initialization_results['backup_created'] else 'No'}"
        )

        print(
            f"\n📝 Archivos creados: {len(self.initialization_results['created_files'])}"
        )
        for file_path in self.initialization_results["created_files"]:
            print(f"   ✅ {file_path}")

        print(
            f"\n🔍 Configuraciones validadas: {len(self.initialization_results['validated_configs'])}"
        )
        for config in self.initialization_results["validated_configs"]:
            print(f"   ✅ {config}")

        if self.initialization_results["errors"]:
            print(
                f"\n❌ Errores encontrados: {len(self.initialization_results['errors'])}"
            )
            for error in self.initialization_results["errors"]:
                print(f"   ❌ {error}")

        if self.initialization_results["warnings"]:
            print(f"\n⚠️  Advertencias: {len(self.initialization_results['warnings'])}")
            for warning in self.initialization_results["warnings"]:
                print(f"   ⚠️  {warning}")

        print("\n" + "=" * 60)


def main():
    """Función principal"""
    print("🚀 Inicializando Sistema de Configuración NeuroFusion")
    print("=" * 60)

    # Verificar que estamos en el directorio correcto
    if not Path("config").exists():
        print("❌ Error: No se encontró el directorio 'config'")
        print("   Asegúrate de ejecutar este script desde la raíz del proyecto")
        sys.exit(1)

    # Inicializar sistema
    initializer = ConfigSystemInitializer()
    results = initializer.initialize_config_system()

    # Mostrar resumen
    initializer.print_summary()

    # Retornar código de salida apropiado
    if results["success"]:
        print("\n✅ Inicialización completada exitosamente")
        sys.exit(0)
    else:
        print("\n❌ Inicialización falló. Revisa los errores arriba.")
        sys.exit(1)


if __name__ == "__main__":
    main()
