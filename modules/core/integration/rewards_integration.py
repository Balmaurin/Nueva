#!/usr/bin/env python3
import sys
import os
import logging
from typing import Dict, Any, Optional

# Añadir directorios al path
sys.path.append(
    os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
)

from modules.rewards.reward_system import SheilyRewardSystem
from modules.rewards.tracker import SessionTracker
from modules.rewards.contextual_accuracy import ContextualAccuracyEvaluator
from datetime import datetime, UTC


class SheilyModelRewardsIntegrator:
    """
    Integrador de recompensas para el modelo Sheily-AI
    Gestiona la interacción entre el modelo de lenguaje y el sistema de recompensas
    """

    def __init__(
        self,
        model_config_path: Optional[str] = None,
        rewards_config: Optional[Dict[str, Any]] = None,
    ):
        """
        Inicializar integrador de recompensas

        Args:
            model_config_path (str, optional): Ruta a la configuración del modelo
            rewards_config (dict, optional): Configuración personalizada de recompensas
        """
        # Configuración de logging
        logging.basicConfig(
            level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
        )
        self.logger = logging.getLogger(__name__)

        # Cargar configuraciones
        self.model_config = self._load_model_config(model_config_path)
        self.rewards_config = rewards_config or {}

        # Inicializar componentes de recompensas
        self.reward_system = SheilyRewardSystem(
            vault_path=self.rewards_config.get("vault_path", "rewards/vault"),
            max_vault_size=self.rewards_config.get("max_vault_size", 10000),
            retention_days=self.rewards_config.get("retention_days", 90),
        )

        self.session_tracker = SessionTracker(
            storage_path=self.rewards_config.get("sessions_path", "rewards/sessions"),
            max_sessions=self.rewards_config.get("max_sessions", 1000),
            retention_days=self.rewards_config.get("retention_days", 90),
        )

        self.contextual_evaluator = ContextualAccuracyEvaluator()

        # Métricas de rendimiento
        self.performance_metrics = {
            "total_interactions": 0,
            "total_sheilys_earned": 0,
            "domain_performance": {},
        }

    def _load_model_config(self, config_path: Optional[str] = None) -> Dict[str, Any]:
        """
        Cargar configuración del modelo

        Args:
            config_path (str, optional): Ruta al archivo de configuración

        Returns:
            dict: Configuración del modelo
        """
        # Implementación básica, expandir según necesidad
        default_config = {
            "model_type": "sheily-personal-model",
            "context_window": 128000,
            "quantization": "4-bit NF4",
        }

        if config_path and os.path.exists(config_path):
            try:
                import yaml

                with open(config_path, "r") as f:
                    user_config = yaml.safe_load(f)
                    default_config.update(user_config)
            except Exception as e:
                self.logger.warning(f"Error cargando configuración: {e}")

        return default_config

    def process_interaction(
        self,
        domain: str,
        query: str,
        response: str,
        additional_metadata: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """
        Procesar una interacción completa con sistema de recompensas

        Args:
            domain (str): Dominio de la interacción
            query (str): Consulta del usuario
            response (str): Respuesta generada
            additional_metadata (dict, optional): Metadatos adicionales

        Returns:
            dict: Resultado de la interacción con recompensas
        """
        # 1. Evaluar precisión contextual
        contextual_score = self.contextual_evaluator.contextual_precision(
            query, response
        )

        # 2. Calcular puntuación de calidad
        quality_score = (
            contextual_score * 0.7  # Precisión contextual
            + 0.3  # Componente base de calidad
        )

        # 3. Preparar datos de sesión
        session_data = {
            "domain": domain,
            "query": query,
            "response": response,
            "quality_score": quality_score,
            "tokens_used": len(query.split()) + len(response.split()),
            "contextual_accuracy": contextual_score,
            "additional_metadata": additional_metadata or {},
        }

        # 4. Registrar sesión
        tracked_session = self.session_tracker.track_session(
            domain=domain, query=query, response=response, quality_score=quality_score
        )

        # 5. Calcular y registrar recompensa
        reward = self.reward_system.record_reward(tracked_session)

        # 6. Actualizar métricas de rendimiento
        self._update_performance_metrics(domain, reward["sheilys"])

        # 7. Preparar resultado detallado
        interaction_result = {
            "session_id": tracked_session["session_id"],
            "domain": domain,
            "contextual_score": contextual_score,
            "quality_score": quality_score,
            "sheilys_earned": reward["sheilys"],
            "additional_metadata": additional_metadata,
        }

        return interaction_result

    def _update_performance_metrics(self, domain: str, sheilys: float):
        """
        Actualizar métricas de rendimiento

        Args:
            domain (str): Dominio de la interacción
            sheilys (float): Sheilys ganados
        """
        # Incrementar contadores globales
        self.performance_metrics["total_interactions"] += 1
        self.performance_metrics["total_sheilys_earned"] += sheilys

        # Actualizar rendimiento por dominio
        if domain not in self.performance_metrics["domain_performance"]:
            self.performance_metrics["domain_performance"][domain] = {
                "total_interactions": 0,
                "total_sheilys": 0,
                "average_sheilys_per_interaction": 0,
            }

        domain_metrics = self.performance_metrics["domain_performance"][domain]
        domain_metrics["total_interactions"] += 1
        domain_metrics["total_sheilys"] += sheilys
        domain_metrics["average_sheilys_per_interaction"] = (
            domain_metrics["total_sheilys"] / domain_metrics["total_interactions"]
        )

    def get_domain_performance(self, domain: Optional[str] = None) -> Dict[str, Any]:
        """
        Obtener métricas de rendimiento

        Args:
            domain (str, optional): Dominio específico a consultar

        Returns:
            dict: Métricas de rendimiento
        """
        if domain:
            return self.performance_metrics["domain_performance"].get(domain, {})

        return self.performance_metrics

    def export_performance_report(
        self, output_path: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Exportar informe de rendimiento

        Args:
            output_path (str, optional): Ruta para guardar el informe

        Returns:
            dict: Informe de rendimiento
        """
        import json
        from datetime import datetime

        report = {
            "timestamp": datetime.now(UTC).isoformat(),
            "total_interactions": self.performance_metrics["total_interactions"],
            "total_sheilys_earned": self.performance_metrics["total_sheilys_earned"],
            "domain_performance": self.performance_metrics["domain_performance"],
        }

        if output_path:
            try:
                with open(output_path, "w") as f:
                    json.dump(report, f, indent=2)
                self.logger.info(f"Informe exportado a {output_path}")
            except Exception as e:
                self.logger.error(f"Error exportando informe: {e}")

        return report


# Ejemplo de uso
def main():
    # Inicializar integrador
    rewards_integrator = SheilyModelRewardsIntegrator()

    # Ejemplo de interacciones en diferentes dominios
    interactions = [
        {
            "domain": "vida_diaria,_legal_práctico_y_trámites",
            "query": "¿Cuáles son los documentos necesarios para tramitar un pasaporte?",
            "response": "Para tramitar un pasaporte, necesitas presentar tu documento de identidad, comprobante de domicilio, y fotografías recientes.",
        },
        {
            "domain": "sistemas_devops_redes",
            "query": "Explícame los conceptos básicos de Docker",
            "response": "Docker es una plataforma de contenedores que permite empaquetar, distribuir y ejecutar aplicaciones de manera consistente en diferentes entornos.",
        },
    ]

    # Procesar interacciones
    for interaction in interactions:
        result = rewards_integrator.process_interaction(
            domain=interaction["domain"],
            query=interaction["query"],
            response=interaction["response"],
        )
        print(json.dumps(result, indent=2))

    # Exportar informe de rendimiento
    rewards_integrator.export_performance_report("performance_report.json")

    # Mostrar métricas globales
    print("\nMétricas Globales:")
    print(json.dumps(rewards_integrator.get_domain_performance(), indent=2))


if __name__ == "__main__":
    main()
