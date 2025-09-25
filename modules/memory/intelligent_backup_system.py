"""
Sistema de Respaldo Inteligente para Shaili AI
==============================================

Sistema inteligente de respaldo y recuperación de datos que proporciona
respuestas de respaldo cuando el sistema principal no está disponible.
"""

import logging
import json
import os
import time
from typing import Dict, Any, List, Optional, Tuple
from datetime import datetime, timedelta
import numpy as np

# Agregar path para importar módulos
import sys

sys.path.append(os.path.join(os.path.dirname(__file__), "../.."))

try:
    from modules.core.model.simple_shaili import SimpleShailiModel
    from modules.ai.text_processor import TextProcessor
    from modules.ai.semantic_analyzer import SemanticAnalyzer

    LLM_AVAILABLE = True
except ImportError as e:
    logging.error(f"Error importando módulos: {e}")
    LLM_AVAILABLE = False

logger = logging.getLogger(__name__)


class IntelligentBackupSystem:
    """
    Sistema inteligente de respaldo que proporciona respuestas de respaldo
    cuando el sistema principal falla o no está disponible
    """

    def __init__(self, backup_data_path: str = "data/backup/"):
        self.logger = logging.getLogger(__name__)
        self.backup_data_path = backup_data_path
        self.knowledge_base = {}
        self.response_patterns = {}
        self.query_history = []
        self.backup_metrics = {
            "total_queries": 0,
            "successful_responses": 0,
            "failed_responses": 0,
            "average_confidence": 0.0,
        }

        self._initialize_backup_system()

    def _initialize_backup_system(self):
        """Inicializar sistema de respaldo con datos reales"""
        try:
            # Crear directorio de respaldo si no existe
            os.makedirs(self.backup_data_path, exist_ok=True)

            # Cargar base de conocimiento de respaldo desde archivos reales
            self._load_backup_knowledge_base()

            # Cargar patrones de respuesta desde archivos reales
            self._load_response_patterns()

            self.logger.info("✅ Sistema de respaldo inteligente inicializado")

        except Exception as e:
            self.logger.error(f"❌ Error inicializando sistema de respaldo: {e}")

    def _load_backup_knowledge_base(self):
        """Cargar base de conocimiento de respaldo desde archivos reales"""
        try:
            knowledge_file = os.path.join(self.backup_data_path, "knowledge_base.json")

            if os.path.exists(knowledge_file):
                with open(knowledge_file, "r", encoding="utf-8") as f:
                    self.knowledge_base = json.load(f)
                self.logger.info(
                    f"Base de conocimiento cargada: {len(self.knowledge_base)} entradas"
                )
            else:
                # Crear base de conocimiento básica si no existe
                self.knowledge_base = self._create_basic_knowledge_base()
                self._save_knowledge_base()

        except Exception as e:
            self.logger.error(f"Error cargando base de conocimiento: {e}")
            self.knowledge_base = self._create_basic_knowledge_base()

    def _create_basic_knowledge_base(self) -> Dict[str, Any]:
        """Crear base de conocimiento básica real"""
        return {
            "greetings": {
                "patterns": ["hola", "buenos días", "buenas tardes", "saludos"],
                "responses": [
                    "¡Hola! Soy Sheily AI. ¿En qué puedo ayudarte?",
                    "¡Buenos días! Estoy aquí para asistirte.",
                    "¡Hola! ¿Cómo puedo ayudarte hoy?",
                ],
            },
            "model_info": {
                "patterns": ["modelo", "capacidades", "qué puedes hacer"],
                "responses": [
                    "Soy Sheily AI, un sistema de IA avanzado con capacidades de chat y generación de archivos LoRA.",
                    "Puedo ayudarte con consultas, generar respuestas y crear archivos LoRA para entrenamiento.",
                    "Mis capacidades incluyen procesamiento de lenguaje natural y asistencia inteligente.",
                ],
            },
            "training": {
                "patterns": ["entrenamiento", "lora", "ramas especializadas"],
                "responses": [
                    "El sistema incluye 32 ramas especializadas que se entrenan usando archivos LoRA.",
                    "Puedo generar archivos LoRA para entrenar modelos especializados en diferentes dominios.",
                    "El entrenamiento se realiza usando el modelo de 16-bit con adaptadores LoRA.",
                ],
            },
        }

    def _save_knowledge_base(self):
        """Guardar base de conocimiento en un archivo JSON"""
        try:
            knowledge_file = os.path.join(self.backup_data_path, "knowledge_base.json")
            with open(knowledge_file, "w", encoding="utf-8") as f:
                json.dump(self.knowledge_base, f, indent=4, ensure_ascii=False)
            self.logger.info(
                f"Base de conocimiento guardada: {len(self.knowledge_base)} entradas"
            )
        except Exception as e:
            self.logger.error(f"Error guardando base de conocimiento: {e}")

    def _load_response_patterns(self):
        """Cargar patrones de respuesta desde archivos reales"""
        try:
            patterns_file = os.path.join(
                self.backup_data_path, "response_patterns.json"
            )

            if os.path.exists(patterns_file):
                with open(patterns_file, "r", encoding="utf-8") as f:
                    self.response_patterns = json.load(f)
                self.logger.info(
                    f"Patrones de respuesta cargados: {len(self.response_patterns)} patrones"
                )
            else:
                # Crear patrones de respuesta básicos si no existen
                self.response_patterns = self._create_basic_response_patterns()
                self._save_response_patterns()

        except Exception as e:
            self.logger.error(f"Error cargando patrones de respuesta: {e}")
            self.response_patterns = self._create_basic_response_patterns()

    def _create_basic_response_patterns(self) -> Dict[str, Any]:
        """Crear patrones de respuesta básicos reales"""
        return {
            "error_general": {
                "patterns": ["error", "problema", "fallo", "problemas"],
                "responses": [
                    "Lo siento, hubo un error en el procesamiento. Déjame intentar ayudarte de otra manera.",
                    "Parece que hay un problema técnico. Te ayudo con una respuesta alternativa.",
                    "El sistema principal no está disponible. Te proporciono asistencia básica.",
                ],
            },
            "unavailable_service": {
                "patterns": ["servicio", "disponible", "ocupado", "no disponible"],
                "responses": [
                    "El servicio no está disponible en este momento. ¿Puedo ayudarte con algo más?",
                    "Hay un problema temporal. Te ayudo con información básica.",
                    "El sistema está ocupado. Te respondo con lo que puedo.",
                ],
            },
        }

    def _save_response_patterns(self):
        """Guardar patrones de respuesta en un archivo JSON"""
        try:
            patterns_file = os.path.join(
                self.backup_data_path, "response_patterns.json"
            )
            with open(patterns_file, "w", encoding="utf-8") as f:
                json.dump(self.response_patterns, f, indent=4, ensure_ascii=False)
            self.logger.info(
                f"Patrones de respuesta guardados: {len(self.response_patterns)} patrones"
            )
        except Exception as e:
            self.logger.error(f"Error guardando patrones de respuesta: {e}")

    def generate_backup_response(
        self,
        query: str,
        context: Optional[Dict[str, Any]] = None,
        error_type: str = "general",
    ) -> Dict[str, Any]:
        """
        Genera una respuesta de respaldo usando el modelo principal real

        Args:
            query: Consulta del usuario
            context: Contexto adicional
            error_type: Tipo de error que activó el respaldo

        Returns:
            Dict con la respuesta y metadatos
        """
        try:
            start_time = datetime.now()

            # Intentar con el modelo principal real
            if self.llm_model:
                # Generar respuesta con el modelo real
                response = self.llm_model.generate_text(
                    prompt=query, max_length=512, temperature=0.7, top_p=0.9
                )

                # Procesar respuesta
                if self.text_processor:
                    text_analysis = self.text_processor.analyze_text(response)
                    word_count = text_analysis.word_count
                else:
                    word_count = len(response.split())

                processing_time = (datetime.now() - start_time).total_seconds()

                return {
                    "success": True,
                    "response": response,
                    "source": "main_model_backup",
                    "error_type": error_type,
                    "processing_time": processing_time,
                    "word_count": word_count,
                    "confidence": 0.8,
                    "metadata": {
                        "backup_used": True,
                        "model_used": "shaili-personal-model",
                        "quantization": "4bit",
                    },
                }

            # Si no hay modelo, usar respuestas predefinidas
            else:
                import random

                backup_response = random.choice(
                    self.backup_responses.get(
                        error_type, self.backup_responses["error"]
                    )
                )

                return {
                    "success": True,
                    "response": f"{backup_response} Tu consulta fue: '{query}'. Te ayudo cuando el sistema esté disponible.",
                    "source": "predefined_backup",
                    "error_type": error_type,
                    "processing_time": 0.1,
                    "word_count": len(query.split()),
                    "confidence": 0.3,
                    "metadata": {
                        "backup_used": True,
                        "model_used": "predefined",
                        "quantization": "none",
                    },
                }

        except Exception as e:
            logger.error(f"❌ Error en sistema de respaldo: {e}")

            # Respuesta de emergencia
            return {
                "success": False,
                "response": "Error crítico en el sistema de respaldo. Por favor, intenta más tarde.",
                "source": "emergency",
                "error_type": error_type,
                "processing_time": 0.0,
                "word_count": 0,
                "confidence": 0.0,
                "metadata": {
                    "backup_used": True,
                    "model_used": "emergency",
                    "error": str(e),
                },
            }

    def analyze_query_intent(self, query: str) -> Dict[str, Any]:
        """Analizar la intención de la consulta usando componentes reales"""
        try:
            if self.semantic_analyzer:
                # Análisis semántico real
                analysis = self.semantic_analyzer.analyze_text(query)
                return {
                    "intent": analysis.get("intent", "general"),
                    "confidence": analysis.get("confidence", 0.5),
                    "entities": analysis.get("entities", []),
                    "sentiment": analysis.get("sentiment", "neutral"),
                }
            else:
                # Análisis básico
                query_lower = query.lower()
                if "?" in query:
                    intent = "question"
                elif any(
                    word in query_lower for word in ["ayuda", "ayudar", "asistir"]
                ):
                    intent = "help"
                else:
                    intent = "statement"

                return {
                    "intent": intent,
                    "confidence": 0.6,
                    "entities": [],
                    "sentiment": "neutral",
                }

        except Exception as e:
            logger.error(f"Error analizando intención: {e}")
            return {
                "intent": "unknown",
                "confidence": 0.0,
                "entities": [],
                "sentiment": "neutral",
            }

    def get_system_status(self) -> Dict[str, Any]:
        """Obtener estado del sistema de respaldo"""
        return {
            "backup_system_available": LLM_AVAILABLE,
            "main_model_loaded": self.llm_model is not None,
            "text_processor_loaded": self.text_processor is not None,
            "semantic_analyzer_loaded": self.semantic_analyzer is not None,
            "timestamp": datetime.now().isoformat(),
        }


def main():
    """Función principal para pruebas"""
    print("🧠 SISTEMA DE RESPALDO INTELIGENTE - PRUEBAS")
    print("=" * 50)

    system = IntelligentBackupSystem()

    # Probar estado del sistema
    status = system.get_system_status()
    print(f"Estado del sistema: {status}")

    # Probar respuesta de respaldo
    test_query = "¿Qué es la inteligencia artificial?"
    result = system.generate_backup_response(test_query, error_type="general")

    print(f"\nConsulta: {test_query}")
    print(f"Respuesta: {result['response']}")
    print(f"Fuente: {result['source']}")
    print(f"Confianza: {result['confidence']}")
    print(f"Tiempo: {result['processing_time']}s")

    # Probar análisis de intención
    intent_analysis = system.analyze_query_intent(test_query)
    print(f"\nAnálisis de intención: {intent_analysis}")


if __name__ == "__main__":
    main()
