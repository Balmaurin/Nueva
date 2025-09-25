#!/usr/bin/env python3
"""
Módulo Consolidado: Security Systems
==========================================
Consolidado desde: modules/security/authentication.py, modules/security/encryption.py, modules/unified_systems/unified_auth_security_system.py
"""

# === modules/security/authentication.py ===

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
                name=user_data["email"], issuer_name="Sheily AI"
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
    success = auth.create_user("testuser", "test@sheily-ai.com", "SecurePass123!")
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


# === modules/security/encryption.py ===

import os
import base64
import hashlib
import json
import logging
from pathlib import Path
from typing import Dict, Any, Optional, Union, Tuple
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.fernet import Fernet
import secrets
import time

# Configurar logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


class DataEncryption:
    """Sistema de encriptación de datos"""

    def __init__(self, master_key: str = None):
        self.master_key = master_key or self._load_or_generate_master_key()
        self.salt = self._load_or_generate_salt()
        self._derive_key()

        # Crear directorio de seguridad si no existe
        Path("modules/security/encrypted").mkdir(parents=True, exist_ok=True)

    def _load_or_generate_master_key(self) -> str:
        """Cargar o generar clave maestra"""
        key_path = Path("modules/security/master.key")

        if key_path.exists():
            try:
                with open(key_path, "r") as f:
                    return f.read().strip()
            except Exception as e:
                logger.error(f"❌ Error cargando clave maestra: {e}")

        # Generar nueva clave maestra
        master_key = secrets.token_urlsafe(32)
        try:
            with open(key_path, "w") as f:
                f.write(master_key)
            logger.info("✅ Nueva clave maestra generada")
        except Exception as e:
            logger.error(f"❌ Error guardando clave maestra: {e}")

        return master_key

    def _load_or_generate_salt(self) -> bytes:
        """Cargar o generar salt"""
        salt_path = Path("modules/security/encryption.salt")

        if salt_path.exists():
            try:
                with open(salt_path, "rb") as f:
                    return f.read()
            except Exception as e:
                logger.error(f"❌ Error cargando salt: {e}")

        # Generar nuevo salt
        salt = os.urandom(16)
        try:
            with open(salt_path, "wb") as f:
                f.write(salt)
            logger.info("✅ Nuevo salt generado")
        except Exception as e:
            logger.error(f"❌ Error guardando salt: {e}")

        return salt

    def _derive_key(self):
        """Derivar clave de encriptación"""
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=self.salt,
            iterations=100000,
        )
        self.key = base64.urlsafe_b64encode(kdf.derive(self.master_key.encode()))

    def encrypt_data(self, data: Union[str, bytes, Dict[str, Any]]) -> Dict[str, str]:
        """Encriptar datos"""
        try:
            # Convertir datos a bytes
            if isinstance(data, dict):
                data_bytes = json.dumps(data, ensure_ascii=False).encode("utf-8")
            elif isinstance(data, str):
                data_bytes = data.encode("utf-8")
            elif isinstance(data, bytes):
                data_bytes = data
            else:
                raise ValueError("Tipo de datos no soportado")

            # Generar IV
            iv = os.urandom(16)

            # Crear cipher
            cipher = Cipher(algorithms.AES(self.key), modes.CBC(iv))
            encryptor = cipher.encryptor()

            # Padding
            if len(data_bytes) % 16 != 0:
                padding_length = 16 - (len(data_bytes) % 16)
                data_bytes += bytes([padding_length] * padding_length)

            # Encriptar
            encrypted_data = encryptor.update(data_bytes) + encryptor.finalize()

            return {
                "encrypted_data": base64.b64encode(encrypted_data).decode(),
                "iv": base64.b64encode(iv).decode(),
                "salt": base64.b64encode(self.salt).decode(),
                "algorithm": "AES-256-CBC",
                "iterations": 100000,
            }

        except Exception as e:
            logger.error(f"❌ Error encriptando datos: {e}")
            raise

    def decrypt_data(
        self, encrypted_dict: Dict[str, str]
    ) -> Union[str, bytes, Dict[str, Any]]:
        """Desencriptar datos"""
        try:
            # Extraer componentes
            encrypted_data = base64.b64decode(encrypted_dict["encrypted_data"])
            iv = base64.b64decode(encrypted_dict["iv"])

            # Crear cipher
            cipher = Cipher(algorithms.AES(self.key), modes.CBC(iv))
            decryptor = cipher.decryptor()

            # Desencriptar
            decrypted_data = decryptor.update(encrypted_data) + decryptor.finalize()

            # Remover padding
            padding_length = decrypted_data[-1]
            if padding_length < 16:
                decrypted_data = decrypted_data[:-padding_length]

            # Intentar decodificar como JSON primero
            try:
                return json.loads(decrypted_data.decode("utf-8"))
            except json.JSONDecodeError:
                # Si no es JSON, devolver como string
                return decrypted_data.decode("utf-8")

        except Exception as e:
            logger.error(f"❌ Error desencriptando datos: {e}")
            raise

    def encrypt_file(
        self, file_path: Union[str, Path], output_path: Union[str, Path] = None
    ) -> Path:
        """Encriptar archivo"""
        try:
            file_path = Path(file_path)

            if not file_path.exists():
                raise FileNotFoundError(f"Archivo no encontrado: {file_path}")

            if output_path is None:
                output_path = (
                    Path("modules/security/encrypted") / f"{file_path.name}.encrypted"
                )
            else:
                output_path = Path(output_path)

            # Leer archivo
            with open(file_path, "rb") as f:
                file_data = f.read()

            # Encriptar datos
            encrypted_dict = self.encrypt_data(file_data)

            # Guardar archivo encriptado
            with open(output_path, "w") as f:
                json.dump(encrypted_dict, f, indent=2)

            logger.info(f"✅ Archivo encriptado: {file_path} -> {output_path}")
            return output_path

        except Exception as e:
            logger.error(f"❌ Error encriptando archivo: {e}")
            raise

    def decrypt_file(
        self,
        encrypted_file_path: Union[str, Path],
        output_path: Union[str, Path] = None,
    ) -> Path:
        """Desencriptar archivo"""
        try:
            encrypted_file_path = Path(encrypted_file_path)

            if not encrypted_file_path.exists():
                raise FileNotFoundError(
                    f"Archivo encriptado no encontrado: {encrypted_file_path}"
                )

            # Leer archivo encriptado
            with open(encrypted_file_path, "r") as f:
                encrypted_dict = json.load(f)

            # Desencriptar datos
            decrypted_data = self.decrypt_data(encrypted_dict)

            if isinstance(decrypted_data, str):
                decrypted_data = decrypted_data.encode("utf-8")

            # Determinar ruta de salida
            if output_path is None:
                if encrypted_file_path.name.endswith(".encrypted"):
                    output_path = (
                        encrypted_file_path.parent / encrypted_file_path.name[:-10]
                    )
                else:
                    output_path = (
                        encrypted_file_path.parent
                        / f"decrypted_{encrypted_file_path.name}"
                    )
            else:
                output_path = Path(output_path)

            # Guardar archivo desencriptado
            with open(output_path, "wb") as f:
                f.write(decrypted_data)

            logger.info(
                f"✅ Archivo desencriptado: {encrypted_file_path} -> {output_path}"
            )
            return output_path

        except Exception as e:
            logger.error(f"❌ Error desencriptando archivo: {e}")
            raise

    def encrypt_config(self, config_data: Dict[str, Any], config_name: str) -> Path:
        """Encriptar configuración"""
        try:
            # Encriptar datos de configuración
            encrypted_dict = self.encrypt_data(config_data)

            # Guardar configuración encriptada
            output_path = (
                Path("modules/security/encrypted") / f"{config_name}.encrypted"
            )
            with open(output_path, "w") as f:
                json.dump(encrypted_dict, f, indent=2)

            logger.info(f"✅ Configuración encriptada: {config_name}")
            return output_path

        except Exception as e:
            logger.error(f"❌ Error encriptando configuración: {e}")
            raise

    def decrypt_config(self, config_name: str) -> Dict[str, Any]:
        """Desencriptar configuración"""
        try:
            config_path = (
                Path("modules/security/encrypted") / f"{config_name}.encrypted"
            )

            if not config_path.exists():
                raise FileNotFoundError(
                    f"Configuración encriptada no encontrada: {config_name}"
                )

            # Leer configuración encriptada
            with open(config_path, "r") as f:
                encrypted_dict = json.load(f)

            # Desencriptar datos
            decrypted_data = self.decrypt_data(encrypted_dict)

            if not isinstance(decrypted_data, dict):
                raise ValueError("Los datos desencriptados no son un diccionario")

            logger.info(f"✅ Configuración desencriptada: {config_name}")
            return decrypted_data

        except Exception as e:
            logger.error(f"❌ Error desencriptando configuración: {e}")
            raise

    def encrypt_sensitive_string(self, sensitive_data: str) -> str:
        """Encriptar string sensible"""
        try:
            encrypted_dict = self.encrypt_data(sensitive_data)
            return json.dumps(encrypted_dict)

        except Exception as e:
            logger.error(f"❌ Error encriptando string: {e}")
            raise

    def decrypt_sensitive_string(self, encrypted_string: str) -> str:
        """Desencriptar string sensible"""
        try:
            encrypted_dict = json.loads(encrypted_string)
            decrypted_data = self.decrypt_data(encrypted_dict)

            if not isinstance(decrypted_data, str):
                raise ValueError("Los datos desencriptados no son un string")

            return decrypted_data

        except Exception as e:
            logger.error(f"❌ Error desencriptando string: {e}")
            raise

    def create_secure_backup(
        self, source_path: Union[str, Path], backup_name: str = None
    ) -> Path:
        """Crear backup seguro encriptado"""
        try:
            source_path = Path(source_path)

            if not source_path.exists():
                raise FileNotFoundError(f"Ruta de origen no encontrada: {source_path}")

            if backup_name is None:
                backup_name = f"backup_{source_path.name}_{int(time.time())}"

            # Crear backup encriptado
            backup_path = (
                Path("modules/security/encrypted") / f"{backup_name}.encrypted"
            )

            if source_path.is_file():
                self.encrypt_file(source_path, backup_path)
            elif source_path.is_dir():
                # Crear archivo temporal con contenido del directorio
                import tarfile

                temp_archive = Path("modules/security/temp_backup.tar.gz")

                with tarfile.open(temp_archive, "w:gz") as tar:
                    tar.add(source_path, arcname=source_path.name)

                # Encriptar archivo temporal
                self.encrypt_file(temp_archive, backup_path)

                # Limpiar archivo temporal
                temp_archive.unlink()

            logger.info(f"✅ Backup seguro creado: {backup_path}")
            return backup_path

        except Exception as e:
            logger.error(f"❌ Error creando backup seguro: {e}")
            raise

    def verify_encryption_integrity(self, encrypted_dict: Dict[str, str]) -> bool:
        """Verificar integridad de datos encriptados"""
        try:
            # Verificar que todos los campos requeridos estén presentes
            required_fields = ["encrypted_data", "iv", "salt", "algorithm"]
            for field in required_fields:
                if field not in encrypted_dict:
                    logger.error(f"❌ Campo requerido faltante: {field}")
                    return False

            # Verificar que los datos estén en formato base64 válido
            try:
                base64.b64decode(encrypted_dict["encrypted_data"])
                base64.b64decode(encrypted_dict["iv"])
                base64.b64decode(encrypted_dict["salt"])
            except Exception:
                logger.error("❌ Datos en formato base64 inválido")
                return False

            # Intentar desencriptar para verificar integridad
            try:
                self.decrypt_data(encrypted_dict)
                return True
            except Exception:
                logger.error("❌ Error al desencriptar datos")
                return False

        except Exception as e:
            logger.error(f"❌ Error verificando integridad: {e}")
            return False

    def rotate_encryption_key(self, new_master_key: str = None) -> bool:
        """Rotar clave de encriptación"""
        try:
            # Generar nueva clave maestra si no se proporciona
            if new_master_key is None:
                new_master_key = secrets.token_urlsafe(32)

            # Crear nueva instancia con la nueva clave
            new_encryption = DataEncryption(new_master_key)

            # Re-encriptar todos los archivos encriptados
            encrypted_dir = Path("modules/security/encrypted")
            if encrypted_dir.exists():
                for encrypted_file in encrypted_dir.glob("*.encrypted"):
                    try:
                        # Desencriptar con clave antigua
                        decrypted_data = self.decrypt_file(encrypted_file)

                        # Encriptar con nueva clave
                        new_encryption.encrypt_file(decrypted_data, encrypted_file)

                        # Limpiar archivo temporal
                        decrypted_data.unlink()

                    except Exception as e:
                        logger.error(
                            f"❌ Error rotando clave para {encrypted_file}: {e}"
                        )
                        return False

            # Actualizar clave maestra
            key_path = Path("modules/security/master.key")
            with open(key_path, "w") as f:
                f.write(new_master_key)

            # Actualizar salt
            salt_path = Path("modules/security/encryption.salt")
            with open(salt_path, "wb") as f:
                f.write(new_encryption.salt)

            # Actualizar instancia actual
            self.master_key = new_master_key
            self.salt = new_encryption.salt
            self._derive_key()

            logger.info("✅ Clave de encriptación rotada exitosamente")
            return True

        except Exception as e:
            logger.error(f"❌ Error rotando clave de encriptación: {e}")
            return False


class FileEncryption:
    """Encriptación de archivos con metadatos"""

    def __init__(self, encryption: DataEncryption):
        self.encryption = encryption

    def encrypt_file_with_metadata(
        self, file_path: Union[str, Path], metadata: Dict[str, Any] = None
    ) -> Path:
        """Encriptar archivo con metadatos"""
        try:
            file_path = Path(file_path)

            if not file_path.exists():
                raise FileNotFoundError(f"Archivo no encontrado: {file_path}")

            # Preparar metadatos
            if metadata is None:
                metadata = {}

            metadata.update(
                {
                    "original_filename": file_path.name,
                    "original_size": file_path.stat().st_size,
                    "encryption_timestamp": time.time(),
                    "encryption_algorithm": "AES-256-CBC",
                }
            )

            # Leer archivo
            with open(file_path, "rb") as f:
                file_data = f.read()

            # Crear paquete con datos y metadatos
            package = {
                "metadata": metadata,
                "data": base64.b64encode(file_data).decode(),
            }

            # Encriptar paquete
            encrypted_dict = self.encryption.encrypt_data(package)

            # Guardar archivo encriptado
            output_path = (
                Path("modules/security/encrypted") / f"{file_path.name}.encrypted"
            )
            with open(output_path, "w") as f:
                json.dump(encrypted_dict, f, indent=2)

            logger.info(f"✅ Archivo encriptado con metadatos: {file_path}")
            return output_path

        except Exception as e:
            logger.error(f"❌ Error encriptando archivo con metadatos: {e}")
            raise

    def decrypt_file_with_metadata(
        self, encrypted_file_path: Union[str, Path]
    ) -> Tuple[bytes, Dict[str, Any]]:
        """Desencriptar archivo con metadatos"""
        try:
            encrypted_file_path = Path(encrypted_file_path)

            if not encrypted_file_path.exists():
                raise FileNotFoundError(
                    f"Archivo encriptado no encontrado: {encrypted_file_path}"
                )

            # Leer archivo encriptado
            with open(encrypted_file_path, "r") as f:
                encrypted_dict = json.load(f)

            # Desencriptar paquete
            package = self.encryption.decrypt_data(encrypted_dict)

            if (
                not isinstance(package, dict)
                or "metadata" not in package
                or "data" not in package
            ):
                raise ValueError("Formato de archivo encriptado inválido")

            # Extraer datos y metadatos
            metadata = package["metadata"]
            file_data = base64.b64decode(package["data"])

            logger.info(
                f"✅ Archivo desencriptado con metadatos: {encrypted_file_path}"
            )
            return file_data, metadata

        except Exception as e:
            logger.error(f"❌ Error desencriptando archivo con metadatos: {e}")
            raise


def main():
    """Función principal para testing"""
    import time

    # Crear instancia de encriptación
    encryption = DataEncryption()

    # Encriptar datos de prueba
    test_data = {
        "api_key": "sk-1234567890abcdef",
        "database_password": "SecurePass123!",
        "timestamp": time.time(),
    }

    print("🔐 Probando encriptación de datos...")
    encrypted = encryption.encrypt_data(test_data)
    print(f"✅ Datos encriptados: {len(encrypted['encrypted_data'])} caracteres")

    # Desencriptar datos
    decrypted = encryption.decrypt_data(encrypted)
    print(f"✅ Datos desencriptados: {decrypted}")

    # Verificar integridad
    integrity_ok = encryption.verify_encryption_integrity(encrypted)
    print(f"✅ Integridad verificada: {'✅' if integrity_ok else '❌'}")

    # Crear archivo de prueba
    test_file = Path("modules/security/test_config.json")
    test_file.parent.mkdir(parents=True, exist_ok=True)

    with open(test_file, "w") as f:
        json.dump(test_data, f, indent=2)

    # Encriptar archivo
    print("\n📁 Probando encriptación de archivo...")
    encrypted_file = encryption.encrypt_file(test_file)
    print(f"✅ Archivo encriptado: {encrypted_file}")

    # Desencriptar archivo
    decrypted_file = encryption.decrypt_file(encrypted_file)
    print(f"✅ Archivo desencriptado: {decrypted_file}")

    # Limpiar archivos de prueba
    test_file.unlink()
    decrypted_file.unlink()
    encrypted_file.unlink()

    print("\n🎉 Pruebas de encriptación completadas")


if __name__ == "__main__":
    main()


# === modules/unified_systems/unified_auth_security_system.py ===

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


