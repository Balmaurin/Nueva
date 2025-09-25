#!/usr/bin/env python3
import os
import re
import json
import logging
import hashlib
from typing import List, Dict, Any, Optional
import numpy as np
import pandas as pd
import spacy
import fasttext
from sklearn.model_selection import train_test_split
from datasets import Dataset, DatasetDict
import requests
from urllib.parse import urlparse
from bs4 import BeautifulSoup
import chardet


class DataCurationPipeline:
    def __init__(
        self, output_dir: str = "datasets", lang_model_path: str = "lid.176.bin"
    ):
        """
        Inicializar pipeline de curación de datos

        Args:
            output_dir (str): Directorio para guardar datasets
            lang_model_path (str): Ruta al modelo de identificación de idioma
        """
        # Configuración de logging
        self.logger = logging.getLogger(__name__)
        logging.basicConfig(
            level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
        )

        # Directorios
        self.output_dir = output_dir
        os.makedirs(output_dir, exist_ok=True)

        # Cargar modelos
        self.nlp = spacy.load("es_core_news_sm")
        self.lang_detector = fasttext.load_model(lang_model_path)

        # Configuraciones
        self.config = {
            "languages": ["es", "en"],
            "min_text_length": 100,
            "max_text_length": 10000,
            "deduplication_threshold": 0.85,
            "pii_risk_threshold": 0.5,
        }

    def _detect_language(self, text: str) -> str:
        """
        Detectar idioma del texto

        Args:
            text (str): Texto a analizar

        Returns:
            Código de idioma
        """
        try:
            prediction = self.lang_detector.predict(text.replace("\n", " "), k=1)
            return prediction[0][0].replace("__label__", "")
        except Exception as e:
            self.logger.warning(f"Error en detección de idioma: {e}")
            return "unknown"

    def _clean_text(self, text: str) -> str:
        """
        Limpiar texto de elementos no deseados

        Args:
            text (str): Texto a limpiar

        Returns:
            Texto limpio
        """
        # Eliminar HTML
        text = BeautifulSoup(text, "html.parser").get_text()

        # Normalizar espacios
        text = re.sub(r"\s+", " ", text).strip()

        # Eliminar caracteres no imprimibles
        text = "".join(char for char in text if char.isprintable())

        return text

    def _detect_pii(self, text: str) -> float:
        """
        Detectar información de identificación personal (PII)

        Args:
            text (str): Texto a analizar

        Returns:
            Riesgo de PII (0-1)
        """
        doc = self.nlp(text)

        # Contar entidades sensibles
        pii_entities = [
            "PER",  # Nombres de personas
            "LOC",  # Ubicaciones
            "ORG",  # Organizaciones
        ]

        total_entities = len(doc.ents)
        sensitive_entities = sum(1 for ent in doc.ents if ent.label_ in pii_entities)

        return sensitive_entities / total_entities if total_entities > 0 else 0

    def _calculate_text_quality(self, text: str) -> Dict[str, float]:
        """
        Calcular métricas de calidad del texto

        Args:
            text (str): Texto a evaluar

        Returns:
            Diccionario de métricas de calidad
        """
        doc = self.nlp(text)

        # Métricas lingüísticas
        metrics = {
            "token_count": len(doc),
            "unique_tokens_ratio": len(set(token.text for token in doc)) / len(doc),
            "avg_word_length": np.mean([len(token.text) for token in doc]),
            "pos_diversity": len(set(token.pos_ for token in doc)) / len(doc),
        }

        return metrics

    def _hash_text(self, text: str) -> str:
        """
        Generar hash para detección de duplicados

        Args:
            text (str): Texto a hashear

        Returns:
            Hash SHA256
        """
        return hashlib.sha256(text.encode("utf-8")).hexdigest()

    def ingest_data(
        self, sources: List[Dict[str, Any]], domain: str
    ) -> List[Dict[str, str]]:
        """
        Ingestar datos de múltiples fuentes

        Args:
            sources (list): Lista de fuentes de datos
            domain (str): Dominio de los datos

        Returns:
            Lista de documentos procesados
        """
        processed_docs = []

        for source in sources:
            try:
                # Manejar diferentes tipos de fuentes
                if source["type"] == "url":
                    response = requests.get(source["url"], timeout=10)
                    text = self._clean_text(response.text)
                elif source["type"] == "file":
                    with open(source["path"], "rb") as f:
                        raw_data = f.read()
                        encoding = chardet.detect(raw_data)["encoding"]
                        text = self._clean_text(raw_data.decode(encoding))
                elif source["type"] == "text":
                    text = self._clean_text(source["content"])
                else:
                    self.logger.warning(
                        f"Tipo de fuente no soportado: {source['type']}"
                    )
                    continue

                # Filtros de calidad
                if (
                    len(text) < self.config["min_text_length"]
                    or len(text) > self.config["max_text_length"]
                ):
                    continue

                lang = self._detect_language(text)
                if lang not in self.config["languages"]:
                    continue

                pii_risk = self._detect_pii(text)
                if pii_risk > self.config["pii_risk_threshold"]:
                    continue

                # Calcular hash para detección de duplicados
                text_hash = self._hash_text(text)

                processed_docs.append(
                    {
                        "text": text,
                        "source": source.get("url", source.get("path", "unknown")),
                        "domain": domain,
                        "language": lang,
                        "hash": text_hash,
                        "quality_metrics": self._calculate_text_quality(text),
                    }
                )

            except Exception as e:
                self.logger.error(f"Error procesando fuente {source}: {e}")

        return processed_docs

    def deduplicate(self, documents: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Eliminar documentos duplicados usando MinHash

        Args:
            documents (list): Lista de documentos

        Returns:
            Lista de documentos únicos
        """
        from datasketch import MinHash, MinHashLSH

        lsh = MinHashLSH(threshold=self.config["deduplication_threshold"])
        unique_docs = []

        for doc in documents:
            minhash = MinHash(num_perm=128)
            for word in doc["text"].split():
                minhash.update(word.encode("utf-8"))

            if not lsh.query(minhash):
                lsh.insert(doc["hash"], minhash)
                unique_docs.append(doc)

        return unique_docs

    def prepare_training_dataset(
        self, documents: List[Dict[str, Any]], domain: str
    ) -> DatasetDict:
        """
        Preparar dataset de entrenamiento

        Args:
            documents (list): Lista de documentos procesados
            domain (str): Dominio de entrenamiento

        Returns:
            Dataset de Hugging Face
        """
        # Formatear documentos para entrenamiento
        formatted_data = []
        for doc in documents:
            formatted_data.append(
                {
                    "instruction": f"Analiza el siguiente texto del dominio {domain}",
                    "input": doc["text"][:1024],  # Limitar longitud de entrada
                    "output": (
                        doc["text"][1024:2048]
                        if len(doc["text"]) > 1024
                        else doc["text"]
                    ),
                    "domain": domain,
                    "source": doc["source"],
                }
            )

        # Dividir dataset
        train_data, val_data = train_test_split(
            formatted_data, test_size=0.1, random_state=42
        )

        # Convertir a Hugging Face Dataset
        dataset = DatasetDict(
            {
                "train": Dataset.from_list(train_data),
                "validation": Dataset.from_list(val_data),
            }
        )

        # Guardar dataset
        dataset_path = os.path.join(self.output_dir, domain.lower().replace(" ", "_"))
        dataset.save_to_disk(dataset_path)

        return dataset

    def process_domain(self, domain: str, sources: List[Dict[str, Any]]) -> DatasetDict:
        """
        Procesar datos para un dominio específico

        Args:
            domain (str): Dominio a procesar
            sources (list): Fuentes de datos

        Returns:
            Dataset procesado
        """
        # Ingestar datos
        raw_docs = self.ingest_data(sources, domain)

        # Eliminar duplicados
        unique_docs = self.deduplicate(raw_docs)

        # Preparar dataset de entrenamiento
        dataset = self.prepare_training_dataset(unique_docs, domain)

        return dataset


def main():
    """Ejemplo de uso del pipeline de curación de datos"""
    pipeline = DataCurationPipeline()

    # Ejemplo de fuentes para el dominio de Medicina
    medicina_sources = [
        {
            "type": "url",
            "url": "https://medlineplus.gov/spanish/ency/article/000468.htm",
            "domain": "Medicina y Salud",
        },
        {
            "type": "text",
            "content": "La hipertensión arterial es una condición médica...",
            "domain": "Medicina y Salud",
        },
    ]

    # Procesar dominio de Medicina
    medicina_dataset = pipeline.process_domain("Medicina y Salud", medicina_sources)

    print(medicina_dataset)


if __name__ == "__main__":
    main()
