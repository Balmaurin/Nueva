import importlib
import inspect
import logging
from typing import Dict, Any, Type, Callable, Optional, List


class ModulePluginBase:
    """
    Clase base para plugins de módulos en NeuroFusion

    Los plugins pueden:
    - Extender funcionalidades de módulos
    - Añadir comportamientos personalizados
    - Interceptar y modificar flujos de procesamiento
    """

    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """
        Inicializar plugin

        Args:
            config (dict, opcional): Configuración del plugin
        """
        self.config = config or {}
        self.logger = logging.getLogger(self.__class__.__name__)

    def pre_process(self, module, input_data: Any) -> Any:
        """
        Método de preprocesamiento (opcional)

        Args:
            module: Módulo al que se aplica el plugin
            input_data: Datos de entrada

        Returns:
            Datos de entrada modificados o sin cambios
        """
        return input_data

    def post_process(self, module, input_data: Any, output_data: Any) -> Any:
        """
        Método de posprocesamiento (opcional)

        Args:
            module: Módulo al que se aplica el plugin
            input_data: Datos de entrada originales
            output_data: Datos de salida originales

        Returns:
            Datos de salida modificados
        """
        return output_data

    def on_error(self, module, input_data: Any, error: Exception) -> Any:
        """
        Método de manejo de errores (opcional)

        Args:
            module: Módulo donde ocurrió el error
            input_data: Datos de entrada que causaron el error
            error: Excepción original

        Returns:
            Valor de retorno alternativo o re-lanza la excepción
        """
        raise error


class ModulePluginManager:
    """
    Gestor de plugins para módulos de NeuroFusion

    Características:
    - Registro dinámico de plugins
    - Aplicación de plugins a módulos
    - Descubrimiento automático de plugins
    """

    def __init__(self, plugin_base_path: str = "shaili_ai/modules/plugins"):
        """
        Inicializar gestor de plugins

        Args:
            plugin_base_path (str): Ruta base para descubrir plugins
        """
        self.logger = logging.getLogger(__name__)
        self.registered_plugins: Dict[str, Type[ModulePluginBase]] = {}
        self.active_plugins: Dict[str, List[ModulePluginBase]] = {}
        self.plugin_base_path = plugin_base_path

    def discover_plugins(self):
        """
        Descubrir plugins disponibles en el sistema

        Busca clases que hereden de ModulePluginBase
        """
        try:
            # Importar módulos de plugins
            plugin_module = importlib.import_module("shaili_ai.modules.plugins")

            for name, obj in inspect.getmembers(plugin_module):
                if (
                    inspect.isclass(obj)
                    and issubclass(obj, ModulePluginBase)
                    and obj is not ModulePluginBase
                ):
                    self.register_plugin(name, obj)
        except ImportError:
            self.logger.warning("No se encontró el módulo de plugins")

    def register_plugin(self, name: str, plugin_class: Type[ModulePluginBase]):
        """
        Registrar un plugin

        Args:
            name (str): Nombre del plugin
            plugin_class (Type): Clase del plugin
        """
        self.registered_plugins[name] = plugin_class
        self.logger.info(f"Plugin registrado: {name}")

    def create_plugin_instance(
        self, plugin_name: str, config: Optional[Dict[str, Any]] = None
    ) -> Optional[ModulePluginBase]:
        """
        Crear una instancia de plugin

        Args:
            plugin_name (str): Nombre del plugin
            config (dict, opcional): Configuración del plugin

        Returns:
            Instancia del plugin o None
        """
        plugin_class = self.registered_plugins.get(plugin_name)
        if plugin_class:
            return plugin_class(config)
        return None

    def apply_plugin_to_module(
        self, module, plugin_name: str, config: Optional[Dict[str, Any]] = None
    ):
        """
        Aplicar un plugin a un módulo

        Args:
            module: Módulo al que se aplica el plugin
            plugin_name (str): Nombre del plugin
            config (dict, opcional): Configuración del plugin
        """
        plugin = self.create_plugin_instance(plugin_name, config)
        if plugin:
            module_key = module.__class__.__name__

            if module_key not in self.active_plugins:
                self.active_plugins[module_key] = []

            self.active_plugins[module_key].append(plugin)
            self.logger.info(f"Plugin {plugin_name} aplicado a {module_key}")

    def process_with_plugins(
        self, module, input_data: Any, original_process_method: Callable
    ) -> Any:
        """
        Procesar datos con plugins

        Args:
            module: Módulo original
            input_data: Datos de entrada
            original_process_method: Método de procesamiento original

        Returns:
            Resultado del procesamiento
        """
        module_key = module.__class__.__name__
        plugins = self.active_plugins.get(module_key, [])

        try:
            # Pre-procesamiento
            for plugin in plugins:
                input_data = plugin.pre_process(module, input_data)

            # Procesamiento original
            output_data = original_process_method(input_data)

            # Post-procesamiento
            for plugin in reversed(plugins):
                output_data = plugin.post_process(module, input_data, output_data)

            return output_data

        except Exception as e:
            # Manejo de errores por plugins
            for plugin in plugins:
                try:
                    return plugin.on_error(module, input_data, e)
                except Exception:
                    continue

            # Si ningún plugin maneja el error, re-lanzar
            raise

    def get_active_plugins(self, module) -> List[ModulePluginBase]:
        """
        Obtener plugins activos para un módulo

        Args:
            module: Módulo

        Returns:
            Lista de plugins activos
        """
        module_key = module.__class__.__name__
        return self.active_plugins.get(module_key, [])


def main():
    """Demostración del sistema de plugins"""
    logging.basicConfig(level=logging.INFO)

    # Crear gestor de plugins
    plugin_manager = ModulePluginManager()

    # Descubrir plugins disponibles
    plugin_manager.discover_plugins()

    # Simular un módulo de ejemplo
    class ExampleModule:
        def process(self, data):
            print(f"Procesando datos: {data}")
            return data.upper()

    # Crear instancia de módulo
    example_module = ExampleModule()

    # Aplicar un plugin hipotético de logging
    plugin_manager.apply_plugin_to_module(
        example_module, "LoggingPlugin", {"log_level": "INFO"}
    )

    # Procesar datos con plugins
    result = plugin_manager.process_with_plugins(
        example_module, "ejemplo de datos", example_module.process
    )

    print("Resultado:", result)


if __name__ == "__main__":
    main()
