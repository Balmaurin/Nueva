#!/usr/bin/env python3
"""
Gestor de Configuración Unificado - Sheily AI
=============================================
Maneja todas las configuraciones del sistema de forma centralizada
"""

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