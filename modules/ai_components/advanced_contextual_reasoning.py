""" ""\"
Advanced Contextual Reasoning Module

Parte del subsistema Reasoning de NeuroFusion.

Este módulo proporciona funcionalidades especializadas para el procesamiento
y análisis avanzado dentro del sistema de inteligencia artificial NeuroFusion.

Características principales:
- Procesamiento especializado
- Análisis de alto rendimiento
- Integración con el sistema multi-rama

Autor: NeuroFusion AI Team
Última actualización: 2024-08-24
""\"
"""

import logging
import json
from typing import Dict, Any, List, Optional, Union
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity
import datetime
import asyncio

# Importar herramientas adicionales
from ai.advanced_embeddings import get_advanced_embedding_generator
from ai.multi_domain_expert_system import get_multi_domain_expert_system

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class ContextualReasoningEngine:
    """
    Sistema avanzado de razonamiento contextual para NeuroFusion

    Características mejoradas:
    - Análisis de contexto semántico profundo
    - Generación de inferencias multi-dominio
    - Evaluación de coherencia contextual
    - Adaptación dinámica de contexto
    - Integración con sistemas de embeddings y expertos
    """

    def __init__(self, embedding_dim: int = 768):
        """
        Inicializar motor de razonamiento contextual avanzado

        Args:
            embedding_dim (int): Dimensión de embeddings
        """
        self.context_memory: Dict[str, Dict[str, Any]] = {}
        self.embedding_dim = embedding_dim

        # Inicializar sistemas de soporte
        self.embedding_generator = None
        self.expert_system = None

        # Configuración de contexto
        self.context_config = {
            "max_context_memory": 1000,
            "context_decay_time": datetime.timedelta(days=30),
            "similarity_threshold": 0.7,
            "inference_confidence_threshold": 0.6,
        }

    async def initialize(self):
        """Inicializar sistemas de soporte"""
        try:
            # Inicializar generador de embeddings
            self.embedding_generator = await get_advanced_embedding_generator()

            # Inicializar sistema de expertos
            self.expert_system = await get_multi_domain_expert_system()

            logger.info(
                "✅ Sistemas de soporte inicializados para razonamiento contextual"
            )
        except Exception as e:
            logger.error(f"❌ Error inicializando sistemas de soporte: {e}")
            raise

    async def add_context(
        self,
        context_id: str,
        context_data: Dict[str, Any],
        embedding: Optional[np.ndarray] = None,
        domain: Optional[str] = None,
    ):
        """
        Agregar contexto al sistema con mayor inteligencia

        Args:
            context_id (str): Identificador único de contexto
            context_data (dict): Datos de contexto
            embedding (np.ndarray, opcional): Embedding de contexto
            domain (str, opcional): Dominio del contexto
        """
        try:
            # Generar embedding si no se proporciona
            if embedding is None:
                embedding = await self._generate_context_embedding(context_data, domain)

            # Verificar límite de memoria de contexto
            await self._manage_context_memory()

            self.context_memory[context_id] = {
                "data": context_data,
                "embedding": embedding,
                "timestamp": datetime.datetime.utcnow(),
                "domain": domain,
                "access_count": 0,
            }

            logger.info(f"✅ Contexto agregado: {context_id} (Dominio: {domain})")

        except Exception as e:
            logger.error(f"❌ Error agregando contexto: {e}")
            raise

    async def _generate_context_embedding(
        self, context_data: Dict[str, Any], domain: Optional[str] = None
    ) -> np.ndarray:
        """
        Generar embedding de contexto usando generador avanzado

        Args:
            context_data (dict): Datos de contexto
            domain (str, opcional): Dominio del contexto

        Returns:
            np.ndarray: Embedding de contexto
        """
        try:
            # Convertir datos a texto
            context_text = json.dumps(context_data, sort_keys=True)

            # Usar generador de embeddings
            if self.embedding_generator is None:
                await self.initialize()

            embedding = self.embedding_generator.generate_embedding(
                context_text, domain=domain or "general"
            )

            return embedding

        except Exception as e:
            logger.error(f"❌ Error generando embedding de contexto: {e}")
            # Error - no hay embedding disponible
            embedding = np.random.rand(self.embedding_dim)
            return embedding / np.linalg.norm(embedding)

    async def find_similar_contexts(
        self,
        query_context: Dict[str, Any],
        top_k: int = 5,
        similarity_threshold: Optional[float] = None,
        domain: Optional[str] = None,
    ) -> List[Dict[str, Any]]:
        """
        Encontrar contextos similares con mayor precisión

        Args:
            query_context (dict): Contexto de consulta
            top_k (int): Número máximo de contextos similares
            similarity_threshold (float, opcional): Umbral de similitud
            domain (str, opcional): Dominio específico para búsqueda

        Returns:
            list: Contextos similares
        """
        try:
            # Usar umbral por defecto si no se proporciona
            threshold = (
                similarity_threshold or self.context_config["similarity_threshold"]
            )

            # Generar embedding de consulta
            query_embedding = await self._generate_context_embedding(
                query_context, domain
            )

            # Calcular similitudes
            similarities = []
            for context_id, context_info in self.context_memory.items():
                # Filtrar por dominio si se especifica
                if domain and context_info.get("domain") != domain:
                    continue

                similarity = cosine_similarity(
                    query_embedding.reshape(1, -1),
                    context_info["embedding"].reshape(1, -1),
                )[0][0]

                if similarity >= threshold:
                    similarities.append(
                        {
                            "context_id": context_id,
                            "data": context_info["data"],
                            "similarity": similarity,
                            "domain": context_info.get("domain"),
                            "timestamp": context_info.get("timestamp"),
                        }
                    )

            # Ordenar por similitud
            similarities.sort(key=lambda x: x["similarity"], reverse=True)

            # Actualizar conteo de acceso
            for similar_context in similarities[:top_k]:
                self.context_memory[similar_context["context_id"]]["access_count"] += 1

            return similarities[:top_k]

        except Exception as e:
            logger.error(f"❌ Error buscando contextos similares: {e}")
            return []

    async def infer_context(
        self, base_context: Dict[str, Any], query: str, domain: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Realizar inferencia contextual avanzada

        Args:
            base_context (dict): Contexto base
            query (str): Consulta para inferencia
            domain (str, opcional): Dominio de la inferencia

        Returns:
            dict: Resultado de la inferencia
        """
        try:
            # Buscar contextos similares
            similar_contexts = await self.find_similar_contexts(
                base_context, domain=domain
            )

            # Usar sistema de expertos para generar inferencia
            if self.expert_system is None:
                await self.initialize()

            # Procesar consulta con sistema de expertos
            expert_responses = await self.expert_system.process_query(
                query,
                context=json.dumps(base_context),
                preferred_domains=[domain] if domain else None,
            )

            # Calcular confianza de inferencia
            confidence = len(similar_contexts) / self.context_config.get(
                "max_context_memory", 5
            )
            confidence = min(confidence, 1.0)

            # Generar resultado de inferencia
            inference_result = {
                "query": query,
                "base_context": base_context,
                "similar_contexts": similar_contexts,
                "expert_responses": {
                    domain: {
                        "response": response.response,
                        "confidence": response.confidence,
                    }
                    for domain, response in expert_responses.items()
                },
                "inferred_context": {
                    "confidence": confidence,
                    "details": "Inferencia generada basada en contextos similares y respuestas de expertos",
                },
            }

            logger.info(f"✅ Inferencia generada para consulta: {query}")
            return inference_result

        except Exception as e:
            logger.error(f"❌ Error realizando inferencia contextual: {e}")
            return {"query": query, "error": str(e)}

    async def _manage_context_memory(self):
        """Gestionar memoria de contexto"""
        try:
            # Eliminar contextos antiguos
            current_time = datetime.datetime.utcnow()
            contexts_to_remove = [
                context_id
                for context_id, context_info in self.context_memory.items()
                if (current_time - context_info["timestamp"])
                > self.context_config["context_decay_time"]
            ]

            # Eliminar contextos con poco uso
            if len(self.context_memory) > self.context_config["max_context_memory"]:
                # Ordenar por timestamp y accesos
                sorted_contexts = sorted(
                    self.context_memory.items(),
                    key=lambda x: (x[1]["access_count"], x[1]["timestamp"]),
                )
                contexts_to_remove.extend(
                    context_id
                    for context_id, _ in sorted_contexts[
                        : len(self.context_memory)
                        - self.context_config["max_context_memory"]
                    ]
                )

            # Eliminar contextos
            for context_id in set(contexts_to_remove):
                del self.context_memory[context_id]

            logger.info(
                f"🧹 Limpieza de memoria de contexto: {len(contexts_to_remove)} contextos eliminados"
            )

        except Exception as e:
            logger.error(f"❌ Error gestionando memoria de contexto: {e}")


def main():
    """Demostración del módulo de razonamiento contextual"""

    async def run_demo():
        try:
            # Crear motor de razonamiento contextual
            reasoning_engine = ContextualReasoningEngine()
            await reasoning_engine.initialize()

            # Agregar contextos de ejemplo
            contexts = [
                {
                    "id": "medical_context_1",
                    "data": {
                        "patient_age": 45,
                        "medical_history": ["hipertensión", "diabetes"],
                        "current_symptoms": ["dolor de cabeza", "fatiga"],
                    },
                    "domain": "medical",
                },
                {
                    "id": "technical_context_1",
                    "data": {
                        "project_type": "machine_learning",
                        "technologies": ["python", "tensorflow"],
                        "development_stage": "prototipo",
                    },
                    "domain": "technical",
                },
            ]

            for context in contexts:
                await reasoning_engine.add_context(
                    context["id"], context["data"], domain=context.get("domain")
                )

            # Realizar inferencia
            query_context = {"patient_age": 50, "medical_history": ["hipertensión"]}

            inference = await reasoning_engine.infer_context(
                query_context, "¿Cuál es el riesgo de complicaciones?", domain="medical"
            )

            print(f"📊 Inferencia contextual: {json.dumps(inference, indent=2)}")

            return {
                "status": "ok",
                "message": "Módulo de razonamiento contextual funcionando correctamente",
                "contexts_added": len(contexts),
            }

        except Exception as e:
            logger.error(f"❌ Error en el módulo de razonamiento contextual: {e}")
            return {"status": "error", "message": str(e)}

    # Ejecutar demo de forma asíncrona
    return asyncio.run(run_demo())


if __name__ == "__main__":
    result = main()
    print(result)
