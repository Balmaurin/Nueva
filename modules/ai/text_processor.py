"""
Procesamiento de Texto - Text Processor
=======================================

Componentes para procesamiento y análisis de texto.
"""

import logging
import re
from typing import List, Dict, Any, Optional
from dataclasses import dataclass
import json

logger = logging.getLogger(__name__)


@dataclass
class TextAnalysis:
    """Resultado del análisis de texto"""

    word_count: int
    sentence_count: int
    avg_sentence_length: float
    unique_words: int
    vocabulary_diversity: float
    sentiment_score: float
    key_phrases: List[str]
    entities: List[Dict[str, Any]]


class TextProcessor:
    """Procesador de texto principal"""

    def __init__(self, language: str = "spanish"):
        self.language = language
        self.stop_words = self._load_stop_words()
        logger.info(f"✅ Procesador de texto inicializado para {language}")

    def _load_stop_words(self) -> set:
        """Carga palabras de parada básicas"""
        if self.language == "spanish":
            return {
                "a",
                "al",
                "ante",
                "bajo",
                "con",
                "contra",
                "de",
                "del",
                "desde",
                "durante",
                "en",
                "entre",
                "hacia",
                "hasta",
                "mediante",
                "para",
                "por",
                "según",
                "sin",
                "sobre",
                "tras",
                "el",
                "la",
                "los",
                "las",
                "un",
                "una",
                "unos",
                "unas",
                "y",
                "o",
                "pero",
                "si",
                "no",
                "que",
                "cual",
                "quien",
                "cuyo",
                "donde",
                "cuando",
                "como",
                "porque",
                "pues",
                "ya",
                "también",
                "muy",
                "más",
                "menos",
                "muy",
                "tan",
                "tanto",
                "todo",
                "toda",
                "todos",
                "todas",
                "este",
                "esta",
                "estos",
                "estas",
                "ese",
                "esa",
                "esos",
                "esas",
                "aquel",
                "aquella",
                "aquellos",
                "aquellas",
                "yo",
                "tú",
                "él",
                "ella",
                "nosotros",
                "vosotros",
                "ellos",
                "ellas",
                "me",
                "te",
                "le",
                "nos",
                "os",
                "les",
                "mi",
                "tu",
                "su",
                "nuestro",
                "vuestro",
                "su",
                "mío",
                "tuyo",
                "suyo",
                "mía",
                "tuya",
                "suya",
                "míos",
                "tuyos",
                "suyos",
                "mías",
                "tuyas",
                "suyas",
            }
        else:
            return {
                "a",
                "an",
                "and",
                "are",
                "as",
                "at",
                "be",
                "by",
                "for",
                "from",
                "has",
                "he",
                "in",
                "is",
                "it",
                "its",
                "of",
                "on",
                "that",
                "the",
                "to",
                "was",
                "will",
                "with",
                "i",
                "you",
                "your",
                "me",
                "my",
                "this",
                "but",
                "they",
                "have",
                "had",
                "what",
                "said",
                "each",
                "which",
                "she",
                "do",
                "how",
                "their",
                "if",
                "up",
                "out",
                "many",
                "then",
                "them",
                "these",
                "so",
                "some",
                "her",
                "would",
                "make",
                "like",
                "into",
                "him",
                "time",
                "two",
                "more",
                "go",
                "no",
                "way",
                "could",
                "my",
                "than",
                "first",
                "been",
                "call",
                "who",
                "its",
                "now",
                "find",
                "long",
                "down",
                "day",
                "did",
                "get",
                "come",
                "made",
                "may",
                "part",
            }

    def clean_text(self, text: str) -> str:
        """Limpia el texto de caracteres especiales y normaliza"""
        if not text:
            return ""

        # Convertir a minúsculas
        text = text.lower()

        # Remover caracteres especiales pero mantener acentos
        text = re.sub(r"[^\w\sáéíóúñü]", " ", text)

        # Normalizar espacios
        text = re.sub(r"\s+", " ", text)

        return text.strip()

    def tokenize_text(self, text: str) -> List[str]:
        """Tokeniza el texto en palabras"""
        if not text:
            return []

        # División simple por espacios
        tokens = text.split()

        # Filtrar tokens vacíos
        tokens = [token for token in tokens if token.strip()]

        return tokens

    def remove_stop_words(self, tokens: List[str]) -> List[str]:
        """Remueve palabras de parada"""
        return [token for token in tokens if token.lower() not in self.stop_words]

    def extract_key_phrases(self, text: str, max_phrases: int = 5) -> List[str]:
        """Extrae frases clave del texto usando patrones simples"""
        if not text:
            return []

        try:
            # Patrones para frases clave
            patterns = [
                r"\b[A-Z][a-z]+(?:\s+[A-Z][a-z]+)*\b",  # Nombres propios
                r"\b\d+[a-zA-Z]+\b",  # Números seguidos de letras
                r"\b[a-zA-Z]+\d+\b",  # Letras seguidas de números
            ]

            phrases = []
            for pattern in patterns:
                matches = re.findall(pattern, text)
                phrases.extend(matches)

            # Filtrar frases muy cortas o muy largas
            phrases = [phrase for phrase in phrases if 2 <= len(phrase.split()) <= 4]

            # Contar frecuencia
            phrase_freq = {}
            for phrase in phrases:
                phrase_freq[phrase] = phrase_freq.get(phrase, 0) + 1

            # Ordenar por frecuencia
            sorted_phrases = sorted(
                phrase_freq.items(), key=lambda x: x[1], reverse=True
            )
            return [phrase for phrase, freq in sorted_phrases[:max_phrases]]

        except Exception as e:
            logger.error(f"❌ Error extrayendo frases clave: {e}")
            return []

    def extract_entities(self, text: str) -> List[Dict[str, Any]]:
        """Extrae entidades nombradas usando patrones simples"""
        if not text:
            return []

        try:
            entities = []

            # Patrones para diferentes tipos de entidades
            patterns = {
                "PERSON": r"\b[A-Z][a-z]+\s+[A-Z][a-z]+\b",  # Nombres de personas
                "ORG": r"\b[A-Z][a-zA-Z\s&]+(?:Inc|Corp|LLC|Ltd|S\.A\.|S\.L\.)\b",  # Organizaciones
                "GPE": r"\b[A-Z][a-z]+(?:,\s*[A-Z]{2})?\b",  # Lugares
            }

            for entity_type, pattern in patterns.items():
                matches = re.finditer(pattern, text)
                for match in matches:
                    entities.append(
                        {
                            "text": match.group(),
                            "label": entity_type,
                            "start": match.start(),
                            "end": match.end(),
                        }
                    )

            return entities

        except Exception as e:
            logger.error(f"❌ Error extrayendo entidades: {e}")
            return []

    def analyze_sentiment(self, text: str) -> float:
        """Analiza el sentimiento del texto (básico)"""
        if not text:
            return 0.0

        # Palabras positivas y negativas básicas
        positive_words = {
            "bueno",
            "excelente",
            "fantástico",
            "maravilloso",
            "perfecto",
            "genial",
            "increíble",
            "asombroso",
            "feliz",
            "contento",
            "mejor",
            "grande",
            "hermoso",
            "bonito",
            "agradable",
        }

        negative_words = {
            "malo",
            "terrible",
            "horrible",
            "pésimo",
            "deplorable",
            "triste",
            "enojado",
            "frustrado",
            "molesto",
            "irritado",
            "peor",
            "feo",
            "desagradable",
            "difícil",
            "complicado",
        }

        tokens = self.tokenize_text(text.lower())

        positive_count = sum(1 for token in tokens if token in positive_words)
        negative_count = sum(1 for token in tokens if token in negative_words)

        total_words = len(tokens)
        if total_words == 0:
            return 0.0

        # Sentimiento entre -1 y 1
        sentiment = (positive_count - negative_count) / total_words
        return max(-1.0, min(1.0, sentiment))

    def analyze_text(self, text: str) -> TextAnalysis:
        """Realiza análisis completo del texto"""
        if not text:
            return TextAnalysis(0, 0, 0.0, 0, 0.0, 0.0, [], [])

        # Limpiar texto
        clean_text = self.clean_text(text)

        # Tokenización
        tokens = self.tokenize_text(clean_text)
        sentences = re.split(
            r"[.!?]+", text
        )  # División por puntos, exclamaciones y preguntas

        # Estadísticas básicas
        word_count = len(tokens)
        sentence_count = len([s for s in sentences if s.strip()])
        avg_sentence_length = word_count / sentence_count if sentence_count > 0 else 0

        # Vocabulario
        unique_words = len(set(tokens))
        vocabulary_diversity = unique_words / word_count if word_count > 0 else 0

        # Sentimiento
        sentiment_score = self.analyze_sentiment(text)

        # Frases clave y entidades
        key_phrases = self.extract_key_phrases(text)
        entities = self.extract_entities(text)

        return TextAnalysis(
            word_count=word_count,
            sentence_count=sentence_count,
            avg_sentence_length=avg_sentence_length,
            unique_words=unique_words,
            vocabulary_diversity=vocabulary_diversity,
            sentiment_score=sentiment_score,
            key_phrases=key_phrases,
            entities=entities,
        )

    def preprocess_for_llm(self, text: str) -> str:
        """Preprocesa texto para entrada a LLM"""
        if not text:
            return ""

        # Limpiar texto
        text = self.clean_text(text)

        # Tokenizar y remover stop words
        tokens = self.tokenize_text(text)
        tokens = self.remove_stop_words(tokens)

        # Reconstruir texto
        return " ".join(tokens)

    def get_text_stats(self, text: str) -> Dict[str, Any]:
        """Obtiene estadísticas básicas del texto"""
        if not text:
            return {}

        analysis = self.analyze_text(text)

        return {
            "word_count": analysis.word_count,
            "sentence_count": analysis.sentence_count,
            "avg_sentence_length": round(analysis.avg_sentence_length, 2),
            "unique_words": analysis.unique_words,
            "vocabulary_diversity": round(analysis.vocabulary_diversity, 3),
            "sentiment_score": round(analysis.sentiment_score, 3),
            "key_phrases": analysis.key_phrases,
            "entities_count": len(analysis.entities),
        }
