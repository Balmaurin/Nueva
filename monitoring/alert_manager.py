#!/usr/bin/env python3
"""
Gestor de Alertas Real para Shaili AI
=====================================
Sistema de alertas que maneja notificaciones y escalación automática
"""

import smtplib
import json
import logging
import sqlite3
import time
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, Any, List, Optional
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import requests
import threading
import traceback

# Configurar logging con más detalles
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    filename="monitoring/logs/alert_manager.log",
    filemode="a",
)
logger = logging.getLogger(__name__)


def log_error(message: str, error: Exception = None):
    """Método centralizado para registro de errores"""
    error_details = f"{message}\n{traceback.format_exc()}" if error else message
    logger.error(error_details)

    # Opcional: Enviar notificación de error
    try:
        from monitoring.alert_manager import AlertManager

        alert_manager = AlertManager()
        alert_manager.process_alert(
            {
                "alert_type": "alert_system_error",
                "severity": "warning",
                "message": message,
            }
        )
    except Exception as notification_error:
        logger.error(f"Error enviando notificación de error: {notification_error}")


class AlertManager:
    """Gestor de alertas del sistema Shaili AI"""

    def __init__(self, db_path: str = "monitoring/metrics.db"):
        self.db_path = db_path
        self.alert_config = self._load_alert_config()
        self.escalation_rules = self._load_escalation_rules()
        self.notification_channels = self._load_notification_channels()
        self.alert_history = {}

        # Crear directorio si no existe
        Path(self.db_path).parent.mkdir(parents=True, exist_ok=True)

    def _load_alert_config(self) -> Dict[str, Any]:
        """Cargar configuración de alertas"""
        config_path = Path("monitoring/alert_config.json")

        if config_path.exists():
            try:
                with open(config_path, "r") as f:
                    return json.load(f)
            except Exception as e:
                log_error("❌ Error cargando configuración de alertas", e)

        # Configuración por defecto
        default_config = {
            "alert_thresholds": {
                "cpu_percent": 90,
                "memory_percent": 85,
                "disk_usage_percent": 90,
                "error_rate": 5.0,
                "response_time_ms": 5000,
            },
            "alert_cooldown_minutes": 15,
            "max_alerts_per_hour": 10,
            "auto_resolve_hours": 2,
        }

        # Guardar configuración por defecto
        try:
            with open(config_path, "w") as f:
                json.dump(default_config, f, indent=2)
        except Exception as e:
            log_error("❌ Error guardando configuración por defecto", e)

        return default_config

    def _load_escalation_rules(self) -> List[Dict[str, Any]]:
        """Cargar reglas de escalación"""
        rules_path = Path("monitoring/escalation_rules.json")

        if rules_path.exists():
            try:
                with open(rules_path, "r") as f:
                    return json.load(f)
            except Exception as e:
                log_error("❌ Error cargando reglas de escalación", e)

        # Reglas por defecto
        default_rules = [
            {
                "alert_type": "high_cpu",
                "threshold": 3,
                "time_window_minutes": 30,
                "escalation_level": 1,
                "action": "notify_admin",
            },
            {
                "alert_type": "high_memory",
                "threshold": 2,
                "time_window_minutes": 15,
                "escalation_level": 2,
                "action": "notify_team",
            },
            {
                "alert_type": "disk_full",
                "threshold": 1,
                "time_window_minutes": 5,
                "escalation_level": 3,
                "action": "emergency_call",
            },
        ]

        # Guardar reglas por defecto
        try:
            with open(rules_path, "w") as f:
                json.dump(default_rules, f, indent=2)
        except Exception as e:
            log_error("❌ Error guardando reglas por defecto", e)

        return default_rules

    def _load_notification_channels(self) -> Dict[str, Any]:
        """Cargar canales de notificación"""
        channels_path = Path("monitoring/notification_channels.json")

        if channels_path.exists():
            try:
                with open(channels_path, "r") as f:
                    return json.load(f)
            except Exception as e:
                log_error("❌ Error cargando canales de notificación", e)

        # Canales por defecto
        default_channels = {
            "email": {
                "enabled": True,
                "smtp_server": "smtp.gmail.com",
                "smtp_port": 587,
                "username": "alerts@shaili-ai.com",
                "password": "your_password_here",
                "recipients": ["admin@shaili-ai.com", "team@shaili-ai.com"],
            },
            "slack": {
                "enabled": False,
                "webhook_url": "https://hooks.slack.com/services/YOUR/WEBHOOK/URL",
                "channel": "#alerts",
            },
            "telegram": {
                "enabled": False,
                "bot_token": "your_bot_token",
                "chat_id": "your_chat_id",
            },
            "webhook": {
                "enabled": False,
                "url": "https://your-webhook-url.com/alerts",
                "headers": {"Authorization": "Bearer your_token"},
            },
        }

        # Guardar canales por defecto
        try:
            with open(channels_path, "w") as f:
                json.dump(default_channels, f, indent=2)
        except Exception as e:
            log_error("❌ Error guardando canales por defecto", e)

        return default_channels

    def process_alert(self, alert: Dict[str, Any]) -> bool:
        """Procesar una nueva alerta"""
        try:
            # Verificar si la alerta ya existe (cooldown)
            if self._is_alert_in_cooldown(alert):
                logger.info(f"⚠️ Alerta en cooldown: {alert['alert_type']}")
                return False

            # Verificar límite de alertas por hora
            if self._is_alert_limit_reached(alert["alert_type"]):
                logger.warning(
                    f"🚨 Límite de alertas alcanzado para: {alert['alert_type']}"
                )
                return False

            # Guardar alerta en base de datos
            alert_id = self._save_alert_to_db(alert)

            # Verificar escalación
            escalation_level = self._check_escalation(alert)

            # Enviar notificaciones
            self._send_notifications(alert, escalation_level)

            # Registrar en historial
            self._add_to_history(alert_id, alert, escalation_level)

            logger.info(
                f"✅ Alerta procesada: {alert['alert_type']} (Nivel: {escalation_level})"
            )
            return True

        except Exception as e:
            log_error("❌ Error procesando alerta", e)
            return False

    def _is_alert_in_cooldown(self, alert: Dict[str, Any]) -> bool:
        """Verificar si la alerta está en período de cooldown"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()

                cooldown_minutes = self.alert_config.get("alert_cooldown_minutes", 15)
                cutoff_time = datetime.now() - timedelta(minutes=cooldown_minutes)

                cursor.execute(
                    """
                    SELECT COUNT(*) FROM alerts 
                    WHERE alert_type = ? AND timestamp > ? AND resolved = FALSE
                """,
                    (alert["alert_type"], cutoff_time.isoformat()),
                )

                count = cursor.fetchone()[0]
                return count > 0

        except Exception as e:
            log_error("❌ Error verificando cooldown", e)
            return False

    def _is_alert_limit_reached(self, alert_type: str) -> bool:
        """Verificar si se alcanzó el límite de alertas por hora"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()

                max_alerts = self.alert_config.get("max_alerts_per_hour", 10)
                cutoff_time = datetime.now() - timedelta(hours=1)

                cursor.execute(
                    """
                    SELECT COUNT(*) FROM alerts 
                    WHERE alert_type = ? AND timestamp > ?
                """,
                    (alert_type, cutoff_time.isoformat()),
                )

                count = cursor.fetchone()[0]
                return count >= max_alerts

        except Exception as e:
            log_error("❌ Error verificando límite de alertas", e)
            return False

    def _save_alert_to_db(self, alert: Dict[str, Any]) -> int:
        """Guardar alerta en la base de datos"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()

                cursor.execute(
                    """
                    INSERT INTO alerts (alert_type, severity, message, timestamp)
                    VALUES (?, ?, ?, ?)
                """,
                    (
                        alert["alert_type"],
                        alert["severity"],
                        alert["message"],
                        datetime.now().isoformat(),
                    ),
                )

                conn.commit()
                return cursor.lastrowid

        except Exception as e:
            log_error("❌ Error guardando alerta en DB", e)
            return 0

    def _check_escalation(self, alert: Dict[str, Any]) -> int:
        """Verificar si se debe escalar la alerta"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()

                for rule in self.escalation_rules:
                    if rule["alert_type"] == alert["alert_type"]:
                        # Contar alertas similares en la ventana de tiempo
                        cutoff_time = datetime.now() - timedelta(
                            minutes=rule["time_window_minutes"]
                        )

                        cursor.execute(
                            """
                            SELECT COUNT(*) FROM alerts 
                            WHERE alert_type = ? AND timestamp > ?
                        """,
                            (alert["alert_type"], cutoff_time.isoformat()),
                        )

                        count = cursor.fetchone()[0]

                        if count >= rule["threshold"]:
                            return rule["escalation_level"]

                return 0  # Sin escalación

        except Exception as e:
            log_error("❌ Error verificando escalación", e)
            return 0

    def _send_notifications(self, alert: Dict[str, Any], escalation_level: int):
        """Enviar notificaciones por todos los canales habilitados"""
        try:
            # Preparar mensaje
            message = self._format_alert_message(alert, escalation_level)

            # Enviar por email
            if self.notification_channels["email"]["enabled"]:
                self._send_email_notification(message, escalation_level)

            # Enviar por Slack
            if self.notification_channels["slack"]["enabled"]:
                self._send_slack_notification(message, escalation_level)

            # Enviar por Telegram
            if self.notification_channels["telegram"]["enabled"]:
                self._send_telegram_notification(message, escalation_level)

            # Enviar webhook
            if self.notification_channels["webhook"]["enabled"]:
                self._send_webhook_notification(alert, escalation_level)

        except Exception as e:
            log_error("❌ Error enviando notificaciones", e)

    def _format_alert_message(
        self, alert: Dict[str, Any], escalation_level: int
    ) -> str:
        """Formatear mensaje de alerta"""
        severity_emoji = {
            "info": "ℹ️",
            "warning": "⚠️",
            "critical": "🚨",
            "emergency": "🆘",
        }

        emoji = severity_emoji.get(alert["severity"], "📢")

        message = f"""
{emoji} ALERTA SHAILI AI - {alert['severity'].upper()}

📋 Tipo: {alert['alert_type']}
📝 Mensaje: {alert['message']}
⏰ Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
🚨 Nivel de Escalación: {escalation_level}

🔧 Acciones Recomendadas:
"""

        # Agregar acciones específicas según el tipo de alerta
        if alert["alert_type"] == "high_cpu":
            message += "- Verificar procesos que consumen CPU\n- Considerar escalar recursos\n- Revisar logs de aplicación"
        elif alert["alert_type"] == "high_memory":
            message += "- Verificar uso de memoria por procesos\n- Considerar limpiar cache\n- Revisar posibles memory leaks"
        elif alert["alert_type"] == "disk_full":
            message += "- Limpiar archivos temporales\n- Verificar logs antiguos\n- Considerar aumentar espacio en disco"
        else:
            message += "- Revisar logs del sistema\n- Verificar estado de servicios\n- Contactar al equipo de soporte"

        return message

    def _send_email_notification(self, message: str, escalation_level: int):
        """Enviar notificación por email"""
        try:
            email_config = self.notification_channels["email"]

            msg = MIMEMultipart()
            msg["From"] = email_config["username"]
            msg["To"] = ", ".join(email_config["recipients"])
            msg["Subject"] = f"🚨 Alerta Shaili AI - Nivel {escalation_level}"

            msg.attach(MIMEText(message, "plain"))

            with smtplib.SMTP(
                email_config["smtp_server"], email_config["smtp_port"]
            ) as server:
                server.starttls()
                server.login(email_config["username"], email_config["password"])
                server.send_message(msg)

            logger.info("✅ Notificación por email enviada")

        except Exception as e:
            log_error("❌ Error enviando email", e)

    def _send_slack_notification(self, message: str, escalation_level: int):
        """Enviar notificación por Slack"""
        try:
            slack_config = self.notification_channels["slack"]

            payload = {
                "channel": slack_config["channel"],
                "text": message,
                "username": "Shaili AI Alerts",
                "icon_emoji": ":warning:",
            }

            response = requests.post(slack_config["webhook_url"], json=payload)
            response.raise_for_status()

            logger.info("✅ Notificación por Slack enviada")

        except Exception as e:
            log_error("❌ Error enviando Slack", e)

    def _send_telegram_notification(self, message: str, escalation_level: int):
        """Enviar notificación por Telegram"""
        try:
            telegram_config = self.notification_channels["telegram"]

            url = f"https://api.telegram.org/bot{telegram_config['bot_token']}/sendMessage"
            payload = {
                "chat_id": telegram_config["chat_id"],
                "text": message,
                "parse_mode": "HTML",
            }

            response = requests.post(url, json=payload)
            response.raise_for_status()

            logger.info("✅ Notificación por Telegram enviada")

        except Exception as e:
            log_error("❌ Error enviando Telegram", e)

    def _send_webhook_notification(self, alert: Dict[str, Any], escalation_level: int):
        """Enviar notificación por webhook"""
        try:
            webhook_config = self.notification_channels["webhook"]

            payload = {
                "alert": alert,
                "escalation_level": escalation_level,
                "timestamp": datetime.now().isoformat(),
                "source": "shaili_ai_alert_manager",
            }

            response = requests.post(
                webhook_config["url"], json=payload, headers=webhook_config["headers"]
            )
            response.raise_for_status()

            logger.info("✅ Notificación por webhook enviada")

        except Exception as e:
            log_error("❌ Error enviando webhook", e)

    def _add_to_history(
        self, alert_id: int, alert: Dict[str, Any], escalation_level: int
    ):
        """Agregar alerta al historial"""
        self.alert_history[alert_id] = {
            "alert": alert,
            "escalation_level": escalation_level,
            "timestamp": datetime.now(),
            "processed": True,
        }

    def resolve_alert(self, alert_id: int, resolution_notes: str = ""):
        """Marcar alerta como resuelta"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()

                cursor.execute(
                    """
                    UPDATE alerts 
                    SET resolved = TRUE, resolution_notes = ?
                    WHERE id = ?
                """,
                    (resolution_notes, alert_id),
                )

                conn.commit()

                # Remover del historial
                if alert_id in self.alert_history:
                    del self.alert_history[alert_id]

                logger.info(f"✅ Alerta {alert_id} marcada como resuelta")

        except Exception as e:
            log_error("❌ Error resolviendo alerta", e)

    def get_active_alerts(self) -> List[Dict[str, Any]]:
        """Obtener alertas activas"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()

                cursor.execute(
                    """
                    SELECT * FROM alerts 
                    WHERE resolved = FALSE 
                    ORDER BY timestamp DESC
                """
                )

                columns = [description[0] for description in cursor.description]
                alerts = []

                for row in cursor.fetchall():
                    alert = dict(zip(columns, row))
                    alerts.append(alert)

                return alerts

        except Exception as e:
            log_error("❌ Error obteniendo alertas activas", e)
            return []

    def get_alert_statistics(self, hours: int = 24) -> Dict[str, Any]:
        """Obtener estadísticas de alertas"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()

                cutoff_time = datetime.now() - timedelta(hours=hours)

                # Total de alertas
                cursor.execute(
                    """
                    SELECT COUNT(*) FROM alerts 
                    WHERE timestamp > ?
                """,
                    (cutoff_time.isoformat(),),
                )
                total_alerts = cursor.fetchone()[0]

                # Alertas resueltas
                cursor.execute(
                    """
                    SELECT COUNT(*) FROM alerts 
                    WHERE timestamp > ? AND resolved = TRUE
                """,
                    (cutoff_time.isoformat(),),
                )
                resolved_alerts = cursor.fetchone()[0]

                # Alertas por tipo
                cursor.execute(
                    """
                    SELECT alert_type, COUNT(*) FROM alerts 
                    WHERE timestamp > ?
                    GROUP BY alert_type
                """,
                    (cutoff_time.isoformat(),),
                )
                alerts_by_type = dict(cursor.fetchall())

                # Alertas por severidad
                cursor.execute(
                    """
                    SELECT severity, COUNT(*) FROM alerts 
                    WHERE timestamp > ?
                    GROUP BY severity
                """,
                    (cutoff_time.isoformat(),),
                )
                alerts_by_severity = dict(cursor.fetchall())

                return {
                    "total_alerts": total_alerts,
                    "resolved_alerts": resolved_alerts,
                    "pending_alerts": total_alerts - resolved_alerts,
                    "resolution_rate": (
                        (resolved_alerts / total_alerts * 100)
                        if total_alerts > 0
                        else 0
                    ),
                    "alerts_by_type": alerts_by_type,
                    "alerts_by_severity": alerts_by_severity,
                    "time_period_hours": hours,
                }

        except Exception as e:
            log_error("❌ Error obteniendo estadísticas", e)
            return {}


def main():
    """Función principal para testing"""
    alert_manager = AlertManager()

    # Crear alerta de prueba
    test_alert = {
        "alert_type": "high_cpu",
        "severity": "warning",
        "message": "CPU usage is high: 95.2%",
    }

    # Procesar alerta
    try:
        success = alert_manager.process_alert(test_alert)
        print(f"Alerta procesada: {'✅' if success else '❌'}")
    except Exception as e:
        log_error("❌ Error en prueba de alerta", e)

    # Mostrar alertas activas
    active_alerts = alert_manager.get_active_alerts()
    print(f"Alertas activas: {len(active_alerts)}")

    # Mostrar estadísticas
    stats = alert_manager.get_alert_statistics()
    print("📊 Estadísticas de alertas:")
    print(json.dumps(stats, indent=2))


if __name__ == "__main__":
    main()
