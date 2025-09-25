#!/usr/bin/env python3
"""
Generador de Configuración Segura para Sheily AI
===============================================
Genera configuraciones seguras con secretos aleatorios
"""

import os
import secrets
import string
import json
from pathlib import Path
from typing import Dict, Any

class SecureConfigGenerator:
    """Generador de configuración segura"""
    
    def __init__(self):
        self.project_root = Path(__file__).parent.parent
        self.backend_dir = self.project_root / "backend"
        self.config_dir = self.project_root / "config"
        
    def generate_jwt_secret(self, length: int = 64) -> str:
        """Generar JWT secret seguro"""
        return secrets.token_urlsafe(length)
    
    def generate_password(self, length: int = 32) -> str:
        """Generar contraseña segura"""
        alphabet = string.ascii_letters + string.digits + "!@#$%^&*"
        return ''.join(secrets.choice(alphabet) for _ in range(length))
    
    def generate_database_config(self) -> Dict[str, str]:
        """Generar configuración de base de datos segura"""
        return {
            "DB_PASSWORD": self.generate_password(24),
            "DB_USER": "sheily_ai_user",
            "DB_NAME": "sheily_ai_db",
            "DB_HOST": "localhost",
            "DB_PORT": "5432",
            "DB_TYPE": "postgres"
        }
    
    def generate_redis_config(self) -> Dict[str, str]:
        """Generar configuración de Redis segura"""
        return {
            "REDIS_PASSWORD": self.generate_password(24),
            "REDIS_HOST": "localhost",
            "REDIS_PORT": "6379"
        }
    
    def generate_smtp_config(self) -> Dict[str, str]:
        """Generar configuración SMTP segura"""
        return {
            "SMTP_PASSWORD": self.generate_password(24),
            "SMTP_USER": "noreply@sheily-ai.com",
            "SMTP_HOST": "smtp.gmail.com",
            "SMTP_PORT": "587",
            "SMTP_FROM": "noreply@sheily-ai.com"
        }
    
    def generate_blockchain_config(self) -> Dict[str, str]:
        """Generar configuración blockchain segura"""
        return {
            "SOLANA_PRIVATE_KEY": self.generate_password(64),
            "SOLANA_PUBLIC_KEY": self.generate_password(44),
            "SOLANA_RPC_URL": "https://api.devnet.solana.com"
        }
    
    def generate_ssl_config(self) -> Dict[str, str]:
        """Generar configuración SSL"""
        return {
            "SSL_ENABLED": "false",
            "SSL_CERT_PATH": "",
            "SSL_KEY_PATH": ""
        }
    
    def create_env_file(self, config: Dict[str, str], filename: str = "config.env") -> bool:
        """Crear archivo de variables de entorno"""
        try:
            env_path = self.backend_dir / filename
            
            with open(env_path, 'w') as f:
                f.write("# ===========================================\n")
                f.write("# CONFIGURACIÓN SEGURA GENERADA AUTOMÁTICAMENTE\n")
                f.write("# ===========================================\n")
                f.write("# Fecha de generación: {}\n".format(
                    __import__('datetime').datetime.now().isoformat()
                ))
                f.write("# NO COMMITEAR ESTE ARCHIVO AL REPOSITORIO\n")
                f.write("# ===========================================\n\n")
                
                for key, value in config.items():
                    f.write(f"{key}={value}\n")
            
            # Establecer permisos seguros
            os.chmod(env_path, 0o600)
            
            print(f"✅ Archivo {filename} creado exitosamente")
            return True
            
        except Exception as e:
            print(f"❌ Error creando archivo {filename}: {e}")
            return False
    
    def create_env_example(self) -> bool:
        """Crear archivo .env.example sin secretos"""
        try:
            example_config = {
                "PORT": "8000",
                "NODE_ENV": "development",
                "HOST": "127.0.0.1",
                "JWT_SECRET": "GENERAR_SECRET_SEGURO_AQUI",
                "BCRYPT_ROUNDS": "12",
                "SESSION_TIMEOUT": "86400000",
                "MODEL_SERVER_URL": "http://localhost:8005",
                "MODEL_PATH": "./models/llama/model",
                "MODEL_SERVER_PORT": "8005",
                "LLM_MODE": "openai",
                "LLM_BASE_URL": "http://localhost:8005",
                "LLM_MODEL_NAME": "Llama-3.2-3B-Instruct-Q8_0",
                "LLM_TIMEOUT": "60",
                "LLM_MAX_RETRIES": "3",
                "DB_TYPE": "postgres",
                "DB_HOST": "localhost",
                "DB_PORT": "5432",
                "DB_NAME": "sheily_ai_db",
                "DB_USER": "sheily_ai_user",
                "DB_PASSWORD": "GENERAR_PASSWORD_SEGURO_AQUI",
                "REDIS_HOST": "localhost",
                "REDIS_PORT": "6379",
                "REDIS_PASSWORD": "GENERAR_PASSWORD_REDIS_AQUI",
                "BACKUP_DIR": "./backups/chat",
                "MAX_BACKUPS": "10",
                "BACKUP_INTERVAL": "43200000",
                "LOG_LEVEL": "info",
                "LOG_DIR": "./logs",
                "CACHE_ENABLED": "true",
                "CACHE_SIZE": "1000",
                "CACHE_TTL": "300000",
                "TOKENS_PER_VALIDATED_EXERCISE": "10",
                "TOKEN_REWARD_MULTIPLIER": "1.5",
                "RATE_LIMIT_WINDOW_MS": "900000",
                "RATE_LIMIT_MAX_REQUESTS": "100",
                "CORS_ORIGIN": "http://localhost:3000",
                "CORS_CREDENTIALS": "true",
                "SSL_ENABLED": "false",
                "SSL_CERT_PATH": "",
                "SSL_KEY_PATH": "",
                "SMTP_HOST": "smtp.gmail.com",
                "SMTP_PORT": "587",
                "SMTP_USER": "noreply@sheily-ai.com",
                "SMTP_PASSWORD": "GENERAR_PASSWORD_SMTP_AQUI",
                "SMTP_FROM": "noreply@sheily-ai.com",
                "SOLANA_RPC_URL": "https://api.devnet.solana.com",
                "SOLANA_PRIVATE_KEY": "GENERAR_PRIVATE_KEY_AQUI",
                "SOLANA_PUBLIC_KEY": "GENERAR_PUBLIC_KEY_AQUI"
            }
            
            example_path = self.backend_dir / "config.env.example"
            
            with open(example_path, 'w') as f:
                f.write("# ===========================================\n")
                f.write("# CONFIGURACIÓN DE EJEMPLO - BACKEND SHEILY AI\n")
                f.write("# ===========================================\n")
                f.write("# Copia este archivo como config.env y configura los valores reales\n")
                f.write("# ===========================================\n\n")
                
                for key, value in example_config.items():
                    f.write(f"{key}={value}\n")
            
            print("✅ Archivo config.env.example creado exitosamente")
            return True
            
        except Exception as e:
            print(f"❌ Error creando archivo de ejemplo: {e}")
            return False
    
    def generate_all_configs(self) -> bool:
        """Generar todas las configuraciones seguras"""
        print("🔐 Generando configuraciones seguras...")
        
        # Combinar todas las configuraciones
        all_config = {}
        all_config.update(self.generate_database_config())
        all_config.update(self.generate_redis_config())
        all_config.update(self.generate_smtp_config())
        all_config.update(self.generate_blockchain_config())
        all_config.update(self.generate_ssl_config())
        
        # Agregar JWT secret
        all_config["JWT_SECRET"] = self.generate_jwt_secret()
        
        # Crear archivos
        success = True
        success &= self.create_env_file(all_config, "config.env")
        success &= self.create_env_example()
        
        if success:
            print("\n🎉 Configuraciones seguras generadas exitosamente!")
            print("\n📋 Próximos pasos:")
            print("1. Revisar el archivo config.env generado")
            print("2. Configurar las variables específicas de tu entorno")
            print("3. NO commitear config.env al repositorio")
            print("4. Usar config.env.example como plantilla")
            
        return success

def main():
    """Función principal"""
    print("🚀 Generador de Configuración Segura - Sheily AI")
    print("=" * 50)
    
    generator = SecureConfigGenerator()
    
    if generator.generate_all_configs():
        print("\n✅ Proceso completado exitosamente")
    else:
        print("\n❌ Error en el proceso de generación")
        return 1
    
    return 0

if __name__ == "__main__":
    exit(main())

