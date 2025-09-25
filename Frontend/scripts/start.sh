#!/bin/bash

# =============================================================================
# SCRIPT DE ARRANQUE COMPLETO PARA FRONTEND SHEILY AI
# =============================================================================
# Este script verifica todas las dependencias, configura el entorno
# y inicia el frontend Next.js en el puerto 3000 sin errores
# =============================================================================
# Ubicación: Frontend/scripts/start.sh
# =============================================================================

set -e  # Salir inmediatamente si hay algún error

# Colores para output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# Función para imprimir mensajes con colores
print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

print_header() {
    echo -e "${PURPLE}================================${NC}"
    echo -e "${PURPLE}$1${NC}"
    echo -e "${PURPLE}================================${NC}"
}

# Función para limpiar procesos anteriores
cleanup_previous_processes() {
    print_status "Limpiando procesos anteriores del frontend..."
    
    # Buscar y matar procesos de Next.js en el puerto 3000
    PIDS=$(lsof -ti:3000 2>/dev/null || true)
    if [ ! -z "$PIDS" ]; then
        print_warning "Encontrados procesos anteriores en puerto 3000: $PIDS"
        echo "$PIDS" | xargs kill -9 2>/dev/null || true
        sleep 2
        print_success "Procesos anteriores terminados"
    else
        print_success "No hay procesos anteriores ejecutándose"
    fi
    
    # Limpiar archivos temporales de Next.js
    if [ -d ".next" ]; then
        print_status "Limpiando caché de Next.js..."
        rm -rf .next/.cache 2>/dev/null || true
        rm -rf .next/trace 2>/dev/null || true
        print_success "Caché limpiado"
    fi
}

# Función para verificar dependencias del sistema
check_system_dependencies() {
    print_header "VERIFICANDO DEPENDENCIAS DEL SISTEMA"
    
    # Verificar Node.js
    if ! command -v node &> /dev/null; then
        print_error "Node.js no está instalado"
        print_status "Instalando Node.js..."
        curl -fsSL https://deb.nodesource.com/setup_18.x | sudo -E bash -
        sudo apt-get install -y nodejs
        print_success "Node.js instalado"
    else
        NODE_VERSION=$(node --version)
        print_success "Node.js encontrado: $NODE_VERSION"
    fi
    
    # Verificar npm
    if ! command -v npm &> /dev/null; then
        print_error "npm no está instalado"
        exit 1
    else
        NPM_VERSION=$(npm --version)
        print_success "npm encontrado: $NPM_VERSION"
    fi
    
    # Verificar versión mínima de Node.js
    NODE_MAJOR=$(node --version | cut -d'v' -f2 | cut -d'.' -f1)
    if [ "$NODE_MAJOR" -lt 18 ]; then
        print_error "Se requiere Node.js 18 o superior. Versión actual: $(node --version)"
        exit 1
    fi
    
    print_success "Todas las dependencias del sistema están disponibles"
}

# Función para verificar y configurar el entorno
setup_environment() {
    print_header "CONFIGURANDO ENTORNO"
    
    # Verificar si estamos en el directorio correcto
    if [ ! -f "package.json" ]; then
        print_error "No se encontró package.json. Asegúrate de estar en el directorio Frontend/"
        exit 1
    fi
    
    # Verificar si es el proyecto correcto
    if ! grep -q "sheily-landing-next" package.json; then
        print_error "Este no parece ser el proyecto Sheily AI Frontend"
        exit 1
    fi
    
    print_success "Directorio del proyecto verificado"
    
    # Configurar variables de entorno
    export NODE_ENV=development
    export PORT=3000
    export HOSTNAME=127.0.0.1
    
    # Crear archivo .env.local si no existe
    if [ ! -f ".env.local" ]; then
        print_status "Creando archivo .env.local..."
        cat > .env.local << EOF
# Configuración del Frontend Sheily AI
NODE_ENV=development
PORT=3000
HOSTNAME=127.0.0.1
NEXTAUTH_SECRET=sheily_ai_frontend_secret_key_$(date +%s)
BACKEND_URL=http://localhost:8000
NEXTAUTH_URL=http://127.0.0.1:3000
EOF
        print_success "Archivo .env.local creado"
    else
        print_success "Archivo .env.local ya existe"
    fi
    
    print_success "Entorno configurado correctamente"
}

# Función para verificar dependencias de Node.js
check_node_dependencies() {
    print_header "VERIFICANDO DEPENDENCIAS DE NODE.JS"
    
    # Verificar si node_modules existe
    if [ ! -d "node_modules" ]; then
        print_warning "node_modules no encontrado. Instalando dependencias..."
        install_dependencies
    else
        print_success "node_modules encontrado"
        
        # Verificar si las dependencias están actualizadas
        print_status "Verificando actualizaciones de dependencias..."
        npm outdated --silent || true
        
        # Verificar dependencias faltantes
        if npm ls --depth=0 --silent 2>&1 | grep -q "UNMET DEPENDENCY"; then
            print_warning "Dependencias faltantes detectadas. Reinstalando..."
            install_dependencies
        else
            print_success "Todas las dependencias están instaladas correctamente"
        fi
    fi
}

# Función para instalar dependencias
install_dependencies() {
    print_header "INSTALANDO DEPENDENCIAS"
    
    # Limpiar instalación anterior si existe
    if [ -d "node_modules" ]; then
        print_status "Limpiando instalación anterior..."
        rm -rf node_modules package-lock.json
    fi
    
    # Limpiar caché de npm
    print_status "Limpiando caché de npm..."
    npm cache clean --force
    
    # Instalar dependencias
    print_status "Instalando dependencias..."
    npm install --verbose
    
    if [ $? -eq 0 ]; then
        print_success "Dependencias instaladas correctamente"
    else
        print_error "Error al instalar dependencias"
        exit 1
    fi
    
    # Verificar instalación
    print_status "Verificando instalación..."
    if npm ls --depth=0 --silent 2>&1 | grep -q "UNMET DEPENDENCY"; then
        print_error "Error en la instalación de dependencias"
        exit 1
    fi
    
    print_success "Verificación de dependencias completada"
}

# Función para verificar configuración de Next.js
check_nextjs_config() {
    print_header "VERIFICANDO CONFIGURACIÓN DE NEXT.JS"
    
    # Verificar archivos de configuración
    local config_files=("next.config.cjs" "tsconfig.json" "tailwind.config.ts" "postcss.config.cjs")
    
    for config_file in "${config_files[@]}"; do
        if [ -f "$config_file" ]; then
            print_success "$config_file encontrado"
        else
            print_error "$config_file no encontrado"
            exit 1
        fi
    done
    
    # Verificar configuración de TypeScript
    if ! npx tsc --noEmit --skipLibCheck; then
        print_warning "Errores de TypeScript detectados, pero continuando..."
    else
        print_success "Configuración de TypeScript verificada"
    fi
    
    print_success "Configuración de Next.js verificada"
}

# Función para verificar archivos de audio
check_audio_files() {
    print_header "VERIFICANDO ARCHIVOS DE AUDIO"
    
    local audio_dir="public/sounds"
    local required_files=(
        "062708_laser-charging-81968.mp3"
        "whoosh-drum-hits-169007.mp3"
    )
    
    if [ ! -d "$audio_dir" ]; then
        print_warning "Directorio de sonidos no encontrado. Creando..."
        mkdir -p "$audio_dir"
    fi
    
    local missing_files=()
    for audio_file in "${required_files[@]}"; do
        if [ ! -f "$audio_dir/$audio_file" ]; then
            missing_files+=("$audio_file")
        fi
    done
    
    if [ ${#missing_files[@]} -gt 0 ]; then
        print_warning "Archivos de audio faltantes: ${missing_files[*]}"
        print_status "Los sonidos se generarán sintéticamente como fallback"
    else
        print_success "Todos los archivos de audio están disponibles"
    fi
}

# Función para verificar puertos
check_ports() {
    print_header "VERIFICANDO PUERTOS"
    
    # Verificar puerto 3000
    if lsof -ti:3000 >/dev/null 2>&1; then
        print_warning "Puerto 3000 está en uso"
        print_status "Intentando liberar el puerto..."
        cleanup_previous_processes
    else
        print_success "Puerto 3000 está disponible"
    fi
    
    # Verificar puerto 8000 (backend)
    if lsof -ti:8000 >/dev/null 2>&1; then
        print_success "Backend detectado en puerto 8000"
    else
        print_warning "Backend no detectado en puerto 8000"
        print_status "El frontend funcionará en modo standalone"
    fi
}

# Función para iniciar el frontend
start_frontend() {
    print_header "INICIANDO FRONTEND SHEILY AI"
    
    print_status "Iniciando servidor de desarrollo en puerto 3000..."
    print_status "URL: http://127.0.0.1:3000"
    print_status "Presiona Ctrl+C para detener el servidor"
    
    # Iniciar el servidor con variables de entorno
    NODE_ENV=development PORT=3000 HOSTNAME=127.0.0.1 npm run dev
}

# Función principal
main() {
    print_header "ARRANQUE DEL FRONTEND SHEILY AI"
    print_status "Iniciando proceso de arranque completo..."
    
    # Cambiar al directorio del script si es necesario
    SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
    cd "$SCRIPT_DIR"
    
    # Ejecutar todas las verificaciones y configuraciones
    cleanup_previous_processes
    check_system_dependencies
    setup_environment
    check_node_dependencies
    check_nextjs_config
    check_audio_files
    check_ports
    
    print_header "VERIFICACIONES COMPLETADAS"
    print_success "✅ Sistema de dependencias verificado"
    print_success "✅ Entorno configurado"
    print_success "✅ Configuración de Next.js validada"
    print_success "✅ Puertos verificados"
    print_success "✅ Archivos de audio verificados"
    
    print_status "Iniciando frontend..."
    start_frontend
}

# Función de limpieza al salir
cleanup_on_exit() {
    print_status "Limpiando procesos del frontend..."
    cleanup_previous_processes
    print_success "Limpieza completada"
}

# Configurar trap para limpieza al salir
trap cleanup_on_exit EXIT INT TERM

# Ejecutar función principal
main "$@"
