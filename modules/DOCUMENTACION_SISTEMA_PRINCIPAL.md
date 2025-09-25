# Documentación del Sistema Principal de Módulos

## 📋 Sistema de Inicialización (`__init__.py`)

### Clases Principales

#### `ModuleInfo`
**Propósito**: Estructura de datos para almacenar información de un módulo registrado.

**Atributos**:
- `name: str` - Nombre único del módulo
- `category: str` - Categoría del módulo (ai, blockchain, core, etc.)
- `description: str` - Descripción del módulo
- `class_name: str` - Nombre de la clase del módulo
- `instance: Any` - Instancia del módulo
- `dependencies: List[str]` - Lista de dependencias del módulo
- `is_async: bool` - Indica si el módulo es asíncrono
- `status: str` - Estado del módulo (active, inactive, error)
- `last_used: Optional[datetime]` - Última vez que se usó el módulo

#### `ModuleRegistry`
**Propósito**: Registro central de todos los módulos del sistema.

**Métodos principales**:
- `register_module()` - Registrar un nuevo módulo
- `get_module()` - Obtener información de un módulo
- `get_modules_by_category()` - Obtener módulos por categoría
- `list_all_modules()` - Listar todos los módulos
- `get_module_instance()` - Obtener instancia de un módulo

#### `UnifiedModuleSystem`
**Propósito**: Sistema unificado para gestionar todos los módulos.

**Métodos principales**:
- `initialize()` - Inicializar todos los módulos del sistema
- `_register_ai_modules()` - Registrar módulos de IA
- `_register_memory_modules()` - Registrar módulos de memoria
- `_register_training_modules()` - Registrar módulos de entrenamiento
- `_register_blockchain_modules()` - Registrar módulos de blockchain
- `get_module()` - Obtener un módulo por nombre
- `list_modules()` - Listar módulos disponibles
- `execute_module_function()` - Ejecutar función de un módulo

### Funciones de Conveniencia

#### `initialize_modules()`
**Propósito**: Inicializar todos los módulos del sistema.
**Uso**: `await initialize_modules()`

#### `get_module(name: str)`
**Propósito**: Obtener un módulo por nombre.
**Parámetros**: `name` - Nombre del módulo
**Retorna**: Instancia del módulo o None

#### `list_modules(category: str = None)`
**Propósito**: Listar módulos disponibles.
**Parámetros**: `category` - Categoría opcional para filtrar
**Retorna**: Diccionario con módulos organizados por categoría

#### `execute_module_function(module_name: str, function_name: str, *args, **kwargs)`
**Propósito**: Ejecutar una función específica de un módulo.
**Parámetros**: 
- `module_name` - Nombre del módulo
- `function_name` - Nombre de la función
- `*args, **kwargs` - Argumentos para la función

## 🔧 Router de Módulos (`module_router.py`)

### Clases Principales

#### `ModuleRequest`
**Propósito**: Estructura para solicitudes de uso de módulo.

**Atributos**:
- `module_name: str` - Nombre del módulo
- `function_name: str` - Nombre de la función
- `parameters: Dict[str, Any]` - Parámetros de la función
- `user_id: Optional[str]` - ID del usuario
- `session_id: Optional[str]` - ID de la sesión
- `priority: str` - Prioridad (low, normal, high, critical)
- `timeout: int` - Timeout en segundos

#### `ModuleResponse`
**Propósito**: Estructura para respuestas de módulo.

**Atributos**:
- `success: bool` - Indica si la ejecución fue exitosa
- `data: Any` - Datos de respuesta
- `error_message: Optional[str]` - Mensaje de error
- `execution_time: float` - Tiempo de ejecución
- `module_used: str` - Nombre del módulo usado
- `function_called: str` - Nombre de la función llamada

#### `ModuleRouter`
**Propósito**: Enrutador principal para acceso a módulos.

**Métodos principales**:
- `initialize()` - Inicializar el sistema de módulos
- `get_available_modules()` - Obtener módulos disponibles
- `get_module_documentation()` - Obtener documentación de un módulo
- `execute_module_request()` - Ejecutar solicitud de módulo
- `search_modules()` - Buscar módulos por nombre o descripción
- `get_usage_statistics()` - Obtener estadísticas de uso

#### `LLMModuleInterface`
**Propósito**: Interfaz simplificada para uso desde el LLM.

**Métodos principales**:
- `initialize()` - Inicializar la interfaz
- `call_module()` - Llamar a un módulo específico
- `list_modules()` - Listar módulos disponibles
- `get_module_info()` - Obtener información de un módulo
- `search_modules()` - Buscar módulos
- `get_usage_stats()` - Obtener estadísticas de uso

### Funciones de Conveniencia

#### `call_module(module_name: str, function_name: str, **kwargs)`
**Propósito**: Función de conveniencia para llamar módulos.
**Uso**: `await call_module("text_processor", "clean_text", text="Hola mundo")`

#### `get_modules(category: str = None)`
**Propósito**: Función de conveniencia para listar módulos.
**Uso**: `modules = get_modules("ai")`

#### `get_module_docs(module_name: str)`
**Propósito**: Función de conveniencia para obtener documentación.
**Uso**: `docs = get_module_docs("text_processor")`

## 🚀 Inicializador de Módulos (`initialize_modules.py`)

### Clases Principales

#### `ModuleInitializer`
**Propósito**: Inicializador y validador de módulos.

**Métodos principales**:
- `initialize_all_modules()` - Inicializar todos los módulos del sistema
- `_generate_initialization_report()` - Generar reporte de inicialización
- `_validate_critical_modules()` - Validar módulos críticos
- `_test_basic_functionality()` - Probar funcionalidad básica
- `save_report()` - Guardar reporte de inicialización
- `print_summary()` - Imprimir resumen de inicialización

### Funciones Principales

#### `main()`
**Propósito**: Función principal de inicialización.
**Uso**: `asyncio.run(main())`

#### `quick_status()`
**Propósito**: Función rápida para verificar el estado del sistema.
**Uso**: `quick_status()`

## ⚙️ Configuración del Sistema (`config/module_config.json`)

### Secciones Principales

#### `system_info`
- `name`: Nombre del sistema
- `version`: Versión del sistema
- `description`: Descripción del sistema
- `author`: Autor del sistema
- `created_date`: Fecha de creación
- `last_updated`: Última actualización

#### `initialization`
- `auto_initialize`: Inicialización automática
- `validate_critical_modules`: Validar módulos críticos
- `test_basic_functionality`: Probar funcionalidad básica
- `timeout_seconds`: Timeout de inicialización
- `retry_attempts`: Intentos de reintento
- `log_level`: Nivel de logging

#### `module_categories`
Configuración de cada categoría de módulos:
- `description`: Descripción de la categoría
- `priority`: Prioridad (high, medium, low)
- `critical_modules`: Módulos críticos de la categoría

#### `dependencies`
- `required_packages`: Paquetes requeridos
- `optional_packages`: Paquetes opcionales

#### `performance`
- `max_concurrent_requests`: Máximo de requests concurrentes
- `request_timeout`: Timeout de requests
- `memory_limit_mb`: Límite de memoria
- `cpu_limit_percent`: Límite de CPU
- `enable_caching`: Habilitar caché
- `cache_ttl_seconds`: TTL del caché

#### `logging`
- `level`: Nivel de logging
- `format`: Formato de logging
- `file_path`: Ruta del archivo de log
- `max_file_size_mb`: Tamaño máximo del archivo
- `backup_count`: Número de backups

#### `monitoring`
- `enable_metrics`: Habilitar métricas
- `metrics_interval_seconds`: Intervalo de métricas
- `enable_health_checks`: Habilitar health checks
- `health_check_interval_seconds`: Intervalo de health checks
- `alert_on_failure`: Alertar en fallos

#### `security`
- `enable_authentication`: Habilitar autenticación
- `enable_authorization`: Habilitar autorización
- `enable_rate_limiting`: Habilitar rate limiting
- `max_requests_per_minute`: Máximo de requests por minuto
- `enable_audit_logging`: Habilitar audit logging

#### `paths`
- `data_directory`: Directorio de datos
- `logs_directory`: Directorio de logs
- `models_directory`: Directorio de modelos
- `cache_directory`: Directorio de caché
- `config_directory`: Directorio de configuración

#### `features`
- `enable_async_execution`: Habilitar ejecución asíncrona
- `enable_module_hot_reload`: Habilitar hot reload de módulos
- `enable_dependency_injection`: Habilitar inyección de dependencias
- `enable_plugin_system`: Habilitar sistema de plugins
- `enable_metrics_collection`: Habilitar recolección de métricas
- `enable_error_recovery`: Habilitar recuperación de errores

## 🔄 Flujo de Trabajo del Sistema

### 1. Inicialización
```python
# Inicializar el sistema completo
await initialize_modules()

# O verificar estado rápido
quick_status()
```

### 2. Uso de Módulos
```python
# Obtener módulo específico
module = get_module("text_processor")

# Ejecutar función de módulo
result = await execute_module_function(
    "text_processor", 
    "clean_text", 
    text="  Hola mundo!  "
)

# Usar interfaz del LLM
result = await call_module("semantic_analyzer", "calculate_similarity", 
                         text1="Hola mundo", text2="Hello world")
```

### 3. Exploración de Módulos
```python
# Listar todos los módulos
all_modules = list_modules()

# Listar módulos por categoría
ai_modules = list_modules("ai")
blockchain_modules = list_modules("blockchain")

# Buscar módulos
search_results = search_modules("text")

# Obtener documentación
module_docs = get_module_docs("text_processor")
```

### 4. Monitoreo y Estadísticas
```python
# Obtener estadísticas de uso
stats = get_stats()

# Obtener información de módulo
module_info = get_module_info("text_processor")
```

## 🚨 Manejo de Errores

### Errores Comunes

1. **Módulo no encontrado**
   ```python
   # Error: ModuleNotFoundError
   # Solución: Verificar que el módulo esté registrado
   module = get_module("non_existent_module")
   ```

2. **Función no encontrada**
   ```python
   # Error: AttributeError
   # Solución: Verificar que la función exista en el módulo
   result = await execute_module_function("text_processor", "non_existent_function")
   ```

3. **Error de inicialización**
   ```python
   # Error: InitializationError
   # Solución: Verificar configuración y dependencias
   await initialize_modules()
   ```

### Logging y Debugging

```python
import logging

# Configurar logging detallado
logging.basicConfig(level=logging.DEBUG)

# Ver logs de inicialización
initializer = ModuleInitializer()
report = await initializer.initialize_all_modules()
initializer.print_summary()
```

## 📊 Métricas y Monitoreo

### Métricas Disponibles

1. **Uso de Módulos**
   - Número de llamadas por módulo
   - Tiempo promedio de ejecución
   - Tiempo total de ejecución
   - Última vez usado

2. **Errores**
   - Número de errores por módulo
   - Tipos de errores más comunes
   - Tiempo de recuperación

3. **Rendimiento**
   - Uso de memoria
   - Uso de CPU
   - Tiempo de respuesta

### Ejemplo de Monitoreo

```python
# Obtener estadísticas completas
stats = get_stats()

# Ver módulos más usados
usage_stats = stats["usage_stats"]
for module_func, data in usage_stats.items():
    print(f"{module_func}: {data['calls']} llamadas, {data['avg_time']:.3f}s promedio")

# Ver errores recientes
recent_errors = stats["recent_errors"]
for error in recent_errors:
    print(f"Error en {error['module']}.{error['function']}: {error['error']}")
```

## 🔧 Configuración Avanzada

### Personalización de Configuración

```python
# Modificar configuración en tiempo de ejecución
import json

with open("modules/config/module_config.json", "r") as f:
    config = json.load(f)

# Modificar configuración
config["performance"]["max_concurrent_requests"] = 20
config["logging"]["level"] = "DEBUG"

# Guardar configuración
with open("modules/config/module_config.json", "w") as f:
    json.dump(config, f, indent=2)
```

### Configuración de Módulos Específicos

```python
# Configurar módulo específico
module_info = get_module_info("text_processor")
if module_info:
    print(f"Estado: {module_info['status']}")
    print(f"Dependencias: {module_info['dependencies']}")
    print(f"Es asíncrono: {module_info['is_async']}")
```

## 🚀 Optimización y Mejores Prácticas

### 1. Inicialización Eficiente
```python
# Inicializar solo módulos necesarios
async def initialize_critical_modules():
    system = UnifiedModuleSystem()
    await system._register_ai_modules()
    await system._register_memory_modules()
    return system
```

### 2. Manejo de Errores Robusto
```python
async def safe_module_call(module_name: str, function_name: str, **kwargs):
    try:
        result = await call_module(module_name, function_name, **kwargs)
        return result
    except Exception as e:
        logger.error(f"Error en {module_name}.{function_name}: {e}")
        # Usar sistema de fallback
        return await get_fallback_response(module_name, function_name, **kwargs)
```

### 3. Caché de Módulos
```python
# Implementar caché para módulos frecuentemente usados
module_cache = {}

def get_cached_module(module_name: str):
    if module_name not in module_cache:
        module_cache[module_name] = get_module(module_name)
    return module_cache[module_name]
```

### 4. Monitoreo Continuo
```python
import asyncio

async def monitor_system_health():
    while True:
        try:
            # Verificar estado del sistema
            status = quick_status()
            if not status:
                logger.warning("Sistema de módulos no disponible")
                
            # Obtener métricas
            stats = get_stats()
            if stats["error_count"] > 10:
                logger.error("Demasiados errores en el sistema")
                
            await asyncio.sleep(60)  # Verificar cada minuto
        except Exception as e:
            logger.error(f"Error en monitoreo: {e}")
            await asyncio.sleep(30)
```

Esta documentación proporciona una visión completa del sistema principal de módulos, incluyendo todas las clases, funciones, configuraciones y mejores prácticas para su uso efectivo.
