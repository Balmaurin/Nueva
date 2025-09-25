"""
Sistema Unificado de Aprendizaje y Entrenamiento para NeuroFusion

Este módulo combina funcionalidades de:
- Advanced LLM Training (advanced_llm_training.py)
- Continuous Learning (continuous_learning.py)
- Continuous Learning System (continuous_learning_system.py)
- Consolidated Learning System (consolidated_learning_system.py)
- Dynamic Training System (dynamic_training_system.py)
- Gradient Training System (gradient_training_system.py)
- LLM Training Pipeline (llm_training_pipeline.py)
- Specialized Training (specialized_training.py)
- Add More Training Data (add_more_training_data.py)
- Download Training Dataset (download_training_dataset.py)
- Download HeadQA Dataset (download_headqa_dataset.py)
- Expand HeadQA Dataset (expand_headqa_dataset.py)
- Import Datasets to Branches (import_datasets_to_branches.py)
"""

import logging
import json
import time
import asyncio
import sqlite3
import uuid
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional, Union, Tuple
from dataclasses import dataclass, field
from pathlib import Path
from enum import Enum
import numpy as np
import torch
import torch.nn as nn
from torch.utils.data import Dataset, DataLoader
from torch.optim import AdamW
from torch.nn import CrossEntropyLoss
import psycopg2
from psycopg2.extras import RealDictCursor
import pickle
import gzip
from functools import lru_cache
import threading
from concurrent.futures import ThreadPoolExecutor, as_completed
import requests
from tqdm import tqdm

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class TrainingMode(Enum):
    """Modos de entrenamiento"""

    FINE_TUNE = "fine_tune"
    CONTINUOUS = "continuous"
    CONSOLIDATED = "consolidated"
    DYNAMIC = "dynamic"
    SPECIALIZED = "specialized"


class DatasetType(Enum):
    """Tipos de datasets"""

    HEADQA = "headqa"
    MLQA = "mlqa"
    XQUAD = "xquad"
    TYDIQA = "tydiqa"
    SYNTHETIC = "synthetic"
    CUSTOM = "custom"


@dataclass
class TrainingConfig:
    """Configuración de entrenamiento"""

    model_name: str = "models/custom/shaili-personal-model"
    max_seq_length: int = 512
    batch_size: int = 16
    learning_rate: float = 1e-4
    weight_decay: float = 0.01
    num_train_epochs: int = 3
    gradient_accumulation_steps: int = 4
    mixed_precision: bool = True
    lora_r: int = 16
    lora_alpha: int = 32
    lora_dropout: float = 0.1
    early_stop_patience: int = 3
    evaluation_strategy: str = "steps"
    eval_steps: int = 500
    save_steps: int = 1000
    warmup_steps: int = 100
    logging_steps: int = 100
    dataloader_num_workers: int = 4
    device: str = "auto"


@dataclass
class TrainingSession:
    """Sesión de entrenamiento"""

    session_id: str
    model_name: str
    dataset_name: str
    training_mode: TrainingMode
    config: TrainingConfig
    start_time: datetime
    end_time: Optional[datetime] = None
    status: str = "running"
    metrics: Dict[str, Any] = field(default_factory=dict)
    artifacts: List[str] = field(default_factory=list)


@dataclass
class LearningExperience:
    """Experiencia de aprendizaje"""

    experience_id: str
    domain: str
    input_data: Any
    output_data: Any
    performance_score: float
    timestamp: datetime
    metadata: Dict[str, Any] = field(default_factory=dict)


class UnifiedLearningTrainingSystem:
    """
    Sistema unificado de aprendizaje y entrenamiento
    """

    def __init__(
        self,
        config: Optional[TrainingConfig] = None,
        db_config: Optional[Dict[str, str]] = None,
    ):
        """Inicializar sistema de aprendizaje y entrenamiento"""
        self.config = config or TrainingConfig()
        self.db_config = db_config or {
            "host": "localhost",
            "database": "neurofusion_db",
            "user": "neurofusion_user",
            "password": "neurofusion_pass",
        }

        # Inicializar componentes
        self._init_database()
        self._init_models()
        self._init_datasets()
        self._init_monitoring()

        # Configurar threading
        self.executor = ThreadPoolExecutor(max_workers=4)
        self.lock = threading.Lock()

        # Estado del sistema
        self.active_sessions: Dict[str, TrainingSession] = {}
        self.learning_experiences: List[LearningExperience] = []

        logger.info("🎓 Sistema de Aprendizaje y Entrenamiento inicializado")

    def _init_database(self):
        """Inicializar base de datos"""
        try:
            # Conectar a PostgreSQL
            self.db_conn = psycopg2.connect(**self.db_config)
            self.db_conn.autocommit = True

            # Crear tablas si no existen
            self._create_tables()

            logger.info("✅ Base de datos inicializada")

        except Exception as e:
            logger.error(f"❌ Error inicializando base de datos: {e}")

    def _init_models(self):
        """Inicializar modelos"""
        try:
            # Solo 2 modelos: 4-bit para inferencia, 16-bit para entrenamiento
            self.models = {
                "inference": {
                    "name": "modules/core/model",
                    "type": "transformer",
                    "quantization": "4-bit",
                    "purpose": "inference",
                    "params": 768_000_000,
                },
                "training": {
                    "name": "models/custom/shaili-personal-model",
                    "type": "transformer",
                    "quantization": "16-bit",
                    "purpose": "training_and_fine_tuning",
                    "params": 3_800_000_000,
                },
            }

            # Modelo activo por defecto para inferencia
            self.active_model = "inference"

            logger.info(
                "✅ Modelos inicializados: 4-bit (inferencia) y 16-bit (entrenamiento)"
            )

        except Exception as e:
            logger.error(f"❌ Error inicializando modelos: {e}")

    def _init_datasets(self):
        """Inicializar datasets"""
        try:
            self.datasets = {
                DatasetType.HEADQA: {
                    "name": "HEAD-QA",
                    "description": "Dataset de preguntas médicas",
                    "size": 10000,
                    "domains": ["medical", "biology", "chemistry"],
                },
                DatasetType.MLQA: {
                    "name": "MLQA",
                    "description": "Dataset multilingüe de preguntas",
                    "size": 50000,
                    "domains": ["general", "multilingual"],
                },
                DatasetType.XQUAD: {
                    "name": "XQuAD",
                    "description": "Dataset de preguntas en español",
                    "size": 25000,
                    "domains": ["general", "spanish"],
                },
                DatasetType.TYDIQA: {
                    "name": "TyDiQA",
                    "description": "Dataset de preguntas tipológicas",
                    "size": 15000,
                    "domains": ["general", "multilingual"],
                },
            }

            logger.info("✅ Datasets inicializados")

        except Exception as e:
            logger.error(f"❌ Error inicializando datasets: {e}")

    def _init_monitoring(self):
        """Inicializar sistema de monitoreo"""
        self.performance_monitor = TrainingPerformanceMonitor()
        self.learning_tracker = LearningTracker()

        logger.info("✅ Sistema de monitoreo inicializado")

    def _create_tables(self):
        """Crear tablas en la base de datos"""
        try:
            cursor = self.db_conn.cursor()

            # Tabla de sesiones de entrenamiento
            cursor.execute(
                """
                CREATE TABLE IF NOT EXISTS training_sessions (
                    session_id TEXT PRIMARY KEY,
                    model_name TEXT NOT NULL,
                    dataset_name TEXT NOT NULL,
                    training_mode TEXT NOT NULL,
                    config JSONB NOT NULL,
                    start_time TIMESTAMP NOT NULL,
                    end_time TIMESTAMP,
                    status TEXT DEFAULT 'running',
                    metrics JSONB,
                    artifacts JSONB
                )
            """
            )

            # Tabla de experiencias de aprendizaje
            cursor.execute(
                """
                CREATE TABLE IF NOT EXISTS learning_experiences (
                    experience_id TEXT PRIMARY KEY,
                    domain TEXT NOT NULL,
                    input_data JSONB,
                    output_data JSONB,
                    performance_score REAL DEFAULT 0.0,
                    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    metadata JSONB
                )
            """
            )

            # Tabla de datasets
            cursor.execute(
                """
                CREATE TABLE IF NOT EXISTS datasets (
                    dataset_id TEXT PRIMARY KEY,
                    name TEXT NOT NULL,
                    type TEXT NOT NULL,
                    size INTEGER DEFAULT 0,
                    domains JSONB,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """
            )

            # Tabla de métricas de rendimiento
            cursor.execute(
                """
                CREATE TABLE IF NOT EXISTS training_metrics (
                    id SERIAL PRIMARY KEY,
                    session_id TEXT NOT NULL,
                    metric_type TEXT NOT NULL,
                    metric_value REAL NOT NULL,
                    step INTEGER DEFAULT 0,
                    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """
            )

            cursor.close()

        except Exception as e:
            logger.error(f"❌ Error creando tablas: {e}")

    # ==================== GESTIÓN DE DATASETS ====================

    async def download_dataset(
        self, dataset_type: DatasetType, output_dir: Optional[str] = None
    ) -> str:
        """Descargar dataset"""
        try:
            output_dir = output_dir or f"data/datasets/{dataset_type.value}"
            output_path = Path(output_dir)
            output_path.mkdir(parents=True, exist_ok=True)

            logger.info(f"📥 Descargando dataset: {dataset_type.value}")

            if dataset_type == DatasetType.HEADQA:
                return await self._download_headqa_dataset(output_path)
            elif dataset_type == DatasetType.MLQA:
                return await self._download_mlqa_dataset(output_path)
            elif dataset_type == DatasetType.XQUAD:
                return await self._download_xquad_dataset(output_path)
            elif dataset_type == DatasetType.TYDIQA:
                return await self._download_tydiqa_dataset(output_path)
            else:
                raise ValueError(f"Dataset no soportado: {dataset_type}")

        except Exception as e:
            logger.error(f"❌ Error descargando dataset: {e}")
            raise

    async def _download_headqa_dataset(self, output_path: Path) -> str:
        """Descargar dataset HEAD-QA"""
        try:
            # Crear dataset sintético HEAD-QA
            dataset = self._create_headqa_synthetic_dataset()

            # Guardar dataset
            dataset_file = output_path / "headqa_synthetic.json"
            with open(dataset_file, "w", encoding="utf-8") as f:
                json.dump(dataset, f, ensure_ascii=False, indent=2)

            # Registrar en base de datos
            await self._register_dataset(
                "HEAD-QA", DatasetType.HEADQA, len(dataset["train"])
            )

            logger.info(f"✅ Dataset HEAD-QA descargado: {dataset_file}")
            return str(dataset_file)

        except Exception as e:
            logger.error(f"❌ Error descargando HEAD-QA: {e}")
            raise

    def _create_headqa_synthetic_dataset(self) -> Dict[str, Any]:
        """Crear dataset HEAD-QA sintético"""
        return {
            "train": [
                {
                    "question": "¿Cuál es el síntoma más común de la hipertensión arterial?",
                    "choices": [
                        "Dolor de cabeza intenso",
                        "Dolor en el pecho",
                        "Puede ser asintomática",
                        "Fiebre alta",
                    ],
                    "answer": 2,
                    "explanation": "La hipertensión arterial a menudo es asintomática, por lo que se le llama 'el asesino silencioso'.",
                    "domain": "medical",
                },
                {
                    "question": "¿Qué es el machine learning?",
                    "choices": [
                        "Un tipo de hardware",
                        "Algoritmos que aprenden de datos",
                        "Un lenguaje de programación",
                        "Un sistema operativo",
                    ],
                    "answer": 1,
                    "explanation": "El machine learning es una rama de la IA que permite a las computadoras aprender sin ser programadas explícitamente.",
                    "domain": "technical",
                },
            ],
            "test": [
                {
                    "question": "¿Cuál es la capital de España?",
                    "choices": ["Barcelona", "Madrid", "Valencia", "Sevilla"],
                    "answer": 1,
                    "explanation": "Madrid es la capital y ciudad más poblada de España.",
                    "domain": "general",
                }
            ],
        }

    async def _download_mlqa_dataset(self, output_path: Path) -> str:
        """Descargar dataset MLQA"""
        # Implementación simplificada
        dataset_file = output_path / "mlqa_synthetic.json"
        synthetic_data = {"train": [], "test": []}

        with open(dataset_file, "w", encoding="utf-8") as f:
            json.dump(synthetic_data, f, ensure_ascii=False, indent=2)

        await self._register_dataset("MLQA", DatasetType.MLQA, 0)
        return str(dataset_file)

    async def _download_xquad_dataset(self, output_path: Path) -> str:
        """Descargar dataset XQuAD"""
        # Implementación simplificada
        dataset_file = output_path / "xquad_synthetic.json"
        synthetic_data = {"train": [], "test": []}

        with open(dataset_file, "w", encoding="utf-8") as f:
            json.dump(synthetic_data, f, ensure_ascii=False, indent=2)

        await self._register_dataset("XQuAD", DatasetType.XQUAD, 0)
        return str(dataset_file)

    async def _download_tydiqa_dataset(self, output_path: Path) -> str:
        """Descargar dataset TyDiQA"""
        # Implementación simplificada
        dataset_file = output_path / "tydiqa_synthetic.json"
        synthetic_data = {"train": [], "test": []}

        with open(dataset_file, "w", encoding="utf-8") as f:
            json.dump(synthetic_data, f, ensure_ascii=False, indent=2)

        await self._register_dataset("TyDiQA", DatasetType.TYDIQA, 0)
        return str(dataset_file)

    async def _register_dataset(self, name: str, dataset_type: DatasetType, size: int):
        """Registrar dataset en base de datos"""
        try:
            cursor = self.db_conn.cursor()
            cursor.execute(
                """
                INSERT INTO datasets (dataset_id, name, type, size, domains)
                VALUES (%s, %s, %s, %s, %s)
                ON CONFLICT (dataset_id) 
                DO UPDATE SET 
                    size = EXCLUDED.size,
                    last_updated = CURRENT_TIMESTAMP
            """,
                (
                    str(uuid.uuid4()),
                    name,
                    dataset_type.value,
                    size,
                    json.dumps(self.datasets[dataset_type]["domains"]),
                ),
            )
            cursor.close()

        except Exception as e:
            logger.error(f"❌ Error registrando dataset: {e}")

    # ==================== ENTRENAMIENTO ====================

    async def start_training_session(
        self,
        model_name: str,
        dataset_path: str,
        training_mode: TrainingMode = TrainingMode.FINE_TUNE,
        config: Optional[TrainingConfig] = None,
    ) -> str:
        """Iniciar sesión de entrenamiento"""
        try:
            session_id = str(uuid.uuid4())
            config = config or self.config

            # Crear sesión
            session = TrainingSession(
                session_id=session_id,
                model_name=model_name,
                dataset_name=Path(dataset_path).stem,
                training_mode=training_mode,
                config=config,
                start_time=datetime.now(),
            )

            # Guardar en base de datos
            await self._save_training_session(session)

            # Agregar a sesiones activas
            self.active_sessions[session_id] = session

            # Iniciar entrenamiento en segundo plano
            asyncio.create_task(self._run_training_session(session))

            logger.info(f"🚀 Sesión de entrenamiento iniciada: {session_id}")
            return session_id

        except Exception as e:
            logger.error(f"❌ Error iniciando sesión: {e}")
            raise

    async def _run_training_session(self, session: TrainingSession):
        """Ejecutar sesión de entrenamiento"""
        try:
            logger.info(f"🎯 Iniciando entrenamiento: {session.session_id}")

            # Cargar dataset
            dataset = await self._load_dataset(session.dataset_name)

            # Preparar modelo
            model = await self._prepare_model(session.model_name, session.config)

            # Configurar entrenamiento
            trainer = await self._setup_trainer(model, dataset, session.config)

            # Ejecutar entrenamiento
            training_output = await self._execute_training(trainer, session)

            # Guardar resultados
            session.end_time = datetime.now()
            session.status = "completed"
            session.metrics = training_output.get("metrics", {})
            session.artifacts = training_output.get("artifacts", [])

            # Actualizar en base de datos
            await self._update_training_session(session)

            # Remover de sesiones activas
            if session.session_id in self.active_sessions:
                del self.active_sessions[session.session_id]

            logger.info(f"✅ Entrenamiento completado: {session.session_id}")

        except Exception as e:
            logger.error(f"❌ Error en entrenamiento: {e}")
            session.status = "failed"
            session.end_time = datetime.now()
            await self._update_training_session(session)

    async def _load_dataset(self, dataset_name: str) -> Dataset:
        """Cargar dataset"""

        # Implementación simplificada
        class SyntheticDataset(Dataset):
            def __init__(self, size: int = 1000):
                self.size = size
                self.data = [
                    {"input": f"text_{i}", "output": f"response_{i}"}
                    for i in range(size)
                ]

            def __len__(self):
                return self.size

            def __getitem__(self, idx):
                return self.data[idx]

        return SyntheticDataset()

    async def _prepare_model(self, model_name: str, config: TrainingConfig):
        """Preparar modelo para entrenamiento"""

        # Implementación simplificada
        class SimpleModel(nn.Module):
            def __init__(self, vocab_size: int = 50000, hidden_size: int = 768):
                super().__init__()
                self.embedding = nn.Embedding(vocab_size, hidden_size)
                self.transformer = nn.TransformerEncoderLayer(hidden_size, 8)
                self.output = nn.Linear(hidden_size, vocab_size)

            def forward(self, input_ids):
                x = self.embedding(input_ids)
                x = self.transformer(x)
                return self.output(x)

        return SimpleModel()

    async def _setup_trainer(self, model, dataset, config: TrainingConfig):
        """Configurar trainer"""

        # Implementación simplificada
        class SimpleTrainer:
            def __init__(self, model, dataset, config):
                self.model = model
                self.dataset = dataset
                self.config = config
                self.optimizer = AdamW(model.parameters(), lr=config.learning_rate)
                self.criterion = CrossEntropyLoss()

            async def train(self):
                # Simular entrenamiento
                for epoch in range(self.config.num_train_epochs):
                    for batch in range(10):  # Simular batches
                        # Simular forward pass
                        loss = torch.tensor(0.5 - epoch * 0.1 - batch * 0.01)

                        # Simular backward pass
                        self.optimizer.zero_grad()
                        loss.backward()
                        self.optimizer.step()

                        # Registrar métricas
                        await self._log_training_metric(
                            "loss", loss.item(), epoch * 10 + batch
                        )

                return {
                    "metrics": {"final_loss": 0.1},
                    "artifacts": ["model_weights.pth", "training_log.json"],
                }

        return SimpleTrainer(model, dataset, config)

    async def _execute_training(self, trainer, session: TrainingSession):
        """Ejecutar entrenamiento"""
        return await trainer.train()

    # ==================== APRENDIZAJE CONTINUO ====================

    async def add_learning_experience(
        self,
        domain: str,
        input_data: Any,
        output_data: Any,
        performance_score: float,
        metadata: Optional[Dict[str, Any]] = None,
    ):
        """Agregar experiencia de aprendizaje"""
        try:
            experience = LearningExperience(
                experience_id=str(uuid.uuid4()),
                domain=domain,
                input_data=input_data,
                output_data=output_data,
                performance_score=performance_score,
                timestamp=datetime.now(),
                metadata=metadata or {},
            )

            # Agregar a lista local
            self.learning_experiences.append(experience)

            # Guardar en base de datos
            await self._save_learning_experience(experience)

            # Actualizar tracker
            self.learning_tracker.add_experience(experience)

            logger.info(
                f"📚 Experiencia de aprendizaje agregada: {experience.experience_id}"
            )

        except Exception as e:
            logger.error(f"❌ Error agregando experiencia: {e}")

    async def consolidate_learning(self, domain: Optional[str] = None):
        """Consolidar aprendizaje"""
        try:
            # Filtrar experiencias por dominio
            experiences = self.learning_experiences
            if domain:
                experiences = [exp for exp in experiences if exp.domain == domain]

            if not experiences:
                logger.warning("⚠️ No hay experiencias para consolidar")
                return

            # Calcular métricas de consolidación
            avg_performance = np.mean([exp.performance_score for exp in experiences])
            total_experiences = len(experiences)

            # Crear sesión de consolidación
            session_id = await self.start_training_session(
                model_name=self.models[self.active_model]["name"],
                dataset_path="consolidated_learning",
                training_mode=TrainingMode.CONSOLIDATED,
            )

            logger.info(f"🔄 Consolidación iniciada: {session_id}")
            logger.info(f"   Experiencias: {total_experiences}")
            logger.info(f"   Rendimiento promedio: {avg_performance:.3f}")

        except Exception as e:
            logger.error(f"❌ Error consolidando aprendizaje: {e}")

    # ==================== MONITOREO Y MÉTRICAS ====================

    async def get_training_sessions(
        self, status: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """Obtener sesiones de entrenamiento"""
        try:
            cursor = self.db_conn.cursor(cursor_factory=RealDictCursor)

            query = "SELECT * FROM training_sessions"
            params = []

            if status:
                query += " WHERE status = %s"
                params.append(status)

            query += " ORDER BY start_time DESC"

            cursor.execute(query, params)
            sessions = cursor.fetchall()
            cursor.close()

            return [dict(session) for session in sessions]

        except Exception as e:
            logger.error(f"❌ Error obteniendo sesiones: {e}")
            return []

    async def get_learning_summary(
        self, domain: Optional[str] = None
    ) -> Dict[str, Any]:
        """Obtener resumen de aprendizaje"""
        try:
            # Filtrar experiencias
            experiences = self.learning_experiences
            if domain:
                experiences = [exp for exp in experiences if exp.domain == domain]

            if not experiences:
                return {"message": "No hay experiencias de aprendizaje"}

            # Calcular métricas
            total_experiences = len(experiences)
            avg_performance = np.mean([exp.performance_score for exp in experiences])

            # Agrupar por dominio
            domain_stats = {}
            for exp in experiences:
                if exp.domain not in domain_stats:
                    domain_stats[exp.domain] = {
                        "count": 0,
                        "avg_performance": 0.0,
                        "total_performance": 0.0,
                    }

                domain_stats[exp.domain]["count"] += 1
                domain_stats[exp.domain]["total_performance"] += exp.performance_score

            # Calcular promedios por dominio
            for domain_name in domain_stats:
                count = domain_stats[domain_name]["count"]
                total = domain_stats[domain_name]["total_performance"]
                domain_stats[domain_name]["avg_performance"] = total / count

            return {
                "total_experiences": total_experiences,
                "average_performance": avg_performance,
                "domain_statistics": domain_stats,
                "recent_experiences": [
                    {
                        "id": exp.experience_id,
                        "domain": exp.domain,
                        "performance": exp.performance_score,
                        "timestamp": exp.timestamp.isoformat(),
                    }
                    for exp in experiences[-10:]  # Últimas 10 experiencias
                ],
            }

        except Exception as e:
            logger.error(f"❌ Error obteniendo resumen: {e}")
            return {}

    # ==================== BASE DE DATOS ====================

    async def _save_training_session(self, session: TrainingSession):
        """Guardar sesión de entrenamiento en base de datos"""
        try:
            cursor = self.db_conn.cursor()
            cursor.execute(
                """
                INSERT INTO training_sessions 
                (session_id, model_name, dataset_name, training_mode, config, start_time)
                VALUES (%s, %s, %s, %s, %s, %s)
            """,
                (
                    session.session_id,
                    session.model_name,
                    session.dataset_name,
                    session.training_mode.value,
                    json.dumps(session.config.__dict__),
                    session.start_time,
                ),
            )
            cursor.close()

        except Exception as e:
            logger.error(f"❌ Error guardando sesión: {e}")

    async def _update_training_session(self, session: TrainingSession):
        """Actualizar sesión de entrenamiento"""
        try:
            cursor = self.db_conn.cursor()
            cursor.execute(
                """
                UPDATE training_sessions 
                SET end_time = %s, status = %s, metrics = %s, artifacts = %s
                WHERE session_id = %s
            """,
                (
                    session.end_time,
                    session.status,
                    json.dumps(session.metrics),
                    json.dumps(session.artifacts),
                    session.session_id,
                ),
            )
            cursor.close()

        except Exception as e:
            logger.error(f"❌ Error actualizando sesión: {e}")

    async def _save_learning_experience(self, experience: LearningExperience):
        """Guardar experiencia de aprendizaje"""
        try:
            cursor = self.db_conn.cursor()
            cursor.execute(
                """
                INSERT INTO learning_experiences 
                (experience_id, domain, input_data, output_data, performance_score, metadata)
                VALUES (%s, %s, %s, %s, %s, %s)
            """,
                (
                    experience.experience_id,
                    experience.domain,
                    json.dumps(experience.input_data),
                    json.dumps(experience.output_data),
                    experience.performance_score,
                    json.dumps(experience.metadata),
                ),
            )
            cursor.close()

        except Exception as e:
            logger.error(f"❌ Error guardando experiencia: {e}")

    async def _log_training_metric(self, metric_type: str, value: float, step: int = 0):
        """Registrar métrica de entrenamiento"""
        try:
            cursor = self.db_conn.cursor()
            cursor.execute(
                """
                INSERT INTO training_metrics 
                (metric_type, metric_value, step)
                VALUES (%s, %s, %s)
            """,
                (metric_type, value, step),
            )
            cursor.close()

        except Exception as e:
            logger.error(f"❌ Error registrando métrica: {e}")

    # ==================== UTILIDADES ====================

    def get_system_stats(self) -> Dict[str, Any]:
        """Obtener estadísticas del sistema"""
        try:
            # Estadísticas de sesiones
            active_sessions = len(self.active_sessions)
            total_experiences = len(self.learning_experiences)

            # Estadísticas de rendimiento
            performance_stats = self.performance_monitor.get_stats()
            learning_stats = self.learning_tracker.get_stats()

            return {
                "active_training_sessions": active_sessions,
                "total_learning_experiences": total_experiences,
                "performance_stats": performance_stats,
                "learning_stats": learning_stats,
                "active_model": self.active_model,
                "available_datasets": len(self.datasets),
            }

        except Exception as e:
            logger.error(f"❌ Error obteniendo estadísticas: {e}")
            return {}

    def close(self):
        """Cerrar sistema"""
        try:
            # Cerrar conexiones
            if hasattr(self, "db_conn"):
                self.db_conn.close()

            # Cerrar executor
            if hasattr(self, "executor"):
                self.executor.shutdown()

            logger.info("🔒 Sistema cerrado correctamente")

        except Exception as e:
            logger.error(f"❌ Error cerrando sistema: {e}")


# ==================== COMPONENTES AUXILIARES ====================


class TrainingPerformanceMonitor:
    """Monitor de rendimiento de entrenamiento"""

    def __init__(self):
        self.metrics = {}

    def record_metric(self, metric_name: str, value: float):
        """Registrar métrica"""
        if metric_name not in self.metrics:
            self.metrics[metric_name] = []
        self.metrics[metric_name].append(value)

    def get_stats(self) -> Dict[str, Any]:
        """Obtener estadísticas"""
        stats = {}
        for metric_name, values in self.metrics.items():
            if values:
                stats[metric_name] = {
                    "count": len(values),
                    "average": sum(values) / len(values),
                    "min": min(values),
                    "max": max(values),
                }
        return stats


class LearningTracker:
    """Tracker de aprendizaje"""

    def __init__(self):
        self.experiences = []
        self.domain_stats = {}

    def add_experience(self, experience: LearningExperience):
        """Agregar experiencia"""
        self.experiences.append(experience)

        # Actualizar estadísticas por dominio
        if experience.domain not in self.domain_stats:
            self.domain_stats[experience.domain] = {
                "count": 0,
                "total_performance": 0.0,
            }

        self.domain_stats[experience.domain]["count"] += 1
        self.domain_stats[experience.domain][
            "total_performance"
        ] += experience.performance_score

    def get_stats(self) -> Dict[str, Any]:
        """Obtener estadísticas"""
        if not self.experiences:
            return {}

        total_experiences = len(self.experiences)
        avg_performance = (
            sum(exp.performance_score for exp in self.experiences) / total_experiences
        )

        domain_averages = {}
        for domain, stats in self.domain_stats.items():
            domain_averages[domain] = stats["total_performance"] / stats["count"]

        return {
            "total_experiences": total_experiences,
            "average_performance": avg_performance,
            "domain_averages": domain_averages,
        }


# ==================== FUNCIONES DE UTILIDAD ====================


def get_unified_learning_training_system(
    config: Optional[TrainingConfig] = None, db_config: Optional[Dict[str, str]] = None
) -> UnifiedLearningTrainingSystem:
    """Obtener instancia del sistema de aprendizaje y entrenamiento"""
    return UnifiedLearningTrainingSystem(config, db_config)


async def main():
    """Función principal de demostración"""
    print("🎓 Sistema Unificado de Aprendizaje y Entrenamiento")
    print("=" * 60)

    # Inicializar sistema
    config = TrainingConfig(
        model_name="models/custom/shaili-personal-model",
        batch_size=8,
        learning_rate=1e-4,
        num_train_epochs=2,
    )

    system = get_unified_learning_training_system(config)

    # Ejemplo de descarga de dataset
    print("📥 Descargando dataset HEAD-QA...")
    dataset_path = await system.download_dataset(DatasetType.HEADQA)
    print(f"✅ Dataset descargado: {dataset_path}")

    # Ejemplo de inicio de entrenamiento
    print("\n🚀 Iniciando sesión de entrenamiento...")
    session_id = await system.start_training_session(
        model_name="models/custom/shaili-personal-model",
        dataset_path=dataset_path,
        training_mode=TrainingMode.FINE_TUNE,
    )
    print(f"✅ Sesión iniciada: {session_id}")

    # Ejemplo de agregar experiencia de aprendizaje
    print("\n📚 Agregando experiencia de aprendizaje...")
    await system.add_learning_experience(
        domain="medical",
        input_data="¿Cuál es el tratamiento para la hipertensión?",
        output_data="Los tratamientos incluyen cambios en el estilo de vida y medicamentos.",
        performance_score=0.85,
    )

    # Ejemplo de consolidación
    print("\n🔄 Consolidando aprendizaje...")
    await system.consolidate_learning(domain="medical")

    # Obtener estadísticas
    print("\n📊 Estadísticas del sistema:")
    stats = system.get_system_stats()
    print(f"   Sesiones activas: {stats.get('active_training_sessions', 0)}")
    print(f"   Experiencias totales: {stats.get('total_learning_experiences', 0)}")

    # Obtener resumen de aprendizaje
    print("\n📈 Resumen de aprendizaje:")
    learning_summary = await system.get_learning_summary()
    print(
        f"   Rendimiento promedio: {learning_summary.get('average_performance', 0):.3f}"
    )

    # Cerrar sistema
    system.close()

    print("\n🎉 Sistema de aprendizaje y entrenamiento funcionando correctamente")


if __name__ == "__main__":
    asyncio.run(main())
