#!/bin/bash

# Script para iniciar el backend de Shaili AI
# Se puede ejecutar desde cualquier directorio del proyecto

# Obtener el directorio del script y el directorio raíz del proyecto
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"
BACKEND_DIR="$PROJECT_ROOT/interface/api/backend"

echo "🚀 Iniciando Shaili AI Backend..."
echo "📁 Directorio del backend: $BACKEND_DIR"

# Verificar que el directorio del backend existe
if [ ! -d "$BACKEND_DIR" ]; then
    echo "❌ Error: No se encontró el directorio del backend en $BACKEND_DIR"
    exit 1
fi

# Cambiar al directorio del backend
cd "$BACKEND_DIR"

# Verificar que package.json existe
if [ ! -f "package.json" ]; then
    echo "❌ Error: No se encontró package.json en el directorio del backend"
    exit 1
fi

# Verificar si node_modules existe, si no, instalar dependencias
if [ ! -d "node_modules" ]; then
    echo "📦 Instalando dependencias..."
    npm install
fi

# Iniciar el servidor en modo desarrollo
echo "🔥 Iniciando servidor en modo desarrollo..."
echo "📍 URL: http://127.0.0.1:8000"
echo "🔄 Modo: Desarrollo (con recarga automática)"
echo ""
echo "Para detener el servidor, presiona Ctrl+C"
echo ""

npm run dev
