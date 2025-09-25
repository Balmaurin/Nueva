"""
Lanzador Principal Unificado de NeuroFusion
===========================================

Script principal que integra todos los sistemas unificados.
"""

import asyncio
import logging
import sys
from typing import Dict, Any, Optional

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Importar sistemas unificados
try:
    from ai.unified_system_core import (
        UnifiedSystemCore,
        SystemConfig,
        get_unified_system,
    )
    from ai.compatibility_adapter import get_compatibility_adapter
    from ai.dependency_manager import get_dependency_manager
except ImportError as e:
    logger.error(f"Error importando sistemas: {e}")
    sys.exit(1)


class NeuroFusionLauncher:
    """Lanzador principal del sistema unificado"""

    def __init__(self, config: Optional[SystemConfig] = None):
        self.config = config or SystemConfig()
        self.unified_system = None
        self.dependency_manager = None
        self.compatibility_adapter = None

    async def initialize(self) -> bool:
        """Inicializar todos los sistemas"""
        logger.info("Inicializando NeuroFusion Unified Launcher...")

        try:
            # Inicializar gestor de dependencias
            self.dependency_manager = get_dependency_manager()

            # Cargar módulos críticos
            critical_modules = [
                "base_tools",
                "unified_branch_tokenizer",
                "perfect_embeddings",
            ]
            for module_name in critical_modules:
                await self.dependency_manager.load_module(module_name)

            # Inicializar adaptador de compatibilidad
            self.compatibility_adapter = get_compatibility_adapter()

            # Inicializar sistema unificado
            self.unified_system = await get_unified_system(self.config)

            logger.info("NeuroFusion inicializado correctamente")
            return True

        except Exception as e:
            logger.error(f"Error inicializando: {e}")
            return False

    async def run_interactive(self):
        """Modo interactivo"""
        print("\n🤖 NeuroFusion Unified System - Modo Interactivo")
        print("Escribe 'salir' para terminar")

        while True:
            try:
                query = input("\n👤 Tú: ").strip()

                if query.lower() in ["salir", "exit"]:
                    break

                if not query:
                    continue

                # Procesar consulta
                response = await self.unified_system.process_query(query)
                print(f"🤖 NeuroFusion: {response['response']}")

            except KeyboardInterrupt:
                break
            except Exception as e:
                logger.error(f"Error: {e}")
                print(f"❌ Error: {e}")

    async def shutdown(self):
        """Apagar sistema"""
        if self.unified_system:
            await self.unified_system.shutdown()


async def main():
    """Función principal"""
    launcher = NeuroFusionLauncher()

    try:
        if not await launcher.initialize():
            return 1

        await launcher.run_interactive()
        return 0

    except KeyboardInterrupt:
        return 0
    except Exception as e:
        logger.error(f"Error: {e}")
        return 1
    finally:
        await launcher.shutdown()


if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)
