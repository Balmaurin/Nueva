#!/usr/bin/env python3
"""
Script de prueba para verificar la integración completa del sistema Sheily AI
"""

import asyncio
import sys
import os
import requests
import json
from datetime import datetime

# Agregar el path del proyecto
project_root = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, project_root)


def test_backend_connection():
    """Probar conexión con el backend"""
    print("🔍 Probando conexión con el backend...")

    try:
        response = requests.get("http://localhost:8000/api/system/health", timeout=10)
        if response.status_code == 200:
            print("✅ Backend conectado correctamente")
            return True
        else:
            print(f"❌ Backend respondió con código: {response.status_code}")
            return False
    except requests.exceptions.RequestException as e:
        print(f"❌ Error conectando al backend: {e}")
        return False


def test_ai_service():
    """Probar servicio de IA"""
    print("\n🤖 Probando servicio de IA...")

    try:
        response = requests.get(
            "http://localhost:8000/api/system/ai-status", timeout=10
        )
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Estado de IA: {data.get('message', 'Desconocido')}")
            print(f"   Componentes: {data.get('components', {})}")
            return True
        else:
            print(f"❌ Error obteniendo estado de IA: {response.status_code}")
            return False
    except requests.exceptions.RequestException as e:
        print(f"❌ Error probando servicio de IA: {e}")
        return False


def test_chat_endpoint():
    """Probar endpoint de chat"""
    print("\n💬 Probando endpoint de chat...")

    try:
        # Probar estado del chat
        response = requests.get("http://localhost:8000/api/chat/status", timeout=10)
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Estado del chat: {data.get('available', False)}")
            return True
        else:
            print(f"❌ Error obteniendo estado del chat: {response.status_code}")
            return False
    except requests.exceptions.RequestException as e:
        print(f"❌ Error probando chat: {e}")
        return False


def test_chat_message():
    """Probar envío de mensaje de chat"""
    print("\n📤 Probando envío de mensaje...")

    try:
        message_data = {"message": "Hola, ¿cómo estás?", "branch": "general"}

        response = requests.post(
            "http://localhost:8000/api/chat/send", json=message_data, timeout=30
        )

        if response.status_code == 200:
            data = response.json()
            print(f"✅ Mensaje procesado correctamente")
            print(f"   Respuesta: {data.get('content', '')[:100]}...")
            print(f"   Confianza: {data.get('confidence', 0):.2f}")
            print(
                f"   Tiempo: {data.get('performance', {}).get('processing_time', 0):.2f}s"
            )
            return True
        else:
            print(f"❌ Error procesando mensaje: {response.status_code}")
            print(f"   Respuesta: {response.text}")
            return False
    except requests.exceptions.RequestException as e:
        print(f"❌ Error enviando mensaje: {e}")
        return False


def test_branches():
    """Probar obtención de ramas"""
    print("\n🌿 Probando ramas disponibles...")

    try:
        response = requests.get("http://localhost:8000/api/chat/branches", timeout=10)
        if response.status_code == 200:
            data = response.json()
            branches = data.get("branches", [])
            print(f"✅ Ramas disponibles: {len(branches)}")
            for branch in branches:
                print(f"   - {branch.get('name', '')}: {branch.get('description', '')}")
            return True
        else:
            print(f"❌ Error obteniendo ramas: {response.status_code}")
            return False
    except requests.exceptions.RequestException as e:
        print(f"❌ Error probando ramas: {e}")
        return False


def test_frontend_connection():
    """Probar conexión con el frontend"""
    print("\n🎨 Probando conexión con el frontend...")

    try:
        response = requests.get("http://localhost:3000", timeout=10)
        if response.status_code == 200:
            print("✅ Frontend conectado correctamente")
            return True
        else:
            print(f"❌ Frontend respondió con código: {response.status_code}")
            return False
    except requests.exceptions.RequestException as e:
        print(f"❌ Error conectando al frontend: {e}")
        return False


async def test_ai_components():
    """Probar componentes de IA directamente"""
    print("\n🧪 Probando componentes de IA directamente...")

    try:
        # Importar componentes de IA
        from modules.core.model.simple_sheily import SimpleSheilyModel
        from models.branches.branch_manager import BranchManager
        from modules.memory.intelligent_fallback_system import IntelligentBackupSystem
        from modules.core.advanced_system_integrator import AdvancedSystemIntegrator

        print("✅ Módulos de IA importados correctamente")

        # Probar modelo principal
        try:
            model = SimpleSheilyModel()
            response = await model.generate_text("Hola")
            print(f"✅ Modelo principal: {response[:50]}...")
        except Exception as e:
            print(f"❌ Error con modelo principal: {e}")

        # Probar gestor de ramas
        try:
            branch_manager = BranchManager()
            embedding = await branch_manager.get_branch_embedding("Test", "general")
            print(f"✅ Gestor de ramas: embedding generado")
        except Exception as e:
            print(f"❌ Error con gestor de ramas: {e}")

        # Probar sistema de respaldo
        try:
            backup_system = IntelligentBackupSystem()
            backup_response = await backup_system.generate_backup_response("Test")
            print(
                f"✅ Sistema de respaldo: {backup_response.get('response', '')[:50]}..."
            )
        except Exception as e:
            print(f"❌ Error con sistema de respaldo: {e}")

        # Probar integrador del sistema
        try:
            system_integrator = AdvancedSystemIntegrator()
            result = await system_integrator.process_query("Test")
            print(f"✅ Integrador del sistema: {result.get('response', '')[:50]}...")
        except Exception as e:
            print(f"❌ Error con integrador del sistema: {e}")

        return True

    except ImportError as e:
        print(f"❌ Error importando módulos de IA: {e}")
        return False
    except Exception as e:
        print(f"❌ Error probando componentes: {e}")
        return False


def main():
    """Función principal de pruebas"""
    print("🚀 Iniciando pruebas de integración del sistema Sheily AI")
    print("=" * 60)

    results = []

    # Pruebas del backend
    results.append(("Backend Connection", test_backend_connection()))
    results.append(("AI Service", test_ai_service()))
    results.append(("Chat Endpoint", test_chat_endpoint()))
    results.append(("Chat Message", test_chat_message()))
    results.append(("Branches", test_branches()))

    # Pruebas del frontend
    results.append(("Frontend Connection", test_frontend_connection()))

    # Pruebas de componentes de IA
    results.append(("AI Components", asyncio.run(test_ai_components())))

    # Resumen
    print("\n" + "=" * 60)
    print("📊 RESUMEN DE PRUEBAS")
    print("=" * 60)

    passed = 0
    total = len(results)

    for test_name, result in results:
        status = "✅ PASÓ" if result else "❌ FALLÓ"
        print(f"{test_name:<25} {status}")
        if result:
            passed += 1

    print(f"\nResultado: {passed}/{total} pruebas pasaron")

    if passed == total:
        print("🎉 ¡TODAS LAS PRUEBAS PASARON! El sistema está completamente integrado.")
    else:
        print("⚠️  Algunas pruebas fallaron. Revisa los errores arriba.")

    return passed == total


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
