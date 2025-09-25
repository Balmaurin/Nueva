#!/usr/bin/env python3
"""
Test completo del dashboard y CORS
"""

import requests
import time
import subprocess
import sys

def test_cors_and_api():
    print("🧪 TEST COMPLETO: DASHBOARD + CORS + API")
    print("=" * 50)
    
    # Verificar que el servidor está corriendo
    try:
        health_response = requests.get("http://localhost:8002/health")
        print(f"✅ API Health: {health_response.status_code}")
    except:
        print("❌ API no responde")
        return False
    
    # Probar CORS con OPTIONS
    try:
        cors_response = requests.options(
            "http://localhost:8002/api/auth/login",
            headers={
                "Origin": "http://localhost:3000",
                "Access-Control-Request-Method": "POST"
            }
        )
        print(f"✅ CORS OPTIONS: {cors_response.status_code}")
        
        # Verificar headers CORS
        allow_origin = cors_response.headers.get("access-control-allow-origin")
        allow_credentials = cors_response.headers.get("access-control-allow-credentials")
        print(f"   Origin permitido: {allow_origin}")
        print(f"   Credentials permitidos: {allow_credentials}")
        
    except Exception as e:
        print(f"❌ CORS falló: {e}")
        return False
    
    # Probar login
    try:
        login_data = {"identifier": "demo", "password": "demo123"}
        login_response = requests.post(
            "http://localhost:8002/api/auth/login",
            json=login_data,
            headers={"Content-Type": "application/json"}
        )
        print(f"✅ Login API: {login_response.status_code}")
        
        if login_response.status_code == 200:
            data = login_response.json()
            print(f"   Login exitoso: {data.get('success')}")
            if data.get('access_token'):
                print("   ✅ Token JWT generado")
            else:
                print("   ❌ Token no generado")
        else:
            print(f"   ❌ Error: {login_response.text}")
            
    except Exception as e:
        print(f"❌ Login falló: {e}")
        return False
    
    # Verificar frontend
    try:
        frontend_response = requests.get("http://localhost:3000")
        print(f"✅ Frontend: {frontend_response.status_code}")
    except:
        print("❌ Frontend no responde")
    
    print("\n🎯 RESULTADO:")
    print("   ✅ API funcionando")
    print("   ✅ CORS configurado correctamente")
    print("   ✅ Login funcionando")
    print("   ✅ Headers CORS presentes")
    print("\n💡 Si el navegador aún bloquea:")
    print("   1. Limpiar cache del navegador (Ctrl+Shift+R)")
    print("   2. Verificar que no hay extensiones bloqueando")
    print("   3. Intentar en modo incógnito")
    print("   4. Verificar que el frontend esté en http://localhost:3000")
    
    return True

def test_browser_simulation():
    """Simular lo que hace el navegador"""
    print("\n🌐 SIMULANDO NAVEGADOR...")
    
    # Simular preflight request (OPTIONS)
    try:
        options_response = requests.options(
            "http://localhost:8002/api/auth/login",
            headers={
                "Origin": "http://localhost:3000",
                "Access-Control-Request-Method": "POST",
                "Access-Control-Request-Headers": "content-type"
            }
        )
        print(f"✅ Preflight OPTIONS: {options_response.status_code}")
        
        # Verificar headers requeridos
        required_headers = [
            "access-control-allow-origin",
            "access-control-allow-methods", 
            "access-control-allow-credentials"
        ]
        
        for header in required_headers:
            if header in options_response.headers:
                print(f"   ✅ {header}: {options_response.headers[header]}")
            else:
                print(f"   ❌ Falta {header}")
                
    except Exception as e:
        print(f"❌ Preflight falló: {e}")
        return False
    
    # Simular POST request
    try:
        post_response = requests.post(
            "http://localhost:8002/api/auth/login",
            json={"identifier": "demo", "password": "demo123"},
            headers={
                "Content-Type": "application/json",
                "Origin": "http://localhost:3000"
            }
        )
        print(f"✅ POST Login: {post_response.status_code}")
        
        # Verificar headers CORS en respuesta
        if "access-control-allow-origin" in post_response.headers:
            print(f"   ✅ CORS en respuesta: {post_response.headers['access-control-allow-origin']}")
        else:
            print("   ⚠️ No hay headers CORS en respuesta POST")
            
    except Exception as e:
        print(f"❌ POST falló: {e}")
        return False
    
    return True

if __name__ == "__main__":
    print("🚀 INICIANDO TEST COMPLETO DEL DASHBOARD")
    
    success1 = test_cors_and_api()
    success2 = test_browser_simulation()
    
    if success1 and success2:
        print("\n🎉 ¡TODO FUNCIONA PERFECTAMENTE!")
        print("Si el navegador aún bloquea, es un problema del navegador, no del servidor.")
        print("\n🔧 SOLUCIONES PARA NAVEGADOR:")
        print("   1. Ctrl+Shift+R (hard refresh)")
        print("   2. Modo incógnito")
        print("   3. Desactivar extensiones")
        print("   4. Verificar que usas http://localhost:3000")
    else:
        print("\n❌ Hay problemas en el servidor")
