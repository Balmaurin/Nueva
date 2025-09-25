#!/bin/bash

# Script de Detención del Sistema de Monitoreo Shaili AI
# =====================================================

set -e

# Colores para output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Función para logging
log_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

log_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Función para detener proceso por PID
stop_process() {
    local name=$1
    local pid_file=$2
    
    if [ -f "$pid_file" ]; then
        local pid=$(cat "$pid_file")
        if kill -0 $pid 2>/dev/null; then
            log_info "Deteniendo $name (PID: $pid)..."
            kill -TERM $pid
            
            # Esperar hasta 10 segundos para que se detenga gracefully
            local count=0
            while kill -0 $pid 2>/dev/null && [ $count -lt 10 ]; do
                sleep 1
                count=$((count + 1))
            done
            
            # Si aún está ejecutándose, forzar detención
            if kill -0 $pid 2>/dev/null; then
                log_warning "Forzando detención de $name..."
                kill -KILL $pid
                sleep 1
            fi
            
            if ! kill -0 $pid 2>/dev/null; then
                log_success "$name detenido"
                rm -f "$pid_file"
            else
                log_error "No se pudo detener $name"
                return 1
            fi
        else
            log_warning "$name no estaba ejecutándose"
            rm -f "$pid_file"
        fi
    else
        log_warning "Archivo PID no encontrado para $name"
    fi
}

# Función para detener contenedor Docker
stop_docker_container() {
    local container_name=$1
    local display_name=$2
    
    if docker ps --format "{{.Names}}" | grep -q "$container_name"; then
        log_info "Deteniendo $display_name..."
        docker stop "$container_name" >/dev/null 2>&1
        docker rm "$container_name" >/dev/null 2>&1
        log_success "$display_name detenido"
    else
        log_warning "$display_name no estaba ejecutándose"
    fi
}

# Función para detener todos los servicios
stop_all_services() {
    log_info "Deteniendo todos los servicios de monitoreo..."
    
    # Cambiar al directorio del script
    cd "$(dirname "$0")"
    
    # Detener servicios Python
    stop_process "Metrics Collector" "logs/metrics_collector.pid"
    stop_process "Alert Manager" "logs/alert_manager.pid"
    stop_process "Monitoring Dashboard" "logs/monitoring_dashboard.pid"
    
    # Detener contenedores Docker
    if command -v docker &> /dev/null; then
        stop_docker_container "shaili-grafana" "Grafana"
        stop_docker_container "shaili-prometheus" "Prometheus"
        
        # Eliminar red Docker si no hay contenedores
        if ! docker ps --format "{{.Names}}" | grep -q "shaili-"; then
            docker network rm shaili-monitoring 2>/dev/null || true
            log_info "Red Docker eliminada"
        fi
    else
        log_warning "Docker no disponible"
    fi
}

# Función para verificar si hay servicios ejecutándose
check_running_services() {
    local running=0
    
    # Verificar procesos Python
    if pgrep -f "metrics_collector.py" > /dev/null; then
        log_warning "Metrics Collector está ejecutándose"
        running=1
    fi
    
    if pgrep -f "monitoring_dashboard.py" > /dev/null; then
        log_warning "Monitoring Dashboard está ejecutándose"
        running=1
    fi
    
    if pgrep -f "alert_manager.py" > /dev/null; then
        log_warning "Alert Manager está ejecutándose"
        running=1
    fi
    
    # Verificar contenedores Docker
    if command -v docker &> /dev/null; then
        if docker ps --format "{{.Names}}" | grep -q "shaili-"; then
            log_warning "Contenedores Docker están ejecutándose"
            running=1
        fi
    fi
    
    return $running
}

# Función para limpiar archivos temporales
cleanup_temp_files() {
    log_info "Limpiando archivos temporales..."
    
    # Eliminar archivos PID
    rm -f logs/*.pid
    
    # Eliminar archivos de lock si existen
    rm -f logs/*.lock
    
    # Limpiar logs antiguos (más de 30 días)
    find logs/ -name "*.log" -mtime +30 -delete 2>/dev/null || true
    
    log_success "Limpieza completada"
}

# Función para mostrar estado final
show_final_status() {
    echo ""
    log_info "Estado final del sistema:"
    echo "============================"
    
    # Verificar procesos Python
    if pgrep -f "metrics_collector.py" > /dev/null; then
        log_error "Metrics Collector: AÚN EJECUTÁNDOSE"
    else
        log_success "Metrics Collector: Detenido"
    fi
    
    if pgrep -f "monitoring_dashboard.py" > /dev/null; then
        log_error "Monitoring Dashboard: AÚN EJECUTÁNDOSE"
    else
        log_success "Monitoring Dashboard: Detenido"
    fi
    
    if pgrep -f "alert_manager.py" > /dev/null; then
        log_error "Alert Manager: AÚN EJECUTÁNDOSE"
    else
        log_success "Alert Manager: Detenido"
    fi
    
    # Verificar contenedores Docker
    if command -v docker &> /dev/null; then
        if docker ps --format "{{.Names}}" | grep -q "shaili-"; then
            log_error "Contenedores Docker: AÚN EJECUTÁNDOSE"
            docker ps --filter "name=shaili-"
        else
            log_success "Contenedores Docker: Detenidos"
        fi
    fi
    
    echo ""
}

# Función para mostrar información de puertos
show_port_status() {
    echo ""
    log_info "Estado de puertos:"
    echo "==================="
    
    local ports=("8050" "9090" "3100")
    for port in "${ports[@]}"; do
        if netstat -tlnp 2>/dev/null | grep ":$port " > /dev/null; then
            log_warning "Puerto $port: EN USO"
        else
            log_success "Puerto $port: Libre"
        fi
    done
    
    echo ""
}

# Función principal
main() {
    echo "🛑 Deteniendo Sistema de Monitoreo Shaili AI"
    echo "==========================================="
    echo ""
    
    # Verificar si hay servicios ejecutándose
    if ! check_running_services; then
        log_info "No hay servicios de monitoreo ejecutándose"
        show_port_status
        exit 0
    fi
    
    # Preguntar confirmación
    echo -e "${YELLOW}¿Está seguro de que desea detener todos los servicios de monitoreo?${NC}"
    read -p "Esto detendrá Metrics Collector, Alert Manager, Dashboard, Prometheus y Grafana (y/N): " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        log_info "Operación cancelada"
        exit 0
    fi
    
    # Detener todos los servicios
    stop_all_services
    
    # Limpiar archivos temporales
    cleanup_temp_files
    
    # Mostrar estado final
    show_final_status
    
    # Mostrar estado de puertos
    show_port_status
    
    log_success "Sistema de monitoreo detenido correctamente"
    echo ""
    echo -e "${YELLOW}Para reiniciar el sistema, ejecute:${NC} ./start_monitoring.sh"
    echo ""
}

# Función para mostrar ayuda
show_help() {
    echo "Uso: $0 [OPCIONES]"
    echo ""
    echo "Opciones:"
    echo "  -h, --help     Mostrar esta ayuda"
    echo "  -f, --force    Detener sin confirmación"
    echo "  -s, --status   Solo mostrar estado"
    echo ""
    echo "Ejemplos:"
    echo "  $0              Detener con confirmación"
    echo "  $0 --force      Detener sin confirmación"
    echo "  $0 --status     Solo mostrar estado"
}

# Procesar argumentos
FORCE=false
STATUS_ONLY=false

while [[ $# -gt 0 ]]; do
    case $1 in
        -h|--help)
            show_help
            exit 0
            ;;
        -f|--force)
            FORCE=true
            shift
            ;;
        -s|--status)
            STATUS_ONLY=true
            shift
            ;;
        *)
            echo "Opción desconocida: $1"
            show_help
            exit 1
            ;;
    esac
done

# Si solo se quiere mostrar estado
if [ "$STATUS_ONLY" = true ]; then
    echo "📊 Estado del Sistema de Monitoreo Shaili AI"
    echo "==========================================="
    echo ""
    check_running_services
    show_final_status
    show_port_status
    exit 0
fi

# Ejecutar función principal
main "$@"
