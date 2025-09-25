#!/usr/bin/env python3
"""
Gestor de Memoria a Largo Plazo para Sheily AI
Sistema para almacenar y gestionar conocimientos persistentes
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


@dataclass
class LongTermMemoryConfig:
    """Configuración de la memoria a largo plazo"""

    max_entries: int = 10000
    database_path: str = "long_term/memory.db"
    memory_dir: str = "long_term/memory"
    backup_enabled: bool = True
    cleanup_interval: int = 86400  # 24 horas


class LongTermMemoryManager:
    """Gestor principal de memoria a largo plazo"""

    def __init__(self, config: Optional[LongTermMemoryConfig] = None):
        self.config = config or LongTermMemoryConfig()
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
                CREATE TABLE IF NOT EXISTS long_term_memory (
                    id TEXT PRIMARY KEY,
                    category TEXT,
                    content TEXT,
                    metadata TEXT,
                    created_at REAL,
                    last_accessed REAL,
                    access_count INTEGER
                )
            """
            )
            conn.commit()

    def add_memory(
        self, category: str, content: str, metadata: Dict[str, Any] = None
    ) -> str:
        """Añadir una entrada a la memoria a largo plazo"""
        with self.lock:
            memory_id = f"ltm_{int(time.time())}_{hash(content)}"

            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute(
                    """
                    INSERT INTO long_term_memory 
                    (id, category, content, metadata, created_at, last_accessed, access_count)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                """,
                    (
                        memory_id,
                        category,
                        content,
                        json.dumps(metadata or {}),
                        time.time(),
                        time.time(),
                        1,
                    ),
                )
                conn.commit()

            self.logger.debug(f"Memoria a largo plazo añadida: {memory_id}")
            return memory_id

    def get_memories(
        self, category: str = None, limit: int = 100
    ) -> List[Dict[str, Any]]:
        """Recuperar entradas de memoria a largo plazo"""
        with self.lock:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                if category:
                    cursor.execute(
                        """
                        SELECT id, category, content, metadata, created_at, last_accessed, access_count 
                        FROM long_term_memory 
                        WHERE category = ? 
                        ORDER BY last_accessed DESC 
                        LIMIT ?
                    """,
                        (category, limit),
                    )
                else:
                    cursor.execute(
                        """
                        SELECT id, category, content, metadata, created_at, last_accessed, access_count 
                        FROM long_term_memory 
                        ORDER BY last_accessed DESC 
                        LIMIT ?
                    """,
                        (limit,),
                    )

                memories = []
                for row in cursor.fetchall():
                    memory = {
                        "id": row[0],
                        "category": row[1],
                        "content": row[2],
                        "metadata": json.loads(row[3]),
                        "created_at": row[4],
                        "last_accessed": row[5],
                        "access_count": row[6],
                    }
                    memories.append(memory)

                return memories

    def _start_cleanup_thread(self):
        """Iniciar hilo de limpieza periódica"""

        def cleanup():
            while True:
                time.sleep(self.config.cleanup_interval)
                self._cleanup_old_memories()

        cleanup_thread = threading.Thread(target=cleanup, daemon=True)
        cleanup_thread.start()

    def _cleanup_old_memories(self):
        """Limpiar entradas antiguas de memoria"""
        with self.lock:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                # Eliminar entradas con poco uso
                cursor.execute(
                    """
                    DELETE FROM long_term_memory 
                    WHERE access_count < 2 AND last_accessed < ?
                """,
                    (time.time() - 30 * 24 * 3600,),
                )  # 30 días
                conn.commit()

            self.logger.info("Limpieza de memoria a largo plazo completada")


def create_long_term_memory_manager(
    config: LongTermMemoryConfig = None,
) -> LongTermMemoryManager:
    """Crear una instancia del gestor de memoria a largo plazo"""
    return LongTermMemoryManager(config)
