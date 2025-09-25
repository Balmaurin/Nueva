import sys
import os

# Añadir el directorio backend al path
sys.path.append(os.path.join(os.path.dirname(__file__), "..", "backend"))


def test_llm_client():
    """Probar el cliente LLM local"""
    print("\n🔍 Probando cliente LLM...")

    try:
        from llm_client import get_llm_client

        client = get_llm_client()
        print(f"✅ Cliente LLM inicializado - Modelo: {client.model_name}")

        health = client.health_check()
        print(f"📊 Estado del servicio: {health['status']}")

        if health["status"] != "healthy":
            print(f"❌ Servicio no saludable: {health}")
            return False

        messages = [{"role": "user", "content": "Hola, ¿cómo estás?"}]
        response = client.llm_chat(messages, max_tokens=50)
        print(f"✅ Chat funcionando - Respuesta: {response[:100]}...")

        return True
    except Exception as exc:
        print(f"❌ Error en cliente LLM: {exc}")
        return False


def test_orchestrator_integration():
    """Probar integración con el orquestador"""
    print("\n🔍 Probando integración con orquestador...")

    try:
        sys.path.append(os.path.join(os.path.dirname(__file__), ".."))

        from modules.orchestrator.main_orchestrator import MainOrchestrator

        orchestrator = MainOrchestrator()
        print("✅ Orquestador inicializado")

        llm_status = orchestrator.get_llm_status()
        print(f"📊 Estado LLM en orquestador: {llm_status['status']}")

        if llm_status["status"] != "healthy":
            print(f"❌ LLM no disponible en orquestador: {llm_status}")
            return False

        response = orchestrator.process_query("¿Qué es la inteligencia artificial?")
        print(f"✅ Consulta procesada - Fuente: {response.get('source', 'unknown')}")
        print(f"📝 Respuesta: {response.get('text', '')[:100]}...")

        return True
    except Exception as exc:
        print(f"❌ Error en integración orquestador: {exc}")
        return False


def test_pipeline_enhanced():
    """Probar pipeline mejorado draft → critic → fix"""
    print("\n🔍 Probando pipeline mejorado...")

    try:
        from llm_client import get_llm_client

        client = get_llm_client()

        result = client.process_pipeline(
            query="Dame un plan de seguridad informática básico",
            context="Para una pequeña empresa",
        )

        print("✅ Pipeline completado")
        print(f"⏱️ Tiempo de procesamiento: {result['processing_time']:.2f}s")
        print(f"📝 Borrador: {result['draft'][:100]}...")
        print(f"🔍 Crítica: {result['critique'][:100]}...")
        print(f"✨ Respuesta final: {result['final'][:100]}...")

        return True

    except Exception as exc:
        print(f"❌ Error en pipeline mejorado: {exc}")
        return False


def main():
    """Función principal de pruebas"""
    print("🚀 Iniciando pruebas de integración LLM SHEILY")
    print("=" * 50)

    tests = [
        ("Cliente LLM", test_llm_client),
        ("Integración Orquestador", test_orchestrator_integration),
        ("Pipeline Mejorado", test_pipeline_enhanced),
    ]

    results = []

    for test_name, test_func in tests:
        print(f"\n{'='*20} {test_name} {'='*20}")
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as exc:
            print(f"❌ Error inesperado en {test_name}: {exc}")
            results.append((test_name, False))

    print("\n" + "=" * 50)
    print("📊 RESUMEN DE PRUEBAS")
    print("=" * 50)

    passed = 0
    total = len(results)

    for test_name, result in results:
        status = "✅ PASÓ" if result else "❌ FALLÓ"
        print(f"{test_name:.<30} {status}")
        if result:
            passed += 1

    print(f"\nResultado: {passed}/{total} pruebas pasaron")

    if passed == total:
        print("🎉 ¡Todas las pruebas pasaron! Sistema LLM listo.")
        return 0

    print("⚠️ Algunas pruebas fallaron. Revisar configuración.")
    return 1


if __name__ == "__main__":
    sys.exit(main())
