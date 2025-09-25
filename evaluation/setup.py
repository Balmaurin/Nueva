#!/usr/bin/env python3
"""
Script de Instalación y Configuración - Sistema de Evaluación Shaili AI

Este script automatiza la instalación y configuración del sistema de evaluación
de calidad de respuestas de IA.
"""

import os
import sys
import subprocess
import importlib
from pathlib import Path


def check_python_version():
    """Verificar versión de Python"""
    if sys.version_info < (3, 8):
        print("❌ Error: Se requiere Python 3.8 o superior")
        sys.exit(1)
    print(f"✅ Python {sys.version_info.major}.{sys.version_info.minor} detectado")


def install_package(package):
    """Instalar paquete usando pip"""
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", package])
        return True
    except subprocess.CalledProcessError:
        return False


def check_package(package_name):
    """Verificar si un paquete está instalado"""
    try:
        importlib.import_module(package_name)
        return True
    except ImportError:
        return False


def install_dependencies():
    """Instalar dependencias del sistema de evaluación"""
    print("📦 Instalando dependencias...")

    dependencies = [
        "numpy",
        "nltk",
        "spacy",
        "torch",
        "matplotlib",
        # sentence-transformers removido
        "scikit-learn",
    ]

    for package in dependencies:
        if not check_package(package.replace("-", "_")):
            print(f"  Instalando {package}...")
            if install_package(package):
                print(f"  ✅ {package} instalado")
            else:
                print(f"  ❌ Error instalando {package}")
                return False
        else:
            print(f"  ✅ {package} ya está instalado")

    return True


def download_nlp_resources():
    """Descargar recursos de NLP"""
    print("🌐 Descargando recursos de NLP...")

    # Descargar modelo de SpaCy
    try:
        # SpaCy removido
        pass
        print("  ✅ Modelo SpaCy español descargado")
    except subprocess.CalledProcessError:
        print("  ❌ Error descargando modelo SpaCy")
        return False

    # Descargar recursos de NLTK
    try:
        import nltk

        nltk.download("punkt", quiet=True)
        print("  ✅ Recursos NLTK descargados")
    except Exception as e:
        print(f"  ❌ Error descargando recursos NLTK: {e}")
        return False

    return True


def create_directories():
    """Crear directorios necesarios"""
    print("📁 Creando directorios...")

    directories = [
        "logs/evaluation",
        "results/evaluation",
        "models/evaluation",
        "datasets/test",
    ]

    for directory in directories:
        Path(directory).mkdir(parents=True, exist_ok=True)
        print(f"  ✅ Directorio {directory} creado")

    return True


def test_imports():
    """Probar importaciones de los módulos"""
    print("🧪 Probando importaciones...")

    modules_to_test = [
        ("numpy", "numpy"),
        ("nltk", "nltk"),
        ("spacy", "spacy"),
        ("torch", "torch"),
        ("matplotlib", "matplotlib"),
        # sentence_transformers removido
        ("sklearn", "scikit-learn"),
    ]

    for module_name, package_name in modules_to_test:
        try:
            importlib.import_module(module_name)
            print(f"  ✅ {package_name} importado correctamente")
        except ImportError as e:
            print(f"  ❌ Error importando {package_name}: {e}")
            return False

    return True


def test_evaluation_modules():
    """Probar módulos de evaluación"""
    print("🔍 Probando módulos de evaluación...")

    # Cambiar al directorio de evaluación
    original_dir = os.getcwd()
    evaluation_dir = Path(__file__).parent
    os.chdir(evaluation_dir)

    try:
        # Probar importación de módulos
        from diversity import DiversityEvaluator

        print("  ✅ DiversityEvaluator importado")

        from toxicity import ToxicityEvaluator

        print("  ✅ ToxicityEvaluator importado")

        from coherence import CoherenceEvaluator

        print("  ✅ CoherenceEvaluator importado")

        from pipeline import QualityEvaluationPipeline

        print("  ✅ QualityEvaluationPipeline importado")

        from performance_benchmark import PerformanceBenchmark

        print("  ✅ PerformanceBenchmark importado")

        from config import EvaluationConfig

        print("  ✅ EvaluationConfig importado")

    except ImportError as e:
        print(f"  ❌ Error importando módulos de evaluación: {e}")
        os.chdir(original_dir)
        return False

    os.chdir(original_dir)
    return True


def run_basic_tests():
    """Ejecutar pruebas básicas"""
    print("🧪 Ejecutando pruebas básicas...")

    try:
        # Cambiar al directorio de evaluación
        original_dir = os.getcwd()
        evaluation_dir = Path(__file__).parent
        os.chdir(evaluation_dir)

        # Probar evaluador de diversidad
        from diversity import DiversityEvaluator

        evaluator = DiversityEvaluator()
        test_text = "La fotosíntesis es un proceso biológico fascinante."
        result = evaluator.evaluate_diversity(test_text)
        print(f"  ✅ Test de diversidad: {result['diversity_score']:.3f}")

        # Probar evaluador de toxicidad
        from toxicity import ToxicityEvaluator

        toxicity_evaluator = ToxicityEvaluator()
        result = toxicity_evaluator.evaluate_toxicity(test_text)
        print(f"  ✅ Test de toxicidad: {result['toxicity_score']:.3f}")

        # Probar evaluador de coherencia
        from coherence import CoherenceEvaluator

        coherence_evaluator = CoherenceEvaluator()
        result = coherence_evaluator.calculate_coherence(
            "¿Qué es la fotosíntesis?", test_text
        )
        print(f"  ✅ Test de coherencia: {result:.3f}")

        os.chdir(original_dir)
        return True

    except Exception as e:
        print(f"  ❌ Error en pruebas básicas: {e}")
        os.chdir(original_dir)
        return False


def create_sample_data():
    """Crear datos de ejemplo para testing"""
    print("📝 Creando datos de ejemplo...")

    sample_data = {
        "queries": [
            "¿Qué es la fotosíntesis?",
            "¿Cómo funciona la inteligencia artificial?",
            "¿Cuáles son los síntomas de la diabetes?",
            "¿Qué es el cambio climático?",
            "¿Cómo se desarrolla una aplicación web?",
        ],
        "responses": [
            "La fotosíntesis es un proceso biológico donde las plantas transforman luz solar en energía química.",
            "La inteligencia artificial es una rama de la computación que busca crear sistemas capaces de realizar tareas que requieren inteligencia humana.",
            "Los síntomas de la diabetes incluyen sed excesiva, micción frecuente, fatiga y visión borrosa.",
            "El cambio climático se refiere a las alteraciones a largo plazo en los patrones climáticos globales.",
            "Una aplicación web se desarrolla usando tecnologías como HTML, CSS, JavaScript y frameworks modernos.",
        ],
    }

    import json

    test_data_path = Path("datasets/test/sample_data.json")
    test_data_path.parent.mkdir(parents=True, exist_ok=True)

    with open(test_data_path, "w", encoding="utf-8") as f:
        json.dump(sample_data, f, ensure_ascii=False, indent=2)

    print(f"  ✅ Datos de ejemplo creados en {test_data_path}")
    return True


def main():
    """Función principal de instalación"""
    print("🚀 Instalando Sistema de Evaluación - Shaili AI")
    print("=" * 50)

    # Verificar versión de Python
    check_python_version()

    # Instalar dependencias
    if not install_dependencies():
        print("❌ Error instalando dependencias")
        sys.exit(1)

    # Descargar recursos de NLP
    if not download_nlp_resources():
        print("❌ Error descargando recursos de NLP")
        sys.exit(1)

    # Crear directorios
    if not create_directories():
        print("❌ Error creando directorios")
        sys.exit(1)

    # Probar importaciones
    if not test_imports():
        print("❌ Error en importaciones")
        sys.exit(1)

    # Probar módulos de evaluación
    if not test_evaluation_modules():
        print("❌ Error en módulos de evaluación")
        sys.exit(1)

    # Ejecutar pruebas básicas
    if not run_basic_tests():
        print("❌ Error en pruebas básicas")
        sys.exit(1)

    # Crear datos de ejemplo
    create_sample_data()

    print("\n" + "=" * 50)
    print("✅ Instalación completada exitosamente!")
    print("\n📋 Próximos pasos:")
    print("  1. Ejecutar: python evaluation/diversity.py")
    print("  2. Ejecutar: python evaluation/toxicity.py")
    print("  3. Ejecutar: python evaluation/coherence.py")
    print("  4. Ejecutar: python evaluation/pipeline.py")
    print("  5. Ejecutar: python evaluation/performance_benchmark.py")
    print("\n📖 Para más información, consulta: evaluation/README.md")


if __name__ == "__main__":
    main()
