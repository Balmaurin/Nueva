#!/usr/bin/env python3
"""
Debug específico del método verify_password
"""

from backend.database_manager_complete import get_db_manager
from backend.auth_system import AuthSystem
import bcrypt

def debug_verify():
    print("🔍 DEBUG VERIFY_PASSWORD")
    print("=" * 40)
    
    # Obtener usuario de la BD
    db = get_db_manager()
    user = db.get_user(username='demo')
    
    if not user:
        print("❌ Usuario no encontrado")
        return
    
    password_hash = user.get('password_hash', '')
    print(f"Hash de BD: {password_hash}")
    print(f"Hash length: {len(password_hash)}")
    
    # Probar directamente con bcrypt
    test_password = "demo123"
    print(f"Probando contraseña: {test_password}")
    
    try:
        # Método directo
        result1 = bcrypt.checkpw(test_password.encode('utf-8'), password_hash.encode('utf-8'))
        print(f"bcrypt.checkpw() directo: {result1}")
        
        # Crear instancia de AuthSystem y probar
        auth = AuthSystem(db)
        result2 = auth.verify_password(test_password, password_hash)
        print(f"auth.verify_password(): {result2}")
        
        # Comparar tipos
        print(f"Tipo de password_hash: {type(password_hash)}")
        print(f"Es string: {isinstance(password_hash, str)}")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    debug_verify()
