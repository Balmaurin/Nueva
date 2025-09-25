import numpy as np
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.preprocessing import LabelEncoder
from sentence_transformers import SentenceTransformer
import joblib
import os
import logging


class DomainClassifier:
    def __init__(self, domains=None, tfidf_params=None, lr_params=None):
        """
        Inicializa el clasificador de dominio con múltiples estrategias

        Args:
            domains (list): Lista de dominios a clasificar
            tfidf_params (dict): Parámetros para TF-IDF
            lr_params (dict): Parámetros para Logistic Regression
        """
        self.logger = logging.getLogger(__name__)

        # Dominios predefinidos (32 macro-ramas)
        self.domains = domains or [
            "Lengua y Lingüística",
            "Matemáticas",
            "Computación",
            "Ciencia de Datos",
            "Física",
            "Química",
            "Biología",
            "Medicina",
            "Neurociencia",
            "Ingeniería",
            "Electrónica",
            "Ciberseguridad",
            "Sistemas",
            "Ciencias de la Tierra",
            "Astronomía",
            "Economía",
            "Empresa",
            "Derecho",
            "Sociología",
            "Educación",
            "Historia",
            "Geografía",
            "Arte",
            "Literatura",
            "Medios",
            "Diseño",
            "Deportes",
            "Juegos",
            "Hogar",
            "Cocina",
            "Viajes",
            "Vida Diaria",
        ]

        # Configuración TF-IDF
        self.tfidf_params = tfidf_params or {
            "max_features": 5000,
            "ngram_range": (1, 2),
        }

        # Configuración Logistic Regression
        self.lr_params = lr_params or {
            "multi_class": "multinomial",
            "solver": "lbfgs",
            "max_iter": 1000,
        }

        # Componentes del clasificador
        self.label_encoder = LabelEncoder()
        self.tfidf = TfidfVectorizer(**self.tfidf_params)
        self.lr = LogisticRegression(**self.lr_params)
        # Usar el modelo principal para clasificación de dominio
        from transformers import AutoModel, AutoTokenizer

        self.tokenizer = AutoTokenizer.from_pretrained(
            "models/custom/sheily-personal-model"
        )
        self.semantic_model = AutoModel.from_pretrained(
            "models/custom/sheily-personal-model"
        )

    def train(self, texts, labels):
        """
        Entrenar clasificador híbrido

        Args:
            texts (list): Textos de entrenamiento
            labels (list): Etiquetas correspondientes
        """
        # Codificar etiquetas
        y_encoded = self.label_encoder.fit_transform(labels)

        # Vectorización TF-IDF
        X_tfidf = self.tfidf.fit_transform(texts)

        # Embeddings semánticos
        X_semantic = self.semantic_model.encode(texts)

        # Concatenar características
        X_combined = np.hstack([X_tfidf.toarray(), X_semantic])

        # Entrenar modelo
        self.lr.fit(X_combined, y_encoded)

        self.logger.info(f"Modelo entrenado con {len(texts)} ejemplos")

    def predict(self, text):
        """
        Predecir dominio para un texto

        Args:
            text (str): Texto a clasificar

        Returns:
            str: Dominio predicho
        """
        # Vectorización TF-IDF
        X_tfidf = self.tfidf.transform([text])

        # Embedding semántico
        X_semantic = self.semantic_model.encode([text])

        # Combinar características
        X_combined = np.hstack([X_tfidf.toarray(), X_semantic])

        # Predecir probabilidades
        probs = self.lr.predict_proba(X_combined)[0]

        # Obtener dominio con mayor probabilidad
        top_domain_idx = np.argmax(probs)
        top_domain = self.label_encoder.classes_[top_domain_idx]
        top_prob = probs[top_domain_idx]

        self.logger.info(f"Dominio predicho: {top_domain} (p={top_prob:.2f})")

        return top_domain, top_prob

    def save(self, path):
        """
        Guardar modelo entrenado

        Args:
            path (str): Ruta de guardado
        """
        joblib.dump(
            {"tfidf": self.tfidf, "lr": self.lr, "label_encoder": self.label_encoder},
            f"{path}/domain_classifier.joblib",
        )

        self.logger.info(f"Modelo guardado en {path}")

    def load(self, path):
        """
        Cargar modelo entrenado

        Args:
            path (str): Ruta de carga
        """
        saved_model = joblib.load(f"{path}/domain_classifier.joblib")

        self.tfidf = saved_model["tfidf"]
        self.lr = saved_model["lr"]
        self.label_encoder = saved_model["label_encoder"]

        self.logger.info(f"Modelo cargado desde {path}")


# Configuración de logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)


def main():
    # Ejemplo de uso
    classifier = DomainClassifier()

    # Datos de ejemplo para entrenamiento
    training_data = pd.DataFrame(
        {
            "text": [
                "Explica la segunda ley de la termodinámica",
                "Cómo implementar un algoritmo de ordenamiento en Python",
                "Síntomas de la hipertensión arterial",
            ],
            "domain": ["Física", "Computación y Programación", "Medicina y Salud"],
        }
    )

    # Entrenar clasificador
    classifier.train(training_data["text"], training_data["domain"])

    # Ejemplo de predicción
    text = "Calcular la entropía de un sistema termodinámico"
    domain, prob = classifier.predict(text)
    print(f"Dominio: {domain}, Probabilidad: {prob}")


if __name__ == "__main__":
    main()
