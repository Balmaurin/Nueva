#!/usr/bin/env python3
"""
Procesador de Corpus del Sistema NeuroFusion
Maneja la limpieza, tokenización y procesamiento de textos
"""

import re
import json
import logging
import asyncio
import threading
from pathlib import Path
from typing import Dict, Any, List, Optional, Union, Tuple, Set
from dataclasses import dataclass, asdict
from datetime import datetime
import hashlib
import unicodedata
from collections import Counter, defaultdict
import nltk
from nltk.tokenize import word_tokenize, sent_tokenize
from nltk.corpus import stopwords
from nltk.stem import SnowballStemmer
import spacy
from transformers import AutoTokenizer
import numpy as np

# Configuración de logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@dataclass
class ProcessedDocument:
    """Documento procesado"""

    id: str
    original_text: str
    cleaned_text: str
    tokens: List[str]
    sentences: List[str]
    word_count: int
    sentence_count: int
    language: str
    category: str
    metadata: Dict[str, Any]
    processed_at: datetime


@dataclass
class CorpusStats:
    """Estadísticas del corpus procesado"""

    total_documents: int
    total_words: int
    total_sentences: int
    unique_words: int
    vocabulary_size: int
    language_distribution: Dict[str, int]
    category_distribution: Dict[str, int]
    average_document_length: float
    average_sentence_length: float
    processing_time: float


class CorpusProcessor:
    """Procesador principal de corpus del sistema NeuroFusion"""

    def __init__(self, data_dir: str = "data"):
        self.data_dir = Path(data_dir)
        self.nlp_models = {}
        self.tokenizers = {}
        self.stemmers = {}
        self.stop_words = {}
        self.cache = {}
        self.locks = {}

        # Inicializar modelos de procesamiento
        self._initialize_nlp_models()
        self._initialize_tokenizers()
        self._initialize_stemmers()
        self._initialize_stop_words()

    def _initialize_nlp_models(self):
        """Inicializa modelos de procesamiento de lenguaje natural"""
        try:
            # Cargar modelo spaCy para español
            self.nlp_models["es"] = spacy.load("es_core_news_sm")
            logger.info("Modelo spaCy español cargado")
        except OSError:
            logger.warning("Modelo spaCy español no encontrado. Instalando...")
            try:
                import subprocess

                subprocess.run(["python", "-m", "spacy", "download", "es_core_news_sm"])
                self.nlp_models["es"] = spacy.load("es_core_news_sm")
                logger.info("Modelo spaCy español instalado y cargado")
            except Exception as e:
                logger.error(f"Error instalando modelo spaCy: {e}")

        try:
            # Cargar modelo spaCy para inglés
            self.nlp_models["en"] = spacy.load("en_core_web_sm")
            logger.info("Modelo spaCy inglés cargado")
        except OSError:
            logger.warning("Modelo spaCy inglés no encontrado")

    def _initialize_tokenizers(self):
        """Inicializa tokenizers de transformers"""
        try:
            # Tokenizer para modelos de embeddings
            self.tokenizers["embedding"] = AutoTokenizer.from_pretrained(
                "sentence-transformers/all-MiniLM-L6-v2"
            )
            logger.info("Tokenizer de embeddings cargado")
        except Exception as e:
            logger.warning(f"Error cargando tokenizer de embeddings: {e}")

        try:
            # Tokenizer para modelos de generación
            self.tokenizers["generation"] = AutoTokenizer.from_pretrained(
                "microsoft/Phi-3-mini-4k-instruct"
            )
            logger.info("Tokenizer de generación cargado")
        except Exception as e:
            logger.warning(f"Error cargando tokenizer de generación: {e}")

    def _initialize_stemmers(self):
        """Inicializa stemmers para diferentes idiomas"""
        try:
            self.stemmers["es"] = SnowballStemmer("spanish")
            self.stemmers["en"] = SnowballStemmer("english")
            logger.info("Stemmers inicializados")
        except Exception as e:
            logger.warning(f"Error inicializando stemmers: {e}")

    def _initialize_stop_words(self):
        """Inicializa listas de palabras vacías"""
        try:
            # Descargar stop words de NLTK si no están disponibles
            nltk.download("stopwords", quiet=True)

            self.stop_words["es"] = set(stopwords.words("spanish"))
            self.stop_words["en"] = set(stopwords.words("english"))
            logger.info("Stop words inicializadas")
        except Exception as e:
            logger.warning(f"Error inicializando stop words: {e}")

    def detect_language(self, text: str) -> str:
        """Detecta el idioma del texto"""
        try:
            # Análisis simple basado en caracteres comunes
            spanish_chars = len(re.findall(r"[áéíóúñü]", text.lower()))
            english_chars = len(re.findall(r"[a-z]", text.lower()))

            if spanish_chars > english_chars * 0.1:
                return "es"
            else:
                return "en"
        except Exception as e:
            logger.warning(f"Error detectando idioma: {e}")
            return "es"  # Por defecto español

    def clean_text(self, text: str, language: str = "es") -> str:
        """Limpia el texto eliminando caracteres no deseados"""
        if not text:
            return ""

        try:
            # Normalizar unicode
            text = unicodedata.normalize("NFKC", text)

            # Eliminar caracteres de control
            text = re.sub(r"[\x00-\x08\x0b\x0c\x0e-\x1f\x7f-\x9f]", "", text)

            # Normalizar espacios
            text = re.sub(r"\s+", " ", text)

            # Eliminar URLs
            text = re.sub(
                r"http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+",
                "",
                text,
            )

            # Eliminar emails
            text = re.sub(r"\S+@\S+", "", text)

            # Eliminar números (opcional)
            # text = re.sub(r'\d+', '', text)

            # Eliminar caracteres especiales pero mantener acentos
            if language == "es":
                text = re.sub(r"[^\w\sáéíóúñüÁÉÍÓÚÑÜ.,!?;:()]", "", text)
            else:
                text = re.sub(r"[^\w\s.,!?;:()]", "", text)

            # Limpiar espacios al inicio y final
            text = text.strip()

            return text

        except Exception as e:
            logger.error(f"Error limpiando texto: {e}")
            return text

    def tokenize_text(
        self, text: str, language: str = "es", remove_stop_words: bool = False
    ) -> List[str]:
        """Tokeniza el texto en palabras"""
        if not text:
            return []

        try:
            # Usar NLTK para tokenización básica
            tokens = word_tokenize(text.lower(), language=language)

            # Filtrar tokens
            filtered_tokens = []
            for token in tokens:
                # Eliminar tokens muy cortos o muy largos
                if len(token) < 2 or len(token) > 50:
                    continue

                # Eliminar tokens que son solo números
                if token.isdigit():
                    continue

                # Eliminar stop words si se solicita
                if remove_stop_words and token in self.stop_words.get(language, set()):
                    continue

                filtered_tokens.append(token)

            return filtered_tokens

        except Exception as e:
            logger.error(f"Error tokenizando texto: {e}")
            return text.split()

    def segment_sentences(self, text: str, language: str = "es") -> List[str]:
        """Segmenta el texto en oraciones"""
        if not text:
            return []

        try:
            # Usar NLTK para segmentación de oraciones
            sentences = sent_tokenize(text, language=language)

            # Limpiar oraciones
            cleaned_sentences = []
            for sentence in sentences:
                sentence = sentence.strip()
                if len(sentence) > 10:  # Filtrar oraciones muy cortas
                    cleaned_sentences.append(sentence)

            return cleaned_sentences

        except Exception as e:
            logger.error(f"Error segmentando oraciones: {e}")
            return [text]

    def stem_tokens(self, tokens: List[str], language: str = "es") -> List[str]:
        """Aplica stemming a los tokens"""
        if not tokens:
            return []

        try:
            stemmer = self.stemmers.get(language)
            if stemmer:
                return [stemmer.stem(token) for token in tokens]
            else:
                return tokens
        except Exception as e:
            logger.error(f"Error aplicando stemming: {e}")
            return tokens

    def extract_entities(self, text: str, language: str = "es") -> List[Dict[str, Any]]:
        """Extrae entidades nombradas del texto"""
        if not text:
            return []

        try:
            nlp_model = self.nlp_models.get(language)
            if not nlp_model:
                return []

            doc = nlp_model(text)
            entities = []

            for ent in doc.ents:
                entities.append(
                    {
                        "text": ent.text,
                        "label": ent.label_,
                        "start": ent.start_char,
                        "end": ent.end_char,
                    }
                )

            return entities

        except Exception as e:
            logger.error(f"Error extrayendo entidades: {e}")
            return []

    def extract_keywords(
        self, text: str, language: str = "es", top_k: int = 10
    ) -> List[Tuple[str, int]]:
        """Extrae palabras clave del texto"""
        if not text:
            return []

        try:
            # Tokenizar y limpiar
            tokens = self.tokenize_text(text, language, remove_stop_words=True)

            # Contar frecuencias
            word_freq = Counter(tokens)

            # Filtrar palabras muy comunes o muy raras
            filtered_freq = {}
            for word, freq in word_freq.items():
                if 2 <= freq <= len(tokens) * 0.5:  # Entre 2 y 50% del texto
                    filtered_freq[word] = freq

            # Obtener top k palabras clave
            keywords = sorted(filtered_freq.items(), key=lambda x: x[1], reverse=True)[
                :top_k
            ]

            return keywords

        except Exception as e:
            logger.error(f"Error extrayendo palabras clave: {e}")
            return []

    def process_document(self, document: Dict[str, Any]) -> ProcessedDocument:
        """Procesa un documento completo"""
        try:
            # Extraer información del documento
            doc_id = document.get(
                "id", hashlib.md5(document.get("content", "").encode()).hexdigest()
            )
            original_text = document.get("content", "")
            category = document.get("category", "general")
            metadata = document.get("metadata", {})

            # Detectar idioma
            language = self.detect_language(original_text)

            # Limpiar texto
            cleaned_text = self.clean_text(original_text, language)

            # Tokenizar
            tokens = self.tokenize_text(cleaned_text, language)

            # Segmentar oraciones
            sentences = self.segment_sentences(cleaned_text, language)

            # Crear documento procesado
            processed_doc = ProcessedDocument(
                id=doc_id,
                original_text=original_text,
                cleaned_text=cleaned_text,
                tokens=tokens,
                sentences=sentences,
                word_count=len(tokens),
                sentence_count=len(sentences),
                language=language,
                category=category,
                metadata=metadata,
                processed_at=datetime.now(),
            )

            return processed_doc

        except Exception as e:
            logger.error(f"Error procesando documento: {e}")
            raise

    def process_corpus(
        self, corpus_data: Dict[str, Any], save_processed: bool = True
    ) -> Tuple[List[ProcessedDocument], CorpusStats]:
        """Procesa un corpus completo"""
        start_time = datetime.now()

        try:
            documents = corpus_data.get("documents", [])
            processed_docs = []

            logger.info(f"Procesando corpus con {len(documents)} documentos...")

            for i, document in enumerate(documents):
                try:
                    processed_doc = self.process_document(document)
                    processed_docs.append(processed_doc)

                    if (i + 1) % 100 == 0:
                        logger.info(f"Procesados {i + 1}/{len(documents)} documentos")

                except Exception as e:
                    logger.error(f"Error procesando documento {i}: {e}")
                    continue

            # Calcular estadísticas
            stats = self._calculate_corpus_stats(processed_docs, start_time)

            # Guardar corpus procesado si se solicita
            if save_processed:
                self._save_processed_corpus(processed_docs, stats)

            logger.info(
                f"Corpus procesado exitosamente: {len(processed_docs)} documentos"
            )
            return processed_docs, stats

        except Exception as e:
            logger.error(f"Error procesando corpus: {e}")
            raise

    def _calculate_corpus_stats(
        self, processed_docs: List[ProcessedDocument], start_time: datetime
    ) -> CorpusStats:
        """Calcula estadísticas del corpus procesado"""
        try:
            total_documents = len(processed_docs)
            total_words = sum(doc.word_count for doc in processed_docs)
            total_sentences = sum(doc.sentence_count for doc in processed_docs)

            # Vocabulario único
            all_tokens = []
            for doc in processed_docs:
                all_tokens.extend(doc.tokens)
            unique_words = len(set(all_tokens))

            # Distribución de idiomas
            language_dist = Counter(doc.language for doc in processed_docs)

            # Distribución de categorías
            category_dist = Counter(doc.category for doc in processed_docs)

            # Promedios
            avg_doc_length = total_words / total_documents if total_documents > 0 else 0
            avg_sentence_length = (
                total_words / total_sentences if total_sentences > 0 else 0
            )

            # Tiempo de procesamiento
            processing_time = (datetime.now() - start_time).total_seconds()

            return CorpusStats(
                total_documents=total_documents,
                total_words=total_words,
                total_sentences=total_sentences,
                unique_words=unique_words,
                vocabulary_size=unique_words,
                language_distribution=dict(language_dist),
                category_distribution=dict(category_dist),
                average_document_length=avg_doc_length,
                average_sentence_length=avg_sentence_length,
                processing_time=processing_time,
            )

        except Exception as e:
            logger.error(f"Error calculando estadísticas: {e}")
            return CorpusStats(0, 0, 0, 0, 0, {}, {}, 0.0, 0.0, 0.0)

    def _save_processed_corpus(
        self, processed_docs: List[ProcessedDocument], stats: CorpusStats
    ):
        """Guarda el corpus procesado"""
        try:
            # Convertir documentos procesados a diccionarios
            docs_data = []
            for doc in processed_docs:
                doc_dict = asdict(doc)
                doc_dict["processed_at"] = doc_dict["processed_at"].isoformat()
                docs_data.append(doc_dict)

            # Crear estructura del corpus procesado
            processed_corpus = {
                "metadata": {
                    "processed_at": datetime.now().isoformat(),
                    "processor_version": "1.0.0",
                    "stats": asdict(stats),
                },
                "documents": docs_data,
            }

            # Guardar archivo
            output_path = self.data_dir / "corpus" / "processed_corpus.json"
            with open(output_path, "w", encoding="utf-8") as f:
                json.dump(processed_corpus, f, indent=2, ensure_ascii=False)

            logger.info(f"Corpus procesado guardado: {output_path}")

        except Exception as e:
            logger.error(f"Error guardando corpus procesado: {e}")

    def create_vocabulary(
        self, processed_docs: List[ProcessedDocument], min_freq: int = 2
    ) -> Dict[str, int]:
        """Crea un vocabulario a partir de documentos procesados"""
        try:
            # Contar frecuencias de palabras
            word_freq = Counter()
            for doc in processed_docs:
                word_freq.update(doc.tokens)

            # Filtrar por frecuencia mínima
            vocabulary = {
                word: freq for word, freq in word_freq.items() if freq >= min_freq
            }

            # Ordenar por frecuencia
            sorted_vocab = dict(
                sorted(vocabulary.items(), key=lambda x: x[1], reverse=True)
            )

            logger.info(f"Vocabulario creado: {len(sorted_vocab)} palabras")
            return sorted_vocab

        except Exception as e:
            logger.error(f"Error creando vocabulario: {e}")
            return {}

    def create_ngrams(self, tokens: List[str], n: int = 2) -> List[Tuple[str, ...]]:
        """Crea n-gramas a partir de tokens"""
        if len(tokens) < n:
            return []

        try:
            ngrams = []
            for i in range(len(tokens) - n + 1):
                ngram = tuple(tokens[i : i + n])
                ngrams.append(ngram)

            return ngrams

        except Exception as e:
            logger.error(f"Error creando n-gramas: {e}")
            return []

    def calculate_tf_idf(
        self, processed_docs: List[ProcessedDocument]
    ) -> Dict[str, Dict[str, float]]:
        """Calcula TF-IDF para los documentos procesados"""
        try:
            # Calcular frecuencia de términos por documento
            doc_freqs = {}
            for doc in processed_docs:
                doc_freqs[doc.id] = Counter(doc.tokens)

            # Calcular frecuencia de documentos que contienen cada término
            term_doc_freq = Counter()
            for doc_freq in doc_freqs.values():
                for term in doc_freq:
                    term_doc_freq[term] += 1

            # Calcular TF-IDF
            tf_idf = {}
            total_docs = len(processed_docs)

            for doc_id, doc_freq in doc_freqs.items():
                tf_idf[doc_id] = {}
                doc_total_words = sum(doc_freq.values())

                for term, freq in doc_freq.items():
                    tf = freq / doc_total_words
                    idf = np.log(total_docs / term_doc_freq[term])
                    tf_idf[doc_id][term] = tf * idf

            logger.info(f"TF-IDF calculado para {len(processed_docs)} documentos")
            return tf_idf

        except Exception as e:
            logger.error(f"Error calculando TF-IDF: {e}")
            return {}

    def get_cache_key(self, text: str, operation: str) -> str:
        """Genera una clave de caché para el texto"""
        return hashlib.md5(f"{text}_{operation}".encode()).hexdigest()

    def get_cached_result(self, cache_key: str) -> Optional[Any]:
        """Obtiene un resultado del caché"""
        return self.cache.get(cache_key)

    def set_cached_result(self, cache_key: str, result: Any):
        """Establece un resultado en el caché"""
        self.cache[cache_key] = result

    def clear_cache(self):
        """Limpia el caché"""
        self.cache.clear()
        logger.info("Caché del procesador limpiado")


# Instancia global del procesador de corpus
corpus_processor = CorpusProcessor()


def get_corpus_processor() -> CorpusProcessor:
    """Obtiene la instancia global del procesador de corpus"""
    return corpus_processor


if __name__ == "__main__":
    # Ejemplo de uso
    processor = CorpusProcessor()

    # Procesar un documento de ejemplo
    sample_document = {
        "id": "test_001",
        "content": "El sistema NeuroFusion es una plataforma avanzada de inteligencia artificial que procesa textos en español.",
        "category": "tecnología",
        "metadata": {"source": "test"},
    }

    processed_doc = processor.process_document(sample_document)
    print(
        f"Documento procesado: {processed_doc.word_count} palabras, {processed_doc.sentence_count} oraciones"
    )

    # Extraer palabras clave
    keywords = processor.extract_keywords(sample_document["content"])
    print(f"Palabras clave: {keywords}")
