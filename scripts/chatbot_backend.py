#!/usr/bin/env python3
"""
Chatbot SHEILY usando el servidor backend existente
"""

import sys
import os
import time
import json
import requests
from datetime import datetime


def test_backend_server():
    """Probar el servidor backend"""
    print("🔍 Probando servidor backend...")

    try:
        # Verificar que el servidor esté disponible
        response = requests.get("http://localhost:8000/", timeout=10)
        print(f"✅ Servidor backend disponible (status: {response.status_code})")
        return True

    except Exception as e:
        print(f"❌ Error conectando con servidor backend: {e}")
        return False


def chat_with_backend(message):
    """Chat con el servidor backend"""
    try:
        # Preparar datos para el chat
        chat_data = {"messages": [{"role": "user", "content": message}]}

        # Enviar petición al servidor
        response = requests.post(
            "http://localhost:8000/chat", json=chat_data, timeout=60
        )

        if response.status_code == 200:
            result = response.json()
            return result.get("response", "Lo siento, no pude generar una respuesta.")
        else:
            return f"Error del servidor: {response.status_code} - {response.text}"

    except Exception as e:
        return f"Error: {e}"


def start_backend_chatbot():
    """Iniciar chatbot con servidor backend"""
    print("\n🤖 Iniciando Chatbot SHEILY (Backend)")
    print("=" * 50)
    print("Escribe 'salir' para terminar")
    print("=" * 50)

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

            response = chat_with_backend(user_input)

            processing_time = time.time() - start_time

            # Mostrar respuesta
            print(f"\n🤖 SHEILY: {response}")
            print(f"⏱️ Tiempo: {processing_time:.2f}s")

        except KeyboardInterrupt:
            print("\n👋 ¡Hasta luego!")
            break
        except Exception as e:
            print(f"❌ Error: {e}")


def main():
    """Función principal"""
    print("🚀 Iniciando Chatbot SHEILY (Backend)")
    print("=" * 50)

    # Probar servidor backend
    if test_backend_server():
        print("\n✅ Sistema listo para usar")
        start_backend_chatbot()
    else:
        print("\n❌ No se pudo conectar con el servidor backend")
        print("Verifica que el servidor esté ejecutándose en el puerto 8000")
        return 1

    return 0


if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)
