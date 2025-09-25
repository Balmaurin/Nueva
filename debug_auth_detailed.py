#!/usr/bin/env python3
"""
Debug detallado de autenticación
"""

from backend.database_manager_complete import get_db_manager
from backend.auth_system import get_auth_system

def debug_auth():
    print("🔍 DEBUG DETALLADO DE AUTENTICACIÓN")
    print("=" * 50)
    
    try:
        # Probar database manager
        print("1️⃣ Probando Database Manager...")
        db = get_db_manager()
        user = db.get_user(username="demo")
        print(f"   Usuario encontrado: {user is not None}")
        if user:
            print(f"   Username: {user.get('username')}")
            print(f"   Password hash length: {len(user.get('password_hash', ''))}")
            print(f"   Is active: {user.get('is_active')}")
            print(f"   Email verified: {user.get('email_verified')}")
        
        # Probar auth system
        print("\n2️⃣ Probando Auth System...")
        auth = get_auth_system()
        print("   Sistema inicializado")
        
        # Verificar contraseña directamente
        if user:
            print("\n3️⃣ Verificando contraseña...")
            import bcrypt
            password_hash = user.get('password_hash', '')
            test_password = "demo123"
            
            is_valid = bcrypt.checkpw(test_password.encode('utf-8'), password_hash.encode('utf-8'))
            print(f"   bcrypt.checkpw('{test_password}', hash): {is_valid}")
            
            # Probar método del auth system
            auth_result = auth.verify_password(test_password, password_hash)
            print(f"   auth.verify_password(): {auth_result}")
        
        # Probar login completo
        print("\n4️⃣ Probando login completo...")
        result = auth.login_user("demo", "demo123")
        print(f"   Resultado: {result}")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    debug_auth()
