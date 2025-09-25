import importlib
import os
import logging
import networkx as nx
from typing import Dict, Any, Type, List, Optional
import json

from .module_registry import ModuleRegistry


class ModuleDependencyResolver:
    """Resuelve dependencias entre módulos"""

    def __init__(self):
        self.dependency_graph = nx.DiGraph()

    def add_dependency(self, module_name: str, dependencies: List[str]):
        """
        Añadir dependencias para un módulo

        Args:
            module_name (str): Nombre del módulo
            dependencies (List[str]): Lista de módulos de los que depende
        """
        for dep in dependencies:
            self.dependency_graph.add_edge(dep, module_name)

    def get_initialization_order(self) -> List[str]:
        """
        Obtener orden de inicialización de módulos basado en dependencias

        Returns:
            Lista de módulos ordenados para inicialización
        """
        try:
            return list(nx.topological_sort(self.dependency_graph))
        except nx.NetworkXUnfeasible:
            logging.warning("Ciclo de dependencias detectado. Resolviendo...")
            return list(self.dependency_graph.nodes)


class ModuleIntegrator:
    def __init__(
        self, base_path: str = "modules", registry_path: str = "module_registry.json"
    ):
        """
        Inicializar integrador de módulos

        Args:
            base_path (str): Ruta base para descubrir módulos
            registry_path (str): Ruta para el registro de módulos
        """
        self.base_path = base_path
        self.logger = logging.getLogger(__name__)
        self.integrated_modules: Dict[str, Any] = {}
        self.dependency_resolver = ModuleDependencyResolver()
        self.module_registry = ModuleRegistry(registry_path)

    def _discover_modules(self) -> Dict[str, str]:
        """Descubre todos los módulos en el sistema"""
        modules = {}
        for root, dirs, files in os.walk(self.base_path):
            for file in files:
                if file.endswith(".py") and not file.startswith("__"):
                    module_path = os.path.join(root, file)
                    module_name = (
                        os.path.relpath(module_path, self.base_path)
                        .replace("/", ".")
                        .replace(".py", "")
                    )
                    modules[module_name] = module_path
        return modules

    def _import_module(self, module_name: str) -> Any:
        """Importa un módulo de forma dinámica"""
        try:
            module = importlib.import_module(f"modules.{module_name}")
            return module
        except ImportError as e:
            self.logger.error(f"Error importando módulo {module_name}: {e}")
            return None

    def _find_module_dependencies(self, module) -> List[str]:
        """
        Encuentra las dependencias de un módulo

        Args:
            module: Módulo a analizar

        Returns:
            Lista de nombres de módulos de los que depende
        """
        dependencies = []
        try:
            # Analizar importaciones
            for name, obj in module.__dict__.items():
                if hasattr(obj, "__module__"):
                    dep_module_name = obj.__module__.split(".")[-1]
                    if dep_module_name != module.__name__.split(".")[-1]:
                        dependencies.append(dep_module_name)
        except Exception as e:
            self.logger.warning(f"No se pudieron detectar dependencias: {e}")

        return dependencies

    def _find_main_classes(self, module):
        """Encuentra las clases principales en un módulo"""
        main_classes = []
        for name, obj in module.__dict__.items():
            if (
                isinstance(obj, type)
                and hasattr(obj, "__module__")
                and obj.__module__ == module.__name__
            ):
                main_classes.append(obj)
        return main_classes

    def integrate_modules(self, llm_system):
        """
        Integra todos los módulos en el sistema LLM

        Args:
            llm_system: Sistema LLM principal

        Returns:
            Diccionario de módulos integrados
        """
        modules = self._discover_modules()

        for module_name, module_path in modules.items():
            module = self._import_module(module_name)
            if module:
                # Detectar dependencias
                dependencies = self._find_module_dependencies(module)
                self.dependency_resolver.add_dependency(module_name, dependencies)

                # Registrar módulo
                self.module_registry.register_module(
                    module_name,
                    module_path,
                    module_type="generic",
                    dependencies=dependencies,
                )

                classes = self._find_main_classes(module)
                for cls in classes:
                    try:
                        # Intentar integrar clases con métodos de procesamiento
                        if hasattr(cls, "process") or hasattr(cls, "generate"):
                            instance = cls()
                            self.integrated_modules[cls.__name__] = instance

                            # Registrar carga de módulo
                            self.module_registry.log_module_load(cls.__name__)

                            self.logger.info(f"Módulo integrado: {cls.__name__}")
                    except Exception as e:
                        self.logger.warning(f"No se pudo integrar {cls.__name__}: {e}")

        # Obtener orden de inicialización basado en dependencias
        initialization_order = self.dependency_resolver.get_initialization_order()
        self.logger.info(f"Orden de inicialización: {initialization_order}")

        # Generar informe de módulos
        module_report = self.module_registry.generate_module_report()
        self.logger.info("Informe de módulos:\n" + json.dumps(module_report, indent=2))

        return self.integrated_modules

    def get_module(self, module_name: str) -> Any:
        """Obtiene un módulo integrado"""
        return self.integrated_modules.get(module_name)

    def get_module_report(self) -> Dict[str, Any]:
        """
        Obtener informe de estado de módulos

        Returns:
            Informe de estado de módulos
        """
        return self.module_registry.generate_module_report()


def main():
    integrator = ModuleIntegrator()
    integrator.integrate_modules(None)  # Placeholder para sistema LLM


if __name__ == "__main__":
    main()
