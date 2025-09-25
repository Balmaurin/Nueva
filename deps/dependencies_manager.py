#!/usr/bin/env python3
"""
Gestor de Dependencias del Sistema NeuroFusion
Maneja todas las dependencias del proyecto de manera centralizada
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
import hashlib
import pkg_resources
import importlib
import shutil

# Configuración de logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@dataclass
class DependencyInfo:
    """Información de una dependencia"""

    name: str
    version: str
    type: str  # 'python', 'node', 'system'
    source: str
    required: bool
    installed: bool
    installed_version: Optional[str]
    description: str
    dependencies: List[str]


@dataclass
class DependencyStats:
    """Estadísticas de dependencias"""

    total_dependencies: int
    installed_dependencies: int
    missing_dependencies: int
    outdated_dependencies: int
    python_dependencies: int
    node_dependencies: int
    system_dependencies: int
    last_updated: datetime


class DependenciesManager:
    """Gestor principal de dependencias del sistema NeuroFusion"""

    def __init__(self, deps_dir: str = "deps"):
        self.deps_dir = Path(deps_dir)
        self.python_deps = {}
        self.node_deps = {}
        self.system_deps = {}
        self.dependency_cache = {}

        # Inicializar directorios
        self._initialize_directories()

        # Cargar configuraciones de dependencias
        self._load_dependency_configs()

    def _initialize_directories(self):
        """Inicializa los directorios necesarios"""
        directories = [
            self.deps_dir,
            self.deps_dir / "python",
            self.deps_dir / "node",
            self.deps_dir / "system",
            self.deps_dir / "cache",
            self.deps_dir / "backups",
        ]

        for directory in directories:
            directory.mkdir(parents=True, exist_ok=True)
            logger.info(f"Directorio inicializado: {directory}")

    def _load_dependency_configs(self):
        """Carga las configuraciones de dependencias"""
        # Dependencias de Python
        self.python_deps = {
            # Core dependencies
            "numpy": {
                "version": ">=1.21.0",
                "required": True,
                "description": "Biblioteca para computación numérica",
            },
            "torch": {
                "version": ">=1.9.0",
                "required": True,
                "description": "PyTorch para deep learning",
            },
            "transformers": {
                "version": ">=4.20.0",
                "required": True,
                "description": "Biblioteca de transformers de Hugging Face",
            },
            "sentence-transformers": {
                "version": ">=2.2.0",
                "required": True,
                "description": "Modelos de embeddings de oraciones",
            },
            "faiss-cpu": {
                "version": ">=1.7.0",
                "required": True,
                "description": "Biblioteca para búsqueda de similitud",
            },
            "scikit-learn": {
                "version": ">=1.0.0",
                "required": True,
                "description": "Machine learning en Python",
            },
            "nltk": {
                "version": ">=3.7",
                "required": True,
                "description": "Natural Language Toolkit",
            },
            "spacy": {
                "version": ">=3.4.0",
                "required": True,
                "description": "Procesamiento de lenguaje natural",
            },
            "duckdb": {
                "version": ">=0.7.0",
                "required": True,
                "description": "Base de datos analítica",
            },
            "sqlite3": {
                "version": "builtin",
                "required": True,
                "description": "Base de datos SQLite (incluida en Python)",
            },
            "fastapi": {
                "version": ">=0.68.0",
                "required": True,
                "description": "Framework web para APIs",
            },
            "uvicorn": {
                "version": ">=0.15.0",
                "required": True,
                "description": "Servidor ASGI",
            },
            "pydantic": {
                "version": ">=1.8.0",
                "required": True,
                "description": "Validación de datos",
            },
            "python-multipart": {
                "version": ">=0.0.5",
                "required": True,
                "description": "Manejo de formularios multipart",
            },
            "python-jose": {
                "version": ">=3.3.0",
                "required": True,
                "description": "Implementación de JWT",
            },
            "passlib": {
                "version": ">=1.7.4",
                "required": True,
                "description": "Hashing de contraseñas",
            },
            "bcrypt": {
                "version": ">=3.2.0",
                "required": True,
                "description": "Algoritmo de hashing",
            },
            "redis": {
                "version": ">=4.0.0",
                "required": True,
                "description": "Cliente Redis",
            },
            "psycopg2-binary": {
                "version": ">=2.9.0",
                "required": True,
                "description": "Adaptador PostgreSQL",
            },
            "prometheus-client": {
                "version": ">=0.12.0",
                "required": True,
                "description": "Cliente Prometheus",
            },
            "watchdog": {
                "version": ">=2.1.0",
                "required": True,
                "description": "Monitoreo de archivos",
            },
            "jsonschema": {
                "version": ">=3.2.0",
                "required": True,
                "description": "Validación de esquemas JSON",
            },
            "pyyaml": {
                "version": ">=6.0",
                "required": True,
                "description": "Parser YAML",
            },
            "requests": {
                "version": ">=2.25.0",
                "required": True,
                "description": "Cliente HTTP",
            },
            "aiohttp": {
                "version": ">=3.8.0",
                "required": True,
                "description": "Cliente HTTP asíncrono",
            },
            "websockets": {
                "version": ">=10.0",
                "required": True,
                "description": "WebSockets",
            },
            "celery": {
                "version": ">=5.2.0",
                "required": True,
                "description": "Cola de tareas distribuidas",
            },
            "flower": {
                "version": ">=1.0.0",
                "required": False,
                "description": "Monitor de Celery",
            },
            "pytest": {
                "version": ">=6.2.0",
                "required": False,
                "description": "Framework de testing",
            },
            "pytest-asyncio": {
                "version": ">=0.18.0",
                "required": False,
                "description": "Soporte asíncrono para pytest",
            },
            "black": {
                "version": ">=22.0.0",
                "required": False,
                "description": "Formateador de código",
            },
            "flake8": {
                "version": ">=4.0.0",
                "required": False,
                "description": "Linter de código",
            },
            "mypy": {
                "version": ">=0.950",
                "required": False,
                "description": "Verificador de tipos",
            },
            "pre-commit": {
                "version": ">=2.19.0",
                "required": False,
                "description": "Hooks de pre-commit",
            },
        }

        # Dependencias de Node.js
        self.node_deps = {
            "react": {
                "version": "^18.0.0",
                "required": True,
                "description": "Biblioteca de interfaz de usuario",
            },
            "react-dom": {
                "version": "^18.0.0",
                "required": True,
                "description": "Renderizado de React en el DOM",
            },
            "next": {
                "version": "^12.0.0",
                "required": True,
                "description": "Framework de React",
            },
            "typescript": {
                "version": "^4.9.0",
                "required": True,
                "description": "Superset de JavaScript",
            },
            "@types/react": {
                "version": "^18.0.0",
                "required": True,
                "description": "Tipos de TypeScript para React",
            },
            "@types/node": {
                "version": "^18.0.0",
                "required": True,
                "description": "Tipos de TypeScript para Node.js",
            },
            "tailwindcss": {
                "version": "^3.0.0",
                "required": True,
                "description": "Framework CSS utility-first",
            },
            "autoprefixer": {
                "version": "^10.4.0",
                "required": True,
                "description": "Plugin de PostCSS",
            },
            "postcss": {
                "version": "^8.4.0",
                "required": True,
                "description": "Herramienta de transformación CSS",
            },
            "axios": {
                "version": "^0.27.0",
                "required": True,
                "description": "Cliente HTTP",
            },
            "zustand": {
                "version": "^4.0.0",
                "required": True,
                "description": "Gestor de estado",
            },
            "react-query": {
                "version": "^3.39.0",
                "required": True,
                "description": "Gestión de estado del servidor",
            },
            "react-hook-form": {
                "version": "^7.34.0",
                "required": True,
                "description": "Gestión de formularios",
            },
            "framer-motion": {
                "version": "^6.3.0",
                "required": True,
                "description": "Animaciones",
            },
            "lucide-react": {
                "version": "^0.263.0",
                "required": True,
                "description": "Iconos",
            },
            "clsx": {
                "version": "^1.2.0",
                "required": True,
                "description": "Utilidad para clases CSS",
            },
            "date-fns": {
                "version": "^2.29.0",
                "required": True,
                "description": "Utilidades de fecha",
            },
            "recharts": {
                "version": "^2.5.0",
                "required": True,
                "description": "Gráficos de React",
            },
            "react-dropzone": {
                "version": "^14.2.0",
                "required": True,
                "description": "Drag and drop de archivos",
            },
            "react-hot-toast": {
                "version": "^2.4.0",
                "required": True,
                "description": "Notificaciones toast",
            },
        }

        # Dependencias del sistema
        self.system_deps = {
            "python3": {
                "version": ">=3.8",
                "required": True,
                "description": "Python 3.8 o superior",
            },
            "pip": {
                "version": ">=20.0",
                "required": True,
                "description": "Gestor de paquetes de Python",
            },
            "node": {
                "version": ">=16.0",
                "required": True,
                "description": "Node.js 16 o superior",
            },
            "npm": {
                "version": ">=8.0",
                "required": True,
                "description": "Gestor de paquetes de Node.js",
            },
            "git": {
                "version": ">=2.0",
                "required": True,
                "description": "Control de versiones",
            },
            "docker": {
                "version": ">=20.0",
                "required": False,
                "description": "Contenedores Docker",
            },
            "docker-compose": {
                "version": ">=2.0",
                "required": False,
                "description": "Orquestación de contenedores",
            },
            "postgresql": {
                "version": ">=13.0",
                "required": False,
                "description": "Base de datos PostgreSQL",
            },
            "redis": {
                "version": ">=6.0",
                "required": False,
                "description": "Base de datos Redis",
            },
        }

    def check_python_dependency(self, package_name: str) -> DependencyInfo:
        """Verifica una dependencia de Python"""
        try:
            # Obtener información de la dependencia
            dep_config = self.python_deps.get(package_name, {})

            # Verificar si está instalada
            try:
                if package_name == "sqlite3":
                    import sqlite3

                    installed_version = sqlite3.sqlite_version
                else:
                    installed_version = pkg_resources.get_distribution(
                        package_name
                    ).version
                installed = True
            except (pkg_resources.DistributionNotFound, ImportError):
                installed_version = None
                installed = False

            return DependencyInfo(
                name=package_name,
                version=dep_config.get("version", "unknown"),
                type="python",
                source="pypi",
                required=dep_config.get("required", False),
                installed=installed,
                installed_version=installed_version,
                description=dep_config.get("description", ""),
                dependencies=[],
            )

        except Exception as e:
            logger.error(f"Error verificando dependencia Python {package_name}: {e}")
            return DependencyInfo(
                name=package_name,
                version="unknown",
                type="python",
                source="pypi",
                required=False,
                installed=False,
                installed_version=None,
                description="Error verificando dependencia",
                dependencies=[],
            )

    def check_node_dependency(self, package_name: str) -> DependencyInfo:
        """Verifica una dependencia de Node.js"""
        try:
            # Obtener información de la dependencia
            dep_config = self.node_deps.get(package_name, {})

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
                    installed = True
                else:
                    installed_version = None
                    installed = False
            except Exception:
                installed_version = None
                installed = False

            return DependencyInfo(
                name=package_name,
                version=dep_config.get("version", "unknown"),
                type="node",
                source="npm",
                required=dep_config.get("required", False),
                installed=installed,
                installed_version=installed_version,
                description=dep_config.get("description", ""),
                dependencies=[],
            )

        except Exception as e:
            logger.error(f"Error verificando dependencia Node.js {package_name}: {e}")
            return DependencyInfo(
                name=package_name,
                version="unknown",
                type="node",
                source="npm",
                required=False,
                installed=False,
                installed_version=None,
                description="Error verificando dependencia",
                dependencies=[],
            )

    def check_system_dependency(self, package_name: str) -> DependencyInfo:
        """Verifica una dependencia del sistema"""
        try:
            # Obtener información de la dependencia
            dep_config = self.system_deps.get(package_name, {})

            # Verificar si está instalada
            try:
                result = subprocess.run(
                    [package_name, "--version"], capture_output=True, text=True
                )
                if result.returncode == 0:
                    installed_version = result.stdout.strip()
                    installed = True
                else:
                    installed_version = None
                    installed = False
            except FileNotFoundError:
                installed_version = None
                installed = False

            return DependencyInfo(
                name=package_name,
                version=dep_config.get("version", "unknown"),
                type="system",
                source="system",
                required=dep_config.get("required", False),
                installed=installed,
                installed_version=installed_version,
                description=dep_config.get("description", ""),
                dependencies=[],
            )

        except Exception as e:
            logger.error(
                f"Error verificando dependencia del sistema {package_name}: {e}"
            )
            return DependencyInfo(
                name=package_name,
                version="unknown",
                type="system",
                source="system",
                required=False,
                installed=False,
                installed_version=None,
                description="Error verificando dependencia",
                dependencies=[],
            )

    def check_all_dependencies(self) -> List[DependencyInfo]:
        """Verifica todas las dependencias"""
        dependencies = []

        # Verificar dependencias de Python
        logger.info("Verificando dependencias de Python...")
        for package_name in self.python_deps.keys():
            dep_info = self.check_python_dependency(package_name)
            dependencies.append(dep_info)

        # Verificar dependencias de Node.js
        logger.info("Verificando dependencias de Node.js...")
        for package_name in self.node_deps.keys():
            dep_info = self.check_node_dependency(package_name)
            dependencies.append(dep_info)

        # Verificar dependencias del sistema
        logger.info("Verificando dependencias del sistema...")
        for package_name in self.system_deps.keys():
            dep_info = self.check_system_dependency(package_name)
            dependencies.append(dep_info)

        return dependencies

    def install_python_dependency(self, package_name: str, version: str = None) -> bool:
        """Instala una dependencia de Python"""
        try:
            if version:
                package_spec = f"{package_name}{version}"
            else:
                package_spec = package_name

            logger.info(f"Instalando dependencia Python: {package_spec}")

            result = subprocess.run(
                [sys.executable, "-m", "pip", "install", package_spec],
                capture_output=True,
                text=True,
            )

            if result.returncode == 0:
                logger.info(f"Dependencia Python instalada: {package_name}")
                return True
            else:
                logger.error(
                    f"Error instalando dependencia Python {package_name}: {result.stderr}"
                )
                return False

        except Exception as e:
            logger.error(f"Error instalando dependencia Python {package_name}: {e}")
            return False

    def install_node_dependency(self, package_name: str, version: str = None) -> bool:
        """Instala una dependencia de Node.js"""
        try:
            if version:
                package_spec = f"{package_name}@{version}"
            else:
                package_spec = package_name

            logger.info(f"Instalando dependencia Node.js: {package_spec}")

            result = subprocess.run(
                ["npm", "install", package_spec],
                capture_output=True,
                text=True,
                cwd=self.deps_dir,
            )

            if result.returncode == 0:
                logger.info(f"Dependencia Node.js instalada: {package_name}")
                return True
            else:
                logger.error(
                    f"Error instalando dependencia Node.js {package_name}: {result.stderr}"
                )
                return False

        except Exception as e:
            logger.error(f"Error instalando dependencia Node.js {package_name}: {e}")
            return False

    def install_missing_dependencies(self) -> Dict[str, List[str]]:
        """Instala todas las dependencias faltantes"""
        results = {"success": [], "failed": []}

        # Verificar todas las dependencias
        dependencies = self.check_all_dependencies()

        for dep in dependencies:
            if not dep.installed and dep.required:
                logger.info(f"Instalando dependencia faltante: {dep.name}")

                success = False
                if dep.type == "python":
                    success = self.install_python_dependency(dep.name, dep.version)
                elif dep.type == "node":
                    success = self.install_node_dependency(dep.name, dep.version)
                elif dep.type == "system":
                    logger.warning(f"Dependencia del sistema no instalada: {dep.name}")
                    results["failed"].append(f"{dep.name} (sistema)")
                    continue

                if success:
                    results["success"].append(dep.name)
                else:
                    results["failed"].append(dep.name)

        return results

    def create_requirements_txt(self) -> str:
        """Crea un archivo requirements.txt con todas las dependencias de Python"""
        try:
            requirements = []

            for package_name, config in self.python_deps.items():
                if config.get("required", False):
                    requirements.append(f"{package_name}{config['version']}")

            requirements_txt = "\n".join(requirements)

            # Guardar archivo
            requirements_path = self.deps_dir / "requirements.txt"
            with open(requirements_path, "w") as f:
                f.write(requirements_txt)

            logger.info(f"Archivo requirements.txt creado: {requirements_path}")
            return str(requirements_path)

        except Exception as e:
            logger.error(f"Error creando requirements.txt: {e}")
            return ""

    def create_package_json(self) -> str:
        """Crea un archivo package.json con todas las dependencias de Node.js"""
        try:
            package_data = {
                "name": "neurofusion-frontend",
                "version": "1.0.0",
                "description": "Frontend del sistema NeuroFusion",
                "type": "module",
                "scripts": {
                    "dev": "next dev",
                    "build": "next build",
                    "start": "next start",
                    "lint": "next lint",
                },
                "dependencies": {},
                "devDependencies": {},
            }

            # Agregar dependencias
            for package_name, config in self.node_deps.items():
                if config.get("required", False):
                    package_data["dependencies"][package_name] = config["version"]

            # Guardar archivo
            package_json_path = self.deps_dir / "package.json"
            with open(package_json_path, "w") as f:
                json.dump(package_data, f, indent=2)

            logger.info(f"Archivo package.json creado: {package_json_path}")
            return str(package_json_path)

        except Exception as e:
            logger.error(f"Error creando package.json: {e}")
            return ""

    def get_dependency_stats(self) -> DependencyStats:
        """Obtiene estadísticas de las dependencias"""
        try:
            dependencies = self.check_all_dependencies()

            total_deps = len(dependencies)
            installed_deps = sum(1 for dep in dependencies if dep.installed)
            missing_deps = sum(
                1 for dep in dependencies if not dep.installed and dep.required
            )
            outdated_deps = 0  # Implementar verificación de versiones

            python_deps = sum(1 for dep in dependencies if dep.type == "python")
            node_deps = sum(1 for dep in dependencies if dep.type == "node")
            system_deps = sum(1 for dep in dependencies if dep.type == "system")

            return DependencyStats(
                total_dependencies=total_deps,
                installed_dependencies=installed_deps,
                missing_dependencies=missing_deps,
                outdated_dependencies=outdated_deps,
                python_dependencies=python_deps,
                node_dependencies=node_deps,
                system_dependencies=system_deps,
                last_updated=datetime.now(),
            )

        except Exception as e:
            logger.error(f"Error obteniendo estadísticas: {e}")
            return DependencyStats(0, 0, 0, 0, 0, 0, 0, datetime.now())

    def backup_dependencies(self) -> str:
        """Crea un backup de las configuraciones de dependencias"""
        try:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_dir = self.deps_dir / "backups" / f"deps_backup_{timestamp}"
            backup_dir.mkdir(parents=True, exist_ok=True)

            # Backup de configuraciones
            backup_data = {
                "python_dependencies": self.python_deps,
                "node_dependencies": self.node_deps,
                "system_dependencies": self.system_deps,
                "backup_timestamp": timestamp,
            }

            backup_file = backup_dir / "dependencies_config.json"
            with open(backup_file, "w") as f:
                json.dump(backup_data, f, indent=2)

            # Backup de archivos existentes
            for file_name in ["requirements.txt", "package.json"]:
                file_path = self.deps_dir / file_name
                if file_path.exists():
                    shutil.copy2(file_path, backup_dir / file_name)

            logger.info(f"Backup de dependencias creado: {backup_dir}")
            return str(backup_dir)

        except Exception as e:
            logger.error(f"Error creando backup: {e}")
            return ""

    def restore_dependencies(self, backup_path: str) -> bool:
        """Restaura dependencias desde un backup"""
        try:
            backup_dir = Path(backup_path)
            if not backup_dir.exists():
                logger.error(f"Backup no encontrado: {backup_path}")
                return False

            # Restaurar configuraciones
            config_file = backup_dir / "dependencies_config.json"
            if config_file.exists():
                with open(config_file, "r") as f:
                    backup_data = json.load(f)

                self.python_deps = backup_data.get("python_dependencies", {})
                self.node_deps = backup_data.get("node_dependencies", {})
                self.system_deps = backup_data.get("system_dependencies", {})

            # Restaurar archivos
            for file_name in ["requirements.txt", "package.json"]:
                backup_file = backup_dir / file_name
                if backup_file.exists():
                    shutil.copy2(backup_file, self.deps_dir / file_name)

            logger.info(f"Dependencias restauradas desde: {backup_path}")
            return True

        except Exception as e:
            logger.error(f"Error restaurando dependencias: {e}")
            return False

    def update_dependency_versions(self) -> Dict[str, List[str]]:
        """Actualiza las versiones de las dependencias"""
        results = {"updated": [], "failed": []}

        try:
            # Actualizar dependencias de Python
            logger.info("Actualizando dependencias de Python...")
            result = subprocess.run(
                [sys.executable, "-m", "pip", "install", "--upgrade", "pip"],
                capture_output=True,
                text=True,
            )

            for package_name in self.python_deps.keys():
                if package_name != "sqlite3":  # sqlite3 es builtin
                    try:
                        result = subprocess.run(
                            [
                                sys.executable,
                                "-m",
                                "pip",
                                "install",
                                "--upgrade",
                                package_name,
                            ],
                            capture_output=True,
                            text=True,
                        )
                        if result.returncode == 0:
                            results["updated"].append(f"{package_name} (python)")
                        else:
                            results["failed"].append(f"{package_name} (python)")
                    except Exception as e:
                        logger.error(f"Error actualizando {package_name}: {e}")
                        results["failed"].append(f"{package_name} (python)")

            # Actualizar dependencias de Node.js
            logger.info("Actualizando dependencias de Node.js...")
            result = subprocess.run(
                ["npm", "update"], capture_output=True, text=True, cwd=self.deps_dir
            )

            if result.returncode == 0:
                results["updated"].append("node dependencies")
            else:
                results["failed"].append("node dependencies")

            return results

        except Exception as e:
            logger.error(f"Error actualizando dependencias: {e}")
            return results

    def cleanup_cache(self) -> int:
        """Limpia el caché de dependencias"""
        cleaned_count = 0

        try:
            # Limpiar caché de pip
            result = subprocess.run(
                [sys.executable, "-m", "pip", "cache", "purge"],
                capture_output=True,
                text=True,
            )
            if result.returncode == 0:
                cleaned_count += 1

            # Limpiar caché de npm
            result = subprocess.run(
                ["npm", "cache", "clean", "--force"],
                capture_output=True,
                text=True,
                cwd=self.deps_dir,
            )
            if result.returncode == 0:
                cleaned_count += 1

            logger.info(f"Caché limpiado: {cleaned_count} fuentes")
            return cleaned_count

        except Exception as e:
            logger.error(f"Error limpiando caché: {e}")
            return 0


# Instancia global del gestor de dependencias
dependencies_manager = DependenciesManager()


def get_dependencies_manager() -> DependenciesManager:
    """Obtiene la instancia global del gestor de dependencias"""
    return dependencies_manager


if __name__ == "__main__":
    # Ejemplo de uso
    manager = DependenciesManager()

    # Verificar dependencias
    dependencies = manager.check_all_dependencies()
    print(f"Dependencias verificadas: {len(dependencies)}")

    # Obtener estadísticas
    stats = manager.get_dependency_stats()
    print(
        f"Estadísticas: {stats.installed_dependencies}/{stats.total_dependencies} instaladas"
    )

    # Crear archivos de configuración
    manager.create_requirements_txt()
    manager.create_package_json()
