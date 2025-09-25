#!/bin/bash

# Script de Inicio del Sistema de Monitoreo Shaili AI
# ===================================================

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

# Función para verificar dependencias
check_dependencies() {
    log_info "Verificando dependencias..."
    
    # Verificar Python
    if ! command -v python3 &> /dev/null; then
        log_error "Python3 no está instalado"
        exit 1
    fi
    
    # Verificar pip
    if ! command -v pip3 &> /dev/null; then
        log_error "pip3 no está instalado"
        exit 1
    fi
    
    # Verificar Docker (opcional)
    if ! command -v docker &> /dev/null; then
        log_warning "Docker no está instalado - algunas métricas no estarán disponibles"
    fi
    
    log_success "Dependencias verificadas"
}

# Función para instalar dependencias Python
install_python_deps() {
    log_info "Instalando dependencias Python..."
    
    pip3 install --quiet \
        dash \
        plotly \
        pandas \
        psutil \
        requests \
        sqlite3 \
        numpy \
        scipy \
        matplotlib
    
    log_success "Dependencias Python instaladas"
}

# Función para crear directorios necesarios
create_directories() {
    log_info "Creando directorios necesarios..."
    
    mkdir -p monitoring/logs
    mkdir -p monitoring/dashboards
    mkdir -p monitoring/cache
    
    log_success "Directorios creados"
}

# Función para verificar si los servicios ya están ejecutándose
check_running_services() {
    log_info "Verificando servicios en ejecución..."
    
    # Verificar si el collector ya está ejecutándose
    if pgrep -f "metrics_collector.py" > /dev/null; then
        log_warning "Metrics Collector ya está ejecutándose"
        return 1
    fi
    
    # Verificar si el dashboard ya está ejecutándose
    if pgrep -f "monitoring_dashboard.py" > /dev/null; then
        log_warning "Monitoring Dashboard ya está ejecutándose"
        return 1
    fi
    
    # Verificar si el alert manager ya está ejecutándose
    if pgrep -f "alert_manager.py" > /dev/null; then
        log_warning "Alert Manager ya está ejecutándose"
        return 1
    fi
    
    log_success "No hay servicios de monitoreo ejecutándose"
    return 0
}

# Función para iniciar Metrics Collector
start_metrics_collector() {
    log_info "Iniciando Metrics Collector..."
    
    cd "$(dirname "$0")"
    
    # Iniciar en background
    nohup python3 metrics_collector.py > logs/metrics_collector.log 2>&1 &
    COLLECTOR_PID=$!
    
    # Esperar un momento para verificar que inició correctamente
    sleep 3
    
    if kill -0 $COLLECTOR_PID 2>/dev/null; then
        log_success "Metrics Collector iniciado (PID: $COLLECTOR_PID)"
        echo $COLLECTOR_PID > logs/metrics_collector.pid
    else
        log_error "Error iniciando Metrics Collector"
        exit 1
    fi
}

# Función para iniciar Alert Manager
start_alert_manager() {
    log_info "Iniciando Alert Manager..."
    
    cd "$(dirname "$0")"
    
    # Iniciar en background
    nohup python3 alert_manager.py > logs/alert_manager.log 2>&1 &
    ALERT_PID=$!
    
    # Esperar un momento para verificar que inició correctamente
    sleep 2
    
    if kill -0 $ALERT_PID 2>/dev/null; then
        log_success "Alert Manager iniciado (PID: $ALERT_PID)"
        echo $ALERT_PID > logs/alert_manager.pid
    else
        log_error "Error iniciando Alert Manager"
        exit 1
    fi
}

# Función para iniciar Monitoring Dashboard
start_monitoring_dashboard() {
    log_info "Iniciando Monitoring Dashboard..."
    
    cd "$(dirname "$0")"
    
    # Iniciar en background
    nohup python3 monitoring_dashboard.py > logs/monitoring_dashboard.log 2>&1 &
    DASHBOARD_PID=$!
    
    # Esperar un momento para verificar que inició correctamente
    sleep 5
    
    if kill -0 $DASHBOARD_PID 2>/dev/null; then
        log_success "Monitoring Dashboard iniciado (PID: $DASHBOARD_PID)"
        echo $DASHBOARD_PID > logs/monitoring_dashboard.pid
    else
        log_error "Error iniciando Monitoring Dashboard"
        exit 1
    fi
}

# Función para iniciar Prometheus (Docker)
start_prometheus() {
    log_info "Iniciando Prometheus..."
    
    if ! command -v docker &> /dev/null; then
        log_warning "Docker no disponible - saltando Prometheus"
        return
    fi
    
    # Verificar si Prometheus ya está ejecutándose
    if docker ps --format "{{.Names}}" | grep -q "shaili-prometheus"; then
        log_warning "Prometheus ya está ejecutándose"
        return
    fi
    
    # Crear red Docker si no existe
    docker network create shaili-monitoring 2>/dev/null || true
    
    # Iniciar Prometheus
    docker run -d \
        --name shaili-prometheus \
        --network shaili-monitoring \
        -p 9090:9090 \
        -v "$(pwd)/prometheus.yml:/etc/prometheus/prometheus.yml" \
        prom/prometheus:v2.45.0 \
        --config.file=/etc/prometheus/prometheus.yml \
        --storage.tsdb.path=/prometheus \
        --web.console.libraries=/etc/prometheus/console_libraries \
        --web.console.templates=/etc/prometheus/consoles \
        --storage.tsdb.retention.time=200h \
        --web.enable-lifecycle
    
    log_success "Prometheus iniciado"
}

# Función para iniciar Grafana (Docker)
start_grafana() {
    log_info "Iniciando Grafana..."
    
    if ! command -v docker &> /dev/null; then
        log_warning "Docker no disponible - saltando Grafana"
        return
    fi
    
    # Verificar si Grafana ya está ejecutándose
    if docker ps --format "{{.Names}}" | grep -q "shaili-grafana"; then
        log_warning "Grafana ya está ejecutándose"
        return
    fi
    
    # Crear directorio para datos de Grafana
    mkdir -p grafana_data
    
    # Iniciar Grafana
    docker run -d \
        --name shaili-grafana \
        --network shaili-monitoring \
        -p 3100:3000 \
        -e GF_SECURITY_ADMIN_PASSWORD=shaili_grafana_admin \
        -e GF_USERS_ALLOW_SIGN_UP=false \
        -v "$(pwd)/grafana_data:/var/lib/grafana" \
        -v "$(pwd)/dashboards:/etc/grafana/provisioning/dashboards" \
        grafana/grafana:9.5.3
    
    log_success "Grafana iniciado"
}

# Función para verificar estado de servicios
check_services_status() {
    log_info "Verificando estado de servicios..."
    
    # Verificar Metrics Collector
    if [ -f logs/metrics_collector.pid ]; then
        COLLECTOR_PID=$(cat logs/metrics_collector.pid)
        if kill -0 $COLLECTOR_PID 2>/dev/null; then
            log_success "Metrics Collector: Ejecutándose (PID: $COLLECTOR_PID)"
        else
            log_error "Metrics Collector: No está ejecutándose"
        fi
    fi
    
    # Verificar Alert Manager
    if [ -f logs/alert_manager.pid ]; then
        ALERT_PID=$(cat logs/alert_manager.pid)
        if kill -0 $ALERT_PID 2>/dev/null; then
            log_success "Alert Manager: Ejecutándose (PID: $ALERT_PID)"
        else
            log_error "Alert Manager: No está ejecutándose"
        fi
    fi
    
    # Verificar Monitoring Dashboard
    if [ -f logs/monitoring_dashboard.pid ]; then
        DASHBOARD_PID=$(cat logs/monitoring_dashboard.pid)
        if kill -0 $DASHBOARD_PID 2>/dev/null; then
            log_success "Monitoring Dashboard: Ejecutándose (PID: $DASHBOARD_PID)"
        else
            log_error "Monitoring Dashboard: No está ejecutándose"
        fi
    fi
    
    # Verificar Prometheus
    if docker ps --format "{{.Names}}" | grep -q "shaili-prometheus"; then
        log_success "Prometheus: Ejecutándose"
    else
        log_warning "Prometheus: No está ejecutándose"
    fi
    
    # Verificar Grafana
    if docker ps --format "{{.Names}}" | grep -q "shaili-grafana"; then
        log_success "Grafana: Ejecutándose"
    else
        log_warning "Grafana: No está ejecutándose"
    fi
}

# Función para mostrar URLs de acceso
show_access_urls() {
    echo ""
    log_info "URLs de acceso al sistema de monitoreo:"
    echo "=========================================="
    echo -e "${GREEN}📊 Dashboard Principal:${NC} http://127.0.0.1:8050"
    echo -e "${GREEN}📈 Prometheus:${NC} http://127.0.0.1:9090"
    echo -e "${GREEN}📉 Grafana:${NC} http://127.0.0.1:3100"
    echo ""
    echo -e "${YELLOW}Credenciales de Grafana:${NC}"
    echo "Usuario: admin"
    echo "Contraseña: shaili_grafana_admin"
    echo ""
    echo -e "${BLUE}Logs disponibles en:${NC} monitoring/logs/"
    echo ""
}

# Función principal
main() {
    echo "🚀 Iniciando Sistema de Monitoreo Shaili AI"
    echo "=========================================="
    echo ""
    
    # Cambiar al directorio del script
    cd "$(dirname "$0")"
    
    # Verificar dependencias
    check_dependencies
    
    # Instalar dependencias Python si es necesario
    install_python_deps
    
    # Crear directorios
    create_directories
    
    # Verificar servicios en ejecución
    if ! check_running_services; then
        log_warning "Algunos servicios ya están ejecutándose"
        read -p "¿Desea continuar? (y/N): " -n 1 -r
        echo
        if [[ ! $REPLY =~ ^[Yy]$ ]]; then
            log_info "Operación cancelada"
            exit 0
        fi
    fi
    
    # Iniciar servicios
    start_metrics_collector
    start_alert_manager
    start_monitoring_dashboard
    
    # Iniciar servicios Docker (opcionales)
    start_prometheus
    start_grafana
    
    # Esperar un momento para que todos los servicios se inicialicen
    sleep 5
    
    # Verificar estado final
    check_services_status
    
    # Mostrar URLs de acceso
    show_access_urls
    
    log_success "Sistema de monitoreo iniciado correctamente"
    echo ""
    echo -e "${YELLOW}Para detener el sistema, ejecute:${NC} ./stop_monitoring.sh"
    echo ""
}

# Ejecutar función principal
main "$@"
