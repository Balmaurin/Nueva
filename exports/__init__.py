"""
Sistema de Exportación - Shaili AI

Este paquete proporciona funcionalidades completas para exportar datos
del sistema en diferentes formatos y con diferentes niveles de detalle.
"""

from .export_manager import ExportManager, ExportConfig, ExportMetadata
from .data_exporter import DataExporter, ExportSpecification

# Versión del paquete
__version__ = "3.1.0"
__author__ = "Shaili AI Team"
__description__ = "Sistema completo de exportación de datos para IA"

# Instancias globales para uso directo
_export_manager = None
_data_exporter = None


def get_export_manager(config=None) -> ExportManager:
    """Obtener instancia global del gestor de exportación"""
    global _export_manager
    if _export_manager is None:
        _export_manager = ExportManager(config)
    return _export_manager


def get_data_exporter(base_dir: str = "exports") -> DataExporter:
    """Obtener instancia global del exportador de datos"""
    global _data_exporter
    if _data_exporter is None:
        _data_exporter = DataExporter(base_dir)
    return _data_exporter


# Funciones de conveniencia para exportación rápida
def export_user_data(
    user_id: str,
    data_types: list = None,
    format: str = "jsonl",
    include_pii: bool = False,
) -> dict:
    """
    Exportar datos de usuario específico

    Args:
        user_id: ID del usuario
        data_types: Tipos de datos a exportar
        format: Formato de exportación
        include_pii: Incluir datos personales

    Returns:
        Resultado de la exportación
    """
    config = ExportConfig(format=format, include_pii=include_pii, include_metadata=True)

    manager = get_export_manager(config)
    return manager.export_user_data(user_id, data_types)


def export_conversations(
    user_id: str = None, format: str = "jsonl", date_range: tuple = None
) -> dict:
    """
    Exportar conversaciones

    Args:
        user_id: ID del usuario (opcional)
        format: Formato de exportación
        date_range: Rango de fechas

    Returns:
        Resultado de la exportación
    """
    config = ExportConfig(format=format, include_pii=True, include_metadata=True)

    manager = get_export_manager(config)
    return manager.export_conversations(user_id, date_range)


def export_system_data(
    data_types: list = None, format: str = "json", date_range: tuple = None
) -> dict:
    """
    Exportar datos del sistema

    Args:
        data_types: Tipos de datos a exportar
        format: Formato de exportación
        date_range: Rango de fechas

    Returns:
        Resultado de la exportación
    """
    config = ExportConfig(format=format, include_pii=False, include_metadata=True)

    manager = get_export_manager(config)
    return manager.export_system_data(data_types, date_range)


def export_from_database(
    data_type: str, source_path: str, output_format: str = "csv", filters: dict = None
) -> dict:
    """
    Exportar datos desde una base de datos

    Args:
        data_type: Tipo de datos (conversations, embeddings, user_profiles, etc.)
        source_path: Ruta a la base de datos
        output_format: Formato de salida
        filters: Filtros a aplicar

    Returns:
        Resultado de la exportación
    """
    spec = ExportSpecification(
        data_type=data_type,
        source_path=source_path,
        output_format=output_format,
        filters=filters,
    )

    exporter = get_data_exporter()

    # Mapear tipo de datos a método de exportación
    export_methods = {
        "conversations": exporter.export_conversations,
        "embeddings": exporter.export_embeddings,
        "user_profiles": exporter.export_user_profiles,
        "system_logs": exporter.export_system_logs,
        "configurations": exporter.export_configurations,
        "evaluation_results": exporter.export_evaluation_results,
    }

    if data_type not in export_methods:
        return {"success": False, "error": f"Unsupported data type: {data_type}"}

    return export_methods[data_type](spec)


def export_conversations_from_db(
    source_path: str, output_format: str = "jsonl", filters: dict = None
) -> dict:
    """
    Exportar conversaciones desde base de datos

    Args:
        source_path: Ruta a la base de datos
        output_format: Formato de salida
        filters: Filtros a aplicar

    Returns:
        Resultado de la exportación
    """
    return export_from_database("conversations", source_path, output_format, filters)


def export_embeddings_from_db(
    source_path: str, output_format: str = "parquet", filters: dict = None
) -> dict:
    """
    Exportar embeddings desde base de datos

    Args:
        source_path: Ruta a la base de datos
        output_format: Formato de salida
        filters: Filtros a aplicar

    Returns:
        Resultado de la exportación
    """
    return export_from_database("embeddings", source_path, output_format, filters)


def export_user_profiles_from_db(
    source_path: str, output_format: str = "csv", filters: dict = None
) -> dict:
    """
    Exportar perfiles de usuario desde base de datos

    Args:
        source_path: Ruta a la base de datos
        output_format: Formato de salida
        filters: Filtros a aplicar

    Returns:
        Resultado de la exportación
    """
    return export_from_database("user_profiles", source_path, output_format, filters)


def export_system_logs_from_file(
    log_path: str, output_format: str = "jsonl", filters: dict = None
) -> dict:
    """
    Exportar logs del sistema desde archivo

    Args:
        log_path: Ruta al archivo de logs
        output_format: Formato de salida
        filters: Filtros a aplicar

    Returns:
        Resultado de la exportación
    """
    spec = ExportSpecification(
        data_type="system_logs",
        source_path=log_path,
        output_format=output_format,
        filters=filters,
    )

    exporter = get_data_exporter()
    return exporter.export_system_logs(spec)


def export_configurations_from_file(
    config_path: str, output_format: str = "json"
) -> dict:
    """
    Exportar configuraciones desde archivo

    Args:
        config_path: Ruta al archivo de configuración
        output_format: Formato de salida

    Returns:
        Resultado de la exportación
    """
    spec = ExportSpecification(
        data_type="configurations", source_path=config_path, output_format=output_format
    )

    exporter = get_data_exporter()
    return exporter.export_configurations(spec)


def export_evaluation_results_from_file(
    results_path: str, output_format: str = "json"
) -> dict:
    """
    Exportar resultados de evaluación desde archivo

    Args:
        results_path: Ruta al archivo de resultados
        output_format: Formato de salida

    Returns:
        Resultado de la exportación
    """
    spec = ExportSpecification(
        data_type="evaluation_results",
        source_path=results_path,
        output_format=output_format,
    )

    exporter = get_data_exporter()
    return exporter.export_evaluation_results(spec)


# Funciones de gestión
def get_export_history(limit: int = 50) -> list:
    """
    Obtener historial de exportaciones

    Args:
        limit: Número máximo de entradas

    Returns:
        Lista de exportaciones recientes
    """
    manager = get_export_manager()
    return manager.get_export_history(limit)


def cleanup_old_exports(days: int = 30) -> int:
    """
    Limpiar exportaciones antiguas

    Args:
        days: Número de días para considerar como "antiguo"

    Returns:
        Número de archivos eliminados
    """
    manager = get_export_manager()
    return manager.cleanup_old_exports(days)


def list_available_exports() -> dict:
    """
    Listar exportaciones disponibles

    Returns:
        Diccionario con exportaciones organizadas por tipo
    """
    exporter = get_data_exporter()
    return exporter.list_available_exports()


def get_export_info(data_type: str, filename: str) -> dict:
    """
    Obtener información de una exportación específica

    Args:
        data_type: Tipo de datos
        filename: Nombre del archivo

    Returns:
        Información de la exportación
    """
    exporter = get_data_exporter()
    return exporter.get_export_info(data_type, filename)


# Funciones de configuración
def create_export_config(
    format: str = "jsonl", include_pii: bool = False, compress: bool = False
) -> ExportConfig:
    """
    Crear configuración de exportación

    Args:
        format: Formato de exportación
        include_pii: Incluir datos personales
        compress: Comprimir archivos

    Returns:
        Configuración de exportación
    """
    return ExportConfig(
        format=format, include_pii=include_pii, compress=compress, include_metadata=True
    )


def create_export_specification(
    data_type: str, source_path: str, output_format: str = "csv", filters: dict = None
) -> ExportSpecification:
    """
    Crear especificación de exportación

    Args:
        data_type: Tipo de datos
        source_path: Ruta de origen
        output_format: Formato de salida
        filters: Filtros a aplicar

    Returns:
        Especificación de exportación
    """
    return ExportSpecification(
        data_type=data_type,
        source_path=source_path,
        output_format=output_format,
        filters=filters,
        include_metadata=True,
    )


# Funciones de utilidad
def validate_export_config(config: ExportConfig) -> bool:
    """
    Validar configuración de exportación

    Args:
        config: Configuración a validar

    Returns:
        True si la configuración es válida
    """
    valid_formats = ["jsonl", "json", "csv", "xml", "yaml"]
    return config.format in valid_formats


def get_supported_formats() -> list:
    """
    Obtener formatos soportados

    Returns:
        Lista de formatos soportados
    """
    return ["jsonl", "json", "csv", "xml", "yaml", "parquet", "pickle"]


def get_supported_data_types() -> list:
    """
    Obtener tipos de datos soportados

    Returns:
        Lista de tipos de datos soportados
    """
    return [
        "conversations",
        "embeddings",
        "user_profiles",
        "system_logs",
        "configurations",
        "evaluation_results",
    ]


# Inicialización automática del módulo
def initialize_exports_module():
    """Inicializar el módulo de exportaciones"""
    try:
        # Crear directorios necesarios
        from pathlib import Path

        export_dir = Path("exports")
        export_dir.mkdir(parents=True, exist_ok=True)

        # Crear subdirectorios para diferentes tipos de datos
        data_types = get_supported_data_types()
        for data_type in data_types:
            (export_dir / data_type).mkdir(exist_ok=True)

        print("✅ Módulo de exportaciones inicializado correctamente")
        return True
    except Exception as e:
        print(f"❌ Error inicializando módulo de exportaciones: {e}")
        return False


# Ejecutar inicialización al importar el módulo
initialize_exports_module()

# API pública del módulo
__all__ = [
    # Clases principales
    "ExportManager",
    "ExportConfig",
    "ExportMetadata",
    "DataExporter",
    "ExportSpecification",
    # Funciones de conveniencia
    "export_user_data",
    "export_conversations",
    "export_system_data",
    "export_from_database",
    "export_conversations_from_db",
    "export_embeddings_from_db",
    "export_user_profiles_from_db",
    "export_system_logs_from_file",
    "export_configurations_from_file",
    "export_evaluation_results_from_file",
    # Funciones de gestión
    "get_export_history",
    "cleanup_old_exports",
    "list_available_exports",
    "get_export_info",
    # Funciones de configuración
    "create_export_config",
    "create_export_specification",
    # Funciones de utilidad
    "validate_export_config",
    "get_supported_formats",
    "get_supported_data_types",
    # Funciones de inicialización
    "initialize_exports_module",
    # Metadatos
    "__version__",
    "__author__",
    "__description__",
]
