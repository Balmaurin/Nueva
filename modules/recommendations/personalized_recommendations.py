#!/usr/bin/env python3
"""
Sistema de Recomendaciones Personalizadas
========================================
Genera recomendaciones personalizadas basadas en el historial de entrenamiento
"""

import json
import logging
import sqlite3
from pathlib import Path
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, asdict
from datetime import datetime, timedelta
import math
from collections import defaultdict, Counter

logger = logging.getLogger(__name__)


@dataclass
class UserProfile:
    """Perfil de usuario para recomendaciones"""

    user_id: str
    total_sessions: int
    total_score: int
    average_score: float
    preferred_categories: List[str]
    preferred_difficulties: List[str]
    weak_areas: List[str]
    strong_areas: List[str]
    learning_style: str  # 'visual', 'practical', 'theoretical', 'mixed'
    study_pattern: str  # 'consistent', 'intensive', 'sporadic'
    last_activity: datetime
    created_at: datetime


@dataclass
class ExerciseRecommendation:
    """Recomendación de ejercicio personalizada"""

    exercise_id: str
    title: str
    category: str
    difficulty: str
    confidence_score: float
    reasoning: str
    estimated_completion_time: int
    expected_score: float
    learning_objectives: List[str]
    prerequisites: List[str]


@dataclass
class LearningPath:
    """Ruta de aprendizaje personalizada"""

    path_id: str
    user_id: str
    title: str
    description: str
    exercises: List[ExerciseRecommendation]
    estimated_duration_hours: int
    difficulty_progression: List[str]
    target_skills: List[str]
    completion_rate: float
    created_at: datetime


class PersonalizedRecommendations:
    """Sistema de recomendaciones personalizadas"""

    def __init__(self, db_path: str = "shaili_ai/data/lora_training.db"):
        self.db_path = Path(db_path)
        self.user_profiles: Dict[str, UserProfile] = {}
        self.recommendation_cache: Dict[str, List[ExerciseRecommendation]] = {}
        self.learning_paths: Dict[str, LearningPath] = {}

        # Pesos para diferentes factores de recomendación
        self.weights = {
            "category_preference": 0.3,
            "difficulty_adaptation": 0.25,
            "skill_gap": 0.2,
            "recency": 0.15,
            "diversity": 0.1,
        }

        # Inicializar base de datos
        self._init_database()

        logger.info("🎯 Sistema de recomendaciones personalizadas inicializado")

    def _init_database(self):
        """Inicializar base de datos para recomendaciones"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()

                # Tabla de perfiles de usuario
                cursor.execute(
                    """
                    CREATE TABLE IF NOT EXISTS user_profiles (
                        user_id TEXT PRIMARY KEY,
                        total_sessions INTEGER NOT NULL,
                        total_score INTEGER NOT NULL,
                        average_score REAL NOT NULL,
                        preferred_categories TEXT NOT NULL,
                        preferred_difficulties TEXT NOT NULL,
                        weak_areas TEXT NOT NULL,
                        strong_areas TEXT NOT NULL,
                        learning_style TEXT NOT NULL,
                        study_pattern TEXT NOT NULL,
                        last_activity TIMESTAMP NOT NULL,
                        created_at TIMESTAMP NOT NULL
                    )
                """
                )

                # Tabla de recomendaciones generadas
                cursor.execute(
                    """
                    CREATE TABLE IF NOT EXISTS exercise_recommendations (
                        recommendation_id TEXT PRIMARY KEY,
                        user_id TEXT NOT NULL,
                        exercise_id TEXT NOT NULL,
                        confidence_score REAL NOT NULL,
                        reasoning TEXT NOT NULL,
                        generated_at TIMESTAMP NOT NULL,
                        used BOOLEAN DEFAULT FALSE
                    )
                """
                )

                # Tabla de rutas de aprendizaje
                cursor.execute(
                    """
                    CREATE TABLE IF NOT EXISTS learning_paths (
                        path_id TEXT PRIMARY KEY,
                        user_id TEXT NOT NULL,
                        title TEXT NOT NULL,
                        description TEXT NOT NULL,
                        exercises TEXT NOT NULL,
                        estimated_duration_hours INTEGER NOT NULL,
                        difficulty_progression TEXT NOT NULL,
                        target_skills TEXT NOT NULL,
                        completion_rate REAL DEFAULT 0.0,
                        created_at TIMESTAMP NOT NULL
                    )
                """
                )

                # Tabla de feedback de recomendaciones
                cursor.execute(
                    """
                    CREATE TABLE IF NOT EXISTS recommendation_feedback (
                        feedback_id TEXT PRIMARY KEY,
                        user_id TEXT NOT NULL,
                        exercise_id TEXT NOT NULL,
                        recommendation_id TEXT NOT NULL,
                        rating INTEGER NOT NULL,
                        feedback_text TEXT,
                        completed BOOLEAN DEFAULT FALSE,
                        actual_score REAL,
                        created_at TIMESTAMP NOT NULL
                    )
                """
                )

                conn.commit()

        except Exception as e:
            logger.error(f"❌ Error inicializando base de datos: {e}")

    def generate_user_profile(self, user_id: str) -> UserProfile:
        """Generar perfil de usuario basado en historial de entrenamiento"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()

                # Obtener historial de entrenamiento
                cursor.execute(
                    """
                    SELECT exercise_id, category, difficulty, points, is_correct, created_at
                    FROM lora_training_data
                    WHERE user_id = ?
                    ORDER BY created_at DESC
                """,
                    (user_id,),
                )

                training_history = cursor.fetchall()

                if not training_history:
                    # Usuario nuevo - perfil por defecto
                    return self._create_default_profile(user_id)

                # Analizar patrones de entrenamiento
                total_sessions = len(set(row[0] for row in training_history))
                total_score = sum(
                    row[3] for row in training_history if row[4]
                )  # Solo respuestas correctas
                average_score = (
                    total_score / len(training_history) if training_history else 0
                )

                # Categorías preferidas
                categories = [row[1] for row in training_history]
                category_counts = Counter(categories)
                preferred_categories = [
                    cat for cat, count in category_counts.most_common(3)
                ]

                # Dificultades preferidas
                difficulties = [row[2] for row in training_history]
                difficulty_counts = Counter(difficulties)
                preferred_difficulties = [
                    diff for diff, count in difficulty_counts.most_common(2)
                ]

                # Áreas débiles y fuertes
                correct_by_category = defaultdict(list)
                for row in training_history:
                    correct_by_category[row[1]].append(row[4])

                weak_areas = []
                strong_areas = []

                for category, results in correct_by_category.items():
                    success_rate = sum(results) / len(results)
                    if success_rate < 0.6:
                        weak_areas.append(category)
                    elif success_rate > 0.8:
                        strong_areas.append(category)

                # Estilo de aprendizaje
                learning_style = self._determine_learning_style(training_history)

                # Patrón de estudio
                study_pattern = self._determine_study_pattern(training_history)

                # Última actividad
                last_activity = max(row[5] for row in training_history)

                profile = UserProfile(
                    user_id=user_id,
                    total_sessions=total_sessions,
                    total_score=total_score,
                    average_score=average_score,
                    preferred_categories=preferred_categories,
                    preferred_difficulties=preferred_difficulties,
                    weak_areas=weak_areas,
                    strong_areas=strong_areas,
                    learning_style=learning_style,
                    study_pattern=study_pattern,
                    last_activity=datetime.fromisoformat(last_activity),
                    created_at=datetime.now(),
                )

                # Guardar perfil
                self._save_user_profile(profile)
                self.user_profiles[user_id] = profile

                return profile

        except Exception as e:
            logger.error(f"❌ Error generando perfil: {e}")
            return self._create_default_profile(user_id)

    def _create_default_profile(self, user_id: str) -> UserProfile:
        """Crear perfil por defecto para usuario nuevo"""
        return UserProfile(
            user_id=user_id,
            total_sessions=0,
            total_score=0,
            average_score=0.0,
            preferred_categories=[],
            preferred_difficulties=["easy"],
            weak_areas=[],
            strong_areas=[],
            learning_style="mixed",
            study_pattern="consistent",
            last_activity=datetime.now(),
            created_at=datetime.now(),
        )

    def _determine_learning_style(self, training_history: List[Tuple]) -> str:
        """Determinar estilo de aprendizaje basado en patrones"""
        # Análisis simplificado - en producción sería más sofisticado
        if len(training_history) < 5:
            return "mixed"

        # Analizar tipos de preguntas y respuestas
        theoretical_count = 0
        practical_count = 0

        for row in training_history:
            # Clasificar por categoría (simplificado)
            if row[1] in ["comprehension", "critical_analysis"]:
                theoretical_count += 1
            elif row[1] in ["programming", "problem_solving"]:
                practical_count += 1

        if theoretical_count > practical_count * 1.5:
            return "theoretical"
        elif practical_count > theoretical_count * 1.5:
            return "practical"
        else:
            return "mixed"

    def _determine_study_pattern(self, training_history: List[Tuple]) -> str:
        """Determinar patrón de estudio basado en frecuencia"""
        if len(training_history) < 3:
            return "consistent"

        # Analizar frecuencia de entrenamiento
        dates = [datetime.fromisoformat(row[5]) for row in training_history]
        dates.sort()

        # Calcular intervalos entre sesiones
        intervals = []
        for i in range(1, len(dates)):
            interval = (dates[i] - dates[i - 1]).total_seconds() / 3600  # horas
            intervals.append(interval)

        if not intervals:
            return "consistent"

        avg_interval = sum(intervals) / len(intervals)

        if avg_interval < 24:  # Menos de 1 día
            return "intensive"
        elif avg_interval > 168:  # Más de 1 semana
            return "sporadic"
        else:
            return "consistent"

    def _save_user_profile(self, profile: UserProfile):
        """Guardar perfil de usuario en base de datos"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()

                cursor.execute(
                    """
                    INSERT OR REPLACE INTO user_profiles 
                    (user_id, total_sessions, total_score, average_score, preferred_categories,
                     preferred_difficulties, weak_areas, strong_areas, learning_style, study_pattern,
                     last_activity, created_at)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                    (
                        profile.user_id,
                        profile.total_sessions,
                        profile.total_score,
                        profile.average_score,
                        json.dumps(profile.preferred_categories),
                        json.dumps(profile.preferred_difficulties),
                        json.dumps(profile.weak_areas),
                        json.dumps(profile.strong_areas),
                        profile.learning_style,
                        profile.study_pattern,
                        profile.last_activity.isoformat(),
                        profile.created_at.isoformat(),
                    ),
                )

                conn.commit()

        except Exception as e:
            logger.error(f"❌ Error guardando perfil: {e}")

    def get_exercise_recommendations(
        self, user_id: str, limit: int = 5
    ) -> List[ExerciseRecommendation]:
        """Obtener recomendaciones de ejercicios personalizadas"""
        try:
            # Generar o actualizar perfil de usuario
            profile = self.generate_user_profile(user_id)

            # Cargar ejercicios disponibles
            from ..training.advanced_training_system import get_advanced_training_system

            training_system = get_advanced_training_system()
            available_exercises = training_system.get_all_exercises()

            # Calcular puntuaciones de recomendación
            recommendations = []

            for exercise in available_exercises:
                confidence_score = self._calculate_recommendation_score(
                    exercise, profile
                )

                if confidence_score > 0.3:  # Umbral mínimo
                    recommendation = ExerciseRecommendation(
                        exercise_id=exercise.id,
                        title=exercise.title,
                        category=exercise.category,
                        difficulty=exercise.difficulty,
                        confidence_score=confidence_score,
                        reasoning=self._generate_recommendation_reasoning(
                            exercise, profile
                        ),
                        estimated_completion_time=exercise.time_limit_minutes,
                        expected_score=self._predict_expected_score(exercise, profile),
                        learning_objectives=exercise.learning_objectives,
                        prerequisites=exercise.prerequisites,
                    )
                    recommendations.append(recommendation)

            # Ordenar por puntuación de confianza
            recommendations.sort(key=lambda x: x.confidence_score, reverse=True)

            # Limitar resultados
            recommendations = recommendations[:limit]

            # Guardar recomendaciones
            self._save_recommendations(user_id, recommendations)

            return recommendations

        except Exception as e:
            logger.error(f"❌ Error generando recomendaciones: {e}")
            return []

    def _calculate_recommendation_score(self, exercise, profile: UserProfile) -> float:
        """Calcular puntuación de recomendación para un ejercicio"""
        score = 0.0

        # Preferencia de categoría
        if exercise.category in profile.preferred_categories:
            score += self.weights["category_preference"]
        elif exercise.category in profile.weak_areas:
            score += (
                self.weights["category_preference"] * 0.8
            )  # Priorizar áreas débiles

        # Adaptación de dificultad
        if exercise.difficulty in profile.preferred_difficulties:
            score += self.weights["difficulty_adaptation"]
        else:
            # Ajustar dificultad basado en rendimiento
            if profile.average_score > 80 and exercise.difficulty == "medium":
                score += self.weights["difficulty_adaptation"] * 0.7
            elif profile.average_score > 90 and exercise.difficulty == "hard":
                score += self.weights["difficulty_adaptation"] * 0.6

        # Brecha de habilidades
        if exercise.category in profile.weak_areas:
            score += self.weights["skill_gap"]

        # Diversidad
        if exercise.category not in profile.strong_areas:
            score += self.weights["diversity"]

        # Factor de recencia (ejercicios más recientes tienen prioridad)
        score += self.weights["recency"] * 0.5

        return min(score, 1.0)

    def _generate_recommendation_reasoning(self, exercise, profile: UserProfile) -> str:
        """Generar explicación para la recomendación"""
        reasons = []

        if exercise.category in profile.weak_areas:
            reasons.append(f"Te ayudará a mejorar en {exercise.category}")

        if exercise.category in profile.preferred_categories:
            reasons.append(f"Coincide con tus intereses en {exercise.category}")

        if exercise.difficulty in profile.preferred_difficulties:
            reasons.append(f"Se adapta a tu nivel de dificultad preferido")

        if profile.average_score > 80 and exercise.difficulty == "hard":
            reasons.append("Te desafiará a un nivel superior")

        if not reasons:
            reasons.append("Ejercicio bien balanceado para tu perfil")

        return ". ".join(reasons)

    def _predict_expected_score(self, exercise, profile: UserProfile) -> float:
        """Predecir puntuación esperada para un ejercicio"""
        base_score = profile.average_score

        # Ajustar por categoría
        if exercise.category in profile.strong_areas:
            base_score += 10
        elif exercise.category in profile.weak_areas:
            base_score -= 10

        # Ajustar por dificultad
        if exercise.difficulty == "easy" and profile.average_score > 70:
            base_score += 5
        elif exercise.difficulty == "hard" and profile.average_score < 60:
            base_score -= 15

        return max(min(base_score, 100), 0)

    def _save_recommendations(
        self, user_id: str, recommendations: List[ExerciseRecommendation]
    ):
        """Guardar recomendaciones en base de datos"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()

                for rec in recommendations:
                    recommendation_id = f"rec_{user_id}_{rec.exercise_id}_{int(datetime.now().timestamp())}"

                    cursor.execute(
                        """
                        INSERT INTO exercise_recommendations 
                        (recommendation_id, user_id, exercise_id, confidence_score, reasoning, generated_at)
                        VALUES (?, ?, ?, ?, ?, ?)
                    """,
                        (
                            recommendation_id,
                            user_id,
                            rec.exercise_id,
                            rec.confidence_score,
                            rec.reasoning,
                            datetime.now().isoformat(),
                        ),
                    )

                conn.commit()

        except Exception as e:
            logger.error(f"❌ Error guardando recomendaciones: {e}")

    def create_learning_path(
        self, user_id: str, target_skills: List[str] = None
    ) -> LearningPath:
        """Crear ruta de aprendizaje personalizada"""
        try:
            profile = self.generate_user_profile(user_id)

            if not target_skills:
                # Generar objetivos basados en áreas débiles
                target_skills = profile.weak_areas[:3]

            # Obtener ejercicios para cada habilidad objetivo
            path_exercises = []

            for skill in target_skills:
                skill_exercises = self.get_exercise_recommendations(user_id, limit=3)
                skill_exercises = [ex for ex in skill_exercises if ex.category == skill]
                path_exercises.extend(skill_exercises[:2])  # 2 ejercicios por habilidad

            # Ordenar por dificultad progresiva
            difficulty_order = ["easy", "medium", "hard"]
            path_exercises.sort(key=lambda x: difficulty_order.index(x.difficulty))

            # Calcular duración estimada
            estimated_duration = (
                sum(ex.estimated_completion_time for ex in path_exercises) / 60
            )  # horas

            # Crear ruta de aprendizaje
            path_id = f"path_{user_id}_{int(datetime.now().timestamp())}"
            learning_path = LearningPath(
                path_id=path_id,
                user_id=user_id,
                title=f"Ruta de Aprendizaje: {', '.join(target_skills)}",
                description=f"Ruta personalizada para mejorar en {', '.join(target_skills)}",
                exercises=path_exercises,
                estimated_duration_hours=int(estimated_duration),
                difficulty_progression=[ex.difficulty for ex in path_exercises],
                target_skills=target_skills,
                completion_rate=0.0,
                created_at=datetime.now(),
            )

            # Guardar ruta
            self._save_learning_path(learning_path)
            self.learning_paths[path_id] = learning_path

            return learning_path

        except Exception as e:
            logger.error(f"❌ Error creando ruta de aprendizaje: {e}")
            return None

    def _save_learning_path(self, path: LearningPath):
        """Guardar ruta de aprendizaje en base de datos"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()

                cursor.execute(
                    """
                    INSERT INTO learning_paths 
                    (path_id, user_id, title, description, exercises, estimated_duration_hours,
                     difficulty_progression, target_skills, completion_rate, created_at)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                    (
                        path.path_id,
                        path.user_id,
                        path.title,
                        path.description,
                        json.dumps([asdict(ex) for ex in path.exercises]),
                        path.estimated_duration_hours,
                        json.dumps(path.difficulty_progression),
                        json.dumps(path.target_skills),
                        path.completion_rate,
                        path.created_at.isoformat(),
                    ),
                )

                conn.commit()

        except Exception as e:
            logger.error(f"❌ Error guardando ruta de aprendizaje: {e}")

    def record_feedback(
        self,
        user_id: str,
        exercise_id: str,
        rating: int,
        feedback_text: str = None,
        completed: bool = False,
        actual_score: float = None,
    ):
        """Registrar feedback de una recomendación"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()

                # Obtener recomendación más reciente para este ejercicio
                cursor.execute(
                    """
                    SELECT recommendation_id FROM exercise_recommendations
                    WHERE user_id = ? AND exercise_id = ?
                    ORDER BY generated_at DESC
                    LIMIT 1
                """,
                    (user_id, exercise_id),
                )

                result = cursor.fetchone()
                recommendation_id = result[0] if result else None

                feedback_id = f"feedback_{user_id}_{exercise_id}_{int(datetime.now().timestamp())}"

                cursor.execute(
                    """
                    INSERT INTO recommendation_feedback 
                    (feedback_id, user_id, exercise_id, recommendation_id, rating, 
                     feedback_text, completed, actual_score, created_at)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                    (
                        feedback_id,
                        user_id,
                        exercise_id,
                        recommendation_id,
                        rating,
                        feedback_text,
                        completed,
                        actual_score,
                        datetime.now().isoformat(),
                    ),
                )

                # Marcar recomendación como usada
                if recommendation_id:
                    cursor.execute(
                        """
                        UPDATE exercise_recommendations 
                        SET used = TRUE 
                        WHERE recommendation_id = ?
                    """,
                        (recommendation_id,),
                    )

                conn.commit()

        except Exception as e:
            logger.error(f"❌ Error registrando feedback: {e}")

    def get_user_insights(self, user_id: str) -> Dict[str, Any]:
        """Obtener insights personalizados del usuario"""
        try:
            profile = self.generate_user_profile(user_id)

            insights = {
                "learning_strengths": profile.strong_areas,
                "improvement_areas": profile.weak_areas,
                "learning_style": profile.learning_style,
                "study_pattern": profile.study_pattern,
                "total_training_time": profile.total_sessions * 20,  # minutos
                "average_performance": profile.average_score,
                "consistency_score": self._calculate_consistency_score(user_id),
                "progress_trend": self._calculate_progress_trend(user_id),
                "recommendations": {
                    "next_exercises": [
                        ex.exercise_id
                        for ex in self.get_exercise_recommendations(user_id, 3)
                    ],
                    "suggested_learning_path": self.create_learning_path(user_id)
                    is not None,
                },
            }

            return insights

        except Exception as e:
            logger.error(f"❌ Error obteniendo insights: {e}")
            return {}

    def _calculate_consistency_score(self, user_id: str) -> float:
        """Calcular puntuación de consistencia en el estudio"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()

                cursor.execute(
                    """
                    SELECT created_at FROM lora_training_data
                    WHERE user_id = ?
                    ORDER BY created_at DESC
                    LIMIT 20
                """,
                    (user_id,),
                )

                dates = [datetime.fromisoformat(row[0]) for row in cursor.fetchall()]

                if len(dates) < 2:
                    return 0.5

                # Calcular variabilidad en intervalos
                intervals = []
                for i in range(1, len(dates)):
                    interval = (dates[i - 1] - dates[i]).total_seconds() / 3600
                    intervals.append(interval)

                if not intervals:
                    return 0.5

                # Menor variabilidad = mayor consistencia
                mean_interval = sum(intervals) / len(intervals)
                variance = sum((x - mean_interval) ** 2 for x in intervals) / len(
                    intervals
                )

                # Normalizar a 0-1
                consistency = max(0, 1 - (variance / (mean_interval**2)))

                return min(consistency, 1.0)

        except Exception as e:
            logger.error(f"❌ Error calculando consistencia: {e}")
            return 0.5

    def _calculate_progress_trend(self, user_id: str) -> str:
        """Calcular tendencia de progreso del usuario"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()

                cursor.execute(
                    """
                    SELECT AVG(points) as avg_score, 
                           strftime('%Y-%m', created_at) as month
                    FROM lora_training_data
                    WHERE user_id = ? AND is_correct = 1
                    GROUP BY strftime('%Y-%m', created_at)
                    ORDER BY month DESC
                    LIMIT 3
                """,
                    (user_id,),
                )

                monthly_scores = cursor.fetchall()

                if len(monthly_scores) < 2:
                    return "insufficient_data"

                # Calcular tendencia
                recent_avg = monthly_scores[0][0]
                previous_avg = monthly_scores[1][0]

                if recent_avg > previous_avg * 1.1:
                    return "improving"
                elif recent_avg < previous_avg * 0.9:
                    return "declining"
                else:
                    return "stable"

        except Exception as e:
            logger.error(f"❌ Error calculando tendencia: {e}")
            return "unknown"


# Instancia global
_recommendations_system: Optional[PersonalizedRecommendations] = None


def get_recommendations_system() -> PersonalizedRecommendations:
    """Obtener instancia global del sistema de recomendaciones"""
    global _recommendations_system

    if _recommendations_system is None:
        _recommendations_system = PersonalizedRecommendations()

    return _recommendations_system
