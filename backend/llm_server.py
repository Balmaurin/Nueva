from flask import Flask, request, jsonify
from flask_cors import CORS
from llama_cpp import Llama
import logging
import os
import threading
import time
from typing import Any, Dict, List, Optional, Tuple
from uuid import uuid4

# Configurar logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

app = Flask(__name__)

# Configurar CORS para permitir conexiones desde el frontend
CORS(
    app,
    origins=["http://localhost:3000", "http://localhost:3001"],
    methods=["GET", "POST", "OPTIONS"],
    allow_headers=["Content-Type", "Authorization"],
)

# Configuración del LLM
MODEL_NAME = "Llama-3.2-3B-Instruct-Q4_K_M"
DEFAULT_MODEL_PATH = os.path.abspath(
    os.getenv(
        "LLM_DEFAULT_MODEL_PATH",
        os.path.join(
            os.path.dirname(__file__),
            "..",
            "models",
            "llama",
            "Llama-3.2-3B-Instruct-Q4_K_M.gguf",
        ),
    )
)
LLM_MODEL_PATH = os.path.abspath(os.getenv("LLM_MODEL_PATH", DEFAULT_MODEL_PATH))
LLM_N_CTX = int(os.getenv("LLM_CONTEXT_SIZE", "4096"))
LLM_MAX_TOKENS = int(os.getenv("LLM_MAX_TOKENS", "2048"))
MAX_MESSAGES_IN_CONTEXT = int(os.getenv("LLM_MAX_HISTORY", "10"))

llm_instance: Optional[Llama] = None
model_load_lock = threading.Lock()
is_loading = False


def ensure_model_path_exists(path: str) -> None:
    if not os.path.exists(path):
        raise FileNotFoundError(
            f"No se encontró el modelo local en {path}. "
            "Configura la variable de entorno LLM_MODEL_PATH para apuntar al archivo GGUF."
        )


def load_llm_model() -> Optional[Llama]:
    """Cargar modelo Llama localmente (solo una vez)."""

    global llm_instance, is_loading
    if llm_instance is not None or is_loading:
        return llm_instance

    with model_load_lock:
        if llm_instance is not None:
            return llm_instance

        is_loading = True
        try:
            ensure_model_path_exists(LLM_MODEL_PATH)
            logger.info("🧠 Cargando modelo local desde %s", LLM_MODEL_PATH)
            llm_instance = Llama(
                model_path=LLM_MODEL_PATH,
                n_ctx=LLM_N_CTX,
                verbose=False,
            )
            logger.info("✅ Modelo LLM cargado correctamente: %s", MODEL_NAME)
        except Exception:
            # Asegurarse de que no se quede marcado como cargando
            llm_instance = None
            raise
        finally:
            is_loading = False

    return llm_instance


# Cargar el modelo en un hilo separado al inicio para reducir latencia
threading.Thread(target=load_llm_model, daemon=True).start()


def _truncate_messages(messages: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    if len(messages) <= MAX_MESSAGES_IN_CONTEXT:
        return messages
    return messages[-MAX_MESSAGES_IN_CONTEXT:]


def _run_completion(
    messages: List[Dict[str, str]],
    temperature: float,
    top_p: float,
    max_tokens: int,
) -> Tuple[str, Dict[str, Any], float]:
    instance = load_llm_model()
    if instance is None:
        raise RuntimeError("Modelo LLM no disponible")

    truncated = _truncate_messages(messages)
    start_time = time.perf_counter()
    result = instance.create_chat_completion(
        messages=truncated,
        max_tokens=max_tokens,
        temperature=temperature,
        top_p=top_p,
        stream=False,
    )
    duration = time.perf_counter() - start_time
    content = result["choices"][0]["message"]["content"]
    usage = result.get("usage", {})
    return content, usage, duration


@app.route("/v1/chat/completions", methods=["POST"])
def chat_completions():
    data = request.get_json(force=True, silent=True) or {}
    messages = data.get("messages")
    if not messages:
        return jsonify({"error": "Se requieren mensajes"}), 400

    temperature = float(data.get("temperature", 0.7))
    top_p = float(data.get("top_p", 0.95))
    max_tokens = int(data.get("max_tokens", LLM_MAX_TOKENS))

    try:
        content, usage, duration = _run_completion(messages, temperature, top_p, max_tokens)
    except Exception as exc:
        logger.error("❌ Error generando respuesta: %s", exc)
        return jsonify({"error": str(exc)}), 500

    response = {
        "id": f"chatcmpl-{uuid4()}",
        "object": "chat.completion",
        "created": int(time.time()),
        "model": MODEL_NAME,
        "choices": [
            {
                "index": 0,
                "message": {"role": "assistant", "content": content},
                "finish_reason": "stop",
            }
        ],
        "usage": {
            "prompt_tokens": usage.get("prompt_tokens"),
            "completion_tokens": usage.get("completion_tokens"),
            "total_tokens": usage.get("total_tokens"),
        },
        "processing_time": duration,
    }
    return jsonify(response)


@app.route("/chat", methods=["POST"])
def chat():
    data = request.get_json(force=True, silent=True) or {}
    messages = data.get("messages")
    if not messages:
        return jsonify({"error": "Se requieren mensajes"}), 400

    temperature = float(data.get("temperature", 0.7))
    top_p = float(data.get("top_p", 0.95))
    max_tokens = int(data.get("max_tokens", LLM_MAX_TOKENS))

    try:
        content, usage, duration = _run_completion(messages, temperature, top_p, max_tokens)
        return jsonify(
            {
                "response": content,
                "model": MODEL_NAME,
                "processing_method": "llama_local",
                "usage": {
                    "prompt_tokens": usage.get("prompt_tokens"),
                    "completion_tokens": usage.get("completion_tokens"),
                    "total_tokens": usage.get("total_tokens"),
                },
                "processing_time": duration,
            }
        )
    except Exception as exc:
        logger.error("❌ Error al generar respuesta del LLM: %s", exc)
        return jsonify({"error": str(exc)}), 500


@app.route("/health", methods=["GET"])
def health():
    try:
        current_instance = llm_instance or load_llm_model()
    except Exception as exc:
        logger.error("❌ Error al cargar el modelo para healthcheck: %s", exc)
        return (
            jsonify(
                {
                    "status": "error",
                    "model": MODEL_NAME,
                    "detail": str(exc),
                }
            ),
            500,
        )

    status = "healthy" if current_instance is not None else ("loading" if is_loading else "unavailable")
    return jsonify(
        {
            "status": status,
            "model": MODEL_NAME,
            "context_size": LLM_N_CTX,
            "max_tokens": LLM_MAX_TOKENS,
            "model_path": LLM_MODEL_PATH,
        }
    )


@app.route("/v1/models", methods=["GET"])
def list_models():
    return jsonify({
        "object": "list",
        "data": [
            {
                "id": MODEL_NAME,
                "object": "model",
                "owned_by": "sheily-local",
            }
        ],
    })


if __name__ == "__main__":
    load_llm_model()
    logger.info("🚀 Iniciando servidor LLM en http://127.0.0.1:8005")
    app.run(host="127.0.0.1", port=8005, debug=False)
