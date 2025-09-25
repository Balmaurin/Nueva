"""
Integrador de ejercicios diarios con el sistema de entrenamiento existente
"""

import logging
import asyncio
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
from pathlib import Path

from .daily_exercise_generator import DailyExerciseGenerator, Exercise
from ..training.advanced_training_system import AdvancedTrainingSystem, TrainingExercise

logger = logging.getLogger(__name__)


class DailyExerciseIntegrator:
    """
    Integrador que conecta el generador de ejercicios diarios con el sistema de entrenamiento
    """

    def __init__(self):
        self.daily_generator = DailyExerciseGenerator()
        self.training_system = AdvancedTrainingSystem()
        self.logger = logger

    async def integrate_daily_exercises(self) -> Dict[str, Any]:
        """
        Integrar ejercicios diarios con el sistema de entrenamiento
        """
        try:
            self.logger.info(
                "🔄 Integrando ejercicios diarios con sistema de entrenamiento..."
            )

            # Obtener ejercicios de hoy
            daily_exercises = self.daily_generator.get_today_exercises()

            if not daily_exercises:
                self.logger.info("📅 No hay ejercicios diarios disponibles para hoy")
                return {
                    "status": "no_exercises",
                    "message": "No hay ejercicios diarios para hoy",
                }

            # Convertir ejercicios diarios a formato del sistema de entrenamiento
            converted_exercises = {}

            for branch, daily_exercise in daily_exercises.items():
                training_exercise = self._convert_to_training_exercise(daily_exercise)
                if training_exercise:
                    converted_exercises[branch] = training_exercise
                    self.logger.info(f"✅ Ejercicio de {branch} convertido y listo")

            # Agregar ejercicios al sistema de entrenamiento
            if converted_exercises:
                await self._add_to_training_system(converted_exercises)

                return {
                    "status": "success",
                    "exercises_added": len(converted_exercises),
                    "branches": list(converted_exercises.keys()),
                }
            else:
                return {
                    "status": "no_conversions",
                    "message": "No se pudieron convertir ejercicios",
                }

        except Exception as e:
            self.logger.error(f"❌ Error integrando ejercicios diarios: {e}")
            return {"status": "error", "message": str(e)}

    def _convert_to_training_exercise(
        self, daily_exercise: Exercise
    ) -> Optional[TrainingExercise]:
        """
        Convertir ejercicio diario a formato del sistema de entrenamiento
        """
        try:
            # Crear preguntas basadas en el contenido del ejercicio diario
            questions = self._create_questions_from_exercise(daily_exercise)

            # Crear ejercicio de entrenamiento
            training_exercise = TrainingExercise(
                id=f"daily_{daily_exercise.id}",
                title=daily_exercise.title,
                description=daily_exercise.description,
                category=daily_exercise.branch,
                difficulty=daily_exercise.difficulty,
                total_questions=len(questions),
                time_limit_minutes=daily_exercise.estimated_time,
                points_per_question=daily_exercise.points // len(questions),
                questions=questions,
                learning_objectives=[f"Practicar {daily_exercise.branch}"],
                prerequisites=[],
                metadata={"tags": daily_exercise.tags, "daily_exercise": True},
            )

            return training_exercise

        except Exception as e:
            self.logger.error(
                f"❌ Error convirtiendo ejercicio {daily_exercise.id}: {e}"
            )
            return None

    def _create_questions_from_exercise(
        self, exercise: Exercise
    ) -> List[Dict[str, Any]]:
        """
        Crear preguntas basadas en el contenido del ejercicio diario
        """
        questions = []

        from ..training.advanced_training_system import TrainingQuestion

        # Pregunta principal sobre el contenido
        questions.append(
            TrainingQuestion(
                id=f"{exercise.id}_q1",
                question=exercise.content,
                correct_answer=exercise.solution,
                explanation=f"Solución del ejercicio de {exercise.branch}",
                difficulty=exercise.difficulty,
                category=exercise.branch,
                points=exercise.points // 2,
                metadata={"hints": exercise.hints, "type": "main_exercise"},
            )
        )

        # Pregunta sobre comprensión
        questions.append(
            TrainingQuestion(
                id=f"{exercise.id}_q2",
                question=f"¿Cuál es la dificultad de este ejercicio de {exercise.branch}?",
                correct_answer=exercise.difficulty,
                explanation=f"La dificultad del ejercicio es {exercise.difficulty}",
                difficulty="easy",
                category=exercise.branch,
                points=exercise.points // 4,
                metadata={
                    "type": "comprehension",
                    "options": ["básico", "intermedio", "avanzado"],
                },
            )
        )

        # Pregunta sobre tiempo estimado
        questions.append(
            TrainingQuestion(
                id=f"{exercise.id}_q3",
                question=f"¿Cuánto tiempo estimas que tomará resolver este ejercicio?",
                correct_answer=f"{exercise.estimated_time} minutos",
                explanation=f"El tiempo estimado es {exercise.estimated_time} minutos",
                difficulty="easy",
                category=exercise.branch,
                points=exercise.points // 4,
                metadata={
                    "type": "time_estimation",
                    "options": [
                        f"{exercise.estimated_time - 5} minutos",
                        f"{exercise.estimated_time} minutos",
                        f"{exercise.estimated_time + 5} minutos",
                        f"{exercise.estimated_time + 10} minutos",
                    ],
                },
            )
        )

        return questions

    async def _add_to_training_system(self, exercises: Dict[str, TrainingExercise]):
        """
        Agregar ejercicios convertidos al sistema de entrenamiento
        """
        try:
            # Agregar cada ejercicio al sistema de entrenamiento
            for branch, exercise in exercises.items():
                # Verificar si ya existe
                existing = self.training_system.get_exercise(exercise.id)
                if not existing:
                    # Agregar al sistema
                    self.training_system.exercises[exercise.id] = exercise
                    self.logger.info(
                        f"✅ Ejercicio {exercise.id} agregado al sistema de entrenamiento"
                    )
                else:
                    self.logger.info(
                        f"ℹ️ Ejercicio {exercise.id} ya existe en el sistema"
                    )

            # Guardar cambios
            self.training_system._save_exercises()
            self.logger.info("💾 Cambios guardados en el sistema de entrenamiento")

        except Exception as e:
            self.logger.error(f"❌ Error agregando ejercicios al sistema: {e}")

    async def generate_and_integrate(self) -> Dict[str, Any]:
        """
        Generar ejercicios diarios e integrarlos automáticamente
        """
        try:
            self.logger.info("🚀 Generando e integrando ejercicios diarios...")

            # 1. Generar ejercicios diarios
            daily_exercises = await self.daily_generator.generate_daily_exercises()

            if not daily_exercises:
                self.logger.info("ℹ️ No se generaron nuevos ejercicios diarios")
                return {
                    "status": "no_generation",
                    "message": "No se generaron nuevos ejercicios",
                }

            # 2. Integrar con sistema de entrenamiento
            integration_result = await self.integrate_daily_exercises()

            return {
                "status": "success",
                "generated": len(daily_exercises),
                "integrated": integration_result,
            }

        except Exception as e:
            self.logger.error(f"❌ Error en generación e integración: {e}")
            return {"status": "error", "message": str(e)}

    def get_available_daily_exercises(self) -> Dict[str, Any]:
        """
        Obtener ejercicios diarios disponibles
        """
        try:
            daily_exercises = self.daily_generator.get_today_exercises()

            result = {"total": len(daily_exercises), "exercises": {}}

            for branch, exercise in daily_exercises.items():
                result["exercises"][branch] = {
                    "id": exercise.id,
                    "title": exercise.title,
                    "difficulty": exercise.difficulty,
                    "estimated_time": exercise.estimated_time,
                    "points": exercise.points,
                    "tags": exercise.tags,
                }

            return result

        except Exception as e:
            self.logger.error(f"❌ Error obteniendo ejercicios disponibles: {e}")
            return {"total": 0, "exercises": {}, "error": str(e)}

    async def start_daily_integration_scheduler(self):
        """
        Iniciar scheduler para integración automática diaria
        """
        try:
            self.logger.info("⏰ Iniciando scheduler de integración diaria...")

            # Programar integración diaria a las 12:30 PM (después de la generación)
            from apscheduler.schedulers.asyncio import AsyncIOScheduler
            from apscheduler.triggers.cron import CronTrigger

            scheduler = AsyncIOScheduler()
            scheduler.add_job(
                self.generate_and_integrate,
                CronTrigger(hour=12, minute=30),
                id="daily_integration",
                name="Integración diaria de ejercicios",
            )

            scheduler.start()
            self.logger.info("✅ Scheduler de integración diaria iniciado (12:30 PM)")

            # Mantener corriendo
            try:
                while True:
                    await asyncio.sleep(60)
            except KeyboardInterrupt:
                scheduler.shutdown()
                self.logger.info("🛑 Scheduler de integración detenido")

        except Exception as e:
            self.logger.error(f"❌ Error iniciando scheduler de integración: {e}")


# Función de utilidad para usar el integrador
async def main():
    """Función principal para probar el integrador"""
    integrator = DailyExerciseIntegrator()

    # Probar integración
    result = await integrator.generate_and_integrate()

    print(f"Resultado: {result}")

    # Mostrar ejercicios disponibles
    available = integrator.get_available_daily_exercises()
    print(f"Ejercicios disponibles: {available}")


if __name__ == "__main__":
    asyncio.run(main())
