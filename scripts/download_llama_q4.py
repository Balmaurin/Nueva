#!/usr/bin/env python3
"""
Descargador de Llama 3.2 3B Instructor Q4
==========================================
Descarga únicamente el modelo Llama 3.2 3B Instructor Q4 para el proyecto Sheily AI
"""

import os
import requests
import sys
from pathlib import Path
from tqdm import tqdm
import hashlib

class LlamaModelDownloader:
    def __init__(self):
        self.project_root = Path(__file__).parent.parent
        self.models_dir = self.project_root / "models" / "llama"
        self.models_dir.mkdir(parents=True, exist_ok=True)
        
        # Modelo específico: Llama 3.2 3B Instructor Q4
        self.model_info = {
            "name": "Llama-3.2-3B-Instruct-Q4_K_M.gguf",
            "url": "https://huggingface.co/bartowski/Llama-3.2-3B-Instruct-GGUF/resolve/main/Llama-3.2-3B-Instruct-Q4_K_M.gguf",
            "size_gb": 2.1,
            "description": "Llama 3.2 3B Instructor Q4_K_M - Modelo cuantizado 4-bit"
        }
        
        self.model_path = self.models_dir / self.model_info["name"]
    
    def check_disk_space(self):
        """Verificar espacio en disco disponible"""
        try:
            statvfs = os.statvfs(self.models_dir)
            free_space_gb = (statvfs.f_frsize * statvfs.f_bavail) / (1024**3)
            
            print(f"💾 Espacio disponible: {free_space_gb:.1f} GB")
            print(f"📦 Tamaño del modelo: {self.model_info['size_gb']} GB")
            
            if free_space_gb < self.model_info['size_gb'] * 1.5:  # 50% extra para seguridad
                print("⚠️ Advertencia: Espacio en disco limitado")
                return False
            
            return True
        except Exception as e:
            print(f"❌ Error verificando espacio en disco: {e}")
            return False
    
    def download_file(self, url, filepath):
        """Descargar archivo con barra de progreso"""
        try:
            print(f"📥 Descargando: {self.model_info['name']}")
            print(f"🔗 URL: {url}")
            
            response = requests.get(url, stream=True)
            response.raise_for_status()
            
            total_size = int(response.headers.get('content-length', 0))
            
            with open(filepath, 'wb') as file, tqdm(
                desc="Descargando",
                total=total_size,
                unit='B',
                unit_scale=True,
                unit_divisor=1024,
            ) as progress_bar:
                for chunk in response.iter_content(chunk_size=8192):
                    if chunk:
                        file.write(chunk)
                        progress_bar.update(len(chunk))
            
            print(f"✅ Descarga completada: {filepath}")
            return True
            
        except Exception as e:
            print(f"❌ Error descargando archivo: {e}")
            return False
    
    def verify_download(self):
        """Verificar que el archivo se descargó correctamente"""
        if not self.model_path.exists():
            return False
        
        file_size = self.model_path.stat().st_size
        expected_size_gb = self.model_info['size_gb']
        actual_size_gb = file_size / (1024**3)
        
        print(f"📊 Tamaño del archivo: {actual_size_gb:.2f} GB")
        print(f"📊 Tamaño esperado: {expected_size_gb} GB")
        
        # Verificar que el tamaño esté dentro del rango esperado (±10%)
        if abs(actual_size_gb - expected_size_gb) / expected_size_gb > 0.1:
            print("⚠️ Advertencia: El tamaño del archivo no coincide con el esperado")
            return False
        
        return True
    
    def download_model(self):
        """Descargar el modelo Llama 3.2 3B Instructor Q4"""
        print("🚀 Descargador de Llama 3.2 3B Instructor Q4")
        print("=" * 50)
        print(f"📋 Modelo: {self.model_info['description']}")
        print(f"📁 Directorio: {self.models_dir}")
        print(f"💾 Tamaño: {self.model_info['size_gb']} GB")
        print()
        
        # Verificar si ya existe
        if self.model_path.exists():
            print(f"✅ El modelo ya existe: {self.model_path}")
            if self.verify_download():
                print("✅ Modelo verificado correctamente")
                return True
            else:
                print("⚠️ El archivo existente parece estar corrupto, re-descargando...")
                self.model_path.unlink()
        
        # Verificar espacio en disco
        if not self.check_disk_space():
            print("❌ No hay suficiente espacio en disco")
            return False
        
        # Descargar el modelo
        print(f"\n🔄 Iniciando descarga...")
        success = self.download_file(self.model_info['url'], self.model_path)
        
        if success and self.verify_download():
            print("\n🎉 ¡Descarga completada exitosamente!")
            print(f"📁 Modelo guardado en: {self.model_path}")
            return True
        else:
            print("\n❌ Error en la descarga o verificación")
            return False
    
    def create_symlink(self):
        """Crear enlace simbólico con nombre simplificado"""
        try:
            simple_name = "llama3-2-3b-instructor-q4.gguf"
            simple_path = self.models_dir / simple_name
            
            if simple_path.exists() or simple_path.is_symlink():
                simple_path.unlink()
            
            simple_path.symlink_to(self.model_path.name)
            print(f"🔗 Enlace simbólico creado: {simple_path}")
            return True
            
        except Exception as e:
            print(f"⚠️ No se pudo crear enlace simbólico: {e}")
            return False
    
    def update_config(self):
        """Actualizar configuración del proyecto"""
        try:
            # Actualizar config.env
            config_file = self.project_root / "backend" / "config.env"
            
            if config_file.exists():
                with open(config_file, 'r') as f:
                    content = f.read()
                
                # Actualizar la ruta del modelo
                new_content = content.replace(
                    "MODEL_PATH=./models/llama/model",
                    f"MODEL_PATH={self.model_path}"
                )
                
                with open(config_file, 'w') as f:
                    f.write(new_content)
                
                print(f"✅ Configuración actualizada: {config_file}")
            
            return True
            
        except Exception as e:
            print(f"⚠️ Error actualizando configuración: {e}")
            return False

def main():
    """Función principal"""
    downloader = LlamaModelDownloader()
    
    try:
        # Descargar modelo
        if downloader.download_model():
            # Crear enlace simbólico
            downloader.create_symlink()
            
            # Actualizar configuración
            downloader.update_config()
            
            print("\n🎯 PRÓXIMOS PASOS:")
            print("1. El modelo está listo para usar")
            print("2. Inicia el servidor LLM: python3 backend/llm_server.py")
            print("3. Inicia el backend: node backend/server.js")
            print("4. Prueba el chatbot en: http://localhost:3000")
            
            return 0
        else:
            print("\n❌ Error en la descarga del modelo")
            return 1
            
    except KeyboardInterrupt:
        print("\n⚠️ Descarga cancelada por el usuario")
        return 1
    except Exception as e:
        print(f"\n❌ Error inesperado: {e}")
        return 1

if __name__ == "__main__":
    exit(main())
