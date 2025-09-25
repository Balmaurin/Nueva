#!/usr/bin/env python3
import os
import json
import numpy as np
from typing import Dict, Any, List


class AdaptiveRewardsOptimizer:
    """
    Sistema de optimización adaptativa de algoritmos de recompensa
    Ajusta dinámicamente los pesos y factores de evaluación
    """

    def __init__(
        self,
        initial_config_path: str = "rewards/adaptive_config.json",
        learning_rate: float = 0.1,
        decay_rate: float = 0.95,
    ):
        """
        Inicializar optimizador adaptativo

        Args:
            initial_config_path (str): Ruta a configuración inicial
            learning_rate (float): Tasa de aprendizaje
            decay_rate (float): Tasa de decaimiento para ajustes
        """
        # Cargar configuración inicial
        self.config = self._load_initial_config(initial_config_path)

        # Parámetros de aprendizaje
        self.learning_rate = learning_rate
        self.decay_rate = decay_rate

        # Historial de rendimiento
        self.performance_history = {
            "domain_performance": {},
            "global_metrics": {"total_interactions": 0, "total_sheilys": 0},
        }

    def _load_initial_config(self, config_path: str) -> Dict[str, Any]:
        """
        Cargar configuración inicial de recompensas

        Args:
            config_path (str): Ruta al archivo de configuración

        Returns:
            dict: Configuración de recompensas
        """
        default_config = {
            "factors": {
                "quality_score": 0.25,
                "domain_complexity": 0.2,
                "tokens_complexity": 0.15,
                "novelty_factor": 0.1,
                "interaction_depth": 0.15,
                "contextual_accuracy": 0.15,
            },
            "domain_complexity_map": {
                "medicina": 1.3,
                "ciberseguridad": 1.25,
                "programación": 1.2,
                "matemáticas": 1.15,
                "ciencia": 1.1,
                "ingeniería": 1.05,
                "general": 1.0,
                "entretenimiento": 0.9,
            },
        }

        # Intentar cargar configuración personalizada
        if os.path.exists(config_path):
            try:
                with open(config_path, "r") as f:
                    user_config = json.load(f)
                    default_config.update(user_config)
            except Exception as e:
                print(f"Error cargando configuración: {e}")

        return default_config

    def update_performance(self, domain: str, interaction_data: Dict[str, Any]):
        """
        Actualizar historial de rendimiento

        Args:
            domain (str): Dominio de la interacción
            interaction_data (dict): Datos de la interacción
        """
        # Actualizar métricas globales
        self.performance_history["global_metrics"]["total_interactions"] += 1
        self.performance_history["global_metrics"][
            "total_sheilys"
        ] += interaction_data.get("sheilys_earned", 0)

        # Inicializar rendimiento de dominio si no existe
        if domain not in self.performance_history["domain_performance"]:
            self.performance_history["domain_performance"][domain] = {
                "interactions": [],
                "average_sheilys": 0,
                "performance_trend": [],
            }

        # Agregar interacción al historial
        domain_history = self.performance_history["domain_performance"][domain]
        domain_history["interactions"].append(interaction_data)

        # Calcular promedio de Sheilys
        sheilys_list = [
            interaction.get("sheilys_earned", 0)
            for interaction in domain_history["interactions"]
        ]
        domain_history["average_sheilys"] = np.mean(sheilys_list)

        # Actualizar tendencia de rendimiento
        domain_history["performance_trend"].append(
            interaction_data.get("sheilys_earned", 0)
        )

    def optimize_reward_factors(self):
        """
        Optimizar factores de recompensa basado en el rendimiento histórico

        Returns:
            dict: Configuración de factores optimizada
        """
        # Análisis de rendimiento global
        global_metrics = self.performance_history["global_metrics"]

        # Ajustar factores basado en rendimiento de dominios
        for domain, domain_data in self.performance_history[
            "domain_performance"
        ].items():
            # Calcular varianza de Sheilys
            sheilys_variance = (
                np.var(domain_data["performance_trend"])
                if domain_data["performance_trend"]
                else 0
            )
            average_sheilys = domain_data["average_sheilys"]

            # Estrategias de ajuste
            if sheilys_variance > 1.0:  # Alta variabilidad
                # Aumentar peso de factores de estabilidad
                self.config["factors"]["contextual_accuracy"] += self.learning_rate
                self.config["factors"]["quality_score"] += self.learning_rate * 0.5

            if average_sheilys < 2.0:  # Rendimiento bajo
                # Ajustar complejidad de dominio
                if domain in self.config["domain_complexity_map"]:
                    self.config["domain_complexity_map"][domain] *= (
                        1 + self.learning_rate
                    )

            # Normalizar factores
            total_factors = sum(self.config["factors"].values())
            for factor in self.config["factors"]:
                self.config["factors"][factor] /= total_factors

        # Aplicar decaimiento
        self.learning_rate *= self.decay_rate

        return self.config

    def save_optimized_config(self, output_path: str = "rewards/adaptive_config.json"):
        """
        Guardar configuración optimizada

        Args:
            output_path (str): Ruta para guardar configuración
        """
        try:
            with open(output_path, "w") as f:
                json.dump(self.config, f, indent=2)
            print(f"Configuración guardada en {output_path}")
        except Exception as e:
            print(f"Error guardando configuración: {e}")

    def get_optimized_factors(self) -> Dict[str, float]:
        """
        Obtener factores de recompensa optimizados

        Returns:
            dict: Factores de recompensa
        """
        return self.config["factors"]

    def get_domain_complexity_map(self) -> Dict[str, float]:
        """
        Obtener mapa de complejidad de dominios

        Returns:
            dict: Mapa de complejidad de dominios
        """
        return self.config["domain_complexity_map"]


def main():
    """
    Ejemplo de uso del optimizador adaptativo
    """
    # Inicializar optimizador
    optimizer = AdaptiveRewardsOptimizer()

    # Ejemplo de interacciones
    sample_interactions = [
        {
            "domain": "vida_diaria,_legal_práctico_y_trámites",
            "sheilys_earned": 3.5,
            "contextual_score": 0.8,
        },
        {
            "domain": "sistemas_devops_redes",
            "sheilys_earned": 4.2,
            "contextual_score": 0.9,
        },
    ]

    # Procesar interacciones reales
    for interaction in sample_interactions:
        optimizer.update_performance(
            domain=interaction["domain"], interaction_data=interaction
        )

    # Optimizar factores
    optimized_config = optimizer.optimize_reward_factors()

    # Mostrar resultados
    print("Factores de Recompensa Optimizados:")
    print(json.dumps(optimized_config["factors"], indent=2))

    # Guardar configuración
    optimizer.save_optimized_config()


if __name__ == "__main__":
    main()
