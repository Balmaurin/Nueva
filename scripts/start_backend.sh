#!/bin/bash

# Script de inicio del Backend NeuroFusion
# Versión: 1.0.0
# Autor: Equipo NeuroFusion

# Colores para salida
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # Sin color

# Función para imprimir logs
log_info() {
    echo -e "${YELLOW}[INFO]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[OK]${NC} $1"
}

# Verificar requisitos previos
check_requirements() {
    log_info "Verificando requisitos previos..."
    
    # Python
    if ! command -v python3 &> /dev/null; then
        echo "❌ Python 3 no está instalado"
        exit 1
    fi
    
    # Dependencias
    python3 -m pip install -r requirements.txt > /dev/null 2>&1
    if [ $? -ne 0 ]; then
        echo "❌ Error instalando dependencias"
        exit 1
    fi
    
    log_success "Todos los requisitos verificados"
}

# Inicializar base de datos
initialize_database() {
    log_info "Inicializando base de datos..."
    
    python3 -m scripts.initialize_databases
    if [ $? -ne 0 ]; then
        echo "❌ Error inicializando bases de datos"
        exit 1
    fi
    
    log_success "Base de datos inicializada"
}

# Iniciar servidor backend
start_backend() {
    log_info "Iniciando servidor backend en puerto 8000..."
    
    # Usar uvicorn para servir la API
    python3 -m uvicorn modules.unified_systems.unified_api_server:app \
        --host 127.0.0.1 \
        --port 8000 \
        --reload \
        --log-level info
}

# Función principal
main() {
    echo -e "${YELLOW}🚀 Iniciando Backend NeuroFusion ${NC}"
    
    check_requirements
    initialize_database
    start_backend
}

# Manejar señales de interrupción
trap 'echo -e "\n${YELLOW}Deteniendo Backend NeuroFusion...${NC}"; exit 0' SIGINT SIGTERM

# Ejecutar función principal
main
