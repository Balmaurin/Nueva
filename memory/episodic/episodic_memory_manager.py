#!/usr/bin/env python3
"""
Gestor de Memoria Episódica para Sheily AI
Sistema para almacenar y recuperar eventos y experiencias detalladas
"""

import json
import os
import time
import sqlite3
from pathlib import Path
from typing import List, Dict, Optional, Any
from dataclasses import dataclass, asdict
import logging
import threading
import hashlib


@dataclass
class EpisodicMemoryConfig:
    """Configuración de la memoria episódica"""

    max_episodes: int = 5000
    database_path: str = "episodic/memory.db"
    memory_dir: str = "episodic/memory"
    backup_enabled: bool = True
    cleanup_interval: int = 86400  # 24 horas


class EpisodicMemoryManager:
    """Gestor principal de memoria episódica"""

    def __init__(self, config: Optional[EpisodicMemoryConfig] = None):
        self.config = config or EpisodicMemoryConfig()
        self.logger = logging.getLogger(__name__)

        # Crear directorios necesarios
        self._create_directories()

        # Base de datos
        self.db_path = Path(self.config.database_path)
        self._init_database()

        # Threading
        self.lock = threading.RLock()

        # Iniciar limpieza automática
        self._start_cleanup_thread()

    def _create_directories(self):
        """Crear directorios necesarios"""
        directories = [self.config.memory_dir, Path(self.config.database_path).parent]

        for directory in directories:
            Path(directory).mkdir(parents=True, exist_ok=True)

    def _init_database(self):
        """Inicializar base de datos SQLite"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute(
                """
                CREATE TABLE IF NOT EXISTS episodic_memory (
                    id TEXT PRIMARY KEY,
                    context TEXT,
                    event_type TEXT,
                    details TEXT,
                    timestamp REAL,
                    tags TEXT,
                    importance REAL,
                    related_episodes TEXT
                )
            """
            )
            conn.commit()

    def record_episode(
        self,
        context: str,
        event_type: str,
        details: Dict[str, Any],
        tags: List[str] = None,
        importance: float = 1.0,
        related_episodes: List[str] = None,
    ) -> str:
        """Registrar un nuevo episodio"""
        with self.lock:
            # Generar ID único
            episode_id = f"ep_{int(time.time())}_{hashlib.md5(json.dumps(details).encode()).hexdigest()[:8]}"

            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute(
                    """
                    INSERT INTO episodic_memory 
                    (id, context, event_type, details, timestamp, tags, importance, related_episodes)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """,
                    (
                        episode_id,
                        context,
                        event_type,
                        json.dumps(details),
                        time.time(),
                        json.dumps(tags or []),
                        importance,
                        json.dumps(related_episodes or []),
                    ),
                )
                conn.commit()

            self.logger.debug(f"Episodio registrado: {episode_id}")
            return episode_id

    def get_episodes(
        self,
        context: str = None,
        event_type: str = None,
        tags: List[str] = None,
        min_importance: float = 0.0,
        limit: int = 100,
    ) -> List[Dict[str, Any]]:
        """Recuperar episodios con filtros"""
        with self.lock:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()

                # Construir consulta dinámica
                query = "SELECT * FROM episodic_memory WHERE 1=1"
                params = []

                if context:
                    query += " AND context LIKE ?"
                    params.append(f"%{context}%")

                if event_type:
                    query += " AND event_type = ?"
                    params.append(event_type)

                if tags:
                    query += " AND (" + " OR ".join(["tags LIKE ?"] * len(tags)) + ")"
                    params.extend([f"%{tag}%" for tag in tags])

                query += " AND importance >= ?"
                params.append(min_importance)

                query += " ORDER BY timestamp DESC LIMIT ?"
                params.append(limit)

                cursor.execute(query, params)

                episodes = []
                for row in cursor.fetchall():
                    episode = {
                        "id": row[0],
                        "context": row[1],
                        "event_type": row[2],
                        "details": json.loads(row[3]),
                        "timestamp": row[4],
                        "tags": json.loads(row[5]),
                        "importance": row[6],
                        "related_episodes": json.loads(row[7]),
                    }
                    episodes.append(episode)

                return episodes

    def _start_cleanup_thread(self):
        """Iniciar hilo de limpieza periódica"""

        def cleanup():
            while True:
                time.sleep(self.config.cleanup_interval)
                self._cleanup_old_episodes()

        cleanup_thread = threading.Thread(target=cleanup, daemon=True)
        cleanup_thread.start()

    def _cleanup_old_episodes(self):
        """Limpiar episodios antiguos o de baja importancia"""
        with self.lock:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                # Eliminar episodios antiguos de baja importancia
                cursor.execute(
                    """
                    DELETE FROM episodic_memory 
                    WHERE timestamp < ? AND importance < 0.5
                """,
                    (time.time() - 90 * 24 * 3600,),
                )  # 90 días
                conn.commit()

            self.logger.info("Limpieza de memoria episódica completada")


def create_episodic_memory_manager(
    config: EpisodicMemoryConfig = None,
) -> EpisodicMemoryManager:
    """Crear una instancia del gestor de memoria episódica"""
    return EpisodicMemoryManager(config)
