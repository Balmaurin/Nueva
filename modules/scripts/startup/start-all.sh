#!/bin/bash

# Script para iniciar tanto el backend como el frontend de Shaili AI
# Se puede ejecutar desde cualquier directorio del proyecto

# Obtener el directorio del script y el directorio raíz del proyecto
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"

echo "🚀 Iniciando Shaili AI - Backend y Frontend"
echo "📁 Directorio del proyecto: $PROJECT_ROOT"
echo ""

# Función para manejar la salida limpia
cleanup() {
    echo ""
    echo "🛑 Deteniendo todos los servicios..."
    kill $BACKEND_PID $FRONTEND_PID 2>/dev/null
    exit 0
}

# Configurar trap para manejar Ctrl+C
trap cleanup SIGINT SIGTERM

# Iniciar backend en segundo plano
echo "🔥 Iniciando Backend..."
"$SCRIPT_DIR/start-backend.sh" &
BACKEND_PID=$!

# Esperar un poco para que el backend se inicie
sleep 3

# Iniciar frontend en segundo plano
echo "🔥 Iniciando Frontend..."
"$SCRIPT_DIR/start-frontend.sh" &
FRONTEND_PID=$!

echo ""
echo "✅ Servicios iniciados:"
echo "   📍 Backend: http://127.0.0.1:8000"
echo "   📍 Frontend: http://127.0.0.1:3000"
echo ""
echo "🔄 Ambos servicios están ejecutándose en segundo plano"
echo "🛑 Para detener todos los servicios, presiona Ctrl+C"
echo ""

# Esperar a que ambos procesos terminen
wait $BACKEND_PID $FRONTEND_PID
