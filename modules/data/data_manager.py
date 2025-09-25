#!/usr/bin/env python3
"""
Sistema de Gestión de Datos
Gestiona el almacenamiento, procesamiento y acceso a datos del sistema
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
import faiss
from dataclasses import dataclass, asdict
import pickle
import gzip
import sqlalchemy as sa
from sqlalchemy.orm import sessionmaker, declarative_base
from sqlalchemy.types import JSON, LargeBinary

Base = declarative_base()


class UserInteraction(Base):
    __tablename__ = "user_interactions"

    id = sa.Column(sa.String, primary_key=True)
    user_id = sa.Column(sa.String)
    session_id = sa.Column(sa.String)
    interaction_type = sa.Column(sa.String)
    content = sa.Column(sa.Text)
    response = sa.Column(sa.Text)
    timestamp = sa.Column(sa.DateTime, default=datetime.now)
    duration_ms = sa.Column(sa.Integer)
    metadata = sa.Column(JSON)


class LearningData(Base):
    __tablename__ = "learning_data"

    id = sa.Column(sa.String, primary_key=True)
    branch_name = sa.Column(sa.String)
    question = sa.Column(sa.Text)
    answer = sa.Column(sa.Text)
    difficulty = sa.Column(sa.Float)
    category = sa.Column(sa.String)
    created_at = sa.Column(sa.DateTime, default=datetime.now)
    usage_count = sa.Column(sa.Integer, default=0)
    success_rate = sa.Column(sa.Float, default=0.0)


class RAGMemory(Base):
    __tablename__ = "rag_memory"

    id = sa.Column(sa.String, primary_key=True)
    content = sa.Column(sa.Text, nullable=False)
    embedding_path = sa.Column(sa.String)
    source = sa.Column(sa.String)
    domain = sa.Column(sa.String)
    relevance_score = sa.Column(sa.Float, default=1.0)
    access_count = sa.Column(sa.Integer, default=0)
    last_accessed = sa.Column(sa.DateTime, default=datetime.now)
    created_at = sa.Column(sa.DateTime, default=datetime.now)
    metadata = sa.Column(JSON)


@dataclass
class DataRecord:
    """Estructura de datos para un registro"""

    id: str
    content: str
    embedding: Optional[np.ndarray]
    metadata: Dict[str, Any]
    created_at: datetime
    updated_at: datetime
    data_type: str = "text"
    source: str = "unknown"


class DataManager:
    """Gestor completo de datos con funciones reales"""

    def __init__(
        self,
        data_dir: str = "data",
        db_url: str = "postgresql://user:password@localhost/sheily_db",
    ):
        self.data_dir = Path(data_dir)
        self.data_dir.mkdir(exist_ok=True)

        # Configurar logging
        self.logger = logging.getLogger(__name__)
        self.logger.setLevel(logging.INFO)

        # Configuración de base de datos PostgreSQL
        self.engine = sa.create_engine(db_url)
        Base.metadata.create_all(self.engine)
        self.Session = sessionmaker(bind=self.engine)

        # Lock para operaciones thread-safe
        self._lock = threading.Lock()

        # Configuración de índices
        self.faiss_index = None
        self._load_faiss_index()

        # Métricas de datos
        self.total_records = 0
        self.total_size_mb = 0

        self.logger.info(f"✅ DataManager inicializado en {self.data_dir}")

    def store_user_interaction(
        self,
        user_id: str,
        session_id: str,
        interaction_type: str,
        content: str,
        response: str,
        duration_ms: int = 0,
        metadata: Dict[str, Any] = None,
    ) -> str:
        """Almacenar interacción de usuario"""
        try:
            interaction_id = f"int_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{hashlib.md5(content.encode()).hexdigest()[:8]}"

            session = self.Session()
            try:
                interaction = UserInteraction(
                    id=interaction_id,
                    user_id=user_id,
                    session_id=session_id,
                    interaction_type=interaction_type,
                    content=content,
                    response=response,
                    duration_ms=duration_ms,
                    metadata=metadata or {},
                )
                session.add(interaction)
                session.commit()

                self.logger.debug(f"💾 Interacción almacenada: {interaction_id}")
                return interaction_id
            except Exception as e:
                session.rollback()
                raise
            finally:
                session.close()

        except Exception as e:
            self.logger.error(f"❌ Error almacenando interacción: {e}")
            raise

    def store_learning_data(
        self,
        branch_name: str,
        question: str,
        answer: str,
        difficulty: float = 0.5,
        category: str = "general",
    ) -> str:
        """Almacenar datos de aprendizaje"""
        try:
            learning_id = f"learn_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{hashlib.md5(question.encode()).hexdigest()[:8]}"

            session = self.Session()
            try:
                learning_data = LearningData(
                    id=learning_id,
                    branch_name=branch_name,
                    question=question,
                    answer=answer,
                    difficulty=difficulty,
                    category=category,
                )
                session.add(learning_data)
                session.commit()

                self.logger.info(f"💾 Datos de aprendizaje almacenados: {learning_id}")
                return learning_id
            except Exception as e:
                session.rollback()
                raise
            finally:
                session.close()

        except Exception as e:
            self.logger.error(f"❌ Error almacenando datos de aprendizaje: {e}")
            raise

    def get_learning_data(
        self, branch_name: str = None, category: str = None, limit: int = 100
    ) -> List[Dict[str, Any]]:
        """Obtener datos de aprendizaje"""
        try:
            session = self.Session()
            try:
                query = session.query(LearningData)

                if branch_name:
                    query = query.filter(LearningData.branch_name == branch_name)

                if category:
                    query = query.filter(LearningData.category == category)

                query = query.order_by(LearningData.created_at.desc()).limit(limit)

                result = query.all()
                return [
                    {
                        "id": item.id,
                        "branch_name": item.branch_name,
                        "question": item.question,
                        "answer": item.answer,
                        "difficulty": item.difficulty,
                        "category": item.category,
                        "created_at": item.created_at,
                        "usage_count": item.usage_count,
                        "success_rate": item.success_rate,
                    }
                    for item in result
                ]
            finally:
                session.close()

        except Exception as e:
            self.logger.error(f"❌ Error obteniendo datos de aprendizaje: {e}")
            return []

    def store_rag_memory(
        self,
        content: str,
        embedding: np.ndarray,
        source: str = "unknown",
        domain: str = "general",
        relevance_score: float = 1.0,
        metadata: Dict[str, Any] = None,
    ) -> str:
        """Almacenar en memoria RAG"""
        try:
            memory_id = f"rag_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{hashlib.md5(content.encode()).hexdigest()[:8]}"

            # Guardar embedding
            embedding_path = self.data_dir / "rag_embeddings" / f"{memory_id}.npy"
            embedding_path.parent.mkdir(exist_ok=True)
            np.save(embedding_path, embedding)

            session = self.Session()
            try:
                rag_memory = RAGMemory(
                    id=memory_id,
                    content=content,
                    embedding_path=str(embedding_path),
                    source=source,
                    domain=domain,
                    relevance_score=relevance_score,
                    metadata=metadata or {},
                )
                session.add(rag_memory)
                session.commit()

                self.logger.info(f"💾 Memoria RAG almacenada: {memory_id}")
                return memory_id
            except Exception as e:
                session.rollback()
                raise
            finally:
                session.close()

        except Exception as e:
            self.logger.error(f"❌ Error almacenando memoria RAG: {e}")
            raise

    def search_rag_memory(
        self, query_embedding: np.ndarray, limit: int = 10
    ) -> List[Dict[str, Any]]:
        """Buscar en memoria RAG"""
        try:
            session = self.Session()
            try:
                # Obtener todos los embeddings de memoria RAG
                query = (
                    session.query(RAGMemory)
                    .order_by(
                        RAGMemory.relevance_score.desc(), RAGMemory.last_accessed.desc()
                    )
                    .limit(limit)
                )

                results = []
                for row in query.all():
                    embedding_path = Path(row.embedding_path)
                    if embedding_path.exists():
                        embedding = np.load(embedding_path)
                        similarity = np.dot(
                            query_embedding.flatten(), embedding.flatten()
                        )
                        results.append(
                            {
                                "id": row.id,
                                "content": row.content,
                                "similarity": float(similarity),
                                "relevance_score": row.relevance_score,
                                "metadata": row.metadata or {},
                            }
                        )

                # Ordenar por similitud y relevancia
                results.sort(
                    key=lambda x: x["similarity"] * x["relevance_score"], reverse=True
                )

                return results[:limit]
            finally:
                session.close()

        except Exception as e:
            self.logger.error(f"❌ Error buscando en memoria RAG: {e}")
            return []

    def get_data_stats(self) -> Dict[str, Any]:
        """Obtener estadísticas de datos"""
        try:
            session = self.Session()
            try:
                # Estadísticas de interacciones
                user_interactions = session.query(UserInteraction).count()

                # Estadísticas de datos de aprendizaje
                learning_data = session.query(LearningData).count()

                # Estadísticas de memoria RAG
                rag_memory = session.query(RAGMemory).count()

                return {
                    "user_interactions": user_interactions,
                    "learning_data_records": learning_data,
                    "rag_memory_records": rag_memory,
                    "faiss_index_size": (
                        self.faiss_index.ntotal if self.faiss_index else 0
                    ),
                }
            finally:
                session.close()

        except Exception as e:
            self.logger.error(f"❌ Error obteniendo estadísticas: {e}")
            return {}

    def cleanup_old_data(self, days: int = 90):
        """Limpiar datos antiguos"""
        cutoff_date = datetime.now() - timedelta(days=days)

        with self._lock:
            try:
                session = self.Session()
                try:
                    # Limpiar interacciones antiguas
                    deleted_interactions = (
                        session.query(UserInteraction)
                        .filter(UserInteraction.timestamp < cutoff_date)
                        .delete(synchronize_session=False)
                    )

                    # Limpiar datos de aprendizaje antiguos
                    deleted_learning_data = (
                        session.query(LearningData)
                        .filter(LearningData.created_at < cutoff_date)
                        .delete(synchronize_session=False)
                    )

                    session.commit()

                    self.logger.info(
                        f"🧹 Datos antiguos eliminados: {deleted_interactions} interacciones, {deleted_learning_data} registros de aprendizaje"
                    )

                except Exception as e:
                    session.rollback()
                    raise
                finally:
                    session.close()

            except Exception as e:
                self.logger.error(f"❌ Error limpiando datos antiguos: {e}")

    def _load_faiss_index(self):
        """Cargar índice FAISS existente"""
        index_path = self.data_dir / "faiss_index.index"
        if index_path.exists():
            try:
                self.faiss_index = faiss.read_index(str(index_path))
                self.logger.info(
                    f"✅ Índice FAISS cargado: {self.faiss_index.ntotal} vectores"
                )
            except Exception as e:
                self.logger.error(f"❌ Error cargando índice FAISS: {e}")
                self.faiss_index = None
        else:
            self.logger.info("📝 No se encontró índice FAISS existente")

    def save_faiss_index(self):
        """Guardar índice FAISS"""
        if self.faiss_index is not None:
            try:
                index_path = self.data_dir / "faiss_index.index"
                faiss.write_index(self.faiss_index, str(index_path))
                self.logger.info(
                    f"💾 Índice FAISS guardado: {self.faiss_index.ntotal} vectores"
                )
            except Exception as e:
                self.logger.error(f"❌ Error guardando índice FAISS: {e}")


# Instancia global del gestor de datos
data_manager = DataManager()
