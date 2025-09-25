"""
Sistema de Gestión de Memoria para Shaili AI

Este módulo proporciona diferentes tipos de gestión de memoria:
- Memoria a Corto Plazo
- Memoria a Largo Plazo
- Memoria Episódica
- Memoria Semántica
- Exportación/Importación de Memoria
- Análisis de Memoria
- Integración de Ramas
"""

from .short_term import (
    ShortTermMemoryManager,
    MemoryConfig as ShortTermMemoryConfig,
    create_memory_manager as create_short_term_memory_manager,
)

from .long_term import (
    LongTermMemoryManager,
    LongTermMemoryConfig,
    create_long_term_memory_manager,
)

from .episodic import (
    EpisodicMemoryManager,
    EpisodicMemoryConfig,
    create_episodic_memory_manager,
)

from .semantic import (
    SemanticMemoryManager,
    SemanticMemoryConfig,
    create_semantic_memory_manager,
)

from .export_import_manager import (
    MemoryExportImportManager,
    create_memory_export_import_manager,
)

from .memory_analytics import MemoryAnalytics, create_memory_analytics

from .branch_memory_integrator import (
    BranchMemoryIntegrator,
    create_branch_memory_integrator,
)

__all__ = [
    # Short Term Memory
    "ShortTermMemoryManager",
    "ShortTermMemoryConfig",
    "create_short_term_memory_manager",
    # Long Term Memory
    "LongTermMemoryManager",
    "LongTermMemoryConfig",
    "create_long_term_memory_manager",
    # Episodic Memory
    "EpisodicMemoryManager",
    "EpisodicMemoryConfig",
    "create_episodic_memory_manager",
    # Semantic Memory
    "SemanticMemoryManager",
    "SemanticMemoryConfig",
    "create_semantic_memory_manager",
    # Export/Import
    "MemoryExportImportManager",
    "create_memory_export_import_manager",
    # Analytics
    "MemoryAnalytics",
    "create_memory_analytics",
    # Branch Integration
    "BranchMemoryIntegrator",
    "create_branch_memory_integrator",
]
