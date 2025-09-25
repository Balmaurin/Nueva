"""
Gestor de Dependencias Unificado para NeuroFusion
=================================================

Este módulo gestiona las dependencias entre todos los componentes
del sistema NeuroFusion, asegurando que se carguen en el orden correcto
y resolviendo conflictos de dependencias.
"""

import logging
import asyncio
import importlib
import sys
from typing import Dict, Any, Optional, List, Set, Tuple
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
import traceback

logger = logging.getLogger(__name__)


@dataclass
class DependencyInfo:
    """Información de una dependencia"""

    name: str
    version: str
    required: bool = True
    optional_dependencies: List[str] = field(default_factory=list)
    conflicts: List[str] = field(default_factory=list)
    load_order: int = 0


@dataclass
class ModuleInfo:
    """Información de un módulo"""

    name: str
    path: str
    dependencies: List[str] = field(default_factory=list)
    optional_dependencies: List[str] = field(default_factory=list)
    conflicts: List[str] = field(default_factory=list)
    load_order: int = 0
    status: str = "pending"  # pending, loading, loaded, error
    error_message: Optional[str] = None
    load_time: Optional[datetime] = None


class DependencyManager:
    """
    Gestor de dependencias que maneja la carga ordenada de módulos
    """

    def __init__(self):
        self.modules: Dict[str, ModuleInfo] = {}
        self.loaded_modules: Dict[str, Any] = {}
        self.dependency_graph: Dict[str, List[str]] = {}
        self.load_order: List[str] = []
        self.errors: List[Dict[str, Any]] = []

        # Registrar todos los módulos del sistema
        self._register_system_modules()

        # Construir grafo de dependencias
        self._build_dependency_graph()

        # Calcular orden de carga
        self._calculate_load_order()

    def _register_system_modules(self):
        """Registrar todos los módulos del sistema NeuroFusion"""

        # Módulos base (sin dependencias)
        base_modules = [
            {"name": "base_tools", "path": "ai.base_tools", "dependencies": []},
            {
                "name": "unified_branch_tokenizer",
                "path": "ai.unified_branch_tokenizer",
                "dependencies": [],
            },
            {
                "name": "account_recovery",
                "path": "ai.account_recovery",
                "dependencies": [],
            },
            {
                "name": "digital_signature",
                "path": "ai.digital_signature",
                "dependencies": [],
            },
            {"name": "jwt_auth", "path": "ai.jwt_auth", "dependencies": []},
            {
                "name": "two_factor_auth",
                "path": "ai.two_factor_auth",
                "dependencies": [],
            },
        ]

        # Módulos de embeddings y procesamiento
        embedding_modules = [
            {
                "name": "perfect_embeddings",
                "path": "ai.perfect_embeddings",
                "dependencies": ["base_tools"],
            },
            {
                "name": "real_embeddings",
                "path": "ai.real_embeddings",
                "dependencies": ["base_tools"],
            },
            {
                "name": "real_time_embeddings",
                "path": "ai.real_time_embeddings",
                "dependencies": ["base_tools"],
            },
            {
                "name": "embedding_cache_optimizer",
                "path": "ai.embedding_cache_optimizer",
                "dependencies": ["base_tools"],
            },
            {
                "name": "embedding_performance_monitor",
                "path": "ai.embedding_performance_monitor",
                "dependencies": ["base_tools"],
            },
        ]

        # Módulos de IA y procesamiento
        ai_modules = [
            {
                "name": "advanced_ai_system",
                "path": "ai.advanced_ai_system",
                "dependencies": ["unified_branch_tokenizer", "perfect_embeddings"],
            },
            {
                "name": "neurofusion_hybrid_llm_real",
                "path": "ai.neurofusion_hybrid_llm_real",
                "dependencies": ["unified_branch_tokenizer"],
            },
            {
                "name": "real_transformer",
                "path": "ai.real_transformer",
                "dependencies": ["base_tools"],
            },
            {
                "name": "llm_training_pipeline",
                "path": "ai.llm_training_pipeline",
                "dependencies": ["base_tools"],
            },
        ]

        # Módulos de detección y ramas
        branch_modules = [
            {
                "name": "enhanced_branch_detector",
                "path": "ai.enhanced_branch_detector",
                "dependencies": ["perfect_embeddings"],
            },
            {
                "name": "enhanced_multi_branch_system",
                "path": "ai.enhanced_multi_branch_system",
                "dependencies": ["enhanced_branch_detector", "advanced_ai_system"],
            },
        ]

        # Módulos de aprendizaje
        learning_modules = [
            {
                "name": "continuous_learning",
                "path": "ai.continuous_learning",
                "dependencies": ["base_tools"],
            },
            {
                "name": "continuous_learning_system",
                "path": "ai.continuous_learning_system",
                "dependencies": ["base_tools"],
            },
            {
                "name": "consolidated_learning_system",
                "path": "ai.consolidated_learning_system",
                "dependencies": ["base_tools"],
            },
            {
                "name": "advanced_llm_training",
                "path": "ai.advanced_llm_training",
                "dependencies": ["base_tools"],
            },
            {
                "name": "dynamic_training_system",
                "path": "ai.dynamic_training_system",
                "dependencies": ["base_tools"],
            },
            {
                "name": "gradient_training_system",
                "path": "ai.gradient_training_system",
                "dependencies": ["base_tools"],
            },
            {
                "name": "specialized_training",
                "path": "ai.specialized_training",
                "dependencies": ["base_tools"],
            },
        ]

        # Módulos de memoria
        memory_modules = [
            {
                "name": "episodic_memory_system",
                "path": "ai.episodic_memory_system",
                "dependencies": ["perfect_embeddings"],
            },
            {
                "name": "advanced_episodic_memory",
                "path": "ai.advanced_episodic_memory",
                "dependencies": ["base_tools"],
            },
        ]

        # Módulos de expertos
        expert_modules = [
            {
                "name": "expert_system",
                "path": "ai.expert_system",
                "dependencies": ["base_tools"],
            },
            {
                "name": "multi_domain_expert_system",
                "path": "ai.multi_domain_expert_system",
                "dependencies": ["advanced_ai_system", "enhanced_branch_detector"],
            },
        ]

        # Módulos de seguridad
        security_modules = [
            {
                "name": "unified_auth_security_system",
                "path": "ai.unified_auth_security_system",
                "dependencies": ["jwt_auth", "two_factor_auth", "digital_signature"],
            },
            {
                "name": "password_policy",
                "path": "ai.password_policy",
                "dependencies": ["base_tools"],
            },
            {
                "name": "intrusion_detection",
                "path": "ai.intrusion_detection",
                "dependencies": ["base_tools"],
            },
            {
                "name": "user_activity_monitor",
                "path": "ai.user_activity_monitor",
                "dependencies": ["base_tools"],
            },
            {
                "name": "user_anomaly_detector",
                "path": "ai.user_anomaly_detector",
                "dependencies": ["base_tools"],
            },
        ]

        # Módulos de blockchain
        blockchain_modules = [
            {
                "name": "solana_blockchain_real",
                "path": "ai.solana_blockchain_real",
                "dependencies": ["base_tools"],
            },
            {
                "name": "sheily_tokens_system",
                "path": "ai.sheily_tokens_system",
                "dependencies": ["solana_blockchain_real"],
            },
        ]

        # Módulos de evaluación y calidad
        evaluation_modules = [
            {
                "name": "ai_quality_evaluator",
                "path": "ai.ai_quality_evaluator",
                "dependencies": ["base_tools"],
            },
            {
                "name": "simple_ai_evaluator",
                "path": "ai.simple_ai_evaluator",
                "dependencies": ["base_tools"],
            },
            {
                "name": "score_quality",
                "path": "ai.score_quality",
                "dependencies": ["base_tools"],
            },
        ]

        # Módulos de búsqueda e indexación
        search_modules = [
            {
                "name": "master_indexing_system",
                "path": "ai.master_indexing_system",
                "dependencies": ["perfect_embeddings"],
            },
            {
                "name": "vector_index_manager",
                "path": "ai.vector_index_manager",
                "dependencies": ["base_tools"],
            },
            {
                "name": "semantic_search_engine",
                "path": "ai.semantic_search_engine",
                "dependencies": ["base_tools"],
            },
            {
                "name": "rag_system",
                "path": "ai.rag_system",
                "dependencies": ["perfect_embeddings", "master_indexing_system"],
            },
        ]

        # Módulos de datos y datasets
        data_modules = [
            {
                "name": "download_headqa_dataset",
                "path": "ai.download_headqa_dataset",
                "dependencies": ["base_tools"],
            },
            {
                "name": "download_training_dataset",
                "path": "ai.download_training_dataset",
                "dependencies": ["base_tools"],
            },
            {
                "name": "expand_headqa_dataset",
                "path": "ai.expand_headqa_dataset",
                "dependencies": ["base_tools"],
            },
            {
                "name": "import_datasets_to_branches",
                "path": "ai.import_datasets_to_branches",
                "dependencies": ["base_tools"],
            },
            {
                "name": "add_more_training_data",
                "path": "ai.add_more_training_data",
                "dependencies": ["base_tools"],
            },
        ]

        # Módulos de utilidades y herramientas
        utility_modules = [
            {
                "name": "module_enhancer",
                "path": "ai.module_enhancer",
                "dependencies": ["base_tools"],
            },
            {
                "name": "advanced_module_enhancer",
                "path": "ai.advanced_module_enhancer",
                "dependencies": ["base_tools"],
            },
            {
                "name": "model_validation",
                "path": "ai.model_validation",
                "dependencies": ["base_tools"],
            },
            {
                "name": "performance_metrics",
                "path": "ai.performance_metrics",
                "dependencies": ["base_tools"],
            },
            {
                "name": "weights_initializer",
                "path": "ai.weights_initializer",
                "dependencies": ["base_tools"],
            },
        ]

        # Módulos de análisis y razonamiento
        analysis_modules = [
            {
                "name": "advanced_contextual_reasoning",
                "path": "ai.advanced_contextual_reasoning",
                "dependencies": ["perfect_embeddings"],
            },
            {
                "name": "advanced_reasoning_capabilities",
                "path": "ai.advanced_reasoning_capabilities",
                "dependencies": ["base_tools"],
            },
            {
                "name": "advanced_reasoning_system",
                "path": "ai.advanced_reasoning_system",
                "dependencies": ["base_tools"],
            },
            {
                "name": "contradiction_resolver",
                "path": "ai.contradiction_resolver",
                "dependencies": ["base_tools"],
            },
            {
                "name": "cross_domain_knowledge_transfer",
                "path": "ai.cross_domain_knowledge_transfer",
                "dependencies": ["base_tools"],
            },
        ]

        # Módulos de emociones y conciencia
        emotion_modules = [
            {
                "name": "emotional_controller",
                "path": "ai.emotional_controller",
                "dependencies": ["base_tools"],
            },
            {
                "name": "advanced_emotional_controller",
                "path": "ai.advanced_emotional_controller",
                "dependencies": ["base_tools"],
            },
            {
                "name": "emotional_adapter",
                "path": "ai.emotional_adapter",
                "dependencies": ["base_tools"],
            },
            {
                "name": "real_emotional_analysis",
                "path": "ai.real_emotional_analysis",
                "dependencies": ["base_tools"],
            },
            {
                "name": "consciousness_manager",
                "path": "ai.consciousness_manager",
                "dependencies": ["base_tools"],
            },
            {
                "name": "consciousness_adapter",
                "path": "ai.consciousness_adapter",
                "dependencies": ["base_tools"],
            },
            {
                "name": "consciousness_system",
                "path": "ai.consciousness_system",
                "dependencies": ["base_tools"],
            },
        ]

        # Módulos de mejora y optimización
        improvement_modules = [
            {
                "name": "improve_branch_system",
                "path": "ai.improve_branch_system",
                "dependencies": ["enhanced_multi_branch_system"],
            },
            {
                "name": "advanced_algorithm_refinement",
                "path": "ai.advanced_algorithm_refinement",
                "dependencies": ["base_tools"],
            },
            {
                "name": "neural_plasticity_manager",
                "path": "ai.neural_plasticity_manager",
                "dependencies": ["base_tools"],
            },
        ]

        # Módulos de componentes y arquitectura
        component_modules = [
            {
                "name": "neurofusion_component_hub",
                "path": "ai.neurofusion_component_hub",
                "dependencies": ["base_tools"],
            },
            {
                "name": "layer_manager",
                "path": "ai.layer_manager",
                "dependencies": ["base_tools"],
            },
            {
                "name": "knowledge_domain_manager",
                "path": "ai.knowledge_domain_manager",
                "dependencies": ["base_tools"],
            },
            {
                "name": "dynamic_domain_framework",
                "path": "ai.dynamic_domain_framework",
                "dependencies": ["base_tools"],
            },
        ]

        # Módulos de salida y generación
        output_modules = [
            {
                "name": "classification_output",
                "path": "ai.classification_output",
                "dependencies": ["base_tools"],
            },
            {
                "name": "generation_output",
                "path": "ai.generation_output",
                "dependencies": ["base_tools"],
            },
            {
                "name": "regression_output",
                "path": "ai.regression_output",
                "dependencies": ["base_tools"],
            },
            {
                "name": "output_layer",
                "path": "ai.output_layer",
                "dependencies": ["base_tools"],
            },
        ]

        # Módulos de transformadores y modelos
        model_modules = [
            {
                "name": "transformer_block",
                "path": "ai.transformer_block",
                "dependencies": ["base_tools"],
            },
            {
                "name": "multi_head_attention",
                "path": "ai.multi_head_attention",
                "dependencies": ["base_tools"],
            },
            {
                "name": "positional_encoding",
                "path": "ai.positional_encoding",
                "dependencies": ["base_tools"],
            },
            {
                "name": "neural_models",
                "path": "ai.neural_models",
                "dependencies": ["base_tools"],
            },
            {
                "name": "compact_models",
                "path": "ai.compact_models",
                "dependencies": ["base_tools"],
            },
        ]

        # Módulos de monitoreo y auditoría
        monitoring_modules = [
            {
                "name": "advanced_monitoring_system",
                "path": "ai.advanced_monitoring_system",
                "dependencies": ["base_tools"],
            },
            {
                "name": "advanced_tensor_metrics",
                "path": "ai.advanced_tensor_metrics",
                "dependencies": ["base_tools"],
            },
            {
                "name": "audit_logger",
                "path": "ai.audit_logger",
                "dependencies": ["base_tools"],
            },
            {
                "name": "security_dashboard",
                "path": "ai.security_dashboard",
                "dependencies": ["base_tools"],
            },
            {
                "name": "security_orchestrator",
                "path": "ai.security_orchestrator",
                "dependencies": ["base_tools"],
            },
            {
                "name": "dashboard_resultados",
                "path": "ai.dashboard_resultados",
                "dependencies": ["base_tools"],
            },
        ]

        # Módulos de validación y semántica
        validation_modules = [
            {
                "name": "semantic_validator",
                "path": "ai.semantic_validator",
                "dependencies": ["base_tools"],
            },
            {
                "name": "prompt_adaptativo",
                "path": "ai.prompt_adaptativo",
                "dependencies": ["base_tools"],
            },
            {
                "name": "refinamiento_semantico",
                "path": "ai.refinamiento_semantico",
                "dependencies": ["base_tools"],
            },
            {
                "name": "generacion_adaptativa",
                "path": "ai.generacion_adaptativa",
                "dependencies": ["base_tools"],
            },
        ]

        # Módulos de fusión e integración
        fusion_modules = [
            {
                "name": "hybrid_fusion",
                "path": "ai.hybrid_fusion",
                "dependencies": ["base_tools"],
            },
            {
                "name": "perfect_integrated_system",
                "path": "ai.perfect_integrated_system",
                "dependencies": ["base_tools"],
            },
            {
                "name": "perfect_dynamic_system",
                "path": "ai.perfect_dynamic_system",
                "dependencies": ["base_tools"],
            },
            {
                "name": "unified_learning_training_system",
                "path": "ai.unified_learning_training_system",
                "dependencies": ["base_tools"],
            },
        ]

        # Módulos de demostración
        demo_modules = [
            {
                "name": "demo_branch_system_analysis",
                "path": "ai.demo_branch_system_analysis",
                "dependencies": ["base_tools"],
            },
            {
                "name": "demo_continuous_learning",
                "path": "ai.demo_continuous_learning",
                "dependencies": ["base_tools"],
            },
            {
                "name": "perfect_embeddings_demo",
                "path": "ai.perfect_embeddings_demo",
                "dependencies": ["perfect_embeddings"],
            },
        ]

        # Módulos de tipos y utilidades
        type_modules = [
            {
                "name": "emotion_types",
                "path": "ai.emotion_types",
                "dependencies": ["base_tools"],
            },
            {
                "name": "identity_management",
                "path": "ai.identity_management",
                "dependencies": ["base_tools"],
            },
        ]

        # Combinar todos los módulos
        all_modules = (
            base_modules
            + embedding_modules
            + ai_modules
            + branch_modules
            + learning_modules
            + memory_modules
            + expert_modules
            + security_modules
            + blockchain_modules
            + evaluation_modules
            + search_modules
            + response_modules
            + data_modules
            + utility_modules
            + analysis_modules
            + emotion_modules
            + improvement_modules
            + component_modules
            + output_modules
            + model_modules
            + monitoring_modules
            + validation_modules
            + fusion_modules
            + demo_modules
            + type_modules
        )

        # Registrar módulos
        for module_info in all_modules:
            module = ModuleInfo(**module_info)
            self.modules[module.name] = module
            self.dependency_graph[module.name] = module.dependencies

    def _build_dependency_graph(self):
        """Construir grafo de dependencias"""
        logger.info("🔗 Construyendo grafo de dependencias...")

        # Verificar dependencias circulares
        for module_name, dependencies in self.dependency_graph.items():
            for dep in dependencies:
                if dep not in self.modules:
                    logger.warning(
                        f"⚠️ Dependencia no encontrada: {dep} para {module_name}"
                    )

    def _calculate_load_order(self):
        """Calcular orden de carga usando ordenamiento topológico"""
        logger.info("📋 Calculando orden de carga...")

        # Ordenamiento topológico
        visited = set()
        temp_visited = set()
        order = []

        def dfs(node):
            if node in temp_visited:
                raise ValueError(f"Dependencia circular detectada: {node}")
            if node in visited:
                return

            temp_visited.add(node)

            for neighbor in self.dependency_graph.get(node, []):
                dfs(neighbor)

            temp_visited.remove(node)
            visited.add(node)
            order.append(node)

        for node in self.dependency_graph:
            if node not in visited:
                dfs(node)

        self.load_order = order

        # Asignar orden de carga a módulos
        for i, module_name in enumerate(order):
            if module_name in self.modules:
                self.modules[module_name].load_order = i

        logger.info(f"✅ Orden de carga calculado: {len(order)} módulos")

    async def load_module(self, module_name: str) -> bool:
        """Cargar un módulo específico"""
        if module_name not in self.modules:
            logger.error(f"❌ Módulo no encontrado: {module_name}")
            return False

        module_info = self.modules[module_name]

        # Verificar si ya está cargado
        if module_name in self.loaded_modules:
            logger.info(f"✅ Módulo {module_name} ya está cargado")
            return True

        # Verificar dependencias
        for dep in module_info.dependencies:
            if dep not in self.loaded_modules:
                logger.info(f"🔄 Cargando dependencia: {dep}")
                if not await self.load_module(dep):
                    return False

        try:
            # Marcar como cargando
            module_info.status = "loading"

            # Importar módulo
            module = importlib.import_module(module_info.path)

            # Guardar módulo cargado
            self.loaded_modules[module_name] = module
            module_info.status = "loaded"
            module_info.load_time = datetime.now()

            logger.info(f"✅ Módulo {module_name} cargado correctamente")
            return True

        except Exception as e:
            module_info.status = "error"
            module_info.error_message = str(e)
            self.errors.append(
                {
                    "module": module_name,
                    "error": str(e),
                    "traceback": traceback.format_exc(),
                    "timestamp": datetime.now(),
                }
            )
            logger.error(f"❌ Error cargando {module_name}: {e}")
            return False

    async def load_all_modules(self) -> bool:
        """Cargar todos los módulos en orden"""
        logger.info("🚀 Cargando todos los módulos...")

        for module_name in self.load_order:
            if not await self.load_module(module_name):
                logger.error(f"❌ Falló la carga de {module_name}")
                return False

        logger.info("✅ Todos los módulos cargados correctamente")
        return True

    def get_module(self, module_name: str) -> Optional[Any]:
        """Obtener un módulo cargado"""
        return self.loaded_modules.get(module_name)

    def get_dependency_report(self) -> Dict[str, Any]:
        """Obtener reporte de dependencias"""
        return {
            "total_modules": len(self.modules),
            "loaded_modules": len(self.loaded_modules),
            "load_order": self.load_order,
            "module_status": {
                name: {
                    "status": module.status,
                    "load_order": module.load_order,
                    "dependencies": module.dependencies,
                    "error": module.error_message,
                }
                for name, module in self.modules.items()
            },
            "errors": len(self.errors),
            "recent_errors": self.errors[-5:] if self.errors else [],
        }

    def get_module_dependencies(self, module_name: str) -> List[str]:
        """Obtener dependencias de un módulo"""
        if module_name in self.modules:
            return self.modules[module_name].dependencies
        return []

    def get_modules_by_dependency(self, dependency: str) -> List[str]:
        """Obtener módulos que dependen de un módulo específico"""
        dependent_modules = []
        for module_name, module_info in self.modules.items():
            if dependency in module_info.dependencies:
                dependent_modules.append(module_name)
        return dependent_modules


# Instancia global del gestor de dependencias
_dependency_manager: Optional[DependencyManager] = None


def get_dependency_manager() -> DependencyManager:
    """Obtener instancia global del gestor de dependencias"""
    global _dependency_manager

    if _dependency_manager is None:
        _dependency_manager = DependencyManager()

    return _dependency_manager


async def main():
    """Función de demostración del gestor de dependencias"""
    print("📦 Gestor de Dependencias de NeuroFusion")
    print("=" * 50)

    manager = get_dependency_manager()

    # Mostrar orden de carga
    print(f"📋 Orden de carga ({len(manager.load_order)} módulos):")
    for i, module_name in enumerate(manager.load_order[:10]):  # Mostrar primeros 10
        print(f"   {i+1}. {module_name}")

    if len(manager.load_order) > 10:
        print(f"   ... y {len(manager.load_order) - 10} módulos más")

    # Cargar módulos críticos
    critical_modules = ["base_tools", "unified_branch_tokenizer", "perfect_embeddings"]
    print(f"\n🚀 Cargando módulos críticos...")

    for module_name in critical_modules:
        success = await manager.load_module(module_name)
        if success:
            print(f"✅ {module_name} cargado")
        else:
            print(f"❌ {module_name} falló")

    # Mostrar reporte
    report = manager.get_dependency_report()
    print(f"\n📊 Reporte de dependencias:")
    print(f"   Módulos totales: {report['total_modules']}")
    print(f"   Módulos cargados: {report['loaded_modules']}")
    print(f"   Errores: {report['errors']}")


if __name__ == "__main__":
    asyncio.run(main())
