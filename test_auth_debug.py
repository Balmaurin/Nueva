#!/usr/bin/env python3
"""
Debug de autenticación
"""

from backend.auth_system import get_auth_system

def test_auth():
    print("🔍 Probando autenticación...")
    
    try:
        auth = get_auth_system()
        print("✅ Sistema de auth inicializado")
        
        result = auth.login_user("demo", "demo123")
        print(f"Resultado: {result}")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_auth()
