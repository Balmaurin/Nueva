#!/usr/bin/env python3
"""
Script para descargar y procesar dataset de entrenamiento para el sistema de aprendizaje continuo
"""

import json
import os
from datasets import load_dataset
from pathlib import Path


def download_mlqa_dataset():
    """Descargar dataset MLQA (multilingüe)"""
    print("🔄 Descargando dataset MLQA...")

    try:
        # Descargar dataset MLQA
        dataset = load_dataset("mlqa", "mlqa.es.es")

        print(f"✅ Dataset MLQA descargado exitosamente")
        print(
            f"📊 Tamaño del dataset: {len(dataset['train'])} ejemplos de entrenamiento"
        )

        # Crear directorio si no existe
        output_dir = Path("data/training_datasets")
        output_dir.mkdir(parents=True, exist_ok=True)

        # Procesar datos para formato de entrenamiento
        training_data = []

        for split in ["train", "validation"]:
            if split in dataset:
                print(f"🔄 Procesando split: {split}")

                for i, example in enumerate(dataset[split]):
                    # Extraer pregunta y respuesta
                    question = example.get("question", "")
                    answer = (
                        example.get("answers", {}).get("text", [""])[0]
                        if example.get("answers")
                        else ""
                    )

                    if question and answer:
                        # Determinar dominio basado en el contenido

                        # Determinar dominio basado en el contenido
                        domain = _determine_domain(question, answer)

                        # Crear ejemplo de entrenamiento
                        training_example = {
                            "input_text": question,
                            "target_text": answer,
                            "quality_score": 0.9,  # Alta calidad para dataset profesional
                            "source": f"mlqa_{split}",
                            "timestamp": 1756062674.4658723,
                            "domain": domain,
                        }

                        training_data.append(training_example)

                        # Limitar para no sobrecargar (primeros 3000 ejemplos)
                        if len(training_data) >= 3000:
                            break

        # Guardar dataset procesado
        output_file = output_dir / "mlqa_training_dataset.json"
        with open(output_file, "w", encoding="utf-8") as f:
            json.dump(training_data, f, ensure_ascii=False, indent=2)

        print(f"✅ Dataset guardado en: {output_file}")
        print(f"📊 Total de ejemplos procesados: {len(training_data)}")

        return output_file

    except Exception as e:
        print(f"❌ Error descargando MLQA: {e}")
        return None


def download_xquad_dataset():
    """Descargar dataset XQuAD"""
    print("🔄 Descargando dataset XQuAD...")

    try:
        # Descargar dataset XQuAD
        dataset = load_dataset("xquad", "xquad.es")

        print(f"✅ Dataset XQuAD descargado exitosamente")
        print(f"📊 Tamaño del dataset: {len(dataset['validation'])} ejemplos")

        # Crear directorio si no existe
        output_dir = Path("data/training_datasets")
        output_dir.mkdir(parents=True, exist_ok=True)

        # Procesar datos para formato de entrenamiento
        training_data = []

        for example in dataset["validation"]:
            # Extraer pregunta y respuesta
            question = example.get("question", "")
            answer = (
                example.get("answers", {}).get("text", [""])[0]
                if example.get("answers")
                else ""
            )

            if question and answer:
                # Determinar dominio basado en el contenido
                domain = _determine_domain(question, answer)

                # Crear ejemplo de entrenamiento
                training_example = {
                    "input_text": question,
                    "target_text": answer,
                    "quality_score": 0.9,
                    "source": "xquad_validation",
                    "timestamp": 1756062674.4658723,
                    "domain": domain,
                }

                training_data.append(training_example)

        # Guardar dataset procesado
        output_file = output_dir / "xquad_training_dataset.json"
        with open(output_file, "w", encoding="utf-8") as f:
            json.dump(training_data, f, ensure_ascii=False, indent=2)

        print(f"✅ Dataset guardado en: {output_file}")
        print(f"📊 Total de ejemplos procesados: {len(training_data)}")

        return output_file

    except Exception as e:
        print(f"❌ Error descargando XQuAD: {e}")
        return None


def download_tydiqa_dataset():
    """Descargar dataset TyDiQA"""
    print("🔄 Descargando dataset TyDiQA...")

    try:
        # Descargar dataset TyDiQA
        dataset = load_dataset("tydiqa", "primary_task")

        print(f"✅ Dataset TyDiQA descargado exitosamente")
        print(
            f"📊 Tamaño del dataset: {len(dataset['train'])} ejemplos de entrenamiento"
        )

        # Crear directorio si no existe
        output_dir = Path("data/training_datasets")
        output_dir.mkdir(parents=True, exist_ok=True)

        # Procesar datos para formato de entrenamiento
        training_data = []

        for split in ["train", "validation"]:
            if split in dataset:
                print(f"🔄 Procesando split: {split}")

                for i, example in enumerate(dataset[split]):
                    # Solo procesar ejemplos en español
                    if example.get("language", "") == "spanish":

                        if question and answer:
                            # Determinar dominio basado en el contenido
                            domain = _determine_domain(question, answer)

                            # Crear ejemplo de entrenamiento
                            training_example = {
                                "input_text": question,
                                "target_text": answer,
                                "quality_score": 0.85,
                                "source": f"tydiqa_{split}",
                                "timestamp": 1756062674.4658723,
                                "domain": domain,
                            }

                            training_data.append(training_example)

                            # Limitar para no sobrecargar (primeros 2000 ejemplos)
                            if len(training_data) >= 2000:
                                break

        # Guardar dataset procesado
        output_file = output_dir / "tydiqa_training_dataset.json"
        with open(output_file, "w", encoding="utf-8") as f:
            json.dump(training_data, f, ensure_ascii=False, indent=2)

        print(f"✅ Dataset guardado en: {output_file}")
        print(f"📊 Total de ejemplos procesados: {len(training_data)}")

        return output_file

    except Exception as e:
        print(f"❌ Error descargando TyDiQA: {e}")
        return None


def create_synthetic_dataset():
    """Crear dataset sintético de alta calidad para entrenamiento"""
    print("🔄 Creando dataset sintético de alta calidad...")

    # Crear directorio si no existe
    output_dir = Path("data/training_datasets")
    output_dir.mkdir(parents=True, exist_ok=True)

    # Dataset sintético con preguntas y respuestas de alta calidad
    synthetic_data = [
        # Médico
        {
            "input_text": "¿Cuáles son los síntomas principales del COVID-19?",
            "target_text": "Los síntomas principales del COVID-19 incluyen fiebre, tos seca, fatiga, pérdida del gusto u olfato, dificultad para respirar, dolor muscular y de garganta. En casos graves puede causar neumonía y síndrome de dificultad respiratoria aguda.",
            "quality_score": 0.95,
            "source": "synthetic_medical",
            "timestamp": 1756062674.4658723,
            "domain": "medical",
        },
        {
            "input_text": "¿Qué es la hipertensión arterial?",
            "target_text": "La hipertensión arterial es una condición médica caracterizada por una presión arterial persistentemente elevada. Se considera hipertensión cuando la presión sistólica es ≥140 mmHg y/o la diastólica ≥90 mmHg. Es un factor de riesgo importante para enfermedades cardiovasculares.",
            "quality_score": 0.95,
            "source": "synthetic_medical",
            "timestamp": 1756062674.4658723,
            "domain": "medical",
        },
        # Técnico
        {
            "input_text": "¿Qué es el machine learning?",
            "target_text": "El machine learning es una rama de la inteligencia artificial que permite a las computadoras aprender y mejorar automáticamente a partir de la experiencia sin ser programadas explícitamente. Utiliza algoritmos que identifican patrones en datos para hacer predicciones o decisiones.",
            "quality_score": 0.95,
            "source": "synthetic_technical",
            "timestamp": 1756062674.4658723,
            "domain": "technical",
        },
        {
            "input_text": "¿Cómo funciona una red neuronal?",
            "target_text": "Una red neuronal es un modelo computacional inspirado en el cerebro humano. Consiste en capas de nodos interconectados que procesan información. Cada conexión tiene un peso que se ajusta durante el entrenamiento para minimizar el error en las predicciones.",
            "quality_score": 0.95,
            "source": "synthetic_technical",
            "timestamp": 1756062674.4658723,
            "domain": "technical",
        },
        # Legal
        {
            "input_text": "¿Qué es el derecho constitucional?",
            "target_text": "El derecho constitucional es la rama del derecho público que estudia la organización y funcionamiento del Estado, los derechos fundamentales de las personas y las garantías constitucionales. Se basa en la Constitución como norma suprema del ordenamiento jurídico.",
            "quality_score": 0.95,
            "source": "synthetic_legal",
            "timestamp": 1756062674.4658723,
            "domain": "legal",
        },
        {
            "input_text": "¿Cuáles son los derechos fundamentales?",
            "target_text": "Los derechos fundamentales son aquellos derechos humanos reconocidos y protegidos por la Constitución. Incluyen derechos como la vida, libertad, igualdad, propiedad, educación, salud, trabajo, y otros que garantizan la dignidad humana y el desarrollo integral de la persona.",
            "quality_score": 0.95,
            "source": "synthetic_legal",
            "timestamp": 1756062674.4658723,
            "domain": "legal",
        },
        # Científico
        {
            "input_text": "¿Qué es la teoría de la evolución?",
            "target_text": "La teoría de la evolución propuesta por Charles Darwin explica cómo las especies cambian a lo largo del tiempo mediante el proceso de selección natural. Los individuos con características ventajosas tienen mayor probabilidad de sobrevivir y reproducirse, transmitiendo sus genes a la siguiente generación.",
            "quality_score": 0.95,
            "source": "synthetic_scientific",
            "timestamp": 1756062674.4658723,
            "domain": "scientific",
        },
        {
            "input_text": "¿Cómo funciona la fotosíntesis?",
            "target_text": "La fotosíntesis es el proceso mediante el cual las plantas, algas y algunas bacterias convierten la energía solar en energía química. Utilizan dióxido de carbono y agua para producir glucosa y oxígeno, liberando este último a la atmósfera como subproducto.",
            "quality_score": 0.95,
            "source": "synthetic_scientific",
            "timestamp": 1756062674.4658723,
            "domain": "scientific",
        },
        # Empresarial
        {
            "input_text": "¿Qué es el marketing digital?",
            "target_text": "El marketing digital es el conjunto de estrategias publicitarias y comerciales que se ejecutan en medios y canales de internet. Incluye SEO, SEM, redes sociales, email marketing, content marketing y otras técnicas para promocionar productos o servicios en el entorno digital.",
            "quality_score": 0.95,
            "source": "synthetic_business",
            "timestamp": 1756062674.4658723,
            "domain": "business",
        },
        {
            "input_text": "¿Cómo funciona la economía de mercado?",
            "target_text": "La economía de mercado es un sistema económico donde las decisiones de producción, distribución y consumo están determinadas por la oferta y demanda. Los precios se establecen libremente en el mercado, y la competencia entre empresas regula la eficiencia y calidad de los productos.",
            "quality_score": 0.95,
            "source": "synthetic_business",
            "timestamp": 1756062674.4658723,
            "domain": "business",
        },
    ]

    # Expandir el dataset con más variaciones
    expanded_data = []
    for base_example in synthetic_data:
        expanded_data.append(base_example)

        # Crear variaciones del mismo tema
        variations = _create_variations(base_example)
        expanded_data.extend(variations)

    # Guardar dataset sintético
    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(expanded_data, f, ensure_ascii=False, indent=2)

    print(f"✅ Dataset sintético guardado en: {output_file}")
    print(f"📊 Total de ejemplos creados: {len(expanded_data)}")

    return output_file


def _create_variations(base_example):
    """Crear variaciones de un ejemplo base"""
    variations = []

    # Crear preguntas relacionadas pero diferentes
    if base_example["domain"] == "medical":
        if "COVID-19" in base_example["input_text"]:
            variations.append(
                {
                    "input_text": "¿Cuáles son las medidas de prevención del COVID-19?",
                    "target_text": "Las medidas de prevención incluyen lavado frecuente de manos, uso de mascarilla, distanciamiento social, ventilación de espacios, vacunación y evitar aglomeraciones. Estas medidas reducen significativamente el riesgo de contagio.",
                    "quality_score": 0.95,
                    "source": "synthetic_medical",
                    "timestamp": 1756062674.4658723,
                    "domain": "medical",
                }
            )

    elif base_example["domain"] == "technical":
        if "machine learning" in base_example["input_text"].lower():
            variations.append(
                {
                    "input_text": "¿Cuáles son los tipos principales de machine learning?",
                    "target_text": "Los tipos principales son: aprendizaje supervisado (con datos etiquetados), no supervisado (sin etiquetas), semi-supervisado (mezcla de ambos) y por refuerzo (aprendizaje basado en recompensas). Cada tipo se aplica según el problema específico.",
                    "quality_score": 0.95,
                    "source": "synthetic_technical",
                    "timestamp": 1756062674.4658723,
                    "domain": "technical",
                }
            )

    return variations


def _determine_domain(question, answer):
    """Determinar dominio basado en el contenido"""

    # Palabras clave por dominio
    medical_keywords = [
        "médico",
        "enfermedad",
        "síntoma",
        "tratamiento",
        "paciente",
        "diagnóstico",
        "medicina",
        "salud",
        "covid",
        "hipertensión",
    ]
    technical_keywords = [
        "tecnología",
        "programación",
        "software",
        "hardware",
        "computadora",
        "sistema",
        "algoritmo",
        "machine learning",
        "red neuronal",
    ]
    legal_keywords = [
        "ley",
        "legal",
        "derecho",
        "jurídico",
        "corte",
        "abogado",
        "contrato",
        "norma",
        "constitucional",
    ]
    scientific_keywords = [
        "ciencia",
        "investigación",
        "experimento",
        "laboratorio",
        "método científico",
        "evolución",
        "fotosíntesis",
    ]
    business_keywords = [
        "empresa",
        "negocio",
        "comercial",
        "mercado",
        "economía",
        "finanzas",
        "ventas",
        "marketing",
    ]

    # Combinar pregunta y respuesta para análisis
    text = (question + " " + answer).lower()

    # Contar coincidencias
    scores = {
        "medical": sum(1 for word in medical_keywords if word in text),
        "technical": sum(1 for word in technical_keywords if word in text),
        "legal": sum(1 for word in legal_keywords if word in text),
        "scientific": sum(1 for word in scientific_keywords if word in text),
        "business": sum(1 for word in business_keywords if word in text),
    }

    max_score = max(scores.values())

    # Retornar dominio con mayor puntuación o general si no hay coincidencias
    if max_score > 0:
        return max(scores, key=scores.get)
    else:
        return "general"


if __name__ == "__main__":
    print("🚀 Iniciando descarga de datasets de entrenamiento...")

    datasets_downloaded = []

    # Intentar descargar diferentes datasets
    if mlqa_file:
        datasets_downloaded.append(mlqa_file)

    if xquad_file:
        datasets_downloaded.append(xquad_file)

    if tydiqa_file:
        datasets_downloaded.append(tydiqa_file)

    # Crear dataset sintético como respaldo
    if synthetic_file:
        datasets_downloaded.append(synthetic_file)

    if datasets_downloaded:
        print(f"\n✅ Datasets descargados exitosamente:")
        total_examples = 0

        for dataset_file in datasets_downloaded:
            print(f"  📁 {dataset_file.name}: {file_size:.2f} MB")

            # Contar ejemplos
            with open(dataset_file, "r", encoding="utf-8") as f:
                total_examples += examples_count
                print(f"    📊 Ejemplos: {examples_count}")

        print(f"\n🎉 ¡Descarga completada!")
        print(f"📂 Ubicación: data/training_datasets/")
        print(f"📊 Total de ejemplos disponibles: {total_examples}")
        print(
            f"💡 Los datasets están listos para entrenar tu sistema de aprendizaje continuo"
        )
    else:
        print(
            "❌ No se pudieron descargar datasets externos, pero se creó el dataset sintético"
        )
