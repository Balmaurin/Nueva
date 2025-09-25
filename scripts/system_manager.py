#!/usr/bin/env python3
"""
Gestor de Sistema Real para Sheily AI
=====================================
Sistema de gestión completo que maneja el estado del sistema
"""

import os
import sys
import json
import logging
import subprocess
import psutil
import time
import threading
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, Any, List, Optional, Tuple
import sqlite3
import signal
import shutil
import requests
import socket
import traceback

# Configurar logging con más detalles
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    filename="logs/system_manager.log",
    filemode="a",
)
logger = logging.getLogger(__name__)


def log_error(message: str, error: Exception = None):
    """Método centralizado para registro de errores"""
    error_details = f"{message}\n{traceback.format_exc()}" if error else message
    logger.error(error_details)

    # Opcional: Enviar notificación de error
    try:
        from monitoring.alert_manager import AlertManager

        alert_manager = AlertManager()
        alert_manager.process_alert(
            {
                "alert_type": "system_manager_error",
                "severity": "warning",
                "message": message,
            }
        )
    except Exception as notification_error:
        logger.error(f"Error enviando notificación de error: {notification_error}")


class SystemManager:
    """Gestor de sistema Sheily AI"""

    def __init__(self, db_path: str = "scripts/system.db"):
        self.db_path = db_path
        self.processes = {}
        self.services = {}
        self.is_running = False
        self.monitor_thread = None
        self.backend_url = "http://127.0.0.1:8000"
        self.frontend_url = "http://127.0.0.1:3000"

        # Crear directorio si no existe
        Path(self.db_path).parent.mkdir(parents=True, exist_ok=True)

        # Inicializar base de datos
        self._init_database()

        # Configurar señales
        signal.signal(signal.SIGINT, self._signal_handler)
        signal.signal(signal.SIGTERM, self._signal_handler)

    def _init_database(self):
        """Inicializar base de datos del sistema"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()

                # Tabla de servicios
                cursor.execute(
                    """
                    CREATE TABLE IF NOT EXISTS services (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        name TEXT UNIQUE NOT NULL,
                        command TEXT NOT NULL,
                        working_directory TEXT,
                        environment TEXT,
                        auto_start BOOLEAN DEFAULT FALSE,
                        enabled BOOLEAN DEFAULT TRUE,
                        status TEXT DEFAULT 'stopped',
                        pid INTEGER,
                        start_time DATETIME,
                        last_check DATETIME,
                        restart_count INTEGER DEFAULT 0,
                        max_restarts INTEGER DEFAULT 3,
                        health_check_url TEXT,
                        port INTEGER
                    )
                """
                )

                # Tabla de logs del sistema
                cursor.execute(
                    """
                    CREATE TABLE IF NOT EXISTS system_logs (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                        level TEXT NOT NULL,
                        service TEXT,
                        message TEXT NOT NULL,
                        details TEXT
                    )
                """
                )

                # Tabla de métricas del sistema
                cursor.execute(
                    """
                    CREATE TABLE IF NOT EXISTS system_metrics (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                        cpu_percent REAL,
                        memory_percent REAL,
                        disk_usage_percent REAL,
                        active_services INTEGER,
                        total_services INTEGER,
                        backend_status TEXT,
                        frontend_status TEXT,
                        docker_containers_running INTEGER
                    )
                """
                )

                # Tabla de módulos
                cursor.execute(
                    """
                    CREATE TABLE IF NOT EXISTS modules (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        name TEXT UNIQUE NOT NULL,
                        path TEXT NOT NULL,
                        status TEXT DEFAULT 'inactive',
                        last_modified DATETIME,
                        dependencies TEXT,
                        config TEXT,
                        enabled BOOLEAN DEFAULT TRUE
                    )
                """
                )

                conn.commit()
                logger.info("✅ Base de datos del sistema inicializada")

        except Exception as e:
            logger.error(f"❌ Error inicializando base de datos: {e}")

    def register_service(
        self,
        name: str,
        command: str,
        working_directory: str = None,
        environment: Dict[str, str] = None,
        auto_start: bool = False,
        health_check_url: str = None,
        port: int = None,
    ) -> bool:
        """Registrar un nuevo servicio"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()

                cursor.execute(
                    """
                    INSERT OR REPLACE INTO services 
                    (name, command, working_directory, environment, auto_start, health_check_url, port)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                """,
                    (
                        name,
                        command,
                        working_directory,
                        json.dumps(environment) if environment else None,
                        auto_start,
                        health_check_url,
                        port,
                    ),
                )

                conn.commit()
                logger.info(f"✅ Servicio '{name}' registrado")
                return True

        except Exception as e:
            log_error(f"❌ Error registrando servicio '{name}'", e)
            return False

    def start_service(self, name: str) -> bool:
        """Iniciar un servicio"""
        try:
            # Obtener información del servicio
            service_info = self._get_service_info(name)
            if not service_info:
                logger.error(f"❌ Servicio '{name}' no encontrado")
                return False

            # Verificar si ya está ejecutándose
            if service_info["status"] == "running":
                logger.warning(f"⚠️ Servicio '{name}' ya está ejecutándose")
                return True

            # Preparar comando
            cmd = service_info["command"]
            if service_info["working_directory"]:
                cmd = f"cd {service_info['working_directory']} && {cmd}"

            # Preparar entorno
            env = os.environ.copy()
            if service_info["environment"]:
                env.update(json.loads(service_info["environment"]))

            # Iniciar proceso
            process = subprocess.Popen(
                cmd,
                shell=True,
                env=env,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                preexec_fn=os.setsid,
            )

            # Esperar un momento para verificar que inició
            time.sleep(2)

            if process.poll() is None:
                # Proceso iniciado correctamente
                self._update_service_status(name, "running", process.pid)
                self._log_service_event(
                    name, "INFO", f"Servicio iniciado (PID: {process.pid})"
                )
                logger.info(f"✅ Servicio '{name}' iniciado (PID: {process.pid})")
                return True
            else:
                # Error al iniciar
                stdout, stderr = process.communicate()
                error_msg = stderr.decode() if stderr else "Error desconocido"
                self._log_service_event(
                    name, "ERROR", f"Error iniciando servicio: {error_msg}"
                )
                logger.error(f"❌ Error iniciando servicio '{name}': {error_msg}")
                return False

        except Exception as e:
            log_error(f"❌ Error iniciando servicio '{name}'", e)
            return False

    def stop_service(self, name: str, force: bool = False) -> bool:
        """Detener un servicio"""
        try:
            service_info = self._get_service_info(name)
            if not service_info:
                logger.error(f"❌ Servicio '{name}' no encontrado")
                return False

            if service_info["status"] != "running":
                logger.warning(f"⚠️ Servicio '{name}' no está ejecutándose")
                return True

            pid = service_info["pid"]
            if not pid:
                logger.error(f"❌ PID no encontrado para servicio '{name}'")
                return False

            # Intentar detener gracefully
            try:
                os.kill(pid, signal.SIGTERM)
                time.sleep(5)

                # Verificar si se detuvo
                if not self._is_process_running(pid):
                    self._update_service_status(name, "stopped", None)
                    self._log_service_event(name, "INFO", "Servicio detenido")
                    logger.info(f"✅ Servicio '{name}' detenido")
                    return True

                # Si no se detuvo y force=True, forzar detención
                if force:
                    os.kill(pid, signal.SIGKILL)
                    time.sleep(1)

                    if not self._is_process_running(pid):
                        self._update_service_status(name, "stopped", None)
                        self._log_service_event(
                            name, "WARNING", "Servicio forzado a detener"
                        )
                        logger.info(f"✅ Servicio '{name}' forzado a detener")
                        return True

                logger.error(f"❌ No se pudo detener servicio '{name}'")
                return False

            except ProcessLookupError:
                # Proceso ya no existe
                self._update_service_status(name, "stopped", None)
                logger.info(f"✅ Servicio '{name}' ya estaba detenido")
                return True

        except Exception as e:
            log_error(f"❌ Error deteniendo servicio '{name}'", e)
            return False

    def restart_service(self, name: str) -> bool:
        """Reiniciar un servicio"""
        logger.info(f"🔄 Reiniciando servicio '{name}'...")

        # Detener servicio
        if not self.stop_service(name):
            logger.error(f"❌ No se pudo detener servicio '{name}' para reiniciar")
            return False

        # Esperar un momento
        time.sleep(2)

        # Iniciar servicio
        if not self.start_service(name):
            logger.error(
                f"❌ No se pudo iniciar servicio '{name}' después del reinicio"
            )
            return False

        logger.info(f"✅ Servicio '{name}' reiniciado correctamente")
        return True

    def get_service_status(self, name: str) -> Optional[Dict[str, Any]]:
        """Obtener estado de un servicio"""
        try:
            service_info = self._get_service_info(name)
            if not service_info:
                return None

            # Verificar si el proceso está realmente ejecutándose
            if service_info["status"] == "running" and service_info["pid"]:
                if not self._is_process_running(service_info["pid"]):
                    # Proceso murió, actualizar estado
                    self._update_service_status(name, "stopped", None)
                    service_info["status"] = "stopped"
                    service_info["pid"] = None

            # Verificar salud del servicio
            health_status = self._check_service_health(name)
            service_info["health"] = health_status

            return service_info

        except Exception as e:
            log_error(f"❌ Error obteniendo estado de servicio '{name}'", e)
            return None

    def get_all_services_status(self) -> List[Dict[str, Any]]:
        """Obtener estado de todos los servicios"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()

                cursor.execute("SELECT name FROM services WHERE enabled = TRUE")
                service_names = [row[0] for row in cursor.fetchall()]

                services_status = []
                for name in service_names:
                    status = self.get_service_status(name)
                    if status:
                        services_status.append(status)

                return services_status

        except Exception as e:
            log_error(f"❌ Error obteniendo estado de servicios", e)
            return []

    def start_all_services(self) -> Dict[str, bool]:
        """Iniciar todos los servicios habilitados"""
        results = {}

        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()

                cursor.execute(
                    """
                    SELECT name FROM services 
                    WHERE enabled = TRUE AND auto_start = TRUE
                """
                )

                service_names = [row[0] for row in cursor.fetchall()]

                for name in service_names:
                    logger.info(f"🚀 Iniciando servicio '{name}'...")
                    success = self.start_service(name)
                    results[name] = success

                    if success:
                        logger.info(f"✅ Servicio '{name}' iniciado")
                    else:
                        logger.error(f"❌ Error iniciando servicio '{name}'")

                return results

        except Exception as e:
            log_error(f"❌ Error iniciando servicios", e)
            return results

    def stop_all_services(self) -> Dict[str, bool]:
        """Detener todos los servicios"""
        results = {}

        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()

                cursor.execute(
                    """
                    SELECT name FROM services 
                    WHERE enabled = TRUE AND status = 'running'
                """
                )

                service_names = [row[0] for row in cursor.fetchall()]

                for name in service_names:
                    logger.info(f"🛑 Deteniendo servicio '{name}'...")
                    success = self.stop_service(name)
                    results[name] = success

                    if success:
                        logger.info(f"✅ Servicio '{name}' detenido")
                    else:
                        logger.error(f"❌ Error deteniendo servicio '{name}'")

                return results

        except Exception as e:
            log_error(f"❌ Error deteniendo servicios", e)
            return results

    def start_monitoring(self):
        """Iniciar monitoreo del sistema"""
        if self.is_running:
            logger.warning("⚠️ El monitoreo ya está ejecutándose")
            return

        self.is_running = True
        self.monitor_thread = threading.Thread(target=self._monitor_loop)
        self.monitor_thread.daemon = True
        self.monitor_thread.start()

        logger.info("🚀 Monitoreo del sistema iniciado")

    def stop_monitoring(self):
        """Detener monitoreo del sistema"""
        self.is_running = False
        if self.monitor_thread:
            self.monitor_thread.join()
        logger.info("🛑 Monitoreo del sistema detenido")

    def _monitor_loop(self):
        """Bucle de monitoreo"""
        while self.is_running:
            try:
                # Verificar salud de servicios
                self._check_services_health()

                # Registrar métricas del sistema
                self._record_system_metrics()

                # Esperar antes de la siguiente verificación
                time.sleep(30)  # Verificar cada 30 segundos

            except Exception as e:
                log_error("❌ Error en bucle de monitoreo", e)
                time.sleep(30)

    def _check_services_health(self):
        """Verificar salud de todos los servicios"""
        try:
            services = self.get_all_services_status()

            for service in services:
                name = service["name"]
                status = service["status"]

                # Verificar servicios que deberían estar ejecutándose
                if service.get("auto_start") and status == "stopped":
                    logger.warning(
                        f"⚠️ Servicio '{name}' debería estar ejecutándose, reiniciando..."
                    )
                    self.restart_service(name)

                # Verificar servicios con demasiados reinicios
                restart_count = service.get("restart_count", 0)
                max_restarts = service.get("max_restarts", 3)

                if restart_count >= max_restarts:
                    logger.error(f"❌ Servicio '{name}' excedió el límite de reinicios")
                    self._log_service_event(
                        name,
                        "ERROR",
                        f"Excedido límite de reinicios ({restart_count}/{max_restarts})",
                    )

        except Exception as e:
            log_error(f"❌ Error verificando salud de servicios", e)

    def _record_system_metrics(self):
        """Registrar métricas del sistema"""
        try:
            # Métricas del sistema
            cpu_percent = psutil.cpu_percent()
            memory = psutil.virtual_memory()
            disk = psutil.disk_usage("/")

            # Contar servicios activos
            services = self.get_all_services_status()
            active_services = len([s for s in services if s["status"] == "running"])
            total_services = len(services)

            # Estado de servicios principales
            backend_status = self._check_service_status_url(self.backend_url)
            frontend_status = self._check_service_status_url(self.frontend_url)

            # Contenedores Docker
            docker_containers = self._count_docker_containers()

            # Guardar métricas
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()

                cursor.execute(
                    """
                    INSERT INTO system_metrics 
                    (cpu_percent, memory_percent, disk_usage_percent, active_services, total_services,
                     backend_status, frontend_status, docker_containers_running)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """,
                    (
                        cpu_percent,
                        memory.percent,
                        (disk.used / disk.total) * 100,
                        active_services,
                        total_services,
                        backend_status,
                        frontend_status,
                        docker_containers,
                    ),
                )

                conn.commit()

        except Exception as e:
            log_error(f"❌ Error registrando métricas del sistema", e)

    def _check_service_status_url(self, url: str) -> str:
        """Verificar estado de un servicio por URL"""
        try:
            response = requests.get(url, timeout=5)
            if response.status_code == 200:
                return "running"
            else:
                return f"error_{response.status_code}"
        except requests.exceptions.RequestException:
            return "down"

    def _count_docker_containers(self) -> int:
        """Contar contenedores Docker en ejecución"""
        try:
            result = subprocess.run(
                ["docker", "ps", "--format", "{{.Names}}"],
                capture_output=True,
                text=True,
                timeout=10,
            )
            if result.returncode == 0:
                containers = result.stdout.strip().split("\n")
                return len([c for c in containers if c])
            return 0
        except (subprocess.TimeoutExpired, FileNotFoundError):
            return 0

    def _check_service_health(self, name: str) -> str:
        """Verificar salud de un servicio específico"""
        try:
            service_info = self._get_service_info(name)
            if not service_info:
                return "unknown"

            # Verificar por URL de salud
            health_url = service_info.get("health_check_url")
            if health_url:
                try:
                    response = requests.get(health_url, timeout=5)
                    if response.status_code == 200:
                        return "healthy"
                    else:
                        return f"unhealthy_{response.status_code}"
                except requests.exceptions.RequestException:
                    return "unhealthy"

            # Verificar por puerto
            port = service_info.get("port")
            if port:
                if self._is_port_open(port):
                    return "healthy"
                else:
                    return "unhealthy"

            # Verificar proceso
            pid = service_info.get("pid")
            if pid and self._is_process_running(pid):
                return "healthy"
            else:
                return "unhealthy"

        except Exception as e:
            log_error(f"❌ Error verificando salud de '{name}'", e)
            return "unknown"

    def _is_port_open(self, port: int) -> bool:
        """Verificar si un puerto está abierto"""
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.settimeout(5)
                result = s.connect_ex(("localhost", port))
                return result == 0
        except:
            return False

    def _is_process_running(self, pid: int) -> bool:
        """Verificar si un proceso está ejecutándose"""
        try:
            os.kill(pid, 0)
            return True
        except OSError:
            return False

    def _get_service_info(self, name: str) -> Optional[Dict[str, Any]]:
        """Obtener información de un servicio"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()

                cursor.execute(
                    """
                    SELECT name, command, working_directory, environment, auto_start, 
                           enabled, status, pid, start_time, last_check, restart_count, 
                           max_restarts, health_check_url, port
                    FROM services WHERE name = ?
                """,
                    (name,),
                )

                row = cursor.fetchone()
                if row:
                    return {
                        "name": row[0],
                        "command": row[1],
                        "working_directory": row[2],
                        "environment": json.loads(row[3]) if row[3] else None,
                        "auto_start": bool(row[4]),
                        "enabled": bool(row[5]),
                        "status": row[6],
                        "pid": row[7],
                        "start_time": row[8],
                        "last_check": row[9],
                        "restart_count": row[10],
                        "max_restarts": row[11],
                        "health_check_url": row[12],
                        "port": row[13],
                    }
                return None

        except Exception as e:
            log_error(f"❌ Error obteniendo información de servicio '{name}'", e)
            return None

    def _update_service_status(self, name: str, status: str, pid: Optional[int]):
        """Actualizar estado de un servicio"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()

                cursor.execute(
                    """
                    UPDATE services 
                    SET status = ?, pid = ?, last_check = ?
                    WHERE name = ?
                """,
                    (status, pid, datetime.now().isoformat(), name),
                )

                conn.commit()

        except Exception as e:
            log_error(f"❌ Error actualizando estado de servicio '{name}'", e)

    def _update_last_check(self, name: str):
        """Actualizar última verificación de un servicio"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()

                cursor.execute(
                    """
                    UPDATE services 
                    SET last_check = ?
                    WHERE name = ?
                """,
                    (datetime.now().isoformat(), name),
                )

                conn.commit()

        except Exception as e:
            log_error(f"❌ Error actualizando última verificación de '{name}'", e)

    def _increment_restart_count(self, name: str):
        """Incrementar contador de reinicios de un servicio"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()

                cursor.execute(
                    """
                    UPDATE services 
                    SET restart_count = restart_count + 1
                    WHERE name = ?
                """,
                    (name,),
                )

                conn.commit()

        except Exception as e:
            log_error(f"❌ Error incrementando contador de reinicios de '{name}'", e)

    def _log_service_event(
        self, service: str, level: str, message: str, details: str = None
    ):
        """Registrar evento de servicio"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()

                cursor.execute(
                    """
                    INSERT INTO system_logs (level, service, message, details)
                    VALUES (?, ?, ?, ?)
                """,
                    (level, service, message, details),
                )

                conn.commit()

        except Exception as e:
            log_error(f"❌ Error registrando evento de servicio", e)

    def _signal_handler(self, signum, frame):
        """Manejador de señales del sistema"""
        logger.info(f"🛑 Recibida señal {signum}, deteniendo sistema...")
        self.stop_all_services()
        self.stop_monitoring()
        sys.exit(0)

    def create_backup(self, backup_path: str = None) -> str:
        """Crear backup del sistema"""
        try:
            if not backup_path:
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                backup_path = f"backups/system_backup_{timestamp}.db"

            # Crear directorio de backup si no existe
            Path(backup_path).parent.mkdir(parents=True, exist_ok=True)

            # Copiar base de datos
            shutil.copy2(self.db_path, backup_path)

            logger.info(f"✅ Backup creado: {backup_path}")
            return backup_path

        except Exception as e:
            log_error(f"❌ Error creando backup", e)
            return ""

    def restore_backup(self, backup_path: str) -> bool:
        """Restaurar backup del sistema"""
        try:
            if not os.path.exists(backup_path):
                logger.error(f"❌ Archivo de backup no encontrado: {backup_path}")
                return False

            # Crear backup del estado actual antes de restaurar
            current_backup = self.create_backup()

            # Restaurar backup
            shutil.copy2(backup_path, self.db_path)

            logger.info(f"✅ Backup restaurado desde: {backup_path}")
            return True

        except Exception as e:
            log_error(f"❌ Error restaurando backup", e)
            return False

    def get_system_info(self) -> Dict[str, Any]:
        """Obtener información completa del sistema"""
        try:
            # Información del sistema
            system_info = {
                "hostname": socket.gethostname(),
                "platform": sys.platform,
                "python_version": sys.version,
                "cpu_count": psutil.cpu_count(),
                "memory_total": psutil.virtual_memory().total,
                "disk_total": psutil.disk_usage("/").total,
                "uptime": time.time() - psutil.boot_time(),
            }

            # Estado de servicios
            services = self.get_all_services_status()
            system_info["services"] = services
            system_info["active_services"] = len(
                [s for s in services if s["status"] == "running"]
            )
            system_info["total_services"] = len(services)

            # Métricas actuales
            system_info["cpu_percent"] = psutil.cpu_percent()
            system_info["memory_percent"] = psutil.virtual_memory().percent
            system_info["disk_percent"] = (
                psutil.disk_usage("/").used / psutil.disk_usage("/").total
            ) * 100

            # Estado de servicios principales
            system_info["backend_status"] = self._check_service_status_url(
                self.backend_url
            )
            system_info["frontend_status"] = self._check_service_status_url(
                self.frontend_url
            )
            system_info["docker_containers"] = self._count_docker_containers()

            return system_info

        except Exception as e:
            log_error(f"❌ Error obteniendo información del sistema", e)
            return {}


def main():
    """Función principal para testing"""
    system_manager = SystemManager()

    try:
        # Iniciar servicios críticos
        services_to_start = ["backend", "frontend", "monitoring"]
        for service in services_to_start:
            try:
                success = system_manager.start_service(service)
                print(f"Servicio {service}: {'✅ Iniciado' if success else '❌ Error'}")
            except Exception as e:
                log_error(f"❌ Error iniciando servicio {service}", e)
    except Exception as e:
        log_error("❌ Error en inicialización del sistema", e)


if __name__ == "__main__":
    main()
