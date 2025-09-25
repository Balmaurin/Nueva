# Sistema de Configuración NeuroFusion

Este directorio contiene todo el sistema de configuración del proyecto NeuroFusion, proporcionando una gestión centralizada y robusta de todas las configuraciones del sistema.

## 📁 Estructura del Directorio

```
config/
├── __init__.py                           # Módulo principal de configuración
├── config_manager.py                     # Gestor principal de configuración
├── config_validator.py                   # Validador de configuraciones
├── dynamic_config_manager.py             # Gestor de configuración dinámica
├── init_config_system.py                 # Script de inicialización
├── test_config_system.py                 # Script de pruebas
├── README.md                             # Este archivo
├── .pylintrc                             # Configuración de Pylint
├── neurofusion_config.json               # Configuración principal del sistema
├── module_initialization.json            # Configuración de inicialización de módulos
├── rate_limits.json                      # Configuración de límites de tasa
├── monitoring_config.json                # Configuración de monitoreo
├── training_token_config.json            # Configuración de tokens de entrenamiento
├── sheily_token_config.json              # Configuración del token Sheily
├── sheily_token_metadata.json            # Metadatos del token Sheily
├── advanced_training_config.json         # Configuración avanzada de entrenamiento
├── docker-compose.yml                    # Configuración de Docker Compose
├── docker-compose.dev.yml                # Configuración de Docker Compose para desarrollo
├── backups/                              # Directorio de backups
├── schemas/                              # Esquemas de validación
└── templates/                            # Plantillas de configuración
```

## 🚀 Características Principales

### ✅ Gestión Centralizada
- Acceso unificado a todas las configuraciones del sistema
- Carga automática de configuraciones JSON y YAML
- Cache inteligente para mejorar el rendimiento

### ✅ Validación Robusta
- Validación de esquemas JSON
- Verificación de integridad de configuraciones
- Detección de errores y advertencias

### ✅ Configuración Dinámica
- Actualización en tiempo real sin reiniciar el sistema
- Observación automática de cambios en archivos
- Sistema de callbacks para notificar cambios

### ✅ Backup y Restauración
- Creación automática de backups
- Restauración segura de configuraciones
- Control de versiones de configuración

### ✅ Seguridad
- Validación de permisos de archivos
- Encriptación de configuraciones sensibles
- Control de acceso a configuraciones críticas

## 📋 Archivos de Configuración

### Configuración Principal (`neurofusion_config.json`)
Configuración central del sistema NeuroFusion que incluye:
- Información del sistema (nombre, versión, modo debug)
- Rutas de directorios (datos, modelos, cache, logs)
- Configuración de modelos (embeddings, LLM)
- Configuración de rendimiento y seguridad
- Configuración de componentes del sistema

### Configuración de Módulos (`module_initialization.json`)
Define la inicialización y dependencias de todos los módulos del sistema:
- Dependencias entre módulos
- Parámetros de inicialización
- Orden de carga de módulos

### Configuración de Rate Limits (`rate_limits.json`)
Define los límites de tasa para diferentes operaciones:
- Límites de minteo de tokens
- Límites de transferencias
- Límites de API
- Configuración de cooldown

### Configuración de Monitoreo (`monitoring_config.json`)
Configuración del sistema de monitoreo:
- Umbrales de alerta
- Reglas de monitoreo
- Configuración de notificaciones

### Configuración de Entrenamiento (`training_token_config.json`)
Configuración del sistema de tokens de entrenamiento:
- Puntos por entrenamiento
- Conversión de puntos a tokens
- Tipos de entrenamiento
- Condiciones de bonificación

### Configuración de Tokens (`sheily_token_config.json`)
Configuración del token Sheily:
- Información del token (nombre, símbolo, decimales)
- Direcciones de mint y autoridad
- Configuración de red

### Configuración de Docker (`docker-compose.yml`)
Configuración de servicios Docker:
- Base de datos PostgreSQL
- Redis para cache
- Backend y frontend
- Prometheus y Grafana para monitoreo

## 🔧 Uso del Sistema

### Importación Básica

```python
import config

# Obtener configuración del sistema
system_config = config.get_system_config()

# Obtener configuración específica
embedding_config = config.get_embedding_config()
branch_config = config.get_branch_system_config()
```

### Gestión de Configuración

```python
from config import ConfigManager

# Crear instancia del gestor
manager = ConfigManager()

# Obtener configuración
config_data = manager.get_config('main')

# Actualizar configuración
updates = {'debug_mode': True}
success = manager.update_config('main', updates)

# Validar configuración
validation = manager.validate_config()
```

### Configuración Dinámica

```python
from config import DynamicConfigManager

# Crear gestor dinámico
dynamic_manager = DynamicConfigManager()

# Registrar callback para cambios
def config_change_handler(event):
    print(f"Configuración cambiada: {event.config_name}")

dynamic_manager.register_config_callback('main', config_change_handler)

# Actualizar configuración en tiempo real
dynamic_manager.update_config_partial('main', {'debug_mode': True})
```

### Validación de Configuraciones

```python
from config import ConfigValidator

# Crear validador
validator = ConfigValidator()

# Validar todas las configuraciones
results = validator.validate_all_configs()

# Obtener resumen
summary = validator.get_validation_summary()
```

## 🧪 Pruebas

### Ejecutar Todas las Pruebas

```bash
cd config
python test_config_system.py
```

### Pruebas Específicas

```python
# Probar gestor de configuración
from test_config_system import test_config_manager
test_config_manager()

# Probar validador
from test_config_system import test_config_validator
test_config_validator()

# Probar configuración dinámica
from test_config_system import test_dynamic_config_manager
test_dynamic_config_manager()
```

## 🔄 Inicialización

### Inicialización Automática

```bash
cd config
python init_config_system.py
```

### Inicialización Manual

```python
from init_config_system import ConfigSystemInitializer

initializer = ConfigSystemInitializer()
results = initializer.initialize_config_system()
initializer.print_summary()
```

## 📊 Monitoreo y Logs

### Logs del Sistema

Los logs del sistema de configuración se almacenan en:
- `logs/neurofusion_advanced.log` - Log principal
- `logs/config_manager.log` - Log del gestor de configuración
- `logs/config_validator.log` - Log del validador

### Métricas de Configuración

```python
# Obtener resumen de configuraciones
summary = config.get_config_summary()

# Obtener estadísticas de validación
errors = config.get_config_errors()
warnings = config.get_config_warnings()
```

## 🔒 Seguridad

### Permisos de Archivos

Los archivos de configuración tienen los siguientes permisos:
- Archivos de configuración: 644 (rw-r--r--)
- Directorios: 755 (rwxr-xr-x)

### Encriptación

Las configuraciones sensibles pueden ser encriptadas:
- Claves JWT
- Contraseñas de base de datos
- Tokens de API

### Validación de Integridad

- Verificación de hashes de archivos
- Validación de esquemas JSON
- Detección de configuraciones corruptas

## 🚨 Troubleshooting

### Problemas Comunes

1. **Error de importación de módulos**
   ```bash
   pip install pyyaml jsonschema watchdog
   ```

2. **Configuración no encontrada**
   ```bash
   python init_config_system.py
   ```

3. **Error de validación**
   ```bash
   python test_config_system.py
   ```

4. **Problemas de permisos**
   ```bash
   chmod 644 config/*.json
   chmod 755 config/
   ```

### Logs de Error

Para diagnosticar problemas, revisa los logs:
```bash
tail -f logs/neurofusion_advanced.log
tail -f logs/config_manager.log
```

## 📈 Rendimiento

### Optimizaciones

- Cache inteligente de configuraciones
- Carga lazy de configuraciones
- Compresión de configuraciones grandes
- Indexación de configuraciones frecuentes

### Métricas de Rendimiento

```python
# Obtener información de rendimiento
performance_info = config.get_performance_info()

# Monitorear tiempo de carga
import time
start_time = time.time()
config_data = config.get_system_config()
load_time = time.time() - start_time
```

## 🔄 Actualizaciones

### Actualización de Configuraciones

```python
# Actualización parcial
config.update_config('main', {'debug_mode': True})

# Actualización completa
new_config = {...}
config.set_dynamic_config('main', new_config)

# Recarga de configuraciones
config.reload_configs()
```

### Versionado de Configuraciones

```python
# Crear backup antes de actualizar
backup_path = config.backup_configs()

# Restaurar desde backup
config.restore_configs(backup_path)
```

## 📚 API de Referencia

### Funciones Principales

- `get_system_config()` - Configuración principal del sistema
- `get_branch_config()` - Configuración de ramas
- `get_model_config()` - Configuración de modelos
- `validate_all_configs()` - Validar todas las configuraciones
- `update_config(name, updates)` - Actualizar configuración
- `backup_configs()` - Crear backup
- `restore_configs(path)` - Restaurar desde backup

### Clases Principales

- `ConfigManager` - Gestor principal de configuración
- `ConfigValidator` - Validador de configuraciones
- `DynamicConfigManager` - Gestor de configuración dinámica
- `ConfigChangeEvent` - Evento de cambio de configuración

## 🤝 Contribución

### Agregar Nueva Configuración

1. Crear archivo de configuración JSON/YAML
2. Agregar validación en `config_validator.py`
3. Agregar funciones de acceso en `__init__.py`
4. Actualizar documentación
5. Agregar pruebas

### Estándares de Código

- Seguir PEP 8
- Documentar todas las funciones
- Agregar tipos de datos
- Incluir pruebas unitarias
- Validar configuraciones

## 📄 Licencia

Este sistema de configuración es parte del proyecto NeuroFusion y está sujeto a la misma licencia del proyecto principal.

## 📞 Soporte

Para soporte técnico o preguntas sobre el sistema de configuración:
- Crear un issue en el repositorio
- Revisar la documentación
- Ejecutar las pruebas de diagnóstico

---

**Versión**: 3.1.0  
**Última actualización**: 2024-08-29  
**Mantenido por**: NeuroFusion Team
