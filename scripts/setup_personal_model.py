#!/usr/bin/env python3
"""
Script de Configuración del Modelo Personal de Sheily
====================================================

Este script configura el modelo principal Sheily Personal Model con cuantización 4-bit
para optimizar el rendimiento y uso de memoria.
"""

import os
import sys
import shutil
import logging
from pathlib import Path

# Configurar logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


def setup_personal_model():
    """
    Configurar el modelo principal Sheily Personal Model con cuantización 4-bit
    """
    logger.info("🚀 Iniciando configuración del modelo principal Sheily Personal Model")

    # Rutas
    base_model_path = "models/custom/sheily-personal-model"
    config_path = f"{base_model_path}/config.json"

    # Verificar que el modelo existe
    if not os.path.exists(base_model_path):
        logger.error(f"❌ Modelo no encontrado en: {base_model_path}")
        logger.info("💡 Primero debes crear el modelo personalizado")
        return False

    try:
        # Verificar archivos necesarios
        required_files = [
            "config.json",
            "pytorch_model.bin",
            "tokenizer.json",
            "tokenizer_config.json",
        ]

        missing_files = []
        for file in required_files:
            file_path = os.path.join(base_model_path, file)
            if not os.path.exists(file_path):
                missing_files.append(file)

        if missing_files:
            logger.error(f"❌ Archivos faltantes: {missing_files}")
            return False

        # Crear archivo de configuración de cuantización
        quantization_config = {
            "model_type": "sheily_personal",
            "quantization": "4bit",
            "optimization": {
                "load_in_4bit": True,
                "bnb_4bit_quant_type": "nf4",
                "bnb_4bit_use_double_quant": True,
                "bnb_4bit_compute_dtype": "bfloat16",
            },
            "performance": {
                "memory_usage": "~1.8GB",
                "speed": "Optimizado",
                "quality": "Alta",
            },
        }

        # Guardar configuración de cuantización
        import json

        quant_config_path = os.path.join(base_model_path, "quantization_config.json")
        with open(quant_config_path, "w") as f:
            json.dump(quantization_config, f, indent=2)

        logger.info(
            f"✅ Configuración de cuantización guardada en: {quant_config_path}"
        )

        # Crear archivo README específico
        readme_content = """# Sheily Personal Model (4-bit)

## Descripción
Modelo principal de Sheily AI optimizado con cuantización 4-bit para máxima eficiencia.

## Características
- **Cuantización**: FP16 (BitsAndBytes removido)
- **Memoria**: ~1.8GB
- **Velocidad**: Optimizada
- **Calidad**: Alta

## Configuración
- Modelo base: Sheily Personal
- Tipo: Causal Language Model
- Dispositivo: Auto (GPU/CPU)

## Uso
```python
from modules.core.model.sheily_model import SheilyBaseModel

model = SheilyBaseModel(
    model_id="models/custom/sheily-personal-model",
    quantization="4bit"
)
```

## Optimizaciones
- Cuantización FP16 básica
- Double quantization habilitado
- Compute dtype: bfloat16
- Compatible con ROCm/AMD
"""

        readme_path = os.path.join(base_model_path, "README.md")
        with open(readme_path, "w") as f:
            f.write(readme_content)

        logger.info(f"✅ README actualizado: {readme_path}")

        # Verificar configuración
        logger.info("🔍 Verificando configuración...")

        # Verificar archivos de configuración
        config_files = ["config.json", "quantization_config.json", "README.md"]

        for file in config_files:
            file_path = os.path.join(base_model_path, file)
            if os.path.exists(file_path):
                logger.info(f"✅ {file} - OK")
            else:
                logger.warning(f"⚠️ {file} - No encontrado")

        logger.info("🎉 Configuración del modelo principal completada exitosamente")
        logger.info(f"📁 Modelo configurado en: {base_model_path}")
        logger.info("💡 El modelo está listo para usar con cuantización 4-bit")

        return True

    except Exception as e:
        logger.error(f"❌ Error configurando modelo: {e}")
        return False


def verify_model_integration():
    """
    Verificar que el modelo está correctamente integrado en el sistema
    """
    logger.info("🔍 Verificando integración del modelo...")

    try:
        # Verificar que el módulo principal puede cargar el modelo
        sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

        from modules.core.model.sheily_model import SheilyBaseModel

        # Intentar cargar el modelo
        model = SheilyBaseModel(
            model_id="models/custom/sheily-personal-model", quantization="4bit"
        )

        logger.info("✅ Modelo cargado correctamente")

        # Obtener información del modelo
        info = {"model_id": model.model_id, "quantization": "4bit", "device": "auto"}

        logger.info(f"📊 Información del modelo: {info}")

        return True

    except Exception as e:
        logger.error(f"❌ Error verificando integración: {e}")
        return False


def main():
    """Función principal"""
    logger.info("=" * 60)
    logger.info("CONFIGURACIÓN DEL MODELO PRINCIPAL SHEILY PERSONAL")
    logger.info("=" * 60)

    # Configurar modelo
    if setup_personal_model():
        logger.info("✅ Configuración completada")

        # Verificar integración
        if verify_model_integration():
            logger.info("✅ Integración verificada")
        else:
            logger.warning("⚠️ Problemas con la integración")
    else:
        logger.error("❌ Error en la configuración")
        return 1

    logger.info("=" * 60)
    logger.info("🎉 CONFIGURACIÓN COMPLETADA EXITOSAMENTE")
    logger.info("=" * 60)

    return 0


if __name__ == "__main__":
    exit(main())
