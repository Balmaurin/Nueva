"""
Sistema de Módulos Unificado para Sheily AI
===========================================

Este módulo proporciona acceso unificado a todos los componentes del sistema,
incluyendo el sistema de expansión dinámica de ramas que puede generar
cientos de ramas especializadas automáticamente.
"""

import asyncio
import logging
from typing import Dict, Any, Optional, List
from dataclasses import dataclass, field
from datetime import datetime
import importlib
import inspect

# Configuración de logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@dataclass
class ModuleInfo:
    """Información de un módulo registrado"""

    name: str
    category: str
    description: str
    class_name: str
    instance: Any
    dependencies: List[str] = field(default_factory=list)
    is_async: bool = False
    status: str = "active"
    last_used: Optional[datetime] = None


class ModuleRegistry:
    """Registro central de todos los módulos del sistema"""

    def __init__(self):
        self.modules: Dict[str, ModuleInfo] = {}
        self.categories: Dict[str, List[str]] = {}
        self.initialized = False

    def register_module(
        self,
        name: str,
        category: str,
        description: str,
        instance: Any,
        dependencies: List[str] = None,
        is_async: bool = False,
    ):
        """Registrar un módulo en el sistema"""
        module_info = ModuleInfo(
            name=name,
            category=category,
            description=description,
            class_name=instance.__class__.__name__,
            instance=instance,
            dependencies=dependencies or [],
            is_async=is_async,
        )

        self.modules[name] = module_info

        if category not in self.categories:
            self.categories[category] = []
        self.categories[category].append(name)

        logger.info(f"✅ Módulo registrado: {name} ({category})")

    def get_module(self, name: str) -> Optional[ModuleInfo]:
        """Obtener información de un módulo"""
        return self.modules.get(name)

    def get_modules_by_category(self, category: str) -> List[ModuleInfo]:
        """Obtener todos los módulos de una categoría"""
        module_names = self.categories.get(category, [])
        return [self.modules[name] for name in module_names if name in self.modules]

    def list_all_modules(self) -> Dict[str, List[str]]:
        """Listar todos los módulos por categoría"""
        return self.categories.copy()

    def get_module_instance(self, name: str) -> Any:
        """Obtener la instancia de un módulo"""
        module_info = self.get_module(name)
        if module_info:
            module_info.last_used = datetime.now()
            return module_info.instance
        return None


class UnifiedModuleSystem:
    """Sistema unificado para gestionar todos los módulos"""

    def __init__(self):
        self.registry = ModuleRegistry()
        self.initialized = False

    async def initialize(self):
        """Inicializar todos los módulos del sistema"""
        if self.initialized:
            return

        logger.info("🚀 Inicializando sistema de módulos unificado...")

        # Importar y registrar módulos de IA
        await self._register_ai_modules()

        # Importar y registrar módulos de memoria
        await self._register_memory_modules()

        # Importar y registrar módulos de entrenamiento
        await self._register_training_modules()

        # Importar y registrar módulos de blockchain
        await self._register_blockchain_modules()

        # Importar y registrar módulos de seguridad
        await self._register_security_modules()

        # Importar y registrar módulos de evaluación
        await self._register_evaluation_modules()

        # Importar y registrar módulos de tokens
        await self._register_token_modules()

        # Importar y registrar módulos de recomendaciones
        await self._register_recommendation_modules()

        # Importar y registrar módulos de embeddings
        await self._register_embedding_modules()

        # Importar y registrar módulos de core
        await self._register_core_modules()

        # Importar y registrar módulos de orquestación
        await self._register_orchestrator_modules()

        # Importar y registrar módulos de refuerzo
        await self._register_reinforcement_modules()

        # Importar y registrar módulos de recompensas
        await self._register_rewards_modules()

        # Importar y registrar módulos de adaptadores
        await self._register_adapter_modules()

        # Importar y registrar módulos de plugins
        await self._register_plugin_modules()

        # Importar y registrar módulos de scripts
        await self._register_script_modules()

        # Importar y registrar módulos de utilidades
        await self._register_utils_modules()

        # Importar y registrar módulos de visualización
        await self._register_visualization_modules()

        # Importar y registrar módulos de aprendizaje
        await self._register_learning_modules()

        # Importar y registrar módulos de componentes de IA
        await self._register_ai_components_modules()

        # Importar y registrar módulos de clustering y expansión de dominio
        await self._register_clustering_modules()

        # Importar y registrar módulos unificados
        await self._register_unified_modules()

        self.initialized = True
        logger.info(f"✅ Sistema inicializado con {len(self.registry.modules)} módulos")

    async def _register_ai_modules(self):
        """Registrar módulos de IA"""
        try:
            from .ai.llm_models import LLMModelManager
            from .ai.ml_components import MLModelManager
            from .ai.response_generator import ResponseGenerator
            from .ai.semantic_analyzer import SemanticAnalyzer
            from .ai.text_processor import TextProcessor

            self.registry.register_module(
                "llm_manager",
                "ai",
                "Gestor de modelos de lenguaje",
                LLMModelManager(),
                ["text_processor"],
            )

            self.registry.register_module(
                "ml_manager", "ai", "Gestor de modelos de ML", MLModelManager(), []
            )

            self.registry.register_module(
                "response_generator",
                "ai",
                "Generador de respuestas",
                ResponseGenerator(),
                ["semantic_analyzer"],
            )

            self.registry.register_module(
                "semantic_analyzer",
                "ai",
                "Analizador semántico",
                SemanticAnalyzer(),
                [],
            )

            self.registry.register_module(
                "text_processor", "ai", "Procesador de texto", TextProcessor(), []
            )

        except Exception as e:
            logger.error(f"❌ Error registrando módulos de IA: {e}")

    async def _register_memory_modules(self):
        """Registrar módulos de memoria"""
        try:
            from .memory.data_management import DataManagementService
            from .memory.intelligent_backup_system import IntelligentBackupSystem
            from .memory.rag import RAGRetriever
            from .memory.short_term import ShortTermMemory

            self.registry.register_module(
                "data_management",
                "memory",
                "Servicio de gestión de datos",
                DataManagementService(),
                [],
            )

            self.registry.register_module(
                "backup_system",
                "memory",
                "Sistema de respaldo inteligente",
                IntelligentBackupSystem(),
                ["rag_retriever"],
            )

            self.registry.register_module(
                "rag_retriever",
                "memory",
                "Sistema RAG para recuperación",
                RAGRetriever(),
                [],
            )

            self.registry.register_module(
                "short_term_memory",
                "memory",
                "Memoria a corto plazo",
                ShortTermMemory(),
                [],
            )

        except Exception as e:
            logger.error(f"❌ Error registrando módulos de memoria: {e}")

    async def _register_training_modules(self):
        """Registrar módulos de entrenamiento"""
        try:
            from .training.advanced_training_system import AdvancedTrainingSystem
            from .training.automatic_lora_trainer import AutomaticLoRATrainer

            self.registry.register_module(
                "advanced_training",
                "training",
                "Sistema de entrenamiento avanzado",
                AdvancedTrainingSystem(),
                [],
            )

            self.registry.register_module(
                "lora_trainer",
                "training",
                "Entrenador automático LoRA",
                AutomaticLoRATrainer(),
                [],
            )

        except Exception as e:
            logger.error(f"❌ Error registrando módulos de entrenamiento: {e}")

    async def _register_blockchain_modules(self):
        """Registrar módulos de blockchain"""
        try:
            from .blockchain.rate_limiter import RateLimiter
            from .blockchain.secure_key_management import SecureKeyManagement
            from .blockchain.sheily_spl_manager import SheilySPLManager
            from .blockchain.sheily_spl_real import SheilySPLReal
            from .blockchain.sheily_token_manager import SheilyTokenManager
            from .blockchain.solana_blockchain_real import SolanaBlockchainReal
            from .blockchain.spl_data_persistence import SPLDataPersistence
            from .blockchain.transaction_monitor import TransactionMonitor

            self.registry.register_module(
                "rate_limiter", "blockchain", "Limitador de tasa", RateLimiter(), []
            )

            self.registry.register_module(
                "key_management",
                "blockchain",
                "Gestión segura de claves",
                SecureKeyManagement(),
                [],
            )

            self.registry.register_module(
                "spl_manager", "blockchain", "Gestor SPL", SheilySPLManager(), []
            )

            self.registry.register_module(
                "spl_real", "blockchain", "SPL real", SheilySPLReal(), []
            )

            self.registry.register_module(
                "token_manager",
                "blockchain",
                "Gestor de tokens",
                SheilyTokenManager(),
                [],
            )

            self.registry.register_module(
                "solana_blockchain",
                "blockchain",
                "Blockchain Solana",
                SolanaBlockchainReal(),
                [],
            )

            self.registry.register_module(
                "spl_persistence",
                "blockchain",
                "Persistencia SPL",
                SPLDataPersistence(),
                [],
            )

            self.registry.register_module(
                "transaction_monitor",
                "blockchain",
                "Monitor de transacciones",
                TransactionMonitor(),
                [],
            )

        except Exception as e:
            logger.error(f"❌ Error registrando módulos de blockchain: {e}")

    async def _register_security_modules(self):
        """Registrar módulos de seguridad"""
        try:
            from .security.neurofusion_unified_core import NeuroFusionUnifiedCore
            from .security.neurofusion_unified_launcher import NeuroFusionLauncher

            self.registry.register_module(
                "unified_core",
                "security",
                "Núcleo unificado de seguridad",
                NeuroFusionUnifiedCore(),
                [],
            )

            self.registry.register_module(
                "unified_launcher",
                "security",
                "Lanzador unificado",
                NeuroFusionLauncher(),
                [],
            )

        except Exception as e:
            logger.error(f"❌ Error registrando módulos de seguridad: {e}")

    async def _register_evaluation_modules(self):
        """Registrar módulos de evaluación"""
        try:
            from .evaluation.model_validator import ModelValidator
            from .evaluation.performance_metrics import (
                PerformanceMonitor,
                MetricsCalculator,
            )
            from .evaluation.quality_evaluator import (
                DataQualityEvaluator,
                ModelQualityEvaluator,
            )
            from .evaluation.result_analyzer import ResultAnalyzer

            self.registry.register_module(
                "model_validator",
                "evaluation",
                "Validador de modelos",
                ModelValidator(),
                [],
            )

            self.registry.register_module(
                "performance_monitor",
                "evaluation",
                "Monitor de rendimiento",
                PerformanceMonitor(),
                [],
            )

            self.registry.register_module(
                "metrics_calculator",
                "evaluation",
                "Calculador de métricas",
                MetricsCalculator(),
                [],
            )

            self.registry.register_module(
                "data_quality_evaluator",
                "evaluation",
                "Evaluador de calidad de datos",
                DataQualityEvaluator(),
                [],
            )

            self.registry.register_module(
                "model_quality_evaluator",
                "evaluation",
                "Evaluador de calidad de modelos",
                ModelQualityEvaluator(),
                [],
            )

            self.registry.register_module(
                "result_analyzer",
                "evaluation",
                "Analizador de resultados",
                ResultAnalyzer(),
                [],
            )

        except Exception as e:
            logger.error(f"❌ Error registrando módulos de evaluación: {e}")

    async def _register_token_modules(self):
        """Registrar módulos de tokens"""
        try:
            from .tokens.advanced_sheily_token_system import AdvancedSheilyTokenSystem
            from .tokens.sheily_token_manager import SheilyTokenManager
            from .tokens.sheily_tokens_system import SheilyTokensSystem
            from .tokens.unified_sheily_token_system import UnifiedSheilyTokenSystem

            self.registry.register_module(
                "advanced_token_system",
                "tokens",
                "Sistema avanzado de tokens",
                AdvancedSheilyTokenSystem(),
                [],
            )

            self.registry.register_module(
                "token_manager", "tokens", "Gestor de tokens", SheilyTokenManager(), []
            )

            self.registry.register_module(
                "tokens_system",
                "tokens",
                "Sistema de tokens",
                SheilyTokensSystem({}),
                [],
            )

            self.registry.register_module(
                "unified_token_system",
                "tokens",
                "Sistema unificado de tokens",
                UnifiedSheilyTokenSystem(),
                [],
            )

        except Exception as e:
            logger.error(f"❌ Error registrando módulos de tokens: {e}")

    async def _register_recommendation_modules(self):
        """Registrar módulos de recomendaciones"""
        try:
            from .recommendations.personalized_recommendations import (
                PersonalizedRecommendations,
            )

            self.registry.register_module(
                "personalized_recommendations",
                "recommendations",
                "Recomendaciones personalizadas",
                PersonalizedRecommendations(),
                [],
            )

        except Exception as e:
            logger.error(f"❌ Error registrando módulos de recomendaciones: {e}")

    async def _register_embedding_modules(self):
        """Registrar módulos de embeddings"""
        try:
            from .embeddings.embedding_performance_monitor import (
                EmbeddingPerformanceMonitor,
            )
            from .embeddings.semantic_search_engine import SemanticSearchEngine

            self.registry.register_module(
                "embedding_monitor",
                "embeddings",
                "Monitor de rendimiento de embeddings",
                EmbeddingPerformanceMonitor("default"),
                [],
            )

            self.registry.register_module(
                "semantic_search",
                "embeddings",
                "Motor de búsqueda semántica",
                SemanticSearchEngine(),
                [],
            )

        except Exception as e:
            logger.error(f"❌ Error registrando módulos de embeddings: {e}")

    async def _register_core_modules(self):
        """Registrar módulos del núcleo"""
        try:
            from .core.advanced_system_integrator import AdvancedSystemIntegrator
            from .core.cognitive_understanding_module import (
                CognitiveUnderstandingModule,
            )
            from .core.continuous_improvement import ContinuousImprovement
            from .core.daily_exercise_generator import DailyExerciseGenerator
            from .core.daily_exercise_integrator import DailyExerciseIntegrator
            from .core.dynamic_knowledge_generator import DynamicKnowledgeGenerator
            from .core.enhanced_daily_exercise_generator import (
                EnhancedDailyExerciseGenerator,
            )
            from .core.enhanced_daily_exercise_integrator import (
                EnhancedDailyExerciseIntegrator,
            )
            from .core.integration_manager import IntegrationManager
            from .core.neurofusion_compatibility_validator import (
                NeuroFusionCompatibilitySystem,
            )
            from .core.neurofusion_core import NeuroFusionCore
            from .core.semantic_adaptation_manager import SemanticAdaptationManager

            self.registry.register_module(
                "system_integrator",
                "core",
                "Integrador de sistema avanzado",
                AdvancedSystemIntegrator(),
                [],
            )

            self.registry.register_module(
                "cognitive_understanding",
                "core",
                "Módulo de comprensión cognitiva",
                CognitiveUnderstandingModule(),
                [],
            )

            self.registry.register_module(
                "continuous_improvement",
                "core",
                "Mejora continua",
                ContinuousImprovement(),
                [],
            )

            self.registry.register_module(
                "daily_exercise_generator",
                "core",
                "Generador de ejercicios diarios",
                DailyExerciseGenerator(),
                [],
            )

            self.registry.register_module(
                "daily_exercise_integrator",
                "core",
                "Integrador de ejercicios diarios",
                DailyExerciseIntegrator(),
                [],
            )

            self.registry.register_module(
                "knowledge_generator",
                "core",
                "Generador de conocimiento dinámico",
                DynamicKnowledgeGenerator(),
                [],
            )

            self.registry.register_module(
                "enhanced_exercise_generator",
                "core",
                "Generador mejorado de ejercicios",
                EnhancedDailyExerciseGenerator(),
                [],
            )

            self.registry.register_module(
                "enhanced_exercise_integrator",
                "core",
                "Integrador mejorado de ejercicios",
                EnhancedDailyExerciseIntegrator(),
                [],
            )

            self.registry.register_module(
                "integration_manager",
                "core",
                "Gestor de integración",
                IntegrationManager(),
                [],
            )

            self.registry.register_module(
                "compatibility_validator",
                "core",
                "Validador de compatibilidad",
                NeuroFusionCompatibilitySystem(),
                [],
            )

            self.registry.register_module(
                "neurofusion_core",
                "core",
                "Núcleo de NeuroFusion",
                NeuroFusionCore(),
                [],
            )

            self.registry.register_module(
                "semantic_adaptation",
                "core",
                "Gestor de adaptación semántica",
                SemanticAdaptationManager(),
                [],
            )

        except Exception as e:
            logger.error(f"❌ Error registrando módulos del núcleo: {e}")

    async def _register_orchestrator_modules(self):
        """Registrar módulos de orquestación"""
        try:
            from .orchestrator.domain_classifier import DomainClassifier
            from .orchestrator.router import SemanticRouter

            self.registry.register_module(
                "domain_classifier",
                "orchestrator",
                "Clasificador de dominios",
                DomainClassifier(),
                [],
            )

            # Router necesita dependencias específicas
            self.registry.register_module(
                "semantic_router",
                "orchestrator",
                "Router semántico",
                None,
                ["domain_classifier", "semantic_analyzer"],
            )

        except Exception as e:
            logger.error(f"❌ Error registrando módulos de orquestación: {e}")

    async def _register_reinforcement_modules(self):
        """Registrar módulos de refuerzo"""
        try:
            from .reinforcement.adaptive_learning_agent import AdaptiveLearningAgent

            self.registry.register_module(
                "adaptive_learning_agent",
                "reinforcement",
                "Agente de aprendizaje adaptativo",
                AdaptiveLearningAgent(None, None),
                [],
            )

        except Exception as e:
            logger.error(f"❌ Error registrando módulos de refuerzo: {e}")

    async def _register_rewards_modules(self):
        """Registrar módulos de recompensas"""
        try:
            from .rewards.adaptive_rewards import AdaptiveRewardsOptimizer
            from .rewards.advanced_optimization import AdvancedRewardsOptimizer
            from .rewards.contextual_accuracy import ContextualAccuracyEvaluator
            from .rewards.integration_example import SheilyRewardsIntegration
            from .rewards.reward_system import SheilyRewardSystem
            from .rewards.tracker import SessionTracker

            self.registry.register_module(
                "adaptive_rewards",
                "rewards",
                "Optimizador de recompensas adaptativo",
                AdaptiveRewardsOptimizer(),
                [],
            )

            self.registry.register_module(
                "advanced_optimization",
                "rewards",
                "Optimización avanzada",
                AdvancedRewardsOptimizer(),
                [],
            )

            self.registry.register_module(
                "contextual_accuracy",
                "rewards",
                "Evaluador de precisión contextual",
                ContextualAccuracyEvaluator(),
                [],
            )

            self.registry.register_module(
                "rewards_integration",
                "rewards",
                "Integración de recompensas",
                SheilyRewardsIntegration(),
                [],
            )

            self.registry.register_module(
                "reward_system",
                "rewards",
                "Sistema de recompensas",
                SheilyRewardSystem(),
                [],
            )

            self.registry.register_module(
                "session_tracker",
                "rewards",
                "Rastreador de sesiones",
                SessionTracker(),
                [],
            )

        except Exception as e:
            logger.error(f"❌ Error registrando módulos de recompensas: {e}")

    async def _register_adapter_modules(self):
        """Registrar módulos de adaptadores"""
        try:
            from .adapters.compatibility_adapter import CompatibilityAdapter
            from .adapters.neurofusion_migration_toolkit import (
                ComponentMigrationRegistry,
                ComponentTransformer,
            )

            self.registry.register_module(
                "compatibility_adapter",
                "adapters",
                "Adaptador de compatibilidad",
                CompatibilityAdapter(),
                [],
            )

            self.registry.register_module(
                "migration_registry",
                "adapters",
                "Registro de migración",
                ComponentMigrationRegistry(),
                [],
            )

            self.registry.register_module(
                "component_transformer",
                "adapters",
                "Transformador de componentes",
                ComponentTransformer(),
                [],
            )

        except Exception as e:
            logger.error(f"❌ Error registrando módulos de adaptadores: {e}")

    async def _register_plugin_modules(self):
        """Registrar módulos de plugins"""
        try:
            from .plugins.logging_plugin import LoggingPlugin

            self.registry.register_module(
                "logging_plugin", "plugins", "Plugin de logging", LoggingPlugin(), []
            )

        except Exception as e:
            logger.error(f"❌ Error registrando módulos de plugins: {e}")

    async def _register_script_modules(self):
        """Registrar módulos de scripts"""
        try:
            from .scripts.audit import SheilyAudit
            from .scripts.data_curation import DataCurator
            from .scripts.dependency_manager import DependencyManager
            from .scripts.download_branch_datasets import BranchDatasetDownloader
            from .scripts.download_datasets import DatasetDownloader
            from .scripts.download_models import download_sentence_transformers
            from .scripts.env_manager import EnvManager
            from .scripts.integrate_llm_with_server import LLMIntegrationManager
            from .scripts.layer_manager import LayerManager
            from .scripts.load_local_llm import LocalLLMLoader
            from .scripts.prepare_training_datasets import TrainingDatasetPreparation
            from .scripts.restore_branch_structure import BranchStructureRestorer
            from .scripts.security_audit import SecurityAuditor
            from .scripts.select_micro_branches import select_representative_branches
            from .scripts.slack_notification import (
                generate_slack_message,
                send_slack_message,
            )
            from .scripts.train_branch_adapters import BranchAdapterTrainer
            from .scripts.version_manager import VersionManager

            self.registry.register_module(
                "audit", "scripts", "Auditoría del sistema", SheilyAudit(), []
            )

            self.registry.register_module(
                "data_curator", "scripts", "Curador de datos", DataCurator(), []
            )

            self.registry.register_module(
                "dependency_manager",
                "scripts",
                "Gestor de dependencias",
                DependencyManager(),
                [],
            )

            self.registry.register_module(
                "branch_dataset_downloader",
                "scripts",
                "Descargador de datasets de ramas",
                BranchDatasetDownloader(),
                [],
            )

            self.registry.register_module(
                "dataset_downloader",
                "scripts",
                "Descargador de datasets",
                DatasetDownloader(),
                [],
            )

            self.registry.register_module(
                "env_manager", "scripts", "Gestor de entorno", EnvManager(), []
            )

            self.registry.register_module(
                "llm_integration_manager",
                "scripts",
                "Gestor de integración LLM",
                LLMIntegrationManager(),
                [],
            )

            self.registry.register_module(
                "layer_manager", "scripts", "Gestor de capas", LayerManager(), []
            )

            self.registry.register_module(
                "local_llm_loader",
                "scripts",
                "Cargador de LLM local",
                LocalLLMLoader(),
                [],
            )

            self.registry.register_module(
                "training_dataset_preparation",
                "scripts",
                "Preparación de datasets de entrenamiento",
                TrainingDatasetPreparation(),
                [],
            )

            self.registry.register_module(
                "branch_structure_restorer",
                "scripts",
                "Restaurador de estructura de ramas",
                BranchStructureRestorer(),
                [],
            )

            self.registry.register_module(
                "security_auditor",
                "scripts",
                "Auditor de seguridad",
                SecurityAuditor("http://localhost"),
                [],
            )

            self.registry.register_module(
                "branch_adapter_trainer",
                "scripts",
                "Entrenador de adaptadores de ramas",
                BranchAdapterTrainer(),
                [],
            )

            self.registry.register_module(
                "version_manager",
                "scripts",
                "Gestor de versiones",
                VersionManager(),
                [],
            )

        except Exception as e:
            logger.error(f"❌ Error registrando módulos de scripts: {e}")

    async def _register_utils_modules(self):
        """Registrar módulos de utilidades"""
        try:
            # Los módulos de utils son principalmente archivos de configuración
            # y funciones auxiliares, no necesitan instanciación
            pass

        except Exception as e:
            logger.error(f"❌ Error registrando módulos de utilidades: {e}")

    async def _register_visualization_modules(self):
        """Registrar módulos de visualización"""
        try:
            from .visualization.insights_dashboard import main as insights_dashboard

            self.registry.register_module(
                "insights_dashboard", "visualization", "Dashboard de insights", None, []
            )

        except Exception as e:
            logger.error(f"❌ Error registrando módulos de visualización: {e}")

    async def _register_learning_modules(self):
        """Registrar módulos de aprendizaje"""
        try:
            from .learning.neural_plasticity_manager import NeuralPlasticityManager

            self.registry.register_module(
                "neural_plasticity",
                "learning",
                "Gestor de plasticidad neural",
                NeuralPlasticityManager(),
                [],
            )

        except Exception as e:
            logger.error(f"❌ Error registrando módulos de aprendizaje: {e}")

    async def _register_ai_components_modules(self):
        """Registrar módulos de componentes de IA"""
        try:
            from .ai_components.advanced_ai_system import AdvancedAISystem
            from .ai_components.advanced_algorithm_refinement import (
                AlgorithmRefinementEngine,
            )
            from .ai_components.advanced_contextual_reasoning import (
                ContextualReasoningEngine,
            )
            from .ai_components.advanced_module_enhancer import AdvancedModuleEnhancer
            from .ai_components.module_enhancer import ModuleEnhancer
            from .ai_components.neurofusion_component_adapters import (
                MLModelAdapter,
                NLPComponentAdapter,
                EmbeddingAdapter,
            )

            self.registry.register_module(
                "advanced_ai_system",
                "ai_components",
                "Sistema de IA avanzado",
                AdvancedAISystem(),
                [],
            )

            self.registry.register_module(
                "algorithm_refinement",
                "ai_components",
                "Motor de refinamiento de algoritmos",
                AlgorithmRefinementEngine(),
                [],
            )

            self.registry.register_module(
                "contextual_reasoning",
                "ai_components",
                "Motor de razonamiento contextual",
                ContextualReasoningEngine(),
                [],
            )

            self.registry.register_module(
                "advanced_module_enhancer",
                "ai_components",
                "Mejorador avanzado de módulos",
                AdvancedModuleEnhancer(),
                [],
            )

            self.registry.register_module(
                "module_enhancer",
                "ai_components",
                "Mejorador de módulos",
                ModuleEnhancer(),
                [],
            )

            self.registry.register_module(
                "ml_model_adapter",
                "ai_components",
                "Adaptador de modelos ML",
                MLModelAdapter(),
                [],
            )

            self.registry.register_module(
                "nlp_component_adapter",
                "ai_components",
                "Adaptador de componentes NLP",
                NLPComponentAdapter(),
                [],
            )

            self.registry.register_module(
                "embedding_adapter",
                "ai_components",
                "Adaptador de embeddings",
                EmbeddingAdapter(),
                [],
            )

        except Exception as e:
            logger.error(f"❌ Error registrando módulos de componentes de IA: {e}")

    async def _register_clustering_modules(self):
        """Registrar módulos de clustering y expansión de dominio"""
        try:
            from .src.advanced_clustering.domain_adapter_optimizer import (
                DomainAdapterOptimizer,
            )
            from .src.advanced_clustering.domain_expansion import DomainExpansionEngine
            from .src.advanced_clustering.semantic_clustering import (
                AdvancedSemanticClustering,
            )

            self.registry.register_module(
                "domain_adapter_optimizer",
                "clustering",
                "Optimizador de adaptadores de dominio",
                DomainAdapterOptimizer(),
                [],
            )

            self.registry.register_module(
                "domain_expansion",
                "clustering",
                "Motor de expansión de dominio",
                DomainExpansionEngine(),
                [],
            )

            self.registry.register_module(
                "semantic_clustering",
                "clustering",
                "Clustering semántico avanzado",
                AdvancedSemanticClustering(),
                [],
            )

        except Exception as e:
            logger.error(f"❌ Error registrando módulos de clustering: {e}")

    async def _register_unified_modules(self):
        """Registrar módulos unificados"""
        try:
            # Los módulos unificados son principalmente archivos de configuración
            # y sistemas de alto nivel
            pass

        except Exception as e:
            logger.error(f"❌ Error registrando módulos unificados: {e}")

    def get_module(self, name: str) -> Any:
        """Obtener un módulo por nombre"""
        return self.registry.get_module_instance(name)

    def list_modules(self, category: str = None) -> Dict[str, Any]:
        """Listar módulos disponibles"""
        if category:
            modules = self.registry.get_modules_by_category(category)
            return {
                m.name: {
                    "description": m.description,
                    "class": m.class_name,
                    "status": m.status,
                    "is_async": m.is_async,
                }
                for m in modules
            }
        else:
            return self.registry.list_all_modules()

    def get_module_info(self, name: str) -> Optional[Dict[str, Any]]:
        """Obtener información detallada de un módulo"""
        module_info = self.registry.get_module(name)
        if module_info:
            return {
                "name": module_info.name,
                "category": module_info.category,
                "description": module_info.description,
                "class": module_info.class_name,
                "dependencies": module_info.dependencies,
                "is_async": module_info.is_async,
                "status": module_info.status,
                "last_used": module_info.last_used,
            }
        return None

    async def execute_module_function(
        self, module_name: str, function_name: str, *args, **kwargs
    ):
        """Ejecutar una función de un módulo específico"""
        module = self.get_module(module_name)
        if not module:
            raise ValueError(f"Módulo '{module_name}' no encontrado")

        if not hasattr(module, function_name):
            raise ValueError(
                f"Función '{function_name}' no encontrada en módulo '{module_name}'"
            )

        func = getattr(module, function_name)

        if asyncio.iscoroutinefunction(func):
            return await func(*args, **kwargs)
        else:
            return func(*args, **kwargs)


# Instancia global del sistema
unified_system = UnifiedModuleSystem()


# Funciones de conveniencia para acceso directo
async def initialize_modules():
    """Inicializar todos los módulos"""
    await unified_system.initialize()


def get_module(name: str) -> Any:
    """Obtener un módulo por nombre"""
    return unified_system.get_module(name)


def list_modules(category: str = None) -> Dict[str, Any]:
    """Listar módulos disponibles"""
    return unified_system.list_modules(category)


def get_module_info(name: str) -> Optional[Dict[str, Any]]:
    """Obtener información de un módulo"""
    return unified_system.get_module_info(name)


async def execute_module_function(
    module_name: str, function_name: str, *args, **kwargs
):
    """Ejecutar una función de un módulo"""
    return await unified_system.execute_module_function(
        module_name, function_name, *args, **kwargs
    )


# Exportar las clases principales para uso directo
__all__ = [
    "UnifiedModuleSystem",
    "ModuleRegistry",
    "ModuleInfo",
    "unified_system",
    "initialize_modules",
    "get_module",
    "list_modules",
    "get_module_info",
    "execute_module_function",
]
