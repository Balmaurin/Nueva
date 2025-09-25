"""
Configuración de Límites de Velocidad
====================================

Gestión de límites de velocidad para operaciones del sistema
"""

import json
import os
from typing import Dict, Any


def load_rate_limits() -> Dict[str, Any]:
    """
    Cargar configuración de límites de velocidad

    Returns:
        Dict con la configuración de rate limits
    """
    # Apuntar a la configuración centralizada desde el directorio raíz del proyecto
    current_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.abspath(os.path.join(current_dir, "../../.."))
    config_path = os.path.join(project_root, "config", "rate_limits.json")

    try:
        with open(config_path, "r", encoding="utf-8") as f:
            return json.load(f)
    except FileNotFoundError:
        return {
            "rules": [
                {
                    "rule_id": "default",
                    "description": "Límite por defecto",
                    "config": {
                        "max_requests": 100,
                        "time_window": 3600,
                        "burst_limit": 20,
                        "cooldown_period": 60,
                    },
                    "enabled": True,
                }
            ]
        }
    except Exception as e:
        print(f"Error cargando rate limits: {e}")
        return {}
