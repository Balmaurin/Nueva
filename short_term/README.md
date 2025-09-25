# Shaili AI - Memoria a Corto Plazo

Sistema avanzado de memoria a corto plazo para Shaili AI, diseñado para manejar contexto conversacional, análisis semántico y gestión inteligente de sesiones de memoria temporal.

## 🧠 Características Principales

- **Gestión de Sesiones**: Creación y manejo de sesiones de conversación por usuario
- **Análisis Semántico**: Embeddings y búsqueda por similitud usando TF-IDF
- **Gestión de Contexto**: Recuperación inteligente de contexto conversacional
- **Generación de Resúmenes**: Resúmenes automáticos de conversaciones
- **Base de Datos SQLite**: Persistencia robusta de datos
- **Limpieza Automática**: Gestión automática de sesiones antiguas
- **Sistema de Respaldo**: Respaldo y exportación de datos
- **Threading Seguro**: Operaciones thread-safe para entornos concurrentes
- **Cálculo de Importancia**: Evaluación automática de importancia de mensajes

## 📁 Estructura del Proyecto

```
short_term/
├── __init__.py                 # Paquete principal
├── short_term_manager.py       # Gestor principal de memoria
├── test_short_term_system.py   # Sistema de pruebas completo
├── README.md                   # Documentación
├── memory/                     # Almacenamiento de memoria
│   ├── memory.db              # Base de datos SQLite
│   └── sessions/              # Datos de sesiones
├── cache/                      # Caché de embeddings
│   └── embeddings_cache.pkl   # Caché de embeddings
├── backup/                     # Respaldos automáticos
│   └── memory_backup_*.json   # Archivos de respaldo
└── exports/                    # Exportaciones de sesiones
    └── session_*.json         # Datos exportados
```

## 🚀 Instalación y Configuración

### Requisitos Previos

```bash
pip install numpy scikit-learn sqlite3
```

### Instalación Rápida

```python
from short_term import setup_memory_system, create_memory_manager

# Configurar sistema
setup_memory_system()

# Crear gestor
manager = create_memory_manager()
```

### Configuración Avanzada

```python
from short_term import MemoryConfig, ShortTermMemoryManager

# Configuración personalizada
config = MemoryConfig(
    max_messages=100,
    max_tokens=8192,
    summary_threshold=6000,
    similarity_threshold=0.8,
    cleanup_interval=1800,  # 30 minutos
    compression_enabled=True,
    backup_enabled=True
)

# Crear gestor con configuración personalizada
manager = ShortTermMemoryManager(config)
```

## 📖 Uso Básico

### Crear Sesión y Añadir Mensajes

```python
from short_term import create_session, add_message_to_session, get_memory_context

# Crear sesión para un usuario
session_id = create_session("usuario_123")

# Añadir mensajes a la conversación
add_message_to_session(session_id, "user", "Hola, ¿qué es la inteligencia artificial?")
add_message_to_session(session_id, "assistant", "La inteligencia artificial es un campo de la informática que busca crear sistemas capaces de realizar tareas que normalmente requieren inteligencia humana.")

# Obtener contexto de la conversación
context = get_memory_context(session_id)
for message in context:
    print(f"{message['role']}: {message['content']}")
```

### Búsqueda Semántica

```python
from short_term import search_messages, calculate_similarity

# Buscar mensajes similares
similar_messages = search_messages(session_id, "machine learning", limit=5)
for message, similarity in similar_messages:
    print(f"Similitud: {similarity:.3f} - {message.content}")

# Calcular similitud entre dos textos
similarity = calculate_similarity("Hola, ¿cómo estás?", "Hola, ¿qué tal?")
print(f"Similitud: {similarity:.3f}")
```

### Gestión de Sesiones

```python
from short_term import get_session_info, list_sessions, clear_session

# Obtener información de una sesión
info = get_session_info(session_id)
print(f"Sesión: {info['session_id']}")
print(f"Mensajes: {info['message_count']}")
print(f"Tokens: {info['total_tokens']}")

# Listar todas las sesiones de un usuario
sessions = list_sessions("usuario_123")
for session in sessions:
    print(f"Sesión: {session['session_id']} - Último acceso: {session['last_accessed']}")

# Limpiar mensajes de una sesión
clear_session(session_id)
```

## 🔧 API Completa

### Clases Principales

#### `ShortTermMemoryManager`

Gestor principal de memoria a corto plazo.

```python
class ShortTermMemoryManager:
    def __init__(self, config: Optional[MemoryConfig] = None)
    
    # Gestión de sesiones
    def create_session(self, user_id: str, session_id: str = None) -> str
    def get_session_info(self, session_id: str) -> Optional[Dict]
    def list_sessions(self, user_id: str = None) -> List[Dict]
    def delete_session(self, session_id: str)
    def clear_session(self, session_id: str)
    
    # Gestión de mensajes
    def add_message(self, session_id: str, role: str, content: str, 
                   tokens: int = None, metadata: Dict = None) -> str
    def get_context(self, session_id: str, max_tokens: int = None, 
                   include_system: bool = True, semantic_search: str = None) -> List[Dict]
    def search_messages(self, session_id: str, query: str, 
                       limit: int = 10) -> List[Tuple[MemoryMessage, float]]
    
    # Utilidades
    def backup_memory(self, backup_path: str = None)
```

#### `MemoryConfig`

Configuración del sistema de memoria.

```python
@dataclass
class MemoryConfig:
    max_messages: int = 50
    max_tokens: int = 4096
    max_sessions: int = 100
    summary_threshold: int = 8000
    similarity_threshold: float = 0.7
    cleanup_interval: int = 3600
    compression_enabled: bool = True
    backup_enabled: bool = True
    auto_summarize: bool = True
    semantic_clustering: bool = True
    memory_dir: str = "short_term/memory"
    database_path: str = "short_term/memory.db"
    cache_dir: str = "short_term/cache"
```

#### `SemanticAnalyzer`

Analizador semántico para embeddings y similitud.

```python
class SemanticAnalyzer:
    def get_embedding(self, text: str) -> List[float]
    def calculate_similarity(self, text1: str, text2: str) -> float
    def find_similar_messages(self, query: str, messages: List[MemoryMessage], 
                            threshold: float = None) -> List[Tuple[MemoryMessage, float]]
```

#### `MemorySummarizer`

Generador de resúmenes de conversaciones.

```python
class MemorySummarizer:
    def generate_summary(self, messages: List[MemoryMessage]) -> str
    def _summarize_by_role(self, messages: List[MemoryMessage], role: str) -> str
    def _extract_topics(self, texts: List[str]) -> List[str]
```

### Funciones de Conveniencia

```python
# Gestión básica
create_memory_manager(config=None) -> ShortTermMemoryManager
setup_memory_system(config=None) -> bool
get_memory_context(session_id, manager=None, max_tokens=None) -> list
add_message_to_session(session_id, role, content, manager=None, tokens=None, metadata=None) -> str

# Gestión de sesiones
create_session(user_id, session_id=None, manager=None) -> str
get_session_info(session_id, manager=None) -> dict
list_sessions(user_id=None, manager=None) -> list
delete_session(session_id, manager=None) -> bool
clear_session(session_id, manager=None) -> bool

# Análisis semántico
calculate_similarity(text1, text2, manager=None) -> float
get_text_embedding(text, manager=None) -> list
search_messages(session_id, query, manager=None, limit=10) -> list

# Resúmenes
generate_summary(session_id, manager=None) -> str

# Utilidades
get_memory_stats(manager=None) -> dict
cleanup_old_sessions(manager=None) -> int
backup_memory_data(manager=None, backup_path=None) -> bool
export_session_data(session_id, export_path=None, manager=None) -> bool
```

## 🗄️ Base de Datos

### Esquema de Tablas

```sql
-- Tabla de sesiones
CREATE TABLE sessions (
    session_id TEXT PRIMARY KEY,
    user_id TEXT NOT NULL,
    created_at REAL NOT NULL,
    last_accessed REAL NOT NULL,
    message_count INTEGER DEFAULT 0,
    total_tokens INTEGER DEFAULT 0,
    summary TEXT,
    metadata TEXT
);

-- Tabla de mensajes
CREATE TABLE messages (
    id TEXT PRIMARY KEY,
    session_id TEXT NOT NULL,
    role TEXT NOT NULL,
    content TEXT NOT NULL,
    tokens INTEGER NOT NULL,
    timestamp REAL NOT NULL,
    embedding TEXT,
    metadata TEXT,
    importance_score REAL DEFAULT 1.0,
    access_count INTEGER DEFAULT 0,
    last_accessed REAL,
    FOREIGN KEY (session_id) REFERENCES sessions (session_id)
);

-- Índices
CREATE INDEX idx_messages_session ON messages (session_id);
CREATE INDEX idx_messages_timestamp ON messages (timestamp);
```

### Operaciones de Base de Datos

```python
# Inicializar base de datos
manager._init_database()

# Guardar sesión
manager._save_session_to_db(session)

# Guardar mensaje
manager._save_message_to_db(message)

# Cargar sesiones existentes
manager._load_sessions()
```

## 🔍 Análisis Semántico

### Embeddings con TF-IDF

El sistema utiliza TF-IDF (Term Frequency-Inverse Document Frequency) para generar embeddings semánticos:

```python
# Obtener embedding de un texto
embedding = manager.semantic_analyzer.get_embedding("Texto de ejemplo")

# Calcular similitud coseno
similarity = manager.semantic_analyzer.calculate_similarity(
    "Hola, ¿cómo estás?", 
    "Hola, ¿qué tal?"
)
```

### Búsqueda por Similitud

```python
# Buscar mensajes similares a una consulta
similar_messages = manager.search_messages(
    session_id, 
    "machine learning", 
    limit=5
)

# Filtrar por umbral de similitud
similar_messages = manager.semantic_analyzer.find_similar_messages(
    query="inteligencia artificial",
    messages=messages,
    threshold=0.7
)
```

## 📝 Generación de Resúmenes

### Resúmenes Automáticos

```python
# Generar resumen de una sesión
summary = manager.summarizer.generate_summary(messages)

# Resumen por rol
user_summary = manager.summarizer._summarize_by_role(user_messages, "Usuario")
assistant_summary = manager.summarizer._summarize_by_role(assistant_messages, "Asistente")
```

### Extracción de Temas

```python
# Extraer temas principales de una conversación
topics = manager.summarizer._extract_topics([
    "¿Qué es la inteligencia artificial?",
    "La IA es un campo de la informática...",
    "¿Cuáles son los tipos principales?"
])
```

## ⚙️ Gestión de Límites

### Límites de Mensajes y Tokens

```python
# Configurar límites
config = MemoryConfig(
    max_messages=50,    # Máximo 50 mensajes por sesión
    max_tokens=4096,    # Máximo 4096 tokens por sesión
    summary_threshold=8000  # Generar resumen cada 8000 tokens
)

# El sistema automáticamente:
# 1. Elimina mensajes menos importantes cuando se excede el límite
# 2. Genera resúmenes cuando se alcanza el umbral
# 3. Mantiene la coherencia del contexto
```

### Cálculo de Importancia

```python
def _calculate_importance(self, content: str, role: str) -> float:
    importance = 1.0
    
    # Ajustar por rol
    if role == "system":
        importance *= 1.5
    elif role == "user":
        importance *= 1.2
    
    # Ajustar por longitud
    if len(content) > 100:
        importance *= 1.1
    
    # Ajustar por palabras clave
    keywords = ["importante", "crítico", "urgente", "error", "problema"]
    if any(keyword in content.lower() for keyword in keywords):
        importance *= 1.3
    
    return min(importance, 2.0)
```

## 🔄 Limpieza Automática

### Limpieza de Sesiones Antiguas

```python
# El sistema ejecuta limpieza automática cada hora por defecto
def _cleanup_old_sessions(self):
    current_time = time.time()
    sessions_to_delete = []
    
    for session_id, session in self.sessions.items():
        # Eliminar sesiones con más de 24 horas sin acceso
        if current_time - session.last_accessed > 86400:
            sessions_to_delete.append(session_id)
    
    for session_id in sessions_to_delete:
        self.delete_session(session_id)
```

### Configuración de Limpieza

```python
config = MemoryConfig(
    cleanup_interval=3600,  # Limpieza cada hora
    max_sessions=100        # Máximo 100 sesiones por usuario
)
```

## 💾 Respaldo y Exportación

### Respaldo Automático

```python
# Crear respaldo completo
manager.backup_memory("backup/memory_backup_20241201.json")

# Respaldo comprimido
manager.config.compression_enabled = True
manager.backup_memory("backup/memory_backup_20241201.json.gz")
```

### Exportación de Sesiones

```python
from short_term import export_session_data

# Exportar datos de una sesión
export_success = export_session_data(
    session_id="session_123",
    export_path="exports/session_123_export.json"
)

# Los datos exportados incluyen:
# - Información de la sesión
# - Mensajes completos
# - Metadatos
# - Timestamps
```

## 🧪 Pruebas

### Ejecutar Todas las Pruebas

```bash
python short_term/test_short_term_system.py
```

### Pruebas Específicas

```python
from short_term.test_short_term_system import ShortTermMemoryTestSuite

# Crear suite de pruebas
test_suite = ShortTermMemoryTestSuite()

# Probar componentes específicos
success, results = test_suite.test_memory_manager_initialization()
success, results = test_suite.test_semantic_analysis()
success, results = test_suite.test_integration()
```

### Tipos de Pruebas

- **Inicialización**: Configuración y creación de componentes
- **Gestión de Sesiones**: Creación, listado, eliminación
- **Operaciones de Mensajes**: Añadir, recuperar, buscar
- **Análisis Semántico**: Embeddings, similitud, búsqueda
- **Generación de Resúmenes**: Resúmenes y extracción de temas
- **Base de Datos**: Operaciones CRUD y persistencia
- **Límites de Memoria**: Gestión de límites y limpieza
- **Respaldo y Exportación**: Respaldo y exportación de datos
- **Manejo de Errores**: Casos edge y errores
- **Integración**: Flujo completo del sistema

## 🔧 Configuración Avanzada

### Configuración Personalizada

```python
from short_term import MemoryConfig, ShortTermMemoryManager

# Configuración para entorno de producción
prod_config = MemoryConfig(
    max_messages=200,
    max_tokens=16384,
    summary_threshold=12000,
    similarity_threshold=0.8,
    cleanup_interval=1800,  # 30 minutos
    compression_enabled=True,
    backup_enabled=True,
    auto_summarize=True,
    semantic_clustering=True,
    memory_dir="/var/shaili/memory",
    database_path="/var/shaili/memory.db",
    cache_dir="/var/shaili/cache"
)

# Configuración para desarrollo
dev_config = MemoryConfig(
    max_messages=20,
    max_tokens=2048,
    summary_threshold=4000,
    cleanup_interval=300,  # 5 minutos
    backup_enabled=False
)
```

### Variables de Entorno

```bash
# Configuración de memoria
export SHORT_TERM_MAX_MESSAGES=100
export SHORT_TERM_MAX_TOKENS=8192
export SHORT_TERM_SUMMARY_THRESHOLD=8000
export SHORT_TERM_SIMILARITY_THRESHOLD=0.7
export SHORT_TERM_CLEANUP_INTERVAL=3600
export SHORT_TERM_MEMORY_DIR="/app/memory"
export SHORT_TERM_DATABASE_PATH="/app/memory.db"
```

## 📊 Monitoreo y Métricas

### Estadísticas del Sistema

```python
from short_term import get_memory_stats

# Obtener estadísticas completas
stats = get_memory_stats()
print(f"Total de sesiones: {stats['total_sessions']}")
print(f"Total de mensajes: {stats['total_messages']}")
print(f"Total de tokens: {stats['total_tokens']}")
print(f"Sesiones activas: {stats['active_sessions']}")
```

### Información de Sesión

```python
# Obtener información detallada de una sesión
info = manager.get_session_info(session_id)
print(f"Sesión ID: {info['session_id']}")
print(f"Usuario: {info['user_id']}")
print(f"Mensajes: {info['message_count']}")
print(f"Tokens: {info['total_tokens']}")
print(f"Resumen: {info['summary']}")
print(f"Importancia promedio: {info['avg_importance']:.2f}")
```

## 🔗 Integración con Shaili AI

### Integración con Chat

```python
# En el sistema de chat
from short_term import create_session, add_message_to_session, get_memory_context

class ChatSystem:
    def __init__(self):
        self.memory_manager = create_memory_manager()
    
    def process_message(self, user_id: str, message: str):
        # Obtener o crear sesión
        session_id = self.get_user_session(user_id)
        
        # Añadir mensaje del usuario
        add_message_to_session(session_id, "user", message, manager=self.memory_manager)
        
        # Obtener contexto para el modelo
        context = get_memory_context(session_id, manager=self.memory_manager)
        
        # Generar respuesta
        response = self.generate_response(context, message)
        
        # Añadir respuesta del asistente
        add_message_to_session(session_id, "assistant", response, manager=self.memory_manager)
        
        return response
    
    def get_user_session(self, user_id: str) -> str:
        # Buscar sesión activa o crear nueva
        sessions = self.memory_manager.list_sessions(user_id)
        if sessions:
            return sessions[0]['session_id']
        else:
            return self.memory_manager.create_session(user_id)
```

### Integración con Evaluación

```python
# En el sistema de evaluación
from short_term import search_messages, calculate_similarity

class EvaluationSystem:
    def __init__(self):
        self.memory_manager = create_memory_manager()
    
    def evaluate_conversation_quality(self, session_id: str):
        # Buscar mensajes relacionados con calidad
        quality_messages = search_messages(
            session_id, 
            "calidad respuesta útil", 
            manager=self.memory_manager
        )
        
        # Analizar coherencia de la conversación
        context = self.memory_manager.get_context(session_id)
        coherence_score = self.analyze_coherence(context)
        
        return {
            "quality_messages": len(quality_messages),
            "coherence_score": coherence_score,
            "total_messages": len(context)
        }
```

## 🐛 Solución de Problemas

### Problemas Comunes

1. **Error de base de datos**
   ```bash
   # Verificar permisos del directorio
   chmod 755 short_term/memory/
   
   # Recrear base de datos
   rm short_term/memory/memory.db
   python -c "from short_term import setup_memory_system; setup_memory_system()"
   ```

2. **Error de memoria insuficiente**
   ```python
   # Reducir límites
   config = MemoryConfig(
       max_messages=20,
       max_tokens=2048,
       cleanup_interval=1800
   )
   ```

3. **Error de similitud semántica**
   ```python
   # Verificar dependencias
   pip install scikit-learn numpy
   
   # Usar umbral más bajo
   similar_messages = search_messages(session_id, query, threshold=0.3)
   ```

4. **Error de caché de embeddings**
   ```bash
   # Limpiar caché
   rm short_term/cache/embeddings_cache.pkl
   ```

### Logs y Debugging

```python
import logging

# Configurar logging detallado
logging.basicConfig(level=logging.DEBUG)

# Verificar logs del sistema
from short_term import create_memory_manager
manager = create_memory_manager()
manager.logger.debug("Mensaje de debug")
```

## 📚 Referencias

- [TF-IDF Documentation](https://scikit-learn.org/stable/modules/generated/sklearn.feature_extraction.text.TfidfVectorizer.html)
- [Cosine Similarity](https://scikit-learn.org/stable/modules/generated/sklearn.metrics.pairwise.cosine_similarity.html)
- [SQLite Documentation](https://docs.python.org/3/library/sqlite3.html)
- [Threading in Python](https://docs.python.org/3/library/threading.html)

## 🤝 Contribución

Para contribuir al desarrollo del sistema de memoria a corto plazo:

1. Fork el repositorio
2. Crear una rama para tu feature (`git checkout -b feature/nueva-funcionalidad`)
3. Commit tus cambios (`git commit -am 'Agregar nueva funcionalidad'`)
4. Push a la rama (`git push origin feature/nueva-funcionalidad`)
5. Crear un Pull Request

## 📄 Licencia

Este proyecto está bajo la licencia MIT. Ver el archivo `LICENSE` para más detalles.

---

**Shaili AI - Memoria a Corto Plazo** - Sistema avanzado de gestión de contexto conversacional
