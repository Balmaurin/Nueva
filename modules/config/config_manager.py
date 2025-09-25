#!/usr/bin/env python3
"""
Sistema de Gestión de Configuración
Gestiona la configuración centralizada del sistema
"""

import os
import json
import yaml
import sqlite3
import logging
import shutil
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional, Tuple, Union
from pathlib import Path
import threading
import hashlib
from dataclasses import dataclass, asdict
import configparser


@dataclass
class ConfigSection:
    """Estructura de datos para una sección de configuración"""

    name: str
    data: Dict[str, Any]
    created_at: datetime
    updated_at: datetime
    version: str = "1.0"
    description: str = ""


class ConfigManager:
    """Gestor completo de configuración con funciones reales"""

    def __init__(self, config_dir: str = "config"):
        self.config_dir = Path(config_dir)
        self.config_dir.mkdir(exist_ok=True)

        # Configurar logging
        self.logger = logging.getLogger(__name__)
        self.logger.setLevel(logging.INFO)

        # Inicializar base de datos
        self.db_path = self.config_dir / "config_metadata.db"
        self._init_database()

        # Lock para operaciones thread-safe
        self._lock = threading.Lock()

        # Configuración por defecto
        self.default_config = self._load_default_config()

        # Cargar configuración actual
        self.current_config = self._load_current_config()

        self.logger.info(f"✅ ConfigManager inicializado en {self.config_dir}")

    def _init_database(self):
        """Inicializar base de datos SQLite para metadatos de configuración"""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS config_metadata (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    config_name TEXT UNIQUE NOT NULL,
                    config_type TEXT NOT NULL,
                    file_path TEXT NOT NULL,
                    file_size INTEGER NOT NULL,
                    checksum TEXT NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    version TEXT DEFAULT '1.0',
                    description TEXT,
                    is_active BOOLEAN DEFAULT TRUE,
                    metadata TEXT
                )
            """
            )

            conn.execute(
                """
                CREATE INDEX IF NOT EXISTS idx_config_name ON config_metadata(config_name)
            """
            )

            conn.execute(
                """
                CREATE INDEX IF NOT EXISTS idx_config_type ON config_metadata(config_type)
            """
            )

            conn.execute(
                """
                CREATE INDEX IF NOT EXISTS idx_is_active ON config_metadata(is_active)
            """
            )

    def _load_default_config(self) -> Dict[str, Any]:
        """Cargar configuración por defecto"""
        default_config = {
            "system": {
                "name": "Shaili AI System",
                "version": "3.1.0",
                "debug_mode": False,
                "log_level": "INFO",
                "max_workers": 4,
                "timeout_seconds": 30,
            },
            "models": {
                "default_model": "models/custom/shaili-personal-model",
                "t5_model": "t5-large",
                "embedding_model": "models/custom/shaili-personal-model",
                "max_tokens": 2048,
                "temperature": 0.7,
                "top_p": 0.9,
            },
            "database": {
                "type": "postgresql",
                "host": "localhost",
                "port": 5432,
                "name": "shaili_db",
                "user": "shaili_user",
                "password": "shaili_password",
            },
            "cache": {
                "enabled": True,
                "max_size_mb": 2048,
                "ttl_hours": 24,
                "compression_enabled": True,
            },
            "api": {
                "host": "127.0.0.1",
                "port": 8000,
                "cors_enabled": True,
                "rate_limit_enabled": True,
                "max_requests_per_minute": 100,
            },
            "security": {
                "jwt_secret": "your-secret-key-here",
                "jwt_expiration_hours": 24,
                "password_min_length": 8,
                "encryption_enabled": True,
            },
            "monitoring": {
                "enabled": True,
                "metrics_interval_seconds": 60,
                "alert_threshold": 0.8,
                "log_retention_days": 30,
            },
        }

        return default_config

    def _load_current_config(self) -> Dict[str, Any]:
        """Cargar configuración actual desde archivos"""
        config = self.default_config.copy()

        # Cargar archivos de configuración existentes
        config_files = {
            "neurofusion_config.json": "neurofusion",
            "docker-compose.yml": "docker",
            "docker-compose.dev.yml": "docker_dev",
            "rate_limits.json": "rate_limits",
            "monitoring_config.json": "monitoring",
            "training_token_config.json": "training",
            "sheily_token_config.json": "tokens",
        }

        for filename, config_type in config_files.items():
            file_path = self.config_dir / filename
            if file_path.exists():
                try:
                    with open(file_path, "r", encoding="utf-8") as f:
                        if filename.endswith(".json"):
                            data = json.load(f)
                        elif filename.endswith(".yml") or filename.endswith(".yaml"):
                            data = yaml.safe_load(f)
                        else:
                            continue

                    config[config_type] = data
                    self.logger.info(f"📋 Configuración cargada: {filename}")

                except Exception as e:
                    self.logger.error(f"❌ Error cargando {filename}: {e}")

        return config

    def get_config(self, section: str = None, key: str = None) -> Any:
        """Obtener valor de configuración"""
        try:
            if section is None:
                return self.current_config

            if key is None:
                return self.current_config.get(section, {})

            # Navegar por la estructura anidada
            keys = key.split(".")
            value = self.current_config.get(section, {})

            for k in keys:
                if isinstance(value, dict):
                    value = value.get(k)
                else:
                    return None

            return value

        except Exception as e:
            self.logger.error(f"❌ Error obteniendo configuración: {e}")
            return None

    def set_config(
        self, section: str, key: str, value: Any, save_to_file: bool = True
    ) -> bool:
        """Establecer valor de configuración"""
        with self._lock:
            try:
                # Crear sección si no existe
                if section not in self.current_config:
                    self.current_config[section] = {}

                # Navegar por la estructura anidada
                keys = key.split(".")
                current = self.current_config[section]

                # Crear estructura anidada
                for k in keys[:-1]:
                    if k not in current:
                        current[k] = {}
                    current = current[k]

                # Establecer valor
                current[keys[-1]] = value

                # Guardar en archivo si es requerido
                if save_to_file:
                    self._save_config_to_file(section)

                self.logger.info(f"✅ Configuración actualizada: {section}.{key}")
                return True

            except Exception as e:
                self.logger.error(f"❌ Error estableciendo configuración: {e}")
                return False

    def _save_config_to_file(self, section: str):
        """Guardar sección de configuración en archivo"""
        try:
            config_data = self.current_config.get(section, {})

            # Determinar archivo de destino
            file_mapping = {
                "neurofusion": "neurofusion_config.json",
                "docker": "docker-compose.yml",
                "docker_dev": "docker-compose.dev.yml",
                "rate_limits": "rate_limits.json",
                "monitoring": "monitoring_config.json",
                "training": "training_token_config.json",
                "tokens": "sheily_token_config.json",
            }

            filename = file_mapping.get(section, f"{section}_config.json")
            file_path = self.config_dir / filename

            # Crear backup antes de guardar
            if file_path.exists():
                backup_path = file_path.with_suffix(
                    f".backup.{datetime.now().strftime('%Y%m%d_%H%M%S')}"
                )
                shutil.copy2(file_path, backup_path)

            # Guardar archivo
            with open(file_path, "w", encoding="utf-8") as f:
                if filename.endswith(".json"):
                    json.dump(config_data, f, indent=2, ensure_ascii=False)
                elif filename.endswith(".yml") or filename.endswith(".yaml"):
                    yaml.dump(
                        config_data, f, default_flow_style=False, allow_unicode=True
                    )

            # Registrar en base de datos
            self._register_config_file(section, file_path)

            self.logger.info(f"💾 Configuración guardada: {file_path}")

        except Exception as e:
            self.logger.error(f"❌ Error guardando configuración: {e}")

    def _register_config_file(self, config_name: str, file_path: Path):
        """Registrar archivo de configuración en base de datos"""
        try:
            file_size = file_path.stat().st_size
            checksum = self._calculate_file_checksum(file_path)

            with sqlite3.connect(self.db_path) as conn:
                conn.execute(
                    """
                    INSERT OR REPLACE INTO config_metadata 
                    (config_name, config_type, file_path, file_size, checksum, updated_at)
                    VALUES (?, ?, ?, ?, ?, ?)
                """,
                    (
                        config_name,
                        "json" if file_path.suffix == ".json" else "yaml",
                        str(file_path),
                        file_size,
                        checksum,
                        datetime.now(),
                    ),
                )

        except Exception as e:
            self.logger.error(f"❌ Error registrando archivo de configuración: {e}")

    def _calculate_file_checksum(self, file_path: Path) -> str:
        """Calcular checksum SHA-256 del archivo"""
        hash_sha256 = hashlib.sha256()
        with open(file_path, "rb") as f:
            for chunk in iter(lambda: f.read(4096), b""):
                hash_sha256.update(chunk)
        return hash_sha256.hexdigest()

    def load_config_file(self, file_path: str, config_type: str = "custom") -> bool:
        """Cargar archivo de configuración externo"""
        try:
            file_path = Path(file_path)
            if not file_path.exists():
                self.logger.error(f"❌ Archivo no encontrado: {file_path}")
                return False

            with open(file_path, "r", encoding="utf-8") as f:
                if file_path.suffix == ".json":
                    data = json.load(f)
                elif file_path.suffix in [".yml", ".yaml"]:
                    data = yaml.safe_load(f)
                elif file_path.suffix == ".ini":
                    config_parser = configparser.ConfigParser()
                    config_parser.read(file_path)
                    data = {
                        section: dict(config_parser[section])
                        for section in config_parser.sections()
                    }
                else:
                    self.logger.error(
                        f"❌ Formato de archivo no soportado: {file_path.suffix}"
                    )
                    return False

            # Integrar en configuración actual
            self.current_config[config_type] = data

            # Copiar al directorio de configuración
            dest_path = self.config_dir / f"{config_type}_config{file_path.suffix}"
            shutil.copy2(file_path, dest_path)

            # Registrar en base de datos
            self._register_config_file(config_type, dest_path)

            self.logger.info(f"✅ Configuración cargada: {file_path}")
            return True

        except Exception as e:
            self.logger.error(f"❌ Error cargando archivo de configuración: {e}")
            return False

    def export_config(
        self, section: str = None, format: str = "json", export_path: str = None
    ) -> str:
        """Exportar configuración"""
        try:
            # Determinar datos a exportar
            if section:
                config_data = self.current_config.get(section, {})
                filename = f"{section}_config"
            else:
                config_data = self.current_config
                filename = "complete_config"

            # Crear directorio de exportación
            if export_path:
                export_dir = Path(export_path)
            else:
                export_dir = Path("exports")

            export_dir.mkdir(exist_ok=True)

            # Crear archivo de exportación
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

            if format.lower() == "json":
                export_file = export_dir / f"{filename}_{timestamp}.json"
                with open(export_file, "w", encoding="utf-8") as f:
                    json.dump(config_data, f, indent=2, ensure_ascii=False)

            elif format.lower() == "yaml":
                export_file = export_dir / f"{filename}_{timestamp}.yml"
                with open(export_file, "w", encoding="utf-8") as f:
                    yaml.dump(
                        config_data, f, default_flow_style=False, allow_unicode=True
                    )

            elif format.lower() == "ini":
                export_file = export_dir / f"{filename}_{timestamp}.ini"
                config_parser = configparser.ConfigParser()

                for section_name, section_data in config_data.items():
                    if isinstance(section_data, dict):
                        config_parser[section_name] = section_data

                with open(export_file, "w", encoding="utf-8") as f:
                    config_parser.write(f)

            else:
                raise ValueError(f"Formato no soportado: {format}")

            self.logger.info(f"📤 Configuración exportada: {export_file}")
            return str(export_file)

        except Exception as e:
            self.logger.error(f"❌ Error exportando configuración: {e}")
            raise

    def validate_config(self, section: str = None) -> Dict[str, Any]:
        """Validar configuración"""
        validation_results = {
            "valid": True,
            "errors": [],
            "warnings": [],
            "sections_checked": [],
        }

        try:
            config_to_validate = (
                self.current_config.get(section, {}) if section else self.current_config
            )

            # Validar secciones específicas
            if section:
                validation_results["sections_checked"].append(section)
                self._validate_section(section, config_to_validate, validation_results)
            else:
                for section_name, section_data in config_to_validate.items():
                    validation_results["sections_checked"].append(section_name)
                    self._validate_section(
                        section_name, section_data, validation_results
                    )

            validation_results["valid"] = len(validation_results["errors"]) == 0

        except Exception as e:
            validation_results["valid"] = False
            validation_results["errors"].append(f"Error de validación: {e}")

        return validation_results

    def _validate_section(
        self, section_name: str, section_data: Dict[str, Any], results: Dict[str, Any]
    ):
        """Validar sección específica de configuración"""
        validators = {
            "system": self._validate_system_config,
            "models": self._validate_models_config,
            "database": self._validate_database_config,
            "api": self._validate_api_config,
            "security": self._validate_security_config,
        }

        validator = validators.get(section_name)
        if validator:
            validator(section_data, results)

    def _validate_system_config(self, config: Dict[str, Any], results: Dict[str, Any]):
        """Validar configuración del sistema"""
        required_fields = ["name", "version", "debug_mode"]

        for field in required_fields:
            if field not in config:
                results["errors"].append(f"Campo requerido faltante en system: {field}")

        if "max_workers" in config and config["max_workers"] <= 0:
            results["errors"].append("max_workers debe ser mayor que 0")

    def _validate_models_config(self, config: Dict[str, Any], results: Dict[str, Any]):
        """Validar configuración de modelos"""
        required_fields = ["default_model", "max_tokens", "temperature"]

        for field in required_fields:
            if field not in config:
                results["errors"].append(f"Campo requerido faltante en models: {field}")

        if "temperature" in config and not (0 <= config["temperature"] <= 1):
            results["errors"].append("temperature debe estar entre 0 y 1")

    def _validate_database_config(
        self, config: Dict[str, Any], results: Dict[str, Any]
    ):
        """Validar configuración de base de datos"""
        required_fields = ["type", "host", "port", "name", "user"]

        for field in required_fields:
            if field not in config:
                results["errors"].append(
                    f"Campo requerido faltante en database: {field}"
                )

        if "port" in config and not (1 <= config["port"] <= 65535):
            results["errors"].append("port debe estar entre 1 y 65535")

    def _validate_api_config(self, config: Dict[str, Any], results: Dict[str, Any]):
        """Validar configuración de API"""
        if "port" in config and not (1 <= config["port"] <= 65535):
            results["errors"].append("port debe estar entre 1 y 65535")

    def _validate_security_config(
        self, config: Dict[str, Any], results: Dict[str, Any]
    ):
        """Validar configuración de seguridad"""
        if "jwt_secret" in config and config["jwt_secret"] == "your-secret-key-here":
            results["warnings"].append("jwt_secret debe ser cambiado por seguridad")

    def get_config_history(
        self, section: str = None, limit: int = 50
    ) -> List[Dict[str, Any]]:
        """Obtener historial de cambios de configuración"""
        with sqlite3.connect(self.db_path) as conn:
            query = "SELECT * FROM config_metadata WHERE 1=1"
            params = []

            if section:
                query += " AND config_name = ?"
                params.append(section)

            query += " ORDER BY updated_at DESC LIMIT ?"
            params.append(limit)

            cursor = conn.execute(query, params)
            results = []

            for row in cursor.fetchall():
                results.append(
                    {
                        "config_name": row[1],
                        "config_type": row[2],
                        "file_path": row[3],
                        "file_size_mb": row[4] / (1024 * 1024),
                        "checksum": row[5],
                        "created_at": row[6],
                        "updated_at": row[7],
                        "version": row[8],
                        "description": row[9],
                        "is_active": row[10],
                        "metadata": json.loads(row[11]) if row[11] else {},
                    }
                )

            return results

    def reset_to_default(self, section: str = None) -> bool:
        """Restablecer configuración a valores por defecto"""
        with self._lock:
            try:
                if section:
                    if section in self.default_config:
                        self.current_config[section] = self.default_config[
                            section
                        ].copy()
                        self._save_config_to_file(section)
                        self.logger.info(f"✅ Configuración restablecida: {section}")
                    else:
                        self.logger.error(f"❌ Sección no encontrada: {section}")
                        return False
                else:
                    self.current_config = self.default_config.copy()
                    # Guardar todas las secciones
                    for section_name in self.default_config.keys():
                        self._save_config_to_file(section_name)
                    self.logger.info("✅ Configuración completa restablecida")

                return True

            except Exception as e:
                self.logger.error(f"❌ Error restableciendo configuración: {e}")
                return False

    def get_config_stats(self) -> Dict[str, Any]:
        """Obtener estadísticas de configuración"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute(
                """
                SELECT 
                    COUNT(*) as total_configs,
                    COUNT(DISTINCT config_type) as unique_types,
                    SUM(file_size) as total_size,
                    MIN(created_at) as earliest_config,
                    MAX(updated_at) as latest_update,
                    COUNT(CASE WHEN is_active = 1 THEN 1 END) as active_configs
                FROM config_metadata
            """
            )
            result = cursor.fetchone()

            return {
                "total_configs": result[0],
                "unique_types": result[1],
                "total_size_mb": (result[2] or 0) / (1024 * 1024),
                "earliest_config": result[3],
                "latest_update": result[4],
                "active_configs": result[5],
                "sections_count": len(self.current_config),
                "default_sections": list(self.default_config.keys()),
            }


# Instancia global del gestor de configuración
config_manager = ConfigManager()
