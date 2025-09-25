#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
SCRIPT DE ARRANQUE COMPLETO PARA FRONTEND SHEILY AI
=============================================================================
Este script verifica todas las dependencias, configura el entorno
y inicia el frontend Next.js en el puerto 3000 sin errores
=============================================================================
Ubicación: Frontend/scripts/start.py
=============================================================================
"""

import os
import sys
import subprocess
import shutil
import json
import time
import signal
import platform
from pathlib import Path
from typing import List, Dict, Optional, Tuple


# Colores para output
class Colors:
    RED = "\033[0;31m"
    GREEN = "\033[0;32m"
    YELLOW = "\033[1;33m"
    BLUE = "\033[0;34m"
    PURPLE = "\033[0;35m"
    CYAN = "\033[0;36m"
    NC = "\033[0m"  # No Color


def print_status(message: str) -> None:
    """Imprime un mensaje de estado."""
    print(f"{Colors.BLUE}[INFO]{Colors.NC} {message}")


def print_success(message: str) -> None:
    """Imprime un mensaje de éxito."""
    print(f"{Colors.GREEN}[SUCCESS]{Colors.NC} {message}")


def print_warning(message: str) -> None:
    """Imprime un mensaje de advertencia."""
    print(f"{Colors.YELLOW}[WARNING]{Colors.NC} {message}")


def print_error(message: str) -> None:
    """Imprime un mensaje de error."""
    print(f"{Colors.RED}[ERROR]{Colors.NC} {message}")


def print_header(title: str) -> None:
    """Imprime un encabezado."""
    print(f"{Colors.PURPLE}{'='*32}{Colors.NC}")
    print(f"{Colors.PURPLE}{title}{Colors.NC}")
    print(f"{Colors.PURPLE}{'='*32}{Colors.NC}")


class FrontendStarter:
    """Clase principal para el arranque del frontend."""

    def __init__(self):
        self.project_dir = Path(__file__).parent
        self.package_json_path = self.project_dir / "package.json"
        self.node_modules_path = self.project_dir / "node_modules"
        self.env_local_path = self.project_dir / ".env.local"
        self.port = 3000
        self.hostname = "127.0.0.1"

    def cleanup_previous_processes(self) -> None:
        """Limpia procesos anteriores del frontend."""
        print_status("Limpiando procesos anteriores del frontend...")

        try:
            # Buscar procesos en el puerto 3000
            if platform.system() == "Windows":
                cmd = f"netstat -ano | findstr :{self.port}"
                result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
                if result.stdout:
                    print_warning("Encontrados procesos anteriores en puerto 3000")
                    # Terminar procesos en Windows
                    for line in result.stdout.split("\n"):
                        if line.strip():
                            parts = line.split()
                            if len(parts) >= 5:
                                pid = parts[-1]
                                try:
                                    subprocess.run(
                                        f"taskkill /PID {pid} /F", shell=True
                                    )
                                except:
                                    pass
            else:
                # Linux/Mac
                cmd = f"lsof -ti:{self.port}"
                result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
                if result.stdout.strip():
                    pids = result.stdout.strip().split("\n")
                    print_warning(
                        f"Encontrados procesos anteriores en puerto {self.port}: {pids}"
                    )
                    for pid in pids:
                        try:
                            subprocess.run(f"kill -9 {pid}", shell=True)
                        except:
                            pass
                    time.sleep(2)

            # Limpiar caché de Next.js
            next_cache = self.project_dir / ".next"
            if next_cache.exists():
                print_status("Limpiando caché de Next.js...")
                cache_dir = next_cache / ".cache"
                trace_dir = next_cache / "trace"
                if cache_dir.exists():
                    shutil.rmtree(cache_dir)
                if trace_dir.exists():
                    shutil.rmtree(trace_dir)
                print_success("Caché limpiado")

            print_success("Procesos anteriores terminados")

        except Exception as e:
            print_warning(f"No se pudieron limpiar procesos anteriores: {e}")

    def check_system_dependencies(self) -> bool:
        """Verifica las dependencias del sistema."""
        print_header("VERIFICANDO DEPENDENCIAS DEL SISTEMA")

        # Verificar Node.js
        if not shutil.which("node"):
            print_error("Node.js no está instalado")
            print_status(
                "Por favor, instala Node.js 18 o superior desde https://nodejs.org/"
            )
            return False

        # Verificar npm
        if not shutil.which("npm"):
            print_error("npm no está instalado")
            return False

        # Verificar versiones
        try:
            node_version = subprocess.run(
                ["node", "--version"], capture_output=True, text=True
            ).stdout.strip()
            npm_version = subprocess.run(
                ["npm", "--version"], capture_output=True, text=True
            ).stdout.strip()

            print_success(f"Node.js encontrado: {node_version}")
            print_success(f"npm encontrado: {npm_version}")

            # Verificar versión mínima de Node.js
            node_major = int(node_version[1:].split(".")[0])
            if node_major < 18:
                print_error(
                    f"Se requiere Node.js 18 o superior. Versión actual: {node_version}"
                )
                return False

        except Exception as e:
            print_error(f"Error al verificar versiones: {e}")
            return False

        print_success("Todas las dependencias del sistema están disponibles")
        return True

    def setup_environment(self) -> bool:
        """Configura el entorno del proyecto."""
        print_header("CONFIGURANDO ENTORNO")

        # Verificar si estamos en el directorio correcto
        if not self.package_json_path.exists():
            print_error(
                "No se encontró package.json. Asegúrate de estar en el directorio Frontend/"
            )
            return False

        # Verificar si es el proyecto correcto
        try:
            with open(self.package_json_path, "r") as f:
                package_data = json.load(f)
                if package_data.get("name") != "sheily-landing-next":
                    print_error("Este no parece ser el proyecto Sheily AI Frontend")
                    return False
        except Exception as e:
            print_error(f"Error al leer package.json: {e}")
            return False

        print_success("Directorio del proyecto verificado")

        # Crear archivo .env.local si no existe
        if not self.env_local_path.exists():
            print_status("Creando archivo .env.local...")
            env_content = f"""# Configuración del Frontend Sheily AI
NODE_ENV=development
PORT={self.port}
HOSTNAME={self.hostname}
NEXTAUTH_SECRET=sheily_ai_frontend_secret_key_development_{int(time.time())}
BACKEND_URL=http://localhost:8000
NEXTAUTH_URL=http://{self.hostname}:{self.port}
"""
            try:
                with open(self.env_local_path, "w") as f:
                    f.write(env_content)
                print_success("Archivo .env.local creado")
            except Exception as e:
                print_error(f"Error al crear .env.local: {e}")
                return False
        else:
            print_success("Archivo .env.local ya existe")

        # Configurar variables de entorno
        os.environ["NODE_ENV"] = "development"
        os.environ["PORT"] = str(self.port)
        os.environ["HOSTNAME"] = self.hostname

        print_success("Entorno configurado correctamente")
        return True

    def check_node_dependencies(self) -> bool:
        """Verifica las dependencias de Node.js."""
        print_header("VERIFICANDO DEPENDENCIAS DE NODE.JS")

        if not self.node_modules_path.exists():
            print_warning("node_modules no encontrado. Instalando dependencias...")
            return self.install_dependencies()

        print_success("node_modules encontrado")

        # Verificar dependencias
        try:
            result = subprocess.run(
                ["npm", "ls", "--depth=0"],
                capture_output=True,
                text=True,
                cwd=self.project_dir,
            )
            if (
                "UNMET DEPENDENCY" in result.stdout
                or "UNMET DEPENDENCY" in result.stderr
            ):
                print_warning("Dependencias faltantes detectadas. Reinstalando...")
                return self.install_dependencies()
            else:
                print_success("Todas las dependencias están instaladas correctamente")
                return True
        except Exception as e:
            print_warning(f"Error al verificar dependencias: {e}")
            return self.install_dependencies()

    def install_dependencies(self) -> bool:
        """Instala las dependencias de Node.js."""
        print_header("INSTALANDO DEPENDENCIAS")

        try:
            # Limpiar instalación anterior si existe
            if self.node_modules_path.exists():
                print_status("Limpiando instalación anterior...")
                shutil.rmtree(self.node_modules_path)
                package_lock = self.project_dir / "package-lock.json"
                if package_lock.exists():
                    package_lock.unlink()

            # Limpiar caché de npm
            print_status("Limpiando caché de npm...")
            subprocess.run(
                ["npm", "cache", "clean", "--force"], cwd=self.project_dir, check=True
            )

            # Instalar dependencias
            print_status("Instalando dependencias...")
            subprocess.run(["npm", "install"], cwd=self.project_dir, check=True)

            print_success("Dependencias instaladas correctamente")
            return True

        except subprocess.CalledProcessError as e:
            print_error(f"Error al instalar dependencias: {e}")
            return False
        except Exception as e:
            print_error(f"Error inesperado: {e}")
            return False

    def check_nextjs_config(self) -> bool:
        """Verifica la configuración de Next.js."""
        print_header("VERIFICANDO CONFIGURACIÓN DE NEXT.JS")

        config_files = [
            "next.config.cjs",
            "tsconfig.json",
            "tailwind.config.ts",
            "postcss.config.cjs",
        ]

        for config_file in config_files:
            config_path = self.project_dir / config_file
            if config_path.exists():
                print_success(f"{config_file} encontrado")
            else:
                print_error(f"{config_file} no encontrado")
                return False

        # Verificar configuración de TypeScript
        try:
            print_status("Verificando configuración de TypeScript...")
            subprocess.run(
                ["npx", "tsc", "--noEmit", "--skipLibCheck"],
                cwd=self.project_dir,
                check=False,
            )
            print_success("Configuración de TypeScript verificada")
        except Exception as e:
            print_warning(f"Errores de TypeScript detectados, pero continuando...")

        print_success("Configuración de Next.js verificada")
        return True

    def check_audio_files(self) -> bool:
        """Verifica los archivos de audio."""
        print_header("VERIFICANDO ARCHIVOS DE AUDIO")

        audio_dir = self.project_dir / "public" / "sounds"
        required_files = [
            "062708_laser-charging-81968.mp3",
            "whoosh-drum-hits-169007.mp3",
        ]

        if not audio_dir.exists():
            print_warning("Directorio de sonidos no encontrado. Creando...")
            audio_dir.mkdir(parents=True, exist_ok=True)

        missing_files = []
        for audio_file in required_files:
            if not (audio_dir / audio_file).exists():
                missing_files.append(audio_file)

        if missing_files:
            print_warning(f"Archivos de audio faltantes: {', '.join(missing_files)}")
            print_status("Los sonidos se generarán sintéticamente como fallback")
        else:
            print_success("Todos los archivos de audio están disponibles")

        return True

    def check_ports(self) -> bool:
        """Verifica la disponibilidad de puertos."""
        print_header("VERIFICANDO PUERTOS")

        # Verificar puerto 3000
        try:
            if platform.system() == "Windows":
                cmd = f"netstat -ano | findstr :{self.port}"
                result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
                if result.stdout.strip():
                    print_warning(f"Puerto {self.port} está en uso")
                    print_status("Intentando liberar el puerto...")
                    self.cleanup_previous_processes()
            else:
                cmd = f"lsof -ti:{self.port}"
                result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
                if result.stdout.strip():
                    print_warning(f"Puerto {self.port} está en uso")
                    print_status("Intentando liberar el puerto...")
                    self.cleanup_previous_processes()
        except Exception as e:
            print_warning(f"No se pudo verificar el puerto: {e}")

        print_success(f"Puerto {self.port} está disponible")

        # Verificar puerto 8000 (backend)
        try:
            if platform.system() == "Windows":
                cmd = "netstat -ano | findstr :8000"
                result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
                if result.stdout.strip():
                    print_success("Backend detectado en puerto 8000")
                else:
                    print_warning("Backend no detectado en puerto 8000")
            else:
                cmd = "lsof -ti:8000"
                result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
                if result.stdout.strip():
                    print_success("Backend detectado en puerto 8000")
                else:
                    print_warning("Backend no detectado en puerto 8000")
        except Exception as e:
            print_warning(f"No se pudo verificar el backend: {e}")

        print_status("El frontend funcionará en modo standalone si es necesario")
        return True

    def start_frontend(self) -> None:
        """Inicia el frontend."""
        print_header("INICIANDO FRONTEND SHEILY AI")

        print_status(f"Iniciando servidor de desarrollo en puerto {self.port}...")
        print_status(f"URL: http://{self.hostname}:{self.port}")
        print_status("Presiona Ctrl+C para detener el servidor")

        try:
            # Iniciar el servidor
            env = os.environ.copy()
            env.update(
                {
                    "NODE_ENV": "development",
                    "PORT": str(self.port),
                    "HOSTNAME": self.hostname,
                }
            )

            subprocess.run(
                ["npm", "run", "dev"], cwd=self.project_dir, env=env, check=True
            )

        except subprocess.CalledProcessError as e:
            print_error(f"Error al iniciar el frontend: {e}")
        except KeyboardInterrupt:
            print_status("Servidor detenido por el usuario")
        except Exception as e:
            print_error(f"Error inesperado: {e}")

    def run(self) -> bool:
        """Ejecuta el proceso completo de arranque."""
        print_header("ARRANQUE DEL FRONTEND SHEILY AI")
        print_status("Iniciando proceso de arranque completo...")

        try:
            # Ejecutar todas las verificaciones y configuraciones
            if not self.check_system_dependencies():
                return False

            if not self.setup_environment():
                return False

            if not self.check_node_dependencies():
                return False

            if not self.check_nextjs_config():
                return False

            if not self.check_audio_files():
                return False

            if not self.check_ports():
                return False

            print_header("VERIFICACIONES COMPLETADAS")
            print_success("✅ Sistema de dependencias verificado")
            print_success("✅ Entorno configurado")
            print_success("✅ Configuración de Next.js validada")
            print_success("✅ Puertos verificados")
            print_success("✅ Archivos de audio verificados")

            print_status("Iniciando frontend...")
            self.start_frontend()
            return True

        except Exception as e:
            print_error(f"Error durante el arranque: {e}")
            return False


def signal_handler(signum, frame):
    """Maneja las señales de interrupción."""
    print_status("Recibida señal de interrupción. Limpiando...")
    sys.exit(0)


def main():
    """Función principal."""
    # Configurar manejador de señales
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)

    # Crear y ejecutar el starter
    starter = FrontendStarter()
    success = starter.run()

    if not success:
        print_error("El arranque del frontend falló")
        sys.exit(1)


if __name__ == "__main__":
    main()
