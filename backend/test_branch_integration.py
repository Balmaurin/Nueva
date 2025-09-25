#!/usr/bin/env python3
"""
Script de Prueba para Integración de Ramas
==========================================

Prueba el sistema de ramas integrado con Llama 3.2
"""

import requests
import json
import time
from typing import List, Dict


class BranchIntegrationTester:
    """Tester para el sistema de ramas integrado"""

    def __init__(self, base_url: str = "http://127.0.0.1:8005"):
        self.base_url = base_url
        self.test_results = []

    def test_system_status(self) -> bool:
        """Probar estado del sistema"""
        print("🔍 Probando estado del sistema...")
        try:
            response = requests.get(f"{self.base_url}/system/status")
            if response.status_code == 200:
                status = response.json()
                print(f"✅ Sistema disponible: {status}")
                return True
            else:
                print(f"❌ Error en estado del sistema: {response.status_code}")
                return False
        except Exception as e:
            print(f"❌ Error conectando al sistema: {e}")
            return False

    def test_available_domains(self) -> List[str]:
        """Probar dominios disponibles"""
        print("🌿 Probando dominios disponibles...")
        try:
            response = requests.get(f"{self.base_url}/system/domains")
            if response.status_code == 200:
                data = response.json()
                domains = data.get("domains", [])
                print(f"✅ Dominios disponibles: {len(domains)}")
                for domain in domains[:5]:  # Mostrar solo los primeros 5
                    print(f"   - {domain}")
                return domains
            else:
                print(f"❌ Error obteniendo dominios: {response.status_code}")
                return []
        except Exception as e:
            print(f"❌ Error: {e}")
            return []

    def test_chat_query(self, query: str, expected_domain: str = None) -> Dict:
        """Probar consulta de chat"""
        print(f"💬 Probando consulta: {query[:50]}...")

        try:
            payload = {"messages": [{"role": "user", "content": query}]}

            start_time = time.time()
            response = requests.post(f"{self.base_url}/chat", json=payload)
            end_time = time.time()

            if response.status_code == 200:
                result = response.json()

                # Analizar resultado
                domain = result.get("domain", "unknown")
                confidence = result.get("domain_confidence", 0.0)
                method = result.get("processing_method", "unknown")
                enhanced = result.get("system_enhanced", False)
                response_text = result.get("response", "")

                print(f"✅ Respuesta recibida:")
                print(
                    f"   🎯 Dominio detectado: {domain} (confianza: {confidence:.2f})"
                )
                print(f"   🛣️ Método de procesamiento: {method}")
                print(f"   🚀 Sistema mejorado: {enhanced}")
                print(f"   ⏱️ Tiempo total: {end_time - start_time:.2f}s")
                print(f"   📝 Respuesta: {response_text[:100]}...")

                # Verificar si el dominio esperado coincide
                if expected_domain and domain != expected_domain:
                    print(
                        f"⚠️ Advertencia: Dominio esperado '{expected_domain}' pero detectado '{domain}'"
                    )

                return {
                    "success": True,
                    "domain": domain,
                    "confidence": confidence,
                    "method": method,
                    "enhanced": enhanced,
                    "response_length": len(response_text),
                    "response_time": end_time - start_time,
                }
            else:
                print(f"❌ Error en consulta: {response.status_code}")
                print(f"   Respuesta: {response.text}")
                return {"success": False, "error": response.text}

        except Exception as e:
            print(f"❌ Error en consulta: {e}")
            return {"success": False, "error": str(e)}

    def run_comprehensive_test(self):
        """Ejecutar prueba completa del sistema"""
        print("🚀 INICIANDO PRUEBA COMPLETA DEL SISTEMA DE RAMAS")
        print("=" * 60)

        # 1. Probar estado del sistema
        if not self.test_system_status():
            print("❌ Sistema no disponible, abortando pruebas")
            return

        print()

        # 2. Probar dominios disponibles
        domains = self.test_available_domains()
        print()

        # 3. Probar consultas de diferentes dominios
        test_queries = [
            {
                "query": "¿Cómo funciona la diabetes tipo 2?",
                "expected_domain": "medicina_y_salud",
                "description": "Consulta médica",
            },
            {
                "query": "¿Cómo implementar un algoritmo de ordenamiento rápido?",
                "expected_domain": "computación_y_programación",
                "description": "Consulta de programación",
            },
            {
                "query": "¿Qué es la derivada de x^2?",
                "expected_domain": "matemáticas",
                "description": "Consulta matemática",
            },
            {
                "query": "¿Cómo funciona la fotosíntesis en las plantas?",
                "expected_domain": "biología",
                "description": "Consulta de biología",
            },
            {
                "query": "¿Cuál es la capital de Francia?",
                "expected_domain": "general",
                "description": "Consulta general",
            },
        ]

        print("🧪 PROBANDO CONSULTAS DE DIFERENTES DOMINIOS")
        print("-" * 60)

        for i, test_case in enumerate(test_queries, 1):
            print(f"\n📋 Prueba {i}: {test_case['description']}")
            result = self.test_chat_query(
                test_case["query"], test_case["expected_domain"]
            )

            self.test_results.append({"test_case": test_case, "result": result})

            time.sleep(1)  # Pausa entre pruebas

        # 4. Resumen de resultados
        print("\n📊 RESUMEN DE RESULTADOS")
        print("=" * 60)

        successful_tests = sum(
            1 for r in self.test_results if r["result"].get("success", False)
        )
        total_tests = len(self.test_results)

        print(f"✅ Pruebas exitosas: {successful_tests}/{total_tests}")
        print(f"📈 Tasa de éxito: {(successful_tests/total_tests)*100:.1f}%")

        # Estadísticas por dominio
        domain_stats = {}
        for result in self.test_results:
            if result["result"].get("success"):
                domain = result["result"]["domain"]
                if domain not in domain_stats:
                    domain_stats[domain] = {"count": 0, "avg_confidence": 0}
                domain_stats[domain]["count"] += 1
                domain_stats[domain]["avg_confidence"] += result["result"]["confidence"]

        print("\n🎯 ESTADÍSTICAS POR DOMINIO:")
        for domain, stats in domain_stats.items():
            avg_conf = stats["avg_confidence"] / stats["count"]
            print(
                f"   {domain}: {stats['count']} consultas (confianza promedio: {avg_conf:.2f})"
            )

        # Métodos de procesamiento utilizados
        methods_used = {}
        for result in self.test_results:
            if result["result"].get("success"):
                method = result["result"]["method"]
                methods_used[method] = methods_used.get(method, 0) + 1

        print("\n🛣️ MÉTODOS DE PROCESAMIENTO UTILIZADOS:")
        for method, count in methods_used.items():
            print(f"   {method}: {count} consultas")

        print("\n🎉 PRUEBA COMPLETA FINALIZADA")


def main():
    """Función principal"""
    print("🧪 TESTER DE INTEGRACIÓN DE RAMAS")
    print("=" * 50)

    # Verificar que el servidor esté corriendo
    tester = BranchIntegrationTester()

    print("⚠️ Asegúrate de que el servidor esté corriendo:")
    print("   python llm_server.py")
    print()

    input("Presiona Enter cuando el servidor esté listo...")

    # Ejecutar pruebas
    tester.run_comprehensive_test()


if __name__ == "__main__":
    main()
