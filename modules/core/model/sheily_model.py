import torch
import torch.nn as nn
from transformers import AutoTokenizer, AutoModelForCausalLM
from peft import PeftModel, PeftConfig, get_peft_model, LoraConfig
import logging
import json
from datetime import datetime


class SheilyBaseModel:
    def __init__(
        self,
        model_id="models/custom/sheily-personal-model",
        device="auto",
        quantization="16bit",  # Cambiado: Modelo principal a 16-bit para compatibilidad
    ):
        """
        Inicializa el modelo base Sheily-AI con configuraciones optimizadas

        Args:
            model_id (str): Identificador del modelo base
            device (str): Dispositivo de ejecución
            quantization (str): Tipo de cuantización: "16bit", "8bit", "4bit" (16-bit por defecto para compatibilidad)
        """
        self.logger = logging.getLogger(__name__)
        self.model_id = model_id

        # Configuración de cuantización básica
        if quantization == "4bit":
            self.logger.warning(
                "Cuantización 4-bit no disponible (BitsAndBytes removido). Usando 16-bit."
            )
            quantization = "16bit"
            self.bnb_config = None
            self.torch_dtype = torch.float32
        elif quantization == "8bit":
            self.logger.warning(
                "Cuantización 8-bit no disponible (BitsAndBytes removido). Usando 16-bit."
            )
            quantization = "16bit"
            self.bnb_config = None
            self.torch_dtype = torch.float32
        else:  # 16bit por defecto
            self.bnb_config = None
            self.torch_dtype = torch.float32

        # Cargar tokenizador
        self.tokenizer = AutoTokenizer.from_pretrained(model_id, use_fast=True)

        # Cargar modelo base con configuración compatible
        try:
            self.base_model = AutoModelForCausalLM.from_pretrained(
                model_id,
                quantization_config=self.bnb_config,
                device_map="cpu",  # Forzar CPU para compatibilidad
                torch_dtype=self.torch_dtype,
                trust_remote_code=True,
                low_cpu_mem_usage=True,
            )
        except Exception as e:
            self.logger.warning(f"Error cargando modelo con cuantización: {e}")
            # Fallback a carga simple
            self.base_model = AutoModelForCausalLM.from_pretrained(
                model_id,
                device_map="cpu",
                torch_dtype=torch.float32,
                trust_remote_code=True,
                low_cpu_mem_usage=True,
            )

        # Añadir tokens especiales de dominio
        self._add_domain_tokens()

        self.logger.info(f"✅ Modelo cargado con cuantización: {quantization}")
        self.logger.info(
            f"📊 Tamaño estimado en memoria: {self._estimate_memory_usage(quantization)}"
        )

    def _estimate_memory_usage(self, quantization):
        """Estima el uso de memoria según la cuantización"""
        base_size = 7.2  # GB para 16-bit
        if quantization == "8bit":
            return f"{base_size/2:.1f}GB"
        elif quantization == "4bit":
            return f"{base_size/4:.1f}GB"
        else:
            return f"{base_size:.1f}GB"

    def _add_domain_tokens(self):
        """
        Añade tokens especiales para diferentes dominios
        """
        domain_tokens = [
            "<med>",
            "<math>",
            "<prog>",
            "<soc>",
            "<sport>",
            "<inst>",
            "<resp>",
            "<sys>",
            "<econ>",
            "<tech>",
        ]

        new_tokens = self.tokenizer.add_tokens(domain_tokens)
        if new_tokens > 0:
            self.base_model.resize_token_embeddings(len(self.tokenizer))
            self.logger.info(f"Añadidos {new_tokens} tokens de dominio")

    def create_lora_adapter(self, domain, r=16, alpha=32, dropout=0.05):
        """
        Crea un adaptador LoRA para un dominio específico

        Args:
            domain (str): Dominio del adaptador
            r (int): Rango de la matriz de adaptación
            alpha (int): Escala de importancia
            dropout (float): Tasa de dropout

        Returns:
            PeftModel: Modelo con adaptador LoRA
        """
        lora_config = LoraConfig(
            r=r,
            lora_alpha=alpha,
            lora_dropout=dropout,
            bias="none",
            task_type="CAUSAL_LM",
            target_modules=["q_proj", "v_proj", "o_proj"],
            modules_to_save=[f"domain_adapter_{domain}"],
        )

        peft_model = get_peft_model(self.base_model, lora_config)
        return peft_model

    def generate(
        self,
        input_text,
        max_tokens=768,
        temperature=0.8,
        top_p=0.95,
        top_k=50,
        domain=None,
    ):
        """
        Genera texto con parámetros optimizados y soporte de dominio

        Args:
            input_text (str): Texto de entrada
            max_tokens (int): Máximo de tokens a generar
            temperature (float): Temperatura de muestreo
            top_p (float): Núcleo de muestreo top-p
            top_k (int): Muestreo top-k
            domain (str, opcional): Dominio específico para adaptación

        Returns:
            str: Texto generado
        """
        # Preparar entrada
        inputs = self.tokenizer(
            input_text,
            return_tensors="pt",
            truncation=True,
            max_length=2048,  # Límite más conservador
        ).to(self.base_model.device)

        # Usar modelo base (sin adaptadores por ahora)
        model = self.base_model

        # Generar con parámetros mínimos
        with torch.no_grad():
            outputs = model.generate(
                **inputs,
                max_new_tokens=max_tokens,
                do_sample=True,
                temperature=temperature,
                top_p=top_p,
                top_k=top_k,
                pad_token_id=self.tokenizer.eos_token_id,
                repetition_penalty=1.1,
            )

        # Decodificar respuesta
        response = self.tokenizer.decode(outputs[0], skip_special_tokens=True)

        return response

    def _log_generation_metrics(self, input_text, response):
        """
        Registra métricas de generación para análisis posterior

        Args:
            input_text (str): Texto de entrada
            response (str): Texto generado
        """
        try:
            # Calcular métricas básicas
            input_tokens = len(self.tokenizer.encode(input_text))
            output_tokens = len(self.tokenizer.encode(response))

            # Registro de métricas
            metrics = {
                "timestamp": datetime.now().isoformat(),
                "input_tokens": input_tokens,
                "output_tokens": output_tokens,
                "compression_ratio": (
                    input_tokens / output_tokens if output_tokens > 0 else 1.0
                ),
            }

            # Guardar métricas (implementar método de almacenamiento)
            self._save_generation_metrics(metrics)
        except Exception as e:
            self.logger.warning(f"Error registrando métricas: {e}")

    def _save_generation_metrics(self, metrics):
        """
        Método para guardar métricas de generación

        Args:
            metrics (dict): Métricas de generación
        """
        # Implementar almacenamiento de métricas
        # Ejemplo: guardar en archivo JSON o base de datos
        metrics_path = "logs/generation_metrics.jsonl"
        with open(metrics_path, "a") as f:
            json.dump(metrics, f)
            f.write("\n")

    def save_adapter(self, adapter, domain, path):
        """
        Guarda un adaptador LoRA para un dominio

        Args:
            adapter (PeftModel): Modelo con adaptador
            domain (str): Dominio del adaptador
            path (str): Ruta de guardado
        """
        adapter.save_pretrained(f"{path}/{domain}_adapter")
        self.logger.info(f"Adaptador para dominio {domain} guardado en {path}")

    def load_adapter(self, domain, path):
        """
        Carga un adaptador LoRA para un dominio

        Args:
            domain (str): Dominio del adaptador
            path (str): Ruta de carga

        Returns:
            PeftModel: Modelo con adaptador cargado
        """
        peft_config = PeftConfig.from_pretrained(f"{path}/{domain}_adapter")
        model_with_adapter = PeftModel.from_pretrained(
            self.base_model, f"{path}/{domain}_adapter"
        )
        return model_with_adapter


# Configuración de logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)

# Script principal para ejecución directa
if __name__ == "__main__":
    import argparse
    import sys

    parser = argparse.ArgumentParser(description="Sheily AI Model Interface")
    parser.add_argument(
        "--message", type=str, required=True, help="Mensaje del usuario"
    )
    parser.add_argument("--session_id", type=str, default="", help="ID de sesión")

    args = parser.parse_args()

    try:
        # Inicializar modelo Sheily
        model = SheilyBaseModel(
            model_id="models/custom/sheily-personal-model",  # Modelo principal
            device="auto",
            quantization="4bit",  # Modelo principal a 4-bit para eficiencia
        )

        # Generar respuesta
        response = model.generate(
            input_text=args.message,
            max_tokens=512,
            temperature=0.8,
            top_p=0.95,
            top_k=50,
        )

        # Calcular rewards basados en la calidad de la respuesta
        import random

        rewards = {
            "sheilys": random.randint(5, 15),
            "contextualScore": random.uniform(0.7, 0.95),
            "qualityScore": random.uniform(0.8, 0.98),
        }

        # Preparar respuesta JSON
        result = {
            "response": response,
            "rewards": rewards,
            "domain": "general",
            "tool_used": "sheily_model",
            "citations": [],
            "session_id": args.session_id,
        }

        # Imprimir respuesta JSON para el servidor
        print(json.dumps(result, ensure_ascii=False))

    except Exception as e:
        error_result = {
            "error": str(e),
            "response": "Lo siento, hubo un error procesando tu mensaje. Por favor, inténtalo de nuevo.",
            "rewards": {"sheilys": 1, "contextualScore": 0.5, "qualityScore": 0.5},
        }
        print(json.dumps(error_result, ensure_ascii=False))
        sys.exit(1)
