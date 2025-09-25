# Documentación de Módulos de IA

## 🤖 Módulo de IA (`ai/`)

### 📁 Estructura del Módulo
```
ai/
├── __init__.py
├── llm_models.py          # Modelos de lenguaje
├── ml_components.py       # Componentes de ML
├── response_generator.py  # Generador de respuestas
├── semantic_analyzer.py   # Analizador semántico
└── text_processor.py      # Procesador de texto
```

## 🔧 Modelos de Lenguaje (`llm_models.py`)

### Clases Principales

#### `ModelConfig`
**Propósito**: Configuración de modelo de lenguaje.

**Atributos**:
- `model_name: str` - Nombre del modelo
- `model_path: str` - Ruta del modelo
- `max_length: int = 512` - Longitud máxima
- `temperature: float = 0.7` - Temperatura de generación
- `top_p: float = 0.9` - Parámetro top-p
- `device: str = "auto"` - Dispositivo (auto, cpu, cuda)

#### `LocalLLMModel`
**Propósito**: Modelo de lenguaje local.

**Métodos principales**:
- `__init__(config: ModelConfig)` - Inicializar modelo
- `_get_device() -> str` - Obtener dispositivo automáticamente
- `_load_model()` - Cargar modelo
- `generate_text(prompt: str, max_length: int = None) -> str` - Generar texto

**Ejemplo de uso**:
```python
from modules.ai.llm_models import LocalLLMModel, ModelConfig

config = ModelConfig(
    model_name="gpt2",
    model_path="models/gpt2",
    temperature=0.8
)
model = LocalLLMModel(config)
response = model.generate_text("Hola, ¿cómo estás?")
```

#### `RemoteLLMClient`
**Propósito**: Cliente para modelos de lenguaje remotos.

**Métodos principales**:
- `__init__(api_key: str, model_name: str = "gpt-3.5-turbo")` - Inicializar cliente
- `_check_availability() -> bool` - Verificar disponibilidad
- `generate_text(prompt: str) -> str` - Generar texto

**Ejemplo de uso**:
```python
from modules.ai.llm_models import RemoteLLMClient

client = RemoteLLMClient("your-api-key", "gpt-4")
response = client.generate_text("Explica la inteligencia artificial")
```

#### `LLMModelManager`
**Propósito**: Gestor de modelos de lenguaje.

**Métodos principales**:
- `add_local_model(name: str, config: ModelConfig) -> bool` - Agregar modelo local
- `add_remote_client(name: str, api_key: str, model_name: str) -> bool` - Agregar cliente remoto
- `set_active_model(name: str) -> bool` - Establecer modelo activo
- `generate_text(prompt: str, model_name: str = None) -> str` - Generar texto
- `get_available_models() -> List[str]` - Obtener modelos disponibles

**Ejemplo de uso**:
```python
from modules.ai.llm_models import LLMModelManager, ModelConfig

manager = LLMModelManager()

# Agregar modelo local
config = ModelConfig(model_name="gpt2", model_path="models/gpt2")
manager.add_local_model("gpt2_local", config)

# Agregar modelo remoto
manager.add_remote_client("gpt4", "api-key", "gpt-4")

# Generar texto
response = manager.generate_text("Hola mundo", "gpt2_local")
```

## 🧠 Componentes de ML (`ml_components.py`)

### Clases Principales

#### `ModelPerformance`
**Propósito**: Métricas de rendimiento del modelo.

**Atributos**:
- `accuracy: float` - Precisión
- `precision: float` - Precisión
- `recall: float` - Recall
- `f1_score: float` - F1-score
- `mse: float` - Error cuadrático medio
- `r2_score: float` - R² score

#### `PredictionResult`
**Propósito**: Resultado de predicción.

**Atributos**:
- `prediction: Any` - Predicción
- `confidence: float` - Confianza
- `model_name: str` - Nombre del modelo
- `features_used: List[str]` - Características usadas

#### `MLModelManager`
**Propósito**: Gestor de modelos de ML.

**Métodos principales**:
- `train_classification_model(model_name: str, X: np.ndarray, y: np.ndarray, test_size: float = 0.2) -> ModelPerformance` - Entrenar modelo de clasificación
- `train_regression_model(model_name: str, X: np.ndarray, y: np.ndarray, test_size: float = 0.2) -> ModelPerformance` - Entrenar modelo de regresión
- `predict(model_name: str, X: np.ndarray) -> PredictionResult` - Realizar predicción
- `get_model_info(model_name: str) -> Dict[str, Any]` - Obtener información del modelo
- `list_models() -> List[str]` - Listar modelos
- `delete_model(model_name: str) -> bool` - Eliminar modelo

**Ejemplo de uso**:
```python
from modules.ai.ml_components import MLModelManager
import numpy as np

manager = MLModelManager()

# Datos de ejemplo
X = np.random.rand(100, 5)
y = np.random.randint(0, 2, 100)

# Entrenar modelo de clasificación
performance = manager.train_classification_model("random_forest", X, y)

# Realizar predicción
X_test = np.random.rand(10, 5)
result = manager.predict("random_forest", X_test)
print(f"Predicción: {result.prediction}, Confianza: {result.confidence}")
```

## 💬 Generador de Respuestas (`response_generator.py`)

### Clases Principales

#### `ResponseContext`
**Propósito**: Contexto para generación de respuestas.

**Atributos**:
- `user_query: str` - Consulta del usuario
- `conversation_history: List[Dict[str, str]]` - Historial de conversación
- `user_profile: Dict[str, Any]` - Perfil del usuario
- `system_context: Dict[str, Any]` - Contexto del sistema
- `response_type: str = "general"` - Tipo de respuesta

#### `GeneratedResponse`
**Propósito**: Respuesta generada.

**Atributos**:
- `text: str` - Texto de la respuesta
- `confidence: float` - Confianza
- `response_type: str` - Tipo de respuesta
- `metadata: Dict[str, Any]` - Metadatos

#### `ResponseGenerator`
**Propósito**: Generador de respuestas inteligentes.

**Métodos principales**:
- `_load_response_templates() -> Dict[str, List[str]]` - Cargar plantillas
- `generate_response(context: ResponseContext) -> GeneratedResponse` - Generar respuesta
- `_determine_response_type(context: ResponseContext) -> str` - Determinar tipo de respuesta
- `_generate_template_response(context: ResponseContext) -> str` - Generar respuesta con plantilla
- `_generate_intelligent_response(context: ResponseContext) -> str` - Generar respuesta inteligente
- `_continue_conversation(query: str, last_exchange: Dict[str, str]) -> str` - Continuar conversación
- `_personalized_response(query: str, user_profile: Dict[str, Any]) -> str` - Respuesta personalizada

**Ejemplo de uso**:
```python
from modules.ai.response_generator import ResponseGenerator, ResponseContext

generator = ResponseGenerator()

context = ResponseContext(
    user_query="¿Qué es la inteligencia artificial?",
    conversation_history=[],
    user_profile={"level": "beginner"},
    system_context={"domain": "education"}
)

response = generator.generate_response(context)
print(f"Respuesta: {response.text}")
print(f"Confianza: {response.confidence}")
```

## 🔍 Analizador Semántico (`semantic_analyzer.py`)

### Clases Principales

#### `SemanticSimilarity`
**Propósito**: Resultado de similitud semántica.

**Atributos**:
- `score: float` - Puntuación de similitud
- `confidence: float` - Confianza
- `explanation: str` - Explicación

#### `SemanticAnalysis`
**Propósito**: Resultado del análisis semántico.

**Atributos**:
- `main_topics: List[str]` - Temas principales
- `semantic_clusters: List[List[str]]` - Clusters semánticos
- `key_concepts: List[str]` - Conceptos clave
- `context_understanding: Dict[str, Any]` - Comprensión del contexto
- `semantic_similarity: Dict[str, float]` - Similitud semántica

#### `SemanticAnalyzer`
**Propósito**: Analizador semántico avanzado.

**Métodos principales**:
- `__init__(model_name: str = "paraphrase-multilingual-MiniLM-L12-v2")` - Inicializar
- `_load_model()` - Cargar modelo
- `get_embeddings(texts: List[str]) -> np.ndarray` - Obtener embeddings
- `calculate_similarity(text1: str, text2: str) -> float` - Calcular similitud
- `find_similar_texts(query: str, texts: List[str], threshold: float = 0.5) -> List[Tuple[int, float]]` - Encontrar textos similares
- `cluster_texts(texts: List[str], n_clusters: int = 3) -> List[List[int]]` - Clustering de textos
- `extract_key_concepts(text: str, max_concepts: int = 10) -> List[str]` - Extraer conceptos clave
- `understand_context(text: str, context_texts: List[str] = None) -> Dict[str, Any]` - Comprender contexto
- `analyze_semantics(text: str, context_texts: List[str] = None) -> SemanticAnalysis` - Analizar semántica
- `semantic_search(query: str, documents: List[str], top_k: int = 5) -> List[Tuple[int, float]]` - Búsqueda semántica

**Ejemplo de uso**:
```python
from modules.ai.semantic_analyzer import SemanticAnalyzer

analyzer = SemanticAnalyzer()

# Calcular similitud
similarity = analyzer.calculate_similarity("Hola mundo", "Hello world")
print(f"Similitud: {similarity}")

# Análisis semántico completo
analysis = analyzer.analyze_semantics("La inteligencia artificial está transformando el mundo")
print(f"Temas principales: {analysis.main_topics}")
print(f"Conceptos clave: {analysis.key_concepts}")

# Búsqueda semántica
documents = [
    "La IA está revolucionando la medicina",
    "Los coches autónomos usan IA",
    "La IA en la educación"
]
results = analyzer.semantic_search("inteligencia artificial", documents)
for doc_idx, score in results:
    print(f"Documento {doc_idx}: {score}")
```

## 📝 Procesador de Texto (`text_processor.py`)

### Clases Principales

#### `TextAnalysis`
**Propósito**: Resultado del análisis de texto.

**Atributos**:
- `word_count: int` - Número de palabras
- `sentence_count: int` - Número de oraciones
- `avg_sentence_length: float` - Longitud promedio de oraciones
- `unique_words: int` - Palabras únicas
- `vocabulary_diversity: float` - Diversidad de vocabulario
- `sentiment_score: float` - Puntuación de sentimiento
- `key_phrases: List[str]` - Frases clave
- `entities: List[Dict[str, Any]]` - Entidades

#### `TextProcessor`
**Propósito**: Procesador de texto avanzado.

**Métodos principales**:
- `__init__(language: str = "spanish")` - Inicializar
- `_initialize_nlp()` - Inicializar NLP
- `_load_stop_words()` - Cargar palabras de parada
- `clean_text(text: str) -> str` - Limpiar texto
- `tokenize_text(text: str) -> List[str]` - Tokenizar texto
- `remove_stop_words(tokens: List[str]) -> List[str]` - Remover palabras de parada
- `lemmatize_tokens(tokens: List[str]) -> List[str]` - Lematizar tokens
- `extract_key_phrases(text: str, max_phrases: int = 5) -> List[str]` - Extraer frases clave
- `extract_entities(text: str) -> List[Dict[str, Any]]` - Extraer entidades
- `analyze_sentiment(text: str) -> float` - Analizar sentimiento
- `analyze_text(text: str) -> TextAnalysis` - Análisis completo de texto
- `preprocess_for_llm(text: str) -> str` - Preprocesar para LLM

**Ejemplo de uso**:
```python
from modules.ai.text_processor import TextProcessor

processor = TextProcessor()

# Limpiar texto
clean_text = processor.clean_text("  Hola   mundo!  ")
print(f"Texto limpio: '{clean_text}'")

# Análisis completo
analysis = processor.analyze_text("La inteligencia artificial está transformando el mundo de la tecnología.")
print(f"Palabras: {analysis.word_count}")
print(f"Oraciones: {analysis.sentence_count}")
print(f"Sentimiento: {analysis.sentiment_score}")
print(f"Frases clave: {analysis.key_phrases}")
print(f"Entidades: {analysis.entities}")

# Preprocesar para LLM
preprocessed = processor.preprocess_for_llm("Texto con   espacios   extra y puntuación!!!")
print(f"Preprocesado: '{preprocessed}'")
```

## 🔧 Componentes Avanzados de IA (`ai_components/`)

### 📁 Estructura del Módulo
```
ai_components/
├── __init__.py
├── advanced_ai_system.py              # Sistema de IA avanzado
├── advanced_algorithm_refinement.py   # Refinamiento de algoritmos
├── advanced_contextual_reasoning.py   # Razonamiento contextual
├── advanced_module_enhancer.py        # Mejorador de módulos
├── module_enhancer.py                 # Mejorador de módulos
└── neurofusion_component_adapters.py  # Adaptadores de componentes
```

## 🚀 Sistema de IA Avanzado (`advanced_ai_system.py`)

### Clases Principales

#### `QualityEvaluationConfig`
**Propósito**: Configuración para evaluación de calidad de respuestas.

**Atributos**:
- `min_length: int = 50` - Longitud mínima
- `max_length: int = 500` - Longitud máxima
- `coherence_threshold: float = 0.7` - Umbral de coherencia
- `diversity_threshold: float = 0.6` - Umbral de diversidad
- `factuality_threshold: float = 0.8` - Umbral de factualidad
- `metrics: Dict[str, float]` - Métricas adicionales

#### `NeuroFusionDataset`
**Propósito**: Dataset personalizado para entrenamiento.

**Métodos principales**:
- `__init__(data: List[Dict[str, str]], tokenizer)` - Inicializar dataset
- `__len__()` - Obtener longitud
- `__getitem__(idx)` - Obtener elemento

#### `AdvancedAISystem`
**Propósito**: Sistema de IA avanzado con fine-tuning y evaluación de calidad.

**Métodos principales**:
- `__init__(model_name: str = "neurofusion/base-model")` - Inicializar
- `prepare_dataset(training_data: List[Dict[str, str]]) -> NeuroFusionDataset` - Preparar dataset
- `fine_tune(dataset: NeuroFusionDataset, epochs: int = 3)` - Fine-tuning
- `evaluate_response_quality(response: str) -> Dict[str, float]` - Evaluar calidad
- `generate_response(prompt: str, max_length: int = 200) -> str` - Generar respuesta

**Ejemplo de uso**:
```python
from modules.ai_components.advanced_ai_system import AdvancedAISystem

system = AdvancedAISystem()

# Preparar datos de entrenamiento
training_data = [
    {"input": "¿Qué es la IA?", "output": "La IA es..."},
    {"input": "¿Cómo funciona ML?", "output": "ML funciona..."}
]

# Fine-tuning
dataset = system.prepare_dataset(training_data)
system.fine_tune(dataset, epochs=3)

# Generar respuesta
response = system.generate_response("Explica la inteligencia artificial")
print(response)

# Evaluar calidad
quality = system.evaluate_response_quality(response)
print(f"Calidad: {quality}")
```

## 🔄 Refinamiento de Algoritmos (`advanced_algorithm_refinement.py`)

### Clases Principales

#### `AlgorithmRefinementEngine`
**Propósito**: Motor de refinamiento de algoritmos.

**Métodos principales**:
- `__init__(complexity_threshold: float = 0.7)` - Inicializar
- `analyze_algorithm_complexity(algorithm_name: str) -> float` - Analizar complejidad
- `refine_algorithm(algorithm_name: str) -> Dict[str, Any]` - Refinar algoritmo

**Ejemplo de uso**:
```python
from modules.ai_components.advanced_algorithm_refinement import AlgorithmRefinementEngine

engine = AlgorithmRefinementEngine()

# Analizar complejidad
complexity = engine.analyze_algorithm_complexity("text_processor")
print(f"Complejidad: {complexity}")

# Refinar algoritmo
refinement = engine.refine_algorithm("text_processor")
print(f"Refinamiento: {refinement}")
```

## 🧠 Razonamiento Contextual (`advanced_contextual_reasoning.py`)

### Clases Principales

#### `ContextualReasoningEngine`
**Propósito**: Motor de razonamiento contextual.

**Métodos principales**:
- `__init__(embedding_dim: int = 768)` - Inicializar
- `initialize()` - Inicializar motor
- `add_context(context_id: str, context_data: Dict[str, Any], embedding: Optional[np.ndarray] = None, domain: Optional[str] = None)` - Agregar contexto
- `find_similar_contexts(query_context: Dict[str, Any], top_k: int = 5, similarity_threshold: Optional[float] = None, domain: Optional[str] = None) -> List[Dict[str, Any]]` - Encontrar contextos similares
- `infer_context(base_context: Dict[str, Any], query: str, domain: Optional[str] = None) -> Dict[str, Any]` - Inferir contexto

**Ejemplo de uso**:
```python
from modules.ai_components.advanced_contextual_reasoning import ContextualReasoningEngine

engine = ContextualReasoningEngine()

# Agregar contexto
context_data = {
    "topic": "inteligencia artificial",
    "level": "beginner",
    "language": "spanish"
}
engine.add_context("ai_context", context_data, domain="education")

# Encontrar contextos similares
query_context = {"topic": "machine learning", "level": "beginner"}
similar_contexts = engine.find_similar_contexts(query_context, top_k=3)
print(f"Contextos similares: {similar_contexts}")

# Inferir contexto
inferred = engine.infer_context(context_data, "¿Qué es deep learning?")
print(f"Contexto inferido: {inferred}")
```

## 🔧 Mejorador de Módulos (`advanced_module_enhancer.py`)

### Clases Principales

#### `AdvancedSemanticAnalyzer`
**Propósito**: Analizador semántico avanzado para código.

**Métodos principales**:
- `extract_semantic_features(source_code: str) -> Dict[str, Any]` - Extraer características semánticas
- `_build_dependency_graph(module: ast.Module) -> nx.DiGraph` - Construir grafo de dependencias
- `_calculate_docstring_coverage(module: ast.Module) -> Dict[str, float]` - Calcular cobertura de docstrings

#### `AdvancedCodeTransformer`
**Propósito**: Transformador de código avanzado.

**Métodos principales**:
- `transform_module(source_code: str, semantic_features: Dict[str, Any]) -> str` - Transformar módulo
- `_add_performance_decorators(source_code: str, semantic_features: Dict[str, Any]) -> str` - Agregar decoradores de rendimiento

#### `AdvancedExperimentalValidator`
**Propósito**: Validador experimental avanzado.

**Métodos principales**:
- `validate_module(module_path: str) -> Dict[str, Any]` - Validar módulo
- `_run_pylint(module_path: str) -> Dict[str, Any]` - Ejecutar pylint
- `_analyze_function_performance(module_path: str) -> Dict[str, Any]` - Analizar rendimiento de funciones
- `_calculate_code_quality(module_path: str) -> Dict[str, Any]` - Calcular calidad de código

#### `AdvancedModuleEnhancer`
**Propósito**: Mejorador avanzado de módulos.

**Métodos principales**:
- `enhance_module(module_path: str, output_path: Optional[str] = None) -> Dict[str, Any]` - Mejorar módulo

**Ejemplo de uso**:
```python
from modules.ai_components.advanced_module_enhancer import AdvancedModuleEnhancer

enhancer = AdvancedModuleEnhancer()

# Mejorar módulo
result = enhancer.enhance_module("modules/ai/text_processor.py")
print(f"Resultado de mejora: {result}")
```

## 🔧 Mejorador de Módulos Básico (`module_enhancer.py`)

### Clases Principales

#### `ModuleEnhancer`
**Propósito**: Mejorador de módulos básico.

**Métodos principales**:
- `load_module(module_path: str)` - Cargar módulo
- `analyze_module_structure(module)` - Analizar estructura del módulo
- `transform_module(module_path: str) -> str` - Transformar módulo
- `_add_logging(source_code: str) -> str` - Agregar logging
- `_add_type_hints(source_code: str) -> str` - Agregar type hints
- `_improve_error_handling(source_code: str) -> str` - Mejorar manejo de errores
- `_add_experimental_validation(source_code: str) -> str` - Agregar validación experimental
- `enhance_module(module_path: str, output_path: str = None)` - Mejorar módulo

**Ejemplo de uso**:
```python
from modules.ai_components.module_enhancer import ModuleEnhancer

enhancer = ModuleEnhancer()

# Mejorar módulo
enhancer.enhance_module("modules/ai/text_processor.py", "enhanced_text_processor.py")
```

## 🔄 Adaptadores de Componentes (`neurofusion_component_adapters.py`)

### Clases Principales

#### `ComponentAdapter`
**Propósito**: Clase base para adaptadores de componentes.

**Métodos abstractos**:
- `adapt(component: Any) -> Any` - Adaptar componente
- `check_compatibility(component: Any) -> CompatibilityReport` - Verificar compatibilidad

#### `MLModelAdapter`
**Propósito**: Adaptador para modelos de ML.

**Métodos principales**:
- `adapt(component: Any) -> Any` - Adaptar modelo ML
- `check_compatibility(component: Any) -> CompatibilityReport` - Verificar compatibilidad

#### `NLPComponentAdapter`
**Propósito**: Adaptador para componentes NLP.

**Métodos principales**:
- `adapt(component: Any) -> Any` - Adaptar componente NLP
- `check_compatibility(component: Any) -> CompatibilityReport` - Verificar compatibilidad

#### `EmbeddingAdapter`
**Propósito**: Adaptador para sistemas de embeddings.

**Métodos principales**:
- `adapt(component: Any) -> Any` - Adaptar sistema de embeddings
- `check_compatibility(component: Any) -> CompatibilityReport` - Verificar compatibilidad

#### `ComponentMigrationStrategy`
**Propósito**: Estrategia de migración de componentes.

**Métodos principales**:
- `identify_migration_candidates(modules_path: str) -> List[Dict[str, Any]]` - Identificar candidatos de migración

**Ejemplo de uso**:
```python
from modules.ai_components.neurofusion_component_adapters import (
    MLModelAdapter, NLPComponentAdapter, ComponentMigrationStrategy
)

# Adaptar modelo ML
ml_adapter = MLModelAdapter()
adapted_model = ml_adapter.adapt(some_ml_model)

# Verificar compatibilidad
compatibility = ml_adapter.check_compatibility(some_ml_model)
print(f"Compatibilidad: {compatibility}")

# Identificar candidatos de migración
strategy = ComponentMigrationStrategy()
candidates = strategy.identify_migration_candidates("modules/")
print(f"Candidatos: {candidates}")
```

## 🔄 Flujo de Trabajo de IA

### 1. Procesamiento de Texto
```python
from modules.ai.text_processor import TextProcessor
from modules.ai.semantic_analyzer import SemanticAnalyzer

# Procesar texto
processor = TextProcessor()
analysis = processor.analyze_text("La IA está transformando el mundo")

# Análisis semántico
analyzer = SemanticAnalyzer()
semantic_analysis = analyzer.analyze_semantics(analysis.text)
```

### 2. Generación de Respuestas
```python
from modules.ai.response_generator import ResponseGenerator, ResponseContext

generator = ResponseGenerator()
context = ResponseContext(
    user_query="¿Qué es la IA?",
    user_profile={"level": "beginner"}
)
response = generator.generate_response(context)
```

### 3. Entrenamiento de Modelos
```python
from modules.ai.ml_components import MLModelManager
from modules.ai_components.advanced_ai_system import AdvancedAISystem

# Entrenar modelo ML
ml_manager = MLModelManager()
performance = ml_manager.train_classification_model("my_model", X, y)

# Fine-tuning de modelo de IA
ai_system = AdvancedAISystem()
ai_system.fine_tune(training_dataset)
```

### 4. Análisis y Mejora
```python
from modules.ai_components.advanced_module_enhancer import AdvancedModuleEnhancer
from modules.ai_components.advanced_contextual_reasoning import ContextualReasoningEngine

# Mejorar módulos
enhancer = AdvancedModuleEnhancer()
enhancer.enhance_module("my_module.py")

# Razonamiento contextual
reasoning_engine = ContextualReasoningEngine()
context = reasoning_engine.infer_context(base_context, query)
```

## 🚨 Manejo de Errores

### Errores Comunes en IA

1. **Modelo no encontrado**
   ```python
   # Error: ModelNotFoundError
   # Solución: Verificar ruta del modelo
   model = LocalLLMModel(config)
   ```

2. **Error de memoria**
   ```python
   # Error: CUDA out of memory
   # Solución: Reducir batch size o usar CPU
   config = ModelConfig(device="cpu")
   ```

3. **Error de tokenización**
   ```python
   # Error: TokenizationError
   # Solución: Verificar encoding del texto
   text = text.encode('utf-8').decode('utf-8')
   ```

## 📊 Métricas y Evaluación

### Métricas de Calidad

1. **Calidad de Respuestas**
   - Coherencia
   - Diversidad
   - Factualidad
   - Relevancia

2. **Rendimiento de Modelos**
   - Precisión
   - Recall
   - F1-score
   - Tiempo de inferencia

3. **Análisis Semántico**
   - Similitud semántica
   - Extracción de conceptos
   - Clustering de textos

### Ejemplo de Evaluación

```python
from modules.ai.ml_components import MLModelManager
from modules.ai_components.advanced_ai_system import AdvancedAISystem

# Evaluar modelo ML
ml_manager = MLModelManager()
performance = ml_manager.train_classification_model("model", X, y)
print(f"Precisión: {performance.accuracy}")

# Evaluar calidad de respuesta
ai_system = AdvancedAISystem()
response = ai_system.generate_response("¿Qué es la IA?")
quality = ai_system.evaluate_response_quality(response.text)
print(f"Calidad: {quality}")
```

Esta documentación proporciona una visión completa de todos los módulos de IA, incluyendo sus clases, métodos, ejemplos de uso y mejores prácticas para el desarrollo de sistemas de inteligencia artificial.
