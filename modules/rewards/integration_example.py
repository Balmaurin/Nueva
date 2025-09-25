#!/usr/bin/env python3
import sys
import os
import json
from datetime import datetime

# Añadir el directorio padre al path para importaciones
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from modules.rewards.tracker import SessionTracker
from modules.rewards.reward_system import SheilyRewardSystem
from modules.rewards.contextual_accuracy import ContextualAccuracyEvaluator


class SheilyRewardsIntegration:
    """
    Clase que integra el sistema de tracking, recompensas y precisión contextual
    """

    def __init__(self, sessions_path="rewards/sessions", vault_path="rewards/vault"):
        """
        Inicializar componentes del sistema de recompensas

        Args:
            sessions_path (str): Ruta para almacenar sesiones
            vault_path (str): Ruta para almacenar recompensas
        """
        # Inicializar componentes
        self.session_tracker = SessionTracker(storage_path=sessions_path)
        self.reward_system = ShailiRewardSystem(vault_path=vault_path)
        self.contextual_evaluator = ContextualAccuracyEvaluator()

    def process_interaction(self, domain: str, query: str, response: str) -> dict:
        """
        Procesar una interacción completa

        Args:
            domain (str): Dominio de la interacción
            query (str): Consulta del usuario
            response (str): Respuesta generada

        Returns:
            dict: Detalles de la interacción procesada
        """
        # 1. Evaluar precisión contextual
        contextual_score = self.contextual_evaluator.contextual_precision(
            query, response
        )

        # 2. Calcular puntuación de calidad general
        quality_score = (
            contextual_score * 0.7  # Precisión contextual
            + 0.3  # Componente base de calidad
        )

        # 3. Preparar datos de sesión
        session_data = {
            "timestamp": datetime.utcnow().isoformat(),
            "domain": domain,
            "query": query,
            "response": response,
            "quality_score": quality_score,
            "tokens_used": len(query.split()) + len(response.split()),
            "contextual_accuracy": contextual_score,
        }

        # 4. Registrar sesión
        tracked_session = self.session_tracker.track_session(
            domain=domain, query=query, response=response, quality_score=quality_score
        )

        # 5. Calcular y registrar recompensa
        reward = self.reward_system.record_reward(tracked_session)

        # 6. Preparar resultado detallado
        interaction_result = {
            "session_id": tracked_session["session_id"],
            "domain": domain,
            "contextual_score": contextual_score,
            "quality_score": quality_score,
            "sheilys_earned": reward["sheilys"],
        }

        return interaction_result

    def get_domain_performance(self, domain: str) -> dict:
        """
        Obtener rendimiento de un dominio específico

        Args:
            domain (str): Dominio a evaluar

        Returns:
            dict: Métricas de rendimiento del dominio
        """
        # Obtener sesiones útiles para el dominio
        useful_sessions = self.session_tracker.get_useful_sessions(
            min_quality_score=0.7, domain=domain
        )

        # Calcular métricas
        total_sheilys = self.reward_system.get_total_sheilys(domain)
        avg_quality = (
            sum(session.get("quality_score", 0) for session in useful_sessions)
            / len(useful_sessions)
            if useful_sessions
            else 0
        )

        return {
            "domain": domain,
            "total_sheilys": total_sheilys,
            "useful_sessions_count": len(useful_sessions),
            "average_quality_score": round(avg_quality, 2),
        }


def main():
    """
    Ejemplo de uso del sistema de recompensas
    """
    # Inicializar integración
    rewards_integration = ShailiRewardsIntegration()

    # Ejemplos de interacciones en diferentes dominios
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

    # Procesar cada interacción
    results = []
    for interaction in interactions:
        result = rewards_integration.process_interaction(
            domain=interaction["domain"],
            query=interaction["query"],
            response=interaction["response"],
        )
        results.append(result)
        print(f"Resultado de interacción en {interaction['domain']}:")
        print(json.dumps(result, indent=2))
        print("\n")

    # Obtener rendimiento por dominio
    domain_performances = [
        rewards_integration.get_domain_performance(interaction["domain"])
        for interaction in interactions
    ]

    print("Rendimiento por Dominio:")
    for performance in domain_performances:
        print(json.dumps(performance, indent=2))
        print("\n")


if __name__ == "__main__":
    main()
