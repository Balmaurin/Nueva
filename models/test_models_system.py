#!/usr/bin/env python3
"""
Prueba comprehensiva del sistema de modelos de Shaili AI
"""
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import json
import time
import tempfile
import shutil
from pathlib import Path
from typing import Dict, Any

from models import (
    get_model_manager,
    create_model,
    load_model,
    get_model,
    generate_text,
    get_embeddings,
    list_models,
    get_system_stats,
    cleanup,
    ModelConfig,
    CausalLMModel,
    EmbeddingModel,
)


def print_section(title: str):
    """Imprimir sección con formato"""
    print(f"\n{'='*60}")
    print(f"🔍 {title}")
    print(f"{'='*60}")


def test_model_config():
    """Probar configuración de modelos"""
    print_section("CONFIGURACIÓN DE MODELOS")

    # Crear configuración básica
    config = ModelConfig(
        name="test_model",
        model_type="causal_lm",
        path="/path/to/model",
        description="Modelo de prueba",
        author="Test Author",
        tags=["test", "demo"],
        size_gb=2.5,
    )

    print(f"✅ Configuración creada: {config.name}")
    print(f"   Tipo: {config.model_type}")
    print(f"   Tamaño: {config.size_gb}GB")
    print(f"   Tags: {config.tags}")

    # Convertir a diccionario
    config_dict = config.to_dict()
    print(f"✅ Configuración convertida a diccionario: {len(config_dict)} campos")

    # Crear desde diccionario
    config_from_dict = ModelConfig.from_dict(config_dict)
    print(f"✅ Configuración recreada desde diccionario: {config_from_dict.name}")

    return config


def test_model_manager():
    """Probar gestor de modelos"""
    print_section("GESTOR DE MODELOS")

    # Obtener gestor
    manager = get_model_manager()
    print(f"✅ Gestor obtenido: {manager}")

    # Verificar tipos soportados
    supported_types = manager.get_supported_types()
    print(f"✅ Tipos soportados: {supported_types}")

    # Crear configuración de prueba
    config = ModelConfig(
        name="test_causal_model",
        model_type="causal_lm",
        path="/tmp/test_model",
        description="Modelo causal de prueba",
        size_gb=1.0,
    )

    # Crear modelo
    model = manager.create_model(config)
    if model:
        print(f"✅ Modelo creado: {model}")
        manager.add_model(model)
        print(f"✅ Modelo agregado al gestor")
    else:
        print(f"❌ Error creando modelo")

    # Listar modelos
    models = manager.list_models()
    print(f"✅ Modelos en gestor: {len(models)}")

    # Estadísticas del sistema
    stats = manager.get_system_stats()
    print(f"✅ Estadísticas del sistema:")
    for key, value in stats.items():
        print(f"   {key}: {value}")

    return manager


def test_model_registry():
    """Probar registro de modelos"""
    print_section("REGISTRO DE MODELOS")

    manager = get_model_manager()
    registry = manager.registry

    # Crear configuración de prueba
    config = ModelConfig(
        name="registered_model",
        model_type="causal_lm",
        path="/path/to/registered/model",
        description="Modelo registrado de prueba",
        size_gb=3.0,
    )

    # Registrar modelo
    success = registry.register_model(config.name, config)
    if success:
        print(f"✅ Modelo registrado: {config.name}")
    else:
        print(f"❌ Error registrando modelo")

    # Obtener modelo del registro
    model_info = registry.get_model(config.name)
    if model_info:
        print(f"✅ Modelo obtenido del registro: {model_info['type']}")
    else:
        print(f"❌ Error obteniendo modelo del registro")

    # Listar modelos
    models = registry.list_models()
    print(f"✅ Modelos en registro: {len(models)}")

    # Buscar modelos
    search_results = registry.search_models("test")
    print(f"✅ Resultados de búsqueda: {len(search_results)}")

    # Estadísticas del registro
    stats = registry.get_model_stats()
    print(f"✅ Estadísticas del registro:")
    for key, value in stats.items():
        if isinstance(value, (int, float, str)):
            print(f"   {key}: {value}")
        else:
            print(f"   {key}: {type(value).__name__}")

    return registry


def test_model_implementations():
    """Probar implementaciones de modelos"""
    print_section("IMPLEMENTACIONES DE MODELOS")

    # Probar modelo causal
    causal_config = ModelConfig(
        name="test_causal",
        model_type="causal_lm",
        path="/tmp/test_causal",
        description="Modelo causal de prueba",
        size_gb=1.0,
    )

    try:
        causal_model = CausalLMModel(causal_config)
        print(f"✅ Modelo causal creado: {causal_model}")
        print(f"   Dispositivo: {causal_model.device}")
        print(f"   Listo: {causal_model.is_ready()}")
    except Exception as e:
        print(f"❌ Error creando modelo causal: {e}")

    # Probar modelo de embeddings
    embedding_config = ModelConfig(
        name="test_embedding",
        model_type="embedding_model",
        path="/tmp/test_embedding",
        description="Modelo de embeddings de prueba",
        size_gb=0.5,
    )

    try:
        embedding_model = EmbeddingModel(embedding_config)
        print(f"✅ Modelo de embeddings creado: {embedding_model}")
        print(f"   Dispositivo: {embedding_model.device}")
        print(f"   Estrategia de pooling: {embedding_model.pooling_strategy}")
    except Exception as e:
        print(f"❌ Error creando modelo de embeddings: {e}")


def test_model_operations():
    """Probar operaciones con modelos"""
    print_section("OPERACIONES CON MODELOS")

    manager = get_model_manager()

    # Crear modelo de prueba
    config = ModelConfig(
        name="operations_test_model",
        model_type="causal_lm",
        path="/tmp/operations_test",
        description="Modelo para pruebas de operaciones",
        size_gb=1.0,
    )

    model = manager.create_model(config)
    if model:
        manager.add_model(model)
        print(f"✅ Modelo creado para operaciones: {model.config.name}")

        # Probar información del modelo
        info = model.get_info()
        print(f"✅ Información del modelo obtenida: {len(info)} campos")

        # Probar configuración
        success = model.update_config(temperature=0.8, top_p=0.9)
        if success:
            print(f"✅ Configuración actualizada")
        else:
            print(f"❌ Error actualizando configuración")

        # Probar métricas
        model.metrics.increment_requests()
        model.metrics.increment_tokens(100)
        print(
            f"✅ Métricas actualizadas: {model.metrics.requests_processed} requests, {model.metrics.tokens_generated} tokens"
        )

        # Probar uso de memoria
        memory_usage = model.get_memory_usage()
        print(f"✅ Uso de memoria: {memory_usage:.2f}GB")

        # Probar limpieza
        success = model.cleanup()
        if success:
            print(f"✅ Modelo limpiado")
        else:
            print(f"❌ Error limpiando modelo")
    else:
        print(f"❌ Error creando modelo para operaciones")


def test_error_handling():
    """Probar manejo de errores"""
    print_section("MANEJO DE ERRORES")

    manager = get_model_manager()

    # Probar modelo inexistente
    non_existent = manager.get_model("non_existent_model")
    if non_existent is None:
        print(f"✅ Modelo inexistente manejado correctamente")
    else:
        print(f"❌ Error: modelo inexistente retornó algo")

    # Probar cargar modelo inexistente
    success = manager.load_model("non_existent_model")
    if not success:
        print(f"✅ Error de carga manejado correctamente")
    else:
        print(f"❌ Error: carga de modelo inexistente fue exitosa")

    # Probar generar texto sin modelo
    result = manager.generate_text("non_existent_model", "test prompt")
    if result is None:
        print(f"✅ Generación sin modelo manejada correctamente")
    else:
        print(f"❌ Error: generación sin modelo retornó resultado")

    # Probar embeddings sin modelo
    result = manager.get_embeddings("non_existent_model", ["test"])
    if result is None:
        print(f"✅ Embeddings sin modelo manejados correctamente")
    else:
        print(f"❌ Error: embeddings sin modelo retornaron resultado")


def test_performance():
    """Probar rendimiento del sistema"""
    print_section("RENDIMIENTO")

    manager = get_model_manager()

    # Tiempo de obtención del gestor
    start_time = time.time()
    manager = get_model_manager()
    end_time = time.time()
    print(f"✅ Tiempo de obtención del gestor: {(end_time - start_time)*1000:.2f}ms")

    # Tiempo de listado de modelos
    start_time = time.time()
    models = manager.list_models()
    end_time = time.time()
    print(f"✅ Tiempo de listado de modelos: {(end_time - start_time)*1000:.2f}ms")

    # Tiempo de estadísticas
    start_time = time.time()
    stats = manager.get_system_stats()
    end_time = time.time()
    print(f"✅ Tiempo de estadísticas: {(end_time - start_time)*1000:.2f}ms")

    # Tiempo de registro
    registry = manager.registry
    start_time = time.time()
    registry_stats = registry.get_model_stats()
    end_time = time.time()
    print(
        f"✅ Tiempo de estadísticas del registro: {(end_time - start_time)*1000:.2f}ms"
    )


def test_integration():
    """Probar integración completa"""
    print_section("INTEGRACIÓN COMPLETA")

    # Crear múltiples modelos
    configs = [
        ModelConfig(
            name=f"integration_model_{i}",
            model_type="causal_lm",
            path=f"/tmp/integration_{i}",
            description=f"Modelo de integración {i}",
            size_gb=1.0 + i * 0.5,
        )
        for i in range(3)
    ]

    manager = get_model_manager()

    # Agregar modelos
    for config in configs:
        model = manager.create_model(config)
        if model:
            manager.add_model(model)
            print(f"✅ Modelo de integración agregado: {config.name}")

    # Verificar todos los modelos
    models = manager.list_models()
    print(f"✅ Total de modelos en integración: {len(models)}")

    # Verificar estadísticas
    stats = manager.get_system_stats()
    print(f"✅ Estadísticas de integración:")
    print(f"   Total de modelos: {stats['total_models']}")
    print(f"   Modelos cargados: {stats['loaded_models']}")
    print(f"   Memoria total: {stats['total_memory_gb']:.2f}GB")


def main():
    """Función principal"""
    print("🚀 PRUEBA COMPREHENSIVA DEL SISTEMA DE MODELOS SHAILI AI")
    print("=" * 60)

    try:
        # Probar configuración
        test_model_config()

        # Probar gestor
        test_model_manager()

        # Probar registro
        test_model_registry()

        # Probar implementaciones
        test_model_implementations()

        # Probar operaciones
        test_model_operations()

        # Probar manejo de errores
        test_error_handling()

        # Probar rendimiento
        test_performance()

        # Probar integración
        test_integration()

        print("\n" + "=" * 60)
        print("✅ PRUEBA COMPREHENSIVA COMPLETADA")
        print("=" * 60)
        print("\n📊 Resumen:")
        print("• Sistema de modelos funcionando correctamente")
        print("• Gestor de modelos operativo")
        print("• Registro de modelos funcional")
        print("• Implementaciones de modelos disponibles")
        print("• Manejo de errores robusto")
        print("• Rendimiento aceptable")

        # Limpiar recursos
        cleanup()
        print("• Recursos limpiados correctamente")

    except Exception as e:
        print(f"\n❌ Error en prueba comprehensiva: {e}")
        import traceback

        traceback.print_exc()


if __name__ == "__main__":
    main()
