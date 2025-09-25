#!/bin/bash

# Script para iniciar el frontend de Shaili AI
# Se puede ejecutar desde cualquier directorio del proyecto

# Obtener el directorio del script y el directorio raíz del proyecto
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"
FRONTEND_DIR="$PROJECT_ROOT/interface/api/frontend"

echo "🚀 Iniciando Shaili AI Frontend..."
echo "📁 Directorio del frontend: $FRONTEND_DIR"

# Verificar que el directorio del frontend existe
if [ ! -d "$FRONTEND_DIR" ]; then
    echo "❌ Error: No se encontró el directorio del frontend en $FRONTEND_DIR"
    exit 1
fi

# Cambiar al directorio del frontend
cd "$FRONTEND_DIR"

# Verificar que package.json existe
if [ ! -f "package.json" ]; then
    echo "❌ Error: No se encontró package.json en el directorio del frontend"
    exit 1
fi

# Verificar si node_modules existe, si no, instalar dependencias
if [ ! -d "node_modules" ]; then
    echo "📦 Instalando dependencias..."
    npm install
fi

# Iniciar el servidor de desarrollo
echo "🔥 Iniciando servidor de desarrollo..."
echo "📍 URL: http://127.0.0.1:3000"
echo "🔄 Modo: Desarrollo (con recarga automática)"
echo ""
echo "Para detener el servidor, presiona Ctrl+C"
echo ""

npm run dev
