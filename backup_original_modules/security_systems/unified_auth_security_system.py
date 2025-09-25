"""
Sistema Unificado de Autenticación y Seguridad para NeuroFusion

Este módulo combina funcionalidades de:
- JWT Authentication (jwt_auth.py)
- Two-Factor Authentication (two_factor_auth.py)
- Digital Signatures (digital_signature.py)
- Password Policy (password_policy.py)
- Account Recovery (account_recovery.py)
- User Activity Monitoring (user_activity_monitor.py)
- User Anomaly Detection (user_anomaly_detector.py)
- Intrusion Detection (intrusion_detection.py)
"""

import logging
import json
import hashlib
import hmac
import base64
import secrets
import time
import sqlite3
import uuid
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional, Union, Tuple
from dataclasses import dataclass, field
from pathlib import Path
from enum import Enum
import pyotp
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import rsa, padding
from cryptography.hazmat.backends import default_backend
import jwt
import numpy as np
from sklearn.ensemble import IsolationForest
from sklearn.preprocessing import StandardScaler

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class SecurityLevel(Enum):
    """Niveles de seguridad"""

    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


@dataclass
class UserSecurityProfile:
    """Perfil de seguridad del usuario"""

    user_id: str
    security_level: SecurityLevel = SecurityLevel.MEDIUM
    two_factor_enabled: bool = False
    last_password_change: datetime = field(default_factory=datetime.now)
    failed_login_attempts: int = 0
    account_locked: bool = False
    lockout_until: Optional[datetime] = None
    risk_score: float = 0.0
    last_activity: datetime = field(default_factory=datetime.now)
    ip_whitelist: List[str] = field(default_factory=list)
    device_whitelist: List[str] = field(default_factory=list)


@dataclass
class SecurityEvent:
    """Evento de seguridad"""

    event_id: str
    user_id: str
    event_type: str
    severity: SecurityLevel
    timestamp: datetime
    ip_address: Optional[str] = None
    device_info: Optional[Dict[str, Any]] = None
    details: Dict[str, Any] = field(default_factory=dict)
    risk_score: float = 0.0


class UnifiedAuthSecuritySystem:
    """
    Sistema unificado de autenticación y seguridad
    """

    def __init__(self, db_path: Optional[str] = None, secret_key: Optional[str] = None):
        """Inicializar sistema de autenticación y seguridad"""
        self.db_path = Path(db_path) if db_path else Path("data/auth_security.db")
        self.db_path.parent.mkdir(exist_ok=True)

        # Configuración JWT
        self.secret_key = secret_key or self._generate_secret_key()
        self.algorithm = "HS256"
        self.token_expiration = 3600  # 1 hora

        # Configuración 2FA
        self.totp_issuer = "NeuroFusion"
        self.backup_codes_count = 5

        # Configuración de seguridad
        self.max_failed_attempts = 5
        self.lockout_duration = 1800  # 30 minutos
        self.password_min_length = 8
        self.password_require_special = True

        # Inicializar componentes
        self._init_database()
        self._init_crypto()
        self._init_monitoring()

        logger.info("🔐 Sistema de Autenticación y Seguridad inicializado")

    def _init_database(self):
        """Inicializar base de datos de seguridad"""
        try:
            conn = sqlite3.connect(str(self.db_path))
            cursor = conn.cursor()

            # Tabla de usuarios y perfiles de seguridad
            cursor.execute(
                """
                CREATE TABLE IF NOT EXISTS user_security_profiles (
                    user_id TEXT PRIMARY KEY,
                    security_level TEXT NOT NULL,
                    two_factor_enabled BOOLEAN DEFAULT FALSE,
                    last_password_change TIMESTAMP,
                    failed_login_attempts INTEGER DEFAULT 0,
                    account_locked BOOLEAN DEFAULT FALSE,
                    lockout_until TIMESTAMP,
                    risk_score REAL DEFAULT 0.0,
                    last_activity TIMESTAMP,
                    ip_whitelist TEXT,
                    device_whitelist TEXT
                )
            """
            )

            # Tabla de eventos de seguridad
            cursor.execute(
                """
                CREATE TABLE IF NOT EXISTS security_events (
                    event_id TEXT PRIMARY KEY,
                    user_id TEXT NOT NULL,
                    event_type TEXT NOT NULL,
                    severity TEXT NOT NULL,
                    timestamp TIMESTAMP,
                    ip_address TEXT,
                    device_info TEXT,
                    details TEXT,
                    risk_score REAL DEFAULT 0.0
                )
            """
            )

            # Tabla de tokens JWT
            cursor.execute(
                """
                CREATE TABLE IF NOT EXISTS jwt_tokens (
                    token_id TEXT PRIMARY KEY,
                    user_id TEXT NOT NULL,
                    token_hash TEXT NOT NULL,
                    created_at TIMESTAMP,
                    expires_at TIMESTAMP,
                    is_revoked BOOLEAN DEFAULT FALSE
                )
            """
            )

            # Tabla de códigos de recuperación
            cursor.execute(
                """
                CREATE TABLE IF NOT EXISTS recovery_tokens (
                    token_id TEXT PRIMARY KEY,
                    user_id TEXT NOT NULL,
                    token_hash TEXT NOT NULL,
                    ip_address TEXT,
                    created_at TIMESTAMP,
                    expires_at TIMESTAMP,
                    is_used BOOLEAN DEFAULT FALSE
                )
            """
            )

            # Tabla de códigos 2FA de respaldo
            cursor.execute(
                """
                CREATE TABLE IF NOT EXISTS backup_codes (
                    code_id TEXT PRIMARY KEY,
                    user_id TEXT NOT NULL,
                    code_hash TEXT NOT NULL,
                    created_at TIMESTAMP,
                    is_used BOOLEAN DEFAULT FALSE
                )
            """
            )

            conn.commit()
            conn.close()
            logger.info("✅ Base de datos de seguridad inicializada")

        except Exception as e:
            logger.error(f"❌ Error inicializando base de datos: {e}")

    def _init_crypto(self):
        """Inicializar componentes criptográficos"""
        try:
            # Generar par de claves RSA para firmas digitales
            self.private_key = rsa.generate_private_key(
                public_exponent=65537, key_size=2048, backend=default_backend()
            )
            self.public_key = self.private_key.public_key()

            logger.info("✅ Componentes criptográficos inicializados")

        except Exception as e:
            logger.error(f"❌ Error inicializando criptografía: {e}")

    def _init_monitoring(self):
        """Inicializar sistema de monitoreo"""
        self.activity_monitor = UserActivityMonitor(str(self.db_path))
        self.anomaly_detector = UserAnomalyDetector(str(self.db_path))
        self.intrusion_detector = IntrusionDetectionSystem()

        logger.info("✅ Sistema de monitoreo inicializado")

    def _generate_secret_key(self) -> str:
        """Generar clave secreta para JWT"""
        return secrets.token_urlsafe(32)

    # ==================== JWT AUTHENTICATION ====================

    def generate_jwt_token(
        self, user_id: str, claims: Optional[Dict[str, Any]] = None
    ) -> str:
        """Generar token JWT para usuario"""
        try:
            payload = {
                "user_id": user_id,
                "exp": datetime.utcnow() + timedelta(seconds=self.token_expiration),
                "iat": datetime.utcnow(),
                "jti": str(uuid.uuid4()),
            }

            if claims:
                payload.update(claims)

            token = jwt.encode(payload, self.secret_key, algorithm=self.algorithm)

            # Guardar token en base de datos
            self._save_jwt_token(payload["jti"], user_id, token)

            # Registrar evento
            self._log_security_event(
                user_id,
                "jwt_token_generated",
                SecurityLevel.LOW,
                details={"token_id": payload["jti"]},
            )

            return token

        except Exception as e:
            logger.error(f"❌ Error generando JWT: {e}")
            raise

    def validate_jwt_token(self, token: str) -> Dict[str, Any]:
        """Validar token JWT"""
        try:
            # Verificar si el token está revocado
            if self._is_token_revoked(token):
                raise jwt.InvalidTokenError("Token revocado")

            payload = jwt.decode(token, self.secret_key, algorithms=[self.algorithm])

            # Verificar expiración
            if datetime.utcnow() > datetime.fromtimestamp(payload["exp"]):
                raise jwt.ExpiredSignatureError("Token expirado")

            return payload

        except jwt.ExpiredSignatureError:
            logger.warning("⚠️ Token JWT expirado")
            raise
        except jwt.InvalidTokenError as e:
            logger.warning(f"⚠️ Token JWT inválido: {e}")
            raise
        except Exception as e:
            logger.error(f"❌ Error validando JWT: {e}")
            raise

    def revoke_jwt_token(self, token: str) -> bool:
        """Revocar token JWT"""
        try:
            payload = jwt.decode(token, self.secret_key, algorithms=[self.algorithm])
            token_id = payload.get("jti")

            if token_id:
                conn = sqlite3.connect(str(self.db_path))
                cursor = conn.cursor()
                cursor.execute(
                    "UPDATE jwt_tokens SET is_revoked = TRUE WHERE token_id = ?",
                    (token_id,),
                )
                conn.commit()
                conn.close()

                self._log_security_event(
                    payload["user_id"],
                    "jwt_token_revoked",
                    SecurityLevel.MEDIUM,
                    details={"token_id": token_id},
                )

                return True

            return False

        except Exception as e:
            logger.error(f"❌ Error revocando JWT: {e}")
            return False

    # ==================== TWO-FACTOR AUTHENTICATION ====================

    def setup_2fa(self, user_id: str) -> Dict[str, Any]:
        """Configurar autenticación de dos factores"""
        try:
            # Generar secreto TOTP
            secret = pyotp.random_base32()

            # Crear objeto TOTP
            totp = pyotp.TOTP(secret, issuer=self.totp_issuer)

            # Generar URL QR
            qr_url = totp.provisioning_uri(name=user_id, issuer_name=self.totp_issuer)

            # Generar códigos de respaldo
            backup_codes = self._generate_backup_codes(user_id)

            # Actualizar perfil de usuario
            self._update_user_2fa_status(user_id, True)

            self._log_security_event(
                user_id, "2fa_setup", SecurityLevel.HIGH, details={"method": "totp"}
            )

            return {
                "secret": secret,
                "qr_url": qr_url,
                "backup_codes": backup_codes,
                "setup_complete": True,
            }

        except Exception as e:
            logger.error(f"❌ Error configurando 2FA: {e}")
            raise

    def verify_2fa_code(self, user_id: str, code: str) -> bool:
        """Verificar código 2FA"""
        try:
            # Obtener secreto del usuario
            secret = self._get_user_2fa_secret(user_id)
            if not secret:
                return False

            # Verificar código TOTP
            totp = pyotp.TOTP(secret)
            if totp.verify(code):
                self._log_security_event(
                    user_id, "2fa_verification_success", SecurityLevel.MEDIUM
                )
                return True

            # Verificar código de respaldo
            if self._verify_backup_code(user_id, code):
                self._log_security_event(
                    user_id, "2fa_backup_code_used", SecurityLevel.HIGH
                )
                return True

            self._log_security_event(
                user_id, "2fa_verification_failed", SecurityLevel.MEDIUM
            )
            return False

        except Exception as e:
            logger.error(f"❌ Error verificando 2FA: {e}")
            return False

    def _generate_backup_codes(self, user_id: str) -> List[str]:
        """Generar códigos de respaldo para 2FA"""
        codes = []
        for _ in range(self.backup_codes_count):
            code = secrets.token_hex(4).upper()[:8]
            codes.append(code)

            # Guardar hash del código
            code_hash = hashlib.sha256(code.encode()).hexdigest()
            self._save_backup_code(user_id, code_hash)

        return codes

    # ==================== DIGITAL SIGNATURES ====================

    def sign_data(self, data: str) -> str:
        """Firmar datos digitalmente"""
        try:
            # Convertir datos a bytes
            data_bytes = data.encode("utf-8")

            # Firmar con clave privada
            signature = self.private_key.sign(
                data_bytes,
                padding.PSS(
                    mgf=padding.MGF1(hashes.SHA256()),
                    salt_length=padding.PSS.MAX_LENGTH,
                ),
                hashes.SHA256(),
            )

            # Codificar en base64
            signature_b64 = base64.b64encode(signature).decode("utf-8")

            return signature_b64

        except Exception as e:
            logger.error(f"❌ Error firmando datos: {e}")
            raise

    def verify_signature(self, data: str, signature_b64: str) -> bool:
        """Verificar firma digital"""
        try:
            # Decodificar firma
            signature = base64.b64decode(signature_b64)

            # Verificar con clave pública
            self.public_key.verify(
                signature,
                data.encode("utf-8"),
                padding.PSS(
                    mgf=padding.MGF1(hashes.SHA256()),
                    salt_length=padding.PSS.MAX_LENGTH,
                ),
                hashes.SHA256(),
            )

            return True

        except Exception as e:
            logger.error(f"❌ Error verificando firma: {e}")
            return False

    def export_public_key(self) -> str:
        """Exportar clave pública en formato PEM"""
        try:
            pem = self.public_key.public_bytes(
                encoding=serialization.Encoding.PEM,
                format=serialization.PublicFormat.SubjectPublicKeyInfo,
            )
            return pem.decode("utf-8")

        except Exception as e:
            logger.error(f"❌ Error exportando clave pública: {e}")
            raise

    # ==================== PASSWORD POLICY ====================

    def validate_password(self, password: str) -> Dict[str, Any]:
        """Validar contraseña según política de seguridad"""
        issues = []
        score = 0

        # Verificar longitud mínima
        if len(password) < self.password_min_length:
            issues.append(
                f"La contraseña debe tener al menos {self.password_min_length} caracteres"
            )
        else:
            score += 20

        # Verificar caracteres especiales
        if self.password_require_special and not any(
            c in "!@#$%^&*()_+-=[]{}|;:,.<>?" for c in password
        ):
            issues.append("La contraseña debe contener al menos un carácter especial")
        else:
            score += 20

        # Verificar mayúsculas
        if not any(c.isupper() for c in password):
            issues.append("La contraseña debe contener al menos una mayúscula")
        else:
            score += 20

        # Verificar minúsculas
        if not any(c.islower() for c in password):
            issues.append("La contraseña debe contener al menos una minúscula")
        else:
            score += 20

        # Verificar números
        if not any(c.isdigit() for c in password):
            issues.append("La contraseña debe contener al menos un número")
        else:
            score += 20

        return {"valid": len(issues) == 0, "score": score, "issues": issues}

    def generate_secure_password(self, length: int = 12) -> str:
        """Generar contraseña segura"""
        import string

        # Caracteres disponibles
        lowercase = string.ascii_lowercase
        uppercase = string.ascii_uppercase
        digits = string.digits
        special = "!@#$%^&*()_+-=[]{}|;:,.<>?"

        # Asegurar al menos un carácter de cada tipo
        password = [
            secrets.choice(lowercase),
            secrets.choice(uppercase),
            secrets.choice(digits),
            secrets.choice(special),
        ]

        # Completar con caracteres aleatorios
        all_chars = lowercase + uppercase + digits + special
        for _ in range(length - 4):
            password.append(secrets.choice(all_chars))

        # Mezclar la contraseña
        password_list = list(password)
        secrets.SystemRandom().shuffle(password_list)

        return "".join(password_list)

    # ==================== ACCOUNT RECOVERY ====================

    def generate_recovery_token(
        self, user_id: str, ip_address: Optional[str] = None
    ) -> str:
        """Generar token de recuperación de cuenta"""
        try:
            # Generar token único
            token = secrets.token_urlsafe(32)
            token_hash = hashlib.sha256(token.encode()).hexdigest()

            # Configurar expiración (1 hora)
            expires_at = datetime.utcnow() + timedelta(hours=1)

            # Guardar en base de datos
            conn = sqlite3.connect(str(self.db_path))
            cursor = conn.cursor()
            cursor.execute(
                """
                INSERT INTO recovery_tokens 
                (token_id, user_id, token_hash, ip_address, created_at, expires_at)
                VALUES (?, ?, ?, ?, ?, ?)
            """,
                (
                    str(uuid.uuid4()),
                    user_id,
                    token_hash,
                    ip_address,
                    datetime.utcnow(),
                    expires_at,
                ),
            )
            conn.commit()
            conn.close()

            self._log_security_event(
                user_id,
                "recovery_token_generated",
                SecurityLevel.HIGH,
                ip_address=ip_address,
            )

            return token

        except Exception as e:
            logger.error(f"❌ Error generando token de recuperación: {e}")
            raise

    def validate_recovery_token(self, user_id: str, recovery_token: str) -> bool:
        """Validar token de recuperación"""
        try:
            token_hash = hashlib.sha256(recovery_token.encode()).hexdigest()

            conn = sqlite3.connect(str(self.db_path))
            cursor = conn.cursor()
            cursor.execute(
                """
                SELECT token_id, expires_at, is_used 
                FROM recovery_tokens 
                WHERE user_id = ? AND token_hash = ?
            """,
                (user_id, token_hash),
            )

            result = cursor.fetchone()

            if not result:
                return False

            token_id, expires_at, is_used = result

            # Verificar si ya fue usado
            if is_used:
                return False

            # Verificar expiración
            if datetime.fromisoformat(expires_at) < datetime.utcnow():
                return False

            # Marcar como usado
            cursor.execute(
                "UPDATE recovery_tokens SET is_used = TRUE WHERE token_id = ?",
                (token_id,),
            )
            conn.commit()
            conn.close()

            self._log_security_event(user_id, "recovery_token_used", SecurityLevel.HIGH)

            return True

        except Exception as e:
            logger.error(f"❌ Error validando token de recuperación: {e}")
            return False

    # ==================== USER MONITORING ====================

    def log_user_activity(
        self,
        user_id: str,
        activity_type: str,
        details: Optional[Dict[str, Any]] = None,
        ip_address: Optional[str] = None,
        device_info: Optional[Dict[str, Any]] = None,
    ):
        """Registrar actividad del usuario"""
        try:
            # Registrar en monitor de actividad
            self.activity_monitor.log_activity(
                user_id, activity_type, details, ip_address, device_info
            )

            # Actualizar último acceso
            self._update_user_last_activity(user_id)

            # Detectar anomalías
            anomalies = self.anomaly_detector.detect_anomalies(user_id)
            if anomalies.get("anomalies_detected", False):
                self._handle_anomalies(user_id, anomalies)

            # Detectar intrusiones
            intrusion_risk = self.intrusion_detector.analyze_activity(
                user_id, activity_type, ip_address, device_info
            )
            if intrusion_risk > 0.7:
                self._handle_intrusion_attempt(user_id, intrusion_risk, details)

        except Exception as e:
            logger.error(f"❌ Error registrando actividad: {e}")

    def get_user_security_summary(self, user_id: str) -> Dict[str, Any]:
        """Obtener resumen de seguridad del usuario"""
        try:
            # Obtener perfil de seguridad
            profile = self._get_user_security_profile(user_id)

            # Obtener actividad reciente
            activity_summary = self.activity_monitor.get_user_activity_summary(
                user_id, 30
            )

            # Obtener anomalías recientes
            recent_anomalies = self.anomaly_detector.get_recent_anomalies(7)
            user_anomalies = [
                a for a in recent_anomalies if a.get("user_id") == user_id
            ]

            # Obtener eventos de seguridad recientes
            recent_events = self._get_recent_security_events(user_id, 7)

            return {
                "user_id": user_id,
                "security_profile": profile,
                "activity_summary": activity_summary,
                "recent_anomalies": user_anomalies,
                "recent_security_events": recent_events,
                "risk_assessment": self._calculate_user_risk_score(user_id),
            }

        except Exception as e:
            logger.error(f"❌ Error obteniendo resumen de seguridad: {e}")
            return {}

    # ==================== HELPER METHODS ====================

    def _save_jwt_token(self, token_id: str, user_id: str, token: str):
        """Guardar token JWT en base de datos"""
        try:
            token_hash = hashlib.sha256(token.encode()).hexdigest()
            expires_at = datetime.utcnow() + timedelta(seconds=self.token_expiration)

            conn = sqlite3.connect(str(self.db_path))
            cursor = conn.cursor()
            cursor.execute(
                """
                INSERT INTO jwt_tokens 
                (token_id, user_id, token_hash, created_at, expires_at)
                VALUES (?, ?, ?, ?, ?)
            """,
                (token_id, user_id, token_hash, datetime.utcnow(), expires_at),
            )
            conn.commit()
            conn.close()

        except Exception as e:
            logger.error(f"❌ Error guardando JWT: {e}")

    def _is_token_revoked(self, token: str) -> bool:
        """Verificar si token está revocado"""
        try:
            payload = jwt.decode(token, self.secret_key, algorithms=[self.algorithm])
            token_id = payload.get("jti")

            if not token_id:
                return True

            conn = sqlite3.connect(str(self.db_path))
            cursor = conn.cursor()
            cursor.execute(
                "SELECT is_revoked FROM jwt_tokens WHERE token_id = ?", (token_id,)
            )
            result = cursor.fetchone()
            conn.close()

            return result and result[0]

        except Exception as e:
            logger.error(f"❌ Error verificando revocación: {e}")
            return True

    def _log_security_event(
        self,
        user_id: str,
        event_type: str,
        severity: SecurityLevel,
        details: Optional[Dict[str, Any]] = None,
        ip_address: Optional[str] = None,
        device_info: Optional[Dict[str, Any]] = None,
    ):
        """Registrar evento de seguridad"""
        try:
            event_id = str(uuid.uuid4())
            risk_score = self._calculate_event_risk_score(event_type, severity)

            conn = sqlite3.connect(str(self.db_path))
            cursor = conn.cursor()
            cursor.execute(
                """
                INSERT INTO security_events 
                (event_id, user_id, event_type, severity, timestamp, ip_address, device_info, details, risk_score)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
                (
                    event_id,
                    user_id,
                    event_type,
                    severity.value,
                    datetime.utcnow(),
                    ip_address,
                    json.dumps(device_info) if device_info else None,
                    json.dumps(details) if details else None,
                    risk_score,
                ),
            )
            conn.commit()
            conn.close()

        except Exception as e:
            logger.error(f"❌ Error registrando evento de seguridad: {e}")

    def _calculate_event_risk_score(
        self, event_type: str, severity: SecurityLevel
    ) -> float:
        """Calcular puntuación de riesgo para evento"""
        base_scores = {
            SecurityLevel.LOW: 0.1,
            SecurityLevel.MEDIUM: 0.3,
            SecurityLevel.HIGH: 0.6,
            SecurityLevel.CRITICAL: 0.9,
        }

        base_score = base_scores.get(severity, 0.1)

        # Ajustar según tipo de evento
        event_multipliers = {
            "login_failed": 1.5,
            "2fa_verification_failed": 2.0,
            "recovery_token_used": 1.8,
            "jwt_token_revoked": 1.2,
            "anomaly_detected": 2.5,
            "intrusion_attempt": 3.0,
        }

        multiplier = event_multipliers.get(event_type, 1.0)

        return min(base_score * multiplier, 1.0)

    def _calculate_user_risk_score(self, user_id: str) -> float:
        """Calcular puntuación de riesgo del usuario"""
        try:
            # Obtener eventos recientes
            recent_events = self._get_recent_security_events(user_id, 7)

            if not recent_events:
                return 0.0

            # Calcular puntuación promedio
            total_risk = sum(event.get("risk_score", 0) for event in recent_events)
            avg_risk = total_risk / len(recent_events)

            # Ajustar por frecuencia de eventos
            frequency_factor = min(len(recent_events) / 10, 2.0)  # Máximo 2x

            return min(avg_risk * frequency_factor, 1.0)

        except Exception as e:
            logger.error(f"❌ Error calculando riesgo del usuario: {e}")
            return 0.0

    def _get_recent_security_events(
        self, user_id: str, days: int
    ) -> List[Dict[str, Any]]:
        """Obtener eventos de seguridad recientes"""
        try:
            since_date = datetime.utcnow() - timedelta(days=days)

            conn = sqlite3.connect(str(self.db_path))
            cursor = conn.cursor()
            cursor.execute(
                """
                SELECT event_id, event_type, severity, timestamp, ip_address, 
                       device_info, details, risk_score
                FROM security_events 
                WHERE user_id = ? AND timestamp >= ?
                ORDER BY timestamp DESC
            """,
                (user_id, since_date),
            )

            events = []
            for row in cursor.fetchall():
                events.append(
                    {
                        "event_id": row[0],
                        "event_type": row[1],
                        "severity": row[2],
                        "timestamp": row[3],
                        "ip_address": row[4],
                        "device_info": json.loads(row[5]) if row[5] else None,
                        "details": json.loads(row[6]) if row[6] else None,
                        "risk_score": row[7],
                    }
                )

            conn.close()
            return events

        except Exception as e:
            logger.error(f"❌ Error obteniendo eventos de seguridad: {e}")
            return []


# ==================== COMPONENTES AUXILIARES ====================


class UserActivityMonitor:
    """Monitor de actividad de usuarios"""

    def __init__(self, db_path: str):
        self.db_path = db_path

    def log_activity(
        self,
        user_id: str,
        activity_type: str,
        details: Optional[Dict[str, Any]] = None,
        ip_address: Optional[str] = None,
        device_info: Optional[Dict[str, Any]] = None,
    ) -> str:
        """Registrar actividad del usuario"""
        # Implementación simplificada
        return str(uuid.uuid4())

    def get_user_activity_summary(self, user_id: str, days: int) -> Dict[str, Any]:
        """Obtener resumen de actividad del usuario"""
        # Implementación simplificada
        return {
            "total_activities": 0,
            "last_activity": datetime.utcnow().isoformat(),
            "activity_types": {},
        }


class UserAnomalyDetector:
    """Detector de anomalías de usuarios"""

    def __init__(self, db_path: str):
        self.db_path = db_path

    def detect_anomalies(self, user_id: str) -> Dict[str, Any]:
        """Detectar anomalías para un usuario"""
        # Implementación simplificada
        return {"anomalies_detected": False, "risk_score": 0.0, "anomaly_types": []}

    def get_recent_anomalies(self, days: int) -> List[Dict[str, Any]]:
        """Obtener anomalías recientes"""
        # Implementación simplificada
        return []


class IntrusionDetectionSystem:
    """Sistema de detección de intrusiones"""

    def analyze_activity(
        self,
        user_id: str,
        activity_type: str,
        ip_address: Optional[str] = None,
        device_info: Optional[Dict[str, Any]] = None,
    ) -> float:
        """Analizar actividad para detectar intrusiones"""
        # Implementación simplificada
        return 0.0


# ==================== FUNCIONES DE UTILIDAD ====================


def get_unified_auth_security_system(
    db_path: Optional[str] = None,
) -> UnifiedAuthSecuritySystem:
    """Obtener instancia del sistema de autenticación y seguridad"""
    return UnifiedAuthSecuritySystem(db_path)


async def main():
    """Función principal de demostración"""
    print("🔐 Sistema Unificado de Autenticación y Seguridad")
    print("=" * 50)

    # Inicializar sistema
    auth_system = get_unified_auth_security_system()

    # Ejemplo de uso
    user_id = "test_user_123"

    # Generar token JWT
    token = auth_system.generate_jwt_token(user_id)
    print(f"✅ Token JWT generado: {token[:20]}...")

    # Validar token
    payload = auth_system.validate_jwt_token(token)
    print(f"✅ Token validado para usuario: {payload['user_id']}")

    # Generar contraseña segura
    secure_password = auth_system.generate_secure_password()
    print(f"✅ Contraseña segura generada: {secure_password}")

    # Validar contraseña
    validation = auth_system.validate_password(secure_password)
    print(f"✅ Validación de contraseña: {validation['valid']}")

    # Firmar datos
    data = "Datos importantes para firmar"
    signature = auth_system.sign_data(data)
    print(f"✅ Firma digital generada: {signature[:20]}...")

    # Verificar firma
    is_valid = auth_system.verify_signature(data, signature)
    print(f"✅ Firma verificada: {is_valid}")

    print("\n🎉 Sistema de autenticación y seguridad funcionando correctamente")


if __name__ == "__main__":
    import asyncio

    asyncio.run(main())
