import os
import importlib
import logging
import json
from typing import Dict, Any, List, Optional, Type

# Importar validador de módulos
from .module_validator import ModuleValidator, ModuleHealthStatus


class ModuleInitializationError(Exception):
    """Excepción para errores de inicialización de módulos"""

    pass


class ModuleInitializationConfig:
    """
    Configuración de inicialización de módulos

    Permite definir parámetros de inicialización, dependencias
    y requisitos para cada módulo
    """

    def __init__(
        self, config_path: str = "shaili_ai/config/config/module_initialization.json"
    ):
        """
        Inicializar configuración de módulos

        Args:
            config_path (str): Ruta al archivo de configuración
        """
        self.logger = logging.getLogger(__name__)
        self.config_path = config_path
        self.module_configs: Dict[str, Dict[str, Any]] = {}

        # Cargar configuración
        self._load_configuration()

    def _load_configuration(self):
        """Cargar configuración de módulos desde archivo JSON"""
        try:
            if os.path.exists(self.config_path):
                with open(self.config_path, "r", encoding="utf-8") as f:
                    self.module_configs = json.load(f)
                self.logger.info(
                    f"Configuración de módulos cargada desde {self.config_path}"
                )
            else:
                self.logger.warning(
                    f"Archivo de configuración no encontrado: {self.config_path}"
                )
        except Exception as e:
            self.logger.error(f"Error cargando configuración de módulos: {e}")

    def get_module_config(self, module_name: str) -> Dict[str, Any]:
        """
        Obtener configuración para un módulo específico

        Args:
            module_name (str): Nombre del módulo

        Returns:
            Configuración del módulo
        """
        return self.module_configs.get(module_name, {})

    def validate_module_dependencies(
        self, module_name: str, available_modules: List[str]
    ) -> bool:
        """
        Validar dependencias de un módulo

        Args:
            module_name (str): Nombre del módulo
            available_modules (List[str]): Módulos disponibles

        Returns:
            True si todas las dependencias están disponibles, False en otro caso
        """
        module_config = self.get_module_config(module_name)
        dependencies = module_config.get("dependencies", [])

        for dependency in dependencies:
            if dependency not in available_modules:
                self.logger.warning(
                    f"Dependencia faltante para {module_name}: {dependency}"
                )
                return False

        return True


class ModuleInitializer:
    """
    Sistema de inicialización de módulos para NeuroFusion

    Características:
    - Descubrimiento de módulos
    - Validación de dependencias
    - Inicialización configurable
    - Manejo de errores
    - Validación de módulos
    """

    def __init__(
        self,
        base_path: str = "modules",
        config_path: str = "shaili_ai/config/config/module_initialization.json",
    ):
        """
        Inicializar sistema de inicialización de módulos

        Args:
            base_path (str): Ruta base para descubrir módulos
            config_path (str): Ruta al archivo de configuración
        """
        self.base_path = base_path
        self.logger = logging.getLogger(__name__)
        self.config_manager = ModuleInitializationConfig(config_path)

        # Registro de módulos
        self.discovered_modules: Dict[str, Type] = {}
        self.initialized_modules: Dict[str, Any] = {}
        self.initialization_order: List[str] = []

        # Validador de módulos
        self.module_validator = ModuleValidator()

        # Estrategias de recuperación de módulos
        self._register_recovery_strategies()

    def _register_recovery_strategies(self):
        """
        Registrar estrategias de recuperación de módulos
        """

        def missing_method_recovery(module, context):
            """
            Estrategia de recuperación para métodos faltantes

            Args:
                module (Any): Módulo a recuperar
                context (Dict): Contexto de recuperación

            Returns:
                Módulo recuperado o None
            """
            if "método requerido" in context["error"]:
                # Añadir método de procesamiento predeterminado
                def default_process(data):
                    """Método de procesamiento predeterminado"""
                    self.logger.warning(
                        f"Usando método de procesamiento predeterminado para {module.__class__.__name__}"
                    )
                    return data

                module.process = default_process
                return module

            return None

        # Registrar estrategia de recuperación
        self.module_validator.register_recovery_strategy(
            "método requerido", missing_method_recovery
        )

    def discover_modules(self) -> Dict[str, Type]:
        """
        Descubrir módulos disponibles en el sistema

        Returns:
            Diccionario de módulos descubiertos
        """
        self.discovered_modules.clear()

        for root, _, files in os.walk(self.base_path):
            for file in files:
                if file.endswith(".py") and not file.startswith("__"):
                    module_path = os.path.join(root, file)
                    module_name = (
                        os.path.relpath(module_path, self.base_path)
                        .replace("/", ".")
                        .replace(".py", "")
                    )

                    try:
                        module = importlib.import_module(f"modules.{module_name}")

                        # Buscar clases principales (excluir dataclasses y clases de datos)
                        for name, obj in module.__dict__.items():
                            if (
                                isinstance(obj, type)
                                and hasattr(obj, "__module__")
                                and obj.__module__ == module.__name__
                                and not name.startswith(
                                    "Token"
                                )  # Excluir clases de tokens
                                and not hasattr(
                                    obj, "__dataclass_fields__"
                                )  # Excluir dataclasses
                                and not name.endswith(
                                    "Config"
                                )  # Excluir clases de configuración
                                and not name.endswith(
                                    "Wallet"
                                )  # Excluir clases de wallet
                                and not name.endswith(
                                    "Transaction"
                                )  # Excluir clases de transacción
                            ):
                                self.discovered_modules[name] = obj

                    except ImportError as e:
                        self.logger.error(f"Error importando módulo {module_name}: {e}")

        return self.discovered_modules

    def _resolve_initialization_order(self) -> List[str]:
        """
        Resolver orden de inicialización basado en dependencias

        Returns:
            Lista de módulos ordenados para inicialización
        """
        # Implementación simple de resolución de dependencias
        uninitialized = list(self.discovered_modules.keys())
        order = []

        while uninitialized:
            for module_name in uninitialized[:]:
                module_config = self.config_manager.get_module_config(module_name)
                dependencies = module_config.get("dependencies", [])

                # Verificar si todas las dependencias están inicializadas
                if all(dep in order for dep in dependencies):
                    order.append(module_name)
                    uninitialized.remove(module_name)
                    break
            else:
                # Si no se puede resolver, inicializar en orden de descubrimiento
                order.append(uninitialized.pop(0))

        return order

    def initialize_core_modules(self) -> Dict[str, Any]:
        """
        Inicializar módulos centrales del sistema

        Returns:
            Diccionario de módulos centrales inicializados
        """
        core_modules = [
            "neurofusion_core",
            "integration_manager",
            "config_manager",
            "dynamic_knowledge_generator",
            "advanced_ai_system",
        ]

        self.logger.info("Iniciando inicialización de módulos centrales...")

        try:
            # Inicializar módulos centrales específicamente
            core_initialized = self.initialize_modules(module_filter=core_modules)

            self.logger.info(
                f"Módulos centrales inicializados: {len(core_initialized)}"
            )

            return core_initialized

        except Exception as e:
            self.logger.error(f"Error inicializando módulos centrales: {e}")
            raise ModuleInitializationError(
                f"Fallo en inicialización de módulos centrales: {e}"
            )

    def initialize_modules(
        self, module_filter: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """
        Inicializar módulos descubiertos con validación

        Args:
            module_filter (List[str], opcional): Lista de módulos a inicializar

        Returns:
            Diccionario de módulos inicializados
        """
        # Descubrir módulos si no se han descubierto
        if not self.discovered_modules:
            self.discover_modules()

        # Resolver orden de inicialización
        self.initialization_order = self._resolve_initialization_order()

        # Filtrar módulos si se proporciona un filtro
        modules_to_initialize = module_filter or self.initialization_order

        for module_name in modules_to_initialize:
            if module_name not in self.discovered_modules:
                self.logger.warning(f"Módulo no encontrado: {module_name}")
                continue

            module_class = self.discovered_modules[module_name]

            try:
                # Obtener configuración del módulo
                module_config = self.config_manager.get_module_config(module_name)

                # Validar dependencias
                if not self.config_manager.validate_module_dependencies(
                    module_name, list(self.initialized_modules.keys())
                ):
                    self.logger.warning(
                        f"No se pueden resolver dependencias para {module_name}"
                    )
                    continue

                # Inicializar módulo con configuración
                module_instance = module_class(**module_config.get("init_params", {}))

                # Validar módulo
                module_health = self.module_validator.generate_module_report(
                    module_instance, available_modules=self.initialized_modules
                )

                # Intentar recuperar módulo si no está saludable
                if not module_health["is_healthy"]:
                    recovered_module = self.module_validator.recover_module(
                        module_instance, ModuleHealthStatus(module_name)
                    )

                    if recovered_module:
                        module_instance = recovered_module
                    else:
                        self.logger.error(
                            f"No se pudo recuperar el módulo {module_name}"
                        )
                        continue

                # Registrar módulo inicializado
                self.initialized_modules[module_name] = module_instance

                self.logger.info(f"Módulo inicializado: {module_name}")

            except Exception as e:
                error_msg = f"Error inicializando módulo {module_name}: {e}"
                self.logger.error(error_msg)
                raise ModuleInitializationError(error_msg) from e

        return self.initialized_modules

    def get_initialized_module(self, module_name: str) -> Optional[Any]:
        """
        Obtener un módulo inicializado

        Args:
            module_name (str): Nombre del módulo

        Returns:
            Instancia del módulo o None
        """
        return self.initialized_modules.get(module_name)

    def generate_initialization_report(self) -> Dict[str, Any]:
        """
        Generar informe de inicialización de módulos

        Returns:
            Informe detallado de inicialización
        """
        base_report = super().generate_initialization_report()

        # Añadir validación de módulos al informe
        base_report["module_validations"] = {}

        for module_name, module in self.initialized_modules.items():
            module_validation = self.module_validator.generate_module_report(
                module, available_modules=self.initialized_modules
            )
            base_report["module_validations"][module_name] = module_validation

        return base_report


def main():
    """Demostración del sistema de inicialización"""
    logging.basicConfig(level=logging.INFO)

    # Crear inicializador de módulos
    initializer = ModuleInitializer()

    try:
        # Descubrir módulos
        discovered_modules = initializer.discover_modules()
        print("Módulos descubiertos:", list(discovered_modules.keys()))

        # Inicializar módulos
        initialized_modules = initializer.initialize_modules()
        print("Módulos inicializados:", list(initialized_modules.keys()))

        # Generar informe de inicialización
        report = initializer.generate_initialization_report()
        print("\nInforme de inicialización:")
        print(json.dumps(report, indent=2))

    except ModuleInitializationError as e:
        print(f"Error de inicialización: {e}")


if __name__ == "__main__":
    main()
