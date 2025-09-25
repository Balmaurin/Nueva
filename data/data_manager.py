#!/usr/bin/env python3
"""
Gestor de Datos del Sistema NeuroFusion
Maneja todas las bases de datos, corpus y cachés del sistema
"""

import sqlite3
import json
import logging
import asyncio
import threading
from pathlib import Path
from typing import Dict, Any, List, Optional, Union, Tuple
from dataclasses import dataclass, asdict
import duckdb
import faiss
import numpy as np
from datetime import datetime, timedelta
import hashlib
import pickle
import gzip
import shutil

# Configuración de logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@dataclass
class DataStats:
    """Estadísticas de datos"""

    total_documents: int
    total_embeddings: int
    total_users: int
    total_memories: int
    corpus_size_mb: float
    index_size_mb: float
    last_updated: datetime


@dataclass
class CorpusInfo:
    """Información del corpus"""

    name: str
    language: str
    document_count: int
    total_words: int
    categories: List[str]
    last_updated: datetime
    file_size_mb: float


class DataManager:
    """Gestor principal de datos del sistema NeuroFusion"""

    def __init__(self, data_dir: str = "data"):
        self.data_dir = Path(data_dir)
        self.connections = {}
        self.locks = {}
        self.cache = {}
        self._initialize_directories()
        self._initialize_connections()

    def _initialize_directories(self):
        """Inicializa los directorios necesarios"""
        directories = [
            self.data_dir,
            self.data_dir / "corpus",
            self.data_dir / "embeddings",
            self.data_dir / "cache",
            self.data_dir / "backups",
            self.data_dir / "temp",
            self.data_dir / "exports",
        ]

        for directory in directories:
            directory.mkdir(parents=True, exist_ok=True)
            logger.info(f"Directorio inicializado: {directory}")

    def _initialize_connections(self):
        """Inicializa las conexiones a las bases de datos"""
        databases = {
            "knowledge_base": self.data_dir / "knowledge_base.db",
            "embeddings": self.data_dir / "embeddings_sqlite.db",
            "rag_memory": self.data_dir / "rag_memory.duckdb",
            "user_data": self.data_dir / "user_data.duckdb",
            "embeddings_cache": self.data_dir
            / "embedding_cache"
            / "embeddings_cache.db",
        }

        for db_name, db_path in databases.items():
            if db_path.exists():
                self._create_connection(db_name, db_path)
            else:
                logger.warning(f"Base de datos no encontrada: {db_path}")

    def _create_connection(self, db_name: str, db_path: Path):
        """Crea una conexión a una base de datos"""
        try:
            if db_path.suffix == ".duckdb":
                # Conexión DuckDB
                conn = duckdb.connect(str(db_path))
                self.connections[db_name] = conn
                self.locks[db_name] = threading.Lock()
                logger.info(f"Conexión DuckDB creada: {db_name}")
            else:
                # Conexión SQLite
                conn = sqlite3.connect(str(db_path), check_same_thread=False)
                conn.row_factory = sqlite3.Row
                self.connections[db_name] = conn
                self.locks[db_name] = threading.Lock()
                logger.info(f"Conexión SQLite creada: {db_name}")
        except Exception as e:
            logger.error(f"Error creando conexión a {db_name}: {e}")

    def get_connection(self, db_name: str):
        """Obtiene una conexión a una base de datos específica"""
        if db_name not in self.connections:
            raise ValueError(f"Base de datos no encontrada: {db_name}")
        return self.connections[db_name]

    def execute_query(
        self, db_name: str, query: str, params: tuple = None
    ) -> List[Dict]:
        """Ejecuta una consulta en una base de datos específica"""
        with self.locks[db_name]:
            conn = self.get_connection(db_name)
            try:
                cursor = conn.cursor()
                if params:
                    cursor.execute(query, params)
                else:
                    cursor.execute(query)

                if query.strip().upper().startswith("SELECT"):
                    columns = [description[0] for description in cursor.description]
                    results = [dict(zip(columns, row)) for row in cursor.fetchall()]
                    return results
                else:
                    conn.commit()
                    return [{"affected_rows": cursor.rowcount}]

            except Exception as e:
                logger.error(f"Error ejecutando consulta en {db_name}: {e}")
                conn.rollback()
                raise

    def get_knowledge_base_data(self, limit: int = 100) -> List[Dict]:
        """Obtiene datos de la base de conocimientos"""
        query = """
        SELECT * FROM knowledge_base 
        ORDER BY created_at DESC 
        LIMIT ?
        """
        return self.execute_query("knowledge_base", query, (limit,))

    def add_knowledge_entry(
        self, title: str, content: str, category: str, metadata: Dict = None
    ) -> bool:
        """Agrega una entrada a la base de conocimientos"""
        query = """
        INSERT INTO knowledge_base (title, content, category, metadata, created_at)
        VALUES (?, ?, ?, ?, ?)
        """
        try:
            metadata_json = json.dumps(metadata) if metadata else None
            self.execute_query(
                "knowledge_base",
                query,
                (title, content, category, metadata_json, datetime.now()),
            )
            return True
        except Exception as e:
            logger.error(f"Error agregando entrada de conocimiento: {e}")
            return False

    def get_embeddings_data(self, limit: int = 100) -> List[Dict]:
        """Obtiene datos de embeddings"""
        query = """
        SELECT * FROM embeddings 
        ORDER BY created_at DESC 
        LIMIT ?
        """
        return self.execute_query("embeddings", query, (limit,))

    def add_embedding(
        self,
        text: str,
        embedding_vector: List[float],
        model_name: str,
        metadata: Dict = None,
    ) -> bool:
        """Agrega un embedding a la base de datos"""
        query = """
        INSERT INTO embeddings (text, embedding_vector, model_name, metadata, created_at)
        VALUES (?, ?, ?, ?, ?)
        """
        try:
            embedding_json = json.dumps(embedding_vector)
            metadata_json = json.dumps(metadata) if metadata else None
            self.execute_query(
                "embeddings",
                query,
                (text, embedding_json, model_name, metadata_json, datetime.now()),
            )
            return True
        except Exception as e:
            logger.error(f"Error agregando embedding: {e}")
            return False

    def get_user_data(self, user_id: str = None, limit: int = 100) -> List[Dict]:
        """Obtiene datos de usuarios"""
        if user_id:
            query = "SELECT * FROM user_data WHERE user_id = ? ORDER BY created_at DESC"
            return self.execute_query("user_data", query, (user_id,))
        else:
            query = "SELECT * FROM user_data ORDER BY created_at DESC LIMIT ?"
            return self.execute_query("user_data", query, (limit,))

    def add_user_data(
        self, user_id: str, data_type: str, data_content: Dict, metadata: Dict = None
    ) -> bool:
        """Agrega datos de usuario"""
        query = """
        INSERT INTO user_data (user_id, data_type, data_content, metadata, created_at)
        VALUES (?, ?, ?, ?, ?)
        """
        try:
            content_json = json.dumps(data_content)
            metadata_json = json.dumps(metadata) if metadata else None
            self.execute_query(
                "user_data",
                query,
                (user_id, data_type, content_json, metadata_json, datetime.now()),
            )
            return True
        except Exception as e:
            logger.error(f"Error agregando datos de usuario: {e}")
            return False

    def get_rag_memory_data(self, query: str = None, limit: int = 100) -> List[Dict]:
        """Obtiene datos de memoria RAG"""
        if query:
            sql_query = """
            SELECT * FROM rag_memory 
            WHERE content LIKE ? 
            ORDER BY created_at DESC 
            LIMIT ?
            """
            return self.execute_query("rag_memory", sql_query, (f"%{query}%", limit))
        else:
            sql_query = "SELECT * FROM rag_memory ORDER BY created_at DESC LIMIT ?"
            return self.execute_query("rag_memory", sql_query, (limit,))

    def add_rag_memory(
        self,
        content: str,
        source: str,
        embedding_vector: List[float],
        metadata: Dict = None,
    ) -> bool:
        """Agrega una entrada a la memoria RAG"""
        query = """
        INSERT INTO rag_memory (content, source, embedding_vector, metadata, created_at)
        VALUES (?, ?, ?, ?, ?)
        """
        try:
            embedding_json = json.dumps(embedding_vector)
            metadata_json = json.dumps(metadata) if metadata else None
            self.execute_query(
                "rag_memory",
                query,
                (content, source, embedding_json, metadata_json, datetime.now()),
            )
            return True
        except Exception as e:
            logger.error(f"Error agregando memoria RAG: {e}")
            return False

    def load_corpus(self, corpus_name: str) -> Dict[str, Any]:
        """Carga un corpus desde archivo"""
        corpus_path = self.data_dir / "corpus" / f"{corpus_name}.json"

        if not corpus_path.exists():
            logger.warning(f"Corpus no encontrado: {corpus_path}")
            return {}

        try:
            with open(corpus_path, "r", encoding="utf-8") as f:
                corpus_data = json.load(f)

            # Calcular estadísticas
            stats = self._calculate_corpus_stats(corpus_data)
            corpus_data["stats"] = stats

            logger.info(
                f"Corpus cargado: {corpus_name} ({stats['document_count']} documentos)"
            )
            return corpus_data

        except Exception as e:
            logger.error(f"Error cargando corpus {corpus_name}: {e}")
            return {}

    def save_corpus(self, corpus_name: str, corpus_data: Dict[str, Any]) -> bool:
        """Guarda un corpus en archivo"""
        corpus_path = self.data_dir / "corpus" / f"{corpus_name}.json"

        try:
            # Crear backup si existe
            if corpus_path.exists():
                backup_path = (
                    self.data_dir
                    / "backups"
                    / f"{corpus_name}_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
                )
                shutil.copy2(corpus_path, backup_path)
                logger.info(f"Backup creado: {backup_path}")

            # Guardar corpus
            with open(corpus_path, "w", encoding="utf-8") as f:
                json.dump(corpus_data, f, indent=2, ensure_ascii=False)

            logger.info(f"Corpus guardado: {corpus_name}")
            return True

        except Exception as e:
            logger.error(f"Error guardando corpus {corpus_name}: {e}")
            return False

    def _calculate_corpus_stats(self, corpus_data: Dict[str, Any]) -> Dict[str, Any]:
        """Calcula estadísticas de un corpus"""
        documents = corpus_data.get("documents", [])
        total_words = sum(len(doc.get("content", "").split()) for doc in documents)

        return {
            "document_count": len(documents),
            "total_words": total_words,
            "categories": list(set(doc.get("category", "") for doc in documents)),
            "last_updated": datetime.now().isoformat(),
            "file_size_mb": 0,  # Se calculará después
        }

    def load_faiss_index(
        self, index_name: str = "faiss_index"
    ) -> Optional[faiss.Index]:
        """Carga un índice FAISS"""
        index_path = self.data_dir / f"{index_name}.index"

        if not index_path.exists():
            logger.warning(f"Índice FAISS no encontrado: {index_path}")
            return None

        try:
            index = faiss.read_index(str(index_path))
            logger.info(f"Índice FAISS cargado: {index_name} ({index.ntotal} vectores)")
            return index
        except Exception as e:
            logger.error(f"Error cargando índice FAISS {index_name}: {e}")
            return None

    def save_faiss_index(
        self, index: faiss.Index, index_name: str = "faiss_index"
    ) -> bool:
        """Guarda un índice FAISS"""
        index_path = self.data_dir / f"{index_name}.index"

        try:
            # Crear backup si existe
            if index_path.exists():
                backup_path = (
                    self.data_dir
                    / "backups"
                    / f"{index_name}_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.index"
                )
                shutil.copy2(index_path, backup_path)
                logger.info(f"Backup creado: {backup_path}")

            # Guardar índice
            faiss.write_index(index, str(index_path))
            logger.info(f"Índice FAISS guardado: {index_name}")
            return True

        except Exception as e:
            logger.error(f"Error guardando índice FAISS {index_name}: {e}")
            return False

    def get_cache_data(self, cache_key: str) -> Optional[Any]:
        """Obtiene datos del caché"""
        cache_path = self.data_dir / "cache" / f"{cache_key}.pkl.gz"

        if not cache_path.exists():
            return None

        try:
            with gzip.open(cache_path, "rb") as f:
                data = pickle.load(f)

            # Verificar expiración
            if "expires_at" in data:
                if datetime.now() > datetime.fromisoformat(data["expires_at"]):
                    cache_path.unlink()
                    return None

            return data.get("value")

        except Exception as e:
            logger.error(f"Error cargando caché {cache_key}: {e}")
            return None

    def set_cache_data(self, cache_key: str, value: Any, ttl_hours: int = 24) -> bool:
        """Establece datos en el caché"""
        cache_path = self.data_dir / "cache" / f"{cache_key}.pkl.gz"

        try:
            data = {
                "value": value,
                "created_at": datetime.now().isoformat(),
                "expires_at": (datetime.now() + timedelta(hours=ttl_hours)).isoformat(),
            }

            with gzip.open(cache_path, "wb") as f:
                pickle.dump(data, f)

            logger.debug(f"Datos guardados en caché: {cache_key}")
            return True

        except Exception as e:
            logger.error(f"Error guardando caché {cache_key}: {e}")
            return False

    def clear_cache(self, pattern: str = "*") -> int:
        """Limpia el caché según un patrón"""
        cache_dir = self.data_dir / "cache"
        cleared_count = 0

        try:
            for cache_file in cache_dir.glob(f"{pattern}.pkl.gz"):
                cache_file.unlink()
                cleared_count += 1

            logger.info(f"Caché limpiado: {cleared_count} archivos eliminados")
            return cleared_count

        except Exception as e:
            logger.error(f"Error limpiando caché: {e}")
            return 0

    def get_data_stats(self) -> DataStats:
        """Obtiene estadísticas generales de los datos"""
        try:
            # Contar documentos en bases de datos
            kb_count = len(self.get_knowledge_base_data(limit=10000))
            embeddings_count = len(self.get_embeddings_data(limit=10000))
            user_count = len(self.get_user_data(limit=10000))
            rag_count = len(self.get_rag_memory_data(limit=10000))

            # Calcular tamaños de archivos
            corpus_size = sum(
                f.stat().st_size for f in self.data_dir.glob("corpus/*.json")
            )
            index_size = sum(f.stat().st_size for f in self.data_dir.glob("*.index"))

            return DataStats(
                total_documents=kb_count,
                total_embeddings=embeddings_count,
                total_users=user_count,
                total_memories=rag_count,
                corpus_size_mb=corpus_size / (1024 * 1024),
                index_size_mb=index_size / (1024 * 1024),
                last_updated=datetime.now(),
            )

        except Exception as e:
            logger.error(f"Error obteniendo estadísticas: {e}")
            return DataStats(0, 0, 0, 0, 0.0, 0.0, datetime.now())

    def create_backup(self, backup_name: str = None) -> str:
        """Crea un backup completo de todos los datos"""
        if backup_name is None:
            backup_name = f"data_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}"

        backup_dir = self.data_dir / "backups" / backup_name
        backup_dir.mkdir(parents=True, exist_ok=True)

        try:
            # Backup de bases de datos
            for db_name, conn in self.connections.items():
                if hasattr(conn, "backup"):
                    # SQLite backup
                    backup_path = backup_dir / f"{db_name}.db"
                    conn.backup(backup_path)
                else:
                    # DuckDB backup
                    backup_path = backup_dir / f"{db_name}.duckdb"
                    shutil.copy2(self.data_dir / f"{db_name}.duckdb", backup_path)

            # Backup de archivos de datos
            for file_path in self.data_dir.glob("*.index"):
                shutil.copy2(file_path, backup_dir / file_path.name)

            for file_path in self.data_dir.glob("corpus/*.json"):
                shutil.copy2(file_path, backup_dir / file_path.name)

            logger.info(f"Backup creado: {backup_dir}")
            return str(backup_dir)

        except Exception as e:
            logger.error(f"Error creando backup: {e}")
            raise

    def restore_backup(self, backup_path: str) -> bool:
        """Restaura datos desde un backup"""
        backup_dir = Path(backup_path)

        if not backup_dir.exists():
            logger.error(f"Backup no encontrado: {backup_path}")
            return False

        try:
            # Crear backup del estado actual
            current_backup = self.create_backup()

            # Restaurar bases de datos
            for db_file in backup_dir.glob("*.db"):
                target_path = self.data_dir / db_file.name
                shutil.copy2(db_file, target_path)

            for db_file in backup_dir.glob("*.duckdb"):
                target_path = self.data_dir / db_file.name
                shutil.copy2(db_file, target_path)

            # Restaurar archivos de datos
            for file_path in backup_dir.glob("*.index"):
                shutil.copy2(file_path, self.data_dir / file_path.name)

            for file_path in backup_dir.glob("*.json"):
                shutil.copy2(file_path, self.data_dir / "corpus" / file_path.name)

            # Reinicializar conexiones
            self._initialize_connections()

            logger.info(f"Datos restaurados desde: {backup_path}")
            return True

        except Exception as e:
            logger.error(f"Error restaurando backup: {e}")
            return False

    def export_data(self, export_format: str = "json", filters: Dict = None) -> str:
        """Exporta datos en diferentes formatos"""
        export_dir = self.data_dir / "exports"
        export_dir.mkdir(exist_ok=True)

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        export_file = export_dir / f"data_export_{timestamp}.{export_format}"

        try:
            export_data = {
                "export_info": {
                    "timestamp": timestamp,
                    "format": export_format,
                    "filters": filters,
                },
                "knowledge_base": self.get_knowledge_base_data(limit=1000),
                "embeddings": self.get_embeddings_data(limit=1000),
                "user_data": self.get_user_data(limit=1000),
                "rag_memory": self.get_rag_memory_data(limit=1000),
                "stats": asdict(self.get_data_stats()),
            }

            if export_format == "json":
                with open(export_file, "w", encoding="utf-8") as f:
                    json.dump(export_data, f, indent=2, ensure_ascii=False)
            elif export_format == "csv":
                # Implementar exportación CSV
                pass

            logger.info(f"Datos exportados: {export_file}")
            return str(export_file)

        except Exception as e:
            logger.error(f"Error exportando datos: {e}")
            raise

    def cleanup_old_data(self, days_old: int = 30) -> int:
        """Limpia datos antiguos"""
        cutoff_date = datetime.now() - timedelta(days=days_old)
        cleaned_count = 0

        try:
            # Limpiar caché expirado
            cache_dir = self.data_dir / "cache"
            for cache_file in cache_dir.glob("*.pkl.gz"):
                if cache_file.stat().st_mtime < cutoff_date.timestamp():
                    cache_file.unlink()
                    cleaned_count += 1

            # Limpiar backups antiguos
            backup_dir = self.data_dir / "backups"
            for backup_file in backup_dir.glob("*"):
                if backup_file.stat().st_mtime < cutoff_date.timestamp():
                    if backup_file.is_dir():
                        shutil.rmtree(backup_file)
                    else:
                        backup_file.unlink()
                    cleaned_count += 1

            logger.info(f"Limpieza completada: {cleaned_count} elementos eliminados")
            return cleaned_count

        except Exception as e:
            logger.error(f"Error en limpieza: {e}")
            return 0

    def close_connections(self):
        """Cierra todas las conexiones a bases de datos"""
        for db_name, conn in self.connections.items():
            try:
                conn.close()
                logger.info(f"Conexión cerrada: {db_name}")
            except Exception as e:
                logger.error(f"Error cerrando conexión {db_name}: {e}")

        self.connections.clear()
        self.locks.clear()


# Instancia global del gestor de datos
data_manager = DataManager()


def get_data_manager() -> DataManager:
    """Obtiene la instancia global del gestor de datos"""
    return data_manager


if __name__ == "__main__":
    # Ejemplo de uso
    manager = DataManager()

    # Obtener estadísticas
    stats = manager.get_data_stats()
    print(f"Estadísticas de datos: {stats}")

    # Cargar corpus
    corpus = manager.load_corpus("complete_spanish_corpus")
    print(f"Corpus cargado: {len(corpus.get('documents', []))} documentos")

    # Cerrar conexiones
    manager.close_connections()
