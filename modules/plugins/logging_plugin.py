import logging
from typing import Any, Dict

from ..unified_systems.module_plugin_system import ModulePluginBase


class LoggingPlugin(ModulePluginBase):
    """
    Plugin de logging para módulos de NeuroFusion

    Características:
    - Registro de entrada y salida de datos
    - Configuración de nivel de logging
    - Métricas básicas de procesamiento
    """

    def __init__(self, config: Dict[str, Any] = None):
        """
        Inicializar plugin de logging

        Args:
            config (dict, opcional): Configuración del plugin
        """
        super().__init__(config or {})

        # Configuración de logging
        self.log_level = getattr(logging, self.config.get("log_level", "INFO").upper())
        self.logger = logging.getLogger("NeuroFusionLoggingPlugin")
        self.logger.setLevel(self.log_level)

    def pre_process(self, module, input_data: Any) -> Any:
        """
        Registrar datos de entrada

        Args:
            module: Módulo al que se aplica el plugin
            input_data: Datos de entrada

        Returns:
            Datos de entrada sin modificar
        """
        self.logger.log(
            self.log_level,
            f"Pre-procesamiento en {module.__class__.__name__}: {input_data}",
        )
        return input_data

    def post_process(self, module, input_data: Any, output_data: Any) -> Any:
        """
        Registrar datos de salida y métricas

        Args:
            module: Módulo al que se aplica el plugin
            input_data: Datos de entrada originales
            output_data: Datos de salida originales

        Returns:
            Datos de salida sin modificar
        """
        self.logger.log(
            self.log_level,
            f"Post-procesamiento en {module.__class__.__name__}: {output_data}",
        )

        # Registrar métricas básicas
        if hasattr(module, "add_metric"):
            input_size = len(str(input_data)) if input_data is not None else 0
            output_size = len(str(output_data)) if output_data is not None else 0

            module.add_metric("input_size", input_size)
            module.add_metric("output_size", output_size)
            module.add_metric("processing_ratio", output_size / max(input_size, 1))

        return output_data

    def on_error(self, module, input_data: Any, error: Exception) -> Any:
        """
        Manejar y registrar errores

        Args:
            module: Módulo donde ocurrió el error
            input_data: Datos de entrada que causaron el error
            error: Excepción original

        Returns:
            Valor de retorno alternativo o re-lanza la excepción
        """
        self.logger.error(
            f"Error en {module.__class__.__name__}: {error}\n"
            f"Datos de entrada: {input_data}"
        )

        # Opcional: Implementar lógica de recuperación
        if self.config.get("error_recovery", False):
            # Ejemplo de recuperación simple
            return None

        # Por defecto, re-lanzar el error
        raise error


def main():
    """Demostración del plugin de logging"""
    import logging

    logging.basicConfig(level=logging.INFO)

    # Simular un módulo de ejemplo
    class ExampleModule:
        def process(self, data):
            print(f"Procesando datos: {data}")
            return data.upper()

        def add_metric(self, name, value):
            print(f"Métrica {name}: {value}")

    # Crear instancia de módulo
    example_module = ExampleModule()

    # Crear plugin de logging
    logging_plugin = LoggingPlugin({"log_level": "DEBUG", "error_recovery": True})

    try:
        # Pre-procesamiento
        input_data = logging_plugin.pre_process(example_module, "ejemplo de datos")

        # Procesamiento
        output_data = example_module.process(input_data)

        # Post-procesamiento
        final_output = logging_plugin.post_process(
            example_module, input_data, output_data
        )

        print("Resultado final:", final_output)

    except Exception as e:
        logging_plugin.on_error(example_module, input_data, e)


if __name__ == "__main__":
    main()
