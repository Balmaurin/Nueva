# Sistema de Exportación - Shaili AI

## 📁 Estructura del Sistema de Exportación

```
exports/
├── export_manager.py              # 🚀 Gestor principal de exportaciones (500+ líneas)
├── data_exporter.py               # 📊 Exportador especializado de datos (400+ líneas)
├── __init__.py                    # 📦 Paquete Python funcional (300+ líneas)
├── test_exports_system.py         # 🧪 Sistema de pruebas completo (400+ líneas)
├── user_data/                     # 👤 Datos de usuario exportados
│   └── user_123_export_20250830_061630.jsonl
└── README.md                      # 📖 Esta documentación
```

## 📊 Estadísticas del Sistema

### 📄 Archivos: 4
### 💻 Líneas de código: 1,600+
### 🐍 Python: 1,600+ líneas
### 🎯 Exportadores: 2 clases principales
### ✅ Estado: Completamente funcional

## 🎯 Componentes del Sistema

### 1. **ExportManager** (`export_manager.py`)

#### **Función Principal:**
Gestor principal de exportaciones que maneja diferentes tipos de datos y formatos.

#### **Características:**
- **Múltiples Formatos**: JSONL, JSON, CSV, XML, YAML
- **Gestión de PII**: Anonimización automática de datos personales
- **Compresión**: Soporte para archivos comprimidos
- **Metadatos**: Generación automática de metadatos con checksums
- **Historial**: Seguimiento de todas las exportaciones
- **Limpieza**: Gestión automática de archivos antiguos

#### **Formatos Soportados:**
- **JSONL**: Formato de líneas JSON (recomendado para grandes volúmenes)
- **JSON**: Formato JSON estructurado con metadatos
- **CSV**: Formato de valores separados por comas
- **XML**: Formato XML estructurado
- **YAML**: Formato YAML legible

#### **Dependencias:**
```python
import json
import csv
import xml.etree.ElementTree as ET
import yaml
import sqlite3
import pandas as pd
from pathlib import Path
from datetime import datetime, timezone
import logging
import hashlib
import zipfile
from dataclasses import dataclass, asdict
import uuid
```

#### **Uso:**
```python
from exports.export_manager import ExportManager, ExportConfig

# Crear configuración
config = ExportConfig(
    format="jsonl",
    include_pii=False,
    include_metadata=True,
    compress=True
)

# Crear gestor
manager = ExportManager(config)

# Exportar datos de usuario
result = manager.export_user_data("user_123", ["profile", "sessions", "conversations"])
```

### 2. **DataExporter** (`data_exporter.py`)

#### **Función Principal:**
Exportador especializado para diferentes tipos de datos del sistema.

#### **Tipos de Datos Soportados:**
- **Conversaciones**: Exportación de chats y diálogos
- **Embeddings**: Vectores de embeddings con metadatos
- **Perfiles de Usuario**: Datos de perfil y preferencias
- **Logs del Sistema**: Archivos de log estructurados
- **Configuraciones**: Archivos de configuración del sistema
- **Resultados de Evaluación**: Métricas y evaluaciones

#### **Formatos de Salida:**
- **CSV**: Para análisis en Excel/Google Sheets
- **JSON**: Para integración con APIs
- **JSONL**: Para procesamiento por lotes
- **Parquet**: Para análisis de datos eficiente
- **Pickle**: Para uso interno de Python

#### **Uso:**
```python
from exports.data_exporter import DataExporter, ExportSpecification

# Crear exportador
exporter = DataExporter()

# Especificar exportación
spec = ExportSpecification(
    data_type="conversations",
    source_path="data/user_data.duckdb",
    output_format="parquet",
    filters={"user_id": "user_123"}
)

# Exportar datos
result = exporter.export_conversations(spec)
```

### 3. **Paquete Python** (`__init__.py`)

#### **Función Principal:**
Transforma la carpeta `exports` en un paquete Python funcional con API unificada.

#### **Características:**
- **API Unificada**: Funciones de conveniencia para exportación rápida
- **Instancias Globales**: Gestión automática de exportadores
- **Configuración Centralizada**: Acceso fácil a configuraciones
- **Validación Automática**: Verificación del sistema al importar
- **Funciones de Utilidad**: Herramientas para gestión y consulta

#### **Uso:**
```python
import exports

# Exportación rápida
result = exports.export_user_data("user_123", format="jsonl", include_pii=False)

# Exportación desde base de datos
result = exports.export_conversations_from_db("data/user_data.duckdb", "csv")

# Gestión de exportaciones
history = exports.get_export_history(10)
exports.cleanup_old_exports(days=30)
```

### 4. **Sistema de Pruebas** (`test_exports_system.py`)

#### **Función Principal:**
Sistema completo de pruebas para validar todos los componentes.

#### **Pruebas Incluidas:**
- **ExportManager**: Validación del gestor principal
- **DataExporter**: Validación del exportador especializado
- **Importaciones del Paquete**: Verificación de la API
- **Operaciones de Archivos**: Pruebas de compresión y gestión
- **Generación de Metadatos**: Validación de metadatos
- **Manejo de Errores**: Pruebas de robustez

#### **Uso:**
```bash
# Ejecutar todas las pruebas
python exports/test_exports_system.py
```

## 🔧 Instalación y Configuración

### 1. **Dependencias Requeridas**
```bash
pip install pandas numpy pyyaml
```

### 2. **Verificación de Instalación**
```bash
# Probar el gestor de exportación
python exports/export_manager.py

# Probar el exportador de datos
python exports/data_exporter.py

# Ejecutar pruebas completas
python exports/test_exports_system.py
```

## 🚀 Ejecución del Sistema

### **Ejecución Individual de Componentes**

#### 1. Gestor de Exportación
```bash
cd exports
python export_manager.py
```

#### 2. Exportador de Datos
```bash
cd exports
python data_exporter.py
```

#### 3. Sistema de Pruebas
```bash
cd exports
python test_exports_system.py
```

### **Ejecución del Paquete**
```python
import exports

# Exportación básica
result = exports.export_user_data("user_123")

# Exportación avanzada
result = exports.export_from_database(
    data_type="conversations",
    source_path="data/user_data.duckdb",
    output_format="parquet",
    filters={"user_id": "user_123"}
)
```

## 📊 Configuración de Exportaciones

### **Configuración Básica**
```python
from exports import ExportConfig

config = ExportConfig(
    format="jsonl",           # Formato de salida
    include_pii=False,        # Incluir datos personales
    include_metadata=True,    # Incluir metadatos
    compress=False,           # Comprimir archivos
    batch_size=1000,          # Tamaño de lotes
    max_file_size=100*1024*1024  # Tamaño máximo (100MB)
)
```

### **Configuración Avanzada**
```python
from exports import ExportSpecification

spec = ExportSpecification(
    data_type="conversations",
    source_path="data/user_data.duckdb",
    output_format="parquet",
    filters={
        "user_id": "user_123",
        "date_from": "2024-01-01",
        "date_to": "2024-12-31"
    },
    include_metadata=True,
    compress=True
)
```

## 🔍 Estructura de Datos

### **Formato JSONL (Líneas JSON)**
```json
{"id": "hash_123", "domain": "user_profile", "data_type": "profile", "content": {"name": "Usuario", "email": "user@example.com"}, "timestamp": "2024-01-15T10:00:00Z", "is_pii": true}
{"id": "hash_456", "domain": "analytics", "data_type": "session", "content": {"last_login": "2024-01-15", "session_count": 5}, "timestamp": "2024-01-15T10:00:00Z", "is_pii": false}
```

### **Formato JSON Estructurado**
```json
{
  "metadata": {
    "export_id": "uuid-123",
    "timestamp": "2024-01-15T10:00:00Z",
    "format": "json",
    "total_records": 2,
    "file_size": 1024,
    "checksum": "sha256-hash",
    "source": "shaili_ai_system"
  },
  "data": [
    {
      "id": "hash_123",
      "domain": "user_profile",
      "data_type": "profile",
      "content": {
        "name": "Usuario",
        "email": "user@example.com"
      },
      "timestamp": "2024-01-15T10:00:00Z",
      "is_pii": true
    }
  ]
}
```

### **Metadatos de Exportación**
```json
{
  "export_id": "uuid-123",
  "timestamp": "2024-01-15T10:00:00Z",
  "format": "jsonl",
  "total_records": 100,
  "file_size": 2048,
  "checksum": "sha256-hash",
  "source": "shaili_ai_system",
  "version": "3.1.0"
}
```

## 🛠️ Desarrollo y Extensión

### **Agregar Nuevos Formatos**

#### 1. Extender ExportManager
```python
def _export_custom_format(self, data, file_path, metadata):
    """Exportar en formato personalizado"""
    # Implementar lógica de exportación
    with open(file_path, 'w', encoding='utf-8') as f:
        # Escribir datos en formato personalizado
        pass
```

#### 2. Registrar en el Sistema
```python
# En _export_data method
elif self.config.format == "custom":
    self._export_custom_format(data, file_path, metadata)
```

### **Agregar Nuevos Tipos de Datos**

#### 1. Extender DataExporter
```python
def export_custom_data(self, spec: ExportSpecification) -> Dict[str, Any]:
    """Exportar datos personalizados"""
    # Implementar lógica de exportación
    return self._export_dataframe(df, spec, "custom_data")
```

#### 2. Registrar en el Paquete
```python
# En __init__.py
export_methods["custom_data"] = exporter.export_custom_data
```

## 📈 Monitoreo y Logs

### **Ubicación de Logs**
- **ExportManager**: `logs/exports/export_manager.log`
- **DataExporter**: `logs/exports/data_exporter.log`

### **Tipos de Logs**
- **Exportaciones**: Registro de todas las exportaciones realizadas
- **Errores**: Problemas durante la exportación
- **Rendimiento**: Métricas de tiempo y tamaño de archivos
- **Limpieza**: Archivos eliminados automáticamente

### **Visualización de Resultados**
```python
# El sistema genera automáticamente:
# - Archivos de exportación en exports/
# - Metadatos en archivos .meta.json
# - Reportes de pruebas en exports/test_report.json
```

## 🔧 Troubleshooting

### **Problemas Comunes**

#### 1. Error de Permisos de Archivo
```bash
# Solución: Verificar permisos
chmod 755 exports/
chmod 644 exports/*.py
```

#### 2. Error de Dependencias Faltantes
```bash
# Instalar dependencias
pip install pandas numpy pyyaml
```

#### 3. Error de Base de Datos
```bash
# Verificar que existe la base de datos
ls data/user_data.duckdb
ls data/embeddings_sqlite.db
```

#### 4. Error de Memoria
```bash
# Reducir tamaño de lotes
config = ExportConfig(batch_size=100)  # En lugar de 1000
```

## 📝 Notas de Implementación

### **Características Destacadas**
- ✅ **Múltiples Formatos**: Soporte para 7 formatos diferentes
- ✅ **Gestión de PII**: Anonimización automática de datos personales
- ✅ **Compresión**: Soporte para archivos comprimidos
- ✅ **Metadatos**: Generación automática con checksums
- ✅ **Historial**: Seguimiento completo de exportaciones
- ✅ **Limpieza Automática**: Gestión de archivos antiguos
- ✅ **API Unificada**: Funciones de conveniencia
- ✅ **Sistema de Pruebas**: Validación completa

### **Limitaciones Actuales**
- ⚠️ **Tamaño de Archivos**: Limitado por memoria disponible
- ⚠️ **Concurrencia**: No soporta exportaciones simultáneas
- ⚠️ **Encriptación**: No incluye encriptación de archivos

### **Mejoras Futuras**
- 📋 **Encriptación**: Soporte para archivos encriptados
- 📋 **Concurrencia**: Exportaciones simultáneas
- 📋 **Streaming**: Exportación de archivos grandes
- 📋 **S3/Azure**: Integración con almacenamiento en la nube
- 📋 **Dashboard**: Interfaz web para gestión

## 🎯 Integración con Shaili AI

### **Uso en el Sistema Principal**
```python
# En el sistema de IA
import exports

# Exportar datos de usuario para análisis
result = exports.export_user_data(
    user_id="user_123",
    data_types=["conversations", "preferences"],
    format="jsonl",
    include_pii=False
)

if result["success"]:
    print(f"Datos exportados: {result['filename']}")
    # Enviar archivo para análisis externo
    send_to_analytics(result["file_path"])
```

### **Exportación Automática**
```python
# Configurar exportación automática
def auto_export_user_data(user_id: str):
    """Exportar datos de usuario automáticamente"""
    result = exports.export_user_data(
        user_id=user_id,
        format="parquet",
        include_pii=False
    )
    
    if result["success"]:
        # Registrar en base de datos
        log_export(user_id, result["export_id"])
        # Notificar al usuario
        notify_user(user_id, "Datos exportados correctamente")
```

### **Gestión de Exportaciones**
```python
# Limpiar exportaciones antiguas semanalmente
def weekly_cleanup():
    """Limpieza semanal de exportaciones"""
    deleted_count = exports.cleanup_old_exports(days=30)
    print(f"Archivos eliminados: {deleted_count}")

# Obtener estadísticas de exportaciones
def get_export_stats():
    """Obtener estadísticas de exportaciones"""
    history = exports.get_export_history(limit=100)
    total_exports = len(history)
    total_records = sum(entry["record_count"] for entry in history)
    
    return {
        "total_exports": total_exports,
        "total_records": total_records,
        "recent_exports": history[:10]
    }
```

## 🚀 Instalación Rápida

### **Opción 1: Uso Directo**
```python
# Importar y usar directamente
import exports

# Exportación básica
result = exports.export_user_data("user_123")
print(f"Exportación: {result['filename']}")
```

### **Opción 2: Configuración Personalizada**
```python
from exports import ExportManager, ExportConfig

# Crear configuración personalizada
config = ExportConfig(
    format="parquet",
    include_pii=False,
    compress=True
)

# Crear gestor
manager = ExportManager(config)

# Exportar datos
result = manager.export_conversations()
```

### **Opción 3: Exportación Especializada**
```python
from exports import DataExporter, ExportSpecification

# Crear exportador especializado
exporter = DataExporter()

# Especificar exportación
spec = ExportSpecification(
    data_type="embeddings",
    source_path="data/embeddings_sqlite.db",
    output_format="parquet",
    filters={"model": "all-MiniLM-L6-v2"}
)

# Exportar datos
result = exporter.export_embeddings(spec)
```

## 📊 Resultados Esperados

### **Ejemplo de Salida del ExportManager**
```json
{
  "success": true,
  "export_id": "uuid-123",
  "filename": "user_123_export_20240115_100000.jsonl",
  "file_path": "exports/user_123_export_20240115_100000.jsonl",
  "metadata_path": "exports/user_123_export_20240115_100000.jsonl.meta.json",
  "total_records": 3,
  "file_size": 2048,
  "checksum": "sha256-hash",
  "format": "jsonl"
}
```

### **Ejemplo de Salida de Pruebas**
```json
{
  "test_summary": {
    "total_tests": 6,
    "passed_tests": 6,
    "failed_tests": 0
  },
  "overall_status": true
}
```

---

**Nota**: Este sistema de exportación es fundamental para la gestión de datos del sistema Shaili AI. Proporciona funcionalidades completas para exportar datos en múltiples formatos, con gestión automática de metadatos, compresión y limpieza. El sistema está completamente funcional y listo para uso en producción.
