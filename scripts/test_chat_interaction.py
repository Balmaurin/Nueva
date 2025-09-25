#!/usr/bin/env python3
"""
Script de prueba de interacciones de chat con Modelo Phi-3 de 4 bits
"""

import requests
import json
import logging
import sys
import traceback

# Configurar logging
logging.basicConfig(
    level=logging.DEBUG, format="%(asctime)s - %(levelname)s: %(message)s"
)
logger = logging.getLogger(__name__)

# Configuración de prueba
BASE_URL = "http://localhost:8000/api"  # Cambiar a ruta base con /api
TEST_USER = {
    "username": "usuario_prueba_modelo",
    "email": "usuario_prueba_modelo@sheily.ai",
    "password": "Prueba123!",
    "full_name": "Usuario Prueba Phi-3",
}
TEST_USER_TOKEN = None


def register_or_login():
    """Registrar o iniciar sesión con usuario de prueba"""
    global TEST_USER_TOKEN
    try:
        # Intentar iniciar sesión primero
        login_data = {
            "username": TEST_USER["username"],
            "password": TEST_USER["password"],
        }
        logger.debug(f"Intentando iniciar sesión con: {login_data}")

        login_response = requests.post(f"{BASE_URL}/auth/login", json=login_data)
        logger.debug(f"Respuesta de login: {login_response.status_code}")
        logger.debug(f"Contenido de respuesta: {login_response.text}")

        if login_response.status_code == 200:
            TEST_USER_TOKEN = login_response.json()["token"]
            logger.info("✅ Inicio de sesión exitoso")
            return TEST_USER_TOKEN

        # Si el inicio de sesión falla, intentar registrar
        register_data = {
            "username": TEST_USER["username"],
            "email": TEST_USER["email"],
            "password": TEST_USER["password"],
            "full_name": TEST_USER["full_name"],
        }
        logger.debug(f"Intentando registrar usuario: {register_data}")

        register_response = requests.post(
            f"{BASE_URL}/auth/register", json=register_data
        )
        logger.debug(f"Respuesta de registro: {register_response.status_code}")
        logger.debug(f"Contenido de respuesta: {register_response.text}")

        register_response.raise_for_status()

        TEST_USER_TOKEN = register_response.json()["token"]
        logger.info("✅ Usuario registrado exitosamente")
        return TEST_USER_TOKEN

    except requests.exceptions.RequestException as e:
        logger.error(f"❌ Error en registro/login: {e}")
        if hasattr(e, "response"):
            logger.error(f"Detalles del error: {e.response.text}")
        logger.error(traceback.format_exc())
        return None


def create_chat_session(token):
    """Crear sesión de chat"""
    try:
        headers = {"Authorization": f"Bearer {token}"}

        # Imprimir información de depuración
        logger.debug(f"URL completa: {BASE_URL}/chat/session")
        logger.debug(f"Headers: {headers}")

        response = requests.post(f"{BASE_URL}/chat/session", headers=headers)

        # Imprimir información detallada de la respuesta
        logger.debug(f"Código de estado completo: {response.status_code}")
        logger.debug(f"Contenido de respuesta completo: {response.text}")
        logger.debug(f"Cabeceras de respuesta: {response.headers}")

        response.raise_for_status()
        session_id = response.json()["sessionId"]
        logger.info(f"✅ Sesión de chat creada: {session_id}")
        return session_id
    except requests.exceptions.RequestException as e:
        logger.error(f"❌ Error creando sesión de chat: {e}")
        if hasattr(e, "response"):
            logger.error(f"Detalles del error: {e.response.text}")
            logger.error(f"Código de estado: {e.response.status_code}")
        logger.error(traceback.format_exc())
        return None


def send_chat_message(token, session_id, message):
    """Enviar mensaje de chat"""
    try:
        headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json",
        }
        payload = {"message": message, "sessionId": session_id}
        logger.debug(f"Enviando mensaje: {payload}")

        response = requests.post(f"{BASE_URL}/chat/send", headers=headers, json=payload)

        logger.debug(f"Respuesta de envío de mensaje: {response.status_code}")
        logger.debug(f"Contenido de respuesta: {response.text}")

        response.raise_for_status()
        chat_response = response.json()

        logger.info(f"📨 Mensaje enviado: {message}")
        logger.info(f"🤖 Respuesta: {chat_response['response']}")
        logger.info(f"⏱️ Tiempo de respuesta: {chat_response['responseTime']} segundos")
        logger.info(f"💬 Tokens usados: {chat_response['tokensUsed']}")

        return chat_response
    except Exception as e:
        logger.error(f"❌ Error enviando mensaje de chat: {e}")
        logger.error(traceback.format_exc())
        return None


def test_chat_interactions():
    """Realizar pruebas de interacción de chat"""
    # Iniciar sesión o registrar
    token = register_or_login()
    if not token:
        logger.error("No se pudo obtener token de autenticación")
        return

    # Crear sesión de chat
    session_id = create_chat_session(token)
    if not session_id:
        logger.error("No se pudo crear sesión de chat")
        return

    # Pruebas de conversación
    test_prompts = [
        "Hola, ¿cómo estás?",
        "Explícame qué es la inteligencia artificial en términos simples",
        "¿Cuáles son los beneficios de aprender programación?",
        "Dame un consejo para mejorar mi productividad",
        "Háblame sobre el futuro de la tecnología",
    ]

    for prompt in test_prompts:
        response = send_chat_message(token, session_id, prompt)
        if not response:
            break
        # Pequeña pausa entre mensajes para simular conversación
        import time

        time.sleep(1)


def main():
    """Punto de entrada principal"""
    logger.info("🚀 Iniciando pruebas de interacción de chat con Phi-3 4 bits")
    test_chat_interactions()
    logger.info("🏁 Pruebas de chat completadas")


if __name__ == "__main__":
    main()
