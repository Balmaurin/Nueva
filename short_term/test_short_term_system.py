#!/usr/bin/env python3
"""
Sistema de Pruebas para el Módulo de Memoria a Corto Plazo
Pruebas completas para gestión de sesiones, mensajes, análisis semántico y base de datos
"""

import sys
import time
import json
import tempfile
import sqlite3
from pathlib import Path
from typing import Dict, List, Any, Tuple
import logging

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class ShortTermMemoryTestSuite:
    """Suite de pruebas para el módulo de memoria a corto plazo"""

    def __init__(self):
        self.test_results = {}
        self.temp_dir = None
        self.test_db_path = None

    def setup_test_environment(self) -> bool:
        """Configurar entorno de pruebas"""
        try:
            # Crear directorio temporal
            self.temp_dir = Path(tempfile.mkdtemp(prefix="short_term_test_"))
            self.test_db_path = self.temp_dir / "test_memory.db"

            logger.info(f"✅ Entorno de pruebas configurado en: {self.temp_dir}")
            return True

        except Exception as e:
            logger.error(f"❌ Error configurando entorno de pruebas: {e}")
            return False

    def cleanup_test_environment(self):
        """Limpiar entorno de pruebas"""
        try:
            if self.temp_dir and self.temp_dir.exists():
                import shutil

                shutil.rmtree(self.temp_dir)
                logger.info("✅ Entorno de pruebas limpiado")
        except Exception as e:
            logger.error(f"❌ Error limpiando entorno de pruebas: {e}")

    def test_memory_manager_initialization(self) -> Tuple[bool, Dict[str, Any]]:
        """Probar inicialización del gestor de memoria"""
        logger.info("🧪 Probando inicialización del gestor de memoria...")
        results = {}

        try:
            from short_term.short_term_manager import (
                ShortTermMemoryManager,
                MemoryConfig,
            )

            # Probar configuración por defecto
            config = MemoryConfig()
            results["config_default"] = {
                "status": "success",
                "message": "Configuración por defecto creada",
            }

            # Probar configuración personalizada
            custom_config = MemoryConfig(
                max_messages=30, max_tokens=2048, summary_threshold=4000
            )
            results["config_custom"] = {
                "status": "success",
                "message": "Configuración personalizada creada",
            }

            # Probar inicialización del manager
            manager = ShortTermMemoryManager(custom_config)
            results["manager_init"] = {
                "status": "success",
                "message": "Gestor inicializado",
            }

            # Verificar componentes
            if hasattr(manager, "semantic_analyzer"):
                results["semantic_analyzer"] = {
                    "status": "success",
                    "message": "Analizador semántico presente",
                }
            else:
                results["semantic_analyzer"] = {
                    "status": "error",
                    "message": "Analizador semántico no encontrado",
                }

            if hasattr(manager, "summarizer"):
                results["summarizer"] = {
                    "status": "success",
                    "message": "Generador de resúmenes presente",
                }
            else:
                results["summarizer"] = {
                    "status": "error",
                    "message": "Generador de resúmenes no encontrado",
                }

            success = all(r["status"] == "success" for r in results.values())

        except Exception as e:
            logger.error(f"❌ Error en pruebas de inicialización: {e}")
            results["error"] = {"status": "error", "message": str(e)}
            success = False

        return success, results

    def test_session_management(self) -> Tuple[bool, Dict[str, Any]]:
        """Probar gestión de sesiones"""
        logger.info("🧪 Probando gestión de sesiones...")
        results = {}

        try:
            from short_term.short_term_manager import (
                ShortTermMemoryManager,
                MemoryConfig,
            )

            config = MemoryConfig(database_path=str(self.test_db_path))
            manager = ShortTermMemoryManager(config)

            # Probar creación de sesión
            session_id = manager.create_session("usuario_test")
            results["create_session"] = {
                "status": "success",
                "message": f"Sesión creada: {session_id}",
            }

            # Verificar que la sesión existe
            if session_id in manager.sessions:
                results["session_exists"] = {
                    "status": "success",
                    "message": "Sesión existe en memoria",
                }
            else:
                results["session_exists"] = {
                    "status": "error",
                    "message": "Sesión no encontrada en memoria",
                }

            # Probar información de sesión
            session_info = manager.get_session_info(session_id)
            if session_info:
                results["get_session_info"] = {
                    "status": "success",
                    "message": "Información de sesión obtenida",
                }
            else:
                results["get_session_info"] = {
                    "status": "error",
                    "message": "No se pudo obtener información de sesión",
                }

            # Probar listado de sesiones
            sessions = manager.list_sessions("usuario_test")
            if len(sessions) > 0:
                results["list_sessions"] = {
                    "status": "success",
                    "message": f"{len(sessions)} sesiones listadas",
                }
            else:
                results["list_sessions"] = {
                    "status": "error",
                    "message": "No se encontraron sesiones",
                }

            # Probar creación de sesión con ID personalizado
            custom_session_id = "test_session_123"
            custom_session = manager.create_session("usuario_test", custom_session_id)
            if custom_session == custom_session_id:
                results["custom_session_id"] = {
                    "status": "success",
                    "message": "Sesión con ID personalizado creada",
                }
            else:
                results["custom_session_id"] = {
                    "status": "error",
                    "message": "Error con ID personalizado",
                }

            success = all(r["status"] == "success" for r in results.values())

        except Exception as e:
            logger.error(f"❌ Error en pruebas de gestión de sesiones: {e}")
            results["error"] = {"status": "error", "message": str(e)}
            success = False

        return success, results

    def test_message_operations(self) -> Tuple[bool, Dict[str, Any]]:
        """Probar operaciones con mensajes"""
        logger.info("🧪 Probando operaciones con mensajes...")
        results = {}

        try:
            from short_term.short_term_manager import (
                ShortTermMemoryManager,
                MemoryConfig,
            )

            config = MemoryConfig(database_path=str(self.test_db_path))
            manager = ShortTermMemoryManager(config)

            # Crear sesión
            session_id = manager.create_session("usuario_test")

            # Probar añadir mensaje de usuario
            user_message_id = manager.add_message(
                session_id, "user", "Hola, ¿cómo estás?"
            )
            results["add_user_message"] = {
                "status": "success",
                "message": f"Mensaje de usuario añadido: {user_message_id}",
            }

            # Probar añadir mensaje de asistente
            assistant_message_id = manager.add_message(
                session_id, "assistant", "¡Hola! Estoy bien, gracias por preguntar."
            )
            results["add_assistant_message"] = {
                "status": "success",
                "message": f"Mensaje de asistente añadido: {assistant_message_id}",
            }

            # Probar añadir mensaje de sistema
            system_message_id = manager.add_message(
                session_id, "system", "Este es un mensaje del sistema."
            )
            results["add_system_message"] = {
                "status": "success",
                "message": f"Mensaje de sistema añadido: {system_message_id}",
            }

            # Verificar que los mensajes están en la sesión
            if (
                session_id in manager.messages
                and len(manager.messages[session_id]) == 3
            ):
                results["messages_in_session"] = {
                    "status": "success",
                    "message": "Todos los mensajes están en la sesión",
                }
            else:
                results["messages_in_session"] = {
                    "status": "error",
                    "message": "Mensajes no encontrados en la sesión",
                }

            # Probar añadir mensaje con metadatos
            metadata = {"source": "test", "priority": "high"}
            metadata_message_id = manager.add_message(
                session_id, "user", "Mensaje con metadatos", metadata=metadata
            )
            results["add_message_with_metadata"] = {
                "status": "success",
                "message": f"Mensaje con metadatos añadido: {metadata_message_id}",
            }

            # Probar añadir mensaje con tokens específicos
            token_message_id = manager.add_message(
                session_id, "assistant", "Mensaje con tokens específicos", tokens=50
            )
            results["add_message_with_tokens"] = {
                "status": "success",
                "message": f"Mensaje con tokens añadido: {token_message_id}",
            }

            success = all(r["status"] == "success" for r in results.values())

        except Exception as e:
            logger.error(f"❌ Error en pruebas de operaciones con mensajes: {e}")
            results["error"] = {"status": "error", "message": str(e)}
            success = False

        return success, results

    def test_context_retrieval(self) -> Tuple[bool, Dict[str, Any]]:
        """Probar recuperación de contexto"""
        logger.info("🧪 Probando recuperación de contexto...")
        results = {}

        try:
            from short_term.short_term_manager import (
                ShortTermMemoryManager,
                MemoryConfig,
            )

            config = MemoryConfig(database_path=str(self.test_db_path))
            manager = ShortTermMemoryManager(config)

            # Crear sesión y añadir mensajes
            session_id = manager.create_session("usuario_test")

            messages = [
                ("user", "¿Qué es la inteligencia artificial?"),
                (
                    "assistant",
                    "La inteligencia artificial es un campo de la informática que busca crear sistemas capaces de realizar tareas que normalmente requieren inteligencia humana.",
                ),
                ("user", "¿Cuáles son los tipos principales?"),
                (
                    "assistant",
                    "Los tipos principales incluyen: 1) IA débil (especializada), 2) IA fuerte (general), 3) Machine Learning, 4) Deep Learning.",
                ),
                ("system", "Información sobre IA proporcionada."),
            ]

            for role, content in messages:
                manager.add_message(session_id, role, content)

            # Probar obtención de contexto completo
            context = manager.get_context(session_id)
            if len(context) == len(messages):
                results["get_full_context"] = {
                    "status": "success",
                    "message": f"Contexto completo obtenido: {len(context)} mensajes",
                }
            else:
                results["get_full_context"] = {
                    "status": "error",
                    "message": f"Contexto incompleto: {len(context)} vs {len(messages)}",
                }

            # Probar obtención de contexto sin mensajes de sistema
            context_no_system = manager.get_context(session_id, include_system=False)
            system_messages = sum(
                1 for msg in context_no_system if msg["role"] == "system"
            )
            if system_messages == 0:
                results["context_no_system"] = {
                    "status": "success",
                    "message": "Contexto sin mensajes de sistema obtenido",
                }
            else:
                results["context_no_system"] = {
                    "status": "error",
                    "message": f"Mensajes de sistema encontrados: {system_messages}",
                }

            # Probar obtención de contexto con límite de tokens
            context_limited = manager.get_context(session_id, max_tokens=100)
            if len(context_limited) < len(context):
                results["context_limited_tokens"] = {
                    "status": "success",
                    "message": "Contexto con límite de tokens obtenido",
                }
            else:
                results["context_limited_tokens"] = {
                    "status": "error",
                    "message": "Límite de tokens no aplicado",
                }

            # Probar búsqueda semántica
            context_semantic = manager.get_context(
                session_id, semantic_search="machine learning"
            )
            if context_semantic:
                results["context_semantic_search"] = {
                    "status": "success",
                    "message": "Búsqueda semántica funcionando",
                }
            else:
                results["context_semantic_search"] = {
                    "status": "error",
                    "message": "Búsqueda semántica falló",
                }

            success = all(r["status"] == "success" for r in results.values())

        except Exception as e:
            logger.error(f"❌ Error en pruebas de recuperación de contexto: {e}")
            results["error"] = {"status": "error", "message": str(e)}
            success = False

        return success, results

    def test_semantic_analysis(self) -> Tuple[bool, Dict[str, Any]]:
        """Probar análisis semántico"""
        logger.info("🧪 Probando análisis semántico...")
        results = {}

        try:
            from short_term.short_term_manager import (
                ShortTermMemoryManager,
                MemoryConfig,
            )

            config = MemoryConfig(database_path=str(self.test_db_path))
            manager = ShortTermMemoryManager(config)

            # Probar cálculo de similitud
            similarity = manager.semantic_analyzer.calculate_similarity(
                "Hola, ¿cómo estás?", "Hola, ¿qué tal?"
            )
            if 0 <= similarity <= 1:
                results["calculate_similarity"] = {
                    "status": "success",
                    "message": f"Similitud calculada: {similarity:.3f}",
                }
            else:
                results["calculate_similarity"] = {
                    "status": "error",
                    "message": f"Similitud fuera de rango: {similarity}",
                }

            # Probar obtención de embedding
            embedding = manager.semantic_analyzer.get_embedding(
                "Texto de prueba para embedding"
            )
            if isinstance(embedding, list) and len(embedding) > 0:
                results["get_embedding"] = {
                    "status": "success",
                    "message": f"Embedding obtenido: {len(embedding)} dimensiones",
                }
            else:
                results["get_embedding"] = {
                    "status": "error",
                    "message": "Error obteniendo embedding",
                }

            # Probar búsqueda de mensajes similares
            session_id = manager.create_session("usuario_test")
            manager.add_message(
                session_id, "user", "¿Qué es la inteligencia artificial?"
            )
            manager.add_message(
                session_id, "assistant", "La IA es un campo de la informática."
            )
            manager.add_message(
                session_id, "user", "¿Cómo funciona el machine learning?"
            )

            similar_messages = manager.search_messages(
                session_id, "inteligencia artificial"
            )
            if similar_messages:
                results["search_similar_messages"] = {
                    "status": "success",
                    "message": f"{len(similar_messages)} mensajes similares encontrados",
                }
            else:
                results["search_similar_messages"] = {
                    "status": "error",
                    "message": "No se encontraron mensajes similares",
                }

            # Probar similitud entre textos muy diferentes
            low_similarity = manager.semantic_analyzer.calculate_similarity(
                "Hola mundo", "Fórmula matemática compleja con variables"
            )
            if low_similarity < 0.5:
                results["low_similarity"] = {
                    "status": "success",
                    "message": f"Baja similitud detectada: {low_similarity:.3f}",
                }
            else:
                results["low_similarity"] = {
                    "status": "error",
                    "message": f"Similitud inesperadamente alta: {low_similarity:.3f}",
                }

            success = all(r["status"] == "success" for r in results.values())

        except Exception as e:
            logger.error(f"❌ Error en pruebas de análisis semántico: {e}")
            results["error"] = {"status": "error", "message": str(e)}
            success = False

        return success, results

    def test_summarization(self) -> Tuple[bool, Dict[str, Any]]:
        """Probar generación de resúmenes"""
        logger.info("🧪 Probando generación de resúmenes...")
        results = {}

        try:
            from short_term.short_term_manager import (
                ShortTermMemoryManager,
                MemoryConfig,
                MemoryMessage,
            )

            config = MemoryConfig(database_path=str(self.test_db_path))
            manager = ShortTermMemoryManager(config)

            # Crear mensajes de prueba
            test_messages = [
                MemoryMessage(
                    id="msg1",
                    role="user",
                    content="¿Qué es la inteligencia artificial?",
                    tokens=10,
                    timestamp=time.time(),
                    session_id="test",
                    importance_score=1.0,
                ),
                MemoryMessage(
                    id="msg2",
                    role="assistant",
                    content="La IA es un campo de la informática que busca crear sistemas inteligentes.",
                    tokens=15,
                    timestamp=time.time(),
                    session_id="test",
                    importance_score=1.2,
                ),
                MemoryMessage(
                    id="msg3",
                    role="user",
                    content="¿Cuáles son los tipos principales?",
                    tokens=8,
                    timestamp=time.time(),
                    session_id="test",
                    importance_score=1.0,
                ),
                MemoryMessage(
                    id="msg4",
                    role="assistant",
                    content="Los tipos principales son: IA débil, IA fuerte, Machine Learning y Deep Learning.",
                    tokens=20,
                    timestamp=time.time(),
                    session_id="test",
                    importance_score=1.3,
                ),
            ]

            # Probar generación de resumen
            summary = manager.summarizer.generate_summary(test_messages)
            if summary and len(summary) > 0:
                results["generate_summary"] = {
                    "status": "success",
                    "message": f"Resumen generado: {summary}",
                }
            else:
                results["generate_summary"] = {
                    "status": "error",
                    "message": "No se pudo generar resumen",
                }

            # Probar resumen con mensajes vacíos
            empty_summary = manager.summarizer.generate_summary([])
            if empty_summary == "":
                results["empty_summary"] = {
                    "status": "success",
                    "message": "Resumen vacío manejado correctamente",
                }
            else:
                results["empty_summary"] = {
                    "status": "error",
                    "message": "Resumen vacío no manejado",
                }

            # Probar extracción de temas
            topics = manager.summarizer._extract_topics(
                [msg.content for msg in test_messages]
            )
            if topics and len(topics) > 0:
                results["extract_topics"] = {
                    "status": "success",
                    "message": f"Temas extraídos: {topics}",
                }
            else:
                results["extract_topics"] = {
                    "status": "error",
                    "message": "No se pudieron extraer temas",
                }

            # Probar resumen por rol
            user_messages = [msg for msg in test_messages if msg.role == "user"]
            user_summary = manager.summarizer._summarize_by_role(
                user_messages, "Usuario"
            )
            if user_summary:
                results["summarize_by_role"] = {
                    "status": "success",
                    "message": f"Resumen por rol: {user_summary}",
                }
            else:
                results["summarize_by_role"] = {
                    "status": "error",
                    "message": "Error en resumen por rol",
                }

            success = all(r["status"] == "success" for r in results.values())

        except Exception as e:
            logger.error(f"❌ Error en pruebas de generación de resúmenes: {e}")
            results["error"] = {"status": "error", "message": str(e)}
            success = False

        return success, results

    def test_database_operations(self) -> Tuple[bool, Dict[str, Any]]:
        """Probar operaciones de base de datos"""
        logger.info("🧪 Probando operaciones de base de datos...")
        results = {}

        try:
            from short_term.short_term_manager import (
                ShortTermMemoryManager,
                MemoryConfig,
            )

            config = MemoryConfig(database_path=str(self.test_db_path))
            manager = ShortTermMemoryManager(config)

            # Verificar que la base de datos se creó
            if manager.db_path.exists():
                results["database_created"] = {
                    "status": "success",
                    "message": "Base de datos creada",
                }
            else:
                results["database_created"] = {
                    "status": "error",
                    "message": "Base de datos no creada",
                }

            # Probar inserción y recuperación de sesión
            session_id = manager.create_session("usuario_test")

            # Verificar en base de datos
            with sqlite3.connect(manager.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute(
                    "SELECT * FROM sessions WHERE session_id = ?", (session_id,)
                )
                session_row = cursor.fetchone()

                if session_row:
                    results["session_in_db"] = {
                        "status": "success",
                        "message": "Sesión guardada en base de datos",
                    }
                else:
                    results["session_in_db"] = {
                        "status": "error",
                        "message": "Sesión no encontrada en base de datos",
                    }

            # Probar inserción y recuperación de mensaje
            message_id = manager.add_message(
                session_id, "user", "Mensaje de prueba para DB"
            )

            # Verificar en base de datos
            with sqlite3.connect(manager.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT * FROM messages WHERE id = ?", (message_id,))
                message_row = cursor.fetchone()

                if message_row:
                    results["message_in_db"] = {
                        "status": "success",
                        "message": "Mensaje guardado en base de datos",
                    }
                else:
                    results["message_in_db"] = {
                        "status": "error",
                        "message": "Mensaje no encontrado en base de datos",
                    }

            # Probar eliminación de sesión
            manager.delete_session(session_id)

            # Verificar eliminación
            with sqlite3.connect(manager.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute(
                    "SELECT COUNT(*) FROM sessions WHERE session_id = ?", (session_id,)
                )
                session_count = cursor.fetchone()[0]

                cursor.execute(
                    "SELECT COUNT(*) FROM messages WHERE session_id = ?", (session_id,)
                )
                message_count = cursor.fetchone()[0]

                if session_count == 0 and message_count == 0:
                    results["session_deletion"] = {
                        "status": "success",
                        "message": "Sesión y mensajes eliminados de DB",
                    }
                else:
                    results["session_deletion"] = {
                        "status": "error",
                        "message": "Error eliminando de DB",
                    }

            success = all(r["status"] == "success" for r in results.values())

        except Exception as e:
            logger.error(f"❌ Error en pruebas de base de datos: {e}")
            results["error"] = {"status": "error", "message": str(e)}
            success = False

        return success, results

    def test_memory_limits(self) -> Tuple[bool, Dict[str, Any]]:
        """Probar límites de memoria"""
        logger.info("🧪 Probando límites de memoria...")
        results = {}

        try:
            from short_term.short_term_manager import (
                ShortTermMemoryManager,
                MemoryConfig,
            )

            # Configuración con límites pequeños para pruebas
            config = MemoryConfig(
                max_messages=3, max_tokens=100, database_path=str(self.test_db_path)
            )
            manager = ShortTermMemoryManager(config)

            # Crear sesión
            session_id = manager.create_session("usuario_test")

            # Añadir mensajes hasta alcanzar el límite
            for i in range(5):
                manager.add_message(session_id, "user", f"Mensaje número {i+1}")

            # Verificar que no se excedió el límite de mensajes
            message_count = len(manager.messages[session_id])
            if message_count <= config.max_messages:
                results["message_limit"] = {
                    "status": "success",
                    "message": f"Límite de mensajes respetado: {message_count}",
                }
            else:
                results["message_limit"] = {
                    "status": "error",
                    "message": f"Límite de mensajes excedido: {message_count}",
                }

            # Verificar límite de tokens
            session = manager.sessions[session_id]
            if session.total_tokens <= config.max_tokens:
                results["token_limit"] = {
                    "status": "success",
                    "message": f"Límite de tokens respetado: {session.total_tokens}",
                }
            else:
                results["token_limit"] = {
                    "status": "error",
                    "message": f"Límite de tokens excedido: {session.total_tokens}",
                }

            # Probar limpieza de sesión
            manager.clear_session(session_id)
            if len(manager.messages[session_id]) == 0:
                results["clear_session"] = {
                    "status": "success",
                    "message": "Sesión limpiada correctamente",
                }
            else:
                results["clear_session"] = {
                    "status": "error",
                    "message": "Error limpiando sesión",
                }

            success = all(r["status"] == "success" for r in results.values())

        except Exception as e:
            logger.error(f"❌ Error en pruebas de límites de memoria: {e}")
            results["error"] = {"status": "error", "message": str(e)}
            success = False

        return success, results

    def test_backup_and_export(self) -> Tuple[bool, Dict[str, Any]]:
        """Probar respaldo y exportación"""
        logger.info("🧪 Probando respaldo y exportación...")
        results = {}

        try:
            from short_term.short_term_manager import (
                ShortTermMemoryManager,
                MemoryConfig,
            )

            config = MemoryConfig(database_path=str(self.test_db_path))
            manager = ShortTermMemoryManager(config)

            # Crear datos de prueba
            session_id = manager.create_session("usuario_test")
            manager.add_message(session_id, "user", "Mensaje de prueba para respaldo")
            manager.add_message(session_id, "assistant", "Respuesta de prueba")

            # Probar respaldo
            backup_path = str(self.temp_dir / "test_backup.json")
            manager.backup_memory(backup_path)

            if Path(backup_path).exists():
                results["backup_creation"] = {
                    "status": "success",
                    "message": "Respaldo creado correctamente",
                }
            else:
                results["backup_creation"] = {
                    "status": "error",
                    "message": "Error creando respaldo",
                }

            # Probar respaldo comprimido
            compressed_backup_path = str(
                self.temp_dir / "test_backup_compressed.json.gz"
            )
            manager.config.compression_enabled = True
            manager.backup_memory(compressed_backup_path)

            if Path(compressed_backup_path).exists():
                results["compressed_backup"] = {
                    "status": "success",
                    "message": "Respaldo comprimido creado",
                }
            else:
                results["compressed_backup"] = {
                    "status": "error",
                    "message": "Error creando respaldo comprimido",
                }

            # Probar exportación de sesión
            from short_term import export_session_data

            export_path = str(self.temp_dir / "test_export.json")
            export_success = export_session_data(session_id, export_path, manager)

            if export_success and Path(export_path).exists():
                results["session_export"] = {
                    "status": "success",
                    "message": "Sesión exportada correctamente",
                }
            else:
                results["session_export"] = {
                    "status": "error",
                    "message": "Error exportando sesión",
                }

            success = all(r["status"] == "success" for r in results.values())

        except Exception as e:
            logger.error(f"❌ Error en pruebas de respaldo y exportación: {e}")
            results["error"] = {"status": "error", "message": str(e)}
            success = False

        return success, results

    def test_package_functions(self) -> Tuple[bool, Dict[str, Any]]:
        """Probar funciones del paquete"""
        logger.info("🧪 Probando funciones del paquete...")
        results = {}

        try:
            import short_term

            # Probar información del módulo
            info = short_term.get_module_info()
            if info and "name" in info:
                results["get_module_info"] = {
                    "status": "success",
                    "message": "Información del módulo obtenida",
                }
            else:
                results["get_module_info"] = {
                    "status": "error",
                    "message": "Error obteniendo información",
                }

            # Probar verificación de dependencias
            deps = short_term.check_dependencies()
            if "available" in deps and "missing" in deps:
                results["check_dependencies"] = {
                    "status": "success",
                    "message": "Dependencias verificadas",
                }
            else:
                results["check_dependencies"] = {
                    "status": "error",
                    "message": "Error verificando dependencias",
                }

            # Probar configuración del sistema
            setup_success = short_term.setup_memory_system()
            if setup_success:
                results["setup_memory_system"] = {
                    "status": "success",
                    "message": "Sistema de memoria configurado",
                }
            else:
                results["setup_memory_system"] = {
                    "status": "error",
                    "message": "Error configurando sistema",
                }

            # Probar creación de sesión desde paquete
            session_id = short_term.create_session("usuario_paquete")
            if session_id:
                results["create_session_package"] = {
                    "status": "success",
                    "message": f"Sesión creada desde paquete: {session_id}",
                }
            else:
                results["create_session_package"] = {
                    "status": "error",
                    "message": "Error creando sesión desde paquete",
                }

            # Probar añadir mensaje desde paquete
            message_id = short_term.add_message_to_session(
                session_id, "user", "Mensaje desde paquete"
            )
            if message_id:
                results["add_message_package"] = {
                    "status": "success",
                    "message": f"Mensaje añadido desde paquete: {message_id}",
                }
            else:
                results["add_message_package"] = {
                    "status": "error",
                    "message": "Error añadiendo mensaje desde paquete",
                }

            success = all(r["status"] == "success" for r in results.values())

        except Exception as e:
            logger.error(f"❌ Error en pruebas del paquete: {e}")
            results["error"] = {"status": "error", "message": str(e)}
            success = False

        return success, results

    def test_error_handling(self) -> Tuple[bool, Dict[str, Any]]:
        """Probar manejo de errores"""
        logger.info("🧪 Probando manejo de errores...")
        results = {}

        try:
            from short_term.short_term_manager import (
                ShortTermMemoryManager,
                MemoryConfig,
            )

            config = MemoryConfig(database_path=str(self.test_db_path))
            manager = ShortTermMemoryManager(config)

            # Probar añadir mensaje a sesión inexistente
            try:
                manager.add_message("sesion_inexistente", "user", "Mensaje")
                results["nonexistent_session"] = {
                    "status": "error",
                    "message": "Debería haber fallado",
                }
            except ValueError:
                results["nonexistent_session"] = {
                    "status": "success",
                    "message": "Error manejado correctamente",
                }

            # Probar obtener contexto de sesión inexistente
            context = manager.get_context("sesion_inexistente")
            if context == []:
                results["nonexistent_context"] = {
                    "status": "success",
                    "message": "Contexto vacío para sesión inexistente",
                }
            else:
                results["nonexistent_context"] = {
                    "status": "error",
                    "message": "Debería haber devuelto lista vacía",
                }

            # Probar información de sesión inexistente
            info = manager.get_session_info("sesion_inexistente")
            if info is None:
                results["nonexistent_info"] = {
                    "status": "success",
                    "message": "Info None para sesión inexistente",
                }
            else:
                results["nonexistent_info"] = {
                    "status": "error",
                    "message": "Debería haber devuelto None",
                }

            # Probar similitud con texto vacío
            similarity = manager.semantic_analyzer.calculate_similarity(
                "", "texto normal"
            )
            if similarity == 0.0:
                results["empty_text_similarity"] = {
                    "status": "success",
                    "message": "Similitud 0 para texto vacío",
                }
            else:
                results["empty_text_similarity"] = {
                    "status": "error",
                    "message": "Debería haber devuelto 0",
                }

            success = all(r["status"] == "success" for r in results.values())

        except Exception as e:
            logger.error(f"❌ Error en pruebas de manejo de errores: {e}")
            results["error"] = {"status": "error", "message": str(e)}
            success = False

        return success, results

    def test_integration(self) -> Tuple[bool, Dict[str, Any]]:
        """Probar integración completa"""
        logger.info("🧪 Probando integración completa...")
        results = {}

        try:
            from short_term.short_term_manager import (
                ShortTermMemoryManager,
                MemoryConfig,
            )

            config = MemoryConfig(database_path=str(self.test_db_path))
            manager = ShortTermMemoryManager(config)

            # Flujo completo: crear sesión -> añadir mensajes -> obtener contexto -> buscar -> resumir

            # 1. Crear sesión
            session_id = manager.create_session("usuario_integracion")
            results["create_session"] = {
                "status": "success",
                "message": f"Sesión creada: {session_id}",
            }

            # 2. Añadir mensajes
            messages = [
                ("user", "¿Qué es el machine learning?"),
                (
                    "assistant",
                    "Machine Learning es una rama de la IA que permite a las computadoras aprender sin ser programadas explícitamente.",
                ),
                ("user", "¿Cuáles son los tipos principales?"),
                (
                    "assistant",
                    "Los tipos principales son: Supervisado, No supervisado y Reforzamiento.",
                ),
                ("user", "¿Puedes darme un ejemplo de ML supervisado?"),
                (
                    "assistant",
                    "Un ejemplo es la clasificación de emails como spam o no spam usando datos etiquetados.",
                ),
            ]

            for role, content in messages:
                message_id = manager.add_message(session_id, role, content)
                if message_id:
                    results[f"add_message_{role}"] = {
                        "status": "success",
                        "message": f"Mensaje {role} añadido",
                    }
                else:
                    results[f"add_message_{role}"] = {
                        "status": "error",
                        "message": f"Error añadiendo mensaje {role}",
                    }

            # 3. Obtener contexto
            context = manager.get_context(session_id)
            if len(context) == len(messages):
                results["get_context"] = {
                    "status": "success",
                    "message": f"Contexto obtenido: {len(context)} mensajes",
                }
            else:
                results["get_context"] = {
                    "status": "error",
                    "message": f"Contexto incompleto: {len(context)}",
                }

            # 4. Búsqueda semántica
            similar = manager.search_messages(session_id, "aprendizaje automático")
            if similar:
                results["semantic_search"] = {
                    "status": "success",
                    "message": f"Búsqueda semántica: {len(similar)} resultados",
                }
            else:
                results["semantic_search"] = {
                    "status": "error",
                    "message": "Búsqueda semántica falló",
                }

            # 5. Generar resumen
            summary = manager.summarizer.generate_summary(manager.messages[session_id])
            if summary:
                results["generate_summary"] = {
                    "status": "success",
                    "message": f"Resumen generado: {summary[:50]}...",
                }
            else:
                results["generate_summary"] = {
                    "status": "error",
                    "message": "Error generando resumen",
                }

            # 6. Información de sesión
            info = manager.get_session_info(session_id)
            if info and info["message_count"] == len(messages):
                results["session_info"] = {
                    "status": "success",
                    "message": "Información de sesión correcta",
                }
            else:
                results["session_info"] = {
                    "status": "error",
                    "message": "Información de sesión incorrecta",
                }

            success = all(r["status"] == "success" for r in results.values())

        except Exception as e:
            logger.error(f"❌ Error en pruebas de integración: {e}")
            results["error"] = {"status": "error", "message": str(e)}
            success = False

        return success, results

    def run_all_tests(self) -> Dict[str, Any]:
        """Ejecutar todas las pruebas"""
        logger.info("🚀 INICIANDO PRUEBAS DEL SISTEMA DE MEMORIA A CORTO PLAZO")
        logger.info("=" * 70)

        start_time = time.time()

        # Configurar entorno
        if not self.setup_test_environment():
            return {"error": "No se pudo configurar el entorno de pruebas"}

        # Lista de pruebas
        test_functions = [
            ("memory_manager_initialization", self.test_memory_manager_initialization),
            ("session_management", self.test_session_management),
            ("message_operations", self.test_message_operations),
            ("context_retrieval", self.test_context_retrieval),
            ("semantic_analysis", self.test_semantic_analysis),
            ("summarization", self.test_summarization),
            ("database_operations", self.test_database_operations),
            ("memory_limits", self.test_memory_limits),
            ("backup_and_export", self.test_backup_and_export),
            ("package_functions", self.test_package_functions),
            ("error_handling", self.test_error_handling),
            ("integration", self.test_integration),
        ]

        # Ejecutar pruebas
        for test_name, test_func in test_functions:
            logger.info(f"\n--- {test_name.upper()} ---")
            try:
                success, results = test_func()
                self.test_results[test_name] = (success, results)

                if success:
                    logger.info(f"✅ {test_name} - EXITOSO")
                else:
                    logger.error(f"❌ {test_name} - FALLIDO")

            except Exception as e:
                logger.error(f"❌ {test_name} - ERROR: {e}")
                self.test_results[test_name] = (False, {"error": str(e)})

        # Generar reporte
        end_time = time.time()
        duration = end_time - start_time

        report = self.generate_test_report(duration)

        # Limpiar entorno
        self.cleanup_test_environment()

        return report

    def generate_test_report(self, duration: float) -> Dict[str, Any]:
        """Generar reporte de pruebas"""
        total_tests = len(self.test_results)
        successful_tests = sum(
            1 for success, _ in self.test_results.values() if success
        )
        failed_tests = total_tests - successful_tests

        report = {
            "test_summary": {
                "total_tests": total_tests,
                "successful_tests": successful_tests,
                "failed_tests": failed_tests,
                "success_rate": (
                    (successful_tests / total_tests * 100) if total_tests > 0 else 0
                ),
                "duration_seconds": round(duration, 2),
            },
            "overall_status": failed_tests == 0,
            "test_results": self.test_results,
            "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
            "module": "short_term",
        }

        # Guardar reporte
        report_file = Path("short_term_test_report.json")
        with open(report_file, "w", encoding="utf-8") as f:
            json.dump(report, f, indent=2, ensure_ascii=False)

        logger.info(f"\n📋 RESUMEN DE PRUEBAS:")
        logger.info(f"  Total de pruebas: {total_tests}")
        logger.info(f"  Exitosas: {successful_tests}")
        logger.info(f"  Fallidas: {failed_tests}")
        logger.info(f"  Tasa de éxito: {report['test_summary']['success_rate']:.1f}%")
        logger.info(f"  Duración: {duration:.2f} segundos")
        logger.info(
            f"  Estado general: {'✅ EXITOSO' if report['overall_status'] else '❌ FALLIDO'}"
        )
        logger.info(f"  Reporte guardado en: {report_file}")

        return report


def main():
    """Función principal"""
    test_suite = ShortTermMemoryTestSuite()
    report = test_suite.run_all_tests()

    if report.get("overall_status"):
        print("\n🎉 ¡Todas las pruebas pasaron exitosamente!")
        return 0
    else:
        print("\n⚠️  Algunas pruebas fallaron. Revisa el reporte para más detalles.")
        return 1


if __name__ == "__main__":
    sys.exit(main())
