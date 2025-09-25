"""
Sistema de Evaluación - Shaili AI

Este paquete proporciona herramientas completas para evaluar la calidad
de las respuestas generadas por sistemas de IA, incluyendo métricas de
coherencia, diversidad, toxicidad y rendimiento.
"""

from .diversity import DiversityEvaluator
from .toxicity import ToxicityEvaluator
from .coherence import CoherenceEvaluator
from .pipeline import QualityEvaluationPipeline
from .performance_benchmark import PerformanceBenchmark
from .config import EvaluationConfig, PipelineConfig, BenchmarkConfig

# Versión del paquete
__version__ = "3.1.0"
__author__ = "Shaili AI Team"
__description__ = "Sistema completo de evaluación de calidad para IA"

# Instancias globales para uso directo
_diversity_evaluator = None
_toxicity_evaluator = None
_coherence_evaluator = None
_quality_pipeline = None
_performance_benchmark = None


def get_diversity_evaluator() -> DiversityEvaluator:
    """Obtener instancia global del evaluador de diversidad"""
    global _diversity_evaluator
    if _diversity_evaluator is None:
        _diversity_evaluator = DiversityEvaluator()
    return _diversity_evaluator


def get_toxicity_evaluator() -> ToxicityEvaluator:
    """Obtener instancia global del evaluador de toxicidad"""
    global _toxicity_evaluator
    if _toxicity_evaluator is None:
        _toxicity_evaluator = ToxicityEvaluator()
    return _toxicity_evaluator


def get_coherence_evaluator() -> CoherenceEvaluator:
    """Obtener instancia global del evaluador de coherencia"""
    global _coherence_evaluator
    if _coherence_evaluator is None:
        _coherence_evaluator = CoherenceEvaluator()
    return _coherence_evaluator


def get_quality_pipeline() -> QualityEvaluationPipeline:
    """Obtener instancia global del pipeline de evaluación"""
    global _quality_pipeline
    if _quality_pipeline is None:
        _quality_pipeline = QualityEvaluationPipeline()
    return _quality_pipeline


def get_performance_benchmark() -> PerformanceBenchmark:
    """Obtener instancia global del benchmark de rendimiento"""
    global _performance_benchmark
    if _performance_benchmark is None:
        _performance_benchmark = PerformanceBenchmark()
    return _performance_benchmark


# Funciones de conveniencia para evaluación rápida
def evaluate_diversity(text: str) -> dict:
    """
    Evaluar diversidad de un texto

    Args:
        text: Texto a evaluar

    Returns:
        Diccionario con métricas de diversidad
    """
    evaluator = get_diversity_evaluator()
    return evaluator.evaluate_diversity(text)


def evaluate_toxicity(text: str, threshold: float = 0.3) -> dict:
    """
    Evaluar toxicidad de un texto

    Args:
        text: Texto a evaluar
        threshold: Umbral de toxicidad

    Returns:
        Diccionario con métricas de toxicidad
    """
    evaluator = get_toxicity_evaluator()
    return evaluator.evaluate_toxicity(text, threshold)


def evaluate_coherence(query: str, response: str) -> float:
    """
    Evaluar coherencia entre consulta y respuesta

    Args:
        query: Consulta original
        response: Respuesta generada

    Returns:
        Puntuación de coherencia (0-1)
    """
    evaluator = get_coherence_evaluator()
    return evaluator.calculate_coherence(query, response)


def evaluate_quality(query: str, response: str, domain: str = None) -> dict:
    """
    Evaluar calidad completa de una respuesta

    Args:
        query: Consulta original
        response: Respuesta generada
        domain: Dominio opcional

    Returns:
        Diccionario con métricas de calidad completa
    """
    pipeline = get_quality_pipeline()
    return pipeline.evaluate_response(query, response, domain)


def evaluate_conversation(conversation: list, domain: str = None) -> dict:
    """
    Evaluar calidad de una conversación completa

    Args:
        conversation: Lista de mensajes con 'role' y 'content'
        domain: Dominio opcional

    Returns:
        Diccionario con métricas de calidad de la conversación
    """
    pipeline = get_quality_pipeline()
    return pipeline.evaluate_conversation(conversation, domain)


def run_performance_benchmark() -> dict:
    """
    Ejecutar benchmark completo de rendimiento

    Returns:
        Diccionario con resultados del benchmark
    """
    benchmark = get_performance_benchmark()
    return benchmark.run_comprehensive_benchmark()


# Funciones de configuración
def get_evaluation_config() -> dict:
    """Obtener configuración del sistema de evaluación"""
    return {
        "thresholds": EvaluationConfig.get_quality_thresholds(),
        "weights": EvaluationConfig.get_quality_weights(),
        "pipeline_settings": PipelineConfig.get_pipeline_settings(),
        "benchmark_settings": BenchmarkConfig.get_benchmark_settings(),
    }


def update_evaluation_config(thresholds: dict = None, weights: dict = None) -> bool:
    """
    Actualizar configuración del sistema de evaluación

    Args:
        thresholds: Nuevos umbrales de calidad
        weights: Nuevos pesos de métricas

    Returns:
        True si la actualización fue exitosa
    """
    try:
        if thresholds:
            for key, value in thresholds.items():
                if hasattr(EvaluationConfig, "QUALITY_THRESHOLDS"):
                    EvaluationConfig.QUALITY_THRESHOLDS[key] = value

        if weights:
            for key, value in weights.items():
                if hasattr(EvaluationConfig, "QUALITY_WEIGHTS"):
                    EvaluationConfig.QUALITY_WEIGHTS[key] = value

        return True
    except Exception:
        return False


# Funciones de utilidad
def create_evaluation_report(results: dict, output_path: str = None) -> str:
    """
    Crear reporte de evaluación en formato JSON

    Args:
        results: Resultados de evaluación
        output_path: Ruta de salida (opcional)

    Returns:
        Ruta del archivo generado
    """
    import json
    from datetime import datetime
    from pathlib import Path

    if output_path is None:
        output_path = (
            f"evaluation_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        )

    # Asegurar que el directorio existe
    Path(output_path).parent.mkdir(parents=True, exist_ok=True)

    # Agregar metadatos al reporte
    report_data = {
        "timestamp": datetime.now().isoformat(),
        "version": __version__,
        "results": results,
    }

    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(report_data, f, ensure_ascii=False, indent=2)

    return output_path


def validate_evaluation_system() -> dict:
    """
    Validar que todos los componentes del sistema funcionen correctamente

    Returns:
        Diccionario con resultados de validación
    """
    validation_results = {
        "diversity_evaluator": False,
        "toxicity_evaluator": False,
        "coherence_evaluator": False,
        "quality_pipeline": False,
        "performance_benchmark": False,
        "overall_status": False,
    }

    try:
        # Probar evaluador de diversidad
        div_eval = get_diversity_evaluator()
        test_result = div_eval.evaluate_diversity("Texto de prueba para validación.")
        validation_results["diversity_evaluator"] = "diversity_score" in test_result

        # Probar evaluador de toxicidad
        tox_eval = get_toxicity_evaluator()
        test_result = tox_eval.evaluate_toxicity("Texto de prueba para validación.")
        validation_results["toxicity_evaluator"] = "toxicity_score" in test_result

        # Probar evaluador de coherencia
        coh_eval = get_coherence_evaluator()
        test_result = coh_eval.calculate_coherence(
            "¿Qué es la prueba?", "La prueba es un método de validación."
        )
        validation_results["coherence_evaluator"] = isinstance(test_result, float)

        # Probar pipeline de calidad
        pipeline = get_quality_pipeline()
        test_result = pipeline.evaluate_response(
            "¿Qué es la prueba?", "La prueba es un método de validación."
        )
        validation_results["quality_pipeline"] = "composite_score" in test_result

        # Probar benchmark (sin ejecutar completamente)
        benchmark = get_performance_benchmark()
        validation_results["performance_benchmark"] = benchmark is not None

        # Estado general
        validation_results["overall_status"] = all(
            [
                validation_results["diversity_evaluator"],
                validation_results["toxicity_evaluator"],
                validation_results["coherence_evaluator"],
                validation_results["quality_pipeline"],
                validation_results["performance_benchmark"],
            ]
        )

    except Exception as e:
        print(f"Error durante la validación: {e}")

    return validation_results


# Inicialización automática del módulo
def initialize_evaluation_module():
    """Inicializar el módulo de evaluación"""
    try:
        # Crear directorios necesarios
        EvaluationConfig.create_directories()

        # Validar configuración
        from .config import validate_config

        validate_config()

        print("✅ Módulo de evaluación inicializado correctamente")
        return True
    except Exception as e:
        print(f"❌ Error inicializando módulo de evaluación: {e}")
        return False


# Ejecutar inicialización al importar el módulo
initialize_evaluation_module()

# API pública del módulo
__all__ = [
    # Clases principales
    "DiversityEvaluator",
    "ToxicityEvaluator",
    "CoherenceEvaluator",
    "QualityEvaluationPipeline",
    "PerformanceBenchmark",
    "EvaluationConfig",
    "PipelineConfig",
    "BenchmarkConfig",
    # Funciones de conveniencia
    "evaluate_diversity",
    "evaluate_toxicity",
    "evaluate_coherence",
    "evaluate_quality",
    "evaluate_conversation",
    "run_performance_benchmark",
    # Funciones de configuración
    "get_evaluation_config",
    "update_evaluation_config",
    # Funciones de utilidad
    "create_evaluation_report",
    "validate_evaluation_system",
    # Funciones de inicialización
    "initialize_evaluation_module",
    # Metadatos
    "__version__",
    "__author__",
    "__description__",
]
