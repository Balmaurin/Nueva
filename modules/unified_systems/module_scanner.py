import os
import sys
import importlib
import importlib.util
import inspect
import json
import hashlib
import logging
import traceback
import re
from typing import Dict, List, Any, Optional, Type, Tuple
from dataclasses import dataclass, asdict, field

# Configurar logging
logging.basicConfig(
    level=logging.DEBUG,  # Cambiar a DEBUG para más información
    format="%(asctime)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)


@dataclass
class ModuleMetadata:
    """
    Metadatos detallados de un módulo
    """

    name: str
    path: str
    type: str
    version: str = "0.1.0"
    dependencies: List[str] = field(default_factory=list)
    classes: List[str] = field(default_factory=list)
    functions: List[str] = field(default_factory=list)
    size_bytes: int = 0
    hash: Optional[str] = None
    last_modified: Optional[float] = None
    is_importable: bool = False
    docstring: Optional[str] = None
    import_error: Optional[str] = None
    import_traceback: Optional[str] = None
    syntax_errors: List[str] = field(default_factory=list)
    missing_dependencies: List[str] = field(default_factory=list)


class ModuleScanner:
    """
    Sistema de escaneo y análisis de módulos para NeuroFusion
    """

    def __init__(
        self,
        base_path: str = "shaili_ai/modules",
        ignore_dirs: Optional[List[str]] = None,
        output_path: str = "shaili_ai/config/module_catalog.json",
        detailed_report_path: str = "shaili_ai/config/module_scan_report.json",
    ):
        """
        Inicializar escáner de módulos
        """
        self.base_path = os.path.abspath(base_path)
        self.ignore_dirs = ignore_dirs or [
            "__pycache__",
            ".git",
            "tests",
            "unified_systems",
        ]
        self.output_path = output_path
        self.detailed_report_path = detailed_report_path

        # Configurar ruta de importación
        if self.base_path not in sys.path:
            sys.path.insert(0, self.base_path)

        logger.info(f"Inicializando escáner de módulos en {self.base_path}")
        logger.debug(f"Directorios ignorados: {self.ignore_dirs}")

    def _is_valid_module(self, path: str) -> bool:
        """
        Verificar si un archivo es un módulo Python válido
        """
        is_valid = (
            path.endswith(".py")
            and not path.startswith("__")
            and not path.startswith(".")
            and "test_" not in path
        )
        logger.debug(f"Validando módulo {path}: {is_valid}")
        return is_valid

    def _calculate_file_hash(self, path: str) -> str:
        """
        Calcular hash MD5 de un archivo
        """
        with open(path, "rb") as f:
            file_hash = hashlib.md5(f.read()).hexdigest()
        logger.debug(f"Hash de {path}: {file_hash}")
        return file_hash

    def _check_syntax(self, path: str) -> List[str]:
        """
        Verificar sintaxis de un archivo Python
        """
        syntax_errors = []
        try:
            with open(path, "r", encoding="utf-8") as f:
                content = f.read()
                compile(content, path, "exec")
        except SyntaxError as e:
            # Intentar recuperar información del error
            error_line = e.lineno if hasattr(e, "lineno") else "desconocida"
            error_offset = e.offset if hasattr(e, "offset") else "desconocido"
            error_msg = f"Error de sintaxis en {path} (línea {error_line}, columna {error_offset}): {str(e)}"
            syntax_errors.append(error_msg)
            logger.error(error_msg)
        return syntax_errors

    def _check_dependencies(self, module_path: str) -> List[str]:
        """
        Verificar dependencias de un módulo
        """
        missing_dependencies = []

        try:
            with open(module_path, "r", encoding="utf-8") as f:
                module_content = f.read()

            # Buscar importaciones usando regex
            import_pattern = re.compile(
                r"^(?:from\s+(\w+)|import\s+(\w+))", re.MULTILINE
            )
            imports = import_pattern.findall(module_content)

            # Filtrar nombres de módulos
            module_names = [name for group in imports for name in group if name]

            logger.debug(f"Módulos importados en {module_path}: {module_names}")

            for module_name in module_names:
                try:
                    # Intentar importar
                    importlib.import_module(module_name)
                except ImportError:
                    missing_dependencies.append(module_name)
                    logger.warning(f"Módulo faltante: {module_name}")

        except Exception as e:
            logger.error(f"Error verificando dependencias de {module_path}: {e}")

        return missing_dependencies

    def _analyze_module(self, module_path: str) -> ModuleMetadata:
        """
        Analizar un módulo Python y extraer metadatos
        """
        logger.info(f"Analizando módulo: {module_path}")

        # Verificar sintaxis primero
        syntax_errors = self._check_syntax(module_path)

        try:
            # Calcular ruta relativa
            rel_path = os.path.relpath(module_path, self.base_path)
            module_name = rel_path.replace("/", ".").replace("\\", ".")[:-3]

            logger.debug(f"Nombre del módulo: {module_name}")

            # Verificar dependencias
            missing_dependencies = self._check_dependencies(module_path)

            # Intentar importar el módulo
            try:
                spec = importlib.util.spec_from_file_location(module_name, module_path)
                module = importlib.util.module_from_spec(spec)
                spec.loader.exec_module(module)
            except ImportError as e:
                logger.warning(f"No se pudo importar {module_name}: {e}")
                return ModuleMetadata(
                    name=module_name,
                    path=rel_path,
                    type="unknown",
                    is_importable=False,
                    import_error=str(e),
                    import_traceback=traceback.format_exc(),
                    syntax_errors=syntax_errors,
                    missing_dependencies=missing_dependencies,
                )

            # Extraer clases y funciones
            classes = [
                name
                for name, obj in inspect.getmembers(module, inspect.isclass)
                if obj.__module__ == module_name
            ]

            functions = [
                name
                for name, obj in inspect.getmembers(module, inspect.isfunction)
                if obj.__module__ == module_name
            ]

            logger.debug(f"Clases en {module_name}: {classes}")
            logger.debug(f"Funciones en {module_name}: {functions}")

            # Obtener información del archivo
            file_stats = os.stat(module_path)

            # Intentar determinar el tipo de módulo
            module_type = "module"
            if "ai" in module_name.lower():
                module_type = "ai"
            elif "core" in module_name.lower():
                module_type = "core"
            elif "plugin" in module_name.lower():
                module_type = "plugin"

            logger.debug(f"Tipo de módulo: {module_type}")

            return ModuleMetadata(
                name=module_name,
                path=rel_path,
                type=module_type,
                version="0.1.0",  # Versión por defecto
                dependencies=list(getattr(module, "__dependencies__", [])),
                classes=classes,
                functions=functions,
                size_bytes=file_stats.st_size,
                hash=self._calculate_file_hash(module_path),
                last_modified=file_stats.st_mtime,
                is_importable=True,
                docstring=module.__doc__,
                syntax_errors=syntax_errors,
                missing_dependencies=missing_dependencies,
            )

        except Exception as e:
            logger.error(f"Error analizando {module_path}: {e}")
            logger.error(traceback.format_exc())
            return ModuleMetadata(
                name=os.path.splitext(os.path.basename(module_path))[0],
                path=os.path.relpath(module_path, self.base_path),
                type="unknown",
                is_importable=False,
                import_error=str(e),
                import_traceback=traceback.format_exc(),
                syntax_errors=syntax_errors,
            )

    def scan_modules(self) -> Dict[str, ModuleMetadata]:
        """
        Escanear recursivamente todos los módulos
        """
        module_catalog = {}
        detailed_report = {
            "total_modules_scanned": 0,
            "importable_modules": 0,
            "modules_with_errors": [],
            "syntax_errors": [],
            "import_errors": [],
            "missing_dependencies": [],
        }

        logger.info("Iniciando escaneo de módulos...")

        try:
            # Listar todos los archivos en el directorio base
            logger.debug(f"Directorio base: {self.base_path}")

            for root, dirs, files in os.walk(self.base_path):
                # Ignorar directorios especificados
                dirs[:] = [d for d in dirs if d not in self.ignore_dirs]
                logger.debug(f"Directorios a procesar en {root}: {dirs}")

                for file in files:
                    full_path = os.path.join(root, file)

                    if self._is_valid_module(full_path):
                        try:
                            module_metadata = self._analyze_module(full_path)
                            module_catalog[module_metadata.name] = module_metadata

                            # Actualizar informe detallado
                            detailed_report["total_modules_scanned"] += 1

                            if module_metadata.is_importable:
                                detailed_report["importable_modules"] += 1
                            else:
                                detailed_report["modules_with_errors"].append(
                                    {
                                        "module_name": module_metadata.name,
                                        "path": module_metadata.path,
                                        "import_error": module_metadata.import_error,
                                    }
                                )

                            # Registrar errores de sintaxis
                            if module_metadata.syntax_errors:
                                detailed_report["syntax_errors"].extend(
                                    module_metadata.syntax_errors
                                )

                            # Registrar errores de importación
                            if module_metadata.import_error:
                                detailed_report["import_errors"].append(
                                    {
                                        "module_name": module_metadata.name,
                                        "path": module_metadata.path,
                                        "error": module_metadata.import_error,
                                    }
                                )

                            # Registrar dependencias faltantes
                            if module_metadata.missing_dependencies:
                                detailed_report["missing_dependencies"].extend(
                                    module_metadata.missing_dependencies
                                )

                        except Exception as e:
                            logger.error(f"Error procesando {full_path}: {e}")
                            logger.error(traceback.format_exc())

            # Guardar informe detallado
            os.makedirs(os.path.dirname(self.detailed_report_path), exist_ok=True)
            with open(self.detailed_report_path, "w", encoding="utf-8") as f:
                json.dump(detailed_report, f, indent=2, ensure_ascii=False)

            logger.info(
                f"Escaneo completado. Módulos encontrados: {len(module_catalog)}"
            )

        except Exception as e:
            logger.error(f"Error crítico durante el escaneo de módulos: {e}")
            logger.error(traceback.format_exc())
            detailed_report["critical_error"] = str(e)

            # Intentar guardar informe de error
            try:
                os.makedirs(os.path.dirname(self.detailed_report_path), exist_ok=True)
                with open(self.detailed_report_path, "w", encoding="utf-8") as f:
                    json.dump(detailed_report, f, indent=2, ensure_ascii=False)
            except Exception as save_error:
                logger.error(f"No se pudo guardar el informe de error: {save_error}")

        return module_catalog

    def save_module_catalog(self, catalog: Dict[str, ModuleMetadata]):
        """
        Guardar catálogo de módulos en un archivo JSON
        """
        # Convertir ModuleMetadata a diccionario
        serializable_catalog = {
            name: asdict(metadata) for name, metadata in catalog.items()
        }

        os.makedirs(os.path.dirname(self.output_path), exist_ok=True)

        with open(self.output_path, "w", encoding="utf-8") as f:
            json.dump(serializable_catalog, f, indent=2, ensure_ascii=False)

        logger.info(f"Catálogo de módulos guardado en {self.output_path}")

    def load_module_catalog(self) -> Dict[str, ModuleMetadata]:
        """
        Cargar catálogo de módulos desde archivo JSON

        Returns:
            Dict[str, ModuleMetadata]: Catálogo de módulos
        """
        try:
            with open(self.output_path, "r", encoding="utf-8") as f:
                catalog_data = json.load(f)

            return {
                name: ModuleMetadata(**metadata)
                for name, metadata in catalog_data.items()
            }
        except FileNotFoundError:
            return {}

    def find_modules_by_type(
        self, module_type: str, catalog: Optional[Dict[str, ModuleMetadata]] = None
    ) -> List[ModuleMetadata]:
        """
        Encontrar módulos por tipo

        Args:
            module_type (str): Tipo de módulo a buscar
            catalog (Dict[str, ModuleMetadata], opcional): Catálogo de módulos

        Returns:
            List[ModuleMetadata]: Lista de módulos del tipo especificado
        """
        catalog = catalog or self.load_module_catalog()

        return [
            metadata for metadata in catalog.values() if metadata.type == module_type
        ]

    def generate_module_report(
        self, catalog: Optional[Dict[str, ModuleMetadata]] = None
    ) -> Dict[str, Any]:
        """
        Generar informe detallado de módulos
        """
        catalog = catalog or self.load_module_catalog()

        report = {
            "total_modules": len(catalog),
            "importable_modules": 0,
            "module_types": {},
            "total_size_bytes": 0,
            "module_details": {},
            "import_errors": [],
            "syntax_errors": [],
            "missing_dependencies": [],
        }

        for name, metadata in catalog.items():
            if metadata.is_importable:
                report["importable_modules"] += 1
            else:
                report["import_errors"].append(
                    {
                        "module_name": name,
                        "path": metadata.path,
                        "error": metadata.import_error,
                    }
                )

            # Contar tipos de módulos
            report["module_types"][metadata.type] = (
                report["module_types"].get(metadata.type, 0) + 1
            )

            report["total_size_bytes"] += metadata.size_bytes

            # Detalles de módulos
            report["module_details"][name] = {
                "path": metadata.path,
                "type": metadata.type,
                "version": metadata.version,
                "classes": metadata.classes,
                "functions": metadata.functions,
                "size_bytes": metadata.size_bytes,
                "is_importable": metadata.is_importable,
                "syntax_errors": metadata.syntax_errors,
                "missing_dependencies": metadata.missing_dependencies,
            }

            # Agregar errores de sintaxis
            if metadata.syntax_errors:
                report["syntax_errors"].extend(metadata.syntax_errors)

            # Agregar dependencias faltantes
            if metadata.missing_dependencies:
                report["missing_dependencies"].extend(metadata.missing_dependencies)

        return report


def main():
    """
    Punto de entrada para demostración del escáner de módulos
    """
    scanner = ModuleScanner()

    # Escanear módulos
    module_catalog = scanner.scan_modules()

    # Guardar catálogo
    scanner.save_module_catalog(module_catalog)

    # Generar informe
    module_report = scanner.generate_module_report()

    print("Informe de módulos:")
    print(json.dumps(module_report, indent=2))


if __name__ == "__main__":
    main()
