#!/usr/bin/env python3
import spacy
import numpy as np
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity


class ContextualAccuracyEvaluator:
    def __init__(
        self,
        nlp_model="models/custom/shaili-personal-model",
        embedding_model="models/custom/shaili-personal-model",
    ):
        """
        Inicializar evaluador de precisión contextual

        Args:
            nlp_model (str): Modelo de SpaCy para análisis lingüístico
            embedding_model (str): Modelo de embeddings para similitud semántica
        """
        # Cargar modelo principal
        try:
            from transformers import AutoModel, AutoTokenizer

            self.tokenizer = AutoTokenizer.from_pretrained(embedding_model)
            self.embedding_model = AutoModel.from_pretrained(embedding_model)
            self.embedding_model.eval()
            self.nlp = None  # No usar SpaCy
        except Exception as e:
            print(f"Error cargando modelo principal: {e}")
            self.nlp = None
            self.embedding_model = None

    def semantic_similarity(self, query: str, response: str) -> float:
        """
        Calcular similitud semántica entre consulta y respuesta

        Args:
            query (str): Consulta original
            response (str): Respuesta generada

        Returns:
            float: Puntuación de similitud semántica (0-1)
        """
        if not self.embedding_model:
            return 0.5  # Valor por defecto si no hay modelo

        # Generar embeddings usando el modelo principal
        query_inputs = self.tokenizer(
            query, return_tensors="pt", padding=True, truncation=True
        )
        response_inputs = self.tokenizer(
            response, return_tensors="pt", padding=True, truncation=True
        )

        with torch.no_grad():
            query_outputs = self.embedding_model(**query_inputs)
            response_outputs = self.embedding_model(**response_inputs)

            query_emb = query_outputs.last_hidden_state.mean(dim=1).cpu().numpy()
            response_emb = response_outputs.last_hidden_state.mean(dim=1).cpu().numpy()

        # Calcular similitud coseno
        similarity = cosine_similarity(query_emb, response_emb)[0][0]
        return similarity

    def linguistic_coverage(self, query: str, response: str) -> float:
        """
        Evaluar cobertura lingüística de la respuesta

        Args:
            query (str): Consulta original
            response (str): Respuesta generada

        Returns:
            float: Puntuación de cobertura lingüística (0-1)
        """
        if not self.nlp:
            return 0.5  # Valor por defecto si no hay modelo

        # Procesar consulta y respuesta
        doc_query = self.nlp(query.lower())
        doc_response = self.nlp(response.lower())

        # Extraer entidades y conceptos clave
        query_entities = set(ent.label_ for ent in doc_query.ents)
        response_entities = set(ent.label_ for ent in doc_response.ents)

        # Extraer sustantivos y verbos principales
        query_key_words = set(
            token.lemma_ for token in doc_query if token.pos_ in ["NOUN", "VERB"]
        )
        response_key_words = set(
            token.lemma_ for token in doc_response if token.pos_ in ["NOUN", "VERB"]
        )

        # Calcular cobertura
        entity_coverage = len(query_entities.intersection(response_entities)) / (
            len(query_entities) + 1
        )
        word_coverage = len(query_key_words.intersection(response_key_words)) / (
            len(query_key_words) + 1
        )

        return (entity_coverage + word_coverage) / 2

    def contextual_precision(self, query: str, response: str) -> float:
        """
        Calcular precisión contextual general

        Args:
            query (str): Consulta original
            response (str): Respuesta generada

        Returns:
            float: Puntuación de precisión contextual (0-1)
        """
        # Combinar diferentes métricas de precisión
        semantic_sim = self.semantic_similarity(query, response)
        linguistic_cov = self.linguistic_coverage(query, response)

        # Combinar métricas con pesos
        contextual_score = (
            0.6 * semantic_sim  # Similitud semántica más importante
            + 0.4 * linguistic_cov  # Cobertura lingüística
        )

        return round(contextual_score, 2)


def evaluate_contextual_accuracy(query: str, response: str) -> float:
    """
    Función de conveniencia para evaluar precisión contextual

    Args:
        query (str): Consulta original
        response (str): Respuesta generada

    Returns:
        float: Puntuación de precisión contextual (0-1)
    """
    evaluator = ContextualAccuracyEvaluator()
    return evaluator.contextual_precision(query, response)


# Ejemplo de uso
if __name__ == "__main__":
    # Prueba de ejemplo
    query = "¿Cuáles son los trámites para obtener una licencia de conducir?"
    response1 = "Para obtener una licencia de conducir, necesitas presentar documentos de identidad, aprobar un examen teórico y práctico, y pagar las tarifas correspondientes."
    response2 = "Las licencias de conducir se obtienen en la luna."

    evaluator = ContextualAccuracyEvaluator()

    print("Precisión Contextual - Respuesta Correcta:")
    print(evaluator.contextual_precision(query, response1))

    print("\nPrecisión Contextual - Respuesta Incorrecta:")
    print(evaluator.contextual_precision(query, response2))
