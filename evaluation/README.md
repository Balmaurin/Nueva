# Sistema de Evaluación - Shaili AI

## 📁 Estructura del Sistema de Evaluación

```
evaluation/
├── diversity.py                    # 🎯 Evaluador de diversidad lingüística (200+ líneas)
├── toxicity.py                     # ⚠️ Evaluador de toxicidad (250+ líneas)
├── coherence.py                    # 🔗 Evaluador de coherencia (280+ líneas)
├── pipeline.py                     # 🔄 Pipeline de evaluación de calidad (235 líneas)
├── performance_benchmark.py        # 📊 Benchmark de rendimiento (250 líneas)
├── config.py                       # ⚙️ Configuración del sistema (250 líneas)
├── setup.py                        # 🚀 Script de instalación (288 líneas)
├── __init__.py                     # 📦 Paquete Python funcional (300+ líneas)
├── test_evaluation_system.py       # 🧪 Sistema de pruebas completo (400+ líneas)
└── README.md                       # 📖 Esta documentación
```

## 📊 Estadísticas del Sistema

### 📄 Archivos: 9
### 💻 Líneas de código: 2,000+
### 🐍 Python: 2,000+ líneas
### 🎯 Evaluadores: 5 clases principales
### ✅ Estado: Completamente funcional

## 🎯 Componentes del Sistema

### 1. **DiversityEvaluator** (`diversity.py`)

#### **Función Principal:**
Evaluar la diversidad lingüística de las respuestas generadas por el modelo de IA.

#### **Métricas Implementadas:**
- **Riqueza Léxica**:
  - Type-Token Ratio (TTR)
  - Índice de Guiraud
  - Índice de Herdan
- **Complejidad Sintáctica**:
  - Longitud promedio de oraciones
  - Variedad de estructuras gramaticales
  - Complejidad de palabras
- **Variación Semántica**:
  - Entropía de n-gramas (bigramas y trigramas)
  - Dispersión semántica

#### **Dependencias:**
```python
import numpy as np
import nltk
from nltk.tokenize import word_tokenize, sent_tokenize
from nltk.util import ngrams
from typing import List, Dict, Any
import re
import logging
```

#### **Instalación de Dependencias:**
```bash
pip install numpy nltk
python -m nltk.downloader punkt stopwords
```

#### **Uso:**
```python
from evaluation.diversity import DiversityEvaluator

evaluator = DiversityEvaluator()
diversity_metrics = evaluator.evaluate_diversity(texto)
print(f"Diversidad: {diversity_metrics['diversity_score']}")
```

### 2. **ToxicityEvaluator** (`toxicity.py`)

#### **Función Principal:**
Detectar y evaluar contenido tóxico o inapropiado en las respuestas del modelo.

#### **Categorías de Toxicidad:**
- **Insultos**: Palabras ofensivas directas
- **Discriminación**: Lenguaje discriminatorio
- **Sexismo**: Contenido sexista
- **Violencia**: Referencias violentas
- **Odio**: Expresiones de odio

#### **Métricas Implementadas:**
- **Detección de Lenguaje Tóxico**:
  - Análisis léxico por categorías
  - Puntuación de severidad
  - Detección de negaciones
- **Análisis Contextual**:
  - Patrones agresivos
  - Uso de mayúsculas excesivo
  - Análisis de entidades

#### **Dependencias:**
```python
import re
import numpy as np
from typing import List, Dict, Union, Any
import json
import os
import logging
```

#### **Uso:**
```python
from evaluation.toxicity import ToxicityEvaluator

evaluator = ToxicityEvaluator()
toxicity_result = evaluator.evaluate_toxicity(texto)
print(f"Es tóxico: {toxicity_result['is_toxic']}")
```

### 3. **CoherenceEvaluator** (`coherence.py`)

#### **Función Principal:**
Evaluar la coherencia semántica y lógica de las respuestas del modelo.

#### **Métricas Implementadas:**
- **Coherencia Semántica**: Similitud TF-IDF entre consulta y respuesta
- **Relevancia**: Presencia de palabras clave de la consulta
- **Estructura Lógica**: Análisis de conectores lógicos
- **Consistencia**: Verificación de entidades y coherencia interna

#### **Dependencias:**
```python
import numpy as np
from typing import Dict, Any, List
import re
import logging
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
```

#### **Instalación de Dependencias:**
```bash
pip install scikit-learn
```

#### **Uso:**
```python
from evaluation.coherence import CoherenceEvaluator

evaluator = CoherenceEvaluator()
coherence_score = evaluator.calculate_coherence(query, response)
print(f"Coherencia: {coherence_score}")
```

### 4. **QualityEvaluationPipeline** (`pipeline.py`)

#### **Función Principal:**
Pipeline completo para evaluar la calidad de las respuestas del modelo, combinando múltiples métricas.

#### **Características:**
- **Evaluación Integrada**: Combina coherencia, diversidad y toxicidad
- **Puntuación Compuesta**: Peso configurable para cada métrica
- **Umbrales de Calidad**: Configuración de estándares mínimos
- **Logging Detallado**: Registro de todas las evaluaciones
- **Evaluación de Conversaciones**: Análisis de conversaciones completas

#### **Métricas Combinadas:**
- **Coherencia** (40%): Relevancia y lógica
- **Diversidad** (30%): Variedad lingüística
- **Toxicidad** (30%): Ausencia de contenido inapropiado

#### **Uso:**
```python
from evaluation.pipeline import QualityEvaluationPipeline

pipeline = QualityEvaluationPipeline()
evaluation = pipeline.evaluate_response(query, response, domain="ciencia")
print(f"Puntuación: {evaluation['composite_score']}")
```

### 5. **PerformanceBenchmark** (`performance_benchmark.py`)

#### **Función Principal:**
Evaluar el rendimiento y eficiencia de los componentes del sistema de IA.

#### **Componentes Evaluados:**
- **Clustering Semántico**: `AdvancedSemanticClustering`
- **Optimización de Adapters**: `DomainAdapterOptimizer`
- **Expansión de Dominios**: `DomainExpansionEngine`

#### **Métricas de Rendimiento:**
- **Tiempo de Ejecución**: Duración de operaciones
- **Uso de Memoria**: Consumo de RAM/GPU
- **Escalabilidad**: Rendimiento con diferentes tamaños de datos
- **Coherencia**: Calidad de resultados

#### **Uso:**
```python
from evaluation.performance_benchmark import PerformanceBenchmark

benchmark = PerformanceBenchmark()
results = benchmark.run_comprehensive_benchmark()
print("Benchmark completado")
```

### 6. **EvaluationConfig** (`config.py`)

#### **Función Principal:**
Configuración centralizada del sistema de evaluación.

#### **Características:**
- **Umbrales de Calidad**: Configuración de estándares mínimos
- **Pesos de Métricas**: Configuración de importancia relativa
- **Configuración de Logging**: Niveles y formatos de logs
- **Configuración de Entorno**: Desarrollo, producción, testing

#### **Uso:**
```python
from evaluation.config import EvaluationConfig

# Obtener configuración
thresholds = EvaluationConfig.get_quality_thresholds()
weights = EvaluationConfig.get_quality_weights()

# Crear directorios
EvaluationConfig.create_directories()
```

### 7. **Setup Script** (`setup.py`)

#### **Función Principal:**
Script de instalación automática del sistema de evaluación.

#### **Características:**
- **Instalación de Dependencias**: Automática con pip
- **Descarga de Recursos**: Modelos NLP y datasets
- **Creación de Directorios**: Estructura de carpetas
- **Pruebas de Importación**: Verificación de módulos
- **Pruebas Básicas**: Validación de funcionalidad

#### **Uso:**
```bash
# Instalación completa
python evaluation/setup.py
```

### 8. **Paquete Python** (`__init__.py`)

#### **Función Principal:**
Transforma la carpeta `evaluation` en un paquete Python funcional.

#### **Características:**
- **API Unificada**: Funciones de conveniencia para evaluación rápida
- **Instancias Globales**: Gestión automática de evaluadores
- **Configuración Centralizada**: Acceso fácil a configuraciones
- **Validación Automática**: Verificación del sistema al importar
- **Reportes**: Generación automática de reportes de evaluación

#### **Uso:**
```python
import evaluation

# Evaluación rápida
diversity_score = evaluation.evaluate_diversity(texto)
toxicity_score = evaluation.evaluate_toxicity(texto)
coherence_score = evaluation.evaluate_coherence(query, response)

# Evaluación completa
quality_result = evaluation.evaluate_quality(query, response, domain="ciencia")

# Validación del sistema
validation = evaluation.validate_evaluation_system()
```

### 9. **Sistema de Pruebas** (`test_evaluation_system.py`)

#### **Función Principal:**
Sistema completo de pruebas para validar todos los componentes.

#### **Características:**
- **Pruebas Unitarias**: Validación individual de cada evaluador
- **Pruebas de Integración**: Verificación del pipeline completo
- **Pruebas de Configuración**: Validación de configuraciones
- **Reportes Automáticos**: Generación de reportes de pruebas
- **Validación del Paquete**: Pruebas de importación y API

#### **Uso:**
```bash
# Ejecutar todas las pruebas
python evaluation/test_evaluation_system.py
```

## 🔧 Instalación y Configuración

### 1. **Instalación Automática (Recomendada)**
```bash
# Ejecutar script de instalación
python evaluation/setup.py
```

### 2. **Instalación Manual**
```bash
# Instalar dependencias
pip install numpy nltk scikit-learn matplotlib

# Descargar recursos NLTK
python -m nltk.downloader punkt stopwords

# Crear directorios
mkdir -p logs/evaluation results/evaluation models/evaluation datasets/test
```

### 3. **Verificación de Instalación**
```bash
# Probar todos los evaluadores
python evaluation/diversity.py
python evaluation/toxicity.py
python evaluation/coherence.py
python evaluation/pipeline.py

# Ejecutar pruebas completas
python evaluation/test_evaluation_system.py
```

## 🚀 Ejecución del Sistema

### **Ejecución Individual de Evaluadores**

#### 1. Evaluación de Diversidad
```bash
cd evaluation
python diversity.py
```

#### 2. Evaluación de Toxicidad
```bash
cd evaluation
python toxicity.py
```

#### 3. Evaluación de Coherencia
```bash
cd evaluation
python coherence.py
```

#### 4. Pipeline Completo
```bash
cd evaluation
python pipeline.py
```

#### 5. Benchmark de Rendimiento
```bash
cd evaluation
python performance_benchmark.py
```

### **Ejecución del Sistema de Pruebas**
```bash
cd evaluation
python test_evaluation_system.py
```

## 📊 Configuración de Métricas

### **Umbrales de Calidad (Pipeline)**
```python
pipeline = QualityEvaluationPipeline(
    coherence_weight=0.4,      # Peso de coherencia
    diversity_weight=0.3,      # Peso de diversidad
    toxicity_weight=0.3,       # Peso de toxicidad
    coherence_threshold=0.6,   # Umbral mínimo de coherencia
    diversity_threshold=0.5,   # Umbral mínimo de diversidad
    toxicity_threshold=0.3     # Umbral máximo de toxicidad
)
```

### **Configuración de Logging**
```python
# Los evaluadores crean automáticamente:
# - logs/evaluation/quality_evaluation.log
# - logs/performance/performance_benchmark.log
```

## 🔍 Estructura de Datos

### **Resultado de Evaluación de Diversidad**
```python
{
    'diversity_score': 0.75,
    'lexical_metrics': {
        'type_token_ratio': 0.65,
        'guiraud_index': 12.3,
        'herdan_index': 0.45
    },
    'syntactic_metrics': {
        'avg_sentence_length': 15.2,
        'max_syntax_depth': 4,
        'pos_diversity': 0.78,
        'word_complexity': 5.8
    },
    'semantic_metrics': {
        'bigram_entropy': 8.5,
        'trigram_entropy': 12.3,
        'semantic_dispersion': 0.67
    }
}
```

### **Resultado de Evaluación de Toxicidad**
```python
{
    'is_toxic': False,
    'toxicity_score': 0.1,
    'base_toxicity': 0.05,
    'context_penalty': 0.03,
    'uppercase_penalty': 0.02,
    'toxic_categories': [],
    'context_analysis': {
        'entidades': ['plantas', 'energía'],
        'dependencias_agresivas': 0.05,
        'pattern_matches': [],
        'avg_word_length': 6.2,
        'uppercase_ratio': 0.02
    }
}
```

### **Resultado del Pipeline**
```python
{
    'composite_score': 0.82,
    'passes_quality': True,
    'metrics': {
        'coherence': {
            'score': 0.85,
            'passes_threshold': True
        },
        'diversity': {
            'score': 0.75,
            'passes_threshold': True
        },
        'toxicity': {
            'score': 0.90,
            'passes_threshold': True
        }
    },
    'domain': 'ciencia'
}
```

## 🛠️ Desarrollo y Extensión

### **Agregar Nuevas Métricas**

#### 1. Crear Nuevo Evaluador
```python
class CustomEvaluator:
    def __init__(self):
        # Inicialización
        pass
    
    def evaluate(self, text: str) -> Dict[str, Any]:
        # Lógica de evaluación
        return {'custom_score': 0.85}
```

#### 2. Integrar en Pipeline
```python
# En pipeline.py
from .custom_evaluator import CustomEvaluator

class QualityEvaluationPipeline:
    def __init__(self):
        self.custom_evaluator = CustomEvaluator()
        # ... resto del código
```

### **Personalizar Umbrales**
```python
# Crear configuración personalizada
config = {
    'coherence_threshold': 0.7,
    'diversity_threshold': 0.6,
    'toxicity_threshold': 0.2,
    'weights': {
        'coherence': 0.5,
        'diversity': 0.3,
        'toxicity': 0.2
    }
}
```

## 📈 Monitoreo y Logs

### **Ubicación de Logs**
- **Pipeline**: `logs/evaluation/`
- **Benchmark**: `logs/performance/`
- **Pruebas**: `results/evaluation/`

### **Tipos de Logs**
- **Evaluaciones**: Resultados detallados de cada evaluación
- **Rendimiento**: Métricas de tiempo y memoria
- **Errores**: Problemas durante la evaluación
- **Pruebas**: Reportes de validación del sistema

### **Visualización de Resultados**
```python
# El benchmark genera automáticamente:
# - performance_visualization.png
# - performance_results.json
# - test_report.json
```

## 🔧 Troubleshooting

### **Problemas Comunes**

#### 1. Error de Importación de NLTK
```bash
# Solución: Descargar recursos NLTK
python -m nltk.downloader punkt stopwords
```

#### 2. Error de Dependencias Faltantes
```bash
# Instalar dependencias
pip install numpy nltk scikit-learn matplotlib
```

#### 3. Error de Configuración
```bash
# Validar configuración
python evaluation/config.py
```

#### 4. Error de Memoria
```bash
# Reducir tamaño de datos de prueba
test_texts = evaluator.generate_test_data(num_texts=50)
```

## 📝 Notas de Implementación

### **Características Destacadas**
- ✅ **Evaluación Multi-dimensional**: Combina múltiples métricas
- ✅ **Configuración Flexible**: Umbrales y pesos ajustables
- ✅ **Logging Detallado**: Registro completo de evaluaciones
- ✅ **Visualización**: Gráficos automáticos de rendimiento
- ✅ **Extensibilidad**: Fácil agregar nuevas métricas
- ✅ **Paquete Python**: API unificada y fácil de usar
- ✅ **Sistema de Pruebas**: Validación completa del sistema
- ✅ **Sin Dependencias Externas**: No requiere SpaCy o transformers

### **Mejoras Implementadas**
- 🔧 **Eliminación de SpaCy**: Reemplazado con análisis basado en regex y NLTK
- 🔧 **Eliminación de Transformers**: Reemplazado con TF-IDF para similitud semántica
- 🔧 **Mejor Manejo de Errores**: Validación robusta y fallbacks
- 🔧 **API Unificada**: Funciones de conveniencia en el paquete
- 🔧 **Sistema de Pruebas**: Validación completa de todos los componentes

### **Limitaciones Actuales**
- ⚠️ **Análisis Sintáctico**: Limitado sin SpaCy (usando patrones simples)
- ⚠️ **Similitud Semántica**: Basada en TF-IDF en lugar de embeddings
- ⚠️ **Recursos de NLP**: Requiere descarga de recursos NLTK

### **Mejoras Futuras**
- 📋 **Métricas Adicionales**: Fluidez, precisión, completitud
- 📋 **Evaluación Automática**: Integración con CI/CD
- 📋 **Dashboard Web**: Interfaz para visualizar resultados
- 📋 **Optimización de Rendimiento**: Caching y procesamiento paralelo
- 📋 **Análisis Sintáctico Avanzado**: Integración con herramientas más sofisticadas

## 🎯 Integración con Shaili AI

### **Uso en el Sistema Principal**
```python
# En el sistema de IA
import evaluation

# Evaluar respuesta antes de enviar
quality_check = evaluation.evaluate_quality(query, response)

if quality_check['passes_quality']:
    # Enviar respuesta
    send_response(response)
else:
    # Generar respuesta alternativa
    generate_alternative_response()
```

### **Monitoreo Continuo**
```python
# Evaluar calidad de conversaciones completas
conversation_quality = evaluation.evaluate_conversation(conversation)
print(f"Calidad promedio: {conversation_quality['mean_composite_score']}")
```

### **Validación del Sistema**
```python
# Validar que todo funcione correctamente
validation = evaluation.validate_evaluation_system()
if validation['overall_status']:
    print("✅ Sistema de evaluación funcionando correctamente")
else:
    print("❌ Problemas detectados en el sistema de evaluación")
```

## 🚀 Instalación Rápida

### **Opción 1: Instalación Automática (Recomendada)**
```bash
# Clonar o navegar al directorio del proyecto
cd /path/to/shaili-ai

# Ejecutar instalación automática
python evaluation/setup.py
```

### **Opción 2: Instalación Manual**
```bash
# 1. Instalar dependencias
pip install numpy nltk scikit-learn matplotlib

# 2. Descargar recursos NLP
python -m nltk.downloader punkt stopwords

# 3. Crear directorios
mkdir -p logs/evaluation results/evaluation models/evaluation datasets/test

# 4. Validar configuración
python evaluation/config.py
```

### **Verificación de Instalación**
```bash
# Probar todos los evaluadores
python evaluation/diversity.py
python evaluation/toxicity.py
python evaluation/coherence.py
python evaluation/pipeline.py

# Ejecutar pruebas completas
python evaluation/test_evaluation_system.py
```

## 📊 Resultados Esperados

### **Ejemplo de Salida del Pipeline**
```json
{
  "composite_score": 0.82,
  "passes_quality": true,
  "metrics": {
    "coherence": {"score": 0.85, "passes_threshold": true},
    "diversity": {"score": 0.75, "passes_threshold": true},
    "toxicity": {"score": 0.90, "passes_threshold": true}
  }
}
```

### **Ejemplo de Salida de Pruebas**
```json
{
  "test_summary": {
    "total_tests": 7,
    "passed_tests": 7,
    "failed_tests": 0
  },
  "overall_status": true
}
```

---

**Nota**: Este sistema de evaluación es fundamental para garantizar la calidad de las respuestas del modelo de IA. Se recomienda ejecutar evaluaciones regularmente y ajustar los umbrales según las necesidades específicas del proyecto. El sistema está completamente funcional y no requiere dependencias externas complejas.
