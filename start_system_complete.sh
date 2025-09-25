#!/bin/bash
# ===========================================
# SCRIPT DE INICIO COMPLETO - SHEILY AI
# ===========================================
# Script que inicia todo el sistema de forma real
# SIN mocks, fallbacks ni simulaciones

set -e  # Salir si hay errores

echo "🚀 INICIANDO SISTEMA SHEILY AI COMPLETO"
echo "========================================"

# Colores para output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Función para imprimir mensajes
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

# Verificar que estamos en el directorio correcto
if [ ! -f "package.json" ] && [ ! -d "Frontend" ]; then
    print_error "No se encontró el proyecto Sheily AI. Ejecutar desde el directorio raíz."
    exit 1
fi

print_status "Verificando sistema..."

# 1. Verificar dependencias del sistema
print_status "Verificando dependencias del sistema..."
if ! command -v node &> /dev/null; then
    print_error "Node.js no está instalado"
    exit 1
fi

if ! command -v npm &> /dev/null; then
    print_error "npm no está instalado"
    exit 1
fi

if ! command -v python3 &> /dev/null; then
    print_error "Python3 no está instalado"
    exit 1
fi

print_success "Dependencias del sistema verificadas"

# 2. Verificar configuración de seguridad
print_status "Verificando configuración de seguridad..."
if [ -f "backend/config.env" ]; then
    print_warning "config.env encontrado - moviendo a backup por seguridad"
    mv backend/config.env backend/config.env.backup
fi

if [ ! -f "backend/config.env.example" ]; then
    print_error "config.env.example no encontrado"
    exit 1
fi

print_success "Configuración de seguridad verificada"

# 3. Instalar dependencias del frontend
print_status "Instalando dependencias del frontend..."
cd Frontend

if [ ! -d "node_modules" ]; then
    print_status "Instalando dependencias de Node.js..."
    npm install --force
    if [ $? -ne 0 ]; then
        print_error "Error instalando dependencias del frontend"
        exit 1
    fi
else
    print_success "Dependencias del frontend ya instaladas"
fi

# 4. Verificar configuración del frontend
print_status "Verificando configuración del frontend..."
if [ ! -f ".env.local" ]; then
    print_warning "Creando .env.local desde ejemplo..."
    cat > .env.local << EOF
# Configuraciones de NextAuth
NEXTAUTH_URL=http://localhost:3000
NEXTAUTH_SECRET=mTrIzAHkyQnHf3e+gSYdTTxQKw+y1brBAjRwXohXpUk=

# URLs de Backend
NEXT_PUBLIC_BACKEND_URL=http://localhost:8000
BACKEND_API_URL=http://localhost:8000/api

# Configuraciones de Entorno
NODE_ENV=development
EOF
fi

print_success "Configuración del frontend verificada"

# 5. Verificar estructura de datos
print_status "Verificando estructura de datos..."
cd ..

if [ ! -d "data/branches" ]; then
    print_error "Directorio data/branches no encontrado"
    exit 1
fi

# Contar ramas implementadas
BRANCH_COUNT=$(ls data/branches/branch_*_dataset.jsonl 2>/dev/null | wc -l)
if [ $BRANCH_COUNT -ne 35 ]; then
    print_warning "Se encontraron $BRANCH_COUNT ramas, se esperaban 35"
else
    print_success "Todas las 35 ramas están implementadas"
fi

# 6. Verificar bases de datos
print_status "Verificando bases de datos..."
DB_FILES=("knowledge_base.db" "embeddings_sqlite.db" "rag_memory.duckdb" "user_data.duckdb" "metrics.db")
for db_file in "${DB_FILES[@]}"; do
    if [ -f "data/$db_file" ]; then
        print_success "Base de datos $db_file encontrada"
    else
        print_warning "Base de datos $db_file no encontrada"
    fi
done

# 7. Ejecutar verificación de seguridad
print_status "Ejecutando verificación de seguridad..."
if [ -f "scripts/security_validator.py" ]; then
    python3 scripts/security_validator.py
    if [ $? -ne 0 ]; then
        print_warning "Se encontraron vulnerabilidades de seguridad"
    else
        print_success "Verificación de seguridad completada"
    fi
fi

# 8. Ejecutar verificación del sistema
print_status "Ejecutando verificación del sistema..."
if [ -f "scripts/optimized_system_verifier.py" ]; then
    python3 scripts/optimized_system_verifier.py
    if [ $? -ne 0 ]; then
        print_error "Verificación del sistema falló"
        exit 1
    else
        print_success "Verificación del sistema completada"
    fi
fi

# 9. Iniciar servicios
print_status "Iniciando servicios..."

# Iniciar backend en background
print_status "Iniciando backend..."
cd backend
if [ -f "server.js" ]; then
    # Verificar si ya está ejecutándose
    if pgrep -f "node server.js" > /dev/null; then
        print_warning "Backend ya está ejecutándose"
    else
        nohup node server.js > ../logs/backend.log 2>&1 &
        BACKEND_PID=$!
        echo $BACKEND_PID > ../logs/backend.pid
        print_success "Backend iniciado con PID $BACKEND_PID"
    fi
else
    print_error "server.js no encontrado"
    exit 1
fi

# Esperar a que el backend esté listo
print_status "Esperando a que el backend esté listo..."
for i in {1..30}; do
    if curl -s http://localhost:8000/api/health > /dev/null 2>&1; then
        print_success "Backend está listo"
        break
    fi
    if [ $i -eq 30 ]; then
        print_error "Backend no respondió después de 30 segundos"
        exit 1
    fi
    sleep 1
done

# Iniciar frontend
print_status "Iniciando frontend..."
cd ../Frontend
if [ -f "package.json" ]; then
    # Verificar si ya está ejecutándose
    if pgrep -f "next dev" > /dev/null; then
        print_warning "Frontend ya está ejecutándose"
    else
        nohup npm run dev > ../logs/frontend.log 2>&1 &
        FRONTEND_PID=$!
        echo $FRONTEND_PID > ../logs/frontend.pid
        print_success "Frontend iniciado con PID $FRONTEND_PID"
    fi
else
    print_error "package.json no encontrado"
    exit 1
fi

# Esperar a que el frontend esté listo
print_status "Esperando a que el frontend esté listo..."
for i in {1..60}; do
    if curl -s http://localhost:3000 > /dev/null 2>&1; then
        print_success "Frontend está listo"
        break
    fi
    if [ $i -eq 60 ]; then
        print_error "Frontend no respondió después de 60 segundos"
        exit 1
    fi
    sleep 1
done

# 10. Verificación final
print_status "Ejecutando verificación final..."
cd ..

# Verificar que ambos servicios estén ejecutándose
if pgrep -f "node server.js" > /dev/null && pgrep -f "next dev" > /dev/null; then
    print_success "Ambos servicios están ejecutándose"
else
    print_error "Algunos servicios no están ejecutándose"
    exit 1
fi

# 11. Mostrar información de acceso
echo ""
echo "🎉 SISTEMA SHEILY AI INICIADO EXITOSAMENTE"
echo "=========================================="
echo ""
echo "🌐 URLs de acceso:"
echo "  Frontend: http://localhost:3000"
echo "  Backend:  http://localhost:8000"
echo "  API Health: http://localhost:8000/api/health"
echo ""
echo "📊 Estado de servicios:"
echo "  Backend PID: $(cat logs/backend.pid 2>/dev/null || echo 'N/A')"
echo "  Frontend PID: $(cat logs/frontend.pid 2>/dev/null || echo 'N/A')"
echo ""
echo "📝 Logs:"
echo "  Backend: logs/backend.log"
echo "  Frontend: logs/frontend.log"
echo ""
echo "🛑 Para detener el sistema:"
echo "  ./stop_system.sh"
echo ""
echo "✅ Sistema listo para usar - SIN mocks, fallbacks ni simulaciones"
