#!/usr/bin/env python3
"""
Paquete de Memoria a Corto Plazo para Shaili AI
Sistema avanzado para manejo de contexto conversacional y memoria temporal
"""

from .short_term_manager import (
    ShortTermMemoryManager,
    MemoryConfig,
    MemoryMessage,
    MemorySession,
    SemanticAnalyzer,
    MemorySummarizer,
    create_memory_manager,
    setup_memory_system,
    get_memory_context,
    add_message_to_session,
    search_messages,
    backup_memory_data,
)

__version__ = "3.1.0"
__author__ = "Shaili AI Team"
__description__ = "Sistema avanzado de memoria a corto plazo para Shaili AI"

# Configuración por defecto
DEFAULT_CONFIG = MemoryConfig()


def initialize_short_term_module():
    """Inicializar el módulo de memoria a corto plazo"""
    try:
        from pathlib import Path
        import logging

        # Crear directorios necesarios
        directories = ["short_term/memory", "short_term/cache", "short_term/backup"]

        for directory in directories:
            Path(directory).mkdir(parents=True, exist_ok=True)

        print("✅ Módulo de memoria a corto plazo inicializado correctamente")
        return True

    except Exception as e:
        print(f"❌ Error inicializando módulo de memoria a corto plazo: {e}")
        return False


# Auto-inicialización
initialize_short_term_module()


# Funciones de conveniencia
def create_memory_manager(config: MemoryConfig = None) -> ShortTermMemoryManager:
    """Crear gestor de memoria a corto plazo"""
    return ShortTermMemoryManager(config or DEFAULT_CONFIG)


def setup_memory_system(config: MemoryConfig = None) -> bool:
    """Configurar sistema de memoria completo"""
    try:
        manager = create_memory_manager(config)
        print("✅ Sistema de memoria configurado")
        return True
    except Exception as e:
        print(f"❌ Error configurando sistema de memoria: {e}")
        return False


def get_memory_context(
    session_id: str, manager: ShortTermMemoryManager = None, max_tokens: int = None
) -> list:
    """Obtener contexto de memoria"""
    if manager is None:
        manager = create_memory_manager()

    return manager.get_context(session_id, max_tokens)


def add_message_to_session(
    session_id: str,
    role: str,
    content: str,
    manager: ShortTermMemoryManager = None,
    tokens: int = None,
    metadata: dict = None,
) -> str:
    """Añadir mensaje a una sesión"""
    if manager is None:
        manager = create_memory_manager()

    return manager.add_message(session_id, role, content, tokens, metadata)


def search_messages(
    session_id: str, query: str, manager: ShortTermMemoryManager = None, limit: int = 10
) -> list:
    """Buscar mensajes por similitud semántica"""
    if manager is None:
        manager = create_memory_manager()

    return manager.search_messages(session_id, query, limit)


def backup_memory_data(
    manager: ShortTermMemoryManager = None, backup_path: str = None
) -> bool:
    """Crear respaldo de datos de memoria"""
    if manager is None:
        manager = create_memory_manager()

    try:
        manager.backup_memory(backup_path)
        return True
    except Exception as e:
        print(f"❌ Error creando respaldo: {e}")
        return False


def create_session(
    user_id: str, session_id: str = None, manager: ShortTermMemoryManager = None
) -> str:
    """Crear nueva sesión de memoria"""
    if manager is None:
        manager = create_memory_manager()

    return manager.create_session(user_id, session_id)


def get_session_info(session_id: str, manager: ShortTermMemoryManager = None) -> dict:
    """Obtener información de una sesión"""
    if manager is None:
        manager = create_memory_manager()

    return manager.get_session_info(session_id)


def list_sessions(user_id: str = None, manager: ShortTermMemoryManager = None) -> list:
    """Listar sesiones de memoria"""
    if manager is None:
        manager = create_memory_manager()

    return manager.list_sessions(user_id)


def delete_session(session_id: str, manager: ShortTermMemoryManager = None) -> bool:
    """Eliminar sesión de memoria"""
    if manager is None:
        manager = create_memory_manager()

    try:
        manager.delete_session(session_id)
        return True
    except Exception as e:
        print(f"❌ Error eliminando sesión: {e}")
        return False


def clear_session(session_id: str, manager: ShortTermMemoryManager = None) -> bool:
    """Limpiar mensajes de una sesión"""
    if manager is None:
        manager = create_memory_manager()

    try:
        manager.clear_session(session_id)
        return True
    except Exception as e:
        print(f"❌ Error limpiando sesión: {e}")
        return False


# Funciones de análisis semántico
def calculate_similarity(
    text1: str, text2: str, manager: ShortTermMemoryManager = None
) -> float:
    """Calcular similitud semántica entre dos textos"""
    if manager is None:
        manager = create_memory_manager()

    return manager.semantic_analyzer.calculate_similarity(text1, text2)


def get_text_embedding(text: str, manager: ShortTermMemoryManager = None) -> list:
    """Obtener embedding de un texto"""
    if manager is None:
        manager = create_memory_manager()

    return manager.semantic_analyzer.get_embedding(text)


# Funciones de resumen
def generate_summary(session_id: str, manager: ShortTermMemoryManager = None) -> str:
    """Generar resumen de una sesión"""
    if manager is None:
        manager = create_memory_manager()

    if session_id not in manager.messages:
        return ""

    messages = manager.messages[session_id]
    return manager.summarizer.generate_summary(messages)


# Funciones de utilidad
def get_memory_stats(manager: ShortTermMemoryManager = None) -> dict:
    """Obtener estadísticas de memoria"""
    if manager is None:
        manager = create_memory_manager()

    total_sessions = len(manager.sessions)
    total_messages = sum(len(messages) for messages in manager.messages.values())
    total_tokens = sum(session.total_tokens for session in manager.sessions.values())

    return {
        "total_sessions": total_sessions,
        "total_messages": total_messages,
        "total_tokens": total_tokens,
        "active_sessions": len(
            [
                s
                for s in manager.sessions.values()
                if time.time() - s.last_accessed < 3600
            ]
        ),
    }


def cleanup_old_sessions(manager: ShortTermMemoryManager = None) -> int:
    """Limpiar sesiones antiguas"""
    if manager is None:
        manager = create_memory_manager()

    initial_count = len(manager.sessions)
    manager._cleanup_old_sessions()
    final_count = len(manager.sessions)

    return initial_count - final_count


def export_session_data(
    session_id: str, export_path: str = None, manager: ShortTermMemoryManager = None
) -> bool:
    """Exportar datos de una sesión"""
    if manager is None:
        manager = create_memory_manager()

    try:
        import json
        from pathlib import Path

        if session_id not in manager.sessions:
            return False

        session_info = manager.get_session_info(session_id)
        context = manager.get_context(session_id)

        export_data = {
            "session_info": session_info,
            "messages": context,
            "exported_at": time.time(),
            "version": __version__,
        }

        if export_path is None:
            export_path = (
                f"short_term/exports/session_{session_id}_{int(time.time())}.json"
            )

        Path(export_path).parent.mkdir(parents=True, exist_ok=True)

        with open(export_path, "w", encoding="utf-8") as f:
            json.dump(export_data, f, ensure_ascii=False, indent=2)

        print(f"✅ Datos exportados a: {export_path}")
        return True

    except Exception as e:
        print(f"❌ Error exportando datos: {e}")
        return False


# Exportar funciones principales
__all__ = [
    # Clases principales
    "ShortTermMemoryManager",
    "MemoryConfig",
    "MemoryMessage",
    "MemorySession",
    "SemanticAnalyzer",
    "MemorySummarizer",
    # Funciones de conveniencia
    "create_memory_manager",
    "setup_memory_system",
    "get_memory_context",
    "add_message_to_session",
    "search_messages",
    "backup_memory_data",
    # Funciones de gestión de sesiones
    "create_session",
    "get_session_info",
    "list_sessions",
    "delete_session",
    "clear_session",
    # Funciones de análisis semántico
    "calculate_similarity",
    "get_text_embedding",
    # Funciones de resumen
    "generate_summary",
    # Funciones de utilidad
    "get_memory_stats",
    "cleanup_old_sessions",
    "export_session_data",
]


# Información del módulo
def get_module_info() -> dict:
    """Obtener información del módulo"""
    return {
        "name": "short_term",
        "version": __version__,
        "author": __author__,
        "description": __description__,
        "components": {
            "memory_manager": "Gestor principal de memoria a corto plazo",
            "semantic_analyzer": "Análisis semántico y embeddings",
            "memory_summarizer": "Generación de resúmenes",
            "database": "SQLite para persistencia de datos",
            "features": [
                "Gestión de sesiones de conversación",
                "Análisis semántico con TF-IDF",
                "Búsqueda por similitud",
                "Generación automática de resúmenes",
                "Limpieza automática de sesiones",
                "Sistema de respaldo y exportación",
                "Cálculo de importancia de mensajes",
                "Gestión de límites de tokens",
            ],
        },
    }


# Verificación de dependencias
def check_dependencies() -> dict:
    """Verificar dependencias del módulo"""
    dependencies = {
        "core": {
            "sqlite3": "Base de datos",
            "numpy": "Cálculos numéricos",
            "sklearn": "Análisis semántico",
            "pickle": "Serialización",
            "gzip": "Compresión",
        }
    }

    missing = []
    available = []

    # Verificar dependencias
    try:
        import sqlite3

        available.append("sqlite3")
    except ImportError:
        missing.append("sqlite3")

    try:
        import numpy

        available.append("numpy")
    except ImportError:
        missing.append("numpy")

    try:
        import sklearn

        available.append("sklearn")
    except ImportError:
        missing.append("sklearn")

    try:
        import pickle

        available.append("pickle")
    except ImportError:
        missing.append("pickle")

    try:
        import gzip

        available.append("gzip")
    except ImportError:
        missing.append("gzip")

    return {
        "available": available,
        "missing": missing,
        "all_available": len(missing) == 0,
    }


# Mensaje de bienvenida
if __name__ == "__main__":
    import time

    print("🧠 Módulo de Memoria a Corto Plazo Shaili AI")
    print("=" * 50)
    print(f"Versión: {__version__}")
    print(f"Descripción: {__description__}")

    # Verificar dependencias
    deps = check_dependencies()
    if deps["all_available"]:
        print("✅ Todas las dependencias están disponibles")
    else:
        print("⚠️  Dependencias faltantes:")
        for dep in deps["missing"]:
            print(f"   - {dep}")

    # Mostrar información del módulo
    info = get_module_info()
    print(f"\n📋 Componentes disponibles:")
    for component, description in info["components"].items():
        print(f"   - {component}: {description}")

    print(f"\n🔧 Para usar el sistema de memoria:")
    print(
        "   from short_term import create_memory_manager, create_session, add_message_to_session"
    )
    print("   manager = create_memory_manager()")
    print("   session_id = create_session('usuario_123')")
    print("   add_message_to_session(session_id, 'user', 'Hola, ¿cómo estás?')")
