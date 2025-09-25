"""
Sistema Unificado de Conciencia y Memoria para NeuroFusion

Este módulo combina funcionalidades de:
- Consciousness Manager (consciousness_manager.py)
- Consciousness System (consciousness_system.py)
- Advanced Episodic Memory (advanced_episodic_memory.py)
- Episodic Memory System (episodic_memory_system.py)
- Advanced Contextual Reasoning (advanced_contextual_reasoning.py)
- Advanced Reasoning System (advanced_reasoning_system.py)
- Advanced Reasoning Capabilities (advanced_reasoning_capabilities.py)
- Neural Plasticity Manager (neural_plasticity_manager.py)
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

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class ConsciousnessLevel(Enum):
    """Niveles de conciencia"""

    BASIC = "basic"
    AWARE = "aware"
    SELF_AWARE = "self_aware"
    REFLECTIVE = "reflective"
    CREATIVE = "creative"


class MemoryType(Enum):
    """Tipos de memoria"""

    EPISODIC = "episodic"
    SEMANTIC = "semantic"
    WORKING = "working"
    EMOTIONAL = "emotional"
    PROCEDURAL = "procedural"


class ReasoningMode(Enum):
    """Modos de razonamiento"""

    LOGICAL = "logical"
    CREATIVE = "creative"
    ANALYTICAL = "analytical"
    INTUITIVE = "intuitive"
    CONTEXTUAL = "contextual"


@dataclass
class ConsciousnessConfig:
    """Configuración del sistema de conciencia"""

    consciousness_level: ConsciousnessLevel = ConsciousnessLevel.AWARE
    memory_capacity: int = 10000
    working_memory_size: int = 100
    episodic_memory_retention: float = 0.8
    semantic_memory_consolidation: float = 0.6
    reasoning_depth: int = 3
    reflection_enabled: bool = True
    creativity_enabled: bool = True
    emotional_awareness: bool = True


@dataclass
class MemoryItem:
    """Elemento de memoria"""

    id: str
    content: str
    memory_type: MemoryType
    consciousness_level: ConsciousnessLevel
    emotional_valence: float
    importance_score: float
    created_at: datetime
    last_accessed: datetime
    access_count: int = 0
    associations: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)
    embedding: Optional[np.ndarray] = None


@dataclass
class Thought:
    """Pensamiento consciente"""

    id: str
    content: str
    reasoning_mode: ReasoningMode
    consciousness_level: ConsciousnessLevel
    context: Dict[str, Any]
    timestamp: datetime
    duration: float = 0.0
    complexity: float = 0.0
    creativity_score: float = 0.0
    emotional_impact: float = 0.0


@dataclass
class ConsciousnessState:
    """Estado de conciencia"""

    level: ConsciousnessLevel
    awareness_score: float
    attention_focus: str
    emotional_state: Dict[str, float]
    cognitive_load: float
    creativity_level: float
    timestamp: datetime
    metadata: Dict[str, Any] = field(default_factory=dict)


class UnifiedConsciousnessMemorySystem:
    """Sistema unificado de conciencia y memoria"""

    def __init__(
        self,
        config: Optional[ConsciousnessConfig] = None,
        db_path: Optional[str] = None,
    ):
        """Inicializar sistema unificado"""
        self.config = config or ConsciousnessConfig()
        self.db_path = db_path or "./data/consciousness_memory_system.db"

        # Componentes del sistema
        self.memories: Dict[str, MemoryItem] = {}
        self.working_memory: deque = deque(maxlen=self.config.working_memory_size)
        self.thoughts: List[Thought] = []
        self.consciousness_history: List[ConsciousnessState] = []
        self.associations: Dict[str, List[str]] = defaultdict(list)

        # Estado actual
        self.current_state = ConsciousnessState(
            level=self.config.consciousness_level,
            awareness_score=0.5,
            attention_focus="general",
            emotional_state={"neutral": 0.5},
            cognitive_load=0.3,
            creativity_level=0.4,
            timestamp=datetime.now(),
        )

        # Inicializar componentes
        self._init_database()
        self._init_consciousness_components()
        self._init_memory_components()
        self._init_reasoning_components()

        logger.info("✅ Sistema Unificado de Conciencia y Memoria inicializado")

    def _init_database(self):
        """Inicializar base de datos"""
        try:
            # Crear directorio si no existe
            Path(self.db_path).parent.mkdir(parents=True, exist_ok=True)
            self.conn = sqlite3.connect(self.db_path)
            self._create_tables()
            logger.info("✅ Base de datos de conciencia y memoria inicializada")
        except Exception as e:
            logger.error(f"Error inicializando base de datos: {e}")
            raise

    def _create_tables(self):
        """Crear tablas en base de datos"""
        cursor = self.conn.cursor()

        # Tabla de memorias
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS memories (
                id TEXT PRIMARY KEY,
                content TEXT NOT NULL,
                memory_type TEXT NOT NULL,
                consciousness_level TEXT NOT NULL,
                emotional_valence REAL NOT NULL,
                importance_score REAL NOT NULL,
                created_at TEXT NOT NULL,
                last_accessed TEXT NOT NULL,
                access_count INTEGER DEFAULT 0,
                associations TEXT,
                metadata TEXT,
                embedding BLOB
            )
        """
        )

        # Tabla de pensamientos
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS thoughts (
                id TEXT PRIMARY KEY,
                content TEXT NOT NULL,
                reasoning_mode TEXT NOT NULL,
                consciousness_level TEXT NOT NULL,
                context TEXT NOT NULL,
                timestamp TEXT NOT NULL,
                duration REAL DEFAULT 0.0,
                complexity REAL DEFAULT 0.0,
                creativity_score REAL DEFAULT 0.0,
                emotional_impact REAL DEFAULT 0.0
            )
        """
        )

        # Tabla de estados de conciencia
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS consciousness_states (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                level TEXT NOT NULL,
                awareness_score REAL NOT NULL,
                attention_focus TEXT NOT NULL,
                emotional_state TEXT NOT NULL,
                cognitive_load REAL NOT NULL,
                creativity_level REAL NOT NULL,
                timestamp TEXT NOT NULL,
                metadata TEXT
            )
        """
        )

        # Tabla de asociaciones
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS memory_associations (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                memory_id TEXT NOT NULL,
                associated_memory_id TEXT NOT NULL,
                association_strength REAL NOT NULL,
                created_at TEXT NOT NULL,
                FOREIGN KEY (memory_id) REFERENCES memories (id),
                FOREIGN KEY (associated_memory_id) REFERENCES memories (id)
            )
        """
        )

        # Índices
        cursor.execute(
            "CREATE INDEX IF NOT EXISTS idx_memory_type ON memories(memory_type)"
        )
        cursor.execute(
            "CREATE INDEX IF NOT EXISTS idx_consciousness_level ON memories(consciousness_level)"
        )
        cursor.execute(
            "CREATE INDEX IF NOT EXISTS idx_importance_score ON memories(importance_score)"
        )
        cursor.execute(
            "CREATE INDEX IF NOT EXISTS idx_thoughts_timestamp ON thoughts(timestamp)"
        )
        cursor.execute(
            "CREATE INDEX IF NOT EXISTS idx_consciousness_timestamp ON consciousness_states(timestamp)"
        )

        self.conn.commit()
        cursor.close()

    def _init_consciousness_components(self):
        """Inicializar componentes de conciencia"""
        self.consciousness_levels = {
            ConsciousnessLevel.BASIC: self._basic_consciousness,
            ConsciousnessLevel.AWARE: self._aware_consciousness,
            ConsciousnessLevel.SELF_AWARE: self._self_aware_consciousness,
            ConsciousnessLevel.REFLECTIVE: self._reflective_consciousness,
            ConsciousnessLevel.CREATIVE: self._creative_consciousness,
        }

        self.awareness_factors = {
            "attention": 0.3,
            "memory": 0.25,
            "reasoning": 0.25,
            "emotion": 0.2,
        }

    def _init_memory_components(self):
        """Inicializar componentes de memoria"""
        self.memory_types = {
            MemoryType.EPISODIC: self._process_episodic_memory,
            MemoryType.SEMANTIC: self._process_semantic_memory,
            MemoryType.WORKING: self._process_working_memory,
            MemoryType.EMOTIONAL: self._process_emotional_memory,
            MemoryType.PROCEDURAL: self._process_procedural_memory,
        }

        # Inicializar modelo de embeddings para memoria semántica
        try:
            self.embedding_model = SentenceTransformer(
                "paraphrase-multilingual-MiniLM-L12-v2"
            )
        except Exception as e:
            logger.warning(f"No se pudo cargar modelo de embeddings: {e}")
            self.embedding_model = None

    def _init_reasoning_components(self):
        """Inicializar componentes de razonamiento"""
        self.reasoning_modes = {
            ReasoningMode.LOGICAL: self._logical_reasoning,
            ReasoningMode.CREATIVE: self._creative_reasoning,
            ReasoningMode.ANALYTICAL: self._analytical_reasoning,
            ReasoningMode.INTUITIVE: self._intuitive_reasoning,
            ReasoningMode.CONTEXTUAL: self._contextual_reasoning,
        }

    def _logical_reasoning(
        self, input_text: str, context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Razonamiento lógico"""
        return {
            "mode": "logical",
            "confidence": 0.8,
            "conclusions": ["conclusión lógica"],
        }

    def _creative_reasoning(
        self, input_text: str, context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Razonamiento creativo"""
        return {"mode": "creative", "confidence": 0.6, "ideas": ["idea creativa"]}

    def _analytical_reasoning(
        self, input_text: str, context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Razonamiento analítico"""
        return {
            "mode": "analytical",
            "confidence": 0.9,
            "analysis": ["análisis detallado"],
        }

    def _intuitive_reasoning(
        self, input_text: str, context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Razonamiento intuitivo"""
        return {
            "mode": "intuitive",
            "confidence": 0.7,
            "insights": ["insight intuitivo"],
        }

    def _contextual_reasoning(
        self, input_text: str, context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Razonamiento contextual"""
        return {
            "mode": "contextual",
            "confidence": 0.75,
            "context_analysis": ["análisis contextual"],
        }

    async def process_input(
        self, input_text: str, context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Procesar entrada con conciencia y memoria"""
        start_time = time.time()

        try:
            # Actualizar estado de conciencia
            await self._update_consciousness_state(input_text, context)

            # Procesar con el nivel de conciencia actual
            consciousness_processor = self.consciousness_levels[
                self.current_state.level
            ]
            consciousness_result = await consciousness_processor(input_text, context)

            # Almacenar en memoria
            memory_result = await self._store_memory(input_text, consciousness_result)

            # Generar pensamiento
            thought_result = await self._generate_thought(
                input_text, consciousness_result, context
            )

            # Razonamiento contextual
            reasoning_result = await self._contextual_reasoning(input_text, context)

            processing_time = time.time() - start_time

            return {
                "consciousness_level": self.current_state.level.value,
                "awareness_score": self.current_state.awareness_score,
                "memory_stored": memory_result["stored"],
                "thought_generated": thought_result["generated"],
                "reasoning_result": reasoning_result,
                "processing_time": processing_time,
                "emotional_state": self.current_state.emotional_state,
                "cognitive_load": self.current_state.cognitive_load,
            }

        except Exception as e:
            logger.error(f"Error procesando entrada: {e}")
            return {
                "error": str(e),
                "consciousness_level": self.current_state.level.value,
            }

    async def _basic_consciousness(
        self, input_text: str, context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Conciencia básica - procesamiento simple"""
        # Análisis básico del input
        word_count = len(input_text.split())
        complexity = min(word_count / 50, 1.0)

        # Detectar emociones básicas
        emotional_analysis = self._analyze_emotions_basic(input_text)

        return {
            "processing_level": "basic",
            "complexity": complexity,
            "emotional_analysis": emotional_analysis,
            "attention_required": complexity > 0.5,
        }

    async def _aware_consciousness(
        self, input_text: str, context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Conciencia consciente - procesamiento con atención"""
        # Análisis más profundo
        semantic_analysis = self._analyze_semantics(input_text)
        emotional_analysis = self._analyze_emotions_advanced(input_text)

        # Determinar atención requerida
        attention_score = self._calculate_attention_score(input_text, semantic_analysis)

        return {
            "processing_level": "aware",
            "semantic_analysis": semantic_analysis,
            "emotional_analysis": emotional_analysis,
            "attention_score": attention_score,
            "requires_deep_processing": attention_score > 0.7,
        }

    async def _self_aware_consciousness(
        self, input_text: str, context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Conciencia auto-consciente - procesamiento reflexivo"""
        # Análisis reflexivo
        self_reflection = self._generate_self_reflection(input_text, context)
        meta_cognition = self._analyze_meta_cognition(input_text)

        # Actualizar autoconcepto
        self._update_self_concept(input_text, self_reflection)

        return {
            "processing_level": "self_aware",
            "self_reflection": self_reflection,
            "meta_cognition": meta_cognition,
            "self_concept_updated": True,
        }

    def _generate_self_reflection(
        self, input_text: str, context: Optional[Dict[str, Any]] = None
    ) -> str:
        """Generar reflexión sobre sí mismo"""
        return f"Reflexionando sobre: {input_text[:30]}... (autoconciencia activa)"

    def _analyze_meta_cognition(self, input_text: str) -> Dict[str, Any]:
        """Analizar metacognición"""
        return {
            "awareness_level": 0.8,
            "self_monitoring": True,
            "cognitive_control": 0.7,
        }

    def _update_self_concept(self, input_text: str, self_reflection: str):
        """Actualizar autoconcepto"""
        # Simular actualización del autoconcepto
        pass

    async def _reflective_consciousness(
        self, input_text: str, context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Conciencia reflexiva - procesamiento profundo"""
        # Reflexión profunda
        deep_analysis = self._deep_reflection(input_text, context)
        pattern_recognition = self._recognize_patterns(input_text)

        # Generar insights
        insights = self._generate_insights(
            input_text, deep_analysis, pattern_recognition
        )

        return {
            "processing_level": "reflective",
            "deep_analysis": deep_analysis,
            "pattern_recognition": pattern_recognition,
            "insights": insights,
        }

    def _deep_reflection(
        self, input_text: str, context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Reflexión profunda"""
        return {"depth": 0.9, "complexity": 0.8, "insights_count": 3}

    def _recognize_patterns(self, input_text: str) -> List[str]:
        """Reconocer patrones en el texto"""
        patterns = []

        # Patrones básicos
        if "?" in input_text:
            patterns.append("pregunta")
        if "!" in input_text:
            patterns.append("exclamación")
        if len(input_text.split()) > 20:
            patterns.append("texto_largo")

        return patterns

    def _generate_insights(
        self,
        input_text: str,
        deep_analysis: Dict[str, Any],
        pattern_recognition: List[str],
    ) -> List[str]:
        """Generar insights basados en análisis profundo"""
        insights = []

        if deep_analysis.get("depth", 0) > 0.7:
            insights.append("Análisis profundo realizado")

        if pattern_recognition:
            insights.append(f"Patrones detectados: {', '.join(pattern_recognition)}")

        return insights

    async def _creative_consciousness(
        self, input_text: str, context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Conciencia creativa - procesamiento innovador"""
        # Pensamiento creativo
        creative_analysis = self._creative_thinking(input_text, context)
        innovation_potential = self._assess_innovation_potential(input_text)

        # Generar ideas creativas
        creative_ideas = self._generate_creative_ideas(input_text, creative_analysis)

        return {
            "processing_level": "creative",
            "creative_analysis": creative_analysis,
            "innovation_potential": innovation_potential,
            "creative_ideas": creative_ideas,
        }

    def _creative_thinking(
        self, input_text: str, context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Pensamiento creativo"""
        return {"creativity_level": 0.8, "originality": 0.7, "flexibility": 0.6}

    def _assess_innovation_potential(self, input_text: str) -> float:
        """Evaluar potencial de innovación"""
        innovation_indicators = ["nuevo", "innovador", "creativo", "original", "único"]
        indicator_count = sum(
            1 for indicator in innovation_indicators if indicator in input_text.lower()
        )
        return min(indicator_count * 0.2, 1.0)

    def _generate_creative_ideas(
        self, input_text: str, creative_analysis: Dict[str, Any]
    ) -> List[str]:
        """Generar ideas creativas"""
        ideas = []

        if creative_analysis.get("creativity_level", 0) > 0.6:
            ideas.append("Idea creativa basada en el input")
            ideas.append("Perspectiva innovadora identificada")

        return ideas

    async def _store_memory(
        self, content: str, consciousness_result: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Almacenar en memoria"""
        try:
            # Determinar tipo de memoria
            memory_type = self._determine_memory_type(content, consciousness_result)

            # Calcular importancia
            importance_score = self._calculate_importance(content, consciousness_result)

            # Calcular valencia emocional
            emotional_valence = self._calculate_emotional_valence(content)

            # Crear elemento de memoria
            memory_id = f"mem_{int(time.time() * 1000)}"
            memory_item = MemoryItem(
                id=memory_id,
                content=content,
                memory_type=memory_type,
                consciousness_level=self.current_state.level,
                emotional_valence=emotional_valence,
                importance_score=importance_score,
                created_at=datetime.now(),
                last_accessed=datetime.now(),
                metadata=consciousness_result,
            )

            # Procesar según tipo
            processor = self.memory_types[memory_type]
            processing_result = await processor(memory_item)

            # Guardar en base de datos
            await self._save_memory_to_db(memory_item)

            # Agregar a memoria de trabajo si es importante
            if importance_score > 0.7:
                self.working_memory.append(memory_item)

            # Almacenar en memoria principal
            self.memories[memory_id] = memory_item

            return {
                "stored": True,
                "memory_id": memory_id,
                "memory_type": memory_type.value,
                "importance_score": importance_score,
                "processing_result": processing_result,
            }

        except Exception as e:
            logger.error(f"Error almacenando memoria: {e}")
            return {"stored": False, "error": str(e)}

    async def _generate_thought(
        self,
        input_text: str,
        consciousness_result: Dict[str, Any],
        context: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """Generar pensamiento consciente"""
        try:
            # Determinar modo de razonamiento
            reasoning_mode = self._determine_reasoning_mode(
                input_text, consciousness_result
            )

            # Generar contenido del pensamiento
            thought_content = self._generate_thought_content(
                input_text, consciousness_result, reasoning_mode
            )

            # Calcular métricas
            complexity = self._calculate_thought_complexity(thought_content)
            creativity_score = self._calculate_creativity_score(thought_content)
            emotional_impact = self._calculate_emotional_impact(thought_content)

            # Crear pensamiento
            thought_id = f"thought_{int(time.time() * 1000)}"
            thought = Thought(
                id=thought_id,
                content=thought_content,
                reasoning_mode=reasoning_mode,
                consciousness_level=self.current_state.level,
                context=context or {},
                timestamp=datetime.now(),
                complexity=complexity,
                creativity_score=creativity_score,
                emotional_impact=emotional_impact,
            )

            # Guardar pensamiento
            await self._save_thought_to_db(thought)
            self.thoughts.append(thought)

            return {
                "generated": True,
                "thought_id": thought_id,
                "reasoning_mode": reasoning_mode.value,
                "complexity": complexity,
                "creativity_score": creativity_score,
            }

        except Exception as e:
            logger.error(f"Error generando pensamiento: {e}")
            return {"generated": False, "error": str(e)}

    def _determine_reasoning_mode(
        self, input_text: str, consciousness_result: Dict[str, Any]
    ) -> ReasoningMode:
        """Determinar modo de razonamiento"""
        if consciousness_result.get("processing_level") in ["reflective", "creative"]:
            return ReasoningMode.CREATIVE
        elif consciousness_result.get("attention_score", 0) > 0.7:
            return ReasoningMode.ANALYTICAL
        else:
            return ReasoningMode.LOGICAL

    def _generate_thought_content(
        self,
        input_text: str,
        consciousness_result: Dict[str, Any],
        reasoning_mode: ReasoningMode,
    ) -> str:
        """Generar contenido del pensamiento"""
        base_content = f"Pensamiento sobre: {input_text[:50]}..."

        if reasoning_mode == ReasoningMode.CREATIVE:
            return f"💡 {base_content} (modo creativo)"
        elif reasoning_mode == ReasoningMode.ANALYTICAL:
            return f"🔍 {base_content} (modo analítico)"
        else:
            return f"💭 {base_content} (modo lógico)"

    def _calculate_thought_complexity(self, thought_content: str) -> float:
        """Calcular complejidad del pensamiento"""
        word_count = len(thought_content.split())
        return min(word_count / 20, 1.0)

    def _calculate_creativity_score(self, thought_content: str) -> float:
        """Calcular score de creatividad"""
        creative_indicators = ["💡", "🔍", "💭", "creativo", "innovador", "original"]
        indicator_count = sum(
            1 for indicator in creative_indicators if indicator in thought_content
        )
        return min(indicator_count * 0.2, 1.0)

    def _calculate_emotional_impact(self, thought_content: str) -> float:
        """Calcular impacto emocional"""
        emotional_words = ["feliz", "triste", "emocionado", "preocupado", "sorprendido"]
        emotional_count = sum(1 for word in emotional_words if word in thought_content)
        return min(emotional_count * 0.15, 1.0)

    async def _contextual_reasoning(
        self, input_text: str, context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Razonamiento contextual"""
        try:
            # Buscar memorias relevantes
            relevant_memories = await self._find_relevant_memories(input_text, context)

            # Aplicar razonamiento contextual
            reasoning_result = self._apply_contextual_reasoning(
                input_text, relevant_memories, context
            )

            # Generar conclusiones
            conclusions = self._generate_conclusions(
                reasoning_result, relevant_memories
            )

            return {
                "reasoning_applied": True,
                "relevant_memories_count": len(relevant_memories),
                "reasoning_result": reasoning_result,
                "conclusions": conclusions,
            }

        except Exception as e:
            logger.error(f"Error en razonamiento contextual: {e}")
            return {"reasoning_applied": False, "error": str(e)}

    async def _find_relevant_memories(
        self, input_text: str, context: Optional[Dict[str, Any]] = None
    ) -> List[MemoryItem]:
        """Buscar memorias relevantes"""
        relevant_memories = []

        # Buscar por contenido similar
        for memory in self.memories.values():
            if self._is_memory_relevant(memory, input_text, context):
                relevant_memories.append(memory)

        # Ordenar por importancia y relevancia
        relevant_memories.sort(key=lambda x: x.importance_score, reverse=True)

        return relevant_memories[:10]  # Limitar a 10 memorias más relevantes

    def _is_memory_relevant(
        self,
        memory: MemoryItem,
        input_text: str,
        context: Optional[Dict[str, Any]] = None,
    ) -> bool:
        """Determinar si una memoria es relevante"""
        # Verificar similitud de contenido
        input_words = set(input_text.lower().split())
        memory_words = set(memory.content.lower().split())

        # Calcular overlap de palabras
        overlap = len(input_words.intersection(memory_words))
        relevance_score = overlap / max(len(input_words), 1)

        return relevance_score > 0.1  # Umbral de relevancia

    def _apply_contextual_reasoning(
        self,
        input_text: str,
        relevant_memories: List[MemoryItem],
        context: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """Aplicar razonamiento contextual"""
        if not relevant_memories:
            return {"reasoning": "no_context", "confidence": 0.5}

        # Analizar patrones en las memorias relevantes
        patterns = self._extract_patterns_from_memories(relevant_memories)

        # Generar razonamiento basado en patrones
        reasoning = self._generate_pattern_based_reasoning(
            input_text, patterns, context
        )

        return {
            "reasoning": reasoning,
            "patterns_found": len(patterns),
            "confidence": min(len(relevant_memories) * 0.1, 0.9),
        }

    def _extract_patterns_from_memories(
        self, memories: List[MemoryItem]
    ) -> List[Dict[str, Any]]:
        """Extraer patrones de las memorias"""
        patterns = []

        # Agrupar por tipo de memoria
        memory_types = {}
        for memory in memories:
            if memory.memory_type.value not in memory_types:
                memory_types[memory.memory_type.value] = []
            memory_types[memory.memory_type.value].append(memory)

        # Analizar patrones por tipo
        for memory_type, type_memories in memory_types.items():
            if len(type_memories) > 1:
                pattern = {
                    "type": memory_type,
                    "count": len(type_memories),
                    "avg_importance": sum(m.importance_score for m in type_memories)
                    / len(type_memories),
                    "emotional_trend": self._calculate_emotional_trend(type_memories),
                }
                patterns.append(pattern)

        return patterns

    def _calculate_emotional_trend(self, memories: List[MemoryItem]) -> str:
        """Calcular tendencia emocional"""
        positive_count = sum(1 for m in memories if m.emotional_valence > 0.6)
        negative_count = sum(1 for m in memories if m.emotional_valence < 0.4)

        if positive_count > negative_count:
            return "positive"
        elif negative_count > positive_count:
            return "negative"
        else:
            return "neutral"

    def _generate_pattern_based_reasoning(
        self,
        input_text: str,
        patterns: List[Dict[str, Any]],
        context: Optional[Dict[str, Any]] = None,
    ) -> str:
        """Generar razonamiento basado en patrones"""
        if not patterns:
            return "Sin patrones suficientes para razonamiento contextual"

        # Analizar el patrón más fuerte
        strongest_pattern = max(patterns, key=lambda x: x["count"])

        reasoning = f"Basado en {strongest_pattern['count']} memorias de tipo {strongest_pattern['type']}, "
        reasoning += f"con tendencia emocional {strongest_pattern['emotional_trend']} "
        reasoning += f"y importancia promedio {strongest_pattern['avg_importance']:.2f}"

        return reasoning

    def _generate_conclusions(
        self, reasoning_result: Dict[str, Any], relevant_memories: List[MemoryItem]
    ) -> List[str]:
        """Generar conclusiones del razonamiento"""
        conclusions = []

        if reasoning_result.get("reasoning"):
            conclusions.append(reasoning_result["reasoning"])

        if relevant_memories:
            avg_importance = sum(m.importance_score for m in relevant_memories) / len(
                relevant_memories
            )
            conclusions.append(f"Relevancia promedio: {avg_importance:.2f}")

        return conclusions

    def _analyze_emotions_basic(self, text: str) -> Dict[str, float]:
        """Análisis básico de emociones"""
        emotions = {
            "joy": 0.0,
            "sadness": 0.0,
            "anger": 0.0,
            "fear": 0.0,
            "surprise": 0.0,
        }

        text_lower = text.lower()

        # Palabras clave de emociones
        emotion_keywords = {
            "joy": ["feliz", "alegre", "contento", "disfrutar", "excelente"],
            "sadness": ["triste", "deprimido", "melancólico", "desanimado"],
            "anger": ["enojado", "furioso", "irritado", "molesto"],
            "fear": ["miedo", "asustado", "aterrorizado", "preocupado"],
            "surprise": ["sorprendido", "asombrado", "increíble", "wow"],
        }

        for emotion, keywords in emotion_keywords.items():
            count = sum(1 for keyword in keywords if keyword in text_lower)
            emotions[emotion] = min(count * 0.2, 1.0)

        return emotions

    def _analyze_emotions_advanced(self, text: str) -> Dict[str, float]:
        """Análisis avanzado de emociones"""
        basic_emotions = self._analyze_emotions_basic(text)

        # Análisis de intensidad
        intensity_indicators = ["muy", "extremadamente", "totalmente", "completamente"]
        intensity = (
            sum(1 for indicator in intensity_indicators if indicator in text.lower())
            * 0.1
        )

        # Análisis de contexto
        context_emotions = {
            "curiosity": 0.0,
            "confidence": 0.0,
            "uncertainty": 0.0,
            "enthusiasm": 0.0,
        }

        if "?" in text:
            context_emotions["curiosity"] += 0.3
        if any(word in text.lower() for word in ["sé", "conozco", "entiendo"]):
            context_emotions["confidence"] += 0.4
        if any(word in text.lower() for word in ["tal vez", "quizás", "no sé"]):
            context_emotions["uncertainty"] += 0.4

        return {**basic_emotions, **context_emotions, "intensity": min(intensity, 1.0)}

    def _analyze_semantics(self, text: str) -> Dict[str, Any]:
        """Análisis semántico del texto"""
        return {
            "word_count": len(text.split()),
            "sentence_count": text.count(".") + text.count("!") + text.count("?"),
            "complexity": len(text) / 100,
            "topics": self._extract_topics(text),
            "sentiment": self._analyze_sentiment(text),
        }

    def _extract_topics(self, text: str) -> List[str]:
        """Extraer temas del texto"""
        # Palabras clave por tema
        topic_keywords = {
            "technology": ["computadora", "programa", "tecnología", "software"],
            "science": ["ciencia", "investigación", "experimento", "teoría"],
            "emotions": ["sentir", "emoción", "sentimiento", "estado de ánimo"],
            "learning": ["aprender", "estudiar", "conocimiento", "educación"],
            "creativity": ["crear", "arte", "imaginación", "innovación"],
        }

        text_lower = text.lower()
        topics = []

        for topic, keywords in topic_keywords.items():
            if any(keyword in text_lower for keyword in keywords):
                topics.append(topic)

        return topics

    def _analyze_sentiment(self, text: str) -> float:
        """Análisis de sentimiento"""
        positive_words = ["bueno", "excelente", "genial", "fantástico", "maravilloso"]
        negative_words = ["malo", "terrible", "horrible", "pésimo", "deplorable"]

        text_lower = text.lower()
        positive_count = sum(1 for word in positive_words if word in text_lower)
        negative_count = sum(1 for word in negative_words if word in text_lower)

        if positive_count == 0 and negative_count == 0:
            return 0.5  # Neutral

        return positive_count / (positive_count + negative_count)

    def _calculate_attention_score(
        self, text: str, semantic_analysis: Dict[str, Any]
    ) -> float:
        """Calcular score de atención requerida"""
        attention_factors = {
            "complexity": semantic_analysis["complexity"] * 0.3,
            "word_count": min(semantic_analysis["word_count"] / 50, 1.0) * 0.2,
            "sentiment_intensity": abs(semantic_analysis["sentiment"] - 0.5) * 2 * 0.3,
            "topic_importance": len(semantic_analysis["topics"]) * 0.1,
        }

        return sum(attention_factors.values())

    def _determine_memory_type(
        self, content: str, consciousness_result: Dict[str, Any]
    ) -> MemoryType:
        """Determinar tipo de memoria"""
        if consciousness_result.get("emotional_analysis", {}).get("intensity", 0) > 0.5:
            return MemoryType.EMOTIONAL
        elif consciousness_result.get("processing_level") in ["reflective", "creative"]:
            return MemoryType.SEMANTIC
        elif consciousness_result.get("attention_score", 0) > 0.7:
            return MemoryType.EPISODIC
        else:
            return MemoryType.WORKING

    def _calculate_importance(
        self, content: str, consciousness_result: Dict[str, Any]
    ) -> float:
        """Calcular importancia del contenido"""
        importance_factors = {
            "attention_score": consciousness_result.get("attention_score", 0) * 0.4,
            "emotional_intensity": consciousness_result.get(
                "emotional_analysis", {}
            ).get("intensity", 0)
            * 0.3,
            "complexity": len(content) / 200 * 0.2,
            "processing_level": {
                "basic": 0.2,
                "aware": 0.4,
                "self_aware": 0.6,
                "reflective": 0.8,
                "creative": 0.9,
            }.get(consciousness_result.get("processing_level", "basic"), 0.5)
            * 0.1,
        }

        return sum(importance_factors.values())

    def _calculate_emotional_valence(self, content: str) -> float:
        """Calcular valencia emocional"""
        emotions = self._analyze_emotions_advanced(content)

        # Calcular valencia (positiva vs negativa)
        positive_emotions = emotions.get("joy", 0) + emotions.get("enthusiasm", 0)
        negative_emotions = (
            emotions.get("sadness", 0)
            + emotions.get("anger", 0)
            + emotions.get("fear", 0)
        )

        if positive_emotions == 0 and negative_emotions == 0:
            return 0.5  # Neutral

        return positive_emotions / (positive_emotions + negative_emotions)

    async def _process_episodic_memory(self, memory_item: MemoryItem) -> Dict[str, Any]:
        """Procesar memoria episódica"""
        # Crear asociaciones temporales
        temporal_associations = await self._create_temporal_associations(memory_item)

        # Consolidar memoria
        consolidation_strength = (
            self.config.episodic_memory_retention * memory_item.importance_score
        )

        return {
            "temporal_associations": temporal_associations,
            "consolidation_strength": consolidation_strength,
            "retention_probability": consolidation_strength,
        }

    async def _create_temporal_associations(self, memory_item: MemoryItem) -> List[str]:
        """Crear asociaciones temporales"""
        associations = []

        # Buscar memorias creadas en el mismo período de tiempo
        time_window = timedelta(hours=1)
        for memory in self.memories.values():
            if memory.id != memory_item.id:
                time_diff = abs(
                    (memory.created_at - memory_item.created_at).total_seconds()
                )
                if time_diff <= time_window.total_seconds():
                    associations.append(memory.id)

        return associations[:5]  # Limitar a 5 asociaciones

    async def _process_semantic_memory(self, memory_item: MemoryItem) -> Dict[str, Any]:
        """Procesar memoria semántica"""
        # Generar embedding si está disponible
        if self.embedding_model:
            try:
                embedding = self.embedding_model.encode(memory_item.content)
                memory_item.embedding = embedding
            except Exception as e:
                logger.warning(f"Error generando embedding: {e}")

        # Crear asociaciones semánticas
        semantic_associations = await self._create_semantic_associations(memory_item)

        return {
            "semantic_associations": semantic_associations,
            "embedding_generated": memory_item.embedding is not None,
        }

    async def _create_semantic_associations(self, memory_item: MemoryItem) -> List[str]:
        """Crear asociaciones semánticas"""
        associations = []

        if memory_item.embedding is not None:
            # Buscar memorias con embeddings similares
            for memory in self.memories.values():
                if memory.id != memory_item.id and memory.embedding is not None:
                    similarity = np.dot(memory_item.embedding, memory.embedding) / (
                        np.linalg.norm(memory_item.embedding)
                        * np.linalg.norm(memory.embedding)
                    )
                    if similarity > 0.7:  # Umbral de similitud
                        associations.append(memory.id)

        return associations[:5]  # Limitar a 5 asociaciones

    async def _process_working_memory(self, memory_item: MemoryItem) -> Dict[str, Any]:
        """Procesar memoria de trabajo"""
        # Agregar a memoria de trabajo
        if len(self.working_memory) >= self.config.working_memory_size:
            # Remover elemento menos importante
            least_important = min(self.working_memory, key=lambda x: x.importance_score)
            self.working_memory.remove(least_important)

        self.working_memory.append(memory_item)

        return {
            "added_to_working_memory": True,
            "working_memory_size": len(self.working_memory),
        }

    async def _process_emotional_memory(
        self, memory_item: MemoryItem
    ) -> Dict[str, Any]:
        """Procesar memoria emocional"""
        # Crear asociaciones emocionales
        emotional_associations = await self._create_emotional_associations(memory_item)

        # Actualizar estado emocional
        self._update_emotional_state(memory_item.emotional_valence)

        return {
            "emotional_associations": emotional_associations,
            "emotional_state_updated": True,
        }

    async def _create_emotional_associations(
        self, memory_item: MemoryItem
    ) -> List[str]:
        """Crear asociaciones emocionales"""
        associations = []

        # Buscar memorias con valencia emocional similar
        for memory in self.memories.values():
            if memory.id != memory_item.id:
                emotional_diff = abs(
                    memory.emotional_valence - memory_item.emotional_valence
                )
                if emotional_diff < 0.2:  # Umbral de similitud emocional
                    associations.append(memory.id)

        return associations[:5]  # Limitar a 5 asociaciones

    def _update_emotional_state(self, emotional_valence: float):
        """Actualizar estado emocional"""
        if emotional_valence > 0.7:
            self.current_state.emotional_state["joy"] = 0.8
        elif emotional_valence < 0.3:
            self.current_state.emotional_state["sadness"] = 0.6
        else:
            self.current_state.emotional_state["neutral"] = 0.5

    async def _process_procedural_memory(
        self, memory_item: MemoryItem
    ) -> Dict[str, Any]:
        """Procesar memoria procedimental"""
        # Extraer patrones de acción
        action_patterns = self._extract_action_patterns(memory_item.content)

        return {"action_patterns": action_patterns, "procedural_learning": True}

    def _extract_action_patterns(self, content: str) -> List[str]:
        """Extraer patrones de acción del contenido"""
        action_verbs = [
            "hacer",
            "crear",
            "construir",
            "desarrollar",
            "implementar",
            "ejecutar",
        ]
        patterns = []

        content_lower = content.lower()
        for verb in action_verbs:
            if verb in content_lower:
                patterns.append(f"acción: {verb}")

        return patterns

    async def _update_consciousness_state(
        self, input_text: str, context: Optional[Dict[str, Any]] = None
    ):
        """Actualizar estado de conciencia"""
        # Calcular factores de conciencia
        attention_factor = self._calculate_attention_score(
            input_text, self._analyze_semantics(input_text)
        )
        memory_factor = len(self.working_memory) / self.config.working_memory_size
        reasoning_factor = (
            len(self.thoughts) / 100
        )  # Factor basado en actividad de pensamiento
        emotion_factor = self._calculate_emotional_balance()

        # Calcular score de conciencia
        awareness_score = (
            attention_factor * self.awareness_factors["attention"]
            + memory_factor * self.awareness_factors["memory"]
            + reasoning_factor * self.awareness_factors["reasoning"]
            + emotion_factor * self.awareness_factors["emotion"]
        )

        # Actualizar estado
        self.current_state.awareness_score = min(awareness_score, 1.0)
        self.current_state.cognitive_load = min(attention_factor + memory_factor, 1.0)
        self.current_state.timestamp = datetime.now()

        # Guardar estado
        await self._save_consciousness_state(self.current_state)
        self.consciousness_history.append(self.current_state)

    def _calculate_emotional_balance(self) -> float:
        """Calcular balance emocional"""
        if not self.current_state.emotional_state:
            return 0.5

        positive_emotions = sum(
            score
            for emotion, score in self.current_state.emotional_state.items()
            if emotion in ["joy", "enthusiasm", "confidence"]
        )
        negative_emotions = sum(
            score
            for emotion, score in self.current_state.emotional_state.items()
            if emotion in ["sadness", "anger", "fear"]
        )

        total_emotions = positive_emotions + negative_emotions
        if total_emotions == 0:
            return 0.5

        return positive_emotions / total_emotions

    async def _save_memory_to_db(self, memory_item: MemoryItem):
        """Guardar memoria en base de datos"""
        try:
            cursor = self.conn.cursor()

            cursor.execute(
                """
                INSERT INTO memories 
                (id, content, memory_type, consciousness_level, emotional_valence, importance_score,
                 created_at, last_accessed, access_count, associations, metadata, embedding)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
                (
                    memory_item.id,
                    memory_item.content,
                    memory_item.memory_type.value,
                    memory_item.consciousness_level.value,
                    memory_item.emotional_valence,
                    memory_item.importance_score,
                    memory_item.created_at.isoformat(),
                    memory_item.last_accessed.isoformat(),
                    memory_item.access_count,
                    json.dumps(memory_item.associations),
                    json.dumps(memory_item.metadata),
                    (
                        memory_item.embedding.tobytes()
                        if memory_item.embedding is not None
                        else None
                    ),
                ),
            )

            self.conn.commit()
            cursor.close()

        except Exception as e:
            logger.error(f"Error guardando memoria: {e}")

    async def _save_thought_to_db(self, thought: Thought):
        """Guardar pensamiento en base de datos"""
        try:
            cursor = self.conn.cursor()

            cursor.execute(
                """
                INSERT INTO thoughts 
                (id, content, reasoning_mode, consciousness_level, context, timestamp,
                 duration, complexity, creativity_score, emotional_impact)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
                (
                    thought.id,
                    thought.content,
                    thought.reasoning_mode.value,
                    thought.consciousness_level.value,
                    json.dumps(thought.context),
                    thought.timestamp.isoformat(),
                    thought.duration,
                    thought.complexity,
                    thought.creativity_score,
                    thought.emotional_impact,
                ),
            )

            self.conn.commit()
            cursor.close()

        except Exception as e:
            logger.error(f"Error guardando pensamiento: {e}")

    async def _save_consciousness_state(self, state: ConsciousnessState):
        """Guardar estado de conciencia en base de datos"""
        try:
            cursor = self.conn.cursor()

            cursor.execute(
                """
                INSERT INTO consciousness_states 
                (level, awareness_score, attention_focus, emotional_state, cognitive_load,
                 creativity_level, timestamp, metadata)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """,
                (
                    state.level.value,
                    state.awareness_score,
                    state.attention_focus,
                    json.dumps(state.emotional_state),
                    state.cognitive_load,
                    state.creativity_level,
                    state.timestamp.isoformat(),
                    json.dumps(state.metadata),
                ),
            )

            self.conn.commit()
            cursor.close()

        except Exception as e:
            logger.error(f"Error guardando estado de conciencia: {e}")

    def get_system_stats(self) -> Dict[str, Any]:
        """Obtener estadísticas del sistema"""
        try:
            cursor = self.conn.cursor()

            # Estadísticas de memorias
            cursor.execute("SELECT COUNT(*) FROM memories")
            total_memories = cursor.fetchone()[0]

            cursor.execute("SELECT AVG(importance_score) FROM memories")
            avg_importance = cursor.fetchone()[0] or 0.0

            # Estadísticas de pensamientos
            cursor.execute("SELECT COUNT(*) FROM thoughts")
            total_thoughts = cursor.fetchone()[0]

            # Estadísticas de estados de conciencia
            cursor.execute("SELECT COUNT(*) FROM consciousness_states")
            total_states = cursor.fetchone()[0]

            cursor.close()

            return {
                "memories": {
                    "total": total_memories,
                    "working_memory": len(self.working_memory),
                    "average_importance": round(avg_importance, 3),
                },
                "thoughts": {"total": total_thoughts, "in_memory": len(self.thoughts)},
                "consciousness": {
                    "current_level": self.current_state.level.value,
                    "awareness_score": round(self.current_state.awareness_score, 3),
                    "total_states": total_states,
                },
                "performance": {
                    "memory_types": list(
                        set(mem.memory_type.value for mem in self.memories.values())
                    ),
                    "reasoning_modes": list(
                        set(thought.reasoning_mode.value for thought in self.thoughts)
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
            logger.info("✅ Sistema de conciencia y memoria cerrado")
        except Exception as e:
            logger.error(f"Error cerrando sistema: {e}")


def get_unified_consciousness_memory_system(
    config: Optional[ConsciousnessConfig] = None, db_path: Optional[str] = None
) -> UnifiedConsciousnessMemorySystem:
    """Función factory para crear sistema unificado"""
    return UnifiedConsciousnessMemorySystem(config, db_path)


async def main():
    """Función principal de demostración"""
    # Configurar sistema
    config = ConsciousnessConfig(
        consciousness_level=ConsciousnessLevel.AWARE,
        memory_capacity=5000,
        working_memory_size=50,
        reflection_enabled=True,
        creativity_enabled=True,
    )

    system = get_unified_consciousness_memory_system(config)

    print("🚀 Sistema Unificado de Conciencia y Memoria")
    print("=" * 50)

    # Ejemplo de procesamiento con conciencia
    print("\n🧠 Procesamiento Consciente:")
    input_text = (
        "La inteligencia artificial está transformando el mundo de manera increíble"
    )
    result = await system.process_input(input_text, {"context": "discussion_about_ai"})

    print(f"   Nivel de conciencia: {result['consciousness_level']}")
    print(f"   Score de conciencia: {result['awareness_score']:.3f}")
    print(f"   Memoria almacenada: {result['memory_stored']}")
    print(f"   Pensamiento generado: {result['thought_generated']}")
    print(f"   Tiempo de procesamiento: {result['processing_time']:.3f}s")

    # Ejemplo de procesamiento emocional
    print("\n😊 Procesamiento Emocional:")
    emotional_text = "Me siento muy feliz y emocionado por este proyecto"
    emotional_result = await system.process_input(emotional_text)

    print(f"   Estado emocional: {emotional_result['emotional_state']}")
    print(f"   Carga cognitiva: {emotional_result['cognitive_load']:.3f}")

    # Estadísticas
    print("\n📊 Estadísticas del Sistema:")
    stats = system.get_system_stats()
    print(f"   Memorias totales: {stats['memories']['total']}")
    print(f"   Memoria de trabajo: {stats['memories']['working_memory']}")
    print(f"   Pensamientos: {stats['thoughts']['total']}")
    print(f"   Nivel de conciencia actual: {stats['consciousness']['current_level']}")
    print(f"   Score de conciencia: {stats['consciousness']['awareness_score']}")

    # Cerrar sistema
    system.close()


if __name__ == "__main__":
    asyncio.run(main())
