import logging
from typing import Dict, Any, List
import plotly.graph_objs as go
import plotly.express as px
import pandas as pd
import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output

from evaluation.quality_metrics_advanced import AdvancedQualityMetricsEvaluator
from modules.core.integration_manager import IntegrationManager


class InsightsDashboard:
    def __init__(
        self,
        integration_manager: IntegrationManager,
        quality_evaluator: AdvancedQualityMetricsEvaluator,
    ):
        """
        Panel de visualización de insights con componentes interactivos

        Args:
            integration_manager (IntegrationManager): Gestor de integración
            quality_evaluator (AdvancedQualityMetricsEvaluator): Evaluador de calidad
        """
        self.logger = logging.getLogger(__name__)

        self.integration_manager = integration_manager
        self.quality_evaluator = quality_evaluator

        # Inicializar aplicación Dash
        self.app = dash.Dash(__name__)
        self._setup_dashboard_layout()
        self._setup_dashboard_callbacks()

    def _setup_dashboard_layout(self):
        """
        Configurar diseño del panel de insights
        """
        self.app.layout = html.Div(
            [
                html.H1("Sheily-AI: Panel de Insights"),
                # Sección de métricas de calidad
                html.Div(
                    [
                        html.H2("Métricas de Calidad"),
                        dcc.Graph(id="quality-metrics-chart"),
                        dcc.Interval(
                            id="interval-component",
                            interval=60 * 1000,  # Actualizar cada minuto
                            n_intervals=0,
                        ),
                    ]
                ),
                # Sección de clustering semántico
                html.Div(
                    [
                        html.H2("Clustering Semántico"),
                        dcc.Graph(id="semantic-clustering-chart"),
                    ]
                ),
                # Sección de complejidad cognitiva
                html.Div(
                    [
                        html.H2("Complejidad Cognitiva"),
                        dcc.Graph(id="cognitive-complexity-chart"),
                    ]
                ),
            ]
        )

    def _setup_dashboard_callbacks(self):
        """
        Configurar callbacks para actualización dinámica
        """

        @self.app.callback(
            Output("quality-metrics-chart", "figure"),
            [Input("interval-component", "n_intervals")],
        )
        def update_quality_metrics(n):
            """
            Actualizar gráfico de métricas de calidad
            """
            # Obtener rendimiento histórico
            historical_performance = self.quality_evaluator.get_historical_performance()

            # Crear gráfico de barras
            metrics = historical_performance.get("aggregated_metrics", {})

            fig = go.Figure(
                data=[
                    go.Bar(
                        x=list(metrics.keys()),
                        y=list(metrics.values()),
                        marker_color="rgba(58, 71, 80, 0.6)",
                    )
                ]
            )

            fig.update_layout(
                title="Métricas de Calidad",
                xaxis_title="Métricas",
                yaxis_title="Puntuación",
            )

            return fig

        @self.app.callback(
            Output("semantic-clustering-chart", "figure"),
            [Input("interval-component", "n_intervals")],
        )
        def update_semantic_clustering(n):
            """
            Actualizar gráfico de clustering semántico
            """
            # Obtener insights avanzados
            recent_interactions = (
                self.integration_manager.continuous_improvement.get_recent_interactions()
            )
            insights = self.integration_manager.generate_advanced_insights(
                recent_interactions
            )

            # Convertir clusters a DataFrame
            clusters_data = []
            for cluster, texts in insights["semantic_clusters"].items():
                clusters_data.extend(
                    [{"Cluster": cluster, "Texto": texto} for texto in texts]
                )

            df_clusters = pd.DataFrame(clusters_data)

            # Crear gráfico de dispersión
            fig = px.scatter(
                df_clusters,
                x="Cluster",
                y="Texto",
                color="Cluster",
                title="Clustering Semántico de Interacciones",
            )

            return fig

        @self.app.callback(
            Output("cognitive-complexity-chart", "figure"),
            [Input("interval-component", "n_intervals")],
        )
        def update_cognitive_complexity(n):
            """
            Actualizar gráfico de complejidad cognitiva
            """
            # Obtener insights avanzados
            recent_interactions = (
                self.integration_manager.continuous_improvement.get_recent_interactions()
            )
            insights = self.integration_manager.generate_advanced_insights(
                recent_interactions
            )

            # Preparar datos de complejidad
            complexity_data = []
            for cluster, complexities in insights["complexity_analysis"].items():
                complexity_data.extend(
                    [{"Cluster": cluster, **complexity} for complexity in complexities]
                )

            df_complexity = pd.DataFrame(complexity_data)

            # Crear gráfico de cajas
            fig = px.box(
                df_complexity,
                x="Cluster",
                y=["linguistic_complexity", "semantic_depth", "information_density"],
                title="Complejidad Cognitiva por Cluster",
            )

            return fig

    def run(self, host: str = "127.0.0.1", port: int = 8050):
        """
        Ejecutar dashboard de insights

        Args:
            host (str): Host para servir el dashboard
            port (int): Puerto para servir el dashboard
        """
        self.app.run_server(debug=True, host=host, port=port)

    def generate_report(self, time_window_hours: int = 24) -> Dict[str, Any]:
        """
        Generar informe detallado de insights

        Args:
            time_window_hours (int): Ventana de tiempo para el informe

        Returns:
            Informe de insights
        """
        # Obtener rendimiento histórico
        historical_performance = self.quality_evaluator.get_historical_performance(
            time_window_hours
        )

        # Obtener insights avanzados
        recent_interactions = (
            self.integration_manager.continuous_improvement.get_recent_interactions()
        )
        advanced_insights = self.integration_manager.generate_advanced_insights(
            recent_interactions
        )

        return {
            "performance_metrics": historical_performance,
            "semantic_insights": advanced_insights,
            "time_window_hours": time_window_hours,
        }
