"""
Configuración del Sistema de Evaluación - Shaili AI

Este archivo contiene todas las configuraciones necesarias para el sistema
de evaluación de calidad de respuestas de IA.
"""

import os
from typing import Dict, Any


class EvaluationConfig:
    """Configuración centralizada para el sistema de evaluación"""

    # Configuración de directorios
    LOG_DIR = "logs/evaluation"
    RESULTS_DIR = "results/evaluation"
    MODELS_DIR = "models/evaluation"

    # Configuración de modelos de NLP
    MAIN_MODEL = "models/custom/shaili-personal-model"

    # Configuración de umbrales de calidad
    QUALITY_THRESHOLDS = {
        "coherence": 0.6,
        "diversity": 0.5,
        "toxicity": 0.3,
        "overall": 0.7,
    }

    # Pesos para puntuación compuesta
    QUALITY_WEIGHTS = {"coherence": 0.4, "diversity": 0.3, "toxicity": 0.3}

    # Configuración de logging
    LOGGING_CONFIG = {
        "level": "INFO",
        "format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        "file_rotation": "daily",
        "max_files": 30,
    }

    # Configuración de benchmark
    BENCHMARK_CONFIG = {
        "test_data_size": 500,
        "timeout_seconds": 300,
        "memory_limit_mb": 2048,
        "save_visualizations": True,
    }

    # Configuración de toxicidad
    TOXICITY_CONFIG = {
        "categories": {
            "insultos": {
                "severity": 0.7,
                "keywords": ["idiota", "estúpido", "imbécil", "tonto", "pendejo"],
            },
            "discriminacion": {
                "severity": 0.8,
                "keywords": ["negro", "indio", "sudaca", "extranjero", "inmigrante"],
            },
            "sexismo": {
                "severity": 0.6,
                "keywords": ["machista", "feminazi", "sexista", "débil", "histérica"],
            },
            "violencia": {
                "severity": 0.9,
                "keywords": ["matar", "golpear", "agredir", "violencia", "muerte"],
            },
        },
        "context_penalty": 0.3,
        "max_toxicity_score": 1.0,
    }

    # Configuración de diversidad
    DIVERSITY_CONFIG = {
        "min_sentence_length": 5,
        "max_sentence_length": 50,
        "min_lexical_diversity": 0.3,
        "min_syntactic_complexity": 0.4,
    }

    # Configuración de coherencia
    COHERENCE_CONFIG = {
        "min_semantic_similarity": 0.5,
        "min_relevance_score": 0.6,
        "min_connector_density": 0.1,
        "min_entity_consistency": 0.7,
    }

    @classmethod
    def get_model_paths(cls) -> Dict[str, str]:
        """Obtener rutas de modelos"""
        return {"main_model": cls.MAIN_MODEL}

    @classmethod
    def get_quality_thresholds(cls) -> Dict[str, float]:
        """Obtener umbrales de calidad"""
        return cls.QUALITY_THRESHOLDS.copy()

    @classmethod
    def get_quality_weights(cls) -> Dict[str, float]:
        """Obtener pesos de calidad"""
        return cls.QUALITY_WEIGHTS.copy()

    @classmethod
    def create_directories(cls):
        """Crear directorios necesarios"""
        directories = [cls.LOG_DIR, cls.RESULTS_DIR, cls.MODELS_DIR]
        for directory in directories:
            os.makedirs(directory, exist_ok=True)

    @classmethod
    def get_log_file_path(cls, evaluator_name: str) -> str:
        """Obtener ruta del archivo de log"""
        return os.path.join(cls.LOG_DIR, f"{evaluator_name}.log")

    @classmethod
    def get_results_file_path(cls, evaluator_name: str) -> str:
        """Obtener ruta del archivo de resultados"""
        return os.path.join(cls.RESULTS_DIR, f"{evaluator_name}_results.json")

    @classmethod
    def get_visualization_path(cls, name: str) -> str:
        """Obtener ruta para visualizaciones"""
        return os.path.join(cls.RESULTS_DIR, f"{name}.png")


class PipelineConfig:
    """Configuración específica para el pipeline de evaluación"""

    # Configuración de procesamiento por lotes
    BATCH_SIZE = 10
    MAX_WORKERS = 4

    # Configuración de cache
    ENABLE_CACHE = True
    CACHE_TTL = 3600  # 1 hora

    # Configuración de evaluación de conversaciones
    MAX_CONVERSATION_LENGTH = 50
    MIN_CONVERSATION_LENGTH = 2

    # Configuración de reportes
    GENERATE_REPORTS = True
    REPORT_FORMATS = ["json", "html", "csv"]

    @classmethod
    def get_pipeline_settings(cls) -> Dict[str, Any]:
        """Obtener configuración del pipeline"""
        return {
            "batch_size": cls.BATCH_SIZE,
            "max_workers": cls.MAX_WORKERS,
            "enable_cache": cls.ENABLE_CACHE,
            "cache_ttl": cls.CACHE_TTL,
            "max_conversation_length": cls.MAX_CONVERSATION_LENGTH,
            "min_conversation_length": cls.MIN_CONVERSATION_LENGTH,
            "generate_reports": cls.GENERATE_REPORTS,
            "report_formats": cls.REPORT_FORMATS,
        }


class BenchmarkConfig:
    """Configuración específica para benchmarks de rendimiento"""

    # Configuración de pruebas
    TEST_SIZES = [10, 50, 100, 500, 1000]
    REPETITIONS = 3

    # Configuración de métricas
    METRICS_TO_TRACK = [
        "execution_time",
        "memory_usage",
        "cpu_usage",
        "accuracy",
        "throughput",
    ]

    # Configuración de visualización
    PLOT_STYLES = {"figure_size": (12, 8), "dpi": 300, "style": "seaborn-v0_8"}

    @classmethod
    def get_benchmark_settings(cls) -> Dict[str, Any]:
        """Obtener configuración del benchmark"""
        return {
            "test_sizes": cls.TEST_SIZES,
            "repetitions": cls.REPETITIONS,
            "metrics_to_track": cls.METRICS_TO_TRACK,
            "plot_styles": cls.PLOT_STYLES,
        }


# Configuración de entorno
ENVIRONMENT_CONFIG = {
    "development": {
        "log_level": "DEBUG",
        "save_intermediate_results": True,
        "enable_profiling": True,
    },
    "production": {
        "log_level": "INFO",
        "save_intermediate_results": False,
        "enable_profiling": False,
    },
    "testing": {
        "log_level": "WARNING",
        "save_intermediate_results": True,
        "enable_profiling": False,
    },
}


def get_environment_config(env: str = "development") -> Dict[str, Any]:
    """Obtener configuración según el entorno"""
    return ENVIRONMENT_CONFIG.get(env, ENVIRONMENT_CONFIG["development"])


def validate_config():
    """Validar configuración"""
    # Verificar que los pesos sumen 1.0
    weights = EvaluationConfig.get_quality_weights()
    total_weight = sum(weights.values())
    if abs(total_weight - 1.0) > 0.01:
        raise ValueError(
            f"Los pesos de calidad deben sumar 1.0, actual: {total_weight}"
        )

    # Verificar umbrales válidos
    thresholds = EvaluationConfig.get_quality_thresholds()
    for name, threshold in thresholds.items():
        if not 0 <= threshold <= 1:
            raise ValueError(
                f"Umbral {name} debe estar entre 0 y 1, actual: {threshold}"
            )

    print("✅ Configuración validada correctamente")


if __name__ == "__main__":
    # Crear directorios
    EvaluationConfig.create_directories()

    # Validar configuración
    validate_config()

    # Mostrar configuración
    print("📋 Configuración del Sistema de Evaluación:")
    print(f"  Umbrales: {EvaluationConfig.get_quality_thresholds()}")
    print(f"  Pesos: {EvaluationConfig.get_quality_weights()}")
    print(f"  Modelos: {EvaluationConfig.get_model_paths()}")
    print(
        f"  Directorios creados: {EvaluationConfig.LOG_DIR}, {EvaluationConfig.RESULTS_DIR}"
    )
