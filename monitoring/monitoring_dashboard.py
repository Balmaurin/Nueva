#!/usr/bin/env python3
"""
Dashboard de Monitoreo Real para Shaili AI
==========================================
Interfaz web para visualizar métricas y alertas del sistema
"""

import dash
from dash import dcc, html, Input, Output, callback
import plotly.graph_objs as go
import plotly.express as px
from plotly.subplots import make_subplots
import pandas as pd
import sqlite3
import json
import logging
import traceback
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, Any, List
import threading
import time
import requests  # Añadir esta importación al principio del archivo

# Configurar logging con más detalles
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    filename="monitoring/logs/monitoring_dashboard.log",
    filemode="a",
)
logger = logging.getLogger(__name__)


def log_error(message: str, error: Exception = None):
    """Método centralizado para registro de errores"""
    error_details = f"{message}\n{traceback.format_exc()}" if error else message
    logger.error(error_details)

    # Opcional: Enviar notificación de error
    try:
        from monitoring.alert_manager import AlertManager

        alert_manager = AlertManager()
        alert_manager.process_alert(
            {"alert_type": "dashboard_error", "severity": "warning", "message": message}
        )
    except Exception as notification_error:
        logger.error(f"Error enviando notificación de error: {notification_error}")


# Inicializar Dash app
app = dash.Dash(__name__, title="Shaili AI Monitoring Dashboard")
app.config.suppress_callback_exceptions = True


class MonitoringDashboard:
    """Dashboard de monitoreo del sistema Shaili AI"""

    def __init__(self, db_path: str = "monitoring/metrics.db"):
        self.db_path = db_path
        self.update_interval = 30000  # 30 segundos

        # Crear directorio si no existe
        Path(self.db_path).parent.mkdir(parents=True, exist_ok=True)

    def get_system_metrics_data(self, hours: int = 24) -> pd.DataFrame:
        """Obtener datos de métricas del sistema"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cutoff_time = datetime.now() - timedelta(hours=hours)

                query = """
                    SELECT timestamp, cpu_percent, memory_percent, disk_usage_percent,
                           memory_used_bytes, memory_total_bytes, active_connections
                    FROM system_metrics 
                    WHERE timestamp > ?
                    ORDER BY timestamp
                """

                df = pd.read_sql_query(query, conn, params=(cutoff_time.isoformat(),))
                df["timestamp"] = pd.to_datetime(df["timestamp"])

                return df

        except Exception as e:
            log_error("❌ Error obteniendo métricas del sistema", e)
            return pd.DataFrame()

    def get_model_metrics_data(self, hours: int = 24) -> pd.DataFrame:
        """Obtener datos de métricas del modelo"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cutoff_time = datetime.now() - timedelta(hours=hours)

                query = """
                    SELECT timestamp, model_name, inference_time_ms, memory_usage_bytes,
                           gpu_usage_percent, requests_per_minute, error_rate, response_time_avg_ms
                    FROM model_metrics 
                    WHERE timestamp > ?
                    ORDER BY timestamp
                """

                df = pd.read_sql_query(query, conn, params=(cutoff_time.isoformat(),))
                df["timestamp"] = pd.to_datetime(df["timestamp"])

                return df

        except Exception as e:
            log_error("❌ Error obteniendo métricas del modelo", e)
            return pd.DataFrame()

    def get_branch_metrics_data(self, hours: int = 24) -> pd.DataFrame:
        """Obtener datos de métricas de ramas"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cutoff_time = datetime.now() - timedelta(hours=hours)

                query = """
                    SELECT timestamp, branch_name, active_adapters, training_progress,
                           accuracy_score, loss_value, samples_processed
                    FROM branch_metrics 
                    WHERE timestamp > ?
                    ORDER BY timestamp
                """

                df = pd.read_sql_query(query, conn, params=(cutoff_time.isoformat(),))
                df["timestamp"] = pd.to_datetime(df["timestamp"])

                return df

        except Exception as e:
            log_error("❌ Error obteniendo métricas de ramas", e)
            return pd.DataFrame()

    def get_alerts_data(self, hours: int = 24) -> pd.DataFrame:
        """Obtener datos de alertas"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cutoff_time = datetime.now() - timedelta(hours=hours)

                query = """
                    SELECT timestamp, alert_type, severity, message, resolved
                    FROM alerts 
                    WHERE timestamp > ?
                    ORDER BY timestamp DESC
                """

                df = pd.read_sql_query(query, conn, params=(cutoff_time.isoformat(),))
                df["timestamp"] = pd.to_datetime(df["timestamp"])

                return df

        except Exception as e:
            log_error("❌ Error obteniendo alertas", e)
            return pd.DataFrame()

    def create_system_metrics_chart(self, df: pd.DataFrame) -> go.Figure:
        """Crear gráfico de métricas del sistema"""
        if df.empty:
            return go.Figure().add_annotation(
                text="No hay datos disponibles",
                xref="paper",
                yref="paper",
                x=0.5,
                y=0.5,
                showarrow=False,
            )

        fig = make_subplots(
            rows=3,
            cols=1,
            subplot_titles=("CPU Usage (%)", "Memory Usage (%)", "Disk Usage (%)"),
            vertical_spacing=0.1,
        )

        # CPU Usage
        fig.add_trace(
            go.Scatter(
                x=df["timestamp"],
                y=df["cpu_percent"],
                mode="lines",
                name="CPU %",
                line=dict(color="#1f77b4", width=2),
            ),
            row=1,
            col=1,
        )

        # Memory Usage
        fig.add_trace(
            go.Scatter(
                x=df["timestamp"],
                y=df["memory_percent"],
                mode="lines",
                name="Memory %",
                line=dict(color="#ff7f0e", width=2),
            ),
            row=2,
            col=1,
        )

        # Disk Usage
        fig.add_trace(
            go.Scatter(
                x=df["timestamp"],
                y=df["disk_usage_percent"],
                mode="lines",
                name="Disk %",
                line=dict(color="#2ca02c", width=2),
            ),
            row=3,
            col=1,
        )

        fig.update_layout(
            height=600, showlegend=False, title_text="System Metrics", title_x=0.5
        )

        return fig

    def create_model_metrics_chart(self, df: pd.DataFrame) -> go.Figure:
        """Crear gráfico de métricas del modelo"""
        if df.empty:
            return go.Figure().add_annotation(
                text="No hay datos disponibles",
                xref="paper",
                yref="paper",
                x=0.5,
                y=0.5,
                showarrow=False,
            )

        fig = make_subplots(
            rows=2,
            cols=2,
            subplot_titles=(
                "Inference Time (ms)",
                "GPU Usage (%)",
                "Requests/min",
                "Error Rate (%)",
            ),
            specs=[
                [{"secondary_y": False}, {"secondary_y": False}],
                [{"secondary_y": False}, {"secondary_y": False}],
            ],
        )

        # Inference Time
        for model in df["model_name"].unique():
            model_data = df[df["model_name"] == model]
            fig.add_trace(
                go.Scatter(
                    x=model_data["timestamp"],
                    y=model_data["inference_time_ms"],
                    mode="lines",
                    name=f"{model} - Inference",
                    line=dict(width=2),
                ),
                row=1,
                col=1,
            )

        # GPU Usage
        for model in df["model_name"].unique():
            model_data = df[df["model_name"] == model]
            fig.add_trace(
                go.Scatter(
                    x=model_data["timestamp"],
                    y=model_data["gpu_usage_percent"],
                    mode="lines",
                    name=f"{model} - GPU",
                    line=dict(width=2),
                ),
                row=1,
                col=2,
            )

        # Requests per minute
        for model in df["model_name"].unique():
            model_data = df[df["model_name"] == model]
            fig.add_trace(
                go.Scatter(
                    x=model_data["timestamp"],
                    y=model_data["requests_per_minute"],
                    mode="lines",
                    name=f"{model} - Requests",
                    line=dict(width=2),
                ),
                row=2,
                col=1,
            )

        # Error Rate
        for model in df["model_name"].unique():
            model_data = df[df["model_name"] == model]
            fig.add_trace(
                go.Scatter(
                    x=model_data["timestamp"],
                    y=model_data["error_rate"],
                    mode="lines",
                    name=f"{model} - Errors",
                    line=dict(width=2),
                ),
                row=2,
                col=2,
            )

        fig.update_layout(
            height=500, title_text="Model Metrics", title_x=0.5, showlegend=True
        )

        return fig

    def create_branch_metrics_chart(self, df: pd.DataFrame) -> go.Figure:
        """Crear gráfico de métricas de ramas"""
        if df.empty:
            return go.Figure().add_annotation(
                text="No hay datos disponibles",
                xref="paper",
                yref="paper",
                x=0.5,
                y=0.5,
                showarrow=False,
            )

        fig = make_subplots(
            rows=2,
            cols=2,
            subplot_titles=(
                "Training Progress (%)",
                "Accuracy Score (%)",
                "Loss Value",
                "Active Adapters",
            ),
            specs=[
                [{"secondary_y": False}, {"secondary_y": False}],
                [{"secondary_y": False}, {"secondary_y": False}],
            ],
        )

        # Training Progress
        for branch in df["branch_name"].unique():
            branch_data = df[df["branch_name"] == branch]
            fig.add_trace(
                go.Scatter(
                    x=branch_data["timestamp"],
                    y=branch_data["training_progress"],
                    mode="lines",
                    name=f"{branch} - Progress",
                    line=dict(width=2),
                ),
                row=1,
                col=1,
            )

        # Accuracy Score
        for branch in df["branch_name"].unique():
            branch_data = df[df["branch_name"] == branch]
            fig.add_trace(
                go.Scatter(
                    x=branch_data["timestamp"],
                    y=branch_data["accuracy_score"],
                    mode="lines",
                    name=f"{branch} - Accuracy",
                    line=dict(width=2),
                ),
                row=1,
                col=2,
            )

        # Loss Value
        for branch in df["branch_name"].unique():
            branch_data = df[df["branch_name"] == branch]
            fig.add_trace(
                go.Scatter(
                    x=branch_data["timestamp"],
                    y=branch_data["loss_value"],
                    mode="lines",
                    name=f"{branch} - Loss",
                    line=dict(width=2),
                ),
                row=2,
                col=1,
            )

        # Active Adapters
        for branch in df["branch_name"].unique():
            branch_data = df[df["branch_name"] == branch]
            fig.add_trace(
                go.Scatter(
                    x=branch_data["timestamp"],
                    y=branch_data["active_adapters"],
                    mode="lines",
                    name=f"{branch} - Adapters",
                    line=dict(width=2),
                ),
                row=2,
                col=2,
            )

        fig.update_layout(
            height=500, title_text="Branch Metrics", title_x=0.5, showlegend=True
        )

        return fig

    def create_alerts_table(self, df: pd.DataFrame) -> go.Figure:
        """Crear tabla de alertas"""
        if df.empty:
            return go.Figure().add_annotation(
                text="No hay alertas disponibles",
                xref="paper",
                yref="paper",
                x=0.5,
                y=0.5,
                showarrow=False,
            )

        # Filtrar solo las últimas 10 alertas
        recent_alerts = df.head(10)

        fig = go.Figure(
            data=[
                go.Table(
                    header=dict(
                        values=["Timestamp", "Type", "Severity", "Message", "Status"],
                        fill_color="#1f77b4",
                        font=dict(color="white", size=12),
                        align="left",
                    ),
                    cells=dict(
                        values=[
                            recent_alerts["timestamp"].dt.strftime("%Y-%m-%d %H:%M"),
                            recent_alerts["alert_type"],
                            recent_alerts["severity"],
                            recent_alerts["message"],
                            [
                                "Resolved" if x else "Active"
                                for x in recent_alerts["resolved"]
                            ],
                        ],
                        fill_color="lavender",
                        align="left",
                        font=dict(size=10),
                    ),
                )
            ]
        )

        fig.update_layout(title_text="Recent Alerts", title_x=0.5, height=400)

        return fig


# Crear instancia del dashboard
dashboard = MonitoringDashboard()

# Layout del dashboard
app.layout = html.Div(
    [
        # Header
        html.Div(
            [
                html.H1(
                    "🚀 Shaili AI Monitoring Dashboard",
                    style={
                        "textAlign": "center",
                        "color": "#1f77b4",
                        "marginBottom": 20,
                    },
                ),
                html.Div(
                    [
                        html.Span("Last updated: ", style={"fontWeight": "bold"}),
                        html.Span(id="last-update", style={"color": "#666"}),
                    ],
                    style={"textAlign": "center", "marginBottom": 20},
                ),
            ]
        ),
        # Controles
        html.Div(
            [
                html.Label("Time Range (hours):", style={"marginRight": 10}),
                dcc.Dropdown(
                    id="time-range",
                    options=[
                        {"label": "1 hour", "value": 1},
                        {"label": "6 hours", "value": 6},
                        {"label": "12 hours", "value": 12},
                        {"label": "24 hours", "value": 24},
                    ],
                    value=24,
                    style={"width": 150, "display": "inline-block"},
                ),
                html.Button(
                    "Refresh",
                    id="refresh-btn",
                    n_clicks=0,
                    style={"marginLeft": 20, "padding": "5px 15px"},
                ),
            ],
            style={"textAlign": "center", "marginBottom": 30},
        ),
        # Métricas del sistema
        html.Div(
            [
                html.H2(
                    "📊 System Metrics",
                    style={"textAlign": "center", "color": "#1f77b4"},
                ),
                dcc.Graph(id="system-metrics-chart"),
            ],
            style={"marginBottom": 40},
        ),
        # Métricas del modelo
        html.Div(
            [
                html.H2(
                    "🤖 Model Metrics",
                    style={"textAlign": "center", "color": "#1f77b4"},
                ),
                dcc.Graph(id="model-metrics-chart"),
            ],
            style={"marginBottom": 40},
        ),
        # Métricas de ramas
        html.Div(
            [
                html.H2(
                    "🌿 Branch Metrics",
                    style={"textAlign": "center", "color": "#1f77b4"},
                ),
                dcc.Graph(id="branch-metrics-chart"),
            ],
            style={"marginBottom": 40},
        ),
        # Alertas
        html.Div(
            [
                html.H2(
                    "🚨 Recent Alerts",
                    style={"textAlign": "center", "color": "#1f77b4"},
                ),
                dcc.Graph(id="alerts-table"),
            ],
            style={"marginBottom": 40},
        ),
        # Intervalo de actualización automática
        dcc.Interval(
            id="interval-component", interval=dashboard.update_interval, n_intervals=0
        ),
        # Sección de chat (nueva)
        html.Div(
            [
                html.H2(
                    "💬 Chat with LLM",
                    style={"textAlign": "center", "color": "#1f77b4"},
                ),
                html.Div(
                    id="chat-history",
                    style={
                        "height": "300px",
                        "overflowY": "scroll",
                        "border": "1px solid #ddd",
                        "padding": "10px",
                        "marginBottom": "10px",
                    },
                ),
                dcc.Input(
                    id="user-chat-input",
                    type="text",
                    placeholder="Escribe tu mensaje aquí...",
                    style={
                        "width": "calc(100% - 20px)",
                        "padding": "10px",
                        "border": "1px solid #ccc",
                    },
                ),
                html.Button(
                    "Enviar",
                    id="send-chat-btn",
                    n_clicks=0,
                    style={
                        "marginLeft": "10px",
                        "padding": "10px 15px",
                        "backgroundColor": "#1f77b4",
                        "color": "white",
                        "border": "none",
                    },
                ),
            ],
            style={"marginBottom": 40},
        ),
        # Almacenar el historial del chat (oculto)
        dcc.Store(id="chat-storage", data=[]),
    ]
)


# Callbacks
@app.callback(
    [
        Output("system-metrics-chart", "figure"),
        Output("model-metrics-chart", "figure"),
        Output("branch-metrics-chart", "figure"),
        Output("alerts-table", "figure"),
        Output("last-update", "children"),
    ],
    [
        Input("interval-component", "n_intervals"),
        Input("refresh-btn", "n_clicks"),
        Input("time-range", "value"),
    ],
)
def update_charts(n_intervals, n_clicks, time_range):
    """Actualizar todos los gráficos"""
    try:
        # Obtener datos
        system_df = dashboard.get_system_metrics_data(time_range)
        model_df = dashboard.get_model_metrics_data(time_range)
        branch_df = dashboard.get_branch_metrics_data(time_range)
        alerts_df = dashboard.get_alerts_data(time_range)

        # Crear gráficos
        system_chart = dashboard.create_system_metrics_chart(system_df)
        model_chart = dashboard.create_model_metrics_chart(model_df)
        branch_chart = dashboard.create_branch_metrics_chart(branch_df)
        alerts_table = dashboard.create_alerts_table(alerts_df)

        # Timestamp de última actualización
        last_update = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        return system_chart, model_chart, branch_chart, alerts_table, last_update

    except Exception as e:
        log_error("❌ Error actualizando gráficos", e)
        # Retornar gráficos vacíos en caso de error
        empty_fig = go.Figure().add_annotation(
            text="Error loading data",
            xref="paper",
            yref="paper",
            x=0.5,
            y=0.5,
            showarrow=False,
        )
        return empty_fig, empty_fig, empty_fig, empty_fig, "Error"


@app.callback(
    [
        Output("chat-history", "children"),
        Output("user-chat-input", "value"),
        Output("chat-storage", "data"),
    ],
    [
        Input("send-chat-btn", "n_clicks"),
        Input("user-chat-input", "n_submit"),
    ],  # Para enviar con Enter
    [dash.State("user-chat-input", "value"), dash.State("chat-storage", "data")],
)
def handle_chat_input(send_btn_clicks, n_submit, user_message, chat_history):
    ctx = dash.callback_context

    if not ctx.triggered:
        return dash.no_update, "", chat_history

    button_id = ctx.triggered[0]["prop_id"].split(".")[0]

    if (button_id == "send-chat-btn" and send_btn_clicks > 0) or (
        button_id == "user-chat-input" and n_submit
    ):
        if user_message is None or user_message.strip() == "":
            return dash.no_update, "", chat_history

        # Añadir mensaje del usuario al historial
        chat_history.append({"role": "user", "content": user_message})

        # Preparar mensajes para enviar al LLM (solo el contenido y rol)
        llm_messages = [
            {"role": msg["role"], "content": msg["content"]} for msg in chat_history
        ]

        try:
            # Enviar mensaje al servidor LLM
            response = requests.post(
                "http://127.0.0.1:8005/chat",
                json={"messages": llm_messages},
                timeout=120,
            )
            response.raise_for_status()  # Lanza excepción para códigos de error HTTP
            llm_response = response.json()["response"]
        except requests.exceptions.RequestException as e:
            logger.error(f"❌ Error al conectar con el servidor LLM: {e}")
            llm_response = f"Error: No se pudo conectar con el LLM. ({e})"
        except Exception as e:
            logger.error(f"❌ Error inesperado del LLM: {e}")
            llm_response = f"Error: Respuesta inesperada del LLM. ({e})"

        # Añadir respuesta del LLM al historial
        chat_history.append({"role": "assistant", "content": llm_response})

        # Formatear historial para mostrar en el Div
        display_history = []
        for msg in chat_history:
            style = (
                {"textAlign": "right", "color": "#1f77b4", "marginBottom": "5px"}
                if msg["role"] == "user"
                else {"textAlign": "left", "color": "#333", "marginBottom": "5px"}
            )
            prefix = "Usted: " if msg["role"] == "user" else "LLM: "
            display_history.append(html.Div(f"{prefix}{msg['content']}", style=style))

        return display_history, "", chat_history

    return dash.no_update, "", chat_history


def run_dashboard(host: str = "127.0.0.1", port: int = 8050, debug: bool = False):
    """Ejecutar el dashboard"""
    logger.info(f"🚀 Iniciando dashboard en http://{host}:{port}")
    app.run(host=host, port=port, debug=debug)


def main():
    """Función principal"""
    print("🚀 Shaili AI Monitoring Dashboard")
    print("=" * 40)
    print("Iniciando servidor...")

    try:
        run_dashboard(debug=True)
    except KeyboardInterrupt:
        print("\n🛑 Dashboard detenido")
    except Exception as e:
        log_error("❌ Error ejecutando dashboard", e)


if __name__ == "__main__":
    main()
