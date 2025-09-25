#!/usr/bin/env python3
from tracker import SessionTracker
from reward_system import ShailiRewardSystem


def main():
    # Inicializar tracker de sesiones
    session_tracker = SessionTracker()

    # Inicializar sistema de recompensas
    reward_system = ShailiRewardSystem()

    # Ejemplo de sesiones en diferentes dominios
    sessions = [
        {
            "domain": "medicina",
            "query": "¿Cuáles son los síntomas de la hipertensión?",
            "response": "Los síntomas principales incluyen...",
            "quality_score": 0.85,
        },
        {
            "domain": "programación",
            "query": "Explícame el patrón de diseño Singleton en Python",
            "response": "El patrón Singleton asegura que una clase tenga solo una instancia...",
            "quality_score": 0.75,
        },
        {
            "domain": "general",
            "query": "¿Qué es la inteligencia artificial?",
            "response": "La inteligencia artificial es un campo de la computación...",
            "quality_score": 0.65,
        },
    ]

    # Procesar cada sesión
    for session_data in sessions:
        # Registrar sesión
        tracked_session = session_tracker.track_session(
            domain=session_data["domain"],
            query=session_data["query"],
            response=session_data["response"],
            quality_score=session_data["quality_score"],
        )

        # Registrar recompensa
        reward = reward_system.record_reward(tracked_session)
        print(f"Sesión en dominio {session_data['domain']}:")
        print(f"  Sheilys ganados: {reward['sheilys']}")

    # Obtener total de Sheilys por dominio
    print("\nTotal de Sheilys:")
    print(f"Medicina: {reward_system.get_total_sheilys('medicina')}")
    print(f"Programación: {reward_system.get_total_sheilys('programación')}")
    print(f"General: {reward_system.get_total_sheilys('general')}")

    # Limpiar sesiones y recompensas antiguas
    session_tracker.cleanup_old_sessions()
    reward_system.cleanup_old_rewards()


if __name__ == "__main__":
    main()
