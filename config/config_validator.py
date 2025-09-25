#!/usr/bin/env python3
"""
Validador de Configuración del Sistema NeuroFusion
Verifica la integridad y validez de todas las configuraciones del sistema
"""

import json
import yaml
import logging
from pathlib import Path
from typing import Dict, Any, List, Tuple
from dataclasses import dataclass
import jsonschema
from jsonschema import validate, ValidationError
import re

# Configuración de logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@dataclass
class ValidationResult:
    """Resultado de validación de configuración"""

    is_valid: bool
    errors: List[str]
    warnings: List[str]
    file_path: str
    config_type: str


class ConfigValidator:
    """Validador principal de configuraciones del sistema NeuroFusion"""

    def __init__(self, config_dir: str = "config"):
        self.config_dir = Path(config_dir)
        self.validation_results = []

        # Esquemas de validación JSON
        self.schemas = self._load_validation_schemas()

    def _load_validation_schemas(self) -> Dict[str, Dict]:
        """Carga los esquemas de validación para cada tipo de configuración"""
        return {
            "main_config": {
                "type": "object",
                "required": [
                    "system_name",
                    "version",
                    "debug_mode",
                    "base_path",
                    "data_path",
                    "models_path",
                    "cache_path",
                    "logs_path",
                    "default_embedding_model",
                    "default_llm_model",
                    "max_concurrent_operations",
                    "cache_enabled",
                    "cache_size",
                    "enable_encryption",
                    "blockchain_enabled",
                    "solana_network",
                    "log_level",
                    "log_file",
                    "frontend_port",
                    "backend_port",
                    "host",
                    "enable_monitoring",
                    "advanced_modules_enabled",
                    "components",
                    "performance",
                    "security",
                ],
                "properties": {
                    "system_name": {"type": "string"},
                    "version": {"type": "string", "pattern": r"^\d+\.\d+\.\d+$"},
                    "debug_mode": {"type": "boolean"},
                    "base_path": {"type": "string"},
                    "data_path": {"type": "string"},
                    "models_path": {"type": "string"},
                    "cache_path": {"type": "string"},
                    "logs_path": {"type": "string"},
                    "default_embedding_model": {"type": "string"},
                    "default_llm_model": {"type": "string"},
                    "max_concurrent_operations": {"type": "integer", "minimum": 1},
                    "cache_enabled": {"type": "boolean"},
                    "cache_size": {"type": "integer", "minimum": 1000},
                    "enable_encryption": {"type": "boolean"},
                    "blockchain_enabled": {"type": "boolean"},
                    "solana_network": {
                        "type": "string",
                        "enum": ["devnet", "testnet", "mainnet"],
                    },
                    "log_level": {
                        "type": "string",
                        "enum": ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"],
                    },
                    "log_file": {"type": "string"},
                    "frontend_port": {
                        "type": "integer",
                        "minimum": 1024,
                        "maximum": 65535,
                    },
                    "backend_port": {
                        "type": "integer",
                        "minimum": 1024,
                        "maximum": 65535,
                    },
                    "host": {"type": "string"},
                    "enable_monitoring": {"type": "boolean"},
                    "advanced_modules_enabled": {"type": "boolean"},
                    "components": {"type": "object"},
                    "performance": {"type": "object"},
                    "security": {"type": "object"},
                },
            },
            "module_init": {
                "type": "object",
                "patternProperties": {
                    "^.*$": {
                        "type": "object",
                        "required": ["dependencies", "init_params"],
                        "properties": {
                            "dependencies": {
                                "type": "array",
                                "items": {"type": "string"},
                            },
                            "init_params": {"type": "object"},
                        },
                    }
                },
            },
            "rate_limits": {
                "type": "object",
                "required": ["rules"],
                "properties": {
                    "rules": {
                        "type": "array",
                        "items": {
                            "type": "object",
                            "required": ["rule_id", "description", "config", "enabled"],
                            "properties": {
                                "rule_id": {"type": "string"},
                                "description": {"type": "string"},
                                "config": {"type": "object"},
                                "enabled": {"type": "boolean"},
                            },
                        },
                    }
                },
            },
            "monitoring_config": {
                "type": "object",
                "required": ["enabled", "alert_thresholds", "monitoring_rules"],
                "properties": {
                    "enabled": {"type": "boolean"},
                    "alert_thresholds": {"type": "object"},
                    "monitoring_rules": {"type": "array"},
                },
            },
            "training_config": {
                "type": "object",
                "required": [
                    "points_per_training",
                    "tokens_per_point",
                    "min_training_duration",
                    "max_daily_tokens",
                    "training_types",
                    "bonus_conditions",
                ],
                "properties": {
                    "points_per_training": {"type": "integer", "minimum": 1},
                    "tokens_per_point": {"type": "number", "minimum": 0},
                    "min_training_duration": {"type": "integer", "minimum": 1},
                    "max_daily_tokens": {"type": "integer", "minimum": 1},
                    "training_types": {"type": "object"},
                    "bonus_conditions": {"type": "object"},
                },
            },
            "sheily_token_config": {
                "type": "object",
                "required": [
                    "name",
                    "symbol",
                    "description",
                    "decimals",
                    "initial_supply",
                    "mint_address",
                    "authority",
                    "created_at",
                    "network",
                ],
                "properties": {
                    "name": {"type": "string"},
                    "symbol": {"type": "string"},
                    "description": {"type": "string"},
                    "decimals": {"type": "integer", "minimum": 0, "maximum": 18},
                    "initial_supply": {"type": "integer", "minimum": 1},
                    "mint_address": {"type": "string"},
                    "authority": {"type": "string"},
                    "created_at": {"type": "string"},
                    "network": {"type": "string"},
                },
            },
        }

    def validate_all_configs(self) -> List[ValidationResult]:
        """Valida todas las configuraciones del sistema"""
        self.validation_results = []

        # Validar archivos JSON
        json_configs = [
            ("neurofusion_config.json", "main_config"),
            ("module_initialization.json", "module_init"),
            ("rate_limits.json", "rate_limits"),
            ("monitoring_config.json", "monitoring_config"),
            ("training_token_config.json", "training_config"),
            ("sheily_token_config.json", "sheily_token_config"),
            ("sheily_token_metadata.json", "sheily_token_metadata"),
            ("advanced_training_config.json", "advanced_training_config"),
        ]

        for filename, config_type in json_configs:
            result = self.validate_json_config(filename, config_type)
            self.validation_results.append(result)

        # Validar archivos YAML
        yaml_configs = [
            ("docker-compose.yml", "docker_compose"),
            ("docker-compose.dev.yml", "docker_compose_dev"),
        ]

        for filename, config_type in yaml_configs:
            result = self.validate_yaml_config(filename, config_type)
            self.validation_results.append(result)

        # Validaciones adicionales
        self._validate_cross_config_consistency()
        self._validate_paths_existence()
        self._validate_port_conflicts()

        return self.validation_results

    def validate_json_config(self, filename: str, config_type: str) -> ValidationResult:
        """Valida una configuración JSON específica"""
        file_path = self.config_dir / filename
        result = ValidationResult(
            is_valid=True,
            errors=[],
            warnings=[],
            file_path=str(file_path),
            config_type=config_type,
        )

        try:
            if not file_path.exists():
                result.errors.append(f"Archivo no encontrado: {filename}")
                result.is_valid = False
                return result

            with open(file_path, "r", encoding="utf-8") as f:
                config_data = json.load(f)

            # Validar esquema JSON si existe
            if config_type in self.schemas:
                try:
                    validate(instance=config_data, schema=self.schemas[config_type])
                except ValidationError as e:
                    result.errors.append(f"Error de validación JSON: {e.message}")
                    result.is_valid = False

            # Validaciones específicas por tipo
            if config_type == "main_config":
                self._validate_main_config(config_data, result)
            elif config_type == "module_init":
                self._validate_module_init_config(config_data, result)
            elif config_type == "rate_limits":
                self._validate_rate_limits_config(config_data, result)
            elif config_type == "monitoring_config":
                self._validate_monitoring_config(config_data, result)
            elif config_type == "training_config":
                self._validate_training_config(config_data, result)
            elif config_type == "sheily_token_config":
                self._validate_sheily_token_config(config_data, result)

        except json.JSONDecodeError as e:
            result.errors.append(f"Error de sintaxis JSON: {e}")
            result.is_valid = False
        except Exception as e:
            result.errors.append(f"Error inesperado: {e}")
            result.is_valid = False

        return result

    def validate_yaml_config(self, filename: str, config_type: str) -> ValidationResult:
        """Valida una configuración YAML específica"""
        file_path = self.config_dir / filename
        result = ValidationResult(
            is_valid=True,
            errors=[],
            warnings=[],
            file_path=str(file_path),
            config_type=config_type,
        )

        try:
            if not file_path.exists():
                result.errors.append(f"Archivo no encontrado: {filename}")
                result.is_valid = False
                return result

            with open(file_path, "r", encoding="utf-8") as f:
                config_data = yaml.safe_load(f)

            # Validaciones específicas para Docker Compose
            if config_type.startswith("docker_compose"):
                self._validate_docker_compose_config(config_data, result)

        except yaml.YAMLError as e:
            result.errors.append(f"Error de sintaxis YAML: {e}")
            result.is_valid = False
        except Exception as e:
            result.errors.append(f"Error inesperado: {e}")
            result.is_valid = False

        return result

    def _validate_main_config(self, config: Dict[str, Any], result: ValidationResult):
        """Validaciones específicas para la configuración principal"""
        # Validar puertos
        if config.get("frontend_port") == config.get("backend_port"):
            result.errors.append("Los puertos frontend y backend no pueden ser iguales")
            result.is_valid = False

        # Validar rutas
        paths_to_check = [
            "base_path",
            "data_path",
            "models_path",
            "cache_path",
            "logs_path",
        ]
        for path_field in paths_to_check:
            if path_field in config:
                path = Path(config[path_field])
                if not path.exists():
                    result.warnings.append(f"Ruta no existe: {path}")

        # Validar componentes requeridos
        components = config.get("components", {})
        required_components = ["embeddings", "branch_system", "learning", "memory"]
        for component in required_components:
            if component not in components:
                result.errors.append(f"Componente requerido faltante: {component}")
                result.is_valid = False

        # Validar configuración de rendimiento
        performance = config.get("performance", {})
        if performance.get("memory_limit_mb", 0) <= 0:
            result.errors.append("memory_limit_mb debe ser mayor que 0")
            result.is_valid = False

        if (
            performance.get("cpu_limit_percent", 0) <= 0
            or performance.get("cpu_limit_percent", 0) > 100
        ):
            result.errors.append("cpu_limit_percent debe estar entre 1 y 100")
            result.is_valid = False

    def _validate_module_init_config(
        self, config: Dict[str, Any], result: ValidationResult
    ):
        """Validaciones específicas para la configuración de inicialización de módulos"""
        for module_name, module_config in config.items():
            # Verificar dependencias circulares
            dependencies = module_config.get("dependencies", [])
            if module_name in dependencies:
                result.errors.append(f"Dependencia circular detectada en {module_name}")
                result.is_valid = False

            # Verificar que las dependencias existan
            for dep in dependencies:
                if dep not in config:
                    result.errors.append(
                        f"Dependencia no encontrada: {dep} en {module_name}"
                    )
                    result.is_valid = False

    def _validate_rate_limits_config(
        self, config: Dict[str, Any], result: ValidationResult
    ):
        """Validaciones específicas para la configuración de rate limits"""
        rules = config.get("rules", [])
        rule_ids = set()

        for rule in rules:
            rule_id = rule.get("rule_id")
            if rule_id in rule_ids:
                result.errors.append(f"ID de regla duplicado: {rule_id}")
                result.is_valid = False
            rule_ids.add(rule_id)

            # Validar configuración de regla
            rule_config = rule.get("config", {})
            if rule_config.get("max_requests", 0) <= 0:
                result.errors.append(
                    f"max_requests debe ser mayor que 0 en regla {rule_id}"
                )
                result.is_valid = False

    def _validate_monitoring_config(
        self, config: Dict[str, Any], result: ValidationResult
    ):
        """Validaciones específicas para la configuración de monitoreo"""
        if not config.get("enabled", False):
            result.warnings.append("El monitoreo está deshabilitado")

        alert_thresholds = config.get("alert_thresholds", {})
        for threshold_name, threshold_value in alert_thresholds.items():
            if isinstance(threshold_value, (int, float)) and threshold_value < 0:
                result.errors.append(f"Umbral de alerta negativo: {threshold_name}")
                result.is_valid = False

    def _validate_training_config(
        self, config: Dict[str, Any], result: ValidationResult
    ):
        """Validaciones específicas para la configuración de entrenamiento"""
        if config.get("points_per_training", 0) <= 0:
            result.errors.append("points_per_training debe ser mayor que 0")
            result.is_valid = False

        if config.get("tokens_per_point", 0) < 0:
            result.errors.append("tokens_per_point no puede ser negativo")
            result.is_valid = False

        training_types = config.get("training_types", {})
        for training_type, type_config in training_types.items():
            if type_config.get("points", 0) <= 0:
                result.errors.append(
                    f"Puntos inválidos para tipo de entrenamiento: {training_type}"
                )
                result.is_valid = False

    def _validate_sheily_token_config(
        self, config: Dict[str, Any], result: ValidationResult
    ):
        """Validaciones específicas para la configuración del token Sheily"""
        # Validar formato de dirección Solana
        mint_address = config.get("mint_address", "")
        authority = config.get("authority", "")

        if not self._is_valid_solana_address(mint_address):
            result.errors.append("Dirección mint_address inválida")
            result.is_valid = False

        if not self._is_valid_solana_address(authority):
            result.errors.append("Dirección authority inválida")
            result.is_valid = False

        # Validar decimales
        decimals = config.get("decimals", 0)
        if decimals < 0 or decimals > 18:
            result.errors.append("Los decimales deben estar entre 0 y 18")
            result.is_valid = False

    def _validate_docker_compose_config(
        self, config: Dict[str, Any], result: ValidationResult
    ):
        """Validaciones específicas para la configuración de Docker Compose"""
        services = config.get("services", {})
        required_services = ["postgres", "redis"]

        for service in required_services:
            if service not in services:
                result.errors.append(f"Servicio requerido faltante: {service}")
                result.is_valid = False

        # Validar configuración de PostgreSQL
        if "postgres" in services:
            postgres_config = services["postgres"]
            required_env_vars = ["POSTGRES_DB", "POSTGRES_USER", "POSTGRES_PASSWORD"]

            for env_var in required_env_vars:
                if env_var not in postgres_config.get("environment", {}):
                    result.errors.append(
                        f"Variable de entorno requerida faltante: {env_var}"
                    )
                    result.is_valid = False

    def _validate_cross_config_consistency(self):
        """Valida la consistencia entre diferentes configuraciones"""
        # Obtener configuraciones principales
        main_config_result = next(
            (r for r in self.validation_results if r.config_type == "main_config"), None
        )
        docker_config_result = next(
            (r for r in self.validation_results if r.config_type == "docker_compose"),
            None,
        )

        if main_config_result and docker_config_result:
            # Verificar que los puertos coincidan
            try:
                with open(main_config_result.file_path, "r") as f:
                    main_config = json.load(f)

                with open(docker_config_result.file_path, "r") as f:
                    docker_config = yaml.safe_load(f)

                frontend_port = main_config.get("frontend_port")
                backend_port = main_config.get("backend_port")

                # Verificar puertos en Docker Compose
                frontend_service = docker_config.get("services", {}).get("frontend", {})
                backend_service = docker_config.get("services", {}).get("backend", {})

                if frontend_service and frontend_port:
                    docker_frontend_port = (
                        frontend_service.get("ports", [None])[0].split(":")[0]
                        if frontend_service.get("ports")
                        else None
                    )
                    if (
                        docker_frontend_port
                        and int(docker_frontend_port) != frontend_port
                    ):
                        main_config_result.warnings.append(
                            "Puerto frontend no coincide con Docker Compose"
                        )

                if backend_service and backend_port:
                    docker_backend_port = (
                        backend_service.get("ports", [None])[0].split(":")[0]
                        if backend_service.get("ports")
                        else None
                    )
                    if docker_backend_port and int(docker_backend_port) != backend_port:
                        main_config_result.warnings.append(
                            "Puerto backend no coincide con Docker Compose"
                        )

            except Exception as e:
                main_config_result.errors.append(f"Error validando consistencia: {e}")
                main_config_result.is_valid = False

    def _validate_paths_existence(self):
        """Valida la existencia de rutas críticas"""
        main_config_result = next(
            (r for r in self.validation_results if r.config_type == "main_config"), None
        )

        if main_config_result:
            try:
                with open(main_config_result.file_path, "r") as f:
                    main_config = json.load(f)

                critical_paths = ["data_path", "models_path", "logs_path"]
                for path_field in critical_paths:
                    path = Path(main_config.get(path_field, ""))
                    if not path.exists():
                        main_config_result.warnings.append(
                            f"Ruta crítica no existe: {path}"
                        )

            except Exception as e:
                main_config_result.errors.append(f"Error validando rutas: {e}")
                main_config_result.is_valid = False

    def _validate_port_conflicts(self):
        """Valida conflictos de puertos"""
        main_config_result = next(
            (r for r in self.validation_results if r.config_type == "main_config"), None
        )

        if main_config_result:
            try:
                with open(main_config_result.file_path, "r") as f:
                    main_config = json.load(f)

                frontend_port = main_config.get("frontend_port")
                backend_port = main_config.get("backend_port")

                if frontend_port == backend_port:
                    main_config_result.errors.append(
                        "Los puertos frontend y backend no pueden ser iguales"
                    )
                    main_config_result.is_valid = False

            except Exception as e:
                main_config_result.errors.append(f"Error validando puertos: {e}")
                main_config_result.is_valid = False

    def _is_valid_solana_address(self, address: str) -> bool:
        """Valida si una dirección de Solana es válida"""
        if not address or len(address) != 44:
            return False

        # Verificar que solo contenga caracteres base58
        base58_chars = "123456789ABCDEFGHJKLMNPQRSTUVWXYZabcdefghijkmnopqrstuvwxyz"
        return all(c in base58_chars for c in address)

    def get_validation_summary(self) -> Dict[str, Any]:
        """Obtiene un resumen de todas las validaciones"""
        total_configs = len(self.validation_results)
        valid_configs = sum(1 for r in self.validation_results if r.is_valid)
        total_errors = sum(len(r.errors) for r in self.validation_results)
        total_warnings = sum(len(r.warnings) for r in self.validation_results)

        return {
            "total_configs": total_configs,
            "valid_configs": valid_configs,
            "invalid_configs": total_configs - valid_configs,
            "total_errors": total_errors,
            "total_warnings": total_warnings,
            "overall_valid": all(r.is_valid for r in self.validation_results),
            "results": [
                {
                    "config_type": r.config_type,
                    "file_path": r.file_path,
                    "is_valid": r.is_valid,
                    "error_count": len(r.errors),
                    "warning_count": len(r.warnings),
                }
                for r in self.validation_results
            ],
        }

    def print_validation_report(self):
        """Imprime un reporte detallado de validación"""
        summary = self.get_validation_summary()

        print("=" * 60)
        print("REPORTE DE VALIDACIÓN DE CONFIGURACIÓN")
        print("=" * 60)
        print(f"Configuraciones totales: {summary['total_configs']}")
        print(f"Configuraciones válidas: {summary['valid_configs']}")
        print(f"Configuraciones inválidas: {summary['invalid_configs']}")
        print(f"Errores totales: {summary['total_errors']}")
        print(f"Advertencias totales: {summary['total_warnings']}")
        print(f"Estado general: {'VÁLIDO' if summary['overall_valid'] else 'INVÁLIDO'}")
        print()

        for result in self.validation_results:
            print(f"📁 {result.config_type}")
            print(f"   Archivo: {result.file_path}")
            print(f"   Estado: {'✅ VÁLIDO' if result.is_valid else '❌ INVÁLIDO'}")

            if result.errors:
                print("   ❌ Errores:")
                for error in result.errors:
                    print(f"      - {error}")

            if result.warnings:
                print("   ⚠️  Advertencias:")
                for warning in result.warnings:
                    print(f"      - {warning}")

            print()


def main():
    """Función principal para ejecutar validaciones"""
    validator = ConfigValidator()
    results = validator.validate_all_configs()
    validator.print_validation_report()

    summary = validator.get_validation_summary()
    if not summary["overall_valid"]:
        print(
            "❌ Se encontraron errores de configuración. Por favor, corrígelos antes de continuar."
        )
        return False
    else:
        print("✅ Todas las configuraciones son válidas.")
        return True


if __name__ == "__main__":
    main()
