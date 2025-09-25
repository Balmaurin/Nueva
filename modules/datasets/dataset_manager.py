#!/usr/bin/env python3
"""
Sistema de Gestión de Datasets
Gestiona la carga, procesamiento y gestión de datasets para entrenamiento
"""

import os
import json
import sqlite3
import logging
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional, Tuple, Union
from pathlib import Path
import threading
import hashlib
import shutil
from dataclasses import dataclass, asdict
import pickle
import gzip
import zipfile
import tarfile


@dataclass
class Dataset:
    """Estructura de datos para un dataset"""

    id: str
    name: str
    description: str
    version: str
    file_path: str
    file_size: int
    format: str
    columns: List[str]
    row_count: int
    created_at: datetime
    updated_at: datetime
    status: str = "active"
    metadata: Dict[str, Any] = None


class DatasetManager:
    """Gestor completo de datasets con funciones reales"""

    def __init__(self, datasets_dir: str = "datasets"):
        self.datasets_dir = Path(datasets_dir)
        self.datasets_dir.mkdir(exist_ok=True)

        # Configurar logging
        self.logger = logging.getLogger(__name__)
        self.logger.setLevel(logging.INFO)

        # Inicializar base de datos
        self.db_path = self.datasets_dir / "datasets.db"
        self._init_database()

        # Lock para operaciones thread-safe
        self._lock = threading.Lock()

        # Crear subdirectorios
        self._create_subdirectories()

        self.logger.info(f"✅ DatasetManager inicializado en {self.datasets_dir}")

    def _init_database(self):
        """Inicializar base de datos SQLite para datasets"""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS datasets (
                    id TEXT PRIMARY KEY,
                    name TEXT UNIQUE NOT NULL,
                    description TEXT,
                    version TEXT DEFAULT '1.0',
                    file_path TEXT NOT NULL,
                    file_size INTEGER NOT NULL,
                    format TEXT NOT NULL,
                    columns TEXT NOT NULL,
                    row_count INTEGER NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    status TEXT DEFAULT 'active',
                    checksum TEXT,
                    metadata TEXT
                )
            """
            )

            conn.execute(
                """
                CREATE INDEX IF NOT EXISTS idx_dataset_name ON datasets(name)
            """
            )

            conn.execute(
                """
                CREATE INDEX IF NOT EXISTS idx_dataset_format ON datasets(format)
            """
            )

            conn.execute(
                """
                CREATE INDEX IF NOT EXISTS idx_dataset_status ON datasets(status)
            """
            )

            # Tabla de versiones de datasets
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS dataset_versions (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    dataset_id TEXT NOT NULL,
                    version TEXT NOT NULL,
                    file_path TEXT NOT NULL,
                    file_size INTEGER NOT NULL,
                    checksum TEXT NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    changes_description TEXT,
                    FOREIGN KEY (dataset_id) REFERENCES datasets(id)
                )
            """
            )

            conn.execute(
                """
                CREATE INDEX IF NOT EXISTS idx_dataset_versions ON dataset_versions(dataset_id, version)
            """
            )

    def _create_subdirectories(self):
        """Crear subdirectorios para organizar datasets"""
        subdirs = [
            "raw",
            "processed",
            "training",
            "validation",
            "test",
            "external",
            "conversations",
            "embeddings",
            "backups",
        ]

        for subdir in subdirs:
            (self.datasets_dir / subdir).mkdir(exist_ok=True)

    def _generate_dataset_id(self, name: str) -> str:
        """Generar ID único para el dataset"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        name_clean = name.lower().replace(" ", "_").replace("-", "_")
        return f"{name_clean}_{timestamp}"

    def _calculate_file_checksum(self, file_path: Path) -> str:
        """Calcular checksum SHA-256 del archivo"""
        hash_sha256 = hashlib.sha256()
        with open(file_path, "rb") as f:
            for chunk in iter(lambda: f.read(4096), b""):
                hash_sha256.update(chunk)
        return hash_sha256.hexdigest()

    def _get_file_info(self, file_path: Path) -> Tuple[int, str]:
        """Obtener información del archivo"""
        file_size = file_path.stat().st_size
        file_format = file_path.suffix.lower().lstrip(".")
        return file_size, file_format

    def load_dataset(
        self,
        file_path: str,
        name: str,
        description: str = "",
        target_dir: str = "raw",
        metadata: Dict[str, Any] = None,
    ) -> str:
        """Cargar dataset desde archivo externo"""
        with self._lock:
            try:
                source_path = Path(file_path)
                if not source_path.exists():
                    raise FileNotFoundError(f"Archivo no encontrado: {file_path}")

                # Generar ID único
                dataset_id = self._generate_dataset_id(name)

                # Verificar que el nombre no exista
                if self.get_dataset_by_name(name):
                    raise ValueError(f"Ya existe un dataset con el nombre: {name}")

                # Determinar directorio de destino
                target_path = (
                    self.datasets_dir / target_dir / f"{dataset_id}{source_path.suffix}"
                )

                # Copiar archivo
                shutil.copy2(source_path, target_path)

                # Obtener información del archivo
                file_size, file_format = self._get_file_info(target_path)
                checksum = self._calculate_file_checksum(target_path)

                # Analizar dataset
                columns, row_count = self._analyze_dataset(target_path, file_format)

                # Registrar en base de datos
                with sqlite3.connect(self.db_path) as conn:
                    conn.execute(
                        """
                        INSERT INTO datasets 
                        (id, name, description, file_path, file_size, format, columns, row_count, checksum, metadata)
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """,
                        (
                            dataset_id,
                            name,
                            description,
                            str(target_path),
                            file_size,
                            file_format,
                            json.dumps(columns),
                            row_count,
                            checksum,
                            json.dumps(metadata or {}),
                        ),
                    )

                self.logger.info(
                    f"✅ Dataset cargado: {name} ({row_count} filas, {len(columns)} columnas)"
                )
                return dataset_id

            except Exception as e:
                self.logger.error(f"❌ Error cargando dataset: {e}")
                raise

    def _analyze_dataset(
        self, file_path: Path, file_format: str
    ) -> Tuple[List[str], int]:
        """Analizar estructura del dataset"""
        try:
            if file_format in ["csv", "tsv"]:
                df = pd.read_csv(
                    file_path, nrows=1000
                )  # Leer solo las primeras 1000 filas para análisis
                columns = df.columns.tolist()

                # Contar filas totales
                with open(file_path, "r", encoding="utf-8") as f:
                    row_count = sum(1 for line in f) - 1  # Restar header

            elif file_format in ["json", "jsonl"]:
                if file_format == "json":
                    with open(file_path, "r", encoding="utf-8") as f:
                        data = json.load(f)
                    if isinstance(data, list):
                        df = pd.DataFrame(data[:1000])
                    else:
                        df = pd.DataFrame([data])
                else:  # jsonl
                    data = []
                    with open(file_path, "r", encoding="utf-8") as f:
                        for i, line in enumerate(f):
                            if i >= 1000:
                                break
                            data.append(json.loads(line))
                    df = pd.DataFrame(data)

                columns = df.columns.tolist()

                # Contar líneas totales
                with open(file_path, "r", encoding="utf-8") as f:
                    row_count = sum(1 for line in f)
                if file_format == "json":
                    row_count = len(data) if isinstance(data, list) else 1

            elif file_format in ["xlsx", "xls"]:
                df = pd.read_excel(file_path, nrows=1000)
                columns = df.columns.tolist()
                row_count = len(pd.read_excel(file_path))

            elif file_format in ["parquet"]:
                df = pd.read_parquet(file_path)
                columns = df.columns.tolist()
                row_count = len(df)

            else:
                # Formato no soportado, intentar como texto
                columns = ["text"]
                with open(file_path, "r", encoding="utf-8") as f:
                    row_count = sum(1 for line in f)

            return columns, row_count

        except Exception as e:
            self.logger.warning(f"⚠️ Error analizando dataset: {e}")
            return ["unknown"], 0

    def get_dataset(self, dataset_id: str) -> Optional[Dataset]:
        """Obtener dataset por ID"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.execute(
                    """
                    SELECT * FROM datasets WHERE id = ? AND status = 'active'
                """,
                    (dataset_id,),
                )
                row = cursor.fetchone()

                if row:
                    return Dataset(
                        id=row[0],
                        name=row[1],
                        description=row[2],
                        version=row[3],
                        file_path=row[4],
                        file_size=row[5],
                        format=row[6],
                        columns=json.loads(row[7]),
                        row_count=row[8],
                        created_at=datetime.fromisoformat(row[9]),
                        updated_at=datetime.fromisoformat(row[10]),
                        status=row[11],
                        metadata=json.loads(row[13]) if row[13] else {},
                    )
            return None

        except Exception as e:
            self.logger.error(f"❌ Error obteniendo dataset: {e}")
            return None

    def get_dataset_by_name(self, name: str) -> Optional[Dataset]:
        """Obtener dataset por nombre"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.execute(
                    """
                    SELECT * FROM datasets WHERE name = ? AND status = 'active'
                """,
                    (name,),
                )
                row = cursor.fetchone()

                if row:
                    return Dataset(
                        id=row[0],
                        name=row[1],
                        description=row[2],
                        version=row[3],
                        file_path=row[4],
                        file_size=row[5],
                        format=row[6],
                        columns=json.loads(row[7]),
                        row_count=row[8],
                        created_at=datetime.fromisoformat(row[9]),
                        updated_at=datetime.fromisoformat(row[10]),
                        status=row[11],
                        metadata=json.loads(row[13]) if row[13] else {},
                    )
            return None

        except Exception as e:
            self.logger.error(f"❌ Error obteniendo dataset por nombre: {e}")
            return None

    def list_datasets(
        self, format: str = None, status: str = "active", limit: int = 100
    ) -> List[Dataset]:
        """Listar datasets con filtros"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                query = "SELECT * FROM datasets WHERE 1=1"
                params = []

                if format:
                    query += " AND format = ?"
                    params.append(format)

                if status:
                    query += " AND status = ?"
                    params.append(status)

                query += " ORDER BY updated_at DESC LIMIT ?"
                params.append(limit)

                cursor = conn.execute(query, params)
                datasets = []

                for row in cursor.fetchall():
                    datasets.append(
                        Dataset(
                            id=row[0],
                            name=row[1],
                            description=row[2],
                            version=row[3],
                            file_path=row[4],
                            file_size=row[5],
                            format=row[6],
                            columns=json.loads(row[7]),
                            row_count=row[8],
                            created_at=datetime.fromisoformat(row[9]),
                            updated_at=datetime.fromisoformat(row[10]),
                            status=row[11],
                            metadata=json.loads(row[13]) if row[13] else {},
                        )
                    )

                return datasets

        except Exception as e:
            self.logger.error(f"❌ Error listando datasets: {e}")
            return []

    def read_dataset(
        self, dataset_id: str, limit: int = None, columns: List[str] = None
    ) -> Optional[pd.DataFrame]:
        """Leer dataset como DataFrame"""
        try:
            dataset = self.get_dataset(dataset_id)
            if not dataset:
                return None

            file_path = Path(dataset.file_path)
            if not file_path.exists():
                self.logger.error(f"❌ Archivo de dataset no encontrado: {file_path}")
                return None

            # Leer según el formato
            if dataset.format == "csv":
                df = pd.read_csv(file_path, usecols=columns, nrows=limit)
            elif dataset.format == "tsv":
                df = pd.read_csv(file_path, sep="\t", usecols=columns, nrows=limit)
            elif dataset.format == "json":
                with open(file_path, "r", encoding="utf-8") as f:
                    data = json.load(f)
                if isinstance(data, list):
                    df = pd.DataFrame(data[:limit] if limit else data)
                else:
                    df = pd.DataFrame([data])
                if columns:
                    df = df[columns]
            elif dataset.format == "jsonl":
                data = []
                with open(file_path, "r", encoding="utf-8") as f:
                    for i, line in enumerate(f):
                        if limit and i >= limit:
                            break
                        data.append(json.loads(line))
                df = pd.DataFrame(data)
                if columns:
                    df = df[columns]
            elif dataset.format in ["xlsx", "xls"]:
                df = pd.read_excel(file_path, usecols=columns, nrows=limit)
            elif dataset.format == "parquet":
                df = pd.read_parquet(file_path, columns=columns)
                if limit:
                    df = df.head(limit)
            else:
                # Formato no soportado, leer como texto
                with open(file_path, "r", encoding="utf-8") as f:
                    lines = f.readlines()[:limit] if limit else f.readlines()
                df = pd.DataFrame({"text": lines})

            return df

        except Exception as e:
            self.logger.error(f"❌ Error leyendo dataset: {e}")
            return None

    def process_dataset(
        self, dataset_id: str, processing_config: Dict[str, Any]
    ) -> str:
        """Procesar dataset con configuración específica"""
        with self._lock:
            try:
                dataset = self.get_dataset(dataset_id)
                if not dataset:
                    raise ValueError(f"Dataset {dataset_id} no encontrado")

                # Leer dataset original
                df = self.read_dataset(dataset_id)
                if df is None:
                    raise ValueError("No se pudo leer el dataset original")

                # Aplicar procesamiento
                processed_df = self._apply_processing(df, processing_config)

                # Generar ID para dataset procesado
                processed_id = (
                    f"{dataset_id}_processed_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
                )

                # Guardar dataset procesado
                output_format = processing_config.get("output_format", "csv")
                output_path = (
                    self.datasets_dir / "processed" / f"{processed_id}.{output_format}"
                )

                if output_format == "csv":
                    processed_df.to_csv(output_path, index=False)
                elif output_format == "json":
                    processed_df.to_json(output_path, orient="records", indent=2)
                elif output_format == "parquet":
                    processed_df.to_parquet(output_path, index=False)
                else:
                    raise ValueError(f"Formato de salida no soportado: {output_format}")

                # Registrar dataset procesado
                file_size, _ = self._get_file_info(output_path)
                checksum = self._calculate_file_checksum(output_path)

                with sqlite3.connect(self.db_path) as conn:
                    conn.execute(
                        """
                        INSERT INTO datasets 
                        (id, name, description, file_path, file_size, format, columns, row_count, checksum, metadata)
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """,
                        (
                            processed_id,
                            f"{dataset.name} (Procesado)",
                            f"Dataset procesado de {dataset.name}",
                            str(output_path),
                            file_size,
                            output_format,
                            json.dumps(processed_df.columns.tolist()),
                            len(processed_df),
                            checksum,
                            json.dumps(
                                {
                                    "original_dataset": dataset_id,
                                    "processing_config": processing_config,
                                    "processing_date": datetime.now().isoformat(),
                                }
                            ),
                        ),
                    )

                self.logger.info(f"✅ Dataset procesado: {processed_id}")
                return processed_id

            except Exception as e:
                self.logger.error(f"❌ Error procesando dataset: {e}")
                raise

    def _apply_processing(
        self, df: pd.DataFrame, config: Dict[str, Any]
    ) -> pd.DataFrame:
        """Aplicar configuración de procesamiento al DataFrame"""
        processed_df = df.copy()

        # Limpieza de datos
        if config.get("clean_data", False):
            # Eliminar filas duplicadas
            processed_df = processed_df.drop_duplicates()

            # Eliminar filas con valores nulos si se especifica
            if config.get("remove_nulls", False):
                processed_df = processed_df.dropna()

        # Filtrado de columnas
        if "columns" in config:
            available_columns = [
                col for col in config["columns"] if col in processed_df.columns
            ]
            processed_df = processed_df[available_columns]

        # Filtrado de filas
        if "row_limit" in config:
            processed_df = processed_df.head(config["row_limit"])

        # Transformaciones de texto
        if config.get("text_processing", {}):
            text_config = config["text_processing"]

            # Convertir a minúsculas
            if text_config.get("lowercase", False):
                text_columns = processed_df.select_dtypes(include=["object"]).columns
                for col in text_columns:
                    processed_df[col] = processed_df[col].astype(str).str.lower()

            # Eliminar caracteres especiales
            if text_config.get("remove_special_chars", False):
                text_columns = processed_df.select_dtypes(include=["object"]).columns
                for col in text_columns:
                    processed_df[col] = (
                        processed_df[col]
                        .astype(str)
                        .str.replace(r"[^\w\s]", "", regex=True)
                    )

        return processed_df

    def split_dataset(
        self, dataset_id: str, split_config: Dict[str, float]
    ) -> Dict[str, str]:
        """Dividir dataset en conjuntos de entrenamiento, validación y test"""
        with self._lock:
            try:
                dataset = self.get_dataset(dataset_id)
                if not dataset:
                    raise ValueError(f"Dataset {dataset_id} no encontrado")

                # Leer dataset
                df = self.read_dataset(dataset_id)
                if df is None:
                    raise ValueError("No se pudo leer el dataset")

                # Validar configuración de división
                total_ratio = sum(split_config.values())
                if abs(total_ratio - 1.0) > 0.01:
                    raise ValueError("Las proporciones de división deben sumar 1.0")

                # Dividir dataset
                splits = {}
                start_idx = 0

                for split_name, ratio in split_config.items():
                    end_idx = int(start_idx + len(df) * ratio)
                    split_df = df.iloc[start_idx:end_idx]

                    # Guardar split
                    split_id = f"{dataset_id}_{split_name}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
                    split_path = self.datasets_dir / split_name / f"{split_id}.csv"
                    split_df.to_csv(split_path, index=False)

                    # Registrar split
                    file_size, _ = self._get_file_info(split_path)
                    checksum = self._calculate_file_checksum(split_path)

                    with sqlite3.connect(self.db_path) as conn:
                        conn.execute(
                            """
                            INSERT INTO datasets 
                            (id, name, description, file_path, file_size, format, columns, row_count, checksum, metadata)
                            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                        """,
                            (
                                split_id,
                                f"{dataset.name} ({split_name})",
                                f"Split {split_name} de {dataset.name}",
                                str(split_path),
                                file_size,
                                "csv",
                                json.dumps(split_df.columns.tolist()),
                                len(split_df),
                                checksum,
                                json.dumps(
                                    {
                                        "original_dataset": dataset_id,
                                        "split_type": split_name,
                                        "split_ratio": ratio,
                                        "split_date": datetime.now().isoformat(),
                                    }
                                ),
                            ),
                        )

                    splits[split_name] = split_id
                    start_idx = end_idx

                self.logger.info(f"✅ Dataset dividido: {splits}")
                return splits

            except Exception as e:
                self.logger.error(f"❌ Error dividiendo dataset: {e}")
                raise

    def update_dataset(self, dataset_id: str, updates: Dict[str, Any]) -> bool:
        """Actualizar metadatos del dataset"""
        with self._lock:
            try:
                dataset = self.get_dataset(dataset_id)
                if not dataset:
                    self.logger.error(f"❌ Dataset {dataset_id} no encontrado")
                    return False

                # Actualizar campos permitidos
                allowed_fields = ["description", "metadata"]
                update_data = {}

                for field, value in updates.items():
                    if field in allowed_fields:
                        update_data[field] = value

                if not update_data:
                    self.logger.warning("⚠️ No hay campos válidos para actualizar")
                    return False

                # Actualizar en base de datos
                with sqlite3.connect(self.db_path) as conn:
                    set_clause = ", ".join(
                        [f"{field} = ?" for field in update_data.keys()]
                    )
                    set_clause += ", updated_at = ?"

                    values = []
                    for field in update_data.keys():
                        if field == "metadata":
                            values.append(json.dumps(update_data[field]))
                        else:
                            values.append(update_data[field])
                    values.append(datetime.now().isoformat())
                    values.append(dataset_id)

                    conn.execute(
                        f"""
                        UPDATE datasets 
                        SET {set_clause}
                        WHERE id = ?
                    """,
                        values,
                    )

                self.logger.info(f"✅ Dataset {dataset_id} actualizado exitosamente")
                return True

            except Exception as e:
                self.logger.error(f"❌ Error actualizando dataset {dataset_id}: {e}")
                return False

    def delete_dataset(self, dataset_id: str, permanent: bool = False) -> bool:
        """Eliminar dataset"""
        with self._lock:
            try:
                dataset = self.get_dataset(dataset_id)
                if not dataset:
                    self.logger.error(f"❌ Dataset {dataset_id} no encontrado")
                    return False

                if permanent:
                    # Eliminación permanente
                    with sqlite3.connect(self.db_path) as conn:
                        conn.execute("DELETE FROM datasets WHERE id = ?", (dataset_id,))

                    # Eliminar archivo
                    file_path = Path(dataset.file_path)
                    if file_path.exists():
                        file_path.unlink()

                    self.logger.info(
                        f"🗑️ Dataset {dataset_id} eliminado permanentemente"
                    )
                else:
                    # Eliminación lógica (marcar como inactivo)
                    with sqlite3.connect(self.db_path) as conn:
                        conn.execute(
                            """
                            UPDATE datasets 
                            SET status = 'deleted', updated_at = ?
                            WHERE id = ?
                        """,
                            (datetime.now().isoformat(), dataset_id),
                        )

                    self.logger.info(f"🗑️ Dataset {dataset_id} marcado como eliminado")

                return True

            except Exception as e:
                self.logger.error(f"❌ Error eliminando dataset {dataset_id}: {e}")
                return False

    def export_dataset(
        self, dataset_id: str, format: str = "csv", export_path: str = None
    ) -> str:
        """Exportar dataset"""
        try:
            dataset = self.get_dataset(dataset_id)
            if not dataset:
                raise ValueError(f"Dataset {dataset_id} no encontrado")

            # Leer dataset
            df = self.read_dataset(dataset_id)
            if df is None:
                raise ValueError("No se pudo leer el dataset")

            # Crear directorio de exportación
            if export_path:
                export_dir = Path(export_path)
            else:
                export_dir = Path("exports")

            export_dir.mkdir(exist_ok=True)

            # Crear archivo de exportación
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            export_file = export_dir / f"{dataset.name}_{timestamp}.{format}"

            if format == "csv":
                df.to_csv(export_file, index=False)
            elif format == "json":
                df.to_json(export_file, orient="records", indent=2)
            elif format == "parquet":
                df.to_parquet(export_file, index=False)
            elif format == "xlsx":
                df.to_excel(export_file, index=False)
            else:
                raise ValueError(f"Formato no soportado: {format}")

            self.logger.info(f"📤 Dataset exportado: {export_file}")
            return str(export_file)

        except Exception as e:
            self.logger.error(f"❌ Error exportando dataset: {e}")
            raise

    def get_dataset_stats(self) -> Dict[str, Any]:
        """Obtener estadísticas de datasets"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.execute(
                    """
                    SELECT 
                        COUNT(*) as total_datasets,
                        COUNT(DISTINCT format) as unique_formats,
                        SUM(file_size) as total_size,
                        SUM(row_count) as total_rows,
                        MIN(created_at) as earliest_dataset,
                        MAX(updated_at) as latest_update,
                        COUNT(CASE WHEN status = 'active' THEN 1 END) as active_datasets
                    FROM datasets
                """
                )
                result = cursor.fetchone()

                return {
                    "total_datasets": result[0],
                    "unique_formats": result[1],
                    "total_size_gb": (result[2] or 0) / (1024 * 1024 * 1024),
                    "total_rows": result[3] or 0,
                    "earliest_dataset": result[4],
                    "latest_update": result[5],
                    "active_datasets": result[6],
                }

        except Exception as e:
            self.logger.error(f"❌ Error obteniendo estadísticas: {e}")
            return {}

    def create_conversation_dataset(
        self, conversations: List[Dict[str, Any]], name: str, description: str = ""
    ) -> str:
        """Crear dataset de conversaciones"""
        try:
            # Convertir a DataFrame
            df = pd.DataFrame(conversations)

            # Generar ID único
            dataset_id = self._generate_dataset_id(name)

            # Guardar archivo
            file_path = self.datasets_dir / "conversations" / f"{dataset_id}.json"
            df.to_json(file_path, orient="records", indent=2)

            # Obtener información del archivo
            file_size, _ = self._get_file_info(file_path)
            checksum = self._calculate_file_checksum(file_path)

            # Registrar en base de datos
            with sqlite3.connect(self.db_path) as conn:
                conn.execute(
                    """
                    INSERT INTO datasets 
                    (id, name, description, file_path, file_size, format, columns, row_count, checksum, metadata)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                    (
                        dataset_id,
                        name,
                        description,
                        str(file_path),
                        file_size,
                        "json",
                        json.dumps(df.columns.tolist()),
                        len(df),
                        checksum,
                        json.dumps(
                            {"type": "conversations", "created_from_memory": True}
                        ),
                    ),
                )

            self.logger.info(
                f"✅ Dataset de conversaciones creado: {name} ({len(df)} conversaciones)"
            )
            return dataset_id

        except Exception as e:
            self.logger.error(f"❌ Error creando dataset de conversaciones: {e}")
            raise


# Instancia global del gestor de datasets
dataset_manager = DatasetManager()
