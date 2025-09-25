#!/usr/bin/env python3
"""
Sistema de Encriptación Real para Shaili AI
===========================================
Implementación completa de encriptación de datos y archivos
"""

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
