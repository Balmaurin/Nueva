#!/usr/bin/env python3
import os
import re
import json
import logging
from typing import List, Dict
import requests
import pandas as pd
import numpy as np
from bs4 import BeautifulSoup
from urllib.parse import urlparse

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s: %(message)s"
)
logger = logging.getLogger(__name__)


class DataCurator:
    def __init__(self, sources_config: str = "utils/data_sources.json"):
        with open(sources_config, "r") as f:
            self.sources = json.load(f)

        self.corpus_path = "datasets/corpus_clean.txt"
        self.metadata_path = "datasets/corpus_metadata.jsonl"

    def _sanitize_text(self, text: str) -> str:
        """Limpieza profunda de texto"""
        # Remover scripts, HTML, URLs
        text = re.sub(r"<script.*?</script>", "", text, flags=re.DOTALL)
        text = BeautifulSoup(text, "html.parser").get_text()
        text = re.sub(
            r"http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+",
            "",
            text,
        )

        # Normalizar espacios
        text = re.sub(r"\s+", " ", text).strip()

        # Remover caracteres no imprimibles
        text = "".join(char for char in text if char.isprintable())

        return text

    def fetch_academic_papers(self) -> List[Dict]:
        """Obtener papers académicos de fuentes abiertas"""
        papers = []
        try:
            # Ejemplo con arXiv (API real)
            base_url = "http://export.arxiv.org/api/query"
            categories = ["cs.AI", "stat.ML", "cs.LG"]

            for category in categories:
                params = {
                    "search_query": f"cat:{category}",
                    "start": 0,
                    "max_results": 50,
                }
                response = requests.get(base_url, params=params)

                if response.status_code == 200:
                    soup = BeautifulSoup(response.text, "xml")
                    for entry in soup.find_all("entry"):
                        paper = {
                            "title": entry.title.text,
                            "summary": self._sanitize_text(entry.summary.text),
                            "category": category,
                        }
                        papers.append(paper)

        except Exception as e:
            logger.error(f"Error fetching academic papers: {e}")

        return papers

    def process_data_sources(self) -> None:
        """Procesar múltiples fuentes de datos"""
        all_texts = []
        metadata = []

        # Papers académicos
        academic_papers = self.fetch_academic_papers()
        for paper in academic_papers:
            text = f"{paper['title']}\n{paper['summary']}"
            sanitized_text = self._sanitize_text(text)

            if len(sanitized_text) > 100:  # Filtrar textos muy cortos
                all_texts.append(sanitized_text)
                metadata.append(
                    {
                        "source": "arXiv",
                        "category": paper["category"],
                        "length": len(sanitized_text),
                    }
                )

        # Guardar corpus
        with open(self.corpus_path, "w", encoding="utf-8") as f:
            f.write("\n".join(all_texts))

        # Guardar metadatos
        with open(self.metadata_path, "w", encoding="utf-8") as f:
            for meta in metadata:
                f.write(json.dumps(meta) + "\n")

        logger.info(f"Corpus generado: {len(all_texts)} documentos")
        logger.info(f"Metadatos guardados en {self.metadata_path}")


def main():
    curator = DataCurator()
    curator.process_data_sources()


if __name__ == "__main__":
    main()
