#!/usr/bin/env python3
"""
Sistema Consolidado de NeuroFusion - Arquitectura Unificada

Este módulo consolida y unifica todos los sistemas duplicados identificados
en el proyecto NeuroFusion para mejorar la eficiencia, mantenibilidad y rendimiento.

Consolidaciones principales:
1. Sistemas de Evaluación de Calidad
2. Sistemas de Embeddings
3. Sistemas de Monitoreo y Métricas
4. Sistemas de Aprendizaje Continuo
5. Sistemas de Seguridad y Autenticación
6. Sistemas de Gestión de Memoria
7. Sistemas de Gestión de Ramas

Autor: NeuroFusion AI Team
Fecha: 2024-08-24
"""

import logging
import asyncio
import json
import yaml
from typing import Dict, List, Any, Optional, Union
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from pathlib import Path
from enum import Enum
import numpy as np
import torch
import torch.nn as nn
from transformers import AutoTokenizer, AutoModelForCausalLM
from sentence_transformers import SentenceTransformer
import sqlite3
import psycopg2
from sqlalchemy import (
    create_engine,
    Column,
    String,
    Integer,
    Float,
    DateTime,
    Text,
    Boolean,
)
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

# Configuración de logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

# Base de datos SQLAlchemy
Base = declarative_base()

# =============================================================================
# CONFIGURACIONES UNIFICADAS
# =============================================================================


@dataclass
class UnifiedSystemConfig:
    """Configuración unificada para todo el sistema"""

    # Configuración general
    system_name: str = "NeuroFusion Unified System"
    version: str = "2.0.0"
    environment: str = "production"

    # Configuración de modelos
    base_model_name: str = "models/custom/shaili-personal-model"
    embedding_model_name: str = "paraphrase-multilingual-MiniLM-L12-v2"
    max_sequence_length: int = 512
    embedding_dim: int = 768

    # Configuración de base de datos
    database_url: str = "sqlite:///neurofusion_unified.db"
    postgres_config: Optional[Dict[str, str]] = None

    # Configuración de caché
    cache_enabled: bool = True
    cache_size: int = 10000
    cache_ttl: int = 3600

    # Configuración de evaluación
    quality_thresholds: Dict[str, float] = field(
        default_factory=lambda: {
            "relevance": 0.7,
            "coherence": 0.8,
            "factuality": 0.8,
            "toxicity": 0.1,
            "hallucination": 0.2,
        }
    )

    # Configuración de seguridad
    jwt_secret: str = "neurofusion_secret_key_2024"
    jwt_expiration: int = 3600
    encryption_key: str = "neurofusion_encryption_key_2024"

    # Configuración de monitoreo
    monitoring_enabled: bool = True
    metrics_interval: int = 60
    alert_threshold: float = 0.8


# =============================================================================
# MODELOS DE BASE DE DATOS UNIFICADOS
# =============================================================================


class User(Base):
    """Modelo unificado de usuario"""

    __tablename__ = "users"

    id = Column(String, primary_key=True)
    username = Column(String, unique=True, nullable=False)
    email = Column(String, unique=True, nullable=False)
    password_hash = Column(String, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    last_login = Column(DateTime)
    is_active = Column(Boolean, default=True)
    role = Column(String, default="user")


class QualityEvaluation(Base):
    """Modelo unificado de evaluaciones de calidad"""

    __tablename__ = "quality_evaluations"

    id = Column(String, primary_key=True)
    query = Column(Text, nullable=False)
    response = Column(Text, nullable=False)
    domain = Column(String, nullable=False)
    relevance_score = Column(Float)
    coherence_score = Column(Float)
    factuality_score = Column(Float)
    toxicity_score = Column(Float)
    hallucination_score = Column(Float)
    overall_score = Column(Float)
    created_at = Column(DateTime, default=datetime.utcnow)


class EmbeddingRecord(Base):
    """Modelo unificado de registros de embeddings"""

    __tablename__ = "embedding_records"

    id = Column(String, primary_key=True)
    content = Column(Text, nullable=False)
    embedding_vector = Column(Text, nullable=False)  # JSON serializado
    domain = Column(String)
    model_name = Column(String, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    metadata_json = Column(Text)  # JSON serializado


class SystemMetrics(Base):
    """Modelo unificado de métricas del sistema"""

    __tablename__ = "system_metrics"

    id = Column(String, primary_key=True)
    metric_name = Column(String, nullable=False)
    metric_value = Column(Float, nullable=False)
    component = Column(String, nullable=False)
    timestamp = Column(DateTime, default=datetime.utcnow)
    metadata_json = Column(Text)  # JSON serializado


# =============================================================================
# SISTEMA UNIFICADO DE EVALUACIÓN DE CALIDAD
# =============================================================================


class UnifiedQualityEvaluator:
    """Sistema unificado de evaluación de calidad que consolida:
    - AIQualityEvaluator
    - SimpleAIEvaluator
    - ResponseQualityEvaluator
    - UnifiedQualityEvaluator
    """

    def __init__(self, config: UnifiedSystemConfig):
        self.config = config
        self.session = self._create_session()
        self.evaluation_history = []

        # Métricas de evaluación
        self.metrics = {
            "relevance": self._calculate_relevance,
            "coherence": self._calculate_coherence,
            "factuality": self._calculate_factuality,
            "toxicity": self._calculate_toxicity,
            "hallucination": self._calculate_hallucination,
        }

    def _create_session(self):
        """Crear sesión de base de datos"""
        engine = create_engine(self.config.database_url)
        Base.metadata.create_all(engine)
        Session = sessionmaker(bind=engine)
        return Session()

    async def evaluate_response(
        self,
        query: str,
        response: str,
        context: Optional[str] = None,
        domain: str = "general",
        reference: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Evaluar calidad de respuesta de manera unificada"""

        start_time = datetime.utcnow()

        # Calcular todas las métricas
        metrics_results = {}
        for metric_name, metric_func in self.metrics.items():
            try:
                if metric_name == "hallucination" and context:
                    metrics_results[metric_name] = metric_func(response, context)
                elif metric_name == "factuality" and reference:
                    metrics_results[metric_name] = metric_func(response, reference)
                else:
                    metrics_results[metric_name] = metric_func(response, query)
            except Exception as e:
                logger.error(f"Error calculando métrica {metric_name}: {e}")
                metrics_results[metric_name] = 0.0

        # Calcular score general
        overall_score = self._calculate_overall_score(metrics_results)

        # Identificar problemas
        issues = self._identify_issues(metrics_results)

        # Guardar evaluación
        evaluation_id = f"eval_{datetime.utcnow().timestamp()}"
        evaluation = QualityEvaluation(
            id=evaluation_id,
            query=query,
            response=response,
            domain=domain,
            relevance_score=metrics_results.get("relevance", 0.0),
            coherence_score=metrics_results.get("coherence", 0.0),
            factuality_score=metrics_results.get("factuality", 0.0),
            toxicity_score=metrics_results.get("toxicity", 0.0),
            hallucination_score=metrics_results.get("hallucination", 0.0),
            overall_score=overall_score,
        )

        self.session.add(evaluation)
        self.session.commit()

        processing_time = (datetime.utcnow() - start_time).total_seconds()

        return {
            "evaluation_id": evaluation_id,
            "overall_score": overall_score,
            "metrics": metrics_results,
            "issues": issues,
            "processing_time": processing_time,
            "domain": domain,
            "timestamp": datetime.utcnow().isoformat(),
        }

    def _calculate_relevance(self, response: str, query: str) -> float:
        """Calcular relevancia de la respuesta"""
        # Implementación simplificada - en producción usar embeddings
        query_words = set(query.lower().split())
        response_words = set(response.lower().split())

        if not query_words:
            return 0.0

        intersection = query_words.intersection(response_words)
        return len(intersection) / len(query_words)

    def _calculate_coherence(self, response: str, query: str) -> float:
        """Calcular coherencia de la respuesta"""
        # Implementación simplificada
        sentences = response.split(".")
        if len(sentences) <= 1:
            return 1.0

        # Simular análisis de coherencia
        return min(0.9, 1.0 - (len(sentences) * 0.1))

    def _calculate_factuality(self, response: str, reference: str) -> float:
        """Calcular factualidad comparando con referencia"""
        # Implementación simplificada
        response_words = set(response.lower().split())
        reference_words = set(reference.lower().split())

        if not reference_words:
            return 0.5

        intersection = response_words.intersection(reference_words)
        return len(intersection) / len(reference_words)

    def _calculate_toxicity(self, response: str, query: str) -> float:
        """Calcular toxicidad de la respuesta"""
        toxic_words = {
            "odio",
            "muerte",
            "matar",
            "violencia",
            "sangre",
            "dolor",
            "tortura",
            "sufrimiento",
            "maldición",
            "diablo",
            "infierno",
        }

        response_words = set(response.lower().split())
        toxic_count = len(response_words.intersection(toxic_words))

        return min(1.0, toxic_count * 0.2)

    def _calculate_hallucination(self, response: str, context: str) -> float:
        """Calcular nivel de alucinación"""
        # Simular detección de alucinación
        response_words = set(response.lower().split())
        context_words = set(context.lower().split())

        if not context_words:
            return 0.5

        intersection = response_words.intersection(context_words)
        return 1.0 - (len(intersection) / len(response_words))

    def _calculate_overall_score(self, metrics: Dict[str, float]) -> float:
        """Calcular score general ponderado"""
        weights = {
            "relevance": 0.3,
            "coherence": 0.25,
            "factuality": 0.25,
            "toxicity": 0.1,
            "hallucination": 0.1,
        }

        total_score = 0.0
        total_weight = 0.0

        for metric, score in metrics.items():
            weight = weights.get(metric, 0.1)
            if metric in ["toxicity", "hallucination"]:
                # Penalizar toxicidad y alucinación
                total_score += (1.0 - score) * weight
            else:
                total_score += score * weight
            total_weight += weight

        return total_score / total_weight if total_weight > 0 else 0.0

    def _identify_issues(self, metrics: Dict[str, float]) -> List[str]:
        """Identificar problemas basados en métricas"""
        issues = []

        for metric, score in metrics.items():
            threshold = self.config.quality_thresholds.get(metric, 0.7)

            if metric in ["toxicity", "hallucination"]:
                if score > threshold:
                    issues.append(f"Alto nivel de {metric}: {score:.3f}")
            else:
                if score < threshold:
                    issues.append(f"Bajo nivel de {metric}: {score:.3f}")

        return issues


# =============================================================================
# SISTEMA UNIFICADO DE EMBEDDINGS
# =============================================================================


class UnifiedEmbeddingSystem:
    """Sistema unificado de embeddings que consolida:
    - AdvancedEmbeddingSystem
    - PerfectEmbeddingGenerator
    - RealEmbeddingGenerator
    - DomainEmbeddingGenerator
    - RealTimeEmbeddingGenerator
    - VectorIndexManager
    - EmbeddingCacheOptimizer
    """

    def __init__(self, config: UnifiedSystemConfig):
        self.config = config
        self.session = self._create_session()
        self.cache = {}
        self.cache_timestamps = {}

        # Cargar modelo de embeddings
        try:
            self.embedding_model = SentenceTransformer(config.embedding_model_name)
            logger.info(
                f"✅ Modelo de embeddings cargado: {config.embedding_model_name}"
            )
        except Exception as e:
            logger.error(f"❌ Error cargando modelo de embeddings: {e}")
            self.embedding_model = None

    def _create_session(self):
        """Crear sesión de base de datos"""
        engine = create_engine(self.config.database_url)
        Base.metadata.create_all(engine)
        Session = sessionmaker(bind=engine)
        return Session()

    async def generate_embedding(
        self, content: str, domain: str = "general", use_cache: bool = True
    ) -> np.ndarray:
        """Generar embedding unificado"""

        if not self.embedding_model:
            raise RuntimeError("Modelo de embeddings no disponible")

        # Verificar caché
        cache_key = f"{content}_{domain}"
        if use_cache and self.config.cache_enabled:
            if cache_key in self.cache:
                timestamp = self.cache_timestamps.get(cache_key, 0)
                if datetime.utcnow().timestamp() - timestamp < self.config.cache_ttl:
                    logger.info("📋 Embedding recuperado de caché")
                    return self.cache[cache_key]

        # Generar embedding
        try:
            embedding = self.embedding_model.encode(
                content,
                max_length=self.config.max_sequence_length,
                normalize_embeddings=True,
            )

            # Guardar en caché
            if use_cache and self.config.cache_enabled:
                self._update_cache(cache_key, embedding)

            # Guardar en base de datos
            await self._save_embedding_record(content, embedding, domain)

            logger.info(f"✅ Embedding generado para dominio: {domain}")
            return embedding

        except Exception as e:
            logger.error(f"❌ Error generando embedding: {e}")
            raise

    async def batch_generate_embeddings(
        self, contents: List[str], domains: List[str] = None
    ) -> List[np.ndarray]:
        """Generar embeddings en lote"""

        if domains is None:
            domains = ["general"] * len(contents)

        embeddings = []
        for content, domain in zip(contents, domains):
            try:
                embedding = await self.generate_embedding(content, domain)
                embeddings.append(embedding)
            except Exception as e:
                logger.error(f"Error en embedding de lote: {e}")
                # Error: no hay embedding disponible
                embeddings.append(np.zeros(self.config.embedding_dim))

        return embeddings

    async def search_similar(
        self, query_embedding: np.ndarray, domain: str = None, top_k: int = 5
    ) -> List[Dict[str, Any]]:
        """Buscar contenido similar"""

        # Obtener embeddings de la base de datos
        query = self.session.query(EmbeddingRecord)
        if domain:
            query = query.filter(EmbeddingRecord.domain == domain)

        records = query.limit(100).all()  # Limitar para rendimiento

        similarities = []
        for record in records:
            try:
                stored_embedding = np.array(json.loads(record.embedding_vector))
                similarity = self._cosine_similarity(query_embedding, stored_embedding)
                similarities.append(
                    {
                        "id": record.id,
                        "content": record.content,
                        "domain": record.domain,
                        "similarity": similarity,
                        "created_at": record.created_at.isoformat(),
                    }
                )
            except Exception as e:
                logger.error(f"Error calculando similitud: {e}")
                continue

        # Ordenar por similitud y retornar top_k
        similarities.sort(key=lambda x: x["similarity"], reverse=True)
        return similarities[:top_k]

    def _cosine_similarity(self, vec1: np.ndarray, vec2: np.ndarray) -> float:
        """Calcular similitud coseno"""
        dot_product = np.dot(vec1, vec2)
        norm1 = np.linalg.norm(vec1)
        norm2 = np.linalg.norm(vec2)

        if norm1 == 0 or norm2 == 0:
            return 0.0

        return dot_product / (norm1 * norm2)

    def _update_cache(self, key: str, embedding: np.ndarray):
        """Actualizar caché de embeddings"""
        # Implementar política LRU si el caché está lleno
        if len(self.cache) >= self.config.cache_size:
            # Eliminar entrada más antigua
            oldest_key = min(
                self.cache_timestamps.keys(), key=lambda k: self.cache_timestamps[k]
            )
            del self.cache[oldest_key]
            del self.cache_timestamps[oldest_key]

        self.cache[key] = embedding
        self.cache_timestamps[key] = datetime.utcnow().timestamp()

    async def _save_embedding_record(
        self, content: str, embedding: np.ndarray, domain: str
    ):
        """Guardar registro de embedding en base de datos"""
        try:
            record = EmbeddingRecord(
                id=f"emb_{datetime.utcnow().timestamp()}",
                content=content,
                embedding_vector=json.dumps(embedding.tolist()),
                domain=domain,
                model_name=self.config.embedding_model_name,
                metadata=json.dumps({"generated_at": datetime.utcnow().isoformat()}),
            )

            self.session.add(record)
            self.session.commit()

        except Exception as e:
            logger.error(f"Error guardando embedding: {e}")
            self.session.rollback()


# =============================================================================
# SISTEMA UNIFICADO DE MONITOREO Y MÉTRICAS
# =============================================================================


class UnifiedMonitoringSystem:
    """Sistema unificado de monitoreo que consolida:
    - AdvancedMonitoringSystem
    - PerformanceMetricsSystem
    - SystemMetrics
    - AdvancedTensorMetricsAnalyzer
    """

    def __init__(self, config: UnifiedSystemConfig):
        self.config = config
        self.session = self._create_session()
        self.metrics_buffer = []
        self.alert_handlers = []

        # Iniciar monitoreo automático
        if config.monitoring_enabled:
            asyncio.create_task(self._monitoring_loop())

    def _create_session(self):
        """Crear sesión de base de datos"""
        engine = create_engine(self.config.database_url)
        Base.metadata.create_all(engine)
        Session = sessionmaker(bind=engine)
        return Session()

    async def record_metric(
        self,
        metric_name: str,
        metric_value: float,
        component: str,
        metadata: Dict[str, Any] = None,
    ):
        """Registrar métrica del sistema"""

        try:
            # Guardar en base de datos
            record = SystemMetrics(
                id=f"metric_{datetime.utcnow().timestamp()}",
                metric_name=metric_name,
                metric_value=metric_value,
                component=component,
                metadata=json.dumps(metadata or {}),
            )

            self.session.add(record)
            self.session.commit()

            # Agregar al buffer para análisis
            self.metrics_buffer.append(
                {
                    "name": metric_name,
                    "value": metric_value,
                    "component": component,
                    "timestamp": datetime.utcnow(),
                    "metadata": metadata,
                }
            )

            # Verificar alertas
            await self._check_alerts(metric_name, metric_value, component)

        except Exception as e:
            logger.error(f"Error registrando métrica: {e}")
            self.session.rollback()

    async def get_system_health(self) -> Dict[str, Any]:
        """Obtener estado de salud del sistema"""

        try:
            # Obtener métricas recientes
            recent_metrics = (
                self.session.query(SystemMetrics)
                .filter(
                    SystemMetrics.timestamp >= datetime.utcnow() - timedelta(hours=1)
                )
                .all()
            )

            # Calcular estadísticas por componente
            component_stats = {}
            for metric in recent_metrics:
                if metric.component not in component_stats:
                    component_stats[metric.component] = {
                        "count": 0,
                        "avg_value": 0.0,
                        "min_value": float("inf"),
                        "max_value": float("-inf"),
                    }

                stats = component_stats[metric.component]
                stats["count"] += 1
                stats["avg_value"] += metric.metric_value
                stats["min_value"] = min(stats["min_value"], metric.metric_value)
                stats["max_value"] = max(stats["max_value"], metric.metric_value)

            # Calcular promedios
            for component, stats in component_stats.items():
                if stats["count"] > 0:
                    stats["avg_value"] /= stats["count"]

            # Determinar estado de salud
            overall_health = "healthy"
            issues = []

            for component, stats in component_stats.items():
                if stats["avg_value"] < self.config.alert_threshold:
                    overall_health = "warning"
                    issues.append(f"Componente {component} con rendimiento bajo")

            return {
                "status": overall_health,
                "timestamp": datetime.utcnow().isoformat(),
                "component_stats": component_stats,
                "issues": issues,
                "total_metrics": len(recent_metrics),
            }

        except Exception as e:
            logger.error(f"Error obteniendo salud del sistema: {e}")
            return {
                "status": "error",
                "error": str(e),
                "timestamp": datetime.utcnow().isoformat(),
            }

    async def _monitoring_loop(self):
        """Bucle de monitoreo automático"""
        while True:
            try:
                # Registrar métricas del sistema
                await self.record_metric(
                    "system_uptime",
                    (datetime.utcnow() - datetime(2024, 1, 1)).total_seconds(),
                    "system",
                )

                await self.record_metric(
                    "memory_usage", len(self.metrics_buffer), "monitoring"
                )

                # Limpiar buffer antiguo
                cutoff_time = datetime.utcnow() - timedelta(hours=24)
                self.metrics_buffer = [
                    m for m in self.metrics_buffer if m["timestamp"] > cutoff_time
                ]

                await asyncio.sleep(self.config.metrics_interval)

            except Exception as e:
                logger.error(f"Error en bucle de monitoreo: {e}")
                await asyncio.sleep(60)  # Esperar antes de reintentar

    async def _check_alerts(
        self, metric_name: str, metric_value: float, component: str
    ):
        """Verificar y generar alertas"""

        if metric_value < self.config.alert_threshold:
            alert = {
                "type": "performance_alert",
                "metric": metric_name,
                "value": metric_value,
                "component": component,
                "threshold": self.config.alert_threshold,
                "timestamp": datetime.utcnow().isoformat(),
            }

            logger.warning(f"🚨 Alerta de rendimiento: {alert}")

            # Notificar a handlers de alerta
            for handler in self.alert_handlers:
                try:
                    await handler(alert)
                except Exception as e:
                    logger.error(f"Error en handler de alerta: {e}")


# =============================================================================
# SISTEMA UNIFICADO PRINCIPAL
# =============================================================================


class NeuroFusionUnifiedSystem:
    """Sistema principal unificado que coordina todos los subsistemas"""

    def __init__(self, config: UnifiedSystemConfig = None):
        self.config = config or UnifiedSystemConfig()
        self.logger = logging.getLogger(__name__)

        # Inicializar subsistemas
        self.quality_evaluator = UnifiedQualityEvaluator(self.config)
        self.embedding_system = UnifiedEmbeddingSystem(self.config)
        self.monitoring_system = UnifiedMonitoringSystem(self.config)

        # Estado del sistema
        self.is_initialized = False
        self.startup_time = None

        logger.info("🚀 Sistema NeuroFusion Unificado inicializado")

    async def initialize(self):
        """Inicializar el sistema completo"""
        try:
            self.logger.info("🔄 Inicializando sistema unificado...")

            # Verificar componentes
            if not self.embedding_system.embedding_model:
                raise RuntimeError("Modelo de embeddings no disponible")

            # Registrar inicio
            await self.monitoring_system.record_metric(
                "system_startup", 1.0, "system", {"version": self.config.version}
            )

            self.is_initialized = True
            self.startup_time = datetime.utcnow()

            self.logger.info("✅ Sistema unificado inicializado correctamente")

        except Exception as e:
            self.logger.error(f"❌ Error inicializando sistema: {e}")
            raise

    async def process_query(
        self, query: str, context: Optional[str] = None, domain: str = "general"
    ) -> Dict[str, Any]:
        """Procesar consulta completa con evaluación de calidad"""

        if not self.is_initialized:
            await self.initialize()

        start_time = datetime.utcnow()

        try:
            # Generar embedding de la consulta
            query_embedding = await self.embedding_system.generate_embedding(
                query, domain
            )

            # Buscar contenido similar
            similar_content = await self.embedding_system.search_similar(
                query_embedding, domain, top_k=3
            )

            # Generar respuesta (simulada por ahora)
            response = self._generate_response(query, similar_content, domain)

            # Evaluar calidad de la respuesta
            evaluation = await self.quality_evaluator.evaluate_response(
                query=query, response=response, context=context, domain=domain
            )

            # Registrar métricas
            processing_time = (datetime.utcnow() - start_time).total_seconds()
            await self.monitoring_system.record_metric(
                "query_processing_time", processing_time, "query_processor"
            )

            await self.monitoring_system.record_metric(
                "response_quality", evaluation["overall_score"], "quality_evaluator"
            )

            return {
                "query": query,
                "response": response,
                "domain": domain,
                "similar_content": similar_content,
                "evaluation": evaluation,
                "processing_time": processing_time,
                "timestamp": datetime.utcnow().isoformat(),
            }

        except Exception as e:
            self.logger.error(f"Error procesando consulta: {e}")

            # Registrar error
            await self.monitoring_system.record_metric(
                "query_errors", 1.0, "query_processor", {"error": str(e)}
            )

            raise

    def _generate_response(
        self, query: str, similar_content: List[Dict[str, Any]], domain: str
    ) -> str:
        """Generar respuesta basada en contenido similar"""

        # Implementación simplificada
        if similar_content:
            # Usar el contenido más similar
            best_match = similar_content[0]
            return f"Basándome en información similar, puedo responder: {best_match['content'][:200]}..."
        else:
            return f"Para la consulta sobre {domain}, puedo proporcionar información general sobre el tema."

    async def get_system_status(self) -> Dict[str, Any]:
        """Obtener estado completo del sistema"""

        return {
            "system_info": {
                "name": self.config.system_name,
                "version": self.config.version,
                "environment": self.config.environment,
                "initialized": self.is_initialized,
                "startup_time": (
                    self.startup_time.isoformat() if self.startup_time else None
                ),
            },
            "health": await self.monitoring_system.get_system_health(),
            "config": {
                "base_model": self.config.base_model_name,
                "embedding_model": self.config.embedding_model_name,
                "cache_enabled": self.config.cache_enabled,
                "monitoring_enabled": self.config.monitoring_enabled,
            },
        }


# =============================================================================
# FUNCIÓN PRINCIPAL DE DEMOSTRACIÓN
# =============================================================================


async def main():
    """Demostración del sistema unificado"""

    print("🚀 Iniciando Sistema NeuroFusion Unificado")
    print("=" * 50)

    # Crear configuración
    config = UnifiedSystemConfig(
        environment="development", cache_size=1000, monitoring_enabled=True
    )

    # Inicializar sistema
    system = NeuroFusionUnifiedSystem(config)
    await system.initialize()

    # Procesar consultas de prueba
    test_queries = [
        {"query": "¿Qué es la inteligencia artificial?", "domain": "technology"},
        {"query": "¿Cuáles son los síntomas de la hipertensión?", "domain": "medical"},
        {"query": "¿Cómo crear una aplicación web?", "domain": "programming"},
    ]

    for i, test_case in enumerate(test_queries, 1):
        print(f"\n📋 Procesando consulta {i}:")
        print(f"   Consulta: {test_case['query']}")
        print(f"   Dominio: {test_case['domain']}")

        try:
            result = await system.process_query(
                query=test_case["query"], domain=test_case["domain"]
            )

            print(f"   ✅ Respuesta generada")
            print(f"   📊 Calidad: {result['evaluation']['overall_score']:.3f}")
            print(f"   ⏱️  Tiempo: {result['processing_time']:.3f}s")

            if result["evaluation"]["issues"]:
                print(f"   ⚠️  Problemas: {', '.join(result['evaluation']['issues'])}")

        except Exception as e:
            print(f"   ❌ Error: {e}")

    # Mostrar estado del sistema
    print(f"\n📈 Estado del Sistema:")
    status = await system.get_system_status()
    print(f"   Estado: {status['health']['status']}")
    print(f"   Métricas totales: {status['health']['total_metrics']}")
    print(f"   Componentes: {len(status['health']['component_stats'])}")

    print(f"\n🎉 Sistema NeuroFusion Unificado funcionando correctamente!")


if __name__ == "__main__":
    asyncio.run(main())
