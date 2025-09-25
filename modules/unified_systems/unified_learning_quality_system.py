"""
Sistema Unificado de Aprendizaje y Evaluación de Calidad para NeuroFusion

Este módulo combina funcionalidades de:
- Continuous Learning (continuous_learning.py)
- Consolidated Learning System (consolidated_learning_system.py)
- AI Quality Evaluator (ai_quality_evaluator.py)
- Simple AI Evaluator (simple_ai_evaluator.py)
- Unified Quality Evaluator (unified_quality_evaluator.py)
- Advanced AI System (advanced_ai_system.py)
- Performance Metrics (performance_metrics.py)
"""

import logging
import json
import time
import sqlite3
import asyncio
from datetime import datetime, timedelta
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
from typing import Dict, List, Optional, Any, Tuple, Union
from collections import defaultdict
import numpy as np
import torch
import torch.nn as nn
from sklearn.metrics.pairwise import cosine_similarity
import difflib

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class LearningMode(Enum):
    """Modos de aprendizaje"""

    CONTINUOUS = "continuous"
    BATCH = "batch"
    ADAPTIVE = "adaptive"
    REINFORCEMENT = "reinforcement"


class QualityMetric(Enum):
    """Métricas de calidad"""

    SIMILARITY = "similarity"
    COHERENCE = "coherence"
    RELEVANCE = "relevance"
    ACCURACY = "accuracy"
    TOXICITY = "toxicity"
    HALLUCINATION = "hallucination"
    COMPLETENESS = "completeness"


@dataclass
class LearningConfig:
    """Configuración del sistema de aprendizaje"""

    learning_rate: float = 0.01
    batch_size: int = 32
    max_epochs: int = 100
    early_stopping_patience: int = 10
    validation_split: float = 0.2
    enable_adaptive_learning: bool = True
    quality_threshold: float = 0.7
    performance_tracking: bool = True
    knowledge_base_size: int = 10000


@dataclass
class QualityConfig:
    """Configuración de evaluación de calidad"""

    similarity_threshold: float = 0.6
    toxicity_threshold: float = 0.1
    hallucination_threshold: float = 0.3
    coherence_threshold: float = 0.7
    relevance_threshold: float = 0.8
    completeness_threshold: float = 0.6
    enable_advanced_metrics: bool = True
    performance_tracking: bool = True


@dataclass
class LearningExperience:
    """Experiencia de aprendizaje individual"""

    id: str
    input_data: str
    target_data: str
    domain: str
    quality_score: float
    learning_mode: LearningMode
    timestamp: datetime
    metadata: Dict[str, Any] = field(default_factory=dict)
    performance_metrics: Dict[str, float] = field(default_factory=dict)


@dataclass
class QualityEvaluation:
    """Evaluación de calidad"""

    query: str
    response: str
    reference: Optional[str] = None
    context: Optional[str] = None
    domain: str = "general"
    metrics: Dict[str, float] = field(default_factory=dict)
    overall_score: float = 0.0
    issues: List[str] = field(default_factory=list)
    timestamp: datetime = field(default_factory=datetime.now)
    processing_time: float = 0.0


class UnifiedLearningQualitySystem:
    """Sistema unificado de aprendizaje y evaluación de calidad"""

    def __init__(
        self,
        learning_config: Optional[LearningConfig] = None,
        quality_config: Optional[QualityConfig] = None,
        db_path: Optional[str] = None,
    ):
        """Inicializar sistema unificado"""
        self.learning_config = learning_config or LearningConfig()
        self.quality_config = quality_config or QualityConfig()
        self.db_path = db_path or "./data/learning_quality_system.db"

        # Componentes del sistema
        self.knowledge_base: Dict[str, List[LearningExperience]] = defaultdict(list)
        self.quality_history: List[QualityEvaluation] = []
        self.performance_metrics = defaultdict(list)
        self.learning_stats = {
            "total_experiences": 0,
            "total_evaluations": 0,
            "average_quality": 0.0,
            "improvement_rate": 0.0,
        }

        # Inicializar componentes
        self._init_database()
        self._init_learning_components()
        self._init_quality_components()

        logger.info("✅ Sistema Unificado de Aprendizaje y Calidad inicializado")

    def _init_database(self):
        """Inicializar base de datos"""
        try:
            self.conn = sqlite3.connect(self.db_path)
            self._create_tables()
            logger.info("✅ Base de datos de aprendizaje y calidad inicializada")
        except Exception as e:
            logger.error(f"Error inicializando base de datos: {e}")
            # Crear directorio si no existe
            Path(self.db_path).parent.mkdir(parents=True, exist_ok=True)
            try:
                self.conn = sqlite3.connect(self.db_path)
                self._create_tables()
                logger.info("✅ Base de datos creada exitosamente")
            except Exception as e2:
                logger.error(f"Error crítico creando base de datos: {e2}")
                raise

    def _create_tables(self):
        """Crear tablas en base de datos"""
        cursor = self.conn.cursor()

        # Tabla de experiencias de aprendizaje
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS learning_experiences (
                id TEXT PRIMARY KEY,
                input_data TEXT NOT NULL,
                target_data TEXT NOT NULL,
                domain TEXT NOT NULL,
                quality_score REAL NOT NULL,
                learning_mode TEXT NOT NULL,
                timestamp TEXT NOT NULL,
                metadata TEXT,
                performance_metrics TEXT
            )
        """
        )

        # Tabla de evaluaciones de calidad
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS quality_evaluations (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                query TEXT NOT NULL,
                response TEXT NOT NULL,
                reference TEXT,
                context TEXT,
                domain TEXT NOT NULL,
                metrics TEXT NOT NULL,
                overall_score REAL NOT NULL,
                issues TEXT,
                timestamp TEXT NOT NULL,
                processing_time REAL NOT NULL
            )
        """
        )

        # Tabla de métricas de rendimiento
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS performance_metrics (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                metric_type TEXT NOT NULL,
                metric_value REAL NOT NULL,
                domain TEXT,
                timestamp TEXT NOT NULL
            )
        """
        )

        # Tabla de conocimiento consolidado
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS consolidated_knowledge (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                domain TEXT NOT NULL,
                knowledge_pattern TEXT NOT NULL,
                confidence_score REAL NOT NULL,
                usage_count INTEGER DEFAULT 0,
                last_updated TEXT NOT NULL,
                metadata TEXT
            )
        """
        )

        # Índices
        cursor.execute(
            "CREATE INDEX IF NOT EXISTS idx_domain ON learning_experiences(domain)"
        )
        cursor.execute(
            "CREATE INDEX IF NOT EXISTS idx_timestamp ON learning_experiences(timestamp)"
        )
        cursor.execute(
            "CREATE INDEX IF NOT EXISTS idx_quality_score ON learning_experiences(quality_score)"
        )
        cursor.execute(
            "CREATE INDEX IF NOT EXISTS idx_eval_domain ON quality_evaluations(domain)"
        )
        cursor.execute(
            "CREATE INDEX IF NOT EXISTS idx_eval_score ON quality_evaluations(overall_score)"
        )

        self.conn.commit()
        cursor.close()

    def _init_learning_components(self):
        """Inicializar componentes de aprendizaje"""
        self.learning_modes = {
            LearningMode.CONTINUOUS: self._continuous_learning,
            LearningMode.BATCH: self._batch_learning,
            LearningMode.ADAPTIVE: self._adaptive_learning,
            LearningMode.REINFORCEMENT: self._reinforcement_learning,
        }

        self.learning_rate = self.learning_config.learning_rate
        self.performance_history = []

    def _init_quality_components(self):
        """Inicializar componentes de calidad"""
        self.quality_metrics = {
            QualityMetric.SIMILARITY: self._calculate_similarity,
            QualityMetric.COHERENCE: self._calculate_coherence,
            QualityMetric.RELEVANCE: self._calculate_relevance,
            QualityMetric.ACCURACY: self._calculate_accuracy,
            QualityMetric.TOXICITY: self._calculate_toxicity,
            QualityMetric.HALLUCINATION: self._calculate_hallucination,
            QualityMetric.COMPLETENESS: self._calculate_completeness,
        }

    async def learn_from_experience(
        self,
        input_data: str,
        target_data: str,
        domain: str = "general",
        learning_mode: LearningMode = LearningMode.CONTINUOUS,
        quality_score: float = 0.8,
    ) -> Dict[str, Any]:
        """Aprender de una experiencia"""
        start_time = time.time()

        try:
            # Crear experiencia de aprendizaje
            experience_id = f"exp_{int(time.time() * 1000)}"
            experience = LearningExperience(
                id=experience_id,
                input_data=input_data,
                target_data=target_data,
                domain=domain,
                quality_score=quality_score,
                learning_mode=learning_mode,
                timestamp=datetime.now(),
                metadata={"source": "user_input"},
            )

            # Aplicar modo de aprendizaje
            learning_result = await self.learning_modes[learning_mode](experience)

            # Guardar experiencia
            await self._save_learning_experience(experience)

            # Actualizar conocimiento
            self._update_knowledge_base(experience, learning_result)

            # Calcular métricas de rendimiento
            processing_time = time.time() - start_time
            performance_metrics = self._calculate_learning_performance(
                experience, learning_result
            )

            # Registrar métricas
            self._log_performance_metric("learning_time", processing_time, domain)
            self._log_performance_metric("learning_quality", quality_score, domain)

            # Actualizar estadísticas
            self.learning_stats["total_experiences"] += 1
            self.learning_stats["average_quality"] = (
                self.learning_stats["average_quality"]
                * (self.learning_stats["total_experiences"] - 1)
                + quality_score
            ) / self.learning_stats["total_experiences"]

            return {
                "experience_id": experience_id,
                "learning_mode": learning_mode.value,
                "quality_score": quality_score,
                "processing_time": processing_time,
                "performance_metrics": performance_metrics,
                "knowledge_updated": True,
            }

        except Exception as e:
            logger.error(f"Error en aprendizaje: {e}")
            return {
                "error": str(e),
                "learning_mode": learning_mode.value,
                "quality_score": 0.0,
            }

    async def evaluate_quality(
        self,
        query: str,
        response: str,
        reference: Optional[str] = None,
        context: Optional[str] = None,
        domain: str = "general",
    ) -> QualityEvaluation:
        """Evaluar calidad de una respuesta"""
        start_time = time.time()

        try:
            # Calcular métricas de calidad
            metrics = {}
            issues = []

            for metric_type, metric_func in self.quality_metrics.items():
                try:
                    if metric_type == QualityMetric.SIMILARITY and reference:
                        score = metric_func(response, reference)
                    elif metric_type == QualityMetric.HALLUCINATION and context:
                        score = metric_func(response, context)
                    elif metric_type == QualityMetric.RELEVANCE:
                        score = metric_func(query, response)
                    else:
                        score = metric_func(response)

                    metrics[metric_type.value] = score

                    # Verificar umbrales
                    threshold = getattr(
                        self.quality_config, f"{metric_type.value}_threshold", 0.5
                    )
                    if score < threshold:
                        issues.append(f"{metric_type.value} baja: {score:.3f}")

                except Exception as e:
                    logger.warning(f"Error calculando métrica {metric_type.value}: {e}")
                    metrics[metric_type.value] = 0.0

            # Calcular score general
            overall_score = self._calculate_overall_quality_score(metrics)

            # Crear evaluación
            evaluation = QualityEvaluation(
                query=query,
                response=response,
                reference=reference,
                context=context,
                domain=domain,
                metrics=metrics,
                overall_score=overall_score,
                issues=issues,
                processing_time=time.time() - start_time,
            )

            # Guardar evaluación
            await self._save_quality_evaluation(evaluation)

            # Actualizar historial
            self.quality_history.append(evaluation)
            self.learning_stats["total_evaluations"] += 1

            # Registrar métricas
            self._log_performance_metric(
                "evaluation_time", evaluation.processing_time, domain
            )
            self._log_performance_metric("quality_score", overall_score, domain)

            return evaluation

        except Exception as e:
            logger.error(f"Error en evaluación de calidad: {e}")
            return QualityEvaluation(
                query=query,
                response=response,
                overall_score=0.0,
                issues=[f"Error en evaluación: {str(e)}"],
            )

    async def _continuous_learning(
        self, experience: LearningExperience
    ) -> Dict[str, Any]:
        """Aprendizaje continuo"""
        # Calcular mejora basada en la calidad de la experiencia
        base_improvement = experience.quality_score * 0.01

        # Factor de dominio
        domain_factors = {
            "technical": 1.2,
            "medical": 1.3,
            "creative": 0.9,
            "business": 1.1,
            "scientific": 1.4,
        }
        domain_factor = domain_factors.get(experience.domain, 1.0)

        # Factor de tiempo (experiencias más recientes tienen más peso)
        time_factor = (
            1.0 + (datetime.now() - experience.timestamp).total_seconds() / 86400 * 0.1
        )

        improvement = base_improvement * domain_factor * time_factor

        # Actualizar tasa de aprendizaje adaptativamente
        if self.learning_config.enable_adaptive_learning:
            if experience.quality_score > 0.8:
                self.learning_rate = max(
                    self.learning_rate * 0.95, 0.001
                )  # Reducir si la calidad es alta
            elif experience.quality_score < 0.5:
                self.learning_rate = min(
                    self.learning_rate * 1.05, 0.1
                )  # Aumentar si la calidad es baja

        # Registrar métricas de aprendizaje
        self.performance_metrics["learning_improvement"].append(improvement)
        self.performance_metrics["learning_rate_history"].append(self.learning_rate)

        return {
            "improvement": improvement,
            "learning_rate": self.learning_rate,
            "domain_factor": domain_factor,
            "time_factor": time_factor,
            "mode": "continuous",
        }

    async def _batch_learning(self, experience: LearningExperience) -> Dict[str, Any]:
        """Aprendizaje por lotes"""
        # Simular aprendizaje por lotes
        batch_improvement = np.random.uniform(0.005, 0.02)

        return {
            "improvement": batch_improvement,
            "batch_size": self.learning_config.batch_size,
            "mode": "batch",
        }

    async def _adaptive_learning(
        self, experience: LearningExperience
    ) -> Dict[str, Any]:
        """Aprendizaje adaptativo"""
        # Ajustar parámetros basado en la experiencia
        adaptive_improvement = experience.quality_score * 0.01

        # Ajustar configuración basado en el dominio
        domain_adaptation = self._get_domain_adaptation(experience.domain)

        return {
            "improvement": adaptive_improvement,
            "domain_adaptation": domain_adaptation,
            "mode": "adaptive",
        }

    async def _reinforcement_learning(
        self, experience: LearningExperience
    ) -> Dict[str, Any]:
        """Aprendizaje por refuerzo"""
        # Simular aprendizaje por refuerzo
        reward = experience.quality_score
        reinforcement_improvement = reward * 0.02

        return {
            "improvement": reinforcement_improvement,
            "reward": reward,
            "mode": "reinforcement",
        }

    def _calculate_similarity(self, response: str, reference: str) -> float:
        """Calcular similitud entre respuesta y referencia"""
        if not response or not reference:
            return 0.0

        # Normalizar textos
        response_norm = response.lower().strip()
        reference_norm = reference.lower().strip()

        # Similitud de secuencia usando difflib
        sequence_similarity = difflib.SequenceMatcher(
            None, response_norm, reference_norm
        ).ratio()

        # Similitud de palabras clave
        response_words = set(response_norm.split())
        reference_words = set(reference_norm.split())

        if not reference_words:
            return sequence_similarity

        keyword_overlap = len(response_words.intersection(reference_words)) / len(
            reference_words
        )

        # Combinar métricas (70% secuencia, 30% palabras clave)
        combined_similarity = sequence_similarity * 0.7 + keyword_overlap * 0.3

        return min(combined_similarity, 1.0)

    def _calculate_coherence(self, text: str) -> float:
        """Calcular coherencia del texto"""
        if not text:
            return 0.0

        # Métricas simples de coherencia
        sentences = text.split(".")
        if len(sentences) < 2:
            return 0.5

        # Simular coherencia basada en longitud y estructura
        coherence = min(len(text) / 100, 1.0) * 0.8 + 0.2
        return coherence

    def _calculate_relevance(self, query: str, response: str) -> float:
        """Calcular relevancia de la respuesta respecto a la consulta"""
        if not query or not response:
            return 0.0

        # Palabras clave de la consulta
        query_words = set(query.lower().split())
        response_words = set(response.lower().split())

        if not query_words:
            return 0.0

        # Calcular overlap
        overlap = len(query_words.intersection(response_words))
        relevance = overlap / len(query_words)

        return min(relevance, 1.0)

    def _calculate_accuracy(self, text: str) -> float:
        """Calcular precisión del texto"""
        if not text:
            return 0.0

        # Simular precisión basada en características del texto
        accuracy = 0.5  # Base

        # Factores que mejoran la precisión
        if len(text) > 50:
            accuracy += 0.2
        if any(
            word in text.lower()
            for word in ["según", "estudios", "investigación", "datos"]
        ):
            accuracy += 0.2
        if text.count(".") > 2:
            accuracy += 0.1

        return min(accuracy, 1.0)

    def _calculate_toxicity(self, text: str) -> float:
        """Calcular toxicidad del texto"""
        if not text:
            return 0.0

        # Lista de palabras tóxicas
        toxic_words = [
            "odio",
            "muerte",
            "matar",
            "suicidio",
            "violencia",
            "sangre",
            "dolor",
            "tortura",
            "sufrimiento",
            "maldición",
            "diablo",
            "infierno",
            "demonio",
            "asesinato",
            "crimen",
            "robo",
        ]

        text_lower = text.lower()
        toxic_count = sum(1 for word in toxic_words if word in text_lower)

        # Normalizar por longitud
        word_count = len(text.split())
        if word_count == 0:
            return 0.0

        toxicity = (toxic_count * 10) / word_count
        return min(toxicity, 1.0)

    def _calculate_hallucination(self, response: str, context: str) -> float:
        """Calcular nivel de alucinación"""
        if not response or not context:
            return 0.0

        # Simular detección de alucinación
        # En una implementación real, usar modelos más sofisticados
        response_words = set(response.lower().split())
        context_words = set(context.lower().split())

        if not response_words:
            return 0.0

        # Calcular palabras no presentes en el contexto
        hallucinated_words = response_words - context_words
        hallucination_score = len(hallucinated_words) / len(response_words)

        return min(hallucination_score, 1.0)

    def _calculate_completeness(self, text: str) -> float:
        """Calcular completitud del texto"""
        if not text:
            return 0.0

        # Métricas de completitud
        completeness = 0.3  # Base

        # Factores que mejoran la completitud
        if len(text) > 100:
            completeness += 0.3
        if text.count(".") > 3:
            completeness += 0.2
        if any(
            word in text.lower()
            for word in ["porque", "debido", "ya que", "puesto que"]
        ):
            completeness += 0.2

        return min(completeness, 1.0)

    def _calculate_overall_quality_score(self, metrics: Dict[str, float]) -> float:
        """Calcular score de calidad general"""
        if not metrics:
            return 0.0

        # Pesos para diferentes métricas
        weights = {
            "similarity": 0.25,
            "coherence": 0.20,
            "relevance": 0.20,
            "accuracy": 0.15,
            "completeness": 0.10,
            "toxicity": 0.05,  # Penalización
            "hallucination": 0.05,  # Penalización
        }

        total_score = 0.0
        total_weight = 0.0

        for metric_name, score in metrics.items():
            if metric_name in weights:
                weight = weights[metric_name]

                # Para métricas de penalización, invertir el score
                if metric_name in ["toxicity", "hallucination"]:
                    adjusted_score = 1.0 - score
                else:
                    adjusted_score = score

                total_score += adjusted_score * weight
                total_weight += weight

        return total_score / total_weight if total_weight > 0 else 0.0

    def _calculate_learning_performance(
        self, experience: LearningExperience, learning_result: Dict[str, Any]
    ) -> Dict[str, float]:
        """Calcular métricas de rendimiento del aprendizaje"""
        return {
            "improvement": learning_result.get("improvement", 0.0),
            "learning_rate": learning_result.get("learning_rate", self.learning_rate),
            "quality_score": experience.quality_score,
            "processing_efficiency": 1.0 / (1.0 + experience.quality_score),
        }

    def _get_domain_adaptation(self, domain: str) -> Dict[str, Any]:
        """Obtener adaptación específica del dominio"""
        domain_adaptations = {
            "medical": {"precision_weight": 0.8, "safety_threshold": 0.9},
            "technical": {"complexity_weight": 0.7, "accuracy_threshold": 0.8},
            "creative": {"diversity_weight": 0.6, "originality_threshold": 0.7},
            "business": {"clarity_weight": 0.8, "actionability_threshold": 0.7},
        }

        return domain_adaptations.get(domain, {"general_weight": 0.5})

    def _update_knowledge_base(
        self, experience: LearningExperience, learning_result: Dict[str, Any]
    ):
        """Actualizar base de conocimiento"""
        domain = experience.domain

        # Agregar experiencia al conocimiento
        self.knowledge_base[domain].append(experience)

        # Limitar tamaño del conocimiento por dominio
        max_experiences = self.learning_config.knowledge_base_size // len(
            self.knowledge_base
        )
        if len(self.knowledge_base[domain]) > max_experiences:
            # Mantener las experiencias más recientes y de mayor calidad
            self.knowledge_base[domain].sort(
                key=lambda x: (x.quality_score, x.timestamp), reverse=True
            )
            self.knowledge_base[domain] = self.knowledge_base[domain][:max_experiences]

    async def _save_learning_experience(self, experience: LearningExperience):
        """Guardar experiencia de aprendizaje en base de datos"""
        try:
            cursor = self.conn.cursor()

            cursor.execute(
                """
                INSERT INTO learning_experiences 
                (id, input_data, target_data, domain, quality_score, learning_mode, timestamp, metadata, performance_metrics)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
                (
                    experience.id,
                    experience.input_data,
                    experience.target_data,
                    experience.domain,
                    experience.quality_score,
                    experience.learning_mode.value,
                    experience.timestamp.isoformat(),
                    json.dumps(experience.metadata),
                    json.dumps(experience.performance_metrics),
                ),
            )

            self.conn.commit()
            cursor.close()

        except Exception as e:
            logger.error(f"Error guardando experiencia de aprendizaje: {e}")

    async def _save_quality_evaluation(self, evaluation: QualityEvaluation):
        """Guardar evaluación de calidad en base de datos"""
        try:
            cursor = self.conn.cursor()

            cursor.execute(
                """
                INSERT INTO quality_evaluations 
                (query, response, reference, context, domain, metrics, overall_score, issues, timestamp, processing_time)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
                (
                    evaluation.query,
                    evaluation.response,
                    evaluation.reference,
                    evaluation.context,
                    evaluation.domain,
                    json.dumps(evaluation.metrics),
                    evaluation.overall_score,
                    json.dumps(evaluation.issues),
                    evaluation.timestamp.isoformat(),
                    evaluation.processing_time,
                ),
            )

            self.conn.commit()
            cursor.close()

        except Exception as e:
            logger.error(f"Error guardando evaluación de calidad: {e}")

    def _log_performance_metric(
        self, metric_type: str, value: float, domain: str = "general"
    ):
        """Registrar métrica de rendimiento"""
        try:
            cursor = self.conn.cursor()

            cursor.execute(
                """
                INSERT INTO performance_metrics (metric_type, metric_value, domain, timestamp)
                VALUES (?, ?, ?, ?)
            """,
                (metric_type, value, domain, datetime.now().isoformat()),
            )

            self.conn.commit()
            cursor.close()

            # También guardar en memoria
            self.performance_metrics[metric_type].append(value)

        except Exception as e:
            logger.error(f"Error registrando métrica: {e}")

    def get_learning_stats(self, domain: Optional[str] = None) -> Dict[str, Any]:
        """Obtener estadísticas de aprendizaje"""
        try:
            cursor = self.conn.cursor()

            # Estadísticas generales
            cursor.execute("SELECT COUNT(*) FROM learning_experiences")
            total_experiences = cursor.fetchone()[0]

            cursor.execute("SELECT AVG(quality_score) FROM learning_experiences")
            avg_quality = cursor.fetchone()[0] or 0.0

            # Estadísticas por dominio
            if domain:
                cursor.execute(
                    "SELECT COUNT(*) FROM learning_experiences WHERE domain = ?",
                    (domain,),
                )
                domain_experiences = cursor.fetchone()[0]

                cursor.execute(
                    "SELECT AVG(quality_score) FROM learning_experiences WHERE domain = ?",
                    (domain,),
                )
                domain_avg_quality = cursor.fetchone()[0] or 0.0
            else:
                domain_experiences = total_experiences
                domain_avg_quality = avg_quality

            cursor.close()

            return {
                "total_experiences": total_experiences,
                "average_quality": round(avg_quality, 3),
                "domain_experiences": domain_experiences,
                "domain_average_quality": round(domain_avg_quality, 3),
                "learning_rate": self.learning_rate,
                "knowledge_base_size": sum(
                    len(exp) for exp in self.knowledge_base.values()
                ),
                "domains_covered": list(self.knowledge_base.keys()),
            }

        except Exception as e:
            logger.error(f"Error obteniendo estadísticas de aprendizaje: {e}")
            return {"error": str(e)}

    def get_quality_stats(self, domain: Optional[str] = None) -> Dict[str, Any]:
        """Obtener estadísticas de calidad"""
        try:
            cursor = self.conn.cursor()

            # Estadísticas generales
            cursor.execute("SELECT COUNT(*) FROM quality_evaluations")
            total_evaluations = cursor.fetchone()[0]

            cursor.execute("SELECT AVG(overall_score) FROM quality_evaluations")
            avg_score = cursor.fetchone()[0] or 0.0

            # Estadísticas por dominio
            if domain:
                cursor.execute(
                    "SELECT COUNT(*) FROM quality_evaluations WHERE domain = ?",
                    (domain,),
                )
                domain_evaluations = cursor.fetchone()[0]

                cursor.execute(
                    "SELECT AVG(overall_score) FROM quality_evaluations WHERE domain = ?",
                    (domain,),
                )
                domain_avg_score = cursor.fetchone()[0] or 0.0
            else:
                domain_evaluations = total_evaluations
                domain_avg_score = avg_score

            cursor.close()

            return {
                "total_evaluations": total_evaluations,
                "average_score": round(avg_score, 3),
                "domain_evaluations": domain_evaluations,
                "domain_average_score": round(domain_avg_score, 3),
                "recent_evaluations": (
                    len(self.quality_history[-100:]) if self.quality_history else 0
                ),
            }

        except Exception as e:
            logger.error(f"Error obteniendo estadísticas de calidad: {e}")
            return {"error": str(e)}

    def get_system_stats(self) -> Dict[str, Any]:
        """Obtener estadísticas generales del sistema"""
        learning_stats = self.get_learning_stats()
        quality_stats = self.get_quality_stats()

        return {
            "learning": learning_stats,
            "quality": quality_stats,
            "performance_metrics": dict(self.performance_metrics),
            "system_health": {
                "database_connected": hasattr(self, "conn"),
                "knowledge_base_size": len(self.knowledge_base),
                "quality_history_size": len(self.quality_history),
            },
        }

    def close(self):
        """Cerrar sistema"""
        try:
            if hasattr(self, "conn"):
                self.conn.close()
            logger.info("✅ Sistema de aprendizaje y calidad cerrado")
        except Exception as e:
            logger.error(f"Error cerrando sistema: {e}")


def get_unified_learning_quality_system(
    learning_config: Optional[LearningConfig] = None,
    quality_config: Optional[QualityConfig] = None,
    db_path: Optional[str] = None,
) -> UnifiedLearningQualitySystem:
    """Función factory para crear sistema unificado"""
    return UnifiedLearningQualitySystem(learning_config, quality_config, db_path)


async def main():
    """Función principal de demostración"""
    # Configurar sistema
    learning_config = LearningConfig(
        learning_rate=0.01, enable_adaptive_learning=True, quality_threshold=0.7
    )

    quality_config = QualityConfig(
        similarity_threshold=0.6, coherence_threshold=0.7, enable_advanced_metrics=True
    )

    system = get_unified_learning_quality_system(learning_config, quality_config)

    print("🚀 Sistema Unificado de Aprendizaje y Calidad")
    print("=" * 50)

    # Ejemplo de aprendizaje
    print("\n📚 Aprendizaje:")
    learning_result = await system.learn_from_experience(
        input_data="¿Qué es la inteligencia artificial?",
        target_data="La inteligencia artificial es un campo de la informática que busca crear sistemas capaces de realizar tareas que requieren inteligencia humana.",
        domain="technical",
        learning_mode=LearningMode.CONTINUOUS,
        quality_score=0.9,
    )

    print(f"   Experiencia ID: {learning_result['experience_id']}")
    print(f"   Modo: {learning_result['learning_mode']}")
    print(f"   Calidad: {learning_result['quality_score']:.3f}")
    print(f"   Tiempo: {learning_result['processing_time']:.3f}s")

    # Ejemplo de evaluación de calidad
    print("\n🔍 Evaluación de Calidad:")
    evaluation = await system.evaluate_quality(
        query="¿Qué es la inteligencia artificial?",
        response="La IA es una tecnología que permite a las máquinas aprender y tomar decisiones.",
        reference="La inteligencia artificial es un campo de la informática que busca crear sistemas capaces de realizar tareas que requieren inteligencia humana.",
        domain="technical",
    )

    print(f"   Score general: {evaluation.overall_score:.3f}")
    print(f"   Tiempo: {evaluation.processing_time:.3f}s")
    print(f"   Métricas:")
    for metric_name, score in evaluation.metrics.items():
        print(f"     - {metric_name}: {score:.3f}")

    if evaluation.issues:
        print(f"   ⚠️ Problemas: {', '.join(evaluation.issues)}")

    # Estadísticas
    print("\n📊 Estadísticas del Sistema:")
    stats = system.get_system_stats()
    print(f"   Experiencias de aprendizaje: {stats['learning']['total_experiences']}")
    print(f"   Evaluaciones de calidad: {stats['quality']['total_evaluations']}")
    print(f"   Calidad promedio: {stats['learning']['average_quality']:.3f}")
    print(f"   Score promedio: {stats['quality']['average_score']:.3f}")

    # Cerrar sistema
    system.close()


if __name__ == "__main__":
    asyncio.run(main())
