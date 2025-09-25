#!/usr/bin/env python3
"""
Script de Prueba del Orquestador
================================

Prueba completa del sistema de orquestación
"""

import os
import sys
import json
import time
import requests
from datetime import datetime

# Agregar el directorio raíz al path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


def test_orchestrator_direct():
    """Probar orquestador directamente"""
    print("🧪 Probando orquestador directamente...")

    try:
        from modules.orchestrator.main_orchestrator import MainOrchestrator

        # Crear orquestador
        orchestrator = MainOrchestrator()
        print("✅ Orquestador creado")

        # Consultas de prueba
        test_queries = [
            "¿Qué es la inteligencia artificial?",
            "Explica el teorema de Pitágoras",
            "¿Cómo funciona la fotosíntesis?",
            "Cuéntame sobre la historia de Roma",
            "¿Cuál es la capital de Francia?",
        ]

        results = []

        for i, query in enumerate(test_queries, 1):
            print(f"\n📝 Consulta {i}: {query}")

            start_time = time.time()
            response = orchestrator.process_query(query)
            response_time = time.time() - start_time

            print(f"⏱️  Tiempo de respuesta: {response_time:.2f}s")
            print(f"🏷️  Dominio: {response.get('domain', 'N/A')}")
            print(f"🛣️  Ruta: {response.get('route_type', 'N/A')}")
            print(f"📄 Respuesta: {response.get('text', 'N/A')[:100]}...")

            results.append(
                {
                    "query": query,
                    "response_time": response_time,
                    "domain": response.get("domain"),
                    "route_type": response.get("route_type"),
                    "success": "text" in response,
                }
            )

        # Mostrar estadísticas
        successful = sum(1 for r in results if r["success"])
        avg_time = sum(r["response_time"] for r in results) / len(results)

        print(f"\n📊 Estadísticas:")
        print(f"   ✅ Exitosas: {successful}/{len(results)}")
        print(f"   ⏱️  Tiempo promedio: {avg_time:.2f}s")

        return successful == len(results)

    except Exception as e:
        print(f"❌ Error en prueba directa: {e}")
        return False


def test_orchestrator_api():
    """Probar orquestador a través de API"""
    print("\n🌐 Probando orquestador a través de API...")

    base_url = "http://127.0.0.1:8000/api/orchestrator"

    try:
        # Probar health check
        print("🔍 Health check...")
        response = requests.get(f"{base_url}/health", timeout=10)

        if response.status_code == 200:
            print("✅ Health check exitoso")
            health_data = response.json()
            print(
                f"📊 Estado: {health_data.get('data', {}).get('orchestrator_status')}"
            )
        else:
            print(f"❌ Health check falló: {response.status_code}")
            return False

        # Probar procesamiento de consulta
        print("\n📝 Procesando consulta...")
        test_query = {
            "query": "¿Qué es la inteligencia artificial?",
            "user_context": {"language": "es"},
        }

        response = requests.post(f"{base_url}/query", json=test_query, timeout=30)

        if response.status_code == 200:
            print("✅ Consulta procesada exitosamente")
            query_data = response.json()
            print(
                f"📄 Respuesta: {query_data.get('data', {}).get('text', '')[:100]}..."
            )
        else:
            print(f"❌ Error procesando consulta: {response.status_code}")
            return False

        # Probar estado del sistema
        print("\n📊 Estado del sistema...")
        response = requests.get(f"{base_url}/status", timeout=10)

        if response.status_code == 200:
            print("✅ Estado del sistema obtenido")
            status_data = response.json()
            metrics = status_data.get("data", {}).get("metrics", {})
            print(f"📈 Total requests: {metrics.get('total_requests', 0)}")
        else:
            print(f"❌ Error obteniendo estado: {response.status_code}")
            return False

        # Probar métricas
        print("\n📈 Métricas...")
        response = requests.get(f"{base_url}/metrics", timeout=10)

        if response.status_code == 200:
            print("✅ Métricas obtenidas")
            metrics_data = response.json()
            performance = metrics_data.get("data", {}).get("performance", {})
            print(f"🎯 Tasa de éxito: {performance.get('success_rate', 0):.2%}")
        else:
            print(f"❌ Error obteniendo métricas: {response.status_code}")
            return False

        return True

    except requests.exceptions.ConnectionError:
        print("❌ No se pudo conectar al servidor API")
        print(
            "💡 Asegúrate de que el servidor backend esté ejecutándose en puerto 8000"
        )
        return False
    except Exception as e:
        print(f"❌ Error en prueba de API: {e}")
        return False


def test_branch_management():
    """Probar gestión de ramas"""
    print("\n🌿 Probando gestión de ramas...")

    try:
        from branches.branch_manager import BranchManager

        # Crear gestor de ramas
        branch_manager = BranchManager()
        print("✅ Gestor de ramas creado")

        # Obtener dominios disponibles
        domains = branch_manager.get_available_domains()
        print(f"📚 Dominios disponibles: {len(domains)}")

        # Mostrar algunos dominios
        for i, domain in enumerate(domains[:5], 1):
            print(f"   {i}. {domain}")

        if len(domains) > 5:
            print(f"   ... y {len(domains) - 5} más")

        # Probar estado de una rama específica
        if domains:
            test_domain = domains[0]
            status = branch_manager.get_branch_status(test_domain)
            print(f"\n📊 Estado de '{test_domain}':")
            print(f"   🏷️  Nombre: {status.get('branch_name')}")
            print(f"   🔧 Adapter existe: {status.get('adapter_exists')}")
            print(f"   🌱 Micro-ramas: {len(status.get('micro_branches', []))}")

        return True

    except Exception as e:
        print(f"❌ Error probando gestión de ramas: {e}")
        return False


def test_adapter_policy():
    """Probar política de adapters"""
    print("\n⚙️ Probando política de adapters...")

    try:
        from branches.adapter_policy import AdapterUpdatePolicy

        # Crear política de adapters
        policy = AdapterUpdatePolicy()
        print("✅ Política de adapters creada")

        # Probar gestión de adapters
        test_metrics = {"accuracy": 0.85, "response_time": 1.2, "memory_usage": 0.6}

        result = policy.manage_domain_adapters("Matemáticas", test_metrics)
        print("✅ Gestión de adapters probada")

        # Probar optimización de caché
        optimization = policy.optimize_cache()
        print("✅ Optimización de caché probada")

        # Obtener métricas de rendimiento
        metrics = policy.get_all_performance_metrics()
        print(f"📊 Métricas de rendimiento: {len(metrics)} dominios")

        return True

    except Exception as e:
        print(f"❌ Error probando política de adapters: {e}")
        return False


def generate_test_report(results):
    """Generar reporte de pruebas"""
    print("\n📊 Generando reporte de pruebas...")

    report = {
        "timestamp": datetime.now().isoformat(),
        "tests": results,
        "summary": {
            "total_tests": len(results),
            "passed_tests": sum(results.values()),
            "success_rate": sum(results.values()) / len(results) if results else 0,
        },
    }

    # Guardar reporte
    report_path = "logs/orchestrator_test_report.json"
    os.makedirs(os.path.dirname(report_path), exist_ok=True)

    with open(report_path, "w", encoding="utf-8") as f:
        json.dump(report, f, indent=2, ensure_ascii=False)

    print(f"📄 Reporte guardado en: {report_path}")

    return report


def main():
    """Función principal"""
    print("🧪 Pruebas del Orquestador de Sheily-AI")
    print("=" * 50)

    results = {}

    # Ejecutar pruebas
    tests = [
        ("Orquestador Directo", test_orchestrator_direct),
        ("Gestión de Ramas", test_branch_management),
        ("Política de Adapters", test_adapter_policy),
        ("API del Orquestador", test_orchestrator_api),
    ]

    for test_name, test_func in tests:
        print(f"\n{'='*20} {test_name} {'='*20}")
        try:
            results[test_name] = test_func()
            status = "✅ PASÓ" if results[test_name] else "❌ FALLÓ"
            print(f"\n{status} - {test_name}")
        except Exception as e:
            print(f"❌ ERROR - {test_name}: {e}")
            results[test_name] = False

    # Generar reporte
    report = generate_test_report(results)

    # Mostrar resumen
    print(f"\n{'='*50}")
    print("📊 RESUMEN DE PRUEBAS")
    print(f"{'='*50}")

    for test_name, passed in results.items():
        status = "✅ PASÓ" if passed else "❌ FALLÓ"
        print(f"{status} - {test_name}")

    summary = report["summary"]
    print(
        f"\n🎯 Total: {summary['passed_tests']}/{summary['total_tests']} pruebas exitosas"
    )
    print(f"📈 Tasa de éxito: {summary['success_rate']:.1%}")

    if summary["success_rate"] >= 0.75:
        print("\n🎉 ¡El orquestador está funcionando correctamente!")
    else:
        print("\n⚠️  Algunas pruebas fallaron. Revisa los logs para más detalles.")

    return summary["success_rate"] >= 0.75


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
