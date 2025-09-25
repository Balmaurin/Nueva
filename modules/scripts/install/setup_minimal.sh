#!/bin/bash
set -euo pipefail

# Limpiar caché
pip cache purge
rm -rf ~/.cache/pip

# Configuración de entorno virtual
python3 -m venv venv_minimal
source venv_minimal/bin/activate

# Instalar dependencias mínimas
pip install --no-cache-dir \
    torch==2.3.0 \
    transformers==4.41.1 \
    numpy==1.26.4 \
    fastapi==0.110.2 \
    pydantic==2.7.1 \
    sentencepiece==0.2.0

# Verificar instalación
python -c "import torch; print(torch.__version__)"

echo "Instalación minimalista completada."
