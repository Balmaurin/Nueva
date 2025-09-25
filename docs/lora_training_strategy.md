# Estrategia de Entrenamiento LoRA basada en los datasets verificados

Esta guía describe la arquitectura propuesta para entrenar adaptadores LoRA sobre el modelo local **Llama-3.2-3B-Instruct-Q8_0** utilizando únicamente datasets generados y validados dentro de la plataforma. El flujo se activa cuando los usuarios alcanzan el umbral de calidad del 95 % en los ejercicios oficiales de cualquiera de las 35 ramas.

## 1. Infraestructura de entrenamiento

- **Modelo base**: `Llama-3.2-3B-Instruct-Q8_0` cargado en el servidor local (`backend/llm_server.py`).
- **Hardware esperado**: GPU con al menos 24 GB de VRAM o clúster con soporte para cuantización Q8. En entornos sin GPU se utilizará CPU de alto rendimiento con compilación AVX2.
- **Entorno de ejecución**: contenedor Docker dedicado con acceso al volumen `datasets/` y al registro de modelos `backend/database/model_registry`.
- **Gestor de tareas**: se recomienda integrar `Celery` o `RQ` para orquestar ejecuciones asincrónicas, consumiendo eventos de la tabla `user_branch_progress`.

## 2. Pipeline de datasets

1. **Generación**: cada ejercicio resuelto con ≥ 95 % de precisión inserta un snapshot JSON en `user_branch_progress.dataset_snapshot` con el identificador del intento y la respuesta normalizada.
2. **Consolidación**: un proceso nocturno agrupa los intentos verificados por rama y tipo de ejercicio. Los datasets se almacenan en `datasets/<branch_key>/<timestamp>.jsonl` con metadatos de versión.
3. **Validación offline**: antes de entrenar, se ejecutan validaciones sintácticas (`pydantic`) y semánticas (consistencia de respuestas correctas, longitud mínima, detección de contenido duplicado).
4. **Aprobación manual** (opcional): los operadores pueden revisar un muestreo desde el dashboard y aprobar el lote antes del entrenamiento.

## 3. Entrenamiento LoRA

- **Configuración base**: parámetros iniciales definidos en `Frontend/services/branchTrainingService.ts` (learning rate `2e-5`, `r=16`, `alpha=32`, `dropout=0.05`).
- **Agendamiento**: cuando un lote alcanza al menos 200 muestras válidas por rama y tipo, se crea un registro en `model_registry` con estado `pending-training`.
- **Ejecución**:
  1. Cargar pesos Q8 del modelo base.
  2. Preparar el dataset tokenizado en batches de tamaño 4 con `gradient_accumulation_steps=4`.
  3. Aplicar el adaptador LoRA en las proyecciones claves/valores (`q_proj`, `k_proj`, `v_proj`, `o_proj`).
  4. Guardar checkpoints cada 500 pasos y registrar métricas en `model_training_metrics`.
- **Entrega**: al finalizar, se actualiza `model_registry.status` a `ready` y se publica el adaptador en `models/lora/<branch_key>/<version>`.

## 4. Triggers de calidad

- **Nivel usuario**: cuando un nivel se marca como `completed` (≥ 95 %), se suman tokens y se registra el dataset en `user_branch_progress`.
- **Nivel rama**: un proceso agrega la precisión media (`metrics.average_accuracy`) desde `/api/training/branches`. Si una rama mantiene ≥ 92 % durante dos ciclos, se programa un entrenamiento.
- **Post-entrenamiento**: los adaptadores se evalúan con los conjuntos de validación generados por ejercicios de tipo `multiple_choice`. Los resultados se almacenan con `verification_status='verified'`.

## 5. Seguridad y auditoría

- Toda la información sensible (tokens de usuarios, respuestas correctas) permanece en PostgreSQL con roles restringidos.
- Los datasets exportados incluyen hash SHA-256 y firma opcional del operador.
- Cada ejecución LoRA guarda un manifiesto (`training_sessions`) con hardware, duración y commit del repositorio.

Esta estrategia garantiza que los modelos adaptados evolucionen exclusivamente a partir de datos comprobados por la plataforma, eliminando dependencias de servicios externos o métricas ficticias.
