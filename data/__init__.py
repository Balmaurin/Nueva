#!/usr/bin/env python3
"""
Módulo de Gestión de Datos del Sistema NeuroFusion
Proporciona acceso centralizado a todas las funcionalidades de gestión de datos
"""

import os
import sys
from pathlib import Path

# Agregar el directorio actual al path para importaciones
current_dir = Path(__file__).parent
if str(current_dir) not in sys.path:
    sys.path.insert(0, str(current_dir))

# Importar los gestores de datos
try:
    from .data_manager import DataManager, get_data_manager, DataStats
    from .corpus_processor import (
        CorpusProcessor,
        get_corpus_processor,
        ProcessedDocument,
        CorpusStats as CorpusProcessorStats,
    )
    from .embeddings_manager import (
        EmbeddingsManager,
        get_embeddings_manager,
        EmbeddingInfo,
        SearchResult,
    )
except ImportError as e:
    print(f"Error importando módulos de datos: {e}")

    # Crear versiones mínimas si no se pueden importar
    class DataManager:
        def __init__(self):
            pass

        def get_data_stats(self):
            return DataStats(0, 0, 0, 0, 0.0, 0.0, None)

    class CorpusProcessor:
        def __init__(self):
            pass

        def process_document(self, doc):
            return None

    class EmbeddingsManager:
        def __init__(self):
            pass

        def generate_embedding(self, text):
            return None


# Versión del módulo
__version__ = "3.1.0"
__author__ = "NeuroFusion Team"
__description__ = "Sistema de Gestión de Datos NeuroFusion"

# Configuración por defecto
DEFAULT_DATA_DIR = "data"
DEFAULT_CORPUS_DIR = "data/corpus"
DEFAULT_EMBEDDINGS_DIR = "data/embeddings"

# Instancias globales
_data_manager = None
_corpus_processor = None
_embeddings_manager = None


def get_data_manager_instance() -> DataManager:
    """Obtiene la instancia global del gestor de datos"""
    global _data_manager
    if _data_manager is None:
        _data_manager = DataManager()
    return _data_manager


def get_corpus_processor_instance() -> CorpusProcessor:
    """Obtiene la instancia global del procesador de corpus"""
    global _corpus_processor
    if _corpus_processor is None:
        _corpus_processor = CorpusProcessor()
    return _corpus_processor


def get_embeddings_manager_instance() -> EmbeddingsManager:
    """Obtiene la instancia global del gestor de embeddings"""
    global _embeddings_manager
    if _embeddings_manager is None:
        _embeddings_manager = EmbeddingsManager()
    return _embeddings_manager


# Funciones de gestión de datos
def get_data_stats() -> DataStats:
    """Obtiene estadísticas generales de los datos"""
    manager = get_data_manager_instance()
    return manager.get_data_stats()


def get_knowledge_base_data(limit: int = 100) -> list:
    """Obtiene datos de la base de conocimientos"""
    manager = get_data_manager_instance()
    return manager.get_knowledge_base_data(limit)


def add_knowledge_entry(
    title: str, content: str, category: str, metadata: dict = None
) -> bool:
    """Agrega una entrada a la base de conocimientos"""
    manager = get_data_manager_instance()
    return manager.add_knowledge_entry(title, content, category, metadata)


def get_embeddings_data(limit: int = 100) -> list:
    """Obtiene datos de embeddings"""
    manager = get_data_manager_instance()
    return manager.get_embeddings_data(limit)


def get_user_data(user_id: str = None, limit: int = 100) -> list:
    """Obtiene datos de usuarios"""
    manager = get_data_manager_instance()
    return manager.get_user_data(user_id, limit)


def get_rag_memory_data(query: str = None, limit: int = 100) -> list:
    """Obtiene datos de memoria RAG"""
    manager = get_data_manager_instance()
    return manager.get_rag_memory_data(query, limit)


# Funciones de procesamiento de corpus
def process_document(document: dict) -> ProcessedDocument:
    """Procesa un documento"""
    processor = get_corpus_processor_instance()
    return processor.process_document(document)


def process_corpus(corpus_data: dict, save_processed: bool = True) -> tuple:
    """Procesa un corpus completo"""
    processor = get_corpus_processor_instance()
    return processor.process_corpus(corpus_data, save_processed)


def clean_text(text: str, language: str = "es") -> str:
    """Limpia un texto"""
    processor = get_corpus_processor_instance()
    return processor.clean_text(text, language)


def tokenize_text(
    text: str, language: str = "es", remove_stop_words: bool = False
) -> list:
    """Tokeniza un texto"""
    processor = get_corpus_processor_instance()
    return processor.tokenize_text(text, language, remove_stop_words)


def extract_keywords(text: str, language: str = "es", top_k: int = 10) -> list:
    """Extrae palabras clave de un texto"""
    processor = get_corpus_processor_instance()
    return processor.extract_keywords(text, language, top_k)


def detect_language(text: str) -> str:
    """Detecta el idioma de un texto"""
    processor = get_corpus_processor_instance()
    return processor.detect_language(text)


# Funciones de gestión de embeddings
def generate_embedding(text: str, model_name: str = "all-MiniLM-L6-v2") -> list:
    """Genera un embedding para un texto"""
    manager = get_embeddings_manager_instance()
    return manager.generate_embedding(text, model_name)


def generate_batch_embeddings(
    texts: list, model_name: str = "all-MiniLM-L6-v2"
) -> list:
    """Genera embeddings para un lote de textos"""
    manager = get_embeddings_manager_instance()
    return manager.generate_batch_embeddings(texts, model_name)


def save_embedding(
    text: str, embedding_vector: list, model_name: str, metadata: dict = None
) -> bool:
    """Guarda un embedding"""
    manager = get_embeddings_manager_instance()
    return manager.save_embedding(text, embedding_vector, model_name, metadata)


def get_embedding(embedding_id: str) -> EmbeddingInfo:
    """Obtiene un embedding por ID"""
    manager = get_embeddings_manager_instance()
    return manager.get_embedding(embedding_id)


def search_similar_embeddings(
    query_embedding: list, model_name: str = "all-MiniLM-L6-v2", top_k: int = 10
) -> list:
    """Busca embeddings similares"""
    manager = get_embeddings_manager_instance()
    return manager.search_similar_embeddings(query_embedding, model_name, top_k)


def search_faiss_index(
    query_embedding: list, model_name: str = "all-MiniLM-L6-v2", top_k: int = 10
) -> list:
    """Busca usando índice FAISS"""
    manager = get_embeddings_manager_instance()
    return manager.search_faiss_index(query_embedding, model_name, top_k)


def create_faiss_index(model_name: str = "all-MiniLM-L6-v2") -> bool:
    """Crea un índice FAISS"""
    manager = get_embeddings_manager_instance()
    return manager.create_faiss_index(model_name)


# Funciones de gestión de corpus
def load_corpus(corpus_name: str) -> dict:
    """Carga un corpus"""
    manager = get_data_manager_instance()
    return manager.load_corpus(corpus_name)


def save_corpus(corpus_name: str, corpus_data: dict) -> bool:
    """Guarda un corpus"""
    manager = get_data_manager_instance()
    return manager.save_corpus(corpus_name, corpus_data)


def create_vocabulary(processed_docs: list, min_freq: int = 2) -> dict:
    """Crea un vocabulario"""
    processor = get_corpus_processor_instance()
    return processor.create_vocabulary(processed_docs, min_freq)


def calculate_tf_idf(processed_docs: list) -> dict:
    """Calcula TF-IDF"""
    processor = get_corpus_processor_instance()
    return processor.calculate_tf_idf(processed_docs)


# Funciones de caché
def get_cache_data(cache_key: str) -> any:
    """Obtiene datos del caché"""
    manager = get_data_manager_instance()
    return manager.get_cache_data(cache_key)


def set_cache_data(cache_key: str, value: any, ttl_hours: int = 24) -> bool:
    """Establece datos en el caché"""
    manager = get_data_manager_instance()
    return manager.set_cache_data(cache_key, value, ttl_hours)


def clear_cache(pattern: str = "*") -> int:
    """Limpia el caché"""
    manager = get_data_manager_instance()
    return manager.clear_cache(pattern)


# Funciones de backup y exportación
def create_backup(backup_name: str = None) -> str:
    """Crea un backup de todos los datos"""
    manager = get_data_manager_instance()
    return manager.create_backup(backup_name)


def restore_backup(backup_path: str) -> bool:
    """Restaura datos desde un backup"""
    manager = get_data_manager_instance()
    return manager.restore_backup(backup_path)


def export_data(export_format: str = "json", filters: dict = None) -> str:
    """Exporta datos"""
    manager = get_data_manager_instance()
    return manager.export_data(export_format, filters)


def backup_embeddings(backup_name: str = None) -> str:
    """Crea un backup de embeddings"""
    manager = get_embeddings_manager_instance()
    return manager.backup_embeddings(backup_name)


# Funciones de limpieza y mantenimiento
def cleanup_old_data(days_old: int = 30) -> int:
    """Limpia datos antiguos"""
    manager = get_data_manager_instance()
    return manager.cleanup_old_data(days_old)


def clear_embeddings_cache(pattern: str = "*") -> int:
    """Limpia el caché de embeddings"""
    manager = get_embeddings_manager_instance()
    return manager.clear_cache(pattern)


def clear_corpus_cache():
    """Limpia el caché del procesador de corpus"""
    processor = get_corpus_processor_instance()
    processor.clear_cache()


# Funciones de estadísticas
def get_embeddings_stats() -> dict:
    """Obtiene estadísticas de embeddings"""
    manager = get_embeddings_manager_instance()
    return manager.get_embeddings_stats()


def get_corpus_stats(corpus_data: dict) -> CorpusProcessorStats:
    """Obtiene estadísticas de un corpus"""
    processor = get_corpus_processor_instance()
    return processor._calculate_corpus_stats(corpus_data.get("documents", []), None)


# Funciones de utilidad
def get_data_directory() -> str:
    """Obtiene el directorio de datos"""
    return str(Path(DEFAULT_DATA_DIR))


def get_corpus_directory() -> str:
    """Obtiene el directorio de corpus"""
    return str(Path(DEFAULT_CORPUS_DIR))


def get_embeddings_directory() -> str:
    """Obtiene el directorio de embeddings"""
    return str(Path(DEFAULT_EMBEDDINGS_DIR))


def list_available_corpus() -> list:
    """Lista los corpus disponibles"""
    corpus_dir = Path(DEFAULT_CORPUS_DIR)
    if not corpus_dir.exists():
        return []

    return [f.stem for f in corpus_dir.glob("*.json")]


def list_available_models() -> list:
    """Lista los modelos de embeddings disponibles"""
    embeddings_manager = get_embeddings_manager_instance()
    return list(embeddings_manager.models.keys())


# Funciones de inicialización y cierre
def initialize_data_system():
    """Inicializa el sistema de datos"""
    try:
        # Inicializar gestores
        get_data_manager_instance()
        get_corpus_processor_instance()
        get_embeddings_manager_instance()

        print(f"✅ Sistema de datos NeuroFusion v{__version__} inicializado")
        return True

    except Exception as e:
        print(f"❌ Error inicializando sistema de datos: {e}")
        return False


def close_data_system():
    """Cierra el sistema de datos"""
    try:
        global _data_manager, _embeddings_manager

        if _data_manager:
            _data_manager.close_connections()

        if _embeddings_manager:
            _embeddings_manager.close_connection()

        print("✅ Sistema de datos cerrado")
        return True

    except Exception as e:
        print(f"❌ Error cerrando sistema de datos: {e}")
        return False


# Función de inicialización del módulo
def initialize_data_module():
    """Inicializa el módulo de datos"""
    try:
        # Verificar que los directorios existan
        data_dir = Path(DEFAULT_DATA_DIR)
        if not data_dir.exists():
            print("⚠️  Advertencia: Directorio de datos no encontrado")

        # Inicializar sistema
        initialize_data_system()

    except Exception as e:
        print(f"❌ Error inicializando módulo de datos: {e}")


# Inicializar el módulo al importarlo
initialize_data_module()

# Exportar funciones y clases principales
__all__ = [
    "DataManager",
    "CorpusProcessor",
    "EmbeddingsManager",
    "DataStats",
    "ProcessedDocument",
    "CorpusProcessorStats",
    "EmbeddingInfo",
    "SearchResult",
    "get_data_manager",
    "get_corpus_processor",
    "get_embeddings_manager",
    "get_data_stats",
    "get_knowledge_base_data",
    "add_knowledge_entry",
    "get_embeddings_data",
    "get_user_data",
    "get_rag_memory_data",
    "process_document",
    "process_corpus",
    "clean_text",
    "tokenize_text",
    "extract_keywords",
    "detect_language",
    "generate_embedding",
    "generate_batch_embeddings",
    "save_embedding",
    "get_embedding",
    "search_similar_embeddings",
    "search_faiss_index",
    "create_faiss_index",
    "load_corpus",
    "save_corpus",
    "create_vocabulary",
    "calculate_tf_idf",
    "get_cache_data",
    "set_cache_data",
    "clear_cache",
    "create_backup",
    "restore_backup",
    "export_data",
    "backup_embeddings",
    "cleanup_old_data",
    "clear_embeddings_cache",
    "clear_corpus_cache",
    "get_embeddings_stats",
    "get_corpus_stats",
    "get_data_directory",
    "get_corpus_directory",
    "get_embeddings_directory",
    "list_available_corpus",
    "list_available_models",
    "initialize_data_system",
    "close_data_system",
    "__version__",
    "__author__",
    "__description__",
]
