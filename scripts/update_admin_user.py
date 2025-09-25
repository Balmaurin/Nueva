#!/usr/bin/env python3
"""
Script para actualizar usuario administrador en la base de datos Sheily AI
"""

import os
import sys
import bcrypt
import psycopg2
from dotenv import load_dotenv

def main():
    print("🔄 Actualizando usuario administrador en Sheily AI")
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

    # Datos del administrador actualizados
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

        # Generar hash de la nueva contraseña
        print("🔐 Generando hash de la nueva contraseña...")
        salt_rounds = 12
        password_bytes = admin_data['password'].encode('utf-8')
        hashed_password = bcrypt.hashpw(password_bytes, bcrypt.gensalt(salt_rounds))

        # Actualizar usuario administrador
        print("📝 Actualizando usuario administrador...")
        cursor.execute("""
            UPDATE users
            SET username = %s, password = %s, role = %s, updated_at = CURRENT_TIMESTAMP
            WHERE email = %s
            RETURNING id, username, email, role
        """, (
            admin_data['username'],
            hashed_password.decode('utf-8'),
            admin_data['role'],
            admin_data['email']
        ))

        result = cursor.fetchone()

        if result:
            user_id, username, email, role = result

            # Confirmar cambios
            conn.commit()

            print("✅ Usuario administrador actualizado exitosamente!")
            print("📋 Información del usuario actualizado:")
            print(f"   ID: {user_id}")
            print(f"   Usuario: {username}")
            print(f"   Email: {email}")
            print(f"   Rol: {role}")
            print(f"   Contraseña: {admin_data['password']} (hasheada)")

            print("\n🔑 Ahora puedes iniciar sesión con:")
            print(f"   Usuario: {admin_data['username']}")
            print(f"   Email: {admin_data['email']}")
            print(f"   Contraseña: {admin_data['password']}")
        else:
            print("❌ No se encontró el usuario con el email especificado")

    except psycopg2.Error as e:
        print(f"❌ Error de base de datos: {e}")
        conn.rollback()
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
