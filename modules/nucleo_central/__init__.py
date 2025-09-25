"""
Núcleo Central - Sistema de Inteligencia Artificial NeuroFusion
==============================================================

Paquete central del sistema de IA avanzado con capacidades de:
- Procesamiento de lenguaje natural
- Aprendizaje automático
- Blockchain y tokens
- Memoria y conciencia artificial
- Sistema de ramas especializadas
"""

__version__ = "1.0.0"
__author__ = "Sheily AI Team"
__description__ = "Núcleo Central del Sistema de Inteligencia Artificial NeuroFusion"

# Importaciones principales del sistema
try:
    # Importar desde las ubicaciones correctas
    from ..core.neurofusion_core import NeuroFusionCore
    from ..unified_systems.module_initializer import ModuleInitializer
    from ..unified_systems.module_integrator import ModuleIntegrator
    from ..unified_systems.module_plugin_system import ModulePluginManager
    from ..unified_systems.module_monitor import ModuleMonitor
except ImportError as e:
    # Fallback para cuando los módulos no están disponibles
    print(
        f"⚠️ Advertencia: No se pudieron importar algunos módulos del núcleo central: {e}"
    )
    NeuroFusionCore = None
    ModuleInitializer = None
    ModuleIntegrator = None
    ModulePluginManager = None
    ModuleMonitor = None

__all__ = [
    "NeuroFusionCore",
    "ModuleInitializer",
    "ModuleIntegrator",
    "ModulePluginManager",
    "ModuleMonitor",
]
