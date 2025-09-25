"""
Analizador de Resultados - Result Analyzer
=========================================

Componentes para análisis y visualización de resultados.
"""

import logging
from typing import List, Dict, Any, Optional, Union
from dataclasses import dataclass
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.metrics import confusion_matrix, classification_report
import json
import os

logger = logging.getLogger(__name__)


@dataclass
class AnalysisResult:
    """Resultado del análisis"""

    summary: Dict[str, Any]
    insights: List[str]
    recommendations: List[str]
    visualizations: Dict[str, str]


class ResultAnalyzer:
    """Analizador de resultados de modelos y experimentos"""

    def __init__(self, output_dir: str = "analysis_results"):
        self.output_dir = output_dir
        self._ensure_output_directory()

    def _ensure_output_directory(self):
        """Asegura que existe el directorio de salida"""
        if not os.path.exists(self.output_dir):
            os.makedirs(self.output_dir)
            logger.info(f"✅ Directorio de análisis creado: {self.output_dir}")

    def analyze_classification_results(
        self,
        y_true: Union[List, np.ndarray],
        y_pred: Union[List, np.ndarray],
        class_names: Optional[List[str]] = None,
        save_plots: bool = True,
    ) -> AnalysisResult:
        """Analiza resultados de clasificación"""
        try:
            logger.info("🔄 Analizando resultados de clasificación")

            y_true = np.array(y_true)
            y_pred = np.array(y_pred)

            # Métricas básicas
            from sklearn.metrics import (
                accuracy_score,
                precision_score,
                recall_score,
                f1_score,
            )

            accuracy = accuracy_score(y_true, y_pred)
            precision = precision_score(
                y_true, y_pred, average="weighted", zero_division=0
            )
            recall = recall_score(y_true, y_pred, average="weighted", zero_division=0)
            f1 = f1_score(y_true, y_pred, average="weighted", zero_division=0)

            # Análisis detallado
            insights = []
            recommendations = []

            # Análisis de precisión
            if accuracy < 0.7:
                insights.append("La precisión general es baja")
                recommendations.append(
                    "Considerar más datos de entrenamiento o ajustar hiperparámetros"
                )
            elif accuracy > 0.9:
                insights.append("La precisión es muy alta, posible overfitting")
                recommendations.append(
                    "Verificar en conjunto de validación independiente"
                )

            # Análisis de balance de clases
            class_counts = np.bincount(y_true)
            if len(class_counts) > 1:
                class_balance = min(class_counts) / max(class_counts)
                if class_balance < 0.3:
                    insights.append("Datos desbalanceados detectados")
                    recommendations.append("Considerar técnicas de balanceo de clases")

            # Generar visualizaciones
            visualizations = {}
            if save_plots:
                visualizations = self._generate_classification_plots(
                    y_true, y_pred, class_names
                )

            summary = {
                "accuracy": accuracy,
                "precision": precision,
                "recall": recall,
                "f1_score": f1,
                "n_classes": len(np.unique(y_true)),
                "class_distribution": (
                    class_counts.tolist()
                    if len(class_counts) <= 10
                    else "Demasiadas clases para mostrar"
                ),
            }

            result = AnalysisResult(
                summary=summary,
                insights=insights,
                recommendations=recommendations,
                visualizations=visualizations,
            )

            logger.info(
                f"✅ Análisis de clasificación completado. Accuracy: {accuracy:.3f}"
            )
            return result

        except Exception as e:
            logger.error(f"❌ Error analizando resultados de clasificación: {e}")
            return AnalysisResult({}, [], [], {})

    def analyze_regression_results(
        self,
        y_true: Union[List, np.ndarray],
        y_pred: Union[List, np.ndarray],
        save_plots: bool = True,
    ) -> AnalysisResult:
        """Analiza resultados de regresión"""
        try:
            logger.info("🔄 Analizando resultados de regresión")

            y_true = np.array(y_true)
            y_pred = np.array(y_pred)

            # Métricas básicas
            from sklearn.metrics import (
                mean_squared_error,
                mean_absolute_error,
                r2_score,
            )

            mse = mean_squared_error(y_true, y_pred)
            mae = mean_absolute_error(y_true, y_pred)
            r2 = r2_score(y_true, y_pred)
            rmse = np.sqrt(mse)

            # Análisis de errores
            errors = y_true - y_pred
            mean_error = np.mean(errors)
            std_error = np.std(errors)

            insights = []
            recommendations = []

            # Análisis de R²
            if r2 < 0.5:
                insights.append("El modelo explica menos del 50% de la varianza")
                recommendations.append(
                    "Considerar características adicionales o modelo más complejo"
                )
            elif r2 > 0.95:
                insights.append("R² muy alto, posible overfitting")
                recommendations.append(
                    "Verificar en conjunto de validación independiente"
                )

            # Análisis de sesgo
            if abs(mean_error) > 0.1 * np.std(y_true):
                insights.append("El modelo tiene sesgo significativo")
                recommendations.append("Considerar técnicas de corrección de sesgo")

            # Análisis de outliers en errores
            outlier_threshold = 2 * std_error
            outliers = np.sum(np.abs(errors) > outlier_threshold)
            outlier_percentage = outliers / len(errors) * 100

            if outlier_percentage > 10:
                insights.append(
                    f"Alto porcentaje de outliers en errores: {outlier_percentage:.1f}%"
                )
                recommendations.append("Investigar casos con errores grandes")

            # Generar visualizaciones
            visualizations = {}
            if save_plots:
                visualizations = self._generate_regression_plots(y_true, y_pred)

            summary = {
                "mse": mse,
                "mae": mae,
                "rmse": rmse,
                "r2_score": r2,
                "mean_error": mean_error,
                "std_error": std_error,
                "outlier_percentage": outlier_percentage,
            }

            result = AnalysisResult(
                summary=summary,
                insights=insights,
                recommendations=recommendations,
                visualizations=visualizations,
            )

            logger.info(f"✅ Análisis de regresión completado. R²: {r2:.3f}")
            return result

        except Exception as e:
            logger.error(f"❌ Error analizando resultados de regresión: {e}")
            return AnalysisResult({}, [], [], {})

    def _generate_classification_plots(
        self,
        y_true: np.ndarray,
        y_pred: np.ndarray,
        class_names: Optional[List[str]] = None,
    ) -> Dict[str, str]:
        """Genera visualizaciones para clasificación"""
        try:
            plots = {}

            # Configurar estilo
            plt.style.use("default")
            sns.set_palette("husl")

            # 1. Matriz de confusión
            fig, ax = plt.subplots(figsize=(8, 6))
            cm = confusion_matrix(y_true, y_pred)
            sns.heatmap(cm, annot=True, fmt="d", cmap="Blues", ax=ax)
            ax.set_title("Matriz de Confusión")
            ax.set_xlabel("Predicción")
            ax.set_ylabel("Real")

            if class_names:
                ax.set_xticklabels(class_names)
                ax.set_yticklabels(class_names)

            confusion_plot_path = os.path.join(self.output_dir, "confusion_matrix.png")
            plt.savefig(confusion_plot_path, dpi=300, bbox_inches="tight")
            plt.close()
            plots["confusion_matrix"] = confusion_plot_path

            # 2. Distribución de clases
            fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 5))

            # Distribución real
            unique_true, counts_true = np.unique(y_true, return_counts=True)
            ax1.bar(unique_true, counts_true, alpha=0.7, label="Real")
            ax1.set_title("Distribución de Clases - Real")
            ax1.set_xlabel("Clase")
            ax1.set_ylabel("Frecuencia")

            # Distribución predicha
            unique_pred, counts_pred = np.unique(y_pred, return_counts=True)
            ax2.bar(
                unique_pred, counts_pred, alpha=0.7, label="Predicción", color="orange"
            )
            ax2.set_title("Distribución de Clases - Predicción")
            ax2.set_xlabel("Clase")
            ax2.set_ylabel("Frecuencia")

            plt.tight_layout()
            distribution_plot_path = os.path.join(
                self.output_dir, "class_distribution.png"
            )
            plt.savefig(distribution_plot_path, dpi=300, bbox_inches="tight")
            plt.close()
            plots["class_distribution"] = distribution_plot_path

            return plots

        except Exception as e:
            logger.error(f"❌ Error generando gráficos de clasificación: {e}")
            return {}

    def _generate_regression_plots(
        self, y_true: np.ndarray, y_pred: np.ndarray
    ) -> Dict[str, str]:
        """Genera visualizaciones para regresión"""
        try:
            plots = {}

            # Configurar estilo
            plt.style.use("default")
            sns.set_palette("husl")

            # 1. Predicciones vs Valores reales
            fig, ax = plt.subplots(figsize=(8, 6))
            ax.scatter(y_true, y_pred, alpha=0.6)

            # Línea de referencia perfecta
            min_val = min(y_true.min(), y_pred.min())
            max_val = max(y_true.max(), y_pred.max())
            ax.plot(
                [min_val, max_val],
                [min_val, max_val],
                "r--",
                lw=2,
                label="Predicción perfecta",
            )

            ax.set_xlabel("Valores Reales")
            ax.set_ylabel("Predicciones")
            ax.set_title("Predicciones vs Valores Reales")
            ax.legend()
            ax.grid(True, alpha=0.3)

            scatter_plot_path = os.path.join(self.output_dir, "predictions_vs_real.png")
            plt.savefig(scatter_plot_path, dpi=300, bbox_inches="tight")
            plt.close()
            plots["predictions_vs_real"] = scatter_plot_path

            # 2. Distribución de errores
            fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 5))

            errors = y_true - y_pred

            # Histograma de errores
            ax1.hist(errors, bins=30, alpha=0.7, edgecolor="black")
            ax1.set_title("Distribución de Errores")
            ax1.set_xlabel("Error")
            ax1.set_ylabel("Frecuencia")
            ax1.axvline(0, color="red", linestyle="--", label="Error = 0")
            ax1.legend()

            # Q-Q plot de errores
            from scipy import stats

            stats.probplot(errors, dist="norm", plot=ax2)
            ax2.set_title("Q-Q Plot de Errores")
            ax2.grid(True, alpha=0.3)

            plt.tight_layout()
            errors_plot_path = os.path.join(self.output_dir, "error_analysis.png")
            plt.savefig(errors_plot_path, dpi=300, bbox_inches="tight")
            plt.close()
            plots["error_analysis"] = errors_plot_path

            return plots

        except Exception as e:
            logger.error(f"❌ Error generando gráficos de regresión: {e}")
            return {}

    def generate_comprehensive_report(
        self,
        analysis_results: List[AnalysisResult],
        experiment_name: str = "experiment",
    ) -> str:
        """Genera un reporte completo de análisis"""
        try:
            report_path = os.path.join(
                self.output_dir, f"{experiment_name}_report.html"
            )

            html_content = f"""
            <!DOCTYPE html>
            <html>
            <head>
                <title>Reporte de Análisis - {experiment_name}</title>
                <style>
                    body {{ font-family: Arial, sans-serif; margin: 20px; }}
                    .header {{ background-color: #f0f0f0; padding: 20px; border-radius: 5px; }}
                    .section {{ margin: 20px 0; padding: 15px; border: 1px solid #ddd; border-radius: 5px; }}
                    .metric {{ display: inline-block; margin: 10px; padding: 10px; background-color: #e8f4f8; border-radius: 3px; }}
                    .insight {{ background-color: #fff3cd; padding: 10px; margin: 5px 0; border-left: 4px solid #ffc107; }}
                    .recommendation {{ background-color: #d1ecf1; padding: 10px; margin: 5px 0; border-left: 4px solid #17a2b8; }}
                    .plot {{ text-align: center; margin: 20px 0; }}
                    .plot img {{ max-width: 100%; height: auto; }}
                </style>
            </head>
            <body>
                <div class="header">
                    <h1>Reporte de Análisis - {experiment_name}</h1>
                    <p>Generado el: {pd.Timestamp.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
                </div>
            """

            for i, result in enumerate(analysis_results):
                html_content += f"""
                <div class="section">
                    <h2>Análisis {i+1}</h2>
                    
                    <h3>Resumen de Métricas</h3>
                    <div>
                """

                for key, value in result.summary.items():
                    if isinstance(value, float):
                        html_content += f'<div class="metric"><strong>{key}:</strong> {value:.3f}</div>'
                    else:
                        html_content += (
                            f'<div class="metric"><strong>{key}:</strong> {value}</div>'
                        )

                html_content += """
                    </div>
                    
                    <h3>Insights</h3>
                """

                for insight in result.insights:
                    html_content += f'<div class="insight">{insight}</div>'

                html_content += """
                    <h3>Recomendaciones</h3>
                """

                for recommendation in result.recommendations:
                    html_content += (
                        f'<div class="recommendation">{recommendation}</div>'
                    )

                if result.visualizations:
                    html_content += """
                        <h3>Visualizaciones</h3>
                    """

                    for plot_name, plot_path in result.visualizations.items():
                        if os.path.exists(plot_path):
                            html_content += f"""
                                <div class="plot">
                                    <h4>{plot_name.replace('_', ' ').title()}</h4>
                                    <img src="{os.path.basename(plot_path)}" alt="{plot_name}">
                                </div>
                            """

                html_content += "</div>"

            html_content += """
            </body>
            </html>
            """

            with open(report_path, "w", encoding="utf-8") as f:
                f.write(html_content)

            logger.info(f"✅ Reporte HTML generado: {report_path}")
            return report_path

        except Exception as e:
            logger.error(f"❌ Error generando reporte HTML: {e}")
            return ""

    def save_analysis_to_json(
        self, analysis_result: AnalysisResult, filename: str
    ) -> str:
        """Guarda el análisis en formato JSON"""
        try:
            # Convertir a formato serializable
            serializable_result = {
                "summary": analysis_result.summary,
                "insights": analysis_result.insights,
                "recommendations": analysis_result.recommendations,
                "visualizations": {
                    k: os.path.basename(v)
                    for k, v in analysis_result.visualizations.items()
                },
            }

            json_path = os.path.join(self.output_dir, filename)
            with open(json_path, "w", encoding="utf-8") as f:
                json.dump(serializable_result, f, indent=2, ensure_ascii=False)

            logger.info(f"✅ Análisis guardado en JSON: {json_path}")
            return json_path

        except Exception as e:
            logger.error(f"❌ Error guardando análisis en JSON: {e}")
            return ""
