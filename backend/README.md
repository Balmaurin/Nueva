# 🚀 Sheily AI Backend

Backend completo y funcional para el sistema de IA inteligente Sheily AI, con autenticación segura, chat con modelos 4-bit y 16-bit, sistema de entrenamiento, y monitoreo en tiempo real.

## ✨ Características Principales

- 🔐 **Autenticación JWT Segura** con bcrypt y validación robusta
- 🧠 **Chat con IA** usando modelos Phi-3 (4-bit para chat, 16-bit para entrenamiento)
- 📊 **Dashboard Completo** con métricas reales y estadísticas
- 🎯 **Sistema de Entrenamiento** con 35 ramas especializadas
- 🧩 **Banco de Ejercicios Verificado** con CRUD completo por rama, validación del 95 % y generación de datasets listos para LoRA
- 💾 **Base de Datos PostgreSQL** con esquema optimizado
- 📈 **Monitoreo en Tiempo Real** via WebSocket
- 🚨 **Sistema de Alertas** automático por email
- 💾 **Backup Automático** con compresión y rotación
- 🛡️ **Seguridad Avanzada** con Helmet, CORS y rate limiting

## 🏗️ Arquitectura

```
backend/
├── server.js                 # Servidor principal Express
├── start_backend.js          # Script de inicio robusto
├── config.env               # Configuración segura
├── database/                # Esquema y migraciones PostgreSQL
├── models/                  # Servicios de modelo de IA
├── monitoring/              # Sistema de métricas y alertas
└── test_endpoints.py        # Pruebas completas del sistema
```

## 🚀 Instalación

### Prerrequisitos

- Node.js >= 18.0.0
- PostgreSQL >= 13
- Python 3.8+ (para modelos de IA)
- npm >= 8.0.0

### 1. Clonar y Instalar Dependencias

```bash
git clone https://github.com/sheily-ai/backend.git
cd backend
npm install
```

### 2. Configurar Base de Datos

```bash
# Crear usuario y base de datos
sudo -u postgres psql
CREATE USER sheily_ai_user WITH PASSWORD 'SheilyAI2025SecurePassword!';
CREATE DATABASE sheily_ai_db OWNER sheily_ai_user;
GRANT ALL PRIVILEGES ON DATABASE sheily_ai_db TO sheily_ai_user;
\q

# Inicializar esquema
npm run init-db

# Ejecutar migraciones (opcional)
npm run migrate
```

### Tablas clave del esquema

| Tabla | Descripción |
|-------|-------------|
| `branches` | Catálogo oficial de las 35 ramas con dominio, descripción y mapa de competencias |
| `branch_exercises` | Banco de ejercicios por rama, tipo y nivel con metadatos verificables |
| `branch_exercise_answers` | Respuestas oficiales, explicación y trazabilidad de validación |
| `branch_exercise_options` | Opciones normalizadas para ejercicios de respuesta múltiple |
| `user_branch_attempts` | Registro auditable de cada intento realizado por los usuarios |
| `user_branch_progress` | Estado agregado de progreso, tokens y validaciones por rama/nivel |

### 3. Configurar Variables de Entorno

```bash
cp config.env.example config.env
# Editar config.env con tus credenciales
```

### 4. Iniciar Servidor

```bash
# Desarrollo
npm run dev

# Producción
npm start
```

## 🔧 Configuración

### Variables de Entorno Críticas

```env
# Base de Datos
DB_HOST=localhost
DB_PORT=5432
DB_NAME=sheily_ai_db
DB_USER=sheily_ai_user
DB_PASSWORD=SheilyAI2025SecurePassword!

# Seguridad
JWT_SECRET=sheily-ai-jwt-secret-2025-ultra-secure-random-string-128-bits
BCRYPT_ROUNDS=12

# Servidor
PORT=8000
NODE_ENV=development

# Modelo de IA
MODEL_SERVER_URL=http://localhost:8001
MODEL_PATH=models/custom/sheily-ai-model

# Monitoreo
ALERT_EMAIL_USER=alerts@sheily-ai.com
ALERT_EMAIL_PASS=AlertPassword2025!
```

## 📡 Endpoints API

### 🔐 Autenticación

| Método | Endpoint | Descripción |
|--------|----------|-------------|
| `POST` | `/api/auth/register` | Registro de usuario |
| `POST` | `/api/auth/login` | Inicio de sesión |
| `GET` | `/api/auth/profile` | Perfil del usuario |
| `PUT` | `/api/auth/profile` | Actualizar perfil |
| `PUT` | `/api/auth/change-password` | Cambiar contraseña |
| `GET` | `/api/auth/tokens` | Tokens del usuario |
| `POST` | `/api/auth/logout` | Cerrar sesión |

### 🧠 Chat y Modelos

| Método | Endpoint | Descripción |
|--------|----------|-------------|
| `POST` | `/api/chat/session` | Crear sesión de chat |
| `POST` | `/api/chat/send` | Enviar mensaje |
| `POST` | `/api/chat/4bit` | Chat con modelo 4-bit |
| `GET` | `/api/chat/history` | Historial de chat |
| `GET` | `/api/chat/stats` | Estadísticas del chat |
| `GET` | `/api/models/available` | Modelos disponibles |

### 🎯 Entrenamiento

| Método | Endpoint | Descripción |
|--------|----------|-------------|
| `GET` | `/api/training/branches` | Ramas disponibles |
| `POST` | `/api/training/start` | Iniciar entrenamiento |
| `POST` | `/api/training/submit` | Enviar ejercicio |
| `GET` | `/api/training/session/:id` | Detalles de sesión |
| `GET` | `/api/training/branch-stats` | Estadísticas por rama |
| `GET` | `/api/training/progress` | Progreso del usuario |
| `GET` | `/api/training/dashboard` | Dashboard de entrenamiento |

### 🧩 Ejercicios por rama

> **Notas:** Estos endpoints requieren autenticación JWT. Las operaciones `POST`, `PUT` y `DELETE` sólo están disponibles para roles `admin`, `super_admin` o `editor` y necesitan una base de datos PostgreSQL activa (no SQLite).

| Método | Endpoint | Descripción |
|--------|----------|-------------|
| `GET` | `/api/branches` | Lista todas las ramas y, opcionalmente, el progreso del usuario autenticado |
| `GET` | `/api/branches/:branchKey` | Obtiene el detalle de una rama concreta y su progreso asociado |
| `GET` | `/api/branches/:branchKey/exercises` | Consulta ejercicios por rama con filtros por tipo, nivel y ámbito |
| `POST` | `/api/branches/:branchKey/exercises` | Crea un ejercicio oficial para la rama (requiere rol autorizado) |
| `PUT` | `/api/branches/:branchKey/exercises/:exerciseId` | Actualiza en bloque el ejercicio y sus opciones oficiales |
| `DELETE` | `/api/branches/:branchKey/exercises/:exerciseId` | Elimina un ejercicio y sus opciones asociadas |
| `GET` | `/api/branches/:branchKey/progress` | Recupera el progreso del usuario autenticado en la rama |
| `POST` | `/api/branches/:branchKey/progress` | Registra o valida un avance con métricas verificadas |
| `PUT` | `/api/branches/:branchKey/progress/:progressId` | Ajusta un registro de progreso existente |
| `DELETE` | `/api/branches/:branchKey/progress/:progressId` | Elimina el progreso del usuario para un nivel específico |

### 📊 Dashboard y Sistema

| Método | Endpoint | Descripción |
|--------|----------|-------------|
| `GET` | `/api/dashboard` | Dashboard principal |
| `GET` | `/api/system/status` | Estado del sistema |
| `GET` | `/api/system/logs` | Logs del sistema |
| `GET` | `/api/health` | Salud general |
| `GET` | `/api/chat/health` | Salud del chat |

### 🛡️ Administración

| Método | Endpoint | Descripción |
|--------|----------|-------------|
| `GET` | `/api/admin/chat/metrics` | Métricas del chat |
| `GET` | `/api/admin/chat/alerts` | Alertas del sistema |
| `GET` | `/api/admin/chat/backups` | Lista de backups |
| `POST` | `/api/admin/chat/backup` | Backup manual |

### 💰 Caja Fuerte

| Método | Endpoint | Descripción |
|--------|----------|-------------|
| `POST` | `/api/vault/authenticate` | Autenticación de caja fuerte |
| `GET` | `/api/vault/data` | Datos de la caja fuerte |
| `GET` | `/api/vault/transactions` | Transacciones |
| `POST` | `/api/vault/deposit` | Depósito |
| `POST` | `/api/vault/withdraw` | Retiro |

### 📝 Prompts

| Método | Endpoint | Descripción |
|--------|----------|-------------|
| `POST` | `/api/prompts` | Crear prompt |
| `GET` | `/api/prompts` | Listar prompts |
| `PUT` | `/api/prompts/:id` | Actualizar prompt |
| `DELETE` | `/api/prompts/:id` | Eliminar prompt |
| `POST` | `/api/prompts/evaluate` | Evaluar prompt |

## 🗄️ Base de Datos

### Esquema Principal

- **users**: Usuarios del sistema
- **user_tokens**: Tokens y créditos de usuario
- **training_sessions**: Sesiones de entrenamiento
- **training_exercises**: Ejercicios de entrenamiento
- **branch_exercises**: Banco de ejercicios por rama y ámbito
- **branch_exercise_answers**: Respuestas oficiales asociadas a cada ejercicio
- **chat_sessions**: Sesiones de chat
- **chat_messages**: Mensajes de chat
- **chat_conversations**: Conversaciones completas
- **model_registry**: Registro de modelos de IA
- **model_training_metrics**: Métricas de entrenamiento
- **prompts**: Prompts del sistema
- **vault_transactions**: Transacciones de caja fuerte

### Funciones PL/pgSQL

- `insert_training_metrics()`: Insertar métricas de entrenamiento
- `update_model_registry()`: Actualizar registro de modelos
- `generate_training_sessions()`: Generar sesiones de entrenamiento
- `get_training_statistics()`: Obtener estadísticas reales
- `cleanup_training_data()`: Limpiar datos de entrenamiento

### Generación de ejercicios por rama

Para crear o actualizar los ejercicios oficiales de las 35 macro-ramas ejecuta:

```bash
python scripts/generate_branch_exercises.py --levels 20
```

El script recorre cada rama y ámbito configurado, genera preguntas de los tres
tipos soportados y almacena tanto los enunciados como sus respuestas en las
tablas `branch_exercises` y `branch_exercise_answers`.

## 🧪 Testing

### Ejecutar Pruebas

```bash
# Pruebas de endpoints
npm test

# Pruebas manuales
python3 test_endpoints.py
```

### Cobertura de Pruebas

- ✅ Endpoints de autenticación
- ✅ Endpoints de chat
- ✅ Endpoints de entrenamiento
- ✅ Endpoints del dashboard
- ✅ Endpoints de sistema
- ✅ Validación de entrada
- ✅ Manejo de errores

## 🔒 Seguridad

### Medidas Implementadas

- **JWT con expiración configurable**
- **Bcrypt con salt configurable (12 rondas)**
- **Helmet para headers de seguridad**
- **CORS configurado restrictivamente**
- **Rate limiting por IP y usuario**
- **Validación de entrada robusta**
- **Sanitización de datos**
- **Logging estructurado con request IDs**

### Validaciones de Seguridad

- Contraseñas mínimas de 8 caracteres
- JWT_SECRET mínimo de 32 caracteres
- Rate limiting diferenciado por endpoint
- Verificación de roles y permisos
- Timeouts configurados para todas las operaciones

## 📊 Monitoreo

### Métricas Recopiladas

- Tiempo de respuesta por endpoint
- Tasa de errores
- Tokens utilizados
- Usuarios activos
- Estado del modelo de IA
- Uso de memoria y CPU
- Conexiones de base de datos

### Sistema de Alertas

- **Email**: Notificaciones automáticas
- **WebSocket**: Métricas en tiempo real
- **Console**: Logs estructurados
- **Umbrales configurables** para cada métrica

### Backup Automático

- **Frecuencia**: Cada 12 horas (configurable)
- **Compresión**: ZIP con nivel 6
- **Rotación**: Máximo 10 backups
- **Verificación**: Integridad de archivos
- **Restauración**: Proceso automatizado

## 🚀 Despliegue

### Docker (Recomendado)

```bash
# Construir imagen
docker build -t sheily-ai-backend .

# Ejecutar contenedor
docker run -d \
  --name sheily-ai-backend \
  -p 8000:8000 \
  -p 8002:8002 \
  --env-file config.env \
  sheily-ai-backend
```

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

## 🔧 Mantenimiento

### Comandos Útiles

```bash
# Verificar estado del sistema
curl http://localhost:8000/api/health

# Verificar logs
pm2 logs sheily-ai-backend

# Reiniciar servicio
pm2 restart sheily-ai-backend

# Backup manual
curl -X POST http://localhost:8000/api/admin/chat/backup \
  -H "Authorization: Bearer YOUR_TOKEN"

# Escaneo de seguridad
curl -X POST http://localhost:8000/api/security/scan \
  -H "Authorization: Bearer YOUR_TOKEN"
```

### Logs y Debugging

- **Request IDs**: Cada solicitud tiene un ID único
- **Logging estructurado**: Formato JSON para análisis
- **Niveles de log**: DEBUG, INFO, WARN, ERROR
- **Rotación automática**: Logs se rotan diariamente

## 🤝 Contribución

### Estándares de Código

- **ESLint**: Configuración estricta
- **Prettier**: Formato consistente
- **TypeScript**: Tipado opcional
- **Tests**: Cobertura mínima del 80%

### Flujo de Trabajo

1. Fork del repositorio
2. Crear rama feature (`git checkout -b feature/nueva-funcionalidad`)
3. Commit cambios (`git commit -am 'Agregar nueva funcionalidad'`)
4. Push a la rama (`git push origin feature/nueva-funcionalidad`)
5. Crear Pull Request

## 📄 Licencia

Este proyecto está bajo la licencia MIT. Ver [LICENSE](LICENSE) para más detalles.

## 🆘 Soporte

### Canales de Ayuda

- **Issues**: [GitHub Issues](https://github.com/sheily-ai/backend/issues)
- **Documentación**: [Wiki del proyecto](https://github.com/sheily-ai/backend/wiki)
- **Discord**: [Servidor de la comunidad](https://discord.gg/sheily-ai)

### Reportar Bugs

Por favor, incluye:
- Versión del backend
- Pasos para reproducir
- Logs de error
- Configuración del sistema

---

**Desarrollado con ❤️ por el equipo de Sheily AI**

*Construyendo el futuro de la inteligencia artificial*
