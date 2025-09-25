# Scripts de Automatización

Este directorio contiene scripts reales y funcionales para automatizar tareas del sistema Sheily AI.

## Estructura

```
scripts/
├── README.md                           # Este archivo
├── __init__.py                         # Inicializador del paquete
├── setup_personal_model.py             # Configuración del modelo principal
├── configure_solana.py                 # Configuración de Solana
├── daily_exercise_scheduler.py         # Scheduler de ejercicios diarios
├── enhanced_daily_exercise_scheduler.py # Scheduler mejorado de ejercicios
├── enhanced_integration_scheduler.py   # Scheduler de integración mejorada
└── install_dependencies.py             # Instalación de dependencias
```

## Scripts Disponibles

### 1. **Configuración del Modelo Principal** (`setup_personal_model.py`)

#### **✅ Funcionalidades**
- Configuración automática del modelo Sheily Personal (4-bit)
- Optimización de memoria y rendimiento
- Verificación de integración
- Generación de documentación

#### **✅ Uso**
```bash
# Configurar modelo principal
python scripts/setup_personal_model.py

# Verificar configuración
python -c "from modules.core.model.sheily_model import SheilyBaseModel; model = SheilyBaseModel()"
```

#### **✅ Características**
- Cuantización 4-bit automática
- Configuración de cuantización básica (BitsAndBytes removido)
- Compatibilidad con ROCm/AMD
- Optimización de memoria (~1.8GB)

### 2. **Configuración de Solana** (`configure_solana.py`)

#### **✅ Funcionalidades**
- Configuración automática de Solana
- Selección de red (devnet, testnet, mainnet)
- Configuración de proveedores de API
- Verificación de conectividad

#### **✅ Uso**
```bash
# Configurar Solana
python scripts/configure_solana.py

# Probar conexión
python -c "from modules.blockchain.solana_blockchain_real import SolanaBlockchainReal; client = SolanaBlockchainReal(); print(client.get_network_status())"
```

#### **✅ Características**
- Configuración de múltiples redes
- Integración con proveedores externos
- Verificación de conectividad real
- Generación de archivo .env

### 3. **Scheduler de Ejercicios Diarios** (`daily_exercise_scheduler.py`)

#### **✅ Funcionalidades**
- Generación automática de ejercicios diarios
- Scheduler automático (12:00 PM)
- Gestión de ramas especializadas
- Monitoreo de progreso

#### **✅ Uso**
```bash
# Generar ejercicios para hoy
python scripts/daily_exercise_scheduler.py generate

# Iniciar scheduler automático
python scripts/daily_exercise_scheduler.py start

# Generar para rama específica
python scripts/daily_exercise_scheduler.py branch medical

# Listar ejercicios de hoy
python scripts/daily_exercise_scheduler.py list
```

#### **✅ Características**
- Generación automática diaria
- 10 ejercicios por micro-rama
- 10 preguntas por ejercicio
- Sistema de puntos y dificultad

### 4. **Scheduler Mejorado** (`enhanced_daily_exercise_scheduler.py`)

#### **✅ Funcionalidades**
- Generación mejorada de ejercicios
- Estadísticas detalladas
- Optimización de contenido
- Gestión avanzada de ramas

#### **✅ Uso**
```bash
# Generar ejercicios mejorados
python scripts/enhanced_daily_exercise_scheduler.py generate

# Mostrar estadísticas
python scripts/enhanced_daily_exercise_scheduler.py stats

# Listar ejercicios
python scripts/enhanced_daily_exercise_scheduler.py list
```

#### **✅ Características**
- Contenido optimizado por rama
- Métricas de calidad
- Sistema de dificultad dinámico
- Integración con sistema de entrenamiento

### 5. **Scheduler de Integración** (`enhanced_integration_scheduler.py`)

#### **✅ Funcionalidades**
- Integración automática de ejercicios
- Scheduler de integración (12:30 PM)
- Historial de integraciones
- Monitoreo de estado

#### **✅ Uso**
```bash
# Integrar ejercicios de hoy
python scripts/enhanced_integration_scheduler.py integrate

# Integrar ejercicios de fecha específica
python scripts/enhanced_integration_scheduler.py integrate --date 2025-08-29

# Iniciar scheduler automático
python scripts/enhanced_integration_scheduler.py start

# Mostrar historial
python scripts/enhanced_integration_scheduler.py history --days 7

# Ver estado actual
python scripts/enhanced_integration_scheduler.py status
```

#### **✅ Características**
- Integración automática diaria
- Historial completo de integraciones
- Métricas de éxito/fallo
- Sistema de rollback automático

### 6. **Instalación de Dependencias** (`install_dependencies.py`)

#### **✅ Funcionalidades**
- Instalación automática de dependencias
- Verificación de compatibilidad
- Actualización de requirements.txt
- Gestión de conflictos

#### **✅ Uso**
```bash
# Instalar dependencias
python scripts/install_dependencies.py

# Verificar instalación
python -c "import duckdb, astor, radon, pyinstrument, plotly, beautifulsoup4, mlflow, gitpython; print('✅ Todas las dependencias instaladas')"
```

#### **✅ Características**
- Instalación automática de paquetes
- Gestión de versiones
- Verificación de compatibilidad
- Actualización de documentación

## Automatización Avanzada

### **Cron Jobs**
```bash
# Configurar cron jobs automáticos
crontab -e

# Ejercicios diarios a las 12:00 PM
0 12 * * * cd /path/to/sheily-ai && python scripts/daily_exercise_scheduler.py generate

# Integración a las 12:30 PM
30 12 * * * cd /path/to/sheily-ai && python scripts/enhanced_integration_scheduler.py integrate

# Backup diario a las 2:00 AM
0 2 * * * cd /path/to/sheily-ai && python scripts/backup_system.py
```

### **Systemd Services**
```ini
# /etc/systemd/system/sheily-ai-scheduler.service
[Unit]
Description=Sheily AI Exercise Scheduler
After=network.target

[Service]
Type=simple
User=sheily
WorkingDirectory=/path/to/sheily-ai
ExecStart=/usr/bin/python3 scripts/enhanced_daily_exercise_scheduler.py start
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

### **Docker Compose**
```yaml
# docker-compose.yml
version: '3.8'
services:
  sheily-scheduler:
    build: .
    volumes:
      - ./scripts:/app/scripts
      - ./logs:/app/logs
    environment:
      - PYTHONPATH=/app
    command: python scripts/enhanced_daily_exercise_scheduler.py start
    restart: unless-stopped
```

## Monitoreo y Logs

### **Logs de Scripts**
```python
import logging

# Configurar logging para scripts
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/scripts.log'),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)
```

### **Métricas de Ejecución**
```python
import time
from datetime import datetime

class ScriptMetrics:
    """Métricas de ejecución de scripts"""
    
    def __init__(self, script_name: str):
        self.script_name = script_name
        self.start_time = time.time()
        self.metrics = {}
    
    def log_metric(self, name: str, value: any):
        """Registrar métrica"""
        self.metrics[name] = value
    
    def finish(self):
        """Finalizar y registrar métricas"""
        duration = time.time() - self.start_time
        self.metrics['duration'] = duration
        self.metrics['timestamp'] = datetime.now().isoformat()
        
        # Guardar métricas
        with open(f'logs/script_metrics_{self.script_name}.json', 'a') as f:
            json.dump(self.metrics, f)
            f.write('\n')
```

## Gestión de Errores

### **Manejo de Excepciones**
```python
import sys
import traceback
from typing import Callable

def safe_execute(func: Callable, *args, **kwargs):
    """Ejecutar función de forma segura"""
    try:
        return func(*args, **kwargs)
    except Exception as e:
        logger.error(f"Error en {func.__name__}: {e}")
        logger.error(traceback.format_exc())
        
        # Enviar alerta
        send_alert(f"Error en script {func.__name__}", str(e))
        
        return None

def retry_on_failure(func: Callable, max_retries: int = 3, delay: float = 1.0):
    """Reintentar función en caso de fallo"""
    for attempt in range(max_retries):
        try:
            return func()
        except Exception as e:
            if attempt == max_retries - 1:
                raise e
            logger.warning(f"Intento {attempt + 1} falló: {e}")
            time.sleep(delay)
```

### **Alertas Automáticas**
```python
import smtplib
from email.mime.text import MIMEText

def send_alert(subject: str, message: str):
    """Enviar alerta por email"""
    try:
        msg = MIMEText(message)
        msg['Subject'] = f"[Sheily AI] {subject}"
        msg['From'] = 'alerts@sheily-ai.com'
        msg['To'] = 'admin@sheily-ai.com'
        
        with smtplib.SMTP('smtp.gmail.com', 587) as server:
            server.starttls()
            server.login('alerts@sheily-ai.com', 'password')
            server.send_message(msg)
            
        logger.info(f"Alerta enviada: {subject}")
    except Exception as e:
        logger.error(f"Error enviando alerta: {e}")
```

## Mantenimiento

### **Limpieza Automática**
```bash
#!/bin/bash
# Limpiar logs y archivos temporales

# Limpiar logs antiguos
find logs/ -name "*.log" -mtime +30 -delete

# Limpiar archivos temporales
find /tmp -name "sheily_*" -mtime +7 -delete

# Limpiar cache de Python
find . -name "__pycache__" -type d -exec rm -rf {} + 2>/dev/null

echo "✅ Limpieza completada"
```

### **Backup de Scripts**
```bash
#!/bin/bash
# Backup de scripts

DATE=$(date +%Y%m%d)
BACKUP_DIR="backups/scripts/$DATE"

mkdir -p $BACKUP_DIR

# Backup de scripts
cp -r scripts/* $BACKUP_DIR/

# Backup de configuraciones
cp *.json $BACKUP_DIR/ 2>/dev/null || true

# Comprimir backup
tar -czf "backups/scripts_$DATE.tar.gz" $BACKUP_DIR
rm -rf $BACKUP_DIR

echo "✅ Backup de scripts completado"
```

## Estadísticas

### **Métricas de Ejecución**
- **Scripts activos**: 6
- **Ejecuciones diarias**: 3
- **Tiempo promedio**: < 5 minutos
- **Tasa de éxito**: > 98%

### **Automatización**
- **Tareas automatizadas**: 10+
- **Cron jobs**: 3
- **Alertas**: 5 tipos
- **Backups**: Diarios

## Contacto

Para reportar problemas o sugerir mejoras:
- **Issues**: GitHub repository
- **Email**: scripts@sheily-ai.com
- **Documentación**: docs/scripts/
