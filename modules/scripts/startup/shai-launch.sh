#!/bin/bash

# Script global para Shaili AI - Se puede ejecutar desde cualquier ubicación
# Uso: ./shai-launch.sh [frontend|backend|both|status|diagnose]

set -e

# Obtener la ruta absoluta del script y el directorio raíz del proyecto
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"
INTERFACE_DIR="$PROJECT_ROOT"

echo "🚀 Shaili AI - Sistema de Inicio Global"
echo "====================================="
echo "📁 Directorio base: $PROJECT_ROOT"
echo ""

# Verificar que el directorio interface existe
if [ ! -d "$INTERFACE_DIR" ]; then
    echo "❌ Error: No se encontró el directorio interface en: $INTERFACE_DIR"
    echo "💡 Asegúrate de ejecutar este script desde el directorio raíz de Shaili AI"
    exit 1
fi

# Verificar que el script start-all.sh existe
if [ ! -f "$INTERFACE_DIR/scripts/startup/start-all.sh" ]; then
    echo "❌ Error: No se encontró start-all.sh en: $INTERFACE_DIR/scripts/startup/"
    echo "💡 Asegúrate de que todos los scripts estén creados"
    exit 1
fi

# Cambiar al directorio raíz del proyecto
cd "$INTERFACE_DIR"

echo "✅ Directorio raíz encontrado"
echo "🔧 Ejecutando comando: $INTERFACE_DIR/scripts/startup/start-all.sh $@"
echo ""

# Ejecutar el script de inicio con todos los argumentos
exec "$INTERFACE_DIR/scripts/startup/start-all.sh" "$@"
