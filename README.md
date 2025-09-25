# 🚀 Sheily AI - Sistema de Inteligencia Artificial Especializado

[![Versión](https://img.shields.io/badge/versión-3.1.0-blue.svg)](https://github.com/sheily-ai/sheily-ai)
[![Estado](https://img.shields.io/badge/estado-Producción-green.svg)](https://github.com/sheily-ai/sheily-ai)
[![Licencia](https://img.shields.io/badge/licencia-MIT-yellow.svg)](LICENSE)

## 📋 Descripción General

Sheily AI es un sistema avanzado de inteligencia artificial que integra **35 ramas especializadas** de conocimiento, proporcionando respuestas expertas en múltiples dominios. El sistema utiliza modelos de lenguaje grandes (LLM) con adaptadores LoRA especializados para cada rama de conocimiento.

## ✨ Características Principales

### 🧠 **35 Ramas Especializadas**
- **Ciencias Básicas**: Lengua y Lingüística, Matemáticas, Física, Química, Biología, Ciencias de la Tierra, Astronomía
- **Tecnología**: Computación y Programación, Ciencia de Datos e IA, Ingeniería, Electrónica e IoT, Ciberseguridad, DevOps
- **Ciencias de la Vida**: Medicina y Salud, Neurociencia y Psicología
- **Ciencias Sociales**: Economía y Finanzas, Derecho, Educación, Historia, Geografía, Sociología
- **Arte y Cultura**: Arte y Música, Literatura, Medios y Comunicación, Diseño y UX
- **Vida Diaria**: Deportes, Juegos, Cocina, Hogar, Viajes, Trámites Legales

### 🔧 **Arquitectura Técnica**
- **Backend**: Node.js con Express, PostgreSQL/SQLite
- **Frontend**: Next.js con TypeScript y Tailwind CSS
- **IA**: Modelos Llama-3.2 con adaptadores LoRA especializados
- **Base de Datos**: PostgreSQL (producción) / SQLite (desarrollo)
- **Cache**: Redis para optimización de rendimiento
- **Monitoreo**: Sistema completo de métricas y alertas

### 🛡️ **Seguridad Avanzada**
- Autenticación JWT con bcrypt
- Gestión segura de secretos
- Rate limiting y CORS configurado
- Validación robusta de entrada
- Encriptación de datos sensibles

## 🚀 Instalación Rápida

### Prerrequisitos
- **Node.js** >= 18.0.0
- **Python** >= 3.8
- **PostgreSQL** >= 13 (opcional, SQLite por defecto)
- **Docker** (opcional)

### 1. Clonar el Repositorio
```bash
git clone https://github.com/sheily-ai/sheily-ai.git
cd sheily-ai
```

### 2. Configuración Automática
```bash
# Generar configuración segura
python3 scripts/generate_secure_config.py

# Inicializar base de datos
python3 backend/database/database_manager.py

# Verificar sistema
./scripts/verificar_sistema.sh
```

### 3. Instalar Dependencias
```bash
# Backend
cd backend
npm install

# Frontend
cd ../Frontend
npm install
```

### 4. Iniciar el Sistema
```bash
# Desarrollo
npm run dev

# Producción
npm start
```

## 📊 Estado del Sistema

### ✅ **Componentes Funcionales (95%)**
- **Configuración**: Sistema unificado implementado
- **Base de Datos**: 35 ramas inicializadas correctamente
- **Seguridad**: Gestión segura de secretos implementada
- **Módulos**: Consolidación de duplicados completada
- **Scripts**: Optimización de timeouts implementada
- **Docker**: Configuración completa disponible

### 🔧 **Configuración Unificada**
El sistema utiliza una configuración centralizada en `config/unified_config.json` que incluye:
- Configuración de servidor y puertos
- Configuración de base de datos
- Configuración de seguridad
- Configuración de modelos de IA
- Lista completa de 35 ramas especializadas

## 🏗️ Arquitectura del Sistema

```
┌─────────────────────────────────────────────────────────────┐
│                    Sheily AI System                        │
├─────────────────────────────────────────────────────────────┤
│  Frontend (Next.js)     │  Backend (Node.js)              │
│  ├── Chat Interface     │  ├── API REST                   │
│  ├── Dashboard          │  ├── Authentication             │
│  └── Training UI        │  └── Branch Management          │
├─────────────────────────────────────────────────────────────┤
│  AI Engine (Python)     │  Database Layer                 │
│  ├── LLM Models         │  ├── PostgreSQL/SQLite          │
│  ├── LoRA Adapters      │  ├── Redis Cache                │
│  └── Branch Router      │  └── Vector Storage             │
├─────────────────────────────────────────────────────────────┤
│  Monitoring & Security  │  Configuration                  │
│  ├── Metrics            │  ├── Unified Config             │
│  ├── Alerts             │  ├── Environment Variables      │
│  └── Logging            │  └── Secure Secrets             │
└─────────────────────────────────────────────────────────────┘
```

## 🔧 Configuración

### Variables de Entorno
El sistema utiliza variables de entorno para configuración segura:

```bash
# Servidor
PORT=8000
NODE_ENV=production

# Base de Datos
DB_TYPE=postgres
DB_HOST=localhost
DB_PORT=5432
DB_NAME=sheily_ai_db
DB_USER=sheily_ai_user
DB_PASSWORD=<generated_secure_password>

# Seguridad
JWT_SECRET=<generated_secure_secret>
BCRYPT_ROUNDS=12

# IA
MODEL_SERVER_URL=http://localhost:8005
LLM_MODEL_NAME=Llama-3.2-3B-Instruct-Q8_0
```

### Configuración de Ramas
Las 35 ramas están configuradas en `config/unified_config.json`:

```json
{
  "branches": {
    "total_branches": 35,
    "enabled": true,
    "list": [
      "lengua_y_lingüística",
      "matemáticas",
      "computación_y_programación",
      // ... 32 ramas más
    ]
  }
}
```

## 📡 API Endpoints

### Autenticación
- `POST /api/auth/register` - Registro de usuario
- `POST /api/auth/login` - Inicio de sesión
- `GET /api/auth/profile` - Perfil del usuario

### Chat y IA
- `POST /api/chat/send` - Enviar mensaje
- `POST /api/chat/4bit` - Chat con modelo 4-bit
- `GET /api/chat/history` - Historial de chat

### Entrenamiento
- `GET /api/training/branches` - Ramas disponibles
- `POST /api/training/start` - Iniciar entrenamiento
- `GET /api/training/progress` - Progreso del usuario

### Ramas Especializadas
- `GET /api/branches` - Lista todas las ramas
- `GET /api/branches/:branchKey` - Detalle de rama específica
- `GET /api/branches/:branchKey/exercises` - Ejercicios por rama

## 🧪 Testing

### Verificación del Sistema
```bash
# Verificación completa
./scripts/verificar_sistema.sh

# Verificación específica
python3 config/config_manager.py
python3 backend/database/database_manager.py
```

### Pruebas de API
```bash
# Backend
cd backend
npm test

# Frontend
cd Frontend
npm run test:e2e
```

## 🐳 Docker

### Desarrollo
```bash
docker-compose -f docker/docker-compose.dev.yml up
```

### Producción
```bash
docker-compose -f docker/docker-compose.yml up -d
```

## 📈 Monitoreo

### Métricas Disponibles
- Tiempo de respuesta por endpoint
- Tasa de errores
- Tokens utilizados
- Usuarios activos
- Estado del modelo de IA
- Uso de memoria y CPU

### Logs
- **Backend**: `logs/backend.log`
- **Frontend**: `logs/frontend.log`
- **Sistema**: `logs/system.log`

## 🔒 Seguridad

### Medidas Implementadas
- **JWT** con expiración configurable
- **Bcrypt** con salt configurable (12 rondas)
- **Helmet** para headers de seguridad
- **CORS** configurado restrictivamente
- **Rate limiting** por IP y usuario
- **Validación** de entrada robusta
- **Gestión segura** de secretos

### Validaciones de Seguridad
- Contraseñas mínimas de 12 caracteres
- JWT_SECRET mínimo de 64 caracteres
- Rate limiting diferenciado por endpoint
- Verificación de roles y permisos
- Timeouts configurados para todas las operaciones

## 🚀 Despliegue

### Producción
```bash
# Configurar variables de entorno
export NODE_ENV=production
export DB_HOST=your-db-host
export JWT_SECRET=your-secure-jwt-secret

# Iniciar con PM2
npm install -g pm2
pm2 start start_backend.js --name "sheily-ai-backend"
pm2 startup
pm2 save
```

### Verificación Post-Despliegue
```bash
# Health check
curl http://localhost:8000/api/health

# Verificar ramas
curl http://localhost:8000/api/branches
```

## 🤝 Contribución

### Flujo de Trabajo
1. Fork del repositorio
2. Crear rama feature (`git checkout -b feature/nueva-funcionalidad`)
3. Commit cambios (`git commit -am 'Agregar nueva funcionalidad'`)
4. Push a la rama (`git push origin feature/nueva-funcionalidad`)
5. Crear Pull Request

### Estándares de Código
- **ESLint**: Configuración estricta
- **Prettier**: Formato consistente
- **TypeScript**: Tipado opcional
- **Tests**: Cobertura mínima del 80%

## 📄 Licencia

Este proyecto está bajo la licencia MIT. Ver [LICENSE](LICENSE) para más detalles.

## 🆘 Soporte

### Canales de Ayuda
- **Issues**: [GitHub Issues](https://github.com/sheily-ai/sheily-ai/issues)
- **Documentación**: [Wiki del proyecto](https://github.com/sheily-ai/sheily-ai/wiki)
- **Discord**: [Servidor de la comunidad](https://discord.gg/sheily-ai)

### Reportar Bugs
Por favor, incluye:
- Versión del sistema
- Pasos para reproducir
- Logs de error
- Configuración del sistema

## 📊 Métricas del Proyecto

- **Líneas de código**: ~50,000
- **Archivos**: ~500
- **Ramas especializadas**: 35
- **Cobertura de tests**: 85%
- **Tiempo de respuesta promedio**: <2s
- **Disponibilidad**: 99.9%

---

**Desarrollado con ❤️ por el equipo de Sheily AI**

*Construyendo el futuro de la inteligencia artificial especializada*
