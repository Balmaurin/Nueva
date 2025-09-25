"""
Integrador Mejorado de Ejercicios Diarios para Sheily-AI
Conecta los ejercicios mejorados con el sistema de entrenamiento avanzado
"""

import logging
import json
import asyncio
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
from pathlib import Path
from dataclasses import dataclass, asdict

# Importar el sistema de entrenamiento avanzado
from ..training.advanced_training_system import (
    AdvancedTrainingSystem,
    TrainingExercise,
    TrainingQuestion,
)

# Importar el generador de ejercicios mejorados
from .enhanced_daily_exercise_generator import (
    EnhancedDailyExerciseGenerator,
    EnhancedExercise,
)

logger = logging.getLogger(__name__)


@dataclass
class IntegrationStats:
    """Estadísticas de integración de ejercicios"""

    total_exercises_processed: int
    total_questions_processed: int
    successful_integrations: int
    failed_integrations: int
    branches_processed: List[str]
    integration_time: float
    created_date: datetime


class EnhancedDailyExerciseIntegrator:
    """
    Integrador mejorado que conecta los ejercicios diarios mejorados
    con el sistema de entrenamiento avanzado
    """

    def __init__(
        self,
        enhanced_exercises_path: str = "sheily_ai/data/enhanced_daily_exercises",
        training_system_path: str = "sheily_ai/data/training_system",
    ):
        self.enhanced_exercises_path = Path(enhanced_exercises_path)
        self.training_system_path = Path(training_system_path)
        self.training_system = AdvancedTrainingSystem(training_system_path)
        self.generator = EnhancedDailyExerciseGenerator()

        # Asegurar que los directorios existan
        self.enhanced_exercises_path.mkdir(parents=True, exist_ok=True)
        self.training_system_path.mkdir(parents=True, exist_ok=True)

        logger.info("🔗 Integrador de ejercicios mejorados inicializado")

    async def integrate_enhanced_exercises(
        self, target_date: Optional[datetime] = None
    ) -> IntegrationStats:
        """
        Integrar ejercicios mejorados del día especificado al sistema de entrenamiento

        Args:
            target_date: Fecha objetivo (por defecto, hoy)

        Returns:
            IntegrationStats: Estadísticas de la integración
        """
        start_time = datetime.now()

        if target_date is None:
            target_date = datetime.now()

        logger.info(
            f"🚀 Iniciando integración de ejercicios mejorados para {target_date.date()}"
        )

        # Obtener ejercicios mejorados del día
        enhanced_exercises = await self._load_enhanced_exercises_for_date(target_date)

        if not enhanced_exercises:
            logger.warning(
                f"No se encontraron ejercicios mejorados para {target_date.date()}"
            )
            return IntegrationStats(
                total_exercises_processed=0,
                total_questions_processed=0,
                successful_integrations=0,
                failed_integrations=0,
                branches_processed=[],
                integration_time=0.0,
                created_date=datetime.now(),
            )

        # Estadísticas de integración
        stats = IntegrationStats(
            total_exercises_processed=len(enhanced_exercises),
            total_questions_processed=sum(
                len(ex.questions) for ex in enhanced_exercises
            ),
            successful_integrations=0,
            failed_integrations=0,
            branches_processed=list(set(ex.branch for ex in enhanced_exercises)),
            integration_time=0.0,
            created_date=datetime.now(),
        )

        # Procesar cada ejercicio mejorado
        for enhanced_exercise in enhanced_exercises:
            try:
                success = await self._integrate_single_enhanced_exercise(
                    enhanced_exercise
                )
                if success:
                    stats.successful_integrations += 1
                else:
                    stats.failed_integrations += 1

            except Exception as e:
                logger.error(f"Error integrando ejercicio {enhanced_exercise.id}: {e}")
                stats.failed_integrations += 1

        # Calcular tiempo de integración
        stats.integration_time = (datetime.now() - start_time).total_seconds()

        # Guardar estadísticas de integración
        await self._save_integration_stats(stats, target_date)

        logger.info(f"✅ Integración completada:")
        logger.info(f"   - Ejercicios procesados: {stats.total_exercises_processed}")
        logger.info(f"   - Preguntas procesadas: {stats.total_questions_processed}")
        logger.info(f"   - Integraciones exitosas: {stats.successful_integrations}")
        logger.info(f"   - Integraciones fallidas: {stats.failed_integrations}")
        logger.info(f"   - Tiempo de integración: {stats.integration_time:.2f}s")

        return stats

    async def _load_enhanced_exercises_for_date(
        self, target_date: datetime
    ) -> List[EnhancedExercise]:
        """
        Cargar ejercicios mejorados para una fecha específica

        Args:
            target_date: Fecha objetivo

        Returns:
            List[EnhancedExercise]: Lista de ejercicios mejorados
        """
        exercises = []
        date_str = target_date.strftime("%Y%m%d")

        # Buscar archivos de ejercicios mejorados para la fecha
        pattern = f"*_{date_str}_*.json"
        exercise_files = list(self.enhanced_exercises_path.glob(pattern))

        logger.info(
            f"📁 Encontrados {len(exercise_files)} archivos de ejercicios para {target_date.date()}"
        )

        for file_path in exercise_files:
            try:
                with open(file_path, "r", encoding="utf-8") as f:
                    exercise_data = json.load(f)

                # Convertir a EnhancedExercise
                enhanced_exercise = EnhancedExercise(
                    id=exercise_data["id"],
                    branch=exercise_data["branch"],
                    micro_branch=exercise_data["micro_branch"],
                    exercise_type=exercise_data["exercise_type"],
                    title=exercise_data["title"],
                    description=exercise_data["description"],
                    difficulty=exercise_data["difficulty"],
                    content=exercise_data["content"],
                    solution=exercise_data["solution"],
                    hints=exercise_data["hints"],
                    tags=exercise_data["tags"],
                    created_date=datetime.fromisoformat(exercise_data["created_date"]),
                    estimated_time=exercise_data["estimated_time"],
                    points=exercise_data["points"],
                    questions=exercise_data["questions"],
                )

                exercises.append(enhanced_exercise)

            except Exception as e:
                logger.error(f"Error cargando ejercicio desde {file_path}: {e}")

        return exercises

    async def _integrate_single_enhanced_exercise(
        self, enhanced_exercise: EnhancedExercise
    ) -> bool:
        """
        Integrar un solo ejercicio mejorado al sistema de entrenamiento

        Args:
            enhanced_exercise: Ejercicio mejorado a integrar

        Returns:
            bool: True si la integración fue exitosa
        """
        try:
            # Convertir a TrainingExercise
            training_exercise = await self._convert_to_training_exercise(
                enhanced_exercise
            )

            # Agregar al sistema de entrenamiento
            await self.training_system.add_training_exercise(training_exercise)

            logger.debug(f"✅ Ejercicio {enhanced_exercise.id} integrado exitosamente")
            return True

        except Exception as e:
            logger.error(f"❌ Error integrando ejercicio {enhanced_exercise.id}: {e}")
            return False

    async def _convert_to_training_exercise(
        self, enhanced_exercise: EnhancedExercise
    ) -> TrainingExercise:
        """
        Convertir un EnhancedExercise a TrainingExercise

        Args:
            enhanced_exercise: Ejercicio mejorado

        Returns:
            TrainingExercise: Ejercicio de entrenamiento
        """
        # Mapear dificultad
        difficulty_map = {"básico": "easy", "intermedio": "medium", "avanzado": "hard"}

        difficulty = difficulty_map.get(enhanced_exercise.difficulty, "medium")

        # Crear preguntas de entrenamiento
        training_questions = (
            await self._create_training_questions_from_enhanced_exercise(
                enhanced_exercise
            )
        )

        # Calcular puntos por pregunta
        points_per_question = (
            enhanced_exercise.points // len(enhanced_exercise.questions)
            if enhanced_exercise.questions
            else 0
        )

        # Crear TrainingExercise
        training_exercise = TrainingExercise(
            id=f"enhanced_{enhanced_exercise.id}",
            title=enhanced_exercise.title,
            description=enhanced_exercise.description,
            category=enhanced_exercise.branch,
            difficulty=difficulty,
            total_questions=len(enhanced_exercise.questions),
            time_limit_minutes=enhanced_exercise.estimated_time,
            points_per_question=points_per_question,
            questions=training_questions,
            learning_objectives=[
                f"Comprender conceptos de {enhanced_exercise.micro_branch}",
                f"Aplicar técnicas de {enhanced_exercise.exercise_type}",
                f"Desarrollar habilidades en {enhanced_exercise.branch}",
            ],
            prerequisites=[
                f"Conocimientos básicos de {enhanced_exercise.branch}",
                f"Familiaridad con {enhanced_exercise.micro_branch}",
            ],
            metadata={
                "source": "enhanced_daily_exercise",
                "original_id": enhanced_exercise.id,
                "exercise_type": enhanced_exercise.exercise_type,
                "generation_date": enhanced_exercise.created_date.isoformat(),
                "branch": enhanced_exercise.branch,
                "micro_branch": enhanced_exercise.micro_branch,
                "content": enhanced_exercise.content,
                "solution": enhanced_exercise.solution,
                "hints": enhanced_exercise.hints,
                "tags": enhanced_exercise.tags,
            },
        )

        return training_exercise

    async def _create_training_questions_from_enhanced_exercise(
        self, enhanced_exercise: EnhancedExercise
    ) -> List[TrainingQuestion]:
        """
        Crear preguntas de entrenamiento desde un ejercicio mejorado

        Args:
            enhanced_exercise: Ejercicio mejorado

        Returns:
            List[TrainingQuestion]: Lista de preguntas de entrenamiento
        """
        training_questions = []

        for question_data in enhanced_exercise.questions:
            try:
                # Determinar tipo de pregunta
                question_type = self._determine_question_type(question_data)

                # Mapear dificultad
                difficulty_map = {
                    "básico": DifficultyLevel.BEGINNER,
                    "intermedio": DifficultyLevel.INTERMEDIATE,
                    "avanzado": DifficultyLevel.ADVANCED,
                }

                difficulty = difficulty_map.get(
                    question_data.get("difficulty", enhanced_exercise.difficulty),
                    DifficultyLevel.INTERMEDIATE,
                )

                # Crear TrainingQuestion
                training_question = TrainingQuestion(
                    id=question_data["id"],
                    number=question_data["number"],
                    question=question_data["question"],
                    question_type=question_type,
                    options=question_data.get("options", []),
                    correct_answer=question_data["correct_answer"],
                    explanation=question_data["explanation"],
                    difficulty=difficulty,
                    points=question_data["points"],
                    estimated_time=question_data["estimated_time"],
                    metadata={
                        "source": "enhanced_daily_exercise",
                        "original_exercise_id": enhanced_exercise.id,
                        "question_number": question_data["number"],
                    },
                )

                training_questions.append(training_question)

            except Exception as e:
                logger.error(f"Error creando pregunta de entrenamiento: {e}")

        return training_questions

    def _determine_question_type(self, question_data: Dict[str, Any]) -> QuestionType:
        """
        Determinar el tipo de pregunta basado en su contenido

        Args:
            question_data: Datos de la pregunta

        Returns:
            QuestionType: Tipo de pregunta
        """
        question_text = question_data.get("question", "").lower()
        options = question_data.get("options", [])

        # Pregunta de opción múltiple
        if options and len(options) > 1:
            return QuestionType.MULTIPLE_CHOICE

        # Pregunta de verdadero/falso
        if "verdadero" in question_text or "falso" in question_text:
            return QuestionType.TRUE_FALSE

        # Pregunta de código
        if any(
            keyword in question_text
            for keyword in ["código", "programa", "función", "algoritmo"]
        ):
            return QuestionType.CODING

        # Pregunta de texto libre
        if any(
            keyword in question_text
            for keyword in ["explica", "describe", "analiza", "comenta"]
        ):
            return QuestionType.TEXT

        # Por defecto, pregunta de texto libre
        return QuestionType.TEXT

    async def _save_integration_stats(
        self, stats: IntegrationStats, target_date: datetime
    ):
        """
        Guardar estadísticas de integración

        Args:
            stats: Estadísticas de integración
            target_date: Fecha objetivo
        """
        stats_file = (
            self.training_system_path
            / "integration_stats"
            / f"stats_{target_date.strftime('%Y%m%d')}.json"
        )
        stats_file.parent.mkdir(parents=True, exist_ok=True)

        stats_data = asdict(stats)
        stats_data["created_date"] = stats.created_date.isoformat()

        with open(stats_file, "w", encoding="utf-8") as f:
            json.dump(stats_data, f, indent=2, ensure_ascii=False)

        logger.debug(f"📊 Estadísticas de integración guardadas en {stats_file}")

    async def get_integration_history(self, days: int = 7) -> List[IntegrationStats]:
        """
        Obtener historial de integraciones de los últimos días

        Args:
            days: Número de días hacia atrás

        Returns:
            List[IntegrationStats]: Lista de estadísticas de integración
        """
        stats_list = []
        stats_dir = self.training_system_path / "integration_stats"

        if not stats_dir.exists():
            return stats_list

        # Obtener fechas de los últimos días
        end_date = datetime.now()
        start_date = end_date - timedelta(days=days)

        for i in range(days):
            target_date = end_date - timedelta(days=i)
            stats_file = stats_dir / f"stats_{target_date.strftime('%Y%m%d')}.json"

            if stats_file.exists():
                try:
                    with open(stats_file, "r", encoding="utf-8") as f:
                        stats_data = json.load(f)

                    stats = IntegrationStats(
                        total_exercises_processed=stats_data[
                            "total_exercises_processed"
                        ],
                        total_questions_processed=stats_data[
                            "total_questions_processed"
                        ],
                        successful_integrations=stats_data["successful_integrations"],
                        failed_integrations=stats_data["failed_integrations"],
                        branches_processed=stats_data["branches_processed"],
                        integration_time=stats_data["integration_time"],
                        created_date=datetime.fromisoformat(stats_data["created_date"]),
                    )

                    stats_list.append(stats)

                except Exception as e:
                    logger.error(f"Error cargando estadísticas de {stats_file}: {e}")

        return stats_list

    async def start_enhanced_integration_scheduler(self):
        """
        Iniciar scheduler para integración automática de ejercicios mejorados
        """
        from apscheduler.schedulers.asyncio import AsyncIOScheduler
        from apscheduler.triggers.cron import CronTrigger

        scheduler = AsyncIOScheduler()

        # Programar integración a las 12:30 PM (30 minutos después de la generación)
        scheduler.add_job(
            self.integrate_enhanced_exercises,
            CronTrigger(hour=12, minute=30),
            id="enhanced_exercise_integration",
            name="Integración de ejercicios mejorados",
            replace_existing=True,
        )

        scheduler.start()
        logger.info(
            "⏰ Scheduler de integración de ejercicios mejorados iniciado (12:30 PM diario)"
        )

        return scheduler


# Función de utilidad para integración manual
async def integrate_enhanced_exercises_manual(target_date: Optional[datetime] = None):
    """
    Función de utilidad para integración manual de ejercicios mejorados

    Args:
        target_date: Fecha objetivo (por defecto, hoy)
    """
    integrator = EnhancedDailyExerciseIntegrator()
    stats = await integrator.integrate_enhanced_exercises(target_date)

    print(f"\n📊 Estadísticas de Integración:")
    print(f"   - Ejercicios procesados: {stats.total_exercises_processed}")
    print(f"   - Preguntas procesadas: {stats.total_questions_processed}")
    print(f"   - Integraciones exitosas: {stats.successful_integrations}")
    print(f"   - Integraciones fallidas: {stats.failed_integrations}")
    print(f"   - Tiempo de integración: {stats.integration_time:.2f}s")
    print(f"   - Ramas procesadas: {', '.join(stats.branches_processed)}")


if __name__ == "__main__":
    import asyncio

    # Configurar logging
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    )

    # Ejecutar integración manual
    asyncio.run(integrate_enhanced_exercises_manual())
