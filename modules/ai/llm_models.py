"""
Modelos de Lenguaje - LLM Models
================================

Componentes para manejo de modelos de lenguaje locales y remotos.
"""

import logging
from typing import Dict, Any, Optional, List
from dataclasses import dataclass
import torch
from transformers import AutoTokenizer, AutoModelForCausalLM, pipeline

logger = logging.getLogger(__name__)


@dataclass
class ModelConfig:
    """Configuración de modelo de lenguaje"""

    model_name: str
    model_path: str
    max_length: int = 512
    temperature: float = 0.7
    top_p: float = 0.9
    device: str = "auto"


class LocalLLMModel:
    """Modelo de lenguaje local"""

    def __init__(self, config: ModelConfig):
        self.config = config
        self.model = None
        self.tokenizer = None
        self.device = self._get_device()
        self._load_model()

    def _get_device(self) -> str:
        """Determina el dispositivo a usar"""
        if self.config.device == "auto":
            return "cuda" if torch.cuda.is_available() else "cpu"
        return self.config.device

    def _load_model(self):
        """Carga el modelo y tokenizer"""
        try:
            logger.info(f"🔄 Cargando modelo local: {self.config.model_name}")

            self.tokenizer = AutoTokenizer.from_pretrained(
                self.config.model_path, trust_remote_code=True
            )

            self.model = AutoModelForCausalLM.from_pretrained(
                self.config.model_path,
                torch_dtype=torch.float16 if self.device == "cuda" else torch.float32,
                device_map=self.device,
                trust_remote_code=True,
            )

            logger.info(f"✅ Modelo {self.config.model_name} cargado exitosamente")

        except Exception as e:
            logger.error(f"❌ Error cargando modelo {self.config.model_name}: {e}")
            self.model = None
            self.tokenizer = None

    def generate_text(self, prompt: str, max_length: int = None) -> str:
        """Genera texto usando el modelo local"""
        if not self.model or not self.tokenizer:
            return "Modelo no disponible"

        try:
            inputs = self.tokenizer(prompt, return_tensors="pt").to(self.device)

            max_len = max_length or self.config.max_length

            with torch.no_grad():
                outputs = self.model.generate(
                    **inputs,
                    max_length=max_len,
                    temperature=self.config.temperature,
                    top_p=self.config.top_p,
                    do_sample=True,
                    pad_token_id=self.tokenizer.eos_token_id,
                )

            response = self.tokenizer.decode(outputs[0], skip_special_tokens=True)
            return response[len(prompt) :].strip()

        except Exception as e:
            logger.error(f"❌ Error generando texto: {e}")
            return "Error en generación de texto"


class RemoteLLMClient:
    """Cliente para modelos de lenguaje remotos"""

    def __init__(self, api_key: str, model_name: str = "gpt-3.5-turbo"):
        self.api_key = api_key
        self.model_name = model_name
        self.available = self._check_availability()

    def _check_availability(self) -> bool:
        """Verifica disponibilidad del servicio remoto"""
        try:
            # Aquí se implementaría la verificación real
            return True
        except:
            return False

    def generate_text(self, prompt: str) -> str:
        """Genera texto usando modelo remoto"""
        if not self.available:
            return "Servicio remoto no disponible"

        try:
            # Aquí se implementaría la llamada real a la API
            return f"Respuesta simulada para: {prompt[:50]}..."
        except Exception as e:
            logger.error(f"❌ Error en modelo remoto: {e}")
            return "Error en servicio remoto"


class LLMModelManager:
    """Gestor de modelos de lenguaje"""

    def __init__(self):
        self.local_models: Dict[str, LocalLLMModel] = {}
        self.remote_clients: Dict[str, RemoteLLMClient] = {}
        self.active_model = None

    def add_local_model(self, name: str, config: ModelConfig) -> bool:
        """Añade un modelo local"""
        try:
            model = LocalLLMModel(config)
            if model.model:
                self.local_models[name] = model
                logger.info(f"✅ Modelo local {name} añadido")
                return True
            return False
        except Exception as e:
            logger.error(f"❌ Error añadiendo modelo local {name}: {e}")
            return False

    def add_remote_client(self, name: str, api_key: str, model_name: str) -> bool:
        """Añade un cliente remoto"""
        try:
            client = RemoteLLMClient(api_key, model_name)
            if client.available:
                self.remote_clients[name] = client
                logger.info(f"✅ Cliente remoto {name} añadido")
                return True
            return False
        except Exception as e:
            logger.error(f"❌ Error añadiendo cliente remoto {name}: {e}")
            return False

    def set_active_model(self, name: str) -> bool:
        """Establece el modelo activo"""
        if name in self.local_models or name in self.remote_clients:
            self.active_model = name
            logger.info(f"✅ Modelo activo establecido: {name}")
            return True
        return False

    def generate_text(self, prompt: str, model_name: str = None) -> str:
        """Genera texto usando el modelo especificado o activo"""
        target_model = model_name or self.active_model

        if not target_model:
            return "No hay modelo activo"

        if target_model in self.local_models:
            return self.local_models[target_model].generate_text(prompt)
        elif target_model in self.remote_clients:
            return self.remote_clients[target_model].generate_text(prompt)
        else:
            return f"Modelo {target_model} no encontrado"

    def get_available_models(self) -> List[str]:
        """Obtiene lista de modelos disponibles"""
        models = list(self.local_models.keys()) + list(self.remote_clients.keys())
        return models
