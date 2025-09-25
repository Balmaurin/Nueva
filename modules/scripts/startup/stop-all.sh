#!/bin/bash

# Script para detener todos los servicios de Shaili AI
# Se puede ejecutar desde cualquier directorio del proyecto

echo "🛑 Deteniendo todos los servicios de Shaili AI..."

# Detener procesos de Node.js relacionados con el proyecto
echo "📋 Buscando procesos de Node.js..."

# Detener procesos de ts-node y nodemon
pkill -f "ts-node.*server" 2>/dev/null
pkill -f "nodemon.*server" 2>/dev/null

# Detener procesos de vite (frontend)
pkill -f "vite" 2>/dev/null

# Detener procesos de npm
pkill -f "npm.*run.*dev" 2>/dev/null

# Detener procesos que escuchan en los puertos específicos
echo "🔌 Liberando puertos..."

# Puerto 8000 (backend)
lsof -ti:8000 | xargs kill -9 2>/dev/null

# Puerto 3000 (frontend)
lsof -ti:3000 | xargs kill -9 2>/dev/null

echo "✅ Todos los servicios han sido detenidos"
echo "📍 Puertos liberados: 3000, 8000"
