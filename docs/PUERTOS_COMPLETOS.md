# Puertos Completos del Sistema NeuroFusion

## 🚀 Resumen de Puertos

| Puerto | Servicio | Función | URL | Estado |
|--------|----------|---------|-----|--------|
| **8000** | Backend API | API REST principal | `http://127.0.0.1:8000` | ✅ |
| **8050** | Dashboard | Monitoreo Dash/Plotly | `http://127.0.0.1:8050` | ✅ |
| **3000** | Frontend | Interfaz React/Vite | `http://127.0.0.1:3000` | ✅ |
| **9090** | Prometheus | Métricas y monitoreo | `http://127.0.0.1:9090` | ✅ |
| **3100** | Grafana | Visualización de métricas | `http://127.0.0.1:3100` | ✅ |
| **6379** | Redis | Caché y sesiones | `redis://127.0.0.1:6379` | ✅ |

## 📊 Arquitectura de Monitoreo

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Frontend      │    │   Backend       │    │   Dashboard     │
│   Puerto 3000   │◄──►│   Puerto 8000   │◄──►│   Puerto 8050   │
└─────────────────┘    └─────────────────┘    └─────────────────┘
                                │
                                ▼
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Prometheus    │    │     Grafana     │    │     Redis       │
│   Puerto 9090   │◄──►│   Puerto 3100   │    │   Puerto 6379   │
└─────────────────┘    └─────────────────┘    └─────────────────┘
```

## 🔧 Configuración por Entorno

### **Desarrollo Local**
```bash
# Iniciar todos los servicios
./start_sistema_unificado.sh

# O individualmente:
# Backend
cd interface/backend && python main.py

# Dashboard
cd monitoring && python monitoring_dashboard.py

# Frontend
cd interface/frontend && npm run dev

# Prometheus
docker run -p 9090:9090 -v $(pwd)/monitoring/monitoring/prometheus.yml:/etc/prometheus/monitoring/prometheus.yml prom/prometheus

# Grafana
docker run -p 3100:3000 -e GF_SECURITY_ADMIN_PASSWORD=shaili_grafana_admin grafana/grafana

# Redis
docker run -p 6379:6379 redis:7-alpine redis-server --requirepass shaili_redis_password
```

### **Docker Compose**
```bash
# Iniciar todo el stack
docker-compose up -d

# Verificar servicios
docker-compose ps

# Logs de servicios
docker-compose logs -f [servicio]
```

## 🔍 Verificación Rápida

### **Comando de Verificación**
```bash
# Verificar todos los puertos
netstat -tlnp | grep -E ":(8000|8050|3000|9090|3100|6379)"

# Script automático
./scripts/verificar_sistema.sh
```

### **Verificación de Salud**
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

## 📈 Métricas y Monitoreo

### **Prometheus (Puerto 9090)**
- **Targets**: Endpoints de métricas del sistema
- **Scraping**: Cada 15 segundos
- **Almacenamiento**: Series temporales
- **Alertas**: Configurables

### **Grafana (Puerto 3100)**
- **Dashboards**: Visualización de métricas
- **Datasource**: Prometheus
- **Alertas**: Notificaciones configurables
- **Usuarios**: admin / shaili_grafana_admin

### **Dashboard (Puerto 8050)**
- **Métricas en tiempo real**: Sistema y modelos
- **Gráficos interactivos**: Plotly/Dash
- **Actualización**: Automática cada 30s
- **Alertas**: Visualización de eventos

## 🔐 Seguridad

### **Configuración de Seguridad**
- **Host**: 127.0.0.1 (solo localhost en desarrollo)
- **Autenticación**: JWT + MFA
- **Rate Limiting**: Habilitado
- **CORS**: Configurado para desarrollo

### **Credenciales**
- **Grafana**: admin / shaili_grafana_admin
- **Redis**: shaili_redis_password
- **PostgreSQL**: shaili_user / shaili_password

## 🚨 Solución de Problemas

### **Puerto Ocupado**
```bash
# Encontrar proceso
lsof -i :[PUERTO]

# Matar proceso
kill -9 [PID]

# O reiniciar servicio
docker-compose restart [servicio]
```

### **Firewall**
```bash
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
# Backend
tail -f logs/logs/neurofusion_core.log

# Frontend
tail -f interface/frontend/frontend.log

# Dashboard
tail -f monitoring/dashboard.log

# Docker
docker-compose logs -f [servicio]
```

## 📋 Checklist de Inicio

- [ ] **Backend API** (8000) - Funcionando
- [ ] **Dashboard** (8050) - Accesible
- [ ] **Frontend** (3000) - Disponible
- [ ] **Prometheus** (9090) - Recolectando métricas
- [ ] **Grafana** (3100) - Visualizando datos
- [ ] **Redis** (6379) - Caché funcionando
- [ ] **Firewall** - Puertos abiertos
- [ ] **Logs** - Sin errores críticos

---

**Última actualización**: 29 de Agosto, 2025  
**Versión**: 2.0.0  
**Estado**: ✅ Completamente documentado
