#!/usr/bin/env python3
"""
Script de Gestión de Integración de Ejercicios Mejorados
Conecta los ejercicios mejorados con el sistema de entrenamiento avanzado
"""

import asyncio
import argparse
import logging
from datetime import datetime, timedelta
from pathlib import Path

import sys
from pathlib import Path

# Agregar el directorio raíz al path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

# Importar el integrador mejorado
from modules.core.enhanced_daily_exercise_integrator import (
    EnhancedDailyExerciseIntegrator,
    integrate_enhanced_exercises_manual,
)

# Configurar logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


class EnhancedIntegrationScheduler:
    """
    Scheduler para la integración de ejercicios mejorados
    """

    def __init__(self):
        self.integrator = EnhancedDailyExerciseIntegrator()
        self.scheduler = None

    async def integrate_exercises(self, target_date: str = None):
        """
        Integrar ejercicios mejorados al sistema de entrenamiento

        Args:
            target_date: Fecha objetivo en formato YYYY-MM-DD (opcional)
        """
        try:
            logger.info("🚀 Iniciando integración de ejercicios mejorados...")

            # Parsear fecha objetivo si se proporciona
            parsed_date = None
            if target_date:
                try:
                    parsed_date = datetime.strptime(target_date, "%Y-%m-%d")
                except ValueError:
                    logger.error(
                        f"Formato de fecha inválido: {target_date}. Use YYYY-MM-DD"
                    )
                    return

            # Ejecutar integración
            stats = await self.integrator.integrate_enhanced_exercises(parsed_date)

            # Mostrar resumen
            print(f"\n📊 Resumen de Integración:")
            print(f"   - Ejercicios procesados: {stats.total_exercises_processed}")
            print(f"   - Preguntas procesadas: {stats.total_questions_processed}")
            print(f"   - Integraciones exitosas: {stats.successful_integrations}")
            print(f"   - Integraciones fallidas: {stats.failed_integrations}")
            print(f"   - Tiempo de integración: {stats.integration_time:.2f}s")

            if stats.branches_processed:
                print(f"   - Ramas procesadas: {', '.join(stats.branches_processed)}")

            if stats.successful_integrations > 0:
                print(f"\n✅ Integración completada exitosamente!")
            else:
                print(
                    f"\n⚠️  No se integraron ejercicios. Verifique que existan ejercicios para la fecha especificada."
                )

        except Exception as e:
            logger.error(f"❌ Error en la integración: {e}")
            print(f"\n❌ Error durante la integración: {e}")

    async def start_scheduler(self):
        """
        Iniciar scheduler automático de integración
        """
        try:
            logger.info("⏰ Iniciando scheduler de integración automática...")

            self.scheduler = (
                await self.integrator.start_enhanced_integration_scheduler()
            )

            print("✅ Scheduler de integración iniciado")
            print(
                "   - Integración automática programada para las 12:30 PM diariamente"
            )
            print("   - Presione Ctrl+C para detener")

            # Mantener el scheduler ejecutándose
            try:
                while True:
                    await asyncio.sleep(1)
            except KeyboardInterrupt:
                logger.info("Deteniendo scheduler...")
                self.scheduler.shutdown()
                print("\n🛑 Scheduler detenido")

        except Exception as e:
            logger.error(f"❌ Error iniciando scheduler: {e}")
            print(f"\n❌ Error iniciando scheduler: {e}")

    async def show_integration_history(self, days: int = 7):
        """
        Mostrar historial de integraciones

        Args:
            days: Número de días hacia atrás
        """
        try:
            logger.info(
                f"📊 Obteniendo historial de integraciones de los últimos {days} días..."
            )

            history = await self.integrator.get_integration_history(days)

            if not history:
                print(
                    f"\n📊 No se encontraron registros de integración en los últimos {days} días"
                )
                return

            print(f"\n📊 Historial de Integraciones (últimos {days} días):")
            print("=" * 80)

            total_exercises = 0
            total_questions = 0
            total_successful = 0
            total_failed = 0

            for stats in history:
                date_str = stats.created_date.strftime("%Y-%m-%d")
                print(f"\n📅 {date_str}:")
                print(f"   - Ejercicios: {stats.total_exercises_processed}")
                print(f"   - Preguntas: {stats.total_questions_processed}")
                print(f"   - Exitosas: {stats.successful_integrations}")
                print(f"   - Fallidas: {stats.failed_integrations}")
                print(f"   - Tiempo: {stats.integration_time:.2f}s")

                total_exercises += stats.total_exercises_processed
                total_questions += stats.total_questions_processed
                total_successful += stats.successful_integrations
                total_failed += stats.failed_integrations

            print("\n" + "=" * 80)
            print(f"📈 Totales ({days} días):")
            print(f"   - Ejercicios totales: {total_exercises}")
            print(f"   - Preguntas totales: {total_questions}")
            print(f"   - Integraciones exitosas: {total_successful}")
            print(f"   - Integraciones fallidas: {total_failed}")

            if total_successful > 0:
                success_rate = (
                    total_successful / (total_successful + total_failed)
                ) * 100
                print(f"   - Tasa de éxito: {success_rate:.1f}%")

        except Exception as e:
            logger.error(f"❌ Error obteniendo historial: {e}")
            print(f"\n❌ Error obteniendo historial: {e}")

    async def show_integration_status(self):
        """
        Mostrar estado actual de la integración
        """
        try:
            logger.info("📊 Verificando estado de integración...")

            # Verificar si hay ejercicios mejorados disponibles
            enhanced_exercises_path = Path("sheily_ai/data/enhanced_daily_exercises")
            if not enhanced_exercises_path.exists():
                print("\n📊 Estado de Integración:")
                print("   - ❌ No se encontró directorio de ejercicios mejorados")
                return

            # Contar archivos de ejercicios
            exercise_files = list(enhanced_exercises_path.glob("*.json"))

            # Verificar sistema de entrenamiento
            training_system_path = Path("sheily_ai/data/training_system")
            training_files = []
            if training_system_path.exists():
                training_files = list(training_system_path.rglob("*.json"))

            print("\n📊 Estado de Integración:")
            print(f"   - 📁 Ejercicios mejorados disponibles: {len(exercise_files)}")
            print(
                f"   - 🎯 Ejercicios en sistema de entrenamiento: {len(training_files)}"
            )

            if exercise_files:
                # Mostrar ejercicios más recientes
                latest_files = sorted(
                    exercise_files, key=lambda x: x.stat().st_mtime, reverse=True
                )[:5]
                print(f"\n📅 Ejercicios más recientes:")
                for file_path in latest_files:
                    mtime = datetime.fromtimestamp(file_path.stat().st_mtime)
                    print(f"   - {file_path.name} ({mtime.strftime('%Y-%m-%d %H:%M')})")

            # Verificar scheduler
            if self.scheduler and self.scheduler.running:
                print(f"\n⏰ Scheduler de integración: ✅ Activo")
            else:
                print(f"\n⏰ Scheduler de integración: ❌ Inactivo")

        except Exception as e:
            logger.error(f"❌ Error verificando estado: {e}")
            print(f"\n❌ Error verificando estado: {e}")


async def main():
    """
    Función principal del script
    """
    parser = argparse.ArgumentParser(
        description="Gestión de Integración de Ejercicios Mejorados",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Ejemplos de uso:
  # Integrar ejercicios de hoy
  python enhanced_integration_scheduler.py integrate
  
  # Integrar ejercicios de una fecha específica
  python enhanced_integration_scheduler.py integrate --date 2025-08-29
  
  # Iniciar scheduler automático
  python enhanced_integration_scheduler.py start
  
  # Mostrar historial de integraciones
  python enhanced_integration_scheduler.py history --days 7
  
  # Mostrar estado actual
  python enhanced_integration_scheduler.py status
        """,
    )

    subparsers = parser.add_subparsers(dest="command", help="Comandos disponibles")

    # Comando integrate
    integrate_parser = subparsers.add_parser(
        "integrate", help="Integrar ejercicios mejorados"
    )
    integrate_parser.add_argument(
        "--date",
        type=str,
        help="Fecha objetivo en formato YYYY-MM-DD (por defecto: hoy)",
    )

    # Comando start
    start_parser = subparsers.add_parser("start", help="Iniciar scheduler automático")

    # Comando history
    history_parser = subparsers.add_parser(
        "history", help="Mostrar historial de integraciones"
    )
    history_parser.add_argument(
        "--days",
        type=int,
        default=7,
        help="Número de días hacia atrás (por defecto: 7)",
    )

    # Comando status
    status_parser = subparsers.add_parser(
        "status", help="Mostrar estado actual de integración"
    )

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        return

    scheduler = EnhancedIntegrationScheduler()

    try:
        if args.command == "integrate":
            await scheduler.integrate_exercises(args.date)

        elif args.command == "start":
            await scheduler.start_scheduler()

        elif args.command == "history":
            await scheduler.show_integration_history(args.days)

        elif args.command == "status":
            await scheduler.show_integration_status()

    except KeyboardInterrupt:
        print("\n🛑 Operación cancelada por el usuario")
    except Exception as e:
        logger.error(f"❌ Error en la ejecución: {e}")
        print(f"\n❌ Error en la ejecución: {e}")


if __name__ == "__main__":
    asyncio.run(main())
