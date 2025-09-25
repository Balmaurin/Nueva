# Núcleo Central - NeuroFusion

## Descripción

El núcleo central del sistema NeuroFusion contiene las configuraciones y componentes esenciales del sistema. Este módulo ha sido optimizado para eliminar duplicaciones y mejorar la eficiencia.

## Estructura Optimizada

```
nucleo_central/
├── __init__.py          # Inicialización del paquete (importaciones corregidas)
├── config/              # Configuraciones del sistema (apuntan a config centralizada)
│   ├── __init__.py      # Importaciones de configuraciones
│   ├── advanced_training.py
│   └── rate_limits.py
├── cleanup.py           # Script de limpieza y validación
└── README.md            # Este archivo
```

## Componentes

### Configuraciones (`config/`)

- **`advanced_training.py`**: Gestión de configuraciones para ejercicios de entrenamiento avanzado
- **`rate_limits.py`**: Gestión de límites de velocidad para operaciones del sistema

**Nota**: Las configuraciones JSON están centralizadas en el directorio `config/` raíz para evitar duplicación.

### Script de Limpieza (`cleanup.py`)

Script automatizado para:
- Eliminar archivos de caché (`__pycache__`, `*.pyc`, etc.)
- Verificar integridad de configuraciones centralizadas
- Validar importaciones de módulos
- Generar reportes de estado

## Optimizaciones Implementadas

### ✅ **Archivos Eliminados:**
- `__pycache__/` - Directorio de caché (se regenera automáticamente)
- `config/rate_limits.json` - Duplicado eliminado (usar `config/rate_limits.json`)
- `config/advanced_training_config.json` - Duplicado eliminado (usar `config/advanced_training_config.json`)

### ✅ **Importaciones Corregidas:**
- Rutas relativas actualizadas en `__init__.py`
- Configuraciones apuntan a archivos centralizados
- Manejo de errores mejorado

### ✅ **Configuraciones Centralizadas:**
- Todas las configuraciones JSON están en `config/` raíz
- Eliminación de duplicados
- Rutas actualizadas en archivos de configuración

## Uso

```python
# Importar componentes principales
from modules.nucleo_central import NeuroFusionCore, ModuleInitializer
from modules.nucleo_central.config import load_rate_limits, load_training_config

# Ejecutar limpieza y validación
python modules/nucleo_central/cleanup.py
```

## Mantenimiento

Para mantener el directorio optimizado:

1. **Ejecutar limpieza automática:**
   ```bash
   python modules/nucleo_central/cleanup.py
   ```

2. **Verificar configuraciones:**
   - Rate limits: `config/rate_limits.json`
   - Training config: `config/advanced_training_config.json`
   - NeuroFusion config: `config/config/neurofusion_config.json`

3. **Validar importaciones:**
   - El script de limpieza verifica automáticamente todas las importaciones

## Integración

El núcleo central se integra con:
- Sistema de módulos unificados (`modules/unified_systems/`)
- Sistema de seguridad centralizado (`modules/security/`)
- Sistema de configuración global (`config/`)

## Estado del Sistema

El directorio está optimizado y libre de:
- ✅ Archivos de caché innecesarios
- ✅ Configuraciones duplicadas
- ✅ Importaciones rotas
- ✅ Referencias obsoletas
