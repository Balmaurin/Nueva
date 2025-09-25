import numpy as np
from typing import Dict, Any, List
import re
import logging
from pathlib import Path
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity


class CoherenceEvaluator:
    def __init__(self, model_path: str = "models/custom/shaili-personal-model"):
        """
        Inicializar evaluador de coherencia

        Características:
        - Análisis semántico de coherencia
        - Evaluación de relevancia
        - Análisis de estructura lógica
        """
        # Configurar logging
        self.logger = logging.getLogger(__name__)

        # Inicializar vectorizador TF-IDF para similitud semántica
        self.vectorizer = TfidfVectorizer(
            max_features=1000,
            stop_words="english",
            ngram_range=(1, 2),
            min_df=1,
            max_df=0.95,
        )

        # Palabras de conexión lógica
        self.logical_connectors = {
            "causa": ["porque", "ya que", "dado que", "puesto que", "como", "pues"],
            "consecuencia": [
                "por tanto",
                "así que",
                "por consiguiente",
                "por eso",
                "entonces",
            ],
            "contraste": ["pero", "sin embargo", "no obstante", "aunque", "a pesar de"],
            "adición": [
                "además",
                "también",
                "asimismo",
                "igualmente",
                "del mismo modo",
            ],
            "ejemplo": [
                "por ejemplo",
                "como",
                "tal como",
                "específicamente",
                "en particular",
            ],
        }

        # Palabras clave comunes por dominio
        self.domain_keywords = {
            "ciencia": [
                "investigación",
                "estudio",
                "experimento",
                "datos",
                "análisis",
                "resultados",
            ],
            "tecnología": [
                "sistema",
                "tecnología",
                "aplicación",
                "software",
                "hardware",
                "desarrollo",
            ],
            "medicina": [
                "tratamiento",
                "diagnóstico",
                "síntomas",
                "paciente",
                "enfermedad",
                "medicamento",
            ],
            "educación": [
                "aprendizaje",
                "enseñanza",
                "estudiante",
                "profesor",
                "conocimiento",
                "habilidad",
            ],
        }

    def calculate_semantic_coherence(self, query: str, response: str) -> float:
        """
        Calcular coherencia semántica entre consulta y respuesta usando TF-IDF

        Args:
            query: Consulta original
            response: Respuesta generada

        Returns:
            Puntuación de coherencia semántica (0-1)
        """
        try:
            # Vectorizar consulta y respuesta
            documents = [query, response]
            tfidf_matrix = self.vectorizer.fit_transform(documents)

            # Calcular similitud coseno
            similarity = cosine_similarity(tfidf_matrix[0:1], tfidf_matrix[1:2])[0][0]

            return float(similarity)
        except Exception as e:
            self.logger.warning(f"Error en similitud semántica: {e}")
            # Fallback: similitud simple basada en palabras comunes
            return self._simple_similarity(query, response)

    def _simple_similarity(self, query: str, response: str) -> float:
        """
        Calcular similitud simple basada en palabras comunes

        Args:
            query: Consulta original
            response: Respuesta generada

        Returns:
            Puntuación de similitud (0-1)
        """
        # Limpiar y tokenizar
        query_words = set(re.findall(r"\b\w+\b", query.lower()))
        response_words = set(re.findall(r"\b\w+\b", response.lower()))

        if not query_words or not response_words:
            return 0.0

        # Calcular intersección
        common_words = query_words.intersection(response_words)

        # Calcular similitud Jaccard
        similarity = len(common_words) / len(query_words.union(response_words))

        return similarity

    def analyze_logical_structure(self, text: str) -> Dict[str, Any]:
        """
        Analizar estructura lógica del texto

        Args:
            text: Texto a analizar

        Returns:
            Diccionario con métricas de estructura lógica
        """
        # Tokenizar oraciones
        sentences = re.split(r"[.!?]+", text)
        sentences = [s.strip() for s in sentences if s.strip()]

        if len(sentences) == 0:
            return {
                "connector_counts": {},
                "connector_density": 0.0,
                "avg_sentence_length": 0.0,
                "total_sentences": 0,
            }

        # Contar conectores lógicos
        connector_counts = {category: 0 for category in self.logical_connectors}
        text_lower = text.lower()

        for category, connectors in self.logical_connectors.items():
            for connector in connectors:
                # Buscar conector con límites de palabra
                pattern = r"\b" + re.escape(connector) + r"\b"
                matches = re.findall(pattern, text_lower)
                connector_counts[category] += len(matches)

        # Calcular densidad de conectores
        total_connectors = sum(connector_counts.values())
        connector_density = total_connectors / len(sentences)

        # Analizar estructura de oraciones
        sentence_lengths = [len(sent.split()) for sent in sentences]
        avg_sentence_length = np.mean(sentence_lengths)

        return {
            "connector_counts": connector_counts,
            "connector_density": connector_density,
            "avg_sentence_length": avg_sentence_length,
            "total_sentences": len(sentences),
        }

    def evaluate_relevance(self, query: str, response: str) -> float:
        """
        Evaluar relevancia de la respuesta respecto a la consulta

        Args:
            query: Consulta original
            response: Respuesta generada

        Returns:
            Puntuación de relevancia (0-1)
        """
        # Extraer palabras clave de la consulta
        query_words = set(re.findall(r"\b\w+\b", query.lower()))

        # Filtrar palabras muy comunes
        common_words = {
            "qué",
            "cómo",
            "cuál",
            "dónde",
            "cuándo",
            "por",
            "para",
            "con",
            "de",
            "el",
            "la",
            "los",
            "las",
            "un",
            "una",
            "unos",
            "unas",
            "es",
            "son",
            "está",
            "están",
            "ser",
            "estar",
            "tener",
            "hacer",
            "ver",
            "saber",
            "poder",
            "deber",
            "querer",
        }
        query_keywords = query_words - common_words

        if not query_keywords:
            return 0.5  # Puntuación neutral si no hay palabras clave claras

        # Contar palabras clave en la respuesta
        response_lower = response.lower()
        keyword_matches = 0

        for keyword in query_keywords:
            if len(keyword) > 2:  # Solo palabras significativas
                pattern = r"\b" + re.escape(keyword) + r"\b"
                matches = re.findall(pattern, response_lower)
                keyword_matches += len(matches)

        # Calcular puntuación de relevancia
        relevance_score = keyword_matches / len(query_keywords)

        return min(relevance_score, 1.0)

    def analyze_consistency(self, text: str) -> Dict[str, Any]:
        """
        Analizar consistencia interna del texto

        Args:
            text: Texto a analizar

        Returns:
            Diccionario con métricas de consistencia
        """
        # Extraer entidades nombradas (simplificado)
        entities = re.findall(r"\b[A-Z][a-z]+(?:\s+[A-Z][a-z]+)*\b", text)

        # Verificar consistencia de entidades
        entity_consistency = len(set(entities)) / max(len(entities), 1)

        # Análisis de coherencia temporal
        temporal_indicators = [
            "antes",
            "después",
            "durante",
            "mientras",
            "cuando",
            "siempre",
            "nunca",
            "ahora",
            "entonces",
            "pronto",
            "tarde",
        ]
        temporal_consistency = 1.0  # Placeholder para análisis temporal más complejo

        # Análisis de coherencia de números
        numbers = re.findall(r"\b\d+(?:\.\d+)?\b", text)
        number_consistency = 1.0  # Placeholder para análisis de consistencia numérica

        return {
            "entity_consistency": entity_consistency,
            "temporal_consistency": temporal_consistency,
            "number_consistency": number_consistency,
            "entities": entities,
            "numbers": numbers,
        }

    def calculate_coherence(self, query: str, response: str) -> float:
        """
        Calcular puntuación general de coherencia

        Args:
            query: Consulta original
            response: Respuesta generada

        Returns:
            Puntuación de coherencia (0-1)
        """
        # Calcular métricas individuales
        semantic_coherence = self.calculate_semantic_coherence(query, response)
        relevance = self.evaluate_relevance(query, response)

        # Analizar estructura lógica
        logical_structure = self.analyze_logical_structure(response)
        connector_score = min(logical_structure["connector_density"] * 10, 1.0)

        # Analizar consistencia
        consistency = self.analyze_consistency(response)
        consistency_score = consistency["entity_consistency"]

        # Calcular puntuación compuesta
        coherence_score = (
            semantic_coherence * 0.4
            + relevance * 0.3
            + connector_score * 0.2
            + consistency_score * 0.1
        )

        return float(coherence_score)

    def get_detailed_coherence_analysis(
        self, query: str, response: str
    ) -> Dict[str, Any]:
        """
        Obtener análisis detallado de coherencia

        Args:
            query: Consulta original
            response: Respuesta generada

        Returns:
            Diccionario con análisis detallado
        """
        # Calcular todas las métricas
        semantic_coherence = self.calculate_semantic_coherence(query, response)
        relevance = self.evaluate_relevance(query, response)
        logical_structure = self.analyze_logical_structure(response)
        consistency = self.analyze_consistency(response)

        # Calcular puntuación general
        overall_coherence = self.calculate_coherence(query, response)

        return {
            "overall_coherence": overall_coherence,
            "semantic_coherence": semantic_coherence,
            "relevance": relevance,
            "logical_structure": logical_structure,
            "consistency": consistency,
            "query": query,
            "response": response,
        }


def main():
    # Configurar logging
    logging.basicConfig(level=logging.INFO)

    # Ejemplo de uso
    evaluator = CoherenceEvaluator()

    # Ejemplos de consultas y respuestas
    examples = [
        {
            "query": "¿Qué es la fotosíntesis?",
            "response": "La fotosíntesis es un proceso biológico donde las plantas transforman luz solar en energía química.",
        },
        {
            "query": "¿Cómo funciona la fotosíntesis?",
            "response": "En la fotosíntesis, las plantas utilizan clorofila para capturar energía solar, que luego convierten en glucosa a través de complejas reacciones metabólicas que ocurren en los cloroplastos.",
        },
        {
            "query": "¿Qué es la fotosíntesis?",
            "response": "Los gatos son animales domésticos que cazan ratones.",
        },
    ]

    for i, example in enumerate(examples, 1):
        print(f"\n--- Ejemplo {i} ---")
        print(f"Consulta: {example['query']}")
        print(f"Respuesta: {example['response']}")

        analysis = evaluator.get_detailed_coherence_analysis(
            example["query"], example["response"]
        )

        print(f"\nAnálisis de Coherencia:")
        print(f"  Coherencia General: {analysis['overall_coherence']:.3f}")
        print(f"  Coherencia Semántica: {analysis['semantic_coherence']:.3f}")
        print(f"  Relevancia: {analysis['relevance']:.3f}")
        print(
            f"  Densidad de Conectores: {analysis['logical_structure']['connector_density']:.3f}"
        )
        print(
            f"  Consistencia de Entidades: {analysis['consistency']['entity_consistency']:.3f}"
        )


if __name__ == "__main__":
    main()
