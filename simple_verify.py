#!/usr/bin/env python3
"""
Verificación simple del método verify_password
"""

from backend.auth_system import get_auth_system
import bcrypt

def test():
    # Obtener auth system
    auth = get_auth_system()
    
    # Hash de la BD
    password_hash = '$2b$12$sSJOJUi2crh4Ae0cYh4NHOsjKfm/ZLZtakw6oRwdKU/Qok394snHe'
    
    # Probar directamente
    direct_result = bcrypt.checkpw(b'demo123', password_hash.encode('utf-8'))
    print(f"Direct bcrypt: {direct_result}")
    
    # Probar método del auth system
    auth_result = auth.verify_password('demo123', password_hash)
    print(f"Auth system: {auth_result}")

if __name__ == "__main__":
    test()
