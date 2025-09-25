# Documentación de Módulos de Memoria

## 💾 Módulo de Memoria (`memory/`)

### 📁 Estructura del Módulo
```
memory/
├── __init__.py
├── data_management.py                    # Gestión de datos
├── intelligent_fallback_system.py        # Sistema de fallback inteligente
├── rag.py                               # Sistema RAG
└── short_term.py                        # Memoria a corto plazo
```

## 🗄️ Gestión de Datos (`data_management.py`)

### Clases Principales

#### `DataManagementService`
**Propósito**: Servicio de gestión de datos con DuckDB.

**Métodos principales**:
- `__init__(db_path: str = 'data/user_data.duckdb', log_dir: str = 'logs/data_management')` - Inicializar
- `_init_database()` - Inicializar base de datos
- `store_user_data(user_id: str, data: Dict[str, Any], domain: str, data_type: str, is_pii: bool = False, retention_period: int = 90)` - Almacenar datos de usuario
- `delete_user_data(user_id: str, domain: Optional[str] = None, data_type: Optional[str] = None, reason: str = "Solicitud de usuario")` - Eliminar datos de usuario
- `export_user_data(user_id: str, export_format: str = 'jsonl') -> str` - Exportar datos de usuario
- `cleanup_expired_data()` - Limpiar datos expirados

**Ejemplo de uso**:
```python
from modules.memory.data_management import DataManagementService

# Inicializar servicio de gestión de datos
data_service = DataManagementService()

# Almacenar datos de usuario
user_data = {
    "preferences": {"language": "es", "theme": "dark"},
    "interactions": [{"query": "¿Qué es la IA?", "response": "La IA es..."}],
    "profile": {"age": 25, "interests": ["technology", "science"]}
}

data_service.store_user_data(
    user_id="usuario1",
    data=user_data,
    domain="general",
    data_type="user_profile",
    is_pii=False,
    retention_period=365
)

# Exportar datos de usuario
export_path = data_service.export_user_data("usuario1", "jsonl")
print(f"Datos exportados a: {export_path}")

# Eliminar datos específicos
data_service.delete_user_data(
    user_id="usuario1",
    domain="general",
    data_type="interactions",
    reason="Limpieza de datos"
)

# Limpiar datos expirados
data_service.cleanup_expired_data()
```

## 🔄 Sistema de Fallback Inteligente (`intelligent_fallback_system.py`)

### Clases Principales

#### `IntelligentBackupSystem`
**Propósito**: Sistema de respaldo inteligente con análisis de intención.

**Métodos principales**:
- `__init__()` - Inicializar
- `_initialize_backup_system()` - Inicializar sistema de respaldo
- `generate_backup_response(query: str, context: Optional[Dict[str, Any]] = None, error_type: str = "general") -> Dict[str, Any]` - Generar respuesta de backup
- `analyze_query_intent(query: str) -> Dict[str, Any]` - Analizar intención de consulta
- `get_system_status() -> Dict[str, Any]` - Obtener estado del sistema

**Ejemplo de uso**:
```python
from modules.memory.intelligent_fallback_system import IntelligentBackupSystem

# Inicializar sistema de fallback
fallback_system = IntelligentBackupSystem()

# Analizar intención de consulta
intent_analysis = fallback_system.analyze_query_intent("¿Cómo funciona la inteligencia artificial?")
print(f"Intención detectada: {intent_analysis['intent']}")
print(f"Confianza: {intent_analysis['confidence']}")

# Generar respuesta de backup
backup_response = fallback_system.generate_backup_response(
    query="¿Qué es machine learning?",
    context={"user_level": "beginner"},
    error_type="model_unavailable"
)

print(f"Respuesta de backup: {backup_response['response']}")
print(f"Tipo de respuesta: {backup_response['response_type']}")

# Obtener estado del sistema
status = fallback_system.get_system_status()
print(f"Sistema activo: {status['is_active']}")
print(f"Respuestas generadas: {status['total_responses_generated']}")
```

## 🔍 Sistema RAG (`rag.py`)

### Clases Principales

#### `RAGRetriever`
**Propósito**: Sistema RAG (Retrieval-Augmented Generation) para recuperación de información.

**Métodos principales**:
- `__init__(embed_model: str = "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2", db_path: str = "data/rag_memory.duckdb", index_path: str = "data/faiss_index.index")` - Inicializar
- `_init_database()` - Inicializar base de datos
- `_load_or_create_index() -> faiss.Index` - Cargar o crear índice
- `add_document(content: str, source: str, domain: str, metadata: Optional[Dict] = None)` - Agregar documento
- `retrieve_with_citation(query: str, k: int = 3, domain: Optional[str] = None) -> List[Dict[str, Any]]` - Recuperar con citaciones
- `generate_rag_response(query: str, model, tokenizer, domain: Optional[str] = None) -> Dict[str, Any]` - Generar respuesta RAG

**Ejemplo de uso**:
```python
from modules.memory.rag import RAGRetriever
from transformers import AutoModelForCausalLM, AutoTokenizer

# Inicializar sistema RAG
rag_system = RAGRetriever()

# Agregar documentos
documents = [
    {
        "content": "La inteligencia artificial es una rama de la informática que busca crear sistemas capaces de realizar tareas que normalmente requieren inteligencia humana.",
        "source": "AI_Handbook",
        "domain": "artificial_intelligence"
    },
    {
        "content": "Machine Learning es un subconjunto de la IA que permite a las computadoras aprender sin ser programadas explícitamente.",
        "source": "ML_Guide",
        "domain": "machine_learning"
    }
]

for doc in documents:
    rag_system.add_document(
        content=doc["content"],
        source=doc["source"],
        domain=doc["domain"],
        metadata={"author": "AI Expert", "date": "2024-01-01"}
    )

# Recuperar información con citaciones
results = rag_system.retrieve_with_citation(
    query="¿Qué es la inteligencia artificial?",
    k=3,
    domain="artificial_intelligence"
)

for result in results:
    print(f"Contenido: {result['content']}")
    print(f"Fuente: {result['source']}")
    print(f"Similitud: {result['similarity']}")
    print("---")

# Generar respuesta RAG
model = AutoModelForCausalLM.from_pretrained("gpt2")
tokenizer = AutoTokenizer.from_pretrained("gpt2")

rag_response = rag_system.generate_rag_response(
    query="Explica la diferencia entre IA y ML",
    model=model,
    tokenizer=tokenizer,
    domain="artificial_intelligence"
)

print(f"Respuesta RAG: {rag_response['response']}")
print(f"Fuentes utilizadas: {rag_response['sources']}")
```

## ⚡ Memoria a Corto Plazo (`short_term.py`)

### Clases Principales

#### `ShortTermMemory`
**Propósito**: Sistema de memoria a corto plazo para conversaciones.

**Métodos principales**:
- `__init__(max_messages: int = 10, max_tokens: int = 1024, summary_every: int = 8000)` - Inicializar
- `add_message(role: str, content: str, tokens: int = None, metadata: Dict = None)` - Agregar mensaje
- `_prune_messages(new_tokens: int)` - Podar mensajes
- `_summarize()` - Resumir conversación
- `get_context(max_tokens: int = None, include_system: bool = True) -> List[Dict]` - Obtener contexto
- `save(session_id: str = None)` - Guardar memoria
- `load(session_id: str = None)` - Cargar memoria
- `clear()` - Limpiar memoria

**Ejemplo de uso**:
```python
from modules.memory.short_term import ShortTermMemory

# Inicializar memoria a corto plazo
memory = ShortTermMemory(max_messages=20, max_tokens=2048)

# Agregar mensajes de conversación
memory.add_message("system", "Eres un asistente de IA útil y amigable.")
memory.add_message("user", "Hola, ¿cómo estás?")
memory.add_message("assistant", "¡Hola! Estoy muy bien, gracias por preguntar. ¿En qué puedo ayudarte hoy?")
memory.add_message("user", "¿Puedes explicarme qué es la inteligencia artificial?")
memory.add_message("assistant", "La inteligencia artificial es una rama de la informática que busca crear sistemas capaces de realizar tareas que normalmente requieren inteligencia humana.")

# Obtener contexto para el modelo
context = memory.get_context(max_tokens=1000, include_system=True)
print("Contexto actual:")
for msg in context:
    print(f"{msg['role']}: {msg['content']}")

# Guardar memoria de sesión
memory.save("session_123")

# Cargar memoria de sesión
new_memory = ShortTermMemory()
new_memory.load("session_123")

# Obtener contexto de la sesión cargada
loaded_context = new_memory.get_context()
print(f"Mensajes en memoria cargada: {len(loaded_context)}")

# Limpiar memoria
memory.clear()
```

## 🔄 Flujo de Trabajo de Memoria

### 1. Gestión de Datos de Usuario
```python
from modules.memory.data_management import DataManagementService

# Configurar gestión de datos
data_service = DataManagementService()

# Almacenar datos de usuario
user_data = {
    "conversation_history": [
        {"role": "user", "content": "¿Qué es la IA?"},
        {"role": "assistant", "content": "La IA es..."}
    ],
    "preferences": {"language": "es", "complexity": "intermediate"},
    "learning_progress": {"topics_covered": ["ai_basics", "ml_intro"]}
}

data_service.store_user_data(
    user_id="usuario1",
    data=user_data,
    domain="education",
    data_type="learning_session",
    retention_period=180
)
```

### 2. Sistema RAG para Recuperación
```python
from modules.memory.rag import RAGRetriever

# Configurar sistema RAG
rag_system = RAGRetriever()

# Agregar conocimiento base
knowledge_base = [
    {
        "content": "La inteligencia artificial (IA) es la simulación de procesos de inteligencia humana por parte de máquinas.",
        "source": "AI_Fundamentals",
        "domain": "artificial_intelligence"
    },
    {
        "content": "Machine Learning es una técnica de IA que permite a las computadoras aprender de los datos.",
        "source": "ML_Basics",
        "domain": "machine_learning"
    }
]

for knowledge in knowledge_base:
    rag_system.add_document(
        content=knowledge["content"],
        source=knowledge["source"],
        domain=knowledge["domain"]
    )

# Recuperar información relevante
query = "¿Cómo funciona el machine learning?"
results = rag_system.retrieve_with_citation(query, k=3)
```

### 3. Memoria a Corto Plazo para Conversaciones
```python
from modules.memory.short_term import ShortTermMemory

# Configurar memoria de conversación
conversation_memory = ShortTermMemory(max_messages=15)

# Simular conversación
conversation_memory.add_message("system", "Eres un tutor de IA experto.")
conversation_memory.add_message("user", "¿Puedes explicarme qué es deep learning?")
conversation_memory.add_message("assistant", "Deep Learning es una rama del machine learning que utiliza redes neuronales con múltiples capas.")

# Obtener contexto para continuar conversación
context = conversation_memory.get_context()
```

### 4. Sistema de Fallback Inteligente
```python
from modules.memory.intelligent_fallback_system import IntelligentBackupSystem

# Configurar sistema de fallback
fallback_system = IntelligentBackupSystem()

# Analizar consulta cuando el modelo principal falla
query = "¿Cuáles son las aplicaciones de la IA en medicina?"
intent = fallback_system.analyze_query_intent(query)

# Generar respuesta de backup
backup_response = fallback_system.generate_backup_response(
    query=query,
    context={"domain": "healthcare", "user_level": "intermediate"},
    error_type="model_unavailable"
)
```

### 5. Integración Completa
```python
# Sistema integrado de memoria
class IntegratedMemorySystem:
    def __init__(self):
        self.data_service = DataManagementService()
        self.rag_system = RAGRetriever()
        self.short_term = ShortTermMemory()
        self.fallback_system = IntelligentBackupSystem()
    
    def process_query(self, user_id: str, query: str):
        # 1. Agregar a memoria a corto plazo
        self.short_term.add_message("user", query)
        
        # 2. Recuperar información relevante
        rag_results = self.rag_system.retrieve_with_citation(query)
        
        # 3. Generar respuesta
        try:
            # Intentar con modelo principal
            response = self.generate_response(query, rag_results)
        except Exception as e:
            # Usar fallback si falla
            response = self.fallback_system.generate_backup_response(query)
        
        # 4. Agregar respuesta a memoria
        self.short_term.add_message("assistant", response["response"])
        
        # 5. Almacenar en memoria a largo plazo
        self.data_service.store_user_data(
            user_id=user_id,
            data={
                "query": query,
                "response": response["response"],
                "rag_sources": rag_results
            },
            domain="conversation",
            data_type="interaction"
        )
        
        return response

# Uso del sistema integrado
memory_system = IntegratedMemorySystem()
response = memory_system.process_query("usuario1", "¿Qué es la inteligencia artificial?")
```

## 🚨 Manejo de Errores

### Errores Comunes en Memoria

1. **Error de base de datos**
   ```python
   # Error: DatabaseConnectionError
   # Solución: Verificar conexión y permisos
   data_service = DataManagementService()
   ```

2. **Error de índice FAISS**
   ```python
   # Error: IndexCorruptionError
   # Solución: Recrear índice
   rag_system = RAGRetriever()
   rag_system._load_or_create_index()
   ```

3. **Error de memoria llena**
   ```python
   # Error: MemoryFullError
   # Solución: Limpiar memoria o aumentar límites
   memory.clear()
   memory = ShortTermMemory(max_messages=50)
   ```

## 📊 Métricas y Monitoreo

### Métricas de Memoria

1. **Gestión de Datos**
   - Número de usuarios activos
   - Tamaño de base de datos
   - Tasa de retención de datos
   - Tiempo de respuesta de consultas

2. **Sistema RAG**
   - Número de documentos indexados
   - Precisión de recuperación
   - Tiempo de búsqueda
   - Uso de memoria del índice

3. **Memoria a Corto Plazo**
   - Número de conversaciones activas
   - Tamaño promedio de contexto
   - Frecuencia de resúmenes
   - Tiempo de respuesta

### Ejemplo de Monitoreo

```python
# Monitoreo de sistema de memoria
class MemoryMonitor:
    def __init__(self):
        self.data_service = DataManagementService()
        self.rag_system = RAGRetriever()
        self.short_term = ShortTermMemory()
    
    def get_memory_metrics(self):
        return {
            "data_management": {
                "active_users": self.get_active_users_count(),
                "database_size": self.get_database_size(),
                "retention_rate": self.get_retention_rate()
            },
            "rag_system": {
                "indexed_documents": self.get_indexed_documents_count(),
                "search_accuracy": self.get_search_accuracy(),
                "index_memory_usage": self.get_index_memory_usage()
            },
            "short_term_memory": {
                "active_conversations": self.get_active_conversations_count(),
                "average_context_size": self.get_average_context_size(),
                "summary_frequency": self.get_summary_frequency()
            }
        }
    
    def get_active_users_count(self):
        # Implementar lógica para contar usuarios activos
        return 100
    
    def get_database_size(self):
        # Implementar lógica para obtener tamaño de BD
        return "1.2 GB"
    
    def get_retention_rate(self):
        # Implementar lógica para calcular tasa de retención
        return 0.85

# Uso del monitor
monitor = MemoryMonitor()
metrics = monitor.get_memory_metrics()
print("Métricas de memoria:")
for category, data in metrics.items():
    print(f"\n{category}:")
    for metric, value in data.items():
        print(f"  {metric}: {value}")
```

## 🔧 Configuración Avanzada

### Configuración de Base de Datos
```python
# Configuración personalizada de DuckDB
import duckdb

class CustomDataManagementService(DataManagementService):
    def __init__(self, db_path: str = 'data/custom_user_data.duckdb'):
        super().__init__(db_path)
        
        # Configuraciones adicionales
        self.connection.execute("PRAGMA journal_mode=WAL")
        self.connection.execute("PRAGMA synchronous=NORMAL")
        self.connection.execute("PRAGMA cache_size=10000")
        self.connection.execute("PRAGMA temp_store=MEMORY")
```

### Configuración de Índice FAISS
```python
# Configuración personalizada de FAISS
import faiss

class CustomRAGRetriever(RAGRetriever):
    def __init__(self, embed_model: str = "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2"):
        super().__init__(embed_model)
        
        # Configurar índice FAISS personalizado
        self.index = faiss.IndexFlatIP(768)  # Inner product para similitud coseno
        self.index = faiss.IndexIDMap(self.index)
```

### Configuración de Memoria a Corto Plazo
```python
# Configuración personalizada de memoria
class CustomShortTermMemory(ShortTermMemory):
    def __init__(self, max_messages: int = 20, max_tokens: int = 2048):
        super().__init__(max_messages, max_tokens)
        
        # Configuraciones adicionales
        self.summary_threshold = 0.8  # Umbral para resumir
        self.context_window = 10      # Ventana de contexto
        self.priority_messages = []    # Mensajes prioritarios
```

Esta documentación proporciona una visión completa de todos los módulos de memoria, incluyendo sus clases, métodos, ejemplos de uso y mejores prácticas para el desarrollo de sistemas de memoria inteligente.
