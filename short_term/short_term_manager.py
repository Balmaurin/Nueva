#!/usr/bin/env python3
"""
Gestor de Memoria a Corto Plazo para Shaili AI
Sistema avanzado para manejo de contexto conversacional y memoria temporal
"""

import json
import os
import time
import hashlib
import sqlite3
from pathlib import Path
from typing import List, Dict, Optional, Any, Tuple
from dataclasses import dataclass, asdict
from datetime import datetime, timedelta
import logging
import threading
from collections import deque
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import pickle
import gzip
import traceback

# Configurar logging con más detalles
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    filename="logs/short_term_memory.log",
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
                "alert_type": "short_term_memory_error",
                "severity": "warning",
                "message": message,
            }
        )
    except Exception as notification_error:
        logger.error(f"Error enviando notificación de error: {notification_error}")


@dataclass
class MemoryConfig:
    """Configuración de la memoria a corto plazo"""

    max_messages: int = 50
    max_tokens: int = 4096
    max_sessions: int = 100
    summary_threshold: int = 8000
    similarity_threshold: float = 0.7
    cleanup_interval: int = 3600  # segundos
    compression_enabled: bool = True
    backup_enabled: bool = True
    auto_summarize: bool = True
    semantic_clustering: bool = True
    memory_dir: str = "short_term/memory"
    database_path: str = "short_term/memory.db"
    cache_dir: str = "short_term/cache"


@dataclass
class MemoryMessage:
    """Estructura de un mensaje en memoria"""

    id: str
    role: str
    content: str
    tokens: int
    timestamp: float
    session_id: str
    embedding: Optional[List[float]] = None
    metadata: Dict[str, Any] = None
    importance_score: float = 1.0
    access_count: int = 0
    last_accessed: float = None


@dataclass
class MemorySession:
    """Estructura de una sesión de memoria"""

    session_id: str
    user_id: str
    created_at: float
    last_accessed: float
    message_count: int
    total_tokens: int
    summary: Optional[str] = None
    metadata: Dict[str, Any] = None


class SemanticAnalyzer:
    """Analizador semántico para memoria"""

    def __init__(self, config: MemoryConfig):
        self.config = config
        self.vectorizer = TfidfVectorizer(
            max_features=1000, stop_words="english", ngram_range=(1, 2)
        )
        self.embeddings_cache = {}
        self.cache_file = Path(config.cache_dir) / "embeddings_cache.pkl"
        self._load_cache()

    def _load_cache(self):
        """Cargar caché de embeddings"""
        try:
            if self.cache_file.exists():
                with open(self.cache_file, "rb") as f:
                    self.embeddings_cache = pickle.load(f)
        except Exception as e:
            logging.warning(f"No se pudo cargar caché de embeddings: {e}")
            self.embeddings_cache = {}

    def _save_cache(self):
        """Guardar caché de embeddings"""
        try:
            self.cache_file.parent.mkdir(parents=True, exist_ok=True)
            with open(self.cache_file, "wb") as f:
                pickle.dump(self.embeddings_cache, f)
        except Exception as e:
            logging.warning(f"No se pudo guardar caché de embeddings: {e}")

    def get_embedding(self, text: str) -> List[float]:
        """Obtener embedding de un texto"""
        # Generar hash del texto para caché
        text_hash = hashlib.md5(text.encode()).hexdigest()

        if text_hash in self.embeddings_cache:
            return self.embeddings_cache[text_hash]

        # Calcular embedding usando TF-IDF
        try:
            # Usar el vectorizador para obtener características
            features = self.vectorizer.fit_transform([text])
            embedding = features.toarray()[0].tolist()

            # Normalizar embedding
            norm = np.linalg.norm(embedding)
            if norm > 0:
                embedding = (embedding / norm).tolist()

            # Guardar en caché
            self.embeddings_cache[text_hash] = embedding

            return embedding
        except Exception as e:
            logging.error(f"Error calculando embedding: {e}")
            # Embedding por defecto
            return [0.0] * 100

    def calculate_similarity(self, text1: str, text2: str) -> float:
        """Calcular similitud semántica entre dos textos"""
        try:
            embedding1 = self.get_embedding(text1)
            embedding2 = self.get_embedding(text2)

            # Calcular similitud coseno
            similarity = cosine_similarity([embedding1], [embedding2])[0][0]

            return float(similarity)
        except Exception as e:
            logging.error(f"Error calculando similitud: {e}")
            return 0.0

    def find_similar_messages(
        self, query: str, messages: List[MemoryMessage], threshold: float = None
    ) -> List[Tuple[MemoryMessage, float]]:
        """Encontrar mensajes similares a una consulta"""
        threshold = threshold or self.config.similarity_threshold
        similar_messages = []

        for message in messages:
            similarity = self.calculate_similarity(query, message.content)
            if similarity >= threshold:
                similar_messages.append((message, similarity))

        # Ordenar por similitud
        similar_messages.sort(key=lambda x: x[1], reverse=True)
        return similar_messages


class MemorySummarizer:
    """Generador de resúmenes para memoria"""

    def __init__(self, config: MemoryConfig):
        self.config = config

    def generate_summary(self, messages: List[MemoryMessage]) -> str:
        """Generar resumen de una lista de mensajes"""
        if not messages:
            return ""

        # Extraer contenido de mensajes importantes
        important_messages = [msg for msg in messages if msg.importance_score > 0.5]

        if not important_messages:
            important_messages = messages[:5]  # Tomar los primeros 5

        # Crear resumen basado en contenido
        summary_parts = []

        # Agrupar por rol
        user_messages = [msg for msg in important_messages if msg.role == "user"]
        assistant_messages = [
            msg for msg in important_messages if msg.role == "assistant"
        ]

        if user_messages:
            user_summary = self._summarize_by_role(user_messages, "Usuario")
            summary_parts.append(user_summary)

        if assistant_messages:
            assistant_summary = self._summarize_by_role(assistant_messages, "Asistente")
            summary_parts.append(assistant_summary)

        return " | ".join(summary_parts)

    def _summarize_by_role(self, messages: List[MemoryMessage], role: str) -> str:
        """Resumir mensajes por rol"""
        if not messages:
            return ""

        # Extraer temas principales
        topics = self._extract_topics([msg.content for msg in messages])

        # Crear resumen
        summary = f"{role}: {len(messages)} mensajes"
        if topics:
            summary += f" sobre {', '.join(topics[:3])}"

        return summary

    def _extract_topics(self, texts: List[str]) -> List[str]:
        """Extraer temas principales de una lista de textos"""
        try:
            # Usar TF-IDF para extraer palabras clave
            vectorizer = TfidfVectorizer(
                max_features=20, stop_words="english", ngram_range=(1, 2)
            )

            if len(texts) < 2:
                # Si hay pocos textos, usar palabras simples
                all_text = " ".join(texts)
                words = [word for word in all_text.split() if len(word) > 3]
                return list(set(words))[:5]

            tfidf_matrix = vectorizer.fit_transform(texts)
            feature_names = vectorizer.get_feature_names_out()

            # Obtener palabras con mayor TF-IDF
            tfidf_scores = tfidf_matrix.sum(axis=0).A1
            top_indices = tfidf_scores.argsort()[-10:][::-1]

            topics = [feature_names[i] for i in top_indices]
            return topics[:5]

        except Exception as e:
            logging.error(f"Error extrayendo temas: {e}")
            return []


class ShortTermMemoryManager:
    """Gestor principal de memoria a corto plazo"""

    def __init__(self, config: Optional[MemoryConfig] = None):
        self.config = config or MemoryConfig()
        self.logger = logging.getLogger(__name__)

        # Crear directorios necesarios
        self._create_directories()

        # Inicializar componentes
        self.semantic_analyzer = SemanticAnalyzer(self.config)
        self.summarizer = MemorySummarizer(self.config)

        # Estado de la memoria
        self.sessions: Dict[str, MemorySession] = {}
        self.messages: Dict[str, List[MemoryMessage]] = {}
        self.active_session_id: Optional[str] = None

        # Base de datos
        self.db_path = Path(self.config.database_path)
        self._init_database()

        # Threading
        self.lock = threading.RLock()

        # Cargar sesiones existentes
        self._load_sessions()

        # Iniciar limpieza automática
        self._start_cleanup_thread()

    def _create_directories(self):
        """Crear directorios necesarios"""
        try:
            directories = [
                self.config.memory_dir,
                self.config.cache_dir,
                Path(self.config.database_path).parent,
            ]

            for directory in directories:
                Path(directory).mkdir(parents=True, exist_ok=True)
        except Exception as e:
            log_error("❌ Error creando directorios de memoria a corto plazo", e)

    def _init_database(self):
        """Inicializar base de datos"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()

                # Tabla de sesiones
                cursor.execute(
                    """
                    CREATE TABLE IF NOT EXISTS sessions (
                        session_id TEXT PRIMARY KEY,
                        user_id TEXT NOT NULL,
                        created_at REAL NOT NULL,
                        last_accessed REAL NOT NULL,
                        message_count INTEGER DEFAULT 0,
                        total_tokens INTEGER DEFAULT 0,
                        summary TEXT,
                        metadata TEXT
                    )
                """
                )

                # Tabla de mensajes
                cursor.execute(
                    """
                    CREATE TABLE IF NOT EXISTS messages (
                        id TEXT PRIMARY KEY,
                        session_id TEXT NOT NULL,
                        role TEXT NOT NULL,
                        content TEXT NOT NULL,
                        tokens INTEGER NOT NULL,
                        timestamp REAL NOT NULL,
                        embedding TEXT,
                        metadata TEXT,
                        importance_score REAL DEFAULT 1.0,
                        access_count INTEGER DEFAULT 0,
                        last_accessed REAL,
                        FOREIGN KEY (session_id) REFERENCES sessions (session_id)
                    )
                """
                )

                # Índices
                cursor.execute(
                    """
                    CREATE INDEX IF NOT EXISTS idx_messages_session 
                    ON messages (session_id)
                """
                )
                cursor.execute(
                    """
                    CREATE INDEX IF NOT EXISTS idx_messages_timestamp 
                    ON messages (timestamp)
                """
                )

                conn.commit()

        except Exception as e:
            log_error(
                "❌ Error inicializando base de datos de memoria a corto plazo", e
            )

    def create_session(self, user_id: str, session_id: str = None) -> str:
        """Crear nueva sesión de memoria"""
        try:
            with self.lock:
                if session_id is None:
                    session_id = f"session_{int(time.time())}_{hashlib.md5(user_id.encode()).hexdigest()[:8]}"

                if session_id in self.sessions:
                    return session_id

                # Crear sesión
                session = MemorySession(
                    session_id=session_id,
                    user_id=user_id,
                    created_at=time.time(),
                    last_accessed=time.time(),
                    message_count=0,
                    total_tokens=0,
                )

                self.sessions[session_id] = session
                self.messages[session_id] = []

                # Guardar en base de datos
                self._save_session_to_db(session)

                self.logger.info(f"Sesión creada: {session_id} para usuario {user_id}")
                return session_id
        except Exception as e:
            log_error(f"❌ Error creando sesión para usuario {user_id}", e)
            return None

    def add_message(
        self,
        session_id: str,
        role: str,
        content: str,
        tokens: int = None,
        metadata: Dict = None,
    ) -> str:
        """Añadir mensaje a una sesión"""
        try:
            with self.lock:
                if session_id not in self.sessions:
                    raise ValueError(f"Sesión {session_id} no existe")

                # Calcular tokens si no se proporcionan
                if tokens is None:
                    tokens = len(content.split())  # Aproximación simple

                # Generar ID único
                message_id = f"msg_{int(time.time())}_{hashlib.md5(content.encode()).hexdigest()[:8]}"

                # Obtener embedding
                embedding = self.semantic_analyzer.get_embedding(content)

                # Crear mensaje
                message = MemoryMessage(
                    id=message_id,
                    role=role,
                    content=content,
                    tokens=tokens,
                    timestamp=time.time(),
                    session_id=session_id,
                    embedding=embedding,
                    metadata=metadata or {},
                    importance_score=self._calculate_importance(content, role),
                    access_count=0,
                    last_accessed=time.time(),
                )

                # Añadir a la sesión
                self.messages[session_id].append(message)

                # Actualizar sesión
                session = self.sessions[session_id]
                session.message_count += 1
                session.total_tokens += tokens
                session.last_accessed = time.time()

                # Gestionar límites
                self._manage_session_limits(session_id)

                # Guardar en base de datos
                self._save_message_to_db(message)
                self._update_session_in_db(session)

                self.logger.debug(
                    f"Mensaje añadido: {message_id} a sesión {session_id}"
                )
                return message_id
        except Exception as e:
            log_error(f"❌ Error agregando mensaje a sesión {session_id}", e)
            return None

    def _calculate_importance(self, content: str, role: str) -> float:
        """Calcular importancia de un mensaje"""
        importance = 1.0

        # Ajustar por rol
        if role == "system":
            importance *= 1.5
        elif role == "user":
            importance *= 1.2

        # Ajustar por longitud
        if len(content) > 100:
            importance *= 1.1

        # Ajustar por palabras clave
        keywords = ["importante", "crítico", "urgente", "error", "problema"]
        if any(keyword in content.lower() for keyword in keywords):
            importance *= 1.3

        return min(importance, 2.0)  # Máximo 2.0

    def _manage_session_limits(self, session_id: str):
        """Gestionar límites de la sesión"""
        try:
            session = self.sessions[session_id]
            messages = self.messages[session_id]

            # Verificar límite de mensajes
            if len(messages) > self.config.max_messages:
                # Eliminar mensajes menos importantes
                messages.sort(key=lambda x: x.importance_score)
                messages_to_remove = messages[
                    : len(messages) - self.config.max_messages
                ]

                for msg in messages_to_remove:
                    messages.remove(msg)
                    session.total_tokens -= msg.tokens
                    session.message_count -= 1
                    self._delete_message_from_db(msg.id)

            # Verificar límite de tokens
            while session.total_tokens > self.config.max_tokens and messages:
                # Eliminar mensaje más antiguo
                oldest_message = min(messages, key=lambda x: x.timestamp)
                messages.remove(oldest_message)
                session.total_tokens -= oldest_message.tokens
                session.message_count -= 1
                self._delete_message_from_db(oldest_message.id)

            # Generar resumen si es necesario
            if (
                self.config.auto_summarize
                and session.total_tokens > self.config.summary_threshold
            ):
                self._generate_session_summary(session_id)
        except Exception as e:
            log_error(f"❌ Error manejando límites de sesión {session_id}", e)

    def _generate_session_summary(self, session_id: str):
        """Generar resumen de la sesión"""
        try:
            messages = self.messages[session_id]
            session = self.sessions[session_id]

            summary = self.summarizer.generate_summary(messages)
            session.summary = summary

            self._update_session_in_db(session)
            self.logger.info(f"Resumen generado para sesión {session_id}")

        except Exception as e:
            log_error(f"❌ Error generando resumen de sesión {session_id}", e)

    def get_context(
        self,
        session_id: str,
        max_tokens: int = None,
        include_system: bool = True,
        semantic_search: str = None,
    ) -> List[Dict]:
        """Obtener contexto de una sesión"""
        try:
            with self.lock:
                if session_id not in self.sessions:
                    return []

                messages = self.messages[session_id]
                max_tokens = max_tokens or self.config.max_tokens

                # Filtrar mensajes
                filtered_messages = []
                for msg in messages:
                    if not include_system and msg.role == "system":
                        continue
                    filtered_messages.append(msg)

                # Búsqueda semántica si se especifica
                if semantic_search:
                    similar_messages = self.semantic_analyzer.find_similar_messages(
                        semantic_search, filtered_messages
                    )
                    # Ordenar por similitud y luego por timestamp
                    filtered_messages = [msg for msg, _ in similar_messages]

                # Ordenar por timestamp
                filtered_messages.sort(key=lambda x: x.timestamp)

                # Aplicar límite de tokens
                context = []
                current_tokens = 0

                for msg in filtered_messages:
                    if current_tokens + msg.tokens > max_tokens:
                        break

                    # Actualizar contador de acceso
                    msg.access_count += 1
                    msg.last_accessed = time.time()
                    self._update_message_in_db(msg)

                    context.append(
                        {
                            "role": msg.role,
                            "content": msg.content,
                            "timestamp": msg.timestamp,
                            "importance": msg.importance_score,
                        }
                    )
                    current_tokens += msg.tokens

                return context
        except Exception as e:
            log_error(f"❌ Error obteniendo contexto de sesión {session_id}", e)
            return []

    def search_messages(
        self, session_id: str, query: str, limit: int = 10
    ) -> List[Tuple[MemoryMessage, float]]:
        """Buscar mensajes por similitud semántica"""
        try:
            with self.lock:
                if session_id not in self.messages:
                    return []

                messages = self.messages[session_id]
                similar_messages = self.semantic_analyzer.find_similar_messages(
                    query, messages, threshold=0.3
                )

                return similar_messages[:limit]
        except Exception as e:
            log_error(f"❌ Error buscando mensajes en sesión {session_id}", e)
            return []

    def get_session_info(self, session_id: str) -> Optional[Dict]:
        """Obtener información de una sesión"""
        try:
            with self.lock:
                if session_id not in self.sessions:
                    return None

                session = self.sessions[session_id]
                messages = self.messages[session_id]

                return {
                    "session_id": session.session_id,
                    "user_id": session.user_id,
                    "created_at": session.created_at,
                    "last_accessed": session.last_accessed,
                    "message_count": session.message_count,
                    "total_tokens": session.total_tokens,
                    "summary": session.summary,
                    "metadata": session.metadata,
                    "active_messages": len(messages),
                    "avg_importance": (
                        sum(msg.importance_score for msg in messages) / len(messages)
                        if messages
                        else 0
                    ),
                }
        except Exception as e:
            log_error(f"❌ Error obteniendo información de sesión {session_id}", e)
            return None

    def list_sessions(self, user_id: str = None) -> List[Dict]:
        """Listar sesiones"""
        try:
            with self.lock:
                sessions = []

                for session in self.sessions.values():
                    if user_id and session.user_id != user_id:
                        continue

                    sessions.append(self.get_session_info(session.session_id))

                # Ordenar por último acceso
                sessions.sort(key=lambda x: x["last_accessed"], reverse=True)
                return sessions
        except Exception as e:
            log_error("❌ Error listando sesiones", e)
            return []

    def delete_session(self, session_id: str):
        """Eliminar sesión"""
        try:
            with self.lock:
                if session_id not in self.sessions:
                    return

                # Eliminar mensajes de la base de datos
                messages = self.messages[session_id]
                for msg in messages:
                    self._delete_message_from_db(msg.id)

                # Eliminar sesión de la base de datos
                self._delete_session_from_db(session_id)

                # Eliminar de memoria
                del self.sessions[session_id]
                del self.messages[session_id]

                self.logger.info(f"Sesión eliminada: {session_id}")
        except Exception as e:
            log_error(f"❌ Error eliminando sesión {session_id}", e)

    def clear_session(self, session_id: str):
        """Limpiar mensajes de una sesión"""
        try:
            with self.lock:
                if session_id not in self.sessions:
                    return

                # Eliminar mensajes de la base de datos
                messages = self.messages[session_id]
                for msg in messages:
                    self._delete_message_from_db(msg.id)

                # Limpiar en memoria
                self.messages[session_id] = []

                # Actualizar sesión
                session = self.sessions[session_id]
                session.message_count = 0
                session.total_tokens = 0
                session.last_accessed = time.time()

                self._update_session_in_db(session)

                self.logger.info(f"Sesión limpiada: {session_id}")
        except Exception as e:
            log_error(f"❌ Error limpiando sesión {session_id}", e)

    def backup_memory(self, backup_path: str = None):
        """Crear respaldo de la memoria"""
        try:
            if not self.config.backup_enabled:
                return

            backup_path = (
                backup_path
                or f"short_term/backup/memory_backup_{int(time.time())}.json"
            )

            backup_data = {
                "sessions": {
                    sid: asdict(session) for sid, session in self.sessions.items()
                },
                "messages": {
                    sid: [asdict(msg) for msg in messages]
                    for sid, messages in self.messages.items()
                },
                "timestamp": time.time(),
                "version": "3.1.0",
            }

            Path(backup_path).parent.mkdir(parents=True, exist_ok=True)

            if self.config.compression_enabled:
                with gzip.open(f"{backup_path}.gz", "wt", encoding="utf-8") as f:
                    json.dump(backup_data, f, ensure_ascii=False, indent=2)
            else:
                with open(backup_path, "w", encoding="utf-8") as f:
                    json.dump(backup_data, f, ensure_ascii=False, indent=2)

            self.logger.info(f"Respaldo creado: {backup_path}")

        except Exception as e:
            log_error("❌ Error realizando backup de memoria", e)

    def _save_session_to_db(self, session: MemorySession):
        """Guardar sesión en base de datos"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute(
                    """
                    INSERT OR REPLACE INTO sessions 
                    (session_id, user_id, created_at, last_accessed, message_count, 
                     total_tokens, summary, metadata)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """,
                    (
                        session.session_id,
                        session.user_id,
                        session.created_at,
                        session.last_accessed,
                        session.message_count,
                        session.total_tokens,
                        session.summary,
                        json.dumps(session.metadata) if session.metadata else None,
                    ),
                )
                conn.commit()
        except Exception as e:
            log_error("❌ Error guardando sesión en DB", e)

    def _save_message_to_db(self, message: MemoryMessage):
        """Guardar mensaje en base de datos"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute(
                    """
                    INSERT OR REPLACE INTO messages 
                    (id, session_id, role, content, tokens, timestamp, embedding,
                     metadata, importance_score, access_count, last_accessed)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                    (
                        message.id,
                        message.session_id,
                        message.role,
                        message.content,
                        message.tokens,
                        message.timestamp,
                        json.dumps(message.embedding) if message.embedding else None,
                        json.dumps(message.metadata) if message.metadata else None,
                        message.importance_score,
                        message.access_count,
                        message.last_accessed,
                    ),
                )
                conn.commit()
        except Exception as e:
            log_error("❌ Error guardando mensaje en DB", e)

    def _update_session_in_db(self, session: MemorySession):
        """Actualizar sesión en base de datos"""
        self._save_session_to_db(session)

    def _update_message_in_db(self, message: MemoryMessage):
        """Actualizar mensaje en base de datos"""
        self._save_message_to_db(message)

    def _delete_session_from_db(self, session_id: str):
        """Eliminar sesión de la base de datos"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute(
                    "DELETE FROM sessions WHERE session_id = ?", (session_id,)
                )
                cursor.execute(
                    "DELETE FROM messages WHERE session_id = ?", (session_id,)
                )
                conn.commit()
        except Exception as e:
            log_error("❌ Error eliminando sesión de DB", e)

    def _delete_message_from_db(self, message_id: str):
        """Eliminar mensaje de la base de datos"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute("DELETE FROM messages WHERE id = ?", (message_id,))
                conn.commit()
        except Exception as e:
            log_error("❌ Error eliminando mensaje de DB", e)

    def _load_sessions(self):
        """Cargar sesiones desde la base de datos"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()

                # Cargar sesiones
                cursor.execute("SELECT * FROM sessions")
                for row in cursor.fetchall():
                    session = MemorySession(
                        session_id=row[0],
                        user_id=row[1],
                        created_at=row[2],
                        last_accessed=row[3],
                        message_count=row[4],
                        total_tokens=row[5],
                        summary=row[6],
                        metadata=json.loads(row[7]) if row[7] else {},
                    )
                    self.sessions[session.session_id] = session
                    self.messages[session.session_id] = []

                # Cargar mensajes
                cursor.execute("SELECT * FROM messages ORDER BY timestamp")
                for row in cursor.fetchall():
                    message = MemoryMessage(
                        id=row[0],
                        session_id=row[1],
                        role=row[2],
                        content=row[3],
                        tokens=row[4],
                        timestamp=row[5],
                        embedding=json.loads(row[6]) if row[6] else None,
                        metadata=json.loads(row[7]) if row[7] else {},
                        importance_score=row[8],
                        access_count=row[9],
                        last_accessed=row[10],
                    )

                    if message.session_id in self.messages:
                        self.messages[message.session_id].append(message)

        except Exception as e:
            log_error("❌ Error cargando sesiones", e)

    def _start_cleanup_thread(self):
        """Iniciar thread de limpieza automática"""

        def cleanup_worker():
            while True:
                try:
                    time.sleep(self.config.cleanup_interval)
                    self._cleanup_old_sessions()
                    self.semantic_analyzer._save_cache()
                except Exception as e:
                    log_error("❌ Error en hilo de limpieza de memoria", e)
                    time.sleep(self.config.cleanup_interval)

        cleanup_thread = threading.Thread(target=cleanup_worker, daemon=True)
        cleanup_thread.start()

    def _cleanup_old_sessions(self):
        """Limpiar sesiones antiguas"""
        try:
            current_time = time.time()
            sessions_to_delete = []

            for session_id, session in self.sessions.items():
                # Eliminar sesiones con más de 24 horas sin acceso
                if current_time - session.last_accessed > 86400:  # 24 horas
                    sessions_to_delete.append(session_id)

            for session_id in sessions_to_delete:
                self.delete_session(session_id)

            if sessions_to_delete:
                self.logger.info(
                    f"Limpieza automática: {len(sessions_to_delete)} sesiones eliminadas"
                )
        except Exception as e:
            log_error("❌ Error limpiando sesiones antiguas", e)


def main():
    """Función principal de ejemplo"""
    # Configurar logging con más detalles
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        filename="logs/short_term_memory.log",
        filemode="a",
    )
    logger = logging.getLogger(__name__)

    # Crear gestor de memoria
    config = MemoryConfig(max_messages=20, max_tokens=2048, summary_threshold=4000)

    manager = ShortTermMemoryManager(config)

    try:
        # Iniciar sistema de memoria a corto plazo
        manager._start_cleanup_thread()
        print("🚀 Sistema de memoria a corto plazo iniciado")
    except Exception as e:
        log_error("❌ Error iniciando sistema de memoria a corto plazo", e)

    # Crear sesión
    session_id = manager.create_session("usuario_ejemplo")

    # Añadir mensajes
    manager.add_message(session_id, "user", "Hola, ¿qué es la inteligencia artificial?")
    manager.add_message(
        session_id,
        "assistant",
        "La inteligencia artificial es un campo de la informática que busca crear sistemas capaces de realizar tareas que normalmente requieren inteligencia humana.",
    )
    manager.add_message(session_id, "user", "¿Cuáles son los tipos principales de IA?")
    manager.add_message(
        session_id,
        "assistant",
        "Los tipos principales incluyen: 1) IA débil (especializada), 2) IA fuerte (general), 3) Machine Learning, 4) Deep Learning.",
    )

    # Obtener contexto
    context = manager.get_context(session_id)
    print("Contexto actual:")
    for msg in context:
        print(f"  {msg['role']}: {msg['content']}")

    # Buscar mensajes similares
    similar = manager.search_messages(session_id, "machine learning")
    print(f"\nMensajes similares a 'machine learning': {len(similar)} encontrados")

    # Información de la sesión
    info = manager.get_session_info(session_id)
    print(f"\nInformación de sesión: {info}")


if __name__ == "__main__":
    main()
