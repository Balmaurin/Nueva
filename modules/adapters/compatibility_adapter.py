"""
Adaptador de Compatibilidad para NeuroFusion
============================================

Este módulo resuelve incompatibilidades entre diferentes componentes
del sistema NeuroFusion, proporcionando interfaces unificadas y
adaptadores para módulos que no siguen el mismo patrón.
"""

import logging
import asyncio
from typing import Dict, Any, Optional, List, Union, Callable
from dataclasses import dataclass
from datetime import datetime
import traceback

logger = logging.getLogger(__name__)


@dataclass
class CompatibilityIssue:
    """Problema de compatibilidad identificado"""

    component_name: str
    issue_type: str  # import, interface, version, dependency
    description: str
    severity: str  # low, medium, high, critical
    solution: str
    timestamp: datetime = None

    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = datetime.now()


class CompatibilityAdapter:
    """
    Adaptador que resuelve incompatibilidades entre módulos
    """

    def __init__(self):
        self.adapters: Dict[str, Callable] = {}
        self.issues: List[CompatibilityIssue] = []
        self.fixes_applied: List[str] = []

        # Registrar adaptadores
        self._register_adapters()

    def _register_adapters(self):
        """Registrar todos los adaptadores de compatibilidad"""

        # Adaptador para sistemas de embeddings
        self.adapters["embedding_system"] = self._adapt_embedding_system

        # Adaptador para sistemas de tokenización
        self.adapters["tokenizer_system"] = self._adapt_tokenizer_system

        # Adaptador para sistemas de IA
        self.adapters["ai_system"] = self._adapt_ai_system

        # Adaptador para sistemas de ramas
        self.adapters["branch_system"] = self._adapt_branch_system

        # Adaptador para sistemas de aprendizaje
        self.adapters["learning_system"] = self._adapt_learning_system

        # Adaptador para sistemas de memoria
        self.adapters["memory_system"] = self._adapt_memory_system

        # Adaptador para sistemas de seguridad
        self.adapters["security_system"] = self._adapt_security_system

    def _adapt_embedding_system(self, component: Any, config: Dict[str, Any]) -> Any:
        """Adaptar sistema de embeddings para compatibilidad"""
        try:
            # Verificar si el componente tiene la interfaz esperada
            if hasattr(component, "generate_embedding"):
                # Ya es compatible
                return component

            # Adaptar diferentes implementaciones
            if hasattr(component, "embed"):
                # Adaptar método 'embed' a 'generate_embedding'
                original_embed = component.embed

                def generate_embedding(text: str, **kwargs):
                    return original_embed(text, **kwargs)

                component.generate_embedding = generate_embedding
                self.fixes_applied.append(
                    f"Adaptado método 'embed' a 'generate_embedding' en {component.__class__.__name__}"
                )

            elif hasattr(component, "encode"):
                # Adaptar método 'encode' a 'generate_embedding'
                original_encode = component.encode

                def generate_embedding(text: str, **kwargs):
                    return original_encode(text, **kwargs)

                component.generate_embedding = generate_embedding
                self.fixes_applied.append(
                    f"Adaptado método 'encode' a 'generate_embedding' en {component.__class__.__name__}"
                )

            return component

        except Exception as e:
            self.issues.append(
                CompatibilityIssue(
                    component_name=component.__class__.__name__,
                    issue_type="interface",
                    description=f"Error adaptando sistema de embeddings: {e}",
                    severity="high",
                )
            )
            return component

    def _adapt_tokenizer_system(self, component: Any, config: Dict[str, Any]) -> Any:
        """Adaptar sistema de tokenización para compatibilidad"""
        try:
            # Verificar métodos requeridos
            required_methods = ["encode", "decode"]

            for method in required_methods:
                if not hasattr(component, method):
                    # Crear método faltante con implementación básica
                    if method == "encode":

                        def encode(text: str, **kwargs):
                            return text.split()

                        component.encode = encode
                    elif method == "decode":

                        def decode(tokens, **kwargs):
                            if isinstance(tokens, list):
                                return " ".join(tokens)
                            return str(tokens)

                        component.decode = decode

                    self.fixes_applied.append(
                        f"Agregado método '{method}' a {component.__class__.__name__}"
                    )

            return component

        except Exception as e:
            self.issues.append(
                CompatibilityIssue(
                    component_name=component.__class__.__name__,
                    issue_type="interface",
                    description=f"Error adaptando sistema de tokenización: {e}",
                    severity="high",
                )
            )
            return component

    def _adapt_ai_system(self, component: Any, config: Dict[str, Any]) -> Any:
        """Adaptar sistema de IA para compatibilidad"""
        try:
            # Verificar método de generación de respuestas
            if not hasattr(component, "generate_response"):
                if hasattr(component, "process_query"):
                    # Adaptar process_query a generate_response
                    original_process = component.process_query

                    def generate_response(prompt: str, **kwargs):
                        result = original_process(prompt, **kwargs)
                        if isinstance(result, dict):
                            return result.get("response", str(result))
                        return str(result)

                    component.generate_response = generate_response
                    self.fixes_applied.append(
                        f"Adaptado 'process_query' a 'generate_response' en {component.__class__.__name__}"
                    )

                elif hasattr(component, "answer"):
                    # Adaptar answer a generate_response
                    original_answer = component.answer

                    def generate_response(prompt: str, **kwargs):
                        return original_answer(prompt, **kwargs)

                    component.generate_response = generate_response
                    self.fixes_applied.append(
                        f"Adaptado 'answer' a 'generate_response' en {component.__class__.__name__}"
                    )

            return component

        except Exception as e:
            self.issues.append(
                CompatibilityIssue(
                    component_name=component.__class__.__name__,
                    issue_type="interface",
                    description=f"Error adaptando sistema de IA: {e}",
                    severity="high",
                )
            )
            return component

    def _adapt_branch_system(self, component: Any, config: Dict[str, Any]) -> Any:
        """Adaptar sistema de ramas para compatibilidad"""
        try:
            # Verificar método de detección de ramas
            if not hasattr(component, "detect_branches"):
                if hasattr(component, "detect_domain"):
                    # Adaptar detect_domain a detect_branches
                    original_detect = component.detect_domain

                    async def detect_branches(query: str, **kwargs):
                        domain = await original_detect(query, **kwargs)
                        return [domain] if domain else ["general"]

                    component.detect_branches = detect_branches
                    self.fixes_applied.append(
                        f"Adaptado 'detect_domain' a 'detect_branches' en {component.__class__.__name__}"
                    )

                elif hasattr(component, "classify"):
                    # Adaptar classify a detect_branches
                    original_classify = component.classify

                    async def detect_branches(query: str, **kwargs):
                        classification = await original_classify(query, **kwargs)
                        if isinstance(classification, list):
                            return classification
                        elif isinstance(classification, str):
                            return [classification]
                        return ["general"]

                    component.detect_branches = detect_branches
                    self.fixes_applied.append(
                        f"Adaptado 'classify' a 'detect_branches' en {component.__class__.__name__}"
                    )

            return component

        except Exception as e:
            self.issues.append(
                CompatibilityIssue(
                    component_name=component.__class__.__name__,
                    issue_type="interface",
                    description=f"Error adaptando sistema de ramas: {e}",
                    severity="medium",
                )
            )
            return component

    def _adapt_learning_system(self, component: Any, config: Dict[str, Any]) -> Any:
        """Adaptar sistema de aprendizaje para compatibilidad"""
        try:
            # Verificar método de entrenamiento
            if not hasattr(component, "train_with_data"):
                if hasattr(component, "learn"):
                    # Adaptar learn a train_with_data
                    original_learn = component.learn

                    def train_with_data(
                        data: str, domain: str = "general", learning_rate: float = 0.001
                    ):
                        return original_learn(data, domain, learning_rate)

                    component.train_with_data = train_with_data
                    self.fixes_applied.append(
                        f"Adaptado 'learn' a 'train_with_data' en {component.__class__.__name__}"
                    )

                elif hasattr(component, "update"):
                    # Adaptar update a train_with_data
                    original_update = component.update

                    def train_with_data(
                        data: str, domain: str = "general", learning_rate: float = 0.001
                    ):
                        return original_update(data, domain, learning_rate)

                    component.train_with_data = train_with_data
                    self.fixes_applied.append(
                        f"Adaptado 'update' a 'train_with_data' en {component.__class__.__name__}"
                    )

            return component

        except Exception as e:
            self.issues.append(
                CompatibilityIssue(
                    component_name=component.__class__.__name__,
                    issue_type="interface",
                    description=f"Error adaptando sistema de aprendizaje: {e}",
                    severity="medium",
                )
            )
            return component

    def _adapt_memory_system(self, component: Any, config: Dict[str, Any]) -> Any:
        """Adaptar sistema de memoria para compatibilidad"""
        try:
            # Verificar método de almacenamiento de memoria
            if not hasattr(component, "add_memory"):
                if hasattr(component, "store"):
                    # Adaptar store a add_memory
                    original_store = component.store

                    def add_memory(
                        content: str,
                        memory_type: str = "custom",
                        tags: List[str] = None,
                    ):
                        return original_store(content, memory_type, tags)

                    component.add_memory = add_memory
                    self.fixes_applied.append(
                        f"Adaptado 'store' a 'add_memory' en {component.__class__.__name__}"
                    )

                elif hasattr(component, "save"):
                    # Adaptar save a add_memory
                    original_save = component.save

                    def add_memory(
                        content: str,
                        memory_type: str = "custom",
                        tags: List[str] = None,
                    ):
                        return original_save(content, memory_type, tags)

                    component.add_memory = add_memory
                    self.fixes_applied.append(
                        f"Adaptado 'save' a 'add_memory' en {component.__class__.__name__}"
                    )

            return component

        except Exception as e:
            self.issues.append(
                CompatibilityIssue(
                    component_name=component.__class__.__name__,
                    issue_type="interface",
                    description=f"Error adaptando sistema de memoria: {e}",
                    severity="medium",
                )
            )
            return component

    def _adapt_security_system(self, component: Any, config: Dict[str, Any]) -> Any:
        """Adaptar sistema de seguridad para compatibilidad"""
        try:
            # Verificar métodos de autenticación
            if not hasattr(component, "authenticate"):
                if hasattr(component, "verify"):
                    # Adaptar verify a authenticate
                    original_verify = component.verify

                    def authenticate(credentials: Dict[str, Any]):
                        return original_verify(credentials)

                    component.authenticate = authenticate
                    self.fixes_applied.append(
                        f"Adaptado 'verify' a 'authenticate' en {component.__class__.__name__}"
                    )

                elif hasattr(component, "validate"):
                    # Adaptar validate a authenticate
                    original_validate = component.validate

                    def authenticate(credentials: Dict[str, Any]):
                        return original_validate(credentials)

                    component.authenticate = authenticate
                    self.fixes_applied.append(
                        f"Adaptado 'validate' a 'authenticate' en {component.__class__.__name__}"
                    )

            return component

        except Exception as e:
            self.issues.append(
                CompatibilityIssue(
                    component_name=component.__class__.__name__,
                    issue_type="interface",
                    description=f"Error adaptando sistema de seguridad: {e}",
                    severity="medium",
                )
            )
            return component

    def adapt_component(
        self, component_name: str, component: Any, config: Dict[str, Any]
    ) -> Any:
        """Adaptar un componente específico"""
        try:
            if component_name in self.adapters:
                adapted_component = self.adapters[component_name](component, config)
                logger.info(f"✅ Componente {component_name} adaptado correctamente")
                return adapted_component
            else:
                logger.warning(f"⚠️ No hay adaptador para {component_name}")
                return component

        except Exception as e:
            logger.error(f"❌ Error adaptando {component_name}: {e}")
            self.issues.append(
                CompatibilityIssue(
                    component_name=component_name,
                    issue_type="adapter",
                    description=f"Error en adaptador: {e}",
                    severity="high",
                    solution="Revisar implementación del adaptador",
                )
            )
            return component

    def get_compatibility_report(self) -> Dict[str, Any]:
        """Obtener reporte de compatibilidad"""
        return {
            "total_issues": len(self.issues),
            "total_fixes": len(self.fixes_applied),
            "issues_by_severity": {
                "critical": len([i for i in self.issues if i.severity == "critical"]),
                "high": len([i for i in self.issues if i.severity == "high"]),
                "medium": len([i for i in self.issues if i.severity == "medium"]),
                "low": len([i for i in self.issues if i.severity == "low"]),
            },
            "recent_issues": [
                {
                    "component": i.component_name,
                    "type": i.issue_type,
                    "description": i.description,
                    "severity": i.severity,
                    "timestamp": i.timestamp.isoformat(),
                }
                for i in self.issues[-10:]  # Últimos 10 problemas
            ],
            "applied_fixes": self.fixes_applied[-10:],  # Últimas 10 correcciones
        }

    def clear_issues(self):
        """Limpiar historial de problemas"""
        self.issues.clear()
        self.fixes_applied.clear()
        logger.info("🧹 Historial de problemas limpiado")


# Instancia global del adaptador
_compatibility_adapter: Optional[CompatibilityAdapter] = None


def get_compatibility_adapter() -> CompatibilityAdapter:
    """Obtener instancia global del adaptador de compatibilidad"""
    global _compatibility_adapter

    if _compatibility_adapter is None:
        _compatibility_adapter = CompatibilityAdapter()

    return _compatibility_adapter


def main():
    """Función de demostración del adaptador"""
    print("🔧 Adaptador de Compatibilidad de NeuroFusion")
    print("=" * 50)

    adapter = get_compatibility_adapter()

    # Simular algunos problemas de compatibilidad
    class RealComponent:
        def embed(self, text):
            return [1, 2, 3]

    real_component = RealComponent()

    # Adaptar componente
    adapted = adapter.adapt_component("embedding_system", real_component, {})

    # Verificar que se agregó el método
    if hasattr(adapted, "generate_embedding"):
        print("✅ Adaptación exitosa: método 'generate_embedding' agregado")

    # Mostrar reporte
    report = adapter.get_compatibility_report()
    print(f"\n📊 Reporte de compatibilidad:")
    print(f"   Problemas totales: {report['total_issues']}")
    print(f"   Correcciones aplicadas: {report['total_fixes']}")
    print(f"   Problemas por severidad: {report['issues_by_severity']}")


if __name__ == "__main__":
    main()
