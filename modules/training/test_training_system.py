#!/usr/bin/env python3
"""
Script de prueba para el sistema de entrenamiento avanzado
"""

import sys
import os
import tempfile
import json

sys.path.append(os.path.join(os.path.dirname(__file__), "modules"))

from modules.training.advanced_training_system import AdvancedTrainingSystem


def test_training_system():
    """Prueba el sistema de entrenamiento avanzado"""
    print("🧪 Probando sistema de entrenamiento avanzado...")

    # Crear directorio temporal para configuración
    test_dir = tempfile.mkdtemp()
    config_path = os.path.join(test_dir, "test_training_config.json")

    try:
        # Crear instancia del sistema
        system = AdvancedTrainingSystem(config_path=config_path)

        print(f"📚 Ejercicios disponibles: {len(system.exercises)}")

        # Listar ejercicios
        print("\n📋 Lista de ejercicios:")
        for exercise_id, exercise in system.exercises.items():
            print(f"  - {exercise.title} ({exercise.difficulty})")
            print(f"    Preguntas: {exercise.total_questions}")
            print(f"    Categoría: {exercise.category}")
            print(f"    Tiempo límite: {exercise.time_limit_minutes} minutos")
            print()

        # Probar obtención de ejercicio específico
        if "comprehension" in system.exercises:
            print("🎯 Probando ejercicio de comprensión:")
            exercise = system.exercises["comprehension"]

            print(f"Título: {exercise.title}")
            print(f"Descripción: {exercise.description}")
            print(f"Objetivos de aprendizaje: {exercise.learning_objectives}")
            print(f"Preguntas: {len(exercise.questions)}")

            # Mostrar algunas preguntas
            print("\n📝 Ejemplos de preguntas:")
            for i, question in enumerate(exercise.questions[:3]):
                print(f"  {i+1}. {question.question}")
                print(f"     Dificultad: {question.difficulty}")
                print(f"     Puntos: {question.points}")
                print(f"     Categoría: {question.category}")
                print()

        # Probar simulación de entrenamiento
        print("🎮 Simulando entrenamiento...")
        user_id = "test_user_123"

        # Simular progreso del usuario
        system.user_progress[user_id] = {
            "completed_exercises": [],
            "total_points": 0,
            "current_streak": 0,
            "last_activity": "2024-01-15",
        }

        # Simular completar un ejercicio
        if "comprehension" in system.exercises:
            exercise = system.exercises["comprehension"]
            system.user_progress[user_id]["completed_exercises"].append(
                {
                    "exercise_id": "comprehension",
                    "score": 85,
                    "completed_at": "2024-01-15T10:30:00",
                    "time_taken": 15,
                }
            )
            system.user_progress[user_id]["total_points"] += 85
            system.user_progress[user_id]["current_streak"] = 1

            print(f"✅ Usuario {user_id} completó ejercicio de comprensión")
            print(f"   Puntuación: 85/100")
            print(f"   Tiempo: 15 minutos")
            print(f"   Puntos totales: {system.user_progress[user_id]['total_points']}")

        # Probar obtención de estadísticas
        print("\n📊 Estadísticas del sistema:")
        stats = system.get_system_statistics()
        print(f"Total de ejercicios: {stats['total_exercises']}")
        print(f"Total de preguntas: {stats['total_questions']}")
        print(f"Categorías disponibles: {stats['categories']}")
        print(f"Usuarios activos: {stats['active_users']}")

        # Probar recomendaciones
        print("\n💡 Recomendaciones para el usuario:")
        recommendations = system.get_recommendations_for_user(user_id)
        print(f"Ejercicios recomendados: {len(recommendations)}")
        for rec in recommendations[:3]:
            print(f"  - {rec['title']} ({rec['reason']})")

        print("\n✅ Pruebas completadas exitosamente!")

    except Exception as e:
        print(f"❌ Error durante las pruebas: {e}")
        raise
    finally:
        # Limpiar archivos temporales
        import shutil

        if os.path.exists(test_dir):
            shutil.rmtree(test_dir)
        print(f"🧹 Directorio temporal eliminado: {test_dir}")


if __name__ == "__main__":
    test_training_system()
