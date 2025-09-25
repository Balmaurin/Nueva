"""
Modelo Simple de Sheily AI
==========================

Versión simplificada que usa el modelo principal Sheily Personal Model con cuantización 4-bit
"""

import torch
import logging
from transformers import AutoTokenizer, AutoModelForCausalLM


class SimpleSheilyModel:
    """
    Modelo simple de Sheily AI usando el modelo principal personalizado

    Características:
    - Modelo: Sheily Personal Model (4-bit)
    - Optimizado para velocidad y eficiencia
    - Configuración simplificada
    """

    def __init__(
        self,
        model_id="models/custom/sheily-personal-model",
        device="auto",
        quantization="4bit",
    ):
        """
        Inicializar modelo simple de Sheily

        Args:
            model_id (str): Ruta del modelo personalizado
            device (str): Dispositivo de ejecución
            quantization (str): Tipo de cuantización (4-bit por defecto)
        """
        self.logger = logging.getLogger(__name__)
        self.name = "Sheily Personal Model (4-bit)"
        self.model_id = model_id
        self.device = device
        self.quantization = quantization

        # Configuración de cuantización básica
        if quantization == "4bit":
            self.logger.warning(
                "Cuantización 4-bit no disponible (BitsAndBytes removido). Usando FP16."
            )
            self.bnb_config = None
            self.torch_dtype = torch.float16
        else:
            self.bnb_config = None
            self.torch_dtype = torch.float16

        # Cargar modelo
        self._load_model()

    def _load_model(self):
        """Cargar modelo y tokenizador"""
        try:
            self.logger.info(f"🔄 Cargando modelo simple: {self.model_id}")

            # Cargar tokenizador
            self.tokenizer = AutoTokenizer.from_pretrained(self.model_id, use_fast=True)

            # Cargar modelo
            self.model = AutoModelForCausalLM.from_pretrained(
                self.model_id,
                quantization_config=self.bnb_config,
                device_map=self.device,
                torch_dtype=self.torch_dtype,
                trust_remote_code=True,
            )

            self.logger.info(f"✅ Modelo simple cargado ({self.quantization})")

        except Exception as e:
            self.logger.error(f"❌ Error cargando modelo simple: {e}")
            raise

    def generate_text(
        self,
        prompt: str,
        max_length: int = 2048,
        temperature: float = 0.8,
        top_p: float = 0.95,
        top_k: int = 50,
        repetition_penalty: float = 1.1,
    ) -> str:
        """
        Generar texto usando el modelo simple

        Args:
            prompt (str): Texto de entrada
            max_length (int): Longitud máxima de respuesta
            temperature (float): Temperatura de muestreo
            top_p (float): Núcleo de muestreo top-p
            top_k (int): Muestreo top-k
            repetition_penalty (float): Penalización de repetición

        Returns:
            str: Texto generado
        """
        try:
            # Preparar entrada
            inputs = self.tokenizer(
                prompt, return_tensors="pt", truncation=True, max_length=2048
            ).to(self.model.device)

            # Generar texto
            with torch.no_grad():
                outputs = self.model.generate(
                    **inputs,
                    max_new_tokens=max_length,
                    do_sample=True,
                    temperature=temperature,
                    top_p=top_p,
                    top_k=top_k,
                    pad_token_id=self.tokenizer.eos_token_id,
                    repetition_penalty=repetition_penalty,
                )

            # Decodificar respuesta
            response = self.tokenizer.decode(outputs[0], skip_special_tokens=True)

            # Remover el prompt original de la respuesta
            if response.startswith(prompt):
                response = response[len(prompt) :].strip()

            return response

        except Exception as e:
            self.logger.error(f"❌ Error generando texto: {e}")
            return "Error generando respuesta"

    def get_model_info(self) -> dict:
        """Obtener información del modelo"""
        return {
            "name": self.name,
            "model_id": self.model_id,
            "quantization": self.quantization,
            "device": str(self.model.device),
            "parameters": sum(p.numel() for p in self.model.parameters()),
            "trainable_parameters": sum(
                p.numel() for p in self.model.parameters() if p.requires_grad
            ),
        }


# Configuración de logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)


# Ejemplo de uso
def main():
    """Ejemplo de uso del modelo simple de Sheily"""
    model = SimpleSheilyModel()

    # Información del modelo
    info = model.get_model_info()
    print(f"Modelo: {info['name']}")
    print(f"Cuantización: {info['quantization']}")
    print(f"Parámetros: {info['parameters']:,}")

    # Generar texto
    prompt = "Explica brevemente qué es la inteligencia artificial:"
    response = model.generate_text(prompt)
    print(f"\nPrompt: {prompt}")
    print(f"Respuesta: {response}")


if __name__ == "__main__":
    main()
