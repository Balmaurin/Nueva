"""
Componentes de Machine Learning - ML Components
==============================================

Componentes para machine learning y análisis predictivo.
"""

import logging
from typing import List, Dict, Any, Optional, Tuple
from dataclasses import dataclass
import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestClassifier, RandomForestRegressor
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, mean_squared_error, classification_report
from sklearn.preprocessing import StandardScaler, LabelEncoder
import joblib
import os

logger = logging.getLogger(__name__)


@dataclass
class ModelPerformance:
    """Métricas de rendimiento del modelo"""

    accuracy: float
    precision: float
    recall: float
    f1_score: float
    mse: float
    r2_score: float


@dataclass
class PredictionResult:
    """Resultado de predicción"""

    prediction: Any
    confidence: float
    model_name: str
    features_used: List[str]


class MLModelManager:
    """Gestor de modelos de machine learning"""

    def __init__(self, models_dir: str = "models"):
        self.models_dir = models_dir
        self.models: Dict[str, Any] = {}
        self.scalers: Dict[str, StandardScaler] = {}
        self.encoders: Dict[str, LabelEncoder] = {}
        self._ensure_models_directory()

    def _ensure_models_directory(self):
        """Asegura que existe el directorio de modelos"""
        if not os.path.exists(self.models_dir):
            os.makedirs(self.models_dir)
            logger.info(f"✅ Directorio de modelos creado: {self.models_dir}")

    def train_classification_model(
        self, model_name: str, X: np.ndarray, y: np.ndarray, test_size: float = 0.2
    ) -> ModelPerformance:
        """Entrena un modelo de clasificación"""
        try:
            logger.info(f"🔄 Entrenando modelo de clasificación: {model_name}")

            # Dividir datos
            X_train, X_test, y_train, y_test = train_test_split(
                X, y, test_size=test_size, random_state=42
            )

            # Escalar características
            scaler = StandardScaler()
            X_train_scaled = scaler.fit_transform(X_train)
            X_test_scaled = scaler.transform(X_test)

            # Entrenar modelo
            model = RandomForestClassifier(n_estimators=100, random_state=42)
            model.fit(X_train_scaled, y_train)

            # Predicciones
            y_pred = model.predict(X_test_scaled)
            y_pred_proba = model.predict_proba(X_test_scaled)

            # Calcular métricas
            accuracy = accuracy_score(y_test, y_pred)
            report = classification_report(y_test, y_pred, output_dict=True)

            performance = ModelPerformance(
                accuracy=accuracy,
                precision=report["weighted avg"]["precision"],
                recall=report["weighted avg"]["recall"],
                f1_score=report["weighted avg"]["f1-score"],
                mse=mean_squared_error(y_test, y_pred),
                r2_score=model.score(X_test_scaled, y_test),
            )

            # Guardar modelo y componentes
            self.models[model_name] = model
            self.scalers[f"{model_name}_scaler"] = scaler

            # Guardar en disco
            self._save_model(model_name, model, scaler)

            logger.info(f"✅ Modelo {model_name} entrenado exitosamente")
            logger.info(
                f"📊 Accuracy: {accuracy:.4f}, F1-Score: {performance.f1_score:.4f}"
            )

            return performance

        except Exception as e:
            logger.error(f"❌ Error entrenando modelo {model_name}: {e}")
            return ModelPerformance(0.0, 0.0, 0.0, 0.0, 0.0, 0.0)

    def train_regression_model(
        self, model_name: str, X: np.ndarray, y: np.ndarray, test_size: float = 0.2
    ) -> ModelPerformance:
        """Entrena un modelo de regresión"""
        try:
            logger.info(f"🔄 Entrenando modelo de regresión: {model_name}")

            # Dividir datos
            X_train, X_test, y_train, y_test = train_test_split(
                X, y, test_size=test_size, random_state=42
            )

            # Escalar características
            scaler = StandardScaler()
            X_train_scaled = scaler.fit_transform(X_train)
            X_test_scaled = scaler.transform(X_test)

            # Entrenar modelo
            model = RandomForestRegressor(n_estimators=100, random_state=42)
            model.fit(X_train_scaled, y_train)

            # Predicciones
            y_pred = model.predict(X_test_scaled)

            # Calcular métricas
            mse = mean_squared_error(y_test, y_pred)
            r2 = model.score(X_test_scaled, y_test)

            performance = ModelPerformance(
                accuracy=r2,  # Usar R² como accuracy para regresión
                precision=0.0,  # No aplicable para regresión
                recall=0.0,  # No aplicable para regresión
                f1_score=0.0,  # No aplicable para regresión
                mse=mse,
                r2_score=r2,
            )

            # Guardar modelo y componentes
            self.models[model_name] = model
            self.scalers[f"{model_name}_scaler"] = scaler

            # Guardar en disco
            self._save_model(model_name, model, scaler)

            logger.info(f"✅ Modelo {model_name} entrenado exitosamente")
            logger.info(f"📊 R² Score: {r2:.4f}, MSE: {mse:.4f}")

            return performance

        except Exception as e:
            logger.error(f"❌ Error entrenando modelo {model_name}: {e}")
            return ModelPerformance(0.0, 0.0, 0.0, 0.0, 0.0, 0.0)

    def predict(self, model_name: str, X: np.ndarray) -> PredictionResult:
        """Realiza predicción usando un modelo"""
        try:
            if model_name not in self.models:
                # Intentar cargar modelo desde disco
                self._load_model(model_name)

            if model_name not in self.models:
                raise ValueError(f"Modelo {model_name} no encontrado")

            model = self.models[model_name]
            scaler = self.scalers.get(f"{model_name}_scaler")

            # Escalar datos si hay scaler
            if scaler:
                X_scaled = scaler.transform(X)
            else:
                X_scaled = X

            # Realizar predicción
            prediction = model.predict(X_scaled)

            # Calcular confianza (probabilidad para clasificación)
            confidence = 1.0
            if hasattr(model, "predict_proba"):
                proba = model.predict_proba(X_scaled)
                confidence = np.max(proba, axis=1).mean()

            # Obtener nombres de características si están disponibles
            features_used = []
            if hasattr(model, "feature_importances_"):
                features_used = [
                    f"feature_{i}" for i in range(len(model.feature_importances_))
                ]

            return PredictionResult(
                prediction=prediction,
                confidence=confidence,
                model_name=model_name,
                features_used=features_used,
            )

        except Exception as e:
            logger.error(f"❌ Error en predicción con modelo {model_name}: {e}")
            return PredictionResult(None, 0.0, model_name, [])

    def _save_model(self, model_name: str, model: Any, scaler: StandardScaler = None):
        """Guarda modelo en disco"""
        try:
            model_path = os.path.join(self.models_dir, f"{model_name}.joblib")
            scaler_path = os.path.join(self.models_dir, f"{model_name}_scaler.joblib")

            joblib.dump(model, model_path)
            if scaler:
                joblib.dump(scaler, scaler_path)

            logger.info(f"💾 Modelo {model_name} guardado en {model_path}")

        except Exception as e:
            logger.error(f"❌ Error guardando modelo {model_name}: {e}")

    def _load_model(self, model_name: str):
        """Carga modelo desde disco"""
        try:
            model_path = os.path.join(self.models_dir, f"{model_name}.joblib")
            scaler_path = os.path.join(self.models_dir, f"{model_name}_scaler.joblib")

            if os.path.exists(model_path):
                model = joblib.load(model_path)
                self.models[model_name] = model
                logger.info(f"📂 Modelo {model_name} cargado desde {model_path}")

            if os.path.exists(scaler_path):
                scaler = joblib.load(scaler_path)
                self.scalers[f"{model_name}_scaler"] = scaler
                logger.info(f"📂 Scaler {model_name} cargado desde {scaler_path}")

        except Exception as e:
            logger.error(f"❌ Error cargando modelo {model_name}: {e}")

    def get_model_info(self, model_name: str) -> Dict[str, Any]:
        """Obtiene información del modelo"""
        if model_name not in self.models:
            return {"error": f"Modelo {model_name} no encontrado"}

        model = self.models[model_name]
        info = {
            "model_type": type(model).__name__,
            "has_scaler": f"{model_name}_scaler" in self.scalers,
            "has_encoder": f"{model_name}_encoder" in self.encoders,
        }

        if hasattr(model, "n_estimators"):
            info["n_estimators"] = model.n_estimators

        if hasattr(model, "feature_importances_"):
            info["n_features"] = len(model.feature_importances_)
            info["top_features"] = self._get_top_features(model)

        return info

    def _get_top_features(self, model: Any, top_n: int = 5) -> List[Tuple[str, float]]:
        """Obtiene las características más importantes"""
        if not hasattr(model, "feature_importances_"):
            return []

        feature_importances = model.feature_importances_
        feature_names = [f"feature_{i}" for i in range(len(feature_importances))]

        # Ordenar por importancia
        feature_importance_pairs = list(zip(feature_names, feature_importances))
        feature_importance_pairs.sort(key=lambda x: x[1], reverse=True)

        return feature_importance_pairs[:top_n]

    def list_models(self) -> List[str]:
        """Lista todos los modelos disponibles"""
        return list(self.models.keys())

    def delete_model(self, model_name: str) -> bool:
        """Elimina un modelo"""
        try:
            if model_name in self.models:
                del self.models[model_name]

            if f"{model_name}_scaler" in self.scalers:
                del self.scalers[f"{model_name}_scaler"]

            if f"{model_name}_encoder" in self.encoders:
                del self.encoders[f"{model_name}_encoder"]

            # Eliminar archivos
            model_path = os.path.join(self.models_dir, f"{model_name}.joblib")
            scaler_path = os.path.join(self.models_dir, f"{model_name}_scaler.joblib")

            if os.path.exists(model_path):
                os.remove(model_path)

            if os.path.exists(scaler_path):
                os.remove(scaler_path)

            logger.info(f"🗑️ Modelo {model_name} eliminado")
            return True

        except Exception as e:
            logger.error(f"❌ Error eliminando modelo {model_name}: {e}")
            return False
