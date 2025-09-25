#!/usr/bin/env python3
"""
Sistema Completo de Inicio - Sheily AI
=====================================
Script maestro que inicia todos los servicios del sistema
"""

import os
import sys
import time
import subprocess
import signal
import logging
from pathlib import Path
from typing import List, Dict, Any
import threading
import requests
import json

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/system_startup.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class SheilySystemManager:
    """Gestor completo del sistema Sheily AI"""

    def __init__(self):
        self.base_dir = Path(__file__).parent
        self.processes: Dict[str, subprocess.Popen] = {}
        self.services = {
            'api_server': {
                'name': 'API Server',
                'command': [sys.executable, 'backend/main_server.py'],
                'cwd': self.base_dir,
                'env': {'API_PORT': '8002'},
                'port': 8002,
                'health_check': 'http://localhost:8002/health',
                'required': True
            },
            'llm_server': {
                'name': 'LLM Server (Llama-3.2)',
                'command': [sys.executable, 'backend/llm_server.py'],
                'cwd': self.base_dir,
                'port': 8001,
                'health_check': 'http://localhost:8001/health',
                'required': False  # Opcional por ahora
            },
            'frontend': {
                'name': 'Frontend (Next.js)',
                'command': ['npm', 'run', 'dev'],
                'cwd': self.base_dir / 'Frontend',
                'port': 3000,
                'health_check': 'http://localhost:3000',
                'required': True
            }
        }

        self.running = False
        self.stop_event = threading.Event()

    def check_dependencies(self) -> bool:
        """Verificar dependencias del sistema"""
        logger.info("🔍 Verificando dependencias del sistema...")

        # Verificar Python
        try:
            import fastapi, uvicorn, sqlalchemy
            logger.info("✅ Dependencias de Python verificadas")
        except ImportError as e:
            logger.error(f"❌ Faltan dependencias de Python: {e}")
            return False

        # Verificar Node.js y npm
        try:
            result = subprocess.run(['node', '--version'], capture_output=True, text=True)
            if result.returncode != 0:
                raise Exception("Node.js no encontrado")

            result = subprocess.run(['npm', '--version'], capture_output=True, text=True)
            if result.returncode != 0:
                raise Exception("npm no encontrado")

            logger.info("✅ Node.js y npm verificados")
        except Exception as e:
            logger.error(f"❌ Error con Node.js/npm: {e}")
            return False

        # Verificar base de datos
        try:
            from backend.database_manager_complete import get_db_manager
            db = get_db_manager()
            info = db.get_database_info()
            if info.get('status') == 'connected':
                logger.info("✅ Base de datos conectada")
                db.close()
            else:
                logger.warning("⚠️ Base de datos no disponible, usando modo offline")
        except Exception as e:
            logger.error(f"❌ Error conectando a base de datos: {e}")
            return False

        return True

    def start_service(self, service_name: str) -> bool:
        """Iniciar un servicio específico"""
        if service_name not in self.services:
            logger.error(f"❌ Servicio desconocido: {service_name}")
            return False

        service = self.services[service_name]

        try:
            logger.info(f"🚀 Iniciando {service['name']}...")

            # Crear directorios necesarios
            log_dir = self.base_dir / 'logs'
            log_dir.mkdir(exist_ok=True)

            # Archivo de log para el servicio
            log_file = log_dir / f"{service_name}.log"

            # Preparar entorno
            env_vars = {**os.environ, 'PYTHONPATH': str(self.base_dir)}
            if 'env' in service:
                env_vars.update(service['env'])

            # Iniciar proceso
            with open(log_file, 'w') as logfile:
                process = subprocess.Popen(
                    service['command'],
                    cwd=service['cwd'],
                    stdout=logfile,
                    stderr=logfile,
                    env=env_vars
                )

            self.processes[service_name] = process

            # Esperar un poco para que inicie
            time.sleep(3)

            # Verificar si está corriendo
            if process.poll() is None:
                logger.info(f"✅ {service['name']} iniciado (PID: {process.pid})")

                # Health check si está definido
                if 'health_check' in service:
                    if self.wait_for_service(service['health_check'], timeout=30):
                        logger.info(f"✅ {service['name']} está saludable")
                        return True
                    else:
                        logger.warning(f"⚠️ {service['name']} iniciado pero health check falló")
                        if service.get('required', False):
                            return False
                        return True
                else:
                    return True
            else:
                logger.error(f"❌ {service['name']} falló al iniciar")
                return False

        except Exception as e:
            logger.error(f"❌ Error iniciando {service['name']}: {e}")
            return False

    def wait_for_service(self, url: str, timeout: int = 30) -> bool:
        """Esperar a que un servicio esté disponible"""
        start_time = time.time()

        while time.time() - start_time < timeout:
            try:
                response = requests.get(url, timeout=5)
                if response.status_code == 200:
                    return True
            except:
                pass

            time.sleep(1)

        return False

    def stop_service(self, service_name: str) -> bool:
        """Detener un servicio específico"""
        if service_name not in self.processes:
            return True

        process = self.processes[service_name]
        service = self.services[service_name]

        try:
            logger.info(f"🛑 Deteniendo {service['name']}...")

            # Enviar señal SIGTERM
            process.terminate()

            # Esperar a que termine
            try:
                process.wait(timeout=10)
                logger.info(f"✅ {service['name']} detenido correctamente")
                return True
            except subprocess.TimeoutExpired:
                # Si no responde, forzar terminación
                process.kill()
                process.wait()
                logger.warning(f"⚠️ {service['name']} forzado a detener")
                return True

        except Exception as e:
            logger.error(f"❌ Error deteniendo {service['name']}: {e}")
            return False

    def start_all_services(self) -> bool:
        """Iniciar todos los servicios"""
        logger.info("🚀 Iniciando sistema completo Sheily AI...")
        logger.info("=" * 50)

        success_count = 0
        total_count = len(self.services)

        for service_name, service in self.services.items():
            if self.start_service(service_name):
                success_count += 1
            elif service.get('required', False):
                logger.error(f"❌ Servicio requerido {service['name']} falló, abortando...")
                self.stop_all_services()
                return False

        logger.info(f"📊 Servicios iniciados: {success_count}/{total_count}")

        if success_count == total_count:
            logger.info("🎉 ¡Sistema Sheily AI completamente operativo!")
            self.print_service_status()
            return True
        else:
            logger.warning("⚠️ Sistema iniciado parcialmente")
            return True

    def stop_all_services(self):
        """Detener todos los servicios"""
        logger.info("🛑 Deteniendo todos los servicios...")

        for service_name in list(self.processes.keys()):
            self.stop_service(service_name)

        self.processes.clear()
        logger.info("✅ Todos los servicios detenidos")

    def print_service_status(self):
        """Mostrar estado de todos los servicios"""
        logger.info("\n📋 ESTADO DE SERVICIOS:")
        logger.info("-" * 40)

        for service_name, service in self.services.items():
            status = "✅ Activo" if service_name in self.processes and self.processes[service_name].poll() is None else "❌ Inactivo"
            port = service.get('port', 'N/A')
            logger.info(f"  {service['name']:<25} | {status:<10} | Puerto: {port}")

        logger.info("-" * 40)
        logger.info("🌐 URLs de acceso:")
        logger.info("  📱 Dashboard: http://localhost:3000")
        logger.info("  🔌 API: http://localhost:8002")
        logger.info("  📚 Documentación API: http://localhost:8002/docs")
        logger.info("  🧠 LLM Server: http://localhost:8001 (opcional)")

    def monitor_services(self):
        """Monitorear servicios en ejecución"""
        logger.info("👀 Iniciando monitoreo de servicios...")

        while not self.stop_event.is_set():
            # Verificar que todos los servicios estén corriendo
            for service_name, process in list(self.processes.items()):
                if process.poll() is not None:
                    service = self.services[service_name]
                    logger.warning(f"⚠️ Servicio {service['name']} se detuvo inesperadamente")

                    # Intentar reiniciar si es requerido
                    if service.get('required', False):
                        logger.info(f"🔄 Intentando reiniciar {service['name']}...")
                        if self.start_service(service_name):
                            logger.info(f"✅ {service['name']} reiniciado correctamente")
                        else:
                            logger.error(f"❌ Falló reinicio de {service['name']}")

            time.sleep(10)  # Verificar cada 10 segundos

    def create_default_config(self):
        """Crear configuración por defecto si no existe"""
        config_path = self.base_dir / 'config' / 'unified_config.json'

        if not config_path.exists():
            logger.info("📝 Creando configuración por defecto...")

            default_config = {
                "system": {
                    "name": "Sheily AI",
                    "version": "3.1.0",
                    "environment": "development"
                },
                "database": {
                    "type": "sqlite",
                    "sqlite_path": "data/sheily_ai.db",
                    "postgres_host": "localhost",
                    "postgres_port": 5432,
                    "postgres_name": "sheily_ai_db",
                    "postgres_user": "sheily_ai_user",
                    "postgres_password": ""
                },
                "api": {
                    "host": "0.0.0.0",
                    "port": 8000,
                    "cors_origins": ["http://localhost:3000", "http://localhost:3001"]
                },
                "llm": {
                    "model": "Llama-3.2-3B-Instruct-Q4_K_M",
                    "port": 8001,
                    "context_length": 4096,
                    "temperature": 0.7,
                    "top_p": 0.95
                },
                "frontend": {
                    "port": 3000,
                    "api_url": "http://localhost:8000"
                },
                "blockchain": {
                    "network": "solana",
                    "rpc_url": "https://api.mainnet-beta.solana.com",
                    "token_address": "TBD",
                    "phantom_integration": True
                },
                "branches": {
                    "count": 35,
                    "enabled_by_default": True,
                    "list": [
                        "lengua_y_lingüística", "matemáticas", "computación_y_programación",
                        "medicina_y_salud", "física", "química", "biología", "historia",
                        "geografía_y_geo_política", "economía_y_finanzas", "derecho_y_políticas_públicas",
                        "educación_y_pedagogía", "ingeniería", "empresa_y_emprendimiento",
                        "arte_música_y_cultura", "literatura_y_escritura", "medios_y_comunicación",
                        "deportes_y_esports", "juegos_y_entretenimiento", "cocina_y_nutrición",
                        "hogar_diy_y_reparaciones", "viajes_e_idiomas", "vida_diaria_legal_práctico_y_trámites",
                        "sociología_y_antropología", "neurociencia_y_psicología", "astronomía_y_espacio",
                        "ciencias_de_la_tierra_y_clima", "ciencia_de_datos_e_ia", "ciberseguridad_y_criptografía",
                        "electrónica_y_iot", "sistemas_devops_redes", "diseño_y_ux", "general",
                        "maestros_de_los_números", "sanadores_del_cuerpo_y_alma"
                    ]
                }
            }

            # Crear directorio
            config_path.parent.mkdir(parents=True, exist_ok=True)

            # Guardar configuración
            with open(config_path, 'w', encoding='utf-8') as f:
                json.dump(default_config, f, indent=2, ensure_ascii=False)

            logger.info("✅ Configuración por defecto creada")

    def run(self):
        """Ejecutar el sistema completo"""
        try:
            # Configurar signal handlers
            signal.signal(signal.SIGINT, self.signal_handler)
            signal.signal(signal.SIGTERM, self.signal_handler)

            # Crear configuración si no existe
            self.create_default_config()

            # Verificar dependencias
            if not self.check_dependencies():
                logger.error("❌ Verificación de dependencias falló")
                return False

            # Iniciar servicios
            if not self.start_all_services():
                logger.error("❌ Falló inicio de servicios")
                return False

            # Iniciar monitoreo
            self.running = True
            monitor_thread = threading.Thread(target=self.monitor_services, daemon=True)
            monitor_thread.start()

            logger.info("\n🎯 ¡SISTEMA SHEILY AI OPERATIVO!")
            logger.info("Presiona Ctrl+C para detener...")

            # Mantener vivo
            while self.running and not self.stop_event.is_set():
                time.sleep(1)

        except KeyboardInterrupt:
            logger.info("\n🛑 Interrupción detectada...")
        except Exception as e:
            logger.error(f"❌ Error en ejecución del sistema: {e}")
            import traceback
            traceback.print_exc()
        finally:
            self.stop_all_services()

        return True

    def signal_handler(self, signum, frame):
        """Manejador de señales"""
        logger.info(f"\n📡 Señal {signum} recibida, deteniendo sistema...")
        self.running = False
        self.stop_event.set()


def main():
    """Función principal"""
    print("🤖 SHEILY AI - SISTEMA COMPLETO")
    print("=" * 50)
    print("Iniciando todos los servicios del sistema...")
    print()

    # Crear directorio de logs
    log_dir = Path('logs')
    log_dir.mkdir(exist_ok=True)

    # Iniciar sistema
    manager = SheilySystemManager()
    success = manager.run()

    if success:
        print("\n✅ Sistema detenido correctamente")
    else:
        print("\n❌ Error en el sistema")
        sys.exit(1)


if __name__ == "__main__":
    main()
