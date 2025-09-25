"""
Sistema de Seguridad - Módulo de Seguridad para NeuroFusion
===========================================================

Módulo especializado en seguridad del sistema NeuroFusion:
- Autenticación multi-factor (MFA)
- Encriptación de datos y archivos
- Gestión de sesiones seguras
- Control de acceso y permisos
- Auditoría de seguridad
- Cumplimiento GDPR
"""

__version__ = "1.0.0"
__author__ = "Shaili AI Team"
__description__ = "Sistema de Seguridad para NeuroFusion"

# Importaciones principales del sistema de seguridad
try:
    from .authentication import MultiFactorAuth
    from .encryption import DataEncryption, FileEncryption
except ImportError:
    # Fallback para cuando los módulos no están disponibles
    pass

__all__ = [
    "MultiFactorAuth",
    "DataEncryption",
    "FileEncryption",
]
