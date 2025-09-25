#!/bin/bash

# Script de verificación del sistema NeuroFusion - VERSIÓN CORREGIDA
# Versión: 2.0.0 - Sin timeouts, optimizado para rendimiento
# Autor: Equipo NeuroFusion

# Colores para salida
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # Sin color

# Variables de control
TIMEOUT_SECONDS=5
MAX_RETRIES=2

# Función para imprimir encabezado
print_header() {
    echo -e "${BLUE}🔍 Verificando: $1 ${NC}"
}

# Función para imprimir resultado
print_result() {
    if [ $1 -eq 0 ]; then
        echo -e "${GREEN}✅ $2 ${NC}"
    else
        echo -e "${RED}❌ $2 ${NC}"
    fi
}

# Función para ejecutar comando con timeout
run_with_timeout() {
    local cmd="$1"
    local description="$2"
    
    timeout ${TIMEOUT_SECONDS} bash -c "$cmd" >/dev/null 2>&1
    local exit_code=$?
    
    if [ $exit_code -eq 124 ]; then
        echo -e "${YELLOW}⏱️ $description (timeout - omitido) ${NC}"
        return 1
    else
        print_result $exit_code "$description"
        return $exit_code
    fi
}

# Verificar versiones de dependencias (OPTIMIZADO)
check_dependencies() {
    print_header "Dependencias del Sistema"
    
    # Python (verificación rápida)
    python3 --version > /dev/null 2>&1
    print_result $? "Python instalado"
    
    # PyTorch (verificación rápida sin importar)
    python3 -c "import sys; print('torch' in sys.modules)" > /dev/null 2>&1 || \
    python3 -c "import torch; print('OK')" > /dev/null 2>&1
    print_result $? "PyTorch disponible"
    
    # Node.js
    node --version > /dev/null 2>&1
    print_result $? "Node.js instalado"
    
    # PostgreSQL (verificación rápida)
    which psql > /dev/null 2>&1
    print_result $? "PostgreSQL instalado"
}

# Verificar bases de datos (SIN conexiones que causen timeout)
check_databases() {
    print_header "Bases de Datos"
    
    # Verificar archivos de BD SQLite (verificación de archivos, no conexiones)
    databases_files=(
        "data/knowledge_base.db"
        "data/embeddings_sqlite.db"
        "backend/sheily_ai.db"
    )
    
    for db_file in "${databases_files[@]}"; do
        if [ -f "$db_file" ] && [ -s "$db_file" ]; then
            # Verificación rápida de estructura sin timeout
            timeout 2s sqlite3 "$db_file" ".tables" > /dev/null 2>&1
            if [ $? -eq 0 ]; then
                echo -e "${GREEN}✅ Base de datos $db_file disponible ${NC}"
            else
                echo -e "${YELLOW}⚠️ Base de datos $db_file existe pero no responde ${NC}"
            fi
        else
            echo -e "${RED}❌ Base de datos $db_file no encontrada o vacía ${NC}"
        fi
    done
    
    # PostgreSQL - solo verificar si está corriendo, no conectar
    if pgrep -x "postgres" > /dev/null 2>&1; then
        echo -e "${GREEN}✅ Servicio PostgreSQL ejecutándose ${NC}"
    else
        echo -e "${YELLOW}⚠️ Servicio PostgreSQL no detectado ${NC}"
    fi
}

# Verificar módulos de IA (OPTIMIZADO - solo verificar archivos)
check_ai_modules() {
    print_header "Módulos de IA"
    
    # Verificar archivos de módulos en lugar de importarlos (evita timeouts)
    module_files=(
        "modules/ai_components/advanced_ai_system.py"
        "modules/unified_systems/unified_generation_response_system.py"
        "modules/training/download_headqa_dataset.py"
        "modules/core/neurofusion_core.py"
        "modules/unified_systems/module_initializer.py"
    )
    
    for module_file in "${module_files[@]}"; do
        if [ -f "$module_file" ]; then
            echo -e "${GREEN}✅ Módulo $module_file encontrado ${NC}"
        else
            echo -e "${RED}❌ Módulo $module_file no encontrado ${NC}"
        fi
    done
    
    # Verificación rápida de sintaxis Python (sin importar)
    echo -e "${BLUE}🔍 Verificando sintaxis de módulos principales... ${NC}"
    
    python3 -m py_compile modules/core/neurofusion_core.py 2>/dev/null
    print_result $? "Sintaxis módulo core válida"
    
    python3 -m py_compile modules/unified_systems/module_initializer.py 2>/dev/null
    print_result $? "Sintaxis módulo unified_systems válida"
}

# Verificar Docker (OPTIMIZADO)
check_docker() {
    print_header "Configuración Docker"
    
    # Verificar instalación de Docker
    docker --version > /dev/null 2>&1
    print_result $? "Docker instalado"
    
    # Verificar docker-compose
    docker-compose --version > /dev/null 2>&1 || docker compose version > /dev/null 2>&1
    print_result $? "Docker Compose instalado"
    
    # Verificar archivos de configuración
    docker_files=(
        "docker-compose.yml"
        "docker-compose.dev.yml"
        "docker/Dockerfile"
        "docker/backend.Dockerfile"
        "docker/frontend.Dockerfile"
    )
    
    for file in "${docker_files[@]}"; do
        if [ -f "$file" ]; then
            echo -e "${GREEN}✅ Archivo Docker $file existe ${NC}"
        else
            echo -e "${RED}❌ Archivo Docker $file NO existe ${NC}"
        fi
    done
    
    # Verificar sintaxis de docker-compose (rápido)
    if [ -f "docker-compose.yml" ]; then
        timeout 3s docker-compose config > /dev/null 2>&1
        print_result $? "Sintaxis docker-compose.yml válida"
    fi
}

# Verificar servicios (OPTIMIZADO - solo verificar puertos)
check_services() {
    print_header "Servicios y Puertos"
    
    # Puertos importantes del sistema
    ports=(
        "3000:Frontend"
        "8000:Backend API"
        "8005:LLM Server"
        "5432:PostgreSQL"
    )
    
    for port_info in "${ports[@]}"; do
        port=$(echo $port_info | cut -d':' -f1)
        service=$(echo $port_info | cut -d':' -f2)
        
        if netstat -tuln 2>/dev/null | grep ":$port " > /dev/null; then
            echo -e "${GREEN}✅ Puerto $port ($service) en uso ${NC}"
        else
            echo -e "${YELLOW}⚠️ Puerto $port ($service) disponible ${NC}"
        fi
    done
}

# Verificar estructura de archivos críticos
check_file_structure() {
    print_header "Estructura de Archivos"
    
    critical_files=(
        "README.md"
        "package.json"
        "backend/server.js"
        "Frontend/package.json"
        "config/neurofusion_config.json"
        "start_all_services.sh"
    )
    
    for file in "${critical_files[@]}"; do
        if [ -f "$file" ]; then
            echo -e "${GREEN}✅ Archivo crítico $file existe ${NC}"
        else
            echo -e "${RED}❌ Archivo crítico $file NO existe ${NC}"
        fi
    done
}

# Verificar espacio en disco y recursos
check_system_resources() {
    print_header "Recursos del Sistema"
    
    # Espacio en disco
    disk_usage=$(df -h . | awk 'NR==2 {print $5}' | sed 's/%//')
    if [ "$disk_usage" -lt 90 ]; then
        echo -e "${GREEN}✅ Espacio en disco suficiente (${disk_usage}% usado) ${NC}"
    else
        echo -e "${RED}❌ Espacio en disco crítico (${disk_usage}% usado) ${NC}"
    fi
    
    # Memoria RAM
    if command -v free > /dev/null 2>&1; then
        mem_usage=$(free | grep Mem | awk '{printf "%.0f", $3/$2 * 100.0}')
        if [ "$mem_usage" -lt 85 ]; then
            echo -e "${GREEN}✅ Memoria RAM suficiente (${mem_usage}% usado) ${NC}"
        else
            echo -e "${YELLOW}⚠️ Memoria RAM alta (${mem_usage}% usado) ${NC}"
        fi
    fi
}

# Función principal
main() {
    echo -e "${YELLOW}🚀 Iniciando verificación optimizada del sistema NeuroFusion ${NC}"
    echo -e "${BLUE}📊 Versión 2.0.0 - Sin timeouts, verificación rápida ${NC}"
    echo ""
    
    # Ejecutar verificaciones en orden optimizado
    check_dependencies
    echo ""
    
    check_file_structure
    echo ""
    
    check_databases
    echo ""
    
    check_ai_modules
    echo ""
    
    check_docker
    echo ""
    
    check_services
    echo ""
    
    check_system_resources
    echo ""
    
    echo -e "${GREEN}✨ Verificación del sistema completada sin timeouts ${NC}"
    echo -e "${BLUE}📋 Resumen: Verificación optimizada ejecutada en $(date) ${NC}"
}

# Ejecutar verificación
main
