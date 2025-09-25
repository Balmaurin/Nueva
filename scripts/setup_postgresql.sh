#!/bin/bash

# Script para configurar PostgreSQL para Sheily AI
# ================================================

echo "🐘 Configurando PostgreSQL para Sheily AI..."
echo "=============================================="

# Variables de configuración
DB_NAME="sheily_ai_db"
DB_USER="sheily_ai_user"
DB_PASSWORD="aLntLq1vjQ^*t#H0Lxfwz5!B"

echo "📋 Configuración:"
echo "   - Base de datos: $DB_NAME"
echo "   - Usuario: $DB_USER"
echo "   - Host: localhost"
echo "   - Puerto: 5432"
echo ""

# Verificar si PostgreSQL está ejecutándose
if ! sudo systemctl is-active --quiet postgresql; then
    echo "🚀 Iniciando PostgreSQL..."
    sudo systemctl start postgresql
    if [ $? -eq 0 ]; then
        echo "✅ PostgreSQL iniciado correctamente"
    else
        echo "❌ Error iniciando PostgreSQL"
        exit 1
    fi
else
    echo "✅ PostgreSQL ya está ejecutándose"
fi

# Crear usuario y base de datos
echo ""
echo "👤 Creando usuario y base de datos..."

# Crear usuario
sudo -u postgres psql -c "CREATE USER $DB_USER WITH PASSWORD '$DB_PASSWORD';" 2>/dev/null
if [ $? -eq 0 ]; then
    echo "✅ Usuario '$DB_USER' creado exitosamente"
else
    echo "⚠️ Usuario '$DB_USER' ya existe o error en creación"
fi

# Crear base de datos
sudo -u postgres psql -c "CREATE DATABASE $DB_NAME OWNER $DB_USER;" 2>/dev/null
if [ $? -eq 0 ]; then
    echo "✅ Base de datos '$DB_NAME' creada exitosamente"
else
    echo "⚠️ Base de datos '$DB_NAME' ya existe o error en creación"
fi

# Otorgar permisos
sudo -u postgres psql -c "GRANT ALL PRIVILEGES ON DATABASE $DB_NAME TO $DB_USER;" 2>/dev/null
if [ $? -eq 0 ]; then
    echo "✅ Permisos otorgados al usuario '$DB_USER'"
else
    echo "⚠️ Error otorgando permisos"
fi

# Configurar autenticación local
echo ""
echo "🔐 Configurando autenticación..."

# Crear backup del archivo pg_hba.conf
sudo cp /etc/postgresql/*/main/pg_hba.conf /etc/postgresql/*/main/pg_hba.conf.backup 2>/dev/null

# Configurar autenticación para el usuario local
echo "local   $DB_NAME   $DB_USER   md5" | sudo tee -a /etc/postgresql/*/main/pg_hba.conf > /dev/null 2>&1

# Reiniciar PostgreSQL para aplicar cambios
echo "🔄 Reiniciando PostgreSQL..."
sudo systemctl restart postgresql

if [ $? -eq 0 ]; then
    echo "✅ PostgreSQL reiniciado correctamente"
else
    echo "❌ Error reiniciando PostgreSQL"
    exit 1
fi

# Probar conexión
echo ""
echo "🧪 Probando conexión..."
PGPASSWORD="$DB_PASSWORD" psql -h localhost -U "$DB_USER" -d "$DB_NAME" -c "SELECT version();" > /dev/null 2>&1

if [ $? -eq 0 ]; then
    echo "✅ Conexión a PostgreSQL exitosa"
    echo ""
    echo "🎉 PostgreSQL configurado correctamente para Sheily AI!"
    echo ""
    echo "📋 Información de conexión:"
    echo "   - Host: localhost"
    echo "   - Puerto: 5432"
    echo "   - Base de datos: $DB_NAME"
    echo "   - Usuario: $DB_USER"
    echo "   - Contraseña: $DB_PASSWORD"
    echo ""
    echo "🚀 Ahora puedes iniciar el backend de Sheily AI"
else
    echo "❌ Error en la conexión a PostgreSQL"
    echo "💡 Verifica la configuración manualmente"
    exit 1
fi
