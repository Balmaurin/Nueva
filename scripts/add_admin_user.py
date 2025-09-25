#!/usr/bin/env python3
"""
Script para añadir usuario administrador a la base de datos Sheily AI
"""

import os
import sys
import bcrypt
import psycopg2
from dotenv import load_dotenv

def main():
    print("🚀 Añadiendo usuario administrador a Sheily AI")
    print("=" * 50)

    # Cargar variables de entorno desde el directorio backend
    config_path = os.path.join(os.path.dirname(__file__), '..', 'backend', 'config.env')
    load_dotenv(dotenv_path=config_path)

    # Configuración de la base de datos
    db_config = {
        'host': os.getenv('DB_HOST', 'localhost'),
        'port': os.getenv('DB_PORT', '5432'),
        'database': os.getenv('DB_NAME', 'sheily_ai_db'),
        'user': os.getenv('DB_USER', 'sheily_ai_user'),
        'password': os.getenv('DB_PASSWORD', 'vf@3YNskdhTq9bOXAYhHvzbZ')
    }

    print(f"🔧 Configuración de BD:")
    print(f"   Host: {db_config['host']}")
    print(f"   Puerto: {db_config['port']}")
    print(f"   Base de datos: {db_config['database']}")
    print(f"   Usuario: {db_config['user']}")
    print(f"   Contraseña: {'*' * len(db_config['password'])}")

    # Datos del administrador
    admin_data = {
        'username': 'Admin',
        'email': 'sergiobalma.gomez@gmail.com',
        'password': 'Admin123',
        'role': 'admin'
    }

    try:
        # Conectar a la base de datos
        print("🔌 Conectando a la base de datos...")
        conn = psycopg2.connect(**db_config)
        cursor = conn.cursor()

        # Verificar si el usuario ya existe
        print("🔍 Verificando si el usuario ya existe...")
        cursor.execute("SELECT id FROM users WHERE username = %s OR email = %s",
                      (admin_data['username'], admin_data['email']))
        existing_user = cursor.fetchone()

        if existing_user:
            print("⚠️ El usuario administrador ya existe en la base de datos")
            print("📋 Información del usuario existente:")
            cursor.execute("SELECT id, username, email, role, created_at FROM users WHERE id = %s",
                          (existing_user[0],))
            user_info = cursor.fetchone()
            print(f"   ID: {user_info[0]}")
            print(f"   Usuario: {user_info[1]}")
            print(f"   Email: {user_info[2]}")
            print(f"   Rol: {user_info[3]}")
            print(f"   Creado: {user_info[4]}")
            return

        # Generar hash de la contraseña
        print("🔐 Generando hash de la contraseña...")
        salt_rounds = 12
        password_bytes = admin_data['password'].encode('utf-8')
        hashed_password = bcrypt.hashpw(password_bytes, bcrypt.gensalt(salt_rounds))

        # Insertar usuario administrador
        print("💾 Insertando usuario administrador...")
        cursor.execute("""
            INSERT INTO users (username, email, password, role, created_at, updated_at)
            VALUES (%s, %s, %s, %s, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP)
            RETURNING id
        """, (
            admin_data['username'],
            admin_data['email'],
            hashed_password.decode('utf-8'),
            admin_data['role']
        ))

        user_id = cursor.fetchone()[0]

        # Confirmar cambios
        conn.commit()

        print("✅ Usuario administrador añadido exitosamente!")
        print("📋 Información del nuevo usuario:")
        print(f"   ID: {user_id}")
        print(f"   Usuario: {admin_data['username']}")
        print(f"   Email: {admin_data['email']}")
        print(f"   Rol: {admin_data['role']}")
        print(f"   Contraseña: {admin_data['password']} (hasheada)")

        print("\n🔑 Ahora puedes iniciar sesión con:")
        print(f"   Usuario: {admin_data['username']}")
        print(f"   Email: {admin_data['email']}")
        print(f"   Contraseña: {admin_data['password']}")

    except psycopg2.Error as e:
        print(f"❌ Error de base de datos: {e}")
        print("💡 Asegúrate de que:")
        print("   - PostgreSQL esté ejecutándose")
        print("   - La base de datos 'sheily_ai_db' existe")
        print("   - El usuario 'sheily_ai_user' tiene permisos")
        print("   - Las credenciales en config.env son correctas")
        sys.exit(1)

    except Exception as e:
        print(f"❌ Error inesperado: {e}")
        sys.exit(1)

    finally:
        if 'cursor' in locals():
            cursor.close()
        if 'conn' in locals():
            conn.close()

if __name__ == "__main__":
    main()
