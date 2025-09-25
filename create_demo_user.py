#!/usr/bin/env python3
"""
Crear usuario demo con contraseña conocida
"""

import sqlite3
import bcrypt

def create_demo_user():
    db_path = 'data/sheily_ai.db'
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Crear hash de contraseña simple
    password = "demo123"
    salt = bcrypt.gensalt()
    password_hash = bcrypt.hashpw(password.encode('utf-8'), salt)
    
    # Insertar usuario
    cursor.execute('''
        INSERT OR REPLACE INTO users 
        (id, username, email, password_hash, full_name, role, is_active, email_verified, created_at, last_login)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, datetime('now'), datetime('now'))
    ''', (
        1,
        'demo',
        'demo@example.com',
        password_hash.decode('utf-8'),
        'Usuario Demo',
        'user',
        True,
        True
    ))
    
    conn.commit()
    conn.close()
    
    print("✅ Usuario demo creado:")
    print("   👤 Username: demo")
    print("   🔒 Password: demo123")

if __name__ == "__main__":
    create_demo_user()
