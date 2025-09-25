# Documentación de Módulos de Entrenamiento

## 🎓 Módulo de Entrenamiento (`training/`)

### 📁 Estructura del Módulo
```
training/
├── __init__.py
├── add_more_training_data.py              # Agregar más datos de entrenamiento
├── advanced_training_system.py            # Sistema avanzado de entrenamiento
├── automatic_lora_trainer.py              # Entrenador automático LoRA
├── download_headqa_dataset.py             # Descargar dataset HEAD-QA
├── download_training_dataset.py           # Descargar dataset de entrenamiento
├── expand_headqa_dataset.py               # Expandir dataset HEAD-QA
├── import_datasets_to_branches.py         # Importar datasets a ramas
├── llm_training_pipeline.py               # Pipeline de entrenamiento LLM
├── lora_finetuning_generator.py           # Generador de fine-tuning LoRA
└── training_token_sync.py                 # Sincronización de tokens de entrenamiento
```

## 📊 Agregar Más Datos de Entrenamiento (`add_more_training_data.py`)

### Funciones Principales

#### `add_training_data()`
**Propósito**: Agregar datos de entrenamiento adicionales al sistema.

**Parámetros**:
- `data_source: str` - Fuente de datos
- `data_type: str` - Tipo de datos
- `domain: str` - Dominio de los datos
- `quality_threshold: float = 0.8` - Umbral de calidad

**Ejemplo de uso**:
```python
from modules.training.add_more_training_data import add_training_data

# Agregar datos de entrenamiento
result = add_training_data(
    data_source="external_api",
    data_type="question_answer",
    domain="artificial_intelligence",
    quality_threshold=0.85
)

print(f"Datos agregados: {result['added_count']}")
print(f"Calidad promedio: {result['average_quality']}")
```

## 🚀 Sistema Avanzado de Entrenamiento (`advanced_training_system.py`)

### Clases Principales

#### `AdvancedTrainingSystem`
**Propósito**: Sistema avanzado de entrenamiento con múltiples estrategias.

**Métodos principales**:
- `__init__()` - Inicializar sistema
- `start_exercise_session(user_id: str, exercise_id: str) -> Dict[str, Any]` - Iniciar sesión de ejercicio
- `submit_answer(session_id: str, user_id: str, question_id: str, answer: str) -> Dict[str, Any]` - Enviar respuesta
- `start_monitoring()` - Iniciar monitoreo
- `get_training_statistics() -> Dict[str, Any]` - Obtener estadísticas de entrenamiento

**Ejemplo de uso**:
```python
from modules.training.advanced_training_system import AdvancedTrainingSystem

# Inicializar sistema de entrenamiento
training_system = AdvancedTrainingSystem()

# Iniciar sesión de ejercicio
session = training_system.start_exercise_session("usuario1", "exercise_001")
print(f"Sesión iniciada: {session['session_id']}")

# Enviar respuesta
result = training_system.submit_answer(
    session_id=session["session_id"],
    user_id="usuario1",
    question_id="question_001",
    answer="La inteligencia artificial es una rama de la informática."
)

print(f"Respuesta correcta: {result['is_correct']}")
print(f"Puntuación: {result['score']}")

# Obtener estadísticas
stats = training_system.get_training_statistics()
print(f"Total de sesiones: {stats['total_sessions']}")
print(f"Promedio de puntuación: {stats['average_score']}")
```

## 🔄 Entrenador Automático LoRA (`automatic_lora_trainer.py`)

### Clases Principales

#### `AutomaticLoRATrainer`
**Propósito**: Entrenador automático de LoRA (Low-Rank Adaptation).

**Métodos principales**:
- `__init__()` - Inicializar entrenador
- `prepare_dataset(data_path: str) -> Dataset` - Preparar dataset
- `train_lora_adapter(model_name: str, dataset: Dataset, output_path: str) -> Dict[str, Any]` - Entrenar adaptador LoRA
- `evaluate_adapter(adapter_path: str, test_dataset: Dataset) -> Dict[str, float]` - Evaluar adaptador
- `optimize_hyperparameters(dataset: Dataset) -> Dict[str, Any]` - Optimizar hiperparámetros

**Ejemplo de uso**:
```python
from modules.training.automatic_lora_trainer import AutomaticLoRATrainer

# Inicializar entrenador LoRA
lora_trainer = AutomaticLoRATrainer()

# Preparar dataset
dataset = lora_trainer.prepare_dataset("data/training_data.json")

# Optimizar hiperparámetros
hyperparams = lora_trainer.optimize_hyperparameters(dataset)
print(f"Hiperparámetros optimizados: {hyperparams}")

# Entrenar adaptador LoRA
training_result = lora_trainer.train_lora_adapter(
    model_name="gpt2",
    dataset=dataset,
    output_path="models/lora_adapters/ai_domain"
)

print(f"Entrenamiento completado: {training_result['status']}")
print(f"Pérdida final: {training_result['final_loss']}")

# Evaluar adaptador
evaluation = lora_trainer.evaluate_adapter(
    adapter_path="models/lora_adapters/ai_domain",
    test_dataset=dataset
)

print(f"Precisión: {evaluation['accuracy']}")
print(f"F1-score: {evaluation['f1_score']}")
```

## 📥 Descargar Dataset HEAD-QA (`download_headqa_dataset.py`)

### Funciones Principales

#### `download_headqa_method1()`
**Propósito**: Descargar dataset HEAD-QA usando método 1.

**Parámetros**:
- `output_path: str = "datasets/headqa"` - Ruta de salida
- `language: str = "es"` - Idioma

**Ejemplo de uso**:
```python
from modules.training.download_headqa_dataset import download_headqa_method1

# Descargar dataset HEAD-QA
result = download_headqa_method1(
    output_path="datasets/headqa_spanish",
    language="es"
)

print(f"Dataset descargado: {result['status']}")
print(f"Archivos descargados: {result['files_count']}")
print(f"Tamaño total: {result['total_size']} MB")
```

#### `download_headqa_method2()`
**Propósito**: Descargar dataset HEAD-QA usando método 2.

**Parámetros**:
- `output_path: str = "datasets/headqa"` - Ruta de salida
- `format: str = "json"` - Formato de salida

**Ejemplo de uso**:
```python
from modules.training.download_headqa_dataset import download_headqa_method2

# Descargar dataset HEAD-QA con formato JSON
result = download_headqa_method2(
    output_path="datasets/headqa_json",
    format="json"
)

print(f"Dataset descargado: {result['status']}")
print(f"Preguntas descargadas: {result['questions_count']}")
```

## 📥 Descargar Dataset de Entrenamiento (`download_training_dataset.py`)

### Funciones Principales

#### `download_training_dataset()`
**Propósito**: Descargar dataset de entrenamiento general.

**Parámetros**:
- `dataset_name: str` - Nombre del dataset
- `output_path: str` - Ruta de salida
- `split: str = "train"` - División del dataset

**Ejemplo de uso**:
```python
from modules.training.download_training_dataset import download_training_dataset

# Descargar dataset de entrenamiento
result = download_training_dataset(
    dataset_name="squad",
    output_path="datasets/squad",
    split="train"
)

print(f"Dataset descargado: {result['status']}")
print(f"Ejemplos descargados: {result['examples_count']}")
```

## 🔄 Expandir Dataset HEAD-QA (`expand_headqa_dataset.py`)

### Funciones Principales

#### `expand_headqa_dataset()`
**Propósito**: Expandir dataset HEAD-QA con datos adicionales.

**Parámetros**:
- `input_path: str` - Ruta del dataset original
- `output_path: str` - Ruta de salida expandida
- `expansion_factor: float = 2.0` - Factor de expansión

**Ejemplo de uso**:
```python
from modules.training.expand_headqa_dataset import expand_headqa_dataset

# Expandir dataset HEAD-QA
result = expand_headqa_dataset(
    input_path="datasets/headqa/original",
    output_path="datasets/headqa/expanded",
    expansion_factor=2.5
)

print(f"Dataset expandido: {result['status']}")
print(f"Preguntas originales: {result['original_count']}")
print(f"Preguntas expandidas: {result['expanded_count']}")
```

## 📁 Importar Datasets a Ramas (`import_datasets_to_branches.py`)

### Funciones Principales

#### `import_datasets_to_branches()`
**Propósito**: Importar datasets a las ramas del sistema.

**Parámetros**:
- `datasets_path: str` - Ruta de los datasets
- `branches_path: str` - Ruta de las ramas
- `mapping_config: Dict[str, str]` - Configuración de mapeo

**Ejemplo de uso**:
```python
from modules.training.import_datasets_to_branches import import_datasets_to_branches

# Configurar mapeo de datasets a ramas
mapping_config = {
    "artificial_intelligence": "ai_branch",
    "machine_learning": "ml_branch",
    "deep_learning": "dl_branch"
}

# Importar datasets a ramas
result = import_datasets_to_branches(
    datasets_path="datasets/",
    branches_path="branches/",
    mapping_config=mapping_config
)

print(f"Importación completada: {result['status']}")
print(f"Ramas actualizadas: {result['updated_branches']}")
```

## 🔄 Pipeline de Entrenamiento LLM (`llm_training_pipeline.py`)

### Clases Principales

#### `LLMTrainingPipeline`
**Propósito**: Pipeline completo de entrenamiento para modelos de lenguaje.

**Métodos principales**:
- `__init__(config_path: str = "config/training_config.json")` - Inicializar pipeline
- `prepare_data(data_path: str) -> Dataset` - Preparar datos
- `train_model(model_name: str, dataset: Dataset) -> Dict[str, Any]` - Entrenar modelo
- `evaluate_model(model_path: str, test_dataset: Dataset) -> Dict[str, float]` - Evaluar modelo
- `save_model(model, output_path: str)` - Guardar modelo
- `load_model(model_path: str)` - Cargar modelo

**Ejemplo de uso**:
```python
from modules.training.llm_training_pipeline import LLMTrainingPipeline

# Inicializar pipeline de entrenamiento
pipeline = LLMTrainingPipeline()

# Preparar datos
dataset = pipeline.prepare_data("data/training_data.json")
print(f"Dataset preparado: {len(dataset)} ejemplos")

# Entrenar modelo
training_result = pipeline.train_model("gpt2", dataset)
print(f"Entrenamiento completado: {training_result['status']}")
print(f"Pérdida final: {training_result['final_loss']}")

# Evaluar modelo
evaluation = pipeline.evaluate_model(
    model_path="models/trained_model",
    test_dataset=dataset
)

print(f"Precisión: {evaluation['accuracy']}")
print(f"Perplexidad: {evaluation['perplexity']}")

# Guardar modelo
pipeline.save_model(training_result['model'], "models/final_model")
```

## 🔄 Generador de Fine-tuning LoRA (`lora_finetuning_generator.py`)

### Clases Principales

#### `LoRAFineTuningGenerator`
**Propósito**: Generador de configuraciones de fine-tuning LoRA.

**Métodos principales**:
- `__init__()` - Inicializar generador
- `generate_lora_config(model_name: str, task_type: str) -> Dict[str, Any]` - Generar configuración LoRA
- `optimize_lora_parameters(dataset: Dataset) -> Dict[str, Any]` - Optimizar parámetros LoRA
- `create_training_script(config: Dict[str, Any], output_path: str)` - Crear script de entrenamiento

**Ejemplo de uso**:
```python
from modules.training.lora_finetuning_generator import LoRAFineTuningGenerator

# Inicializar generador LoRA
lora_generator = LoRAFineTuningGenerator()

# Generar configuración LoRA
config = lora_generator.generate_lora_config(
    model_name="gpt2",
    task_type="text_generation"
)

print(f"Configuración LoRA generada:")
print(f"  r: {config['r']}")
print(f"  alpha: {config['alpha']}")
print(f"  dropout: {config['dropout']}")

# Optimizar parámetros
optimized_params = lora_generator.optimize_lora_parameters(dataset)
print(f"Parámetros optimizados: {optimized_params}")

# Crear script de entrenamiento
lora_generator.create_training_script(
    config=config,
    output_path="scripts/train_lora.py"
)
```

## 🔄 Sincronización de Tokens de Entrenamiento (`training_token_sync.py`)

### Funciones Principales

#### `sync_training_tokens()`
**Propósito**: Sincronizar tokens de entrenamiento entre diferentes componentes.

**Parámetros**:
- `source_path: str` - Ruta de origen
- `target_path: str` - Ruta de destino
- `sync_type: str = "full"` - Tipo de sincronización

**Ejemplo de uso**:
```python
from modules.training.training_token_sync import sync_training_tokens

# Sincronizar tokens de entrenamiento
result = sync_training_tokens(
    source_path="tokens/source/",
    target_path="tokens/target/",
    sync_type="incremental"
)

print(f"Sincronización completada: {result['status']}")
print(f"Tokens sincronizados: {result['synced_tokens']}")
```

## 🔄 Flujo de Trabajo de Entrenamiento

### 1. Preparación de Datos
```python
from modules.training.download_training_dataset import download_training_dataset
from modules.training.expand_headqa_dataset import expand_headqa_dataset

# Descargar dataset base
download_training_dataset("squad", "datasets/squad")

# Expandir dataset HEAD-QA
expand_headqa_dataset(
    input_path="datasets/headqa/original",
    output_path="datasets/headqa/expanded",
    expansion_factor=2.0
)
```

### 2. Importación a Ramas
```python
from modules.training.import_datasets_to_branches import import_datasets_to_branches

# Configurar mapeo
mapping = {
    "artificial_intelligence": "ai_branch",
    "machine_learning": "ml_branch"
}

# Importar datasets
import_datasets_to_branches(
    datasets_path="datasets/",
    branches_path="branches/",
    mapping_config=mapping
)
```

### 3. Entrenamiento con LoRA
```python
from modules.training.automatic_lora_trainer import AutomaticLoRATrainer
from modules.training.lora_finetuning_generator import LoRAFineTuningGenerator

# Preparar entrenador LoRA
lora_trainer = AutomaticLoRATrainer()
lora_generator = LoRAFineTuningGenerator()

# Generar configuración
config = lora_generator.generate_lora_config("gpt2", "text_generation")

# Preparar dataset
dataset = lora_trainer.prepare_dataset("data/training_data.json")

# Entrenar adaptador
result = lora_trainer.train_lora_adapter(
    model_name="gpt2",
    dataset=dataset,
    output_path="models/lora_adapters"
)
```

### 4. Pipeline Completo
```python
from modules.training.llm_training_pipeline import LLMTrainingPipeline

# Configurar pipeline
pipeline = LLMTrainingPipeline()

# Preparar datos
dataset = pipeline.prepare_data("data/complete_dataset.json")

# Entrenar modelo
training_result = pipeline.train_model("gpt2", dataset)

# Evaluar modelo
evaluation = pipeline.evaluate_model(
    model_path="models/trained_model",
    test_dataset=dataset
)

# Guardar modelo final
pipeline.save_model(training_result['model'], "models/final_model")
```

### 5. Sistema de Entrenamiento Avanzado
```python
from modules.training.advanced_training_system import AdvancedTrainingSystem

# Configurar sistema avanzado
training_system = AdvancedTrainingSystem()

# Iniciar sesión de entrenamiento
session = training_system.start_exercise_session("usuario1", "exercise_001")

# Procesar respuestas
for question in session['questions']:
    result = training_system.submit_answer(
        session_id=session['session_id'],
        user_id="usuario1",
        question_id=question['id'],
        answer=question['user_answer']
    )
    print(f"Pregunta {question['id']}: {result['score']}")

# Obtener estadísticas finales
stats = training_system.get_training_statistics()
print(f"Puntuación final: {stats['final_score']}")
```

## 🚨 Manejo de Errores

### Errores Comunes en Entrenamiento

1. **Error de dataset**
   ```python
   # Error: DatasetNotFoundError
   # Solución: Verificar ruta y formato del dataset
   dataset = lora_trainer.prepare_dataset("data/training_data.json")
   ```

2. **Error de memoria**
   ```python
   # Error: OutOfMemoryError
   # Solución: Reducir batch size o usar gradient accumulation
   config = lora_generator.generate_lora_config("gpt2", "text_generation")
   config['batch_size'] = 4
   ```

3. **Error de convergencia**
   ```python
   # Error: ConvergenceError
   # Solución: Ajustar learning rate o usar early stopping
   training_result = lora_trainer.train_lora_adapter(
       model_name="gpt2",
       dataset=dataset,
       output_path="models/lora_adapters"
   )
   ```

## 📊 Métricas y Monitoreo

### Métricas de Entrenamiento

1. **Calidad de Datos**
   - Número de ejemplos
   - Distribución de clases
   - Calidad de anotaciones
   - Duplicados

2. **Rendimiento de Entrenamiento**
   - Pérdida de entrenamiento
   - Pérdida de validación
   - Precisión
   - F1-score

3. **Eficiencia**
   - Tiempo de entrenamiento
   - Uso de memoria
   - Uso de GPU
   - Throughput

### Ejemplo de Monitoreo

```python
# Monitoreo de entrenamiento
class TrainingMonitor:
    def __init__(self):
        self.metrics = {}
    
    def log_metric(self, name: str, value: float, step: int):
        if name not in self.metrics:
            self.metrics[name] = []
        self.metrics[name].append({'step': step, 'value': value})
    
    def get_training_summary(self):
        summary = {}
        for metric_name, values in self.metrics.items():
            if values:
                summary[metric_name] = {
                    'current': values[-1]['value'],
                    'best': min([v['value'] for v in values]),
                    'worst': max([v['value'] for v in values]),
                    'steps': len(values)
                }
        return summary

# Uso del monitor
monitor = TrainingMonitor()

# Durante el entrenamiento
for epoch in range(num_epochs):
    loss = train_epoch()
    monitor.log_metric('loss', loss, epoch)
    
    if epoch % 10 == 0:
        summary = monitor.get_training_summary()
        print(f"Época {epoch}: Pérdida = {summary['loss']['current']:.4f}")
```

## 🔧 Configuración Avanzada

### Configuración de Entrenamiento Personalizada
```python
# Configuración personalizada de LoRA
class CustomLoRATrainer(AutomaticLoRATrainer):
    def __init__(self):
        super().__init__()
        
        # Configuraciones adicionales
        self.custom_config = {
            'learning_rate': 1e-4,
            'weight_decay': 0.01,
            'warmup_steps': 100,
            'gradient_accumulation_steps': 4
        }
    
    def train_lora_adapter(self, model_name: str, dataset: Dataset, output_path: str):
        # Usar configuración personalizada
        config = self.custom_config.copy()
        config.update({
            'model_name': model_name,
            'dataset': dataset,
            'output_path': output_path
        })
        
        return self._train_with_config(config)
```

### Configuración de Pipeline Personalizada
```python
# Pipeline personalizado
class CustomTrainingPipeline(LLMTrainingPipeline):
    def __init__(self, config_path: str = "config/custom_training_config.json"):
        super().__init__(config_path)
        
        # Agregar componentes personalizados
        self.custom_preprocessor = CustomDataPreprocessor()
        self.custom_evaluator = CustomModelEvaluator()
    
    def prepare_data(self, data_path: str):
        # Usar preprocesador personalizado
        raw_data = super().prepare_data(data_path)
        return self.custom_preprocessor.process(raw_data)
    
    def evaluate_model(self, model_path: str, test_dataset: Dataset):
        # Usar evaluador personalizado
        basic_eval = super().evaluate_model(model_path, test_dataset)
        custom_eval = self.custom_evaluator.evaluate(model_path, test_dataset)
        
        return {**basic_eval, **custom_eval}
```

Esta documentación proporciona una visión completa de todos los módulos de entrenamiento, incluyendo sus clases, métodos, ejemplos de uso y mejores prácticas para el desarrollo de sistemas de entrenamiento de modelos de IA.
