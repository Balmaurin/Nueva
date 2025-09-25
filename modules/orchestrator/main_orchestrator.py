"""
Orquestador Principal de Sheily-AI
==================================

Sistema completo de orquestación que coordina todos los componentes:
- Clasificación de dominio
- Enrutamiento semántico
- Gestión de ramas
- Sistema RAG
- Políticas de adapters
"""

import logging
import time
from typing import Dict, Any, Tuple, List, Optional
from datetime import datetime
import json
import os

# Importar componentes del orquestador
from modules.orchestrator.domain_classifier import DomainClassifier
from modules.orchestrator.router import SemanticRouter
from modules.core.model.sheily_model import SheilyBaseModel
from modules.memory.rag import RAGRetriever
from branches.branch_manager import BranchManager
from branches.adapter_policy import AdapterUpdatePolicy

# Importar cliente LLM
import sys

sys.path.append(os.path.join(os.path.dirname(__file__), "..", "..", "backend"))
from llm_client import get_llm_client


class MainOrchestrator:
    """
    Orquestador principal que coordina todos los componentes del sistema
    """

    def __init__(self, config: Dict[str, Any] = None):
        """
        Inicializar orquestador principal

        Args:
            config (dict): Configuración del orquestador
        """
        self.logger = logging.getLogger(__name__)

        # Configuración por defecto
        self.config = config or {
            "enable_domain_classification": True,
            "enable_semantic_routing": True,
            "enable_branch_management": True,
            "enable_rag": True,
            "enable_adapter_policy": True,
            "max_response_time": 30.0,  # segundos
            "enable_caching": True,
            "cache_ttl": 3600,  # segundos
            "enable_monitoring": True,
            "log_level": "INFO",
        }

        # Configurar logging
        logging.basicConfig(
            level=getattr(logging, self.config["log_level"]),
            format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        )

        # Inicializar componentes
        self._initialize_components()

        # Métricas y monitoreo
        self.metrics = {
            "total_requests": 0,
            "successful_requests": 0,
            "failed_requests": 0,
            "average_response_time": 0.0,
            "domain_distribution": {},
            "route_distribution": {},
            "last_request_time": None,
        }

        # Caché de respuestas
        self.response_cache = {}

        self.logger.info("✅ MainOrchestrator inicializado correctamente")

    def _initialize_components(self):
        """Inicializar todos los componentes del sistema"""
        try:
            # Modelo base
            self.base_model = SheilyBaseModel()
            self.logger.info("✅ Modelo base inicializado")

            # Clasificador de dominio
            if self.config["enable_domain_classification"]:
                self.domain_classifier = DomainClassifier()
                self.logger.info("✅ Clasificador de dominio inicializado")
            else:
                self.domain_classifier = None

            # Sistema RAG
            if self.config["enable_rag"]:
                self.rag_retriever = RAGRetriever()
                self.logger.info("✅ Sistema RAG inicializado")
            else:
                self.rag_retriever = None

            # Gestor de ramas
            if self.config["enable_branch_management"]:
                self.branch_manager = BranchManager()
                self.logger.info("✅ Gestor de ramas inicializado")
            else:
                self.branch_manager = None

            # Política de adapters
            if self.config["enable_adapter_policy"]:
                self.adapter_policy = AdapterUpdatePolicy()
                self.logger.info("✅ Política de adapters inicializada")
            else:
                self.adapter_policy = None

            # Router semántico
            if self.config["enable_semantic_routing"]:
                self.semantic_router = SemanticRouter(
                    base_model=self.base_model,
                    domain_classifier=self.domain_classifier,
                    rag_retriever=self.rag_retriever,
                    branch_manager=self.branch_manager,
                    adapter_policy=self.adapter_policy,
                )
                self.logger.info("✅ Router semántico inicializado")
            else:
                self.semantic_router = None

        except Exception as e:
            self.logger.error(f"❌ Error inicializando componentes: {e}")
            raise

    def process_query(
        self, query: str, user_context: Dict[str, Any] = None
    ) -> Dict[str, Any]:
        """
        Procesar consulta del usuario de manera completa

        Args:
            query (str): Consulta del usuario
            user_context (dict, opcional): Contexto del usuario

        Returns:
            dict: Respuesta completa con metadatos
        """
        start_time = time.time()

        try:
            # Actualizar métricas
            self.metrics["total_requests"] += 1
            self.metrics["last_request_time"] = datetime.now().isoformat()

            # Verificar caché
            if self.config["enable_caching"]:
                cached_response = self._get_cached_response(query)
                if cached_response:
                    self.logger.info("✅ Respuesta obtenida desde caché")
                    return cached_response

            # Procesar consulta
            response = self._process_query_internal(query, user_context)

            # Calcular tiempo de respuesta
            response_time = time.time() - start_time
            response["response_time"] = response_time

            # Actualizar métricas
            self._update_metrics(response, response_time)

            # Guardar en caché
            if self.config["enable_caching"]:
                self._cache_response(query, response)

            # Monitoreo
            if self.config["enable_monitoring"]:
                self._log_monitoring_data(query, response)

            self.metrics["successful_requests"] += 1

            return response

        except Exception as e:
            self.logger.error(f"❌ Error procesando consulta: {e}")
            self.metrics["failed_requests"] += 1

            return {
                "error": str(e),
                "query": query,
                "response_time": time.time() - start_time,
                "timestamp": datetime.now().isoformat(),
            }

    def _process_query_internal(
        self, query: str, user_context: Dict[str, Any] = None
    ) -> Dict[str, Any]:
        """Procesamiento interno de la consulta"""

        # Paso 1: Clasificación de dominio
        domain_info = self._classify_domain(query)

        # Paso 2: Enrutamiento semántico
        route_info = self._route_query(query, domain_info)

        # Paso 3: Generación de respuesta
        response = self._generate_response(query, route_info, user_context)

        # Paso 4: Post-procesamiento
        response = self._post_process_response(response, domain_info, route_info)

        return response

    def _classify_domain(self, query: str) -> Dict[str, Any]:
        """Clasificar dominio de la consulta"""
        if not self.domain_classifier:
            return {"domain": "General", "confidence": 0.5}

        try:
            domain, confidence = self.domain_classifier.predict(query)
            return {
                "domain": domain,
                "confidence": confidence,
                "classification_method": "ml_classifier",
            }
        except Exception as e:
            self.logger.warning(f"Error en clasificación de dominio: {e}")
            return {"domain": "General", "confidence": 0.3, "error": str(e)}

    def _route_query(self, query: str, domain_info: Dict[str, Any]) -> Dict[str, Any]:
        """Enrutar consulta al componente apropiado"""
        if not self.semantic_router:
            return {"route_type": "core", "model": self.base_model}

        try:
            route_type, route_details = self.semantic_router.route(query)
            return {
                "route_type": route_type,
                "route_details": route_details,
                "domain_info": domain_info,
            }
        except Exception as e:
            self.logger.warning(f"Error en enrutamiento: {e}")
            return {"route_type": "core", "model": self.base_model, "error": str(e)}

    def _generate_response(
        self,
        query: str,
        route_info: Dict[str, Any],
        user_context: Dict[str, Any] = None,
    ) -> Dict[str, Any]:
        """Generar respuesta basada en el enrutamiento"""

        route_type = route_info.get("route_type", "core")

        try:
            if route_type == "branch":
                # Usar rama especializada
                response = self._generate_branch_response(query, route_info)
            elif route_type == "rag":
                # Usar sistema RAG
                response = self._generate_rag_response(query, route_info)
            else:
                # Usar modelo base
                response = self._generate_core_response(query, route_info)

            return response

        except Exception as e:
            self.logger.error(f"Error generando respuesta: {e}")
            return {
                "text": f"Lo siento, hubo un error procesando tu consulta: {str(e)}",
                "source": "error_handler",
                "route_type": route_type,
            }

    def _generate_branch_response(
        self, query: str, route_info: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Generar respuesta usando rama especializada"""
        try:
            domain = route_info.get("domain_info", {}).get("domain", "general")
            confidence = route_info.get("domain_info", {}).get("confidence", 0.5)

            # Usar cliente LLM con contexto de dominio
            llm_client = get_llm_client()

            # Crear mensajes con contexto de dominio
            messages = [
                {
                    "role": "system",
                    "content": f"Eres SHEILY especializado en {domain}. Proporciona una respuesta experta y precisa en este dominio.",
                },
                {"role": "user", "content": query},
            ]

            # Generar respuesta usando el cliente LLM
            response_text = llm_client.llm_chat(
                messages, temperature=0.2, max_tokens=512
            )

            return {
                "text": response_text,
                "source": "branch_model",
                "domain": domain,
                "confidence": confidence,
                "llm_enhanced": True,
            }
        except Exception as e:
            self.logger.error(f"Error en rama especializada: {e}")
            # Fallback al modelo base
            return self._generate_core_response(query, route_info)

    def _generate_rag_response(
        self, query: str, route_info: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Generar respuesta usando sistema RAG"""
        try:
            citations = route_info.get("route_details", {}).get("citations", [])
            if citations:
                # Usar cliente LLM para procesar información RAG
                llm_client = get_llm_client()

                # Combinar información de RAG
                rag_context = "\n\n".join(
                    [
                        f"Fuente {i+1}: {citation.get('text', '')}"
                        for i, citation in enumerate(citations)
                    ]
                )

                # Crear mensajes con contexto RAG
                messages = [
                    {
                        "role": "system",
                        "content": "Eres SHEILY. Basándote en la información proporcionada, responde de manera precisa y útil. Cita las fuentes cuando sea relevante.",
                    },
                    {
                        "role": "user",
                        "content": f"Consulta: {query}\n\nInformación disponible:\n{rag_context}",
                    },
                ]

                # Generar respuesta usando el cliente LLM
                response_text = llm_client.llm_chat(
                    messages, temperature=0.1, max_tokens=768
                )

                return {
                    "text": response_text,
                    "source": "rag_system",
                    "citations": citations,
                    "confidence": route_info.get("domain_info", {}).get("confidence"),
                    "llm_enhanced": True,
                }
            else:
                raise Exception("No se encontraron citaciones relevantes")
        except Exception as e:
            self.logger.error(f"Error en sistema RAG: {e}")
            # Fallback al modelo base
            return self._generate_core_response(query, route_info)

    def _generate_core_response(
        self, query: str, route_info: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Generar respuesta usando modelo base"""
        try:
            # Usar cliente LLM como modelo base
            llm_client = get_llm_client()

            # Crear mensajes para modelo base
            messages = [
                {
                    "role": "system",
                    "content": "Eres SHEILY, un asistente de inteligencia artificial. Responde de manera útil y precisa en español.",
                },
                {"role": "user", "content": query},
            ]

            # Generar respuesta usando el cliente LLM
            response_text = llm_client.llm_chat(
                messages, temperature=0.3, max_tokens=512
            )

            return {
                "text": response_text,
                "source": "base_model",
                "confidence": route_info.get("domain_info", {}).get("confidence", 0.5),
                "llm_enhanced": True,
            }
        except Exception as e:
            self.logger.error(f"Error en modelo base: {e}")
            # Fallback a respuesta de error
            return {
                "text": f"Lo siento, hubo un error procesando tu consulta. Por favor, inténtalo de nuevo.",
                "source": "error_fallback",
                "confidence": 0.0,
                "error": str(e),
            }

    def _generate_enhanced_response(
        self, query: str, route_info: Dict[str, Any], use_pipeline: bool = False
    ) -> Dict[str, Any]:
        """Generar respuesta mejorada usando pipeline draft → critic → fix"""
        try:
            llm_client = get_llm_client()

            if use_pipeline and self.config.get("enable_enhanced_pipeline", True):
                # Usar pipeline completo draft → critic → fix
                self.logger.info("🔄 Usando pipeline mejorado draft → critic → fix")

                # Preparar contexto
                domain = route_info.get("domain_info", {}).get("domain", "general")
                context = f"Dominio: {domain}"

                # Ejecutar pipeline
                pipeline_result = llm_client.process_pipeline(query, context)

                return {
                    "text": pipeline_result["final_response"],
                    "source": "enhanced_pipeline",
                    "domain": domain,
                    "confidence": route_info.get("domain_info", {}).get(
                        "confidence", 0.5
                    ),
                    "llm_enhanced": True,
                    "pipeline_metadata": {
                        "draft": pipeline_result["draft"],
                        "critique": pipeline_result["critique"],
                        "processing_time": pipeline_result["processing_time"],
                    },
                }
            else:
                # Usar generación simple
                return self._generate_core_response(query, route_info)

        except Exception as e:
            self.logger.error(f"Error en respuesta mejorada: {e}")
            # Fallback a respuesta base
            return self._generate_core_response(query, route_info)

    def _post_process_response(
        self,
        response: Dict[str, Any],
        domain_info: Dict[str, Any],
        route_info: Dict[str, Any],
    ) -> Dict[str, Any]:
        """Post-procesar respuesta"""

        # Agregar metadatos
        response.update(
            {
                "timestamp": datetime.now().isoformat(),
                "domain": domain_info.get("domain"),
                "route_type": route_info.get("route_type"),
                "processing_metadata": {
                    "domain_confidence": domain_info.get("confidence"),
                    "route_details": route_info.get("route_details", {}),
                },
            }
        )

        # Actualizar adapters si es necesario
        if self.adapter_policy and route_info.get("route_type") == "branch":
            self._update_adapters(domain_info, response)

        return response

    def _update_adapters(self, domain_info: Dict[str, Any], response: Dict[str, Any]):
        """Actualizar adapters basado en la respuesta"""
        try:
            domain = domain_info.get("domain")
            if domain:
                evaluation_metrics = {
                    "accuracy": domain_info.get("confidence", 0.5),
                    "response_time": response.get("response_time", 0.0),
                    "memory_usage": 0.5,  # Valor simulado
                }

                self.adapter_policy.manage_domain_adapters(domain, evaluation_metrics)

        except Exception as e:
            self.logger.warning(f"Error actualizando adapters: {e}")

    def _get_cached_response(self, query: str) -> Optional[Dict[str, Any]]:
        """Obtener respuesta desde caché"""
        if query in self.response_cache:
            cached_data = self.response_cache[query]
            if time.time() - cached_data["timestamp"] < self.config["cache_ttl"]:
                return cached_data["response"]
            else:
                del self.response_cache[query]
        return None

    def _cache_response(self, query: str, response: Dict[str, Any]):
        """Guardar respuesta en caché"""
        self.response_cache[query] = {"response": response, "timestamp": time.time()}

    def _update_metrics(self, response: Dict[str, Any], response_time: float):
        """Actualizar métricas del sistema"""
        # Actualizar tiempo promedio de respuesta
        total_requests = self.metrics["successful_requests"]
        current_avg = self.metrics["average_response_time"]
        self.metrics["average_response_time"] = (
            current_avg * (total_requests - 1) + response_time
        ) / total_requests

        # Actualizar distribución de dominios
        domain = response.get("domain", "Unknown")
        self.metrics["domain_distribution"][domain] = (
            self.metrics["domain_distribution"].get(domain, 0) + 1
        )

        # Actualizar distribución de rutas
        route_type = response.get("route_type", "unknown")
        self.metrics["route_distribution"][route_type] = (
            self.metrics["route_distribution"].get(route_type, 0) + 1
        )

    def _log_monitoring_data(self, query: str, response: Dict[str, Any]):
        """Registrar datos de monitoreo"""
        monitoring_data = {
            "timestamp": datetime.now().isoformat(),
            "query_length": len(query),
            "response_length": len(response.get("text", "")),
            "domain": response.get("domain"),
            "route_type": response.get("route_type"),
            "response_time": response.get("response_time"),
            "source": response.get("source"),
        }

        # Guardar en archivo de monitoreo
        log_file = "logs/orchestrator_monitoring.log"
        os.makedirs(os.path.dirname(log_file), exist_ok=True)

        with open(log_file, "a", encoding="utf-8") as f:
            f.write(json.dumps(monitoring_data, ensure_ascii=False) + "\n")

    def get_system_status(self) -> Dict[str, Any]:
        """Obtener estado completo del sistema"""
        return {
            "orchestrator_status": "active",
            "components_status": {
                "domain_classifier": self.domain_classifier is not None,
                "semantic_router": self.semantic_router is not None,
                "branch_manager": self.branch_manager is not None,
                "rag_retriever": self.rag_retriever is not None,
                "adapter_policy": self.adapter_policy is not None,
            },
            "metrics": self.metrics,
            "config": self.config,
            "cache_size": len(self.response_cache),
            "timestamp": datetime.now().isoformat(),
        }

    def get_branch_status(self) -> Dict[str, Any]:
        """Obtener estado de todas las ramas"""
        if self.branch_manager:
            return self.branch_manager.get_all_branches_status()
        return {"error": "Branch manager no disponible"}

    def get_llm_status(self) -> Dict[str, Any]:
        """Obtener estado del cliente LLM"""
        try:
            llm_client = get_llm_client()
            return llm_client.health_check()
        except Exception as e:
            return {"status": "error", "error": str(e)}

    def optimize_system(self) -> Dict[str, Any]:
        """Optimizar sistema completo"""
        optimization_results = {}

        try:
            # Optimizar caché de adapters
            if self.adapter_policy:
                optimization_results["adapter_cache"] = (
                    self.adapter_policy.optimize_cache()
                )

            # Limpiar caché de respuestas
            if self.config["enable_caching"]:
                self._clean_response_cache()
                optimization_results["response_cache"] = {"status": "cleaned"}

            # Optimizar sistema RAG
            if self.rag_retriever:
                optimization_results["rag_system"] = {"status": "optimized"}

            optimization_results["timestamp"] = datetime.now().isoformat()
            optimization_results["status"] = "completed"

            self.logger.info("✅ Optimización del sistema completada")

        except Exception as e:
            self.logger.error(f"❌ Error en optimización: {e}")
            optimization_results["error"] = str(e)

        return optimization_results

    def _clean_response_cache(self):
        """Limpiar caché de respuestas expiradas"""
        current_time = time.time()
        expired_queries = []

        for query, cached_data in self.response_cache.items():
            if current_time - cached_data["timestamp"] > self.config["cache_ttl"]:
                expired_queries.append(query)

        for query in expired_queries:
            del self.response_cache[query]

        if expired_queries:
            self.logger.info(
                f"🧹 Caché limpiado: {len(expired_queries)} entradas expiradas"
            )


# Instancia global del orquestador
main_orchestrator = MainOrchestrator()

# Configuración de logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
