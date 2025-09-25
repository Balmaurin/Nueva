#!/usr/bin/env python3
"""
Script para iniciar el chatbot SHEILY
"""

import sys
import os
import time
import json
from datetime import datetime

# Añadir paths necesarios
sys.path.append(os.path.join(os.path.dirname(__file__), ".."))
sys.path.append(os.path.join(os.path.dirname(__file__), "..", "backend"))


def test_llm_client():
    """Probar el cliente LLM"""
    print("🔍 Probando cliente LLM...")

    try:
        from llm_client import get_llm_client

        client = get_llm_client()
        health = client.health_check()

        print(f"📊 Estado del LLM: {health['status']}")

        if health["status"] == "healthy":
            # Probar una consulta simple
            messages = [{"role": "user", "content": "Hola SHEILY, ¿cómo estás?"}]
            response = client.llm_chat(messages, max_tokens=50)
            print(f"✅ Respuesta: {response[:100]}...")
            return True
        else:
            print(f"⚠️ LLM no disponible: {health}")
            return False

    except Exception as e:
        print(f"❌ Error en cliente LLM: {e}")
        return False


def test_orchestrator():
    """Probar el orquestador"""
    print("\n🔍 Probando orquestador...")

    try:
        from modules.orchestrator.main_orchestrator import MainOrchestrator

        orchestrator = MainOrchestrator()
        print("✅ Orquestador inicializado")

        # Verificar estado del LLM
        llm_status = orchestrator.get_llm_status()
        print(f"📊 Estado LLM en orquestador: {llm_status['status']}")

        # Probar una consulta
        response = orchestrator.process_query("¿Qué es la inteligencia artificial?")
        print(f"✅ Consulta procesada - Fuente: {response.get('source', 'unknown')}")
        print(f"📝 Respuesta: {response.get('text', '')[:100]}...")

        return True

    except Exception as e:
        print(f"❌ Error en orquestador: {e}")
        return False


def start_chatbot():
    """Iniciar el chatbot interactivo"""
    print("\n🤖 Iniciando chatbot SHEILY...")
    print("=" * 50)
    print("Escribe 'salir' para terminar")
    print("=" * 50)

    try:
        from modules.orchestrator.main_orchestrator import MainOrchestrator

        orchestrator = MainOrchestrator()

        while True:
            try:
                # Obtener entrada del usuario
                user_input = input("\n👤 Tú: ").strip()

                if user_input.lower() in ["salir", "exit", "quit"]:
                    print("👋 ¡Hasta luego!")
                    break

                if not user_input:
                    continue

                # Procesar consulta
                print("🤔 SHEILY está pensando...")
                start_time = time.time()

                response = orchestrator.process_query(user_input)

                processing_time = time.time() - start_time

                # Mostrar respuesta
                print(
                    f"\n🤖 SHEILY: {response.get('text', 'Lo siento, no pude procesar tu consulta.')}"
                )
                print(
                    f"⏱️ Tiempo: {processing_time:.2f}s | Fuente: {response.get('source', 'unknown')}"
                )

            except KeyboardInterrupt:
                print("\n👋 ¡Hasta luego!")
                break
            except Exception as e:
                print(f"❌ Error: {e}")

    except Exception as e:
        print(f"❌ Error iniciando chatbot: {e}")


def main():
    """Función principal"""
    print("🚀 Iniciando Sistema Chatbot SHEILY")
    print("=" * 50)

    # Probar componentes
    llm_ok = test_llm_client()
    orchestrator_ok = test_orchestrator()

    if llm_ok and orchestrator_ok:
        print("\n✅ Sistema listo para usar")
        start_chatbot()
    else:
        print("\n⚠️ Hay problemas con el sistema")
        print("Revisa la configuración y vuelve a intentar")
        return 1

    return 0


if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)
