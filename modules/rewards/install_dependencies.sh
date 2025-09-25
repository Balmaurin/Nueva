#!/bin/bash
set -e

# Cambiar al directorio raíz del proyecto
cd "$(dirname "$0")/../.."

# Activar entorno virtual principal
source ./activate_venv.sh

# Instalar dependencias específicas del módulo de recompensas
pip install -r modules/rewards/requirements.txt

# Descargar modelo de lenguaje español
python -m spacy download es_core_news_lg

# Mensaje de éxito
echo "Dependencias del sistema de recompensas Sheilys instaladas correctamente."
echo "Entorno virtual principal ya activado."
