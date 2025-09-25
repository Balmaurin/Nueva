#!/usr/bin/env python3
"""
Gestor de Exportación e Importación de Memoria para Sheily AI

Este módulo permite exportar e importar datos de memoria entre diferentes
instancias o versiones del sistema.
"""

import os
import json
import sqlite3
import logging
from typing import Dict, List, Any, Optional
from datetime import datetime
from pathlib import Path

from .short_term import ShortTermMemoryManager, MemoryConfig as ShortTermConfig
from .long_term import LongTermMemoryManager, LongTermMemoryConfig
from .episodic import EpisodicMemoryManager, EpisodicMemoryConfig
from .semantic import SemanticMemoryManager, SemanticMemoryConfig


class MemoryExportImportManager:
    """
    Gestor centralizado para exportación e importación de memoria
    """

    def __init__(self, export_dir: str = "memory_exports"):
        """
        Inicializar gestor de exportación/importación

        :param export_dir: Directorio para almacenar exportaciones
        """
        self.export_dir = Path(export_dir)
        self.export_dir.mkdir(parents=True, exist_ok=True)
        self.logger = logging.getLogger(__name__)

    def export_memory(
        self,
        short_term_memory: ShortTermMemoryManager = None,
        long_term_memory: LongTermMemoryManager = None,
        episodic_memory: EpisodicMemoryManager = None,
        semantic_memory: SemanticMemoryManager = None,
        export_name: Optional[str] = None,
    ) -> str:
        """
        Exportar todos los tipos de memoria a un archivo JSON

        :param short_term_memory: Gestor de memoria a corto plazo
        :param long_term_memory: Gestor de memoria a largo plazo
        :param episodic_memory: Gestor de memoria episódica
        :param semantic_memory: Gestor de memoria semántica
        :param export_name: Nombre personalizado para el archivo de exportación
        :return: Ruta del archivo de exportación
        """
        # Generar nombre de exportación si no se proporciona
        if not export_name:
            export_name = (
                f"sheily_memory_export_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            )

        export_data = {
            "metadata": {
                "timestamp": datetime.now().isoformat(),
                "export_name": export_name,
            },
            "memory_types": {},
        }

        # Exportar memoria a corto plazo
        if short_term_memory:
            try:
                with sqlite3.connect(short_term_memory.config.database_path) as conn:
                    cursor = conn.cursor()
                    cursor.execute("SELECT * FROM sessions")
                    export_data["memory_types"][
                        "short_term_sessions"
                    ] = cursor.fetchall()

                    cursor.execute("SELECT * FROM messages")
                    export_data["memory_types"][
                        "short_term_messages"
                    ] = cursor.fetchall()
            except Exception as e:
                self.logger.error(f"Error exportando memoria a corto plazo: {e}")

        # Exportar memoria a largo plazo
        if long_term_memory:
            try:
                with sqlite3.connect(long_term_memory.config.database_path) as conn:
                    cursor = conn.cursor()
                    cursor.execute("SELECT * FROM long_term_memory")
                    export_data["memory_types"]["long_term_memory"] = cursor.fetchall()
            except Exception as e:
                self.logger.error(f"Error exportando memoria a largo plazo: {e}")

        # Exportar memoria episódica
        if episodic_memory:
            try:
                with sqlite3.connect(episodic_memory.config.database_path) as conn:
                    cursor = conn.cursor()
                    cursor.execute("SELECT * FROM episodic_memory")
                    export_data["memory_types"]["episodic_memory"] = cursor.fetchall()
            except Exception as e:
                self.logger.error(f"Error exportando memoria episódica: {e}")

        # Exportar memoria semántica
        if semantic_memory:
            try:
                with sqlite3.connect(semantic_memory.config.database_path) as conn:
                    cursor = conn.cursor()
                    cursor.execute("SELECT * FROM semantic_memory")
                    export_data["memory_types"]["semantic_memory"] = cursor.fetchall()
            except Exception as e:
                self.logger.error(f"Error exportando memoria semántica: {e}")

        # Guardar archivo de exportación
        export_path = self.export_dir / f"{export_name}.json"
        with open(export_path, "w", encoding="utf-8") as f:
            json.dump(export_data, f, ensure_ascii=False, indent=2)

        self.logger.info(f"Memoria exportada exitosamente: {export_path}")
        return str(export_path)

    def import_memory(
        self,
        export_file: str,
        short_term_memory: Optional[ShortTermMemoryManager] = None,
        long_term_memory: Optional[LongTermMemoryManager] = None,
        episodic_memory: Optional[EpisodicMemoryManager] = None,
        semantic_memory: Optional[SemanticMemoryManager] = None,
        merge: bool = False,
    ) -> Dict[str, int]:
        """
        Importar memoria desde un archivo JSON

        :param export_file: Ruta del archivo de exportación
        :param short_term_memory: Gestor de memoria a corto plazo
        :param long_term_memory: Gestor de memoria a largo plazo
        :param episodic_memory: Gestor de memoria episódica
        :param semantic_memory: Gestor de memoria semántica
        :param merge: Si es True, fusiona con datos existentes; si es False, reemplaza
        :return: Diccionario con número de elementos importados por tipo de memoria
        """
        # Cargar archivo de exportación
        with open(export_file, "r", encoding="utf-8") as f:
            export_data = json.load(f)

        import_stats = {}

        # Importar memoria a corto plazo
        if short_term_memory and "short_term_sessions" in export_data["memory_types"]:
            try:
                with sqlite3.connect(short_term_memory.config.database_path) as conn:
                    cursor = conn.cursor()

                    # Limpiar datos existentes si no se va a fusionar
                    if not merge:
                        cursor.execute("DELETE FROM sessions")
                        cursor.execute("DELETE FROM messages")

                    # Importar sesiones
                    sessions = export_data["memory_types"]["short_term_sessions"]
                    cursor.executemany(
                        "INSERT OR REPLACE INTO sessions VALUES (?, ?, ?, ?, ?, ?)",
                        sessions,
                    )

                    # Importar mensajes
                    messages = export_data["memory_types"]["short_term_messages"]
                    cursor.executemany(
                        "INSERT OR REPLACE INTO messages VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)",
                        messages,
                    )

                    conn.commit()
                    import_stats["short_term"] = len(sessions) + len(messages)
            except Exception as e:
                self.logger.error(f"Error importando memoria a corto plazo: {e}")

        # Importar memoria a largo plazo
        if long_term_memory and "long_term_memory" in export_data["memory_types"]:
            try:
                with sqlite3.connect(long_term_memory.config.database_path) as conn:
                    cursor = conn.cursor()

                    if not merge:
                        cursor.execute("DELETE FROM long_term_memory")

                    memories = export_data["memory_types"]["long_term_memory"]
                    cursor.executemany(
                        "INSERT OR REPLACE INTO long_term_memory VALUES (?, ?, ?, ?, ?, ?, ?)",
                        memories,
                    )

                    conn.commit()
                    import_stats["long_term"] = len(memories)
            except Exception as e:
                self.logger.error(f"Error importando memoria a largo plazo: {e}")

        # Importar memoria episódica
        if episodic_memory and "episodic_memory" in export_data["memory_types"]:
            try:
                with sqlite3.connect(episodic_memory.config.database_path) as conn:
                    cursor = conn.cursor()

                    if not merge:
                        cursor.execute("DELETE FROM episodic_memory")

                    episodes = export_data["memory_types"]["episodic_memory"]
                    cursor.executemany(
                        "INSERT OR REPLACE INTO episodic_memory VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
                        episodes,
                    )

                    conn.commit()
                    import_stats["episodic"] = len(episodes)
            except Exception as e:
                self.logger.error(f"Error importando memoria episódica: {e}")

        # Importar memoria semántica
        if semantic_memory and "semantic_memory" in export_data["memory_types"]:
            try:
                with sqlite3.connect(semantic_memory.config.database_path) as conn:
                    cursor = conn.cursor()

                    if not merge:
                        cursor.execute("DELETE FROM semantic_memory")

                    concepts = export_data["memory_types"]["semantic_memory"]
                    cursor.executemany(
                        "INSERT OR REPLACE INTO semantic_memory VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)",
                        concepts,
                    )

                    conn.commit()
                    import_stats["semantic"] = len(concepts)
            except Exception as e:
                self.logger.error(f"Error importando memoria semántica: {e}")

        self.logger.info(
            f"Memoria importada exitosamente. Estadísticas: {import_stats}"
        )
        return import_stats


def create_memory_export_import_manager(
    export_dir: str = "memory_exports",
) -> MemoryExportImportManager:
    """
    Crear una instancia del gestor de exportación/importación de memoria

    :param export_dir: Directorio para almacenar exportaciones
    :return: Instancia de MemoryExportImportManager
    """
    return MemoryExportImportManager(export_dir)
