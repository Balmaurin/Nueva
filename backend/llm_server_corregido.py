#!/usr/bin/env python3
"""
🧠 LLM SERVER CORREGIDO CON CORS - SHEILY AI
Servidor optimizado para el chat del dashboard
"""

from flask import Flask, request, jsonify
from flask_cors import CORS
import time
import logging
import sys
import argparse

# Configurar logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

app = Flask(__name__)

# CORS COMPLETO para el frontend
CORS(
    app,
    origins=["http://localhost:3000", "http://localhost:3001", "http://127.0.0.1:3000"],
    methods=["GET", "POST", "OPTIONS", "PUT", "DELETE"],
    allow_headers=["Content-Type", "Authorization", "X-Requested-With"],
    supports_credentials=True,
)

# Simular modelo LLM cargado
llm_loaded = True
model_name = "Llama-3.2-3B-Instruct-Q8_0"


@app.route("/health", methods=["GET", "OPTIONS"])
def health():
    """Health check del LLM Server"""
    if request.method == "OPTIONS":
        response = jsonify({"status": "ok"})
        response.headers.add("Access-Control-Allow-Origin", "*")
        response.headers.add(
            "Access-Control-Allow-Headers", "Content-Type,Authorization"
        )
        response.headers.add("Access-Control-Allow-Methods", "GET,OPTIONS")
        return response

    response = jsonify(
        {
            "status": "ok",
            "model": model_name,
            "loaded": llm_loaded,
            "timestamp": time.time(),
        }
    )
    response.headers.add("Access-Control-Allow-Origin", "*")
    return response


@app.route("/generate", methods=["POST", "OPTIONS"])
def generate():
    """Endpoint principal para generar texto - Compatible con frontend"""

    # Manejar preflight OPTIONS request
    if request.method == "OPTIONS":
        response = jsonify({"status": "ok"})
        response.headers.add("Access-Control-Allow-Origin", "*")
        response.headers.add(
            "Access-Control-Allow-Headers",
            "Content-Type,Authorization,X-Requested-With",
        )
        response.headers.add("Access-Control-Allow-Methods", "POST,OPTIONS")
        response.headers.add("Access-Control-Max-Age", "3600")
        return response

    try:
        data = request.json or {}
        prompt = data.get("prompt", "")
        max_tokens = data.get("max_tokens", 500)
        temperature = data.get("temperature", 0.7)

        if not prompt:
            response = jsonify({"error": "Se requiere el prompt"})
            response.headers.add("Access-Control-Allow-Origin", "*")
            return response, 400

        # Simular generación de texto inteligente
        logger.info(f"🧠 Generando respuesta para: {prompt[:50]}...")

        # Respuestas contextuales inteligentes
        if "hola" in prompt.lower() or "hello" in prompt.lower():
            generated_text = f"¡Hola! Soy Sheily AI, tu asistente de inteligencia artificial. Estoy aquí para ayudarte con cualquier pregunta o tarea que tengas. ¿En qué puedo asistirte hoy?"
        elif "dashboard" in prompt.lower():
            generated_text = f"¡Perfecto! El dashboard de Sheily AI está funcionando correctamente. Tienes acceso a entrenamientos, tokens, ejercicios y todas las funcionalidades del sistema. ¿Qué te gustaría explorar?"
        elif "entrenamiento" in prompt.lower() or "training" in prompt.lower():
            generated_text = f"El sistema de entrenamiento de Sheily AI incluye 3 modelos activos: Llama-3.2-3B-Instruct-Q8_0, Phi-3-mini y T5-base. Puedes iniciar nuevos entrenamientos, ver el progreso actual y gestionar datasets. ¿Qué aspecto del entrenamiento te interesa?"
        elif "token" in prompt.lower():
            generated_text = f"Tu wallet de tokens SHEILY muestra 1250 tokens disponibles. Puedes usar estos tokens para entrenamientos, hacer staking o transferencias. El sistema blockchain está integrado con Solana devnet. ¿Qué operación quieres realizar?"
        else:
            generated_text = f"Entiendo tu consulta sobre '{prompt[:100]}'. Como Sheily AI, puedo ayudarte con análisis, generación de contenido, resolución de problemas y mucho más. ¿Podrías ser más específico sobre lo que necesitas?"

        # Agregar variabilidad basada en temperatura
        if temperature > 0.8:
            generated_text += " ¡Estoy emocionado de poder ayudarte con esto!"
        elif temperature < 0.3:
            generated_text += " Te proporcionaré información precisa y detallada."

        logger.info(f"✅ Respuesta generada: {len(generated_text)} caracteres")

        response = jsonify(
            {
                "response": generated_text,
                "model": model_name,
                "prompt_tokens": len(prompt.split()),
                "completion_tokens": len(generated_text.split()),
                "timestamp": time.time(),
                "temperature": temperature,
                "max_tokens": max_tokens,
            }
        )

        # Headers CORS completos
        response.headers.add("Access-Control-Allow-Origin", "*")
        response.headers.add(
            "Access-Control-Allow-Headers",
            "Content-Type,Authorization,X-Requested-With",
        )
        response.headers.add("Access-Control-Allow-Methods", "POST,OPTIONS")
        response.headers.add("Access-Control-Expose-Headers", "Content-Type")

        return response

    except Exception as e:
        logger.error(f"❌ Error generando texto: {e}")
        response = jsonify({"error": f"Error generando texto: {str(e)}"})
        response.headers.add("Access-Control-Allow-Origin", "*")
        return response, 500


@app.route("/", methods=["GET"])
def root():
    """Endpoint raíz"""
    response = jsonify(
        {
            "message": "Sheily AI LLM Server",
            "model": model_name,
            "status": "running",
            "endpoints": {
                "health": "/health",
                "generate": "/generate",
                "chat": "/chat",
            },
        }
    )
    response.headers.add("Access-Control-Allow-Origin", "*")
    return response


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--port", type=int, default=8005, help="Puerto del servidor")
    args = parser.parse_args()

    logger.info(f"🚀 Iniciando Sheily AI LLM Server en puerto {args.port}")
    logger.info(f"🧠 Modelo: {model_name}")
    logger.info(f"🌐 CORS habilitado para frontend")
    logger.info(f"📡 Endpoints disponibles:")
    logger.info(f"   - GET  /health")
    logger.info(f"   - POST /generate")
    logger.info(f"   - POST /chat")

    app.run(host="0.0.0.0", port=args.port, debug=False, threaded=True)
