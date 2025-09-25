#!/usr/bin/env python3
"""
Exportador de Datos Especializado - Sheily AI

Este módulo proporciona exportadores especializados para diferentes tipos
de datos del sistema, incluyendo conversaciones, embeddings, configuraciones, etc.
"""

import json
import sqlite3
import pandas as pd
from pathlib import Path
from datetime import datetime, timezone
from typing import Dict, List, Any, Optional, Union
import logging
import hashlib
import numpy as np
from dataclasses import dataclass, asdict
import pickle
import gzip
import sqlalchemy as sa
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base


@dataclass
class ExportSpecification:
    """Especificación de exportación"""

    data_type: str
    source_path: str
    output_format: str
    filters: Dict[str, Any] = None
    include_metadata: bool = True
    compress: bool = False


class DataExporter:
    """Exportador especializado de datos"""

    def __init__(self, base_dir: str = "exports"):
        """
        Inicializar exportador de datos

        Args:
            base_dir: Directorio base para exportaciones
        """
        self.base_dir = Path(base_dir)
        self.base_dir.mkdir(parents=True, exist_ok=True)
        self.logger = logging.getLogger(__name__)

        # Configurar logging
        self._setup_logging()

    def _setup_logging(self):
        """Configurar logging"""
        log_dir = Path("logs/exports")
        log_dir.mkdir(parents=True, exist_ok=True)

        logging.basicConfig(
            level=logging.INFO,
            format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
            handlers=[
                logging.FileHandler(log_dir / "data_exporter.log"),
                logging.StreamHandler(),
            ],
        )

    def export_conversations(self, spec: ExportSpecification) -> Dict[str, Any]:
        """
        Exportar conversaciones desde la base de datos

        Args:
            spec: Especificación de exportación

        Returns:
            Resultado de la exportación
        """
        self.logger.info(f"Exportando conversaciones desde {spec.source_path}")

        try:
            # Conectar a la base de datos
            conn = sqlite3.connect(spec.source_path)

            # Construir consulta
            query = "SELECT * FROM conversations"
            if spec.filters:
                conditions = []
                for key, value in spec.filters.items():
                    if isinstance(value, str):
                        conditions.append(f"{key} = '{value}'")
                    else:
                        conditions.append(f"{key} = {value}")
                if conditions:
                    query += " WHERE " + " AND ".join(conditions)

            # Ejecutar consulta
            df = pd.read_sql_query(query, conn)
            conn.close()

            if df.empty:
                return {"success": False, "error": "No conversations found"}

            # Exportar datos
            return self._export_dataframe(df, spec, "conversations")

        except Exception as e:
            self.logger.error(f"Error exportando conversaciones: {e}")
            return {"success": False, "error": str(e)}

    def export_embeddings(self, spec: ExportSpecification) -> Dict[str, Any]:
        """
        Exportar embeddings desde la base de datos

        Args:
            spec: Especificación de exportación

        Returns:
            Resultado de la exportación
        """
        self.logger.info(f"Exportando embeddings desde {spec.source_path}")

        try:
            # Conectar a la base de datos
            conn = sqlite3.connect(spec.source_path)

            # Obtener embeddings
            query = "SELECT * FROM embeddings"
            if spec.filters:
                conditions = []
                for key, value in spec.filters.items():
                    if isinstance(value, str):
                        conditions.append(f"{key} = '{value}'")
                    else:
                        conditions.append(f"{key} = {value}")
                if conditions:
                    query += " WHERE " + " AND ".join(conditions)

            df = pd.read_sql_query(query, conn)
            conn.close()

            if df.empty:
                return {"success": False, "error": "No embeddings found"}

            # Convertir embeddings de string a numpy arrays
            if "embedding" in df.columns:
                df["embedding"] = df["embedding"].apply(
                    lambda x: (
                        np.frombuffer(x.encode(), dtype=np.float32)
                        if isinstance(x, str)
                        else x
                    )
                )

            # Exportar datos
            return self._export_dataframe(df, spec, "embeddings")

        except Exception as e:
            self.logger.error(f"Error exportando embeddings: {e}")
            return {"success": False, "error": str(e)}

    def export_user_profiles(self, spec: ExportSpecification) -> Dict[str, Any]:
        """
        Exportar perfiles de usuario

        Args:
            spec: Especificación de exportación

        Returns:
            Resultado de la exportación
        """
        self.logger.info(f"Exportando perfiles de usuario desde {spec.source_path}")

        try:
            # Conectar a la base de datos
            conn = sqlite3.connect(spec.source_path)

            # Obtener perfiles
            query = "SELECT * FROM user_profiles"
            if spec.filters:
                conditions = []
                for key, value in spec.filters.items():
                    if isinstance(value, str):
                        conditions.append(f"{key} = '{value}'")
                    else:
                        conditions.append(f"{key} = {value}")
                if conditions:
                    query += " WHERE " + " AND ".join(conditions)

            df = pd.read_sql_query(query, conn)
            conn.close()

            if df.empty:
                return {"success": False, "error": "No user profiles found"}

            # Exportar datos
            return self._export_dataframe(df, spec, "user_profiles")

        except Exception as e:
            self.logger.error(f"Error exportando perfiles de usuario: {e}")
            return {"success": False, "error": str(e)}

    def export_system_logs(self, spec: ExportSpecification) -> Dict[str, Any]:
        """
        Exportar logs del sistema

        Args:
            spec: Especificación de exportación

        Returns:
            Resultado de la exportación
        """
        self.logger.info(f"Exportando logs del sistema desde {spec.source_path}")

        try:
            log_path = Path(spec.source_path)
            if not log_path.exists():
                return {"success": False, "error": "Log file not found"}

            # Leer logs
            logs = []
            with open(log_path, "r", encoding="utf-8") as f:
                for line in f:
                    line = line.strip()
                    if line:
                        try:
                            # Intentar parsear como JSON
                            log_entry = json.loads(line)
                            logs.append(log_entry)
                        except json.JSONDecodeError:
                            # Si no es JSON, crear entrada simple
                            logs.append(
                                {
                                    "timestamp": datetime.now().isoformat(),
                                    "message": line,
                                    "level": "INFO",
                                }
                            )

            if not logs:
                return {"success": False, "error": "No logs found"}

            # Convertir a DataFrame
            df = pd.DataFrame(logs)

            # Aplicar filtros
            if spec.filters:
                for key, value in spec.filters.items():
                    if key in df.columns:
                        df = df[df[key] == value]

            if df.empty:
                return {"success": False, "error": "No logs match filters"}

            # Exportar datos
            return self._export_dataframe(df, spec, "system_logs")

        except Exception as e:
            self.logger.error(f"Error exportando logs del sistema: {e}")
            return {"success": False, "error": str(e)}

    def export_configurations(self, spec: ExportSpecification) -> Dict[str, Any]:
        """
        Exportar configuraciones del sistema

        Args:
            spec: Especificación de exportación

        Returns:
            Resultado de la exportación
        """
        self.logger.info(f"Exportando configuraciones desde {spec.source_path}")

        try:
            config_path = Path(spec.source_path)
            if not config_path.exists():
                return {"success": False, "error": "Configuration file not found"}

            # Leer configuración
            with open(config_path, "r", encoding="utf-8") as f:
                if config_path.suffix == ".json":
                    config_data = json.load(f)
                elif config_path.suffix == ".yaml":
                    import yaml

                    config_data = yaml.safe_load(f)
                else:
                    return {
                        "success": False,
                        "error": "Unsupported configuration format",
                    }

            # Crear DataFrame
            config_records = []
            for key, value in config_data.items():
                config_records.append(
                    {
                        "key": key,
                        "value": (
                            json.dumps(value)
                            if isinstance(value, (dict, list))
                            else str(value)
                        ),
                        "type": type(value).__name__,
                        "timestamp": datetime.now().isoformat(),
                    }
                )

            df = pd.DataFrame(config_records)

            # Exportar datos
            return self._export_dataframe(df, spec, "configurations")

        except Exception as e:
            self.logger.error(f"Error exportando configuraciones: {e}")
            return {"success": False, "error": str(e)}

    def export_evaluation_results(self, spec: ExportSpecification) -> Dict[str, Any]:
        """
        Exportar resultados de evaluación

        Args:
            spec: Especificación de exportación

        Returns:
            Resultado de la exportación
        """
        self.logger.info(
            f"Exportando resultados de evaluación desde {spec.source_path}"
        )

        try:
            results_path = Path(spec.source_path)
            if not results_path.exists():
                return {"success": False, "error": "Evaluation results file not found"}

            # Leer resultados
            with open(results_path, "r", encoding="utf-8") as f:
                results_data = json.load(f)

            # Convertir a DataFrame
            if isinstance(results_data, list):
                df = pd.DataFrame(results_data)
            elif isinstance(results_data, dict):
                # Aplanar estructura anidada
                flattened = []
                for key, value in results_data.items():
                    if isinstance(value, dict):
                        value["result_type"] = key
                        flattened.append(value)
                    else:
                        flattened.append({"result_type": key, "value": value})
                df = pd.DataFrame(flattened)
            else:
                return {"success": False, "error": "Invalid evaluation results format"}

            if df.empty:
                return {"success": False, "error": "No evaluation results found"}

            # Exportar datos
            return self._export_dataframe(df, spec, "evaluation_results")

        except Exception as e:
            self.logger.error(f"Error exportando resultados de evaluación: {e}")
            return {"success": False, "error": str(e)}

    def _export_dataframe(
        self, df: pd.DataFrame, spec: ExportSpecification, data_type: str
    ) -> Dict[str, Any]:
        """Exportar DataFrame en el formato especificado"""
        try:
            # Generar nombre de archivo
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"{data_type}_{timestamp}"

            # Crear directorio específico
            output_dir = self.base_dir / data_type
            output_dir.mkdir(parents=True, exist_ok=True)

            # Exportar según el formato
            if spec.output_format == "csv":
                file_path = output_dir / f"{filename}.csv"
                df.to_csv(file_path, index=False, encoding="utf-8")
            elif spec.output_format == "json":
                file_path = output_dir / f"{filename}.json"
                df.to_json(file_path, orient="records", indent=2, force_ascii=False)
            elif spec.output_format == "jsonl":
                file_path = output_dir / f"{filename}.jsonl"
                with open(file_path, "w", encoding="utf-8") as f:
                    for _, row in df.iterrows():
                        f.write(row.to_json() + "\n")
            elif spec.output_format == "parquet":
                file_path = output_dir / f"{filename}.parquet"
                df.to_parquet(file_path, index=False)
            elif spec.output_format == "pickle":
                file_path = output_dir / f"{filename}.pkl"
                with open(file_path, "wb") as f:
                    pickle.dump(df, f)
            else:
                return {
                    "success": False,
                    "error": f"Unsupported format: {spec.output_format}",
                }

            # Comprimir si se solicita
            if spec.compress:
                file_path = self._compress_file(file_path)

            # Crear metadatos
            metadata = {
                "data_type": data_type,
                "timestamp": datetime.now().isoformat(),
                "format": spec.output_format,
                "total_records": len(df),
                "columns": list(df.columns),
                "file_size": file_path.stat().st_size,
                "checksum": self._calculate_checksum(file_path),
                "source_path": spec.source_path,
                "filters": spec.filters,
            }

            # Guardar metadatos
            metadata_path = file_path.with_suffix(f"{file_path.suffix}.meta.json")
            with open(metadata_path, "w", encoding="utf-8") as f:
                json.dump(metadata, f, ensure_ascii=False, indent=2)

            return {
                "success": True,
                "filename": file_path.name,
                "file_path": str(file_path),
                "metadata_path": str(metadata_path),
                "total_records": len(df),
                "file_size": metadata["file_size"],
                "checksum": metadata["checksum"],
                "format": spec.output_format,
            }

        except Exception as e:
            self.logger.error(f"Error en exportación de DataFrame: {e}")
            return {"success": False, "error": str(e)}

    def _calculate_checksum(self, file_path: Path) -> str:
        """Calcular checksum SHA-256 de un archivo"""
        sha256_hash = hashlib.sha256()
        with open(file_path, "rb") as f:
            for chunk in iter(lambda: f.read(4096), b""):
                sha256_hash.update(chunk)
        return sha256_hash.hexdigest()

    def _compress_file(self, file_path: Path) -> Path:
        """Comprimir archivo con gzip"""
        gz_path = file_path.with_suffix(f"{file_path.suffix}.gz")

        with open(file_path, "rb") as f_in:
            with gzip.open(gz_path, "wb") as f_out:
                f_out.writelines(f_in)

        # Eliminar archivo original
        file_path.unlink()

        return gz_path

    def list_available_exports(self) -> Dict[str, List[str]]:
        """Listar exportaciones disponibles"""
        exports = {}

        for data_type_dir in self.base_dir.iterdir():
            if data_type_dir.is_dir():
                files = [
                    f.name
                    for f in data_type_dir.iterdir()
                    if f.is_file() and not f.name.endswith(".meta.json")
                ]
                exports[data_type_dir.name] = files

        return exports

    def get_export_info(self, data_type: str, filename: str) -> Dict[str, Any]:
        """Obtener información de una exportación específica"""
        try:
            file_path = self.base_dir / data_type / filename
            metadata_path = file_path.with_suffix(f"{file_path.suffix}.meta.json")

            if not file_path.exists():
                return {"success": False, "error": "Export file not found"}

            info = {
                "success": True,
                "filename": filename,
                "file_path": str(file_path),
                "file_size": file_path.stat().st_size,
                "modified": datetime.fromtimestamp(
                    file_path.stat().st_mtime
                ).isoformat(),
            }

            # Agregar metadatos si existen
            if metadata_path.exists():
                with open(metadata_path, "r", encoding="utf-8") as f:
                    metadata = json.load(f)
                info["metadata"] = metadata

            return info

        except Exception as e:
            return {"success": False, "error": str(e)}


def main():
    """Función principal para demostración"""
    # Configurar logging
    logging.basicConfig(level=logging.INFO)

    # Crear exportador
    exporter = DataExporter()

    # Ejemplo de exportación de conversaciones
    print("🚀 Exportando conversaciones...")
    conv_spec = ExportSpecification(
        data_type="conversations",
        source_path="data/user_data.duckdb",
        output_format="jsonl",
        filters={"user_id": "user_123"},
    )

    result = exporter.export_conversations(conv_spec)
    if result["success"]:
        print(f"✅ Conversaciones exportadas: {result['filename']}")
    else:
        print(f"❌ Error: {result.get('error', 'Unknown error')}")

    # Ejemplo de exportación de embeddings
    print("\n🚀 Exportando embeddings...")
    emb_spec = ExportSpecification(
        data_type="embeddings",
        source_path="data/embeddings_sqlite.db",
        output_format="parquet",
        compress=True,
    )

    result = exporter.export_embeddings(emb_spec)
    if result["success"]:
        print(f"✅ Embeddings exportados: {result['filename']}")
    else:
        print(f"❌ Error: {result.get('error', 'Unknown error')}")

    # Listar exportaciones disponibles
    print("\n📋 Exportaciones disponibles:")
    exports = exporter.list_available_exports()
    for data_type, files in exports.items():
        print(f"  {data_type}: {len(files)} archivos")
        for file in files[:3]:  # Mostrar solo los primeros 3
            print(f"    - {file}")


if __name__ == "__main__":
    main()
