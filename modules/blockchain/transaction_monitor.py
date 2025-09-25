#!/usr/bin/env python3
"""
Sistema de Monitoreo de Transacciones SPL
========================================
Monitoreo y alertas de transacciones en tiempo real
"""

import json
import logging
from pathlib import Path
from typing import Dict, List, Optional, Any, Callable
from dataclasses import dataclass
from datetime import datetime, timedelta
import threading
import time
from collections import defaultdict, deque
import asyncio
from enum import Enum

logger = logging.getLogger(__name__)


class TransactionStatus(Enum):
    """Estados de transacción"""

    PENDING = "pending"
    CONFIRMED = "confirmed"
    FAILED = "failed"
    EXPIRED = "expired"
    CANCELLED = "cancelled"


class AlertLevel(Enum):
    """Niveles de alerta"""

    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"


@dataclass
class TransactionEvent:
    """Evento de transacción"""

    transaction_id: str
    event_type: str
    status: TransactionStatus
    timestamp: datetime
    user_id: str
    amount: int
    token_mint: str
    metadata: Optional[Dict[str, Any]] = None


@dataclass
class Alert:
    """Alerta del sistema"""

    alert_id: str
    level: AlertLevel
    title: str
    message: str
    timestamp: datetime
    transaction_id: Optional[str] = None
    user_id: Optional[str] = None
    resolved: bool = False
    metadata: Optional[Dict[str, Any]] = None


@dataclass
class MonitoringRule:
    """Regla de monitoreo"""

    rule_id: str
    name: str
    description: str
    enabled: bool = True
    conditions: Optional[Dict[str, Any]] = None
    actions: Optional[List[str]] = None


class TransactionMonitor:
    """Sistema de monitoreo de transacciones"""

    def __init__(self, config_path: str = "shaili_ai/config/monitoring_config.json"):
        self.config_path = Path(config_path)
        self.lock = threading.Lock()

        # Configuración de monitoreo
        self.monitoring_rules: Dict[str, MonitoringRule] = {}

        # Eventos de transacciones
        self.transaction_events: List[TransactionEvent] = []

        # Alertas activas
        self.active_alerts: List[Alert] = []

        # Métricas de transacciones
        self.transaction_metrics: Dict[str, Any] = defaultdict(int)

        # Callbacks de alerta
        self.alert_callbacks: List[Callable[[Alert], None]] = []

        # Estado del monitoreo
        self.monitoring_enabled = True
        self.alert_thresholds = {
            "failed_transactions": 10,
            "pending_timeout": 300,  # segundos
            "high_value_transaction": 10000,
            "suspicious_activity": 5,
        }

        # Cargar configuración
        self._load_config()

        # Iniciar monitoreo en background
        self._start_background_monitoring()

        logger.info("📊 Sistema de monitoreo de transacciones inicializado")

    def _load_config(self):
        """Cargar configuración de monitoreo"""
        if self.config_path.exists():
            with open(self.config_path, "r", encoding="utf-8") as f:
                config_data = json.load(f)

            self.monitoring_enabled = config_data.get("enabled", True)
            self.alert_thresholds = config_data.get(
                "alert_thresholds", self.alert_thresholds
            )

            # Cargar reglas de monitoreo
            for rule_data in config_data.get("monitoring_rules", []):
                rule = MonitoringRule(
                    rule_id=rule_data["rule_id"],
                    name=rule_data["name"],
                    description=rule_data["description"],
                    enabled=rule_data.get("enabled", True),
                    conditions=rule_data.get("conditions"),
                    actions=rule_data.get("actions", []),
                )
                self.monitoring_rules[rule.rule_id] = rule

            logger.info(
                f"✅ Configuración de monitoreo cargada: {len(self.monitoring_rules)} reglas"
            )
        else:
            self._create_default_config()

    def _create_default_config(self):
        """Crear configuración por defecto"""
        default_rules = [
            MonitoringRule(
                rule_id="failed_transactions",
                name="Transacciones Fallidas",
                description="Alerta cuando hay muchas transacciones fallidas",
                conditions={"max_failed": 10, "time_window": 3600},
            ),
            MonitoringRule(
                rule_id="pending_timeout",
                name="Timeout de Transacciones Pendientes",
                description="Alerta cuando transacciones están pendientes por mucho tiempo",
                conditions={"max_pending_time": 300},
            ),
            MonitoringRule(
                rule_id="high_value_transactions",
                name="Transacciones de Alto Valor",
                description="Alerta para transacciones de alto valor",
                conditions={"min_amount": 10000},
            ),
            MonitoringRule(
                rule_id="suspicious_activity",
                name="Actividad Sospechosa",
                description="Alerta para actividad sospechosa",
                conditions={"max_transactions_per_user": 5, "time_window": 300},
            ),
        ]

        for rule in default_rules:
            self.monitoring_rules[rule.rule_id] = rule

        self._save_config()
        logger.info("✅ Configuración por defecto de monitoreo creada")

    def _save_config(self):
        """Guardar configuración"""
        config_data = {
            "enabled": self.monitoring_enabled,
            "alert_thresholds": self.alert_thresholds,
            "monitoring_rules": [
                {
                    "rule_id": rule.rule_id,
                    "name": rule.name,
                    "description": rule.description,
                    "enabled": rule.enabled,
                    "conditions": rule.conditions,
                    "actions": rule.actions,
                }
                for rule in self.monitoring_rules.values()
            ],
        }

        self.config_path.parent.mkdir(parents=True, exist_ok=True)
        with open(self.config_path, "w", encoding="utf-8") as f:
            json.dump(config_data, f, indent=2)

    def _start_background_monitoring(self):
        """Iniciar monitoreo en background"""

        def background_monitor():
            while self.monitoring_enabled:
                try:
                    self._check_monitoring_rules()
                    time.sleep(30)  # Verificar cada 30 segundos
                except Exception as e:
                    logger.error(f"❌ Error en monitoreo background: {e}")
                    time.sleep(60)  # Esperar más tiempo en caso de error

        monitor_thread = threading.Thread(target=background_monitor, daemon=True)
        monitor_thread.start()
        logger.info("✅ Monitoreo background iniciado")

    def record_transaction_event(self, event: TransactionEvent) -> bool:
        """Registrar evento de transacción"""
        try:
            with self.lock:
                self.transaction_events.append(event)

                # Actualizar métricas
                self._update_metrics(event)

                # Verificar reglas de monitoreo
                self._check_event_rules(event)

                # Limpiar eventos antiguos (mantener solo últimos 1000)
                if len(self.transaction_events) > 1000:
                    self.transaction_events = self.transaction_events[-1000:]

                logger.debug(
                    f"📝 Evento registrado: {event.transaction_id} - {event.event_type}"
                )
                return True

        except Exception as e:
            logger.error(f"❌ Error registrando evento: {e}")
            return False

    def _update_metrics(self, event: TransactionEvent):
        """Actualizar métricas de transacciones"""
        # Contador por estado
        self.transaction_metrics[f"status_{event.status.value}"] += 1

        # Contador por usuario
        self.transaction_metrics[f"user_{event.user_id}"] += 1

        # Contador por token
        self.transaction_metrics[f"token_{event.token_mint}"] += 1

        # Contador por tipo de evento
        self.transaction_metrics[f"event_{event.event_type}"] += 1

        # Total de transacciones
        self.transaction_metrics["total_transactions"] += 1

    def _check_event_rules(self, event: TransactionEvent):
        """Verificar reglas de monitoreo para evento"""
        for rule in self.monitoring_rules.values():
            if not rule.enabled:
                continue

            if self._evaluate_rule(rule, event):
                self._trigger_alert(rule, event)

    def _evaluate_rule(self, rule: MonitoringRule, event: TransactionEvent) -> bool:
        """Evaluar regla de monitoreo"""
        if not rule.conditions:
            return False

        conditions = rule.conditions

        # Regla: Transacciones fallidas
        if rule.rule_id == "failed_transactions":
            if event.status == TransactionStatus.FAILED:
                failed_count = self._get_failed_transactions_count(
                    conditions.get("time_window", 3600)
                )
                return failed_count >= conditions.get("max_failed", 10)

        # Regla: Timeout de transacciones pendientes
        elif rule.rule_id == "pending_timeout":
            if event.status == TransactionStatus.PENDING:
                pending_time = (datetime.now() - event.timestamp).total_seconds()
                return pending_time >= conditions.get("max_pending_time", 300)

        # Regla: Transacciones de alto valor
        elif rule.rule_id == "high_value_transactions":
            return event.amount >= conditions.get("min_amount", 10000)

        # Regla: Actividad sospechosa
        elif rule.rule_id == "suspicious_activity":
            user_transactions = self._get_user_transactions_count(
                event.user_id, conditions.get("time_window", 300)
            )
            return user_transactions >= conditions.get("max_transactions_per_user", 5)

        return False

    def _get_failed_transactions_count(self, time_window: int) -> int:
        """Obtener cantidad de transacciones fallidas en ventana de tiempo"""
        cutoff_time = datetime.now() - timedelta(seconds=time_window)
        return sum(
            1
            for event in self.transaction_events
            if event.status == TransactionStatus.FAILED
            and event.timestamp >= cutoff_time
        )

    def _get_user_transactions_count(self, user_id: str, time_window: int) -> int:
        """Obtener cantidad de transacciones de usuario en ventana de tiempo"""
        cutoff_time = datetime.now() - timedelta(seconds=time_window)
        return sum(
            1
            for event in self.transaction_events
            if event.user_id == user_id and event.timestamp >= cutoff_time
        )

    def _trigger_alert(self, rule: MonitoringRule, event: TransactionEvent):
        """Disparar alerta"""
        alert = Alert(
            alert_id=f"{rule.rule_id}_{event.transaction_id}_{int(time.time())}",
            level=AlertLevel.WARNING,
            title=f"Alerta: {rule.name}",
            message=f"Se detectó actividad que cumple con la regla '{rule.name}': {event.transaction_id}",
            timestamp=datetime.now(),
            transaction_id=event.transaction_id,
            user_id=event.user_id,
            metadata={
                "rule_id": rule.rule_id,
                "event_type": event.event_type,
                "amount": event.amount,
                "token_mint": event.token_mint,
            },
        )

        self.active_alerts.append(alert)

        # Ejecutar callbacks de alerta
        for callback in self.alert_callbacks:
            try:
                callback(alert)
            except Exception as e:
                logger.error(f"❌ Error en callback de alerta: {e}")

        logger.warning(f"🚨 Alerta disparada: {alert.title}")

    def _check_monitoring_rules(self):
        """Verificar reglas de monitoreo en background"""
        try:
            # Verificar transacciones pendientes por mucho tiempo
            self._check_pending_transactions()

            # Verificar métricas generales
            self._check_general_metrics()

            # Limpiar alertas antiguas
            self._cleanup_old_alerts()

        except Exception as e:
            logger.error(f"❌ Error verificando reglas de monitoreo: {e}")

    def _check_pending_transactions(self):
        """Verificar transacciones pendientes"""
        cutoff_time = datetime.now() - timedelta(
            seconds=self.alert_thresholds["pending_timeout"]
        )

        for event in self.transaction_events:
            if (
                event.status == TransactionStatus.PENDING
                and event.timestamp <= cutoff_time
            ):

                alert = Alert(
                    alert_id=f"pending_timeout_{event.transaction_id}_{int(time.time())}",
                    level=AlertLevel.WARNING,
                    title="Transacción Pendiente por Mucho Tiempo",
                    message=f"La transacción {event.transaction_id} está pendiente desde {event.timestamp}",
                    timestamp=datetime.now(),
                    transaction_id=event.transaction_id,
                    user_id=event.user_id,
                )

                self.active_alerts.append(alert)

    def _check_general_metrics(self):
        """Verificar métricas generales"""
        # Verificar transacciones fallidas
        failed_count = self._get_failed_transactions_count(3600)  # última hora
        if failed_count >= self.alert_thresholds["failed_transactions"]:
            alert = Alert(
                alert_id=f"high_failure_rate_{int(time.time())}",
                level=AlertLevel.ERROR,
                title="Alta Tasa de Transacciones Fallidas",
                message=f"Se han detectado {failed_count} transacciones fallidas en la última hora",
                timestamp=datetime.now(),
            )
            self.active_alerts.append(alert)

    def _cleanup_old_alerts(self):
        """Limpiar alertas antiguas"""
        cutoff_time = datetime.now() - timedelta(days=7)  # 7 días
        self.active_alerts = [
            alert for alert in self.active_alerts if alert.timestamp >= cutoff_time
        ]

    def add_alert_callback(self, callback: Callable[[Alert], None]):
        """Agregar callback de alerta"""
        self.alert_callbacks.append(callback)
        logger.info("✅ Callback de alerta agregado")

    def get_transaction_events(
        self, user_id: Optional[str] = None, limit: int = 100
    ) -> List[TransactionEvent]:
        """Obtener eventos de transacciones"""
        events = self.transaction_events

        if user_id:
            events = [e for e in events if e.user_id == user_id]

        return events[-limit:]

    def get_active_alerts(self, level: Optional[AlertLevel] = None) -> List[Alert]:
        """Obtener alertas activas"""
        alerts = self.active_alerts

        if level:
            alerts = [a for a in alerts if a.level == level]

        return alerts

    def resolve_alert(self, alert_id: str) -> bool:
        """Resolver alerta"""
        try:
            with self.lock:
                for alert in self.active_alerts:
                    if alert.alert_id == alert_id:
                        alert.resolved = True
                        logger.info(f"✅ Alerta resuelta: {alert_id}")
                        return True

                logger.warning(f"⚠️ Alerta no encontrada: {alert_id}")
                return False

        except Exception as e:
            logger.error(f"❌ Error resolviendo alerta: {e}")
            return False

    def get_transaction_metrics(self) -> Dict[str, Any]:
        """Obtener métricas de transacciones"""
        try:
            # Métricas básicas
            metrics = {
                "total_transactions": self.transaction_metrics["total_transactions"],
                "pending_transactions": self.transaction_metrics.get(
                    "status_pending", 0
                ),
                "confirmed_transactions": self.transaction_metrics.get(
                    "status_confirmed", 0
                ),
                "failed_transactions": self.transaction_metrics.get("status_failed", 0),
                "active_alerts": len([a for a in self.active_alerts if not a.resolved]),
                "total_alerts": len(self.active_alerts),
                "last_updated": datetime.now().isoformat(),
            }

            # Métricas por estado
            for status in TransactionStatus:
                key = f"status_{status.value}"
                metrics[key] = self.transaction_metrics.get(key, 0)

            # Métricas por evento
            event_types = set(event.event_type for event in self.transaction_events)
            for event_type in event_types:
                key = f"event_{event_type}"
                metrics[key] = self.transaction_metrics.get(key, 0)

            return metrics

        except Exception as e:
            logger.error(f"❌ Error obteniendo métricas: {e}")
            return {}

    def get_monitoring_status(self) -> Dict[str, Any]:
        """Obtener estado del monitoreo"""
        return {
            "monitoring_enabled": self.monitoring_enabled,
            "active_rules": len(
                [r for r in self.monitoring_rules.values() if r.enabled]
            ),
            "total_rules": len(self.monitoring_rules),
            "alert_thresholds": self.alert_thresholds,
            "callbacks_registered": len(self.alert_callbacks),
            "last_updated": datetime.now().isoformat(),
        }

    def enable_monitoring(self):
        """Habilitar monitoreo"""
        self.monitoring_enabled = True
        self._save_config()
        logger.info("✅ Monitoreo habilitado")

    def disable_monitoring(self):
        """Deshabilitar monitoreo"""
        self.monitoring_enabled = False
        self._save_config()
        logger.info("⚠️ Monitoreo deshabilitado")

    def add_monitoring_rule(self, rule: MonitoringRule) -> bool:
        """Agregar regla de monitoreo"""
        try:
            with self.lock:
                self.monitoring_rules[rule.rule_id] = rule
                self._save_config()

                logger.info(f"✅ Nueva regla de monitoreo agregada: {rule.rule_id}")
                return True

        except Exception as e:
            logger.error(f"❌ Error agregando regla de monitoreo: {e}")
            return False

    def update_alert_thresholds(self, thresholds: Dict[str, Any]) -> bool:
        """Actualizar umbrales de alerta"""
        try:
            with self.lock:
                self.alert_thresholds.update(thresholds)
                self._save_config()

                logger.info("✅ Umbrales de alerta actualizados")
                return True

        except Exception as e:
            logger.error(f"❌ Error actualizando umbrales: {e}")
            return False


# Instancia global
_transaction_monitor: Optional[TransactionMonitor] = None


def get_transaction_monitor() -> TransactionMonitor:
    """Obtener instancia global del monitor de transacciones"""
    global _transaction_monitor

    if _transaction_monitor is None:
        _transaction_monitor = TransactionMonitor()

    return _transaction_monitor
