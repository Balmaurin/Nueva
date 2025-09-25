#!/usr/bin/env python3
"""
Sistema de Pruebas - Sistema de Evaluación Shaili AI

Este script ejecuta pruebas completas para validar que todos los componentes
del sistema de evaluación funcionen correctamente.
"""

import sys
import json
import time
from pathlib import Path
from datetime import datetime


def test_diversity_evaluator():
    """Probar el evaluador de diversidad"""
    print("🧪 Probando DiversityEvaluator...")

    try:
        from diversity import DiversityEvaluator

        evaluator = DiversityEvaluator()

        # Textos de prueba
        test_texts = [
            "La fotosíntesis es un proceso biológico fascinante.",
            "En la fotosíntesis, las plantas utilizan clorofila para capturar energía solar, que luego convierten en glucosa a través de complejas reacciones metabólicas que ocurren en los cloroplastos.",
            "Las plantas, organismos fotosintéticos fundamentales, despliegan un intrincado mecanismo molecular para transformar la radiación lumínica en energía química.",
        ]

        results = []
        for i, text in enumerate(test_texts, 1):
            result = evaluator.evaluate_diversity(text)
            results.append(
                {
                    "text_id": i,
                    "text": text[:50] + "..." if len(text) > 50 else text,
                    "diversity_score": result["diversity_score"],
                    "lexical_metrics": result["lexical_metrics"],
                    "syntactic_metrics": result["syntactic_metrics"],
                    "semantic_metrics": result["semantic_metrics"],
                }
            )

        print(f"  ✅ Evaluador de diversidad probado con {len(test_texts)} textos")
        return True, results

    except Exception as e:
        print(f"  ❌ Error en evaluador de diversidad: {e}")
        return False, None


def test_toxicity_evaluator():
    """Probar el evaluador de toxicidad"""
    print("🧪 Probando ToxicityEvaluator...")

    try:
        from toxicity import ToxicityEvaluator

        evaluator = ToxicityEvaluator()

        # Textos de prueba
        test_texts = [
            "La fotosíntesis es un proceso biológico fascinante.",
            "Ese tipo es un idiota completo, no sabe nada.",
            "Los inmigrantes deberían ser expulsados del país.",
            "NO ESTOY DE ACUERDO CON TU OPINIÓN ESTÚPIDA!",
            "No creo que sea una buena idea, pero respeto tu opinión.",
        ]

        results = []
        for i, text in enumerate(test_texts, 1):
            result = evaluator.evaluate_toxicity(text)
            results.append(
                {
                    "text_id": i,
                    "text": text[:50] + "..." if len(text) > 50 else text,
                    "is_toxic": result["is_toxic"],
                    "toxicity_score": result["toxicity_score"],
                    "toxic_categories": result["toxic_categories"],
                }
            )

        print(f"  ✅ Evaluador de toxicidad probado con {len(test_texts)} textos")
        return True, results

    except Exception as e:
        print(f"  ❌ Error en evaluador de toxicidad: {e}")
        return False, None


def test_coherence_evaluator():
    """Probar el evaluador de coherencia"""
    print("🧪 Probando CoherenceEvaluator...")

    try:
        from coherence import CoherenceEvaluator

        evaluator = CoherenceEvaluator()

        # Pares de consulta-respuesta de prueba
        test_pairs = [
            {
                "query": "¿Qué es la fotosíntesis?",
                "response": "La fotosíntesis es un proceso biológico donde las plantas transforman luz solar en energía química.",
            },
            {
                "query": "¿Cómo funciona la fotosíntesis?",
                "response": "En la fotosíntesis, las plantas utilizan clorofila para capturar energía solar, que luego convierten en glucosa a través de complejas reacciones metabólicas.",
            },
            {
                "query": "¿Qué es la fotosíntesis?",
                "response": "Los gatos son animales domésticos que cazan ratones.",
            },
        ]

        results = []
        for i, pair in enumerate(test_pairs, 1):
            coherence_score = evaluator.calculate_coherence(
                pair["query"], pair["response"]
            )
            detailed_analysis = evaluator.get_detailed_coherence_analysis(
                pair["query"], pair["response"]
            )

            results.append(
                {
                    "pair_id": i,
                    "query": pair["query"],
                    "response": (
                        pair["response"][:50] + "..."
                        if len(pair["response"]) > 50
                        else pair["response"]
                    ),
                    "coherence_score": coherence_score,
                    "semantic_coherence": detailed_analysis["semantic_coherence"],
                    "relevance": detailed_analysis["relevance"],
                }
            )

        print(f"  ✅ Evaluador de coherencia probado con {len(test_pairs)} pares")
        return True, results

    except Exception as e:
        print(f"  ❌ Error en evaluador de coherencia: {e}")
        return False, None


def test_quality_pipeline():
    """Probar el pipeline de evaluación de calidad"""
    print("🧪 Probando QualityEvaluationPipeline...")

    try:
        from pipeline import QualityEvaluationPipeline

        pipeline = QualityEvaluationPipeline()

        # Ejemplo de conversación
        conversation = [
            {"role": "user", "content": "¿Qué es la fotosíntesis?"},
            {
                "role": "assistant",
                "content": "La fotosíntesis es un proceso biológico donde las plantas transforman luz solar en energía química.",
            },
            {"role": "user", "content": "¿Cómo funciona exactamente?"},
            {
                "role": "assistant",
                "content": "En la fotosíntesis, las plantas utilizan clorofila para capturar energía solar, que luego convierten en glucosa a través de complejas reacciones metabólicas.",
            },
        ]

        # Evaluar respuesta individual
        response_eval = pipeline.evaluate_response(
            conversation[0]["content"], conversation[1]["content"], domain="Biología"
        )

        # Evaluar conversación completa
        conversation_eval = pipeline.evaluate_conversation(
            conversation, domain="Biología"
        )

        results = {
            "response_evaluation": response_eval,
            "conversation_evaluation": conversation_eval,
        }

        print("  ✅ Pipeline de evaluación de calidad probado")
        return True, results

    except Exception as e:
        print(f"  ❌ Error en pipeline de evaluación: {e}")
        return False, None


def test_performance_benchmark():
    """Probar el benchmark de rendimiento"""
    print("🧪 Probando PerformanceBenchmark...")

    try:
        from performance_benchmark import PerformanceBenchmark

        benchmark = PerformanceBenchmark()

        # Generar datos de prueba
        test_texts = benchmark.generate_test_data(num_texts=10)

        # Probar generación de datos
        if len(test_texts) > 0:
            print(f"  ✅ Benchmark generó {len(test_texts)} textos de prueba")
            return True, {"test_texts_count": len(test_texts)}
        else:
            print("  ⚠️ Benchmark no generó textos de prueba")
            return False, None

    except Exception as e:
        print(f"  ❌ Error en benchmark de rendimiento: {e}")
        return False, None


def test_configuration():
    """Probar la configuración del sistema"""
    print("🧪 Probando configuración...")

    try:
        from config import EvaluationConfig, PipelineConfig, BenchmarkConfig

        # Probar obtención de configuración
        thresholds = EvaluationConfig.get_quality_thresholds()
        weights = EvaluationConfig.get_quality_weights()
        pipeline_settings = PipelineConfig.get_pipeline_settings()
        benchmark_settings = BenchmarkConfig.get_benchmark_settings()

        # Crear directorios
        EvaluationConfig.create_directories()

        config_results = {
            "thresholds": thresholds,
            "weights": weights,
            "pipeline_settings": pipeline_settings,
            "benchmark_settings": benchmark_settings,
        }

        print("  ✅ Configuración probada correctamente")
        return True, config_results

    except Exception as e:
        print(f"  ❌ Error en configuración: {e}")
        return False, None


def test_package_imports():
    """Probar importaciones del paquete"""
    print("🧪 Probando importaciones del paquete...")

    try:
        import evaluation

        # Probar funciones de conveniencia
        diversity_result = evaluation.evaluate_diversity(
            "Texto de prueba para diversidad."
        )
        toxicity_result = evaluation.evaluate_toxicity(
            "Texto de prueba para toxicidad."
        )
        coherence_result = evaluation.evaluate_coherence(
            "¿Qué es la prueba?", "La prueba es un método de validación."
        )

        # Probar configuración
        config = evaluation.get_evaluation_config()

        # Probar validación del sistema
        validation = evaluation.validate_evaluation_system()

        import_results = {
            "diversity_test": "diversity_score" in diversity_result,
            "toxicity_test": "toxicity_score" in toxicity_result,
            "coherence_test": isinstance(coherence_result, float),
            "config_test": "thresholds" in config,
            "validation_test": validation["overall_status"],
        }

        print("  ✅ Importaciones del paquete probadas correctamente")
        return True, import_results

    except Exception as e:
        print(f"  ❌ Error en importaciones del paquete: {e}")
        return False, None


def generate_test_report(test_results):
    """Generar reporte de pruebas"""
    print("📊 Generando reporte de pruebas...")

    report = {
        "timestamp": datetime.now().isoformat(),
        "test_summary": {
            "total_tests": len(test_results),
            "passed_tests": sum(1 for result in test_results.values() if result[0]),
            "failed_tests": sum(1 for result in test_results.values() if not result[0]),
        },
        "test_results": test_results,
        "overall_status": all(result[0] for result in test_results.values()),
    }

    # Guardar reporte
    report_path = Path("results/evaluation/test_report.json")
    report_path.parent.mkdir(parents=True, exist_ok=True)

    with open(report_path, "w", encoding="utf-8") as f:
        json.dump(report, f, ensure_ascii=False, indent=2)

    print(f"  ✅ Reporte guardado en: {report_path}")
    return report


def main():
    """Función principal de pruebas"""
    print("🚀 INICIANDO PRUEBAS DEL SISTEMA DE EVALUACIÓN")
    print("=" * 60)

    start_time = time.time()

    # Ejecutar todas las pruebas
    test_functions = [
        ("diversity_evaluator", test_diversity_evaluator),
        ("toxicity_evaluator", test_toxicity_evaluator),
        ("coherence_evaluator", test_coherence_evaluator),
        ("quality_pipeline", test_quality_pipeline),
        ("performance_benchmark", test_performance_benchmark),
        ("configuration", test_configuration),
        ("package_imports", test_package_imports),
    ]

    test_results = {}

    for test_name, test_func in test_functions:
        print(f"\n--- {test_name.upper()} ---")
        success, results = test_func()
        test_results[test_name] = (success, results)

        if success:
            print(f"✅ {test_name} - EXITOSO")
        else:
            print(f"❌ {test_name} - FALLIDO")

    # Generar reporte
    print("\n" + "=" * 60)
    report = generate_test_report(test_results)

    # Mostrar resumen
    print("\n📋 RESUMEN DE PRUEBAS:")
    print(f"  Total de pruebas: {report['test_summary']['total_tests']}")
    print(f"  Pruebas exitosas: {report['test_summary']['passed_tests']}")
    print(f"  Pruebas fallidas: {report['test_summary']['failed_tests']}")
    print(
        f"  Estado general: {'✅ EXITOSO' if report['overall_status'] else '❌ FALLIDO'}"
    )

    end_time = time.time()
    print(f"\n⏱️  Tiempo total de pruebas: {end_time - start_time:.2f} segundos")

    # Mostrar detalles de pruebas fallidas
    failed_tests = [name for name, (success, _) in test_results.items() if not success]
    if failed_tests:
        print(f"\n⚠️  Pruebas fallidas: {', '.join(failed_tests)}")

    print("\n" + "=" * 60)

    # Retornar código de salida
    return 0 if report["overall_status"] else 1


if __name__ == "__main__":
    sys.exit(main())
