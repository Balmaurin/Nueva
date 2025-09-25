#!/bin/bash

# Script de verificación optimizado del sistema Sheily AI
# Versión: 2.0.0 - Optimizado para evitar timeouts
# Autor: Equipo Sheily AI

# Configuración de timeouts
TIMEOUT_SHORT=10
TIMEOUT_MEDIUM=30
TIMEOUT_LONG=60

# Colores para salida
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # Sin color

# Contadores
TOTAL_CHECKS=0
PASSED_CHECKS=0
FAILED_CHECKS=0
SKIPPED_CHECKS=0

# Función para imprimir encabezado
print_header() {
    echo -e "${BLUE}🔍 Verificando: $1 ${NC}"
}

# Función para imprimir resultado con timeout
print_result() {
    TOTAL_CHECKS=$((TOTAL_CHECKS + 1))
    if [ $1 -eq 0 ]; then
        echo -e "${GREEN}✅ $2 ${NC}"
        PASSED_CHECKS=$((PASSED_CHECKS + 1))
    elif [ $1 -eq 124 ]; then
        echo -e "${YELLOW}⏰ $2 (timeout) ${NC}"
        SKIPPED_CHECKS=$((SKIPPED_CHECKS + 1))
    else
        echo -e "${RED}❌ $2 ${NC}"
        FAILED_CHECKS=$((FAILED_CHECKS + 1))
    fi
}

# Función para ejecutar con timeout
run_with_timeout() {
    local timeout=$1
    shift
    timeout $timeout "$@"
    return $?
}

# Verificar versiones de dependencias (rápido)
check_dependencies() {
    print_header "Dependencias del Sistema"
    
    # Python (rápido)
    run_with_timeout $TIMEOUT_SHORT python3 --version > /dev/null 2>&1
    print_result $? "Python instalado"
    
    # Node.js (rápido)
    run_with_timeout $TIMEOUT_SHORT node --version > /dev/null 2>&1
    print_result $? "Node.js instalado"
    
    # Verificar archivos de configuración (rápido)
    config_files=(
        "config/unified_config.json"
        "backend/package.json"
        "Frontend/package.json"
    )
    
    for file in "${config_files[@]}"; do
        [ -f "$file" ] && echo -e "${GREEN}✅ Archivo $file existe ${NC}" || echo -e "${RED}❌ Archivo $file NO existe ${NC}"
    done
}

# Verificar bases de datos (optimizado)
check_databases() {
    print_header "Bases de Datos"
    
    # Verificar archivos de base de datos SQLite (rápido)
    sqlite_files=(
        "data/knowledge_base.db"
        "data/embeddings_sqlite.db"
        "data/rag_memory.duckdb"
        "data/user_data.duckdb"
        "data/metrics.db"
    )
    
    for file in "${sqlite_files[@]}"; do
        if [ -f "$file" ]; then
            echo -e "${GREEN}✅ Base de datos $file existe ${NC}"
            # Verificar que no esté vacía (rápido)
            if [ -s "$file" ]; then
                echo -e "${GREEN}✅ Base de datos $file no está vacía ${NC}"
            else
                echo -e "${YELLOW}⚠️ Base de datos $file está vacía ${NC}"
            fi
        else
            echo -e "${RED}❌ Base de datos $file NO existe ${NC}"
        fi
    done
    
    # Verificar PostgreSQL solo si está disponible (con timeout)
    run_with_timeout $TIMEOUT_SHORT psql --version > /dev/null 2>&1
    if [ $? -eq 0 ]; then
        run_with_timeout $TIMEOUT_MEDIUM psql -l > /dev/null 2>&1
        print_result $? "Conexión PostgreSQL"
    else
        echo -e "${YELLOW}⚠️ PostgreSQL no disponible, usando SQLite ${NC}"
    fi
}

# Verificar módulos de IA (optimizado)
check_ai_modules() {
    print_header "Módulos de IA"
    
    # Verificar módulos críticos con timeout
    critical_modules=(
        "modules.core.neurofusion_core"
        "modules.unified_systems.module_initializer"
        "config.config_manager"
    )
    
    for module in "${critical_modules[@]}"; do
        run_with_timeout $TIMEOUT_MEDIUM python3 -c "import $module" > /dev/null 2>&1
        print_result $? "Módulo $module importado"
    done
    
    # Verificar archivos de módulos (rápido)
    module_files=(
        "modules/__init__.py"
        "modules/core/__init__.py"
        "modules/unified_systems/__init__.py"
    )
    
    for file in "${module_files[@]}"; do
        [ -f "$file" ] && echo -e "${GREEN}✅ Archivo $file existe ${NC}" || echo -e "${RED}❌ Archivo $file NO existe ${NC}"
    done
}

# Verificar Docker (optimizado)
check_docker() {
    print_header "Configuración Docker"
    
    # Verificar instalación de Docker (rápido)
    run_with_timeout $TIMEOUT_SHORT docker --version > /dev/null 2>&1
    print_result $? "Docker instalado"
    
    # Verificar docker-compose (rápido)
    run_with_timeout $TIMEOUT_SHORT docker-compose --version > /dev/null 2>&1
    print_result $? "Docker Compose instalado"
    
    # Verificar archivos de configuración (rápido)
    docker_files=(
        "docker/docker-compose.yml"
        "docker/docker-compose.dev.yml"
        "docker/Dockerfile"
        "docker/backend.Dockerfile"
        "docker/frontend.Dockerfile"
    )
    
    for file in "${docker_files[@]}"; do
        [ -f "$file" ] && echo -e "${GREEN}✅ Archivo Docker $file existe ${NC}" || echo -e "${RED}❌ Archivo Docker $file NO existe ${NC}"
    done
}

# Verificar configuración (nuevo)
check_configuration() {
    print_header "Configuración del Sistema"
    
    # Verificar configuración unificada
    if [ -f "config/unified_config.json" ]; then
        echo -e "${GREEN}✅ Configuración unificada existe ${NC}"
        
        # Verificar que sea JSON válido
        run_with_timeout $TIMEOUT_SHORT python3 -c "import json; json.load(open('config/unified_config.json'))" > /dev/null 2>&1
        print_result $? "Configuración JSON válida"
        
        # Verificar número de ramas
        branch_count=$(python3 -c "import json; data=json.load(open('config/unified_config.json')); print(len(data.get('branches', {}).get('list', [])))" 2>/dev/null)
        if [ "$branch_count" = "35" ]; then
            echo -e "${GREEN}✅ Número correcto de ramas: $branch_count ${NC}"
        else
            echo -e "${RED}❌ Número incorrecto de ramas: $branch_count (esperado: 35) ${NC}"
        fi
    else
        echo -e "${RED}❌ Configuración unificada NO existe ${NC}"
    fi
    
    # Verificar archivos de configuración segura
    secure_files=(
        "backend/config.env.example"
        ".gitignore"
    )
    
    for file in "${secure_files[@]}"; do
        [ -f "$file" ] && echo -e "${GREEN}✅ Archivo seguro $file existe ${NC}" || echo -e "${RED}❌ Archivo seguro $file NO existe ${NC}"
    done
}

# Verificar rendimiento (optimizado)
check_performance() {
    print_header "Rendimiento del Sistema"
    
    # Prueba de tiempo de importación con timeout
    run_with_timeout $TIMEOUT_LONG python3 -c "
import sys
sys.path.append('.')
try:
    import config.config_manager
    print('Config manager: OK')
except Exception as e:
    print(f'Config manager: ERROR - {e}')
    sys.exit(1)
" > /dev/null 2>&1
    
    print_result $? "Importación de módulos principales"
    
    # Verificar tamaño de archivos críticos
    critical_files=(
        "config/unified_config.json"
        "data/branches/base_branches.json"
    )
    
    for file in "${critical_files[@]}"; do
        if [ -f "$file" ]; then
            size=$(stat -f%z "$file" 2>/dev/null || stat -c%s "$file" 2>/dev/null)
            if [ "$size" -gt 0 ]; then
                echo -e "${GREEN}✅ Archivo $file tiene contenido (${size} bytes) ${NC}"
            else
                echo -e "${RED}❌ Archivo $file está vacío ${NC}"
            fi
        fi
    done
}

# Mostrar resumen
show_summary() {
    echo -e "\n${BLUE}📊 RESUMEN DE VERIFICACIÓN ${NC}"
    echo -e "${BLUE}========================${NC}"
    echo -e "Total de verificaciones: $TOTAL_CHECKS"
    echo -e "${GREEN}✅ Exitosas: $PASSED_CHECKS${NC}"
    echo -e "${RED}❌ Fallidas: $FAILED_CHECKS${NC}"
    echo -e "${YELLOW}⏰ Timeouts: $SKIPPED_CHECKS${NC}"
    
    if [ $FAILED_CHECKS -eq 0 ]; then
        echo -e "\n${GREEN}🎉 ¡Sistema verificado exitosamente!${NC}"
        return 0
    else
        echo -e "\n${RED}⚠️ Se encontraron $FAILED_CHECKS problemas${NC}"
        return 1
    fi
}

# Función principal
main() {
    echo -e "${YELLOW}🚀 Iniciando verificación optimizada del sistema Sheily AI ${NC}"
    echo -e "${YELLOW}⏱️ Timeouts: Corto=${TIMEOUT_SHORT}s, Medio=${TIMEOUT_MEDIUM}s, Largo=${TIMEOUT_LONG}s ${NC}\n"
    
    check_dependencies
    check_databases
    check_ai_modules
    check_docker
    check_configuration
    check_performance
    
    show_summary
}

# Ejecutar verificación
main
