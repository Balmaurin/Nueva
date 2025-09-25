# Sistema de Monitoreo Shaili AI

## 📊 Descripción General

El sistema de monitoreo de Shaili AI proporciona una solución completa para el seguimiento en tiempo real de métricas del sistema, modelos de IA, ramas especializadas y alertas automáticas.

## 🏗️ Arquitectura del Sistema

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│  Metrics        │    │  Alert          │    │  Monitoring     │
│  Collector      │───►│  Manager        │───►│  Dashboard      │
│  (Python)       │    │  (Python)       │    │  (Dash/Plotly)  │
└─────────────────┘    └─────────────────┘    └─────────────────┘
         │                       │                       │
         ▼                       ▼                       ▼
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│  Prometheus     │    │  Grafana        │    │  SQLite DB      │
│  (Docker)       │    │  (Docker)       │    │  (metrics.db)   │
└─────────────────┘    └─────────────────┘    └─────────────────┘
```

## 🚀 Componentes del Sistema

### 1. **Metrics Collector** (`metrics_collector.py`)
- **Función**: Recopila métricas del sistema, modelos y ramas
- **Intervalo**: Cada 15 segundos
- **Métricas recopiladas**:
  - Sistema: CPU, memoria, disco, red, conexiones
  - Modelos: tiempo de inferencia, uso de memoria, GPU, requests/min
  - Ramas: adapters activos, progreso de entrenamiento, precisión

### 2. **Alert Manager** (`alert_manager.py`)
- **Función**: Gestiona alertas y notificaciones
- **Características**:
  - Detección automática de problemas
  - Escalación de alertas
  - Notificaciones por email, Slack, Telegram, webhook
  - Cooldown y límites de alertas

### 3. **Monitoring Dashboard** (`monitoring_dashboard.py`)
- **Función**: Interfaz web para visualización de métricas
- **Tecnología**: Dash + Plotly
- **Puerto**: 8050
- **Características**:
  - Gráficos en tiempo real
  - Múltiples paneles de métricas
  - Actualización automática cada 30s

### 4. **Prometheus** (Docker)
- **Función**: Sistema de monitoreo y alertas
- **Puerto**: 9090
- **Características**:
  - Recolección de métricas
  - Almacenamiento de series temporales
  - Configuración de alertas

### 5. **Grafana** (Docker)
- **Función**: Visualización avanzada de métricas
- **Puerto**: 3100
- **Credenciales**: admin / shaili_grafana_admin
- **Características**:
  - Dashboards personalizables
  - Integración con Prometheus
  - Alertas y notificaciones

## 📁 Estructura de Archivos

```
monitoring/
├── README.md                    # Esta documentación
├── start_monitoring.sh          # Script de inicio
├── stop_monitoring.sh           # Script de detención
├── metrics_collector.py         # Colector de métricas
├── alert_manager.py             # Gestor de alertas
├── monitoring_dashboard.py      # Dashboard web
├── prometheus.yml              # Configuración de Prometheus
├── metrics.db                  # Base de datos SQLite
├── dashboards/
│   └── shaili_model_dashboard.json  # Dashboard de Grafana
└── logs/                       # Directorio de logs
    ├── metrics_collector.log
    ├── alert_manager.log
    ├── monitoring_dashboard.log
    ├── prometheus.log
    └── grafana.log
```

## 🔧 Instalación y Configuración

### Prerrequisitos

1. **Python 3.8+** con las siguientes dependencias:
   ```bash
   pip install dash plotly pandas psutil sqlite3 requests
   ```

2. **Docker** (opcional, para Prometheus y Grafana):
   ```bash
   # Verificar instalación
   docker --version
   ```

### Configuración Inicial

1. **Clonar el repositorio** (si no está hecho):
   ```bash
   git clone <repository-url>
   cd shaili-ai
   ```

2. **Instalar dependencias**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Configurar credenciales** (opcional):
   - Editar `monitoring/alert_manager.py` para configurar notificaciones
   - Modificar `monitoring/prometheus.yml` para ajustar targets

## 🚀 Uso del Sistema

### Inicio Rápido

```bash
# Desde el directorio raíz del proyecto
./monitoring/start_monitoring.sh
```

### Detención

```bash
./monitoring/stop_monitoring.sh
```

### Inicio Manual de Componentes

```bash
# 1. Metrics Collector
python monitoring/metrics_collector.py &

# 2. Alert Manager
python monitoring/alert_manager.py &

# 3. Monitoring Dashboard
python monitoring/monitoring_dashboard.py &

# 4. Prometheus (con Docker)
docker run -d --name shaili-prometheus -p 9090:9090 \
  -v $(pwd)/monitoring/prometheus.yml:/etc/prometheus/prometheus.yml \
  prom/prometheus:v2.45.0

# 5. Grafana (con Docker)
docker run -d --name shaili-grafana -p 3100:3000 \
  -e GF_SECURITY_ADMIN_PASSWORD=shaili_grafana_admin \
  grafana/grafana:9.5.3
```

## 🌐 Acceso a las Interfaces

| Servicio | URL | Descripción |
|----------|-----|-------------|
| **Dashboard** | http://127.0.0.1:8050 | Interfaz principal de monitoreo |
| **Prometheus** | http://127.0.0.1:9090 | Sistema de métricas y alertas |
| **Grafana** | http://127.0.0.1:3100 | Visualización avanzada |

### Credenciales de Grafana
- **Usuario**: admin
- **Contraseña**: shaili_grafana_admin

## 📊 Métricas Disponibles

### Métricas del Sistema
- **CPU**: Uso porcentual del procesador
- **Memoria**: Uso y disponibilidad de RAM
- **Disco**: Espacio utilizado y disponible
- **Red**: Bytes enviados/recibidos
- **Conexiones**: Conexiones activas

### Métricas de Modelos
- **Tiempo de Inferencia**: Latencia de respuesta
- **Uso de Memoria**: Memoria consumida por modelo
- **GPU**: Uso de GPU (si está disponible)
- **Requests/min**: Tasa de solicitudes
- **Tasa de Error**: Porcentaje de errores

### Métricas de Ramas
- **Adapters Activos**: Número de adaptadores en uso
- **Progreso de Entrenamiento**: Porcentaje completado
- **Precisión**: Score de accuracy
- **Pérdida**: Valor de loss
- **Muestras Procesadas**: Cantidad de datos procesados

## 🚨 Sistema de Alertas

### Tipos de Alertas
- **high_cpu**: CPU > 90%
- **high_memory**: Memoria > 85%
- **disk_full**: Disco > 90%
- **model_error**: Tasa de error > 5%

### Canales de Notificación
- **Email**: SMTP configurable
- **Slack**: Webhook personalizable
- **Telegram**: Bot con token
- **Webhook**: Endpoint personalizado

### Configuración de Alertas
Editar `monitoring/alert_manager.py` para configurar:
- Umbrales de alertas
- Canales de notificación
- Reglas de escalación
- Cooldown y límites

## 🔍 Troubleshooting

### Problemas Comunes

1. **Puerto ocupado**:
   ```bash
   # Verificar qué proceso usa el puerto
   lsof -i :8050
   
   # Matar proceso
   kill -9 <PID>
   ```

2. **Dashboard no carga**:
   ```bash
   # Verificar logs
   tail -f monitoring/logs/monitoring_dashboard.log
   
   # Verificar dependencias
   pip list | grep dash
   ```

3. **Prometheus no inicia**:
   ```bash
   # Verificar Docker
   docker ps -a | grep prometheus
   
   # Verificar configuración
   cat monitoring/prometheus.yml
   ```

4. **Métricas no se recopilan**:
   ```bash
   # Verificar collector
   tail -f monitoring/logs/metrics_collector.log
   
   # Verificar base de datos
   sqlite3 monitoring/metrics.db ".tables"
   ```

### Logs y Debugging

```bash
# Ver todos los logs
ls -la monitoring/logs/

# Ver logs en tiempo real
tail -f monitoring/logs/*.log

# Verificar estado de servicios
ps aux | grep -E "(metrics_collector|monitoring_dashboard|alert_manager)"
```

## 📈 Personalización

### Agregar Nuevas Métricas

1. **Modificar `metrics_collector.py`**:
   ```python
   def collect_custom_metrics(self):
       # Implementar recopilación de métricas personalizadas
       pass
   ```

2. **Actualizar base de datos**:
   ```sql
   ALTER TABLE system_metrics ADD COLUMN custom_metric REAL;
   ```

3. **Actualizar dashboard**:
   ```python
   def create_custom_chart(self, df):
       # Crear gráfico para nuevas métricas
       pass
   ```

### Configurar Nuevas Alertas

1. **Agregar regla en `alert_manager.py`**:
   ```python
   if custom_metric > threshold:
       alerts.append({
           'alert_type': 'custom_alert',
           'severity': 'warning',
           'message': f'Custom metric is high: {custom_metric}'
       })
   ```

2. **Configurar notificación**:
   ```python
   # En notification_channels.json
   {
       "custom_channel": {
           "enabled": True,
           "webhook_url": "https://your-webhook.com"
       }
   }
   ```

## 🔒 Seguridad

### Configuración de Seguridad
- **Host**: 127.0.0.1 (solo localhost en desarrollo)
- **Autenticación**: Configurable en Grafana
- **Rate Limiting**: Implementado en alertas
- **Logs**: Rotación automática

### Recomendaciones
- Cambiar credenciales por defecto
- Configurar firewall para producción
- Usar HTTPS en entornos de producción
- Implementar autenticación adicional

## 📞 Soporte

### Comandos Útiles

```bash
# Estado del sistema
./verificar_sistema.sh

# Verificar puertos
netstat -tlnp | grep -E ":(8050|9090|3100)"

# Reiniciar servicios
./monitoring/stop_monitoring.sh && ./monitoring/start_monitoring.sh

# Ver métricas en tiempo real
sqlite3 monitoring/metrics.db "SELECT * FROM system_metrics ORDER BY timestamp DESC LIMIT 5;"
```

### Archivos de Configuración Importantes
- `monitoring/prometheus.yml`: Configuración de Prometheus
- `monitoring/alert_manager.py`: Configuración de alertas
- `monitoring/metrics.db`: Base de datos de métricas

---

**Última actualización**: 29 de Agosto, 2025  
**Versión**: 2.0.0  
**Estado**: ✅ Completamente implementado y documentado
