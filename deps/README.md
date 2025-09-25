# Sistema de Gestión de Dependencias - NeuroFusion

## Descripción

El sistema de gestión de dependencias del proyecto NeuroFusion proporciona herramientas completas para manejar todas las dependencias del proyecto de manera centralizada y automatizada. Incluye gestión, instalación, validación y monitoreo de dependencias de Python, Node.js y del sistema.

## Características Principales

### 🔧 Gestión Centralizada
- **DependenciesManager**: Gestor principal que maneja todas las dependencias del proyecto
- **DependencyInstaller**: Instalador automático con soporte para instalación paralela
- **DependencyValidator**: Validador de compatibilidad y versiones con detección de vulnerabilidades

### 📦 Soporte Multiplataforma
- **Python**: Gestión de paquetes pip con versiones específicas
- **Node.js**: Gestión de paquetes npm con semver
- **Sistema**: Instalación de dependencias del sistema operativo

### 🔒 Seguridad y Validación
- Detección automática de vulnerabilidades de seguridad conocidas
- Validación de compatibilidad entre dependencias
- Verificación de versiones mínimas requeridas
- Análisis de rendimiento y recomendaciones

### 📊 Monitoreo y Reportes
- Estadísticas detalladas de dependencias
- Reportes de validación con puntuaciones
- Logs de instalación y errores
- Backup y restore de configuraciones

## Estructura del Directorio

```
deps/
├── __init__.py                 # Paquete principal
├── dependencies_manager.py     # Gestor de dependencias
├── dependency_installer.py     # Instalador automático
├── dependency_validator.py     # Validador de dependencias
├── test_deps_system.py         # Script de pruebas
├── README.md                   # Documentación
├── package.json                # Configuración Node.js
├── _metadata.json              # Metadatos del sistema
├── requirements.txt            # Dependencias Python (generado)
├── python/                     # Dependencias Python específicas
├── node/                       # Dependencias Node.js específicas
├── system/                     # Dependencias del sistema
├── cache/                      # Caché de dependencias
├── backups/                    # Backups de configuraciones
├── installation_reports/       # Reportes de instalación
├── validation_reports/         # Reportes de validación
└── test_reports/               # Reportes de pruebas
```

## Instalación y Configuración

### Requisitos Previos

```bash
# Python 3.8+
python3 --version

# Node.js 16+
node --version

# npm 8+
npm --version

# Git 2.0+
git --version
```

### Instalación Automática

```python
from deps import initialize_deps_module

# Inicializar el sistema de dependencias
initialize_deps_module()
```

### Configuración Manual

```python
from deps import DependenciesManager

# Crear gestor de dependencias
manager = DependenciesManager("deps")

# Verificar dependencias
dependencies = manager.check_all_dependencies()

# Instalar dependencias faltantes
results = manager.install_missing_dependencies()
```

## Uso del Sistema

### Gestión Básica de Dependencias

```python
from deps import (
    get_dependency_stats,
    check_all_dependencies,
    install_missing_dependencies
)

# Obtener estadísticas
stats = get_dependency_stats()
print(f"Total: {stats.total_dependencies}, Instaladas: {stats.installed_dependencies}")

# Verificar estado de dependencias
dependencies = check_all_dependencies()
for dep in dependencies:
    print(f"{dep.name}: {'✅' if dep.installed else '❌'}")

# Instalar dependencias faltantes
results = install_missing_dependencies()
print(f"Instaladas: {len(results['success'])}, Fallidas: {len(results['failed'])}")
```

### Instalación Automática

```python
from deps import DependencyInstaller

# Crear instalador
installer = DependencyInstaller()

# Configuración de dependencias
config = {
    'python_dependencies': {
        'requests': {'version': '>=2.25.0', 'required': True},
        'numpy': {'version': '>=1.21.0', 'required': True}
    },
    'node_dependencies': {
        'react': {'version': '^18.0.0', 'required': True}
    }
}

# Instalar todas las dependencias
results = installer.install_all_dependencies(config)

# Obtener resumen
summary = installer.get_installation_summary()
print(f"Éxito: {summary['successful_installations']}/{summary['total_installations']}")
```

### Validación de Dependencias

```python
from deps import DependencyValidator

# Crear validador
validator = DependencyValidator()

# Validar dependencias
results = validator.validate_all_dependencies(config)

# Obtener resumen
summary = validator.get_validation_summary()
print(f"Puntuación: {summary.overall_score:.2f}/1.00")

# Mostrar reporte detallado
validator.print_validation_report()

# Guardar reporte
validator.save_validation_report()
```

### Gestión de Archivos de Configuración

```python
from deps import (
    create_requirements_txt,
    create_package_json,
    backup_dependencies,
    restore_dependencies
)

# Crear archivos de configuración
requirements_path = create_requirements_txt()
package_json_path = create_package_json()

# Crear backup
backup_path = backup_dependencies()

# Restaurar desde backup
success = restore_dependencies(backup_path)
```

## API de Referencia

### Clases Principales

#### DependenciesManager

```python
class DependenciesManager:
    def __init__(self, deps_dir: str = "deps")
    def check_all_dependencies() -> List[DependencyInfo]
    def get_dependency_stats() -> DependencyStats
    def install_missing_dependencies() -> Dict[str, List[str]]
    def create_requirements_txt() -> str
    def create_package_json() -> str
    def backup_dependencies() -> str
    def restore_dependencies(backup_path: str) -> bool
    def update_dependency_versions() -> Dict[str, List[str]]
    def cleanup_cache() -> int
```

#### DependencyInstaller

```python
class DependencyInstaller:
    def __init__(self, deps_dir: str = "deps")
    def install_all_dependencies(config: Dict) -> List[InstallationResult]
    def set_progress_callback(callback)
    def stop_installation_process()
    def get_installation_summary() -> Dict[str, Any]
    def save_installation_report(filepath: str = None) -> str
```

#### DependencyValidator

```python
class DependencyValidator:
    def __init__(self, deps_dir: str = "deps")
    def validate_all_dependencies(config: Dict) -> List[DependencyValidationResult]
    def get_validation_summary() -> ValidationSummary
    def save_validation_report(filepath: str = None) -> str
    def print_validation_report()
```

### Dataclasses

#### DependencyInfo

```python
@dataclass
class DependencyInfo:
    name: str
    version: str
    type: str  # 'python', 'node', 'system'
    source: str
    required: bool
    installed: bool
    installed_version: Optional[str]
    description: str
    dependencies: List[str]
```

#### DependencyStats

```python
@dataclass
class DependencyStats:
    total_dependencies: int
    installed_dependencies: int
    missing_dependencies: int
    outdated_dependencies: int
    python_dependencies: int
    node_dependencies: int
    system_dependencies: int
    last_updated: datetime
```

#### InstallationResult

```python
@dataclass
class InstallationResult:
    package_name: str
    package_type: str
    success: bool
    version_installed: Optional[str]
    error_message: Optional[str]
    installation_time: float
    dependencies_installed: List[str]
```

#### DependencyValidationResult

```python
@dataclass
class DependencyValidationResult:
    package_name: str
    package_type: str
    required_version: str
    installed_version: Optional[str]
    is_installed: bool
    is_compatible: bool
    compatibility_issues: List[str]
    security_issues: List[str]
    performance_issues: List[str]
    recommendations: List[str]
    validation_score: float
```

## Funciones de Utilidad

### Gestión General

```python
# Verificar dependencias
dependencies = check_all_dependencies()

# Obtener estadísticas
stats = get_dependency_stats()

# Instalar dependencias faltantes
results = install_missing_dependencies()

# Validar dependencias
validation_results = validate_dependencies(config)
```

### Gestión por Tipo

```python
# Python
python_dep = check_python_dependency('requests')
success = install_python_dependency('numpy', '>=1.21.0')
result = validate_python_dependency('torch', '>=1.9.0')

# Node.js
node_dep = check_node_dependency('react')
success = install_node_dependency('axios', '^0.27.0')
result = validate_node_dependency('next', '^12.0.0')

# Sistema
system_dep = check_system_dependency('git')
result = install_system_dependency('docker')
validation = validate_system_dependency('python3', '>=3.8')
```

### Configuración y Mantenimiento

```python
# Crear archivos de configuración
create_requirements_txt()
create_package_json()

# Backup y restore
backup_path = backup_dependencies()
restore_dependencies(backup_path)

# Actualización y limpieza
update_dependency_versions()
cleanup_cache()
```

## Configuración de Dependencias

### Dependencias de Python

El sistema incluye las siguientes dependencias de Python por defecto:

```python
python_dependencies = {
    # Core ML/AI
    'numpy': {'version': '>=1.21.0', 'required': True},
    'torch': {'version': '>=1.9.0', 'required': True},
    'transformers': {'version': '>=4.20.0', 'required': True},
    'sentence-transformers': {'version': '>=2.2.0', 'required': True},
    'faiss-cpu': {'version': '>=1.7.0', 'required': True},
    'scikit-learn': {'version': '>=1.0.0', 'required': True},
    
    # NLP
    'nltk': {'version': '>=3.7', 'required': True},
    'spacy': {'version': '>=3.4.0', 'required': True},
    
    # Databases
    'duckdb': {'version': '>=0.7.0', 'required': True},
    'psycopg2-binary': {'version': '>=2.9.0', 'required': True},
    'redis': {'version': '>=4.0.0', 'required': True},
    
    # Web Framework
    'fastapi': {'version': '>=0.68.0', 'required': True},
    'uvicorn': {'version': '>=0.15.0', 'required': True},
    'pydantic': {'version': '>=1.8.0', 'required': True},
    
    # Utilities
    'requests': {'version': '>=2.25.0', 'required': True},
    'aiohttp': {'version': '>=3.8.0', 'required': True},
    'watchdog': {'version': '>=2.1.0', 'required': True},
    'jsonschema': {'version': '>=3.2.0', 'required': True},
    'pyyaml': {'version': '>=6.0', 'required': True},
    
    # Development (optional)
    'pytest': {'version': '>=6.2.0', 'required': False},
    'black': {'version': '>=22.0.0', 'required': False},
    'flake8': {'version': '>=4.0.0', 'required': False}
}
```

### Dependencias de Node.js

```python
node_dependencies = {
    # Core React
    'react': {'version': '^18.0.0', 'required': True},
    'react-dom': {'version': '^18.0.0', 'required': True},
    'next': {'version': '^12.0.0', 'required': True},
    
    # TypeScript
    'typescript': {'version': '^4.9.0', 'required': True},
    '@types/react': {'version': '^18.0.0', 'required': True},
    '@types/node': {'version': '^18.0.0', 'required': True},
    
    # Styling
    'tailwindcss': {'version': '^3.0.0', 'required': True},
    'autoprefixer': {'version': '^10.4.0', 'required': True},
    'postcss': {'version': '^8.4.0', 'required': True},
    
    # HTTP Client
    'axios': {'version': '^0.27.0', 'required': True},
    
    # State Management
    'zustand': {'version': '^4.0.0', 'required': True},
    'react-query': {'version': '^3.39.0', 'required': True},
    
    # UI Components
    'react-hook-form': {'version': '^7.34.0', 'required': True},
    'framer-motion': {'version': '^6.3.0', 'required': True},
    'lucide-react': {'version': '^0.263.0', 'required': True},
    
    # Utilities
    'clsx': {'version': '^1.2.0', 'required': True},
    'date-fns': {'version': '^2.29.0', 'required': True},
    'recharts': {'version': '^2.5.0', 'required': True}
}
```

### Dependencias del Sistema

```python
system_dependencies = {
    'python3': {'version': '>=3.8', 'required': True},
    'pip': {'version': '>=20.0', 'required': True},
    'node': {'version': '>=16.0', 'required': True},
    'npm': {'version': '>=8.0', 'required': True},
    'git': {'version': '>=2.0', 'required': True},
    'docker': {'version': '>=20.0', 'required': False},
    'docker-compose': {'version': '>=2.0', 'required': False},
    'postgresql': {'version': '>=13.0', 'required': False},
    'redis': {'version': '>=6.0', 'required': False}
}
```

## Validación y Seguridad

### Detección de Vulnerabilidades

El sistema incluye una base de datos de vulnerabilidades conocidas:

```python
security_database = {
    'python': {
        'requests': {
            'versions': ['<2.25.0'],
            'severity': 'high',
            'description': 'Vulnerabilidad de seguridad en versiones anteriores a 2.25.0',
            'cve': 'CVE-2021-33503'
        }
    },
    'node': {
        'axios': {
            'versions': ['<0.21.0'],
            'severity': 'medium',
            'description': 'Vulnerabilidad de seguridad en versiones anteriores a 0.21.0',
            'cve': 'CVE-2021-3749'
        }
    }
}
```

### Matriz de Compatibilidad

```python
compatibility_matrix = {
    'python': {
        'torch': {
            'numpy': '>=1.21.0',
            'python': '>=3.8'
        },
        'transformers': {
            'torch': '>=1.9.0',
            'numpy': '>=1.21.0'
        }
    },
    'node': {
        'next': {
            'react': '>=18.0.0',
            'react-dom': '>=18.0.0',
            'node': '>=16.0'
        }
    }
}
```

## Pruebas y Validación

### Ejecutar Pruebas

```bash
# Ejecutar todas las pruebas
python deps/test_deps_system.py

# Ejecutar pruebas específicas
python -c "
from deps.test_deps_system import test_dependencies_manager
test_dependencies_manager()
"
```

### Reportes de Pruebas

Los reportes se guardan en `deps/test_reports/` con el siguiente formato:

```json
{
  "test_summary": {
    "total_tests": 7,
    "passed_tests": 7,
    "failed_tests": 0,
    "success_rate": 100.0,
    "timestamp": "2024-01-15T10:30:00"
  },
  "test_results": {
    "dependencies_manager": true,
    "dependency_installer": true,
    "dependency_validator": true,
    "deps_module": true,
    "deps_files": true,
    "deps_backup_restore": true,
    "deps_integration": true
  }
}
```

## Monitoreo y Logging

### Configuración de Logging

```python
import logging

# Configurar logging para el sistema de dependencias
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
```

### Niveles de Log

- **INFO**: Operaciones normales (instalación, verificación)
- **WARNING**: Problemas no críticos (dependencias opcionales faltantes)
- **ERROR**: Errores críticos (fallos de instalación, dependencias requeridas faltantes)
- **DEBUG**: Información detallada para debugging

### Archivos de Log

Los logs se guardan en:
- `deps/installation_reports/`: Reportes de instalación
- `deps/validation_reports/`: Reportes de validación
- `deps/test_reports/`: Reportes de pruebas

## Troubleshooting

### Problemas Comunes

#### Dependencias de Python no se instalan

```python
# Verificar pip
import subprocess
result = subprocess.run([sys.executable, '-m', 'pip', '--version'])

# Actualizar pip
subprocess.run([sys.executable, '-m', 'pip', 'install', '--upgrade', 'pip'])

# Limpiar caché
from deps import cleanup_cache
cleanup_cache()
```

#### Dependencias de Node.js no se instalan

```bash
# Verificar npm
npm --version

# Limpiar caché de npm
npm cache clean --force

# Verificar permisos
sudo chown -R $USER:$GROUP ~/.npm
```

#### Errores de permisos

```bash
# Para dependencias del sistema
sudo apt-get update
sudo apt-get install -y python3-pip nodejs npm

# Para directorios del proyecto
chmod -R 755 deps/
```

#### Conflictos de versiones

```python
# Validar dependencias
from deps import validate_dependencies
results = validate_dependencies(config)

# Verificar compatibilidad
for result in results:
    if not result.is_compatible:
        print(f"Conflicto en {result.package_name}: {result.compatibility_issues}")
```

### Debugging

```python
# Habilitar logging detallado
import logging
logging.getLogger('deps').setLevel(logging.DEBUG)

# Verificar estado del sistema
from deps import get_dependency_stats
stats = get_dependency_stats()
print(f"Estado: {stats}")

# Verificar archivos de configuración
import json
with open('deps/package.json', 'r') as f:
    print(json.dumps(json.load(f), indent=2))
```

## Contribución

### Agregar Nuevas Dependencias

1. **Python**: Agregar a `python_deps` en `DependenciesManager._load_dependency_configs()`
2. **Node.js**: Agregar a `node_deps` en `DependenciesManager._load_dependency_configs()`
3. **Sistema**: Agregar a `system_deps` en `DependenciesManager._load_dependency_configs()`

### Agregar Validaciones

1. **Vulnerabilidades**: Agregar a `security_database` en `DependencyValidator._load_validation_configs()`
2. **Compatibilidad**: Agregar a `compatibility_matrix` en `DependencyValidator._load_validation_configs()`
3. **Rendimiento**: Agregar a `performance_benchmarks` en `DependencyValidator._load_validation_configs()`

### Ejecutar Pruebas

```bash
# Ejecutar todas las pruebas
python deps/test_deps_system.py

# Ejecutar pruebas específicas
python -c "
from deps.test_deps_system import test_deps_integration
test_deps_integration()
"
```

## Licencia

Este sistema de gestión de dependencias es parte del proyecto NeuroFusion y está sujeto a la misma licencia del proyecto principal.

## Soporte

Para soporte técnico o reportar problemas:

1. Revisar la documentación en este README
2. Ejecutar las pruebas para identificar problemas
3. Revisar los logs en los directorios de reportes
4. Crear un issue en el repositorio del proyecto

---

**Versión**: 3.1.0  
**Última actualización**: Enero 2024  
**Mantenido por**: NeuroFusion Team
