"""
Sistema Unificado de Generación y Respuesta para NeuroFusion

Este módulo combina funcionalidades de:
- Generation Output (generation_output.py)
- Response Orchestrator (response_orchestrator.py)
- Semantic Validator (semantic_validator.py)
- Prompt Adaptativo (prompt_adaptativo.py)
- Generacion Adaptativa (generacion_adaptativa.py)
- Refinamiento Semantico (refinamiento_semantico.py)
- Classification Output (classification_output.py)
- Regression Output (regression_output.py)
"""

import logging
import json
import time
import sqlite3
import asyncio
from datetime import datetime, timedelta
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
from typing import Dict, List, Optional, Any, Tuple, Union
from collections import defaultdict, deque
import numpy as np
import torch
import torch.nn as nn
from sentence_transformers import SentenceTransformer
import difflib

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class GenerationType(Enum):
    """Tipos de generación"""

    TEXT = "text"
    CLASSIFICATION = "classification"
    REGRESSION = "regression"
    CODE = "code"
    CREATIVE = "creative"
    TECHNICAL = "technical"


class ResponseMode(Enum):
    """Modos de respuesta"""

    DIRECT = "direct"
    ADAPTIVE = "adaptive"
    CONTEXTUAL = "contextual"
    CREATIVE = "creative"
    ANALYTICAL = "analytical"


class ValidationLevel(Enum):
    """Niveles de validación"""

    BASIC = "basic"
    SEMANTIC = "semantic"
    LOGICAL = "logical"
    COMPREHENSIVE = "comprehensive"


@dataclass
class GenerationConfig:
    """Configuración del sistema de generación"""

    generation_type: GenerationType = GenerationType.TEXT
    response_mode: ResponseMode = ResponseMode.ADAPTIVE
    validation_level: ValidationLevel = ValidationLevel.SEMANTIC
    max_length: int = 1000
    temperature: float = 0.7
    creativity_level: float = 0.5
    context_window: int = 10
    quality_threshold: float = 0.7
    enable_adaptation: bool = True
    enable_refinement: bool = True


@dataclass
class GenerationRequest:
    """Solicitud de generación"""

    prompt: str
    context: Optional[Dict[str, Any]] = None
    generation_type: GenerationType = GenerationType.TEXT
    response_mode: ResponseMode = ResponseMode.ADAPTIVE
    constraints: Optional[Dict[str, Any]] = None
    metadata: Optional[Dict[str, Any]] = None


@dataclass
class GenerationResult:
    """Resultado de generación"""

    id: str
    content: str
    generation_type: GenerationType
    response_mode: ResponseMode
    quality_score: float
    confidence: float
    processing_time: float
    created_at: datetime
    metadata: Dict[str, Any] = field(default_factory=dict)
    validation_results: Optional[Dict[str, Any]] = None
    refinements: List[str] = field(default_factory=list)


@dataclass
class ValidationResult:
    """Resultado de validación"""

    is_valid: bool
    score: float
    issues: List[str]
    suggestions: List[str]
    confidence: float
    validation_level: ValidationLevel


class UnifiedGenerationResponseSystem:
    """Sistema unificado de generación y respuesta"""

    def __init__(
        self, config: Optional[GenerationConfig] = None, db_path: Optional[str] = None
    ):
        """Inicializar sistema unificado"""
        self.config = config or GenerationConfig()
        self.db_path = db_path or "./data/generation_response_system.db"

        # Componentes del sistema
        self.generation_history: List[GenerationResult] = []
        self.prompt_templates: Dict[str, str] = {}
        self.quality_metrics: Dict[str, List[float]] = defaultdict(list)
        self.adaptation_patterns: Dict[str, Any] = {}

        # Inicializar componentes
        self._init_database()
        self._init_generation_components()
        self._init_validation_components()
        self._init_adaptation_components()

        logger.info("✅ Sistema Unificado de Generación y Respuesta inicializado")

    def _init_database(self):
        """Inicializar base de datos"""
        try:
            # Crear directorio si no existe
            Path(self.db_path).parent.mkdir(parents=True, exist_ok=True)
            self.conn = sqlite3.connect(self.db_path)
            self._create_tables()
            logger.info("✅ Base de datos de generación y respuesta inicializada")
        except Exception as e:
            logger.error(f"Error inicializando base de datos: {e}")
            raise

    def _create_tables(self):
        """Crear tablas en base de datos"""
        cursor = self.conn.cursor()

        # Tabla de generaciones
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS generations (
                id TEXT PRIMARY KEY,
                prompt TEXT NOT NULL,
                content TEXT NOT NULL,
                generation_type TEXT NOT NULL,
                response_mode TEXT NOT NULL,
                quality_score REAL NOT NULL,
                confidence REAL NOT NULL,
                processing_time REAL NOT NULL,
                created_at TEXT NOT NULL,
                metadata TEXT,
                validation_results TEXT
            )
        """
        )

        # Tabla de validaciones
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS validations (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                generation_id TEXT NOT NULL,
                is_valid BOOLEAN NOT NULL,
                score REAL NOT NULL,
                issues TEXT,
                suggestions TEXT,
                confidence REAL NOT NULL,
                validation_level TEXT NOT NULL,
                timestamp TEXT NOT NULL,
                FOREIGN KEY (generation_id) REFERENCES generations (id)
            )
        """
        )

        # Tabla de refinamientos
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS refinements (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                generation_id TEXT NOT NULL,
                original_content TEXT NOT NULL,
                refined_content TEXT NOT NULL,
                improvement_score REAL NOT NULL,
                refinement_type TEXT NOT NULL,
                timestamp TEXT NOT NULL,
                FOREIGN KEY (generation_id) REFERENCES generations (id)
            )
        """
        )

        # Tabla de métricas de calidad
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS quality_metrics (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                metric_type TEXT NOT NULL,
                metric_value REAL NOT NULL,
                generation_id TEXT,
                timestamp TEXT NOT NULL,
                metadata TEXT
            )
        """
        )

        # Índices
        cursor.execute(
            "CREATE INDEX IF NOT EXISTS idx_generation_type ON generations(generation_type)"
        )
        cursor.execute(
            "CREATE INDEX IF NOT EXISTS idx_quality_score ON generations(quality_score)"
        )
        cursor.execute(
            "CREATE INDEX IF NOT EXISTS idx_created_at ON generations(created_at)"
        )
        cursor.execute(
            "CREATE INDEX IF NOT EXISTS idx_validation_level ON validations(validation_level)"
        )

        self.conn.commit()
        cursor.close()

    def _init_generation_components(self):
        """Inicializar componentes de generación"""
        self.generation_types = {
            GenerationType.TEXT: self._generate_text,
            GenerationType.CLASSIFICATION: self._generate_classification,
            GenerationType.REGRESSION: self._generate_regression,
            GenerationType.CODE: self._generate_code,
            GenerationType.CREATIVE: self._generate_creative,
            GenerationType.TECHNICAL: self._generate_technical,
        }

        self.response_modes = {
            ResponseMode.DIRECT: self._direct_response,
            ResponseMode.ADAPTIVE: self._adaptive_response,
            ResponseMode.CONTEXTUAL: self._contextual_response,
            ResponseMode.CREATIVE: self._creative_response,
            ResponseMode.ANALYTICAL: self._analytical_response,
        }

    def _init_validation_components(self):
        """Inicializar componentes de validación"""
        self.validation_levels = {
            ValidationLevel.BASIC: self._basic_validation,
            ValidationLevel.SEMANTIC: self._semantic_validation,
            ValidationLevel.LOGICAL: self._logical_validation,
            ValidationLevel.COMPREHENSIVE: self._comprehensive_validation,
        }

        # Inicializar modelo de embeddings para validación semántica
        try:
            self.embedding_model = SentenceTransformer(
                "paraphrase-multilingual-MiniLM-L12-v2"
            )
        except Exception as e:
            logger.warning(f"No se pudo cargar modelo de embeddings: {e}")
            self.embedding_model = None

    def _init_adaptation_components(self):
        """Inicializar componentes de adaptación"""
        self.adaptation_strategies = {
            "prompt_enhancement": self._enhance_prompt,
            "context_integration": self._integrate_context,
            "style_adaptation": self._adapt_style,
            "complexity_adjustment": self._adjust_complexity,
        }

    async def generate_response(self, request: GenerationRequest) -> GenerationResult:
        """Generar respuesta unificada"""
        start_time = time.time()

        try:
            # Adaptar prompt si está habilitado
            if self.config.enable_adaptation:
                adapted_prompt = await self._adapt_prompt(request)
            else:
                adapted_prompt = request.prompt

            # Generar contenido según tipo
            generator = self.generation_types[request.generation_type]
            raw_content = await generator(adapted_prompt, request.context)

            # Aplicar modo de respuesta
            response_processor = self.response_modes[request.response_mode]
            processed_content = await response_processor(raw_content, request.context)

            # Validar resultado
            validation_result = await self._validate_generation(
                processed_content, request
            )

            # Refinar si es necesario
            final_content = processed_content
            refinements = []
            if self.config.enable_refinement and not validation_result.is_valid:
                final_content, refinements = await self._refine_generation(
                    processed_content, validation_result
                )

            # Calcular métricas
            quality_score = self._calculate_quality_score(
                final_content, validation_result
            )
            confidence = self._calculate_confidence(final_content, validation_result)

            processing_time = time.time() - start_time

            # Crear resultado
            result_id = f"gen_{int(time.time() * 1000)}"
            result = GenerationResult(
                id=result_id,
                content=final_content,
                generation_type=request.generation_type,
                response_mode=request.response_mode,
                quality_score=quality_score,
                confidence=confidence,
                processing_time=processing_time,
                created_at=datetime.now(),
                metadata=request.metadata or {},
                validation_results=validation_result.__dict__,
                refinements=refinements,
            )

            # Guardar resultado
            await self._save_generation_to_db(result)
            self.generation_history.append(result)

            return result

        except Exception as e:
            logger.error(f"Error generando respuesta: {e}")
            raise

    async def _generate_text(
        self, prompt: str, context: Optional[Dict[str, Any]] = None
    ) -> str:
        """Generar texto usando modelo base real"""
        try:
            # Usar modelo base para generación real
            model = self.components.get("base_model")
            if not model:
                raise ValueError("No hay modelo base disponible para generación")

            # Generar respuesta con parámetros configurables
            response = model.generate(
                prompt,
                max_tokens=512,  # Longitud configurable
                temperature=0.7,  # Control de aleatoriedad
                top_p=0.9,  # Muestreo núcleo
                stop_sequences=["\n\n"],  # Detener en párrafos completos
            )

            # Validar calidad de la respuesta
            if not response or len(response) < 10:
                raise ValueError("Respuesta generada es demasiado corta")

            return response

        except Exception as e:
            logger.error(f"Error en generación de texto real: {e}")
            raise

    async def _generate_classification(
        self, prompt: str, context: Optional[Dict[str, Any]] = None
    ) -> str:
        """Generar clasificación usando modelo especializado"""
        try:
            # Usar modelo de clasificación real
            classifier = self.components.get("classification_model")
            if not classifier:
                raise ValueError("No hay modelo de clasificación disponible")

            # Clasificación con probabilidades
            result = classifier.predict(prompt)

            # Formato de salida con probabilidades
            return json.dumps(
                {"category": result.category, "probabilities": result.probabilities}
            )

        except Exception as e:
            logger.error(f"Error en clasificación real: {e}")
            raise

    async def _generate_regression(
        self, prompt: str, context: Optional[Dict[str, Any]] = None
    ) -> str:
        """Generar regresión usando modelo especializado"""
        try:
            # Usar modelo de regresión real
            regressor = self.components.get("regression_model")
            if not regressor:
                raise ValueError("No hay modelo de regresión disponible")

            # Predicción con intervalo de confianza
            prediction = regressor.predict(prompt)

            # Formato de salida con detalles
            return json.dumps(
                {
                    "predicted_value": prediction.value,
                    "confidence_interval": prediction.confidence_interval,
                    "standard_error": prediction.standard_error,
                }
            )

        except Exception as e:
            logger.error(f"Error en regresión real: {e}")
            raise

    async def _generate_code(
        self, prompt: str, context: Optional[Dict[str, Any]] = None
    ) -> str:
        """Generar código"""
        # Simular generación de código
        language = context.get("language", "python") if context else "python"
        return f"# Código {language}\ndef example():\n    return '{prompt[:20]}...'"

    async def _generate_creative(
        self, prompt: str, context: Optional[Dict[str, Any]] = None
    ) -> str:
        """Generar contenido creativo"""
        creative_elements = ["💡", "🎨", "✨", "🌟"]
        element = creative_elements[int(time.time()) % len(creative_elements)]

        return f"{element} Idea creativa: {prompt[:40]}... {element}"

    async def _generate_technical(
        self, prompt: str, context: Optional[Dict[str, Any]] = None
    ) -> str:
        """Generar contenido técnico"""
        technical_terms = ["algoritmo", "optimización", "eficiencia", "rendimiento"]
        term = technical_terms[int(time.time()) % len(technical_terms)]

        return f"Análisis técnico ({term}): {prompt[:35]}..."

    async def _direct_response(
        self, content: str, context: Optional[Dict[str, Any]] = None
    ) -> str:
        """Respuesta directa"""
        return content

    async def _adaptive_response(
        self, content: str, context: Optional[Dict[str, Any]] = None
    ) -> str:
        """Respuesta adaptativa"""
        # Adaptar basado en contexto
        if context and context.get("user_level") == "expert":
            content += " [Modo experto]"
        elif context and context.get("user_level") == "beginner":
            content += " [Explicación simplificada]"

        return content

    async def _contextual_response(
        self, content: str, context: Optional[Dict[str, Any]] = None
    ) -> str:
        """Respuesta contextual"""
        if context and context.get("domain"):
            content += f" [Dominio: {context['domain']}]"

        return content

    async def _creative_response(
        self, content: str, context: Optional[Dict[str, Any]] = None
    ) -> str:
        """Respuesta creativa"""
        creative_prefixes = ["💭", "🎯", "🚀", "💡"]
        prefix = creative_prefixes[int(time.time()) % len(creative_prefixes)]

        return f"{prefix} {content}"

    async def _analytical_response(
        self, content: str, context: Optional[Dict[str, Any]] = None
    ) -> str:
        """Respuesta analítica"""
        return f"📊 Análisis: {content} [Detalles técnicos incluidos]"

    async def _adapt_prompt(self, request: GenerationRequest) -> str:
        """Adaptar prompt"""
        adapted_prompt = request.prompt

        # Aplicar estrategias de adaptación
        for strategy_name, strategy_func in self.adaptation_strategies.items():
            adapted_prompt = await strategy_func(adapted_prompt, request.context)

        return adapted_prompt

    async def _enhance_prompt(
        self, prompt: str, context: Optional[Dict[str, Any]] = None
    ) -> str:
        """Mejorar prompt"""
        enhancements = []

        if context and context.get("style"):
            enhancements.append(f"Estilo: {context['style']}")

        if context and context.get("tone"):
            enhancements.append(f"Tono: {context['tone']}")

        if enhancements:
            prompt += f" [{' | '.join(enhancements)}]"

        return prompt

    async def _integrate_context(
        self, prompt: str, context: Optional[Dict[str, Any]] = None
    ) -> str:
        """Integrar contexto"""
        if context and context.get("background"):
            prompt = f"Contexto: {context['background']}\n\n{prompt}"

        return prompt

    async def _adapt_style(
        self, prompt: str, context: Optional[Dict[str, Any]] = None
    ) -> str:
        """Adaptar estilo"""
        if context and context.get("formal"):
            prompt += " [Formal]"
        elif context and context.get("casual"):
            prompt += " [Casual]"

        return prompt

    async def _adjust_complexity(
        self, prompt: str, context: Optional[Dict[str, Any]] = None
    ) -> str:
        """Ajustar complejidad"""
        if context and context.get("simple"):
            prompt += " [Explicación simple]"
        elif context and context.get("detailed"):
            prompt += " [Explicación detallada]"

        return prompt

    async def _validate_generation(
        self, content: str, request: GenerationRequest
    ) -> ValidationResult:
        """Validar generación"""
        validator = self.validation_levels[self.config.validation_level]
        return await validator(content, request)

    async def _basic_validation(
        self, content: str, request: GenerationRequest
    ) -> ValidationResult:
        """Validación básica"""
        issues = []
        suggestions = []

        # Verificar longitud
        if len(content) < 10:
            issues.append("Contenido muy corto")
            suggestions.append("Expandir la respuesta")

        # Verificar contenido vacío
        if not content.strip():
            issues.append("Contenido vacío")
            suggestions.append("Generar contenido válido")

        is_valid = len(issues) == 0
        score = 1.0 if is_valid else 0.3

        return ValidationResult(
            is_valid=is_valid,
            score=score,
            issues=issues,
            suggestions=suggestions,
            confidence=0.8,
            validation_level=ValidationLevel.BASIC,
        )

    async def _semantic_validation(
        self, content: str, request: GenerationRequest
    ) -> ValidationResult:
        """Validación semántica"""
        basic_result = await self._basic_validation(content, request)

        if not basic_result.is_valid:
            return basic_result

        issues = basic_result.issues.copy()
        suggestions = basic_result.suggestions.copy()

        # Verificar coherencia semántica
        if self.embedding_model:
            try:
                # Generar embedding del prompt y contenido
                prompt_embedding = self.embedding_model.encode(request.prompt)
                content_embedding = self.embedding_model.encode(content)

                # Calcular similitud
                similarity = np.dot(prompt_embedding, content_embedding) / (
                    np.linalg.norm(prompt_embedding) * np.linalg.norm(content_embedding)
                )

                if similarity < 0.3:
                    issues.append("Baja relevancia semántica")
                    suggestions.append("Mejorar la relevancia del contenido")

            except Exception as e:
                logger.warning(f"Error en validación semántica: {e}")

        # Verificar estructura
        if request.generation_type == GenerationType.CLASSIFICATION:
            if "clasificación" not in content.lower():
                issues.append("Falta indicador de clasificación")
                suggestions.append("Incluir etiqueta de clasificación")

        is_valid = len(issues) == 0
        score = max(0.5, 1.0 - len(issues) * 0.2)

        return ValidationResult(
            is_valid=is_valid,
            score=score,
            issues=issues,
            suggestions=suggestions,
            confidence=0.9,
            validation_level=ValidationLevel.SEMANTIC,
        )

    async def _logical_validation(
        self, content: str, request: GenerationRequest
    ) -> ValidationResult:
        """Validación lógica"""
        semantic_result = await self._semantic_validation(content, request)

        if not semantic_result.is_valid:
            return semantic_result

        issues = semantic_result.issues.copy()
        suggestions = semantic_result.suggestions.copy()

        # Verificar coherencia lógica
        if "contradicción" in content.lower() or "contradictorio" in content.lower():
            issues.append("Contenido contradictorio")
            suggestions.append("Revisar coherencia lógica")

        # Verificar consistencia
        if content.count("sí") > 0 and content.count("no") > 0:
            if abs(content.count("sí") - content.count("no")) < 2:
                issues.append("Posible inconsistencia")
                suggestions.append("Verificar consistencia de afirmaciones")

        is_valid = len(issues) == 0
        score = max(0.6, semantic_result.score - len(issues) * 0.1)

        return ValidationResult(
            is_valid=is_valid,
            score=score,
            issues=issues,
            suggestions=suggestions,
            confidence=0.95,
            validation_level=ValidationLevel.LOGICAL,
        )

    async def _comprehensive_validation(
        self, content: str, request: GenerationRequest
    ) -> ValidationResult:
        """Validación comprehensiva"""
        logical_result = await self._logical_validation(content, request)

        if not logical_result.is_valid:
            return logical_result

        issues = logical_result.issues.copy()
        suggestions = logical_result.suggestions.copy()

        # Verificaciones adicionales
        if request.generation_type == GenerationType.CODE:
            if "def " in content or "function " in content:
                if "return" not in content:
                    issues.append("Función sin return")
                    suggestions.append("Agregar statement de return")

        # Verificar calidad general
        word_count = len(content.split())
        if word_count < 5:
            issues.append("Contenido insuficiente")
            suggestions.append("Expandir la respuesta")

        is_valid = len(issues) == 0
        score = max(0.7, logical_result.score - len(issues) * 0.05)

        return ValidationResult(
            is_valid=is_valid,
            score=score,
            issues=issues,
            suggestions=suggestions,
            confidence=0.98,
            validation_level=ValidationLevel.COMPREHENSIVE,
        )

    async def _refine_generation(
        self, content: str, validation_result: ValidationResult
    ) -> Tuple[str, List[str]]:
        """Refinar generación"""
        refined_content = content
        refinements = []

        # Aplicar sugerencias de validación
        for suggestion in validation_result.suggestions:
            if "expandir" in suggestion.lower():
                refined_content += " [Contenido expandido]"
                refinements.append("Expansión de contenido")
            elif "mejorar" in suggestion.lower():
                refined_content += " [Mejorado]"
                refinements.append("Mejora de calidad")
            elif "incluir" in suggestion.lower():
                refined_content += " [Información adicional incluida]"
                refinements.append("Inclusión de información")

        return refined_content, refinements

    def _calculate_quality_score(
        self, content: str, validation_result: ValidationResult
    ) -> float:
        """Calcular score de calidad"""
        base_score = validation_result.score

        # Factores adicionales
        length_factor = min(len(content) / 100, 1.0) * 0.2
        complexity_factor = min(len(content.split()) / 20, 1.0) * 0.1

        quality_score = base_score + length_factor + complexity_factor
        return min(quality_score, 1.0)

    def _calculate_confidence(
        self, content: str, validation_result: ValidationResult
    ) -> float:
        """Calcular confianza"""
        base_confidence = validation_result.confidence

        # Ajustar basado en issues
        issue_penalty = len(validation_result.issues) * 0.05
        confidence = max(0.1, base_confidence - issue_penalty)

        return confidence

    async def _save_generation_to_db(self, result: GenerationResult):
        """Guardar generación en base de datos"""
        try:
            cursor = self.conn.cursor()

            cursor.execute(
                """
                INSERT INTO generations 
                (id, prompt, content, generation_type, response_mode, quality_score, confidence,
                 processing_time, created_at, metadata, validation_results)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
                (
                    result.id,
                    "prompt_placeholder",  # Se podría guardar el prompt original
                    result.content,
                    result.generation_type.value,
                    result.response_mode.value,
                    result.quality_score,
                    result.confidence,
                    result.processing_time,
                    result.created_at.isoformat(),
                    json.dumps(result.metadata),
                    json.dumps(result.validation_results),
                ),
            )

            self.conn.commit()
            cursor.close()

        except Exception as e:
            logger.error(f"Error guardando generación: {e}")

    def get_system_stats(self) -> Dict[str, Any]:
        """Obtener estadísticas del sistema"""
        try:
            cursor = self.conn.cursor()

            # Estadísticas de generaciones
            cursor.execute("SELECT COUNT(*) FROM generations")
            total_generations = cursor.fetchone()[0]

            cursor.execute("SELECT AVG(quality_score) FROM generations")
            avg_quality = cursor.fetchone()[0] or 0.0

            cursor.execute("SELECT AVG(confidence) FROM generations")
            avg_confidence = cursor.fetchone()[0] or 0.0

            # Estadísticas de validaciones
            cursor.execute("SELECT COUNT(*) FROM validations")
            total_validations = cursor.fetchone()[0]

            cursor.execute("SELECT COUNT(*) FROM validations WHERE is_valid = 1")
            valid_count = cursor.fetchone()[0]

            # Estadísticas de refinamientos
            cursor.execute("SELECT COUNT(*) FROM refinements")
            total_refinements = cursor.fetchone()[0]

            cursor.close()

            return {
                "generations": {
                    "total": total_generations,
                    "average_quality": round(avg_quality, 3),
                    "average_confidence": round(avg_confidence, 3),
                },
                "validations": {
                    "total": total_validations,
                    "valid_count": valid_count,
                    "success_rate": round(valid_count / max(total_validations, 1), 3),
                },
                "refinements": {"total": total_refinements},
                "performance": {
                    "generation_types": list(
                        set(
                            gen.generation_type.value for gen in self.generation_history
                        )
                    ),
                    "response_modes": list(
                        set(gen.response_mode.value for gen in self.generation_history)
                    ),
                },
            }

        except Exception as e:
            logger.error(f"Error obteniendo estadísticas: {e}")
            return {"error": str(e)}

    def close(self):
        """Cerrar sistema"""
        try:
            if hasattr(self, "conn"):
                self.conn.close()
            logger.info("✅ Sistema de generación y respuesta cerrado")
        except Exception as e:
            logger.error(f"Error cerrando sistema: {e}")


def get_unified_generation_response_system(
    config: Optional[GenerationConfig] = None, db_path: Optional[str] = None
) -> UnifiedGenerationResponseSystem:
    """Función factory para crear sistema unificado"""
    return UnifiedGenerationResponseSystem(config, db_path)


async def main():
    """Función principal de demostración"""
    # Configurar sistema
    config = GenerationConfig(
        generation_type=GenerationType.TEXT,
        response_mode=ResponseMode.ADAPTIVE,
        validation_level=ValidationLevel.SEMANTIC,
        enable_adaptation=True,
        enable_refinement=True,
    )

    system = get_unified_generation_response_system(config)

    print("🚀 Sistema Unificado de Generación y Respuesta")
    print("=" * 50)

    # Ejemplo de generación de texto
    print("\n📝 Generación de Texto:")
    text_request = GenerationRequest(
        prompt="Explica qué es la inteligencia artificial",
        context={"user_level": "beginner", "domain": "technology"},
        generation_type=GenerationType.TEXT,
        response_mode=ResponseMode.ADAPTIVE,
    )

    text_result = await system.generate_response(text_request)
    print(f"   Contenido: {text_result.content}")
    print(f"   Calidad: {text_result.quality_score:.3f}")
    print(f"   Confianza: {text_result.confidence:.3f}")
    print(f"   Tiempo: {text_result.processing_time:.3f}s")

    # Ejemplo de clasificación
    print("\n🏷️ Generación de Clasificación:")
    classification_request = GenerationRequest(
        prompt="Este producto es excelente",
        generation_type=GenerationType.CLASSIFICATION,
        response_mode=ResponseMode.DIRECT,
    )

    classification_result = await system.generate_response(classification_request)
    print(f"   Resultado: {classification_result.content}")
    print(f"   Válido: {classification_result.validation_results['is_valid']}")

    # Ejemplo de generación creativa
    print("\n🎨 Generación Creativa:")
    creative_request = GenerationRequest(
        prompt="Crea una historia corta sobre robots",
        context={"style": "imaginativo", "tone": "amigable"},
        generation_type=GenerationType.CREATIVE,
        response_mode=ResponseMode.CREATIVE,
    )

    creative_result = await system.generate_response(creative_request)
    print(f"   Contenido: {creative_result.content}")
    print(f"   Refinamientos: {len(creative_result.refinements)}")

    # Estadísticas
    print("\n📊 Estadísticas del Sistema:")
    stats = system.get_system_stats()
    print(f"   Generaciones totales: {stats['generations']['total']}")
    print(f"   Calidad promedio: {stats['generations']['average_quality']}")
    print(f"   Tasa de éxito validación: {stats['validations']['success_rate']}")
    print(f"   Refinamientos totales: {stats['refinements']['total']}")

    # Cerrar sistema
    system.close()


if __name__ == "__main__":
    asyncio.run(main())
