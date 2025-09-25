"""
Generación de Respuestas - Response Generator
============================================

Componentes para generación inteligente de respuestas.
"""

import logging
from typing import List, Dict, Any, Optional
from dataclasses import dataclass
import random
import json

logger = logging.getLogger(__name__)


@dataclass
class ResponseContext:
    """Contexto para generación de respuestas"""

    user_query: str
    conversation_history: List[Dict[str, str]]
    user_profile: Dict[str, Any]
    system_context: Dict[str, Any]
    response_type: str = "general"


@dataclass
class GeneratedResponse:
    """Respuesta generada"""

    text: str
    confidence: float
    response_type: str
    metadata: Dict[str, Any]


class ResponseGenerator:
    """Generador de respuestas principal"""

    def __init__(self):
        self.response_templates = self._load_response_templates()

    def _load_response_templates(self) -> Dict[str, List[str]]:
        """Carga plantillas de respuesta"""
        return {
            "greeting": [
                "¡Hola! ¿En qué puedo ayudarte hoy?",
                "Hola, soy tu asistente. ¿Qué necesitas?",
                "¡Bienvenido! ¿Cómo puedo asistirte?",
            ],
            "farewell": [
                "¡Hasta luego! Ha sido un placer ayudarte.",
                "Que tengas un buen día. ¡Vuelve cuando quieras!",
                "¡Adiós! No dudes en volver si necesitas más ayuda.",
            ],
            "confirmation": [
                "Perfecto, entiendo lo que necesitas.",
                "Excelente, procederé con eso.",
                "De acuerdo, lo tengo claro.",
            ],
            "clarification": [
                "¿Podrías ser más específico?",
                "Necesito más detalles para ayudarte mejor.",
                "¿Me puedes explicar un poco más?",
            ],
            "error": [
                "Lo siento, no pude procesar tu solicitud.",
                "Hubo un error. ¿Podrías intentarlo de nuevo?",
                "No pude entender eso. ¿Puedes reformularlo?",
            ],
            "thinking": [
                "Déjame pensar en eso...",
                "Estoy procesando tu solicitud...",
                "Un momento, estoy analizando...",
            ],
        }

    def generate_response(self, context: ResponseContext) -> GeneratedResponse:
        """Genera una respuesta basada en el contexto"""
        try:
            # Usar únicamente generación inteligente
            text = self._generate_intelligent_response(context)

            # Calcular confianza
            confidence = self._calculate_confidence(context, "intelligent")

            # Metadata
            metadata = {
                "response_type": "intelligent",
                "context_used": bool(context.conversation_history),
                "user_profile_used": bool(context.user_profile),
            }

            return GeneratedResponse(
                text=text,
                confidence=confidence,
                response_type="intelligent",
                metadata=metadata,
            )

        except Exception as e:
            logger.error(f"❌ Error generando respuesta: {e}")
            return self._generate_error_response()

    def _determine_response_type(self, context: ResponseContext) -> str:
        """Determina el tipo de respuesta a generar"""
        query = context.user_query.lower()

        # Detectar saludos
        if any(word in query for word in ["hola", "buenos días", "buenas", "saludos"]):
            return "template"

        # Detectar despedidas
        if any(word in query for word in ["adiós", "hasta luego", "chao", "nos vemos"]):
            return "template"

        # Detectar preguntas de clarificación
        if any(word in query for word in ["qué", "cómo", "cuándo", "dónde", "por qué"]):
            return "intelligent"

        # Detectar confirmaciones
        if any(word in query for word in ["sí", "correcto", "exacto", "perfecto"]):
            return "template"

        return "intelligent"

    def _generate_template_response(self, context: ResponseContext) -> str:
        """Genera respuesta usando plantillas"""
        query = context.user_query.lower()

        # Saludos
        if any(word in query for word in ["hola", "buenos días", "buenas", "saludos"]):
            return random.choice(self.response_templates["greeting"])

        # Despedidas
        if any(word in query for word in ["adiós", "hasta luego", "chao", "nos vemos"]):
            return random.choice(self.response_templates["farewell"])

        # Confirmaciones
        if any(word in query for word in ["sí", "correcto", "exacto", "perfecto"]):
            return random.choice(self.response_templates["confirmation"])

        # Clarificaciones
        if len(query.split()) < 3:
            return random.choice(self.response_templates["clarification"])

        raise Exception("Tipo de respuesta no soportado")

    def _generate_intelligent_response(self, context: ResponseContext) -> str:
        """Genera respuesta inteligente basada en contexto"""
        query = context.user_query

        # Analizar el contexto de la conversación
        if context.conversation_history:
            # Usar historial para generar respuesta más contextual
            last_exchange = context.conversation_history[-1]
            if "user" in last_exchange and "assistant" in last_exchange:
                # Continuar la conversación
                return self._continue_conversation(query, last_exchange)

        # Usar perfil del usuario si está disponible
        if context.user_profile:
            return self._personalized_response(query, context.user_profile)

        # Respuesta basada en el tipo de consulta
        return self._analyze_query_type(query)

    def _continue_conversation(self, query: str, last_exchange: Dict[str, str]) -> str:
        """Continúa la conversación basándose en el último intercambio"""
        last_user = last_exchange.get("user", "").lower()
        last_assistant = last_exchange.get("assistant", "").lower()

        # Detectar si es una pregunta de seguimiento
        if "?" in query:
            return f"Basándome en lo que mencionaste antes, {self._generate_helpful_response(query)}"

        # Detectar si es una confirmación o negación
        if any(
            word in query.lower() for word in ["sí", "no", "correcto", "incorrecto"]
        ):
            if "sí" in query.lower() or "correcto" in query.lower():
                return "Perfecto, entonces procedemos con eso. ¿Hay algo más que necesites?"
            else:
                return "Entiendo, entonces ajustemos el enfoque. ¿Qué prefieres?"

        return self._generate_helpful_response(query)

    def _personalized_response(self, query: str, user_profile: Dict[str, Any]) -> str:
        """Genera respuesta personalizada basada en el perfil del usuario"""
        # Usar información del perfil para personalizar
        user_level = user_profile.get("expertise_level", "beginner")
        user_interests = user_profile.get("interests", [])

        if user_level == "expert":
            return f"Como experto, te puedo dar una respuesta técnica detallada: {self._generate_technical_response(query)}"
        elif user_level == "intermediate":
            return f"Te explico de manera clara: {self._generate_clear_response(query)}"
        else:
            return f"Te ayudo paso a paso: {self._generate_simple_response(query)}"

    def _analyze_query_type(self, query: str) -> str:
        """Analiza el tipo de consulta y genera respuesta apropiada"""
        query_lower = query.lower()

        # Preguntas de información
        if any(word in query_lower for word in ["qué es", "cómo funciona", "explica"]):
            return f"Te explico sobre {query}: Es un tema interesante que requiere atención especial."

        # Preguntas de procedimiento
        if any(word in query_lower for word in ["cómo hacer", "pasos", "proceso"]):
            return f"Para {query}, te recomiendo seguir estos pasos: 1) Preparar, 2) Ejecutar, 3) Verificar."

        # Preguntas de comparación
        if any(
            word in query_lower for word in ["diferencias", "comparar", "vs", "versus"]
        ):
            return f"Al comparar {query}, hay varias diferencias importantes que debes considerar."

        # Preguntas de opinión
        if any(word in query_lower for word in ["qué opinas", "crees", "piensas"]):
            return f"Mi opinión sobre {query} es que depende del contexto específico y tus necesidades."

        return self._generate_helpful_response(query)

    def _generate_helpful_response(self, query: str) -> str:
        """Genera respuesta útil genérica"""
        return f"Respecto a tu consulta sobre '{query}', puedo ayudarte con información relevante y soluciones prácticas."

    def _generate_technical_response(self, query: str) -> str:
        """Genera respuesta técnica"""
        return f"Desde una perspectiva técnica, {query} involucra consideraciones avanzadas de implementación y optimización."

    def _generate_clear_response(self, query: str) -> str:
        """Genera respuesta clara y comprensible"""
        return f"Te explico de manera clara: {query} se puede entender como un proceso estructurado con resultados predecibles."

    def _generate_simple_response(self, query: str) -> str:
        """Genera respuesta simple y directa"""
        return f"De manera simple: {query} es algo que puedes aprender paso a paso sin complicaciones."

    def _calculate_confidence(
        self, context: ResponseContext, response_type: str
    ) -> float:
        """Calcula la confianza de la respuesta"""
        confidence = 0.5  # Base

        # Aumentar confianza si hay contexto
        if context.conversation_history:
            confidence += 0.2

        if context.user_profile:
            confidence += 0.1

        # Ajustar por tipo de respuesta
        if response_type == "template":
            confidence += 0.1
        elif response_type == "intelligent":
            confidence += 0.2

        # Ajustar por longitud de consulta
        if len(context.user_query.split()) > 5:
            confidence += 0.1

        return min(1.0, confidence)

    def _generate_backup_response(self, context: ResponseContext) -> str:
        """Genera respuesta de respaldo"""
        raise Exception("Respuesta no disponible")

    def _generate_error_response(self) -> GeneratedResponse:
        """Genera respuesta de error"""
        return GeneratedResponse(
            text=random.choice(self.response_templates["error"]),
            confidence=0.1,
            response_type="error",
            metadata={"error": True},
        )
