#!/usr/bin/env python3
"""
Gestor de Exportación - Shaili AI

Este módulo proporciona funcionalidades completas para exportar datos
del sistema en diferentes formatos y con diferentes niveles de detalle.
"""

import json
import csv
import xml.etree.ElementTree as ET
import yaml
import sqlite3
import pandas as pd
from pathlib import Path
from datetime import datetime, timezone, timedelta
from typing import Dict, List, Any, Optional, Union
import logging
import hashlib
import zipfile
import shutil
from dataclasses import dataclass, asdict
import uuid


@dataclass
class ExportConfig:
    """Configuración para exportaciones"""

    format: str = "jsonl"  # jsonl, json, csv, xml, yaml
    include_pii: bool = False
    include_metadata: bool = True
    compress: bool = False
    encrypt: bool = False
    batch_size: int = 1000
    max_file_size: int = 100 * 1024 * 1024  # 100MB
    output_dir: str = "exports"
    backup_existing: bool = True


@dataclass
class ExportMetadata:
    """Metadatos de exportación"""

    export_id: str
    timestamp: str
    format: str
    total_records: int
    file_size: int
    checksum: str
    source: str
    version: str = "3.1.0"


class ExportManager:
    """Gestor principal de exportaciones del sistema"""

    def __init__(self, config: Optional[ExportConfig] = None):
        """
        Inicializar gestor de exportación

        Args:
            config: Configuración de exportación
        """
        self.config = config or ExportConfig()
        self.logger = logging.getLogger(__name__)
        self.export_history = []

        # Crear directorio de exportaciones
        self.export_dir = Path(self.config.output_dir)
        self.export_dir.mkdir(parents=True, exist_ok=True)

        # Configurar logging
        self._setup_logging()

    def _setup_logging(self):
        """Configurar logging para exportaciones"""
        log_dir = Path("logs/exports")
        log_dir.mkdir(parents=True, exist_ok=True)

        logging.basicConfig(
            level=logging.INFO,
            format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
            handlers=[
                logging.FileHandler(log_dir / "export_manager.log"),
                logging.StreamHandler(),
            ],
        )

    def _generate_export_id(self) -> str:
        """Generar ID único para la exportación"""
        return str(uuid.uuid4())

    def _calculate_checksum(self, file_path: Path) -> str:
        """Calcular checksum SHA-256 de un archivo"""
        sha256_hash = hashlib.sha256()
        with open(file_path, "rb") as f:
            for chunk in iter(lambda: f.read(4096), b""):
                sha256_hash.update(chunk)
        return sha256_hash.hexdigest()

    def _sanitize_filename(self, filename: str) -> str:
        """Sanitizar nombre de archivo"""
        import re

        # Remover caracteres no permitidos
        sanitized = re.sub(r'[<>:"/\\|?*]', "_", filename)
        # Limitar longitud
        return sanitized[:100]

    def export_user_data(
        self, user_id: str, data_types: List[str] = None
    ) -> Dict[str, Any]:
        """
        Exportar datos de usuario específico

        Args:
            user_id: ID del usuario
            data_types: Tipos de datos a exportar (profile, sessions, conversations, etc.)

        Returns:
            Diccionario con información de la exportación
        """
        self.logger.info(f"Iniciando exportación de datos para usuario {user_id}")

        export_id = self._generate_export_id()
        timestamp = datetime.now(timezone.utc).isoformat()

        # Obtener datos del usuario
        user_data = self._get_user_data(user_id, data_types)

        if not user_data:
            self.logger.warning(f"No se encontraron datos para el usuario {user_id}")
            return {"success": False, "error": "No data found"}

        # Generar nombre de archivo
        filename = self._sanitize_filename(
            f"user_{user_id}_export_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        )

        # Exportar datos
        export_result = self._export_data(user_data, filename, export_id, timestamp)

        # Registrar en historial
        self.export_history.append(
            {
                "export_id": export_id,
                "user_id": user_id,
                "timestamp": timestamp,
                "filename": export_result["filename"],
                "record_count": len(user_data),
            }
        )

        self.logger.info(f"Exportación completada: {export_result['filename']}")
        return export_result

    def export_system_data(
        self, data_types: List[str] = None, date_range: tuple = None
    ) -> Dict[str, Any]:
        """
        Exportar datos del sistema

        Args:
            data_types: Tipos de datos a exportar
            date_range: Rango de fechas (start_date, end_date)

        Returns:
            Diccionario con información de la exportación
        """
        self.logger.info("Iniciando exportación de datos del sistema")

        export_id = self._generate_export_id()
        timestamp = datetime.now(timezone.utc).isoformat()

        # Obtener datos del sistema
        system_data = self._get_system_data(data_types, date_range)

        if not system_data:
            self.logger.warning("No se encontraron datos del sistema para exportar")
            return {"success": False, "error": "No data found"}

        # Generar nombre de archivo
        filename = self._sanitize_filename(
            f"system_export_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        )

        # Exportar datos
        export_result = self._export_data(system_data, filename, export_id, timestamp)

        self.logger.info(
            f"Exportación del sistema completada: {export_result['filename']}"
        )
        return export_result

    def export_conversations(
        self, user_id: str = None, date_range: tuple = None
    ) -> Dict[str, Any]:
        """
        Exportar conversaciones

        Args:
            user_id: ID del usuario (opcional, si no se especifica exporta todas)
            date_range: Rango de fechas (start_date, end_date)

        Returns:
            Diccionario con información de la exportación
        """
        self.logger.info("Iniciando exportación de conversaciones")

        export_id = self._generate_export_id()
        timestamp = datetime.now(timezone.utc).isoformat()

        # Obtener conversaciones
        conversations = self._get_conversations(user_id, date_range)

        if not conversations:
            self.logger.warning("No se encontraron conversaciones para exportar")
            return {"success": False, "error": "No conversations found"}

        # Generar nombre de archivo
        user_suffix = f"_user_{user_id}" if user_id else ""
        filename = self._sanitize_filename(
            f"conversations{user_suffix}_export_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        )

        # Exportar datos
        export_result = self._export_data(conversations, filename, export_id, timestamp)

        self.logger.info(
            f"Exportación de conversaciones completada: {export_result['filename']}"
        )
        return export_result

    def _get_user_data(
        self, user_id: str, data_types: List[str] = None
    ) -> List[Dict[str, Any]]:
        """Obtener datos de usuario desde la base de datos"""
        try:
            # Conectar a la base de datos
            db_path = Path("data/user_data.duckdb")
            if not db_path.exists():
                self.logger.warning("Base de datos de usuarios no encontrada")
                return []

            # Simular datos de usuario (en un sistema real, esto vendría de la BD)
            user_data = []

            # Datos de perfil
            if not data_types or "profile" in data_types:
                profile_data = {
                    "id": self._generate_hash(f"profile_{user_id}"),
                    "domain": "user_profile",
                    "data_type": "profile",
                    "content": {
                        "name": "Usuario Ejemplo",
                        "email": f"user{user_id}@example.com",
                        "preferences": {
                            "language": "es",
                            "theme": "dark",
                            "notifications": True,
                        },
                    },
                    "timestamp": datetime.now(timezone.utc).isoformat(),
                    "is_pii": True,
                }
                user_data.append(profile_data)

            # Datos de sesión
            if not data_types or "sessions" in data_types:
                session_data = {
                    "id": self._generate_hash(f"session_{user_id}"),
                    "domain": "analytics",
                    "data_type": "session",
                    "content": {
                        "last_login": datetime.now().strftime("%Y-%m-%d"),
                        "session_count": 5,
                        "total_time": 3600,
                    },
                    "timestamp": datetime.now(timezone.utc).isoformat(),
                    "is_pii": False,
                }
                user_data.append(session_data)

            # Datos de conversaciones
            if not data_types or "conversations" in data_types:
                conversation_data = {
                    "id": self._generate_hash(f"conversation_{user_id}"),
                    "domain": "chat",
                    "data_type": "conversation",
                    "content": {
                        "messages": [
                            {"role": "user", "content": "¿Qué es la fotosíntesis?"},
                            {
                                "role": "assistant",
                                "content": "La fotosíntesis es un proceso biológico...",
                            },
                        ],
                        "topic": "ciencia",
                        "duration": 120,
                    },
                    "timestamp": datetime.now(timezone.utc).isoformat(),
                    "is_pii": True,
                }
                user_data.append(conversation_data)

            return user_data

        except Exception as e:
            self.logger.error(f"Error obteniendo datos de usuario: {e}")
            return []

    def _get_system_data(
        self, data_types: List[str] = None, date_range: tuple = None
    ) -> List[Dict[str, Any]]:
        """Obtener datos del sistema"""
        try:
            system_data = []

            # Datos de configuración
            if not data_types or "config" in data_types:
                config_data = {
                    "id": self._generate_hash("system_config"),
                    "domain": "system",
                    "data_type": "configuration",
                    "content": {
                        "version": "3.1.0",
                        "environment": "production",
                        "features": ["chat", "training", "evaluation"],
                    },
                    "timestamp": datetime.now(timezone.utc).isoformat(),
                    "is_pii": False,
                }
                system_data.append(config_data)

            # Datos de rendimiento
            if not data_types or "performance" in data_types:
                performance_data = {
                    "id": self._generate_hash("system_performance"),
                    "domain": "system",
                    "data_type": "performance",
                    "content": {
                        "cpu_usage": 45.2,
                        "memory_usage": 67.8,
                        "active_users": 150,
                        "requests_per_minute": 25,
                    },
                    "timestamp": datetime.now(timezone.utc).isoformat(),
                    "is_pii": False,
                }
                system_data.append(performance_data)

            return system_data

        except Exception as e:
            self.logger.error(f"Error obteniendo datos del sistema: {e}")
            return []

    def _get_conversations(
        self, user_id: str = None, date_range: tuple = None
    ) -> List[Dict[str, Any]]:
        """Obtener conversaciones"""
        try:
            conversations = []

            # Simular conversaciones (en un sistema real, esto vendría de la BD)
            sample_conversations = [
                {
                    "id": self._generate_hash("conv_1"),
                    "user_id": "user_123",
                    "domain": "chat",
                    "data_type": "conversation",
                    "content": {
                        "messages": [
                            {"role": "user", "content": "¿Qué es la fotosíntesis?"},
                            {
                                "role": "assistant",
                                "content": "La fotosíntesis es un proceso biológico donde las plantas transforman luz solar en energía química.",
                            },
                        ],
                        "topic": "ciencia",
                        "duration": 120,
                    },
                    "timestamp": datetime.now(timezone.utc).isoformat(),
                    "is_pii": True,
                },
                {
                    "id": self._generate_hash("conv_2"),
                    "user_id": "user_456",
                    "domain": "chat",
                    "data_type": "conversation",
                    "content": {
                        "messages": [
                            {
                                "role": "user",
                                "content": "¿Cómo funciona la inteligencia artificial?",
                            },
                            {
                                "role": "assistant",
                                "content": "La inteligencia artificial es una rama de la computación que busca crear sistemas capaces de realizar tareas que requieren inteligencia humana.",
                            },
                        ],
                        "topic": "tecnología",
                        "duration": 180,
                    },
                    "timestamp": datetime.now(timezone.utc).isoformat(),
                    "is_pii": True,
                },
            ]

            # Filtrar por usuario si se especifica
            if user_id:
                conversations = [
                    conv
                    for conv in sample_conversations
                    if conv.get("user_id") == user_id
                ]
            else:
                conversations = sample_conversations

            return conversations

        except Exception as e:
            self.logger.error(f"Error obteniendo conversaciones: {e}")
            return []

    def _generate_hash(self, content: str) -> str:
        """Generar hash SHA-256 para IDs"""
        return hashlib.sha256(content.encode()).hexdigest()

    def _export_data(
        self, data: List[Dict[str, Any]], filename: str, export_id: str, timestamp: str
    ) -> Dict[str, Any]:
        """Exportar datos en el formato especificado"""
        try:
            # Crear metadatos
            metadata = ExportMetadata(
                export_id=export_id,
                timestamp=timestamp,
                format=self.config.format,
                total_records=len(data),
                file_size=0,
                checksum="",
                source="shaili_ai_system",
            )

            # Determinar extensión de archivo
            extensions = {
                "jsonl": ".jsonl",
                "json": ".json",
                "csv": ".csv",
                "xml": ".xml",
                "yaml": ".yaml",
            }
            extension = extensions.get(self.config.format, ".jsonl")

            # Crear archivo de exportación
            file_path = self.export_dir / f"{filename}{extension}"

            # Exportar según el formato
            if self.config.format == "jsonl":
                self._export_jsonl(data, file_path, metadata)
            elif self.config.format == "json":
                self._export_json(data, file_path, metadata)
            elif self.config.format == "csv":
                self._export_csv(data, file_path, metadata)
            elif self.config.format == "xml":
                self._export_xml(data, file_path, metadata)
            elif self.config.format == "yaml":
                self._export_yaml(data, file_path, metadata)
            else:
                raise ValueError(f"Formato no soportado: {self.config.format}")

            # Calcular checksum
            checksum = self._calculate_checksum(file_path)
            metadata.checksum = checksum
            metadata.file_size = file_path.stat().st_size

            # Comprimir si se solicita
            if self.config.compress:
                file_path = self._compress_file(file_path)

            # Crear archivo de metadatos
            metadata_path = file_path.with_suffix(f"{file_path.suffix}.meta.json")
            with open(metadata_path, "w", encoding="utf-8") as f:
                json.dump(asdict(metadata), f, ensure_ascii=False, indent=2)

            return {
                "success": True,
                "export_id": export_id,
                "filename": file_path.name,
                "file_path": str(file_path),
                "metadata_path": str(metadata_path),
                "total_records": len(data),
                "file_size": metadata.file_size,
                "checksum": checksum,
                "format": self.config.format,
            }

        except Exception as e:
            self.logger.error(f"Error en exportación: {e}")
            return {"success": False, "error": str(e)}

    def _export_jsonl(
        self, data: List[Dict[str, Any]], file_path: Path, metadata: ExportMetadata
    ):
        """Exportar en formato JSONL"""
        with open(file_path, "w", encoding="utf-8") as f:
            for record in data:
                # Filtrar PII si no se incluye
                if not self.config.include_pii and record.get("is_pii", False):
                    record = self._anonymize_record(record)

                f.write(json.dumps(record, ensure_ascii=False) + "\n")

    def _export_json(
        self, data: List[Dict[str, Any]], file_path: Path, metadata: ExportMetadata
    ):
        """Exportar en formato JSON"""
        export_data = {"metadata": asdict(metadata), "data": data}

        # Filtrar PII si no se incluye
        if not self.config.include_pii:
            export_data["data"] = [
                (
                    self._anonymize_record(record)
                    if record.get("is_pii", False)
                    else record
                )
                for record in data
            ]

        with open(file_path, "w", encoding="utf-8") as f:
            json.dump(export_data, f, ensure_ascii=False, indent=2)

    def _export_csv(
        self, data: List[Dict[str, Any]], file_path: Path, metadata: ExportMetadata
    ):
        """Exportar en formato CSV"""
        if not data:
            return

        # Aplanar datos para CSV
        flattened_data = []
        for record in data:
            flat_record = {
                "id": record.get("id", ""),
                "domain": record.get("domain", ""),
                "data_type": record.get("data_type", ""),
                "timestamp": record.get("timestamp", ""),
                "is_pii": record.get("is_pii", False),
            }

            # Aplanar contenido
            content = record.get("content", {})
            if isinstance(content, dict):
                for key, value in content.items():
                    if isinstance(value, (dict, list)):
                        flat_record[f"content_{key}"] = json.dumps(
                            value, ensure_ascii=False
                        )
                    else:
                        flat_record[f"content_{key}"] = str(value)

            flattened_data.append(flat_record)

        # Filtrar PII si no se incluye
        if not self.config.include_pii:
            flattened_data = [
                (
                    self._anonymize_record(record)
                    if record.get("is_pii", False)
                    else record
                )
                for record in flattened_data
            ]

        # Escribir CSV
        df = pd.DataFrame(flattened_data)
        df.to_csv(file_path, index=False, encoding="utf-8")

    def _export_xml(
        self, data: List[Dict[str, Any]], file_path: Path, metadata: ExportMetadata
    ):
        """Exportar en formato XML"""
        root = ET.Element("export")

        # Agregar metadatos
        meta_elem = ET.SubElement(root, "metadata")
        for key, value in asdict(metadata).items():
            meta_elem.set(key, str(value))

        # Agregar datos
        data_elem = ET.SubElement(root, "data")
        for record in data:
            record_elem = ET.SubElement(data_elem, "record")
            for key, value in record.items():
                if key == "content" and isinstance(value, dict):
                    content_elem = ET.SubElement(record_elem, "content")
                    for content_key, content_value in value.items():
                        content_elem.set(content_key, str(content_value))
                else:
                    record_elem.set(key, str(value))

        # Filtrar PII si no se incluye
        if not self.config.include_pii:
            for record_elem in data_elem.findall("record"):
                if record_elem.get("is_pii") == "True":
                    self._anonymize_xml_record(record_elem)

        # Escribir XML
        tree = ET.ElementTree(root)
        tree.write(file_path, encoding="utf-8", xml_declaration=True)

    def _export_yaml(
        self, data: List[Dict[str, Any]], file_path: Path, metadata: ExportMetadata
    ):
        """Exportar en formato YAML"""
        export_data = {"metadata": asdict(metadata), "data": data}

        # Filtrar PII si no se incluye
        if not self.config.include_pii:
            export_data["data"] = [
                (
                    self._anonymize_record(record)
                    if record.get("is_pii", False)
                    else record
                )
                for record in data
            ]

        with open(file_path, "w", encoding="utf-8") as f:
            yaml.dump(export_data, f, default_flow_style=False, allow_unicode=True)

    def _anonymize_record(self, record: Dict[str, Any]) -> Dict[str, Any]:
        """Anonimizar registro con datos PII"""
        anonymized = record.copy()

        # Anonimizar contenido
        if "content" in anonymized and isinstance(anonymized["content"], dict):
            content = anonymized["content"]

            # Anonimizar campos comunes
            if "name" in content:
                content["name"] = "[ANONYMIZED]"
            if "email" in content:
                content["email"] = "[ANONYMIZED]"
            if "messages" in content:
                content["messages"] = "[ANONYMIZED]"

        return anonymized

    def _anonymize_xml_record(self, record_elem):
        """Anonimizar registro XML"""
        content_elem = record_elem.find("content")
        if content_elem is not None:
            for key in ["name", "email", "messages"]:
                if content_elem.get(key):
                    content_elem.set(key, "[ANONYMIZED]")

    def _compress_file(self, file_path: Path) -> Path:
        """Comprimir archivo"""
        zip_path = file_path.with_suffix(f"{file_path.suffix}.zip")

        with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as zipf:
            zipf.write(file_path, file_path.name)

        # Eliminar archivo original
        file_path.unlink()

        return zip_path

    def get_export_history(self, limit: int = 50) -> List[Dict[str, Any]]:
        """Obtener historial de exportaciones"""
        return self.export_history[-limit:] if limit else self.export_history

    def cleanup_old_exports(self, days: int = 30) -> int:
        """Limpiar exportaciones antiguas"""
        cutoff_date = datetime.now() - timedelta(days=days)
        deleted_count = 0

        for file_path in self.export_dir.glob("*"):
            if file_path.is_file():
                file_time = datetime.fromtimestamp(file_path.stat().st_mtime)
                if file_time < cutoff_date:
                    try:
                        file_path.unlink()
                        deleted_count += 1
                        self.logger.info(f"Archivo eliminado: {file_path}")
                    except Exception as e:
                        self.logger.error(f"Error eliminando archivo {file_path}: {e}")

        return deleted_count


def main():
    """Función principal para demostración"""
    # Configurar logging
    logging.basicConfig(level=logging.INFO)

    # Crear gestor de exportación
    config = ExportConfig(
        format="jsonl", include_pii=True, include_metadata=True, compress=False
    )

    export_manager = ExportManager(config)

    # Ejemplo de exportación de datos de usuario
    print("🚀 Exportando datos de usuario...")
    result = export_manager.export_user_data(
        "user_123", ["profile", "sessions", "conversations"]
    )

    if result["success"]:
        print(f"✅ Exportación exitosa: {result['filename']}")
        print(f"   Registros: {result['total_records']}")
        print(f"   Tamaño: {result['file_size']} bytes")
        print(f"   Checksum: {result['checksum'][:16]}...")
    else:
        print(f"❌ Error en exportación: {result.get('error', 'Unknown error')}")

    # Ejemplo de exportación de conversaciones
    print("\n🚀 Exportando conversaciones...")
    conv_result = export_manager.export_conversations()

    if conv_result["success"]:
        print(f"✅ Exportación de conversaciones exitosa: {conv_result['filename']}")
    else:
        print(
            f"❌ Error en exportación de conversaciones: {conv_result.get('error', 'Unknown error')}"
        )

    # Mostrar historial
    print("\n📋 Historial de exportaciones:")
    history = export_manager.get_export_history(5)
    for entry in history:
        print(
            f"   {entry['timestamp']}: {entry['filename']} ({entry['record_count']} registros)"
        )


if __name__ == "__main__":
    main()
