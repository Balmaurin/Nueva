# Configuración de Puertos - Sistema NeuroFusion

## 🚀 Puertos del Sistema

El sistema NeuroFusion utiliza **6 puertos principales** para diferentes servicios:

### **1. Puerto 8000 - Backend API**
- **Servicio**: FastAPI/Uvicorn
- **Función**: API REST principal del sistema
- **Endpoints**:
  - `/api/auth` - Autenticación
  - `/api/training` - Sistema de entrenamiento
  - `/api/recommendations` - Recomendaciones
  - `/api/blockchain` - Operaciones blockchain
  - `/api/health` - Estado del sistema
- **URL**: `http://127.0.0.1:8000`
- **Documentación**: `http://127.0.0.1:8000/docs`

### **2. Puerto 8050 - Dashboard de Monitoreo**
- **Servicio**: Dash/Plotly
- **Función**: Dashboard web interactivo de monitoreo
- **Características**:
  - Métricas del sistema en tiempo real
  - Gráficos de rendimiento
  - Alertas y notificaciones
  - Estado de servicios
- **URL**: `http://127.0.0.1:8050`
- **Actualización**: Automática cada 30 segundos

### **3. Puerto 3000 - Frontend**
- **Servicio**: React/Vite
- **Función**: Interfaz de usuario principal
- **Características**:
  - Interfaz web moderna
  - Componentes interactivos
  - Gestión de sesiones
  - Integración con APIs
- **URL**: `http://127.0.0.1:3000`
- **Desarrollo**: Hot reload habilitado

### **4. Puerto 9090 - Prometheus**
- **Servicio**: Prometheus
- **Función**: Sistema de monitoreo y métricas
- **Características**:
  - Recolección de métricas del sistema
  - Almacenamiento de series temporales
  - Configuración de alertas
  - Scraping de endpoints de métricas
- **URL**: `http://127.0.0.1:9090`
- **Configuración**: `monitoring/monitoring/prometheus.yml`

### **5. Puerto 3100 - Grafana**
- **Servicio**: Grafana
- **Función**: Visualización de métricas y dashboards
- **Características**:
  - Dashboards interactivos
  - Visualización de métricas de Prometheus
  - Alertas y notificaciones
  - Paneles personalizables
- **URL**: `http://127.0.0.1:3100`
- **Credenciales**: admin / shaili_grafana_admin

### **6. Puerto 6379 - Redis**
- **Servicio**: Redis
- **Función**: Base de datos en memoria y caché
- **Características**:
  - Caché de sesiones
  - Cola de tareas
  - Almacenamiento temporal
  - Pub/Sub para notificaciones
- **URL**: `redis://127.0.0.1:6379`
- **Contraseña**: shaili_redis_password

## 📋 Configuración en Archivos

### **Configuración Principal**
```json
// config/config/neurofusion_config.json
{
  "frontend_port": 3000,
  "backend_port": 8000,
  "host": "127.0.0.1"
}
```

### **Scripts de Verificación**
```bash
# scripts/verificar_sistema.sh
ports=("8000" "8050" "3000" "9090" "3100" "6379")
```

### **Docker Compose**
```yaml
# config/docker-compose.yml
services:
  backend:
    ports:
      - "8000:8000"
  frontend:
    ports:
      - "3000:3000"
  prometheus:
    ports:
      - "9090:9090"
  grafana:
    ports:
      - "3100:3000"
  redis:
    ports:
      - "6379:6379"
```

## 🔧 Comandos de Inicio

### **Iniciar Backend (Puerto 8000)**
```bash
cd interface/backend
source venv/bin/activate
python main.py
# o
uvicorn main:app --host 127.0.0.1 --port 8000
```

### **Iniciar Dashboard (Puerto 8050)**
```bash
cd monitoring
source venv/bin/activate
python monitoring_dashboard.py
```

### **Iniciar Frontend (Puerto 3000)**
```bash
cd interface/frontend
npm install
npm run dev
```

### **Iniciar Prometheus (Puerto 9090)**
```bash
# Con Docker
docker run -p 9090:9090 -v $(pwd)/monitoring/monitoring/prometheus.yml:/etc/prometheus/monitoring/prometheus.yml prom/prometheus

# O con docker-compose
docker-compose up prometheus
```

### **Iniciar Grafana (Puerto 3100)**
```bash
# Con Docker
docker run -p 3100:3000 -e GF_SECURITY_ADMIN_PASSWORD=shaili_grafana_admin grafana/grafana

# O con docker-compose
docker-compose up grafana
```

### **Iniciar Redis (Puerto 6379)**
```bash
# Con Docker
docker run -p 6379:6379 redis:7-alpine redis-server --requirepass shaili_redis_password

# O con docker-compose
docker-compose up redis
```

### **Iniciar Todo el Sistema**
```bash
./start_sistema_unificado.sh
```

## 🔍 Verificación de Puertos

### **Verificar Puertos en Uso**
```bash
netstat -tlnp | grep -E ":(8000|8050|3000|9090|3100|6379)"
```

### **Verificar Acceso Web**
```bash
# Backend API
curl -s http://127.0.0.1:8000/health

# Dashboard
curl -s http://127.0.0.1:8050

# Frontend
curl -s http://127.0.0.1:3000

# Prometheus
curl -s http://127.0.0.1:9090/-/healthy

# Grafana
curl -s http://127.0.0.1:3100/api/health

# Redis
redis-cli -h 127.0.0.1 -p 6379 -a shaili_redis_password ping
```

### **Script de Verificación Automática**
```bash
./scripts/verificar_sistema.sh
```

## 🚨 Solución de Problemas

### **Puerto Ocupado**
```bash
# Encontrar proceso usando el puerto
lsof -i :8000
lsof -i :8050
lsof -i :3000
lsof -i :9090
lsof -i :3100
lsof -i :6379

# Matar proceso
kill -9 <PID>
```

### **Firewall**
```bash
# Verificar firewall
sudo ufw status

# Permitir puertos
sudo ufw allow 8000
sudo ufw allow 8050
sudo ufw allow 3000
sudo ufw allow 9090
sudo ufw allow 3100
sudo ufw allow 6379
```

### **Logs de Errores**
```bash
# Backend logs
tail -f logs/logs/neurofusion_core.log

# Frontend logs
tail -f interface/frontend/frontend.log

# Dashboard logs
tail -f monitoring/dashboard.log
```

## 📊 Monitoreo de Puertos

### **Estado de Servicios**
- ✅ **Puerto 8000**: Backend API funcionando
- ✅ **Puerto 8050**: Dashboard accesible
- ✅ **Puerto 3000**: Frontend disponible
- ✅ **Puerto 9090**: Prometheus funcionando
- ✅ **Puerto 3100**: Grafana accesible
- ✅ **Puerto 6379**: Redis funcionando

### **Métricas de Rendimiento**
- **Tiempo de respuesta**: < 3 segundos
- **Disponibilidad**: 99.9%
- **Concurrentes**: 20 usuarios

## 🔐 Seguridad

### **Configuración de Seguridad**
- **Host**: 127.0.0.1 (solo localhost)
- **CORS**: Configurado para desarrollo
- **Rate Limiting**: Habilitado
- **Autenticación**: JWT + MFA

### **Puertos de Desarrollo vs Producción**
- **Desarrollo**: 127.0.0.1 (localhost)
- **Producción**: 0.0.0.0 (todos los interfaces)

---

**Última actualización**: 29 de Agosto, 2025  
**Versión**: 2.0.0  
**Estado**: ✅ Verificado
