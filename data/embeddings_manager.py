#!/usr/bin/env python3
"""
Gestor de Embeddings del Sistema NeuroFusion
Maneja la generación, almacenamiento y búsqueda de embeddings vectoriales
"""

import json
import logging
import asyncio
import threading
from pathlib import Path
from typing import Dict, Any, List, Optional, Union, Tuple
from dataclasses import dataclass, asdict
import numpy as np
import faiss
from datetime import datetime, timedelta
import hashlib
import pickle
import gzip
from sentence_transformers import SentenceTransformer
from transformers import AutoTokenizer, AutoModel
import torch
from sklearn.metrics.pairwise import cosine_similarity
import sqlite3

# Configuración de logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@dataclass
class EmbeddingInfo:
    """Información de un embedding"""

    id: str
    text: str
    embedding_vector: List[float]
    model_name: str
    dimension: int
    created_at: datetime
    metadata: Dict[str, Any]


@dataclass
class SearchResult:
    """Resultado de búsqueda de embeddings"""

    id: str
    text: str
    similarity_score: float
    embedding_vector: List[float]
    metadata: Dict[str, Any]


class EmbeddingsManager:
    """Gestor principal de embeddings del sistema NeuroFusion"""

    def __init__(self, data_dir: str = "data"):
        self.data_dir = Path(data_dir)
        self.models = {}
        self.tokenizers = {}
        self.indices = {}
        self.cache = {}
        self.locks = {}
        self.connection = None

        # Inicializar directorios y conexiones
        self._initialize_directories()
        self._initialize_database()
        self._initialize_models()

    def _initialize_directories(self):
        """Inicializa los directorios necesarios"""
        directories = [
            self.data_dir / "embeddings",
            self.data_dir / "embeddings" / "models",
            self.data_dir / "embeddings" / "indices",
            self.data_dir / "embeddings" / "cache",
            self.data_dir / "embeddings" / "backups",
        ]

        for directory in directories:
            directory.mkdir(parents=True, exist_ok=True)
            logger.info(f"Directorio inicializado: {directory}")

    def _initialize_database(self):
        """Inicializa la base de datos de embeddings"""
        db_path = self.data_dir / "embeddings" / "embeddings.db"

        try:
            self.connection = sqlite3.connect(str(db_path), check_same_thread=False)
            self.connection.row_factory = sqlite3.Row
            self.locks["database"] = threading.Lock()

            # Crear tabla si no existe
            self._create_tables()
            logger.info("Base de datos de embeddings inicializada")

        except Exception as e:
            logger.error(f"Error inicializando base de datos: {e}")

    def _create_tables(self):
        """Crea las tablas necesarias en la base de datos"""
        with self.locks["database"]:
            cursor = self.connection.cursor()

            # Tabla de embeddings
            cursor.execute(
                """
                CREATE TABLE IF NOT EXISTS embeddings (
                    id TEXT PRIMARY KEY,
                    text TEXT NOT NULL,
                    embedding_vector TEXT NOT NULL,
                    model_name TEXT NOT NULL,
                    dimension INTEGER NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    metadata TEXT
                )
            """
            )

            # Tabla de modelos
            cursor.execute(
                """
                CREATE TABLE IF NOT EXISTS models (
                    name TEXT PRIMARY KEY,
                    type TEXT NOT NULL,
                    dimension INTEGER NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    metadata TEXT
                )
            """
            )

            # Tabla de índices
            cursor.execute(
                """
                CREATE TABLE IF NOT EXISTS indices (
                    name TEXT PRIMARY KEY,
                    model_name TEXT NOT NULL,
                    dimension INTEGER NOT NULL,
                    total_vectors INTEGER NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    metadata TEXT
                )
            """
            )

            self.connection.commit()

    def _initialize_models(self):
        """Inicializa los modelos de embeddings"""
        models_config = {
            "all-MiniLM-L6-v2": {
                "type": "sentence_transformer",
                "dimension": 384,
                "description": "Modelo de embeddings para oraciones",
            },
            "microsoft/Phi-3-mini-4k-instruct": {
                "type": "transformer",
                "dimension": 3072,
                "description": "Modelo de generación de texto",
            },
        }

        for model_name, config in models_config.items():
            try:
                if config["type"] == "sentence_transformer":
                    model = SentenceTransformer(model_name)
                    self.models[model_name] = model
                    logger.info(f"Modelo cargado: {model_name}")
                elif config["type"] == "transformer":
                    tokenizer = AutoTokenizer.from_pretrained(model_name)
                    model = AutoModel.from_pretrained(model_name)
                    self.tokenizers[model_name] = tokenizer
                    self.models[model_name] = model
                    logger.info(f"Modelo cargado: {model_name}")

            except Exception as e:
                logger.warning(f"Error cargando modelo {model_name}: {e}")

    def generate_embedding(
        self, text: str, model_name: str = "all-MiniLM-L6-v2"
    ) -> Optional[List[float]]:
        """Genera un embedding para un texto dado"""
        if not text:
            return None

        try:
            # Verificar caché
            cache_key = self._get_cache_key(text, model_name)
            cached_embedding = self.get_cached_embedding(cache_key)
            if cached_embedding is not None:
                return cached_embedding

            model = self.models.get(model_name)
            if not model:
                logger.error(f"Modelo no encontrado: {model_name}")
                return None

            # Generar embedding
            if isinstance(model, SentenceTransformer):
                embedding = model.encode(text, convert_to_tensor=False)
                embedding_list = (
                    embedding.tolist() if hasattr(embedding, "tolist") else embedding
                )
            else:
                # Modelo transformer
                tokenizer = self.tokenizers.get(model_name)
                if not tokenizer:
                    logger.error(f"Tokenizer no encontrado para: {model_name}")
                    return None

                inputs = tokenizer(
                    text,
                    return_tensors="pt",
                    padding=True,
                    truncation=True,
                    max_length=512,
                )
                with torch.no_grad():
                    outputs = model(**inputs)
                    # Usar el último estado oculto del primer token [CLS]
                    embedding = outputs.last_hidden_state[:, 0, :].numpy().flatten()
                    embedding_list = embedding.tolist()

            # Guardar en caché
            self.set_cached_embedding(cache_key, embedding_list)

            return embedding_list

        except Exception as e:
            logger.error(f"Error generando embedding: {e}")
            return None

    def generate_batch_embeddings(
        self, texts: List[str], model_name: str = "all-MiniLM-L6-v2"
    ) -> List[Optional[List[float]]]:
        """Genera embeddings para un lote de textos"""
        if not texts:
            return []

        try:
            model = self.models.get(model_name)
            if not model:
                logger.error(f"Modelo no encontrado: {model_name}")
                return [None] * len(texts)

            # Filtrar textos no vacíos
            valid_texts = [(i, text) for i, text in enumerate(texts) if text]
            valid_indices = [i for i, _ in valid_texts]
            valid_text_list = [text for _, text in valid_texts]

            if not valid_text_list:
                return [None] * len(texts)

            # Generar embeddings en lote
            if isinstance(model, SentenceTransformer):
                embeddings = model.encode(valid_text_list, convert_to_tensor=False)
                embeddings_list = (
                    embeddings.tolist() if hasattr(embeddings, "tolist") else embeddings
                )
            else:
                # Modelo transformer
                tokenizer = self.tokenizers.get(model_name)
                if not tokenizer:
                    logger.error(f"Tokenizer no encontrado para: {model_name}")
                    return [None] * len(texts)

                embeddings_list = []
                for text in valid_text_list:
                    inputs = tokenizer(
                        text,
                        return_tensors="pt",
                        padding=True,
                        truncation=True,
                        max_length=512,
                    )
                    with torch.no_grad():
                        outputs = model(**inputs)
                        embedding = outputs.last_hidden_state[:, 0, :].numpy().flatten()
                        embeddings_list.append(embedding.tolist())

            # Reconstruir lista completa
            result = [None] * len(texts)
            for (original_idx, _), embedding in zip(valid_texts, embeddings_list):
                result[original_idx] = embedding

            return result

        except Exception as e:
            logger.error(f"Error generando embeddings en lote: {e}")
            return [None] * len(texts)

    def save_embedding(
        self,
        text: str,
        embedding_vector: List[float],
        model_name: str,
        metadata: Dict = None,
    ) -> bool:
        """Guarda un embedding en la base de datos"""
        if not text or not embedding_vector:
            return False

        try:
            # Generar ID único
            embedding_id = hashlib.md5(f"{text}_{model_name}".encode()).hexdigest()

            with self.locks["database"]:
                cursor = self.connection.cursor()

                # Verificar si ya existe
                cursor.execute(
                    "SELECT id FROM embeddings WHERE id = ?", (embedding_id,)
                )
                if cursor.fetchone():
                    logger.warning(f"Embedding ya existe: {embedding_id}")
                    return False

                # Insertar embedding
                embedding_json = json.dumps(embedding_vector)
                metadata_json = json.dumps(metadata) if metadata else None

                cursor.execute(
                    """
                    INSERT INTO embeddings (id, text, embedding_vector, model_name, dimension, metadata)
                    VALUES (?, ?, ?, ?, ?, ?)
                """,
                    (
                        embedding_id,
                        text,
                        embedding_json,
                        model_name,
                        len(embedding_vector),
                        metadata_json,
                    ),
                )

                self.connection.commit()
                logger.info(f"Embedding guardado: {embedding_id}")
                return True

        except Exception as e:
            logger.error(f"Error guardando embedding: {e}")
            return False

    def get_embedding(self, embedding_id: str) -> Optional[EmbeddingInfo]:
        """Obtiene un embedding por ID"""
        try:
            with self.locks["database"]:
                cursor = self.connection.cursor()
                cursor.execute("SELECT * FROM embeddings WHERE id = ?", (embedding_id,))
                row = cursor.fetchone()

                if row:
                    return EmbeddingInfo(
                        id=row["id"],
                        text=row["text"],
                        embedding_vector=json.loads(row["embedding_vector"]),
                        model_name=row["model_name"],
                        dimension=row["dimension"],
                        created_at=datetime.fromisoformat(row["created_at"]),
                        metadata=json.loads(row["metadata"]) if row["metadata"] else {},
                    )
                else:
                    return None

        except Exception as e:
            logger.error(f"Error obteniendo embedding: {e}")
            return None

    def search_similar_embeddings(
        self,
        query_embedding: List[float],
        model_name: str = "all-MiniLM-L6-v2",
        top_k: int = 10,
    ) -> List[SearchResult]:
        """Busca embeddings similares"""
        if not query_embedding:
            return []

        try:
            # Obtener todos los embeddings del modelo
            with self.locks["database"]:
                cursor = self.connection.cursor()
                cursor.execute(
                    """
                    SELECT * FROM embeddings 
                    WHERE model_name = ? 
                    ORDER BY created_at DESC
                """,
                    (model_name,),
                )
                rows = cursor.fetchall()

            if not rows:
                return []

            # Calcular similitudes
            similarities = []
            query_array = np.array(query_embedding)

            for row in rows:
                embedding_vector = json.loads(row["embedding_vector"])
                embedding_array = np.array(embedding_vector)

                # Calcular similitud coseno
                similarity = np.dot(query_array, embedding_array) / (
                    np.linalg.norm(query_array) * np.linalg.norm(embedding_array)
                )

                similarities.append(
                    SearchResult(
                        id=row["id"],
                        text=row["text"],
                        similarity_score=float(similarity),
                        embedding_vector=embedding_vector,
                        metadata=json.loads(row["metadata"]) if row["metadata"] else {},
                    )
                )

            # Ordenar por similitud y retornar top k
            similarities.sort(key=lambda x: x.similarity_score, reverse=True)
            return similarities[:top_k]

        except Exception as e:
            logger.error(f"Error buscando embeddings similares: {e}")
            return []

    def create_faiss_index(self, model_name: str = "all-MiniLM-L6-v2") -> bool:
        """Crea un índice FAISS para búsqueda rápida"""
        try:
            # Obtener embeddings del modelo
            with self.locks["database"]:
                cursor = self.connection.cursor()
                cursor.execute(
                    """
                    SELECT * FROM embeddings 
                    WHERE model_name = ?
                """,
                    (model_name,),
                )
                rows = cursor.fetchall()

            if not rows:
                logger.warning(f"No hay embeddings para crear índice: {model_name}")
                return False

            # Preparar datos para FAISS
            embeddings = []
            ids = []

            for row in rows:
                embedding_vector = json.loads(row["embedding_vector"])
                embeddings.append(embedding_vector)
                ids.append(row["id"])

            embeddings_array = np.array(embeddings, dtype=np.float32)
            dimension = embeddings_array.shape[1]

            # Crear índice FAISS
            index = faiss.IndexFlatIP(dimension)  # Inner Product para similitud coseno
            index.add(embeddings_array)

            # Guardar índice
            index_path = (
                self.data_dir / "embeddings" / "indices" / f"{model_name}_index.faiss"
            )
            faiss.write_index(index, str(index_path))

            # Guardar mapeo de IDs
            ids_path = (
                self.data_dir / "embeddings" / "indices" / f"{model_name}_ids.pkl"
            )
            with open(ids_path, "wb") as f:
                pickle.dump(ids, f)

            # Actualizar base de datos
            with self.locks["database"]:
                cursor = self.connection.cursor()
                cursor.execute(
                    """
                    INSERT OR REPLACE INTO indices (name, model_name, dimension, total_vectors, metadata)
                    VALUES (?, ?, ?, ?, ?)
                """,
                    (
                        f"{model_name}_index",
                        model_name,
                        dimension,
                        len(embeddings),
                        json.dumps({"created_at": datetime.now().isoformat()}),
                    ),
                )
                self.connection.commit()

            logger.info(
                f"Índice FAISS creado: {model_name} ({len(embeddings)} vectores)"
            )
            return True

        except Exception as e:
            logger.error(f"Error creando índice FAISS: {e}")
            return False

    def load_faiss_index(
        self, model_name: str = "all-MiniLM-L6-v2"
    ) -> Optional[Tuple[faiss.Index, List[str]]]:
        """Carga un índice FAISS"""
        try:
            index_path = (
                self.data_dir / "embeddings" / "indices" / f"{model_name}_index.faiss"
            )
            ids_path = (
                self.data_dir / "embeddings" / "indices" / f"{model_name}_ids.pkl"
            )

            if not index_path.exists() or not ids_path.exists():
                logger.warning(f"Índice FAISS no encontrado: {model_name}")
                return None

            # Cargar índice
            index = faiss.read_index(str(index_path))

            # Cargar IDs
            with open(ids_path, "rb") as f:
                ids = pickle.load(f)

            logger.info(f"Índice FAISS cargado: {model_name} ({len(ids)} vectores)")
            return index, ids

        except Exception as e:
            logger.error(f"Error cargando índice FAISS: {e}")
            return None

    def search_faiss_index(
        self,
        query_embedding: List[float],
        model_name: str = "all-MiniLM-L6-v2",
        top_k: int = 10,
    ) -> List[SearchResult]:
        """Busca usando índice FAISS"""
        try:
            # Cargar índice
            index_data = self.load_faiss_index(model_name)
            if not index_data:
                return []

            index, ids = index_data

            # Preparar query
            query_array = np.array([query_embedding], dtype=np.float32)

            # Buscar
            similarities, indices = index.search(query_array, top_k)

            # Obtener resultados
            results = []
            for i, (similarity, idx) in enumerate(zip(similarities[0], indices[0])):
                if idx != -1:  # FAISS retorna -1 para resultados no válidos
                    embedding_id = ids[idx]
                    embedding_info = self.get_embedding(embedding_id)

                    if embedding_info:
                        results.append(
                            SearchResult(
                                id=embedding_info.id,
                                text=embedding_info.text,
                                similarity_score=float(similarity),
                                embedding_vector=embedding_info.embedding_vector,
                                metadata=embedding_info.metadata,
                            )
                        )

            return results

        except Exception as e:
            logger.error(f"Error buscando en índice FAISS: {e}")
            return []

    def _get_cache_key(self, text: str, model_name: str) -> str:
        """Genera una clave de caché"""
        return hashlib.md5(f"{text}_{model_name}".encode()).hexdigest()

    def get_cached_embedding(self, cache_key: str) -> Optional[List[float]]:
        """Obtiene un embedding del caché"""
        cache_path = self.data_dir / "embeddings" / "cache" / f"{cache_key}.pkl.gz"

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

            return data.get("embedding")

        except Exception as e:
            logger.error(f"Error cargando caché: {e}")
            return None

    def set_cached_embedding(
        self, cache_key: str, embedding: List[float], ttl_hours: int = 24
    ):
        """Guarda un embedding en el caché"""
        cache_path = self.data_dir / "embeddings" / "cache" / f"{cache_key}.pkl.gz"

        try:
            data = {
                "embedding": embedding,
                "created_at": datetime.now().isoformat(),
                "expires_at": (datetime.now() + timedelta(hours=ttl_hours)).isoformat(),
            }

            with gzip.open(cache_path, "wb") as f:
                pickle.dump(data, f)

        except Exception as e:
            logger.error(f"Error guardando caché: {e}")

    def clear_cache(self, pattern: str = "*") -> int:
        """Limpia el caché de embeddings"""
        cache_dir = self.data_dir / "embeddings" / "cache"
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

    def get_embeddings_stats(self) -> Dict[str, Any]:
        """Obtiene estadísticas de embeddings"""
        try:
            with self.locks["database"]:
                cursor = self.connection.cursor()

                # Estadísticas generales
                cursor.execute("SELECT COUNT(*) as total FROM embeddings")
                total_embeddings = cursor.fetchone()["total"]

                # Estadísticas por modelo
                cursor.execute(
                    """
                    SELECT model_name, COUNT(*) as count, AVG(dimension) as avg_dimension
                    FROM embeddings 
                    GROUP BY model_name
                """
                )
                model_stats = [dict(row) for row in cursor.fetchall()]

                # Estadísticas de índices
                cursor.execute("SELECT * FROM indices")
                index_stats = [dict(row) for row in cursor.fetchall()]

                return {
                    "total_embeddings": total_embeddings,
                    "model_stats": model_stats,
                    "index_stats": index_stats,
                    "cache_size": len(
                        list((self.data_dir / "embeddings" / "cache").glob("*.pkl.gz"))
                    ),
                }

        except Exception as e:
            logger.error(f"Error obteniendo estadísticas: {e}")
            return {}

    def backup_embeddings(self, backup_name: str = None) -> str:
        """Crea un backup de todos los embeddings"""
        if backup_name is None:
            backup_name = (
                f"embeddings_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            )

        backup_dir = self.data_dir / "embeddings" / "backups" / backup_name
        backup_dir.mkdir(parents=True, exist_ok=True)

        try:
            # Backup de base de datos
            db_backup_path = backup_dir / "embeddings.db"
            with self.locks["database"]:
                backup_conn = sqlite3.connect(str(db_backup_path))
                self.connection.backup(backup_conn)
                backup_conn.close()

            # Backup de índices
            indices_dir = self.data_dir / "embeddings" / "indices"
            if indices_dir.exists():
                import shutil

                shutil.copytree(indices_dir, backup_dir / "indices")

            logger.info(f"Backup de embeddings creado: {backup_dir}")
            return str(backup_dir)

        except Exception as e:
            logger.error(f"Error creando backup: {e}")
            raise

    def close_connection(self):
        """Cierra la conexión a la base de datos"""
        if self.connection:
            try:
                self.connection.close()
                logger.info("Conexión a base de datos cerrada")
            except Exception as e:
                logger.error(f"Error cerrando conexión: {e}")


# Instancia global del gestor de embeddings
embeddings_manager = EmbeddingsManager()


def get_embeddings_manager() -> EmbeddingsManager:
    """Obtiene la instancia global del gestor de embeddings"""
    return embeddings_manager


if __name__ == "__main__":
    # Ejemplo de uso
    manager = EmbeddingsManager()

    # Generar embedding
    text = "El sistema NeuroFusion es una plataforma avanzada de IA"
    embedding = manager.generate_embedding(text)

    if embedding:
        print(f"Embedding generado: {len(embedding)} dimensiones")

        # Guardar embedding
        success = manager.save_embedding(text, embedding, "all-MiniLM-L6-v2")
        print(f"Embedding guardado: {success}")

        # Buscar similares
        results = manager.search_similar_embeddings(embedding, top_k=5)
        print(f"Resultados encontrados: {len(results)}")

    # Cerrar conexión
    manager.close_connection()
