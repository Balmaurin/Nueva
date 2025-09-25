import logging
from typing import Dict, Any, Optional, List

from modules.orchestrator.router import SemanticRouter
from modules.core.continuous_improvement import ContinuousImprovement
from branches.branch_manager import BranchManager
from modules.memory.rag import RAGRetriever
from security.access_control import SecurityManager
from evaluation.error_detector import ErrorDetector
from modules.core.dynamic_knowledge_generator import DynamicKnowledgeGenerator
from modules.core.semantic_adaptation_manager import SemanticAdaptationManager
from modules.core.cognitive_understanding_module import CognitiveUnderstandingModule


class IntegrationManager:
    def __init__(self, base_config: Optional[Dict[str, Any]] = None):
        """
        Gestor central de integración de módulos de Shaili-AI

        Args:
            base_config (dict, opcional): Configuración base del sistema
        """
        self.logger = logging.getLogger(__name__)
        self.config = base_config or {}

        # Inicializar componentes principales
        self.semantic_router = SemanticRouter(
            base_model=self.config.get("base_model"),
            domain_classifier=self.config.get("domain_classifier"),
            rag_retriever=RAGRetriever(),
            branch_manager=BranchManager(),
        )

        # Nuevos módulos avanzados
        self.knowledge_generator = DynamicKnowledgeGenerator()
        self.semantic_adapter = SemanticAdaptationManager()
        self.cognitive_understanding = CognitiveUnderstandingModule()

        # Módulos existentes
        self.continuous_improvement = ContinuousImprovement()
        self.security_manager = SecurityManager()
        self.error_detector = ErrorDetector()

    def process_query(self, query: str) -> Dict[str, Any]:
        """
        Procesar consulta unificando todos los módulos

        Args:
            query (str): Consulta de entrada

        Returns:
            dict: Resultado procesado con información de todos los módulos
        """
        # Seguridad: Validar acceso
        if not self.security_manager.validate_access(query):
            return {"error": "Acceso denegado"}

        # Adaptación semántica
        adapted_query = self.semantic_adapter.adapt_semantic_context(
            query, domain_contexts=self.semantic_router.get_domain_contexts()
        )

        # Enrutamiento semántico
        route_type, route_details = self.semantic_router.route(adapted_query)

        # Generación de conocimiento contextual
        contextual_knowledge = self.knowledge_generator.generate_contextual_knowledge(
            context=adapted_query, domain=route_details.get("domain")
        )

        # Detección de errores
        potential_errors = self.error_detector.analyze(adapted_query, route_details)

        # Análisis de complejidad cognitiva
        cognitive_feedback = self.cognitive_understanding.generate_cognitive_feedback(
            original_text=query, processed_text=adapted_query
        )

        # Mejora continua: Registrar interacción
        self.continuous_improvement.analyze_interaction(adapted_query, route_details)

        return {
            "original_query": query,
            "adapted_query": adapted_query,
            "route_type": route_type,
            "route_details": route_details,
            "contextual_knowledge": contextual_knowledge,
            "potential_errors": potential_errors,
            "cognitive_feedback": cognitive_feedback,
        }

    def train_and_improve(self):
        """
        Método para entrenar y mejorar el sistema de manera continua
        """
        # Optimizar ramas de conocimiento
        self.continuous_improvement.optimize_branches()

        # Actualizar métricas de rendimiento
        self.continuous_improvement.update_performance_metrics()

        # Optimizar generador de conocimiento
        self.knowledge_generator.optimize_knowledge_generation()

        # Actualizar adaptador semántico
        self.semantic_adapter.update_domain_knowledge(
            domain="general",
            new_knowledge=self.continuous_improvement.get_recent_interactions(),
        )

    def generate_advanced_insights(self, interactions: List[str]) -> Dict[str, Any]:
        """
        Generar insights avanzados a partir de interacciones

        Args:
            interactions (List[str]): Lista de interacciones

        Returns:
            Diccionario de insights generados
        """
        # Clustering semántico de interacciones
        semantic_clusters = self.semantic_adapter.cluster_semantic_domains(interactions)

        # Análisis de complejidad cognitiva
        complexity_analysis = {
            cluster: [
                self.cognitive_understanding.analyze_cognitive_complexity(text)
                for text in texts
            ]
            for cluster, texts in semantic_clusters.items()
        }

        # Generar conocimiento contextual para cada cluster
        contextual_knowledge = {
            cluster: self.knowledge_generator.generate_contextual_knowledge(
                context=" ".join(texts), domain=str(cluster)
            )
            for cluster, texts in semantic_clusters.items()
        }

        return {
            "semantic_clusters": semantic_clusters,
            "complexity_analysis": complexity_analysis,
            "contextual_knowledge": contextual_knowledge,
        }
