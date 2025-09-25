#!/usr/bin/env python3
"""
Servidor Principal de API - Sheily AI
===================================
Servidor FastAPI completo que integra todos los sistemas
"""

import os
import logging
from datetime import datetime
from typing import Dict, Any, Optional
from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException, Depends, status, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel, EmailStr, Field
import uvicorn

from database_manager_complete import get_db_manager
from auth_system import get_auth_system, AuthSystem

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/api_server.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Instancias globales
db_manager = get_db_manager()
auth_system = get_auth_system()

# Modelos Pydantic para requests/responses
class UserRegister(BaseModel):
    username: str = Field(..., min_length=3, max_length=50)
    email: EmailStr
    password: str = Field(..., min_length=8)
    full_name: Optional[str] = None

class UserLogin(BaseModel):
    identifier: str  # username or email
    password: str

class TokenRefresh(BaseModel):
    refresh_token: str

class PasswordResetRequest(BaseModel):
    email: EmailStr

class PasswordReset(BaseModel):
    token: str
    new_password: str = Field(..., min_length=8)

class EmailVerification(BaseModel):
    token: str

class ProfileUpdate(BaseModel):
    full_name: Optional[str] = None

class PasswordChange(BaseModel):
    current_password: str
    new_password: str = Field(..., min_length=8)

class ChatMessage(BaseModel):
    message: str
    branch: Optional[str] = "general"

class SystemStatus(BaseModel):
    status: str
    timestamp: datetime
    version: str = "3.1.0"

# Dependencias de seguridad
security = HTTPBearer()

async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)) -> Dict[str, Any]:
    """Obtener usuario actual desde token JWT"""
    token = credentials.credentials
    payload = auth_system.verify_token(token)

    if not payload:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token inválido o expirado",
            headers={"WWW-Authenticate": "Bearer"},
        )

    user = db_manager.get_user(user_id=payload["user_id"])
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Usuario no encontrado"
        )

    return user

def require_role(required_role: str):
    """Dependencia para requerir rol específico"""
    async def role_checker(user: Dict[str, Any] = Depends(get_current_user)):
        if user.get("role") != required_role:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Permisos insuficientes"
            )
        return user
    return role_checker

# Crear aplicación FastAPI
@asynccontextmanager
async def lifespan(app: FastAPI):
    """Manejador de ciclo de vida de la aplicación"""
    logger.info("🚀 Iniciando servidor de API Sheily AI...")
    yield
    logger.info("🛑 Servidor de API detenido")

app = FastAPI(
    title="Sheily AI API",
    description="API completa para el sistema de inteligencia artificial especializada Sheily AI",
    version="3.1.0",
    lifespan=lifespan
)

# Configurar CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:3001", "https://sheily-ai.com"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ============ ENDPOINTS DE AUTENTICACIÓN ============

@app.post("/api/auth/register", response_model=Dict[str, Any])
async def register_user(user_data: UserRegister):
    """Registrar nuevo usuario"""
    result = auth_system.register_user(
        username=user_data.username,
        email=user_data.email,
        password=user_data.password,
        full_name=user_data.full_name
    )

    if not result["success"]:
        raise HTTPException(status_code=400, detail=result["error"])

    return result

@app.post("/api/auth/login", response_model=Dict[str, Any])
async def login_user(login_data: UserLogin):
    """Iniciar sesión"""
    result = auth_system.login_user(login_data.identifier, login_data.password)

    if not result["success"]:
        raise HTTPException(status_code=401, detail=result["error"])

    return result

@app.post("/api/auth/refresh", response_model=Dict[str, Any])
async def refresh_token(token_data: TokenRefresh):
    """Refrescar token de acceso"""
    new_tokens = auth_system.refresh_access_token(token_data.refresh_token)

    if not new_tokens:
        raise HTTPException(status_code=401, detail="Token de refresco inválido")

    return {
        "success": True,
        "access_token": new_tokens[0],
        "refresh_token": new_tokens[1]
    }

@app.post("/api/auth/forgot-password", response_model=Dict[str, Any])
async def forgot_password(data: PasswordResetRequest):
    """Solicitar recuperación de contraseña"""
    result = auth_system.request_password_reset(data.email)

    if not result["success"]:
        raise HTTPException(status_code=400, detail=result["error"])

    return result

@app.post("/api/auth/reset-password", response_model=Dict[str, Any])
async def reset_password(data: PasswordReset):
    """Restablecer contraseña"""
    result = auth_system.reset_password(data.token, data.new_password)

    if not result["success"]:
        raise HTTPException(status_code=400, detail=result["error"])

    return result

@app.post("/api/auth/verify-email", response_model=Dict[str, Any])
async def verify_email(data: EmailVerification):
    """Verificar email"""
    result = auth_system.verify_email(data.token)

    if not result["success"]:
        raise HTTPException(status_code=400, detail=result["error"])

    return result

@app.post("/api/auth/resend-verification", response_model=Dict[str, Any])
async def resend_verification(email: EmailStr):
    """Reenviar verificación de email"""
    result = auth_system.resend_verification_email(email)

    if not result["success"]:
        raise HTTPException(status_code=400, detail=result["error"])

    return result

@app.get("/api/auth/me", response_model=Dict[str, Any])
async def get_current_user_info(current_user: Dict[str, Any] = Depends(get_current_user)):
    """Obtener información del usuario actual"""
    return {
        "success": True,
        "user": {
            "id": current_user["id"],
            "username": current_user["username"],
            "email": current_user["email"],
            "full_name": current_user.get("full_name"),
            "role": current_user.get("role", "user"),
            "tokens": current_user.get("tokens", 100),
            "level": current_user.get("level", 1),
            "is_active": current_user.get("is_active", True),
            "email_verified": current_user.get("email_verified", False),
            "created_at": current_user.get("created_at"),
            "last_login": current_user.get("last_login")
        }
    }

@app.put("/api/auth/profile", response_model=Dict[str, Any])
async def update_profile(updates: ProfileUpdate, current_user: Dict[str, Any] = Depends(get_current_user)):
    """Actualizar perfil de usuario"""
    result = auth_system.update_profile(current_user["id"], updates.dict(exclude_unset=True))

    if not result["success"]:
        raise HTTPException(status_code=400, detail=result["error"])

    return result

@app.post("/api/auth/change-password", response_model=Dict[str, Any])
async def change_password(data: PasswordChange, current_user: Dict[str, Any] = Depends(get_current_user)):
    """Cambiar contraseña"""
    result = auth_system.change_password(current_user["id"], data.current_password, data.new_password)

    if not result["success"]:
        raise HTTPException(status_code=400, detail=result["error"])

    return result

# ============ ENDPOINTS DE CHAT ============

@app.post("/api/chat/send", response_model=Dict[str, Any])
async def send_chat_message(message_data: ChatMessage, current_user: Dict[str, Any] = Depends(get_current_user)):
    """Enviar mensaje de chat (placeholder - se integrará con Sheily)"""
    try:
        # Crear sesión de chat si no existe
        session_id = f"chat_{current_user['id']}_{int(datetime.now().timestamp())}"

        # Guardar mensaje del usuario
        db_manager.save_chat_message(session_id, current_user["id"], message_data.message, False)

        # Respuesta simulada (aquí se integraría con el LLM)
        ai_response = f"¡Hola! Soy Sheily AI. He recibido tu mensaje sobre '{message_data.branch}': '{message_data.message[:50]}...'. Esta funcionalidad se integrará completamente con el sistema de IA avanzado."

        # Guardar respuesta de IA
        db_manager.save_chat_message(session_id, current_user["id"], ai_response, True, 50)

        return {
            "success": True,
            "response": ai_response,
            "session_id": session_id,
            "model": "sheily-chat-preview",
            "tokens_used": 50
        }

    except Exception as e:
        logger.error(f"Error en chat: {e}")
        raise HTTPException(status_code=500, detail="Error interno del servidor")

@app.get("/api/chat/history", response_model=Dict[str, Any])
async def get_chat_history(session_id: Optional[str] = None, limit: int = 50, current_user: Dict[str, Any] = Depends(get_current_user)):
    """Obtener historial de chat"""
    try:
        if session_id:
            history = db_manager.get_chat_history(session_id, limit)
        else:
            # Obtener la última sesión activa del usuario
            # Por simplicidad, devolver historial vacío por ahora
            history = []

        return {
            "success": True,
            "session_id": session_id,
            "messages": history,
            "total_messages": len(history)
        }

    except Exception as e:
        logger.error(f"Error obteniendo historial: {e}")
        raise HTTPException(status_code=500, detail="Error interno del servidor")

@app.post("/api/chat/session", response_model=Dict[str, Any])
async def create_chat_session(branch: str = "general", current_user: Dict[str, Any] = Depends(get_current_user)):
    """Crear nueva sesión de chat"""
    try:
        session_id = db_manager.create_chat_session(current_user["id"], branch)

        return {
            "success": True,
            "session_id": session_id,
            "branch": branch,
            "created_at": datetime.now().isoformat()
        }

    except Exception as e:
        logger.error(f"Error creando sesión: {e}")
        raise HTTPException(status_code=500, detail="Error interno del servidor")

# ============ ENDPOINTS DE RAMAS ============

@app.get("/api/branches", response_model=Dict[str, Any])
async def get_branches():
    """Obtener todas las ramas disponibles"""
    try:
        # Obtener ramas de la base de datos
        branches = []
        if db_manager.db_type == "sqlite":
            cursor = db_manager.connection.execute("SELECT * FROM branches WHERE enabled = 1")
            rows = cursor.fetchall()
            columns = [desc[0] for desc in cursor.description]
            for row in rows:
                branch_data = dict(zip(columns, row))
                # Parsear keywords desde JSON string
                keywords = []
                if branch_data.get("keywords"):
                    try:
                        import json
                        keywords = json.loads(branch_data["keywords"])
                    except:
                        keywords = []

                branches.append({
                    "id": branch_data["id"],
                    "name": branch_data["name"],
                    "description": branch_data["description"] or f"Rama especializada en {branch_data['name']}",
                    "keywords": keywords,
                    "enabled": bool(branch_data["enabled"])
                })
        else:
            # PostgreSQL
            cursor = db_manager.connection.cursor()
            cursor.execute("SELECT * FROM branches WHERE enabled = true")
            rows = cursor.fetchall()
            columns = [desc[0] for desc in cursor.description]
            for row in rows:
                branch_data = dict(zip(columns, row))
                # Parsear keywords desde JSON string
                keywords = []
                if branch_data.get("keywords"):
                    try:
                        import json
                        keywords = json.loads(branch_data["keywords"])
                    except:
                        keywords = []

                branches.append({
                    "id": branch_data["id"],
                    "name": branch_data["name"],
                    "description": branch_data["description"] or f"Rama especializada en {branch_data['name']}",
                    "keywords": keywords,
                    "enabled": branch_data["enabled"]
                })
            cursor.close()

        return {
            "success": True,
            "branches": branches,
            "total": len(branches)
        }

    except Exception as e:
        logger.error(f"Error obteniendo ramas: {e}")
        raise HTTPException(status_code=500, detail="Error interno del servidor")

@app.get("/api/branches/{branch_name}", response_model=Dict[str, Any])
async def get_branch_info(branch_name: str):
    """Obtener información detallada de una rama"""
    try:
        # Buscar rama en la base de datos
        branch_info = None

        if db_manager.db_type == "sqlite":
            cursor = db_manager.connection.execute("SELECT * FROM branches WHERE name = ?", (branch_name,))
            row = cursor.fetchone()
            if row:
                columns = [desc[0] for desc in cursor.description]
                branch_data = dict(zip(columns, row))
                # Parsear keywords desde JSON string
                keywords = []
                if branch_data.get("keywords"):
                    try:
                        import json
                        keywords = json.loads(branch_data["keywords"])
                    except:
                        keywords = []

                branch_info = {
                    "id": branch_data["id"],
                    "name": branch_data["name"],
                    "description": branch_data["description"],
                    "keywords": keywords,
                    "enabled": bool(branch_data["enabled"])
                }
        else:
            cursor = db_manager.connection.cursor()
            cursor.execute("SELECT * FROM branches WHERE name = %s", (branch_name,))
            row = cursor.fetchone()
            if row:
                columns = [desc[0] for desc in cursor.description]
                branch_data = dict(zip(columns, row))
                # Parsear keywords desde JSON string
                keywords = []
                if branch_data.get("keywords"):
                    try:
                        import json
                        keywords = json.loads(branch_data["keywords"])
                    except:
                        keywords = []

                branch_info = {
                    "id": branch_data["id"],
                    "name": branch_data["name"],
                    "description": branch_data["description"],
                    "keywords": keywords,
                    "enabled": branch_data["enabled"]
                }
            cursor.close()

        if not branch_info:
            raise HTTPException(status_code=404, detail="Rama no encontrada")

        return {
            "success": True,
            "branch": branch_info
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error obteniendo rama {branch_name}: {e}")
        raise HTTPException(status_code=500, detail="Error interno del servidor")

# ============ ENDPOINTS DE SISTEMA ============

@app.get("/health", response_model=SystemStatus)
async def health_check():
    """Health check del sistema"""
    return SystemStatus(
        status="healthy",
        timestamp=datetime.now(),
        version="3.1.0"
    )

@app.get("/api/system/metrics", response_model=Dict[str, Any])
async def get_system_metrics():
    """Obtener métricas del sistema"""
    try:
        # Métricas básicas del sistema
        import psutil

        cpu_percent = psutil.cpu_percent(interval=1)
        memory = psutil.virtual_memory()
        disk = psutil.disk_usage('/')

        metrics = {
            "cpu_usage": cpu_percent,
            "memory_usage": memory.percent,
            "disk_usage": disk.percent,
            "uptime": "N/A",  # Se calcularía desde el inicio del proceso
            "active_connections": 0,  # Placeholder
            "total_requests": 0,  # Placeholder
            "error_rate": 0.0,  # Placeholder
            "timestamp": datetime.now().isoformat()
        }

        return {
            "success": True,
            "metrics": metrics
        }

    except Exception as e:
        logger.error(f"Error obteniendo métricas: {e}")
        raise HTTPException(status_code=500, detail="Error interno del servidor")

@app.get("/api/system/info", response_model=Dict[str, Any])
async def get_system_info():
    """Obtener información completa del sistema"""
    try:
        db_info = db_manager.get_database_info()

        system_info = {
            "version": "3.1.0",
            "environment": os.getenv("NODE_ENV", "development"),
            "database": db_info,
            "branches_count": db_info.get("branches_count", 0),
            "users_count": db_info.get("users_count", 0),
            "timestamp": datetime.now().isoformat()
        }

        return {
            "success": True,
            "system": system_info
        }

    except Exception as e:
        logger.error(f"Error obteniendo info del sistema: {e}")
        raise HTTPException(status_code=500, detail="Error interno del servidor")

# ============ ENDPOINTS DE ADMINISTRACIÓN (REQUIEREN ROL ADMIN) ============

@app.get("/api/admin/users", response_model=Dict[str, Any])
async def get_all_users(admin_user: Dict[str, Any] = Depends(require_role("admin"))):
    """Obtener todos los usuarios (solo admin)"""
    try:
        # Obtener todos los usuarios
        users = []
        if db_manager.db_type == "sqlite":
            cursor = db_manager.connection.execute("SELECT id, username, email, full_name, role, tokens, level, is_active, email_verified, created_at, last_login FROM users")
            rows = cursor.fetchall()
            columns = [desc[0] for desc in cursor.description]
            users = [dict(zip(columns, row)) for row in rows]
        else:
            cursor = db_manager.connection.cursor()
            cursor.execute("SELECT id, username, email, full_name, role, tokens, level, is_active, email_verified, created_at, last_login FROM users")
            rows = cursor.fetchall()
            columns = [desc[0] for desc in cursor.description]
            users = [dict(zip(columns, row)) for row in rows]
            cursor.close()

        return {
            "success": True,
            "users": users,
            "total": len(users)
        }

    except Exception as e:
        logger.error(f"Error obteniendo usuarios: {e}")
        raise HTTPException(status_code=500, detail="Error interno del servidor")

@app.post("/api/admin/branch", response_model=Dict[str, Any])
async def create_branch(branch_data: Dict[str, Any], admin_user: Dict[str, Any] = Depends(require_role("admin"))):
    """Crear nueva rama (solo admin)"""
    try:
        name = branch_data.get("name")
        description = branch_data.get("description", "")
        keywords = branch_data.get("keywords", [])

        if not name:
            raise HTTPException(status_code=400, detail="Nombre de rama requerido")

        # Verificar que no exista
        if db_manager.db_type == "sqlite":
            cursor = db_manager.connection.execute("SELECT id FROM branches WHERE name = ?", (name,))
            if cursor.fetchone():
                raise HTTPException(status_code=400, detail="La rama ya existe")
        else:
            cursor = db_manager.connection.cursor()
            cursor.execute("SELECT id FROM branches WHERE name = %s", (name,))
            if cursor.fetchone():
                cursor.close()
                raise HTTPException(status_code=400, detail="La rama ya existe")
            cursor.close()

        # Crear rama
        keywords_json = str(keywords) if db_manager.db_type == "sqlite" else keywords

        if db_manager.db_type == "sqlite":
            db_manager.connection.execute(
                "INSERT INTO branches (name, description, keywords, enabled) VALUES (?, ?, ?, 1)",
                (name, description, keywords_json)
            )
            db_manager.connection.commit()
        else:
            cursor = db_manager.connection.cursor()
            cursor.execute(
                "INSERT INTO branches (name, description, keywords, enabled) VALUES (%s, %s, %s, %s)",
                (name, description, keywords, True)
            )
            db_manager.connection.commit()
            cursor.close()

        logger.info(f"✅ Rama creada: {name}")
        return {
            "success": True,
            "message": f"Rama '{name}' creada exitosamente"
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error creando rama: {e}")
        raise HTTPException(status_code=500, detail="Error interno del servidor")

# ============ MANEJADORES DE ERRORES ============

@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    """Manejador de excepciones HTTP"""
    return {
        "success": False,
        "error": exc.detail,
        "status_code": exc.status_code
    }

@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception):
    """Manejador de excepciones generales"""
    logger.error(f"Error no manejado: {exc}")
    return {
        "success": False,
        "error": "Error interno del servidor",
        "status_code": 500
    }

# ============ INICIO DEL SERVIDOR ============

if __name__ == "__main__":
    port = int(os.getenv("API_PORT", "8000"))
    host = os.getenv("API_HOST", "0.0.0.0")

    logger.info(f"🚀 Iniciando servidor API Sheily AI en {host}:{port}")

    uvicorn.run(
        "main_server:app",
        host=host,
        port=port,
        reload=True,
        log_level="info"
    )
