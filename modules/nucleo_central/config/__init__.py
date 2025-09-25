"""
Configuraciones del Núcleo Central
==================================

Configuraciones específicas del sistema NeuroFusion:
- Límites de velocidad (rate limits)
- Configuración de entrenamiento avanzado
- Parámetros del sistema

Nota: Las configuraciones están centralizadas en el directorio config/
y este módulo proporciona acceso a ellas.
"""

from .rate_limits import load_rate_limits
from .advanced_training import load_training_config

__all__ = [
    "load_rate_limits",
    "load_training_config",
]
