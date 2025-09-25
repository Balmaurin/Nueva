#!/usr/bin/env python3
"""
Sistema de Autenticación Real para Shaili AI
============================================
Implementación completa de autenticación multi-factor y gestión de sesiones
"""

import hashlib
import hmac
import secrets
import time
import json
import logging
import sqlite3
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, Any, Optional, Tuple
import pyotp
import qrcode
from cryptography.fernet import Fernet
import jwt
import bcrypt

# Configurar logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


class MultiFactorAuth:
    """Sistema de autenticación multi-factor"""

    def __init__(self, db_path: str = "modules/security/auth.db"):
        self.db_path = db_path
        self.encryption_key = self._load_or_generate_encryption_key()
        self.cipher = Fernet(self.encryption_key)

        # Crear directorio si no existe
        Path(self.db_path).parent.mkdir(parents=True, exist_ok=True)

        # Inicializar base de datos
        self._init_database()

    def _load_or_generate_encryption_key(self) -> bytes:
        """Cargar o generar clave de encriptación"""
        key_path = Path("modules/security/encryption.key")

        if key_path.exists():
            try:
                with open(key_path, "rb") as f:
                    return f.read()
            except Exception as e:
                logger.error(f"❌ Error cargando clave de encriptación: {e}")

        # Generar nueva clave
        key = Fernet.generate_key()
        try:
            with open(key_path, "wb") as f:
                f.write(key)
            logger.info("✅ Nueva clave de encriptación generada")
        except Exception as e:
            logger.error(f"❌ Error guardando clave de encriptación: {e}")

        return key

    def _init_database(self):
        """Inicializar base de datos de autenticación"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()

                # Tabla de usuarios
                cursor.execute(
                    """
                    CREATE TABLE IF NOT EXISTS users (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        username TEXT UNIQUE NOT NULL,
                        email TEXT UNIQUE NOT NULL,
                        password_hash TEXT NOT NULL,
                        mfa_secret TEXT,
                        mfa_enabled BOOLEAN DEFAULT FALSE,
                        account_locked BOOLEAN DEFAULT FALSE,
                        failed_login_attempts INTEGER DEFAULT 0,
                        last_failed_login DATETIME,
                        account_created DATETIME DEFAULT CURRENT_TIMESTAMP,
                        last_login DATETIME,
                        is_active BOOLEAN DEFAULT TRUE
                    )
                """
                )

                # Tabla de sesiones
                cursor.execute(
                    """
                    CREATE TABLE IF NOT EXISTS sessions (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        user_id INTEGER NOT NULL,
                        session_token TEXT UNIQUE NOT NULL,
                        created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                        expires_at DATETIME NOT NULL,
                        ip_address TEXT,
                        user_agent TEXT,
                        is_active BOOLEAN DEFAULT TRUE,
                        FOREIGN KEY (user_id) REFERENCES users (id)
                    )
                """
                )

                # Tabla de intentos de login
                cursor.execute(
                    """
                    CREATE TABLE IF NOT EXISTS login_attempts (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        username TEXT NOT NULL,
                        ip_address TEXT,
                        timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                        success BOOLEAN DEFAULT FALSE,
                        failure_reason TEXT
                    )
                """
                )

                # Tabla de códigos de recuperación
                cursor.execute(
                    """
                    CREATE TABLE IF NOT EXISTS recovery_codes (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        user_id INTEGER NOT NULL,
                        code_hash TEXT NOT NULL,
                        used BOOLEAN DEFAULT FALSE,
                        created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                        expires_at DATETIME NOT NULL,
                        FOREIGN KEY (user_id) REFERENCES users (id)
                    )
                """
                )

                conn.commit()
                logger.info("✅ Base de datos de autenticación inicializada")

        except Exception as e:
            logger.error(f"❌ Error inicializando base de datos: {e}")

    def create_user(self, username: str, email: str, password: str) -> bool:
        """Crear nuevo usuario"""
        try:
            # Validar datos de entrada
            if not self._validate_username(username):
                logger.warning(f"❌ Nombre de usuario inválido: {username}")
                return False

            if not self._validate_email(email):
                logger.warning(f"❌ Email inválido: {email}")
                return False

            if not self._validate_password(password):
                logger.warning("❌ Contraseña no cumple requisitos de seguridad")
                return False

            # Hashear contraseña
            password_hash = self._hash_password(password)

            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()

                cursor.execute(
                    """
                    INSERT INTO users (username, email, password_hash)
                    VALUES (?, ?, ?)
                """,
                    (username, email, password_hash),
                )

                conn.commit()
                logger.info(f"✅ Usuario creado: {username}")
                return True

        except sqlite3.IntegrityError:
            logger.error(f"❌ Usuario o email ya existe: {username}")
            return False
        except Exception as e:
            logger.error(f"❌ Error creando usuario: {e}")
            return False

    def authenticate_user(
        self,
        username: str,
        password: str,
        mfa_token: str = None,
        ip_address: str = None,
    ) -> Tuple[bool, str, Optional[str]]:
        """Autenticar usuario"""
        try:
            # Verificar si la cuenta está bloqueada
            if self._is_account_locked(username):
                logger.warning(f"❌ Cuenta bloqueada: {username}")
                return False, "Cuenta bloqueada por múltiples intentos fallidos", None

            # Verificar credenciales
            user_data = self._get_user_by_username(username)
            if not user_data:
                self._record_failed_login(username, ip_address, "Usuario no encontrado")
                return False, "Credenciales inválidas", None

            # Verificar contraseña
            if not self._verify_password(password, user_data["password_hash"]):
                self._record_failed_login(username, ip_address, "Contraseña incorrecta")
                self._increment_failed_attempts(username)
                return False, "Credenciales inválidas", None

            # Verificar MFA si está habilitado
            if user_data["mfa_enabled"]:
                if not mfa_token:
                    return False, "Token MFA requerido", None

                if not self._verify_mfa_token(user_data["mfa_secret"], mfa_token):
                    self._record_failed_login(
                        username, ip_address, "Token MFA inválido"
                    )
                    return False, "Token MFA inválido", None

            # Autenticación exitosa
            self._reset_failed_attempts(username)
            self._update_last_login(username)
            self._record_successful_login(username, ip_address)

            # Generar token de sesión
            session_token = self._create_session(user_data["id"], ip_address)

            logger.info(f"✅ Usuario autenticado: {username}")
            return True, "Autenticación exitosa", session_token

        except Exception as e:
            logger.error(f"❌ Error en autenticación: {e}")
            return False, "Error interno del sistema", None

    def setup_mfa(self, username: str) -> Tuple[bool, str, Optional[str]]:
        """Configurar MFA para usuario"""
        try:
            user_data = self._get_user_by_username(username)
            if not user_data:
                return False, "Usuario no encontrado", None

            # Generar secreto MFA
            mfa_secret = pyotp.random_base32()

            # Generar código QR
            totp = pyotp.TOTP(mfa_secret)
            provisioning_uri = totp.provisioning_uri(
                name=user_data["email"], issuer_name="Shaili AI"
            )

            # Generar códigos de recuperación
            recovery_codes = self._generate_recovery_codes(user_data["id"])

            # Guardar secreto MFA (encriptado)
            encrypted_secret = self.cipher.encrypt(mfa_secret.encode()).decode()

            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()

                cursor.execute(
                    """
                    UPDATE users 
                    SET mfa_secret = ?, mfa_enabled = TRUE
                    WHERE id = ?
                """,
                    (encrypted_secret, user_data["id"]),
                )

                conn.commit()

            logger.info(f"✅ MFA configurado para: {username}")
            return True, "MFA configurado exitosamente", provisioning_uri

        except Exception as e:
            logger.error(f"❌ Error configurando MFA: {e}")
            return False, "Error configurando MFA", None

    def verify_mfa_token(self, username: str, token: str) -> bool:
        """Verificar token MFA"""
        try:
            user_data = self._get_user_by_username(username)
            if not user_data or not user_data["mfa_enabled"]:
                return False

            # Desencriptar secreto
            encrypted_secret = user_data["mfa_secret"]
            mfa_secret = self.cipher.decrypt(encrypted_secret.encode()).decode()

            return self._verify_mfa_token(mfa_secret, token)

        except Exception as e:
            logger.error(f"❌ Error verificando token MFA: {e}")
            return False

    def generate_recovery_codes(
        self, username: str
    ) -> Tuple[bool, str, Optional[list]]:
        """Generar códigos de recuperación"""
        try:
            user_data = self._get_user_by_username(username)
            if not user_data:
                return False, "Usuario no encontrado", None

            recovery_codes = self._generate_recovery_codes(user_data["id"])

            logger.info(f"✅ Códigos de recuperación generados para: {username}")
            return True, "Códigos de recuperación generados", recovery_codes

        except Exception as e:
            logger.error(f"❌ Error generando códigos de recuperación: {e}")
            return False, "Error generando códigos", None

    def verify_recovery_code(self, username: str, code: str) -> bool:
        """Verificar código de recuperación"""
        try:
            user_data = self._get_user_by_username(username)
            if not user_data:
                return False

            # Hashear código
            code_hash = hashlib.sha256(code.encode()).hexdigest()

            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()

                cursor.execute(
                    """
                    SELECT id FROM recovery_codes 
                    WHERE user_id = ? AND code_hash = ? AND used = FALSE AND expires_at > ?
                """,
                    (user_data["id"], code_hash, datetime.now().isoformat()),
                )

                result = cursor.fetchone()

                if result:
                    # Marcar código como usado
                    cursor.execute(
                        """
                        UPDATE recovery_codes 
                        SET used = TRUE 
                        WHERE id = ?
                    """,
                        (result[0],),
                    )

                    conn.commit()
                    return True

            return False

        except Exception as e:
            logger.error(f"❌ Error verificando código de recuperación: {e}")
            return False

    def validate_session(self, session_token: str) -> Optional[Dict[str, Any]]:
        """Validar token de sesión"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()

                cursor.execute(
                    """
                    SELECT s.*, u.username, u.email 
                    FROM sessions s
                    JOIN users u ON s.user_id = u.id
                    WHERE s.session_token = ? AND s.is_active = TRUE AND s.expires_at > ?
                """,
                    (session_token, datetime.now().isoformat()),
                )

                result = cursor.fetchone()

                if result:
                    # Actualizar última actividad
                    cursor.execute(
                        """
                        UPDATE sessions 
                        SET expires_at = ? 
                        WHERE id = ?
                    """,
                        ((datetime.now() + timedelta(hours=24)).isoformat(), result[0]),
                    )

                    conn.commit()

                    return {
                        "session_id": result[0],
                        "user_id": result[1],
                        "username": result[7],
                        "email": result[8],
                        "ip_address": result[5],
                        "created_at": result[3],
                    }

            return None

        except Exception as e:
            logger.error(f"❌ Error validando sesión: {e}")
            return None

    def revoke_session(self, session_token: str) -> bool:
        """Revocar sesión"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()

                cursor.execute(
                    """
                    UPDATE sessions 
                    SET is_active = FALSE 
                    WHERE session_token = ?
                """,
                    (session_token,),
                )

                conn.commit()

                logger.info("✅ Sesión revocada")
                return True

        except Exception as e:
            logger.error(f"❌ Error revocando sesión: {e}")
            return False

    def _validate_username(self, username: str) -> bool:
        """Validar nombre de usuario"""
        return len(username) >= 3 and len(username) <= 50 and username.isalnum()

    def _validate_email(self, email: str) -> bool:
        """Validar email"""
        import re

        pattern = r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"
        return re.match(pattern, email) is not None

    def _validate_password(self, password: str) -> bool:
        """Validar contraseña"""
        # Mínimo 8 caracteres, al menos una mayúscula, una minúscula y un número
        if len(password) < 8:
            return False

        has_upper = any(c.isupper() for c in password)
        has_lower = any(c.islower() for c in password)
        has_digit = any(c.isdigit() for c in password)

        return has_upper and has_lower and has_digit

    def _hash_password(self, password: str) -> str:
        """Hashear contraseña"""
        salt = bcrypt.gensalt()
        return bcrypt.hashpw(password.encode(), salt).decode()

    def _verify_password(self, password: str, password_hash: str) -> bool:
        """Verificar contraseña"""
        return bcrypt.checkpw(password.encode(), password_hash.encode())

    def _verify_mfa_token(self, secret: str, token: str) -> bool:
        """Verificar token MFA"""
        totp = pyotp.TOTP(secret)
        return totp.verify(token)

    def _get_user_by_username(self, username: str) -> Optional[Dict[str, Any]]:
        """Obtener usuario por nombre de usuario"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()

                cursor.execute(
                    """
                    SELECT * FROM users WHERE username = ?
                """,
                    (username,),
                )

                result = cursor.fetchone()

                if result:
                    columns = [description[0] for description in cursor.description]
                    return dict(zip(columns, result))

            return None

        except Exception as e:
            logger.error(f"❌ Error obteniendo usuario: {e}")
            return None

    def _is_account_locked(self, username: str) -> bool:
        """Verificar si la cuenta está bloqueada"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()

                cursor.execute(
                    """
                    SELECT account_locked, failed_login_attempts, last_failed_login
                    FROM users WHERE username = ?
                """,
                    (username,),
                )

                result = cursor.fetchone()

                if result:
                    account_locked, failed_attempts, last_failed = result

                    # Si la cuenta está bloqueada, verificar si han pasado 30 minutos
                    if account_locked and last_failed:
                        last_failed_dt = datetime.fromisoformat(last_failed)
                        if datetime.now() - last_failed_dt > timedelta(minutes=30):
                            # Desbloquear cuenta
                            cursor.execute(
                                """
                                UPDATE users 
                                SET account_locked = FALSE, failed_login_attempts = 0
                                WHERE username = ?
                            """,
                                (username,),
                            )
                            conn.commit()
                            return False

                    return account_locked

            return False

        except Exception as e:
            logger.error(f"❌ Error verificando bloqueo de cuenta: {e}")
            return False

    def _increment_failed_attempts(self, username: str):
        """Incrementar intentos fallidos"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()

                cursor.execute(
                    """
                    UPDATE users 
                    SET failed_login_attempts = failed_login_attempts + 1,
                        last_failed_login = ?
                    WHERE username = ?
                """,
                    (datetime.now().isoformat(), username),
                )

                # Bloquear cuenta si hay 5 intentos fallidos
                cursor.execute(
                    """
                    UPDATE users 
                    SET account_locked = TRUE
                    WHERE username = ? AND failed_login_attempts >= 5
                """,
                    (username,),
                )

                conn.commit()

        except Exception as e:
            logger.error(f"❌ Error incrementando intentos fallidos: {e}")

    def _reset_failed_attempts(self, username: str):
        """Resetear intentos fallidos"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()

                cursor.execute(
                    """
                    UPDATE users 
                    SET failed_login_attempts = 0, account_locked = FALSE
                    WHERE username = ?
                """,
                    (username,),
                )

                conn.commit()

        except Exception as e:
            logger.error(f"❌ Error reseteando intentos fallidos: {e}")

    def _update_last_login(self, username: str):
        """Actualizar último login"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()

                cursor.execute(
                    """
                    UPDATE users 
                    SET last_login = ?
                    WHERE username = ?
                """,
                    (datetime.now().isoformat(), username),
                )

                conn.commit()

        except Exception as e:
            logger.error(f"❌ Error actualizando último login: {e}")

    def _create_session(self, user_id: int, ip_address: str = None) -> str:
        """Crear sesión"""
        try:
            session_token = secrets.token_urlsafe(32)
            expires_at = datetime.now() + timedelta(hours=24)

            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()

                cursor.execute(
                    """
                    INSERT INTO sessions (user_id, session_token, expires_at, ip_address)
                    VALUES (?, ?, ?, ?)
                """,
                    (user_id, session_token, expires_at.isoformat(), ip_address),
                )

                conn.commit()

            return session_token

        except Exception as e:
            logger.error(f"❌ Error creando sesión: {e}")
            return None

    def _record_failed_login(self, username: str, ip_address: str, reason: str):
        """Registrar intento de login fallido"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()

                cursor.execute(
                    """
                    INSERT INTO login_attempts (username, ip_address, success, failure_reason)
                    VALUES (?, ?, FALSE, ?)
                """,
                    (username, ip_address, reason),
                )

                conn.commit()

        except Exception as e:
            logger.error(f"❌ Error registrando login fallido: {e}")

    def _record_successful_login(self, username: str, ip_address: str):
        """Registrar login exitoso"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()

                cursor.execute(
                    """
                    INSERT INTO login_attempts (username, ip_address, success)
                    VALUES (?, ?, TRUE)
                """,
                    (username, ip_address),
                )

                conn.commit()

        except Exception as e:
            logger.error(f"❌ Error registrando login exitoso: {e}")

    def _generate_recovery_codes(self, user_id: int) -> list:
        """Generar códigos de recuperación"""
        codes = []
        expires_at = datetime.now() + timedelta(days=30)

        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()

                for _ in range(10):
                    code = secrets.token_hex(4).upper()
                    code_hash = hashlib.sha256(code.encode()).hexdigest()

                    cursor.execute(
                        """
                        INSERT INTO recovery_codes (user_id, code_hash, expires_at)
                        VALUES (?, ?, ?)
                    """,
                        (user_id, code_hash, expires_at.isoformat()),
                    )

                    codes.append(code)

                conn.commit()

            return codes

        except Exception as e:
            logger.error(f"❌ Error generando códigos de recuperación: {e}")
            return []


def main():
    """Función principal para testing"""
    auth = MultiFactorAuth()

    # Crear usuario de prueba
    success = auth.create_user("testuser", "test@shaili-ai.com", "SecurePass123!")
    print(f"Usuario creado: {'✅' if success else '❌'}")

    # Autenticar usuario
    success, message, session_token = auth.authenticate_user(
        "testuser", "SecurePass123!"
    )
    print(f"Autenticación: {'✅' if success else '❌'} - {message}")

    if success:
        # Configurar MFA
        success, message, qr_uri = auth.setup_mfa("testuser")
        print(f"MFA configurado: {'✅' if success else '❌'} - {message}")

        if success:
            print(f"QR URI: {qr_uri}")


if __name__ == "__main__":
    main()
