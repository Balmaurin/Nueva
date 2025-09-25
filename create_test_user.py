#!/usr/bin/env python3
"""
Script para crear usuario de prueba
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'backend'))

from database_manager_complete import get_db_manager
from auth_system import get_auth_system

def create_test_user():
    """Crear usuario de prueba para testing"""

    # Inicializar DB y auth
    db = get_db_manager()
    auth = get_auth_system()

    try:
        # Crear usuario de prueba
        result = auth.register_user(
            username="test",
            email="test@example.com",
            password="test123456",
            full_name="Usuario de Prueba"
        )

        if result["success"]:
            print("✅ Usuario de prueba creado exitosamente!")
            print(f"   Username: test")
            print(f"   Email: test@example.com")
            print(f"   Password: test123456")
        else:
            print(f"❌ Error creando usuario: {result['error']}")

    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    create_test_user()