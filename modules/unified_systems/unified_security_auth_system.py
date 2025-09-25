"""
Sistema Unificado de Seguridad y Autenticación para NeuroFusion

Este módulo combina funcionalidades de:
- JWT Authentication (jwt_auth.py)
- Two Factor Authentication (two_factor_auth.py)
- Digital Signature (digital_signature.py)
- Account Recovery (account_recovery.py)
- Password Policy (password_policy.py)
- Intrusion Detection (intrusion_detection.py)
- User Activity Monitor (user_activity_monitor.py)
- User Anomaly Detector (user_anomaly_detector.py)
- Security Dashboard (security_dashboard.py)
- Security Orchestrator (security_orchestrator.py)
- Audit Logger (audit_logger.py)
"""

import logging
import json
import time
import sqlite3
import asyncio
import hashlib
import secrets
import base64
import hmac
from datetime import datetime, timedelta
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
from typing import Dict, List, Optional, Any, Tuple, Union
from collections import defaultdict
import jwt
import pyotp
import qrcode
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import rsa, padding
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.fernet import Fernet

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class SecurityLevel(Enum):
    """Niveles de seguridad"""

    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class AuthMethod(Enum):
    """Métodos de autenticación"""

    PASSWORD = os.getenv("DEFAULT_PASSWORD", "default_password")
    TWO_FACTOR = "two_factor"
    BIOMETRIC = "biometric"
    HARDWARE_KEY = "hardware_key"
    SSO = "sso"


class ThreatLevel(Enum):
    """Niveles de amenaza"""

    NONE = "none"
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


@dataclass
class SecurityConfig:
    """Configuración de seguridad"""

    jwt_secret: str = os.getenv("JWT_SECRET", "default_secret_key")
    jwt_algorithm: str = "HS256"
    jwt_expiration: int = 3600  # 1 hora
    password_min_length: int = 8
    password_require_special: bool = True
    password_require_numbers: bool = True
    password_require_uppercase: bool = True
    max_login_attempts: int = 5
    lockout_duration: int = 900  # 15 minutos
    session_timeout: int = 1800  # 30 minutos
    enable_2fa: bool = True
    enable_audit_logging: bool = True
    enable_intrusion_detection: bool = True


@dataclass
class UserSession:
    """Sesión de usuario"""

    user_id: str
    session_id: str
    auth_method: AuthMethod
    security_level: SecurityLevel
    created_at: datetime
    expires_at: datetime
    ip_address: str
    user_agent: str
    is_active: bool = True
    last_activity: datetime = field(default_factory=datetime.now)


@dataclass
class SecurityEvent:
    """Evento de seguridad"""

    event_id: str
    user_id: str
    event_type: str
    threat_level: ThreatLevel
    description: str
    ip_address: str
    user_agent: str
    timestamp: datetime
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class AuditLog:
    """Registro de auditoría"""

    log_id: str
    user_id: str
    action: str
    resource: str
    timestamp: datetime
    ip_address: str
    user_agent: str
    success: bool
    details: Dict[str, Any] = field(default_factory=dict)


class UnifiedSecurityAuthSystem:
    """Sistema unificado de seguridad y autenticación"""

    def __init__(
        self, config: Optional[SecurityConfig] = None, db_path: Optional[str] = None
    ):
        """Inicializar sistema unificado"""
        self.config = config or SecurityConfig()
        self.db_path = db_path or "./data/security_auth_system.db"

        # Componentes del sistema
        self.active_sessions: Dict[str, UserSession] = {}
        self.security_events: List[SecurityEvent] = []
        self.audit_logs: List[AuditLog] = []
        self.user_attempts: Dict[str, Dict[str, Any]] = defaultdict(dict)
        self.blocked_ips: Dict[str, datetime] = {}

        # Inicializar componentes
        self._init_database()
        self._init_security_components()
        self._init_auth_components()

        logger.info("✅ Sistema Unificado de Seguridad y Autenticación inicializado")

    def _init_database(self):
        """Inicializar base de datos"""
        try:
            # Crear directorio si no existe
            Path(self.db_path).parent.mkdir(parents=True, exist_ok=True)
            self.conn = sqlite3.connect(self.db_path)
            self._create_tables()
            logger.info("✅ Base de datos de seguridad y autenticación inicializada")
        except Exception as e:
            logger.error(f"Error inicializando base de datos: {e}")
            raise

    def _create_tables(self):
        """Crear tablas en base de datos"""
        cursor = self.conn.cursor()

        # Tabla de usuarios
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS users (
                id TEXT PRIMARY KEY,
                username TEXT UNIQUE NOT NULL,
                email TEXT UNIQUE NOT NULL,
                password_hash TEXT NOT NULL,
                salt TEXT NOT NULL,
                security_level TEXT NOT NULL,
                created_at TEXT NOT NULL,
                last_login TEXT,
                is_active BOOLEAN DEFAULT TRUE,
                metadata TEXT
            )
        """
        )

        # Tabla de sesiones
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS user_sessions (
                session_id TEXT PRIMARY KEY,
                user_id TEXT NOT NULL,
                auth_method TEXT NOT NULL,
                security_level TEXT NOT NULL,
                created_at TEXT NOT NULL,
                expires_at TEXT NOT NULL,
                ip_address TEXT NOT NULL,
                user_agent TEXT NOT NULL,
                is_active BOOLEAN DEFAULT TRUE,
                last_activity TEXT NOT NULL,
                FOREIGN KEY (user_id) REFERENCES users (id)
            )
        """
        )

        # Tabla de autenticación de dos factores
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS two_factor_auth (
                user_id TEXT PRIMARY KEY,
                secret_key TEXT NOT NULL,
                backup_codes TEXT NOT NULL,
                is_enabled BOOLEAN DEFAULT FALSE,
                created_at TEXT NOT NULL,
                last_used TEXT,
                FOREIGN KEY (user_id) REFERENCES users (id)
            )
        """
        )

        # Tabla de eventos de seguridad
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS security_events (
                event_id TEXT PRIMARY KEY,
                user_id TEXT,
                event_type TEXT NOT NULL,
                threat_level TEXT NOT NULL,
                description TEXT NOT NULL,
                ip_address TEXT NOT NULL,
                user_agent TEXT NOT NULL,
                timestamp TEXT NOT NULL,
                metadata TEXT,
                FOREIGN KEY (user_id) REFERENCES users (id)
            )
        """
        )

        # Tabla de registros de auditoría
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS audit_logs (
                log_id TEXT PRIMARY KEY,
                user_id TEXT,
                action TEXT NOT NULL,
                resource TEXT NOT NULL,
                timestamp TEXT NOT NULL,
                ip_address TEXT NOT NULL,
                user_agent TEXT NOT NULL,
                success BOOLEAN NOT NULL,
                details TEXT,
                FOREIGN KEY (user_id) REFERENCES users (id)
            )
        """
        )

        # Tabla de recuperación de cuentas
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS account_recovery (
                recovery_id TEXT PRIMARY KEY,
                user_id TEXT NOT NULL,
                recovery_token TEXT NOT NULL,
                expires_at TEXT NOT NULL,
                used BOOLEAN DEFAULT FALSE,
                created_at TEXT NOT NULL,
                FOREIGN KEY (user_id) REFERENCES users (id)
            )
        """
        )

        # Tabla de firmas digitales
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS digital_signatures (
                signature_id TEXT PRIMARY KEY,
                user_id TEXT NOT NULL,
                data_hash TEXT NOT NULL,
                signature TEXT NOT NULL,
                public_key TEXT NOT NULL,
                created_at TEXT NOT NULL,
                verified BOOLEAN DEFAULT FALSE,
                FOREIGN KEY (user_id) REFERENCES users (id)
            )
        """
        )

        # Índices
        cursor.execute(
            "CREATE INDEX IF NOT EXISTS idx_user_sessions ON user_sessions(user_id)"
        )
        cursor.execute(
            "CREATE INDEX IF NOT EXISTS idx_session_expires ON user_sessions(expires_at)"
        )
        cursor.execute(
            "CREATE INDEX IF NOT EXISTS idx_security_events ON security_events(user_id, timestamp)"
        )
        cursor.execute(
            "CREATE INDEX IF NOT EXISTS idx_audit_logs ON audit_logs(user_id, timestamp)"
        )
        cursor.execute(
            "CREATE INDEX IF NOT EXISTS idx_recovery_token ON account_recovery(recovery_token)"
        )

        self.conn.commit()
        cursor.close()

    def _init_security_components(self):
        """Inicializar componentes de seguridad"""
        self.jwt_secret = self.config.jwt_secret
        self.fernet_key = Fernet.generate_key()
        self.fernet = Fernet(self.fernet_key)

        # Generar claves RSA para firmas digitales
        self.private_key = rsa.generate_private_key(
            public_exponent=65537, key_size=2048
        )
        self.public_key = self.private_key.public_key()

    def _init_auth_components(self):
        """Inicializar componentes de autenticación"""
        self.password_policy = {
            "min_length": self.config.password_min_length,
            "require_special": self.config.password_require_special,
            "require_numbers": self.config.password_require_numbers,
            "require_uppercase": self.config.password_require_uppercase,
        }

    async def register_user(
        self,
        username: str,
        email: str,
        password: str,
        security_level: SecurityLevel = SecurityLevel.MEDIUM,
    ) -> Dict[str, Any]:
        """Registrar nuevo usuario"""
        try:
            # Validar contraseña
            password_validation = self._validate_password(password)
            if not password_validation["valid"]:
                return {
                    "success": False,
                    "error": "Contraseña no cumple con los requisitos de seguridad",
                    "details": password_validation["issues"],
                }

            # Verificar si el usuario ya existe
            if await self._user_exists(username, email):
                return {"success": False, "error": "Usuario o email ya existe"}

            # Generar salt y hash de contraseña
            salt = secrets.token_hex(16)
            password_hash = self._hash_password(password, salt)

            # Crear usuario
            user_id = f"user_{int(time.time() * 1000)}"

            cursor = self.conn.cursor()
            cursor.execute(
                """
                INSERT INTO users (id, username, email, password_hash, salt, security_level, created_at)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """,
                (
                    user_id,
                    username,
                    email,
                    password_hash,
                    salt,
                    security_level.value,
                    datetime.now().isoformat(),
                ),
            )

            self.conn.commit()
            cursor.close()

            # Registrar evento de auditoría
            await self._log_audit_event(
                user_id,
                "user_registration",
                "users",
                True,
                {
                    "username": username,
                    "email": email,
                    "security_level": security_level.value,
                },
            )

            return {
                "success": True,
                "user_id": user_id,
                "message": "Usuario registrado exitosamente",
            }

        except Exception as e:
            logger.error(f"Error registrando usuario: {e}")
            return {"success": False, "error": str(e)}

    async def authenticate_user(
        self,
        username: str,
        password: str,
        ip_address: str,
        user_agent: str,
        auth_method: AuthMethod = AuthMethod.PASSWORD,
    ) -> Dict[str, Any]:
        """Autenticar usuario"""
        try:
            # Verificar si la IP está bloqueada
            if self._is_ip_blocked(ip_address):
                return {
                    "success": False,
                    "error": "IP bloqueada por múltiples intentos fallidos",
                }

            # Obtener usuario
            user = await self._get_user_by_username(username)
            if not user:
                await self._record_failed_attempt(ip_address, username)
                return {"success": False, "error": "Credenciales inválidas"}

            # Verificar contraseña
            if not self._verify_password(password, user["password_hash"], user["salt"]):
                await self._record_failed_attempt(ip_address, username)
                return {"success": False, "error": "Credenciales inválidas"}

            # Verificar si la cuenta está activa
            if not user["is_active"]:
                return {"success": False, "error": "Cuenta desactivada"}

            # Crear sesión
            session = await self._create_user_session(
                user["id"],
                auth_method,
                SecurityLevel(user["security_level"]),
                ip_address,
                user_agent,
            )

            # Generar JWT
            jwt_token = self._generate_jwt_token(user["id"], session.session_id)

            # Actualizar último login
            await self._update_last_login(user["id"])

            # Registrar evento de auditoría
            await self._log_audit_event(
                user["id"],
                "user_login",
                "sessions",
                True,
                {"auth_method": auth_method.value, "ip_address": ip_address},
            )

            return {
                "success": True,
                "user_id": user["id"],
                "session_id": session.session_id,
                "jwt_token": jwt_token,
                "security_level": user["security_level"],
                "expires_at": session.expires_at.isoformat(),
            }

        except Exception as e:
            logger.error(f"Error autenticando usuario: {e}")
            return {"success": False, "error": str(e)}

    async def verify_jwt_token(self, token: str) -> Dict[str, Any]:
        """Verificar token JWT"""
        try:
            # Decodificar token
            payload = jwt.decode(
                token, self.jwt_secret, algorithms=[self.config.jwt_algorithm]
            )

            user_id = payload.get("user_id")
            session_id = payload.get("session_id")

            if not user_id or not session_id:
                return {"valid": False, "error": "Token inválido"}

            # Verificar sesión
            session = await self._get_session(session_id)
            if not session or not session.is_active:
                return {"valid": False, "error": "Sesión expirada o inválida"}

            # Verificar expiración
            if datetime.now() > session.expires_at:
                await self._deactivate_session(session_id)
                return {"valid": False, "error": "Sesión expirada"}

            # Actualizar última actividad
            session.last_activity = datetime.now()
            await self._update_session_activity(session_id)

            return {
                "valid": True,
                "user_id": user_id,
                "session_id": session_id,
                "security_level": session.security_level.value,
            }

        except jwt.ExpiredSignatureError:
            return {"valid": False, "error": "Token expirado"}
        except jwt.InvalidTokenError:
            return {"valid": False, "error": "Token inválido"}
        except Exception as e:
            logger.error(f"Error verificando token: {e}")
            return {"valid": False, "error": str(e)}

    async def setup_2fa(self, user_id: str) -> Dict[str, Any]:
        """Configurar autenticación de dos factores"""
        try:
            # Generar clave secreta
            secret_key = pyotp.random_base32()

            # Generar códigos de respaldo
            backup_codes = [secrets.token_hex(4).upper() for _ in range(5)]

            # Guardar configuración 2FA
            cursor = self.conn.cursor()
            cursor.execute(
                """
                INSERT OR REPLACE INTO two_factor_auth 
                (user_id, secret_key, backup_codes, is_enabled, created_at)
                VALUES (?, ?, ?, ?, ?)
            """,
                (
                    user_id,
                    secret_key,
                    json.dumps(backup_codes),
                    False,
                    datetime.now().isoformat(),
                ),
            )

            self.conn.commit()
            cursor.close()

            # Generar QR code
            totp = pyotp.TOTP(secret_key)
            provisioning_uri = totp.provisioning_uri(
                name=user_id, issuer_name="NeuroFusion"
            )

            return {
                "success": True,
                "secret_key": secret_key,
                "backup_codes": backup_codes,
                "qr_code_uri": provisioning_uri,
            }

        except Exception as e:
            logger.error(f"Error configurando 2FA: {e}")
            return {"success": False, "error": str(e)}

    async def verify_2fa(self, user_id: str, code: str) -> Dict[str, Any]:
        """Verificar código 2FA"""
        try:
            # Obtener configuración 2FA
            cursor = self.conn.cursor()
            cursor.execute(
                "SELECT secret_key, backup_codes FROM two_factor_auth WHERE user_id = ?",
                (user_id,),
            )
            result = cursor.fetchone()
            cursor.close()

            if not result:
                return {"valid": False, "error": "2FA no configurado"}

            secret_key, backup_codes_json = result
            backup_codes = json.loads(backup_codes_json)

            # Verificar código TOTP
            totp = pyotp.TOTP(secret_key)
            if totp.verify(code):
                return {"valid": True, "method": "totp"}

            # Verificar código de respaldo
            if code in backup_codes:
                # Remover código usado
                backup_codes.remove(code)
                cursor = self.conn.cursor()
                cursor.execute(
                    """
                    UPDATE two_factor_auth 
                    SET backup_codes = ?, last_used = ?
                    WHERE user_id = ?
                """,
                    (json.dumps(backup_codes), datetime.now().isoformat(), user_id),
                )
                self.conn.commit()
                cursor.close()

                return {"valid": True, "method": "backup_code"}

            return {"valid": False, "error": "Código inválido"}

        except Exception as e:
            logger.error(f"Error verificando 2FA: {e}")
            return {"valid": False, "error": str(e)}

    async def sign_data(self, user_id: str, data: str) -> Dict[str, Any]:
        """Firmar datos digitalmente"""
        try:
            # Generar hash de datos
            data_hash = hashlib.sha256(data.encode()).hexdigest()

            # Firmar hash
            signature = self.private_key.sign(
                data_hash.encode(),
                padding.PSS(
                    mgf=padding.MGF1(hashes.SHA256()),
                    salt_length=padding.PSS.MAX_LENGTH,
                ),
                hashes.SHA256(),
            )

            # Serializar clave pública
            public_key_pem = self.public_key.public_bytes(
                encoding=serialization.Encoding.PEM,
                format=serialization.PublicFormat.SubjectPublicKeyInfo,
            ).decode()

            # Guardar firma
            signature_id = f"sig_{int(time.time() * 1000)}"
            cursor = self.conn.cursor()
            cursor.execute(
                """
                INSERT INTO digital_signatures 
                (signature_id, user_id, data_hash, signature, public_key, created_at)
                VALUES (?, ?, ?, ?, ?, ?)
            """,
                (
                    signature_id,
                    user_id,
                    data_hash,
                    base64.b64encode(signature).decode(),
                    public_key_pem,
                    datetime.now().isoformat(),
                ),
            )

            self.conn.commit()
            cursor.close()

            return {
                "success": True,
                "signature_id": signature_id,
                "data_hash": data_hash,
                "signature": base64.b64encode(signature).decode(),
                "public_key": public_key_pem,
            }

        except Exception as e:
            logger.error(f"Error firmando datos: {e}")
            return {"success": False, "error": str(e)}

    async def verify_signature(
        self, data: str, signature: str, public_key_pem: str
    ) -> Dict[str, Any]:
        """Verificar firma digital"""
        try:
            # Generar hash de datos
            data_hash = hashlib.sha256(data.encode()).hexdigest()

            # Cargar clave pública
            public_key = serialization.load_pem_public_key(public_key_pem.encode())

            # Decodificar firma
            signature_bytes = base64.b64decode(signature)

            # Verificar firma
            public_key.verify(
                signature_bytes,
                data_hash.encode(),
                padding.PSS(
                    mgf=padding.MGF1(hashes.SHA256()),
                    salt_length=padding.PSS.MAX_LENGTH,
                ),
                hashes.SHA256(),
            )

            return {"valid": True, "data_hash": data_hash}

        except Exception as e:
            logger.error(f"Error verificando firma: {e}")
            return {"valid": False, "error": str(e)}

    async def generate_recovery_token(self, email: str) -> Dict[str, Any]:
        """Generar token de recuperación de cuenta"""
        try:
            # Obtener usuario por email
            user = await self._get_user_by_email(email)
            if not user:
                return {"success": False, "error": "Email no encontrado"}

            # Generar token
            recovery_token = secrets.token_urlsafe(32)
            expires_at = datetime.now() + timedelta(hours=1)

            # Guardar token
            recovery_id = f"rec_{int(time.time() * 1000)}"
            cursor = self.conn.cursor()
            cursor.execute(
                """
                INSERT INTO account_recovery 
                (recovery_id, user_id, recovery_token, expires_at, created_at)
                VALUES (?, ?, ?, ?, ?)
            """,
                (
                    recovery_id,
                    user["id"],
                    recovery_token,
                    expires_at.isoformat(),
                    datetime.now().isoformat(),
                ),
            )

            self.conn.commit()
            cursor.close()

            return {
                "success": True,
                "recovery_token": recovery_token,
                "expires_at": expires_at.isoformat(),
            }

        except Exception as e:
            logger.error(f"Error generando token de recuperación: {e}")
            return {"success": False, "error": str(e)}

    async def reset_password(
        self, recovery_token: str, new_password: str
    ) -> Dict[str, Any]:
        """Restablecer contraseña usando token de recuperación"""
        try:
            # Validar nueva contraseña
            password_validation = self._validate_password(new_password)
            if not password_validation["valid"]:
                return {
                    "success": False,
                    "error": "Contraseña no cumple con los requisitos de seguridad",
                    "details": password_validation["issues"],
                }

            # Verificar token
            cursor = self.conn.cursor()
            cursor.execute(
                """
                SELECT user_id, expires_at, used 
                FROM account_recovery 
                WHERE recovery_token = ?
            """,
                (recovery_token,),
            )
            result = cursor.fetchone()

            if not result:
                return {"success": False, "error": "Token de recuperación inválido"}

            user_id, expires_at, used = result

            if used:
                return {"success": False, "error": "Token ya utilizado"}

            if datetime.fromisoformat(expires_at) < datetime.now():
                return {"success": False, "error": "Token expirado"}

            # Actualizar contraseña
            salt = secrets.token_hex(16)
            password_hash = self._hash_password(new_password, salt)

            cursor.execute(
                """
                UPDATE users 
                SET password_hash = ?, salt = ?
                WHERE id = ?
            """,
                (password_hash, salt, user_id),
            )

            # Marcar token como usado
            cursor.execute(
                """
                UPDATE account_recovery 
                SET used = TRUE 
                WHERE recovery_token = ?
            """,
                (recovery_token,),
            )

            self.conn.commit()
            cursor.close()

            # Registrar evento de auditoría
            await self._log_audit_event(
                user_id, "password_reset", "users", True, {"method": "recovery_token"}
            )

            return {"success": True, "message": "Contraseña restablecida exitosamente"}

        except Exception as e:
            logger.error(f"Error restableciendo contraseña: {e}")
            return {"success": False, "error": str(e)}

    def _validate_password(self, password: str) -> Dict[str, Any]:
        """Validar contraseña según política"""
        issues = []

        if len(password) < self.password_policy["min_length"]:
            issues.append(
                f"La contraseña debe tener al menos {self.password_policy['min_length']} caracteres"
            )

        if self.password_policy["require_uppercase"] and not any(
            c.isupper() for c in password
        ):
            issues.append("La contraseña debe contener al menos una letra mayúscula")

        if self.password_policy["require_numbers"] and not any(
            c.isdigit() for c in password
        ):
            issues.append("La contraseña debe contener al menos un número")

        if self.password_policy["require_special"] and not any(
            c in "!@#$%^&*()_+-=[]{}|;:,.<>?" for c in password
        ):
            issues.append("La contraseña debe contener al menos un carácter especial")

        return {"valid": len(issues) == 0, "issues": issues}

    def _hash_password(self, password: str, salt: str) -> str:
        """Generar hash de contraseña"""
        return hashlib.pbkdf2_hmac(
            "sha256", password.encode(), salt.encode(), 100000
        ).hex()

    def _verify_password(self, password: str, stored_hash: str, salt: str) -> bool:
        """Verificar contraseña"""
        return self._hash_password(password, salt) == stored_hash

    def _generate_jwt_token(self, user_id: str, session_id: str) -> str:
        """Generar token JWT"""
        payload = {
            "user_id": user_id,
            "session_id": session_id,
            "exp": datetime.utcnow() + timedelta(seconds=self.config.jwt_expiration),
            "iat": datetime.utcnow(),
        }
        return jwt.encode(payload, self.jwt_secret, algorithm=self.config.jwt_algorithm)

    async def _create_user_session(
        self,
        user_id: str,
        auth_method: AuthMethod,
        security_level: SecurityLevel,
        ip_address: str,
        user_agent: str,
    ) -> UserSession:
        """Crear sesión de usuario"""
        session_id = f"session_{int(time.time() * 1000)}"
        created_at = datetime.now()
        expires_at = created_at + timedelta(seconds=self.config.session_timeout)

        session = UserSession(
            user_id=user_id,
            session_id=session_id,
            auth_method=auth_method,
            security_level=security_level,
            created_at=created_at,
            expires_at=expires_at,
            ip_address=ip_address,
            user_agent=user_agent,
        )

        # Guardar en base de datos
        cursor = self.conn.cursor()
        cursor.execute(
            """
            INSERT INTO user_sessions 
            (session_id, user_id, auth_method, security_level, created_at, expires_at, ip_address, user_agent, last_activity)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
            (
                session_id,
                user_id,
                auth_method.value,
                security_level.value,
                created_at.isoformat(),
                expires_at.isoformat(),
                ip_address,
                user_agent,
                created_at.isoformat(),
            ),
        )

        self.conn.commit()
        cursor.close()

        # Guardar en memoria
        self.active_sessions[session_id] = session

        return session

    async def _get_session(self, session_id: str) -> Optional[UserSession]:
        """Obtener sesión"""
        if session_id in self.active_sessions:
            return self.active_sessions[session_id]

        # Buscar en base de datos
        cursor = self.conn.cursor()
        cursor.execute(
            """
            SELECT user_id, auth_method, security_level, created_at, expires_at, 
                   ip_address, user_agent, is_active, last_activity
            FROM user_sessions 
            WHERE session_id = ?
        """,
            (session_id,),
        )
        result = cursor.fetchone()
        cursor.close()

        if result:
            session = UserSession(
                user_id=result[0],
                session_id=session_id,
                auth_method=AuthMethod(result[1]),
                security_level=SecurityLevel(result[2]),
                created_at=datetime.fromisoformat(result[3]),
                expires_at=datetime.fromisoformat(result[4]),
                ip_address=result[5],
                user_agent=result[6],
                is_active=bool(result[7]),
                last_activity=datetime.fromisoformat(result[8]),
            )
            self.active_sessions[session_id] = session
            return session

        return None

    async def _deactivate_session(self, session_id: str):
        """Desactivar sesión"""
        if session_id in self.active_sessions:
            del self.active_sessions[session_id]

        cursor = self.conn.cursor()
        cursor.execute(
            "UPDATE user_sessions SET is_active = FALSE WHERE session_id = ?",
            (session_id,),
        )
        self.conn.commit()
        cursor.close()

    async def _update_session_activity(self, session_id: str):
        """Actualizar actividad de sesión"""
        cursor = self.conn.cursor()
        cursor.execute(
            """
            UPDATE user_sessions 
            SET last_activity = ? 
            WHERE session_id = ?
        """,
            (datetime.now().isoformat(), session_id),
        )
        self.conn.commit()
        cursor.close()

    async def _get_user_by_username(self, username: str) -> Optional[Dict[str, Any]]:
        """Obtener usuario por nombre de usuario"""
        cursor = self.conn.cursor()
        cursor.execute(
            """
            SELECT id, username, email, password_hash, salt, security_level, is_active
            FROM users 
            WHERE username = ?
        """,
            (username,),
        )
        result = cursor.fetchone()
        cursor.close()

        if result:
            return {
                "id": result[0],
                "username": result[1],
                "email": result[2],
                "password_hash": result[3],
                "salt": result[4],
                "security_level": result[5],
                "is_active": bool(result[6]),
            }
        return None

    async def _get_user_by_email(self, email: str) -> Optional[Dict[str, Any]]:
        """Obtener usuario por email"""
        cursor = self.conn.cursor()
        cursor.execute(
            """
            SELECT id, username, email, password_hash, salt, security_level, is_active
            FROM users 
            WHERE email = ?
        """,
            (email,),
        )
        result = cursor.fetchone()
        cursor.close()

        if result:
            return {
                "id": result[0],
                "username": result[1],
                "email": result[2],
                "password_hash": result[3],
                "salt": result[4],
                "security_level": result[5],
                "is_active": bool(result[6]),
            }
        return None

    async def _user_exists(self, username: str, email: str) -> bool:
        """Verificar si el usuario existe"""
        cursor = self.conn.cursor()
        cursor.execute(
            "SELECT COUNT(*) FROM users WHERE username = ? OR email = ?",
            (username, email),
        )
        count = cursor.fetchone()[0]
        cursor.close()
        return count > 0

    async def _update_last_login(self, user_id: str):
        """Actualizar último login"""
        cursor = self.conn.cursor()
        cursor.execute(
            "UPDATE users SET last_login = ? WHERE id = ?",
            (datetime.now().isoformat(), user_id),
        )
        self.conn.commit()
        cursor.close()

    def _is_ip_blocked(self, ip_address: str) -> bool:
        """Verificar si IP está bloqueada"""
        if ip_address in self.blocked_ips:
            block_until = self.blocked_ips[ip_address]
            if datetime.now() < block_until:
                return True
            else:
                del self.blocked_ips[ip_address]
        return False

    async def _record_failed_attempt(self, ip_address: str, username: str):
        """Registrar intento fallido"""
        if ip_address not in self.user_attempts:
            self.user_attempts[ip_address] = {
                "count": 0,
                "first_attempt": datetime.now(),
                "usernames": set(),
                "last_attempt": datetime.now(),
            }

        self.user_attempts[ip_address]["count"] += 1
        self.user_attempts[ip_address]["usernames"].add(username)
        self.user_attempts[ip_address]["last_attempt"] = datetime.now()

        # Verificar si hay demasiados intentos en poco tiempo
        time_since_first = (
            datetime.now() - self.user_attempts[ip_address]["first_attempt"]
        ).total_seconds()

        # Bloquear IP si hay demasiados intentos o si son muy rápidos
        should_block = self.user_attempts[ip_address][
            "count"
        ] >= self.config.max_login_attempts or (
            self.user_attempts[ip_address]["count"] >= 3 and time_since_first < 60
        )  # 3 intentos en 1 minuto

        if should_block:
            block_until = datetime.now() + timedelta(
                seconds=self.config.lockout_duration
            )
            self.blocked_ips[ip_address] = block_until

            # Determinar nivel de amenaza
            threat_level = (
                ThreatLevel.CRITICAL if time_since_first < 60 else ThreatLevel.HIGH
            )

            # Registrar evento de seguridad
            await self._log_security_event(
                None,
                "multiple_failed_attempts",
                threat_level,
                f"Múltiples intentos fallidos desde IP {ip_address} en {time_since_first:.1f}s",
                ip_address,
                "Unknown",
            )

            logger.warning(
                f"IP {ip_address} bloqueada por {self.config.lockout_duration}s"
            )

    async def _log_security_event(
        self,
        user_id: Optional[str],
        event_type: str,
        threat_level: ThreatLevel,
        description: str,
        ip_address: str,
        user_agent: str,
    ):
        """Registrar evento de seguridad"""
        event_id = f"sec_{int(time.time() * 1000)}"
        event = SecurityEvent(
            event_id=event_id,
            user_id=user_id or "unknown",
            event_type=event_type,
            threat_level=threat_level,
            description=description,
            ip_address=ip_address,
            user_agent=user_agent,
            timestamp=datetime.now(),
        )

        # Guardar en base de datos
        cursor = self.conn.cursor()
        cursor.execute(
            """
            INSERT INTO security_events 
            (event_id, user_id, event_type, threat_level, description, ip_address, user_agent, timestamp)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """,
            (
                event_id,
                user_id,
                event_type,
                threat_level.value,
                description,
                ip_address,
                user_agent,
                datetime.now().isoformat(),
            ),
        )

        self.conn.commit()
        cursor.close()

        # Guardar en memoria
        self.security_events.append(event)

    async def _log_audit_event(
        self,
        user_id: str,
        action: str,
        resource: str,
        success: bool,
        details: Dict[str, Any],
    ):
        """Registrar evento de auditoría"""
        if not self.config.enable_audit_logging:
            return

        log_id = f"audit_{int(time.time() * 1000)}"
        log = AuditLog(
            log_id=log_id,
            user_id=user_id,
            action=action,
            resource=resource,
            timestamp=datetime.now(),
            ip_address="unknown",
            user_agent="unknown",
            success=success,
            details=details,
        )

        # Guardar en base de datos
        cursor = self.conn.cursor()
        cursor.execute(
            """
            INSERT INTO audit_logs 
            (log_id, user_id, action, resource, timestamp, ip_address, user_agent, success, details)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
            (
                log_id,
                user_id,
                action,
                resource,
                datetime.now().isoformat(),
                log.ip_address,
                log.user_agent,
                success,
                json.dumps(details),
            ),
        )

        self.conn.commit()
        cursor.close()

        # Guardar en memoria
        self.audit_logs.append(log)

    def get_security_stats(self) -> Dict[str, Any]:
        """Obtener estadísticas de seguridad"""
        try:
            cursor = self.conn.cursor()

            # Estadísticas de usuarios
            cursor.execute("SELECT COUNT(*) FROM users")
            total_users = cursor.fetchone()[0]

            cursor.execute("SELECT COUNT(*) FROM users WHERE is_active = TRUE")
            active_users = cursor.fetchone()[0]

            # Estadísticas de sesiones
            cursor.execute("SELECT COUNT(*) FROM user_sessions WHERE is_active = TRUE")
            active_sessions = cursor.fetchone()[0]

            # Estadísticas de eventos de seguridad
            cursor.execute("SELECT COUNT(*) FROM security_events")
            total_security_events = cursor.fetchone()[0]

            cursor.execute(
                "SELECT COUNT(*) FROM security_events WHERE threat_level = 'high' OR threat_level = 'critical'"
            )
            high_threat_events = cursor.fetchone()[0]

            # Estadísticas de auditoría
            cursor.execute("SELECT COUNT(*) FROM audit_logs")
            total_audit_logs = cursor.fetchone()[0]

            cursor.close()

            return {
                "users": {
                    "total": total_users,
                    "active": active_users,
                    "inactive": total_users - active_users,
                },
                "sessions": {
                    "active": active_sessions,
                    "in_memory": len(self.active_sessions),
                },
                "security": {
                    "total_events": total_security_events,
                    "high_threat_events": high_threat_events,
                    "blocked_ips": len(self.blocked_ips),
                },
                "audit": {
                    "total_logs": total_audit_logs,
                    "in_memory": len(self.audit_logs),
                },
            }

        except Exception as e:
            logger.error(f"Error obteniendo estadísticas de seguridad: {e}")
            return {"error": str(e)}

    def close(self):
        """Cerrar sistema"""
        try:
            if hasattr(self, "conn"):
                self.conn.close()
            logger.info("✅ Sistema de seguridad y autenticación cerrado")
        except Exception as e:
            logger.error(f"Error cerrando sistema: {e}")


def get_unified_security_auth_system(
    config: Optional[SecurityConfig] = None, db_path: Optional[str] = None
) -> UnifiedSecurityAuthSystem:
    """Función factory para crear sistema unificado"""
    return UnifiedSecurityAuthSystem(config, db_path)


async def main():
    """Función principal de demostración"""
    # Configurar sistema
    config = SecurityConfig(
        jwt_secret="neurofusion_demo_secret_key_2024",
        enable_2fa=True,
        enable_audit_logging=True,
        enable_intrusion_detection=True,
    )

    system = get_unified_security_auth_system(config)

    print("🚀 Sistema Unificado de Seguridad y Autenticación")
    print("=" * 50)

    # Ejemplo de registro de usuario
    print("\n👤 Registro de Usuario:")
    register_result = await system.register_user(
        username="demo_user",
        email="demo@neurofusion.com",
        password="SecurePass123!",
        security_level=SecurityLevel.HIGH,
    )

    if register_result["success"]:
        print(f"   ✅ Usuario registrado: {register_result['user_id']}")
        user_id = register_result["user_id"]
    else:
        print(f"   ❌ Error: {register_result['error']}")
        return

    # Ejemplo de autenticación
    print("\n🔐 Autenticación:")
    auth_result = await system.authenticate_user(
        username="demo_user",
        password="SecurePass123!",
        ip_address="192.168.1.100",
        user_agent="Mozilla/5.0 (Demo Browser)",
    )

    if auth_result["success"]:
        print(f"   ✅ Autenticación exitosa")
        print(f"   JWT Token: {auth_result['jwt_token'][:50]}...")
        jwt_token = auth_result["jwt_token"]
    else:
        print(f"   ❌ Error: {auth_result['error']}")
        return

    # Ejemplo de verificación de token
    print("\n🔍 Verificación de Token:")
    verify_result = await system.verify_jwt_token(jwt_token)

    if verify_result["valid"]:
        print(f"   ✅ Token válido")
        print(f"   Usuario: {verify_result['user_id']}")
        print(f"   Nivel de seguridad: {verify_result['security_level']}")
    else:
        print(f"   ❌ Error: {verify_result['error']}")

    # Ejemplo de configuración 2FA
    print("\n🔐 Configuración 2FA:")
    twofa_result = await system.setup_2fa(user_id)

    if twofa_result["success"]:
        print(f"   ✅ 2FA configurado")
        print(f"   Clave secreta: {twofa_result['secret_key'][:10]}...")
        print(f"   Códigos de respaldo: {twofa_result['backup_codes'][:2]}...")
    else:
        print(f"   ❌ Error: {twofa_result['error']}")

    # Ejemplo de firma digital
    print("\n✍️ Firma Digital:")
    data_to_sign = "Datos importantes de NeuroFusion"
    sign_result = await system.sign_data(user_id, data_to_sign)

    if sign_result["success"]:
        print(f"   ✅ Datos firmados")
        print(f"   ID de firma: {sign_result['signature_id']}")
        print(f"   Hash: {sign_result['data_hash'][:20]}...")
    else:
        print(f"   ❌ Error: {sign_result['error']}")

    # Estadísticas
    print("\n📊 Estadísticas del Sistema:")
    stats = system.get_security_stats()
    print(f"   Usuarios totales: {stats['users']['total']}")
    print(f"   Sesiones activas: {stats['sessions']['active']}")
    print(f"   Eventos de seguridad: {stats['security']['total_events']}")
    print(f"   Registros de auditoría: {stats['audit']['total_logs']}")

    # Cerrar sistema
    system.close()


if __name__ == "__main__":
    asyncio.run(main())
