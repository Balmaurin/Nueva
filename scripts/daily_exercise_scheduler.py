#!/usr/bin/env python3
"""
Script para programar y ejecutar la generación automática de ejercicios diarios
"""

import asyncio
import logging
import sys
from pathlib import Path
from datetime import datetime

# Agregar el directorio raíz al path
sys.path.append(str(Path(__file__).parent.parent.parent))

from modules.core.daily_exercise_generator import DailyExerciseGenerator

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[logging.FileHandler("logs/daily_exercises.log"), logging.StreamHandler()],
)

logger = logging.getLogger(__name__)


class DailyExerciseScheduler:
    """Scheduler para ejercicios diarios"""

    def __init__(self):
        self.generator = DailyExerciseGenerator()
        self.is_running = False

    async def start_daily_generation(self):
        """Iniciar generación diaria de ejercicios"""
        try:
            logger.info("🚀 Iniciando generación diaria de ejercicios...")

            # Generar ejercicios para todas las ramas activas
            exercises = await self.generator.generate_daily_exercises()

            if exercises:
                logger.info(f"✅ Generados {len(exercises)} ejercicios diarios:")
                for branch, exercise in exercises.items():
                    logger.info(
                        f"  📚 {branch}: {exercise.title} ({exercise.difficulty})"
                    )
            else:
                logger.info(
                    "ℹ️ No se generaron nuevos ejercicios (ya existían para hoy)"
                )

        except Exception as e:
            logger.error(f"❌ Error en generación diaria: {e}")

    async def start_scheduler(self):
        """Iniciar el scheduler automático"""
        try:
            self.generator.start_scheduler()
            self.is_running = True
            logger.info("⏰ Scheduler de ejercicios diarios iniciado (12:00 PM)")

            # Mantener el script corriendo
            try:
                while self.is_running:
                    await asyncio.sleep(60)  # Verificar cada minuto
            except KeyboardInterrupt:
                logger.info("🛑 Deteniendo scheduler...")
                self.stop_scheduler()

        except Exception as e:
            logger.error(f"❌ Error iniciando scheduler: {e}")

    def stop_scheduler(self):
        """Detener el scheduler"""
        self.is_running = False
        self.generator.stop_scheduler()
        logger.info("🛑 Scheduler detenido")

    async def generate_for_specific_branch(self, branch: str):
        """Generar ejercicio para una rama específica"""
        try:
            logger.info(f"🎯 Generando ejercicio para rama: {branch}")
            exercise = await self.generator.generate_exercises_for_branch(branch)

            if exercise:
                logger.info(f"✅ Ejercicio generado: {exercise.title}")
                return exercise
            else:
                logger.info(f"ℹ️ No se pudo generar ejercicio para {branch}")
                return None

        except Exception as e:
            logger.error(f"❌ Error generando ejercicio para {branch}: {e}")
            return None

    def get_today_exercises(self):
        """Obtener ejercicios de hoy"""
        try:
            exercises = self.generator.get_today_exercises()
            if exercises:
                logger.info(f"📅 Ejercicios disponibles para hoy ({len(exercises)}):")
                for branch, exercise in exercises.items():
                    logger.info(f"  📚 {branch}: {exercise.title}")
            else:
                logger.info("📅 No hay ejercicios disponibles para hoy")

            return exercises

        except Exception as e:
            logger.error(f"❌ Error obteniendo ejercicios de hoy: {e}")
            return {}


async def main():
    """Función principal"""
    scheduler = DailyExerciseScheduler()

    # Verificar argumentos de línea de comandos
    if len(sys.argv) > 1:
        command = sys.argv[1]

        if command == "generate":
            # Generar ejercicios para hoy
            await scheduler.start_daily_generation()

        elif command == "start":
            # Iniciar scheduler automático
            await scheduler.start_scheduler()

        elif command == "branch":
            # Generar para rama específica
            if len(sys.argv) > 2:
                branch = sys.argv[2]
                await scheduler.generate_for_specific_branch(branch)
            else:
                logger.error(
                    "❌ Debes especificar una rama: python daily_exercise_scheduler.py branch <rama>"
                )

        elif command == "list":
            # Listar ejercicios de hoy
            scheduler.get_today_exercises()

        elif command == "test":
            # Probar generación
            logger.info("🧪 Probando generación de ejercicios...")
            await scheduler.start_daily_generation()

        else:
            logger.error(f"❌ Comando desconocido: {command}")
            print_usage()
    else:
        print_usage()


def print_usage():
    """Mostrar uso del script"""
    print(
        """
📚 Generador de Ejercicios Diarios - Sheily AI

Uso:
  python daily_exercise_scheduler.py <comando>

Comandos:
  generate    - Generar ejercicios para hoy
  start       - Iniciar scheduler automático (12:00 PM)
  branch <r>  - Generar ejercicio para rama específica
  list        - Listar ejercicios de hoy
  test        - Probar generación

Ejemplos:
  python daily_exercise_scheduler.py generate
  python daily_exercise_scheduler.py branch computación_y_programación
  python daily_exercise_scheduler.py start
    """
    )


if __name__ == "__main__":
    # Crear directorio de logs si no existe
    Path("logs").mkdir(exist_ok=True)

    # Ejecutar
    asyncio.run(main())
