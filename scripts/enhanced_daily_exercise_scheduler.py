#!/usr/bin/env python3
"""
Script para el generador mejorado de ejercicios diarios
Genera 10 ejercicios por micro-rama, cada uno con 10 preguntas
"""

import asyncio
import logging
import argparse
import sys
from pathlib import Path

# Agregar el directorio raíz al path
sys.path.append(str(Path(__file__).parent.parent.parent))

from modules.core.enhanced_daily_exercise_generator import (
    EnhancedDailyExerciseGenerator,
)

# Configurar logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


class EnhancedDailyExerciseScheduler:
    """Scheduler para el generador mejorado de ejercicios diarios"""

    def __init__(self):
        self.generator = EnhancedDailyExerciseGenerator()
        self.is_running = False

    async def generate_exercises(self):
        """Generar ejercicios mejorados para todas las ramas"""
        try:
            logger.info("🚀 Iniciando generación de ejercicios mejorados...")

            exercises_by_branch = (
                await self.generator.generate_enhanced_daily_exercises()
            )

            total_exercises = sum(
                len(exercises) for exercises in exercises_by_branch.values()
            )
            total_questions = sum(
                len(exercise.questions)
                for exercises in exercises_by_branch.values()
                for exercise in exercises
            )

            logger.info(f"✅ Generación completada:")
            logger.info(f"   - Ramas procesadas: {len(exercises_by_branch)}")
            logger.info(f"   - Ejercicios generados: {total_exercises}")
            logger.info(f"   - Preguntas totales: {total_questions}")

            # Mostrar resumen por rama
            for branch, exercises in exercises_by_branch.items():
                branch_questions = sum(
                    len(exercise.questions) for exercise in exercises
                )
                logger.info(
                    f"   - {branch}: {len(exercises)} ejercicios, {branch_questions} preguntas"
                )

            return exercises_by_branch

        except Exception as e:
            logger.error(f"❌ Error en la generación: {e}")
            return {}

    async def start_scheduler(self):
        """Iniciar el scheduler automático"""
        try:
            self.generator.start_enhanced_scheduler()
            self.is_running = True
            logger.info("⏰ Scheduler de ejercicios mejorados iniciado (12:00 PM)")

            # Mantener el scheduler corriendo
            while self.is_running:
                await asyncio.sleep(60)  # Verificar cada minuto

        except KeyboardInterrupt:
            logger.info("🛑 Scheduler detenido por el usuario")
            self.is_running = False
        except Exception as e:
            logger.error(f"❌ Error en el scheduler: {e}")
            self.is_running = False

    async def list_exercises(self):
        """Listar ejercicios mejorados de hoy"""
        try:
            exercises_by_branch = await self.generator.get_today_enhanced_exercises()

            if not exercises_by_branch:
                logger.info("📝 No hay ejercicios mejorados generados para hoy")
                return

            logger.info("📋 Ejercicios mejorados de hoy:")
            logger.info("=" * 60)

            for branch, exercises in exercises_by_branch.items():
                logger.info(f"\n🌿 RAMA: {branch.upper()}")
                logger.info("-" * 40)

                for exercise in exercises:
                    logger.info(f"  📚 Ejercicio: {exercise.title}")
                    logger.info(f"     Micro-rama: {exercise.micro_branch}")
                    logger.info(f"     Tipo: {exercise.exercise_type}")
                    logger.info(f"     Dificultad: {exercise.difficulty}")
                    logger.info(f"     Preguntas: {len(exercise.questions)}")
                    logger.info(f"     Puntos: {exercise.points}")
                    logger.info(f"     Tiempo estimado: {exercise.estimated_time} min")

                    # Mostrar algunas preguntas de ejemplo
                    for i, question in enumerate(
                        exercise.questions[:3]
                    ):  # Solo las primeras 3
                        logger.info(f"       Q{i+1}: {question['question'][:50]}...")

                    if len(exercise.questions) > 3:
                        logger.info(
                            f"       ... y {len(exercise.questions) - 3} preguntas más"
                        )
                    logger.info("")

        except Exception as e:
            logger.error(f"❌ Error listando ejercicios: {e}")

    async def show_statistics(self):
        """Mostrar estadísticas de ejercicios mejorados"""
        try:
            exercises_by_branch = await self.generator.get_today_enhanced_exercises()

            if not exercises_by_branch:
                logger.info("📊 No hay ejercicios mejorados para mostrar estadísticas")
                return

            total_exercises = sum(
                len(exercises) for exercises in exercises_by_branch.values()
            )
            total_questions = sum(
                len(exercise.questions)
                for exercises in exercises_by_branch.values()
                for exercise in exercises
            )

            logger.info("📊 ESTADÍSTICAS DE EJERCICIOS MEJORADOS")
            logger.info("=" * 50)
            logger.info(f"Total de ramas: {len(exercises_by_branch)}")
            logger.info(f"Total de ejercicios: {total_exercises}")
            logger.info(f"Total de preguntas: {total_questions}")
            logger.info(
                f"Promedio de preguntas por ejercicio: {total_questions/total_exercises:.1f}"
            )

            # Estadísticas por rama
            logger.info("\n📈 POR RAMA:")
            for branch, exercises in exercises_by_branch.items():
                branch_questions = sum(
                    len(exercise.questions) for exercise in exercises
                )
                logger.info(
                    f"  {branch}: {len(exercises)} ejercicios, {branch_questions} preguntas"
                )

            # Estadísticas por dificultad
            difficulty_stats = {}
            for exercises in exercises_by_branch.values():
                for exercise in exercises:
                    diff = exercise.difficulty
                    if diff not in difficulty_stats:
                        difficulty_stats[diff] = {"exercises": 0, "questions": 0}
                    difficulty_stats[diff]["exercises"] += 1
                    difficulty_stats[diff]["questions"] += len(exercise.questions)

            logger.info("\n📊 POR DIFICULTAD:")
            for difficulty, stats in difficulty_stats.items():
                logger.info(
                    f"  {difficulty}: {stats['exercises']} ejercicios, {stats['questions']} preguntas"
                )

        except Exception as e:
            logger.error(f"❌ Error mostrando estadísticas: {e}")


async def main():
    """Función principal"""
    parser = argparse.ArgumentParser(
        description="Generador mejorado de ejercicios diarios"
    )
    parser.add_argument(
        "command",
        choices=["generate", "start", "list", "stats"],
        help="Comando a ejecutar",
    )

    args = parser.parse_args()

    scheduler = EnhancedDailyExerciseScheduler()

    if args.command == "generate":
        await scheduler.generate_exercises()

    elif args.command == "start":
        await scheduler.start_scheduler()

    elif args.command == "list":
        await scheduler.list_exercises()

    elif args.command == "stats":
        await scheduler.show_statistics()


if __name__ == "__main__":
    asyncio.run(main())
