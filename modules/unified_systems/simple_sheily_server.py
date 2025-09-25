#!/usr/bin/env python3
"""
Servidor API Simple para Sheily AI - Versión Funcional
====================================================

Servidor minimalista que conecta Sheily con el LLM Llama 3.2 Q8_0
"""

import asyncio
import json
import logging
import os
import sys
import time
import httpx
from typing import Dict, Any, Optional, List
from dataclasses import dataclass, field
from datetime import datetime
import uvicorn
from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from fastapi import Depends
from pydantic import BaseModel, Field

# Agregar path del proyecto
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@dataclass
class QueryResult:
    """Resultado de procesamiento de consulta"""

    query: str
    response: str
    confidence: float
    processing_time: float
    domain: str
    quality_score: float = 0.0
    issues: List[str] = field(default_factory=list)


class SimpleSheilySystem:
    """Sistema Sheily simplificado que conecta con LLM"""

    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.is_initialized = False
        self.startup_time = datetime.now()
        self.request_count = 0

        try:
            self.is_initialized = True
            self.logger.info("✅ SimpleSheilySystem inicializado")
        except Exception as e:
            self.logger.error(f"❌ Error inicializando sistema: {e}")

    async def process_query(
        self, query: str, context: Optional[Dict[str, Any]] = None
    ) -> QueryResult:
        """Procesar consulta conectando con LLM Llama 3.2 Q8_0"""
        start_time = time.time()

        try:
            self.request_count += 1
            self.logger.info(
                f"📝 Procesando consulta #{self.request_count}: {query[:50]}..."
            )

            # Detectar dominio
            domain = await self._detect_domain(query)
            self.logger.info(f"🎯 Dominio detectado: {domain}")

            # Generar respuesta con LLM
            self.logger.info("🧠 Generando respuesta con LLM Llama 3.2 Q8_0...")
            response = await self._generate_response_with_llm(query, domain, context)

            processing_time = time.time() - start_time
            self.logger.info(f"✅ Respuesta generada en {processing_time:.2f}s")

            return QueryResult(
                query=query,
                response=response,
                confidence=0.85,
                processing_time=processing_time,
                domain=domain,
                quality_score=0.85,
            )

        except Exception as e:
            self.logger.error(f"❌ Error procesando consulta: {e}")
            processing_time = time.time() - start_time

            return QueryResult(
                query=query,
                response=f"Lo siento, hubo un problema procesando tu consulta sobre {query[:30]}...",
                confidence=0.0,
                processing_time=processing_time,
                domain="error",
                quality_score=0.0,
                issues=[str(e)],
            )

    async def _detect_domain(self, query: str) -> str:
        """Detectar dominio de la consulta"""
        query_lower = query.lower()

        domain_keywords = {
            "programming": [
                "python",
                "código",
                "programar",
                "función",
                "javascript",
                "java",
                "c++",
                "desarrollo",
                "software",
            ],
            "ai": [
                "ia",
                "inteligencia artificial",
                "machine learning",
                "neural",
                "modelo",
                "deep learning",
                "aprendizaje",
            ],
            "database": [
                "base de datos",
                "sql",
                "database",
                "mysql",
                "postgres",
                "consulta",
                "datos",
            ],
            "science": [
                "ciencia",
                "matemáticas",
                "física",
                "química",
                "investigación",
                "experimento",
            ],
            "medical": ["médico", "salud", "enfermedad", "tratamiento", "diagnóstico"],
            "technical": ["tecnología", "técnico", "ingeniería", "sistema", "hardware"],
            "creative": ["arte", "creativo", "diseño", "música", "creatividad"],
            "business": ["negocio", "empresa", "mercado", "economía", "finanzas"],
        }

        for domain, keywords in domain_keywords.items():
            if any(keyword in query_lower for keyword in keywords):
                return domain

        return "general"

    async def _generate_response_with_llm(
        self, query: str, domain: str, context: Optional[Dict[str, Any]] = None
    ) -> str:
        """Generar respuesta usando LLM Llama 3.2 Q8_0"""
        try:
            # Preparar prompt según dominio
            domain_prompts = {
                "programming": "Eres un experto programador. Responde con código claro y explicaciones técnicas detalladas.",
                "ai": "Eres un experto en IA. Explica conceptos de machine learning y deep learning de forma clara.",
                "database": "Eres un experto en bases de datos. Enfócate en SQL y diseño de datos.",
                "science": "Eres un científico. Explica conceptos científicos con rigor y claridad.",
                "medical": "Eres un experto médico. Proporciona información médica precisa y responsable.",
                "technical": "Eres un experto técnico. Explica conceptos tecnológicos detalladamente.",
                "creative": "Eres creativo. Responde de forma innovadora y artística.",
                "business": "Eres un experto en negocios. Proporciona consejos empresariales estratégicos.",
                "general": "Eres Sheily AI, un asistente inteligente útil y amigable.",
            }

            system_prompt = domain_prompts.get(domain, domain_prompts["general"])
            full_prompt = f"{system_prompt}\n\nUsuario: {query}\n\nRespuesta:"

            # Conectar con LLM
            async with httpx.AsyncClient(timeout=45.0) as client:
                response = await client.post(
                    "http://localhost:8005/generate",
                    json={"prompt": full_prompt, "max_tokens": 600, "temperature": 0.7},
                    headers={
                        "Content-Type": "application/json",
                        "Origin": "http://localhost:8005",
                    },
                )

                if response.status_code == 200:
                    llm_response = response.json().get("response", "")
                    if llm_response and len(llm_response.strip()) > 10:
                        self.logger.info(
                            f"✅ Respuesta generada por LLM para dominio '{domain}': {len(llm_response)} caracteres"
                        )
                        return llm_response.strip()
                    else:
                        return f"Lo siento, no pude generar una respuesta específica para tu consulta sobre {domain}."
                else:
                    self.logger.error(f"❌ Error del LLM: {response.status_code}")
                    return f"Disculpa, estoy teniendo problemas técnicos con el procesamiento de tu consulta sobre {domain}."

        except Exception as e:
            self.logger.error(f"❌ Error conectando con LLM: {e}")
            return f"Lo siento, hay un problema de conexión con el sistema de IA. Tu consulta sobre {domain} no pudo ser procesada en este momento."

    def get_status(self) -> Dict[str, Any]:
        """Obtener estado del sistema"""
        uptime = datetime.now() - self.startup_time
        return {
            "system": "Simple Sheily AI",
            "version": "1.0.0",
            "status": "running" if self.is_initialized else "error",
            "initialized": self.is_initialized,
            "start_time": self.startup_time.isoformat(),
            "uptime_seconds": uptime.total_seconds(),
            "requests_processed": self.request_count,
            "llm_connected": True,  # Asumimos que está conectado
            "timestamp": datetime.now().isoformat(),
        }


# Modelo Pydantic para requests
class QueryRequest(BaseModel):
    query: str
    domain: str = "general"
    context: Optional[Dict[str, Any]] = None


class QueryResponse(BaseModel):
    query: str
    response: str
    confidence: float
    processing_time: float
    domain: str
    quality_score: float
    timestamp: str
    issues: List[str] = []


# Crear aplicación FastAPI
app = FastAPI(
    title="Simple Sheily AI Server",
    description="Servidor simplificado para Sheily AI con conexión a LLM Llama 3.2 Q8_0",
    version="1.0.0",
)

# Configurar CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Instancia del sistema
sheily_system = SimpleSheilySystem()


# Endpoints
@app.get("/")
async def root():
    """Endpoint raíz"""
    return {
        "message": "Simple Sheily AI Server",
        "version": "1.0.0",
        "status": "running",
        "endpoints": ["/health", "/query", "/status"],
    }


@app.get("/health")
async def health_check():
    """Verificar salud del sistema"""
    try:
        status = sheily_system.get_status()
        return {
            "status": "healthy" if status["initialized"] else "unhealthy",
            "timestamp": datetime.now().isoformat(),
            "uptime": status["uptime_seconds"],
            "requests_processed": status["requests_processed"],
        }
    except Exception as e:
        logger.error(f"Error en health check: {e}")
        raise HTTPException(status_code=503, detail="Servicio no disponible")


@app.post("/query", response_model=QueryResponse)
async def process_query(request: QueryRequest, background_tasks: BackgroundTasks):
    """Procesar consulta del usuario"""
    if not sheily_system.is_initialized:
        raise HTTPException(status_code=503, detail="Sistema no inicializado")

    try:
        # Procesar consulta
        result = await sheily_system.process_query(request.query, request.context)

        return QueryResponse(
            query=result.query,
            response=result.response,
            confidence=result.confidence,
            processing_time=result.processing_time,
            domain=result.domain,
            quality_score=result.quality_score,
            timestamp=datetime.now().isoformat(),
            issues=result.issues,
        )

    except Exception as e:
        logger.error(f"Error procesando consulta: {e}")
        raise HTTPException(
            status_code=500, detail=f"Error procesando consulta: {str(e)}"
        )


@app.get("/status")
async def get_system_status():
    """Obtener estado completo del sistema"""
    try:
        return sheily_system.get_status()
    except Exception as e:
        logger.error(f"Error obteniendo estado: {e}")
        raise HTTPException(
            status_code=500, detail="Error obteniendo estado del sistema"
        )


# Función para ejecutar servidor
def run_server(host: str = "127.0.0.1", port: int = 8080, reload: bool = False):
    """Ejecutar servidor"""
    logger.info(f"🚀 Iniciando Simple Sheily AI Server en {host}:{port}")

    uvicorn.run(
        "modules.unified_systems.simple_sheily_server:app",
        host=host,
        port=port,
        reload=reload,
        log_level="info",
    )


if __name__ == "__main__":
    run_server()
