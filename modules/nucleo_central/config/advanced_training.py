"""
Configuración de Entrenamiento Avanzado
======================================

Gestión de configuraciones para ejercicios de entrenamiento avanzado
"""

import json
import os
from typing import Dict, Any


def load_training_config() -> Dict[str, Any]:
    """
    Cargar configuración de entrenamiento avanzado

    Returns:
        Dict con la configuración de entrenamiento
    """
    # Apuntar a la configuración centralizada desde el directorio raíz del proyecto
    current_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.abspath(os.path.join(current_dir, "../../.."))
    config_path = os.path.join(project_root, "config", "advanced_training_config.json")

    try:
        with open(config_path, "r", encoding="utf-8") as f:
            return json.load(f)
    except FileNotFoundError:
        return {
            "exercises": [
                {
                    "id": "default",
                    "title": "Ejercicio por defecto",
                    "description": "Ejercicio básico de entrenamiento",
                    "category": "general",
                    "difficulty": "easy",
                    "total_questions": 5,
                    "time_limit_minutes": 10,
                    "points_per_question": 5,
                }
            ]
        }
    except Exception as e:
        print(f"Error cargando configuración de entrenamiento: {e}")
        return {}
