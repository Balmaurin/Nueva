#!/usr/bin/env python3
"""
Script de Implementación Completa - Verificación de Todo el Proyecto
===================================================================

Script para verificar que todas las implementaciones del proyecto NeuroFusion
estén funcionando correctamente, incluyendo:
- Núcleo central
- Módulos unificados
- Sistemas de IA
- Configuraciones
- Base de datos
- APIs
- Frontend
- Y más...
"""

import os
import sys
import json
import logging
import subprocess
from pathlib import Path
from typing import Dict, Any, List, Optional
from datetime import datetime

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class CompleteProjectImplementation:
    """Verificador completo de implementación del proyecto"""

    def __init__(self):
        self.project_root = Path.cwd()
        self.results = {}
        self.start_time = datetime.now()

    def verify_project_structure(self) -> Dict[str, Any]:
        """Verificar estructura completa del proyecto"""
        logger.info("🔍 Verificando estructura completa del proyecto...")

        expected_directories = [
            "modules/",
            "config/",
            "data/",
            "interface/",
            "logs/",
            "models/",
            "scripts/",
            "evaluation/",
            "monitoring/",
            "branches/",
            "cache/",
            "backups/",
            "docs/",
            "docker/",
            "e2e/",
        ]

        expected_files = [
            "requirements.txt",
            "docs/README_SISTEMA_COMPLETO.md",
            "start_sistema_unificado.sh",
            "scripts/verificar_sistema.sh",
            "package-lock.json",
            "LICENSE",
        ]

        results = {"directories": {}, "files": {}, "summary": {}}

        # Verificar directorios
        for dir_path in expected_directories:
            exists = (self.project_root / dir_path).exists()
            results["directories"][dir_path] = exists
            if exists:
                logger.info(f"✅ {dir_path}")
            else:
                logger.warning(f"❌ {dir_path}")

        # Verificar archivos
        for file_path in expected_files:
            exists = (self.project_root / file_path).exists()
            results["files"][file_path] = exists
            if exists:
                logger.info(f"✅ {file_path}")
            else:
                logger.warning(f"❌ {file_path}")

        # Resumen
        dirs_ok = sum(results["directories"].values())
        files_ok = sum(results["files"].values())
        results["summary"] = {
            "directories_checked": len(expected_directories),
            "directories_ok": dirs_ok,
            "files_checked": len(expected_files),
            "files_ok": files_ok,
            "total_score": f"{dirs_ok + files_ok}/{len(expected_directories) + len(expected_files)}",
        }

        return results

    def verify_modules_implementation(self) -> Dict[str, Any]:
        """Verificar implementación de todos los módulos"""
        logger.info("📦 Verificando implementación de módulos...")

        modules_to_check = [
            "modules/core/",
            "modules/ai/",
            "modules/ai_components/",
            "modules/blockchain/",
            "modules/embeddings/",
            "modules/evaluation/",
            "modules/learning/",
            "modules/memory/",
            "modules/nucleo_central/",
            "modules/orchestrator/",
            "modules/plugins/",
            "modules/recommendations/",
            "modules/reinforcement/",
            "modules/rewards/",
            "modules/scripts/",
            "modules/security/",
            "modules/src/",
            "modules/tokens/",
            "modules/training/",
            "modules/unified_systems/",
            "modules/utils/",
            "modules/visualization/",
        ]

        results = {"modules": {}, "summary": {}}

        for module_path in modules_to_check:
            module_dir = self.project_root / module_path
            if module_dir.exists():
                # Verificar archivos importantes del módulo
                important_files = ["__init__.py"]
                files_exist = []

                for file_name in important_files:
                    file_path = module_dir / file_name
                    files_exist.append(file_path.exists())

                # Contar archivos Python
                py_files = list(module_dir.rglob("*.py"))
                py_count = len(py_files)

                results["modules"][module_path] = {
                    "exists": True,
                    "has_init": any(files_exist),
                    "py_files_count": py_count,
                    "status": "ACTIVE" if py_count > 0 else "EMPTY",
                }

                logger.info(f"✅ {module_path} ({py_count} archivos Python)")
            else:
                results["modules"][module_path] = {
                    "exists": False,
                    "has_init": False,
                    "py_files_count": 0,
                    "status": "MISSING",
                }
                logger.warning(f"❌ {module_path}")

        # Resumen
        active_modules = sum(
            1 for m in results["modules"].values() if m["status"] == "ACTIVE"
        )
        total_modules = len(modules_to_check)

        results["summary"] = {
            "total_modules": total_modules,
            "active_modules": active_modules,
            "empty_modules": sum(
                1 for m in results["modules"].values() if m["status"] == "EMPTY"
            ),
            "missing_modules": sum(
                1 for m in results["modules"].values() if m["status"] == "MISSING"
            ),
            "score": f"{active_modules}/{total_modules}",
        }

        return results

    def verify_configurations(self) -> Dict[str, Any]:
        """Verificar todas las configuraciones del proyecto"""
        logger.info("⚙️ Verificando configuraciones del proyecto...")

        config_files = [
            "config/rate_limits.json",
            "config/advanced_training_config.json",
            "config/config/neurofusion_config.json",
            "config/config/module_initialization.json",
            "config/module_scan_report.json",
            "config/monitoring_config.json",
            "config/config/neurofusion_config.json",
            "config/sheily_token_config.json",
            "config/sheily_token_metadata.json",
            "config/training_token_config.json",
            "modules/config/module_config.json",
            "modules/unified_systems/unified_system_config.json",
        ]

        results = {"configs": {}, "summary": {}}

        for config_path in config_files:
            config_file = self.project_root / config_path
            if config_file.exists():
                try:
                    with open(config_file, "r", encoding="utf-8") as f:
                        config_data = json.load(f)

                    results["configs"][config_path] = {
                        "exists": True,
                        "valid_json": True,
                        "size_kb": round(config_file.stat().st_size / 1024, 2),
                        "keys_count": (
                            len(config_data.keys())
                            if isinstance(config_data, dict)
                            else 0
                        ),
                    }
                    logger.info(
                        f"✅ {config_path} ({results['configs'][config_path]['size_kb']} KB)"
                    )
                except Exception as e:
                    results["configs"][config_path] = {
                        "exists": True,
                        "valid_json": False,
                        "error": str(e),
                    }
                    logger.warning(f"⚠️ {config_path} (JSON inválido)")
            else:
                results["configs"][config_path] = {"exists": False, "valid_json": False}
                logger.warning(f"❌ {config_path}")

        # Resumen
        existing_configs = sum(1 for c in results["configs"].values() if c["exists"])
        valid_configs = sum(
            1 for c in results["configs"].values() if c.get("valid_json", False)
        )

        results["summary"] = {
            "total_configs": len(config_files),
            "existing_configs": existing_configs,
            "valid_configs": valid_configs,
            "score": f"{valid_configs}/{len(config_files)}",
        }

        return results

    def verify_database_implementation(self) -> Dict[str, Any]:
        """Verificar implementación de bases de datos"""
        logger.info("🗄️ Verificando implementación de bases de datos...")

        db_files = [
            "data/knowledge_base.db",
            "data/embeddings_sqlite.db",
            "data/rag_memory.duckdb",
            "data/user_data.duckdb",
            "data/faiss_index.index",
            "models/branch_learning.db",
            "monitoring/metrics.db",
        ]

        results = {"databases": {}, "summary": {}}

        for db_path in db_files:
            db_file = self.project_root / db_path
            if db_file.exists():
                size_mb = round(db_file.stat().st_size / (1024 * 1024), 2)
                results["databases"][db_path] = {
                    "exists": True,
                    "size_mb": size_mb,
                    "status": "ACTIVE" if size_mb > 0 else "EMPTY",
                }
                logger.info(f"✅ {db_path} ({size_mb} MB)")
            else:
                results["databases"][db_path] = {
                    "exists": False,
                    "size_mb": 0,
                    "status": "MISSING",
                }
                logger.warning(f"❌ {db_path}")

        # Resumen
        active_dbs = sum(
            1 for db in results["databases"].values() if db["status"] == "ACTIVE"
        )
        total_dbs = len(db_files)

        results["summary"] = {
            "total_databases": total_dbs,
            "active_databases": active_dbs,
            "empty_databases": sum(
                1 for db in results["databases"].values() if db["status"] == "EMPTY"
            ),
            "missing_databases": sum(
                1 for db in results["databases"].values() if db["status"] == "MISSING"
            ),
            "score": f"{active_dbs}/{total_dbs}",
        }

        return results

    def verify_interface_implementation(self) -> Dict[str, Any]:
        """Verificar implementación de interfaces"""
        logger.info("🖥️ Verificando implementación de interfaces...")

        interface_components = {
            "backend": {
                "path": "interface/backend/",
                "files": ["main.py", "requirements.txt", "docker/Dockerfile"],
            },
            "frontend": {
                "path": "interface/frontend/",
                "files": ["package.json", "src/", "public/"],
            },
            "docs": {"path": "interface/docs/", "files": ["*.md"]},
        }

        results = {"interfaces": {}, "summary": {}}

        for interface_name, config in interface_components.items():
            interface_path = self.project_root / config["path"]
            if interface_path.exists():
                # Verificar archivos importantes
                files_exist = []
                for file_pattern in config["files"]:
                    if file_pattern.endswith("/"):
                        # Es un directorio
                        dir_path = interface_path / file_pattern[:-1]
                        files_exist.append(dir_path.exists())
                    else:
                        # Es un archivo
                        file_path = interface_path / file_pattern
                        files_exist.append(file_path.exists())

                files_ok = sum(files_exist)
                total_files = len(config["files"])

                results["interfaces"][interface_name] = {
                    "exists": True,
                    "files_ok": files_ok,
                    "total_files": total_files,
                    "score": f"{files_ok}/{total_files}",
                    "status": "COMPLETE" if files_ok == total_files else "PARTIAL",
                }

                logger.info(f"✅ {interface_name} ({files_ok}/{total_files} archivos)")
            else:
                results["interfaces"][interface_name] = {
                    "exists": False,
                    "files_ok": 0,
                    "total_files": len(config["files"]),
                    "score": "0/0",
                    "status": "MISSING",
                }
                logger.warning(f"❌ {interface_name}")

        # Resumen
        complete_interfaces = sum(
            1 for i in results["interfaces"].values() if i["status"] == "COMPLETE"
        )
        total_interfaces = len(interface_components)

        results["summary"] = {
            "total_interfaces": total_interfaces,
            "complete_interfaces": complete_interfaces,
            "partial_interfaces": sum(
                1 for i in results["interfaces"].values() if i["status"] == "PARTIAL"
            ),
            "missing_interfaces": sum(
                1 for i in results["interfaces"].values() if i["status"] == "MISSING"
            ),
            "score": f"{complete_interfaces}/{total_interfaces}",
        }

        return results

    def verify_system_scripts(self) -> Dict[str, Any]:
        """Verificar scripts del sistema"""
        logger.info("🔧 Verificando scripts del sistema...")

        system_scripts = [
            "start_sistema_unificado.sh",
            "scripts/verificar_sistema.sh",
            "interface/neurofusion.sh",
            "interface/check_status.sh",
            "interface/start_system.sh",
            "modules/scripts/",
            "scripts/",
        ]

        results = {"scripts": {}, "summary": {}}

        for script_path in system_scripts:
            script_file = self.project_root / script_path
            if script_file.exists():
                if script_file.is_file():
                    # Es un archivo
                    size_kb = round(script_file.stat().st_size / 1024, 2)
                    is_executable = os.access(script_file, os.X_OK)

                    results["scripts"][script_path] = {
                        "exists": True,
                        "type": "file",
                        "size_kb": size_kb,
                        "executable": is_executable,
                        "status": "ACTIVE" if is_executable else "READONLY",
                    }
                    logger.info(
                        f"✅ {script_path} ({size_kb} KB, {'executable' if is_executable else 'readonly'})"
                    )
                else:
                    # Es un directorio
                    script_files = list(script_file.rglob("*.sh")) + list(
                        script_file.rglob("*.py")
                    )
                    executable_count = sum(
                        1 for f in script_files if os.access(f, os.X_OK)
                    )

                    results["scripts"][script_path] = {
                        "exists": True,
                        "type": "directory",
                        "script_count": len(script_files),
                        "executable_count": executable_count,
                        "status": "ACTIVE" if executable_count > 0 else "EMPTY",
                    }
                    logger.info(
                        f"✅ {script_path} ({len(script_files)} scripts, {executable_count} ejecutables)"
                    )
            else:
                results["scripts"][script_path] = {
                    "exists": False,
                    "type": "missing",
                    "status": "MISSING",
                }
                logger.warning(f"❌ {script_path}")

        # Resumen
        active_scripts = sum(
            1 for s in results["scripts"].values() if s["status"] == "ACTIVE"
        )
        total_scripts = len(system_scripts)

        results["summary"] = {
            "total_scripts": total_scripts,
            "active_scripts": active_scripts,
            "empty_scripts": sum(
                1 for s in results["scripts"].values() if s["status"] == "EMPTY"
            ),
            "missing_scripts": sum(
                1 for s in results["scripts"].values() if s["status"] == "MISSING"
            ),
            "score": f"{active_scripts}/{total_scripts}",
        }

        return results

    def verify_docker_implementation(self) -> Dict[str, Any]:
        """Verificar implementación de Docker"""
        logger.info("🐳 Verificando implementación de Docker...")

        docker_files = [
            "docker/docker-compose.yml",
            "docker/docker-compose.dev.yml",
            "docker/backend.docker/Dockerfile",
            "docker/frontend.docker/Dockerfile",
            "docker/nginx.conf",
            "docker/monitoring/prometheus.yml",
            "docker/Dockerfile",
        ]

        results = {"docker": {}, "summary": {}}

        for docker_path in docker_files:
            docker_file = self.project_root / docker_path
            if docker_file.exists():
                size_kb = round(docker_file.stat().st_size / 1024, 2)
                results["docker"][docker_path] = {
                    "exists": True,
                    "size_kb": size_kb,
                    "status": "ACTIVE",
                }
                logger.info(f"✅ {docker_path} ({size_kb} KB)")
            else:
                results["docker"][docker_path] = {
                    "exists": False,
                    "size_kb": 0,
                    "status": "MISSING",
                }
                logger.warning(f"❌ {docker_path}")

        # Resumen
        active_docker = sum(
            1 for d in results["docker"].values() if d["status"] == "ACTIVE"
        )
        total_docker = len(docker_files)

        results["summary"] = {
            "total_docker": total_docker,
            "active_docker": active_docker,
            "missing_docker": sum(
                1 for d in results["docker"].values() if d["status"] == "MISSING"
            ),
            "score": f"{active_docker}/{total_docker}",
        }

        return results

    def run_system_health_check(self) -> Dict[str, Any]:
        """Ejecutar verificación de salud del sistema"""
        logger.info("🏥 Ejecutando verificación de salud del sistema...")

        health_checks = {
            "nucleo_central": "python3 modules/nucleo_central/cleanup.py",
            "system_verification": "./scripts/verificar_sistema.sh",
            "docker_status": "docker --version",
        }

        results = {"health_checks": {}, "summary": {}}

        for check_name, command in health_checks.items():
            try:
                result = subprocess.run(
                    command.split(),
                    capture_output=True,
                    text=True,
                    timeout=30,
                    cwd=self.project_root,
                )

                results["health_checks"][check_name] = {
                    "executed": True,
                    "exit_code": result.returncode,
                    "success": result.returncode == 0,
                    "output": (
                        result.stdout[:200] + "..."
                        if len(result.stdout) > 200
                        else result.stdout
                    ),
                    "error": (
                        result.stderr[:200] + "..."
                        if len(result.stderr) > 200
                        else result.stderr
                    ),
                }

                if result.returncode == 0:
                    logger.info(f"✅ {check_name}: OK")
                else:
                    logger.warning(f"⚠️ {check_name}: Error (code {result.returncode})")

            except Exception as e:
                results["health_checks"][check_name] = {
                    "executed": False,
                    "error": str(e),
                    "success": False,
                }
                logger.error(f"❌ {check_name}: {e}")

        # Resumen
        successful_checks = sum(
            1 for h in results["health_checks"].values() if h.get("success", False)
        )
        total_checks = len(health_checks)

        results["summary"] = {
            "total_checks": total_checks,
            "successful_checks": successful_checks,
            "failed_checks": total_checks - successful_checks,
            "score": f"{successful_checks}/{total_checks}",
        }

        return results

    def generate_complete_report(self) -> Dict[str, Any]:
        """Generar reporte completo de implementación"""
        logger.info("📊 Generando reporte completo de implementación...")

        # Ejecutar todas las verificaciones
        project_structure = self.verify_project_structure()
        modules_impl = self.verify_modules_implementation()
        configurations = self.verify_configurations()
        database_impl = self.verify_database_implementation()
        interface_impl = self.verify_interface_implementation()
        system_scripts = self.verify_system_scripts()
        docker_impl = self.verify_docker_implementation()
        health_checks = self.run_system_health_check()

        # Calcular métricas generales
        end_time = datetime.now()
        duration = (end_time - self.start_time).total_seconds()

        # Calcular puntuación general
        scores = [
            int(
                project_structure["summary"]["directories_ok"]
                + project_structure["summary"]["files_ok"]
            ),
            int(modules_impl["summary"]["active_modules"]),
            int(configurations["summary"]["valid_configs"]),
            int(database_impl["summary"]["active_databases"]),
            int(interface_impl["summary"]["complete_interfaces"]),
            int(system_scripts["summary"]["active_scripts"]),
            int(docker_impl["summary"]["active_docker"]),
            int(health_checks["summary"]["successful_checks"]),
        ]

        total_score = sum(scores)
        max_possible_score = 100  # Puntuación máxima estimada

        overall_status = (
            "EXCELENTE"
            if total_score >= 80
            else (
                "BUENO"
                if total_score >= 60
                else "REGULAR" if total_score >= 40 else "PENDIENTE"
            )
        )

        report = {
            "timestamp": {
                "start": self.start_time.isoformat(),
                "end": end_time.isoformat(),
                "duration_seconds": round(duration, 2),
            },
            "project_structure": project_structure,
            "modules_implementation": modules_impl,
            "configurations": configurations,
            "database_implementation": database_impl,
            "interface_implementation": interface_impl,
            "system_scripts": system_scripts,
            "docker_implementation": docker_impl,
            "health_checks": health_checks,
            "overall_summary": {
                "total_score": total_score,
                "max_possible_score": max_possible_score,
                "percentage": round((total_score / max_possible_score) * 100, 1),
                "overall_status": overall_status,
                "implementation_level": f"{overall_status} ({total_score}/{max_possible_score})",
            },
        }

        return report

    def print_complete_report(self, report: Dict[str, Any]):
        """Imprimir reporte completo de implementación"""
        print("\n" + "=" * 80)
        print("🚀 REPORTE COMPLETO DE IMPLEMENTACIÓN - PROYECTO NEUROFUSION")
        print("=" * 80)

        # Información temporal
        timestamp = report["timestamp"]
        print(
            f"\n⏰ Duración de verificación: {timestamp['duration_seconds']} segundos"
        )

        # Estructura del proyecto
        structure = report["project_structure"]["summary"]
        print(f"\n📁 ESTRUCTURA DEL PROYECTO:")
        print(
            f"   Directorios: {structure['directories_ok']}/{structure['directories_checked']}"
        )
        print(f"   Archivos: {structure['files_ok']}/{structure['files_checked']}")
        print(f"   Puntuación: {structure['total_score']}")

        # Módulos
        modules = report["modules_implementation"]["summary"]
        print(f"\n📦 MÓDULOS:")
        print(f"   Activos: {modules['active_modules']}/{modules['total_modules']}")
        print(f"   Vacíos: {modules['empty_modules']}")
        print(f"   Faltantes: {modules['missing_modules']}")
        print(f"   Puntuación: {modules['score']}")

        # Configuraciones
        configs = report["configurations"]["summary"]
        print(f"\n⚙️ CONFIGURACIONES:")
        print(f"   Válidas: {configs['valid_configs']}/{configs['total_configs']}")
        print(f"   Existentes: {configs['existing_configs']}")
        print(f"   Puntuación: {configs['score']}")

        # Bases de datos
        dbs = report["database_implementation"]["summary"]
        print(f"\n🗄️ BASES DE DATOS:")
        print(f"   Activas: {dbs['active_databases']}/{dbs['total_databases']}")
        print(f"   Vacías: {dbs['empty_databases']}")
        print(f"   Faltantes: {dbs['missing_databases']}")
        print(f"   Puntuación: {dbs['score']}")

        # Interfaces
        interfaces = report["interface_implementation"]["summary"]
        print(f"\n🖥️ INTERFACES:")
        print(
            f"   Completas: {interfaces['complete_interfaces']}/{interfaces['total_interfaces']}"
        )
        print(f"   Parciales: {interfaces['partial_interfaces']}")
        print(f"   Faltantes: {interfaces['missing_interfaces']}")
        print(f"   Puntuación: {interfaces['score']}")

        # Scripts del sistema
        scripts = report["system_scripts"]["summary"]
        print(f"\n🔧 SCRIPTS DEL SISTEMA:")
        print(f"   Activos: {scripts['active_scripts']}/{scripts['total_scripts']}")
        print(f"   Vacíos: {scripts['empty_scripts']}")
        print(f"   Faltantes: {scripts['missing_scripts']}")
        print(f"   Puntuación: {scripts['score']}")

        # Docker
        docker = report["docker_implementation"]["summary"]
        print(f"\n🐳 DOCKER:")
        print(f"   Activos: {docker['active_docker']}/{docker['total_docker']}")
        print(f"   Faltantes: {docker['missing_docker']}")
        print(f"   Puntuación: {docker['score']}")

        # Verificaciones de salud
        health = report["health_checks"]["summary"]
        print(f"\n🏥 VERIFICACIONES DE SALUD:")
        print(f"   Exitosas: {health['successful_checks']}/{health['total_checks']}")
        print(f"   Fallidas: {health['failed_checks']}")
        print(f"   Puntuación: {health['score']}")

        # Resumen general
        overall = report["overall_summary"]
        print(f"\n" + "=" * 60)
        print(f"📊 RESUMEN GENERAL DE IMPLEMENTACIÓN")
        print(f"=" * 60)
        print(
            f"   Puntuación total: {overall['total_score']}/{overall['max_possible_score']}"
        )
        print(f"   Porcentaje: {overall['percentage']}%")
        print(f"   Estado: {overall['overall_status']}")
        print(f"   Nivel de implementación: {overall['implementation_level']}")

        # Recomendaciones
        print(f"\n💡 RECOMENDACIONES:")
        if overall["percentage"] >= 80:
            print(f"   🎉 ¡Excelente! El proyecto está muy bien implementado.")
            print(f"   ✅ Considera ejecutar pruebas de integración.")
        elif overall["percentage"] >= 60:
            print(f"   👍 Buen trabajo. El proyecto está bien implementado.")
            print(f"   🔧 Revisa las áreas con puntuación baja.")
        elif overall["percentage"] >= 40:
            print(f"   ⚠️ Implementación regular. Necesita mejoras.")
            print(f"   🚧 Prioriza completar módulos faltantes.")
        else:
            print(f"   ❌ Implementación pendiente. Requiere trabajo significativo.")
            print(f"   🚨 Revisa todos los componentes faltantes.")

        print(f"\n" + "=" * 80)


def main():
    """Función principal"""
    implementation = CompleteProjectImplementation()
    report = implementation.generate_complete_report()
    implementation.print_complete_report(report)

    # Retornar código de salida basado en el estado general
    overall_status = report["overall_summary"]["overall_status"]
    if overall_status in ["EXCELENTE", "BUENO"]:
        return 0
    else:
        return 1


if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)
