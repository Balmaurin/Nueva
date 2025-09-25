#!/usr/bin/env python3
"""
Integrador de Memoria y Ramas para Sheily AI

Este módulo permite integrar los datos de las ramas con los diferentes
tipos de memoria del sistema.
"""

import os
import json
import logging
from typing import List, Dict, Any, Optional
import jsonlines
from pathlib import Path

from .short_term import ShortTermMemoryManager
from .long_term import LongTermMemoryManager
from .episodic import EpisodicMemoryManager
from .semantic import SemanticMemoryManager


class BranchMemoryIntegrator:
    """
    Clase para integrar datos de ramas con el sistema de memoria
    """

    def __init__(
        self,
        branches_dir: str = "data/branches",
        short_term_memory: Optional[ShortTermMemoryManager] = None,
        long_term_memory: Optional[LongTermMemoryManager] = None,
        episodic_memory: Optional[EpisodicMemoryManager] = None,
        semantic_memory: Optional[SemanticMemoryManager] = None,
    ):
        """
        Inicializar integrador de memoria y ramas

        :param branches_dir: Directorio que contiene los archivos de ramas
        :param short_term_memory: Gestor de memoria a corto plazo
        :param long_term_memory: Gestor de memoria a largo plazo
        :param episodic_memory: Gestor de memoria episódica
        :param semantic_memory: Gestor de memoria semántica
        """
        self.branches_dir = Path(branches_dir)
        self.short_term_memory = short_term_memory
        self.long_term_memory = long_term_memory
        self.episodic_memory = episodic_memory
        self.semantic_memory = semantic_memory

        self.logger = logging.getLogger(__name__)

    def load_branch_files(
        self, max_branches: Optional[int] = None
    ) -> List[Dict[str, Any]]:
        """
        Cargar archivos de ramas

        :param max_branches: Número máximo de archivos de ramas a cargar
        :return: Lista de datos de ramas
        """
        branch_files = sorted(self.branches_dir.glob("branch_*_dataset.jsonl"))

        if max_branches:
            branch_files = branch_files[:max_branches]

        branch_data = []
        for branch_file in branch_files:
            try:
                with jsonlines.open(branch_file) as reader:
                    branch_data.extend(list(reader))
            except Exception as e:
                self.logger.error(f"Error cargando archivo de rama {branch_file}: {e}")

        return branch_data

    def integrate_branches_with_memory(self, max_branches: Optional[int] = None):
        """
        Integrar datos de ramas con los diferentes tipos de memoria

        :param max_branches: Número máximo de archivos de ramas a integrar
        """
        branch_data = self.load_branch_files(max_branches)

        # Integración con memoria a largo plazo
        if self.long_term_memory:
            self._integrate_long_term_memory(branch_data)

        # Integración con memoria episódica
        if self.episodic_memory:
            self._integrate_episodic_memory(branch_data)

        # Integración con memoria semántica
        if self.semantic_memory:
            self._integrate_semantic_memory(branch_data)

    def _integrate_long_term_memory(self, branch_data: List[Dict[str, Any]]):
        """
        Integrar datos de ramas en memoria a largo plazo

        :param branch_data: Datos de ramas
        """
        for entry in branch_data:
            try:
                # Extraer información relevante para memoria a largo plazo
                content = entry.get("text", "") or entry.get("content", "")
                category = entry.get("category", "branch_data")

                self.long_term_memory.add_memory(
                    category=category,
                    content=content,
                    metadata={
                        "branch_id": entry.get("branch_id"),
                        "source": "branch_dataset",
                    },
                )
            except Exception as e:
                self.logger.error(
                    f"Error integrando entrada de rama en memoria a largo plazo: {e}"
                )

    def _integrate_episodic_memory(self, branch_data: List[Dict[str, Any]]):
        """
        Integrar datos de ramas en memoria episódica

        :param branch_data: Datos de ramas
        """
        for entry in branch_data:
            try:
                # Extraer información relevante para memoria episódica
                content = entry.get("text", "") or entry.get("content", "")
                event_type = entry.get("type", "branch_data")

                self.episodic_memory.record_episode(
                    context="Datos de Rama",
                    event_type=event_type,
                    details={"branch_id": entry.get("branch_id"), "content": content},
                    tags=["branch", event_type],
                    importance=entry.get("importance", 0.5),
                )
            except Exception as e:
                self.logger.error(
                    f"Error integrando entrada de rama en memoria episódica: {e}"
                )

    def _integrate_semantic_memory(self, branch_data: List[Dict[str, Any]]):
        """
        Integrar datos de ramas en memoria semántica

        :param branch_data: Datos de ramas
        """
        for entry in branch_data:
            try:
                # Extraer información relevante para memoria semántica
                content = entry.get("text", "") or entry.get("content", "")
                domain = entry.get("category", "branch_data")
                concept = entry.get("concept", "Datos de Rama")

                self.semantic_memory.add_concept(
                    domain=domain,
                    concept=concept,
                    description=content,
                    metadata={
                        "branch_id": entry.get("branch_id"),
                        "source": "branch_dataset",
                    },
                )
            except Exception as e:
                self.logger.error(
                    f"Error integrando entrada de rama en memoria semántica: {e}"
                )


def create_branch_memory_integrator(
    branches_dir: str = "data/branches",
    short_term_memory: Optional[ShortTermMemoryManager] = None,
    long_term_memory: Optional[LongTermMemoryManager] = None,
    episodic_memory: Optional[EpisodicMemoryManager] = None,
    semantic_memory: Optional[SemanticMemoryManager] = None,
) -> BranchMemoryIntegrator:
    """
    Crear una instancia del integrador de memoria y ramas

    :return: Instancia de BranchMemoryIntegrator
    """
    return BranchMemoryIntegrator(
        branches_dir,
        short_term_memory,
        long_term_memory,
        episodic_memory,
        semantic_memory,
    )
