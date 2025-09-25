"""
Sistema de gestión de modelos de IA para Shaili AI
"""

# Importar solo las clases que existen
try:
    from .core.quantization_manager import (
        quantization_manager,
        QuantizationManager,
        QuantizationType,
    )
    from .core.model_loader import load_model, generate_response, detect_platform
except ImportError:
    # Si no se pueden importar, crear placeholders
    quantization_manager = None
    QuantizationManager = None
    QuantizationType = None
    load_model = None
    generate_response = None
    detect_platform = None

# Configuración global
__version__ = "1.0.0"
__author__ = "Shaili AI Team"


def get_quantization_manager():
    """Obtener el gestor de cuantización"""
    return quantization_manager


def get_model_loader():
    """Obtener funciones del cargador de modelos"""
    return {
        "load_model": load_model,
        "generate_response": generate_response,
        "detect_platform": detect_platform,
    }


def get_system_info():
    """Obtener información del sistema"""
    return {
        "version": __version__,
        "quantization_available": quantization_manager is not None,
        "model_loader_available": load_model is not None,
    }


# Exponer solo lo que está disponible
__all__ = [
    "quantization_manager",
    "QuantizationManager",
    "QuantizationType",
    "load_model",
    "generate_response",
    "detect_platform",
    "get_quantization_manager",
    "get_model_loader",
    "get_system_info",
]
