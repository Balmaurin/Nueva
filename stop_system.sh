#!/bin/bash
# ===========================================
# SCRIPT DE DETENCIÓN - SHEILY AI
# ===========================================
# Script que detiene todos los servicios del sistema

echo "🛑 DETENIENDO SISTEMA SHEILY AI"
echo "==============================="

# Colores para output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

# Detener backend
print_status "Deteniendo backend..."
if [ -f "logs/backend.pid" ]; then
    BACKEND_PID=$(cat logs/backend.pid)
    if kill -0 $BACKEND_PID 2>/dev/null; then
        kill $BACKEND_PID
        print_success "Backend detenido (PID: $BACKEND_PID)"
    else
        print_warning "Backend ya estaba detenido"
    fi
    rm -f logs/backend.pid
else
    # Intentar detener por nombre de proceso
    if pgrep -f "node server.js" > /dev/null; then
        pkill -f "node server.js"
        print_success "Backend detenido por nombre de proceso"
    else
        print_warning "Backend no estaba ejecutándose"
    fi
fi

# Detener frontend
print_status "Deteniendo frontend..."
if [ -f "logs/frontend.pid" ]; then
    FRONTEND_PID=$(cat logs/frontend.pid)
    if kill -0 $FRONTEND_PID 2>/dev/null; then
        kill $FRONTEND_PID
        print_success "Frontend detenido (PID: $FRONTEND_PID)"
    else
        print_warning "Frontend ya estaba detenido"
    fi
    rm -f logs/frontend.pid
else
    # Intentar detener por nombre de proceso
    if pgrep -f "next dev" > /dev/null; then
        pkill -f "next dev"
        print_success "Frontend detenido por nombre de proceso"
    else
        print_warning "Frontend no estaba ejecutándose"
    fi
fi

# Detener otros procesos relacionados
print_status "Deteniendo otros procesos relacionados..."
pkill -f "sheily" 2>/dev/null || true
pkill -f "llama" 2>/dev/null || true

print_success "Sistema Sheily AI detenido completamente"
