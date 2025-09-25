"""
Sistema de Aprendizaje Continuo Real para Shaili AI
===================================================

Sistema que implementa aprendizaje continuo usando el modelo principal
y el gestor de ramas para mejorar las respuestas.
"""

import logging
import os
import sys
from typing import Dict, Any, List, Optional
import numpy as np
from datetime import datetime
import json

# Agregar path para importar módulos
sys.path.append(os.path.join(os.path.dirname(__file__), "../.."))

try:
    from modules.core.model.simple_shaili import SimpleShailiModel
    from models.branches.branch_manager import BranchManager
    from modules.ai.text_processor import TextProcessor
    from modules.ai.semantic_analyzer import SemanticAnalyzer

    COMPONENTS_AVAILABLE = True
except ImportError as e:
    logging.error(f"Error importando módulos: {e}")
    COMPONENTS_AVAILABLE = False

logger = logging.getLogger(__name__)


class ContinuousLearningSystem:
    """
    Sistema de aprendizaje continuo que mejora las respuestas
    basándose en feedback del usuario
    """

    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.main_model = None
        self.branch_manager = None
        self.text_processor = None
        self.semantic_analyzer = None

        self.learning_data = {
            "queries": [],
            "responses": [],
            "feedback": [],
            "improvements": [],
        }

        self.performance_metrics = {
            "total_queries": 0,
            "positive_feedback": 0,
            "negative_feedback": 0,
            "improvement_rate": 0.0,
        }

        self._initialize_learning_system()

    def _initialize_learning_system(self):
        """Inicializar sistema de aprendizaje con componentes reales"""
        try:
            if not COMPONENTS_AVAILABLE:
                raise Exception("Componentes no disponibles")

            # Cargar modelo principal
            self.main_model = SimpleShailiModel(
                model_id="models/custom/shaili-personal-model", quantization="4bit"
            )
            logger.info("✅ Modelo principal cargado para aprendizaje")

            # Cargar gestor de ramas
            self.branch_manager = BranchManager()
            logger.info("✅ Gestor de ramas cargado para aprendizaje")

            # Cargar procesador de texto
            self.text_processor = TextProcessor()
            logger.info("✅ Procesador de texto cargado para aprendizaje")

            # Cargar analizador semántico
            self.semantic_analyzer = SemanticAnalyzer()
            logger.info("✅ Analizador semántico cargado para aprendizaje")

            logger.info("🎉 Sistema de aprendizaje continuo inicializado")

        except Exception as e:
            logger.error(f"❌ Error inicializando sistema de aprendizaje: {e}")

    def process_query_with_learning(
        self,
        query: str,
        context: Optional[Dict[str, Any]] = None,
        branch: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Procesar consulta con aprendizaje continuo

        Args:
            query: Consulta del usuario
            context: Contexto adicional
            branch: Rama específica a usar

        Returns:
            Dict con respuesta y datos de aprendizaje
        """
        try:
            start_time = datetime.now()

            # Registrar consulta
            self.learning_data["queries"].append(
                {
                    "query": query,
                    "timestamp": datetime.now().isoformat(),
                    "branch": branch,
                    "context": context,
                }
            )

            # Analizar consulta
            query_analysis = None
            if self.text_processor:
                query_analysis = self.text_processor.analyze_text(query)

            # Generar respuesta principal
            main_response = None
            if self.main_model:
                main_response = self.main_model.generate_text(
                    prompt=query, max_length=1024, temperature=0.7, top_p=0.9
                )

            # Generar embedding para rama específica
            embedding = None
            if branch and self.branch_manager:
                try:
                    embedding = self.branch_manager.generate_embeddings(branch, query)
                    # Aprender de la consulta
                    self.branch_manager.learn_from_feedback(
                        branch, query, str(embedding.shape), 1.0
                    )
                except Exception as e:
                    logger.warning(
                        f"No se pudo generar embedding para rama {branch}: {e}"
                    )

            # Registrar respuesta
            response_data = {
                "response": main_response,
                "query_analysis": query_analysis,
                "embedding_shape": embedding.shape if embedding is not None else None,
                "processing_time": (datetime.now() - start_time).total_seconds(),
                "timestamp": datetime.now().isoformat(),
            }
            self.learning_data["responses"].append(response_data)

            # Actualizar métricas
            self.performance_metrics["total_queries"] += 1

            return {
                "success": True,
                "response": main_response,
                "learning_data": {
                    "query_analyzed": query_analysis is not None,
                    "embedding_generated": embedding is not None,
                    "branch_used": branch,
                    "query_id": len(self.learning_data["queries"]) - 1,
                },
                "performance_metrics": self.performance_metrics,
                "processing_time": response_data["processing_time"],
                "timestamp": datetime.now().isoformat(),
            }

        except Exception as e:
            logger.error(f"❌ Error en procesamiento con aprendizaje: {e}")
            return {
                "success": False,
                "response": "Error en el procesamiento con aprendizaje",
                "error": str(e),
                "timestamp": datetime.now().isoformat(),
            }

    def provide_feedback(
        self, query_id: int, feedback_score: float, feedback_text: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Proporcionar feedback para mejorar el sistema

        Args:
            query_id: ID de la consulta
            feedback_score: Puntuación del feedback (0.0 a 1.0)
            feedback_text: Texto adicional del feedback

        Returns:
            Dict con resultado del feedback
        """
        try:
            if query_id >= len(self.learning_data["queries"]):
                raise Exception("ID de consulta inválido")

            # Registrar feedback
            feedback_data = {
                "query_id": query_id,
                "score": feedback_score,
                "text": feedback_text,
                "timestamp": datetime.now().isoformat(),
            }
            self.learning_data["feedback"].append(feedback_data)

            # Actualizar métricas
            if feedback_score >= 0.7:
                self.performance_metrics["positive_feedback"] += 1
            else:
                self.performance_metrics["negative_feedback"] += 1

            # Calcular tasa de mejora
            total_feedback = len(self.learning_data["feedback"])
            if total_feedback > 0:
                self.performance_metrics["improvement_rate"] = (
                    self.performance_metrics["positive_feedback"] / total_feedback
                )

            # Aplicar aprendizaje si es feedback negativo
            if feedback_score < 0.7 and query_id < len(self.learning_data["queries"]):
                query_data = self.learning_data["queries"][query_id]
                self._apply_learning_from_feedback(query_data, feedback_data)

            return {
                "success": True,
                "feedback_registered": True,
                "performance_metrics": self.performance_metrics,
                "timestamp": datetime.now().isoformat(),
            }

        except Exception as e:
            logger.error(f"❌ Error registrando feedback: {e}")
            return {
                "success": False,
                "error": str(e),
                "timestamp": datetime.now().isoformat(),
            }

    def _apply_learning_from_feedback(
        self, query_data: Dict[str, Any], feedback_data: Dict[str, Any]
    ) -> None:
        """Aplicar aprendizaje basado en feedback negativo"""
        try:
            query = query_data["query"]
            branch = query_data.get("branch")

            if branch and self.branch_manager:
                # Aprender de feedback negativo
                self.branch_manager.learn_from_feedback(
                    branch, query, "384", feedback_data["score"]
                )

                # Registrar mejora
                improvement_data = {
                    "query": query,
                    "branch": branch,
                    "feedback_score": feedback_data["score"],
                    "improvement_type": "branch_learning",
                    "timestamp": datetime.now().isoformat(),
                }
                self.learning_data["improvements"].append(improvement_data)

                logger.info(f"✅ Aprendizaje aplicado para rama {branch}")

        except Exception as e:
            logger.error(f"❌ Error aplicando aprendizaje: {e}")

    def get_learning_statistics(self) -> Dict[str, Any]:
        """Obtener estadísticas del aprendizaje"""
        return {
            "total_queries": len(self.learning_data["queries"]),
            "total_responses": len(self.learning_data["responses"]),
            "total_feedback": len(self.learning_data["feedback"]),
            "total_improvements": len(self.learning_data["improvements"]),
            "performance_metrics": self.performance_metrics,
            "branches_available": (
                self.branch_manager.list_branches() if self.branch_manager else []
            ),
            "timestamp": datetime.now().isoformat(),
        }

    def save_learning_data(
        self, filepath: str = "learning_data.json"
    ) -> Dict[str, Any]:
        """Guardar datos de aprendizaje en archivo"""
        try:
            data_to_save = {
                "learning_data": self.learning_data,
                "performance_metrics": self.performance_metrics,
                "export_timestamp": datetime.now().isoformat(),
            }

            with open(filepath, "w", encoding="utf-8") as f:
                json.dump(data_to_save, f, indent=2, ensure_ascii=False)

            return {
                "success": True,
                "filepath": filepath,
                "data_saved": True,
                "timestamp": datetime.now().isoformat(),
            }

        except Exception as e:
            logger.error(f"❌ Error guardando datos de aprendizaje: {e}")
            return {
                "success": False,
                "error": str(e),
                "timestamp": datetime.now().isoformat(),
            }


def main():
    """Función principal para pruebas"""
    print("🧠 SISTEMA DE APRENDIZAJE CONTINUO - PRUEBAS")
    print("=" * 50)

    learning_system = ContinuousLearningSystem()

    # Probar procesamiento con aprendizaje
    test_query = "¿Qué es la inteligencia artificial?"
    result = learning_system.process_query_with_learning(test_query, branch="general")

    print(f"Consulta: {test_query}")
    print(f"Respuesta: {result['response']}")
    print(f"Datos de aprendizaje: {result['learning_data']}")

    # Probar feedback
    if result["success"]:
        feedback_result = learning_system.provide_feedback(
            query_id=result["learning_data"]["query_id"],
            feedback_score=0.8,
            feedback_text="Buena respuesta",
        )
        print(f"Feedback: {feedback_result}")

    # Obtener estadísticas
    stats = learning_system.get_learning_statistics()
    print(f"Estadísticas: {stats}")

    # Guardar datos
    save_result = learning_system.save_learning_data()
    print(f"Guardado: {save_result}")


if __name__ == "__main__":
    main()
