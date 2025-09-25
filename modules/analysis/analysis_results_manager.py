#!/usr/bin/env python3
"""
Sistema de Gestión de Análisis de Resultados
Gestiona el almacenamiento, análisis y reportes de resultados del sistema
"""

import os
import json
import sqlite3
import logging
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional, Tuple
from pathlib import Path
import matplotlib.pyplot as plt
import seaborn as sns
from dataclasses import dataclass, asdict
import threading
import hashlib


@dataclass
class AnalysisResult:
    """Estructura de datos para resultados de análisis"""

    id: str
    analysis_type: str
    model_name: str
    branch_name: str
    timestamp: datetime
    metrics: Dict[str, float]
    metadata: Dict[str, Any]
    status: str = "completed"
    duration_seconds: float = 0.0
    error_message: str = ""


class AnalysisResultsManager:
    """Gestor completo de análisis de resultados con funciones reales"""

    def __init__(self, results_dir: str = "analysis_results"):
        self.results_dir = Path(results_dir)
        self.results_dir.mkdir(exist_ok=True)

        # Configurar logging
        self.logger = logging.getLogger(__name__)
        self.logger.setLevel(logging.INFO)

        # Inicializar base de datos
        self.db_path = self.results_dir / "analysis_results.db"
        self._init_database()

        # Lock para operaciones thread-safe
        self._lock = threading.Lock()

        # Configurar matplotlib para no mostrar ventanas
        plt.ioff()

        self.logger.info(
            f"✅ AnalysisResultsManager inicializado en {self.results_dir}"
        )

    def _init_database(self):
        """Inicializar base de datos SQLite para resultados"""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS analysis_results (
                    id TEXT PRIMARY KEY,
                    analysis_type TEXT NOT NULL,
                    model_name TEXT NOT NULL,
                    branch_name TEXT NOT NULL,
                    timestamp TIMESTAMP NOT NULL,
                    metrics TEXT NOT NULL,
                    metadata TEXT,
                    status TEXT DEFAULT 'completed',
                    duration_seconds REAL DEFAULT 0.0,
                    error_message TEXT DEFAULT '',
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """
            )

            conn.execute(
                """
                CREATE INDEX IF NOT EXISTS idx_analysis_type ON analysis_results(analysis_type)
            """
            )

            conn.execute(
                """
                CREATE INDEX IF NOT EXISTS idx_model_branch ON analysis_results(model_name, branch_name)
            """
            )

            conn.execute(
                """
                CREATE INDEX IF NOT EXISTS idx_timestamp ON analysis_results(timestamp)
            """
            )

            conn.execute(
                """
                CREATE INDEX IF NOT EXISTS idx_status ON analysis_results(status)
            """
            )

    def _generate_result_id(
        self, analysis_type: str, model_name: str, branch_name: str
    ) -> str:
        """Generar ID único para el resultado"""
        content = (
            f"{analysis_type}:{model_name}:{branch_name}:{datetime.now().isoformat()}"
        )
        return hashlib.sha256(content.encode()).hexdigest()[:16]

    def store_result(
        self,
        analysis_type: str,
        model_name: str,
        branch_name: str,
        metrics: Dict[str, float],
        metadata: Dict[str, Any] = None,
        duration_seconds: float = 0.0,
        error_message: str = "",
    ) -> str:
        """Almacenar resultado de análisis"""
        with self._lock:
            try:
                result_id = self._generate_result_id(
                    analysis_type, model_name, branch_name
                )
                timestamp = datetime.now()

                with sqlite3.connect(self.db_path) as conn:
                    conn.execute(
                        """
                        INSERT INTO analysis_results 
                        (id, analysis_type, model_name, branch_name, timestamp, 
                         metrics, metadata, duration_seconds, error_message)
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """,
                        (
                            result_id,
                            analysis_type,
                            model_name,
                            branch_name,
                            timestamp,
                            json.dumps(metrics),
                            json.dumps(metadata or {}),
                            duration_seconds,
                            error_message,
                        ),
                    )

                self.logger.info(
                    f"💾 Resultado {result_id} almacenado: {analysis_type}"
                )
                return result_id

            except Exception as e:
                self.logger.error(f"❌ Error almacenando resultado: {e}")
                raise

    def get_result(self, result_id: str) -> Optional[AnalysisResult]:
        """Obtener resultado específico"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute(
                """
                SELECT * FROM analysis_results WHERE id = ?
            """,
                (result_id,),
            )
            row = cursor.fetchone()

            if row:
                return AnalysisResult(
                    id=row[0],
                    analysis_type=row[1],
                    model_name=row[2],
                    branch_name=row[3],
                    timestamp=datetime.fromisoformat(row[4]),
                    metrics=json.loads(row[5]),
                    metadata=json.loads(row[6]) if row[6] else {},
                    status=row[7],
                    duration_seconds=row[8],
                    error_message=row[9],
                )
            return None

    def list_results(
        self,
        analysis_type: str = None,
        model_name: str = None,
        branch_name: str = None,
        limit: int = 100,
    ) -> List[AnalysisResult]:
        """Listar resultados con filtros"""
        with sqlite3.connect(self.db_path) as conn:
            query = "SELECT * FROM analysis_results WHERE 1=1"
            params = []

            if analysis_type:
                query += " AND analysis_type = ?"
                params.append(analysis_type)

            if model_name:
                query += " AND model_name = ?"
                params.append(model_name)

            if branch_name:
                query += " AND branch_name = ?"
                params.append(branch_name)

            query += " ORDER BY timestamp DESC LIMIT ?"
            params.append(limit)

            cursor = conn.execute(query, params)
            results = []

            for row in cursor.fetchall():
                results.append(
                    AnalysisResult(
                        id=row[0],
                        analysis_type=row[1],
                        model_name=row[2],
                        branch_name=row[3],
                        timestamp=datetime.fromisoformat(row[4]),
                        metrics=json.loads(row[5]),
                        metadata=json.loads(row[6]) if row[6] else {},
                        status=row[7],
                        duration_seconds=row[8],
                        error_message=row[9],
                    )
                )

            return results

    def get_metrics_summary(
        self,
        analysis_type: str = None,
        model_name: str = None,
        branch_name: str = None,
        days: int = 30,
    ) -> Dict[str, Any]:
        """Obtener resumen de métricas"""
        cutoff_date = datetime.now() - timedelta(days=days)

        with sqlite3.connect(self.db_path) as conn:
            query = """
                SELECT analysis_type, model_name, branch_name,
                       COUNT(*) as total_results,
                       AVG(duration_seconds) as avg_duration,
                       COUNT(CASE WHEN status = 'completed' THEN 1 END) as completed_count,
                       COUNT(CASE WHEN status = 'error' THEN 1 END) as error_count
                FROM analysis_results 
                WHERE timestamp >= ?
            """
            params = [cutoff_date]

            if analysis_type:
                query += " AND analysis_type = ?"
                params.append(analysis_type)

            if model_name:
                query += " AND model_name = ?"
                params.append(model_name)

            if branch_name:
                query += " AND branch_name = ?"
                params.append(branch_name)

            query += " GROUP BY analysis_type, model_name, branch_name"

            cursor = conn.execute(query, params)
            results = []

            for row in cursor.fetchall():
                results.append(
                    {
                        "analysis_type": row[0],
                        "model_name": row[1],
                        "branch_name": row[2],
                        "total_results": row[3],
                        "avg_duration_seconds": row[4] or 0,
                        "completed_count": row[5],
                        "error_count": row[6],
                        "success_rate": (row[5] / row[3] * 100) if row[3] > 0 else 0,
                    }
                )

            return {
                "summary_period_days": days,
                "cutoff_date": cutoff_date.isoformat(),
                "results": results,
                "total_analyses": sum(r["total_results"] for r in results),
            }

    def generate_performance_report(
        self, model_name: str = None, days: int = 30
    ) -> Dict[str, Any]:
        """Generar reporte de rendimiento"""
        results = self.list_results(model_name=model_name, limit=1000)

        if not results:
            return {"error": "No hay resultados para generar reporte"}

        # Convertir a DataFrame para análisis
        df_data = []
        for result in results:
            if result.timestamp >= datetime.now() - timedelta(days=days):
                df_data.append(
                    {
                        "timestamp": result.timestamp,
                        "analysis_type": result.analysis_type,
                        "model_name": result.model_name,
                        "branch_name": result.branch_name,
                        "duration_seconds": result.duration_seconds,
                        "status": result.status,
                        **result.metrics,
                    }
                )

        if not df_data:
            return {"error": "No hay resultados en el período especificado"}

        df = pd.DataFrame(df_data)

        # Análisis de rendimiento
        performance_metrics = {
            "total_analyses": len(df),
            "success_rate": (df["status"] == "completed").mean() * 100,
            "avg_duration_seconds": df["duration_seconds"].mean(),
            "median_duration_seconds": df["duration_seconds"].median(),
            "max_duration_seconds": df["duration_seconds"].max(),
            "min_duration_seconds": df["duration_seconds"].min(),
            "analyses_per_day": len(df) / days,
            "unique_models": df["model_name"].nunique(),
            "unique_branches": df["branch_name"].nunique(),
            "unique_analysis_types": df["analysis_type"].nunique(),
        }

        # Análisis por tipo de análisis
        analysis_type_summary = (
            df.groupby("analysis_type")
            .agg(
                {
                    "duration_seconds": ["count", "mean", "median"],
                    "status": lambda x: (x == "completed").sum(),
                }
            )
            .round(2)
        )

        # Análisis por modelo
        model_summary = (
            df.groupby("model_name")
            .agg(
                {
                    "duration_seconds": ["count", "mean"],
                    "status": lambda x: (x == "completed").sum(),
                }
            )
            .round(2)
        )

        return {
            "report_generated": datetime.now().isoformat(),
            "analysis_period_days": days,
            "performance_metrics": performance_metrics,
            "analysis_type_summary": analysis_type_summary.to_dict(),
            "model_summary": model_summary.to_dict(),
            "recent_results": len(df),
        }

    def generate_visualization(
        self,
        analysis_type: str = None,
        model_name: str = None,
        days: int = 30,
        save_path: str = None,
    ) -> str:
        """Generar visualizaciones de resultados"""
        results = self.list_results(
            analysis_type=analysis_type, model_name=model_name, limit=1000
        )

        if not results:
            return "No hay resultados para visualizar"

        # Filtrar por período
        cutoff_date = datetime.now() - timedelta(days=days)
        filtered_results = [r for r in results if r.timestamp >= cutoff_date]

        if not filtered_results:
            return "No hay resultados en el período especificado"

        # Crear figura con subplots
        fig, axes = plt.subplots(2, 2, figsize=(15, 12))
        fig.suptitle(f"Análisis de Resultados - Últimos {days} días", fontsize=16)

        # 1. Duración por tipo de análisis
        df_duration = pd.DataFrame(
            [
                {
                    "analysis_type": r.analysis_type,
                    "duration_seconds": r.duration_seconds,
                    "status": r.status,
                }
                for r in filtered_results
            ]
        )

        if not df_duration.empty:
            sns.boxplot(
                data=df_duration, x="analysis_type", y="duration_seconds", ax=axes[0, 0]
            )
            axes[0, 0].set_title("Duración por Tipo de Análisis")
            axes[0, 0].set_ylabel("Duración (segundos)")
            axes[0, 0].tick_params(axis="x", rotation=45)

        # 2. Distribución de estados
        status_counts = pd.Series([r.status for r in filtered_results]).value_counts()
        axes[0, 1].pie(
            status_counts.values, labels=status_counts.index, autopct="%1.1f%%"
        )
        axes[0, 1].set_title("Distribución de Estados")

        # 3. Métricas por modelo (si hay métricas numéricas)
        model_metrics = {}
        for result in filtered_results:
            if result.model_name not in model_metrics:
                model_metrics[result.model_name] = []
            for metric_name, metric_value in result.metrics.items():
                if isinstance(metric_value, (int, float)):
                    model_metrics[result.model_name].append(metric_value)

        if model_metrics:
            model_avg_metrics = {
                model: np.mean(values)
                for model, values in model_metrics.items()
                if values
            }
            if model_avg_metrics:
                axes[1, 0].bar(model_avg_metrics.keys(), model_avg_metrics.values())
                axes[1, 0].set_title("Métricas Promedio por Modelo")
                axes[1, 0].tick_params(axis="x", rotation=45)

        # 4. Tendencias temporales
        df_time = pd.DataFrame(
            [
                {
                    "timestamp": r.timestamp,
                    "duration_seconds": r.duration_seconds,
                    "analysis_type": r.analysis_type,
                }
                for r in filtered_results
            ]
        )

        if not df_time.empty:
            df_time.set_index("timestamp", inplace=True)
            df_time.resample("D")["duration_seconds"].mean().plot(ax=axes[1, 1])
            axes[1, 1].set_title("Tendencia de Duración (Promedio Diario)")
            axes[1, 1].set_ylabel("Duración (segundos)")

        plt.tight_layout()

        # Guardar o mostrar
        if save_path:
            save_file = (
                Path(save_path)
                / f"analysis_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png"
            )
            plt.savefig(save_file, dpi=300, bbox_inches="tight")
            plt.close()
            return str(save_file)
        else:
            save_file = (
                self.results_dir
                / f"analysis_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png"
            )
            plt.savefig(save_file, dpi=300, bbox_inches="tight")
            plt.close()
            return str(save_file)

    def export_results(
        self,
        format: str = "json",
        analysis_type: str = None,
        model_name: str = None,
        days: int = 30,
    ) -> str:
        """Exportar resultados en diferentes formatos"""
        results = self.list_results(
            analysis_type=analysis_type, model_name=model_name, limit=10000
        )

        # Filtrar por período
        cutoff_date = datetime.now() - timedelta(days=days)
        filtered_results = [r for r in results if r.timestamp >= cutoff_date]

        if format.lower() == "json":
            export_data = [asdict(r) for r in filtered_results]
            export_file = (
                self.results_dir
                / f"export_results_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            )

            with open(export_file, "w", encoding="utf-8") as f:
                json.dump(export_data, f, indent=2, default=str)

            return str(export_file)

        elif format.lower() == "csv":
            df_data = []
            for result in filtered_results:
                row = {
                    "id": result.id,
                    "analysis_type": result.analysis_type,
                    "model_name": result.model_name,
                    "branch_name": result.branch_name,
                    "timestamp": result.timestamp.isoformat(),
                    "status": result.status,
                    "duration_seconds": result.duration_seconds,
                    "error_message": result.error_message,
                }
                # Añadir métricas
                for metric_name, metric_value in result.metrics.items():
                    row[f"metric_{metric_name}"] = metric_value

                df_data.append(row)

            df = pd.DataFrame(df_data)
            export_file = (
                self.results_dir
                / f"export_results_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
            )
            df.to_csv(export_file, index=False, encoding="utf-8")

            return str(export_file)

        else:
            raise ValueError(f"Formato no soportado: {format}")

    def cleanup_old_results(self, days: int = 90):
        """Limpiar resultados antiguos"""
        cutoff_date = datetime.now() - timedelta(days=days)

        with self._lock:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.execute(
                    """
                    DELETE FROM analysis_results 
                    WHERE timestamp < ?
                """,
                    (cutoff_date,),
                )

                deleted_count = cursor.rowcount
                self.logger.info(f"🧹 {deleted_count} resultados antiguos eliminados")
                return deleted_count

    def get_database_stats(self) -> Dict[str, Any]:
        """Obtener estadísticas de la base de datos"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute(
                """
                SELECT 
                    COUNT(*) as total_results,
                    COUNT(DISTINCT analysis_type) as unique_analysis_types,
                    COUNT(DISTINCT model_name) as unique_models,
                    COUNT(DISTINCT branch_name) as unique_branches,
                    MIN(timestamp) as earliest_result,
                    MAX(timestamp) as latest_result,
                    AVG(duration_seconds) as avg_duration,
                    COUNT(CASE WHEN status = 'completed' THEN 1 END) as completed_count,
                    COUNT(CASE WHEN status = 'error' THEN 1 END) as error_count
                FROM analysis_results
            """
            )
            result = cursor.fetchone()

            return {
                "total_results": result[0],
                "unique_analysis_types": result[1],
                "unique_models": result[2],
                "unique_branches": result[3],
                "earliest_result": result[4],
                "latest_result": result[5],
                "avg_duration_seconds": result[6] or 0,
                "completed_count": result[7],
                "error_count": result[8],
                "success_rate_percent": (
                    (result[7] / result[0] * 100) if result[0] > 0 else 0
                ),
            }


# Instancia global del gestor de resultados
analysis_results_manager = AnalysisResultsManager()
