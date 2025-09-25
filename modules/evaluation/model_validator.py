"""
Validador de Modelos - Model Validator
=====================================

Componentes para validación y verificación de modelos.
"""

import logging
from typing import List, Dict, Any, Optional, Union, Tuple
from dataclasses import dataclass
import numpy as np
import pandas as pd
from sklearn.model_selection import cross_val_score, KFold
from sklearn.metrics import mean_squared_error, accuracy_score
import joblib
import os

logger = logging.getLogger(__name__)


@dataclass
class ValidationResult:
    """Resultado de validación del modelo"""

    is_valid: bool
    score: float
    confidence: float
    issues: List[str]
    recommendations: List[str]


@dataclass
class CrossValidationResult:
    """Resultado de validación cruzada"""

    mean_score: float
    std_score: float
    fold_scores: List[float]
    cv_folds: int


class ModelValidator:
    """Validador de modelos de machine learning"""

    def __init__(self):
        self.validation_thresholds = {
            "min_accuracy": 0.7,
            "min_cv_score": 0.6,
            "max_cv_std": 0.2,
            "min_confidence": 0.8,
        }

    def validate_model(
        self,
        model: Any,
        X: np.ndarray,
        y: np.ndarray,
        validation_type: str = "cross_validation",
    ) -> ValidationResult:
        """Valida un modelo usando diferentes métodos"""
        try:
            logger.info(f"🔄 Validando modelo con método: {validation_type}")

            issues = []
            recommendations = []

            if validation_type == "cross_validation":
                cv_result = self._cross_validate_model(model, X, y)
                score = cv_result.mean_score
                confidence = self._calculate_confidence(cv_result)

                if cv_result.mean_score < self.validation_thresholds["min_cv_score"]:
                    issues.append(
                        f"Puntuación de validación cruzada baja: {cv_result.mean_score:.3f}"
                    )
                    recommendations.append(
                        "Considerar ajustar hiperparámetros o usar más datos"
                    )

                if cv_result.std_score > self.validation_thresholds["max_cv_std"]:
                    issues.append(
                        f"Alta variabilidad en validación cruzada: {cv_result.std_score:.3f}"
                    )
                    recommendations.append(
                        "El modelo puede ser inestable, considerar regularización"
                    )

            elif validation_type == "holdout":
                score, confidence = self._holdout_validate_model(model, X, y)

                if score < self.validation_thresholds["min_accuracy"]:
                    issues.append(f"Puntuación de holdout baja: {score:.3f}")
                    recommendations.append("El modelo necesita mejor entrenamiento")

            else:
                raise ValueError(f"Tipo de validación no soportado: {validation_type}")

            # Validaciones adicionales
            additional_issues = self._validate_model_structure(model)
            issues.extend(additional_issues)

            # Determinar si el modelo es válido
            is_valid = (
                len(issues) == 0
                and confidence >= self.validation_thresholds["min_confidence"]
            )

            if is_valid:
                recommendations.append("El modelo es válido y listo para producción")
            else:
                recommendations.append("El modelo necesita mejoras antes de producción")

            result = ValidationResult(
                is_valid=is_valid,
                score=score,
                confidence=confidence,
                issues=issues,
                recommendations=recommendations,
            )

            logger.info(
                f"✅ Validación completada. Válido: {is_valid}, Puntuación: {score:.3f}"
            )
            return result

        except Exception as e:
            logger.error(f"❌ Error validando modelo: {e}")
            return ValidationResult(
                is_valid=False,
                score=0.0,
                confidence=0.0,
                issues=[f"Error en validación: {str(e)}"],
                recommendations=["Revisar configuración del modelo"],
            )

    def _cross_validate_model(
        self, model: Any, X: np.ndarray, y: np.ndarray
    ) -> CrossValidationResult:
        """Realiza validación cruzada del modelo"""
        try:
            # Configurar validación cruzada
            cv_folds = min(
                5, len(X) // 10
            )  # Máximo 5 folds, mínimo 10 muestras por fold
            cv = KFold(n_splits=cv_folds, shuffle=True, random_state=42)

            # Realizar validación cruzada
            if hasattr(model, "predict_proba"):
                # Para clasificación
                scores = cross_val_score(model, X, y, cv=cv, scoring="accuracy")
            else:
                # Para regresión
                scores = cross_val_score(model, X, y, cv=cv, scoring="r2")

            return CrossValidationResult(
                mean_score=np.mean(scores),
                std_score=np.std(scores),
                fold_scores=scores.tolist(),
                cv_folds=cv_folds,
            )

        except Exception as e:
            logger.error(f"❌ Error en validación cruzada: {e}")
            return CrossValidationResult(0.0, 0.0, [], 0)

    def _holdout_validate_model(
        self, model: Any, X: np.ndarray, y: np.ndarray
    ) -> Tuple[float, float]:
        """Realiza validación holdout del modelo"""
        try:
            from sklearn.model_selection import train_test_split

            # Dividir datos
            X_train, X_test, y_train, y_test = train_test_split(
                X, y, test_size=0.2, random_state=42
            )

            # Entrenar modelo
            model.fit(X_train, y_train)

            # Predicciones
            y_pred = model.predict(X_test)

            # Calcular métricas
            if hasattr(model, "predict_proba"):
                score = accuracy_score(y_test, y_pred)
            else:
                score = max(0, 1 - mean_squared_error(y_test, y_pred))

            # Calcular confianza (simplificado)
            confidence = min(1.0, score + 0.1)

            return score, confidence

        except Exception as e:
            logger.error(f"❌ Error en validación holdout: {e}")
            return 0.0, 0.0

    def _validate_model_structure(self, model: Any) -> List[str]:
        """Valida la estructura del modelo"""
        issues = []

        try:
            # Verificar que el modelo tenga método predict
            if not hasattr(model, "predict"):
                issues.append("El modelo no tiene método predict")

            # Verificar que el modelo esté entrenado
            if hasattr(model, "coef_") and model.coef_ is None:
                issues.append(
                    "El modelo no está entrenado (coeficientes no disponibles)"
                )

            if (
                hasattr(model, "feature_importances_")
                and model.feature_importances_ is None
            ):
                issues.append(
                    "El modelo no está entrenado (importancias no disponibles)"
                )

            # Verificar tamaño del modelo (simplificado)
            model_size = self._estimate_model_size(model)
            if model_size > 1000000:  # 1MB
                issues.append(f"El modelo es muy grande: {model_size/1000000:.1f}MB")

            return issues

        except Exception as e:
            logger.error(f"❌ Error validando estructura del modelo: {e}")
            return ["Error validando estructura del modelo"]

    def _estimate_model_size(self, model: Any) -> int:
        """Estima el tamaño del modelo en bytes"""
        try:
            # Guardar modelo temporalmente
            temp_path = "temp_model.joblib"
            joblib.dump(model, temp_path)

            # Obtener tamaño del archivo
            size = os.path.getsize(temp_path)

            # Limpiar archivo temporal
            os.remove(temp_path)

            return size

        except Exception as e:
            logger.error(f"❌ Error estimando tamaño del modelo: {e}")
            return 0

    def _calculate_confidence(self, cv_result: CrossValidationResult) -> float:
        """Calcula la confianza basada en los resultados de validación cruzada"""
        try:
            # Basado en la puntuación media y la estabilidad
            mean_score = cv_result.mean_score
            std_score = cv_result.std_score

            # Confianza alta si puntuación alta y baja variabilidad
            confidence = mean_score * (1 - std_score)
            return max(0.0, min(1.0, confidence))

        except Exception as e:
            logger.error(f"❌ Error calculando confianza: {e}")
            return 0.5

    def validate_data_compatibility(
        self, model: Any, X: np.ndarray
    ) -> ValidationResult:
        """Valida la compatibilidad de los datos con el modelo"""
        try:
            issues = []
            recommendations = []

            # Verificar dimensiones
            if hasattr(model, "n_features_in_"):
                expected_features = model.n_features_in_
                actual_features = X.shape[1] if len(X.shape) > 1 else 1

                if expected_features != actual_features:
                    issues.append(
                        f"Incompatibilidad de características: esperadas {expected_features}, obtenidas {actual_features}"
                    )
                    recommendations.append(
                        "Ajustar el número de características en los datos de entrada"
                    )

            # Verificar tipos de datos
            if X.dtype not in [np.float32, np.float64, np.int32, np.int64]:
                issues.append("Los datos no son numéricos")
                recommendations.append("Convertir datos a tipos numéricos")

            # Verificar valores faltantes
            if np.isnan(X).any():
                issues.append("Los datos contienen valores NaN")
                recommendations.append("Limpiar o imputar valores faltantes")

            # Verificar valores infinitos
            if np.isinf(X).any():
                issues.append("Los datos contienen valores infinitos")
                recommendations.append("Limpiar valores infinitos")

            is_valid = len(issues) == 0
            score = 1.0 if is_valid else 0.5
            confidence = 1.0 if is_valid else 0.3

            if is_valid:
                recommendations.append("Los datos son compatibles con el modelo")

            return ValidationResult(
                is_valid=is_valid,
                score=score,
                confidence=confidence,
                issues=issues,
                recommendations=recommendations,
            )

        except Exception as e:
            logger.error(f"❌ Error validando compatibilidad de datos: {e}")
            return ValidationResult(
                is_valid=False,
                score=0.0,
                confidence=0.0,
                issues=[f"Error validando datos: {str(e)}"],
                recommendations=["Revisar formato de datos"],
            )

    def generate_validation_report(
        self, model: Any, X: np.ndarray, y: np.ndarray
    ) -> Dict[str, Any]:
        """Genera un reporte completo de validación"""
        try:
            # Validación del modelo
            model_validation = self.validate_model(model, X, y, "cross_validation")

            # Validación de compatibilidad de datos
            data_validation = self.validate_data_compatibility(model, X)

            # Validación cruzada detallada
            cv_result = self._cross_validate_model(model, X, y)

            return {
                "model_validation": {
                    "is_valid": model_validation.is_valid,
                    "score": model_validation.score,
                    "confidence": model_validation.confidence,
                    "issues": model_validation.issues,
                    "recommendations": model_validation.recommendations,
                },
                "data_validation": {
                    "is_valid": data_validation.is_valid,
                    "score": data_validation.score,
                    "confidence": data_validation.confidence,
                    "issues": data_validation.issues,
                    "recommendations": data_validation.recommendations,
                },
                "cross_validation": {
                    "mean_score": cv_result.mean_score,
                    "std_score": cv_result.std_score,
                    "fold_scores": cv_result.fold_scores,
                    "cv_folds": cv_result.cv_folds,
                },
                "overall_assessment": {
                    "is_production_ready": model_validation.is_valid
                    and data_validation.is_valid,
                    "overall_score": (model_validation.score + data_validation.score)
                    / 2,
                    "critical_issues": len(
                        [
                            i
                            for i in model_validation.issues + data_validation.issues
                            if "crítico" in i.lower()
                        ]
                    ),
                },
            }

        except Exception as e:
            logger.error(f"❌ Error generando reporte de validación: {e}")
            return {"error": str(e)}
