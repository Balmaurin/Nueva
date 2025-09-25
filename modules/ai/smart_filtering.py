"""
Sistema de Filtrado Inteligente para Datasets de IA
Analiza respuestas, filtra calidad y mejora ramas de modelos personales
"""

import json
import logging
from typing import Dict, List, Any, Tuple, Optional
from datetime import datetime, timedelta
from collections import defaultdict, Counter
import numpy as np
from dataclasses import dataclass, field
from enum import Enum

logger = logging.getLogger(__name__)


class QualityTier(Enum):
    EXCELLENT = "excellent"  # >95% calidad
    HIGH = "high"  # 90-95% calidad
    GOOD = "good"  # 80-90% calidad
    AVERAGE = "average"  # 70-80% calidad
    LOW = "low"  # 60-70% calidad
    POOR = "poor"  # <60% calidad


class ContentCategory(Enum):
    CREATIVE = "creative"
    TECHNICAL = "technical"
    ANALYTICAL = "analytical"
    EDUCATIONAL = "educational"
    PROFESSIONAL = "professional"
    PERSONAL = "personal"


@dataclass
class FilteredDataset:
    """Dataset filtrado y optimizado"""

    id: str
    name: str
    description: str
    category: ContentCategory
    quality_tier: QualityTier
    entries: List[Dict[str, Any]] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)
    created_at: datetime = field(default_factory=datetime.now)
    size: int = 0
    avg_quality_score: float = 0.0
    diversity_score: float = 0.0
    coverage_score: float = 0.0


@dataclass
class ModelBranch:
    """Rama de modelo personal"""

    id: str
    name: str
    base_model: str
    datasets_used: List[str] = field(default_factory=list)
    training_config: Dict[str, Any] = field(default_factory=dict)
    performance_metrics: Dict[str, Any] = field(default_factory=dict)
    quality_improvements: List[Dict[str, Any]] = field(default_factory=list)
    created_at: datetime = field(default_factory=datetime.now)
    last_updated: datetime = field(default_factory=datetime.now)
    is_active: bool = False


class SmartFilteringSystem:
    """
    Sistema inteligente de filtrado y mejora de datasets
    """

    def __init__(self):
        self.datasets: Dict[str, FilteredDataset] = {}
        self.model_branches: Dict[str, ModelBranch] = {}
        self.quality_thresholds = {
            QualityTier.EXCELLENT: 95,
            QualityTier.HIGH: 90,
            QualityTier.GOOD: 80,
            QualityTier.AVERAGE: 70,
            QualityTier.LOW: 60,
            QualityTier.POOR: 0,
        }

    def analyze_and_filter_responses(
        self, responses: List[Dict[str, Any]], exercise_config: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Analiza y filtra respuestas para crear datasets optimizados

        Args:
            responses: Lista de respuestas con metadata
            exercise_config: Configuración del ejercicio

        Returns:
            Dict con datasets filtrados y métricas
        """
        try:
            # 1. Clasificar respuestas por calidad
            quality_analysis = self._analyze_response_quality(responses)

            # 2. Filtrar respuestas de alta calidad
            high_quality_responses = self._filter_high_quality_responses(
                responses, quality_analysis
            )

            # 3. Crear datasets optimizados por categoría
            datasets = self._create_optimized_datasets(
                high_quality_responses, exercise_config
            )

            # 4. Calcular métricas de mejora
            improvement_metrics = self._calculate_improvement_metrics(
                responses, high_quality_responses
            )

            # 5. Generar recomendaciones para ramas de modelos
            branch_recommendations = self._generate_branch_recommendations(
                datasets, exercise_config
            )

            return {
                "datasets": datasets,
                "quality_analysis": quality_analysis,
                "improvement_metrics": improvement_metrics,
                "branch_recommendations": branch_recommendations,
                "total_responses": len(responses),
                "filtered_responses": len(high_quality_responses),
                "filtration_rate": (
                    len(high_quality_responses) / len(responses) if responses else 0
                ),
                "timestamp": datetime.now().isoformat(),
            }

        except Exception as e:
            logger.error(f"Error en análisis y filtrado: {e}")
            return {
                "error": str(e),
                "datasets": [],
                "quality_analysis": {},
                "improvement_metrics": {},
                "branch_recommendations": [],
            }

    def _analyze_response_quality(
        self, responses: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Analiza la calidad de todas las respuestas"""
        if not responses:
            return {}

        quality_scores = [r.get("qualityScore", 0) for r in responses]
        quality_distribution = defaultdict(int)

        for score in quality_scores:
            for tier, threshold in self.quality_thresholds.items():
                if score >= threshold:
                    quality_distribution[tier.value] += 1
                    break

        # Calcular estadísticas
        stats = {
            "total_responses": len(responses),
            "avg_quality_score": np.mean(quality_scores),
            "median_quality_score": np.median(quality_scores),
            "std_quality_score": np.std(quality_scores),
            "min_quality_score": min(quality_scores),
            "max_quality_score": max(quality_scores),
            "quality_distribution": dict(quality_distribution),
        }

        # Análisis de tendencias
        stats["quality_trends"] = self._analyze_quality_trends(responses)

        return stats

    def _filter_high_quality_responses(
        self, responses: List[Dict[str, Any]], quality_analysis: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """Filtra respuestas de alta calidad"""
        min_quality_threshold = 80  # 80% mínimo para datasets

        high_quality = []
        for response in responses:
            score = response.get("qualityScore", 0)
            if score >= min_quality_threshold:
                high_quality.append(response)

        # Ordenar por calidad descendente
        high_quality.sort(key=lambda x: x.get("qualityScore", 0), reverse=True)

        # Limitar a las mejores respuestas (top 50% o máximo 1000)
        max_responses = min(len(high_quality) // 2, 1000)
        return high_quality[:max_responses]

    def _create_optimized_datasets(
        self, responses: List[Dict[str, Any]], exercise_config: Dict[str, Any]
    ) -> List[FilteredDataset]:
        """Crea datasets optimizados por categorías"""
        datasets = []

        # Agrupar por categorías de contenido
        category_groups = defaultdict(list)

        for response in responses:
            # Determinar categoría automáticamente o usar la del ejercicio
            category = self._determine_content_category(response, exercise_config)
            category_groups[category].append(response)

        # Crear dataset por categoría
        for category, category_responses in category_groups.items():
            if len(category_responses) < 5:  # Mínimo 5 respuestas por dataset
                continue

            # Determinar tier de calidad promedio
            avg_quality = np.mean(
                [r.get("qualityScore", 0) for r in category_responses]
            )
            quality_tier = self._determine_quality_tier(avg_quality)

            # Calcular métricas del dataset
            dataset_metrics = self._calculate_dataset_metrics(category_responses)

            # Crear dataset
            dataset = FilteredDataset(
                id=f"dataset_{category.value}_{int(datetime.now().timestamp())}",
                name=f"Dataset {category.value.title()} - {quality_tier.value.title()}",
                description=f"Dataset optimizado de respuestas {category.value} con calidad {quality_tier.value}",
                category=category,
                quality_tier=quality_tier,
                entries=category_responses,
                metadata={
                    "exercise_config": exercise_config,
                    "creation_method": "smart_filtering",
                    "quality_filters_applied": [
                        "score_threshold",
                        "diversity_check",
                        "relevance_filter",
                    ],
                },
                size=len(category_responses),
                avg_quality_score=avg_quality,
                diversity_score=dataset_metrics["diversity_score"],
                coverage_score=dataset_metrics["coverage_score"],
            )

            datasets.append(dataset)
            self.datasets[dataset.id] = dataset

        return datasets

    def _determine_content_category(
        self, response: Dict[str, Any], exercise_config: Dict[str, Any]
    ) -> ContentCategory:
        """Determina la categoría de contenido de una respuesta"""
        # Usar categoría del ejercicio si existe
        exercise_category = exercise_config.get("category", "").lower()
        if exercise_category:
            try:
                return ContentCategory(exercise_category)
            except ValueError:
                pass

        # Análisis automático basado en contenido
        content = response.get("response", "").lower()

        # Palabras clave por categoría
        category_keywords = {
            ContentCategory.CREATIVE: [
                "imagina",
                "crea",
                "diseña",
                "inventa",
                "fantasía",
                "historia",
            ],
            ContentCategory.TECHNICAL: [
                "código",
                "programa",
                "algoritmo",
                "sistema",
                "tecnología",
                "api",
            ],
            ContentCategory.ANALYTICAL: [
                "analiza",
                "compara",
                "evalúa",
                "diferencia",
                "pros",
                "contras",
            ],
            ContentCategory.EDUCATIONAL: [
                "explica",
                "enseña",
                "aprende",
                "concepto",
                "definición",
                "ejemplo",
            ],
            ContentCategory.PROFESSIONAL: [
                "empresa",
                "trabajo",
                "proyecto",
                "cliente",
                "reunión",
                "estrategia",
            ],
            ContentCategory.PERSONAL: [
                "yo",
                "mi",
                "personal",
                "vida",
                "experiencia",
                "sentimiento",
            ],
        }

        # Contar coincidencias
        category_scores = {}
        for category, keywords in category_keywords.items():
            score = sum(1 for keyword in keywords if keyword in content)
            category_scores[category] = score

        # Retornar categoría con mayor score
        return max(category_scores, key=category_scores.get)

    def _determine_quality_tier(self, avg_quality: float) -> QualityTier:
        """Determina el tier de calidad basado en el score promedio"""
        for tier, threshold in self.quality_thresholds.items():
            if avg_quality >= threshold:
                return tier
        return QualityTier.POOR

    def _calculate_dataset_metrics(
        self, responses: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Calcula métricas avanzadas del dataset"""
        if not responses:
            return {"diversity_score": 0, "coverage_score": 0}

        # Diversidad: variación en longitudes y vocabulario
        lengths = [len(r.get("response", "")) for r in responses]
        length_variance = np.var(lengths) if lengths else 0
        diversity_score = min(100, length_variance / 1000)  # Normalizar

        # Cobertura: qué tan bien cubre diferentes aspectos
        all_words = []
        for response in responses:
            words = response.get("response", "").lower().split()
            all_words.extend(words)

        word_freq = Counter(all_words)
        unique_words = len(word_freq)

        # Métrica de cobertura: palabras únicas vs total
        coverage_score = (
            min(100, (unique_words / len(all_words)) * 200) if all_words else 0
        )

        return {
            "diversity_score": diversity_score,
            "coverage_score": coverage_score,
            "unique_words": unique_words,
            "total_words": len(all_words),
            "avg_response_length": np.mean(lengths) if lengths else 0,
        }

    def _analyze_quality_trends(
        self, responses: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Analiza tendencias de calidad en el tiempo"""
        if not responses:
            return {}

        # Ordenar por timestamp
        sorted_responses = sorted(
            responses, key=lambda x: x.get("timestamp", datetime.now())
        )

        # Calcular promedio móvil de calidad
        window_size = 10
        moving_avg = []

        for i in range(len(sorted_responses)):
            start_idx = max(0, i - window_size + 1)
            window = sorted_responses[start_idx : i + 1]
            avg_quality = np.mean([r.get("qualityScore", 0) for r in window])
            moving_avg.append(avg_quality)

        return {
            "moving_average": moving_avg,
            "trend_direction": (
                "improving" if moving_avg[-1] > moving_avg[0] else "declining"
            ),
            "volatility": np.std(moving_avg) if moving_avg else 0,
        }

    def _calculate_improvement_metrics(
        self, original: List[Dict[str, Any]], filtered: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Calcula métricas de mejora después del filtrado"""
        if not original:
            return {}

        original_avg = np.mean([r.get("qualityScore", 0) for r in original])
        filtered_avg = np.mean([r.get("qualityScore", 0) for r in filtered])

        improvement = {
            "original_avg_quality": original_avg,
            "filtered_avg_quality": filtered_avg,
            "quality_improvement": filtered_avg - original_avg,
            "improvement_percentage": (
                ((filtered_avg - original_avg) / original_avg) * 100
                if original_avg > 0
                else 0
            ),
            "filtration_efficiency": len(filtered) / len(original),
            "data_reduction_ratio": 1 - (len(filtered) / len(original)),
        }

        return improvement

    def _generate_branch_recommendations(
        self, datasets: List[FilteredDataset], exercise_config: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """Genera recomendaciones para ramas de modelos"""
        recommendations = []

        for dataset in datasets:
            # Recomendaciones basadas en el dataset
            if dataset.quality_tier in [QualityTier.EXCELLENT, QualityTier.HIGH]:
                recommendation = {
                    "dataset_id": dataset.id,
                    "recommended_action": "create_branch",
                    "branch_name": f"branch_{dataset.category.value}_{dataset.quality_tier.value}",
                    "training_config": {
                        "base_model": "meta-llama/Llama-3.1-8B-Instruct",
                        "dataset": dataset.id,
                        "learning_rate": 2e-5,
                        "epochs": 3,
                        "batch_size": 4,
                        "specialization": dataset.category.value,
                    },
                    "expected_improvement": f"+{dataset.avg_quality_score - 70:.1f}% en {dataset.category.value}",
                    "confidence": "high" if dataset.size > 50 else "medium",
                }
                recommendations.append(recommendation)

        return recommendations

    def create_model_branch(
        self, branch_config: Dict[str, Any]
    ) -> Optional[ModelBranch]:
        """Crea una nueva rama de modelo basada en datasets filtrados"""
        try:
            branch = ModelBranch(
                id=f"branch_{int(datetime.now().timestamp())}",
                name=branch_config["name"],
                base_model=branch_config["base_model"],
                datasets_used=branch_config["datasets"],
                training_config=branch_config["training_config"],
                performance_metrics={},
            )

            self.model_branches[branch.id] = branch
            return branch

        except Exception as e:
            logger.error(f"Error creando rama de modelo: {e}")
            return None

    def get_branch_recommendations(self, user_id: str) -> List[Dict[str, Any]]:
        """Obtiene recomendaciones de ramas para un usuario"""
        # Lógica para generar recomendaciones basadas en el historial del usuario
        # Por ahora, retornar recomendaciones generales
        return [
            {
                "type": "specialization_branch",
                "title": "Rama de Escritura Creativa",
                "description": "Especializa tu IA en generación de contenido creativo",
                "datasets_needed": 100,
                "expected_benefits": [
                    "Mejor creatividad",
                    "Más variedad en respuestas",
                    "Estilo único",
                ],
            },
            {
                "type": "technical_branch",
                "title": "Rama Técnica Avanzada",
                "description": "Mejora las capacidades técnicas de tu IA",
                "datasets_needed": 150,
                "expected_benefits": [
                    "Código más preciso",
                    "Explicaciones técnicas",
                    "Solución de problemas",
                ],
            },
        ]


# Instancia global del sistema de filtrado
smart_filtering_system = SmartFilteringSystem()
