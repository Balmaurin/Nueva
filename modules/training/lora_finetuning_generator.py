#!/usr/bin/env python3
"""
Generador Automático de Datos para Fine-tuning LoRA
==================================================
Genera datos de entrenamiento limpios para mejorar el LLM de ramas especialistas
"""

import json
import logging
import hashlib
from pathlib import Path
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, asdict
from datetime import datetime
import sqlite3
import threading

logger = logging.getLogger(__name__)


@dataclass
class LoRATrainingData:
    """Datos de entrenamiento para LoRA"""

    id: str
    branch_name: str
    exercise_id: str
    user_id: str
    session_id: str
    question: str
    user_answer: str
    correct_answer: str
    explanation: str
    difficulty: str
    category: str
    points: int
    is_correct: bool
    training_format: str  # 'qa', 'yes_no', 'multiple_choice', 'open_ended'
    metadata: Dict[str, Any]
    created_at: datetime
    quality_score: float


@dataclass
class BranchSpecialist:
    """Especialista de rama para fine-tuning"""

    branch_name: str
    description: str
    domain: str
    training_data_count: int
    last_updated: datetime
    performance_metrics: Dict[str, float]
    is_active: bool


class LoRAFinetuningGenerator:
    """Generador automático de datos para fine-tuning LoRA"""

    def __init__(self, db_path: str = "shaili_ai/data/lora_training.db"):
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self.lock = threading.Lock()

        # Mapeo de ejercicios a ramas especialistas
        self.exercise_branch_mapping = {
            "comprehension": "ai_ml_specialist",
            "logic": "mathematics_specialist",
            "programming": "programming_specialist",
            "creativity": "creativity_innovation_specialist",
            "communication": "communication_specialist",
            "critical_thinking": "critical_analysis_specialist",
            "problem_solving": "problem_solving_specialist",
            "data_analysis": "data_science_specialist",
            "leadership": "leadership_management_specialist",
            "innovation": "entrepreneurship_specialist",
        }

        # Inicializar base de datos
        self._init_database()

        logger.info("🎯 Generador de datos LoRA inicializado")

    def _init_database(self):
        """Inicializar base de datos para datos de entrenamiento LoRA"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()

                # Tabla de datos de entrenamiento LoRA
                cursor.execute(
                    """
                    CREATE TABLE IF NOT EXISTS lora_training_data (
                        id TEXT PRIMARY KEY,
                        branch_name TEXT NOT NULL,
                        exercise_id TEXT NOT NULL,
                        user_id TEXT NOT NULL,
                        session_id TEXT NOT NULL,
                        question TEXT NOT NULL,
                        user_answer TEXT NOT NULL,
                        correct_answer TEXT NOT NULL,
                        explanation TEXT NOT NULL,
                        difficulty TEXT NOT NULL,
                        category TEXT NOT NULL,
                        points INTEGER NOT NULL,
                        is_correct BOOLEAN NOT NULL,
                        training_format TEXT NOT NULL,
                        metadata TEXT NOT NULL,
                        created_at TIMESTAMP NOT NULL,
                        quality_score REAL NOT NULL
                    )
                """
                )

                # Crear índices por separado
                cursor.execute(
                    "CREATE INDEX IF NOT EXISTS idx_lora_branch_name ON lora_training_data (branch_name)"
                )
                cursor.execute(
                    "CREATE INDEX IF NOT EXISTS idx_lora_exercise_id ON lora_training_data (exercise_id)"
                )
                cursor.execute(
                    "CREATE INDEX IF NOT EXISTS idx_lora_user_id ON lora_training_data (user_id)"
                )

                # Tabla de especialistas de rama
                cursor.execute(
                    """
                    CREATE TABLE IF NOT EXISTS branch_specialists (
                        branch_name TEXT PRIMARY KEY,
                        description TEXT NOT NULL,
                        domain TEXT NOT NULL,
                        training_data_count INTEGER DEFAULT 0,
                        last_updated TIMESTAMP NOT NULL,
                        performance_metrics TEXT NOT NULL,
                        is_active BOOLEAN DEFAULT TRUE
                    )
                """
                )

                # Tabla de sesiones de entrenamiento completadas
                cursor.execute(
                    """
                    CREATE TABLE IF NOT EXISTS completed_training_sessions (
                        session_id TEXT PRIMARY KEY,
                        user_id TEXT NOT NULL,
                        exercise_id TEXT NOT NULL,
                        branch_name TEXT NOT NULL,
                        total_questions INTEGER NOT NULL,
                        correct_answers INTEGER NOT NULL,
                        total_score INTEGER NOT NULL,
                        completion_time_minutes INTEGER NOT NULL,
                        quality_metrics TEXT NOT NULL,
                        created_at TIMESTAMP NOT NULL,
                        lora_data_generated BOOLEAN DEFAULT FALSE
                    )
                """
                )

                conn.commit()

                # Crear especialistas de rama por defecto
                self._create_default_branch_specialists()

        except Exception as e:
            logger.error(f"❌ Error inicializando base de datos: {e}")

    def _create_default_branch_specialists(self):
        """Crear especialistas de rama por defecto"""
        default_specialists = [
            {
                "branch_name": "ai_ml_specialist",
                "description": "Especialista en Inteligencia Artificial y Machine Learning",
                "domain": "AI/ML",
                "performance_metrics": {
                    "accuracy": 0.0,
                    "response_quality": 0.0,
                    "knowledge_depth": 0.0,
                },
            },
            {
                "branch_name": "mathematics_specialist",
                "description": "Especialista en Matemáticas y Lógica",
                "domain": "Mathematics",
                "performance_metrics": {
                    "accuracy": 0.0,
                    "response_quality": 0.0,
                    "knowledge_depth": 0.0,
                },
            },
            {
                "branch_name": "programming_specialist",
                "description": "Especialista en Programación y Algoritmos",
                "domain": "Programming",
                "performance_metrics": {
                    "accuracy": 0.0,
                    "response_quality": 0.0,
                    "knowledge_depth": 0.0,
                },
            },
            {
                "branch_name": "creativity_innovation_specialist",
                "description": "Especialista en Creatividad e Innovación",
                "domain": "Creativity",
                "performance_metrics": {
                    "accuracy": 0.0,
                    "response_quality": 0.0,
                    "knowledge_depth": 0.0,
                },
            },
            {
                "branch_name": "communication_specialist",
                "description": "Especialista en Comunicación y Persuasión",
                "domain": "Communication",
                "performance_metrics": {
                    "accuracy": 0.0,
                    "response_quality": 0.0,
                    "knowledge_depth": 0.0,
                },
            },
            {
                "branch_name": "critical_analysis_specialist",
                "description": "Especialista en Pensamiento Crítico y Análisis",
                "domain": "Critical Thinking",
                "performance_metrics": {
                    "accuracy": 0.0,
                    "response_quality": 0.0,
                    "knowledge_depth": 0.0,
                },
            },
            {
                "branch_name": "problem_solving_specialist",
                "description": "Especialista en Resolución de Problemas",
                "domain": "Problem Solving",
                "performance_metrics": {
                    "accuracy": 0.0,
                    "response_quality": 0.0,
                    "knowledge_depth": 0.0,
                },
            },
            {
                "branch_name": "data_science_specialist",
                "description": "Especialista en Análisis de Datos y Estadística",
                "domain": "Data Science",
                "performance_metrics": {
                    "accuracy": 0.0,
                    "response_quality": 0.0,
                    "knowledge_depth": 0.0,
                },
            },
            {
                "branch_name": "leadership_management_specialist",
                "description": "Especialista en Liderazgo y Gestión de Equipos",
                "domain": "Leadership",
                "performance_metrics": {
                    "accuracy": 0.0,
                    "response_quality": 0.0,
                    "knowledge_depth": 0.0,
                },
            },
            {
                "branch_name": "entrepreneurship_specialist",
                "description": "Especialista en Innovación y Emprendimiento",
                "domain": "Entrepreneurship",
                "performance_metrics": {
                    "accuracy": 0.0,
                    "response_quality": 0.0,
                    "knowledge_depth": 0.0,
                },
            },
        ]

        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()

                for specialist in default_specialists:
                    cursor.execute(
                        """
                        INSERT OR IGNORE INTO branch_specialists 
                        (branch_name, description, domain, training_data_count, last_updated, performance_metrics, is_active)
                        VALUES (?, ?, ?, ?, ?, ?, ?)
                    """,
                        (
                            specialist["branch_name"],
                            specialist["description"],
                            specialist["domain"],
                            0,
                            datetime.now().isoformat(),
                            json.dumps(specialist["performance_metrics"]),
                            True,
                        ),
                    )

                conn.commit()
                logger.info(
                    f"✅ {len(default_specialists)} especialistas de rama creados"
                )

        except Exception as e:
            logger.error(f"❌ Error creando especialistas por defecto: {e}")

    def get_branch_for_exercise(self, exercise_id: str) -> str:
        """Obtener la rama especialista para un ejercicio"""
        return self.exercise_branch_mapping.get(exercise_id, "general_specialist")

    def generate_lora_training_data(
        self, session_data: Dict[str, Any], exercise_data: Dict[str, Any]
    ) -> List[LoRATrainingData]:
        """Generar datos de entrenamiento LoRA desde una sesión completada"""
        try:
            training_data_list = []
            branch_name = self.get_branch_for_exercise(session_data["exercise_id"])

            # Obtener preguntas del ejercicio
            questions = exercise_data.get("questions", [])

            for question_data in questions:
                question_id = question_data["id"]
                user_answer_data = session_data["answers"].get(question_id, {})

                if user_answer_data:
                    # Generar formato de entrenamiento
                    training_format = self._determine_training_format(question_data)

                    # Calcular calidad de la respuesta
                    quality_score = self._calculate_quality_score(
                        user_answer_data["answer"],
                        question_data["correct_answer"],
                        user_answer_data["correct"],
                        question_data["difficulty"],
                    )

                    # Crear datos de entrenamiento
                    training_data = LoRATrainingData(
                        id=f"lora_{session_data['session_id']}_{question_id}",
                        branch_name=branch_name,
                        exercise_id=session_data["exercise_id"],
                        user_id=session_data["user_id"],
                        session_id=session_data["session_id"],
                        question=question_data["question"],
                        user_answer=user_answer_data["answer"],
                        correct_answer=question_data["correct_answer"],
                        explanation=question_data["explanation"],
                        difficulty=question_data["difficulty"],
                        category=question_data["category"],
                        points=question_data["points"],
                        is_correct=user_answer_data["correct"],
                        training_format=training_format,
                        metadata={
                            "topic": question_data["metadata"].get("topic", ""),
                            "complexity": question_data["metadata"].get(
                                "complexity", ""
                            ),
                            "session_score": session_data["score"],
                            "completion_time": session_data.get("time_spent", 0),
                        },
                        created_at=datetime.now(),
                        quality_score=quality_score,
                    )

                    training_data_list.append(training_data)

            # Guardar datos en base de datos
            self._save_training_data(training_data_list)

            # Actualizar métricas del especialista
            self._update_branch_specialist_metrics(branch_name, len(training_data_list))

            logger.info(
                f"✅ Generados {len(training_data_list)} datos de entrenamiento para {branch_name}"
            )
            return training_data_list

        except Exception as e:
            logger.error(f"❌ Error generando datos LoRA: {e}")
            return []

    def _determine_training_format(self, question_data: Dict[str, Any]) -> str:
        """Determinar el formato de entrenamiento basado en la pregunta"""
        question_text = question_data["question"].lower()
        correct_answer = question_data["correct_answer"].lower()

        # Detectar formato de respuesta
        if any(
            word in question_text
            for word in ["¿cuál es", "qué es", "explica", "describe"]
        ):
            return "open_ended"
        elif any(word in question_text for word in ["sí", "no", "verdadero", "falso"]):
            return "yes_no"
        elif len(correct_answer.split()) <= 5:
            return "qa"
        else:
            return "open_ended"

    def _calculate_quality_score(
        self, user_answer: str, correct_answer: str, is_correct: bool, difficulty: str
    ) -> float:
        """Calcular puntuación de calidad de la respuesta"""
        try:
            base_score = 1.0 if is_correct else 0.3

            # Factor de dificultad
            difficulty_multiplier = {"easy": 0.8, "medium": 1.0, "hard": 1.2}.get(
                difficulty, 1.0
            )

            # Factor de longitud de respuesta
            user_length = len(user_answer.split())
            correct_length = len(correct_answer.split())

            if user_length > 0 and correct_length > 0:
                length_ratio = min(
                    user_length / correct_length, correct_length / user_length
                )
                length_factor = 0.5 + (length_ratio * 0.5)
            else:
                length_factor = 0.5

            # Factor de similitud semántica (simplificado)
            similarity_factor = 0.8 if is_correct else 0.3

            # Calcular puntuación final
            quality_score = (
                base_score * difficulty_multiplier * length_factor * similarity_factor
            )

            return min(quality_score, 1.0)

        except Exception as e:
            logger.error(f"❌ Error calculando calidad: {e}")
            return 0.5

    def _save_training_data(self, training_data_list: List[LoRATrainingData]):
        """Guardar datos de entrenamiento en base de datos"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()

                for training_data in training_data_list:
                    cursor.execute(
                        """
                        INSERT OR REPLACE INTO lora_training_data 
                        (id, branch_name, exercise_id, user_id, session_id, question, user_answer, 
                         correct_answer, explanation, difficulty, category, points, is_correct, 
                         training_format, metadata, created_at, quality_score)
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """,
                        (
                            training_data.id,
                            training_data.branch_name,
                            training_data.exercise_id,
                            training_data.user_id,
                            training_data.session_id,
                            training_data.question,
                            training_data.user_answer,
                            training_data.correct_answer,
                            training_data.explanation,
                            training_data.difficulty,
                            training_data.category,
                            training_data.points,
                            training_data.is_correct,
                            training_data.training_format,
                            json.dumps(training_data.metadata),
                            training_data.created_at.isoformat(),
                            training_data.quality_score,
                        ),
                    )

                conn.commit()
                logger.info(
                    f"✅ {len(training_data_list)} datos de entrenamiento guardados"
                )

        except Exception as e:
            logger.error(f"❌ Error guardando datos de entrenamiento: {e}")

    def _update_branch_specialist_metrics(self, branch_name: str, new_data_count: int):
        """Actualizar métricas del especialista de rama"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()

                # Obtener métricas actuales
                cursor.execute(
                    """
                    SELECT training_data_count, performance_metrics 
                    FROM branch_specialists 
                    WHERE branch_name = ?
                """,
                    (branch_name,),
                )

                result = cursor.fetchone()
                if result:
                    current_count, current_metrics = result
                    current_metrics = json.loads(current_metrics)

                    # Actualizar métricas
                    new_count = current_count + new_data_count
                    current_metrics["training_data_count"] = new_count
                    current_metrics["last_updated"] = datetime.now().isoformat()

                    # Calcular métricas de rendimiento (simplificado)
                    cursor.execute(
                        """
                        SELECT AVG(quality_score), COUNT(*) 
                        FROM lora_training_data 
                        WHERE branch_name = ?
                    """,
                        (branch_name,),
                    )

                    avg_quality, total_data = cursor.fetchone()
                    if avg_quality:
                        current_metrics["accuracy"] = avg_quality
                        current_metrics["response_quality"] = avg_quality
                        current_metrics["knowledge_depth"] = min(avg_quality * 1.2, 1.0)

                    # Actualizar en base de datos
                    cursor.execute(
                        """
                        UPDATE branch_specialists 
                        SET training_data_count = ?, performance_metrics = ?, last_updated = ?
                        WHERE branch_name = ?
                    """,
                        (
                            new_count,
                            json.dumps(current_metrics),
                            datetime.now().isoformat(),
                            branch_name,
                        ),
                    )

                    conn.commit()
                    logger.info(f"✅ Métricas actualizadas para {branch_name}")

        except Exception as e:
            logger.error(f"❌ Error actualizando métricas: {e}")

    def get_training_data_for_branch(
        self, branch_name: str, limit: int = 100
    ) -> List[LoRATrainingData]:
        """Obtener datos de entrenamiento para una rama específica"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()

                cursor.execute(
                    """
                    SELECT * FROM lora_training_data 
                    WHERE branch_name = ? 
                    ORDER BY quality_score DESC, created_at DESC 
                    LIMIT ?
                """,
                    (branch_name, limit),
                )

                results = cursor.fetchall()
                training_data_list = []

                for row in results:
                    training_data = LoRATrainingData(
                        id=row[0],
                        branch_name=row[1],
                        exercise_id=row[2],
                        user_id=row[3],
                        session_id=row[4],
                        question=row[5],
                        user_answer=row[6],
                        correct_answer=row[7],
                        explanation=row[8],
                        difficulty=row[9],
                        category=row[10],
                        points=row[11],
                        is_correct=bool(row[12]),
                        training_format=row[13],
                        metadata=json.loads(row[14]),
                        created_at=datetime.fromisoformat(row[15]),
                        quality_score=row[16],
                    )
                    training_data_list.append(training_data)

                return training_data_list

        except Exception as e:
            logger.error(f"❌ Error obteniendo datos de entrenamiento: {e}")
            return []

    def export_lora_dataset(self, branch_name: str, output_path: str = None) -> str:
        """Exportar dataset para fine-tuning LoRA"""
        try:
            training_data = self.get_training_data_for_branch(branch_name)

            if not training_data:
                logger.warning(f"No hay datos de entrenamiento para {branch_name}")
                return ""

            # Generar formato para fine-tuning
            lora_dataset = []

            for data in training_data:
                # Formato de instrucción-respuesta para fine-tuning
                instruction = f"Pregunta sobre {data.category}: {data.question}"

                if data.training_format == "yes_no":
                    response = f"Respuesta: {'Sí' if data.is_correct else 'No'}. Explicación: {data.explanation}"
                elif data.training_format == "qa":
                    response = f"Respuesta: {data.correct_answer}. Explicación: {data.explanation}"
                else:
                    response = f"Respuesta completa: {data.correct_answer}. Explicación detallada: {data.explanation}"

                lora_dataset.append(
                    {
                        "instruction": instruction,
                        "input": "",
                        "output": response,
                        "domain": data.category,
                        "difficulty": data.difficulty,
                        "quality_score": data.quality_score,
                        "metadata": data.metadata,
                    }
                )

            # Guardar dataset
            if output_path is None:
                output_path = (
                    f"shaili_ai/data/lora_datasets/{branch_name}_dataset.jsonl"
                )

            Path(output_path).parent.mkdir(parents=True, exist_ok=True)

            with open(output_path, "w", encoding="utf-8") as f:
                for item in lora_dataset:
                    f.write(json.dumps(item, ensure_ascii=False) + "\n")

            logger.info(
                f"✅ Dataset exportado: {output_path} ({len(lora_dataset)} ejemplos)"
            )
            return output_path

        except Exception as e:
            logger.error(f"❌ Error exportando dataset: {e}")
            return ""

    def get_branch_statistics(self) -> Dict[str, Any]:
        """Obtener estadísticas de todas las ramas"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()

                cursor.execute(
                    """
                    SELECT branch_name, training_data_count, performance_metrics, last_updated
                    FROM branch_specialists
                    WHERE is_active = TRUE
                    ORDER BY training_data_count DESC
                """
                )

                results = cursor.fetchall()
                statistics = {}

                for row in results:
                    branch_name, data_count, metrics, last_updated = row
                    statistics[branch_name] = {
                        "training_data_count": data_count,
                        "performance_metrics": json.loads(metrics),
                        "last_updated": last_updated,
                    }

                return statistics

        except Exception as e:
            logger.error(f"❌ Error obteniendo estadísticas: {e}")
            return {}


# Instancia global
_lora_generator: Optional[LoRAFinetuningGenerator] = None


def get_lora_generator() -> LoRAFinetuningGenerator:
    """Obtener instancia global del generador LoRA"""
    global _lora_generator

    if _lora_generator is None:
        _lora_generator = LoRAFinetuningGenerator()

    return _lora_generator
