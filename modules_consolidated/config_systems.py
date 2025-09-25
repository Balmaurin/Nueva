#!/usr/bin/env python3
"""
Módulo Consolidado: Config Systems
==========================================
Consolidado desde: config/config_manager.py, modules/config/config_manager.py
"""

# === config/config_manager.py ===

import json
import os
import logging
from pathlib import Path
from typing import Dict, Any, Optional, Union
from dataclasses import dataclass
import yaml

logger = logging.getLogger(__name__)

@dataclass
class ConfigSection:
    """Sección de configuración"""
    name: str
    data: Dict[str, Any]
    required: bool = True

class UnifiedConfigManager:
    """Gestor de configuración unificado"""
    
    def __init__(self, config_dir: str = "config"):
        self.config_dir = Path(config_dir)
        self.config_file = self.config_dir / "unified_config.json"
        self.config_data: Dict[str, Any] = {}
        self.environment = os.getenv("NODE_ENV", "development")
        
        # Cargar configuración
        self._load_config()
        
    def _load_config(self) -> None:
        """Cargar configuración desde archivo"""
        try:
            if self.config_file.exists():
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    self.config_data = json.load(f)
                logger.info(f"✅ Configuración cargada desde {self.config_file}")
            else:
                logger.warning(f"⚠️ Archivo de configuración no encontrado: {self.config_file}")
                self.config_data = self._get_default_config()
                
        except Exception as e:
            logger.error(f"❌ Error cargando configuración: {e}")
            self.config_data = self._get_default_config()
    
    def _get_default_config(self) -> Dict[str, Any]:
        """Obtener configuración por defecto"""
        return {
            "system_name": "Sheily AI",
            "version": "3.1.0",
            "environment": self.environment,
            "debug_mode": self.environment == "development"
        }
    
    def get(self, key: str, default: Any = None) -> Any:
        """Obtener valor de configuración"""
        keys = key.split('.')
        value = self.config_data
        
        try:
            for k in keys:
                value = value[k]
            return value
        except (KeyError, TypeError):
            return default
    
    def set(self, key: str, value: Any) -> None:
        """Establecer valor de configuración"""
        keys = key.split('.')
        config = self.config_data
        
        for k in keys[:-1]:
            if k not in config:
                config[k] = {}
            config = config[k]
        
        config[keys[-1]] = value
        logger.info(f"✅ Configuración actualizada: {key} = {value}")
    
    def get_section(self, section: str) -> Dict[str, Any]:
        """Obtener sección completa de configuración"""
        return self.get(section, {})
    
    def update_section(self, section: str, data: Dict[str, Any]) -> None:
        """Actualizar sección completa"""
        self.set(section, data)
    
    def validate_config(self) -> Dict[str, Any]:
        """Validar configuración"""
        errors = []
        warnings = []
        
        # Validar secciones requeridas
        required_sections = [
            "server", "database", "security", "ai_models", 
            "branches", "training", "memory", "monitoring"
        ]
        
        for section in required_sections:
            if not self.get(section):
                errors.append(f"Sección requerida faltante: {section}")
        
        # Validar configuración de base de datos
        db_config = self.get_section("database")
        if db_config:
            if not db_config.get("type"):
                errors.append("Tipo de base de datos no especificado")
            if not db_config.get("host"):
                errors.append("Host de base de datos no especificado")
        
        # Validar configuración de seguridad
        security_config = self.get_section("security")
        if security_config:
            jwt_config = security_config.get("jwt", {})
            if not jwt_config.get("expiration"):
                warnings.append("Expiración JWT no especificada, usando valor por defecto")
        
        # Validar ramas
        branches_config = self.get_section("branches")
        if branches_config:
            total_branches = branches_config.get("total_branches", 0)
            branch_list = branches_config.get("list", [])
            if total_branches != len(branch_list):
                errors.append(f"Inconsistencia en ramas: total={total_branches}, lista={len(branch_list)}")
        
        return {
            "valid": len(errors) == 0,
            "errors": errors,
            "warnings": warnings
        }
    
    def save_config(self) -> bool:
        """Guardar configuración a archivo"""
        try:
            # Crear directorio si no existe
            self.config_dir.mkdir(exist_ok=True)
            
            # Validar antes de guardar
            validation = self.validate_config()
            if not validation["valid"]:
                logger.error(f"❌ Configuración inválida, no se puede guardar: {validation['errors']}")
                return False
            
            # Guardar archivo
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(self.config_data, f, indent=2, ensure_ascii=False)
            
            logger.info(f"✅ Configuración guardada en {self.config_file}")
            return True
            
        except Exception as e:
            logger.error(f"❌ Error guardando configuración: {e}")
            return False
    
    def load_from_env(self) -> None:
        """Cargar configuración desde variables de entorno"""
        env_mappings = {
            "server.port": "PORT",
            "server.host": "HOST",
            "database.host": "DB_HOST",
            "database.port": "DB_PORT",
            "database.name": "DB_NAME",
            "database.user": "DB_USER",
            "database.type": "DB_TYPE",
            "ai_models.llm.server_url": "MODEL_SERVER_URL",
            "ai_models.llm.model_name": "LLM_MODEL_NAME",
            "monitoring.log_level": "LOG_LEVEL"
        }
        
        for config_key, env_key in env_mappings.items():
            env_value = os.getenv(env_key)
            if env_value:
                # Convertir tipos
                if env_key in ["PORT", "DB_PORT"]:
                    env_value = int(env_value)
                elif env_key in ["DB_TYPE"]:
                    env_value = env_value.lower()
                
                self.set(config_key, env_value)
                logger.info(f"✅ Configuración desde ENV: {config_key} = {env_value}")
    
    def get_database_url(self) -> str:
        """Obtener URL de conexión a base de datos"""
        db_config = self.get_section("database")
        
        if db_config.get("type") == "postgres":
            host = db_config.get("host", "localhost")
            port = db_config.get("port", 5432)
            name = db_config.get("name", "sheily_ai_db")
            user = db_config.get("user", "sheily_ai_user")
            password = os.getenv("DB_PASSWORD", "")
            
            return f"postgresql://{user}:{password}@{host}:{port}/{name}"
        elif db_config.get("type") == "sqlite":
            name = db_config.get("name", "sheily_ai.db")
            return f"sqlite:///{name}"
        else:
            raise ValueError(f"Tipo de base de datos no soportado: {db_config.get('type')}")
    
    def get_redis_url(self) -> str:
        """Obtener URL de conexión a Redis"""
        redis_config = self.get_section("redis")
        host = redis_config.get("host", "localhost")
        port = redis_config.get("port", 6379)
        db = redis_config.get("db", 0)
        password = os.getenv("REDIS_PASSWORD", "")
        
        if password:
            return f"redis://:{password}@{host}:{port}/{db}"
        else:
            return f"redis://{host}:{port}/{db}"
    
    def export_to_env_file(self, output_file: str = "config.env") -> bool:
        """Exportar configuración a archivo .env"""
        try:
            env_mappings = {
                "PORT": "server.port",
                "HOST": "server.host",
                "NODE_ENV": "environment",
                "DB_HOST": "database.host",
                "DB_PORT": "database.port",
                "DB_NAME": "database.name",
                "DB_USER": "database.user",
                "DB_TYPE": "database.type",
                "MODEL_SERVER_URL": "ai_models.llm.server_url",
                "LLM_MODEL_NAME": "ai_models.llm.model_name",
                "LOG_LEVEL": "monitoring.log_level"
            }
            
            with open(output_file, 'w') as f:
                f.write("# Configuración exportada desde unified_config.json\n")
                f.write(f"# Generado automáticamente\n\n")
                
                for env_key, config_key in env_mappings.items():
                    value = self.get(config_key)
                    if value is not None:
                        f.write(f"{env_key}={value}\n")
            
            logger.info(f"✅ Configuración exportada a {output_file}")
            return True
            
        except Exception as e:
            logger.error(f"❌ Error exportando configuración: {e}")
            return False
    
    def get_summary(self) -> Dict[str, Any]:
        """Obtener resumen de configuración"""
        validation = self.validate_config()
        
        return {
            "system_name": self.get("system_name"),
            "version": self.get("version"),
            "environment": self.get("environment"),
            "debug_mode": self.get("debug_mode"),
            "total_branches": self.get("branches.total_branches", 0),
            "database_type": self.get("database.type"),
            "ai_model": self.get("ai_models.llm.model_name"),
            "validation": validation,
            "config_file": str(self.config_file)
        }

# Instancia global del gestor de configuración
config_manager = UnifiedConfigManager()

def get_config(key: str = None, default: Any = None) -> Any:
    """Función de conveniencia para obtener configuración"""
    if key is None:
        return config_manager.config_data
    return config_manager.get(key, default)

def set_config(key: str, value: Any) -> None:
    """Función de conveniencia para establecer configuración"""
    config_manager.set(key, value)

def validate_config() -> Dict[str, Any]:
    """Función de conveniencia para validar configuración"""
    return config_manager.validate_config()

def save_config() -> bool:
    """Función de conveniencia para guardar configuración"""
    return config_manager.save_config()

if __name__ == "__main__":
    # Configurar logging
    logging.basicConfig(level=logging.INFO)
    
    # Crear instancia del gestor
    manager = UnifiedConfigManager()
    
    # Cargar desde variables de entorno
    manager.load_from_env()
    
    # Validar configuración
    validation = manager.validate_config()
    print(f"Validación: {validation}")
    
    # Mostrar resumen
    summary = manager.get_summary()
    print(f"Resumen: {summary}")
    
    # Guardar configuración
    if manager.save_config():
        print("✅ Configuración guardada exitosamente")
    else:
        print("❌ Error guardando configuración")

# === modules/config/config_manager.py ===

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
                "name": "Sheily AI System",
                "version": "3.1.0",
                "debug_mode": False,
                "log_level": "INFO",
                "max_workers": 4,
                "timeout_seconds": 30,
            },
            "models": {
                "default_model": "models/custom/sheily-personal-model",
                "t5_model": "t5-large",
                "embedding_model": "models/custom/sheily-personal-model",
                "max_tokens": 2048,
                "temperature": 0.7,
                "top_p": 0.9,
            },
            "database": {
                "type": "postgresql",
                "host": "localhost",
                "port": 5432,
                "name": "sheily_db",
                "user": "sheily_user",
                "password": "sheily_password",
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


