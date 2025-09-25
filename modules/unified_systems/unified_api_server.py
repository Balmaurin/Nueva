"""
Servidor API REST Unificado de NeuroFusion
==========================================

Este módulo proporciona una API REST completa que expone todas las
funcionalidades del sistema NeuroFusion unificado.
"""

import asyncio
import json
import logging
from typing import Dict, Any, Optional, List
from datetime import datetime
import uvicorn
from fastapi import FastAPI, HTTPException, Depends, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel, Field
import httpx

# Importaciones simplificadas (sin dependencias problemáticas)
# from sqlalchemy.orm import Session  # Comentado temporalmente
# from models import User  # Comentado temporalmente
# from config.database import SessionLocal  # Comentado temporalmente

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Importar sistema unificado
try:
    from ai.unified_system_core import get_unified_system, SystemConfig, QueryResult
    from ai.jwt_auth import JWTAuthenticator
    from ai.unified_config import get_unified_config
except ImportError as e:
    logger.error(f"Error importando módulos: {e}")
    raise


# Modelos Pydantic para la API
class QueryRequest(BaseModel):
    query: str = Field(..., description="Consulta del usuario")
    context: Optional[Dict[str, Any]] = Field(None, description="Contexto adicional")
    user_id: Optional[str] = Field(None, description="ID del usuario")


class QueryResponse(BaseModel):
    query: str
    response: str
    confidence: float
    processing_time: float
    domain: str
    quality_score: float
    issues: List[str] = []
    timestamp: datetime


class SystemStatusResponse(BaseModel):
    system_name: str
    version: str
    initialized: bool
    components: Dict[str, Any]
    conversation_history_length: int
    timestamp: float


class TrainingRequest(BaseModel):
    data: str = Field(..., description="Datos de entrenamiento")
    domain: str = Field("general", description="Dominio de los datos")
    learning_rate: float = Field(0.001, description="Tasa de aprendizaje")


class MemoryRequest(BaseModel):
    content: str = Field(..., description="Contenido a memorizar")
    memory_type: str = Field("custom", description="Tipo de memoria")
    tags: Optional[List[str]] = Field(None, description="Etiquetas")


class TokenGenerationRequest(BaseModel):
    user_id: str = Field(..., description="ID del usuario")
    response_quality: float = Field(..., description="Calidad de la respuesta")
    response_length: int = Field(..., description="Longitud de la respuesta")


# Configurar FastAPI
app = FastAPI(
    title="NeuroFusion Unified API",
    description="API REST unificada para el sistema NeuroFusion",
    version="2.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
)

# Configurar CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Configurar autenticación
security = HTTPBearer(auto_error=False)

# Variables globales
unified_system = None
jwt_auth = None
config = None


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
) -> Optional[str]:
    """Obtener usuario actual desde token JWT"""
    if not credentials:
        return None

    try:
        if jwt_auth:
            payload = jwt_auth.validate_token(credentials.credentials)
            return payload.get("user_id")
    except Exception as e:
        logger.warning(f"Error validando token: {e}")

    return None


async def startup_event():
    """Evento de inicio del servidor"""
    global unified_system, jwt_auth, config

    logger.info("🚀 Iniciando servidor API unificado...")

    try:
        # Obtener configuración
        config = get_unified_config()

        # Inicializar sistema unificado
        system_config = SystemConfig(
            system_name=config.system_name,
            version=config.version,
            debug_mode=config.debug_mode,
            base_path=config.base_path,
            data_path=config.data_path,
            models_path=config.models_path,
            cache_path=config.cache_path,
            logs_path=config.logs_path,
            default_embedding_model=config.default_embedding_model,
            default_llm_model=config.default_llm_model,
            max_concurrent_operations=config.max_concurrent_operations,
            cache_enabled=config.cache_enabled,
            cache_size=config.cache_size,
            enable_encryption=config.enable_encryption,
            encryption_key=config.encryption_key,
            blockchain_enabled=config.blockchain_enabled,
            solana_network=config.solana_network,
            log_level=config.log_level,
            log_file=config.log_file,
            frontend_port=config.frontend_port,
            backend_port=config.backend_port,
        )

        unified_system = await get_unified_system(system_config)

        # Inicializar autenticación JWT
        jwt_auth = JWTAuthenticator()

        logger.info("✅ Servidor API unificado iniciado correctamente")

    except Exception as e:
        logger.error(f"❌ Error iniciando servidor: {e}")
        raise


async def shutdown_event():
    """Evento de apagado del servidor"""
    global unified_system

    logger.info("🔄 Apagando servidor API unificado...")

    if unified_system:
        await unified_system.shutdown()

    logger.info("✅ Servidor API unificado apagado correctamente")


# Configurar eventos
app.add_event_handler("startup", startup_event)
app.add_event_handler("shutdown", shutdown_event)

# Endpoints de la API


@app.get("/", response_model=Dict[str, str])
async def root():
    """Endpoint raíz"""
    return {
        "message": "NeuroFusion Unified API",
        "version": "2.0.0",
        "status": "active",
    }


@app.get("/health", response_model=Dict[str, Any])
async def health_check():
    """Verificar salud del sistema"""
    if not unified_system:
        raise HTTPException(status_code=503, detail="Sistema no inicializado")

    try:
        status = await unified_system.get_system_status()
        return {
            "status": "healthy",
            "system": status,
            "timestamp": datetime.now().isoformat(),
        }
    except Exception as e:
        raise HTTPException(status_code=503, detail=f"Error de salud: {str(e)}")


@app.post("/query", response_model=QueryResponse)
async def process_query(
    request: QueryRequest,
    background_tasks: BackgroundTasks,
    current_user: Optional[str] = Depends(get_current_user),
):
    """Procesar consulta del usuario"""
    if not unified_system:
        raise HTTPException(status_code=503, detail="Sistema no inicializado")

    try:
        # Procesar consulta
        result = await unified_system.process_query(request.query, request.context)

        # Tareas en segundo plano
        background_tasks.add_task(log_interaction, request.query, result, current_user)

        return QueryResponse(
            query=result.query,
            response=result.response,
            confidence=result.confidence,
            processing_time=result.processing_time,
            domain=result.domain,
            quality_score=result.quality_score,
            issues=result.issues,
            timestamp=datetime.now(),
        )

    except Exception as e:
        logger.error(f"Error procesando consulta: {e}")
        raise HTTPException(
            status_code=500, detail=f"Error procesando consulta: {str(e)}"
        )


@app.get("/status", response_model=SystemStatusResponse)
async def get_system_status():
    """Obtener estado del sistema"""
    if not unified_system:
        raise HTTPException(status_code=503, detail="Sistema no inicializado")

    try:
        status = await unified_system.get_system_status()
        return SystemStatusResponse(**status)
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Error obteniendo estado: {str(e)}"
        )


@app.post("/train")
async def train_system(request: TrainingRequest):
    """Entrenar el sistema con nuevos datos"""
    if not unified_system:
        raise HTTPException(status_code=503, detail="Sistema no inicializado")

    try:
        if "learning" in unified_system.components:
            result = await unified_system.components["learning"].train_with_data(
                data=request.data,
                domain=request.domain,
                learning_rate=request.learning_rate,
            )
            return {
                "status": "success",
                "training_result": result,
                "timestamp": datetime.now().isoformat(),
            }
        else:
            raise HTTPException(
                status_code=503, detail="Sistema de aprendizaje no disponible"
            )

    except Exception as e:
        logger.error(f"Error en entrenamiento: {e}")
        raise HTTPException(status_code=500, detail=f"Error en entrenamiento: {str(e)}")


@app.post("/memory")
async def add_memory(request: MemoryRequest):
    """Añadir memoria al sistema"""
    if not unified_system:
        raise HTTPException(status_code=503, detail="Sistema no inicializado")

    try:
        if "memory" in unified_system.components:
            memory_id = await unified_system.components["memory"].add_memory(
                content=request.content,
                memory_type=request.memory_type,
                tags=request.tags,
            )
            return {
                "status": "success",
                "memory_id": memory_id,
                "timestamp": datetime.now().isoformat(),
            }
        else:
            raise HTTPException(
                status_code=503, detail="Sistema de memoria no disponible"
            )

    except Exception as e:
        logger.error(f"Error añadiendo memoria: {e}")
        raise HTTPException(
            status_code=500, detail=f"Error añadiendo memoria: {str(e)}"
        )


@app.get("/memory/search")
async def search_memories(query: str, limit: int = 10):
    """Buscar en memorias"""
    if not unified_system:
        raise HTTPException(status_code=503, detail="Sistema no inicializado")

    try:
        if "memory" in unified_system.components:
            memories = await unified_system.components["memory"].search_memories(
                query, limit
            )
            return {
                "status": "success",
                "memories": memories,
                "count": len(memories),
                "timestamp": datetime.now().isoformat(),
            }
        else:
            raise HTTPException(
                status_code=503, detail="Sistema de memoria no disponible"
            )

    except Exception as e:
        logger.error(f"Error buscando memorias: {e}")
        raise HTTPException(
            status_code=500, detail=f"Error buscando memorias: {str(e)}"
        )


@app.post("/tokens/generate")
async def generate_tokens(request: TokenGenerationRequest):
    """Generar tokens Sheily"""
    if not unified_system:
        raise HTTPException(status_code=503, detail="Sistema no inicializado")

    try:
        if "tokens" in unified_system.components:
            tokens = await unified_system.components[
                "tokens"
            ].generate_tokens_for_response(
                user_id=request.user_id,
                response_quality=request.response_quality,
                response_length=request.response_length,
            )
            return {
                "status": "success",
                "tokens": [token.__dict__ for token in tokens],
                "count": len(tokens),
                "timestamp": datetime.now().isoformat(),
            }
        else:
            raise HTTPException(
                status_code=503, detail="Sistema de tokens no disponible"
            )

    except Exception as e:
        logger.error(f"Error generando tokens: {e}")
        raise HTTPException(status_code=500, detail=f"Error generando tokens: {str(e)}")


@app.get("/embeddings/generate")
async def generate_embedding(text: str, domain: str = "general"):
    """Generar embedding para texto"""
    if not unified_system:
        raise HTTPException(status_code=503, detail="Sistema no inicializado")

    try:
        if "embeddings" in unified_system.components:
            embedding = unified_system.components["embeddings"].generate_embedding(
                text, domain
            )
            return {
                "status": "success",
                "embedding": embedding.tolist(),
                "dimension": len(embedding),
                "timestamp": datetime.now().isoformat(),
            }
        else:
            raise HTTPException(
                status_code=503, detail="Sistema de embeddings no disponible"
            )

    except Exception as e:
        logger.error(f"Error generando embedding: {e}")
        raise HTTPException(
            status_code=500, detail=f"Error generando embedding: {str(e)}"
        )


@app.post("/auth/login")
async def login(username: str, password: str):
    """Iniciar sesión y obtener token JWT"""
    if not jwt_auth:
        raise HTTPException(
            status_code=503, detail="Sistema de autenticación no disponible"
        )

    try:
        # Aquí se implementaría la validación real de credenciales
        # Por ahora, simulamos una validación exitosa
        if username and password:
            token = jwt_auth.generate_token(username)
            return {
                "status": "success",
                "token": token,
                "user_id": username,
                "timestamp": datetime.now().isoformat(),
            }
        else:
            raise HTTPException(status_code=401, detail="Credenciales inválidas")

    except Exception as e:
        logger.error(f"Error en login: {e}")
        raise HTTPException(status_code=500, detail=f"Error en login: {str(e)}")


@app.post("/api/auth/oauth-login")
async def oauth_login(request: Dict[str, str]):
    """Manejar inicio de sesión con proveedores OAuth"""
    try:
        email = request.get("email")
        name = request.get("name")
        provider = request.get("provider")

        if not email or not name or not provider:
            raise HTTPException(status_code=400, detail="Datos de OAuth incompletos")

        # Buscar usuario por email
        db = SessionLocal()
        try:
            user = db.query(User).filter(User.email == email).first()

            if not user:
                # Crear nuevo usuario si no existe
                user = User(
                    username=email.split("@")[0],
                    email=email,
                    full_name=name,
                    is_active=True,
                    created_at=datetime.utcnow(),
                    last_login=datetime.utcnow(),
                )
                db.add(user)
                db.commit()
                db.refresh(user)

            # Generar token
            token = jwt_auth.generate_token(str(user.id))

            return {
                "success": True,
                "message": "Inicio de sesión exitoso",
                "data": {
                    "user_id": user.id,
                    "username": user.username,
                    "email": user.email,
                    "full_name": user.full_name,
                    "provider": provider,
                    "token": token,
                },
            }
        finally:
            db.close()

    except Exception as e:
        logger.error(f"Error en OAuth login: {e}")
        raise HTTPException(
            status_code=500, detail=f"Error en autenticación OAuth: {str(e)}"
        )


@app.get("/config")
async def get_configuration():
    """Obtener configuración del sistema"""
    if not config:
        raise HTTPException(status_code=503, detail="Configuración no disponible")

    try:
        return {
            "status": "success",
            "config": config.to_dict(),
            "timestamp": datetime.now().isoformat(),
        }
    except Exception as e:
        logger.error(f"Error obteniendo configuración: {e}")
        raise HTTPException(
            status_code=500, detail=f"Error obteniendo configuración: {str(e)}"
        )


@app.post("/config/update")
async def update_configuration(new_config: Dict[str, Any]):
    """Actualizar configuración del sistema"""
    if not config:
        raise HTTPException(status_code=503, detail="Configuración no disponible")

    try:
        # Actualizar configuración
        for key, value in new_config.items():
            if hasattr(config, key):
                setattr(config, key, value)

        # Guardar configuración
        config.save("config/config/neurofusion_config.json")

        return {
            "status": "success",
            "message": "Configuración actualizada",
            "timestamp": datetime.now().isoformat(),
        }
    except Exception as e:
        logger.error(f"Error actualizando configuración: {e}")
        raise HTTPException(
            status_code=500, detail=f"Error actualizando configuración: {str(e)}"
        )


@app.get("/training/models")
async def get_training_models():
    """Obtener lista de modelos de entrenamiento disponibles"""
    try:
        # Verificar si el sistema unificado está inicializado
        if not unified_system:
            return {
                "status": "error",
                "message": "Sistema de entrenamiento no inicializado",
                "models": [],
            }
        # Aquí iría la lógica para obtener los modelos disponibles
        return {
            "status": "success",
            "message": "Modelos obtenidos correctamente",
            "models": [],
        }
    except Exception as e:
        logger.error(f"Error obteniendo modelos de entrenamiento: {e}")
        raise HTTPException(
            status_code=500, detail=f"Error obteniendo modelos: {str(e)}"
        )


if __name__ == "__main__":
    run_server()
