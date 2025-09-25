#!/bin/bash
set -e

# Cambiar al directorio del proyecto
cd "$(dirname "$0")/.."

# Mensaje de inicio
echo "🔄 Iniciando restauración de estructura de ramas de Shaili-AI"

# Verificar Python
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 no está instalado. Por favor, instálalo primero."
    exit 1
fi

# Crear entorno virtual si no existe
if [ ! -d "venv" ]; then
    echo "🔧 Creando entorno virtual..."
    python3 -m venv venv
fi

# Activar entorno virtual
source venv/bin/activate

# Instalar dependencias
pip install --quiet --upgrade pip
pip install --quiet setuptools

# Ejecutar script de restauración
python3 scripts/restore_branch_structure.py

# Desactivar entorno virtual
deactivate

# Mensaje de finalización
echo "✅ Restauración de ramas completada con éxito."
