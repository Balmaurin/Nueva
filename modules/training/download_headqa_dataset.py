#!/usr/bin/env python3
"""
Script para descargar HEAD-QA dataset usando diferentes métodos
"""

import requests
import json
import logging
from pathlib import Path
from typing import List, Dict, Optional

logger = logging.getLogger(__name__)


def download_headqa_dataset(
    output_path: Optional[str] = None, version: str = "latest"
) -> Dict[str, List[Dict[str, str]]]:
    """
    Descargar dataset HEAD-QA de fuente oficial

    Args:
        output_path: Ruta para guardar el dataset
        version: Versión del dataset a descargar

    Returns:
        Diccionario con datos de entrenamiento, validación y prueba
    """
    try:
        # URL oficial del dataset HEAD-QA
        BASE_URL = "https://huggingface.co/datasets/headqa/resolve/main"

        # Mapeo de versiones
        version_map = {"latest": "v1.0.0", "v1.0.0": "v1.0.0"}

        selected_version = version_map.get(version, "v1.0.0")

        # URLs de descarga
        urls = {
            "train": f"{BASE_URL}/{selected_version}/train.json",
            "validation": f"{BASE_URL}/{selected_version}/validation.json",
            "test": f"{BASE_URL}/{selected_version}/test.json",
        }

        # Descargar datasets
        datasets = {}
        for split, url in urls.items():
            response = requests.get(url, timeout=30)
            response.raise_for_status()

            datasets[split] = response.json()

        # Guardar si se proporciona ruta
        if output_path:
            output_dir = Path(output_path)
            output_dir.mkdir(parents=True, exist_ok=True)

            for split, data in datasets.items():
                with open(output_dir / f"{split}.json", "w", encoding="utf-8") as f:
                    json.dump(data, f, ensure_ascii=False, indent=2)

        logger.info(f"✅ Dataset HEAD-QA {selected_version} descargado exitosamente")

        return datasets

    except requests.RequestException as e:
        logger.error(f"❌ Error descargando dataset: {e}")
        raise
    except json.JSONDecodeError as e:
        logger.error(f"❌ Error procesando JSON: {e}")
        raise
    except Exception as e:
        logger.error(f"❌ Error inesperado: {e}")
        raise


def validate_headqa_dataset(dataset: Dict[str, List[Dict[str, str]]]) -> bool:
    """
    Validar estructura y calidad del dataset HEAD-QA

    Args:
        dataset: Dataset descargado

    Returns:
        Booleano indicando si el dataset es válido
    """
    try:
        required_keys = ["question", "options", "answer"]

        for split in ["train", "validation", "test"]:
            if split not in dataset:
                logger.warning(f"Falta split: {split}")
                return False

            for item in dataset[split]:
                # Validar campos requeridos
                if not all(key in item for key in required_keys):
                    logger.warning(f"Item inválido: {item}")
                    return False

                # Validar longitud de pregunta y opciones
                if len(item["question"]) < 5 or len(item["options"]) < 2:
                    logger.warning(f"Pregunta o opciones inválidas: {item}")
                    return False

        logger.info("✅ Dataset HEAD-QA validado correctamente")
        return True

    except Exception as e:
        logger.error(f"❌ Error validando dataset: {e}")
        return False


# Ejemplo de uso
if __name__ == "__main__":
    try:
        dataset = download_headqa_dataset(
            output_path="datasets/headqa", version="latest"
        )

        if validate_headqa_dataset(dataset):
            print("Dataset descargado y validado con éxito")
    except Exception as e:
        print(f"Error en descarga o validación: {e}")
