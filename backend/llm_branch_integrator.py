"""
Integrador de LLM con Sistema de Ramas
=====================================

Conecta el Llama 3.2 con el sistema de ramas especializadas existente.
"""

import logging
import sys
import os
from typing import Dict, Any, Optional, List
from datetime import datetime

# Agregar path para importar módulos
sys.path.append(os.path.join(os.path.dirname(__file__), ".."))

try:
    from modules.orchestrator.main_orchestrator import MainOrchestrator
    from modules.orchestrator.router import SemanticRouter
    from modules.orchestrator.domain_classifier import DomainClassifier
    from modules.memory.rag import RAGRetriever
    from models.branches.branch_manager import BranchManager
    from models.branches.adapter_policy import AdapterUpdatePolicy

    MODULES_AVAILABLE = True
except ImportError as e:
    logging.error(f"Error importando módulos: {e}")
    MODULES_AVAILABLE = False

logger = logging.getLogger(__name__)


class LLMBranchIntegrator:
    """
    Integrador que conecta Llama 3.2 con el sistema de ramas especializadas
    """

    def __init__(self, llama_instance=None):
        """
        Inicializar integrador

        Args:
            llama_instance: Instancia de Llama 3.2 cargada
        """
        self.logger = logging.getLogger(__name__)
        self.llama_instance = llama_instance
        self.orchestrator = None
        self.semantic_router = None
        self.branch_manager = None
        self.domain_classifier = None
        self.rag_retriever = None

        self.system_status = {
            "initialized": False,
            "modules_available": MODULES_AVAILABLE,
            "components_loaded": 0,
            "total_components": 5,
        }

        if MODULES_AVAILABLE:
            self._initialize_system()
        else:
            self.logger.warning("⚠️ Módulos no disponibles, usando solo Llama 3.2 base")

    def _initialize_system(self):
        """Inicializar todos los componentes del sistema de ramas"""
        try:
            self.logger.info("🔄 Inicializando sistema de ramas...")

            # Configuración del orquestador
            config = {
                "enable_domain_classification": True,
                "enable_rag": True,
                "enable_branch_management": True,
                "enable_adapter_policy": True,
                "enable_semantic_routing": True,
            }

            # Inicializar orquestador principal
            self.orchestrator = MainOrchestrator(config)
            self.system_status["components_loaded"] += 1
            self.logger.info("✅ Orquestador principal inicializado")

            # Obtener componentes del orquestador
            self.semantic_router = self.orchestrator.semantic_router
            self.branch_manager = self.orchestrator.branch_manager
            self.domain_classifier = self.orchestrator.domain_classifier
            self.rag_retriever = self.orchestrator.rag_retriever

            self.system_status["components_loaded"] += 4
            self.logger.info(
                "✅ Todos los componentes del sistema de ramas inicializados"
            )

            self.system_status["initialized"] = True
            self.logger.info("🎉 Sistema de ramas completamente inicializado")

        except Exception as e:
            self.logger.error(f"❌ Error inicializando sistema de ramas: {e}")
            self.system_status["initialized"] = False

    def process_query(self, messages: List[Dict[str, str]]) -> Dict[str, Any]:
        """
        Procesar consulta usando el sistema de ramas

        Args:
            messages: Lista de mensajes del chat

        Returns:
            Dict con respuesta y metadatos
        """
        try:
            start_time = datetime.now()

            # Extraer la consulta del último mensaje
            if not messages:
                return {"error": "No messages provided"}

            query = messages[-1].get("content", "")
            if not query:
                return {"error": "Empty query"}

            self.logger.info(f"🔍 Procesando consulta: {query[:100]}...")

            # Si el sistema de ramas no está disponible, usar solo Llama 3.2
            if not self.system_status["initialized"]:
                return self._fallback_to_llama(messages)

            # Detectar dominio de la consulta
            domain, domain_confidence = self._detect_domain(query)
            self.logger.info(
                f"🎯 Dominio detectado: {domain} (confianza: {domain_confidence:.2f})"
            )

            # Enrutar consulta
            route_type, route_info = self.semantic_router.route(query)
            self.logger.info(f"🛣️ Ruta seleccionada: {route_type}")

            # Procesar según el tipo de ruta
            if route_type == "branch" and route_info.get("model"):
                # Usar adaptador especializado
                response = self._process_with_branch_adapter(query, route_info)
                processing_method = "branch_specialized"
            elif route_type == "rag" and route_info.get("citations"):
                # Usar RAG con contexto
                response = self._process_with_rag(query, route_info)
                processing_method = "rag_enhanced"
            else:
                # Usar Llama 3.2 base
                response = self._process_with_llama_base(messages)
                processing_method = "llama_base"

            processing_time = (datetime.now() - start_time).total_seconds()

            return {
                "response": response,
                "processing_method": processing_method,
                "domain": domain,
                "domain_confidence": domain_confidence,
                "route_type": route_type,
                "processing_time": processing_time,
                "timestamp": datetime.now().isoformat(),
                "system_status": self.system_status,
            }

        except Exception as e:
            self.logger.error(f"❌ Error procesando consulta: {e}")
            return self._fallback_to_llama(messages, error=str(e))

    def _detect_domain(self, query: str) -> tuple:
        """Detectar dominio de la consulta"""
        try:
            if self.domain_classifier:
                domain, confidence = self.domain_classifier.predict(query)
                return domain, confidence
            else:
                # Detección simple por palabras clave
                return self._simple_domain_detection(query)
        except Exception as e:
            self.logger.warning(f"Error detectando dominio: {e}")
            return "general", 0.5

    def _simple_domain_detection(self, query: str) -> tuple:
        """Detección simple de dominio por palabras clave"""
        query_lower = query.lower()

        # Mapeo de palabras clave a dominios
        domain_keywords = {
            "medicina_y_salud": [
                "médico",
                "salud",
                "enfermedad",
                "tratamiento",
                "síntoma",
                "diagnóstico",
            ],
            "computación_y_programación": [
                "código",
                "programa",
                "software",
                "algoritmo",
                "python",
                "javascript",
            ],
            "matemáticas": [
                "matemática",
                "cálculo",
                "álgebra",
                "ecuación",
                "función",
                "derivada",
            ],
            "física": [
                "física",
                "mecánica",
                "energía",
                "fuerza",
                "velocidad",
                "aceleración",
            ],
            "química": [
                "química",
                "molécula",
                "átomo",
                "reacción",
                "compuesto",
                "elemento",
            ],
            "biología": ["biología", "célula", "gen", "ADN", "evolución", "ecosistema"],
        }

        for domain, keywords in domain_keywords.items():
            if any(keyword in query_lower for keyword in keywords):
                return domain, 0.8

        return "general", 0.5

    def _process_with_branch_adapter(
        self, query: str, route_info: Dict[str, Any]
    ) -> str:
        """Procesar consulta con adaptador de rama especializada"""
        try:
            adapter_model = route_info.get("model")
            if adapter_model:
                # Usar el adaptador especializado
                response = adapter_model.generate(query, max_tokens=1024)
                self.logger.info(f"✅ Respuesta generada con adaptador especializado")
                return response
            else:
                return self._fallback_to_llama([{"role": "user", "content": query}])
        except Exception as e:
            self.logger.error(f"Error con adaptador especializado: {e}")
            return self._fallback_to_llama([{"role": "user", "content": query}])

    def _process_with_rag(self, query: str, route_info: Dict[str, Any]) -> str:
        """Procesar consulta con RAG"""
        try:
            citations = route_info.get("citations", [])
            if citations:
                # Construir contexto con citaciones
                context = "\n".join(
                    [citation.get("text", "") for citation in citations[:3]]
                )
                enhanced_query = f"Contexto: {context}\n\nPregunta: {query}"

                # Usar Llama 3.2 con contexto enriquecido
                response = self._fallback_to_llama(
                    [{"role": "user", "content": enhanced_query}]
                )
                self.logger.info(f"✅ Respuesta generada con RAG")
                return response
            else:
                return self._fallback_to_llama([{"role": "user", "content": query}])
        except Exception as e:
            self.logger.error(f"Error con RAG: {e}")
            return self._fallback_to_llama([{"role": "user", "content": query}])

    def _process_with_llama_base(self, messages: List[Dict[str, str]]) -> str:
        """Procesar consulta con Llama 3.2 base"""
        return self._fallback_to_llama(messages)

    def _fallback_to_llama(
        self, messages: List[Dict[str, str]], error: str = None
    ) -> Dict[str, Any]:
        """Fallback a Llama 3.2 base"""
        try:
            if not self.llama_instance:
                return {"error": "Llama 3.2 no disponible"}

            # Generar respuesta con Llama 3.2
            response_chunks = []
            full_response_content = ""

            for chunk in self.llama_instance.create_chat_completion(
                messages=messages, max_tokens=2048, stream=True
            ):
                delta = chunk["choices"][0]["delta"]
                if "content" in delta:
                    response_chunks.append(delta["content"])
                    full_response_content += delta["content"]

            return {
                "response": full_response_content,
                "processing_method": "llama_base_fallback",
                "domain": "general",
                "domain_confidence": 0.5,
                "route_type": "fallback",
                "processing_time": 0.0,
                "timestamp": datetime.now().isoformat(),
                "error": error,
                "system_status": self.system_status,
            }

        except Exception as e:
            self.logger.error(f"❌ Error en fallback: {e}")
            return {
                "error": f"Error crítico: {e}",
                "processing_method": "error",
                "timestamp": datetime.now().isoformat(),
            }

    def get_system_status(self) -> Dict[str, Any]:
        """Obtener estado completo del sistema"""
        return {
            "system_initialized": self.system_status["initialized"],
            "modules_available": self.system_status["modules_available"],
            "components_loaded": self.system_status["components_loaded"],
            "total_components": self.system_status["total_components"],
            "llama_available": self.llama_instance is not None,
            "orchestrator_available": self.orchestrator is not None,
            "semantic_router_available": self.semantic_router is not None,
            "branch_manager_available": self.branch_manager is not None,
            "domain_classifier_available": self.domain_classifier is not None,
            "rag_retriever_available": self.rag_retriever is not None,
            "timestamp": datetime.now().isoformat(),
        }

    def get_available_domains(self) -> List[str]:
        """Obtener dominios disponibles"""
        if self.branch_manager:
            return self.branch_manager.get_available_domains()
        return ["general"]

    def get_branch_status(self, domain: str = None) -> Dict[str, Any]:
        """Obtener estado de ramas"""
        if self.branch_manager:
            if domain:
                return self.branch_manager.get_branch_status(domain)
            else:
                return self.branch_manager.get_all_branches_status()
        return {"error": "Branch manager no disponible"}


def main():
    """Función principal para pruebas"""
    print("🚀 INTEGRADOR LLM-BRANCH - PRUEBAS")
    print("=" * 50)

    integrator = LLMBranchIntegrator()

    # Verificar estado del sistema
    status = integrator.get_system_status()
    print(f"Estado del sistema: {status}")

    # Probar consultas de diferentes dominios
    test_queries = [
        "¿Cómo funciona la diabetes?",
        "¿Cómo implementar un algoritmo de ordenamiento?",
        "¿Qué es la derivada de una función?",
        "¿Cómo funciona la fotosíntesis?",
        "¿Cuál es la capital de Francia?",
    ]

    for query in test_queries:
        print(f"\n🔍 Consulta: {query}")
        result = integrator.process_query([{"role": "user", "content": query}])
        print(f"📝 Respuesta: {result.get('response', 'Error')[:100]}...")
        print(
            f"🎯 Dominio: {result.get('domain')} (confianza: {result.get('domain_confidence', 0):.2f})"
        )
        print(f"🛣️ Método: {result.get('processing_method')}")


if __name__ == "__main__":
    main()
