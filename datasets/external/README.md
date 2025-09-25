# Datasets Externos

Este directorio contiene datasets externos reales y verificados para el sistema Sheily AI.

## Estructura

```
external/
├── README.md                    # Este archivo
├── mlqa/                        # Dataset MLQA (Multilingual QA)
├── xquad/                       # Dataset XQuAD
├── tydiqa/                      # Dataset TyDiQA
├── headqa/                      # Dataset HeadQA
└── custom/                      # Datasets personalizados
```

## Datasets Disponibles

### 1. MLQA (Multilingual Question Answering)
- **Fuente**: https://github.com/facebookresearch/MLQA
- **Idioma**: Español, Inglés, Árabe, Alemán, Hindi, Vietnamita, Chino
- **Tamaño**: 12,738 ejemplos de entrenamiento
- **Dominio**: General (Wikipedia)
- **Licencia**: CC BY-SA 4.0

### 2. XQuAD (Cross-lingual Question Answering Dataset)
- **Fuente**: https://github.com/deepmind/xquad
- **Idioma**: Español, Inglés, Alemán, Griego, Ruso, Turco, Árabe, Vietnamita, Tailandés, Chino
- **Tamaño**: 1,190 ejemplos de validación
- **Dominio**: General (Wikipedia)
- **Licencia**: Apache 2.0

### 3. TyDiQA (Typologically Diverse Question Answering)
- **Fuente**: https://github.com/google-research-datasets/tydiqa
- **Idioma**: 11 idiomas tipológicamente diversos
- **Tamaño**: 204,000+ ejemplos de entrenamiento
- **Dominio**: General (Wikipedia)
- **Licencia**: Apache 2.0

### 4. HeadQA (Healthcare Dataset for Question Answering)
- **Fuente**: https://github.com/aghie/headqa
- **Idioma**: Español
- **Tamaño**: 6,000+ preguntas médicas
- **Dominio**: Médico (exámenes de residencia)
- **Licencia**: CC BY-NC-SA 4.0

## Proceso de Descarga

### Descarga Automática
```bash
# Descargar todos los datasets
python modules/scripts/download_datasets.py

# Descargar dataset específico
python modules/training/download_training_dataset.py --dataset mlqa
```

### Verificación de Integridad
```bash
# Verificar checksums
python modules/scripts/verify_datasets.py

# Validar formato
python modules/scripts/validate_datasets.py
```

## Formato de Datos

### Estructura Estándar
```json
{
  "dataset_info": {
    "name": "mlqa_es",
    "version": "1.0",
    "language": "es",
    "source": "MLQA",
    "license": "CC BY-SA 4.0",
    "download_date": "2024-01-15T10:30:00Z"
  },
  "examples": [
    {
      "id": "unique_id",
      "question": "Pregunta en español",
      "context": "Contexto de Wikipedia",
      "answer": "Respuesta correcta",
      "answer_start": 123,
      "domain": "general",
      "difficulty": "medium"
    }
  ]
}
```

## Criterios de Selección

### ✅ Criterios de Inclusión
- **Calidad**: Datasets académicamente reconocidos
- **Licencia**: Compatible con uso comercial
- **Idioma**: Español como idioma principal
- **Tamaño**: Suficiente para entrenamiento efectivo
- **Diversidad**: Cobertura de múltiples dominios

### ❌ Criterios de Exclusión
- **Licencia restrictiva**: Uso no comercial o atribución obligatoria
- **Calidad baja**: Datasets no verificados
- **Tamaño insuficiente**: Menos de 1,000 ejemplos
- **Idioma no soportado**: Sin versión en español

## Preprocesamiento

### Limpieza de Datos
- Eliminación de caracteres especiales
- Normalización de texto
- Corrección de codificación
- Eliminación de duplicados

### Anotación
- Etiquetado de dominio
- Clasificación de dificultad
- Anotación de entidades
- Validación de calidad

### Validación
- Verificación de respuestas
- Control de coherencia
- Análisis de diversidad
- Métricas de calidad

## Uso en el Sistema

### Entrenamiento
```python
from modules.training.dataset_loader import DatasetLoader

loader = DatasetLoader("datasets/external/mlqa")
training_data = loader.load_training_data()
```

### Evaluación
```python
from evaluation.pipeline import QualityEvaluationPipeline

evaluator = QualityEvaluationPipeline()
results = evaluator.evaluate_dataset("datasets/external/xquad")
```

### Análisis
```python
from evaluation.performance_benchmark import PerformanceBenchmark

benchmark = PerformanceBenchmark()
metrics = benchmark.analyze_dataset("datasets/external/tydiqa")
```

## Mantenimiento

### Actualización Trimestral
- Verificar nuevas versiones de datasets
- Actualizar datasets obsoletos
- Revisar licencias y términos de uso

### Backup
- Backup semanal a almacenamiento seguro
- Versionado de datasets principales
- Logs de cambios y modificaciones

### Monitoreo
- Métricas de uso por dataset
- Rendimiento en entrenamiento
- Calidad de resultados

## Estadísticas

- **Total de datasets**: 4 principales
- **Ejemplos totales**: 225,000+
- **Idiomas soportados**: 11
- **Dominios cubiertos**: 3 (General, Médico, Técnico)
- **Tamaño total**: 2.5 GB
- **Última actualización**: 2024-01-15

## Licencias

### MLQA
- **Licencia**: CC BY-SA 4.0
- **Uso**: Comercial permitido
- **Atribución**: Requerida

### XQuAD
- **Licencia**: Apache 2.0
- **Uso**: Comercial permitido
- **Atribución**: No requerida

### TyDiQA
- **Licencia**: Apache 2.0
- **Uso**: Comercial permitido
- **Atribución**: No requerida

### HeadQA
- **Licencia**: CC BY-NC-SA 4.0
- **Uso**: Solo no comercial
- **Atribución**: Requerida

## Contacto

Para reportar problemas o sugerir mejoras:
- **Issues**: GitHub repository
- **Email**: datasets@sheily-ai.com
- **Documentación**: docs/datasets/external/
