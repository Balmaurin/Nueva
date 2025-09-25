#!/usr/bin/env python3
"""
Simulación exacta de lo que hace el navegador para login
"""

import requests
import json

def simulate_browser_login():
    print("🌐 SIMULACIÓN EXACTA DEL NAVEGADOR")
    print("=" * 50)
    
    API_BASE = "http://localhost:8002"
    
    # 1. Simular OPTIONS (preflight) que hace el navegador
    print("1️⃣ Simulando OPTIONS (preflight)...")
    try:
        options_headers = {
            "Origin": "http://localhost:3000",
            "Access-Control-Request-Method": "POST",
            "Access-Control-Request-Headers": "content-type",
            "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36"
        }
        
        response = requests.options(
            f"{API_BASE}/api/auth/login",
            headers=options_headers
        )
        
        print(f"   Status: {response.status_code}")
        print(f"   Headers CORS presentes:")
        
        cors_headers = [
            'access-control-allow-origin',
            'access-control-allow-methods', 
            'access-control-allow-credentials',
            'access-control-allow-headers'
        ]
        
        for header in cors_headers:
            if header in response.headers:
                print(f"   ✅ {header}: {response.headers[header]}")
            else:
                print(f"   ❌ Falta {header}")
                
    except Exception as e:
        print(f"   ❌ Error en OPTIONS: {e}")
        return False
    
    # 2. Simular POST login que hace el navegador
    print("\n2️⃣ Simulando POST login...")
    try:
        post_headers = {
            "Content-Type": "application/json",
            "Origin": "http://localhost:3000",
            "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36",
            "Accept": "application/json, text/plain, */*",
            "Accept-Language": "es-ES,es;q=0.9,en;q=0.8",
            "Accept-Encoding": "gzip, deflate, br",
            "Connection": "keep-alive"
        }
        
        login_data = {
            "identifier": "demo",
            "password": "demo123"
        }
        
        response = requests.post(
            f"{API_BASE}/api/auth/login",
            headers=post_headers,
            json=login_data,
            timeout=10
        )
        
        print(f"   Status: {response.status_code}")
        
        # Verificar headers CORS en respuesta
        if 'access-control-allow-origin' in response.headers:
            print(f"   ✅ CORS Origin: {response.headers['access-control-allow-origin']}")
        else:
            print("   ⚠️ No hay header CORS en respuesta POST")
        
        if response.status_code == 200:
            try:
                data = response.json()
                print(f"   ✅ Login exitoso: {data.get('success')}")
                if data.get('access_token'):
                    print("   ✅ Token generado correctamente")
                return True
            except:
                print(f"   ❌ Respuesta no es JSON válido: {response.text[:200]}")
                return False
        else:
            print(f"   ❌ Error {response.status_code}: {response.text[:200]}")
            return False
            
    except requests.exceptions.RequestException as e:
        print(f"   ❌ Error de conexión: {e}")
        return False
    except Exception as e:
        print(f"   ❌ Error inesperado: {e}")
        return False

def test_frontend_connection():
    print("\n3️⃣ Probando conexión del frontend...")
    try:
        response = requests.get("http://localhost:3000")
        print(f"   ✅ Frontend responde: {response.status_code}")
        return True
    except:
        print("   ❌ Frontend no responde")
        return False

if __name__ == "__main__":
    print("🔍 DEBUG PROFUNDO: CORS + LOGIN")
    
    # Test 1: Simular navegador
    success1 = simulate_browser_login()
    
    # Test 2: Verificar frontend
    success2 = test_frontend_connection()
    
    print(f"\n🎯 RESULTADO FINAL:")
    print(f"   API + CORS: {'✅ FUNCIONANDO' if success1 else '❌ PROBLEMA'}")
    print(f"   Frontend: {'✅ FUNCIONANDO' if success2 else '❌ PROBLEMA'}")
    
    if success1 and success2:
        print("\n🎉 ¡TODO FUNCIONA! El problema debe estar en:")
        print("   1. Cache del navegador (Ctrl+Shift+R)")
        print("   2. Extensiones del navegador")
        print("   3. Firewall o proxy")
        print("   4. Configuración de red")
    else:
        print("\n❌ Hay problemas en el backend")
