#!/usr/bin/env python3
"""
Sistema de Rate Limiting para SPL
================================
Control de frecuencia de transacciones y operaciones
"""

import time
import logging
from pathlib import Path
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass
from datetime import datetime, timedelta
import threading
from collections import defaultdict, deque
import json

logger = logging.getLogger(__name__)


@dataclass
class RateLimitConfig:
    """Configuración de rate limit"""

    max_requests: int
    time_window: int  # segundos
    burst_limit: int = 5
    cooldown_period: int = 60  # segundos


@dataclass
class RateLimitRule:
    """Regla de rate limit"""

    rule_id: str
    description: str
    config: RateLimitConfig
    enabled: bool = True


@dataclass
class RateLimitViolation:
    """Violación de rate limit"""

    user_id: str
    rule_id: str
    timestamp: datetime
    request_count: int
    max_allowed: int
    time_window: int
    cooldown_until: Optional[datetime] = None


class RateLimiter:
    """Sistema de rate limiting"""

    def __init__(self, config_path: str = "shaili_ai/config/rate_limits.json"):
        self.config_path = Path(config_path)
        self.lock = threading.Lock()

        # Configuración de rate limits
        self.rules: Dict[str, RateLimitRule] = {}

        # Almacenamiento de requests por usuario
        self.user_requests: Dict[str, Dict[str, deque]] = defaultdict(
            lambda: defaultdict(deque)
        )

        # Historial de violaciones
        self.violations: List[RateLimitViolation] = []

        # Usuarios en cooldown
        self.cooldown_users: Dict[str, Dict[str, datetime]] = defaultdict(dict)

        # Cargar configuración
        self._load_config()

        logger.info("🚦 Sistema de rate limiting inicializado")

    def _load_config(self):
        """Cargar configuración de rate limits"""
        if self.config_path.exists():
            with open(self.config_path, "r", encoding="utf-8") as f:
                config_data = json.load(f)

            for rule_data in config_data.get("rules", []):
                rule = RateLimitRule(
                    rule_id=rule_data["rule_id"],
                    description=rule_data["description"],
                    config=RateLimitConfig(
                        max_requests=rule_data["config"]["max_requests"],
                        time_window=rule_data["config"]["time_window"],
                        burst_limit=rule_data["config"].get("burst_limit", 5),
                        cooldown_period=rule_data["config"].get("cooldown_period", 60),
                    ),
                    enabled=rule_data.get("enabled", True),
                )
                self.rules[rule.rule_id] = rule

            logger.info(
                f"✅ Configuración de rate limits cargada: {len(self.rules)} reglas"
            )
        else:
            # Configuración por defecto
            self._create_default_config()

    def _create_default_config(self):
        """Crear configuración por defecto"""
        default_rules = [
            RateLimitRule(
                rule_id="mint_tokens",
                description="Limite de minteo de tokens",
                config=RateLimitConfig(
                    max_requests=10, time_window=3600, burst_limit=3
                ),
            ),
            RateLimitRule(
                rule_id="transfer_tokens",
                description="Limite de transferencias",
                config=RateLimitConfig(
                    max_requests=50, time_window=3600, burst_limit=10
                ),
            ),
            RateLimitRule(
                rule_id="burn_tokens",
                description="Limite de quema de tokens",
                config=RateLimitConfig(max_requests=5, time_window=3600, burst_limit=2),
            ),
            RateLimitRule(
                rule_id="create_account",
                description="Limite de creación de cuentas",
                config=RateLimitConfig(max_requests=3, time_window=3600, burst_limit=1),
            ),
            RateLimitRule(
                rule_id="api_requests",
                description="Limite general de API",
                config=RateLimitConfig(
                    max_requests=100, time_window=3600, burst_limit=20
                ),
            ),
        ]

        for rule in default_rules:
            self.rules[rule.rule_id] = rule

        # Guardar configuración por defecto
        self._save_config()

        logger.info("✅ Configuración por defecto de rate limits creada")

    def _save_config(self):
        """Guardar configuración"""
        config_data = {
            "rules": [
                {
                    "rule_id": rule.rule_id,
                    "description": rule.description,
                    "config": {
                        "max_requests": rule.config.max_requests,
                        "time_window": rule.config.time_window,
                        "burst_limit": rule.config.burst_limit,
                        "cooldown_period": rule.config.cooldown_period,
                    },
                    "enabled": rule.enabled,
                }
                for rule in self.rules.values()
            ]
        }

        self.config_path.parent.mkdir(parents=True, exist_ok=True)
        with open(self.config_path, "w", encoding="utf-8") as f:
            json.dump(config_data, f, indent=2)

    def _cleanup_old_requests(self, user_id: str, rule_id: str):
        """Limpiar requests antiguos"""
        current_time = time.time()
        rule = self.rules.get(rule_id)
        if not rule:
            return

        # Remover requests fuera de la ventana de tiempo
        cutoff_time = current_time - rule.config.time_window
        requests = self.user_requests[user_id][rule_id]

        while requests and requests[0] < cutoff_time:
            requests.popleft()

    def _is_in_cooldown(self, user_id: str, rule_id: str) -> bool:
        """Verificar si usuario está en cooldown"""
        if user_id in self.cooldown_users and rule_id in self.cooldown_users[user_id]:
            cooldown_until = self.cooldown_users[user_id][rule_id]
            if datetime.now() < cooldown_until:
                return True
            else:
                # Remover cooldown expirado
                del self.cooldown_users[user_id][rule_id]
        return False

    def check_rate_limit(
        self, user_id: str, rule_id: str
    ) -> Tuple[bool, Optional[str]]:
        """Verificar rate limit para usuario y regla"""
        try:
            with self.lock:
                rule = self.rules.get(rule_id)
                if not rule or not rule.enabled:
                    return True, None  # Sin límite

                # Verificar cooldown
                if self._is_in_cooldown(user_id, rule_id):
                    cooldown_until = self.cooldown_users[user_id][rule_id]
                    return False, f"Usuario en cooldown hasta {cooldown_until}"

                # Limpiar requests antiguos
                self._cleanup_old_requests(user_id, rule_id)

                # Obtener requests actuales
                requests = self.user_requests[user_id][rule_id]
                current_count = len(requests)

                # Verificar límite
                if current_count >= rule.config.max_requests:
                    # Aplicar cooldown
                    cooldown_until = datetime.now() + timedelta(
                        seconds=rule.config.cooldown_period
                    )
                    self.cooldown_users[user_id][rule_id] = cooldown_until

                    # Registrar violación
                    violation = RateLimitViolation(
                        user_id=user_id,
                        rule_id=rule_id,
                        timestamp=datetime.now(),
                        request_count=current_count,
                        max_allowed=rule.config.max_requests,
                        time_window=rule.config.time_window,
                        cooldown_until=cooldown_until,
                    )
                    self.violations.append(violation)

                    logger.warning(f"🚫 Rate limit violado: {user_id} - {rule_id}")
                    return (
                        False,
                        f"Rate limit excedido. Cooldown hasta {cooldown_until}",
                    )

                # Verificar burst limit
                if current_count >= rule.config.burst_limit:
                    # Verificar si hay requests recientes
                    current_time = time.time()
                    recent_requests = sum(
                        1 for req_time in requests if current_time - req_time < 60
                    )  # últimos 60 segundos

                    if recent_requests >= rule.config.burst_limit:
                        return False, "Burst limit excedido. Intente más tarde"

                return True, None

        except Exception as e:
            logger.error(f"❌ Error verificando rate limit: {e}")
            return False, "Error interno"

    def record_request(self, user_id: str, rule_id: str) -> bool:
        """Registrar request de usuario"""
        try:
            with self.lock:
                current_time = time.time()
                self.user_requests[user_id][rule_id].append(current_time)

                # Limitar tamaño del historial
                max_history = (
                    self.rules.get(
                        rule_id, RateLimitRule("", "", RateLimitConfig(100, 3600))
                    ).config.max_requests
                    * 2
                )
                requests = self.user_requests[user_id][rule_id]
                while len(requests) > max_history:
                    requests.popleft()

                return True

        except Exception as e:
            logger.error(f"❌ Error registrando request: {e}")
            return False

    def get_user_stats(self, user_id: str) -> Dict[str, Any]:
        """Obtener estadísticas de usuario"""
        try:
            stats = {}
            current_time = time.time()

            for rule_id, rule in self.rules.items():
                if rule_id in self.user_requests[user_id]:
                    requests = self.user_requests[user_id][rule_id]

                    # Limpiar requests antiguos
                    cutoff_time = current_time - rule.config.time_window
                    recent_requests = [
                        req_time for req_time in requests if req_time >= cutoff_time
                    ]

                    stats[rule_id] = {
                        "current_requests": len(recent_requests),
                        "max_requests": rule.config.max_requests,
                        "time_window": rule.config.time_window,
                        "burst_limit": rule.config.burst_limit,
                        "in_cooldown": self._is_in_cooldown(user_id, rule_id),
                        "cooldown_until": self.cooldown_users.get(user_id, {}).get(
                            rule_id
                        ),
                    }
                else:
                    stats[rule_id] = {
                        "current_requests": 0,
                        "max_requests": rule.config.max_requests,
                        "time_window": rule.config.time_window,
                        "burst_limit": rule.config.burst_limit,
                        "in_cooldown": False,
                        "cooldown_until": None,
                    }

            return stats

        except Exception as e:
            logger.error(f"❌ Error obteniendo estadísticas de usuario: {e}")
            return {}

    def get_system_stats(self) -> Dict[str, Any]:
        """Obtener estadísticas del sistema"""
        try:
            total_users = len(self.user_requests)
            total_violations = len(self.violations)

            # Violaciones por regla
            violations_by_rule = defaultdict(int)
            for violation in self.violations:
                violations_by_rule[violation.rule_id] += 1

            # Usuarios en cooldown
            users_in_cooldown = sum(
                1 for user_cooldowns in self.cooldown_users.values() if user_cooldowns
            )

            return {
                "total_users": total_users,
                "total_violations": total_violations,
                "violations_by_rule": dict(violations_by_rule),
                "users_in_cooldown": users_in_cooldown,
                "active_rules": len([r for r in self.rules.values() if r.enabled]),
                "last_updated": datetime.now().isoformat(),
            }

        except Exception as e:
            logger.error(f"❌ Error obteniendo estadísticas del sistema: {e}")
            return {}

    def add_rate_limit_rule(self, rule: RateLimitRule) -> bool:
        """Agregar nueva regla de rate limit"""
        try:
            with self.lock:
                self.rules[rule.rule_id] = rule
                self._save_config()

                logger.info(f"✅ Nueva regla de rate limit agregada: {rule.rule_id}")
                return True

        except Exception as e:
            logger.error(f"❌ Error agregando regla de rate limit: {e}")
            return False

    def update_rate_limit_rule(self, rule_id: str, config: RateLimitConfig) -> bool:
        """Actualizar regla de rate limit"""
        try:
            with self.lock:
                if rule_id not in self.rules:
                    logger.error(f"Regla no encontrada: {rule_id}")
                    return False

                self.rules[rule_id].config = config
                self._save_config()

                logger.info(f"✅ Regla de rate limit actualizada: {rule_id}")
                return True

        except Exception as e:
            logger.error(f"❌ Error actualizando regla de rate limit: {e}")
            return False

    def enable_rate_limit_rule(self, rule_id: str) -> bool:
        """Habilitar regla de rate limit"""
        try:
            with self.lock:
                if rule_id not in self.rules:
                    logger.error(f"Regla no encontrada: {rule_id}")
                    return False

                self.rules[rule_id].enabled = True
                self._save_config()

                logger.info(f"✅ Regla de rate limit habilitada: {rule_id}")
                return True

        except Exception as e:
            logger.error(f"❌ Error habilitando regla de rate limit: {e}")
            return False

    def disable_rate_limit_rule(self, rule_id: str) -> bool:
        """Deshabilitar regla de rate limit"""
        try:
            with self.lock:
                if rule_id not in self.rules:
                    logger.error(f"Regla no encontrada: {rule_id}")
                    return False

                self.rules[rule_id].enabled = False
                self._save_config()

                logger.info(f"✅ Regla de rate limit deshabilitada: {rule_id}")
                return True

        except Exception as e:
            logger.error(f"❌ Error deshabilitando regla de rate limit: {e}")
            return False

    def reset_user_limits(self, user_id: str) -> bool:
        """Resetear límites de usuario"""
        try:
            with self.lock:
                if user_id in self.user_requests:
                    del self.user_requests[user_id]

                if user_id in self.cooldown_users:
                    del self.cooldown_users[user_id]

                logger.info(f"✅ Límites reseteados para usuario: {user_id}")
                return True

        except Exception as e:
            logger.error(f"❌ Error reseteando límites de usuario: {e}")
            return False

    def clear_violations(self, days: int = 30) -> int:
        """Limpiar violaciones antiguas"""
        try:
            with self.lock:
                cutoff_date = datetime.now() - timedelta(days=days)
                original_count = len(self.violations)

                self.violations = [
                    v for v in self.violations if v.timestamp >= cutoff_date
                ]

                cleared_count = original_count - len(self.violations)
                logger.info(f"✅ {cleared_count} violaciones limpiadas")
                return cleared_count

        except Exception as e:
            logger.error(f"❌ Error limpiando violaciones: {e}")
            return 0


# Instancia global
_rate_limiter: Optional[RateLimiter] = None


def get_rate_limiter() -> RateLimiter:
    """Obtener instancia global del rate limiter"""
    global _rate_limiter

    if _rate_limiter is None:
        _rate_limiter = RateLimiter()

    return _rate_limiter
