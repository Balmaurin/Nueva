"""
Cliente LLM para SHEILY AI
=========================

Cliente unificado para comunicación con el servidor local de inferencia basado en
Llama-3.2-3B-Instruct-Q8_0.
"""

import logging
import os
import time
from datetime import datetime
from typing import Any, Dict, List

import requests

# Configurar logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


class LLMClient:
    """Cliente HTTP para interactuar con el servidor local Llama 3.2."""

    def __init__(self, config: Dict[str, Any] = None):
        self.config = config or {}

        self.base_url = os.getenv("LLM_SERVER_URL", "http://127.0.0.1:8005")
        self.model_name = os.getenv(
            "LLM_MODEL_NAME", "Llama-3.2-3B-Instruct-Q8_0"
        )
        self.timeout = int(os.getenv("LLM_TIMEOUT", "60"))
        self.max_retries = int(os.getenv("LLM_MAX_RETRIES", "3"))

        self.chat_endpoint = f"{self.base_url}/v1/chat/completions"

        logger.info(
            "🔧 Cliente LLM inicializado - Modelo: %s, URL: %s",
            self.model_name,
            self.base_url,
        )

    def _make_request(
        self, endpoint: str, payload: Dict[str, Any], retries: int = None
    ) -> Dict[str, Any]:
        """Realizar petición HTTP con reintentos exponenciales."""

        if retries is None:
            retries = self.max_retries

        for attempt in range(retries + 1):
            try:
                response = requests.post(
                    endpoint,
                    json=payload,
                    timeout=self.timeout,
                    headers={"Content-Type": "application/json"},
                )
                response.raise_for_status()
                return response.json()
            except requests.exceptions.RequestException as exc:
                if attempt < retries:
                    wait_time = 2**attempt
                    logger.warning(
                        "⚠️ Intento %s falló: %s. Reintentando en %ss...",
                        attempt + 1,
                        exc,
                        wait_time,
                    )
                    time.sleep(wait_time)
                else:
                    logger.error("❌ Error después de %s intentos: %s", retries + 1, exc)
                    raise

    def llm_chat(self, messages: List[Dict[str, str]], **kwargs) -> str:
        """Enviar mensajes al servidor LLM y obtener la respuesta del asistente."""

        payload = {
            "model": self.model_name,
            "messages": messages,
            "temperature": kwargs.get("temperature", 0.7),
            "top_p": kwargs.get("top_p", 0.95),
            "max_tokens": kwargs.get("max_tokens", 2048),
            "stream": False,
        }

        response = self._make_request(self.chat_endpoint, payload)
        choices = response.get("choices", [])
        if not choices:
            raise ValueError("Respuesta del servidor LLM inválida")

        return choices[0]["message"]["content"]

    def generate_draft(self, query: str, context: str = "") -> str:
        """Generar un borrador inicial de respuesta."""

        messages = [
            {
                "role": "system",
                "content": (
                    "Eres SHEILY. Genera un borrador inicial de respuesta basado en la consulta del usuario."
                ),
            },
            {"role": "user", "content": f"Consulta: {query}\n\nContexto: {context}"},
        ]
        return self.llm_chat(messages, temperature=0.7, max_tokens=1024)

    def critique_response(self, draft: str, query: str) -> str:
        """Generar una crítica del borrador actual."""

        messages = [
            {
                "role": "system",
                "content": (
                    "Eres SHEILY. Analiza críticamente el borrador de respuesta y identifica áreas de mejora."
                ),
            },
            {
                "role": "user",
                "content": (
                    f"Consulta original: {query}\n\nBorrador: {draft}\n\nProporciona un análisis crítico constructivo."
                ),
            },
        ]
        return self.llm_chat(messages, temperature=0.3, max_tokens=512)

    def fix_response(self, draft: str, critique: str, query: str) -> str:
        """Refinar la respuesta final usando la crítica generada."""

        messages = [
            {
                "role": "system",
                "content": (
                    "Eres SHEILY. Mejora el borrador de respuesta basándote en el análisis crítico proporcionado."
                ),
            },
            {
                "role": "user",
                "content": (
                    f"Consulta: {query}\n\nBorrador original: {draft}\n\nAnálisis crítico: {critique}\n\nGenera una respuesta mejorada."
                ),
            },
        ]
        return self.llm_chat(messages, temperature=0.2, max_tokens=1536)

    def process_pipeline(self, query: str, context: str = "") -> Dict[str, Any]:
        """Ejecutar pipeline draft → critic → fix y devolver resultados detallados."""

        logger.info("🔄 Iniciando pipeline para consulta: %s", query[:100])
        start_time = time.time()

        draft = self.generate_draft(query, context)
        critique = self.critique_response(draft, query)
        final_response = self.fix_response(draft, critique, query)

        processing_time = time.time() - start_time

        return {
            "query": query,
            "context": context,
            "draft": draft,
            "critique": critique,
            "final": final_response,
            "processing_time": processing_time,
            "timestamp": datetime.utcnow().isoformat(),
        }

    def health_check(self) -> Dict[str, Any]:
        """Consultar el estado de salud del servidor LLM."""

        try:
            response = requests.get(f"{self.base_url}/health", timeout=5)
            response.raise_for_status()
            data = response.json()
            data.update({"model": self.model_name, "base_url": self.base_url})
            return data
        except Exception as exc:
            return {
                "status": "error",
                "model": self.model_name,
                "base_url": self.base_url,
                "detail": str(exc),
            }


# Instancia global del cliente
llm_client: LLMClient = None


def get_llm_client() -> LLMClient:
    """Obtener instancia global del cliente LLM."""

    global llm_client
    if llm_client is None:
        llm_client = LLMClient()
    return llm_client


def llm_chat(messages: List[Dict[str, str]], **kwargs) -> str:
    """Función de conveniencia para chat directo."""

    return get_llm_client().llm_chat(messages, **kwargs)


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Cliente LLM SHEILY local")
    parser.add_argument("--message", required=True, help="Mensaje de prueba")
    parser.add_argument("--temperature", type=float, default=0.7)
    parser.add_argument("--max_tokens", type=int, default=256)

    args = parser.parse_args()

    client = LLMClient()
    health = client.health_check()
    print(f"Estado del servidor: {health}")

    messages = [{"role": "user", "content": args.message}]
    reply = client.llm_chat(
        messages,
        temperature=args.temperature,
        max_tokens=args.max_tokens,
    )
    print(f"Respuesta: {reply}")
