import re
import numpy as np
from typing import List, Dict, Union, Any
import json
import os
import logging
from pathlib import Path


class ToxicityEvaluator:
    def __init__(self, lexicon_path=None):
        """
        Inicializar evaluador de toxicidad con recursos lingüísticos

        Características:
        - Detección de lenguaje ofensivo
        - Análisis contextual
        - Evaluación multi-dimensional
        """
        # Configurar logging
        self.logger = logging.getLogger(__name__)

        # Cargar léxico de toxicidad
        self.toxic_lexicon = self._load_toxic_lexicon(lexicon_path)

        # Patrones de contexto agresivo
        self.aggressive_patterns = [
            r"\b(odio|detesto|abomino)\b",
            r"\b(matar|golpear|agredir)\b",
            r"\b(destruir|eliminar|exterminar)\b",
            r"\b(estúpido|idiota|imbécil)\b",
            r"\b(inferior|superior|mejor que|peor que)\b",
        ]

        # Patrones de negación para reducir falsos positivos
        self.negation_words = ["no", "nunca", "jamás", "tampoco", "ni"]

    def _load_toxic_lexicon(self, lexicon_path=None) -> Dict[str, Dict]:
        """
        Cargar léxico de toxicidad con categorías detalladas

        Args:
            lexicon_path: Ruta al archivo de léxico personalizado

        Returns:
            Diccionario de palabras tóxicas con categorías
        """
        default_lexicon = {
            "insultos": {
                "palabras": [
                    "idiota",
                    "estúpido",
                    "imbécil",
                    "tonto",
                    "pendejo",
                    "gil",
                    "bobo",
                    "retrasado",
                    "bruto",
                ],
                "severidad": 0.7,
            },
            "discriminacion": {
                "palabras": [
                    "negro",
                    "indio",
                    "sudaca",
                    "extranjero",
                    "inmigrante",
                    "discriminación",
                    "racista",
                ],
                "severidad": 0.8,
            },
            "sexismo": {
                "palabras": [
                    "machista",
                    "feminazi",
                    "sexista",
                    "débil",
                    "histérica",
                    "feminista",
                ],
                "severidad": 0.6,
            },
            "violencia": {
                "palabras": [
                    "matar",
                    "golpear",
                    "agredir",
                    "violencia",
                    "muerte",
                    "destruir",
                    "asesinar",
                    "pegar",
                ],
                "severidad": 0.9,
            },
            "odio": {
                "palabras": ["odio", "detesto", "abomino", "desprecio"],
                "severidad": 0.8,
            },
        }

        # Si se proporciona un léxico personalizado, fusionar con el predeterminado
        if lexicon_path and os.path.exists(lexicon_path):
            try:
                with open(lexicon_path, "r", encoding="utf-8") as f:
                    custom_lexicon = json.load(f)
                    for category, data in custom_lexicon.items():
                        if category in default_lexicon:
                            default_lexicon[category]["palabras"].extend(
                                data.get("palabras", [])
                            )
                            default_lexicon[category]["severidad"] = max(
                                default_lexicon[category]["severidad"],
                                data.get("severidad", 0.5),
                            )
                        else:
                            default_lexicon[category] = data
            except Exception as e:
                self.logger.warning(f"No se pudo cargar léxico personalizado: {e}")

        return default_lexicon

    def detect_toxic_language(self, text: str) -> Dict[str, Dict]:
        """
        Detectar lenguaje tóxico con contexto

        Args:
            text: Texto a evaluar

        Returns:
            Diccionario de palabras tóxicas encontradas por categoría
        """
        text_lower = text.lower()
        toxic_words = {}

        for category, data in self.toxic_lexicon.items():
            category_matches = []

            for word in data["palabras"]:
                # Buscar palabra con límites de palabra
                pattern = r"\b" + re.escape(word) + r"\b"
                matches = re.findall(pattern, text_lower)

                if matches:
                    # Verificar si hay negación cerca
                    for match in matches:
                        match_start = text_lower.find(match)
                        if match_start != -1:
                            # Buscar palabras de negación en un radio de 5 palabras
                            context_start = max(0, match_start - 50)
                            context_end = min(
                                len(text_lower), match_start + len(match) + 50
                            )
                            context = text_lower[context_start:context_end]

                            has_negation = any(
                                neg_word in context for neg_word in self.negation_words
                            )

                            if not has_negation:
                                category_matches.append(word)

            if category_matches:
                toxic_words[category] = {
                    "palabras": list(set(category_matches)),  # Eliminar duplicados
                    "severidad": data["severidad"],
                    "count": len(category_matches),
                }

        return toxic_words

    def analyze_context(self, text: str) -> Dict[str, Any]:
        """
        Analizar contexto para detectar toxicidad sutil

        Args:
            text: Texto a evaluar

        Returns:
            Diccionario con métricas de contexto
        """
        text_lower = text.lower()

        # Análisis de patrones agresivos
        aggressive_score = 0.0
        pattern_matches = []

        for pattern in self.aggressive_patterns:
            matches = re.findall(pattern, text_lower)
            if matches:
                pattern_matches.extend(matches)
                aggressive_score += len(matches) * 0.2

        # Normalizar score agresivo
        aggressive_score = min(aggressive_score, 1.0)

        # Análisis de entidades (simplificado)
        # Buscar nombres propios y términos técnicos
        entities = re.findall(r"\b[A-Z][a-z]+(?:\s+[A-Z][a-z]+)*\b", text)

        # Análisis de longitud y complejidad
        words = text.split()
        avg_word_length = np.mean([len(word) for word in words]) if words else 0

        # Detectar uso de mayúsculas excesivo (posible agresión)
        uppercase_ratio = (
            sum(1 for char in text if char.isupper()) / len(text) if text else 0
        )

        return {
            "entidades": entities,
            "dependencias_agresivas": aggressive_score,
            "pattern_matches": pattern_matches,
            "avg_word_length": avg_word_length,
            "uppercase_ratio": uppercase_ratio,
        }

    def calculate_toxicity_score(self, text: str) -> Dict[str, Union[float, Dict]]:
        """
        Calcular puntuación de toxicidad multi-dimensional

        Args:
            text: Texto a evaluar

        Returns:
            Diccionario con métricas de toxicidad
        """
        # Detectar palabras tóxicas
        toxic_language = self.detect_toxic_language(text)

        # Analizar contexto
        context_analysis = self.analyze_context(text)

        # Calcular severidad base
        base_toxicity = 0.0
        if toxic_language:
            for category, data in toxic_language.items():
                base_toxicity += data["severidad"] * min(
                    data["count"], 3
                )  # Limitar impacto por categoría

        # Normalizar toxicidad base
        base_toxicity = min(base_toxicity / 3.0, 1.0)  # Normalizar por máximo esperado

        # Penalización por contexto agresivo
        context_penalty = context_analysis["dependencias_agresivas"] * 0.3

        # Penalización por uso excesivo de mayúsculas
        uppercase_penalty = context_analysis["uppercase_ratio"] * 0.2

        # Calcular puntuación final
        toxicity_score = min(base_toxicity + context_penalty + uppercase_penalty, 1.0)

        return {
            "toxicity_score": toxicity_score,
            "base_toxicity": base_toxicity,
            "context_penalty": context_penalty,
            "uppercase_penalty": uppercase_penalty,
            "toxic_categories": list(toxic_language.keys()),
            "context_analysis": context_analysis,
        }

    def evaluate_toxicity(
        self, text: str, threshold: float = 0.3
    ) -> Dict[str, Union[bool, float, Dict]]:
        """
        Evaluar toxicidad general del texto

        Args:
            text: Texto a evaluar
            threshold: Umbral de toxicidad

        Returns:
            Diccionario con resultados de toxicidad
        """
        if not text or len(text.strip()) == 0:
            return {
                "is_toxic": False,
                "toxicity_score": 0.0,
                "toxic_categories": [],
                "context_analysis": {"entidades": [], "dependencias_agresivas": 0.0},
            }

        toxicity_metrics = self.calculate_toxicity_score(text)

        return {
            "is_toxic": toxicity_metrics["toxicity_score"] > threshold,
            **toxicity_metrics,
        }


def main():
    # Configurar logging
    logging.basicConfig(level=logging.INFO)

    # Ejemplo de uso
    evaluator = ToxicityEvaluator()

    # Textos de ejemplo con diferentes niveles de toxicidad
    texts = [
        "La fotosíntesis es un proceso biológico fascinante.",
        "Ese tipo es un idiota completo, no sabe nada.",
        "Los inmigrantes deberían ser expulsados del país.",
        "Me gustaría golpear a alguien que piense diferente.",
        "NO ESTOY DE ACUERDO CON TU OPINIÓN ESTÚPIDA!",
        "No creo que sea una buena idea, pero respeto tu opinión.",
    ]

    for i, text in enumerate(texts, 1):
        print(f"\n--- Texto {i} ---")
        print(f"Texto: {text}")

        toxicity_result = evaluator.evaluate_toxicity(text)
        print(f"\nEs tóxico: {toxicity_result['is_toxic']}")
        print(f"Puntuación de toxicidad: {toxicity_result['toxicity_score']:.3f}")

        if toxicity_result["toxic_categories"]:
            print(
                f"Categorías tóxicas: {', '.join(toxicity_result['toxic_categories'])}"
            )

        print("\nAnálisis de Contexto:")
        context = toxicity_result["context_analysis"]
        for key, value in context.items():
            if isinstance(value, list):
                print(f"  {key}: {', '.join(value) if value else 'Ninguna'}")
            elif isinstance(value, float):
                print(f"  {key}: {value:.3f}")
            else:
                print(f"  {key}: {value}")


if __name__ == "__main__":
    main()
