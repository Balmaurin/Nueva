"""
Generador Dinámico de Conocimiento - Sheily AI
=============================================

Módulo para generar conocimiento contextual dinámico basado en consultas y dominios.
"""

import logging
from typing import Dict, Any, List, Optional
import json
import sqlite3
from pathlib import Path

logger = logging.getLogger(__name__)


class DynamicKnowledgeGenerator:
    """Generador de conocimiento contextual dinámico"""

    def __init__(self, knowledge_db_path: Optional[str] = None):
        """
        Inicializar generador de conocimiento

        Args:
            knowledge_db_path: Ruta a la base de datos de conocimiento
        """
        self.logger = logging.getLogger(__name__)

        # Configurar ruta de base de datos
        if knowledge_db_path:
            self.db_path = knowledge_db_path
        else:
            base_path = Path(__file__).parent.parent.parent
            self.db_path = str(base_path / "data" / "knowledge_base.db")

        # Patrones de conocimiento por dominio
        self.domain_patterns = {
            "programming": {
                "keywords": [
                    "código",
                    "python",
                    "javascript",
                    "función",
                    "variable",
                    "algoritmo",
                ],
                "context_template": "En el contexto de programación, considerando las mejores prácticas...",
            },
            "ai": {
                "keywords": [
                    "inteligencia artificial",
                    "machine learning",
                    "neural network",
                    "modelo",
                    "entrenamiento",
                ],
                "context_template": "Desde la perspectiva de inteligencia artificial y machine learning...",
            },
            "general": {
                "keywords": ["información", "ayuda", "explicación", "definición"],
                "context_template": "Proporcionando información general y útil...",
            },
        }

    def generate_contextual_knowledge(
        self, context: str, domain: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Generar conocimiento contextual basado en el contexto y dominio

        Args:
            context: Contexto de la consulta
            domain: Dominio específico (opcional)

        Returns:
            Diccionario con conocimiento contextual generado
        """
        try:
            # Determinar dominio si no se proporciona
            if not domain:
                domain = self._classify_domain(context)

            # Obtener conocimiento de la base de datos
            db_knowledge = self._get_relevant_knowledge(context, domain)

            # Generar conocimiento dinámico
            dynamic_knowledge = self._generate_dynamic_context(context, domain)

            # Combinar conocimientos
            contextual_knowledge = {
                "domain": domain,
                "context": context,
                "database_knowledge": db_knowledge,
                "dynamic_knowledge": dynamic_knowledge,
                "confidence": self._calculate_confidence(
                    db_knowledge, dynamic_knowledge
                ),
                "suggestions": self._generate_suggestions(context, domain),
            }

            return contextual_knowledge

        except Exception as e:
            self.logger.error(f"Error generando conocimiento contextual: {e}")
            return {
                "domain": domain or "general",
                "context": context,
                "database_knowledge": [],
                "dynamic_knowledge": {"error": str(e)},
                "confidence": 0.0,
                "suggestions": [],
            }

    def _classify_domain(self, context: str) -> str:
        """Clasificar dominio basado en el contexto"""
        context_lower = context.lower()

        domain_scores = {}
        for domain, patterns in self.domain_patterns.items():
            score = 0
            for keyword in patterns["keywords"]:
                if keyword in context_lower:
                    score += 1
            domain_scores[domain] = score

        # Retornar dominio con mayor puntuación
        best_domain = max(domain_scores, key=domain_scores.get)
        if domain_scores[best_domain] == 0:
            return "general"

        return best_domain

    def _get_relevant_knowledge(
        self, context: str, domain: str
    ) -> List[Dict[str, Any]]:
        """Obtener conocimiento relevante de la base de datos"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            # Buscar conocimiento por contenido (sin category ya que no existe)
            cursor.execute(
                """
                SELECT topic, content, source, created_at 
                FROM knowledge_base 
                WHERE content LIKE ? 
                ORDER BY created_at DESC 
                LIMIT 5
            """,
                (f"%{context[:50]}%",),
            )

            results = cursor.fetchall()
            conn.close()

            knowledge_items = []
            for row in results:
                knowledge_items.append(
                    {
                        "topic": row[0],
                        "content": row[1],
                        "source": row[2],
                        "created_at": row[3],
                        "confidence": 0.8,  # Confianza por defecto
                    }
                )

            return knowledge_items

        except Exception as e:
            self.logger.error(f"Error accediendo a base de conocimiento: {e}")
            return []

    def _generate_dynamic_context(self, context: str, domain: str) -> Dict[str, Any]:
        """Generar contexto dinámico basado en patrones"""
        try:
            domain_pattern = self.domain_patterns.get(
                domain, self.domain_patterns["general"]
            )

            dynamic_context = {
                "context_template": domain_pattern["context_template"],
                "relevant_keywords": [
                    kw for kw in domain_pattern["keywords"] if kw in context.lower()
                ],
                "context_length": len(context),
                "complexity_level": self._assess_complexity(context),
                "generated_insights": self._generate_insights(context, domain),
            }

            return dynamic_context

        except Exception as e:
            self.logger.error(f"Error generando contexto dinámico: {e}")
            return {"error": str(e)}

    def _assess_complexity(self, context: str) -> str:
        """Evaluar complejidad del contexto"""
        if len(context) < 50:
            return "simple"
        elif len(context) < 200:
            return "medium"
        else:
            return "complex"

    def _generate_insights(self, context: str, domain: str) -> List[str]:
        """Generar insights basados en el contexto y dominio"""
        insights = []

        if domain == "programming":
            insights.extend(
                [
                    "Considera las mejores prácticas de programación",
                    "Verifica la eficiencia del algoritmo",
                    "Asegúrate de manejar casos edge",
                ]
            )
        elif domain == "ai":
            insights.extend(
                [
                    "Evalúa la calidad de los datos de entrenamiento",
                    "Considera el overfitting y underfitting",
                    "Valida el rendimiento del modelo",
                ]
            )
        else:
            insights.extend(
                [
                    "Proporciona información clara y precisa",
                    "Considera múltiples perspectivas",
                    "Verifica la exactitud de la información",
                ]
            )

        return insights[:3]  # Limitar a 3 insights

    def _calculate_confidence(
        self, db_knowledge: List[Dict], dynamic_knowledge: Dict
    ) -> float:
        """Calcular confianza del conocimiento generado"""
        try:
            # Confianza basada en conocimiento de BD
            db_confidence = 0.0
            if db_knowledge:
                db_confidence = sum(
                    item.get("confidence", 0.0) for item in db_knowledge
                ) / len(db_knowledge)

            # Confianza basada en conocimiento dinámico
            dynamic_confidence = 0.5  # Base
            if "error" not in dynamic_knowledge:
                dynamic_confidence += 0.3
            if dynamic_knowledge.get("relevant_keywords"):
                dynamic_confidence += 0.2

            # Combinar confianzas
            total_confidence = (db_confidence * 0.7) + (dynamic_confidence * 0.3)
            return min(total_confidence, 1.0)

        except Exception as e:
            self.logger.error(f"Error calculando confianza: {e}")
            return 0.0

    def _generate_suggestions(self, context: str, domain: str) -> List[str]:
        """Generar sugerencias basadas en el contexto"""
        suggestions = []

        # Sugerencias generales
        suggestions.append(f"Explorar más sobre {domain}")
        suggestions.append("Considerar ejemplos prácticos")

        # Sugerencias específicas por dominio
        if domain == "programming":
            suggestions.append("Revisar documentación oficial")
            suggestions.append("Probar con ejemplos de código")
        elif domain == "ai":
            suggestions.append("Explorar datasets relacionados")
            suggestions.append("Considerar métricas de evaluación")

        return suggestions[:4]  # Limitar a 4 sugerencias

    def update_knowledge_base(
        self, topic: str, content: str, category: str, confidence: float = 0.8
    ):
        """Actualizar base de conocimiento con nueva información"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            cursor.execute(
                """
                INSERT OR REPLACE INTO knowledge_base 
                (topic, content, category, confidence, created_at) 
                VALUES (?, ?, ?, ?, datetime('now'))
            """,
                (topic, content, category, confidence),
            )

            conn.commit()
            conn.close()

            self.logger.info(f"Conocimiento actualizado: {topic}")
            return True

        except Exception as e:
            self.logger.error(f"Error actualizando base de conocimiento: {e}")
            return False
