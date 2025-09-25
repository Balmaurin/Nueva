# Guía del Orquestador de Shaili-AI

## Descripción General

El Orquestador de Shaili-AI es el componente central que coordina todos los elementos del sistema, incluyendo:

- **Clasificación de Dominio**: Identifica automáticamente el área de conocimiento de cada consulta
- **Enrutamiento Semántico**: Dirige las consultas al componente más apropiado
- **Gestión de Ramas**: Maneja las 35 macro-ramas especializadas
- **Sistema RAG**: Recuperación aumentada de conocimiento
- **Políticas de Adapters**: Optimización automática de rendimiento

## Arquitectura del Sistema

```
┌─────────────────────────────────────────────────────────────┐
│                    MainOrchestrator                         │
├─────────────────────────────────────────────────────────────┤
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐        │
│  │ Domain      │  │ Semantic    │  │ Branch      │        │
│  │ Classifier  │  │ Router      │  │ Manager     │        │
│  └─────────────┘  └─────────────┘  └─────────────┘        │
│                                                             │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐        │
│  │ RAG         │  │ Adapter     │  │ Base        │        │
│  │ Retriever   │  │ Policy      │  │ Model       │        │
│  └─────────────┘  └─────────────┘  └─────────────┘        │
└─────────────────────────────────────────────────────────────┘
```

## Componentes Principales

### 1. MainOrchestrator

El orquestador principal que coordina todos los componentes.

**Características:**
- Procesamiento completo de consultas
- Caché inteligente de respuestas
- Monitoreo y métricas en tiempo real
- Optimización automática del sistema

**Uso básico:**
```python
from modules.orchestrator.main_orchestrator import MainOrchestrator

# Crear orquestador
orchestrator = MainOrchestrator()

# Procesar consulta
response = orchestrator.process_query("¿Qué es la inteligencia artificial?")
print(response['text'])
```

### 2. DomainClassifier

Clasifica automáticamente las consultas en uno de los 35 dominios disponibles.

**Dominios disponibles:**
- Matemáticas
- Computación y Programación
- Física
- Química
- Biología
- Medicina y Salud
- Ingeniería
- Economía y Finanzas
- Educación y Pedagogía
- Historia
- Arte, Música y Cultura
- Literatura y Escritura
- Deportes y eSports
- Cocina y Nutrición
- Viajes e Idiomas
- Vida Diaria, Legal, Práctico y Trámites
- Y 19 dominios más...

**Uso:**
```python
from modules.orchestrator.domain_classifier import DomainClassifier

classifier = DomainClassifier()
domain, confidence = classifier.predict("Explica el teorema de Pitágoras")
print(f"Dominio: {domain}, Confianza: {confidence}")
```

### 3. SemanticRouter

Enruta las consultas al componente más apropiado basado en el dominio y contenido.

**Tipos de ruta:**
- `branch`: Rama especializada del dominio
- `rag`: Sistema de recuperación de conocimiento
- `core`: Modelo base general

**Uso:**
```python
from modules.orchestrator.router import SemanticRouter

router = SemanticRouter(base_model, domain_classifier, rag_retriever)
route_type, route_details = router.route("¿Cómo funciona la fotosíntesis?")
```

### 4. BranchManager

Gestiona las 35 macro-ramas y sus micro-ramas especializadas.

**Funcionalidades:**
- Carga de adapters especializados
- Detección de ramas emergentes
- Gestión de micro-ramas
- Estado y métricas de ramas

**Uso:**
```python
from branches.branch_manager import BranchManager

manager = BranchManager()
domains = manager.get_available_domains()
status = manager.get_branch_status("Matemáticas")
```

### 5. AdapterUpdatePolicy

Optimiza automáticamente el rendimiento y gestión de memoria de los adapters.

**Características:**
- Caché LRU de adapters
- Compresión automática
- Backup de adapters
- Métricas de rendimiento

**Uso:**
```python
from branches.adapter_policy import AdapterUpdatePolicy

policy = AdapterUpdatePolicy()
result = policy.manage_domain_adapters("Matemáticas", metrics)
optimization = policy.optimize_cache()
```

## API REST

El orquestador expone una API REST completa en `/api/orchestrator/`.

### Endpoints Principales

#### Health Check
```bash
GET /api/orchestrator/health
```

#### Procesar Consulta
```bash
POST /api/orchestrator/query
Content-Type: application/json

{
  "query": "¿Qué es la inteligencia artificial?",
  "user_context": {
    "language": "es",
    "user_id": "12345"
  }
}
```

#### Estado del Sistema
```bash
GET /api/orchestrator/status
```

#### Estado de Ramas
```bash
GET /api/orchestrator/branches
GET /api/orchestrator/branches/{domain}
```

#### Métricas
```bash
GET /api/orchestrator/metrics
```

#### Optimización
```bash
POST /api/orchestrator/optimize
```

#### Configuración
```bash
GET /api/orchestrator/config
PUT /api/orchestrator/config
```

#### Limpiar Caché
```bash
POST /api/orchestrator/cache/clear
```

#### Dominios Disponibles
```bash
GET /api/orchestrator/domains
GET /api/orchestrator/domains/{domain}/micro-branches
```

## Configuración

### Configuración del Orquestador

```python
config = {
    'enable_domain_classification': True,
    'enable_semantic_routing': True,
    'enable_branch_management': True,
    'enable_rag': True,
    'enable_adapter_policy': True,
    'max_response_time': 30.0,
    'enable_caching': True,
    'cache_ttl': 3600,
    'enable_monitoring': True,
    'log_level': 'INFO'
}

orchestrator = MainOrchestrator(config)
```

### Configuración de Política de Adapters

```python
adapter_config = {
    'max_adapters_in_memory': 8,
    'adapter_cache_ttl': 3600,
    'performance_threshold': 0.7,
    'memory_threshold': 0.8,
    'update_frequency': 300,
    'backup_adapters': True,
    'compression_enabled': True
}

policy = AdapterUpdatePolicy(adapter_config)
```

## Scripts de Utilidad

### Inicialización
```bash
python scripts/init_orchestrator.py
```

Este script:
- Verifica dependencias
- Valida archivos del modelo
- Comprueba estructura de ramas
- Prueba componentes del orquestador
- Genera reporte de inicialización

### Pruebas
```bash
python scripts/test_orchestrator.py
```

Este script:
- Prueba el orquestador directamente
- Verifica gestión de ramas
- Prueba política de adapters
- Valida API REST
- Genera reporte de pruebas

## Monitoreo y Métricas

### Métricas Disponibles

- **Rendimiento:**
  - Total de requests
  - Requests exitosos/fallidos
  - Tiempo promedio de respuesta
  - Tasa de éxito

- **Distribución:**
  - Uso por dominio
  - Uso por tipo de ruta
  - Patrones de consulta

- **Caché:**
  - Tamaño del caché
  - Tasa de aciertos
  - Entradas expiradas

### Logs

Los logs se guardan en:
- `logs/orchestrator_monitoring.log`: Datos de monitoreo
- `logs/orchestrator_init.log`: Logs de inicialización
- `logs/orchestrator_test_report.json`: Reportes de pruebas

## Optimización

### Optimización Automática

El sistema incluye optimización automática:

1. **Caché de Adapters:** Gestión LRU automática
2. **Compresión:** Adapters inactivos se comprimen
3. **Limpieza:** Entradas expiradas se eliminan automáticamente
4. **Backup:** Adapters importantes se respaldan

### Optimización Manual

```python
# Optimizar sistema completo
optimization_results = orchestrator.optimize_system()

# Limpiar caché
orchestrator.response_cache.clear()

# Optimizar política de adapters
policy.optimize_cache()
```

## Troubleshooting

### Problemas Comunes

1. **Error de modelo no encontrado:**
   - Verificar que el modelo esté en `models/custom/shaili-personal-model`
   - Ejecutar script de inicialización

2. **Error de dependencias:**
   - Instalar dependencias: `pip install -r requirements.txt`
   - Verificar versión de Python (3.8+)

3. **Error de memoria:**
   - Reducir `max_adapters_in_memory`
   - Habilitar compresión
   - Limpiar caché manualmente

4. **Error de API:**
   - Verificar que el servidor esté ejecutándose en puerto 8000
   - Comprobar logs del servidor
   - Validar configuración CORS

### Logs de Debug

Para habilitar logs detallados:

```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

## Integración con Frontend

### Ejemplo de Integración React

```javascript
// Procesar consulta
const processQuery = async (query) => {
  try {
    const response = await fetch('/api/orchestrator/query', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        query: query,
        user_context: {
          language: 'es',
          user_id: 'current_user'
        }
      })
    });
    
    const data = await response.json();
    return data.data;
  } catch (error) {
    console.error('Error procesando consulta:', error);
  }
};

// Obtener estado del sistema
const getSystemStatus = async () => {
  const response = await fetch('/api/orchestrator/status');
  return await response.json();
};
```

## Próximas Mejoras

- [ ] Soporte para múltiples idiomas
- [ ] Aprendizaje continuo de adapters
- [ ] Integración con bases de datos vectoriales
- [ ] Dashboard de monitoreo en tiempo real
- [ ] API GraphQL
- [ ] Soporte para streaming de respuestas

## Contribución

Para contribuir al desarrollo del orquestador:

1. Fork del repositorio
2. Crear rama para nueva funcionalidad
3. Implementar cambios
4. Ejecutar pruebas: `python scripts/test_orchestrator.py`
5. Crear Pull Request

## Licencia

Este proyecto está bajo la licencia MIT. Ver `LICENSE` para más detalles.
