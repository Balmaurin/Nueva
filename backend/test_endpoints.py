import unittest
import requests
import json
import bcrypt
import sys
import os
from datetime import datetime

# Configuración base
BASE_URL = "http://localhost:8000"
TOKEN = None


def debug_print(message):
    """Imprimir mensaje de depuración"""
    print(f"[DEBUG] {message}", file=sys.stderr)


def create_test_user():
    """Crear usuario de prueba si no existe"""
    user_data = {
        "username": "test_user",
        "email": "test@sheily-ai.com",
        "password": "TestPassword123!",
        "full_name": "Usuario de Prueba",
    }

    try:
        response = requests.post(f"{BASE_URL}/api/auth/register", json=user_data)
        if response.status_code == 201:
            print(f"✅ Usuario de prueba creado: {user_data['username']}")
            return user_data
        elif response.status_code == 409:
            print(f"ℹ️ Usuario de prueba ya existe: {user_data['username']}")
            return user_data
        else:
            print(f"⚠️ No se pudo crear usuario de prueba: {response.status_code}")
            return None
    except Exception as e:
        print(f"❌ Error creando usuario de prueba: {e}")
        return None


def login():
    """Iniciar sesión y obtener token"""
    global TOKEN

    # Crear usuario de prueba si no existe
    user_data = create_test_user()
    if not user_data:
        return None

    login_data = {"username": user_data["username"], "password": user_data["password"]}

    debug_print(f"Intentando iniciar sesión con: {login_data['username']}")

    try:
        response = requests.post(f"{BASE_URL}/api/auth/login", json=login_data)
        debug_print(f"Respuesta de login - Código: {response.status_code}")

        if response.status_code == 200:
            TOKEN = response.json()["token"]
            debug_print(f"Token obtenido: {TOKEN[:20]}...")
            return TOKEN
        else:
            debug_print(f"Error de inicio de sesión: {response.text}")
            return None
    except Exception as e:
        debug_print(f"Excepción en login: {e}")
        return None


def test_health_endpoint():
    """Probar endpoint de salud"""
    print("\n🔍 Probando endpoint de salud...")

    try:
        response = requests.get(f"{BASE_URL}/api/health")

        if response.status_code == 200:
            health_data = response.json()
            print(f"✅ Health check exitoso")
            print(f"   Estado: {health_data.get('status')}")
            print(f"   Base de datos: {health_data.get('database', {}).get('status')}")
            print(f"   Modelo: {health_data.get('model', {}).get('status')}")
            print(f"   Uptime: {health_data.get('uptime', 0):.2f}s")
        else:
            print(f"❌ Health check falló: {response.status_code}")

    except Exception as e:
        print(f"❌ Error en health check: {e}")


def test_auth_endpoints():
    """Probar endpoints de autenticación"""
    print("\n🔐 Probando endpoints de autenticación...")

    if not TOKEN:
        print("❌ No hay token disponible")
        return

    headers = {"Authorization": f"Bearer {TOKEN}"}

    # Probar endpoint de perfil
    try:
        response = requests.get(f"{BASE_URL}/api/auth/profile", headers=headers)

        if response.status_code == 200:
            profile_data = response.json()
            print(f"✅ Perfil obtenido: {profile_data['user']['username']}")
        else:
            print(f"❌ Error obteniendo perfil: {response.status_code}")

    except Exception as e:
        print(f"❌ Error en perfil: {e}")

    # Probar endpoint de tokens
    try:
        response = requests.get(f"{BASE_URL}/api/auth/tokens", headers=headers)

        if response.status_code == 200:
            tokens_data = response.json()
            print(f"✅ Tokens obtenidos: {tokens_data['tokens']}")
        else:
            print(f"❌ Error obteniendo tokens: {response.status_code}")

    except Exception as e:
        print(f"❌ Error en tokens: {e}")


def test_models_endpoint():
    """Probar endpoint de modelos"""
    print("\n🤖 Probando endpoint de modelos...")

    try:
        response = requests.get(f"{BASE_URL}/api/models/available")

        if response.status_code == 200:
            models_data = response.json()
            print(f"✅ Modelos obtenidos: {len(models_data)} modelos")

            for model in models_data[:3]:  # Mostrar primeros 3 modelos
                print(f"   - {model.get('name')}: {model.get('status')}")
        else:
            print(f"❌ Error obteniendo modelos: {response.status_code}")

    except Exception as e:
        print(f"❌ Error en modelos: {e}")


def test_dashboard_endpoint():
    """Probar endpoint del dashboard"""
    print("\n📊 Probando endpoint del dashboard...")

    if not TOKEN:
        print("❌ No hay token disponible")
        return

    headers = {"Authorization": f"Bearer {TOKEN}"}

    try:
        response = requests.get(f"{BASE_URL}/api/dashboard", headers=headers)

        if response.status_code == 200:
            dashboard_data = response.json()
            print(f"✅ Dashboard obtenido")
            print(f"   Usuario: {dashboard_data['user']['username']}")
            print(f"   Tokens: {dashboard_data['stats']['tokens']}")
            print(f"   Estado del sistema: {dashboard_data['system']['status']}")
        else:
            print(f"❌ Error obteniendo dashboard: {response.status_code}")

    except Exception as e:
        print(f"❌ Error en dashboard: {e}")


def test_chat_health():
    """Probar salud del servicio de chat"""
    print("\n💬 Probando salud del servicio de chat...")

    try:
        response = requests.get(f"{BASE_URL}/api/chat/health")

        if response.status_code == 200:
            chat_health = response.json()
            print(f"✅ Chat health check exitoso")
            print(f"   Servicio: {chat_health.get('service')}")
            print(f"   Base de datos: {chat_health.get('database', {}).get('status')}")
            print(f"   Modelo: {chat_health.get('model', {}).get('status')}")
        else:
            print(f"❌ Chat health check falló: {response.status_code}")

    except Exception as e:
        print(f"❌ Error en chat health: {e}")


class TestModelEndpoints(unittest.TestCase):
    BASE_URL = "http://localhost:8000"

    def test_model_health_check(self):
        """Verificar endpoint de salud del modelo"""
        response = requests.get(f"{self.BASE_URL}/health")
        self.assertEqual(response.status_code, 200)

        data = response.json()
        self.assertTrue(data["model_loaded"], "El modelo no está cargado")
        self.assertIn(
            "bartowski/Llama-3.2-3B-Instruct-GGUF",
            data["model_info"]["name"],
            "Modelo incorrecto",
        )

    def test_model_generation(self):
        """Probar generación de respuestas con el modelo Llama"""
        payload = {
            "prompt": "Hola, ¿cómo estás?",
            "max_length": 100,
            "temperature": 0.7,
        }

        response = requests.post(f"{self.BASE_URL}/generate", json=payload)
        self.assertEqual(response.status_code, 200)

        data = response.json()
        self.assertIn("response", data, "Respuesta no generada")
        self.assertTrue(len(data["response"]) > 0, "Respuesta vacía")
        self.assertEqual(
            data["model"], "Llama-3.2-3B-Instruct-Q8_0", "Modelo incorrecto"
        )

    def test_model_load(self):
        """Probar carga de modelo"""
        payload = {"model_name": "bartowski/Llama-3.2-3B-Instruct-GGUF"}

        response = requests.post(f"{self.BASE_URL}/load", json=payload)
        self.assertEqual(response.status_code, 200)

        data = response.json()
        self.assertTrue(data["model_loaded"], "Modelo no cargado correctamente")
        self.assertIn("success", data["status"], "Error en carga de modelo")


def run_all_tests():
    """Ejecutar todas las pruebas"""
    print("🧪 INICIANDO PRUEBAS DEL BACKEND SHEILY AI")
    print("=" * 50)

    # Probar endpoint de salud primero
    test_health_endpoint()

    # Intentar login
    if login():
        print(f"\n✅ Autenticación exitosa")

        # Probar endpoints que requieren autenticación
        test_auth_endpoints()
        test_dashboard_endpoint()
    else:
        print(f"\n❌ Fallo en autenticación")

    # Probar endpoints públicos
    test_models_endpoint()
    test_chat_health()

    print("\n" + "=" * 50)
    print("🏁 PRUEBAS COMPLETADAS")


def main():
    """Función principal"""
    try:
        run_all_tests()
    except KeyboardInterrupt:
        print("\n\n⏹️ Pruebas interrumpidas por el usuario")
    except Exception as e:
        print(f"\n❌ Error ejecutando pruebas: {e}")
        sys.exit(1)


if __name__ == "__main__":
    unittest.main()
