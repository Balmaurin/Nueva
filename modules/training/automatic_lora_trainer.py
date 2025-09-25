#!/usr/bin/env python3
"""
Sistema de Fine-tuning Automático LoRA
=====================================
Entrena automáticamente modelos LoRA cuando se acumulan suficientes datos
"""

import json
import logging
import subprocess
import threading
import time
from pathlib import Path
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, asdict
from datetime import datetime, timedelta
import sqlite3
import os

logger = logging.getLogger(__name__)


@dataclass
class LoRATrainingConfig:
    """Configuración para entrenamiento LoRA"""

    branch_name: str
    model_name: str = "models/custom/shaili-personal-model"  # Modelo base
    lora_r: int = 16
    lora_alpha: int = 32
    lora_dropout: float = 0.05
    learning_rate: float = 3e-4
    num_epochs: int = 3
    batch_size: int = 4
    max_length: int = 512
    warmup_steps: int = 100
    save_steps: int = 500
    eval_steps: int = 500
    logging_steps: int = 100
    min_data_points: int = 50  # Mínimo de datos para entrenar
    max_data_points: int = 1000  # Máximo de datos por entrenamiento


@dataclass
class LoRATrainingJob:
    """Trabajo de entrenamiento LoRA"""

    job_id: str
    branch_name: str
    dataset_path: str
    config: LoRATrainingConfig
    status: str  # 'pending', 'running', 'completed', 'failed'
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    metrics: Dict[str, Any] = None
    error_message: str = ""
    created_at: datetime = None


class AutomaticLoRATrainer:
    """Sistema de fine-tuning automático LoRA"""

    def __init__(self, db_path: str = "shaili_ai/data/lora_training.db"):
        self.db_path = Path(db_path)
        self.training_queue: List[LoRATrainingJob] = []
        self.running_jobs: Dict[str, LoRATrainingJob] = {}
        self.max_concurrent_jobs = 2
        self.monitoring_thread = None
        self.is_running = False

        # Configuraciones por rama
        self.branch_configs = {
            "ai_ml_specialist": LoRATrainingConfig(
                branch_name="ai_ml_specialist",
                model_name="models/custom/shaili-personal-model",
                min_data_points=30,
            ),
            "mathematics_specialist": LoRATrainingConfig(
                branch_name="mathematics_specialist",
                model_name="models/custom/shaili-personal-model",
                min_data_points=30,
            ),
            "programming_specialist": LoRATrainingConfig(
                branch_name="programming_specialist",
                model_name="models/custom/shaili-personal-model",
                min_data_points=30,
            ),
            "creativity_innovation_specialist": LoRATrainingConfig(
                branch_name="creativity_innovation_specialist",
                model_name="models/custom/shaili-personal-model",
                min_data_points=30,
            ),
            "communication_specialist": LoRATrainingConfig(
                branch_name="communication_specialist",
                model_name="models/custom/shaili-personal-model",
                min_data_points=30,
            ),
            "critical_analysis_specialist": LoRATrainingConfig(
                branch_name="critical_analysis_specialist",
                model_name="models/custom/shaili-personal-model",
                min_data_points=30,
            ),
            "problem_solving_specialist": LoRATrainingConfig(
                branch_name="problem_solving_specialist",
                model_name="models/custom/shaili-personal-model",
                min_data_points=30,
            ),
            "data_science_specialist": LoRATrainingConfig(
                branch_name="data_science_specialist",
                model_name="models/custom/shaili-personal-model",
                min_data_points=30,
            ),
            "leadership_management_specialist": LoRATrainingConfig(
                branch_name="leadership_management_specialist",
                model_name="models/custom/shaili-personal-model",
                min_data_points=30,
            ),
            "entrepreneurship_specialist": LoRATrainingConfig(
                branch_name="entrepreneurship_specialist",
                model_name="models/custom/shaili-personal-model",
                min_data_points=30,
            ),
        }

        # Inicializar base de datos
        self._init_database()

        logger.info("🎯 Sistema de fine-tuning automático LoRA inicializado")

    def _init_database(self):
        """Inicializar base de datos para trabajos de entrenamiento"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()

                # Tabla de trabajos de entrenamiento LoRA
                cursor.execute(
                    """
                    CREATE TABLE IF NOT EXISTS lora_training_jobs (
                        job_id TEXT PRIMARY KEY,
                        branch_name TEXT NOT NULL,
                        dataset_path TEXT NOT NULL,
                        config TEXT NOT NULL,
                        status TEXT NOT NULL,
                        start_time TIMESTAMP,
                        end_time TIMESTAMP,
                        metrics TEXT,
                        error_message TEXT,
                        created_at TIMESTAMP NOT NULL
                    )
                """
                )

                # Tabla de modelos LoRA entrenados
                cursor.execute(
                    """
                    CREATE TABLE IF NOT EXISTS trained_lora_models (
                        model_id TEXT PRIMARY KEY,
                        branch_name TEXT NOT NULL,
                        job_id TEXT NOT NULL,
                        model_path TEXT NOT NULL,
                        training_metrics TEXT NOT NULL,
                        data_points_used INTEGER NOT NULL,
                        training_duration_minutes INTEGER NOT NULL,
                        created_at TIMESTAMP NOT NULL,
                        is_active BOOLEAN DEFAULT TRUE
                    )
                """
                )

                conn.commit()

        except Exception as e:
            logger.error(f"❌ Error inicializando base de datos: {e}")

    def start_monitoring(self):
        """Iniciar monitoreo automático de datos para entrenamiento"""
        if self.monitoring_thread is None or not self.monitoring_thread.is_alive():
            self.is_running = True
            self.monitoring_thread = threading.Thread(
                target=self._monitoring_loop, daemon=True
            )
            self.monitoring_thread.start()
            logger.info("🔍 Monitoreo automático iniciado")

    def stop_monitoring(self):
        """Detener monitoreo automático"""
        self.is_running = False
        if self.monitoring_thread:
            self.monitoring_thread.join(timeout=5)
        logger.info("⏹️ Monitoreo automático detenido")

    def _monitoring_loop(self):
        """Bucle de monitoreo automático"""
        while self.is_running:
            try:
                # Verificar si hay suficientes datos para entrenar
                self._check_and_schedule_training()

                # Procesar cola de entrenamiento
                self._process_training_queue()

                # Esperar antes de la siguiente verificación
                time.sleep(300)  # 5 minutos

            except Exception as e:
                logger.error(f"❌ Error en bucle de monitoreo: {e}")
                time.sleep(60)  # 1 minuto en caso de error

    def _check_and_schedule_training(self):
        """Verificar y programar entrenamientos automáticos"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()

                # Obtener estadísticas de datos por rama
                cursor.execute(
                    """
                    SELECT branch_name, COUNT(*) as data_count
                    FROM lora_training_data
                    GROUP BY branch_name
                """
                )

                results = cursor.fetchall()

                for branch_name, data_count in results:
                    if branch_name in self.branch_configs:
                        config = self.branch_configs[branch_name]

                        # Verificar si hay suficientes datos y no hay entrenamiento reciente
                        if data_count >= config.min_data_points:
                            # Verificar si ya hay un trabajo pendiente o reciente
                            cursor.execute(
                                """
                                SELECT COUNT(*) FROM lora_training_jobs
                                WHERE branch_name = ? AND status IN ('pending', 'running')
                                AND created_at > datetime('now', '-1 hour')
                            """,
                                (branch_name,),
                            )

                            recent_jobs = cursor.fetchone()[0]

                            if recent_jobs == 0:
                                # Programar entrenamiento automático
                                self._schedule_training(branch_name, data_count)

        except Exception as e:
            logger.error(f"❌ Error verificando entrenamientos: {e}")

    def _schedule_training(self, branch_name: str, data_count: int):
        """Programar entrenamiento automático"""
        try:
            # Generar dataset actualizado
            from .lora_finetuning_generator import get_lora_generator

            lora_generator = get_lora_generator()

            dataset_path = lora_generator.export_lora_dataset(branch_name)

            if dataset_path and Path(dataset_path).exists():
                # Crear trabajo de entrenamiento
                job_id = f"lora_job_{branch_name}_{int(datetime.now().timestamp())}"
                config = self.branch_configs[branch_name]

                training_job = LoRATrainingJob(
                    job_id=job_id,
                    branch_name=branch_name,
                    dataset_path=dataset_path,
                    config=config,
                    status="pending",
                    created_at=datetime.now(),
                )

                # Guardar en base de datos
                self._save_training_job(training_job)

                # Agregar a cola
                self.training_queue.append(training_job)

                logger.info(
                    f"📅 Entrenamiento programado para {branch_name} con {data_count} datos"
                )

        except Exception as e:
            logger.error(f"❌ Error programando entrenamiento: {e}")

    def _save_training_job(self, job: LoRATrainingJob):
        """Guardar trabajo de entrenamiento en base de datos"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()

                cursor.execute(
                    """
                    INSERT INTO lora_training_jobs 
                    (job_id, branch_name, dataset_path, config, status, start_time, 
                     end_time, metrics, error_message, created_at)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                    (
                        job.job_id,
                        job.branch_name,
                        job.dataset_path,
                        json.dumps(asdict(job.config)),
                        job.status,
                        job.start_time.isoformat() if job.start_time else None,
                        job.end_time.isoformat() if job.end_time else None,
                        json.dumps(job.metrics) if job.metrics else None,
                        job.error_message,
                        job.created_at.isoformat(),
                    ),
                )

                conn.commit()

        except Exception as e:
            logger.error(f"❌ Error guardando trabajo: {e}")

    def _process_training_queue(self):
        """Procesar cola de entrenamiento"""
        # Remover trabajos completados
        self.training_queue = [
            job for job in self.training_queue if job.status == "pending"
        ]

        # Procesar trabajos pendientes
        for job in self.training_queue[: self.max_concurrent_jobs]:
            if len(self.running_jobs) < self.max_concurrent_jobs:
                self._start_training_job(job)

    def _start_training_job(self, job: LoRATrainingJob):
        """Iniciar trabajo de entrenamiento"""
        try:
            job.status = "running"
            job.start_time = datetime.now()
            self.running_jobs[job.job_id] = job

            # Actualizar en base de datos
            self._update_job_status(job)

            # Iniciar entrenamiento en hilo separado
            training_thread = threading.Thread(
                target=self._run_training_job, args=(job,), daemon=True
            )
            training_thread.start()

            logger.info(f"🚀 Iniciando entrenamiento LoRA para {job.branch_name}")

        except Exception as e:
            logger.error(f"❌ Error iniciando trabajo: {e}")
            job.status = "failed"
            job.error_message = str(e)
            self._update_job_status(job)

    def _run_training_job(self, job: LoRATrainingJob):
        """Ejecutar trabajo de entrenamiento"""
        try:
            # Crear directorio de salida
            output_dir = Path(f"shaili_ai/models/lora/{job.branch_name}")
            output_dir.mkdir(parents=True, exist_ok=True)

            # Generar script de entrenamiento
            training_script = self._generate_training_script(job, output_dir)

            # Ejecutar entrenamiento
            result = subprocess.run(
                ["python", training_script],
                capture_output=True,
                text=True,
                timeout=3600,  # 1 hora máximo
            )

            if result.returncode == 0:
                # Entrenamiento exitoso
                job.status = "completed"
                job.end_time = datetime.now()
                job.metrics = self._parse_training_metrics(result.stdout)

                # Guardar modelo entrenado
                self._save_trained_model(job, output_dir)

                logger.info(f"✅ Entrenamiento completado para {job.branch_name}")

            else:
                # Error en entrenamiento
                job.status = "failed"
                job.end_time = datetime.now()
                job.error_message = result.stderr

                logger.error(
                    f"❌ Error en entrenamiento para {job.branch_name}: {result.stderr}"
                )

            # Actualizar estado
            self._update_job_status(job)

            # Remover de trabajos en ejecución
            if job.job_id in self.running_jobs:
                del self.running_jobs[job.job_id]

        except Exception as e:
            logger.error(f"❌ Error ejecutando entrenamiento: {e}")
            job.status = "failed"
            job.error_message = str(e)
            job.end_time = datetime.now()
            self._update_job_status(job)

    def _generate_training_script(self, job: LoRATrainingJob, output_dir: Path) -> str:
        """Generar script de entrenamiento LoRA"""
        script_content = f'''#!/usr/bin/env python3
"""
Script de Entrenamiento LoRA Automático para {job.branch_name}
"""

import os
import sys
from pathlib import Path

# Agregar ruta del proyecto
sys.path.append(str(Path.cwd()))

def train_lora():
    """Entrenar modelo LoRA"""
    try:
        from transformers import (
            AutoTokenizer, AutoModelForCausalLM, 
            TrainingArguments, Trainer, DataCollatorForLanguageModeling
        )
        from peft import LoraConfig, get_peft_model, TaskType
        import torch
        from datasets import Dataset
        import json
        
        # Configuración
        model_name = "{job.config.model_name}"
        dataset_path = "{job.dataset_path}"
        output_dir = "{output_dir}"
        
        # Cargar tokenizador y modelo
        tokenizer = AutoTokenizer.from_pretrained(model_name)
        model = AutoModelForCausalLM.from_pretrained(model_name)
        
        # Configurar LoRA
        lora_config = LoraConfig(
            task_type=TaskType.CAUSAL_LM,
            r={job.config.lora_r},
            lora_alpha={job.config.lora_alpha},
            lora_dropout={job.config.lora_dropout},
            target_modules=["q_proj", "v_proj"]
        )
        
        # Aplicar LoRA al modelo
        model = get_peft_model(model, lora_config)
        
        # Cargar dataset
        with open(dataset_path, 'r', encoding='utf-8') as f:
            data = [json.loads(line) for line in f]
        
        # Preparar datos
        def tokenize_function(examples):
            texts = [f"Instruction: {{ex['instruction']}}\\nOutput: {{ex['output']}}" for ex in examples]
            return tokenizer(texts, truncation=True, padding=True, max_length={job.config.max_length})
        
        dataset = Dataset.from_list(data)
        tokenized_dataset = dataset.map(tokenize_function, batched=True)
        
        # Configurar entrenamiento
        training_args = TrainingArguments(
            output_dir=output_dir,
            num_train_epochs={job.config.num_epochs},
            per_device_train_batch_size={job.config.batch_size},
            learning_rate={job.config.learning_rate},
            warmup_steps={job.config.warmup_steps},
            save_steps={job.config.save_steps},
            eval_steps={job.config.eval_steps},
            logging_steps={job.config.logging_steps},
            save_total_limit=2,
            prediction_loss_only=True,
            remove_unused_columns=False,
        )
        
        # Data collator
        data_collator = DataCollatorForLanguageModeling(
            tokenizer=tokenizer,
            mlm=False
        )
        
        # Trainer
        trainer = Trainer(
            model=model,
            args=training_args,
            train_dataset=tokenized_dataset,
            data_collator=data_collator,
        )
        
        # Entrenar
        trainer.train()
        
        # Guardar modelo
        trainer.save_model()
        tokenizer.save_pretrained(output_dir)
        
        print("Training completed successfully!")
        return True
        
    except Exception as e:
        print(f"Training failed: {{e}}")
        return False

if __name__ == "__main__":
    success = train_lora()
    sys.exit(0 if success else 1)
'''

        # Guardar script
        script_path = output_dir / "train_lora.py"
        with open(script_path, "w", encoding="utf-8") as f:
            f.write(script_content)

        return str(script_path)

    def _parse_training_metrics(self, output: str) -> Dict[str, Any]:
        """Parsear métricas de entrenamiento desde la salida"""
        try:
            metrics = {
                "training_loss": 0.0,
                "final_loss": 0.0,
                "training_time_minutes": 0,
                "steps_completed": 0,
            }

            # Parsear métricas básicas (simplificado)
            lines = output.split("\n")
            for line in lines:
                if "loss" in line.lower():
                    try:
                        loss = float(line.split()[-1])
                        metrics["final_loss"] = loss
                    except:
                        pass

            return metrics

        except Exception as e:
            logger.error(f"❌ Error parseando métricas: {e}")
            return {"error": str(e)}

    def _save_trained_model(self, job: LoRATrainingJob, output_dir: Path):
        """Guardar información del modelo entrenado"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()

                model_id = (
                    f"lora_model_{job.branch_name}_{int(datetime.now().timestamp())}"
                )
                training_duration = (job.end_time - job.start_time).total_seconds() / 60

                cursor.execute(
                    """
                    INSERT INTO trained_lora_models 
                    (model_id, branch_name, job_id, model_path, training_metrics, 
                     data_points_used, training_duration_minutes, created_at)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """,
                    (
                        model_id,
                        job.branch_name,
                        job.job_id,
                        str(output_dir),
                        json.dumps(job.metrics),
                        len(self._get_dataset_size(job.dataset_path)),
                        int(training_duration),
                        datetime.now().isoformat(),
                    ),
                )

                conn.commit()

        except Exception as e:
            logger.error(f"❌ Error guardando modelo: {e}")

    def _get_dataset_size(self, dataset_path: str) -> int:
        """Obtener tamaño del dataset"""
        try:
            with open(dataset_path, "r", encoding="utf-8") as f:
                return len(f.readlines())
        except:
            return 0

    def _update_job_status(self, job: LoRATrainingJob):
        """Actualizar estado del trabajo en base de datos"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()

                cursor.execute(
                    """
                    UPDATE lora_training_jobs 
                    SET status = ?, start_time = ?, end_time = ?, 
                        metrics = ?, error_message = ?
                    WHERE job_id = ?
                """,
                    (
                        job.status,
                        job.start_time.isoformat() if job.start_time else None,
                        job.end_time.isoformat() if job.end_time else None,
                        json.dumps(job.metrics) if job.metrics else None,
                        job.error_message,
                        job.job_id,
                    ),
                )

                conn.commit()

        except Exception as e:
            logger.error(f"❌ Error actualizando estado: {e}")

    def get_training_status(self) -> Dict[str, Any]:
        """Obtener estado de entrenamientos"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()

                # Trabajos recientes
                cursor.execute(
                    """
                    SELECT branch_name, status, created_at, start_time, end_time
                    FROM lora_training_jobs
                    ORDER BY created_at DESC
                    LIMIT 10
                """
                )

                recent_jobs = []
                for row in cursor.fetchall():
                    recent_jobs.append(
                        {
                            "branch_name": row[0],
                            "status": row[1],
                            "created_at": row[2],
                            "start_time": row[3],
                            "end_time": row[4],
                        }
                    )

                # Modelos entrenados
                cursor.execute(
                    """
                    SELECT branch_name, model_path, training_metrics, created_at
                    FROM trained_lora_models
                    WHERE is_active = TRUE
                    ORDER BY created_at DESC
                """
                )

                trained_models = []
                for row in cursor.fetchall():
                    trained_models.append(
                        {
                            "branch_name": row[0],
                            "model_path": row[1],
                            "metrics": json.loads(row[2]),
                            "created_at": row[3],
                        }
                    )

                return {
                    "recent_jobs": recent_jobs,
                    "trained_models": trained_models,
                    "queue_size": len(self.training_queue),
                    "running_jobs": len(self.running_jobs),
                }

        except Exception as e:
            logger.error(f"❌ Error obteniendo estado: {e}")
            return {}


# Instancia global
_automatic_trainer: Optional[AutomaticLoRATrainer] = None


def get_automatic_trainer() -> AutomaticLoRATrainer:
    """Obtener instancia global del entrenador automático"""
    global _automatic_trainer

    if _automatic_trainer is None:
        _automatic_trainer = AutomaticLoRATrainer()

    return _automatic_trainer
