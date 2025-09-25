import os
import json
import logging
import socket
import traceback
from datetime import datetime
from typing import Dict, Any, Optional


class StructuredLogger:
    def __init__(
        self, service_name: str, log_dir: str = "logs", log_level: int = logging.INFO
    ):
        """
        Logger estructurado con salida JSON

        Args:
            service_name (str): Nombre del servicio
            log_dir (str): Directorio para almacenar logs
            log_level (int): Nivel de logging
        """
        # Crear directorio de logs
        os.makedirs(log_dir, exist_ok=True)

        # Configuración básica
        self.service_name = service_name
        self.hostname = socket.gethostname()
        self.log_dir = log_dir

        # Configurar logger
        self.logger = logging.getLogger(service_name)
        self.logger.setLevel(log_level)

        # Manejadores de log
        self._setup_handlers()

    def _setup_handlers(self):
        """
        Configurar manejadores de log
        """
        # Manejador de archivo JSON
        json_handler = logging.FileHandler(
            os.path.join(
                self.log_dir,
                f"{self.service_name}_structured_{datetime.now().strftime('%Y%m%d')}.jsonl",
            )
        )
        json_handler.setFormatter(logging.Formatter("%(message)s"))

        # Manejador de consola
        console_handler = logging.StreamHandler()
        console_handler.setFormatter(
            logging.Formatter("%(asctime)s - %(levelname)s: %(message)s")
        )

        # Limpiar manejadores existentes
        self.logger.handlers.clear()

        # Añadir manejadores
        self.logger.addHandler(json_handler)
        self.logger.addHandler(console_handler)

    def _create_log_entry(
        self, level: str, message: str, extra_fields: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Crear entrada de log estructurada

        Args:
            level (str): Nivel de log
            message (str): Mensaje de log
            extra_fields (dict, opcional): Campos adicionales

        Returns:
            Diccionario de entrada de log
        """
        log_entry = {
            "timestamp": datetime.now().isoformat(),
            "level": level,
            "service": self.service_name,
            "hostname": self.hostname,
            "message": message,
        }

        if extra_fields:
            log_entry.update(extra_fields)

        return log_entry

    def info(self, message: str, extra_fields: Optional[Dict[str, Any]] = None):
        """
        Registrar log de información

        Args:
            message (str): Mensaje de log
            extra_fields (dict, opcional): Campos adicionales
        """
        log_entry = self._create_log_entry("INFO", message, extra_fields)
        self.logger.info(json.dumps(log_entry, ensure_ascii=False))

    def warning(self, message: str, extra_fields: Optional[Dict[str, Any]] = None):
        """
        Registrar log de advertencia

        Args:
            message (str): Mensaje de log
            extra_fields (dict, opcional): Campos adicionales
        """
        log_entry = self._create_log_entry("WARNING", message, extra_fields)
        self.logger.warning(json.dumps(log_entry, ensure_ascii=False))

    def error(
        self,
        message: str,
        exception: Optional[Exception] = None,
        extra_fields: Optional[Dict[str, Any]] = None,
    ):
        """
        Registrar log de error

        Args:
            message (str): Mensaje de log
            exception (Exception, opcional): Excepción capturada
            extra_fields (dict, opcional): Campos adicionales
        """
        error_details = {
            "error_type": type(exception).__name__ if exception else None,
            "error_message": str(exception) if exception else None,
            "traceback": traceback.format_exc() if exception else None,
        }

        log_entry = self._create_log_entry(
            "ERROR", message, {**error_details, **(extra_fields or {})}
        )

        self.logger.error(json.dumps(log_entry, ensure_ascii=False))

    def critical(
        self,
        message: str,
        exception: Optional[Exception] = None,
        extra_fields: Optional[Dict[str, Any]] = None,
    ):
        """
        Registrar log crítico

        Args:
            message (str): Mensaje de log
            exception (Exception, opcional): Excepción capturada
            extra_fields (dict, opcional): Campos adicionales
        """
        error_details = {
            "error_type": type(exception).__name__ if exception else None,
            "error_message": str(exception) if exception else None,
            "traceback": traceback.format_exc() if exception else None,
        }

        log_entry = self._create_log_entry(
            "CRITICAL", message, {**error_details, **(extra_fields or {})}
        )

        self.logger.critical(json.dumps(log_entry, ensure_ascii=False))


# Función de configuración global
def configure_logging(
    service_name: str = "sheily-ai",
    log_dir: str = "logs",
    log_level: int = logging.INFO,
) -> StructuredLogger:
    """
    Configurar logging global para el proyecto

    Args:
        service_name (str): Nombre del servicio
        log_dir (str): Directorio de logs
        log_level (int): Nivel de logging

    Returns:
        StructuredLogger configurado
    """
    return StructuredLogger(service_name, log_dir, log_level)
