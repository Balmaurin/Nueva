#!/usr/bin/env python3
"""
Script de Inicio del Sistema Maestro NeuroFusion

Este script permite iniciar el sistema maestro unificado con diferentes modos
de operación y configuraciones.

Modos disponibles:
- full: Sistema completo con todos los componentes
- api: Solo API REST con sistema maestro
- interactive: Modo interactivo de consola
- demo: Modo demostración
- minimal: Sistema mínimo básico

Autor: NeuroFusion AI Team
Fecha: 2024-08-28
"""

import asyncio
import argparse
import signal
import sys
import logging
from pathlib import Path
from typing import Optional

# Agregar el directorio actual al path
sys.path.append(str(Path(__file__).parent))

from neurofusion_master_system import (
    NeuroFusionMasterSystem,
    MasterSystemConfig,
    SystemMode,
    get_master_system,
    shutdown_master_system,
)

# Configuración de logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


class MasterSystemManager:
    """Gestor del sistema maestro"""

    def __init__(self):
        self.master_system = None
        self.running = False

        # Configurar manejo de señales
        signal.signal(signal.SIGINT, self._signal_handler)
        signal.signal(signal.SIGTERM, self._signal_handler)

    def _signal_handler(self, signum, frame):
        """Manejar señales de interrupción"""
        logger.info(f"🛑 Señal recibida: {signum}")
        self.running = False
        asyncio.create_task(self._graceful_shutdown())

    async def _graceful_shutdown(self):
        """Apagado graceful del sistema"""
        logger.info("🔄 Iniciando apagado graceful...")

        if self.master_system:
            await self.master_system.shutdown()

        logger.info("✅ Sistema apagado correctamente")
        sys.exit(0)

    async def start_full_system(self, config_path: Optional[str] = None):
        """Iniciar sistema completo"""
        logger.info("🚀 Iniciando sistema maestro completo...")

        # Cargar configuración
        config = self._load_config(config_path)
        config.mode = SystemMode.PRODUCTION
        config.enable_embeddings = True
        config.enable_generation = True
        config.enable_learning = True
        config.enable_consciousness = True
        config.enable_security = True
        config.enable_training = True
        config.enable_branch_tokenizer = True
        config.enable_consolidated_architecture = True

        # Inicializar sistema maestro
        self.master_system = await get_master_system(config)

        # Mostrar estado inicial
        status = self.master_system.get_system_status()
        logger.info(f"✅ Sistema maestro iniciado:")
        logger.info(
            f"   - Componentes activos: {sum(1 for s in status['components'].values() if s == 'active')}"
        )
        logger.info(f"   - Modo: {status['system_info']['mode']}")
        logger.info(f"   - Versión: {status['system_info']['version']}")

        # Mantener sistema ejecutándose
        self.running = True
        while self.running:
            await asyncio.sleep(1)

    async def start_api_server(self, config_path: Optional[str] = None):
        """Iniciar servidor API"""
        logger.info("🌐 Iniciando servidor API del sistema maestro...")

        # Cargar configuración
        config = self._load_config(config_path)
        config.mode = SystemMode.PRODUCTION
        config.enable_security = True

        # Inicializar sistema maestro
        self.master_system = await get_master_system(config)

        # Importar y configurar FastAPI
        try:
            from fastapi import FastAPI, HTTPException
            from fastapi.middleware.cors import CORSMiddleware
            import uvicorn
            from pydantic import BaseModel
            from typing import Dict, Any, Optional

            # Crear aplicación FastAPI
            app = FastAPI(
                title="NeuroFusion Master System API",
                description="API del Sistema Maestro Unificado NeuroFusion",
                version="3.0.0",
            )

            # Configurar CORS
            app.add_middleware(
                CORSMiddleware,
                allow_origins=["*"],
                allow_credentials=True,
                allow_methods=["*"],
                allow_headers=["*"],
            )

            # Modelos Pydantic
            class QueryRequest(BaseModel):
                query: str
                domain: str = "general"
                context: Optional[Dict[str, Any]] = None
                user_id: Optional[str] = None

            class QueryResponse(BaseModel):
                query: str
                response: str
                domain: str
                quality_score: float
                consciousness_level: str
                processing_time: float
                timestamp: str
                system_status: Dict[str, Any]

            class SystemStatusResponse(BaseModel):
                system_info: Dict[str, Any]
                components: Dict[str, str]
                performance: Dict[str, float]
                errors: int
                warnings: int
                uptime: float

            # Endpoints
            @app.get("/")
            async def root():
                return {
                    "message": "NeuroFusion Master System API",
                    "version": "3.0.0",
                    "status": "running",
                }

            @app.post("/query", response_model=QueryResponse)
            async def process_query(request: QueryRequest):
                """Procesar consulta a través del sistema maestro"""
                try:
                    result = await self.master_system.process_query(
                        query=request.query,
                        context=request.context,
                        domain=request.domain,
                        user_id=request.user_id,
                    )

                    if "error" in result:
                        raise HTTPException(status_code=500, detail=result["error"])

                    return QueryResponse(**result)

                except Exception as e:
                    logger.error(f"Error procesando consulta: {e}")
                    raise HTTPException(status_code=500, detail=str(e))

            @app.get("/status", response_model=SystemStatusResponse)
            async def get_system_status():
                """Obtener estado del sistema"""
                try:
                    status = self.master_system.get_system_status()
                    return SystemStatusResponse(**status)

                except Exception as e:
                    logger.error(f"Error obteniendo estado: {e}")
                    raise HTTPException(status_code=500, detail=str(e))

            @app.get("/components/{component_name}/stats")
            async def get_component_stats(component_name: str):
                """Obtener estadísticas de un componente específico"""
                try:
                    stats = await self.master_system.get_component_stats(component_name)
                    return stats

                except Exception as e:
                    logger.error(f"Error obteniendo stats de {component_name}: {e}")
                    raise HTTPException(status_code=500, detail=str(e))

            @app.post("/shutdown")
            async def shutdown_system():
                """Apagar el sistema"""
                try:
                    await self.master_system.shutdown()
                    return {"message": "Sistema apagado correctamente"}

                except Exception as e:
                    logger.error(f"Error apagando sistema: {e}")
                    raise HTTPException(status_code=500, detail=str(e))

            # Iniciar servidor
            logger.info("🌐 Servidor API iniciado en http://127.0.0.1:8000")
            logger.info("📚 Documentación disponible en http://127.0.0.1:8000/docs")

            config = uvicorn.Config(
                app=app, host="127.0.0.1", port=8000, log_level="info"
            )
            server = uvicorn.Server(config)
            await server.serve()

        except ImportError as e:
            logger.error(f"❌ Error: FastAPI no disponible - {e}")
            logger.info("💡 Instalar con: pip install fastapi uvicorn")
            return

    async def start_interactive_mode(self, config_path: Optional[str] = None):
        """Iniciar modo interactivo"""
        logger.info("💬 Iniciando modo interactivo...")

        # Cargar configuración
        config = self._load_config(config_path)
        config.mode = SystemMode.DEVELOPMENT

        # Inicializar sistema maestro
        self.master_system = await get_master_system(config)

        print("\n🎯 NeuroFusion Master System - Modo Interactivo")
        print("=" * 50)
        print("Comandos disponibles:")
        print("  query <texto> - Procesar consulta")
        print("  status - Mostrar estado del sistema")
        print("  stats <componente> - Estadísticas de componente")
        print("  help - Mostrar ayuda")
        print("  exit - Salir")
        print("=" * 50)

        while True:
            try:
                command = input("\n🤖 NeuroFusion> ").strip()

                if command.lower() in ["exit", "quit", "q"]:
                    break
                elif command.lower() == "help":
                    print(
                        "Comandos: query <texto>, status, stats <componente>, help, exit"
                    )
                elif command.lower() == "status":
                    status = self.master_system.get_system_status()
                    print(f"📊 Estado del Sistema:")
                    print(
                        f"   - Componentes activos: {sum(1 for s in status['components'].values() if s == 'active')}"
                    )
                    print(f"   - Errores: {status['errors']}")
                    print(f"   - Tiempo activo: {status['uptime']:.1f}s")
                elif command.startswith("stats "):
                    component = command[6:].strip()
                    stats = await self.master_system.get_component_stats(component)
                    print(f"📈 Estadísticas de {component}:")
                    print(f"   {stats}")
                elif command.startswith("query "):
                    query = command[6:].strip()
                    print(f"🔄 Procesando: {query}")

                    result = await self.master_system.process_query(query)

                    if "error" not in result:
                        print(f"✅ Respuesta: {result['response']}")
                        print(f"📊 Calidad: {result['quality_score']:.3f}")
                        print(f"🧠 Conciencia: {result['consciousness_level']}")
                        print(f"⏱️  Tiempo: {result['processing_time']:.3f}s")
                    else:
                        print(f"❌ Error: {result['error']}")
                else:
                    print(
                        "❓ Comando no reconocido. Usa 'help' para ver comandos disponibles."
                    )

            except KeyboardInterrupt:
                break
            except Exception as e:
                print(f"❌ Error: {e}")

        print("\n👋 ¡Hasta luego!")

    async def start_demo_mode(self, config_path: Optional[str] = None):
        """Iniciar modo demostración"""
        logger.info("🎭 Iniciando modo demostración...")

        # Cargar configuración
        config = self._load_config(config_path)
        config.mode = SystemMode.DEMO

        # Inicializar sistema maestro
        self.master_system = await get_master_system(config)

        print("\n🎭 NeuroFusion Master System - Modo Demostración")
        print("=" * 50)

        # Consultas de demostración
        demo_queries = [
            {
                "query": "¿Qué es la inteligencia artificial?",
                "domain": "technology",
                "description": "Consulta sobre IA",
            },
            {
                "query": "¿Cuáles son los síntomas de la hipertensión?",
                "domain": "medical",
                "description": "Consulta médica",
            },
            {
                "query": "¿Cómo crear una aplicación web moderna?",
                "domain": "programming",
                "description": "Consulta de programación",
            },
            {
                "query": "¿Cuál es la capital de Francia?",
                "domain": "geography",
                "description": "Consulta geográfica",
            },
            {
                "query": "¿Qué es la fotosíntesis?",
                "domain": "biology",
                "description": "Consulta de biología",
            },
        ]

        for i, demo in enumerate(demo_queries, 1):
            print(f"\n📋 Demostración {i}: {demo['description']}")
            print(f"   Consulta: {demo['query']}")
            print(f"   Dominio: {demo['domain']}")

            try:
                result = await self.master_system.process_query(
                    query=demo["query"], domain=demo["domain"]
                )

                if "error" not in result:
                    print(f"   ✅ Respuesta: {result['response'][:100]}...")
                    print(f"   📊 Calidad: {result['quality_score']:.3f}")
                    print(f"   🧠 Conciencia: {result['consciousness_level']}")
                    print(f"   ⏱️  Tiempo: {result['processing_time']:.3f}s")
                else:
                    print(f"   ❌ Error: {result['error']}")

            except Exception as e:
                print(f"   ❌ Error: {e}")

            await asyncio.sleep(1)  # Pausa entre demostraciones

        # Mostrar estadísticas finales
        print(f"\n📈 Estadísticas Finales:")
        status = self.master_system.get_system_status()
        print(
            f"   - Componentes activos: {sum(1 for s in status['components'].values() if s == 'active')}"
        )
        print(f"   - Errores: {status['errors']}")
        print(
            f"   - Tiempo promedio: {status['performance'].get('avg_processing_time', 0):.3f}s"
        )
        print(
            f"   - Calidad promedio: {status['performance'].get('avg_quality_score', 0):.3f}"
        )

        print(f"\n🎉 ¡Demostración completada!")

    async def start_minimal_system(self, config_path: Optional[str] = None):
        """Iniciar sistema mínimo"""
        logger.info("⚡ Iniciando sistema mínimo...")

        # Cargar configuración
        config = self._load_config(config_path)
        config.mode = SystemMode.DEVELOPMENT
        config.enable_embeddings = False
        config.enable_generation = True
        config.enable_learning = False
        config.enable_consciousness = False
        config.enable_security = False
        config.enable_training = False
        config.enable_branch_tokenizer = False
        config.enable_consolidated_architecture = True

        # Inicializar sistema maestro
        self.master_system = await get_master_system(config)

        logger.info("✅ Sistema mínimo iniciado")

        # Mantener sistema ejecutándose
        self.running = True
        while self.running:
            await asyncio.sleep(1)

    def _load_config(self, config_path: Optional[str] = None) -> MasterSystemConfig:
        """Cargar configuración desde archivo"""

        if config_path and Path(config_path).exists():
            try:
                import json

                with open(config_path, "r") as f:
                    config_data = json.load(f)

                # Crear configuración desde datos
                config = MasterSystemConfig()
                for key, value in config_data.items():
                    if hasattr(config, key):
                        setattr(config, key, value)

                logger.info(f"✅ Configuración cargada desde: {config_path}")
                return config

            except Exception as e:
                logger.warning(f"⚠️ Error cargando configuración: {e}")

        # Configuración por defecto
        return MasterSystemConfig()


async def main():
    """Función principal"""

    parser = argparse.ArgumentParser(
        description="Sistema Maestro NeuroFusion - Iniciador",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Ejemplos de uso:
  python start_master_system.py --mode full
  python start_master_system.py --mode api
  python start_master_system.py --mode interactive
  python start_master_system.py --mode demo
  python start_master_system.py --mode minimal --config config.json
        """,
    )

    parser.add_argument(
        "--mode",
        choices=["full", "api", "interactive", "demo", "minimal"],
        default="interactive",
        help="Modo de operación del sistema",
    )

    parser.add_argument(
        "--config", type=str, help="Ruta al archivo de configuración JSON"
    )

    parser.add_argument(
        "--host",
        type=str,
        default="127.0.0.1",
        help="Host para el servidor API (solo modo api)",
    )

    parser.add_argument(
        "--port",
        type=int,
        default=8000,
        help="Puerto para el servidor API (solo modo api)",
    )

    args = parser.parse_args()

    # Crear gestor del sistema
    manager = MasterSystemManager()

    try:
        # Iniciar según el modo seleccionado
        if args.mode == "full":
            await manager.start_full_system(args.config)
        elif args.mode == "api":
            await manager.start_api_server(args.config)
        elif args.mode == "interactive":
            await manager.start_interactive_mode(args.config)
        elif args.mode == "demo":
            await manager.start_demo_mode(args.config)
        elif args.mode == "minimal":
            await manager.start_minimal_system(args.config)
        else:
            logger.error(f"❌ Modo no válido: {args.mode}")
            return 1

    except KeyboardInterrupt:
        logger.info("🛑 Interrupción del usuario")
    except Exception as e:
        logger.error(f"❌ Error en el sistema: {e}")
        return 1
    finally:
        # Apagado graceful
        await manager._graceful_shutdown()

    return 0


if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)
