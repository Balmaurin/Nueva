"""
Evaluador de Calidad - Quality Evaluator
=======================================

Componentes para evaluación de calidad de datos y modelos.
"""

import logging
from typing import List, Dict, Any, Optional, Union
from dataclasses import dataclass
import numpy as np
import pandas as pd
from sklearn.preprocessing import StandardScaler
from sklearn.decomposition import PCA
import matplotlib.pyplot as plt
import seaborn as sns

logger = logging.getLogger(__name__)


@dataclass
class DataQualityMetrics:
    """Métricas de calidad de datos"""

    completeness: float
    consistency: float
    accuracy: float
    validity: float
    uniqueness: float
    timeliness: float
    overall_score: float


@dataclass
class ModelQualityMetrics:
    """Métricas de calidad del modelo"""

    generalization: float
    robustness: float
    interpretability: float
    efficiency: float
    fairness: float
    overall_score: float


class DataQualityEvaluator:
    """Evaluador de calidad de datos"""

    def __init__(self):
        self.quality_thresholds = {
            "completeness": 0.95,
            "consistency": 0.90,
            "accuracy": 0.85,
            "validity": 0.95,
            "uniqueness": 0.98,
            "timeliness": 0.80,
        }

    def evaluate_dataframe_quality(self, df: pd.DataFrame) -> DataQualityMetrics:
        """Evalúa la calidad de un DataFrame"""
        try:
            logger.info(
                f"🔄 Evaluando calidad de DataFrame con {len(df)} filas y {len(df.columns)} columnas"
            )

            # Completitud
            completeness = self._calculate_completeness(df)

            # Consistencia
            consistency = self._calculate_consistency(df)

            # Precisión (estimación basada en tipos de datos)
            accuracy = self._estimate_accuracy(df)

            # Validez
            validity = self._calculate_validity(df)

            # Unicidad
            uniqueness = self._calculate_uniqueness(df)

            # Oportunidad (asumiendo datos recientes)
            timeliness = self._estimate_timeliness(df)

            # Puntuación general
            overall_score = np.mean(
                [completeness, consistency, accuracy, validity, uniqueness, timeliness]
            )

            metrics = DataQualityMetrics(
                completeness=completeness,
                consistency=consistency,
                accuracy=accuracy,
                validity=validity,
                uniqueness=uniqueness,
                timeliness=timeliness,
                overall_score=overall_score,
            )

            logger.info(
                f"✅ Evaluación de calidad completada. Puntuación general: {overall_score:.3f}"
            )
            return metrics

        except Exception as e:
            logger.error(f"❌ Error evaluando calidad de datos: {e}")
            return DataQualityMetrics(0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0)

    def _calculate_completeness(self, df: pd.DataFrame) -> float:
        """Calcula la completitud de los datos"""
        try:
            total_cells = df.size
            non_null_cells = df.count().sum()
            completeness = non_null_cells / total_cells if total_cells > 0 else 0.0
            return completeness
        except Exception as e:
            logger.error(f"❌ Error calculando completitud: {e}")
            return 0.0

    def _calculate_consistency(self, df: pd.DataFrame) -> float:
        """Calcula la consistencia de los datos"""
        try:
            consistency_scores = []

            for column in df.columns:
                if df[column].dtype in ["object", "string"]:
                    # Para columnas categóricas, verificar consistencia de formato
                    unique_values = df[column].dropna().nunique()
                    total_values = len(df[column].dropna())
                    if total_values > 0:
                        consistency_scores.append(unique_values / total_values)
                else:
                    # Para columnas numéricas, verificar rango lógico
                    if df[column].dtype in ["int64", "float64"]:
                        # Verificar si hay valores extremos
                        q1 = df[column].quantile(0.25)
                        q3 = df[column].quantile(0.75)
                        iqr = q3 - q1
                        lower_bound = q1 - 1.5 * iqr
                        upper_bound = q3 + 1.5 * iqr

                        outliers = (
                            (df[column] < lower_bound) | (df[column] > upper_bound)
                        ).sum()
                        total_values = len(df[column].dropna())

                        if total_values > 0:
                            consistency_score = 1 - (outliers / total_values)
                            consistency_scores.append(consistency_score)

            return np.mean(consistency_scores) if consistency_scores else 1.0

        except Exception as e:
            logger.error(f"❌ Error calculando consistencia: {e}")
            return 1.0

    def _estimate_accuracy(self, df: pd.DataFrame) -> float:
        """Estima la precisión de los datos"""
        try:
            accuracy_scores = []

            for column in df.columns:
                if df[column].dtype in ["int64", "float64"]:
                    # Para datos numéricos, verificar si están en rangos lógicos
                    if column.lower() in ["age", "edad"]:
                        # Edad entre 0 y 120
                        valid_range = (df[column] >= 0) & (df[column] <= 120)
                        accuracy_scores.append(valid_range.mean())
                    elif column.lower() in ["price", "precio", "cost", "costo"]:
                        # Precios positivos
                        valid_range = df[column] >= 0
                        accuracy_scores.append(valid_range.mean())
                    else:
                        # Para otros datos numéricos, asumir precisión alta
                        accuracy_scores.append(0.9)
                else:
                    # Para datos categóricos, asumir precisión alta
                    accuracy_scores.append(0.9)

            return np.mean(accuracy_scores) if accuracy_scores else 0.9

        except Exception as e:
            logger.error(f"❌ Error estimando precisión: {e}")
            return 0.9

    def _calculate_validity(self, df: pd.DataFrame) -> float:
        """Calcula la validez de los datos"""
        try:
            validity_scores = []

            for column in df.columns:
                if df[column].dtype in ["object", "string"]:
                    # Verificar si hay valores vacíos o solo espacios
                    non_empty = df[column].str.strip().ne("").sum()
                    total_values = len(df[column].dropna())
                    if total_values > 0:
                        validity_scores.append(non_empty / total_values)
                else:
                    # Para datos numéricos, verificar que no sean infinitos
                    finite_values = np.isfinite(df[column]).sum()
                    total_values = len(df[column].dropna())
                    if total_values > 0:
                        validity_scores.append(finite_values / total_values)

            return np.mean(validity_scores) if validity_scores else 1.0

        except Exception as e:
            logger.error(f"❌ Error calculando validez: {e}")
            return 1.0

    def _calculate_uniqueness(self, df: pd.DataFrame) -> float:
        """Calcula la unicidad de los datos"""
        try:
            # Verificar duplicados
            total_rows = len(df)
            unique_rows = len(df.drop_duplicates())
            uniqueness = unique_rows / total_rows if total_rows > 0 else 1.0
            return uniqueness
        except Exception as e:
            logger.error(f"❌ Error calculando unicidad: {e}")
            return 1.0

    def _estimate_timeliness(self, df: pd.DataFrame) -> float:
        """Estima la oportunidad de los datos"""
        try:
            # Buscar columnas de fecha
            date_columns = []
            for column in df.columns:
                if (
                    df[column].dtype == "datetime64[ns]"
                    or "date" in column.lower()
                    or "time" in column.lower()
                ):
                    date_columns.append(column)

            if date_columns:
                # Si hay columnas de fecha, verificar si son recientes
                most_recent_date = None
                for column in date_columns:
                    if df[column].dtype == "datetime64[ns]":
                        max_date = df[column].max()
                        if most_recent_date is None or max_date > most_recent_date:
                            most_recent_date = max_date

                if most_recent_date:
                    # Calcular días desde la fecha más reciente
                    days_ago = (pd.Timestamp.now() - most_recent_date).days
                    # Asumir que datos de menos de 30 días son oportunos
                    timeliness = max(0, 1 - (days_ago / 30))
                    return timeliness

            # Si no hay fechas, asumir oportunidad alta
            return 0.9

        except Exception as e:
            logger.error(f"❌ Error estimando oportunidad: {e}")
            return 0.9

    def generate_quality_report(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Genera un reporte completo de calidad"""
        try:
            metrics = self.evaluate_dataframe_quality(df)

            # Análisis adicional
            missing_data = df.isnull().sum().to_dict()
            data_types = df.dtypes.to_dict()
            unique_counts = df.nunique().to_dict()

            # Detectar problemas
            issues = []
            if metrics.completeness < self.quality_thresholds["completeness"]:
                issues.append(f"Completitud baja: {metrics.completeness:.3f}")
            if metrics.consistency < self.quality_thresholds["consistency"]:
                issues.append(f"Consistencia baja: {metrics.consistency:.3f}")
            if metrics.validity < self.quality_thresholds["validity"]:
                issues.append(f"Validez baja: {metrics.validity:.3f}")

            return {
                "metrics": {
                    "completeness": metrics.completeness,
                    "consistency": metrics.consistency,
                    "accuracy": metrics.accuracy,
                    "validity": metrics.validity,
                    "uniqueness": metrics.uniqueness,
                    "timeliness": metrics.timeliness,
                    "overall_score": metrics.overall_score,
                },
                "data_summary": {
                    "rows": len(df),
                    "columns": len(df.columns),
                    "missing_data": missing_data,
                    "data_types": {str(k): str(v) for k, v in data_types.items()},
                    "unique_counts": unique_counts,
                },
                "issues": issues,
                "recommendations": self._generate_recommendations(metrics),
            }

        except Exception as e:
            logger.error(f"❌ Error generando reporte de calidad: {e}")
            return {"error": str(e)}


class ModelQualityEvaluator:
    """Evaluador de calidad de modelos"""

    def __init__(self):
        self.quality_thresholds = {
            "generalization": 0.8,
            "robustness": 0.7,
            "interpretability": 0.6,
            "efficiency": 0.8,
            "fairness": 0.9,
        }

    def evaluate_model_quality(
        self,
        model: Any,
        X_test: np.ndarray,
        y_test: np.ndarray,
        training_time: float = 0.0,
        inference_time: float = 0.0,
    ) -> ModelQualityMetrics:
        """Evalúa la calidad de un modelo"""
        try:
            logger.info("🔄 Evaluando calidad del modelo")

            # Generalización
            generalization = self._evaluate_generalization(model, X_test, y_test)

            # Robustez
            robustness = self._evaluate_robustness(model, X_test, y_test)

            # Interpretabilidad
            interpretability = self._evaluate_interpretability(model)

            # Eficiencia
            efficiency = self._evaluate_efficiency(training_time, inference_time)

            # Equidad (simplificado)
            fairness = self._evaluate_fairness(model, X_test, y_test)

            # Puntuación general
            overall_score = np.mean(
                [generalization, robustness, interpretability, efficiency, fairness]
            )

            metrics = ModelQualityMetrics(
                generalization=generalization,
                robustness=robustness,
                interpretability=interpretability,
                efficiency=efficiency,
                fairness=fairness,
                overall_score=overall_score,
            )

            logger.info(
                f"✅ Evaluación de calidad del modelo completada. Puntuación: {overall_score:.3f}"
            )
            return metrics

        except Exception as e:
            logger.error(f"❌ Error evaluando calidad del modelo: {e}")
            return ModelQualityMetrics(0.0, 0.0, 0.0, 0.0, 0.0, 0.0)

    def _evaluate_generalization(
        self, model: Any, X_test: np.ndarray, y_test: np.ndarray
    ) -> float:
        """Evalúa la capacidad de generalización"""
        try:
            # Predicciones en conjunto de prueba
            y_pred = model.predict(X_test)

            # Calcular métricas de rendimiento
            if hasattr(model, "predict_proba"):
                # Para clasificación
                from sklearn.metrics import accuracy_score

                accuracy = accuracy_score(y_test, y_pred)
                return accuracy
            else:
                # Para regresión
                from sklearn.metrics import r2_score

                r2 = r2_score(y_test, y_pred)
                return max(0, r2)  # R² puede ser negativo

        except Exception as e:
            logger.error(f"❌ Error evaluando generalización: {e}")
            return 0.5

    def _evaluate_robustness(
        self, model: Any, X_test: np.ndarray, y_test: np.ndarray
    ) -> float:
        """Evalúa la robustez del modelo"""
        try:
            # Agregar ruido a los datos de prueba
            noise_level = 0.1
            X_noisy = X_test + np.random.normal(0, noise_level, X_test.shape)

            # Predicciones con datos ruidosos
            y_pred_noisy = model.predict(X_noisy)
            y_pred_original = model.predict(X_test)

            # Calcular similitud entre predicciones
            if hasattr(model, "predict_proba"):
                from sklearn.metrics import accuracy_score

                robustness = accuracy_score(y_pred_original, y_pred_noisy)
            else:
                from sklearn.metrics import r2_score

                robustness = max(0, r2_score(y_pred_original, y_pred_noisy))

            return robustness

        except Exception as e:
            logger.error(f"❌ Error evaluando robustez: {e}")
            return 0.7

    def _evaluate_interpretability(self, model: Any) -> float:
        """Evalúa la interpretabilidad del modelo"""
        try:
            interpretability_score = 0.5  # Base

            # Verificar si el modelo tiene características importantes
            if hasattr(model, "feature_importances_"):
                interpretability_score += 0.3

            # Verificar si es un modelo lineal
            if hasattr(model, "coef_"):
                interpretability_score += 0.2

            # Verificar si tiene atributos interpretables
            if hasattr(model, "intercept_"):
                interpretability_score += 0.1

            return min(1.0, interpretability_score)

        except Exception as e:
            logger.error(f"❌ Error evaluando interpretabilidad: {e}")
            return 0.5

    def _evaluate_efficiency(
        self, training_time: float, inference_time: float
    ) -> float:
        """Evalúa la eficiencia del modelo"""
        try:
            # Basado en tiempos de entrenamiento e inferencia
            # Valores de referencia (en segundos)
            ref_training_time = 60.0  # 1 minuto
            ref_inference_time = 0.1  # 100ms

            training_score = max(0, 1 - (training_time / ref_training_time))
            inference_score = max(0, 1 - (inference_time / ref_inference_time))

            efficiency = (training_score + inference_score) / 2
            return efficiency

        except Exception as e:
            logger.error(f"❌ Error evaluando eficiencia: {e}")
            return 0.8

    def _evaluate_fairness(
        self, model: Any, X_test: np.ndarray, y_test: np.ndarray
    ) -> float:
        """Evalúa la equidad del modelo (simplificado)"""
        try:
            # Implementación simplificada de evaluación de equidad
            # En un caso real, se evaluarían diferentes grupos demográficos

            # Por ahora, asumir equidad alta
            return 0.9

        except Exception as e:
            logger.error(f"❌ Error evaluando equidad: {e}")
            return 0.9

    def _generate_recommendations(self, metrics: DataQualityMetrics) -> List[str]:
        """Genera recomendaciones basadas en las métricas"""
        recommendations = []

        if metrics.completeness < 0.9:
            recommendations.append(
                "Considerar estrategias de imputación de datos faltantes"
            )

        if metrics.consistency < 0.8:
            recommendations.append("Implementar validación de datos más estricta")

        if metrics.validity < 0.9:
            recommendations.append("Revisar y limpiar datos inválidos")

        if metrics.uniqueness < 0.95:
            recommendations.append("Eliminar o manejar duplicados")

        if not recommendations:
            recommendations.append("La calidad de los datos es buena")

        return recommendations
