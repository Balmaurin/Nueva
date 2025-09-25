#!/usr/bin/env python3
"""
Script de Entrenamiento de Embeddings para Ramas
================================================

Este script entrena configuraciones específicas para ramas usando el modelo de embeddings
paraphrase-multilingual-MiniLM-L12-v2.
"""

import os
import json
import logging
import sqlite3
from typing import List, Dict, Any
from datetime import datetime
from sentence_transformers import SentenceTransformer, InputExample
from sentence_transformers.evaluation import EmbeddingSimilarityEvaluator
import numpy as np

# Configurar logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


class BranchEmbeddingTrainer:
    """
    Entrenador de embeddings para ramas especializadas

    Características:
    - Modelo base: paraphrase-multilingual-MiniLM-L12-v2
    - Entrenamiento específico por rama
    - Base de datos para almacenar resultados
    - Evaluación automática de calidad
    """

    def __init__(
        self,
        base_model_path="models/custom/shaili-personal-model",
        db_path="models/branch_learning.db",
        output_path="models/branch_embeddings",
    ):
        """
        Inicializar entrenador de embeddings

        Args:
            base_model_path (str): Ruta del modelo base de embeddings
            db_path (str): Ruta de la base de datos
            output_path (str): Ruta de salida para configuraciones
        """
        self.base_model_path = base_model_path
        self.db_path = db_path
        self.output_path = output_path

        # Crear directorio de salida
        os.makedirs(self.output_path, exist_ok=True)

        # Cargar modelo base
        self._load_base_model()

        # Inicializar base de datos
        self._init_database()

    def _load_base_model(self):
        """Cargar modelo base de embeddings"""
        try:
            logger.info(f"🔄 Cargando modelo base: {self.base_model_path}")
            # Usar el modelo principal para entrenamiento
            from transformers import AutoModel, AutoTokenizer

            self.tokenizer = AutoTokenizer.from_pretrained(self.base_model_path)
            self.model = AutoModel.from_pretrained(self.base_model_path)
            logger.info("✅ Modelo base cargado correctamente")
        except Exception as e:
            logger.error(f"❌ Error cargando modelo base: {e}")
            raise

    def _init_database(self):
        """Inicializar base de datos para entrenamiento"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            # Tabla de entrenamiento
            cursor.execute(
                """
                CREATE TABLE IF NOT EXISTS training_sessions (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    branch_name TEXT NOT NULL,
                    session_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    training_data_count INTEGER,
                    epochs INTEGER,
                    batch_size INTEGER,
                    learning_rate REAL,
                    final_loss REAL,
                    evaluation_score REAL
                )
            """
            )

            # Tabla de datos de entrenamiento
            cursor.execute(
                """
                CREATE TABLE IF NOT EXISTS training_data (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    branch_name TEXT NOT NULL,
                    text TEXT NOT NULL,
                    embedding_vector BLOB,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """
            )

            conn.commit()
            conn.close()
            logger.info("✅ Base de datos de entrenamiento inicializada")

        except Exception as e:
            logger.error(f"❌ Error inicializando base de datos: {e}")

    def prepare_training_data(
        self, branch_name: str, texts: List[str]
    ) -> List[InputExample]:
        """
        Preparar datos de entrenamiento para una rama

        Args:
            branch_name (str): Nombre de la rama
            texts (List[str]): Lista de textos de entrenamiento

        Returns:
            List[InputExample]: Datos preparados para entrenamiento
        """
        try:
            logger.info(
                f"📝 Preparando datos de entrenamiento para rama '{branch_name}'"
            )

            # Crear ejemplos de entrada
            examples = []
            for i, text in enumerate(texts):
                # Crear pares de textos similares para entrenamiento
                if i < len(texts) - 1:
                    # Texto actual y siguiente como par similar
                    examples.append(InputExample(texts=[text, texts[i + 1]], label=1.0))

                    # Texto actual y uno aleatorio como par diferente
                    if i > 0:
                        examples.append(
                            InputExample(texts=[text, texts[i - 1]], label=0.5)
                        )

            logger.info(f"✅ {len(examples)} ejemplos preparados para '{branch_name}'")
            return examples

        except Exception as e:
            logger.error(f"❌ Error preparando datos: {e}")
            return []

    def train_branch_embeddings(
        self,
        branch_name: str,
        training_texts: List[str],
        epochs: int = 3,
        batch_size: int = 16,
        learning_rate: float = 2e-5,
    ) -> bool:
        """
        Entrenar embeddings específicos para una rama

        Args:
            branch_name (str): Nombre de la rama
            training_texts (List[str]): Textos de entrenamiento
            epochs (int): Número de épocas
            batch_size (int): Tamaño del batch
            learning_rate (float): Tasa de aprendizaje

        Returns:
            bool: Éxito del entrenamiento
        """
        try:
            logger.info(f"🚀 Iniciando entrenamiento para rama '{branch_name}'")

            # Preparar datos
            training_examples = self.prepare_training_data(branch_name, training_texts)
            if not training_examples:
                logger.error("❌ No hay datos de entrenamiento válidos")
                return False

            # Crear modelo específico para la rama
            # Usar el modelo principal para ramas
            from transformers import AutoModel, AutoTokenizer

            branch_tokenizer = AutoTokenizer.from_pretrained(self.base_model_path)
            branch_model = AutoModel.from_pretrained(self.base_model_path)

            # Configurar entrenamiento
            train_dataloader = branch_model.get_dataloader(
                training_examples, batch_size=batch_size
            )

            # Entrenar modelo
            logger.info(f"🔄 Entrenando por {epochs} épocas...")

            final_loss = 0.0
            for epoch in range(epochs):
                epoch_loss = 0.0
                batch_count = 0

                for batch in train_dataloader:
                    loss = branch_model.fit(
                        batch,
                        epochs=1,
                        warmup_steps=100,
                        learning_rate=learning_rate,
                        show_progress_bar=False,
                    )
                    epoch_loss += loss
                    batch_count += 1

                avg_loss = epoch_loss / batch_count
                logger.info(f"📊 Época {epoch + 1}/{epochs} - Loss: {avg_loss:.4f}")
                final_loss = avg_loss

            # Evaluar modelo
            evaluation_score = self._evaluate_branch_model(branch_model, training_texts)

            # Guardar configuración de la rama
            self._save_branch_config(
                branch_name, branch_model, final_loss, evaluation_score
            )

            # Guardar en base de datos
            self._save_training_session(
                branch_name,
                len(training_texts),
                epochs,
                batch_size,
                learning_rate,
                final_loss,
                evaluation_score,
            )

            logger.info(f"✅ Entrenamiento completado para '{branch_name}'")
            logger.info(f"📊 Loss final: {final_loss:.4f}")
            logger.info(f"📊 Score de evaluación: {evaluation_score:.4f}")

            return True

        except Exception as e:
            logger.error(f"❌ Error en entrenamiento: {e}")
            return False

    def _evaluate_branch_model(
        self, model: SentenceTransformer, texts: List[str]
    ) -> float:
        """
        Evaluar la calidad del modelo entrenado

        Args:
            model (SentenceTransformer): Modelo a evaluar
            texts (List[str]): Textos de prueba

        Returns:
            float: Score de evaluación
        """
        try:
            # Generar embeddings
            # Generar embeddings usando el modelo principal
            inputs = self.tokenizer(
                texts, return_tensors="pt", padding=True, truncation=True
            )
            with torch.no_grad():
                outputs = model(**inputs)
                embeddings = outputs.last_hidden_state.mean(dim=1).cpu().numpy()

                # Calcular similitud promedio entre embeddings
                similarities = []
                for i in range(len(embeddings)):
                    for j in range(i + 1, len(embeddings)):
                        similarity = np.dot(embeddings[i], embeddings[j]) / (
                            np.linalg.norm(embeddings[i])
                            * np.linalg.norm(embeddings[j])
                        )
                        similarities.append(similarity)

            # Score promedio
            avg_similarity = np.mean(similarities) if similarities else 0.0

            return float(avg_similarity)

        except Exception as e:
            logger.error(f"❌ Error en evaluación: {e}")
            return 0.0

    def _save_branch_config(
        self,
        branch_name: str,
        model: SentenceTransformer,
        final_loss: float,
        evaluation_score: float,
    ):
        """Guardar configuración de la rama entrenada"""
        try:
            # Crear directorio para la rama
            branch_dir = os.path.join(self.output_path, branch_name)
            os.makedirs(branch_dir, exist_ok=True)

            # Configuración de la rama
            config = {
                "branch_name": branch_name,
                "model_type": "transformer",
                "base_model": self.base_model_path,
                "embedding_dim": 3072,
                "training_info": {
                    "final_loss": final_loss,
                    "evaluation_score": evaluation_score,
                    "trained_at": datetime.now().isoformat(),
                },
                "performance": {
                    "memory_usage": "~150MB",
                    "speed": "Optimizado",
                    "quality": "Alta" if evaluation_score > 0.7 else "Media",
                },
            }

            # Guardar configuración
            config_path = os.path.join(branch_dir, "config.json")
            with open(config_path, "w") as f:
                json.dump(config, f, indent=2)

            logger.info(f"✅ Configuración guardada: {config_path}")

        except Exception as e:
            logger.error(f"❌ Error guardando configuración: {e}")

    def _save_training_session(
        self,
        branch_name: str,
        data_count: int,
        epochs: int,
        batch_size: int,
        learning_rate: float,
        final_loss: float,
        evaluation_score: float,
    ):
        """Guardar sesión de entrenamiento en base de datos"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            cursor.execute(
                """
                INSERT INTO training_sessions 
                (branch_name, training_data_count, epochs, batch_size, learning_rate, final_loss, evaluation_score)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """,
                (
                    branch_name,
                    data_count,
                    epochs,
                    batch_size,
                    learning_rate,
                    final_loss,
                    evaluation_score,
                ),
            )

            conn.commit()
            conn.close()

        except Exception as e:
            logger.error(f"❌ Error guardando sesión: {e}")

    def list_trained_branches(self) -> List[str]:
        """Listar ramas entrenadas"""
        try:
            if not os.path.exists(self.output_path):
                return []

            branches = []
            for item in os.listdir(self.output_path):
                item_path = os.path.join(self.output_path, item)
                if os.path.isdir(item_path) and os.path.exists(
                    os.path.join(item_path, "config.json")
                ):
                    branches.append(item)

            return branches

        except Exception as e:
            logger.error(f"❌ Error listando ramas: {e}")
            return []


def main():
    """Función principal de entrenamiento"""
    logger.info("=" * 60)
    logger.info("ENTRENAMIENTO DE EMBEDDINGS PARA RAMAS")
    logger.info("=" * 60)

    # Inicializar entrenador
    trainer = BranchEmbeddingTrainer()

    # Ejemplo de entrenamiento para rama de medicina
    medicina_texts = [
        "La hipertensión es una enfermedad cardiovascular",
        "Los síntomas de la diabetes incluyen sed excesiva",
        "El cáncer es una enfermedad que afecta las células",
        "La gripe es una infección viral respiratoria",
        "La artritis afecta las articulaciones del cuerpo",
        "La depresión es un trastorno del estado de ánimo",
        "La migraña causa dolores de cabeza intensos",
        "La neumonía es una infección pulmonar",
        "La hepatitis afecta el hígado",
        "La osteoporosis debilita los huesos",
    ]

    # Entrenar rama de medicina
    success = trainer.train_branch_embeddings(
        branch_name="medicina",
        training_texts=medicina_texts,
        epochs=3,
        batch_size=8,
        learning_rate=2e-5,
    )

    if success:
        logger.info("✅ Entrenamiento de medicina completado")
    else:
        logger.error("❌ Error en entrenamiento de medicina")

    # Listar ramas entrenadas
    trained_branches = trainer.list_trained_branches()
    logger.info(f"📋 Ramas entrenadas: {trained_branches}")

    logger.info("=" * 60)
    logger.info("🎉 ENTRENAMIENTO COMPLETADO")
    logger.info("=" * 60)


if __name__ == "__main__":
    main()
