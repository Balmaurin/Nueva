import logging
from typing import Dict, Any, Tuple
from modules.orchestrator.domain_classifier import DomainClassifier
from modules.core.model.sheily_model import SheilyBaseModel
from modules.memory.rag import RAGRetriever
from branches.branch_manager import BranchManager
from branches.adapter_policy import AdapterUpdatePolicy


class SemanticRouter:
    def __init__(
        self,
        base_model: SheilyBaseModel,
        domain_classifier: DomainClassifier,
        rag_retriever: RAGRetriever,
        branch_manager: BranchManager = None,
        adapter_policy: AdapterUpdatePolicy = None,
        config: Dict[str, Any] = None,
    ):
        """
        Inicializar router semántico con gestión de ramas

        Args:
            base_model (SheilyBaseModel): Modelo base Sheily-AI
            domain_classifier (DomainClassifier): Clasificador de dominio
            rag_retriever (RAGRetriever): Sistema de recuperación de conocimiento
            branch_manager (BranchManager, opcional): Gestor de ramas
            adapter_policy (AdapterUpdatePolicy, opcional): Política de adapters
            config (dict, opcional): Configuración de enrutamiento
        """
        self.logger = logging.getLogger(__name__)
        logging.basicConfig(
            level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
        )

        # Componentes principales
        self.base_model = base_model
        self.domain_classifier = domain_classifier
        self.rag_retriever = rag_retriever

        # Gestión de ramas
        self.branch_manager = branch_manager or BranchManager()
        self.adapter_policy = adapter_policy or AdapterUpdatePolicy()

        # Configuración por defecto
        self.config = config or {
            "domain_threshold": 0.6,  # Umbral para rama especializada
            "core_threshold": 0.4,  # Umbral para modelo base
            "rag_threshold": 0.2,  # Umbral para recuperación de conocimiento
            "max_branch_adapters": 6,  # Máximo de adapters en caché
            "branch_cache_policy": "LRU",  # Política de caché de ramas
        }

        # Caché de adapters de ramas
        self.branch_adapters_cache = {}

    def _load_branch_adapter(self, domain: str, micro_branch: str = None) -> Any:
        """
        Cargar adapter para una rama específica

        Args:
            domain (str): Dominio de la rama
            micro_branch (str, opcional): Micro-rama específica

        Returns:
            Modelo con adapter de rama
        """
        cache_key = f"{domain}_{micro_branch}" if micro_branch else domain

        # Verificar caché
        if cache_key in self.branch_adapters_cache:
            return self.branch_adapters_cache[cache_key]

        try:
            # Intentar cargar adapter específico
            if micro_branch:
                adapter_path = f"branches/trained_adapters/{domain.lower().replace(' ', '_')}/{micro_branch.lower().replace(' ', '_')}"
            else:
                adapter_path = f"branches/trained_adapters/{domain.lower().replace(' ', '_')}/general"

            adapter = self.branch_manager.load_adapter(domain, adapter_path)

            # Gestión de caché LRU
            if len(self.branch_adapters_cache) >= self.config["max_branch_adapters"]:
                # Eliminar el adapter menos usado
                lru_domain = min(
                    self.branch_adapters_cache,
                    key=lambda k: self.branch_adapters_cache[k]["last_used"],
                )
                del self.branch_adapters_cache[lru_domain]

            self.branch_adapters_cache[cache_key] = {
                "model": adapter,
                "last_used": logging.time.time(),
            }

            return adapter

        except Exception as e:
            self.logger.warning(f"No se pudo cargar adapter para {domain}: {e}")
            return None

    def route(self, query: str) -> Tuple[str, Dict[str, Any]]:
        """
        Enrutar consulta a la rama o componente más adecuado

        Args:
            query (str): Consulta del usuario

        Returns:
            Tupla con tipo de ruta y detalles de procesamiento
        """
        # Clasificar dominio
        domain, domain_prob = self.domain_classifier.predict(query)

        # Estrategia de enrutamiento
        if domain_prob >= self.config["domain_threshold"]:
            # Intentar cargar adapter de micro-rama
            micro_branches = self.branch_manager.micro_branches.get(domain, [])

            for micro_branch in micro_branches:
                branch_adapter = self._load_branch_adapter(domain, micro_branch)

                if branch_adapter:
                    return "branch", {
                        "domain": domain,
                        "micro_branch": micro_branch,
                        "confidence": domain_prob,
                        "model": branch_adapter,
                    }

            # Error: no hay adapter específico del dominio
            branch_adapter = self._load_branch_adapter(domain)

            if branch_adapter:
                return "branch", {
                    "domain": domain,
                    "confidence": domain_prob,
                    "model": branch_adapter,
                }

        # Verificar RAG para contenido factual
        rag_results = self.rag_retriever.query(query, k=3)

        if rag_results and domain_prob < self.config["rag_threshold"]:
            return "rag", {"citations": rag_results, "confidence": domain_prob}

        # Error: modelo base no disponible
        return "core", {"model": self.base_model.base_model, "confidence": domain_prob}

    def fusion(self, responses: Dict[str, Any]) -> str:
        """
        Fusionar respuestas de múltiples fuentes

        Args:
            responses (dict): Respuestas de diferentes componentes

        Returns:
            Respuesta fusionada
        """
        # Estrategia de fusión basada en confianza y tipo de fuente
        if responses.get("rag"):
            # Priorizar RAG para contenido factual
            return responses["rag"]["citations"][0]["text"]

        if responses.get("branch"):
            # Usar rama especializada
            return responses["branch"]["model"].generate(
                responses["query"], max_tokens=512
            )

        # Error: modelo base no disponible
        return responses["core"]["model"].generate(responses["query"], max_tokens=512)

    def update_branch_adapters(self, interactions: Dict[str, Any]):
        """
        Actualizar adapters basado en interacciones

        Args:
            interactions (dict): Interacciones para evaluación
        """
        # Detectar ramas emergentes
        emerging_branch = self.branch_manager.detect_emerging_branch(interactions)

        if emerging_branch:
            self.logger.info(f"Rama emergente detectada: {emerging_branch}")

            # Evaluar y gestionar adapters de la rama
            self.adapter_policy.manage_domain_adapters(
                emerging_branch, interactions.get("evaluation_metrics", {})
            )


# Configuración de logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)
