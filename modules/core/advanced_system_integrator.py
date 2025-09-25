"""
Integrador de Sistema Avanzado para Sheily AI
============================================

Integrador que coordina todos los componentes del sistema de IA
usando modelos y componentes reales.
"""

import logging
import os
import sys
from typing import Dict, Any, Optional, List
import numpy as np
from datetime import datetime

# Agregar path para importar módulos
sys.path.append(os.path.join(os.path.dirname(__file__), "../.."))

try:
    from modules.core.model.simple_sheily import SimpleSheilyModel
    from modules.ai.text_processor import TextProcessor
    from modules.ai.semantic_analyzer import SemanticAnalyzer
    from modules.ai.response_generator import ResponseGenerator
    from modules.memory.intelligent_backup_system import IntelligentBackupSystem
    from models.branches.branch_manager import BranchManager

    COMPONENTS_AVAILABLE = True
except ImportError as e:
    logging.error(f"Error importando módulos: {e}")
    COMPONENTS_AVAILABLE = False

logger = logging.getLogger(__name__)


class AdvancedSystemIntegrator:
    """
    Integrador avanzado del sistema que coordina todos los componentes
    """

    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.main_model = None
        self.text_processor = None
        self.semantic_analyzer = None
        self.response_generator = None
        self.backup_system = None
        self.branch_manager = None

        self.system_status = {
            "initialized": False,
            "components_loaded": 0,
            "total_components": 6,
        }

        self._initialize_system()

    def _initialize_system(self):
        """Inicializar todos los componentes del sistema"""
        try:
            if not COMPONENTS_AVAILABLE:
                raise Exception("Componentes no disponibles")

            # Cargar modelo principal
            self.main_model = SimpleShailiModel(
                model_id="models/custom/shaili-personal-model", quantization="4bit"
            )
            self.system_status["components_loaded"] += 1
            logger.info("✅ Modelo principal cargado")

            # Cargar procesador de texto
            self.text_processor = TextProcessor()
            self.system_status["components_loaded"] += 1
            logger.info("✅ Procesador de texto cargado")

            # Cargar analizador semántico
            self.semantic_analyzer = SemanticAnalyzer()
            self.system_status["components_loaded"] += 1
            logger.info("✅ Analizador semántico cargado")

            # Cargar generador de respuestas
            self.response_generator = ResponseGenerator()
            self.system_status["components_loaded"] += 1
            logger.info("✅ Generador de respuestas cargado")

            # Cargar sistema de respaldo
            self.backup_system = IntelligentBackupSystem()
            self.system_status["components_loaded"] += 1
            logger.info("✅ Sistema de respaldo cargado")

            # Cargar gestor de ramas
            self.branch_manager = BranchManager()
            self.system_status["components_loaded"] += 1
            logger.info("✅ Gestor de ramas cargado")

            self.system_status["initialized"] = True
            logger.info("🎉 Sistema avanzado inicializado completamente")

        except Exception as e:
            logger.error(f"❌ Error inicializando sistema: {e}")
            self.system_status["initialized"] = False

    def process_query(
        self,
        query: str,
        context: Optional[Dict[str, Any]] = None,
        branch: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Procesar consulta completa usando todos los componentes

        Args:
            query: Consulta del usuario
            context: Contexto adicional
            branch: Rama específica a usar

        Returns:
            Dict con respuesta completa y metadatos
        """
        try:
            start_time = datetime.now()

            if not self.system_status["initialized"]:
                raise Exception("Sistema no inicializado")

            # 1. Análisis de texto
            text_analysis = None
            if self.text_processor:
                text_analysis = self.text_processor.analyze_text(query)

            # 2. Análisis semántico
            semantic_analysis = None
            if self.semantic_analyzer:
                semantic_analysis = self.semantic_analyzer.analyze_text(query)

            # 3. Generar embedding si hay rama específica
            embedding = None
            if branch and self.branch_manager:
                try:
                    embedding = self.branch_manager.generate_embeddings(branch, query)
                except Exception as e:
                    logger.warning(
                        f"No se pudo generar embedding para rama {branch}: {e}"
                    )

            # 4. Generar respuesta principal
            main_response = None
            if self.main_model:
                main_response = self.main_model.generate_text(
                    prompt=query, max_length=1024, temperature=0.7, top_p=0.9
                )

            # 5. Procesar respuesta con generador
            processed_response = None
            if self.response_generator and main_response:
                response_context = {
                    "user_query": query,
                    "main_response": main_response,
                    "text_analysis": text_analysis,
                    "semantic_analysis": semantic_analysis,
                    "embedding": embedding,
                    "branch": branch,
                    "context": context or {},
                }

                processed_response = self.response_generator.generate_response(
                    response_context
                )

            processing_time = (datetime.now() - start_time).total_seconds()

            # Construir respuesta final
            final_response = {
                "success": True,
                "response": (
                    processed_response.text if processed_response else main_response
                ),
                "confidence": (
                    processed_response.confidence if processed_response else 0.8
                ),
                "processing_time": processing_time,
                "components_used": {
                    "main_model": self.main_model is not None,
                    "text_processor": self.text_processor is not None,
                    "semantic_analyzer": self.semantic_analyzer is not None,
                    "response_generator": self.response_generator is not None,
                    "branch_manager": self.branch_manager is not None,
                },
                "analysis": {
                    "text_analysis": text_analysis,
                    "semantic_analysis": semantic_analysis,
                    "embedding_shape": (
                        embedding.shape if embedding is not None else None
                    ),
                },
                "metadata": {
                    "branch_used": branch,
                    "model_used": "shaili-personal-model",
                    "quantization": "4bit",
                    "timestamp": datetime.now().isoformat(),
                },
            }

            return final_response

        except Exception as e:
            logger.error(f"❌ Error procesando consulta: {e}")

            # Usar sistema de respaldo
            if self.backup_system:
                backup_result = self.backup_system.generate_backup_response(
                    query, context, "processing_error"
                )
                backup_result["original_error"] = str(e)
                return backup_result

            # Respuesta de emergencia
            return {
                "success": False,
                "response": "Error crítico en el procesamiento. Sistema no disponible.",
                "confidence": 0.0,
                "processing_time": 0.0,
                "error": str(e),
                "metadata": {
                    "emergency": True,
                    "timestamp": datetime.now().isoformat(),
                },
            }

    def get_system_status(self) -> Dict[str, Any]:
        """Obtener estado completo del sistema"""
        return {
            "system_initialized": self.system_status["initialized"],
            "components_loaded": self.system_status["components_loaded"],
            "total_components": self.system_status["total_components"],
            "components": {
                "main_model": self.main_model is not None,
                "text_processor": self.text_processor is not None,
                "semantic_analyzer": self.semantic_analyzer is not None,
                "response_generator": self.response_generator is not None,
                "backup_system": self.backup_system is not None,
                "branch_manager": self.branch_manager is not None,
            },
            "timestamp": datetime.now().isoformat(),
        }

    def analyze_text(self, text: str) -> Dict[str, Any]:
        """Análisis completo de texto"""
        try:
            if not self.text_processor:
                raise Exception("Procesador de texto no disponible")

            analysis = self.text_processor.analyze_text(text)
            return {
                "success": True,
                "analysis": analysis,
                "timestamp": datetime.now().isoformat(),
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "timestamp": datetime.now().isoformat(),
            }

    def get_semantic_similarity(self, text1: str, text2: str) -> Dict[str, Any]:
        """Calcular similitud semántica"""
        try:
            if not self.semantic_analyzer:
                raise Exception("Analizador semántico no disponible")

            similarity = self.semantic_analyzer.calculate_similarity(text1, text2)
            return {
                "success": True,
                "similarity": similarity.similarity_score,
                "timestamp": datetime.now().isoformat(),
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "timestamp": datetime.now().isoformat(),
            }


def main():
    """Función principal para pruebas"""
    print("🚀 INTEGRADOR DE SISTEMA AVANZADO - PRUEBAS")
    print("=" * 50)

    integrator = AdvancedSystemIntegrator()

    # Verificar estado del sistema
    status = integrator.get_system_status()
    print(f"Estado del sistema: {status}")

    # Probar procesamiento de consulta
    test_query = "¿Qué es la inteligencia artificial y cómo funciona?"
    result = integrator.process_query(test_query, branch="general")

    print(f"\nConsulta: {test_query}")
    print(f"Respuesta: {result['response']}")
    print(f"Confianza: {result['confidence']}")
    print(f"Tiempo: {result['processing_time']}s")
    print(f"Componentes usados: {result['components_used']}")

    # Probar análisis de texto
    text_analysis = integrator.analyze_text(test_query)
    print(f"\nAnálisis de texto: {text_analysis}")


if __name__ == "__main__":
    main()
