#!/usr/bin/env python3
"""
Instalador Automático de Dependencias del Sistema NeuroFusion
Maneja la instalación y configuración automática de todas las dependencias
"""

import json
import logging
import subprocess
import sys
import os
from pathlib import Path
from typing import Dict, Any, List, Optional, Union, Tuple
from dataclasses import dataclass
from datetime import datetime
import time
import threading
from concurrent.futures import ThreadPoolExecutor, as_completed

# Configuración de logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@dataclass
class InstallationResult:
    """Resultado de una instalación"""

    package_name: str
    package_type: str
    success: bool
    version_installed: Optional[str]
    error_message: Optional[str]
    installation_time: float
    dependencies_installed: List[str]


@dataclass
class InstallationProgress:
    """Progreso de instalación"""

    total_packages: int
    installed_packages: int
    failed_packages: int
    current_package: str
    current_type: str
    start_time: datetime
    estimated_completion: Optional[datetime]


class DependencyInstaller:
    """Instalador automático de dependencias del sistema NeuroFusion"""

    def __init__(self, deps_dir: str = "deps"):
        self.deps_dir = Path(deps_dir)
        self.installation_log = []
        self.progress_callback = None
        self.stop_installation = False

        # Configuraciones de instalación
        self.install_config = {
            "max_workers": 4,
            "timeout": 300,  # 5 minutos por paquete
            "retry_attempts": 3,
            "install_order": ["system", "python", "node"],
            "skip_optional": False,
        }

    def set_progress_callback(self, callback):
        """Establece un callback para el progreso de instalación"""
        self.progress_callback = callback

    def _log_installation(self, result: InstallationResult):
        """Registra el resultado de una instalación"""
        self.installation_log.append(
            {
                "timestamp": datetime.now().isoformat(),
                "package_name": result.package_name,
                "package_type": result.package_type,
                "success": result.success,
                "version_installed": result.version_installed,
                "error_message": result.error_message,
                "installation_time": result.installation_time,
                "dependencies_installed": result.dependencies_installed,
            }
        )

    def _update_progress(
        self, current: int, total: int, current_package: str, current_type: str
    ):
        """Actualiza el progreso de instalación"""
        if self.progress_callback:
            progress = InstallationProgress(
                total_packages=total,
                installed_packages=current,
                failed_packages=len(
                    [r for r in self.installation_log if not r["success"]]
                ),
                current_package=current_package,
                current_type=current_type,
                start_time=datetime.now(),
                estimated_completion=None,
            )
            self.progress_callback(progress)

    def install_system_dependency(self, package_name: str) -> InstallationResult:
        """Instala una dependencia del sistema"""
        start_time = time.time()

        try:
            logger.info(f"Instalando dependencia del sistema: {package_name}")

            # Comandos de instalación por sistema operativo
            install_commands = {
                "ubuntu": {
                    "python3": [
                        "sudo",
                        "apt-get",
                        "update",
                        "&&",
                        "sudo",
                        "apt-get",
                        "install",
                        "-y",
                        "python3",
                    ],
                    "pip": [
                        "sudo",
                        "apt-get",
                        "update",
                        "&&",
                        "sudo",
                        "apt-get",
                        "install",
                        "-y",
                        "python3-pip",
                    ],
                    "node": [
                        "curl",
                        "-fsSL",
                        "https://deb.nodesource.com/setup_18.x",
                        "|",
                        "sudo",
                        "-E",
                        "bash",
                        "-",
                        "&&",
                        "sudo",
                        "apt-get",
                        "install",
                        "-y",
                        "nodejs",
                    ],
                    "npm": [
                        "sudo",
                        "apt-get",
                        "update",
                        "&&",
                        "sudo",
                        "apt-get",
                        "install",
                        "-y",
                        "npm",
                    ],
                    "git": [
                        "sudo",
                        "apt-get",
                        "update",
                        "&&",
                        "sudo",
                        "apt-get",
                        "install",
                        "-y",
                        "git",
                    ],
                    "docker": [
                        "sudo",
                        "apt-get",
                        "update",
                        "&&",
                        "sudo",
                        "apt-get",
                        "install",
                        "-y",
                        "docker.io",
                    ],
                    "docker-compose": [
                        "sudo",
                        "apt-get",
                        "update",
                        "&&",
                        "sudo",
                        "apt-get",
                        "install",
                        "-y",
                        "docker-compose",
                    ],
                    "postgresql": [
                        "sudo",
                        "apt-get",
                        "update",
                        "&&",
                        "sudo",
                        "apt-get",
                        "install",
                        "-y",
                        "postgresql",
                        "postgresql-contrib",
                    ],
                    "redis": [
                        "sudo",
                        "apt-get",
                        "update",
                        "&&",
                        "sudo",
                        "apt-get",
                        "install",
                        "-y",
                        "redis-server",
                    ],
                },
                "centos": {
                    "python3": ["sudo", "yum", "install", "-y", "python3"],
                    "pip": ["sudo", "yum", "install", "-y", "python3-pip"],
                    "node": [
                        "curl",
                        "-fsSL",
                        "https://rpm.nodesource.com/setup_18.x",
                        "|",
                        "sudo",
                        "bash",
                        "-",
                        "&&",
                        "sudo",
                        "yum",
                        "install",
                        "-y",
                        "nodejs",
                    ],
                    "npm": ["sudo", "yum", "install", "-y", "npm"],
                    "git": ["sudo", "yum", "install", "-y", "git"],
                    "docker": ["sudo", "yum", "install", "-y", "docker"],
                    "docker-compose": [
                        "sudo",
                        "curl",
                        "-L",
                        '"https://github.com/docker/compose/releases/download/v2.0.0/docker-compose-$(uname -s)-$(uname -m)"',
                        "-o",
                        "/usr/local/bin/docker-compose",
                        "&&",
                        "sudo",
                        "chmod",
                        "+x",
                        "/usr/local/bin/docker-compose",
                    ],
                    "postgresql": [
                        "sudo",
                        "yum",
                        "install",
                        "-y",
                        "postgresql-server",
                        "postgresql-contrib",
                    ],
                    "redis": ["sudo", "yum", "install", "-y", "redis"],
                },
            }

            # Detectar sistema operativo
            os_name = self._detect_os()
            if os_name not in install_commands:
                raise Exception(f"Sistema operativo no soportado: {os_name}")

            if package_name not in install_commands[os_name]:
                raise Exception(f"Paquete del sistema no soportado: {package_name}")

            command = install_commands[os_name][package_name]

            # Ejecutar comando de instalación
            result = subprocess.run(
                command,
                capture_output=True,
                text=True,
                timeout=self.install_config["timeout"],
            )

            if result.returncode == 0:
                # Verificar instalación
                version = self._get_system_package_version(package_name)

                installation_result = InstallationResult(
                    package_name=package_name,
                    package_type="system",
                    success=True,
                    version_installed=version,
                    error_message=None,
                    installation_time=time.time() - start_time,
                    dependencies_installed=[],
                )

                logger.info(
                    f"Dependencia del sistema instalada: {package_name} {version}"
                )
                return installation_result
            else:
                raise Exception(f"Error en instalación: {result.stderr}")

        except Exception as e:
            installation_result = InstallationResult(
                package_name=package_name,
                package_type="system",
                success=False,
                version_installed=None,
                error_message=str(e),
                installation_time=time.time() - start_time,
                dependencies_installed=[],
            )

            logger.error(
                f"Error instalando dependencia del sistema {package_name}: {e}"
            )
            return installation_result

    def install_python_dependency(
        self, package_name: str, version: str = None
    ) -> InstallationResult:
        """Instala una dependencia de Python"""
        start_time = time.time()

        try:
            logger.info(f"Instalando dependencia Python: {package_name}")

            # Construir especificación del paquete
            if version and version != "builtin":
                package_spec = f"{package_name}{version}"
            else:
                package_spec = package_name

            # Comando de instalación
            command = [sys.executable, "-m", "pip", "install", package_spec]

            # Ejecutar instalación con reintentos
            for attempt in range(self.install_config["retry_attempts"]):
                try:
                    result = subprocess.run(
                        command,
                        capture_output=True,
                        text=True,
                        timeout=self.install_config["timeout"],
                    )

                    if result.returncode == 0:
                        # Verificar instalación
                        installed_version = self._get_python_package_version(
                            package_name
                        )

                        installation_result = InstallationResult(
                            package_name=package_name,
                            package_type="python",
                            success=True,
                            version_installed=installed_version,
                            error_message=None,
                            installation_time=time.time() - start_time,
                            dependencies_installed=self._extract_installed_dependencies(
                                result.stdout
                            ),
                        )

                        logger.info(
                            f"Dependencia Python instalada: {package_name} {installed_version}"
                        )
                        return installation_result
                    else:
                        if attempt < self.install_config["retry_attempts"] - 1:
                            logger.warning(
                                f"Intento {attempt + 1} fallido para {package_name}, reintentando..."
                            )
                            time.sleep(2)
                            continue
                        else:
                            raise Exception(f"Error en instalación: {result.stderr}")

                except subprocess.TimeoutExpired:
                    if attempt < self.install_config["retry_attempts"] - 1:
                        logger.warning(
                            f"Timeout en intento {attempt + 1} para {package_name}, reintentando..."
                        )
                        continue
                    else:
                        raise Exception("Timeout en instalación")

        except Exception as e:
            installation_result = InstallationResult(
                package_name=package_name,
                package_type="python",
                success=False,
                version_installed=None,
                error_message=str(e),
                installation_time=time.time() - start_time,
                dependencies_installed=[],
            )

            logger.error(f"Error instalando dependencia Python {package_name}: {e}")
            return installation_result

    def install_node_dependency(
        self, package_name: str, version: str = None
    ) -> InstallationResult:
        """Instala una dependencia de Node.js"""
        start_time = time.time()

        try:
            logger.info(f"Instalando dependencia Node.js: {package_name}")

            # Construir especificación del paquete
            if version:
                package_spec = f"{package_name}@{version}"
            else:
                package_spec = package_name

            # Comando de instalación
            command = ["npm", "install", package_spec]

            # Ejecutar instalación con reintentos
            for attempt in range(self.install_config["retry_attempts"]):
                try:
                    result = subprocess.run(
                        command,
                        capture_output=True,
                        text=True,
                        cwd=self.deps_dir,
                        timeout=self.install_config["timeout"],
                    )

                    if result.returncode == 0:
                        # Verificar instalación
                        installed_version = self._get_node_package_version(package_name)

                        installation_result = InstallationResult(
                            package_name=package_name,
                            package_type="node",
                            success=True,
                            version_installed=installed_version,
                            error_message=None,
                            installation_time=time.time() - start_time,
                            dependencies_installed=self._extract_installed_dependencies(
                                result.stdout
                            ),
                        )

                        logger.info(
                            f"Dependencia Node.js instalada: {package_name} {installed_version}"
                        )
                        return installation_result
                    else:
                        if attempt < self.install_config["retry_attempts"] - 1:
                            logger.warning(
                                f"Intento {attempt + 1} fallido para {package_name}, reintentando..."
                            )
                            time.sleep(2)
                            continue
                        else:
                            raise Exception(f"Error en instalación: {result.stderr}")

                except subprocess.TimeoutExpired:
                    if attempt < self.install_config["retry_attempts"] - 1:
                        logger.warning(
                            f"Timeout en intento {attempt + 1} para {package_name}, reintentando..."
                        )
                        continue
                    else:
                        raise Exception("Timeout en instalación")

        except Exception as e:
            installation_result = InstallationResult(
                package_name=package_name,
                package_type="node",
                success=False,
                version_installed=None,
                error_message=str(e),
                installation_time=time.time() - start_time,
                dependencies_installed=[],
            )

            logger.error(f"Error instalando dependencia Node.js {package_name}: {e}")
            return installation_result

    def install_all_dependencies(
        self, dependencies_config: Dict[str, Any]
    ) -> List[InstallationResult]:
        """Instala todas las dependencias según la configuración"""
        results = []
        total_packages = 0
        installed_count = 0

        try:
            # Contar total de paquetes
            for dep_type in self.install_config["install_order"]:
                if dep_type == "system":
                    total_packages += len(
                        dependencies_config.get("system_dependencies", {})
                    )
                elif dep_type == "python":
                    total_packages += len(
                        dependencies_config.get("python_dependencies", {})
                    )
                elif dep_type == "node":
                    total_packages += len(
                        dependencies_config.get("node_dependencies", {})
                    )

            logger.info(f"Iniciando instalación de {total_packages} dependencias...")

            # Instalar por tipo en orden
            for dep_type in self.install_config["install_order"]:
                if self.stop_installation:
                    logger.info("Instalación detenida por el usuario")
                    break

                logger.info(f"Instalando dependencias de tipo: {dep_type}")

                if dep_type == "system":
                    results.extend(
                        self._install_system_dependencies(
                            dependencies_config.get("system_dependencies", {}),
                            total_packages,
                            installed_count,
                        )
                    )
                elif dep_type == "python":
                    results.extend(
                        self._install_python_dependencies(
                            dependencies_config.get("python_dependencies", {}),
                            total_packages,
                            installed_count,
                        )
                    )
                elif dep_type == "node":
                    results.extend(
                        self._install_node_dependencies(
                            dependencies_config.get("node_dependencies", {}),
                            total_packages,
                            installed_count,
                        )
                    )

                installed_count = len([r for r in results if r.success])

            logger.info(
                f"Instalación completada. {installed_count}/{total_packages} paquetes instalados exitosamente"
            )
            return results

        except Exception as e:
            logger.error(f"Error en instalación masiva: {e}")
            return results

    def _install_system_dependencies(
        self, system_deps: Dict[str, Any], total: int, current: int
    ) -> List[InstallationResult]:
        """Instala dependencias del sistema"""
        results = []

        for package_name, config in system_deps.items():
            if self.stop_installation:
                break

            if (
                config.get("required", False)
                or not self.install_config["skip_optional"]
            ):
                self._update_progress(
                    current + len(results), total, package_name, "system"
                )

                result = self.install_system_dependency(package_name)
                results.append(result)
                self._log_installation(result)

                if result.success:
                    logger.info(f"Sistema: {package_name} instalado exitosamente")
                else:
                    logger.error(f"Sistema: {package_name} falló en instalación")

        return results

    def _install_python_dependencies(
        self, python_deps: Dict[str, Any], total: int, current: int
    ) -> List[InstallationResult]:
        """Instala dependencias de Python"""
        results = []

        # Instalar en paralelo usando ThreadPoolExecutor
        with ThreadPoolExecutor(
            max_workers=self.install_config["max_workers"]
        ) as executor:
            futures = []

            for package_name, config in python_deps.items():
                if self.stop_installation:
                    break

                if (
                    config.get("required", False)
                    or not self.install_config["skip_optional"]
                ):
                    future = executor.submit(
                        self.install_python_dependency,
                        package_name,
                        config.get("version"),
                    )
                    futures.append((package_name, future))

            # Recolectar resultados
            for package_name, future in futures:
                if self.stop_installation:
                    break

                try:
                    result = future.result(timeout=self.install_config["timeout"])
                    results.append(result)
                    self._log_installation(result)

                    current += 1
                    self._update_progress(current, total, package_name, "python")

                    if result.success:
                        logger.info(f"Python: {package_name} instalado exitosamente")
                    else:
                        logger.error(f"Python: {package_name} falló en instalación")

                except Exception as e:
                    logger.error(f"Error procesando {package_name}: {e}")
                    results.append(
                        InstallationResult(
                            package_name=package_name,
                            package_type="python",
                            success=False,
                            version_installed=None,
                            error_message=str(e),
                            installation_time=0,
                            dependencies_installed=[],
                        )
                    )

        return results

    def _install_node_dependencies(
        self, node_deps: Dict[str, Any], total: int, current: int
    ) -> List[InstallationResult]:
        """Instala dependencias de Node.js"""
        results = []

        # Instalar en paralelo usando ThreadPoolExecutor
        with ThreadPoolExecutor(
            max_workers=self.install_config["max_workers"]
        ) as executor:
            futures = []

            for package_name, config in node_deps.items():
                if self.stop_installation:
                    break

                if (
                    config.get("required", False)
                    or not self.install_config["skip_optional"]
                ):
                    future = executor.submit(
                        self.install_node_dependency,
                        package_name,
                        config.get("version"),
                    )
                    futures.append((package_name, future))

            # Recolectar resultados
            for package_name, future in futures:
                if self.stop_installation:
                    break

                try:
                    result = future.result(timeout=self.install_config["timeout"])
                    results.append(result)
                    self._log_installation(result)

                    current += 1
                    self._update_progress(current, total, package_name, "node")

                    if result.success:
                        logger.info(f"Node.js: {package_name} instalado exitosamente")
                    else:
                        logger.error(f"Node.js: {package_name} falló en instalación")

                except Exception as e:
                    logger.error(f"Error procesando {package_name}: {e}")
                    results.append(
                        InstallationResult(
                            package_name=package_name,
                            package_type="node",
                            success=False,
                            version_installed=None,
                            error_message=str(e),
                            installation_time=0,
                            dependencies_installed=[],
                        )
                    )

        return results

    def _detect_os(self) -> str:
        """Detecta el sistema operativo"""
        try:
            with open("/etc/os-release", "r") as f:
                content = f.read().lower()
                if "ubuntu" in content or "debian" in content:
                    return "ubuntu"
                elif "centos" in content or "rhel" in content or "fedora" in content:
                    return "centos"
                else:
                    return "unknown"
        except:
            return "unknown"

    def _get_system_package_version(self, package_name: str) -> Optional[str]:
        """Obtiene la versión de un paquete del sistema"""
        try:
            result = subprocess.run(
                [package_name, "--version"], capture_output=True, text=True
            )
            if result.returncode == 0:
                return result.stdout.strip()
            return None
        except:
            return None

    def _get_python_package_version(self, package_name: str) -> Optional[str]:
        """Obtiene la versión de un paquete de Python"""
        try:
            import pkg_resources

            return pkg_resources.get_distribution(package_name).version
        except:
            return None

    def _get_node_package_version(self, package_name: str) -> Optional[str]:
        """Obtiene la versión de un paquete de Node.js"""
        try:
            result = subprocess.run(
                ["npm", "list", package_name],
                capture_output=True,
                text=True,
                cwd=self.deps_dir,
            )
            if result.returncode == 0:
                lines = result.stdout.split("\n")
                for line in lines:
                    if package_name in line and "@" in line:
                        return line.split("@")[1].split(" ")[0]
            return None
        except:
            return None

    def _extract_installed_dependencies(self, output: str) -> List[str]:
        """Extrae las dependencias instaladas del output"""
        dependencies = []
        lines = output.split("\n")

        for line in lines:
            if "Successfully installed" in line:
                # Extraer nombres de paquetes instalados
                packages = line.split("Successfully installed")[-1].strip().split()
                dependencies.extend(packages)

        return dependencies

    def stop_installation_process(self):
        """Detiene el proceso de instalación"""
        self.stop_installation = True
        logger.info("Deteniendo proceso de instalación...")

    def get_installation_summary(self) -> Dict[str, Any]:
        """Obtiene un resumen de la instalación"""
        total_installations = len(self.installation_log)
        successful_installations = len(
            [r for r in self.installation_log if r["success"]]
        )
        failed_installations = total_installations - successful_installations

        # Estadísticas por tipo
        python_installations = [
            r for r in self.installation_log if r["package_type"] == "python"
        ]
        node_installations = [
            r for r in self.installation_log if r["package_type"] == "node"
        ]
        system_installations = [
            r for r in self.installation_log if r["package_type"] == "system"
        ]

        # Tiempo total de instalación
        total_time = sum(r["installation_time"] for r in self.installation_log)

        # Paquetes fallidos
        failed_packages = [
            r["package_name"] for r in self.installation_log if not r["success"]
        ]

        return {
            "total_installations": total_installations,
            "successful_installations": successful_installations,
            "failed_installations": failed_installations,
            "success_rate": (
                (successful_installations / total_installations * 100)
                if total_installations > 0
                else 0
            ),
            "python_installations": len(python_installations),
            "node_installations": len(node_installations),
            "system_installations": len(system_installations),
            "total_installation_time": total_time,
            "failed_packages": failed_packages,
            "installation_log": self.installation_log,
        }

    def save_installation_report(self, filepath: str = None) -> str:
        """Guarda un reporte de instalación"""
        if filepath is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filepath = (
                self.deps_dir
                / "installation_reports"
                / f"installation_report_{timestamp}.json"
            )

        filepath = Path(filepath)
        filepath.parent.mkdir(parents=True, exist_ok=True)

        report_data = {
            "installation_summary": self.get_installation_summary(),
            "timestamp": datetime.now().isoformat(),
            "installer_version": "1.0.0",
        }

        with open(filepath, "w") as f:
            json.dump(report_data, f, indent=2)

        logger.info(f"Reporte de instalación guardado: {filepath}")
        return str(filepath)


# Instancia global del instalador
dependency_installer = DependencyInstaller()


def get_dependency_installer() -> DependencyInstaller:
    """Obtiene la instancia global del instalador de dependencias"""
    return dependency_installer


if __name__ == "__main__":
    # Ejemplo de uso
    installer = DependencyInstaller()

    # Configuración de dependencias de ejemplo
    dependencies_config = {
        "python_dependencies": {
            "requests": {"version": ">=2.25.0", "required": True},
            "numpy": {"version": ">=1.21.0", "required": True},
        },
        "node_dependencies": {"axios": {"version": "^0.27.0", "required": True}},
        "system_dependencies": {"git": {"version": ">=2.0", "required": True}},
    }

    # Instalar dependencias
    results = installer.install_all_dependencies(dependencies_config)

    # Mostrar resumen
    summary = installer.get_installation_summary()
    print(
        f"Instalación completada: {summary['successful_installations']}/{summary['total_installations']} exitosas"
    )

    # Guardar reporte
    installer.save_installation_report()
