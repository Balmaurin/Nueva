#!/usr/bin/env python3
"""
Sistema de Gestión Segura de Claves de Usuario
=============================================
Gestión segura de claves privadas y wallets de usuarios
"""

import json
import base58
import hashlib
import secrets
import logging
from pathlib import Path
from typing import Dict, Optional, Any, List
from dataclasses import dataclass
from datetime import datetime, timedelta
import threading
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
import base64

# Solana imports
try:
    from solana.keypair import Keypair
    from solana.publickey import PublicKey

    SOLANA_AVAILABLE = True
except ImportError:
    try:
        from solanasdk.keypair import Keypair
        from solanasdk.publickey import PublicKey

        SOLANA_AVAILABLE = True
    except ImportError:
        logging.warning("Solana SDK no disponible")
        SOLANA_AVAILABLE = False

logger = logging.getLogger(__name__)


@dataclass
class UserWallet:
    """Wallet de usuario"""

    user_id: str
    public_key: str
    encrypted_private_key: str
    salt: str
    created_at: datetime
    last_used: datetime
    is_active: bool = True
    metadata: Optional[Dict[str, Any]] = None


@dataclass
class KeyDerivationParams:
    """Parámetros de derivación de claves"""

    salt: str
    iterations: int = 100000
    key_length: int = 32


class SecureKeyManagement:
    """Sistema de gestión segura de claves"""

    def __init__(self, master_key_path: str = "shaili_ai/security/master.key"):
        self.master_key_path = Path(master_key_path)
        self.master_key_path.parent.mkdir(parents=True, exist_ok=True)
        self.lock = threading.Lock()

        # Inicializar o cargar clave maestra
        self.master_key = self._load_or_create_master_key()
        self.cipher_suite = Fernet(self.master_key)

        # Almacenamiento de wallets en memoria (en producción usar base de datos)
        self.user_wallets: Dict[str, UserWallet] = {}

        logger.info("🔐 Sistema de gestión segura de claves inicializado")

    def _load_or_create_master_key(self) -> bytes:
        """Cargar o crear clave maestra"""
        if self.master_key_path.exists():
            # Cargar clave existente
            with open(self.master_key_path, "rb") as f:
                master_key = f.read()
            logger.info("✅ Clave maestra cargada")
        else:
            # Crear nueva clave maestra
            master_key = Fernet.generate_key()
            with open(self.master_key_path, "wb") as f:
                f.write(master_key)
            logger.info("✅ Nueva clave maestra creada")

        return master_key

    def _derive_key_from_password(
        self, password: str, salt: str, iterations: int = 100000
    ) -> bytes:
        """Derivar clave desde contraseña"""
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=salt.encode(),
            iterations=iterations,
        )
        return base64.urlsafe_b64encode(kdf.derive(password.encode()))

    def _encrypt_private_key(self, private_key: bytes, password: str, salt: str) -> str:
        """Encriptar clave privada"""
        derived_key = self._derive_key_from_password(password, salt)
        cipher = Fernet(derived_key)
        encrypted_data = cipher.encrypt(private_key)
        return base64.urlsafe_b64encode(encrypted_data).decode()

    def _decrypt_private_key(
        self, encrypted_key: str, password: str, salt: str
    ) -> bytes:
        """Desencriptar clave privada"""
        derived_key = self._derive_key_from_password(password, salt)
        cipher = Fernet(derived_key)
        encrypted_data = base64.urlsafe_b64decode(encrypted_key.encode())
        return cipher.decrypt(encrypted_data)

    def create_user_wallet(self, user_id: str, password: str) -> Optional[UserWallet]:
        """Crear wallet para usuario"""
        try:
            with self.lock:
                if user_id in self.user_wallets:
                    logger.warning(f"Wallet ya existe para usuario: {user_id}")
                    return self.user_wallets[user_id]

                if not SOLANA_AVAILABLE:
                    logger.error("Solana SDK no disponible")
                    return None

                # Generar nueva keypair
                keypair = Keypair()
                private_key_bytes = bytes(keypair.secret_key)
                public_key_str = str(keypair.public_key)

                # Generar salt único
                salt = base64.urlsafe_b64encode(secrets.token_bytes(16)).decode()

                # Encriptar clave privada
                encrypted_private_key = self._encrypt_private_key(
                    private_key_bytes, password, salt
                )

                # Crear wallet
                wallet = UserWallet(
                    user_id=user_id,
                    public_key=public_key_str,
                    encrypted_private_key=encrypted_private_key,
                    salt=salt,
                    created_at=datetime.now(),
                    last_used=datetime.now(),
                    is_active=True,
                    metadata={"created_by": "secure_key_management", "version": "1.0"},
                )

                # Guardar en memoria
                self.user_wallets[user_id] = wallet

                logger.info(f"✅ Wallet creado para usuario: {user_id}")
                return wallet

        except Exception as e:
            logger.error(f"❌ Error creando wallet: {e}")
            return None

    def get_user_wallet(self, user_id: str) -> Optional[UserWallet]:
        """Obtener wallet de usuario"""
        return self.user_wallets.get(user_id)

    def get_user_public_key(self, user_id: str) -> Optional[str]:
        """Obtener clave pública de usuario"""
        wallet = self.get_user_wallet(user_id)
        return wallet.public_key if wallet else None

    def get_user_keypair(self, user_id: str, password: str) -> Optional["Keypair"]:
        """Obtener keypair de usuario"""
        try:
            wallet = self.get_user_wallet(user_id)
            if not wallet:
                logger.error(f"Wallet no encontrado para usuario: {user_id}")
                return None

            # Desencriptar clave privada
            private_key_bytes = self._decrypt_private_key(
                wallet.encrypted_private_key, password, wallet.salt
            )

            # Crear keypair
            keypair = Keypair.from_secret_key(private_key_bytes)

            # Actualizar último uso
            wallet.last_used = datetime.now()

            logger.info(f"✅ Keypair obtenido para usuario: {user_id}")
            return keypair

        except Exception as e:
            logger.error(f"❌ Error obteniendo keypair: {e}")
            return None

    def change_user_password(
        self, user_id: str, old_password: str, new_password: str
    ) -> bool:
        """Cambiar contraseña de usuario"""
        try:
            with self.lock:
                wallet = self.get_user_wallet(user_id)
                if not wallet:
                    logger.error(f"Wallet no encontrado para usuario: {user_id}")
                    return False

                # Obtener clave privada con contraseña antigua
                private_key_bytes = self._decrypt_private_key(
                    wallet.encrypted_private_key, old_password, wallet.salt
                )

                # Generar nuevo salt
                new_salt = base64.urlsafe_b64encode(secrets.token_bytes(16)).decode()

                # Encriptar con nueva contraseña
                new_encrypted_private_key = self._encrypt_private_key(
                    private_key_bytes, new_password, new_salt
                )

                # Actualizar wallet
                wallet.encrypted_private_key = new_encrypted_private_key
                wallet.salt = new_salt
                wallet.last_used = datetime.now()

                logger.info(f"✅ Contraseña cambiada para usuario: {user_id}")
                return True

        except Exception as e:
            logger.error(f"❌ Error cambiando contraseña: {e}")
            return False

    def backup_user_wallet(self, user_id: str, password: str, backup_path: str) -> bool:
        """Crear backup del wallet de usuario"""
        try:
            wallet = self.get_user_wallet(user_id)
            if not wallet:
                logger.error(f"Wallet no encontrado para usuario: {user_id}")
                return False

            # Obtener clave privada
            private_key_bytes = self._decrypt_private_key(
                wallet.encrypted_private_key, password, wallet.salt
            )

            # Crear backup
            backup_data = {
                "user_id": wallet.user_id,
                "public_key": wallet.public_key,
                "private_key": base58.b58encode(private_key_bytes).decode(),
                "created_at": wallet.created_at.isoformat(),
                "backup_created_at": datetime.now().isoformat(),
                "metadata": wallet.metadata,
            }

            # Guardar backup
            backup_file = Path(backup_path)
            backup_file.parent.mkdir(parents=True, exist_ok=True)

            with open(backup_file, "w") as f:
                json.dump(backup_data, f, indent=2)

            logger.info(f"✅ Backup creado para usuario: {user_id}")
            return True

        except Exception as e:
            logger.error(f"❌ Error creando backup: {e}")
            return False

    def restore_user_wallet(
        self, backup_path: str, password: str
    ) -> Optional[UserWallet]:
        """Restaurar wallet desde backup"""
        try:
            with open(backup_path, "r") as f:
                backup_data = json.load(f)

            user_id = backup_data["user_id"]
            private_key_str = backup_data["private_key"]

            # Decodificar clave privada
            private_key_bytes = base58.b58decode(private_key_str)

            # Generar nuevo salt
            salt = base64.urlsafe_b64encode(secrets.token_bytes(16)).decode()

            # Encriptar con nueva contraseña
            encrypted_private_key = self._encrypt_private_key(
                private_key_bytes, password, salt
            )

            # Crear wallet
            wallet = UserWallet(
                user_id=user_id,
                public_key=backup_data["public_key"],
                encrypted_private_key=encrypted_private_key,
                salt=salt,
                created_at=datetime.fromisoformat(backup_data["created_at"]),
                last_used=datetime.now(),
                is_active=True,
                metadata=backup_data.get("metadata", {}),
            )

            # Guardar en memoria
            self.user_wallets[user_id] = wallet

            logger.info(f"✅ Wallet restaurado para usuario: {user_id}")
            return wallet

        except Exception as e:
            logger.error(f"❌ Error restaurando wallet: {e}")
            return None

    def deactivate_user_wallet(self, user_id: str) -> bool:
        """Desactivar wallet de usuario"""
        try:
            with self.lock:
                wallet = self.get_user_wallet(user_id)
                if not wallet:
                    logger.error(f"Wallet no encontrado para usuario: {user_id}")
                    return False

                wallet.is_active = False
                wallet.last_used = datetime.now()

                logger.info(f"✅ Wallet desactivado para usuario: {user_id}")
                return True

        except Exception as e:
            logger.error(f"❌ Error desactivando wallet: {e}")
            return False

    def get_wallet_info(self, user_id: str) -> Optional[Dict[str, Any]]:
        """Obtener información del wallet"""
        wallet = self.get_user_wallet(user_id)
        if not wallet:
            return None

        return {
            "user_id": wallet.user_id,
            "public_key": wallet.public_key,
            "created_at": wallet.created_at.isoformat(),
            "last_used": wallet.last_used.isoformat(),
            "is_active": wallet.is_active,
            "metadata": wallet.metadata,
        }

    def list_user_wallets(self) -> List[Dict[str, Any]]:
        """Listar todos los wallets"""
        wallets = []
        for user_id, wallet in self.user_wallets.items():
            wallets.append(
                {
                    "user_id": user_id,
                    "public_key": wallet.public_key,
                    "created_at": wallet.created_at.isoformat(),
                    "last_used": wallet.last_used.isoformat(),
                    "is_active": wallet.is_active,
                }
            )
        return wallets

    def validate_password(self, user_id: str, password: str) -> bool:
        """Validar contraseña de usuario"""
        try:
            wallet = self.get_user_wallet(user_id)
            if not wallet:
                return False

            # Intentar desencriptar clave privada
            self._decrypt_private_key(
                wallet.encrypted_private_key, password, wallet.salt
            )

            return True

        except Exception:
            return False

    def get_wallet_statistics(self) -> Dict[str, Any]:
        """Obtener estadísticas de wallets"""
        total_wallets = len(self.user_wallets)
        active_wallets = sum(1 for w in self.user_wallets.values() if w.is_active)
        inactive_wallets = total_wallets - active_wallets

        # Wallets creados en los últimos 30 días
        thirty_days_ago = datetime.now() - timedelta(days=30)
        recent_wallets = sum(
            1 for w in self.user_wallets.values() if w.created_at >= thirty_days_ago
        )

        return {
            "total_wallets": total_wallets,
            "active_wallets": active_wallets,
            "inactive_wallets": inactive_wallets,
            "recent_wallets_30d": recent_wallets,
            "last_updated": datetime.now().isoformat(),
        }


# Instancia global
_secure_key_management: Optional[SecureKeyManagement] = None


def get_secure_key_management() -> SecureKeyManagement:
    """Obtener instancia global del sistema de gestión de claves"""
    global _secure_key_management

    if _secure_key_management is None:
        _secure_key_management = SecureKeyManagement()

    return _secure_key_management
