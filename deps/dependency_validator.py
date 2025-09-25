#!/usr/bin/env python3
"""
Validador de Dependencias del Sistema NeuroFusion
Verifica la compatibilidad y versiones de todas las dependencias del proyecto
"""

import json
import logging
import subprocess
import sys
import os
from pathlib import Path
from typing import Dict, Any, List, Optional, Union, Tuple
from dataclasses import dataclass, asdict
from datetime import datetime
import re
import pkg_resources
import importlib
from packaging import version

# Configuración de logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@dataclass
class DependencyValidationResult:
    """Resultado de validación de una dependencia"""

    package_name: str
    package_type: str
    required_version: str
    installed_version: Optional[str]
    is_installed: bool
    is_compatible: bool
    compatibility_issues: List[str]
    security_issues: List[str]
    performance_issues: List[str]
    recommendations: List[str]
    validation_score: float  # 0.0 a 1.0


@dataclass
class ValidationSummary:
    """Resumen de validación de dependencias"""

    total_dependencies: int
    valid_dependencies: int
    invalid_dependencies: int
    missing_dependencies: int
    outdated_dependencies: int
    security_vulnerabilities: int
    performance_issues: int
    overall_score: float
    critical_issues: List[str]
    warnings: List[str]
    recommendations: List[str]


class DependencyValidator:
    """Validador de dependencias del sistema NeuroFusion"""

    def __init__(self, deps_dir: str = "deps"):
        self.deps_dir = Path(deps_dir)
        self.validation_results = []
        self.compatibility_matrix = {}
        self.security_database = {}
        self.performance_benchmarks = {}

        # Cargar configuraciones de validación
        self._load_validation_configs()

    def _load_validation_configs(self):
        """Carga las configuraciones de validación"""
        # Matriz de compatibilidad entre dependencias
        self.compatibility_matrix = {
            "python": {
                "torch": {
                    "numpy": ">=1.21.0",
                    "python": ">=3.8",
                    "incompatible": ["tensorflow<2.0"],
                },
                "transformers": {
                    "torch": ">=1.9.0",
                    "numpy": ">=1.21.0",
                    "python": ">=3.8",
                },
                "sentence-transformers": {
                    "torch": ">=1.9.0",
                    "transformers": ">=4.20.0",
                    "numpy": ">=1.21.0",
                },
                "faiss-cpu": {"numpy": ">=1.21.0", "python": ">=3.8"},
                "fastapi": {"python": ">=3.7", "pydantic": ">=1.8.0"},
                "uvicorn": {"fastapi": ">=0.68.0", "python": ">=3.7"},
            },
            "node": {
                "react": {"node": ">=16.0", "npm": ">=8.0"},
                "next": {
                    "react": ">=18.0.0",
                    "react-dom": ">=18.0.0",
                    "node": ">=16.0",
                },
                "typescript": {"node": ">=16.0"},
            },
        }

        # Base de datos de vulnerabilidades de seguridad conocidas
        self.security_database = {
            "python": {
                "requests": {
                    "versions": ["<2.25.0"],
                    "severity": "high",
                    "description": "Vulnerabilidad de seguridad en versiones anteriores a 2.25.0",
                    "cve": "CVE-2021-33503",
                },
                "urllib3": {
                    "versions": ["<1.26.0"],
                    "severity": "medium",
                    "description": "Vulnerabilidad de seguridad en versiones anteriores a 1.26.0",
                    "cve": "CVE-2021-33503",
                },
            },
            "node": {
                "axios": {
                    "versions": ["<0.21.0"],
                    "severity": "medium",
                    "description": "Vulnerabilidad de seguridad en versiones anteriores a 0.21.0",
                    "cve": "CVE-2021-3749",
                }
            },
        }

        # Benchmarks de rendimiento
        self.performance_benchmarks = {
            "python": {
                "torch": {
                    "min_version": "1.9.0",
                    "recommended_version": "1.13.0",
                    "performance_improvements": [
                        "Mejor rendimiento en GPU",
                        "Optimizaciones de memoria",
                    ],
                },
                "transformers": {
                    "min_version": "4.20.0",
                    "recommended_version": "4.25.0",
                    "performance_improvements": [
                        "Inferencia más rápida",
                        "Menor uso de memoria",
                    ],
                },
            }
        }

    def validate_python_dependency(
        self, package_name: str, required_version: str
    ) -> DependencyValidationResult:
        """Valida una dependencia de Python"""
        try:
            # Verificar si está instalada
            try:
                if package_name == "sqlite3":
                    import sqlite3

                    installed_version = sqlite3.sqlite_version
                    is_installed = True
                else:
                    installed_version = pkg_resources.get_distribution(
                        package_name
                    ).version
                    is_installed = True
            except (pkg_resources.DistributionNotFound, ImportError):
                installed_version = None
                is_installed = False

            # Verificar compatibilidad de versiones
            is_compatible = True
            compatibility_issues = []
            security_issues = []
            performance_issues = []
            recommendations = []
            validation_score = 1.0

            if is_installed and installed_version:
                # Verificar versión requerida
                if not self._check_version_compatibility(
                    installed_version, required_version
                ):
                    is_compatible = False
                    compatibility_issues.append(
                        f"Versión instalada {installed_version} no cumple con requerimiento {required_version}"
                    )
                    validation_score -= 0.3

                # Verificar vulnerabilidades de seguridad
                security_issues.extend(
                    self._check_security_vulnerabilities(
                        "python", package_name, installed_version
                    )
                )
                if security_issues:
                    validation_score -= 0.4

                # Verificar problemas de rendimiento
                performance_issues.extend(
                    self._check_performance_issues(
                        "python", package_name, installed_version
                    )
                )
                if performance_issues:
                    validation_score -= 0.2

                # Generar recomendaciones
                recommendations.extend(
                    self._generate_recommendations(
                        "python", package_name, installed_version
                    )
                )

                # Verificar compatibilidad con otras dependencias
                if package_name in self.compatibility_matrix.get("python", {}):
                    dep_compatibility = self.compatibility_matrix["python"][
                        package_name
                    ]
                    for dep_name, dep_version in dep_compatibility.items():
                        if dep_name != "incompatible":
                            try:
                                if dep_name == "python":
                                    current_version = f"{sys.version_info.major}.{sys.version_info.minor}"
                                else:
                                    current_version = pkg_resources.get_distribution(
                                        dep_name
                                    ).version

                                if not self._check_version_compatibility(
                                    current_version, dep_version
                                ):
                                    compatibility_issues.append(
                                        f"Incompatible con {dep_name} {current_version}, requiere {dep_version}"
                                    )
                                    validation_score -= 0.2
                            except:
                                compatibility_issues.append(
                                    f"No se pudo verificar compatibilidad con {dep_name}"
                                )
                                validation_score -= 0.1
            else:
                validation_score = 0.0
                compatibility_issues.append("Dependencia no instalada")

            return DependencyValidationResult(
                package_name=package_name,
                package_type="python",
                required_version=required_version,
                installed_version=installed_version,
                is_installed=is_installed,
                is_compatible=is_compatible,
                compatibility_issues=compatibility_issues,
                security_issues=security_issues,
                performance_issues=performance_issues,
                recommendations=recommendations,
                validation_score=max(0.0, validation_score),
            )

        except Exception as e:
            logger.error(f"Error validando dependencia Python {package_name}: {e}")
            return DependencyValidationResult(
                package_name=package_name,
                package_type="python",
                required_version=required_version,
                installed_version=None,
                is_installed=False,
                is_compatible=False,
                compatibility_issues=[f"Error en validación: {str(e)}"],
                security_issues=[],
                performance_issues=[],
                recommendations=[],
                validation_score=0.0,
            )

    def validate_node_dependency(
        self, package_name: str, required_version: str
    ) -> DependencyValidationResult:
        """Valida una dependencia de Node.js"""
        try:
            # Verificar si está instalada
            try:
                result = subprocess.run(
                    ["npm", "list", package_name],
                    capture_output=True,
                    text=True,
                    cwd=self.deps_dir,
                )
                if result.returncode == 0:
                    # Extraer versión del output
                    lines = result.stdout.split("\n")
                    for line in lines:
                        if package_name in line and "@" in line:
                            installed_version = line.split("@")[1].split(" ")[0]
                            break
                    else:
                        installed_version = None
                    is_installed = True
                else:
                    installed_version = None
                    is_installed = False
            except Exception:
                installed_version = None
                is_installed = False

            # Verificar compatibilidad de versiones
            is_compatible = True
            compatibility_issues = []
            security_issues = []
            performance_issues = []
            recommendations = []
            validation_score = 1.0

            if is_installed and installed_version:
                # Verificar versión requerida
                if not self._check_version_compatibility(
                    installed_version, required_version
                ):
                    is_compatible = False
                    compatibility_issues.append(
                        f"Versión instalada {installed_version} no cumple con requerimiento {required_version}"
                    )
                    validation_score -= 0.3

                # Verificar vulnerabilidades de seguridad
                security_issues.extend(
                    self._check_security_vulnerabilities(
                        "node", package_name, installed_version
                    )
                )
                if security_issues:
                    validation_score -= 0.4

                # Verificar problemas de rendimiento
                performance_issues.extend(
                    self._check_performance_issues(
                        "node", package_name, installed_version
                    )
                )
                if performance_issues:
                    validation_score -= 0.2

                # Generar recomendaciones
                recommendations.extend(
                    self._generate_recommendations(
                        "node", package_name, installed_version
                    )
                )

                # Verificar compatibilidad con otras dependencias
                if package_name in self.compatibility_matrix.get("node", {}):
                    dep_compatibility = self.compatibility_matrix["node"][package_name]
                    for dep_name, dep_version in dep_compatibility.items():
                        try:
                            # Verificar versión de Node.js
                            if dep_name == "node":
                                result = subprocess.run(
                                    ["node", "--version"],
                                    capture_output=True,
                                    text=True,
                                )
                                if result.returncode == 0:
                                    current_version = result.stdout.strip().lstrip("v")
                                    if not self._check_version_compatibility(
                                        current_version, dep_version
                                    ):
                                        compatibility_issues.append(
                                            f"Incompatible con Node.js {current_version}, requiere {dep_version}"
                                        )
                                        validation_score -= 0.2
                            elif dep_name == "npm":
                                result = subprocess.run(
                                    ["npm", "--version"], capture_output=True, text=True
                                )
                                if result.returncode == 0:
                                    current_version = result.stdout.strip()
                                    if not self._check_version_compatibility(
                                        current_version, dep_version
                                    ):
                                        compatibility_issues.append(
                                            f"Incompatible con npm {current_version}, requiere {dep_version}"
                                        )
                                        validation_score -= 0.2
                        except:
                            compatibility_issues.append(
                                f"No se pudo verificar compatibilidad con {dep_name}"
                            )
                            validation_score -= 0.1
            else:
                validation_score = 0.0
                compatibility_issues.append("Dependencia no instalada")

            return DependencyValidationResult(
                package_name=package_name,
                package_type="node",
                required_version=required_version,
                installed_version=installed_version,
                is_installed=is_installed,
                is_compatible=is_compatible,
                compatibility_issues=compatibility_issues,
                security_issues=security_issues,
                performance_issues=performance_issues,
                recommendations=recommendations,
                validation_score=max(0.0, validation_score),
            )

        except Exception as e:
            logger.error(f"Error validando dependencia Node.js {package_name}: {e}")
            return DependencyValidationResult(
                package_name=package_name,
                package_type="node",
                required_version=required_version,
                installed_version=None,
                is_installed=False,
                is_compatible=False,
                compatibility_issues=[f"Error en validación: {str(e)}"],
                security_issues=[],
                performance_issues=[],
                recommendations=[],
                validation_score=0.0,
            )

    def validate_system_dependency(
        self, package_name: str, required_version: str
    ) -> DependencyValidationResult:
        """Valida una dependencia del sistema"""
        try:
            # Verificar si está instalada
            try:
                result = subprocess.run(
                    [package_name, "--version"], capture_output=True, text=True
                )
                if result.returncode == 0:
                    installed_version = result.stdout.strip()
                    is_installed = True
                else:
                    installed_version = None
                    is_installed = False
            except FileNotFoundError:
                installed_version = None
                is_installed = False

            # Verificar compatibilidad de versiones
            is_compatible = True
            compatibility_issues = []
            security_issues = []
            performance_issues = []
            recommendations = []
            validation_score = 1.0

            if is_installed and installed_version:
                # Verificar versión requerida
                if not self._check_version_compatibility(
                    installed_version, required_version
                ):
                    is_compatible = False
                    compatibility_issues.append(
                        f"Versión instalada {installed_version} no cumple con requerimiento {required_version}"
                    )
                    validation_score -= 0.3

                # Generar recomendaciones
                recommendations.extend(
                    self._generate_recommendations(
                        "system", package_name, installed_version
                    )
                )
            else:
                validation_score = 0.0
                compatibility_issues.append("Dependencia del sistema no instalada")

            return DependencyValidationResult(
                package_name=package_name,
                package_type="system",
                required_version=required_version,
                installed_version=installed_version,
                is_installed=is_installed,
                is_compatible=is_compatible,
                compatibility_issues=compatibility_issues,
                security_issues=security_issues,
                performance_issues=performance_issues,
                recommendations=recommendations,
                validation_score=max(0.0, validation_score),
            )

        except Exception as e:
            logger.error(f"Error validando dependencia del sistema {package_name}: {e}")
            return DependencyValidationResult(
                package_name=package_name,
                package_type="system",
                required_version=required_version,
                installed_version=None,
                is_installed=False,
                is_compatible=False,
                compatibility_issues=[f"Error en validación: {str(e)}"],
                security_issues=[],
                performance_issues=[],
                recommendations=[],
                validation_score=0.0,
            )

    def validate_all_dependencies(
        self, dependencies_config: Dict[str, Any]
    ) -> List[DependencyValidationResult]:
        """Valida todas las dependencias según la configuración"""
        results = []

        # Validar dependencias de Python
        logger.info("Validando dependencias de Python...")
        for package_name, config in dependencies_config.get(
            "python_dependencies", {}
        ).items():
            result = self.validate_python_dependency(
                package_name, config.get("version", "unknown")
            )
            results.append(result)

        # Validar dependencias de Node.js
        logger.info("Validando dependencias de Node.js...")
        for package_name, config in dependencies_config.get(
            "node_dependencies", {}
        ).items():
            result = self.validate_node_dependency(
                package_name, config.get("version", "unknown")
            )
            results.append(result)

        # Validar dependencias del sistema
        logger.info("Validando dependencias del sistema...")
        for package_name, config in dependencies_config.get(
            "system_dependencies", {}
        ).items():
            result = self.validate_system_dependency(
                package_name, config.get("version", "unknown")
            )
            results.append(result)

        self.validation_results = results
        return results

    def _check_version_compatibility(
        self, installed_version: str, required_version: str
    ) -> bool:
        """Verifica la compatibilidad de versiones"""
        try:
            # Limpiar versiones
            installed_clean = re.sub(r"[^\d.]", "", installed_version)
            required_clean = (
                required_version.replace(">=", "")
                .replace("<=", "")
                .replace("==", "")
                .replace("~", "")
                .replace("^", "")
            )

            # Parsear versiones
            installed_ver = version.parse(installed_clean)
            required_ver = version.parse(required_clean)

            # Verificar compatibilidad según el operador
            if ">=" in required_version:
                return installed_ver >= required_ver
            elif "<=" in required_version:
                return installed_ver <= required_ver
            elif "==" in required_version:
                return installed_ver == required_ver
            elif "~" in required_version:
                # Compatible release (~=)
                return installed_ver >= required_ver and installed_ver < version.parse(
                    f"{required_ver.major}.{required_ver.minor + 1}"
                )
            elif "^" in required_version:
                # Caret requirement (^)
                return installed_ver >= required_ver and installed_ver < version.parse(
                    f"{required_ver.major + 1}"
                )
            else:
                # Sin operador, asumir >=
                return installed_ver >= required_ver

        except Exception as e:
            logger.warning(f"Error verificando compatibilidad de versiones: {e}")
            return False

    def _check_security_vulnerabilities(
        self, package_type: str, package_name: str, installed_version: str
    ) -> List[str]:
        """Verifica vulnerabilidades de seguridad conocidas"""
        vulnerabilities = []

        try:
            if (
                package_type in self.security_database
                and package_name in self.security_database[package_type]
            ):
                security_info = self.security_database[package_type][package_name]

                for vuln_version in security_info["versions"]:
                    if self._check_version_compatibility(
                        installed_version, vuln_version
                    ):
                        vulnerabilities.append(
                            f"{security_info['severity'].upper()}: {security_info['description']} ({security_info['cve']})"
                        )

        except Exception as e:
            logger.warning(f"Error verificando vulnerabilidades de seguridad: {e}")

        return vulnerabilities

    def _check_performance_issues(
        self, package_type: str, package_name: str, installed_version: str
    ) -> List[str]:
        """Verifica problemas de rendimiento conocidos"""
        issues = []

        try:
            if (
                package_type in self.performance_benchmarks
                and package_name in self.performance_benchmarks[package_type]
            ):
                perf_info = self.performance_benchmarks[package_type][package_name]

                if not self._check_version_compatibility(
                    installed_version, perf_info["min_version"]
                ):
                    issues.append(
                        f"Versión {installed_version} puede tener problemas de rendimiento. Recomendado: {perf_info['recommended_version']}"
                    )

                if "performance_improvements" in perf_info:
                    for improvement in perf_info["performance_improvements"]:
                        issues.append(f"Mejora disponible: {improvement}")

        except Exception as e:
            logger.warning(f"Error verificando problemas de rendimiento: {e}")

        return issues

    def _generate_recommendations(
        self, package_type: str, package_name: str, installed_version: str
    ) -> List[str]:
        """Genera recomendaciones para la dependencia"""
        recommendations = []

        try:
            # Recomendaciones específicas por paquete
            if package_type == "python":
                if package_name == "torch" and installed_version:
                    if version.parse(installed_version) < version.parse("1.13.0"):
                        recommendations.append(
                            "Actualizar PyTorch a la versión 1.13.0+ para mejor rendimiento"
                        )

                elif package_name == "transformers" and installed_version:
                    if version.parse(installed_version) < version.parse("4.25.0"):
                        recommendations.append(
                            "Actualizar Transformers a la versión 4.25.0+ para mejor rendimiento"
                        )

                elif package_name == "numpy" and installed_version:
                    if version.parse(installed_version) < version.parse("1.24.0"):
                        recommendations.append(
                            "Actualizar NumPy a la versión 1.24.0+ para mejor compatibilidad"
                        )

            elif package_type == "node":
                if package_name == "react" and installed_version:
                    if version.parse(installed_version) < version.parse("18.2.0"):
                        recommendations.append(
                            "Actualizar React a la versión 18.2.0+ para mejor rendimiento"
                        )

                elif package_name == "next" and installed_version:
                    if version.parse(installed_version) < version.parse("13.0.0"):
                        recommendations.append(
                            "Actualizar Next.js a la versión 13.0.0+ para nuevas características"
                        )

            # Recomendaciones generales
            if (
                package_type in self.performance_benchmarks
                and package_name in self.performance_benchmarks[package_type]
            ):
                perf_info = self.performance_benchmarks[package_type][package_name]
                if "recommended_version" in perf_info:
                    recommendations.append(
                        f"Considerar actualizar a {perf_info['recommended_version']} para mejor rendimiento"
                    )

        except Exception as e:
            logger.warning(f"Error generando recomendaciones: {e}")

        return recommendations

    def get_validation_summary(self) -> ValidationSummary:
        """Obtiene un resumen de la validación"""
        if not self.validation_results:
            return ValidationSummary(0, 0, 0, 0, 0, 0, 0, 0.0, [], [], [])

        total_deps = len(self.validation_results)
        valid_deps = len([r for r in self.validation_results if r.is_compatible])
        invalid_deps = len([r for r in self.validation_results if not r.is_compatible])
        missing_deps = len([r for r in self.validation_results if not r.is_installed])
        outdated_deps = len(
            [
                r
                for r in self.validation_results
                if r.is_installed and not r.is_compatible
            ]
        )

        security_vulns = sum(len(r.security_issues) for r in self.validation_results)
        perf_issues = sum(len(r.performance_issues) for r in self.validation_results)

        overall_score = (
            sum(r.validation_score for r in self.validation_results) / total_deps
        )

        # Recopilar problemas críticos y advertencias
        critical_issues = []
        warnings = []
        recommendations = []

        for result in self.validation_results:
            if not result.is_installed:
                critical_issues.append(f"Dependencia faltante: {result.package_name}")

            if result.security_issues:
                critical_issues.extend(result.security_issues)

            if result.compatibility_issues:
                warnings.extend(result.compatibility_issues)

            if result.performance_issues:
                warnings.extend(result.performance_issues)

            if result.recommendations:
                recommendations.extend(result.recommendations)

        return ValidationSummary(
            total_dependencies=total_deps,
            valid_dependencies=valid_deps,
            invalid_dependencies=invalid_deps,
            missing_dependencies=missing_deps,
            outdated_dependencies=outdated_deps,
            security_vulnerabilities=security_vulns,
            performance_issues=perf_issues,
            overall_score=overall_score,
            critical_issues=critical_issues,
            warnings=warnings,
            recommendations=recommendations,
        )

    def save_validation_report(self, filepath: str = None) -> str:
        """Guarda un reporte de validación"""
        if filepath is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filepath = (
                self.deps_dir
                / "validation_reports"
                / f"validation_report_{timestamp}.json"
            )

        filepath = Path(filepath)
        filepath.parent.mkdir(parents=True, exist_ok=True)

        summary = self.get_validation_summary()

        report_data = {
            "validation_summary": asdict(summary),
            "validation_results": [
                asdict(result) for result in self.validation_results
            ],
            "timestamp": datetime.now().isoformat(),
            "validator_version": "1.0.0",
        }

        with open(filepath, "w") as f:
            json.dump(report_data, f, indent=2)

        logger.info(f"Reporte de validación guardado: {filepath}")
        return str(filepath)

    def print_validation_report(self):
        """Imprime un reporte de validación en consola"""
        summary = self.get_validation_summary()

        print("\n" + "=" * 80)
        print("REPORTE DE VALIDACIÓN DE DEPENDENCIAS")
        print("=" * 80)

        print(f"\n📊 RESUMEN GENERAL:")
        print(f"   Total de dependencias: {summary.total_dependencies}")
        print(f"   Dependencias válidas: {summary.valid_dependencies}")
        print(f"   Dependencias inválidas: {summary.invalid_dependencies}")
        print(f"   Dependencias faltantes: {summary.missing_dependencies}")
        print(f"   Dependencias desactualizadas: {summary.outdated_dependencies}")
        print(f"   Vulnerabilidades de seguridad: {summary.security_vulnerabilities}")
        print(f"   Problemas de rendimiento: {summary.performance_issues}")
        print(f"   Puntuación general: {summary.overall_score:.2f}/1.00")

        if summary.critical_issues:
            print(f"\n🚨 PROBLEMAS CRÍTICOS:")
            for issue in summary.critical_issues:
                print(f"   • {issue}")

        if summary.warnings:
            print(f"\n⚠️  ADVERTENCIAS:")
            for warning in summary.warnings:
                print(f"   • {warning}")

        if summary.recommendations:
            print(f"\n💡 RECOMENDACIONES:")
            for rec in summary.recommendations:
                print(f"   • {rec}")

        print(f"\n📋 DETALLES POR DEPENDENCIA:")
        for result in self.validation_results:
            status = "✅" if result.is_compatible else "❌"
            print(f"   {status} {result.package_name} ({result.package_type})")
            print(f"      Versión requerida: {result.required_version}")
            print(
                f"      Versión instalada: {result.installed_version or 'No instalada'}"
            )
            print(f"      Puntuación: {result.validation_score:.2f}/1.00")

            if result.compatibility_issues:
                for issue in result.compatibility_issues:
                    print(f"      ⚠️  {issue}")

            if result.security_issues:
                for issue in result.security_issues:
                    print(f"      🔒 {issue}")

            if result.performance_issues:
                for issue in result.performance_issues:
                    print(f"      ⚡ {issue}")

        print("\n" + "=" * 80)


# Instancia global del validador
dependency_validator = DependencyValidator()


def get_dependency_validator() -> DependencyValidator:
    """Obtiene la instancia global del validador de dependencias"""
    return dependency_validator


if __name__ == "__main__":
    # Ejemplo de uso
    validator = DependencyValidator()

    # Configuración de dependencias de ejemplo
    dependencies_config = {
        "python_dependencies": {
            "requests": {"version": ">=2.25.0", "required": True},
            "numpy": {"version": ">=1.21.0", "required": True},
            "torch": {"version": ">=1.9.0", "required": True},
        },
        "node_dependencies": {
            "react": {"version": "^18.0.0", "required": True},
            "axios": {"version": "^0.27.0", "required": True},
        },
        "system_dependencies": {
            "python3": {"version": ">=3.8", "required": True},
            "node": {"version": ">=16.0", "required": True},
        },
    }

    # Validar dependencias
    results = validator.validate_all_dependencies(dependencies_config)

    # Mostrar reporte
    validator.print_validation_report()

    # Guardar reporte
    validator.save_validation_report()
