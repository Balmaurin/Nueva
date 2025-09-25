import numpy as np
import nltk
from nltk.tokenize import word_tokenize, sent_tokenize
from nltk.util import ngrams
from typing import List, Dict, Any
import re
import logging
from pathlib import Path


class DiversityEvaluator:
    def __init__(self):
        """
        Inicializar evaluador de diversidad lingüística

        Métricas:
        - Riqueza léxica
        - Complejidad sintáctica
        - Variación de estructuras
        """
        # Descargar recursos de NLTK
        try:
            nltk.download("punkt", quiet=True)
            nltk.download("stopwords", quiet=True)
        except Exception as e:
            print(f"Advertencia: No se pudieron descargar recursos NLTK: {e}")

        # Configurar logging
        self.logger = logging.getLogger(__name__)

        # Cargar stopwords en español
        try:
            from nltk.corpus import stopwords

            self.stopwords = set(stopwords.words("spanish"))
        except:
            self.stopwords = set(
                [
                    "el",
                    "la",
                    "de",
                    "que",
                    "y",
                    "a",
                    "en",
                    "un",
                    "es",
                    "se",
                    "no",
                    "te",
                    "lo",
                    "le",
                    "da",
                    "su",
                    "por",
                    "son",
                    "con",
                    "para",
                    "al",
                    "del",
                    "los",
                    "las",
                    "una",
                    "como",
                    "pero",
                    "sus",
                    "me",
                    "hasta",
                    "hay",
                    "donde",
                    "han",
                    "quien",
                    "están",
                    "estado",
                    "desde",
                    "todo",
                    "nos",
                    "durante",
                    "todos",
                    "uno",
                    "les",
                    "ni",
                    "contra",
                    "otros",
                    "ese",
                    "eso",
                    "ante",
                    "ellos",
                    "e",
                    "esto",
                    "mí",
                    "antes",
                    "algunos",
                    "qué",
                    "unos",
                    "yo",
                    "otro",
                    "otras",
                    "otra",
                    "él",
                    "tanto",
                    "esa",
                    "estos",
                    "mucho",
                    "quienes",
                    "nada",
                    "muchos",
                    "cual",
                    "poco",
                    "ella",
                    "estar",
                    "estas",
                    "algunas",
                    "algo",
                    "nosotros",
                ]
            )

    def lexical_diversity(self, text: str) -> Dict[str, float]:
        """
        Calcular diversidad léxica

        Métricas:
        - Type-Token Ratio (TTR)
        - Índice de Guiraud
        - Índice de Herdan
        """
        # Limpiar y tokenizar texto
        text_clean = re.sub(r"[^\w\s]", "", text.lower())
        tokens = word_tokenize(text_clean)

        # Filtrar tokens válidos
        valid_tokens = [
            token for token in tokens if len(token) > 1 and token not in self.stopwords
        ]

        if len(valid_tokens) == 0:
            return {"type_token_ratio": 0.0, "guiraud_index": 0.0, "herdan_index": 0.0}

        unique_tokens = set(valid_tokens)

        metrics = {
            "type_token_ratio": len(unique_tokens) / len(valid_tokens),
            "guiraud_index": len(unique_tokens) / np.sqrt(len(valid_tokens)),
            "herdan_index": np.log(len(unique_tokens)) / np.log(len(valid_tokens)),
        }

        return metrics

    def syntactic_complexity(self, text: str) -> Dict[str, Any]:
        """
        Evaluar complejidad sintáctica

        Métricas:
        - Longitud promedio de oraciones
        - Variedad de estructuras gramaticales
        - Complejidad de palabras
        """
        # Tokenizar oraciones
        sentences = sent_tokenize(text)

        if len(sentences) == 0:
            return {
                "avg_sentence_length": 0.0,
                "max_syntax_depth": 0,
                "pos_diversity": 0.0,
                "word_complexity": 0.0,
            }

        # Longitud de oraciones
        sentence_lengths = [len(word_tokenize(sent)) for sent in sentences]
        avg_sentence_length = np.mean(sentence_lengths)

        # Análisis de complejidad de palabras
        all_words = []
        for sent in sentences:
            words = word_tokenize(sent.lower())
            all_words.extend([w for w in words if len(w) > 1])

        # Calcular complejidad basada en longitud de palabras
        word_lengths = [len(word) for word in all_words]
        word_complexity = np.mean(word_lengths) if word_lengths else 0.0

        # Análisis de patrones gramaticales simples
        patterns = {
            "conectores": [
                "pero",
                "sin embargo",
                "además",
                "también",
                "porque",
                "ya que",
            ],
            "adverbios": ["muy", "bastante", "extremadamente", "completamente"],
            "adjetivos": ["importante", "necesario", "esencial", "fundamental"],
        }

        pattern_counts = {}
        for pattern_type, pattern_words in patterns.items():
            count = sum(1 for word in all_words if word in pattern_words)
            pattern_counts[pattern_type] = count

        # Calcular diversidad de patrones
        total_patterns = sum(pattern_counts.values())
        pos_diversity = total_patterns / max(len(all_words), 1)

        return {
            "avg_sentence_length": avg_sentence_length,
            "max_syntax_depth": max(sentence_lengths) if sentence_lengths else 0,
            "pos_diversity": pos_diversity,
            "word_complexity": word_complexity,
            "pattern_counts": pattern_counts,
        }

    def semantic_variation(self, text: str) -> Dict[str, float]:
        """
        Evaluar variación semántica

        Métricas:
        - Entropía de n-gramas
        - Dispersión semántica
        """
        # Limpiar y tokenizar texto
        text_clean = re.sub(r"[^\w\s]", "", text.lower())
        tokens = word_tokenize(text_clean)

        if len(tokens) < 2:
            return {
                "bigram_entropy": 0.0,
                "trigram_entropy": 0.0,
                "semantic_dispersion": 0.0,
            }

        # Entropía de bigramas
        bigrams = list(ngrams(tokens, 2))
        bigram_freq = {}
        for bg in bigrams:
            bigram_freq[bg] = bigram_freq.get(bg, 0) + 1

        total_bigrams = len(bigrams)
        probabilities = [count / total_bigrams for count in bigram_freq.values()]

        # Calcular entropía
        entropy = -np.sum(p * np.log2(p) for p in probabilities if p > 0)

        # Entropía de trigramas (si hay suficientes tokens)
        trigram_entropy = 0.0
        if len(tokens) >= 3:
            trigrams = list(ngrams(tokens, 3))
            trigram_freq = {}
            for tg in trigrams:
                trigram_freq[tg] = trigram_freq.get(tg, 0) + 1

            total_trigrams = len(trigrams)
            trigram_probs = [count / total_trigrams for count in trigram_freq.values()]
            trigram_entropy = -np.sum(p * np.log2(p) for p in trigram_probs if p > 0)

        # Dispersión semántica (basada en variedad de palabras únicas)
        semantic_dispersion = len(set(tokens)) / len(tokens)

        return {
            "bigram_entropy": entropy,
            "trigram_entropy": trigram_entropy,
            "semantic_dispersion": semantic_dispersion,
        }

    def evaluate_diversity(self, text: str) -> Dict[str, Any]:
        """
        Evaluar diversidad general del texto

        Combina múltiples métricas de diversidad
        """
        if not text or len(text.strip()) == 0:
            return {
                "diversity_score": 0.0,
                "lexical_metrics": {
                    "type_token_ratio": 0.0,
                    "guiraud_index": 0.0,
                    "herdan_index": 0.0,
                },
                "syntactic_metrics": {
                    "avg_sentence_length": 0.0,
                    "max_syntax_depth": 0,
                    "pos_diversity": 0.0,
                },
                "semantic_metrics": {"bigram_entropy": 0.0},
            }

        lexical_metrics = self.lexical_diversity(text)
        syntactic_metrics = self.syntactic_complexity(text)
        semantic_metrics = self.semantic_variation(text)

        # Calcular puntuación compuesta
        lexical_score = lexical_metrics["type_token_ratio"]
        syntactic_score = min(syntactic_metrics["pos_diversity"] * 2, 1.0)  # Normalizar
        semantic_score = min(
            semantic_metrics["bigram_entropy"] / 8.0, 1.0
        )  # Normalizar

        diversity_score = (
            lexical_score * 0.4 + syntactic_score * 0.3 + semantic_score * 0.3
        )

        # Asegurar que el score esté entre 0 y 1
        diversity_score = max(0.0, min(1.0, diversity_score))

        return {
            "diversity_score": diversity_score,
            "lexical_metrics": lexical_metrics,
            "syntactic_metrics": syntactic_metrics,
            "semantic_metrics": semantic_metrics,
        }


def main():
    # Configurar logging
    logging.basicConfig(level=logging.INFO)

    # Ejemplo de uso
    evaluator = DiversityEvaluator()

    # Textos de ejemplo con diferentes niveles de diversidad
    texts = [
        "La fotosíntesis es un proceso biológico donde las plantas transforman luz solar en energía química.",
        "En la fotosíntesis, las plantas utilizan clorofila para capturar energía solar, que luego convierten en glucosa a través de complejas reacciones metabólicas que ocurren en los cloroplastos, permitiendo la producción de oxígeno como subproducto esencial para la vida en el planeta.",
        "Las plantas, organismos fotosintéticos fundamentales, despliegan un intrincado mecanismo molecular para transformar la radiación lumínica en energía química, un proceso que no solo sustenta su propia existencia, sino que constituye la base de las cadenas tróficas y el equilibrio ecosistémico global.",
    ]

    for i, text in enumerate(texts, 1):
        print(f"\n--- Texto {i} ---")
        print(f"Texto: {text}")

        diversity_metrics = evaluator.evaluate_diversity(text)
        print(f"\nPuntuación de Diversidad: {diversity_metrics['diversity_score']:.3f}")

        print("\nMétricas Detalladas:")
        for category, metrics in diversity_metrics.items():
            if isinstance(metrics, dict):
                print(f"\n{category.replace('_', ' ').title()}:")
                for key, value in metrics.items():
                    if isinstance(value, float):
                        print(f"  {key}: {value:.3f}")
                    else:
                        print(f"  {key}: {value}")
            else:
                print(f"\n{category.replace('_', ' ').title()}: {metrics:.3f}")


if __name__ == "__main__":
    main()
