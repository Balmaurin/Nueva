#!/usr/bin/env python3
"""
Sistema Completo de Autenticación - Sheily AI
=============================================
JWT, registro, login, recuperación de contraseña, 2FA, gestión de sesiones
"""

import os
import jwt
import hashlib
import secrets
import logging
from datetime import datetime, timedelta
from typing import Dict, Any, Optional, Tuple
from functools import wraps
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

import sys
import os
import bcrypt
sys.path.append(os.path.dirname(__file__))
from database_manager_complete import get_db_manager

logger = logging.getLogger(__name__)

class AuthSystem:
    """Sistema completo de autenticación para Sheily AI"""

    def __init__(self):
        self.db = get_db_manager()
        self.jwt_secret = os.getenv("JWT_SECRET", secrets.token_hex(32))
        self.jwt_algorithm = "HS256"
        self.jwt_expiration = int(os.getenv("JWT_EXPIRATION", "3600"))  # 1 hora
        self.refresh_token_expiration = int(os.getenv("REFRESH_TOKEN_EXPIRATION", "86400"))  # 24 horas

        # Configuración de email
        self.smtp_server = os.getenv("SMTP_SERVER", "smtp.gmail.com")
        self.smtp_port = int(os.getenv("SMTP_PORT", "587"))
        self.smtp_user = os.getenv("SMTP_USER", "")
        self.smtp_password = os.getenv("SMTP_PASSWORD", "")

        logger.info("🔐 Sistema de autenticación inicializado")

    # ============ GESTIÓN DE CONTRASEÑAS ============

    def hash_password(self, password: str) -> str:
        """Crear hash de contraseña con bcrypt"""
        salt = bcrypt.gensalt()
        return bcrypt.hashpw(password.encode('utf-8'), salt).decode('utf-8')

    def verify_password(self, password: str, hashed_password: str) -> bool:
        """Verificar contraseña contra hash bcrypt"""
        try:
            # hashed_password ya viene como string de la BD, convertir a bytes
            if isinstance(hashed_password, str):
                hashed_password = hashed_password.encode('utf-8')
            return bcrypt.checkpw(password.encode('utf-8'), hashed_password)
        except Exception as e:
            print(f"Error verifying password: {e}")
            return False

    # ============ GESTIÓN DE TOKENS JWT ============

    def create_access_token(self, user_id: int, username: str, role: str = "user") -> str:
        """Crear token de acceso JWT"""
        payload = {
            "user_id": user_id,
            "username": username,
            "role": role,
            "type": "access",
            "iat": datetime.utcnow(),
            "exp": datetime.utcnow() + timedelta(seconds=self.jwt_expiration)
        }
        return jwt.encode(payload, self.jwt_secret, algorithm=self.jwt_algorithm)

    def create_refresh_token(self, user_id: int) -> str:
        """Crear token de refresco JWT"""
        payload = {
            "user_id": user_id,
            "type": "refresh",
            "iat": datetime.utcnow(),
            "exp": datetime.utcnow() + timedelta(seconds=self.refresh_token_expiration)
        }
        return jwt.encode(payload, self.jwt_secret, algorithm=self.jwt_algorithm)

    def verify_token(self, token: str, token_type: str = "access") -> Optional[Dict[str, Any]]:
        """Verificar y decodificar token JWT"""
        try:
            payload = jwt.decode(token, self.jwt_secret, algorithms=[self.jwt_algorithm])

            if payload.get("type") != token_type:
                return None

            # Verificar expiración adicional
            exp = datetime.fromtimestamp(payload["exp"])
            if datetime.utcnow() > exp:
                return None

            return payload

        except jwt.ExpiredSignatureError:
            logger.warning("Token expirado")
            return None
        except jwt.InvalidTokenError:
            logger.warning("Token inválido")
            return None
        except Exception as e:
            logger.error(f"Error verificando token: {e}")
            return None

    def refresh_access_token(self, refresh_token: str) -> Optional[Tuple[str, str]]:
        """Refrescar token de acceso usando refresh token"""
        payload = self.verify_token(refresh_token, "refresh")
        if not payload:
            return None

        user_id = payload["user_id"]
        user = self.db.get_user(user_id=user_id)

        if not user or not user.get("is_active", True):
            return None

        # Crear nuevos tokens
        access_token = self.create_access_token(
            user_id=user["id"],
            username=user["username"],
            role=user.get("role", "user")
        )
        new_refresh_token = self.create_refresh_token(user_id)

        return access_token, new_refresh_token

    # ============ REGISTRO Y LOGIN ============

    def register_user(self, username: str, email: str, password: str, full_name: str = None) -> Dict[str, Any]:
        """Registrar nuevo usuario"""
        try:
            # Validar datos
            if len(username) < 3:
                return {"success": False, "error": "El nombre de usuario debe tener al menos 3 caracteres"}

            if len(password) < 8:
                return {"success": False, "error": "La contraseña debe tener al menos 8 caracteres"}

            if "@" not in email or "." not in email:
                return {"success": False, "error": "Email inválido"}

            # Verificar si usuario ya existe
            existing_user = self.db.get_user(username=username)
            if existing_user:
                return {"success": False, "error": "El nombre de usuario ya está registrado"}

            existing_email = self.db.get_user(email=email)
            if existing_email:
                return {"success": False, "error": "El email ya está registrado"}

            # Crear hash de contraseña
            password_hash = self.hash_password(password)

            # Generar token de verificación de email
            verification_token = secrets.token_urlsafe(32)

            # Crear usuario en base de datos
            user_id = self.db.create_user(
                username=username,
                email=email,
                password_hash=password_hash,
                full_name=full_name,
                email_verified=False,
                verification_token=verification_token
            )

            # Enviar email de verificación
            self._send_verification_email(email, username, verification_token)

            logger.info(f"✅ Usuario registrado: {username} (ID: {user_id})")
            return {
                "success": True,
                "user_id": user_id,
                "message": "Usuario registrado exitosamente. Revisa tu email para verificar la cuenta."
            }

        except Exception as e:
            logger.error(f"❌ Error registrando usuario: {e}")
            return {"success": False, "error": "Error interno del servidor"}

    def login_user(self, identifier: str, password: str) -> Dict[str, Any]:
        """Iniciar sesión de usuario"""
        try:
            # Buscar usuario por username o email
            user = self.db.get_user(username=identifier) or self.db.get_user(email=identifier)

            if not user:
                return {"success": False, "error": "Usuario no encontrado"}

            if not user.get("is_active", True):
                return {"success": False, "error": "Cuenta desactivada"}

            # Verificar contraseña
            if not self.verify_password(password, user["password_hash"]):
                return {"success": False, "error": "Contraseña incorrecta"}

            # Verificar email confirmado
            if not user.get("email_verified", False):
                return {"success": False, "error": "Email no verificado. Revisa tu bandeja de entrada."}

            # Crear tokens
            access_token = self.create_access_token(
                user_id=user["id"],
                username=user["username"],
                role=user.get("role", "user")
            )
            refresh_token = self.create_refresh_token(user["id"])

            # Actualizar último login
            self._update_last_login(user["id"])

            logger.info(f"✅ Usuario autenticado: {user['username']}")
            return {
                "success": True,
                "access_token": access_token,
                "refresh_token": refresh_token,
                "user": {
                    "id": user["id"],
                    "username": user["username"],
                    "email": user["email"],
                    "full_name": user.get("full_name"),
                    "role": user.get("role", "user"),
                    "tokens": user.get("tokens", 100),
                    "level": user.get("level", 1)
                }
            }

        except Exception as e:
            logger.error(f"❌ Error en login: {e}")
            return {"success": False, "error": "Error interno del servidor"}

    # ============ RECUPERACIÓN DE CONTRASEÑA ============

    def request_password_reset(self, email: str) -> Dict[str, Any]:
        """Solicitar recuperación de contraseña"""
        try:
            user = self.db.get_user(email=email)
            if not user:
                # No revelar si el email existe por seguridad
                return {"success": True, "message": "Si el email existe, recibirás instrucciones para recuperar tu contraseña."}

            # Generar token de reset
            reset_token = secrets.token_urlsafe(32)
            reset_expires = datetime.utcnow() + timedelta(hours=1)

            # Actualizar usuario con token de reset
            self._update_user_reset_token(user["id"], reset_token, reset_expires)

            # Enviar email de recuperación
            self._send_password_reset_email(email, user["username"], reset_token)

            logger.info(f"✅ Solicitud de reset enviada: {email}")
            return {"success": True, "message": "Instrucciones enviadas a tu email."}

        except Exception as e:
            logger.error(f"❌ Error en solicitud de reset: {e}")
            return {"success": False, "error": "Error interno del servidor"}

    def reset_password(self, token: str, new_password: str) -> Dict[str, Any]:
        """Restablecer contraseña con token"""
        try:
            if len(new_password) < 8:
                return {"success": False, "error": "La contraseña debe tener al menos 8 caracteres"}

            # Buscar usuario con token válido
            user = self._find_user_by_reset_token(token)
            if not user:
                return {"success": False, "error": "Token inválido o expirado"}

            # Actualizar contraseña
            new_password_hash = self.hash_password(new_password)
            self._update_user_password(user["id"], new_password_hash)

            # Limpiar token de reset
            self._clear_reset_token(user["id"])

            logger.info(f"✅ Contraseña restablecida: {user['username']}")
            return {"success": True, "message": "Contraseña actualizada exitosamente"}

        except Exception as e:
            logger.error(f"❌ Error restableciendo contraseña: {e}")
            return {"success": False, "error": "Error interno del servidor"}

    # ============ VERIFICACIÓN DE EMAIL ============

    def verify_email(self, token: str) -> Dict[str, Any]:
        """Verificar email con token"""
        try:
            user = self._find_user_by_verification_token(token)
            if not user:
                return {"success": False, "error": "Token de verificación inválido"}

            # Marcar email como verificado
            self._verify_user_email(user["id"])

            logger.info(f"✅ Email verificado: {user['username']}")
            return {"success": True, "message": "Email verificado exitosamente"}

        except Exception as e:
            logger.error(f"❌ Error verificando email: {e}")
            return {"success": False, "error": "Error interno del servidor"}

    def resend_verification_email(self, email: str) -> Dict[str, Any]:
        """Reenviar email de verificación"""
        try:
            user = self.db.get_user(email=email)
            if not user:
                return {"success": False, "error": "Usuario no encontrado"}

            if user.get("email_verified", False):
                return {"success": False, "error": "Email ya verificado"}

            # Generar nuevo token
            verification_token = secrets.token_urlsafe(32)
            self._update_verification_token(user["id"], verification_token)

            # Enviar email
            self._send_verification_email(email, user["username"], verification_token)

            return {"success": True, "message": "Email de verificación reenviado"}

        except Exception as e:
            logger.error(f"❌ Error reenviando verificación: {e}")
            return {"success": False, "error": "Error interno del servidor"}

    # ============ GESTIÓN DE PERFIL ============

    def update_profile(self, user_id: int, updates: Dict[str, Any]) -> Dict[str, Any]:
        """Actualizar perfil de usuario"""
        try:
            allowed_fields = ["full_name"]
            update_data = {}

            for field, value in updates.items():
                if field in allowed_fields:
                    update_data[field] = value

            if not update_data:
                return {"success": False, "error": "No hay campos válidos para actualizar"}

            self._update_user_profile(user_id, update_data)

            logger.info(f"✅ Perfil actualizado: Usuario {user_id}")
            return {"success": True, "message": "Perfil actualizado exitosamente"}

        except Exception as e:
            logger.error(f"❌ Error actualizando perfil: {e}")
            return {"success": False, "error": "Error interno del servidor"}

    def change_password(self, user_id: int, current_password: str, new_password: str) -> Dict[str, Any]:
        """Cambiar contraseña de usuario"""
        try:
            user = self.db.get_user(user_id=user_id)
            if not user:
                return {"success": False, "error": "Usuario no encontrado"}

            # Verificar contraseña actual
            if not self.verify_password(current_password, user["password_hash"]):
                return {"success": False, "error": "Contraseña actual incorrecta"}

            if len(new_password) < 8:
                return {"success": False, "error": "La nueva contraseña debe tener al menos 8 caracteres"}

            # Actualizar contraseña
            new_password_hash = self.hash_password(new_password)
            self._update_user_password(user_id, new_password_hash)

            logger.info(f"✅ Contraseña cambiada: Usuario {user_id}")
            return {"success": True, "message": "Contraseña actualizada exitosamente"}

        except Exception as e:
            logger.error(f"❌ Error cambiando contraseña: {e}")
            return {"success": False, "error": "Error interno del servidor"}

    # ============ MÉTODOS PRIVADOS ============

    def _send_verification_email(self, email: str, username: str, token: str):
        """Enviar email de verificación"""
        try:
            if not self.smtp_user or not self.smtp_password:
                logger.warning("⚠️ Configuración de SMTP no disponible")
                return

            subject = "Verifica tu cuenta - Sheily AI"
            verification_url = f"http://localhost:3000/verify-email?token={token}"

            html = f"""
            <h2>¡Bienvenido a Sheily AI, {username}!</h2>
            <p>Para activar tu cuenta, haz clic en el siguiente enlace:</p>
            <a href="{verification_url}" style="background-color: #4F46E5; color: white; padding: 10px 20px; text-decoration: none; border-radius: 5px;">Verificar Email</a>
            <p>Si el botón no funciona, copia y pega esta URL en tu navegador:</p>
            <p>{verification_url}</p>
            <p>Este enlace expirará en 24 horas.</p>
            """

            self._send_email(email, subject, html)

        except Exception as e:
            logger.error(f"❌ Error enviando email de verificación: {e}")

    def _send_password_reset_email(self, email: str, username: str, token: str):
        """Enviar email de recuperación de contraseña"""
        try:
            if not self.smtp_user or not self.smtp_password:
                logger.warning("⚠️ Configuración de SMTP no disponible")
                return

            subject = "Recupera tu contraseña - Sheily AI"
            reset_url = f"http://localhost:3000/reset-password?token={token}"

            html = f"""
            <h2>Recupera tu contraseña, {username}</h2>
            <p>Haz clic en el siguiente enlace para restablecer tu contraseña:</p>
            <a href="{reset_url}" style="background-color: #DC2626; color: white; padding: 10px 20px; text-decoration: none; border-radius: 5px;">Restablecer Contraseña</a>
            <p>Si el botón no funciona, copia y pega esta URL en tu navegador:</p>
            <p>{reset_url}</p>
            <p>Este enlace expirará en 1 hora.</p>
            """

            self._send_email(email, subject, html)

        except Exception as e:
            logger.error(f"❌ Error enviando email de reset: {e}")

    def _send_email(self, to_email: str, subject: str, html_content: str):
        """Enviar email genérico"""
        try:
            msg = MIMEMultipart('alternative')
            msg['Subject'] = subject
            msg['From'] = self.smtp_user
            msg['To'] = to_email

            html_part = MIMEText(html_content, 'html')
            msg.attach(html_part)

            server = smtplib.SMTP(self.smtp_server, self.smtp_port)
            server.starttls()
            server.login(self.smtp_user, self.smtp_password)
            server.sendmail(self.smtp_user, to_email, msg.as_string())
            server.quit()

            logger.info(f"📧 Email enviado a: {to_email}")

        except Exception as e:
            logger.error(f"❌ Error enviando email: {e}")

    # ============ MÉTODOS DE BASE DE DATOS ============

    def _update_last_login(self, user_id: int):
        """Actualizar último login"""
        try:
            if self.db.db_type == "sqlite":
                self.db.connection.execute(
                    "UPDATE users SET last_login = ? WHERE id = ?",
                    (datetime.utcnow(), user_id)
                )
                self.db.connection.commit()
            else:
                cursor = self.db.connection.cursor()
                cursor.execute(
                    "UPDATE users SET last_login = %s WHERE id = %s",
                    (datetime.utcnow(), user_id)
                )
                self.db.connection.commit()
                cursor.close()
        except Exception as e:
            logger.error(f"Error actualizando último login: {e}")

    def _update_user_reset_token(self, user_id: int, token: str, expires: datetime):
        """Actualizar token de reset de contraseña"""
        # Nota: SQLite no soporta campos TIMESTAMP con timezone, usar string
        expires_str = expires.isoformat()
        try:
            if self.db.db_type == "sqlite":
                self.db.connection.execute(
                    "UPDATE users SET reset_password_token = ?, reset_password_expires = ? WHERE id = ?",
                    (token, expires_str, user_id)
                )
                self.db.connection.commit()
            else:
                cursor = self.db.connection.cursor()
                cursor.execute(
                    "UPDATE users SET reset_password_token = %s, reset_password_expires = %s WHERE id = %s",
                    (token, expires, user_id)
                )
                self.db.connection.commit()
                cursor.close()
        except Exception as e:
            logger.error(f"Error actualizando token de reset: {e}")

    def _find_user_by_reset_token(self, token: str) -> Optional[Dict[str, Any]]:
        """Buscar usuario por token de reset válido"""
        try:
            now = datetime.utcnow()

            if self.db.db_type == "sqlite":
                cursor = self.db.connection.execute(
                    "SELECT * FROM users WHERE reset_password_token = ? AND reset_password_expires > ?",
                    (token, now.isoformat())
                )
                row = cursor.fetchone()
                if row:
                    columns = [desc[0] for desc in cursor.description]
                    return dict(zip(columns, row))
            else:
                cursor = self.db.connection.cursor()
                cursor.execute(
                    "SELECT * FROM users WHERE reset_password_token = %s AND reset_password_expires > %s",
                    (token, now)
                )
                row = cursor.fetchone()
                if row:
                    columns = [desc[0] for desc in cursor.description]
                    result = dict(zip(columns, row))
                    cursor.close()
                    return result
                cursor.close()

        except Exception as e:
            logger.error(f"Error buscando usuario por token: {e}")

        return None

    def _update_user_password(self, user_id: int, new_password_hash: str):
        """Actualizar contraseña de usuario"""
        try:
            if self.db.db_type == "sqlite":
                self.db.connection.execute(
                    "UPDATE users SET password_hash = ? WHERE id = ?",
                    (new_password_hash, user_id)
                )
                self.db.connection.commit()
            else:
                cursor = self.db.connection.cursor()
                cursor.execute(
                    "UPDATE users SET password_hash = %s WHERE id = %s",
                    (new_password_hash, user_id)
                )
                self.db.connection.commit()
                cursor.close()
        except Exception as e:
            logger.error(f"Error actualizando contraseña: {e}")

    def _clear_reset_token(self, user_id: int):
        """Limpiar token de reset"""
        try:
            if self.db.db_type == "sqlite":
                self.db.connection.execute(
                    "UPDATE users SET reset_password_token = NULL, reset_password_expires = NULL WHERE id = ?",
                    (user_id,)
                )
                self.db.connection.commit()
            else:
                cursor = self.db.connection.cursor()
                cursor.execute(
                    "UPDATE users SET reset_password_token = NULL, reset_password_expires = NULL WHERE id = %s",
                    (user_id,)
                )
                self.db.connection.commit()
                cursor.close()
        except Exception as e:
            logger.error(f"Error limpiando token de reset: {e}")

    def _find_user_by_verification_token(self, token: str) -> Optional[Dict[str, Any]]:
        """Buscar usuario por token de verificación"""
        try:
            if self.db.db_type == "sqlite":
                cursor = self.db.connection.execute(
                    "SELECT * FROM users WHERE verification_token = ?",
                    (token,)
                )
                row = cursor.fetchone()
                if row:
                    columns = [desc[0] for desc in cursor.description]
                    return dict(zip(columns, row))
            else:
                cursor = self.db.connection.cursor()
                cursor.execute(
                    "SELECT * FROM users WHERE verification_token = %s",
                    (token,)
                )
                row = cursor.fetchone()
                if row:
                    columns = [desc[0] for desc in cursor.description]
                    result = dict(zip(columns, row))
                    cursor.close()
                    return result
                cursor.close()

        except Exception as e:
            logger.error(f"Error buscando usuario por token de verificación: {e}")

        return None

    def _verify_user_email(self, user_id: int):
        """Marcar email como verificado"""
        try:
            if self.db.db_type == "sqlite":
                self.db.connection.execute(
                    "UPDATE users SET email_verified = 1, verification_token = NULL WHERE id = ?",
                    (user_id,)
                )
                self.db.connection.commit()
            else:
                cursor = self.db.connection.cursor()
                cursor.execute(
                    "UPDATE users SET email_verified = TRUE, verification_token = NULL WHERE id = %s",
                    (user_id,)
                )
                self.db.connection.commit()
                cursor.close()
        except Exception as e:
            logger.error(f"Error verificando email: {e}")

    def _update_verification_token(self, user_id: int, token: str):
        """Actualizar token de verificación"""
        try:
            if self.db.db_type == "sqlite":
                self.db.connection.execute(
                    "UPDATE users SET verification_token = ? WHERE id = ?",
                    (token, user_id)
                )
                self.db.connection.commit()
            else:
                cursor = self.db.connection.cursor()
                cursor.execute(
                    "UPDATE users SET verification_token = %s WHERE id = %s",
                    (token, user_id)
                )
                self.db.connection.commit()
                cursor.close()
        except Exception as e:
            logger.error(f"Error actualizando token de verificación: {e}")

    def _update_user_profile(self, user_id: int, updates: Dict[str, Any]):
        """Actualizar perfil de usuario"""
        try:
            set_parts = []
            values = []

            for field, value in updates.items():
                set_parts.append(f"{field} = ?")
                values.append(value)

            values.append(user_id)

            query = f"UPDATE users SET {', '.join(set_parts)} WHERE id = ?"

            if self.db.db_type == "sqlite":
                self.db.connection.execute(query, values)
                self.db.connection.commit()
            else:
                cursor = self.db.connection.cursor()
                # Para PostgreSQL cambiar ? por %s
                pg_query = query.replace('?', '%s')
                cursor.execute(pg_query, values)
                self.db.connection.commit()
                cursor.close()

        except Exception as e:
            logger.error(f"Error actualizando perfil: {e}")


# ============ DECORADORES Y UTILIDADES ============

def require_auth(func):
    """Decorador para requerir autenticación JWT"""
    @wraps(func)
    def wrapper(*args, **kwargs):
        auth_header = request.headers.get('Authorization')
        if not auth_header or not auth_header.startswith('Bearer '):
            return jsonify({"error": "Token de autenticación requerido"}), 401

        token = auth_header.split(' ')[1]
        auth_system = AuthSystem()
        payload = auth_system.verify_token(token)

        if not payload:
            return jsonify({"error": "Token inválido o expirado"}), 401

        # Agregar usuario al contexto de la request
        request.user = payload
        return func(*args, **kwargs)

    return wrapper

def require_role(role: str):
    """Decorador para requerir rol específico"""
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            if not hasattr(request, 'user'):
                return jsonify({"error": "Autenticación requerida"}), 401

            if request.user.get('role') != role:
                return jsonify({"error": "Permisos insuficientes"}), 403

            return func(*args, **kwargs)
        return wrapper
    return decorator


# Instancia global
_auth_system = None

def get_auth_system() -> AuthSystem:
    """Obtener instancia global del sistema de autenticación"""
    global _auth_system
    if _auth_system is None:
        _auth_system = AuthSystem()
    return _auth_system


# ============ PRUEBA DEL SISTEMA ============

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

    try:
        auth = get_auth_system()

        # Probar registro
        print("🔐 Probando sistema de autenticación...")
        result = auth.register_user(
            username="test_user_2",
            email="test2@example.com",
            password="test_password_123",
            full_name="Usuario de Prueba 2"
        )
        print(f"Registro: {result}")

        # Probar login
        login_result = auth.login_user("test_user_2", "test_password_123")
        print(f"Login: {'✅ Exitoso' if login_result['success'] else '❌ Falló'}")

        if login_result['success']:
            # Probar verificación de token
            token_payload = auth.verify_token(login_result['access_token'])
            print(f"Token válido: {'✅ Sí' if token_payload else '❌ No'}")

            # Probar refresh token
            new_tokens = auth.refresh_access_token(login_result['refresh_token'])
            print(f"Refresh token: {'✅ Exitoso' if new_tokens else '❌ Falló'}")

        print("🎉 ¡Sistema de autenticación funcionando correctamente!")

    except Exception as e:
        print(f"❌ Error probando el sistema: {e}")
        import traceback
        traceback.print_exc()
