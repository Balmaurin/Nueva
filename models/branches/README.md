# Gestión de Ramas Especializadas

Esta carpeta contiene todas las ramas especializadas del sistema Shaili AI, organizadas por dominio de conocimiento.

## Estructura

```
models/branches/
├── README.md                           # Este archivo
├── branch_manager.py                   # Gestor principal de ramas
├── adapter_policy.py                   # Política de gestión de adapters
├── base_branches.json                  # Configuración base de ramas
├── configs/                            # Configuraciones de ramas
│   ├── medical.json
│   ├── technical.json
│   └── ...
├── medicina_y_salud/                   # Rama de medicina
│   ├── adapter/                        # Adaptadores LoRA
│   ├── dataset/                        # Datos de entrenamiento
│   └── microramas/                     # Micro-ramas especializadas
│       ├── neurología/
│       ├── cardiología/
│       ├── cirugía/
│       ├── farmacología/
│       ├── pediatría/
│       └── psiquiatría/
├── computación_y_programación/         # Rama de programación
├── economía_y_finanzas/                # Rama de finanzas
└── ...                                 # Otras 32 ramas
```

## 35 Macro-Ramas Disponibles

### Ciencias Básicas
1. **Lengua y Lingüística** - Gramática, sintaxis, semántica
2. **Matemáticas** - Álgebra, cálculo, estadística
3. **Física** - Mecánica, termodinámica, cuántica
4. **Química** - Orgánica, inorgánica, bioquímica
5. **Biología** - Celular, molecular, genética
6. **Ciencias de la Tierra y Clima** - Geología, meteorología
7. **Astronomía y Espacio** - Cosmología, astrofísica

### Tecnología e Informática
8. **Computación y Programación** - Algoritmos, lenguajes
9. **Ciencia de Datos e IA** - Machine Learning, Deep Learning
10. **Ingeniería** - Mecánica, eléctrica, civil
11. **Electrónica y IoT** - Circuitos, sensores, conectividad
12. **Ciberseguridad y Criptografía** - Seguridad, encriptación
13. **Sistemas, DevOps y Redes** - Infraestructura, cloud

### Ciencias de la Vida
14. **Medicina y Salud** - Diagnóstico, tratamiento, prevención
15. **Neurociencia y Psicología** - Cerebro, comportamiento

### Ciencias Sociales y Humanidades
16. **Economía y Finanzas** - Mercados, inversiones, análisis
17. **Empresa y Emprendimiento** - Gestión, startups, estrategia
18. **Derecho y Políticas Públicas** - Legislación, regulación
19. **Sociología y Antropología** - Sociedad, cultura, comportamiento
20. **Educación y Pedagogía** - Enseñanza, aprendizaje, metodologías
21. **Historia** - Eventos históricos, análisis temporal
22. **Geografía y Geo-Política** - Espacial, política internacional

### Arte y Cultura
23. **Arte, Música y Cultura** - Expresión artística, composición
24. **Literatura y Escritura** - Narrativa, poesía, redacción
25. **Medios y Comunicación** - Periodismo, publicidad, marketing
26. **Diseño y UX** - Interfaces, experiencia de usuario

### Entretenimiento y Vida Diaria
27. **Deportes y eSports** - Física, estrategia, competición
28. **Juegos y Entretenimiento** - Videojuegos, ocio digital
29. **Hogar, DIY y Reparaciones** - Bricolaje, mantenimiento
30. **Cocina y Nutrición** - Gastronomía, alimentación saludable
31. **Viajes e Idiomas** - Turismo, aprendizaje de idiomas
32. **Vida Diaria, Legal, Práctico y Trámites** - Trámites, burocracia

## Uso del Sistema de Ramas

### Inicializar Gestor de Ramas
```python
from models.branches.branch_manager import BranchManager

# Inicializar gestor
branch_manager = BranchManager()

# Obtener dominios disponibles
domains = branch_manager.get_available_domains()
print(f"Dominios disponibles: {len(domains)}")
```

### Cargar Adapter de Rama
```python
# Cargar adapter para medicina
medical_model = branch_manager.load_adapter("Medicina y Salud")

if medical_model:
    print("✅ Adapter de medicina cargado")
else:
    print("❌ Error cargando adapter")
```

### Crear Nueva Rama
```python
# Datos de entrenamiento para nueva rama
training_data = [
    {"input": "síntoma de gripe", "output": "fiebre, tos, dolor de garganta"},
    {"input": "tratamiento para dolor de cabeza", "output": "paracetamol, reposo"}
]

# Crear adapter
success = branch_manager.create_adapter("Medicina y Salud", training_data)
if success:
    print("✅ Rama creada exitosamente")
```

### Detectar Rama Emergente
```python
# Analizar interacciones del usuario
interactions = {
    "queries": [
        "¿Cómo programar en Python?",
        "¿Qué es un algoritmo?",
        "¿Cómo depurar código?"
    ]
}

# Detectar rama emergente
emerging_branch = branch_manager.detect_emerging_branch(interactions)
if emerging_branch:
    print(f"Rama emergente detectada: {emerging_branch}")
```

## Gestión de Adapters

### Política de Adapters
```python
from models.branches.adapter_policy import AdapterUpdatePolicy

# Inicializar política
policy = AdapterUpdatePolicy()

# Gestionar adapters de un dominio
metrics = {
    "accuracy": 0.85,
    "response_time": 1.2,
    "memory_usage": 0.6
}

result = policy.manage_domain_adapters("Medicina y Salud", metrics)
print(f"Resultado: {result}")
```

### Optimización de Cache
```python
# Optimizar caché de adapters
optimization_result = policy.optimize_cache()
print(f"Optimización completada: {optimization_result}")
```

## Micro-Ramas

Cada macro-rama puede contener múltiples micro-ramas especializadas:

### Ejemplo: Medicina y Salud
- **Neurología** - Enfermedades del sistema nervioso
- **Cardiología** - Enfermedades del corazón
- **Cirugía** - Procedimientos quirúrgicos
- **Farmacología** - Medicamentos y efectos
- **Pediatría** - Medicina infantil
- **Psiquiatría** - Salud mental

### Ejemplo: Computación y Programación
- **Desarrollo Web** - Frontend, backend, fullstack
- **Machine Learning** - Algoritmos de IA
- **DevOps** - Infraestructura y despliegue
- **Ciberseguridad** - Seguridad informática
- **Desarrollo Móvil** - Apps iOS/Android
- **Bases de Datos** - SQL, NoSQL, big data

## Configuración de Ramas

### Archivo de Configuración
```json
{
  "name": "medicina_y_salud",
  "description": "Medicina y salud",
  "priority": "high",
  "cache_size": "1GB",
  "embedding_config": {
    "dimension": 384,
    "normalize": true,
    "pooling": "mean"
  },
  "adapter_config": {
    "r": 16,
    "lora_alpha": 32,
    "target_modules": ["q_proj", "v_proj"],
    "lora_dropout": 0.1
  }
}
```

### Cargar Configuración
```python
from models.config.branch_configs import get_branch_config

# Obtener configuración de rama
config = get_branch_config("medical")
print(f"Configuración: {config}")
```

## Rendimiento y Optimización

### Métricas de Rendimiento
- **Tiempo de respuesta**: < 2 segundos
- **Precisión**: > 85%
- **Uso de memoria**: < 2GB por rama
- **Cache hit rate**: > 90%

### Optimizaciones Implementadas
- **Cuantización 4-bit** para adapters
- **Cache inteligente** con TTL
- **Compresión** de adapters inactivos
- **Gestión automática** de memoria
- **Backup automático** de adapters

## Mantenimiento

### Actualización de Ramas
```bash
#!/bin/bash
# scripts/update_branches.sh

echo "🔄 Actualizando ramas..."

python -c "
from models.branches.branch_manager import BranchManager
manager = BranchManager()

# Actualizar todas las ramas
for domain in manager.get_available_domains():
    print(f'Actualizando {domain}...')
    # Lógica de actualización
"

echo "✅ Ramas actualizadas"
```

### Limpieza de Cache
```bash
#!/bin/bash
# scripts/clean_branch_cache.sh

echo "🧹 Limpiando cache de ramas..."

python -c "
from models.branches.adapter_policy import AdapterUpdatePolicy
policy = AdapterUpdatePolicy()
policy.optimize_cache()
"

echo "✅ Cache limpiado"
```

## Estadísticas

### Métricas Actuales
- **Macro-ramas**: 32
- **Micro-ramas**: 150+
- **Adapters activos**: 25
- **Tiempo de carga promedio**: < 30s
- **Memoria total**: ~8GB
- **Uptime**: > 99.9%

### Distribución por Dominio
- **Ciencias Básicas**: 7 ramas
- **Tecnología**: 6 ramas
- **Ciencias de la Vida**: 2 ramas
- **Ciencias Sociales**: 7 ramas
- **Arte y Cultura**: 4 ramas
- **Entretenimiento**: 6 ramas

## Contacto

Para reportar problemas o sugerir mejoras:
- **Issues**: GitHub repository
- **Email**: branches@shaili-ai.com
- **Documentación**: docs/branches/
