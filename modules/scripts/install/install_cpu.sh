#!/bin/bash

# Script de instalación para Shaili AI con PyTorch CPU
# Elimina dependencias NVIDIA/CUDA y usa solo CPU

echo "🚀 Configurando Shaili AI con PyTorch CPU..."

# Verificar si Python está instalado
if ! command -v python3 &> /dev/null; then
    echo "❌ Python3 no está instalado. Por favor instala Python 3.10 o superior."
    exit 1
fi

# Crear entorno virtual si no existe
if [ ! -d "venv" ]; then
    echo "📦 Creando entorno virtual..."
    python3 -m venv venv
fi

# Activar entorno virtual
echo "🔧 Activando entorno virtual..."
source venv/bin/activate

# Actualizar pip
echo "⬆️ Actualizando pip..."
pip install --upgrade pip

# Instalar PyTorch CPU
echo "🧠 Instalando PyTorch CPU..."
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cpu

# Instalar dependencias principales
echo "📚 Instalando dependencias principales..."
pip install transformers sentence-transformers scikit-learn numpy

# Instalar dependencias adicionales
echo "🔧 Instalando dependencias adicionales..."
pip install peft datasets pandas prometheus-client python-json-logger wandb faiss-cpu sentencepiece protobuf accelerate

# Instalar dependencias de clustering
echo "🔍 Instalando dependencias de clustering..."
pip install dbscan umap-learn hdbscan

echo "✅ Instalación completada exitosamente!"
echo "🐍 Para activar el entorno virtual: source venv/bin/activate"
echo "🧠 PyTorch CPU está configurado y listo para usar"
