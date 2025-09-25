#!/usr/bin/env python3
"""
Sistema de Sincronización: Entrenamientos → Tokens SHEILY
=======================================================
Conecta el sistema de entrenamientos con la distribución de tokens
"""

import json
import logging
from pathlib import Path
from typing import Dict, List, Optional, Any
from dataclasses import dataclass
from datetime import datetime, timedelta
import threading

# Importar sistemas necesarios
try:
    from ..blockchain.sheily_spl_manager import get_sheily_spl_manager
    from ..blockchain.spl_data_persistence import get_spl_persistence
    from ..blockchain.rate_limiter import get_rate_limiter
    from ..blockchain.transaction_monitor import get_transaction_monitor

    SYSTEMS_AVAILABLE = True
except ImportError:
    logging.warning("Sistemas blockchain no disponibles")
    SYSTEMS_AVAILABLE = False

logger = logging.getLogger(__name__)


@dataclass
class TrainingSession:
    """Sesión de entrenamiento"""

    session_id: str
    user_id: str
    training_type: str
    duration_minutes: int
    difficulty_level: str
    completion_status: str  # 'completed', 'in_progress', 'failed'
    points_earned: int
    tokens_earned: int
    completed_at: Optional[datetime] = None
    metadata: Optional[Dict[str, Any]] = None


@dataclass
class TokenReward:
    """Recompensa de tokens"""

    reward_id: str
    user_id: str
    training_session_id: str
    points_earned: int
    tokens_earned: int
    transaction_id: Optional[str] = None
    minted_at: Optional[datetime] = None
    status: str = "pending"  # 'pending', 'minted', 'failed'


class TrainingTokenSync:
    """Sistema de sincronización entre entrenamientos y tokens"""

    def __init__(
        self, config_path: str = "shaili_ai/config/training_token_config.json"
    ):
        self.config_path = Path(config_path)
        self.lock = threading.Lock()

        # Configuración de recompensas
        self.points_per_training = 10
        self.tokens_per_point = 0.5  # 10 puntos = 5 tokens
        self.min_training_duration = 5  # minutos mínimos
        self.max_daily_tokens = 100  # tokens máximos por día

        # Sistemas blockchain
        if SYSTEMS_AVAILABLE:
            self.spl_manager = get_sheily_spl_manager()
            self.persistence = get_spl_persistence()
            self.rate_limiter = get_rate_limiter()
            self.monitor = get_transaction_monitor()
        else:
            self.spl_manager = None
            self.persistence = None
            self.rate_limiter = None
            self.monitor = None

        # Almacenamiento de sesiones y recompensas
        self.training_sessions: Dict[str, TrainingSession] = {}
        self.token_rewards: Dict[str, TokenReward] = {}

        # Cargar configuración
        self._load_config()

        logger.info("🎯 Sistema de sincronización entrenamientos-tokens inicializado")

    def _load_config(self):
        """Cargar configuración"""
        if self.config_path.exists():
            with open(self.config_path, "r", encoding="utf-8") as f:
                config = json.load(f)

            self.points_per_training = config.get("points_per_training", 10)
            self.tokens_per_point = config.get("tokens_per_point", 0.5)
            self.min_training_duration = config.get("min_training_duration", 5)
            self.max_daily_tokens = config.get("max_daily_tokens", 100)

            logger.info("✅ Configuración de sincronización cargada")
        else:
            self._create_default_config()

    def _create_default_config(self):
        """Crear configuración por defecto"""
        config = {
            "points_per_training": 10,
            "tokens_per_point": 0.5,
            "min_training_duration": 5,
            "max_daily_tokens": 100,
            "training_types": {
                "meditation": {"points": 10, "tokens": 5},
                "breathing": {"points": 8, "tokens": 4},
                "focus": {"points": 12, "tokens": 6},
                "memory": {"points": 15, "tokens": 7.5},
                "creativity": {"points": 10, "tokens": 5},
            },
            "bonus_conditions": {
                "streak_days": {"days": 7, "bonus_tokens": 10},
                "perfect_completion": {"bonus_tokens": 2},
                "long_session": {"minutes": 30, "bonus_tokens": 5},
            },
        }

        self.config_path.parent.mkdir(parents=True, exist_ok=True)
        with open(self.config_path, "w", encoding="utf-8") as f:
            json.dump(config, f, indent=2)

        logger.info("✅ Configuración por defecto creada")

    def start_training_session(
        self, user_id: str, training_type: str, difficulty_level: str = "medium"
    ) -> str:
        """Iniciar sesión de entrenamiento"""
        try:
            with self.lock:
                session_id = f"training_{user_id}_{int(datetime.now().timestamp())}"

                session = TrainingSession(
                    session_id=session_id,
                    user_id=user_id,
                    training_type=training_type,
                    duration_minutes=0,
                    difficulty_level=difficulty_level,
                    completion_status="in_progress",
                    points_earned=0,
                    tokens_earned=0,
                    metadata={
                        "started_at": datetime.now().isoformat(),
                        "difficulty": difficulty_level,
                    },
                )

                self.training_sessions[session_id] = session

                logger.info(f"🎯 Sesión de entrenamiento iniciada: {session_id}")
                return session_id

        except Exception as e:
            logger.error(f"❌ Error iniciando sesión: {e}")
            return None

    def complete_training_session(
        self, session_id: str, duration_minutes: int, completion_quality: float = 1.0
    ) -> Optional[TokenReward]:
        """Completar sesión de entrenamiento y otorgar recompensas"""
        try:
            with self.lock:
                if session_id not in self.training_sessions:
                    logger.error(f"Sesión no encontrada: {session_id}")
                    return None

                session = self.training_sessions[session_id]

                # Verificar duración mínima
                if duration_minutes < self.min_training_duration:
                    logger.warning(f"Sesión muy corta: {duration_minutes} minutos")
                    session.completion_status = "failed"
                    return None

                # Calcular puntos y tokens
                base_points = self.points_per_training
                base_tokens = base_points * self.tokens_per_point

                # Aplicar bonificaciones
                bonus_tokens = 0

                # Bonificación por calidad de completación
                if completion_quality >= 0.9:
                    bonus_tokens += 2  # Perfect completion bonus
                    logger.info(f"🎯 Bonificación por completación perfecta: +2 tokens")

                # Bonificación por sesión larga
                if duration_minutes >= 30:
                    bonus_tokens += 5  # Long session bonus
                    logger.info(f"🎯 Bonificación por sesión larga: +5 tokens")

                # Verificar límite diario
                daily_tokens = self._get_user_daily_tokens(session.user_id)
                total_tokens = base_tokens + bonus_tokens

                if daily_tokens + total_tokens > self.max_daily_tokens:
                    logger.warning(f"Límite diario alcanzado para {session.user_id}")
                    total_tokens = max(0, self.max_daily_tokens - daily_tokens)

                # Actualizar sesión
                session.duration_minutes = duration_minutes
                session.completion_status = "completed"
                session.points_earned = base_points
                session.tokens_earned = total_tokens
                session.completed_at = datetime.now()

                # Crear recompensa de tokens
                reward = TokenReward(
                    reward_id=f"reward_{session_id}",
                    user_id=session.user_id,
                    training_session_id=session_id,
                    points_earned=base_points,
                    tokens_earned=total_tokens,
                    status="pending",
                )

                self.token_rewards[reward.reward_id] = reward

                logger.info(f"🎯 Entrenamiento completado: {session_id}")
                logger.info(f"   Usuario: {session.user_id}")
                logger.info(f"   Puntos: {base_points}")
                logger.info(f"   Tokens: {total_tokens}")
                logger.info(f"   Duración: {duration_minutes} minutos")

                # Mintear tokens si el sistema está disponible
                if SYSTEMS_AVAILABLE and total_tokens > 0:
                    self._mint_training_tokens(reward)

                return reward

        except Exception as e:
            logger.error(f"❌ Error completando sesión: {e}")
            return None

    def _mint_training_tokens(self, reward: TokenReward) -> bool:
        """Mintear tokens por entrenamiento completado"""
        try:
            # Verificar rate limit
            if self.rate_limiter:
                allowed, message = self.rate_limiter.check_rate_limit(
                    reward.user_id, "mint_tokens"
                )
                if not allowed:
                    logger.warning(f"Rate limit alcanzado: {message}")
                    return False

                self.rate_limiter.record_request(reward.user_id, "mint_tokens")

            # Mintear tokens
            if self.spl_manager:
                # Convertir tokens a la unidad correcta (considerando decimales)
                tokens_amount = int(reward.tokens_earned * (10**9))  # 9 decimales

                tx = self.spl_manager.mint_tokens(
                    user_id=reward.user_id,
                    amount=tokens_amount,
                    reason=f"training_completion_{reward.training_session_id}",
                )

                if tx and tx.status == "confirmed":
                    reward.transaction_id = tx.transaction_id
                    reward.minted_at = datetime.now()
                    reward.status = "minted"

                    # Registrar en persistencia
                    if self.persistence:
                        self._save_training_reward(reward)

                    # Registrar evento de monitoreo
                    if self.monitor:
                        self._record_training_event(reward, tx)

                    logger.info(f"✅ Tokens minteados: {reward.tokens_earned} SHEILY")
                    logger.info(f"   Transacción: {tx.transaction_id}")
                    return True
                else:
                    reward.status = "failed"
                    logger.error(
                        f"❌ Error minteando tokens: {tx.status if tx else 'No transaction'}"
                    )
                    return False

            return False

        except Exception as e:
            logger.error(f"❌ Error minteando tokens: {e}")
            reward.status = "failed"
            return False

    def _save_training_reward(self, reward: TokenReward):
        """Guardar recompensa en persistencia"""
        try:
            from ..blockchain.spl_data_persistence import TransactionRecord

            if reward.transaction_id and reward.minted_at:
                transaction = TransactionRecord(
                    transaction_id=reward.transaction_id,
                    signature=None,
                    from_user="training_system",
                    to_user=reward.user_id,
                    amount=int(reward.tokens_earned * (10**9)),
                    token_mint="7p6siXouNRH47npKr1pevTeapnDxUBE4vMD9o7Sc42RP",
                    transaction_type="mint",
                    reason=f"training_reward_{reward.training_session_id}",
                    status="confirmed",
                    created_at=reward.minted_at,
                    confirmed_at=reward.minted_at,
                    block_height=0,
                    fee=0,
                    slot=0,
                    confirmation_status="confirmed",
                    metadata={
                        "training_session_id": reward.training_session_id,
                        "points_earned": reward.points_earned,
                        "tokens_earned": reward.tokens_earned,
                    },
                )

                self.persistence.save_transaction(transaction)

        except Exception as e:
            logger.error(f"❌ Error guardando recompensa: {e}")

    def _record_training_event(self, reward: TokenReward, tx):
        """Registrar evento de entrenamiento en monitoreo"""
        try:
            from ..blockchain.transaction_monitor import (
                TransactionEvent,
                TransactionStatus,
            )

            event = TransactionEvent(
                transaction_id=reward.transaction_id,
                event_type="training_reward",
                status=TransactionStatus.CONFIRMED,
                timestamp=datetime.now(),
                user_id=reward.user_id,
                amount=int(reward.tokens_earned * (10**9)),
                token_mint="7p6siXouNRH47npKr1pevTeapnDxUBE4vMD9o7Sc42RP",
                metadata={
                    "training_session_id": reward.training_session_id,
                    "points_earned": reward.points_earned,
                    "tokens_earned": reward.tokens_earned,
                    "reason": "training_completion",
                },
            )

            self.monitor.record_transaction_event(event)

        except Exception as e:
            logger.error(f"❌ Error registrando evento: {e}")

    def _get_user_daily_tokens(self, user_id: str) -> float:
        """Obtener tokens ganados hoy por usuario"""
        try:
            today = datetime.now().date()
            daily_tokens = 0

            for reward in self.token_rewards.values():
                if (
                    reward.user_id == user_id
                    and reward.minted_at
                    and reward.minted_at.date() == today
                ):
                    daily_tokens += reward.tokens_earned

            return daily_tokens

        except Exception as e:
            logger.error(f"❌ Error calculando tokens diarios: {e}")
            return 0

    def get_user_training_stats(self, user_id: str) -> Dict[str, Any]:
        """Obtener estadísticas de entrenamiento del usuario"""
        try:
            total_sessions = 0
            completed_sessions = 0
            total_points = 0
            total_tokens = 0
            total_duration = 0

            for session in self.training_sessions.values():
                if session.user_id == user_id:
                    total_sessions += 1
                    if session.completion_status == "completed":
                        completed_sessions += 1
                        total_points += session.points_earned
                        total_tokens += session.tokens_earned
                        total_duration += session.duration_minutes

            return {
                "user_id": user_id,
                "total_sessions": total_sessions,
                "completed_sessions": completed_sessions,
                "completion_rate": (
                    completed_sessions / total_sessions if total_sessions > 0 else 0
                ),
                "total_points": total_points,
                "total_tokens": total_tokens,
                "total_duration_minutes": total_duration,
                "average_session_duration": (
                    total_duration / completed_sessions if completed_sessions > 0 else 0
                ),
                "daily_tokens_earned": self._get_user_daily_tokens(user_id),
            }

        except Exception as e:
            logger.error(f"❌ Error obteniendo estadísticas: {e}")
            return {}

    def get_system_training_stats(self) -> Dict[str, Any]:
        """Obtener estadísticas generales del sistema de entrenamiento"""
        try:
            total_sessions = len(self.training_sessions)
            completed_sessions = sum(
                1
                for s in self.training_sessions.values()
                if s.completion_status == "completed"
            )
            total_tokens_minted = sum(
                r.tokens_earned
                for r in self.token_rewards.values()
                if r.status == "minted"
            )

            # Tokens por tipo de entrenamiento
            tokens_by_type = {}
            for session in self.training_sessions.values():
                if session.completion_status == "completed":
                    training_type = session.training_type
                    if training_type not in tokens_by_type:
                        tokens_by_type[training_type] = 0
                    tokens_by_type[training_type] += session.tokens_earned

            return {
                "total_sessions": total_sessions,
                "completed_sessions": completed_sessions,
                "completion_rate": (
                    completed_sessions / total_sessions if total_sessions > 0 else 0
                ),
                "total_tokens_minted": total_tokens_minted,
                "tokens_by_training_type": tokens_by_type,
                "active_users": len(
                    set(s.user_id for s in self.training_sessions.values())
                ),
                "last_updated": datetime.now().isoformat(),
            }

        except Exception as e:
            logger.error(f"❌ Error obteniendo estadísticas del sistema: {e}")
            return {}


# Instancia global
_training_token_sync: Optional[TrainingTokenSync] = None


def get_training_token_sync() -> TrainingTokenSync:
    """Obtener instancia global del sistema de sincronización"""
    global _training_token_sync

    if _training_token_sync is None:
        _training_token_sync = TrainingTokenSync()

    return _training_token_sync
