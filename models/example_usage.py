#!/usr/bin/env python3
"""
Ejemplo de Uso del Sistema de Modelos LLM
=========================================

Este script demuestra cómo usar el nuevo sistema de modelos organizado.
"""

import logging
import sys
import os

# Agregar el directorio raíz al path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from models.core.model_manager import ModelManager
from models.config.model_configs import get_model_config, CausalLMConfig
from models.branches.branch_manager import BranchManager
from models.utils.performance_monitor import PerformanceMonitor
from models.utils.memory_utils import MemoryManager


def setup_logging():
    """Configurar logging"""
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    )


def example_basic_usage():
    """Ejemplo básico de uso del sistema de modelos"""
    print("🚀 Ejemplo Básico de Uso del Sistema de Modelos")
    print("=" * 50)

    # Inicializar gestor de modelos
    manager = ModelManager()

    try:
        # Cargar modelo principal
        print("📥 Cargando modelo principal...")
        model = manager.load_model("shaili-personal-model")

        if model:
            print("✅ Modelo cargado exitosamente")

            # Generar texto
            prompt = "Explica brevemente qué es la inteligencia artificial:"
            print(f"\n🤖 Generando respuesta para: '{prompt}'")

            response = model.generate(prompt, max_new_tokens=100)
            print(f"📝 Respuesta: {response}")

            # Obtener información del modelo
            info = model.get_model_info()
            print(f"\n📊 Información del modelo:")
            print(f"   - Nombre: {info.name}")
            print(f"   - Dispositivo: {info.device}")
            print(f"   - Memoria: {info.memory_usage:.2f} GB")
            print(f"   - Parámetros: {model.get_model_parameters():,}")

        else:
            print("❌ Error cargando modelo")

    except Exception as e:
        print(f"❌ Error: {e}")

    finally:
        # Limpiar recursos
        manager.shutdown()


def example_branch_management():
    """Ejemplo de gestión de ramas"""
    print("\n🌿 Ejemplo de Gestión de Ramas")
    print("=" * 50)

    try:
        # Inicializar gestor de ramas
        branch_manager = BranchManager()

        # Obtener dominios disponibles
        domains = branch_manager.get_available_domains()
        print(f"📋 Dominios disponibles: {len(domains)}")

        # Mostrar algunos dominios
        for i, domain in enumerate(domains[:5]):
            print(f"   {i+1}. {domain}")

        if len(domains) > 5:
            print(f"   ... y {len(domains) - 5} más")

        # Verificar estado de una rama específica
        medical_domain = "Medicina y Salud"
        if medical_domain in domains:
            print(f"\n🏥 Verificando estado de '{medical_domain}'...")
            status = branch_manager.get_branch_status(medical_domain)
            print(f"   - Estado: {status.get('status', 'unknown')}")
            print(f"   - Adapter: {'✅' if status.get('has_adapter') else '❌'}")

    except Exception as e:
        print(f"❌ Error: {e}")


def example_performance_monitoring():
    """Ejemplo de monitoreo de rendimiento"""
    print("\n📈 Ejemplo de Monitoreo de Rendimiento")
    print("=" * 50)

    try:
        # Inicializar monitor de rendimiento
        monitor = PerformanceMonitor()

        # Simular algunas operaciones
        print("🔄 Simulando operaciones...")

        with monitor.track("model_loading"):
            import time

            time.sleep(1)  # Simular carga de modelo

        with monitor.track("text_generation"):
            time.sleep(0.5)  # Simular generación

        with monitor.track("embedding_generation"):
            time.sleep(0.3)  # Simular embeddings

        # Obtener estadísticas
        stats = monitor.get_performance_summary()
        print(f"📊 Estadísticas de rendimiento:")
        print(f"   - Operaciones totales: {stats['total_operations']}")
        print(f"   - Tiempo promedio: {stats['avg_time']:.2f}s")
        print(f"   - Alertas: {len(stats['alerts'])}")

        # Mostrar operaciones más lentas
        if stats["top_operations"]:
            print(f"\n🐌 Operaciones más lentas:")
            for op in stats["top_operations"][:3]:
                print(
                    f"   - {op['operation']}: {op['avg_time']:.2f}s ({op['count']} veces)"
                )

    except Exception as e:
        print(f"❌ Error: {e}")


def example_memory_management():
    """Ejemplo de gestión de memoria"""
    print("\n💾 Ejemplo de Gestión de Memoria")
    print("=" * 50)

    try:
        # Inicializar gestor de memoria
        memory_manager = MemoryManager()

        # Obtener estadísticas de memoria
        summary = memory_manager.get_memory_summary()

        print(f"📊 Resumen de memoria del sistema:")
        system_memory = summary["system_memory"]
        print(f"   - Total: {system_memory['total_gb']:.1f} GB")
        print(f"   - Usado: {system_memory['used_gb']:.1f} GB")
        print(f"   - Disponible: {system_memory['available_gb']:.1f} GB")
        print(f"   - Porcentaje usado: {system_memory['percentage_used']:.1%}")

        # Verificar alertas
        alerts = summary["alerts"]
        if alerts:
            print(f"\n⚠️  Alertas de memoria:")
            for alert in alerts:
                print(f"   - {alert['message']}")
        else:
            print(f"\n✅ Sin alertas de memoria")

        # Obtener tendencias
        trends = memory_manager.get_memory_trends()
        print(f"\n📈 Tendencia de memoria: {trends['trend']}")
        if trends["change_percentage"] != 0:
            print(f"   - Cambio: {trends['change_percentage']:+.1f}%")

    except Exception as e:
        print(f"❌ Error: {e}")


def example_model_validation():
    """Ejemplo de validación de modelos"""
    print("\n🔍 Ejemplo de Validación de Modelos")
    print("=" * 50)

    try:
        # Inicializar gestor de modelos
        manager = ModelManager()

        # Validar modelo
        print("🔍 Validando modelo 'shaili-personal-model'...")
        validation = manager.validate_model("shaili-personal-model")

        print(f"📋 Resultado de validación:")
        print(f"   - Válido: {'✅' if validation['overall_valid'] else '❌'}")

        # Detalles de validación de ruta
        path_validation = validation["path_validation"]
        print(f"   - Ruta existe: {'✅' if path_validation['exists'] else '❌'}")
        print(
            f"   - Tiene configuración: {'✅' if path_validation['has_config'] else '❌'}"
        )
        print(
            f"   - Tiene archivos de modelo: {'✅' if path_validation['has_model_files'] else '❌'}"
        )

        # Detalles de compatibilidad
        compatibility = validation["compatibility"]
        print(
            f"   - Dispositivo soportado: {'✅' if compatibility['device_supported'] else '❌'}"
        )
        print(
            f"   - Memoria suficiente: {'✅' if compatibility['memory_sufficient'] else '❌'}"
        )
        print(
            f"   - Dependencias cumplidas: {'✅' if compatibility['dependencies_met'] else '❌'}"
        )

        # Mostrar errores si los hay
        if path_validation["errors"]:
            print(f"\n❌ Errores de ruta:")
            for error in path_validation["errors"]:
                print(f"   - {error}")

        if compatibility["errors"]:
            print(f"\n❌ Errores de compatibilidad:")
            for error in compatibility["errors"]:
                print(f"   - {error}")

    except Exception as e:
        print(f"❌ Error: {e}")


def main():
    """Función principal"""
    print("🎯 Sistema de Modelos LLM - Ejemplos de Uso")
    print("=" * 60)

    # Configurar logging
    setup_logging()

    # Ejecutar ejemplos
    example_basic_usage()
    example_branch_management()
    example_performance_monitoring()
    example_memory_management()
    example_model_validation()

    print("\n🎉 ¡Ejemplos completados!")
    print("=" * 60)


if __name__ == "__main__":
    main()
