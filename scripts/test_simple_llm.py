"""
Script de prueba simple para el cliente LLM local
"""

import os
import sys

# Añadir el directorio backend al path
sys.path.append(os.path.join(os.path.dirname(__file__), "..", "backend"))


def test_llm_client_simple() -> bool:
    """Probar el cliente LLM con el servidor local."""

    print("🔍 Probando cliente LLM local...")

    try:
        from llm_client import LLMClient

        client = LLMClient()
        print(f"✅ Cliente inicializado - Modelo: {client.model_name}")

        health = client.health_check()
        print(f"📊 Estado: {health['status']}")

        if health["status"] != "healthy":
            print(f"❌ El servidor LLM no está listo: {health}")
            return False

        messages = [{"role": "user", "content": "Hola"}]
        response = client.llm_chat(messages, max_tokens=40, temperature=0.2)
        print(f"✅ Respuesta recibida: {response[:80]}...")
        return True

    except Exception as exc:
        print(f"❌ Error en cliente LLM: {exc}")
        return False


def main() -> int:
    """Función principal."""

    print("🚀 Prueba simple del sistema LLM")
    print("=" * 40)

    client_ok = test_llm_client_simple()

    print("\n" + "=" * 40)
    print("📊 RESUMEN")
    print("=" * 40)
    print(f"Cliente LLM: {'✅ OK' if client_ok else '❌ FALLÓ'}")

    if client_ok:
        print("\n🎉 ¡Sistema funcionando correctamente!")
        return 0

    print("\n⚠️ Hay problemas que resolver")
    return 1


if __name__ == "__main__":
    sys.exit(main())
