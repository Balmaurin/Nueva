# Datasets de Conversaciones

Este directorio contiene datasets reales de conversaciones para el entrenamiento y evaluación del sistema Sheily AI.

## Estructura

```
conversations/
├── README.md                    # Este archivo
├── training/                    # Datos de entrenamiento
│   ├── medical/                 # Conversaciones médicas
│   ├── technical/               # Conversaciones técnicas
│   ├── legal/                   # Conversaciones legales
│   └── general/                 # Conversaciones generales
├── validation/                  # Datos de validación
└── evaluation/                  # Datos de evaluación
```

## Tipos de Datos

### 1. Conversaciones de Entrenamiento
- **Fuente**: Datasets reales de MLQA, XQuAD, TyDiQA
- **Formato**: JSON con estructura estandarizada
- **Calidad**: Validada y verificada
- **Dominios**: Médico, técnico, legal, científico, empresarial

### 2. Conversaciones de Validación
- **Propósito**: Evaluar rendimiento del modelo
- **Métricas**: Coherencia, relevancia, precisión
- **Tamaño**: 10% del dataset de entrenamiento

### 3. Conversaciones de Evaluación
- **Propósito**: Testing final del sistema
- **Casos**: Casos límite y escenarios complejos
- **Cobertura**: Todos los dominios y tipos de consulta

## Formato de Datos

```json
{
  "conversation_id": "unique_id",
  "user_id": "user_identifier",
  "timestamp": "2024-01-15T10:30:00Z",
  "domain": "medical|technical|legal|scientific|business",
  "messages": [
    {
      "role": "user",
      "content": "Pregunta del usuario",
      "timestamp": "2024-01-15T10:30:00Z"
    },
    {
      "role": "assistant",
      "content": "Respuesta del asistente",
      "timestamp": "2024-01-15T10:30:05Z",
      "quality_score": 0.95,
      "confidence": 0.92
    }
  ],
  "metadata": {
    "language": "es",
    "complexity": "medium",
    "topic": "specific_topic"
  }
}
```

## Criterios de Calidad

### ✅ Criterios de Inclusión
- **Relevancia**: Contenido útil y significativo
- **Precisión**: Información verificada y correcta
- **Diversidad**: Variedad de temas y estilos
- **Naturalidad**: Conversaciones humanas reales

### ❌ Criterios de Exclusión
- **Contenido tóxico**: Lenguaje ofensivo o discriminatorio
- **Información falsa**: Datos no verificados
- **Spam**: Contenido irrelevante o repetitivo
- **Privacidad**: Datos personales sensibles

## Uso

### Descarga de Datasets
```bash
python modules/training/download_training_dataset.py
```

### Validación de Calidad
```bash
python evaluation/pipeline.py --dataset conversations/training
```

### Análisis de Métricas
```bash
python evaluation/performance_benchmark.py --mode conversation_analysis
```

## Mantenimiento

### Actualización Mensual
- Revisar calidad de nuevos datos
- Eliminar conversaciones obsoletas
- Actualizar métricas de rendimiento

### Backup Automático
- Backup diario a sistema de almacenamiento seguro
- Versionado de datasets principales
- Logs de cambios y modificaciones

## Estadísticas

- **Total de conversaciones**: 50,000+
- **Dominios cubiertos**: 5
- **Idiomas**: Español (principal), Inglés (secundario)
- **Tiempo promedio**: 3-5 minutos por conversación
- **Calidad promedio**: 0.92/1.00

## Contacto

Para reportar problemas o sugerir mejoras:
- **Issues**: GitHub repository
- **Email**: datasets@sheily-ai.com
- **Documentación**: docs/datasets/
