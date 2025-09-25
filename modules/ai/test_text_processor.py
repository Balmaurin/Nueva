#!/usr/bin/env python3
"""
Script de prueba para el procesador de texto
"""

import sys
import os

sys.path.append(os.path.join(os.path.dirname(__file__), "modules"))

from modules.ai.text_processor import TextProcessor
import json


def test_text_processor():
    """Prueba el procesador de texto"""
    print("🧪 Probando procesador de texto...")

    # Crear instancia del procesador
    processor = TextProcessor(language="spanish")

    # Texto de prueba
    test_text = """
    Hola mundo! Este es un texto de prueba para verificar el funcionamiento
    del procesador de texto. El sistema Shaili AI es increíble y muy útil
    para el procesamiento de lenguaje natural. Juan Pérez trabaja en la
    empresa TechCorp Inc. y vive en Madrid, España.
    """

    print(f"📝 Texto de prueba:\n{test_text.strip()}")

    # Probar limpieza de texto
    print("\n🔧 Limpieza de texto:")
    clean_text = processor.clean_text(test_text)
    print(f"Texto limpio: {clean_text}")

    # Probar tokenización
    print("\n🔤 Tokenización:")
    tokens = processor.tokenize_text(clean_text)
    print(f"Tokens: {tokens}")

    # Probar remoción de stop words
    print("\n🚫 Remoción de stop words:")
    filtered_tokens = processor.remove_stop_words(tokens)
    print(f"Tokens filtrados: {filtered_tokens}")

    # Probar análisis completo
    print("\n📊 Análisis completo:")
    analysis = processor.analyze_text(test_text)
    print(f"Palabras: {analysis.word_count}")
    print(f"Oraciones: {analysis.sentence_count}")
    print(f"Longitud promedio de oración: {analysis.avg_sentence_length:.2f}")
    print(f"Palabras únicas: {analysis.unique_words}")
    print(f"Diversidad de vocabulario: {analysis.vocabulary_diversity:.3f}")
    print(f"Sentimiento: {analysis.sentiment_score:.3f}")
    print(f"Frases clave: {analysis.key_phrases}")
    print(f"Entidades: {len(analysis.entities)}")

    # Probar preprocesamiento para LLM
    print("\n🤖 Preprocesamiento para LLM:")
    preprocessed = processor.preprocess_for_llm(test_text)
    print(f"Texto preprocesado: {preprocessed}")

    # Probar estadísticas
    print("\n📈 Estadísticas:")
    stats = processor.get_text_stats(test_text)
    print(json.dumps(stats, indent=2, ensure_ascii=False))

    print("\n✅ Pruebas completadas exitosamente!")


if __name__ == "__main__":
    test_text_processor()
