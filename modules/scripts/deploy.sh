#!/usr/bin/env bash
set -euo pipefail

# Colores
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

# Log function
log() {
    echo -e "${GREEN}[SHAILI-AI DEPLOY]${NC} $1"
}

# Error function
error() {
    echo -e "${RED}[ERROR]${NC} $1"
    exit 1
}

# Verificar dependencias
check_dependencies() {
    log "Verificando dependencias..."
    command -v docker >/dev/null 2>&1 || error "Docker no está instalado"
    command -v docker-compose >/dev/null 2>&1 || error "Docker Compose no está instalado"
}

# Construir imágenes
build_images() {
    log "Construyendo imágenes de Docker..."
    docker-compose build
}

# Iniciar servicios
start_services() {
    log "Iniciando servicios de Shaili-AI..."
    docker-compose up -d
}

# Detener servicios
stop_services() {
    log "Deteniendo servicios de Shaili-AI..."
    docker-compose down
}

# Mostrar estado de servicios
show_status() {
    log "Estado de servicios:"
    docker-compose ps
}

# Limpiar recursos
clean() {
    log "Limpiando recursos de Docker..."
    docker-compose down --rmi all --volumes
}

# Actualizar servicios
update() {
    log "Actualizando servicios..."
    git pull
    build_images
    start_services
}

# Menú principal
main() {
    case "${1:-}" in
        start)
            check_dependencies
            build_images
            start_services
            ;;
        stop)
            stop_services
            ;;
        restart)
            stop_services
            start_services
            ;;
        status)
            show_status
            ;;
        clean)
            clean
            ;;
        update)
            update
            ;;
        *)
            echo "Uso: $0 {start|stop|restart|status|clean|update}"
            exit 1
            ;;
    esac
}

# Ejecutar script
main "$@"
