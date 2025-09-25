# Módulos del Sistema NeuroFusion

## 📋 Descripción General

El directorio `modules/` contiene todos los módulos especializados del sistema NeuroFusion, organizados por categorías funcionales. Cada módulo es un componente independiente que puede ser cargado dinámicamente y utilizado según las necesidades del sistema.

## 🏗️ Estructura del Directorio (Actualizada)

```
modules/
├── README.md                           # Este archivo
├── __init__.py                         # Inicialización principal del sistema de módulos
├── config/module_config.json                  # Configuración global de módulos
├── module_router.py                    # Router principal de módulos
├── initialize_modules.py               # Inicializador de módulos
├── nucleo_central/                     # ← Núcleo central del sistema
│   ├── __init__.py                     # Importaciones principales
│   ├── config/                         # Configuraciones del núcleo
│   │   ├── rate_limits.json            # Límites de velocidad
│   │   ├── advanced_training_config.json
│   │   └── __init__.py
│   └── security/                       # Seguridad del núcleo
├── security/                           # ← Sistema de seguridad especializado
│   ├── __init__.py
│   ├── authentication.py               # Autenticación multi-factor
│   ├── encryption.py                   # Encriptación AES-256-CBC
│   ├── auth.db                         # Base de datos de autenticación
│   └── encrypted/                      # Archivos encriptados
├── adapters/                           # Adaptadores de compatibilidad
├── ai/                                 # Componentes de IA
├── ai_components/                      # Componentes avanzados de IA
├── blockchain/                         # Sistema de blockchain
├── core/                               # Núcleo del sistema
├── embeddings/                         # Sistema de embeddings
├── evaluation/                         # Evaluación y métricas
├── learning/                           # Sistema de aprendizaje
├── memory/                             # Sistema de memoria
├── orchestrator/                       # Orquestación del sistema
├── plugins/                            # Sistema de plugins
├── recommendations/                    # Sistema de recomendaciones
├── reinforcement/                      # Aprendizaje por refuerzo
├── rewards/                            # Sistema de recompensas
├── scripts/                            # Scripts de utilidad
├── src/                                # Código fuente adicional
├── tokens/                             # Sistema de tokens
├── training/                           # Sistema de entrenamiento
├── unified_systems/                    # Sistemas unificados
├── utils/                              # Utilidades generales
└── visualization/                      # Visualización de datos
```

## 🔧 Módulos Principales

### 1. Sistema de Inicialización (`__init__.py`)

**Clases principales**:
- `ModuleInfo`: Información de módulo registrado
- `ModuleRegistry`: Registro de módulos
- `UnifiedModuleSystem`: Sistema unificado de módulos

**Funciones principales**:
- `initialize_modules()`: Inicializar todos los módulos
- `get_module(name)`: Obtener módulo por nombre
- `list_modules(category)`: Listar módulos por categoría
- `execute_module_function()`: Ejecutar función de módulo

**Dependencias**:
```python
import asyncio
import logging
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, field
from datetime import datetime
```

### 2. Router de Módulos (`module_router.py`)

**Clases principales**:
- `ModuleRequest`: Solicitud de uso de módulo
- `ModuleResponse`: Respuesta de módulo
- `ModuleRouter`: Router principal
- `LLMModuleInterface`: Interfaz para LLMs

**Funciones principales**:
- `execute_module_request()`: Ejecutar solicitud de módulo
- `get_available_modules()`: Obtener módulos disponibles
- `search_modules()`: Buscar módulos
- `get_usage_statistics()`: Obtener estadísticas de uso

**Dependencias**:
```python
import asyncio
import logging
import time
from typing import Dict, List, Optional, Any
from dataclasses import dataclass
from datetime import datetime
```

### 3. Inicializador de Módulos (`initialize_modules.py`)

**Clases principales**:
- `ModuleInitializer`: Inicializador de módulos

**Funciones principales**:
- `initialize_all_modules()`: Inicializar todos los módulos
- `validate_critical_modules()`: Validar módulos críticos
- `test_basic_functionality()`: Probar funcionalidad básica
- `save_report()`: Guardar reporte de inicialización

**Dependencias**:
```python
import asyncio
import json
import logging
from pathlib import Path
from typing import Dict, List, Any
```

## 📁 Módulos por Categoría

### 🔄 Adaptadores (`adapters/`)

**Archivos**:
- `compatibility_adapter.py`: Adaptador de compatibilidad
- `neurofusion_migration_toolkit.py`: Kit de migración

**Funciones principales**:
- `adapt_component()`: Adaptar componente
- `migrate_component()`: Migrar componente
- `transform_module()`: Transformar módulo

**Dependencias**:
```python
import ast
import json
import logging
from typing import Dict, List, Optional, Any
from dataclasses import dataclass
```

### 🤖 IA (`ai/`)

**Archivos**:
- `llm_models.py`: Modelos de lenguaje
- `ml_components.py`: Componentes de ML
- `response_generator.py`: Generador de respuestas
- `semantic_analyzer.py`: Analizador semántico
- `text_processor.py`: Procesador de texto

**Funciones principales**:
- `generate_text()`: Generar texto
- `train_classification_model()`: Entrenar modelo de clasificación
- `generate_response()`: Generar respuesta
- `analyze_semantics()`: Analizar semántica
- `clean_text()`: Limpiar texto

**Dependencias**:
```python
import torch
import numpy as np
import pandas as pd
from transformers import AutoModelForCausalLM, AutoTokenizer
from sklearn.ensemble import RandomForestClassifier
from sentence_transformers import SentenceTransformer
import spacy
```

### 🧠 Componentes de IA (`ai_components/`)

**Archivos**:
- `advanced_ai_system.py`: Sistema de IA avanzado
- `advanced_algorithm_refinement.py`: Refinamiento de algoritmos
- `advanced_contextual_reasoning.py`: Razonamiento contextual
- `advanced_module_enhancer.py`: Mejorador de módulos
- `module_enhancer.py`: Mejorador de módulos
- `neurofusion_component_adapters.py`: Adaptadores de componentes

**Funciones principales**:
- `fine_tune()`: Fine-tuning de modelo
- `evaluate_response_quality()`: Evaluar calidad de respuesta
- `enhance_module()`: Mejorar módulo
- `adapt_component()`: Adaptar componente

**Dependencias**:
```python
import torch
import numpy as np
from transformers import AutoModelForCausalLM, AutoTokenizer
from peft import LoraConfig, get_peft_model
import networkx as nx
import ast
```

### ⛓️ Blockchain (`blockchain/`)

**Archivos**:
- `solana_blockchain_real.py`: Blockchain Solana real
- `sheily_spl_real.py`: Gestor SPL real
- `sheily_spl_manager.py`: Gestor SPL básico
- `sheily_token_manager.py`: Gestor de tokens
- `secure_key_management.py`: Gestión segura de claves
- `rate_limiter.py`: Control de rate limiting
- `transaction_monitor.py`: Monitoreo de transacciones
- `spl_data_persistence.py`: Persistencia de datos SPL

**Funciones principales**:
- `create_wallet()`: Crear wallet
- `transfer_tokens()`: Transferir tokens
- `mint_tokens()`: Mintear tokens
- `check_rate_limit()`: Verificar rate limit
- `record_transaction_event()`: Registrar evento de transacción

**Dependencias**:
```python
from solana.rpc.api import Client
from solana.transaction import Transaction
from solana.keypair import Keypair
from cryptography.fernet import Fernet
import sqlite3
import threading
```

### 🎯 Núcleo (`core/`)

**Archivos**:
- `advanced_system_integrator.py`: Integrador de sistema avanzado
- `cognitive_understanding_module.py`: Módulo de comprensión cognitiva
- `continuous_improvement.py`: Mejora continua
- `daily_exercise_generator.py`: Generador de ejercicios diarios
- `daily_exercise_integrator.py`: Integrador de ejercicios
- `enhanced_daily_exercise_generator.py`: Generador mejorado
- `enhanced_daily_exercise_integrator.py`: Integrador mejorado
- `integration_manager.py`: Gestor de integración
- `neurofusion_core.py`: Núcleo de NeuroFusion
- `semantic_adaptation_manager.py`: Gestor de adaptación semántica

**Funciones principales**:
- `process_query()`: Procesar consulta
- `analyze_cognitive_complexity()`: Analizar complejidad cognitiva
- `generate_daily_exercises()`: Generar ejercicios diarios
- `integrate_exercises()`: Integrar ejercicios

**Dependencias**:
```python
import torch
import numpy as np
from transformers import AutoModelForCausalLM, AutoTokenizer
import yaml
import json
```

### 🔍 Embeddings (`embeddings/`)

**Archivos**:
- `embedding_performance_monitor.py`: Monitor de rendimiento
- `semantic_search_engine.py`: Motor de búsqueda semántica

**Funciones principales**:
- `track_embedding_generation()`: Rastrear generación de embeddings
- `search()`: Buscar semánticamente
- `get_stats()`: Obtener estadísticas

**Dependencias**:
```python
import numpy as np
from sentence_transformers import SentenceTransformer
import faiss
from typing import List, Tuple, Dict, Any
```

### 📊 Evaluación (`evaluation/`)

**Archivos**:
- `model_validator.py`: Validador de modelos
- `performance_metrics.py`: Métricas de rendimiento
- `quality_evaluator.py`: Evaluador de calidad
- `result_analyzer.py`: Analizador de resultados

**Funciones principales**:
- `validate_model()`: Validar modelo
- `calculate_classification_metrics()`: Calcular métricas de clasificación
- `evaluate_dataframe_quality()`: Evaluar calidad de dataframe
- `analyze_classification_results()`: Analizar resultados de clasificación

**Dependencias**:
```python
import numpy as np
import pandas as pd
from sklearn.metrics import accuracy_score, precision_recall_fscore_support
from sklearn.model_selection import cross_val_score
import matplotlib.pyplot as plt
import seaborn as sns
```

### 🧠 Aprendizaje (`learning/`)

**Archivos**:
- `demo_continuous_learning.py`: Demo de aprendizaje continuo
- `neural_plasticity_manager.py`: Gestor de plasticidad neural

**Funciones principales**:
- `process_query_with_learning()`: Procesar consulta con aprendizaje
- `provide_feedback()`: Proporcionar feedback
- `update_plasticity()`: Actualizar plasticidad

**Dependencias**:
```python
import asyncio
import logging
from typing import Dict, List, Optional, Any
from datetime import datetime
```

### 💾 Memoria (`memory/`)

**Archivos**:
- `data_management.py`: Gestión de datos
- `intelligent_fallback_system.py`: Sistema de fallback inteligente
- `rag.py`: Sistema RAG
- `short_term.py`: Memoria a corto plazo

**Funciones principales**:
- `store_user_data()`: Almacenar datos de usuario
- `generate_backup_response()`: Generar respuesta de backup
- `add_document()`: Agregar documento
- `add_message()`: Agregar mensaje

**Dependencias**:
```python
import duckdb
import faiss
import numpy as np
from sentence_transformers import SentenceTransformer
import json
```

### 🔌 Plugins (`plugins/`)

**Archivos**:
- `logging_plugin.py`: Plugin de logging

**Funciones principales**:
- `pre_process()`: Pre-procesar
- `post_process()`: Post-procesar
- `on_error()`: Manejar error

**Dependencias**:
```python
import logging
import time
from typing import Any, Dict
```

### 🎯 Recomendaciones (`recommendations/`)

**Archivos**:
- `personalized_recommendations.py`: Recomendaciones personalizadas

**Funciones principales**:
- `generate_user_profile()`: Generar perfil de usuario
- `get_exercise_recommendations()`: Obtener recomendaciones de ejercicios
- `create_learning_path()`: Crear ruta de aprendizaje
- `record_feedback()`: Registrar feedback

**Dependencias**:
```python
import sqlite3
import numpy as np
from typing import List, Dict, Any
from dataclasses import dataclass
from datetime import datetime
```

### 🎮 Refuerzo (`reinforcement/`)

**Archivos**:
- `adaptive_learning_agent.py`: Agente de aprendizaje adaptativo

**Funciones principales**:
- `select_action()`: Seleccionar acción
- `update_policy()`: Actualizar política
- `generate_reward()`: Generar recompensa
- `learn_from_interaction()`: Aprender de interacción

**Dependencias**:
```python
import torch
import torch.nn as nn
import numpy as np
from typing import Dict, Any, Optional
```

### 🏆 Recompensas (`rewards/`)

**Archivos**:
- `adaptive_rewards.py`: Recompensas adaptativas
- `advanced_optimization.py`: Optimización avanzada
- `contextual_accuracy.py`: Precisión contextual
- `integration_example.py`: Ejemplo de integración
- `reward_system.py`: Sistema de recompensas
- `tracker.py`: Rastreador

**Funciones principales**:
- `update_performance()`: Actualizar rendimiento
- `optimize_reward_factors()`: Optimizar factores de recompensa
- `record_interaction()`: Registrar interacción
- `track_session()`: Rastrear sesión

**Dependencias**:
```python
import json
import numpy as np
from typing import Dict, List, Any
from datetime import datetime
```

### 📜 Scripts (`scripts/`)

**Archivos**:
- `audit.py`: Auditoría
- `data_curation.py`: Curación de datos
- `dependency_manager.py`: Gestor de dependencias
- `download_branch_datasets.py`: Descargar datasets de ramas
- `download_datasets.py`: Descargar datasets
- `env_manager.py`: Gestor de entorno
- `layer_manager.py`: Gestor de capas
- `restore_branch_structure.py`: Restaurar estructura de ramas
- `security_audit.py`: Auditoría de seguridad
- `select_micro_branches.py`: Seleccionar micro-ramas
- `slack_notification.py`: Notificaciones de Slack
- `train_branch_adapters.py`: Entrenar adaptadores de ramas

**Funciones principales**:
- `run_full_audit()`: Ejecutar auditoría completa
- `process_data_sources()`: Procesar fuentes de datos
- `load_all_modules()`: Cargar todos los módulos
- `download_branch_datasets()`: Descargar datasets de ramas

**Dependencias**:
```python
import requests
import json
import yaml
import asyncio
from pathlib import Path
from typing import Dict, List, Any
```

### 🔒 Seguridad (`security/`)

**Archivos**:
- `neurofusion_unified_core.py`: Núcleo unificado
- `neurofusion_unified_launcher.py`: Lanzador unificado

**Funciones principales**:
- `register_component()`: Registrar componente
- `get_component()`: Obtener componente
- `apply_plugin_to_component()`: Aplicar plugin a componente
- `get_system_performance()`: Obtener rendimiento del sistema

**Dependencias**:
```python
import abc
import logging
from typing import Dict, List, Optional, Any, Generic, TypeVar
from dataclasses import dataclass, field
from enum import Enum, auto
```

### 🎫 Tokens (`tokens/`)

**Archivos**:
- `advanced_sheily_token_system.py`: Sistema avanzado de tokens
- `sheily_token_manager.py`: Gestor de tokens
- `sheily_tokens_system.py`: Sistema de tokens
- `unified_sheily_token_system.py`: Sistema unificado de tokens

**Funciones principales**:
- `generate_tokens_for_training_session()`: Generar tokens para sesión de entrenamiento
- `generate_tokens_for_response()`: Generar tokens para respuesta
- `stake_tokens()`: Hacer stake de tokens
- `create_marketplace_listing()`: Crear listado en marketplace

**Dependencias**:
```python
import uuid
import asyncio
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum, auto
```

### 🎓 Entrenamiento (`training/`)

**Archivos**:
- `add_more_training_data.py`: Agregar más datos de entrenamiento
- `advanced_training_system.py`: Sistema avanzado de entrenamiento
- `automatic_lora_trainer.py`: Entrenador automático LoRA
- `download_headqa_dataset.py`: Descargar dataset HEAD-QA
- `download_training_dataset.py`: Descargar dataset de entrenamiento

**Funciones principales**:
- `start_exercise_session()`: Iniciar sesión de ejercicio
- `submit_answer()`: Enviar respuesta
- `start_monitoring()`: Iniciar monitoreo
- `download_headqa_method1()`: Descargar HEAD-QA método 1

**Dependencias**:
```python
import torch
import numpy as np
from transformers import AutoModelForCausalLM, AutoTokenizer
from sentence_transformers import SentenceTransformer
import requests
import json
```

### 🔗 Sistemas Unificados (`unified_systems/`)

**Archivos**:
- `consolidated_system_architecture.py`: Arquitectura consolidada
- `integrated_demo.py`: Demo integrado
- `migration_script.py`: Script de migración
- `module_initializer.py`: Inicializador de módulos
- `module_integrator.py`: Integrador de módulos
- `module_monitor.py`: Monitor de módulos
- `module_plugin_system.py`: Sistema de plugins
- `module_registry.py`: Registro de módulos
- `module_scanner.py`: Escáner de módulos
- `module_validator.py`: Validador de módulos
- `neurofusion_master_system.py`: Sistema maestro
- `start_master_system.py`: Iniciar sistema maestro
- `unified_api_server.py`: Servidor API unificado
- `unified_auth_security_system.py`: Sistema de autenticación unificado
- `unified_branch_tokenizer.py`: Tokenizador unificado
- `unified_consciousness_memory_system.py`: Sistema de memoria consciente
- `unified_generation_response_system.py`: Sistema de generación unificado
- `unified_learning_quality_system.py`: Sistema de calidad de aprendizaje
- `unified_learning_system.py`: Sistema de aprendizaje unificado
- `unified_learning_training_system.py`: Sistema de entrenamiento unificado
- `unified_legacy_integration_system.py`: Sistema de integración legacy
- `unified_quality_evaluator.py`: Evaluador de calidad unificado
- `unified_security_auth_system.py`: Sistema de seguridad unificado
- `unified_system_core.py`: Núcleo del sistema unificado

**Funciones principales**:
- `initialize_system()`: Inicializar sistema
- `register_module()`: Registrar módulo
- `validate_module()`: Validar módulo
- `integrate_modules()`: Integrar módulos

**Dependencias**:
```python
import asyncio
import json
import logging
from typing import Dict, List, Optional, Any
from pathlib import Path
```

### 🛠️ Utilidades (`utils/`)

**Archivos**:
- `base_tools.py`: Herramientas base
- `config.yaml`: Configuración
- `continuous_improvement_config.yaml`: Configuración de mejora continua
- `data_sources.json`: Fuentes de datos
- `data_sources.yaml`: Fuentes de datos YAML
- `logging.py`: Sistema de logging
- `metrics.py`: Métricas
- `training_config.yaml`: Configuración de entrenamiento

**Funciones principales**:
- `setup_logging()`: Configurar logging
- `load_config()`: Cargar configuración
- `calculate_metrics()`: Calcular métricas

**Dependencias**:
```python
import logging
import yaml
import json
from pathlib import Path
from typing import Dict, Any
```

### 📈 Visualización (`visualization/`)

**Archivos**:
- `insights_dashboard.py`: Dashboard de insights

**Funciones principales**:
- `generate_dashboard()`: Generar dashboard
- `create_visualizations()`: Crear visualizaciones

**Dependencias**:
```python
import matplotlib.pyplot as plt
import seaborn as sns
import plotly.express as px
import pandas as pd
```

## 🔗 Dependencias Globales

### Librerías Principales
```python
# Machine Learning y IA
torch>=2.0.0
transformers>=4.30.0
sentence-transformers>=2.2.0
scikit-learn>=1.3.0
numpy>=1.24.0
pandas>=2.0.0

# Procesamiento de texto
spacy>=3.6.0
nltk>=3.8.0

# Blockchain
solana>=0.30.0
cryptography>=41.0.0

# Base de datos
sqlite3
duckdb>=0.8.0
psycopg2-binary>=2.9.0

# Utilidades
asyncio
aiohttp>=3.8.0
requests>=2.31.0
pyyaml>=6.0
python-dotenv>=1.0.0

# Visualización
matplotlib>=3.7.0
seaborn>=0.12.0
plotly>=5.15.0

# Monitoreo y métricas
prometheus-client>=0.17.0
psutil>=5.9.0
```

### Variables de Entorno Requeridas
```bash
# Configuración del sistema
NEUROFUSION_ENV=development
NEUROFUSION_LOG_LEVEL=INFO
NEUROFUSION_CONFIG_PATH=config/

# Base de datos
DATABASE_URL=postgresql://user:pass@localhost/neurofusion
SQLITE_DB_PATH=data/neurofusion.db

# Blockchain
SOLANA_NETWORK=devnet
SOLANA_RPC_URL=https://api.devnet.solana.com
SOLANA_API_KEY=your_api_key

# Modelos de IA
MODEL_PATH=models/custom/sheily-personal-model
EMBEDDING_MODEL=sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2

# Seguridad
SECRET_KEY=your_secret_key
JWT_SECRET=your_jwt_secret
```

## 🚀 Instalación y Configuración

### 1. Instalar dependencias
```bash
pip install -r requirements.txt
```

### 2. Configurar variables de entorno
```bash
cp .env.example .env
# Editar .env con tus configuraciones
```

### 3. Inicializar módulos
```python
from modules import initialize_modules

# Inicializar todos los módulos
await initialize_modules()

# Obtener módulo específico
from modules import get_module
ai_module = get_module("advanced_ai_system")
```

## 📊 Uso del Sistema

### Ejemplo básico de uso
```python
from modules import get_module, execute_module_function

# Obtener módulo de IA
ai_module = get_module("advanced_ai_system")

# Ejecutar función
response = await execute_module_function(
    "advanced_ai_system", 
    "generate_response", 
    prompt="Hola, ¿cómo estás?"
)
```

### Ejemplo con blockchain
```python
from modules.blockchain import get_solana_blockchain

# Obtener sistema blockchain
blockchain = get_solana_blockchain()

# Crear wallet
wallet = blockchain.create_wallet("usuario1")

# Transferir tokens
transaction = blockchain.transfer_tokens("usuario1", "usuario2", 100)
```

### Ejemplo con entrenamiento
```python
from modules.training import get_advanced_training_system

# Obtener sistema de entrenamiento
training = get_advanced_training_system()

# Iniciar sesión de ejercicio
session = training.start_exercise_session("usuario1", "exercise_001")

# Enviar respuesta
result = training.submit_answer(session["session_id"], "usuario1", "question_001", "respuesta")
```

## 🔧 Mantenimiento

### Limpieza de módulos
```python
from modules import list_modules, get_module_info

# Listar módulos por categoría
ai_modules = list_modules("ai")
blockchain_modules = list_modules("blockchain")

# Obtener información de módulo
module_info = get_module_info("advanced_ai_system")
```

### Monitoreo de rendimiento
```python
from modules import get_module

# Obtener métricas de módulo
ai_module = get_module("advanced_ai_system")
metrics = ai_module.get_performance_stats()
```

## 🚨 Troubleshooting

### Problemas comunes

1. **Error de importación de módulo**
   - Verificar que el módulo existe en la ruta correcta
   - Comprobar dependencias instaladas
   - Verificar archivo `__init__.py`

2. **Error de inicialización**
   - Verificar configuración en `config/module_config.json`
   - Comprobar variables de entorno
   - Revisar logs de inicialización

3. **Error de dependencias**
   - Ejecutar `pip install -r requirements.txt`
   - Verificar versiones de librerías
   - Comprobar compatibilidad

4. **Error de blockchain**
   - Verificar conexión a Solana
   - Comprobar configuración de red
   - Verificar API keys

## 📞 Soporte

Para problemas específicos de módulos:

1. Revisar logs del sistema
2. Verificar configuración de módulos
3. Comprobar dependencias
4. Consultar documentación específica del módulo

## 🔄 Actualizaciones

El sistema de módulos se actualiza automáticamente. Para actualizaciones manuales:

1. Hacer backup de configuración
2. Actualizar código de módulos
3. Verificar compatibilidad
4. Probar funcionalidad
5. Restaurar configuración si es necesario
